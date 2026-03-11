
from .sys_libraries import init_sys_libs
# We need to import init_sys_libs before anything else as the imports might have side effects
init_sys_libs()

from dataclasses import dataclass
from platform import platform
import sys
import os
import logging

# Set up logger for addon initialization
logger = logging.getLogger("migaku.addon")
logger.setLevel(logging.INFO)

# Log startup message
logger.info("=" * 60)
logger.info("Migaku Anki Addon loading...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Platform: {platform()}")
logger.info("=" * 60)

import aqt
from aqt.qt import *
import anki
from anki.utils import is_win
from .config import get, set

from inspect import signature

# Set up early logging with memory buffer to capture logs before profile loads
from logging.handlers import MemoryHandler
_early_log_buffer = None

def setup_file_logging():
    """Set up file logging for debugging. Logs are written to profile folder."""
    global _early_log_buffer
    
    try:
        # Check if profile manager and folder are available
        if not hasattr(aqt.mw, 'pm') or not aqt.mw.pm:
            return False
        
        profile_folder = aqt.mw.pm.profileFolder()
        if not profile_folder:
            return False
            
        log_file = os.path.join(profile_folder, "migaku_addon.log")

        # Check if we already added this handler (avoid duplicates)
        migaku_logger = logging.getLogger('migaku')
        for handler in migaku_logger.handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                if hasattr(handler, 'baseFilename') and handler.baseFilename == log_file:
                    # Already set up
                    return True

        # Create file handler with rotation (max 5MB, keep 2 backups)
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=2,
            encoding='utf-8'
        )

        # Format: timestamp - logger name - level - message
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)

        # Add file handler to all Migaku loggers
        migaku_logger.addHandler(file_handler)
        migaku_logger.setLevel(logging.INFO)  # Set to DEBUG for verbose logging

        # Flush buffered logs to file if we had a memory buffer
        if _early_log_buffer:
            _early_log_buffer.setTarget(file_handler)
            _early_log_buffer.flush()
            _early_log_buffer.close()
            migaku_logger.removeHandler(_early_log_buffer)
            _early_log_buffer = None

        migaku_logger.info("File logging initialized")
        return True

    except Exception:
        # If file logging setup fails, will retry later
        return False

# Set up memory buffer to capture early logs before profile is loaded
migaku_logger = logging.getLogger('migaku')
migaku_logger.setLevel(logging.INFO)
_early_log_buffer = MemoryHandler(capacity=1000, flushLevel=logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_early_log_buffer.setFormatter(formatter)
migaku_logger.addHandler(_early_log_buffer)

# Try to initialize file logging immediately (likely will fail, but worth trying)
setup_file_logging()

# Initialize sub modules
logger.info("Importing addon modules...")
try:
    from . import (
        anki_version,
        browser,
        card_layout,
        card_type_selector,
        click_play_audio,
        editor,
        inplace_editor,
        migaku_connection,
        note_type_dialogs,
        note_type_mgr,
        reviewer,
        toolbar,
        webview_contextmenu,
        welcome_wizard,
        menu,
    )
    logger.info("All addon modules imported successfully")
except Exception as e:
    logger.error(f"Failed to import addon modules: {type(e).__name__}: {e}", exc_info=True)
    raise


def setup_hooks():
    # Allow webviews to access necessary resources
    if not get("turned_off_normalize_audio"):
        set("normalize_audio", False)
        set("turned_off_normalize_audio", True)

    aqt.mw.addonManager.setWebExports(
        __name__, r"(languages/.*?\.svg|inplace_editor.css)"
    )

    aqt.gui_hooks.models_did_init_buttons.append(note_type_dialogs.setup_note_editor)
    aqt.editor.Editor.onBridgeCmd = anki.hooks.wrap(
        aqt.editor.Editor.onBridgeCmd, editor.on_migaku_bridge_cmds, "around"
    )
    aqt.gui_hooks.editor_did_init.append(editor.editor_did_init)
    aqt.gui_hooks.editor_did_load_note.append(editor.editor_did_load_note)
    aqt.gui_hooks.editor_did_init_buttons.append(editor.setup_editor_buttons)

    # DECK CHANGE
    def deck_change(id):
        editor.current_editor.on_addcards_did_change_deck(id)
        toolbar.refresh_migaku_toolbar()

    if getattr(aqt.gui_hooks, "add_cards_did_change_deck", None):
        aqt.gui_hooks.add_cards_did_change_deck.append(deck_change)
    else:
        aqt.addcards.AddCards.on_deck_changed = anki.hooks.wrap(
            aqt.addcards.AddCards.on_deck_changed,
            lambda _, id: deck_change(id),
            "before",
        )

    ### MODEL CHANGE
    def notetype_change(id):
        editor.current_editor.on_addcards_did_change_note_type(id)
        toolbar.refresh_migaku_toolbar()

    if getattr(aqt.gui_hooks, "add_cards_did_change_note_type", None):
        aqt.gui_hooks.add_cards_did_change_note_type.append(
            lambda _, id: notetype_change(id)
        )
    elif getattr(aqt.addcards.AddCards, "on_notetype_change", None):
        aqt.addcards.AddCards.on_notetype_change = anki.hooks.wrap(
            aqt.addcards.AddCards.on_notetype_change,
            lambda _, id: notetype_change(id),
        )
    else:
        aqt.addcards.AddCards.onModelChange = anki.hooks.wrap(
            aqt.addcards.AddCards.onModelChange,
            notetype_change,
        )

    aqt.gui_hooks.editor_did_init.append(editor.current_editor.set_current_editor)
    aqt.editor.Editor.cleanup = anki.hooks.wrap(
        aqt.editor.Editor.cleanup, editor.current_editor.remove_editor, "before"
    )

    aqt.gui_hooks.profile_did_open.append(note_type_mgr.update_all_installed)
    aqt.gui_hooks.profile_did_open.append(setup_file_logging)

    aqt.gui_hooks.collection_did_load.append(toolbar.inject_migaku_toolbar)

    @dataclass
    class Defaults:
        notetype_id: int
        deck_id: int

    def set_current_deck_model_to_migaku(current_review_card):
        toolbar.set_deck_type_to_migaku()
        return Defaults(
            get("migakuNotetypeId"),
            get("migakuDeckId"),
        )

    def overwrite_defaults_for_adding(col):
        col.defaults_for_adding = set_current_deck_model_to_migaku

    aqt.gui_hooks.collection_did_load.append(overwrite_defaults_for_adding)

    sig = signature(aqt.addcards.AddCards.on_notetype_change)

    if len(sig.parameters) == 2:
        aqt.addcards.AddCards.on_notetype_change = anki.hooks.wrap(
            aqt.addcards.AddCards.on_notetype_change,
            lambda addcards, _1: editor.reset_migaku_mode(addcards.editor),
            "before",
        )
    else:
        aqt.addcards.AddCards.on_notetype_change = anki.hooks.wrap(
            aqt.addcards.AddCards.on_notetype_change,
            lambda addcards, _1, _2: editor.reset_migaku_mode(addcards.editor),
            "before",
        )

    aqt.gui_hooks.add_cards_did_init.append(
        lambda _: toolbar.refresh_migaku_toolbar_opened_addcards()
    )

    # aqt.deckbrowser.DeckBrowser.set_current_deck = anki.hooks.wrap(
    #     aqt.deckbrowser.DeckBrowser.set_current_deck,
    #     lambda self, deck_id: toolbar.refresh_migaku_toolbar(),
    #     "after",
    # )


logger.info("Setting up menu and hooks...")
menu.setup_menu()
setup_hooks()
anki_version.check_anki_version_dialog()

logger.info("✓ Migaku Anki Addon loaded successfully")
logger.info("=" * 60)
