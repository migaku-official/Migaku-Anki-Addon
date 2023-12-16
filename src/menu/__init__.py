import aqt
from aqt.qt import *

from . import (
    settings_window,
    ease_reset,
    retirement,
    balance_scheduler,
    dayoff_window,
    vacation_window,
)


def setup_menu():
    menu = QMenu("Migaku", aqt.mw)
    menu.addAction(settings_window.action)

    menu.addSeparator()
    menu.addAction(ease_reset.action)
    menu.addAction(retirement.action)
    menu.addAction(balance_scheduler.action)
    menu.addAction(vacation_window.action)
    menu.addAction(dayoff_window.action)

    menu.addSeparator()

    aqt.mw.form.menubar.insertMenu(aqt.mw.form.menuHelp.menuAction(), menu)
