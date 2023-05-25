from anki.buildinfo import version
from aqt.qt import *
from .util import show_msg_box
from . import config
from enum import Enum


# Current recommended version
recommended_version_tuple = (2, 1, 64)

# This can be used when older versions continue to be supported
recommended_version_lower_tuple = (2, 1, 49)

recommended_version = '.'.join(str(x) for x in recommended_version_tuple)
recommended_version_lower = '.'.join(str(x) for x in recommended_version_lower_tuple)


class VersionState(Enum):
    OK = 0
    LOWER = 1
    HIGHER = 2
    UNKNOWN = 3


def get_state() -> VersionState:
    try:
        version_tuple = tuple(int(x) for x in version.split('.'))
    except ValueError:
        return VersionState.UNKNOWN

    if version_tuple < recommended_version_lower_tuple:
        return VersionState.LOWER

    if version_tuple > recommended_version_tuple:
        return VersionState.HIGHER

    return VersionState.OK


def check_anki_version_dialog():
    ignore_version_check = config.get('ignore_version_check', {})
    if version in ignore_version_check:
        return

    state = get_state()

    if state == VersionState.OK:
        return

    result = QMessageBox.No

    if state == VersionState.UNKNOWN:
        result = show_msg_box(
            'Could not determine your Anki version. The Migaku addon may not work correctly.\n\n' +
            F'Version {recommended_version} is recommended.\n\n' +
            'Do you want to hide this message in the future?',
            buttons=(QMessageBox.No, QMessageBox.Yes)
        )

    elif state == VersionState.LOWER:
        result = show_msg_box(
            F'Your Anki version {version} is older than the currently recommended version for the Migaku addons ({recommended_version}).\n\n' +
            'The Migaku addon may not work correctly.\n\n' +
            'Do you want to hide this message in the future for this Anki version?',
            buttons=(QMessageBox.No, QMessageBox.Yes)
        )

    elif state == VersionState.HIGHER:
        result = show_msg_box(
            F'Your Anki version {version} is newer than the currently recommended version for the Migaku addons ({recommended_version}).\n\n' +
            'The Migaku addon may not work correctly.\n\n' +
            'Do you want to hide this message in the future for this Anki version?',
            buttons=(QMessageBox.No, QMessageBox.Yes)
        )

    if result == QMessageBox.Yes:
        ignore_version_check[version] = True
        config.set('ignore_version_check', ignore_version_check, True)
