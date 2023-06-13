import aqt
from aqt.qt import *

from aqt.operations import CollectionOp

from . import util
from . import config


class CardTypeChangeDialog(QDialog):
    def __init__(self, note_ids, parent=None):
        super().__init__(parent)

        self.note_ids = note_ids
        self.is_vocabulary_card_val = ""
        self.is_audio_card_val = ""
        self.checkpoint_id = None

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        self.setWindowTitle("Change Card Type")
        self.setWindowIcon(util.default_icon())

        lyt.addWidget(QLabel("Select the type to convert the selected cards to:"))

        self.selector_box = QComboBox()
        self.selector_box.addItems(
            [
                "Sentence",
                "Vocabulary",
                "Audio Sentence",
                "Audio Vocabulary",
            ]
        )
        lyt.addWidget(self.selector_box)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.start)
        button_box.rejected.connect(self.reject)
        lyt.addWidget(button_box)

    def start(self):
        note_type = self.selector_box.currentIndex()
        is_vocabulary_card = note_type in [1, 3]
        is_audio_card = note_type in [2, 3]

        self.is_vocabulary_card_val = "x" if is_vocabulary_card else ""
        self.is_audio_card_val = "x" if is_audio_card else ""

        target_type_name = self.selector_box.currentText()

        checkpoint_name = f"Change Card Type To {target_type_name}"
        self.checkpoint_id = aqt.mw.col.add_custom_undo_entry(checkpoint_name)

        CollectionOp(self, self.run).success(self.on_done).run_in_background()

    def run(self, col):
        update_notes = []
        tag = config.get("card_type_tag", "")
        for note_id in self.note_ids:
            note = col.get_note(note_id)
            if note:
                if "Is Vocabulary Card" in note:
                    note["Is Vocabulary Card"] = self.is_vocabulary_card_val
                if "Is Audio Card" in note:
                    note["Is Audio Card"] = self.is_audio_card_val
                if tag:
                    note.add_tag(tag)
                update_notes.append(note)
        return col.update_notes(update_notes)

    def on_done(self, _result):
        if not self.checkpoint_id is None:
            aqt.mw.col.merge_undo_entries(self.checkpoint_id)

        self.accept()

    @classmethod
    def show_modal(cls, note_ids, parent=None):
        if note_ids is None or len(note_ids) < 1:
            return

        dlg = cls(note_ids, parent)
        return dlg.exec()
