import aqt
from aqt.qt import *

from . import util
from . import config
from .settings_widgets import SETTINGS_WIDGETS


class SettingsWindow(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Settings/Help - Migaku Anki')
        self.setWindowIcon(util.default_icon())

        lyt = QHBoxLayout()
        self.setLayout(lyt)

        self.stack = QStackedWidget()
        self.stack_selector = QListWidget()
        self.stack_selector.setMaximumWidth(225)
        self.stack_selector.currentRowChanged.connect(self.stack.setCurrentIndex)

        lyt.addWidget(self.stack_selector)
        lyt.addWidget(self.stack)

        self.widgets = []
        for wcls in SETTINGS_WIDGETS:
            w = wcls()
            self.widgets.append(w)
            self.stack_selector.addItem(w.TITLE)
            self.stack.addWidget(w)

    def closeEvent(self, _evt):
        self.accept()

    def accept(self):
        for w in self.widgets:
            w.save()
        super().accept()

    @classmethod
    def show_modal(cls):
        window = cls()
        window.exec_()


action = QAction('Settings/Help', aqt.mw)
action.triggered.connect(SettingsWindow.show_modal)
