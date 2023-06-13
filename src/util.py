import os
import shutil
from typing import Optional, List

import aqt
from aqt.qt import *

addon_dir = os.path.dirname(__file__)
user_files_dir = os.path.join(addon_dir, "user_files")
addon_web_base = f'/_addons/{__name__.split(".")[0]}'


def addon_path(*path_parts):
    return os.path.join(addon_dir, *path_parts)


def user_path(*path_parts):
    return os.path.join(user_files_dir, *path_parts)


# assure that user_files exists
os.makedirs(user_path(), exist_ok=True)


def col_media_path(*path_parts):
    return os.path.join(aqt.mw.col.media.dir(), *path_parts)


def tmp_path(*path_parts):
    return addon_path("tmp", *path_parts)


# assure that tmp folder exists and is empty
shutil.rmtree(tmp_path(), ignore_errors=True)
os.makedirs(tmp_path(), exist_ok=True)


def addon_web_uri(*path_parts):
    return addon_web_base + "/" + "/".join(path_parts)


def make_pixmap(*path_parts):
    path = addon_path("img", *path_parts)
    return QPixmap(path)


def make_icon(*path_parts):
    path = addon_path("img", *path_parts)
    return QIcon(path)


def default_icon():
    return make_icon("migaku_200.png")


def show_info(
    text: str, title: str = "Migaku", parent: Optional[QWidget] = None
) -> int:
    return show_msg_box(text, title, parent, QMessageBox.Icon.Information)


def show_warning(
    text: str, title: str = "Migaku", parent: Optional[QWidget] = None
) -> int:
    return show_msg_box(text, title, parent, QMessageBox.Icon.Warning)


def show_critical(
    text: str, title: str = "Migaku", parent: Optional[QWidget] = None
) -> int:
    return show_msg_box(text, title, parent, QMessageBox.Icon.Critical)


def show_question(
    text: str, title: str = "Migaku", parent: Optional[QWidget] = None
) -> int:
    return show_msg_box(
        text, title, parent, QMessageBox.Question, QMessageBox.Yes | QMessageBox.No
    )


def show_msg_box(
    text: str,
    title: str = "Migaku",
    parent: Optional[QWidget] = None,
    icon: QMessageBox.Icon = QMessageBox.Icon.NoIcon,
    buttons: Optional[List[QMessageBox.StandardButton]] = None,
) -> int:
    if parent is None:
        parent = aqt.mw.app.activeWindow() or aqt.mw

    mb = QMessageBox(parent)
    mb.setText(text)
    mb.setIcon(icon)
    mb.setWindowTitle(title)
    mb.setWindowIcon(default_icon())

    if buttons:
        default = None
        for btn in buttons:
            mb_btn = mb.addButton(btn)
            if not default:
                default = mb_btn
        mb.setDefaultButton(default)
    else:
        mb_btn = mb.addButton(QMessageBox.StandardButton.Ok)
        mb_btn.setDefault(True)

    return mb.exec()


def open_browser(text: str):
    browser = aqt.dialogs.open("Browser", aqt.mw)

    browser.form.searchEdit.lineEdit().setText(text)
    browser.onSearchActivated()
    # For newer Anki versions:
    #   aqt.dialogs.open('Browser', aqt.mw, search=(text,))

    raise_window(browser)


def raise_window(window: QWidget):
    window.setWindowState(
        (window.windowState() & ~Qt.WindowState.WindowMinimized)
        | Qt.WindowState.WindowActive
    )
    window.raise_()
    window.activateWindow()
