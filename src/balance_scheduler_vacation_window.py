from collections import defaultdict

import aqt
from aqt.qt import *

from .balance_scheduler import BalanceScheduler, balance_all


class BalanceSchedulerVacationWindow(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        bsched = BalanceScheduler(aqt.mw.col)
        start_ms = bsched.col_start_ms()
        self.col_date = QDateTime.fromMSecsSinceEpoch(start_ms).date()

        groups = aqt.mw.col.decks.all_config()
        self.group_names = [c['name'] for c in groups]

        self.setWindowTitle('Vacation Manager')
        self.setWindowModality(Qt.ApplicationModal)

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        lbl = QLabel(
            'To add a vacation, click the "Add" button at the bottom.<br>'
            'After that select the start and end date of your vacation. The dates are inclusive.<br>'
            'In the groups dropdown you can select to which option groups the vacation should be applied.<br>'
            'The slider at the right allows you to adjust the amount of reviews you want to do during the vacation '
            'ranging from 0% (left) to 100% (right) the amount you would have usually.<br>'
            '<br>'
            'Note that only option groups for which Migaku Scheduling is enabled are affected by vacations.<br>'
            'To enable Migaku Scheduling for a group, go to <i>Migaku &gt; Settings &gt; Review Scheduling</i>'
        )
        lbl.setWordWrap(True)
        lyt.addWidget(lbl)

        self.list = QTableWidget()
        self.list.setColumnCount(5)
        self.list.setHorizontalHeaderLabels(['Start', 'End', 'Groups', 'Review Amount', ''])
        for i in range(4):
            self.list.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        self.list.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.list.horizontalHeader().resizeSection(4, 25)
        self.list.verticalHeader().setVisible(False)
        lyt.addWidget(self.list)

        btn_lyt = QHBoxLayout()
        lyt.addLayout(btn_lyt)
        btn_lyt.addStretch()

        btn_add = QPushButton('Add')
        btn_add.clicked.connect(lambda: self.add())
        btn_lyt.addWidget(btn_add)

        btn_ok = QPushButton('OK')
        btn_ok.clicked.connect(self.accept)
        btn_lyt.addWidget(btn_ok)

        self.del_buttons = []

        self.resize(700, 475)
        self.reload()

    def accept(self):
        self.save()
        super().accept()

    def add(self, start=None, end=None, groups_enabled=None, factor=None):
        if start is None:
            start = aqt.mw.col.sched.today
        start = self.col_day_to_date(start)

        if end is None:
            end = aqt.mw.col.sched.today
        end = self.col_day_to_date(end)

        if groups_enabled is None:
            groups_enabled = [True] * len(self.group_names)

        if factor is None:
            factor = 0.0

        row = self.list.rowCount()
        self.list.setRowCount(row + 1)

        start_widget = QDateEdit()
        start_widget.setCalendarPopup(True)
        start_widget.setDate(start)
        self.list.setCellWidget(row, 0, start_widget)

        end_widget = QDateEdit()
        end_widget.setCalendarPopup(True)
        end_widget.setDate(end)
        self.list.setCellWidget(row, 1, end_widget)

        group_tool_btn = QToolButton()
        group_tool_btn.setText('Change')
        group_tool_btn.setPopupMode(QToolButton.InstantPopup)

        group_menu = QMenu()
        group_tool_btn.setMenu(group_menu)

        for name, enabled in zip(self.group_names, groups_enabled):
            action = QWidgetAction(group_menu)
            box = QCheckBox(name, group_menu)
            box.setChecked(enabled)
            action.setDefaultWidget(box)
            group_menu.addAction(action)

        self.list.setCellWidget(row, 2, group_tool_btn)

        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 1000)
        slider.setValue(round(factor * 1000))
        self.list.setCellWidget(row, 3, slider)

        btn_del = QPushButton('✖')
        btn_del.clicked.connect(self.remove)
        self.del_buttons.append(btn_del)
        self.list.setCellWidget(row, 4, btn_del)

    def remove(self):
        del_btn = self.sender()
        row = self.del_buttons.index(del_btn)
        if row < 0:
            return
        self.list.removeRow(row)
        del self.del_buttons[row]

    def reload(self):
        self.del_buttons = []
        self.list.setRowCount(0)

        vacations_start = {}
        vacations_end = {}
        vacations_factor = {}
        vacations_groups = defaultdict(list)

        for i, g in enumerate(aqt.mw.col.decks.all_config()):
            for v in g.get('scheduling_vacations', []):
                id_ = v['id']
                vacations_start[id_] = v['start']
                vacations_end[id_] = v['end']
                vacations_factor[id_] = v['factor']
                vacations_groups[id_].append(i)

        for id_ in sorted(vacations_start.keys()):
            groups_enabled = [False] * len(self.group_names)

            for i in vacations_groups[id_]:
                groups_enabled[i] = True

            start = vacations_start[id_]
            end = vacations_end[id_]

            if end < start:
                continue

            if end < aqt.mw.col.sched.today:
                continue

            self.add(
                start,
                end,
                groups_enabled,
                vacations_factor[id_],
            )

    def save(self):
        groups = aqt.mw.col.decks.all_config()

        for g in groups:
            g['scheduling_vacations'] = []

        for row in range(self.list.rowCount()):
            start = self.date_to_col_day(
                self.list.cellWidget(row, 0).date()
            )
            end = self.date_to_col_day(
                self.list.cellWidget(row, 1).date()
            )

            if end < start:
                continue

            id_ = QDateTime.currentMSecsSinceEpoch() + row

            groups_enabled = []
            menu = self.list.cellWidget(row, 2).menu()
            for i, action in enumerate(menu.actions()):
                box = action.defaultWidget()
                groups_enabled.append(box.isChecked())

            factor = self.list.cellWidget(row, 3).value() / 1000.0

            for i in range(len(groups)):
                g = groups[i]
                if not groups_enabled[i]:
                    continue
                g['scheduling_vacations'].append({
                    'id': id_,
                    'start': start,
                    'end': end,
                    'factor': factor,
                })

        for g in groups:
            aqt.mw.col.decks.update_config(g)

        balance_all()

    def col_day_to_date(self, day):
        return self.col_date.addDays(max(0, day))

    def date_to_col_day(self, date):
        return max(0, date.toJulianDay() - self.col_date.toJulianDay())


action = QAction('Manage Vacations', aqt.mw)
action.triggered.connect(lambda: BalanceSchedulerVacationWindow().exec_())
