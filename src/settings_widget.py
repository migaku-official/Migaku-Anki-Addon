import aqt
from aqt.qt import *
from . import util


class SettingsWidget(QWidget):
    class WizardPage(QWizardPage):
        def __init__(self, widget_cls, parent=None, is_tutorial=True):
            super().__init__(parent)
            self.widget = widget_cls(is_tutorial=is_tutorial)
            if self.widget.TITLE:
                self.setTitle(self.widget.TITLE)
            if self.widget.SUBTITLE:
                self.setSubTitle(self.widget.SUBTITLE)
            if self.widget.PIXMAP:
                if hasattr(QWizard, "WizardPixmap"):
                    QWizard_WatermarkPixmap = QWizard.WizardPixmap.WatermarkPixmap
                else:
                    QWizard_WatermarkPixmap = QWizard.WatermarkPixmap
                self.setPixmap(
                    QWizard_WatermarkPixmap, util.make_pixmap(self.widget.PIXMAP)
                )
            self.lyt = QVBoxLayout()
            self.lyt.setContentsMargins(0, 0, 0, 0)
            self.lyt.addWidget(self.widget)
            self.setLayout(self.lyt)

        def save(self):
            self.widget.save()

    TITLE = None
    SUBTITLE = None
    PIXMAP = None
    BOTTOM_STRETCH = True

    def __init__(self, parent=None, is_tutorial=False):
        super().__init__(parent)

        self.is_tutorial = is_tutorial

        self.lyt = QVBoxLayout()
        self.setLayout(self.lyt)
        self.init_ui()
        self.toggle_advanced(False)
        if self.BOTTOM_STRETCH:
            self.lyt.addStretch()

    def init_ui(self) -> None:
        pass

    def toggle_advanced(self, state: bool) -> None:
        pass

    def save(self) -> None:
        pass

    @classmethod
    def wizard_page(cls, parent=None, is_tutorial=True) -> WizardPage:
        return cls.WizardPage(cls, parent, is_tutorial)

    @classmethod
    def make_label(cls, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        lbl.linkActivated.connect(aqt.utils.openLink)
        return lbl

    def add_label(self, text: str) -> QLabel:
        lbl = self.make_label(text)
        self.lyt.addWidget(lbl)
        return lbl
