import aqt
from aqt.qt import *

from .balance_scheduler import BalanceScheduler
from . import util


class BalanceSchedulerDayOffWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Day Off")
        self.setWindowIcon(util.default_icon())

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        lyt.addWidget(
            QLabel(
                "Using the slider below you can set the amout of reviews you want to do today.<br>"
                "Keep it at the left and click OK if you do not want to do any reviews today.<br><br>"
                "Note that this does not affect overdue reviews, only reviews that are due today.<br>"
                "Also only option groups with Migaku Scheduling enabled can be selected.<br>"
                "It can be enabled from <i>Migaku &gt; Settings &gt; Review Scheduling</i><br>"
            )
        )

        self.list = QListWidget()
        lyt.addWidget(self.list)

        for g in aqt.mw.col.decks.all_config():
            item = QListWidgetItem(g["name"])
            if not g.get("scheduling_enabled"):
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                item.setCheckState(Qt.CheckState.Unchecked)
            else:
                item.setCheckState(Qt.CheckState.Checked)
            self.list.addItem(item)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.setValue(0)
        lyt.addWidget(self.slider)

        bbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)

        lyt.addWidget(bbox)

    def accept(self):
        id_ = QDateTime.currentMSecsSinceEpoch()
        today = aqt.mw.col.sched.today
        factor = self.slider.value() / 1000

        vacation = {
            "id": id_,
            "start": today,
            "end": today,
            "factor": factor,
        }

        for i, g in enumerate(aqt.mw.col.decks.all_config()):
            if self.list.item(i).checkState() != Qt.CheckState.Checked:
                continue

            vacs = g.get("scheduling_vacations", [])
            vacs.append(vacation)
            g["scheduling_vacations"] = vacs

            aqt.mw.col.decks.update_config(g)

        bsched = BalanceScheduler(aqt.mw.col)
        bsched.balance_all()

        aqt.mw.reset()

        super().accept()


action = QAction("Day Off", aqt.mw)
action.triggered.connect(lambda: BalanceSchedulerDayOffWindow().exec())
