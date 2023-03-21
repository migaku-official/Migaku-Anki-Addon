from platform import platform
import sys
import os
import platform

import aqt
from aqt.qt import *
import anki


# insert librairies into sys.path

def add_sys_path(*path_parts):
    sys.path.insert(
        0,
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'lib',
            *path_parts
        )
    )

add_sys_path('shared')
if anki.utils.isLin:
    add_sys_path('linux')
elif anki.utils.isMac and platform.processor() == 'arm':
    add_sys_path('macos_arm')
elif anki.utils.isMac:
    add_sys_path('macos')
elif anki.utils.isWin:
    add_sys_path('windows')


# Allow webviews to access necessary resources
aqt.mw.addonManager.setWebExports(__name__, r'(languages/.*?\.svg|inplace_editor.css)')

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
    global_hotkeys,
    webview_contextmenu,
    settings_window,
    ease_reset,
    retirement,
    balance_scheduler,
    balance_scheduler_vacation_window,
    balance_scheduler_dayoff_window,
    #video_driver_fix,
)


from . import migaku_connection


def setup_menu():
    menu = QMenu('Migaku', aqt.mw)
    menu.addAction(settings_window.action)
    menu.addSeparator()
    menu.addAction(ease_reset.action)
    menu.addAction(retirement.action)
    menu.addAction(balance_scheduler.action)
    menu.addAction(balance_scheduler_vacation_window.action)
    menu.addAction(balance_scheduler_dayoff_window.action)
    aqt.mw.form.menubar.insertMenu(aqt.mw.form.menuHelp.menuAction(), menu)

setup_menu()
