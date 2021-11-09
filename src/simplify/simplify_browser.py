from os.path import dirname
from typing import Union

from anki.lang import _
from anki.utils import noBundledLibs
from aqt import gui_hooks, mw
from aqt.qt import *
from aqt.browser import Browser, SidebarItem, SidebarStage
from aqt.utils import MenuList, tooltip

from .configWrapper import readConfig
from .miutils import miAsk

def disableAction(action: Union[QAction, QMenu]):
    """
    Disable the action, and setVisible(False)
    """
    if isinstance(action, QMenu):
        action = action.menuAction()
    action.setEnabled(False)
    action.setVisible(False)

def openMigakuAnkiGuide():
    tooltip(_("Loading..."), period=1000)
    with noBundledLibs():
        QDesktopServices.openUrl(QUrl("https://www.migaku.io/coming-soon"))

def onBrowserMenusDidInit(browser: Browser):
    """
    Will be connected to browser_menus_did_init hook.
    
    Disable all the actions we don't want from our config.

    """

    actionChangeDeck = browser.form.actionChange_Deck
    def warnChangeDeck():

        ### Show Warning
        if not miAsk("""
Are you sure you know what you are doing? 
This is usually managed automatically by Migaku, and inexperienced users could end up breaking the Migaku formatting. 
Would you like to continue?"""):
            return

        ### MAKE SURE THIS LINE IS UP TO DATE WITH ANKI
        browser.setDeck()

    actionChangeDeck.disconnect()
    actionChangeDeck.triggered.connect(warnChangeDeck)

    if not mw.migakuGuiSimplification:
        return

    browserConfig = readConfig()['simplifications']["browser"]

    ###################
    ### Remove Actions
    ###################
    menuActions = browserConfig["menuActions"]
    for actionName, keep in dict(
        menuActions["cardsMenu"]
        , **menuActions["notesMenu"]
        ).items():
        if not keep:
            action = getattr(browser.form, actionName)
            disableAction(action)
    
    ###################
    ### Remove Go menu
    ###################
    if not browserConfig["topMenu"]["goMenu"]:
            goMenu: QMenu = browser.form.menuJump
            disableAction(goMenu)

    #########################################################################
    ### Replace Help-> Guide... Link with migaku guide, and add migaku logo.
    #########################################################################
    
    if browserConfig["topMenu"]["migakuGuide"]:
        addon_path = dirname(__file__)
        actionGuide: QAction = browser.form.actionGuide
        actionGuide.setIcon(
            QIcon(
                os.path.join(addon_path, "img", "migaku_200.png")
            )
        )
        actionGuide.disconnect()
        actionGuide.triggered.connect(openMigakuAnkiGuide)


gui_hooks.browser_menus_did_init.append(onBrowserMenusDidInit)

def onBrowserShow(browser: Browser):

    print("simplify_browser.py onBrowserShow called.")

    pass

gui_hooks.browser_will_show.append(onBrowserShow)


#####################################
### WARNING : Monkey patching ahead!
### I'm not proud, but there was no 
### other way.
#####################################
def myOnFilterButton(self):
    ml = MenuList()

    ml.addChild(self._commonFilters())
    ml.addSeparator()

    ml.addChild(self._todayFilters())
    ml.addChild(self._cardStateFilters())
    ml.addChild(self._deckFilters())
    ml.addChild(self._noteTypeFilters())
    ml.addChild(self._tagFilters())
    ml.addSeparator()

    if readConfig()["simplifications"]["browser"]["toggleSidebar"]:
        ml.addChild(self.sidebarDockWidget.toggleViewAction())
        ml.addSeparator()

    ml.addChild(self._savedSearches())

    ml.popupOver(self.form.filter)

Browser.onFilterButton = myOnFilterButton

'''
    Hook(
        name="browser_will_build_tree",
        args=[
            "handled: bool",
            "tree: aqt.browser.SidebarItem",
            "stage: aqt.browser.SidebarStage",
            "browser: aqt.browser.Browser",
        ],
        return_type="bool",
        doc="""Used to add or replace items in the browser sidebar tree
        
        'tree' is the root SidebarItem that all other items are added to.
        
        'stage' is an enum describing the different construction stages of
        the sidebar tree at which you can interject your changes.
        The different values can be inspected by looking at
        aqt.browser.SidebarStage.
        
        If you want Anki to proceed with the construction of the tree stage
        in question after your have performed your changes or additions,
        return the 'handled' boolean unchanged.
        
        On the other hand, if you want to prevent Anki from adding its own
        items at a particular construction stage (e.g. in case your add-on
        implements its own version of that particular stage), return 'True'.
        
        If you return 'True' at SidebarStage.ROOT, the sidebar will not be
        populated by any of the other construction stages. For any other stage
        the tree construction will just continue as usual.
        
        For example, if your code wishes to replace the tag tree, you could do:
        
            def on_browser_will_build_tree(handled, root, stage, browser):
                if stage != SidebarStage.TAGS:
                    # not at tag tree building stage, pass on
                    return handled
                
                # your tag tree construction code
                # root.addChild(...)
                
                # your code handled tag tree construction, no need for Anki
                # or other add-ons to build the tag tree
                return True
        """,
'''

treeStageTitleMap = {
    SidebarStage.ROOT: None,
    # SidebarStage.STANDARD: "Standard",
    SidebarStage.SAVED_SEARCHES: "Saved Filters",
    SidebarStage.DECKS: "Decks",
    SidebarStage.NOTETYPES: "Note Types",
    SidebarStage.TAGS: "Tags",
}

def onBuildTree(handled: bool, tree: SidebarItem, stage: SidebarStage, browser: Browser) -> bool:
    """
    At each stage we will add the Appropriate heading.
    Return False so that the tree keeps building.
    """
    sectionTitle = treeStageTitleMap[stage]
    if sectionTitle:
        tree.addChild(
            SidebarItem(sectionTitle, "", lambda: None)
        )
    
    return False

gui_hooks.browser_will_build_tree.append(onBuildTree)