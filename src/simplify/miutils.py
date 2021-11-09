# -*- coding: utf-8 -*-
# 
from os.path import dirname, join

import aqt
from aqt.qt import *
from aqt.utils import tooltip
from anki.lang import _
from anki.utils import noBundledLibs

addon_path = dirname(__file__)

def miInfo(text, parent=False, level = 'msg', day = True):
    if level == 'wrn':
        title = "Migaku Quickstart Warning"
    elif level == 'not':
        title = "Migaku Quickstart Notice"
    elif level == 'err':
        title = "Migaku Quickstart Error"
    else:
        title = "Migaku Quickstart"
    if parent is False:
        parent = aqt.mw.app.activeWindow() or aqt.mw
    icon = QIcon(join(addon_path, 'img', 'migaku_200.png'))
    mb = QMessageBox(parent)
    if not day:
        mb.setStyleSheet(" QMessageBox {background-color: #272828;}")
    mb.setText(text)
    mb.setWindowIcon(icon)
    mb.setWindowTitle(title)
    b = mb.addButton(QMessageBox.Ok)
    b.setFixedSize(100, 30)
    b.setDefault(True)

    return mb.exec_()


def miAsk(text, parent=None, day=True):

    msg = QMessageBox(parent)
    # msg.setPalette(nightPalette)
    msg.setWindowTitle("Migaku Quickstart")
    msg.setText(text)
    icon = QIcon(join(addon_path, 'img', 'migaku_200.png'))
    # msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    b = msg.addButton(QMessageBox.Yes)
    b.setFixedSize(100, 30)
    b.setDefault(True)
    c = msg.addButton(QMessageBox.No)
    c.setFixedSize(100, 30)
    if not day:
        msg.setStyleSheet(" QMessageBox {background-color: #272828;}")
    msg.setWindowIcon(icon)
    msg.exec_()
    if msg.clickedButton() == b:
        return True
    else:
        return False


def miAsk_no_exec_(text, parent=None, day=True):

    msg = QMessageBox(parent)
    # msg.setPalette(nightPalette)
    msg.setWindowTitle("Migaku Quickstart")
    msg.setText(text)
    icon = QIcon(join(addon_path, 'img', 'migaku_200.png'))
    # msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    b = msg.addButton(QMessageBox.Yes)
    b.setFixedSize(100, 30)
    b.setDefault(True)
    c = msg.addButton(QMessageBox.No)
    c.setFixedSize(100, 30)
    if not day:
        msg.setStyleSheet(" QMessageBox {background-color: #272828;}")
    msg.setWindowIcon(icon)
    return msg

def makeMigakuHelpButton(onHelpFn: Callable[[], None]):
    migakuHelpButton = QPushButton(_("Help"))
    migakuHelpButton.clicked.connect(onHelpFn)
    migakuHelpButton.setIcon(
        QIcon(join(addon_path, "img","migaku_200.png"))
    )
    migakuHelpButton.setAutoDefault(False)
    
    return migakuHelpButton