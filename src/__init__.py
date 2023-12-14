from platform import platform
import sys
import os

import aqt
from aqt.qt import *
import anki

from .sys_libraries import init_sys_libs

init_sys_libs()

# Initialize sub modules
from . import (
    anki_version,
    balance_scheduler,
    browser,
    balance_scheduler_vacation_window,
    balance_scheduler_dayoff_window,
    card_layout,
    card_type_selector,
    click_play_audio,
    ease_reset,
    editor,
    inplace_editor,
    migaku_connection,
    note_type_dialogs,
    note_type_mgr,
    retirement,
    reviewer,
    settings_window,
    toolbar,
    webview_contextmenu,
    welcome_wizard,
)


def setup_menu():
    menu = QMenu("Migaku", aqt.mw)
    menu.addAction(settings_window.action)
    menu.addSeparator()
    menu.addAction(ease_reset.action)
    menu.addAction(retirement.action)
    menu.addAction(balance_scheduler.action)
    menu.addAction(balance_scheduler_vacation_window.action)
    menu.addAction(balance_scheduler_dayoff_window.action)
    aqt.mw.form.menubar.insertMenu(aqt.mw.form.menuHelp.menuAction(), menu)


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
    aqt.gui_hooks.add_cards_did_change_deck.append(
        editor.current_editor.on_addcards_did_change_deck
    )
    aqt.gui_hooks.addcards_did_change_note_type.append(
        editor.current_editor.on_addcards_did_change_note_type
    )

    aqt.gui_hooks.editor_did_init.append(editor.current_editor.set_current_editor)
    aqt.editor.Editor.cleanup = anki.hooks.wrap(
        aqt.editor.Editor.cleanup, editor.current_editor.remove_editor, "before"
    )

    aqt.gui_hooks.profile_did_open.append(note_type_mgr.update_all_installed)

    aqt.gui_hooks.top_toolbar_will_set_left_tray_content.append(
        toolbar.inject_migaku_toolbar
    )
    aqt.gui_hooks.add_cards_did_change_deck.append(
        lambda _: toolbar.refresh_migaku_toolbar()
    )
    aqt.gui_hooks.addcards_did_change_note_type.append(
        lambda _, _1, _2: toolbar.refresh_migaku_toolbar()
    )

    aqt.gui_hooks.add_cards_did_init.append(
        lambda _: toolbar.refresh_migaku_toolbar_opened_addcards()
    )
    aqt.addcards.AddCards._close = anki.hooks.wrap(
        aqt.addcards.AddCards._close,
        lambda _: toolbar.refresh_migaku_toolbar(),
        "after",
    )

    aqt.addcards.AddCards.on_notetype_change = anki.hooks.wrap(
        aqt.addcards.AddCards.on_notetype_change,
        lambda addcards, _1: editor.reset_migaku_mode(addcards.editor),
        "before",
    )


setup_menu()
setup_hooks()
anki_version.check_anki_version_dialog()
