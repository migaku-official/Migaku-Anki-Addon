import os

import aqt
from aqt.qt import *

addon_dir = os.path.dirname(__file__)
user_files_dir = os.path.join(addon_dir, 'user_files')
addon_web_base = F'/_addons/{__name__.split(".")[0]}'


def addon_path(*path_parts):
    return os.path.join(addon_dir, *path_parts)


def user_path(*path_parts):
    return os.path.join(user_files_dir, *path_parts)


def col_media_path(*path_parts):
    return os.path.join(aqt.mw.col.media.dir(), *path_parts)


def tmp_path(*path_parts):
    return addon_path('tmp', *path_parts)


def addon_web_uri(*path_parts):
    return addon_web_base + '/' + '/'.join(path_parts)


def make_pixmap(*path_parts):
    path = addon_path('img', *path_parts)
    return QPixmap(path)


def make_icon(*path_parts):
    path = addon_path('img', *path_parts)
    return QIcon(path)


def default_icon():
    return make_icon('migaku_200.png')


def open_browser(text: str):
    browser = aqt.dialogs.open('Browser', aqt.mw)

    browser.form.searchEdit.lineEdit().setText(text)
    browser.onSearchActivated()
    # For newer Anki versions:
    #   aqt.dialogs.open('Browser', aqt.mw, search=(text,))

    raise_window(browser)


def raise_window(window: QWidget):
    window.setWindowState( (window.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)
    window.raise_()
    window.activateWindow()
