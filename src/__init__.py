from dataclasses import dataclass
from platform import platform
import sys
import os

import aqt
from aqt.qt import *
import anki
from .config import get

from .sys_libraries import init_sys_libs

init_sys_libs()

# Initialize sub modules
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


def setup_hooks():
    # Allow webviews to access necessary resources
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
    elif getattr(aqt.addcards.AddCards, "on_deck_changed", None):
        aqt.addcards.AddCards.on_deck_changed = anki.hooks.wrap(
            aqt.addcards.AddCards.on_deck_changed,
            lambda _, id: deck_change(id),
            "before",
        )
    else:
        aqt.deckchooser.DeckChooser.choose_deck = anki.hooks.wrap(
            aqt.deckchooser.DeckChooser.choose_deck,
            lambda deckchooser: deck_change(deckchooser.selected_deck_id),
            "after",
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

    aqt.addcards.AddCards.on_notetype_change = anki.hooks.wrap(
        aqt.addcards.AddCards.on_notetype_change,
        lambda addcards, _1: editor.reset_migaku_mode(addcards.editor),
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


menu.setup_menu()
setup_hooks()
anki_version.check_anki_version_dialog()
