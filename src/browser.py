import aqt
from aqt.qt import *
from aqt.browser import Browser

from .langauges import Language
from . import config
from . import note_type_mgr
from . import util
from .migaku_connection import ConnectionStatusLabel


class AddSyntaxDialog(QDialog):

    BATCH_SIZE = 100

    def __init__(self, lang: Language, note_ids, parent=None):
        super().__init__(parent)
        self.lang = lang
        self.note_ids = note_ids

        self.checked_fields = set()
        self.current_idx = 0
        self.current_batch_notes = []

        self.setWindowTitle(F'Add {lang.name_en} language syntax')
        self.setWindowIcon(util.default_icon())

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        lyt.addWidget(QLabel('Fields to add syntax to:'))

        self.field_list = QListWidget()
        last_checked = config.get('syntax_fields_last_checked', {})
        for field_name in aqt.mw.col.field_names_for_note_ids(note_ids):
            itm = QListWidgetItem(field_name)
            itm.setCheckState(
                Qt.Checked if (field_name in last_checked and last_checked[field_name]) else Qt.Unchecked
            )
            self.field_list.addItem(itm)
        lyt.addWidget(self.field_list)

        lyt.addWidget(ConnectionStatusLabel())

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.start_adding)
        button_box.rejected.connect(self.reject)
        lyt.addWidget(button_box)


    def accept(self):
        self.update_last_checked_config()
        super().accept()


    def update_last_checked_config(self):
        checked_fields_states = {}
        for i in range(self.field_list.count()):
            itm = self.field_list.item(i)
            field_name = itm.data(Qt.DisplayRole)
            field_checked = itm.checkState() == Qt.Checked
            checked_fields_states[field_name] = field_checked
        
        last_checked = config.get('syntax_fields_last_checked', {})
        last_checked.update(checked_fields_states)
        config.set('syntax_fields_last_checked', last_checked, do_write=True)


    def start_adding(self):
        self.checked_fields = set()
        for i in range(self.field_list.count()):
            itm = self.field_list.item(i)
            field_name = itm.data(Qt.DisplayRole)
            field_checked = itm.checkState() == Qt.Checked
            if field_checked:
                self.checked_fields.add(field_name)
        
        self.current_idx = 0
        aqt.mw.progress.start(min=0, max=len(self.note_ids), label='Adding Language Syntax', parent=self)
        self.request_next_batch()

    
    def request_next_batch(self):
        current_batch = self.note_ids[self.current_idx:self.current_idx + self.BATCH_SIZE]
        
        batch = []
        self.current_batch_notes = []
        
        for note_id in current_batch:
            note = aqt.mw.col.get_note(note_id)
            if note:
                self.current_batch_notes.append(note)
                batch.append({
                    field: self.lang.remove_syntax(note[field])
                        for field in self.checked_fields
                })

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

        if self.current_idx < len(self.note_ids):
            aqt.mw.progress.update(value=self.current_idx)
            self.request_next_batch()
        else:
            aqt.mw.progress.finish()
            self.accept()

    def on_batch_error(self, msg):
        aqt.mw.progress.clear()
        util.show_critical(msg)


    @classmethod
    def show_modal(cls, note_ids, parent=None):

        if note_ids is None or len(note_ids) < 1:
            return

        try:
            note_type_id = aqt.mw.col.models.get_single_notetype_of_notes(note_ids)
        except Exception as e:
            util.show_warning('Please select notes from a single note type.')
            return
        
        note_type = aqt.mw.col.models.get(note_type_id)
        lang = note_type_mgr.nt_get_lang(note_type)

        if not lang:
            note_type_name = note_type['name']
            util.show_warning('Please select notes that have an associated language.<br><br>'
                             F'If you want to set the language for to the "{note_type_name}" note type go to Tools > Manage Note Types > Migaku Options.')
            return

        dlg = cls(lang, note_ids, parent)
        return dlg.exec_()



def setup_browser_menu(browser: Browser):
    browser.form.menuEdit.addSeparator()

    create_cards_action = QAction('Add language syntax to cards', browser)
    create_cards_action.triggered.connect(
        lambda: AddSyntaxDialog.show_modal(browser.selectedNotes(), browser)
    )
    browser.form.menuEdit.addAction(create_cards_action)


aqt.gui_hooks.browser_menus_did_init.append(setup_browser_menu)
