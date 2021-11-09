from typing import List
from anki.hooks import addHook
from aqt import gui_hooks, mw
from aqt.editor import Editor, EditorWebView
from aqt.webview import WebContent

from .configWrapper import readConfig

def onWebviewSetContent(web_content: WebContent, context):
    if not (isinstance(context, Editor) or isinstance(context, EditorWebView)):
        # print("simplifyeditor.py->onWebViewSetContent: not instance of Editor, skipping...")
        return

    print("simplify_editor onWebviewSetContent called.")

    if mw.migakuGuiSimplification and (not readConfig()['simplifications']["editor"]["fieldsCardsButtons"]):
        addon_package = mw.addonManager.addonFromModule(__name__)
        web_content.css.append(
            f"/_addons/{addon_package}/web/editor.css"
        )
        # print(f"disable web_content css appended. web_content.css={web_content.css}")

gui_hooks.webview_will_set_content.append(onWebviewSetContent)


###################################################
### Very shady because we are just using
###  indices rather than finding the buttons
###  properly. Make sure it matches Anki or it will
###  break.
###################################################

### The reverse index of the buttons
### We go backwards because the chinese addon
### adds some buttons at the front.
buttonNameIndexMap = {
    "superscript": -9,
    "subscript": -8,
    "clozeDeletion": -4,
    "latexMenu": -1
}

def onSetupEditorButtons(righttopbtns: List[str], editor: Editor ) -> List[str]:
    """
    Filter out the buttons on the top right of the editor, based on config.
    As usual, False means remove, True means keep.
    """

    if not mw.migakuGuiSimplification:
        return righttopbtns

    check = readConfig()["simplifications"]["editor"]["rightTopBtns"]

    indices2remove = set()
    for key, keep in check.items():
        if not keep:
            indices2remove.add(righttopbtns[
                buttonNameIndexMap[key]
            ])

    return list(filter(lambda x: x not in indices2remove, righttopbtns))

addHook("setupEditorButtons", onSetupEditorButtons)



### Map the shortcut to list of its index in shortcuts list 
# KEEP UP TO DATE.
shortcutIdxMap = {
    "superscript": (4,),
    "subscript": (5,),
    "clozeDeletion": (9,10),
    "latexMenu": ( ### special because theres loads
        13,14,15,16,17,18
    )
}



def onInitShortcuts(cuts: List[tuple], editor: Editor):
    """
    again depending on config, disable certain functions in the editor,
    IE set them to None.
    """
    print("onInitShortcuts called.")

    if not mw.migakuGuiSimplification:
        return

    check = readConfig()["simplifications"]["editor"]["rightTopBtns"]

    ### Set because we don't want to remove the same
    ### index twice. 
    indices2remove = set()

    for key, keep in check.items():
        if not keep:
            for idx in shortcutIdxMap[key]:
                indices2remove.add(idx)

    for idx in sorted(indices2remove, reverse=True):
        del cuts[idx]



gui_hooks.editor_did_init_shortcuts.append(onInitShortcuts)