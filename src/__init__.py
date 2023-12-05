from platform import platform
import sys
import os

import aqt
from aqt.qt import *
import anki


# insert librairies into sys.path


def add_sys_path(*path_parts):
    sys.path.insert(
        0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib", *path_parts)
    )


add_sys_path("shared")
if anki.utils.is_lin:
    add_sys_path("linux")
elif anki.utils.is_mac and sys.version_info.major >= 3 and sys.version_info.minor >= 11:
    add_sys_path("macos_311")
elif anki.utils.is_mac and sys.version_info.major >= 3 and sys.version_info.minor >= 10:
    add_sys_path("macos_310")
elif anki.utils.is_mac:
    add_sys_path("macos_39")
elif anki.utils.is_win:
    add_sys_path("windows")


# Allow webviews to access necessary resources
aqt.mw.addonManager.setWebExports(__name__, r"(languages/.*?\.svg|inplace_editor.css)")

# Initialize sub modules
from . import (
    note_type_dialogs,
    card_type_selector,
    note_type_mgr,
    reviewer,
    editor,
    inplace_editor,
    click_play_audio,
    browser,
    card_layout,
    welcome_wizard,
    webview_contextmenu,
    settings_window,
    ease_reset,
    retirement,
    balance_scheduler,
    balance_scheduler_vacation_window,
    balance_scheduler_dayoff_window,
    anki_version,
)


from . import migaku_connection


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
    aqt.gui_hooks.models_did_init_buttons.append(note_type_dialogs.setup_note_editor)
    aqt.gui_hooks.editor_did_load_note.append(editor.editor_note_changed)
    aqt.gui_hooks.editor_did_init_buttons.append(editor.setup_editor_buttons)
    aqt.gui_hooks.profile_did_open.append(note_type_mgr.update_all_installed)

setup_menu()
anki_version.check_anki_version_dialog()
