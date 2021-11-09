"""
Modifying widgets in the deck options UI form
"""

from aqt.utils import openLink
from .miutils import makeMigakuHelpButton
from typing import Any, List, Union
from aqt.qt import QDialogButtonBox, QGridLayout, QLayout, QTabWidget, QVBoxLayout, QWidget, QWidgetItem
from aqt import gui_hooks, mw
from aqt.deckconf import DeckConf

from .configWrapper import readConfig

def removeRowsFromGridLayout(layout: QGridLayout, rows: List[int], delete=True):
    """
    Input QGridLayout, rows is a list of rows to remove.
    It will then iterate through the items of the layout and remove any
    that have rowidx in rows.

    """
    itemsToRemove = []
    for idx in range(layout.count()):
        (row, col, _, _) = layout.getItemPosition(idx)
        print(f"row, col = {(row, col)}")
        if row in rows:
            item: QWidgetItem = layout.itemAt(idx)
            widget: QWidget = item.widget()
            if widget:
                print(f"hiding and deleting... {widget}")
                widget.hide()
                if delete:
                    widget.deleteLater()
            else:
                raise Exception(f"item.widget() returned {type(widget)}, \
                    check that the QGridLayouts items all contain just widgets, and no layouts or any other funny business. ")
            itemsToRemove.append(item)

    for item in itemsToRemove:
        print(f"removing QWidgetItem: {item}")
        layout.removeItem(item)

def findItemInLayout(layout: QLayout, itemName: str, itemType: Union[QLayout, QWidget]) -> Any:
    """
    Given the QLayout and item's objectName, find the item
    and return it.

    The item can be a QWidget or a QLayout. 

    """
    if itemType not in (QLayout, QWidget):
        raise TypeError("itemType should be a QLayout or a QWidget")
    

    for idx in range(layout.count()):
        item = layout.itemAt(idx)
        if hasattr(item, "objectName"):
            if item.objectName() == itemName:
                return item        

    raise Exception(f"Could not find item with itemName {itemName} in layout {layout}")



def setupDeckOptions(deckConf: DeckConf):
    """Self-explanatory"""

    print("setupDeckOptions called.")

    if not mw.migakuGuiSimplification:
        return

    tabWidget:QTabWidget = deckConf.form.tabWidget
    #print(f"tabWidget = {tabWidget}")

    ##################
    ### New cards tab
    ##################
    newCardsTab = tabWidget.findChild(QWidget, "tab")
    #print(f"newCardsTab = {newCardsTab}")
    newCardsVBoxLayout: QVBoxLayout = newCardsTab.layout()
    #print(f"newCardsVBoxLayout = {newCardsVBoxLayout}")
    newCardsGridLayout: QGridLayout = findItemInLayout(newCardsVBoxLayout, "gridLayout", QLayout)
    #print(f"newCardsGridLayout = {newCardsGridLayout}")
    config = readConfig()
    rowmap = (
        (0, "steps")
        , (3, "graduatingInterval")
        , (4, "easyInterval")
        , (5, "startingEase")
        , (6, "buryRelatedNew")
    )
    check = config["simplifications"]["deckConf"]
    rows2remove = [x[0] for x in rowmap if not check[x[1]]]
    #print(rows2remove)
    removeRowsFromGridLayout(newCardsGridLayout, rows2remove)

    ###############
    ### Remove Lapses tab
    ###############
    if not check["lapsesTab"]:
        lapsesTab: QWidget = tabWidget.findChild(QWidget, "tab_2")
        print(lapsesTab)
        tabWidget.removeTab(tabWidget.indexOf(lapsesTab))
        ### Removing the tab doesn't delete the widget
        lapsesTab.deleteLater()    

    ################
    ### Reviews tab
    ################
    reviewsTab: QWidget = tabWidget.findChild(QWidget, "tab_3")
    reviewsVBoxLayout: QVBoxLayout = reviewsTab.layout()
    reviewsGridLayout: QGridLayout = findItemInLayout(reviewsVBoxLayout, "gridLayout_3", QLayout)
    rowmap = (
        (0, "maxReviews")
        , (1, "easyBonus")
        , (2, "intervalModifier")
        , (3, "maxInterval")
        , (5, "buryRelatedReviews")
    )
    # 4 is a hidden row for "hard interval" and stuff
    rows2remove = [x[0] for x in rowmap if not check[x[1]]] + [4]
    removeRowsFromGridLayout(reviewsGridLayout, rows2remove)

    if reviewsGridLayout.count() < 1:
        tabWidget.removeTab(tabWidget.indexOf(reviewsTab))
        reviewsTab.deleteLater()

    

def onHelpRequested():
    openLink("https://www.migaku.io/coming-soon")


def setupHelpButton(deckConf: DeckConf):
    ###########################################
    ### Change help button to migakuHelpButton
    ###########################################

    if not mw.migakuGuiSimplification:
        return

    config = readConfig()
    check = config["simplifications"]["deckConf"]["deckConfMigakuHelpButton"]

    if check:
        buttonBox: QDialogButtonBox = deckConf.form.buttonBox
        helpButton = buttonBox.button(QDialogButtonBox.Help)
        buttonBox.removeButton(helpButton)
        helpButton.deleteLater()

        buttonBox.helpRequested.disconnect()

        migakuHelpButton = makeMigakuHelpButton(onHelpRequested)

        buttonBox.addButton(migakuHelpButton, QDialogButtonBox.HelpRole)

gui_hooks.deck_conf_will_show.append(setupHelpButton)
gui_hooks.deck_conf_did_setup_ui_form.append(setupDeckOptions)