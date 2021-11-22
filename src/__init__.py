import sys
import os
import aqt
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
    browser,
    welcome_wizard,
    global_hotkeys,
    #simplify
)


from . import migaku_connection
