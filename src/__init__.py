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
    aqt.gui_hooks.editor_web_view_did_init.append(editor.editor_webview_did_init)
    aqt.gui_hooks.editor_did_load_note.append(editor.editor_note_changed)
    aqt.gui_hooks.editor_did_init_buttons.append(editor.setup_editor_buttons)
    aqt.gui_hooks.profile_did_open.append(note_type_mgr.update_all_installed)


setup_menu()
setup_hooks()
anki_version.check_anki_version_dialog()
