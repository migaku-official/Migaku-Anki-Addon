"""
TODO:
A lot of simplifications can be made here (pun not intended)

For example the .findChild() calls probably aren't necessary. 
We can get the objects directly from the mw I think, 
 with something like mw.form.actionDocumentation, or something
 like that.

"""

import os

from random import choice

import aqt
from aqt import mw
from aqt import gui_hooks
from aqt.utils import openLink, tooltip
from aqt.qt import *
from anki.hooks import wrap
from anki.utils import noBundledLibs
from anki.lang import _

from .configWrapper import OurConfig, readConfig, writeConfig

from .miutils import miAsk, miInfo, miAsk_no_exec_

addon_path = os.path.dirname(__file__)

warningMessages = [
    "Something doesn't feel right..."
    , "Halt! Who goes there?"
    , "Danger Ahead!"
    , "Holy fate-worse-than-death"
]

# define this from config
config = readConfig()
mw.migakuGuiSimplification = config["toggle_gui_simplification"]

def setupMigakuMenu():
    "Sets up the migaku menu, adding our button and keeping all the other buttons that should be there"
    addMenu = False
    if not hasattr(mw, 'MigakuMainMenu'):
        mw.MigakuMainMenu = QMenu('Migaku',  mw)
        addMenu = True
    if not hasattr(mw, 'MigakuMenuSettings'):
        mw.MigakuMenuSettings = []
    if not hasattr(mw, 'MigakuMenuActions'):
        mw.MigakuMenuActions = []


    toggle = QAction("Toggle GUI Simplification", mw)
    toggle.triggered.connect(toggleGuiSimplification)
    mw.MigakuMenuActions.append(toggle)


    mw.MigakuMainMenu.clear()
    for act in mw.MigakuMenuSettings:
        mw.MigakuMainMenu.addAction(act)
    mw.MigakuMainMenu.addSeparator()
    for act in mw.MigakuMenuActions:
        if isinstance(act, QAction):
            mw.MigakuMainMenu.addAction(act)
        elif isinstance(act, QMenu):
            mw.MigakuMainMenu.addMenu(act)

    if addMenu:
        mw.form.menubar.insertMenu(mw.form.menuHelp.menuAction(), mw.MigakuMainMenu)  

def findAction(menu, actionName: str):
    """
    We can't use findChild on menu, because it all interacts weirdly,
    so we can iterate the menu.actions() and find the child with the 
    objectName given.

    """
    if not isinstance(menu, QMenu):
        raise TypeError("menu is not of type QMenu")
    for action in menu.actions():
        if action.objectName() == actionName:
            return action
        

def setActionInMenuEnabled(menu, actionName: str, enabled=True):
    """
    Given a QMenu and the object name of an action in that menu, 
    hide and disable the action from the menu.

    NB: menu can't have type hint because the type hinting is weird about it.
    """
    print(f"removeActionFromMenu called. menu={menu}, actionName = {actionName}")
    if not isinstance(menu, QMenu):
        raise TypeError("menu is not of type QMenu")

    action = findAction(menu, actionName)
    #menu.removeAction(actionStudyDeck) # type:ignore
    action.setEnabled(enabled)
    action.setVisible(enabled)


def simplifyToolsMenu(toolsMenu: QMenu, config: OurConfig):
    """
    Make our changes to the main window's "Tools" Menu
    """
    ###############
    ### Tools Menu
    ###############
    
    for key, val in config["simplifications"]["tools"].items():
        #print(key,val)
        setActionInMenuEnabled(toolsMenu, key, enabled=val)

    ################################################################
    ### Show warning when click Manage Note Types
    ### Potential cause for BUGS here, the warnNoteTypes function
    ### needs to keep up to date with anki.
    ################################################################
    actionNoteTypes = mw.findChild(QAction, "actionNoteTypes")


    actionNoteTypes.disconnect()
    actionNoteTypes.triggered.connect(warnNoteTypes)
    
def warnNoteTypes():
    config = readConfig()
    warningMsg = """
<p style="align: justify">This is usually managed automatically by Migaku, and inexperienced users could end up breaking any Migaku formatting.</p> 
<br><hr><br><span style="align:center"><b>Would you like to continue?</b></span><br>"""
    msgBox = miAsk_no_exec_(
        "<h3 style=\" align: center \">"+choice(warningMessages)+"</h3>"
        )
    msgBox.setInformativeText(warningMsg)
    dontShowAgainCheckBox = QCheckBox("Don't show this again")
    msgBox.setCheckBox(dontShowAgainCheckBox)

    result = QMessageBox.Yes
    if config["warnNoteTypes"]:
        ### Show Warning
        result = msgBox.exec_()
    
    ### save dontshowagain
    if dontShowAgainCheckBox.isChecked():
        config["warnNoteTypes"] = False
        writeConfig(config)

    if result == QMessageBox.Yes:
        ### MAKE SURE THIS LINE IS UP TO DATE WITH ANKI
        mw.onNoteTypes()


def setupToolsMenu(menubar: QMenuBar, config: OurConfig, simplify:bool):
    toolsMenu = menubar.findChild(QMenu, "menuTools")
    simplifyToolsMenu(toolsMenu, config)


def openMigakuAnkiGuide():
    openLink("https://www.migaku.io/tools-guides/anki/guide")

def setupHelpMenu():
    """
    Rename "Guide..." to "Anki Guide..."
    Add a "Migaku Anki Guide..." which links to migaku anki guide on website
    """

    helpMenu: QMenu = mw.form.menubar.findChild(QMenu, "menuHelp")
    actionDocumentation = findAction(helpMenu, "actionDocumentation")
    actionDocumentation.setText("Anki Guide...")


    ### Add Migaku Anki Guide... to HelpMenu
    
    actionMigakuAnkiGuide = QAction(helpMenu)
    actionMigakuAnkiGuide.setText("Migaku Anki Guide...")
    actionMigakuAnkiGuide.setIcon(
        QIcon(
            os.path.join(addon_path, "img", "migaku_200.png")
        )
    )
    actionMigakuAnkiGuide.setObjectName("actionMigakuAnkiGuide")
    ### This didn't work unfortunately:
    helpMenu.setStyleSheet("""
        QMenu::item[objectName="actionMigakuAnkiGuide"] {
            border-radius: 50px;
            box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.1);
        }
        """)
    actionMigakuAnkiGuide.triggered.connect(openMigakuAnkiGuide)
    helpMenu.insertAction(helpMenu.actions()[0], actionMigakuAnkiGuide)

mw.migakuSimplifiedRanOnce = False
def runSimplification():
    
    config: OurConfig = readConfig()
    menubar: QMenuBar = mw.form.menubar
    setupToolsMenu(menubar, config, mw.migakuGuiSimplification)
    if not mw.migakuSimplifiedRanOnce:
        setupHelpMenu()

    mw.migakuSimplifiedRanOnce = True


def toggleGuiSimplification():
    """self-explanatory"""

    mw.migakuGuiSimplification = mw.migakuGuiSimplification != True
    ### Save to config
    config = readConfig()
    config["toggle_gui_simplification"] = mw.migakuGuiSimplification
    writeConfig(config)
    runSimplification()
    msg = "enabled" if mw.migakuGuiSimplification else "disabled"
    miInfo(f"Gui Simplification {msg}")


gui_hooks.profile_did_open.append(runSimplification)
