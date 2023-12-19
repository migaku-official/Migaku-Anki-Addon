import aqt
from aqt.qt import *
from ..editor.current_editor import get_add_cards
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
titleItem.setEnabled(False)

typeItem = QAction("", aqt.mw)


def notetypeTrigger():
    aqt.mw.onAddCard()
    addcards = get_add_cards()["addcards"]
    addcards.show_notetype_selector()


typeItem.triggered.connect(notetypeTrigger)


deckItem = QAction("", aqt.mw)


def deckTrigger():
    aqt.mw.onAddCard()
    addcards = get_add_cards()["addcards"]
    addcards.deck_chooser.choose_deck()


deckItem.triggered.connect(deckTrigger)


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
    menu.addAction(typeItem)
    menu.addAction(deckItem)

    aqt.mw.form.menubar.insertMenu(aqt.mw.form.menuHelp.menuAction(), menu)


def deactivate_deck_type():
    titleItem.setText(f"No Migaku browser extension found...")


def activate_deck_type():
    titleItem.setText(f"Add Migaku cards to:")


def set_type_name(name, id):
    set("migakuNotetypeId", id, do_write=True)
    typeItem.setText(f"Type: {name}")


def set_deck_name(name, id):
    set("migakuDeckId", id, do_write=True)
    deckItem.setText(f"Deck: {name}")
