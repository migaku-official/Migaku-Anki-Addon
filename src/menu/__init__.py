import aqt
from aqt.qt import *
from ..config import set

from . import (
    settings_window,
    ease_reset,
    retirement,
    balance_scheduler,
    dayoff_window,
    vacation_window,
)

menu = QMenu("Migaku", aqt.mw)

titleItem = QAction("No Migaku browser extension found...", aqt.mw)
titleItem.triggered.connect(lambda: aqt.mw.onAddCard())
titleItem.setEnabled(False)

deckItem = QAction("", aqt.mw)
deckItem.triggered.connect(lambda: aqt.mw.onAddCard())

typeItem = QAction("", aqt.mw)
typeItem.triggered.connect(lambda: aqt.mw.onAddCard())


def setup_menu():
    menu.addAction(settings_window.action)

    menu.addSeparator()
    menu.addAction(ease_reset.action)
    menu.addAction(retirement.action)
    menu.addAction(balance_scheduler.action)
    menu.addAction(vacation_window.action)
    menu.addAction(dayoff_window.action)

    menu.addSeparator()
    menu.addAction(titleItem)
    menu.addAction(deckItem)
    menu.addAction(typeItem)

    aqt.mw.form.menubar.insertMenu(aqt.mw.form.menuHelp.menuAction(), menu)


def deactivate_deck_type():
    titleItem.setText(f"Add Migaku cards to:")


def activate_deck_type():
    titleItem.setText(f"No Migaku browser extension found...")


def set_deck_name(name, id):
    set("migakuDeckId", id)
    deckItem.setText(f"Deck: {name}")


def set_type_name(name, id):
    set("migakuNotetypeId", id)
    typeItem.setText(f"Type: {name}")
