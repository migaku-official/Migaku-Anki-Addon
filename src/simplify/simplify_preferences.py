

from anki.hooks import wrap
from aqt.main import AnkiQt
from aqt.qt import *
from aqt import mw
from aqt.preferences import Preferences

from .configWrapper import readConfig
from .simplify_deckconf import removeRowsFromGridLayout


def myinit(self: Preferences, mw: AnkiQt):
    """
    This will be ran after aqt.preferences.Preferences.__init__

    The keys in config.simplifications.preferences are the objectNames
    of the items in the form. Therefore we access those items and delete them.

    The one exception is learnAheadLimit. This is not the name of an object,
    because it relates to a row of a QGridLayout, therefore we need to treat it
    differently. (IE with removeRowsFromGridLayout).

    """

    if not mw.migakuGuiSimplification:
        return

    

    check = readConfig()['simplifications']["preferences"]
    for key in check:
        if key not in ["learnAheadLimit", "renameNetwork"]:
            attr = getattr(self.form, key, None)
            if attr:
                attr.hide()
            else:
                print(f"Could not get attribute {key} from self.form {self.form}")

    if not check["learnAheadLimit"]:
        bottomGridLayout: QGridLayout  = self.form.gridLayout_4
        removeRowsFromGridLayout(bottomGridLayout, [1], delete=False)


    if check["renameNetwork"]:
        tabWidget: QTabWidget = self.form.tabWidget
        networkTab: QWidget = self.form.tab_2
        tabWidget.setTabText(tabWidget.indexOf(networkTab), "Syncing")

Preferences.__init__ = wrap(Preferences.__init__, myinit)