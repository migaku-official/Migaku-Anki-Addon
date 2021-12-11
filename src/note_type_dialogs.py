from typing import Optional
import re

import anki
import aqt
from aqt.qt import *

from . import util
from .languages import Languages
from . import note_type_mgr



class ManageNoteDialog(QDialog):

    INITIAL_SIZE = (670, 400)

    def __init__(self, mw: aqt.AnkiQt, model: anki.models.NotetypeDict, parent: Optional[QDialog] = None):
        QDialog.__init__(self, parent or aqt.mw)

        self.mw = mw
        self.model = model

        self.current_tmpl_idx = -1
        self.current_lang_idx = -1        

        self.qlist = QTableWidget()
        self.alist = QTableWidget()

        self.setWindowTitle('Migaku Options for ' + self.model['name'])
        self.setWindowIcon(util.default_icon())

        lyt = QGridLayout()
        lyt.setColumnStretch(0, 0)
        lyt.setColumnStretch(1, 1)
        self.setLayout(lyt)

        hide_lang_selector = note_type_mgr.nt_was_installed(self.model)
        hide_tmpl_selector = len(self.model['tmpls']) <= 1

        i = 0
        if not hide_lang_selector:
            lyt.addWidget(QLabel('Language'), i, 0, 1, 1)
        self.lang_box = QComboBox()
        self.lang_box.setHidden(hide_lang_selector)
        lyt.addWidget(self.lang_box, i, 1, 1, 1)

        self.lang_box.addItem('None', None)
        for lang in Languages:
            name = lang.name_en
            if lang.name_native and lang.name_native != lang.name_en:
                name += ' - ' + lang.name_native
            self.lang_box.addItem(name, lang.code)

        i += 1
        if not hide_lang_selector:
            lyt.addWidget(QLabel('<hr>'), i, 0, 1, 2)

        i += 1
        if not hide_tmpl_selector:
            lyt.addWidget(QLabel('Card Type'), i, 0, 1, 1)
        self.tmpl_box = QComboBox()
        self.tmpl_box.setHidden(hide_tmpl_selector)
        lyt.addWidget(self.tmpl_box, i, 1, 1, 1)

        for tmpl in self.model['tmpls']:
            self.tmpl_box.addItem(tmpl['name'])

        i += 1
        self.tabs = QTabWidget()
        lyt.addWidget(self.tabs, i, 0, 1, 2)

        self.tabs.addTab(self.qlist, 'Front')
        self.tabs.addTab(self.alist, 'Back')

        self.resize(*self.INITIAL_SIZE)

        # Determine language
        self.current_lang = note_type_mgr.nt_get_lang(self.model)
        if self.current_lang:
            idx = self.lang_box.findData(self.current_lang.code)
        else:
            idx = 0
        self.lang_box.setCurrentIndex(idx)

        self.current_tmpl_idx = 0

        self.tmpl_box.currentIndexChanged.connect(self.on_tmpl_changed)
        self.lang_box.currentIndexChanged.connect(self.on_lang_changed)
        
        self.load_tmpl()


    def closeEvent(self, evt):
        self.save_tmpl()


    def on_tmpl_changed(self, idx):

        self.save_tmpl()
        self.current_tmpl_idx = idx
        self.load_tmpl()


    def on_lang_changed(self, idx):

        self.current_lang = None
        code = self.lang_box.itemData(self.lang_box.currentIndex())
        if code:
            self.current_lang = Languages[code]

        self.load_tmpl()


    def load_tmpl(self):

        for fmt, list_widget in [('qfmt', self.qlist), ('afmt', self.alist)]:
            list_widget.clear()
            list_widget.verticalHeader().hide()
            
            if self.current_lang:
                list_widget.setColumnCount(len(self.current_lang.field_settings) + 1)
                list_widget.setHorizontalHeaderLabels(['Field'] + [f.label for f in self.current_lang.field_settings])
            else:
                list_widget.setColumnCount(1)
                list_widget.setHorizontalHeaderLabels(['Field'])

            list_widget.horizontalHeader().resizeSection(0, 200)

            fields_settings = note_type_mgr.nt_get_tmpl_fields_settings(self.model, self.current_tmpl_idx, fmt, field_names=True)
            list_widget.setRowCount(len(fields_settings))

            for i, (field_name, field_settings) in enumerate(fields_settings):
                
                if self.hide_field(field_name):
                    list_widget.hideRow(i)

                field_name_clean = self.clean_field_name(field_name)

                field_item = QTableWidgetItem(field_name_clean)
                field_item.setFlags(field_item.flags() & ~(Qt.ItemIsEditable | Qt.ItemIsSelectable))

                list_widget.setItem(i, 0, field_item)

                if self.current_lang:
                    for j, f in enumerate(self.current_lang.field_settings):
                        setting_box = QComboBox()
                        setting_box.addItems([f.label for f in f.options])
                        list_widget.setCellWidget(i, j + 1, setting_box)
                        if f.name in field_settings:
                            value = field_settings[f.name]
                            for k, o in enumerate(f.options):
                                if o.value == value:
                                    setting_box.setCurrentIndex(k)
                                    break


    def save_tmpl(self):

        tmpl_idx = self.current_tmpl_idx
        if tmpl_idx < 0:
            return

        for fmt, list_widget in [('qfmt', self.qlist), ('afmt', self.alist)]:

            fields_settings = []

            for rid in range(list_widget.rowCount()):
                field_settings = {}

                if self.current_lang:
                    field_active = False

                    for i in range(len(self.current_lang.field_settings)):
                        setting_box = list_widget.cellWidget(rid, i + 1)
                        if setting_box.currentIndex() > 0:
                            field_active = True
                            break

                    if field_active:
                        for i, s in enumerate(self.current_lang.field_settings):
                            setting_box = list_widget.cellWidget(rid, i + 1)
                            field_settings[s.name] = s.options[setting_box.currentIndex()].value

                fields_settings.append(field_settings)

            note_type_mgr.nt_set_tmpl_lang(self.model, self.current_lang, tmpl_idx, fmt, fields_settings, commit=False)

        note_type_mgr.nt_set_css_lang(self.model, self.current_lang, commit=True)


    def clean_field_name(self, field_name):
        idx = field_name.rfind(':')
        if idx > 0:
            field_name = field_name[idx+1:]
        return field_name


    def hide_field(self, field_name):
        # Some already get parsed out via regex, better safe than sorry

        field_name_lower = field_name.lower()

        # Conditionals
        if len(field_name) >= 1 and field_name[0] in "#/^":
            return True

        # Reserved field names
        if field_name in ['FrontSide', 'Tags']:
            return True

        # audio fields
        if 'audio' in field_name_lower:
            return True

        # image fields
        if 'image' in field_name_lower:
            return True

        # Conditional fields
        if field_name_lower.startswith('is '):
            return True

        return False


class AddNoteDialog(QDialog):

    def __init__(self, mw: aqt.AnkiQt, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Add Migaku Note Type')
        self.setWindowIcon(util.default_icon())

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        self.list = QListWidget()
        lyt.addWidget(self.list)

        for lang in Languages:
            is_installed = note_type_mgr.is_installed(lang)
            item_label = lang.name_en
            if is_installed:
                item_label += ' (Already added)'
            item = QListWidgetItem(item_label)
            if is_installed:
                item.setFlags(item.flags() & ~(Qt.ItemIsSelectable | Qt.ItemIsEnabled))
            item.setData(Qt.UserRole, lang.code)
            self.list.addItem(item)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        lyt.addWidget(button_box)

    def accept(self):
        selected_items = self.list.selectedItems()
        selected_item = selected_items[0] if len(selected_items) == 1 else None
        if not selected_item:
            QMessageBox.information(self, 'Error', 'Please select a language for which you want to add the Migaku card type.')
            return

        code = selected_item.data(Qt.UserRole)
        lang = Languages[code]

        note_type_mgr.install(lang)

        super().accept()



def on_manage_migaku(notes_editor: aqt.models.Models):
    dlg = ManageNoteDialog(notes_editor.mw, notes_editor.current_notetype(), parent=notes_editor)
    dlg.exec_()

def on_add_migaku(notes_editor: aqt.models.Models):
    dlg = AddNoteDialog(notes_editor.mw, parent=notes_editor)
    r = dlg.exec_()
    if r == QDialog.Accepted:
        notes_editor.refresh_list()


def setup_note_editor(buttons, notes_editor: aqt.models.Models):
    buttons.append(
        ('Migaku Options', lambda: on_manage_migaku(notes_editor))
    )
    buttons.append(
        ('Add Migaku\nNote Type', lambda: on_add_migaku(notes_editor))
    )
    return buttons


aqt.gui_hooks.models_did_init_buttons.append(setup_note_editor)
