from typing import TypedDict
from dataclasses import dataclass

from aqt import mw

class NotesMenu(TypedDict):
    # Add Notes...
    actionAdd: bool
    actionExport: bool
    actionAdd_Tags: bool
    actionRemove_Tags: bool
    actionClear_Unused_Tags: bool
    actionToggle_Mark: bool
    actionFindDuplicates: bool
    actionFindReplace: bool
    actionManage_Note_Types: bool

class CardsMenu(TypedDict):
    actionReposition: bool
    menuFlag: bool
    action_Info: bool
class BrowserTopMenu(TypedDict):
    ### keep "Go" menu?
    goMenu: bool
    ### help guide links to Migaku? 
    migakuGuide: bool

class MenuActions(TypedDict):
    ### To get all actions simply combine dicts together
    notesMenu: NotesMenu
    cardsMenu: CardsMenu
    
class Browser(TypedDict):
    ######################
    ### Context Menu items
    ######################
    menuActions: MenuActions
    topMenu: BrowserTopMenu
    toggleSidebar: bool
    

class RightTopBtns(TypedDict):
    superscript: bool
    subscript: bool
    clozeDeletion: bool
    latexMenu: bool

class Editor(TypedDict):
    fieldsCardsButtons: bool
    rightTopBtns: RightTopBtns

class AddWindow(TypedDict):
    ### addWindow prepended to avoid name clashes
    addWindowMigakuHelpButton: bool

class Preferences(TypedDict):
    showEstimates: bool
    showProgress: bool
    newSched: bool
    learnAheadLimit: bool
    renameNetwork: bool

class DeckConf(TypedDict):
    steps: bool
    graduatingInterval: bool
    easyInterval: bool
    startingEase: bool
    buryRelatedNew: bool
    lapsesTab: bool
    maxReviews: bool
    easyBonus: bool
    intervalModifier: bool
    maxInterval: bool
    buryRelatedReviews: bool
    ### deckConf prepended to avoid name clashes
    deckConfMigakuHelpButton: bool

class DeckOverview(TypedDict):
    customStudy: bool
class Tools(TypedDict):
    actionStudyDeck: bool
    actionCreateFiltered: bool

class Simplifications(TypedDict):
    tools: Tools
    deckOverview: DeckOverview
    deckConf: DeckConf
    preferences: Preferences
    addWindow: AddWindow
    editor: Editor
    browser: Browser

class OurConfig(TypedDict):
    """
    This will give us type hints for our config, making reading and
    writing easier.
    """
    toggle_gui_simplification: bool
    simplifications: Simplifications
    warnNoteTypes: bool



def readConfig() -> OurConfig:
    return mw.addonManager.getConfig(__name__)

def writeConfig(config: OurConfig):
    mw.addonManager.writeConfig(__name__, config)

@dataclass
class ConfigInfo:
    displayString: str
    ifCheckedMsg: str
    ifUncheckedMsg: str

    def tooltipMsg(self):
        return f"If checked, {self.ifCheckedMsg}; If unchecked, {self.ifUncheckedMsg}"


configKey2ConfigInfoMap = {
    ###########################################################
    ### "subtrees" / Menus the stuff in the tree with children
    ###########################################################
    "tools" : ConfigInfo(
        "Tools Menu", "",""
    )
    ,"deckOverview" : ConfigInfo(
        "Deck Overview", "",""
    )
    ,"deckConf" : ConfigInfo(
        "Deck Options", "",""
    )
    ,"preferences" : ConfigInfo(
        "Preferences", "",""
    )
    ,"addWindow" : ConfigInfo(
        "\"Add\" Window", "",""
    )
    ,"editor" : ConfigInfo(
        "Editor", "",""
    )
    ,"browser" : ConfigInfo(
        "Browser", "",""
    )
    ,"rightTopBtns" : ConfigInfo(
        "Right-top Buttons", "",""
    )
    ,"menuActions" : ConfigInfo(
        "Menu Actions", "",""
    )
    ,"notesMenu" : ConfigInfo(
        "Notes Menu", "",""
    )
    ,"cardsMenu" : ConfigInfo(
        "Cards Menu", "",""
    )
    ,"topMenu" : ConfigInfo(
        "Top Menubar", "",""
    )
    ##############################################
    ### "Leafs" of the config tree IE no children
    ##############################################
    ,"actionStudyDeck" : ConfigInfo(
        "Study Deck...", "show this menu","hide this menu"
    )
    , "actionCreateFiltered": ConfigInfo(
        "Create Filtered...", "show this menu","hide this menu"
    )
    , "customStudy": ConfigInfo(
        "Custom Study", "show this button","remove this button"
    )
    , "steps": ConfigInfo(
        "Pre-promotion Intervals", "show this option","remove this option"
    )
    , "graduatingInterval": ConfigInfo(
        "Graduating Interval", "show this option","remove this option"
    )
    , "easyInterval": ConfigInfo(
        "Easy Interval", "show this option","remove this option"
    )
    , "startingEase": ConfigInfo(
        "Starting Ease", "show this option","remove this option"
    )
    , "buryRelatedNew": ConfigInfo(
        "Bury Related New", "show this option","remove this option"
    )
    , "lapsesTab": ConfigInfo(
        "Lapses Tab", "show this tab","remove this tab"
    )
    , "maxReviews": ConfigInfo(
        "Max Reviews", "show this option","remove this option"
    )
    , "easyBonus": ConfigInfo(
        "Easy Bonus", "show this option","remove this option"
    )
    , "intervalModifier": ConfigInfo(
        "Interval Modifier", "show this option","remove this option"
    )
    , "maxInterval": ConfigInfo(
        "Max Interval", "show this option","remove this option"
    )
    , "buryRelatedReviews": ConfigInfo(
        "Bury Related Reviews", "show this option","remove this option"
    )
    , "showEstimates": ConfigInfo(
        "Show Estimates", 'show "Show next review time above answer buttons" in preferences',"hide this option"
    )
    , "showProgress": ConfigInfo(
        "Show Progress", 'show "Show remaining card count" option in preferences','hide this option'
    )
    , "newSched": ConfigInfo(
        "New Scheduler", 'show "Anki 2.1 scheduler (beta)" option in preferences',"hide this option"
    )
    , "learnAheadLimit": ConfigInfo(
        "Learn Ahead Limit", 'show "Learn ahead limit" option in preferences',"hide this option"
    )
    , "renameNetwork": ConfigInfo(
        "Rename Network", 'Rename Network tab in preferences to "Syncing"',"don't rename this tab"
    )
    , "deckConfMigakuHelpButton": ConfigInfo(
        "Migaku Help Button", "Help button links to Migaku Help page","help button links to standard page"
    )
    , "addWindowMigakuHelpButton": ConfigInfo(
        "Migaku Help Button", "Help button links to Migaku Help page","help button links to standard page"
    )
    , "fieldsCardsButtons": ConfigInfo(
        "Fields.../Cards... buttons", "Show Fields... and Cards... buttons in Editor","hide these buttons"
    )
    , "superscript": ConfigInfo(
        "Superscript", "Show superscript format-button in Editor","hide this button, and disable hotkey"
    )
    , "subscript": ConfigInfo(
        "Subscript", "Show subscript format-button in Editor","hide this button, and disable hotkey"
    )
    , "clozeDeletion": ConfigInfo(
        "Cloze Deletion", "Show Cloze deletion format-button in Editor","hide this button, and disable hotkey"
    )
    , "latexMenu": ConfigInfo(
        "Latex Menu", "Show latex menu in Editor","hide this menu, and disable hotkeys"
    )
    , "actionAdd": ConfigInfo(
        "Add Notes...", "keep the \"Add Notes...\" actions in the browser (context menu and top menu)","remove these actions (and disable hotkeys)"
    )
    , "actionExport": ConfigInfo(
        "Export Notes...", "keep the \"Export Notes...\" actions in the browser (context menu and top menu)","remove these actions (and disable hotkeys)"
    )
    , "actionAdd_Tags": ConfigInfo(
        "Add Tags...", "keep the \"Add Tags...\" actions in the browser (context menu and top menu)","remove these actions (and disable hotkeys)"
    )
    , "actionRemove_Tags": ConfigInfo(
        "Remove Tags...", "keep the \"Remove Tags...\" actions in the browser (context menu and top menu)","remove these actions (and disable hotkeys)"
    )
    , "actionClear_Unused_Tags": ConfigInfo(
        "Clear Unused Tags", "keep the \"Clear Unused Tags...\" actions in the browser (context menu and top menu)","remove these actions (and disable hotkeys)"
    )
    , "actionToggle_Mark": ConfigInfo(
        "Toggle Mark", "keep the \"Toggle Mark...\" actions in the browser (context menu and top menu)","remove these actions (and disable hotkeys)"
    )
    , "actionFindDuplicates": ConfigInfo(
        "Find Duplicates...", "keep the \"Find Duplicates...\" actions in the browser (context menu and top menu)","remove these actions (and disable hotkeys)"
    )
    , "actionFindReplace": ConfigInfo(
        "Find and Replace...", "keep the \"Find and Replace...\" actions in the browser (context menu and top menu)","remove these actions (and disable hotkeys)"
    )
    , "actionManage_Note_Types": ConfigInfo(
        "Manage Note Types...", "keep the \"Manage Note Types...\" actions in the browser (context menu and top menu)","remove these actions (and disable hotkeys)"
    )
    , "actionReposition": ConfigInfo(
        "Reposition...", "keep the \"Reposition...\" actions in the browser (context menu and top menu)","remove these actions (and disable hotkeys)"
    )
    , "menuFlag": ConfigInfo(
        "Flag Menu", "keep the \"Flag\" menu and actions in the browser (context menu and top menu)","remove this menu and these actions (and disable hotkeys)"
    )
    , "action_Info": ConfigInfo(
        "Info...", "keep the \"Info...\" actions in the browser (context menu and top menu)","remove these actions (and disable hotkeys)"
    )
    , "goMenu": ConfigInfo(
        "Go Menu", "keep the \"Go\" menu in the browser","remove this menu (and disable hotkeys)"
    )
    , "migakuGuide": ConfigInfo(
        "Migaku Guide...", "Replace the Guide... action in the browser with the Migaku Guide.","do not do this"
    )
    , "toggleSidebar": ConfigInfo(
        "Sidebar toggle", "keep the sidebar toggle in the browser","remove this function"
    )
}