import aqt
from aqt.qt import *

from . import config


def reset_ease(sync=True, force_sync=True):
    factor = int(config.get('maintain_ease_factor', 2.5) * 1000)
    aqt.mw.col.db.execute('update cards set factor = ?', factor)

    if sync or force_sync:
        if force_sync:
            aqt.mw.col.set_schema_modified()
        if aqt.mw.pm.sync_auth():
            aqt.mw.on_sync_button_clicked()


action = QAction('Reset Card Ease', aqt.mw)
action.triggered.connect(lambda: reset_ease())
