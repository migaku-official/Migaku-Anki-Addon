# insert librairies into sys.path
import anki
import os
import sys


def add_sys_path(*path_parts):
    sys.path.insert(
        0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib", *path_parts)
    )


def init_sys_libs():
    add_sys_path("shared")
    if anki.utils.is_lin:
        add_sys_path("linux")
    elif (
        anki.utils.is_mac
        and sys.version_info.major >= 3
        and sys.version_info.minor >= 13
    ):
        print("---- Using macOS 13.0+ libraries")
        add_sys_path("macos_313")
        print(sys.path)
    elif (
        anki.utils.is_mac
        and sys.version_info.major >= 3
        and sys.version_info.minor >= 11
    ):
        add_sys_path("macos_311")
    elif (
        anki.utils.is_mac
        and sys.version_info.major >= 3
        and sys.version_info.minor >= 10
    ):
        add_sys_path("macos_310")
    elif anki.utils.is_mac:
        add_sys_path("macos_39")
    elif anki.utils.is_win:
        add_sys_path("windows")
