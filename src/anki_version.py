from anki.buildinfo import version
from aqt.qt import *
from .util import show_msg_box
from . import config
from enum import Enum

# This can be used when older versions continue to be supported
recommended_version_lower_tuple = (2, 1, 49)
# Current recommended version
recommended_version_tuple = (2, 1, 65)

recommended_version = ".".join(str(x) for x in recommended_version_tuple)
recommended_version_lower = ".".join(str(x) for x in recommended_version_lower_tuple)

# We only want to include major and minor here, not patch version
# We do not really care about the patch version
# We trust that Anki will not break anything in a patch version *fingers crossed*
new_recommended_version_tuple = (25, 7)
new_recommended_version = ".".join(str(x).zfill(2) for x in new_recommended_version_tuple)


class VersionState(Enum):
    OK = 0
    LOWER = 1
    HIGHER = 2
    UNKNOWN = 3


def get_state() -> VersionState:
    try:
        version_tuple = tuple(int(x) for x in version.split("."))
    except ValueError:
        return VersionState.UNKNOWN

    major, minor, *rest = version_tuple

    if major <= 2:
        # Old versioning scheme
        # Major, minor, patch are all breaking
        if version_tuple < recommended_version_lower_tuple:
            return VersionState.LOWER

        if version_tuple > recommended_version_tuple:
            return VersionState.HIGHER
    else:
        # New versioning scheme
        # Only major and minor are breaking
        new_version_tuple = (major, minor)

        if new_version_tuple < new_recommended_version_tuple:
            return VersionState.LOWER

        if new_version_tuple > new_recommended_version_tuple:
            return VersionState.HIGHER

    return VersionState.OK


def check_anki_version_dialog():
    ignore_version_check = config.get("ignore_version_check", {})
    if version in ignore_version_check:
        return

    state = get_state()

    if state == VersionState.OK:
        return

    result = QMessageBox.StandardButton.No

    if state == VersionState.UNKNOWN:
        result = show_msg_box(
            "Could not determine your Anki version. The Migaku addon may not work correctly.\n\n"
            + f"Version {recommended_version} is recommended.\n\n"
            + "Do you want to hide this message in the future?",
            buttons=(QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes),
        )

    elif state == VersionState.LOWER:
        result = show_msg_box(
            f"Your Anki version {version} is older than the currently recommended version for the Migaku addons ({new_recommended_version}).\n\n"
            + "The Migaku addon may not work correctly.\n\n"
            + "Do you want to hide this message in the future for this Anki version?",
            buttons=(QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes),
        )

    elif state == VersionState.HIGHER:
        result = show_msg_box(
            f"Your Anki version {version} is newer than the currently recommended version for the Migaku addons ({new_recommended_version}).\n\n"
            + "The Migaku addon may not work correctly.\n\n"
            + "Do you want to hide this message in the future for this Anki version?",
            buttons=(QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes),
        )

    if result == QMessageBox.StandardButton.Yes:
        ignore_version_check[version] = True
        config.set("ignore_version_check", ignore_version_check, True)
