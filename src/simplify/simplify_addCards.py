from os.path import dirname, join

from anki.lang import _
from anki.utils import noBundledLibs
from anki.hooks import wrap
from aqt import gui_hooks, mw
from aqt.qt import *
from aqt.webview import WebContent
from aqt.editor import Editor
from aqt.addcards import AddCards
from aqt.utils import openLink, tooltip

from .configWrapper import readConfig
from .miutils import makeMigakuHelpButton

def onHelpRequested(*args):
    openLink("https://www.migaku.io/tools-guides/anki/guide/#adding-your-own-cards")

def onAddCardsDidInit(addCards: AddCards):

    print("simplify_addCards.py onAddCardsDidInit called.")


    addon_path = dirname(__file__)

    ####################################################
    ### Replace the help button to direct to migaku help
    ####################################################
    if mw.migakuGuiSimplification and readConfig()["simplifications"]["addWindow"]["addWindowMigakuHelpButton"]:
        addCards.helpButton.deleteLater()
        migakuHelpButton = makeMigakuHelpButton(onHelpRequested)

        bb: QDialogButtonBox = addCards.form.buttonBox
        bb.removeButton(addCards.helpButton)
        bb.addButton(migakuHelpButton, QDialogButtonBox.HelpRole)

gui_hooks.add_cards_did_init.append(onAddCardsDidInit)

#AddCards.helpRequested = wrap(AddCards.helpRequested, onHelpRequested)