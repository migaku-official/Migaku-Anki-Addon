import sys
import os
import aqt

# Add lib folder to import path
sys.path.append(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'lib'
    )
)

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