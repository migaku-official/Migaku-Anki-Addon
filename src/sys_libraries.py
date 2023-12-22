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
    if anki.utils.isLin:
        add_sys_path("linux")
    elif anki.utils.isMac and sys.version_info.major >= 3 and sys.version_info.minor >= 11:
        add_sys_path("macos_311")
    elif anki.utils.isMac and sys.version_info.major >= 3 and sys.version_info.minor >= 10:
        add_sys_path("macos_310")
    elif anki.utils.isMac and sys.version_info.major >= 3 and sys.version_info.minor >= 9:
        add_sys_path("macos_39")
    elif anki.utils.isMac:
        add_sys_path("macos_38")
    elif anki.utils.isWin:
        add_sys_path("windows")
