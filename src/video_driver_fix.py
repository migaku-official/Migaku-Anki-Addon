from anki.utils import isWin
import aqt
from aqt.profiles import VideoDriver


def fix_video_driver():
    # This is a bad idea :pensive:
    return

    if isWin:
        driver = VideoDriver.Software
        aqt.mw.pm.set_video_driver(driver)
        # aqt.mw.pm.save() not required, set_video_driver directly writes to a file

fix_video_driver()
