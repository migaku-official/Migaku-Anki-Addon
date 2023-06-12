import re

from anki.notes import NotetypeDict
import aqt
from aqt.operations import CollectionOp
from aqt.qt import *
from aqt.utils import tooltip

from .languages import Language
from . import config
from . import note_type_mgr
from . import util
from .migaku_connection import ConnectionStatusLabel


bracket_regex = re.compile(r"\[[^\[]+?\]")
html_regex = re.compile(r"<[^<]+?>")


def field_words(text):
    text = text.replace(" ", " ")
    text = text.replace("&ensp", " ")
    text = text.replace("\u2002", " ")
    text = text.replace(",", " ")
    text = text.replace("、", " ")

    text = text.strip()
    text = bracket_regex.sub("", text)
    text = html_regex.sub("", text)

    return text.split()


class DefinitionAddDialog(QDialog):
    BATCH_SIZE = 15

    def __init__(self, lang: Language, note_type: NotetypeDict, note_ids, parent=None):
        super().__init__(parent)
        self.lang = lang
        self.note_ids = note_ids

        note_type_fields = [fld["name"] for fld in note_type["flds"]]

        self.current_idx = 0
        self.delivered_batch = []
        self.current_batch_notes = []
        self.note_count = len(self.note_ids)
        self.checkpoint_id = None

        self.progress_string = f"Adding {lang.name_en} Definitions"

        self.setWindowTitle(f"Add {lang.name_en} Definitions")
        self.setWindowIcon(util.default_icon())

        self.config = config.get("definition_adding", {})
        if not "mapping" in self.config:
            self.config["mapping"] = {}

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        top_lyt = QGridLayout()
        lyt.addLayout(top_lyt)

        i = 0
        top_lyt.addWidget(QLabel("Searched Field:"), i, 0)
        self.search_field_box = QComboBox()
        self.search_field_box.addItems(note_type_fields)
        field = self.config.get("search_field", "Target Word")
        if field in note_type_fields:
            self.search_field_box.setCurrentText(field)
        top_lyt.addWidget(self.search_field_box, i, 1)

        i += 1
        top_lyt.addWidget(QLabel("Insert Mode:"), i, 0)
        self.insert_mode_box = QComboBox()
        self.insert_mode_box.addItems(["Append", "Overwrite", "If Empty"])
        self.insert_mode_box.setCurrentIndex(self.config.get("mode", 0))
        top_lyt.addWidget(self.insert_mode_box, i, 1)

        lyt.addWidget(QLabel("<hr>"))

        mapping_lyt = QGridLayout()
        lyt.addLayout(mapping_lyt)

        i = 0
        mapping_lyt.addWidget(QLabel("Definition Type:"), i, 0)
        mapping_lyt.addWidget(QLabel("Output Field:"), i, 1)

        i += 1
        mapping_lyt.addWidget(QLabel("Text Definitions:"), i, 0)
        self.out_box_text = QComboBox()
        self.out_box_text.addItems(note_type_fields)
        field = self.config["mapping"].get("text", "Definitions")
        if field in note_type_fields:
            self.out_box_text.setCurrentText(field)
        mapping_lyt.addWidget(self.out_box_text, i, 1)

        i += 1
        mapping_lyt.addWidget(QLabel("Example Sentences:"), i, 0)
        self.out_box_example_sentences = QComboBox()
        self.out_box_example_sentences.addItems(note_type_fields)
        field = self.config["mapping"].get("example_sentences", "Example Sentences")
        if field in note_type_fields:
            self.out_box_example_sentences.setCurrentText(field)
        mapping_lyt.addWidget(self.out_box_example_sentences, i, 1)

        i += 1
        mapping_lyt.addWidget(QLabel("Word Audio:"), i, 0)
        self.out_box_word_audio = QComboBox()
        self.out_box_word_audio.addItems(note_type_fields)
        field = self.config["mapping"].get("word_audio", "Word Audio")
        if field in note_type_fields:
            self.out_box_word_audio.setCurrentText(field)
        mapping_lyt.addWidget(self.out_box_word_audio, i, 1)

        i += 1
        mapping_lyt.addWidget(QLabel("Images:"), i, 0)
        self.out_box_images = QComboBox()
        self.out_box_images.addItems(note_type_fields)
        field = self.config["mapping"].get("images", "Images")
        if field in note_type_fields:
            self.out_box_images.setCurrentText(field)
        mapping_lyt.addWidget(self.out_box_images, i, 1)

        lyt.addWidget(QLabel("<hr>"))

        lbl = QLabel(
            '<b>Note:</b> The dictionaries that are searched can be configured in the "Automatic definition settings" at the bottom of the card creator of the Migaku dictionary.'
        )
        lbl.setWordWrap(True)
        lyt.addWidget(lbl)

        lyt.addWidget(ConnectionStatusLabel())

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.start)
        button_box.rejected.connect(self.reject)
        lyt.addWidget(button_box)

    def start(self):
        aqt.mw.progress.start(
            min=0, max=self.note_count, label=self.progress_string, parent=self
        )

        self.config["search_field"] = self.search_field_box.currentText()
        self.config["mode"] = self.insert_mode_box.currentIndex()
        self.config["mapping"]["text"] = self.out_box_text.currentText()
        self.config["mapping"][
            "example_sentences"
        ] = self.out_box_example_sentences.currentText()
        self.config["mapping"]["word_audio"] = self.out_box_word_audio.currentText()
        self.config["mapping"]["images"] = self.out_box_images.currentText()

        self.checkpoint_id = aqt.mw.col.add_custom_undo_entry(
            f"Added {self.lang.name_en} Definitions"
        )
        self.current_idx = 0
        self.request_next_batch()

    def request_next_batch(self):
        current_batch = self.note_ids[
            self.current_idx : self.current_idx + self.BATCH_SIZE
        ]

        batch = {}
        self.current_batch_notes = []

        for note_id in current_batch:
            note = aqt.mw.col.get_note(note_id)
            if note:
                self.current_batch_notes.append(note)
                batch[str(note_id)] = field_words(note[self.config["search_field"]])

        aqt.mw.migaku_connection.request_definitions(
            batch,
            self.lang.code,
            on_done=self.on_batch_delivery,
            on_error=self.on_batch_error,
            callback_on_main_thread=True,
            timeout=60,
        )

    def on_batch_delivery(self, batch):
        self.delivered_batch = batch
        CollectionOp(self, self.handle_batch_delivery_data).success(
            self.on_batch_notes_flushed
        ).run_in_background()

    def handle_batch_delivery_data(self, col):
        batch = self.delivered_batch
        current_batch_size = len(self.current_batch_notes)

        assert len(batch) == current_batch_size

        mode = self.config["mode"]

        for note in self.current_batch_notes:
            note_id_str = str(note.id)
            if note_id_str in batch:
                for key, mapping in [
                    ("definitions", "text"),
                    ("googleImages", "images"),
                    ("forvo", "word_audio"),
                    ("tatoeba", "example_sentences"),
                ]:
                    field = self.config["mapping"][mapping]
                    def_text = batch[note_id_str][key]

                    if def_text:
                        # Append
                        if mode == 0:
                            if not note[field].strip():
                                note[field] = batch[note_id_str][key]
                            else:
                                note[field] += "<br><br>" + batch[note_id_str][key]
                        # Overwrite
                        elif mode == 1:
                            note[field] = batch[note_id_str][key]
                        # If Empty
                        elif mode == 2:
                            if not note[field].strip():
                                note[field] = batch[note_id_str][key]

        self.current_idx += current_batch_size
        return col.update_notes(self.current_batch_notes)

    def on_batch_notes_flushed(self, _result):
        if self.current_idx < self.note_count:
            self.on_progress(self.current_idx)
            self.request_next_batch()
        else:
            self.on_finished()

    def on_batch_error(self, msg):
        self.finalize_checkpoint()
        aqt.mw.progress.clear()
        util.show_critical(msg)

    def on_progress(self, progress):
        aqt.mw.progress.update(
            value=progress,
            max=self.note_count,
            label=self.progress_string + f"\n({progress}/{self.note_count})",
        )

    def on_finished(self):
        self.finalize_checkpoint()
        aqt.mw.progress.finish()
        config.set("definition_adding", self.config, do_write=True)
        tooltip("Successfully generated definitions", parent=self.parent())
        self.accept()

    def finalize_checkpoint(self):
        if not self.checkpoint_id is None:
            aqt.mw.col.merge_undo_entries(self.checkpoint_id)
        self.checkpoint_id = None

    @classmethod
    def show_modal(cls, note_ids, parent=None):
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
                f'If you want to set the language for the "{note_type_name}" note type go to Tools > Manage Note Types > Migaku Options.'
            )
            return

        dlg = cls(lang, note_type, note_ids, parent)
        return dlg.exec_()
