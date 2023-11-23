import aqt
from aqt.qt import *

from .languages import Language
from . import config
from . import note_type_mgr
from . import util
from .migaku_connection import ConnectionStatusLabel


class AddRemoveSyntaxDialog(QDialog):
    BATCH_SIZE = 100

    INITIAL_SIZE = (430, 370)

    class RemoveThread(QThread):
        finished = pyqtSignal()
        progress = pyqtSignal(int)

        def __init__(self, lang: Language, note_ids, field_names, parent=None):
            super().__init__(parent)
            self.lang = lang
            self.note_ids = note_ids
            self.field_names = field_names

        def run(self):
            for i, note_id in enumerate(self.note_ids):
                note = aqt.mw.col.get_note(note_id)
                if note:
                    for field_name in self.field_names:
                        text = self.lang.remove_syntax(note[field_name])
                        note[field_name] = text
                    note.flush()
                if i % AddRemoveSyntaxDialog.BATCH_SIZE == 0:
                    self.progress.emit(i)
            self.finished.emit()

    def __init__(self, lang: Language, is_remove: bool, note_ids, parent=None):
        super().__init__(parent)
        self.lang = lang
        self.is_remove = is_remove
        self.note_ids = note_ids
        self.note_count = len(self.note_ids)
        self.progress_string = (
            "Removing" if is_remove else "Adding"
        ) + f" {lang.name_en} Language Syntax"

        self.checked_fields = set()
        self.current_idx = 0
        self.current_batch_notes = []

        window_title = (
            f"Remove {lang.name_en} Language Syntax"
            if is_remove
            else f"Add {lang.name_en} Language Syntax"
        )
        self.setWindowTitle(window_title)
        self.setWindowIcon(util.default_icon())

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        text = (
            f"Fields to remove {lang.name_en} syntax from:"
            if is_remove
            else f"Fields to add {lang.name_en} syntax to:"
        )
        lyt.addWidget(QLabel(text))

        self.field_list = QListWidget()
        last_checked = config.get("syntax_fields_last_checked", {})
        for field_name in aqt.mw.col.field_names_for_note_ids(note_ids):
            itm = QListWidgetItem(field_name)
            itm.setCheckState(
                Qt.CheckState.Checked
                if (field_name in last_checked and last_checked[field_name])
                else Qt.CheckState.Unchecked
            )
            self.field_list.addItem(itm)
        lyt.addWidget(self.field_list)

        if not self.is_remove:
            lyt.addWidget(ConnectionStatusLabel())

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.start)
        button_box.rejected.connect(self.reject)
        lyt.addWidget(button_box)

        self.resize(*self.INITIAL_SIZE)

    def accept(self):
        self.update_last_checked_config()
        aqt.mw.reset()
        super().accept()

    def update_last_checked_config(self):
        checked_fields_states = {}
        for i in range(self.field_list.count()):
            itm = self.field_list.item(i)
            field_name = itm.data(Qt.ItemDataRole.DisplayRole)
            field_checked = itm.checkState() == Qt.CheckState.Checked
            checked_fields_states[field_name] = field_checked

        last_checked = config.get("syntax_fields_last_checked", {})
        last_checked.update(checked_fields_states)
        config.set("syntax_fields_last_checked", last_checked, do_write=True)

    def start(self):
        self.checked_fields = set()
        for i in range(self.field_list.count()):
            itm = self.field_list.item(i)
            field_name = itm.data(Qt.ItemDataRole.DisplayRole)
            field_checked = itm.checkState() == Qt.CheckState.Checked
            if field_checked:
                self.checked_fields.add(field_name)

        aqt.mw.progress.start(
            min=0, max=self.note_count, label=self.progress_string, parent=self
        )

        if self.is_remove:
            self.remove_thread = self.RemoveThread(
                self.lang, self.note_ids, self.checked_fields
            )
            self.remove_thread.finished.connect(self.on_finished)
            self.remove_thread.progress.connect(self.on_progress)
            self.remove_thread.start()

        else:
            self.current_idx = 0
            self.request_next_batch()

    def on_progress(self, progress):
        aqt.mw.progress.update(
            value=progress,
            max=self.note_count,
            label=self.progress_string + f"\n({progress}/{self.note_count})",
        )

    def on_finished(self):
        aqt.mw.progress.finish()
        self.accept()

    def request_next_batch(self):
        current_batch = self.note_ids[
            self.current_idx : self.current_idx + self.BATCH_SIZE
        ]

        batch = []
        self.current_batch_notes = []

        for note_id in current_batch:
            note = aqt.mw.col.get_note(note_id)
            if note:
                self.current_batch_notes.append(note)
                batch.append(
                    {
                        field: self.lang.remove_syntax(note[field])
                        for field in self.checked_fields
                    }
                )

        aqt.mw.migaku_connection.request_syntax(
            batch,
            self.lang.code,
            on_done=self.on_batch_delivery,
            on_error=self.on_batch_error,
            callback_on_main_thread=True,
            timeout=10,
        )

    def on_batch_delivery(self, batch):
        current_batch_size = len(self.current_batch_notes)

        assert len(batch) == current_batch_size

        for note, note_data in zip(self.current_batch_notes, batch):
            for field_name, field_text in note_data.items():
                note[field_name] = field_text
                note.flush()

        self.current_idx += current_batch_size

        if self.current_idx < self.note_count:
            self.on_progress(self.current_idx)
            self.request_next_batch()
        else:
            self.on_finished()

    def on_batch_error(self, msg):
        aqt.mw.progress.clear()
        util.show_critical(msg)

    @classmethod
    def show_modal(cls, note_ids, is_remove, parent=None):
        if note_ids is None or len(note_ids) < 1:
            return

        try:
            note_type_id = aqt.mw.col.models.get_single_notetype_of_notes(note_ids)
        except Exception as e:
            util.show_warning("Please select notes from a single note type.")
            return

        note_type = aqt.mw.col.models.get(note_type_id)
        lang = note_type_mgr.nt_get_lang(note_type)

        if not lang:
            note_type_name = note_type["name"]
            util.show_warning(
                "Please select notes that have an associated language.<br><br>"
                f'If you want to set the language for to the "{note_type_name}" note type go to Tools > Manage Note Types > Migaku Options.'
            )
            return

        dlg = cls(lang, is_remove, note_ids, parent)
        return dlg.exec()
