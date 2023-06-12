import os
from typing import List
import json

import aqt
from aqt.editor import Editor

from . import note_type_mgr
from . import util
from .util import addon_path


def editor_get_lang(editor: Editor):
    if editor.note:
        nt = editor.note.note_type()
        if nt:
            return note_type_mgr.nt_get_lang(nt)
    return None


def editor_generate_syntax(editor: Editor):
    if editor.currentField is None or editor.note is None:
        return

    lang = editor_get_lang(editor)
    if lang is None:
        return

    if not aqt.mw.migaku_connection.is_connected():
        util.show_critical("Anki is not connected to the Browser Extension.")
        return

    note_id = editor.note.id
    note_id_key = str(note_id)

    def do_edit():
        note = editor.note
        field_idx = editor.currentField

        if not note or field_idx is None:
            return

        text = note.fields[field_idx]
        text = lang.remove_syntax(text)

        def handle_syntax(syntax_data):
            if isinstance(syntax_data, list) and len(syntax_data) == 1:
                new_text = syntax_data[0].get(note_id_key)
                if new_text:
                    note.fields[field_idx] = new_text
                    editor.loadNoteKeepingFocus()

        aqt.mw.migaku_connection.request_syntax(
            [{note_id_key: text}],
            lang.code,
            on_done=handle_syntax,
            on_error=lambda msg: util.show_critical(msg, parent=editor.parentWindow),
            callback_on_main_thread=True,
            timeout=10,
        )

    editor.call_after_note_saved(callback=do_edit, keepFocus=True)


def editor_remove_syntax(editor: Editor):
    if editor.currentField is None or editor.note is None:
        return

    lang = editor_get_lang(editor)
    if lang is None:
        return

    def do_edit():
        note = editor.note
        field_idx = editor.currentField

        if not note or field_idx is None:
            return

        text = note.fields[field_idx]
        text = lang.remove_syntax(text)

        note.fields[field_idx] = text
        editor.loadNoteKeepingFocus()

    editor.call_after_note_saved(callback=do_edit, keepFocus=True)


def setup_editor_buttons(buttons: List[str], editor: Editor):
    added_buttons = [
        editor.addButton(
            icon="tmp",
            id="migaku_btn_syntax_generate",
            cmd="migaku_syntax_generate",
            func=editor_generate_syntax,
            tip="Generate syntax (F2)",
            keys="F2",
        ),
        editor.addButton(
            icon="tmp",
            id="migaku_btn_syntax_remove",
            cmd="migaku_syntax_remove",
            func=editor_remove_syntax,
            tip="Remove syntax (F4)",
            keys="F4",
        ),
    ]

    buttons[0:0] = added_buttons
    return buttons


aqt.gui_hooks.editor_did_init_buttons.append(setup_editor_buttons)


def editor_note_changed(editor: Editor):
    lang = editor_get_lang(editor)
    if lang is None:
        js = """
            document.getElementById('migaku_btn_syntax_generate').style.display = 'none';
            document.getElementById('migaku_btn_syntax_remove').style.display = 'none';
        """
    else:
        add_icon_path = lang.web_uri("icons", "generate.svg")
        remove_icon_path = lang.web_uri("icons", "remove.svg")
        no_icon_invert = os.path.exists(lang.file_path("icons", "no_invert"))
        img_filter = "invert(0)" if no_icon_invert else ""

        js = f"""
            document.querySelector('#migaku_btn_syntax_generate img').src = '{add_icon_path}';
            document.querySelector('#migaku_btn_syntax_generate img').style.filter = '{img_filter}';
            document.querySelector('#migaku_btn_syntax_remove img').src = '{remove_icon_path}';
            document.querySelector('#migaku_btn_syntax_remove img').style.filter = '{img_filter}';
            document.getElementById('migaku_btn_syntax_generate').style.display = '';
            document.getElementById('migaku_btn_syntax_remove').style.display = '';
        """
    editor.web.eval(js)


aqt.gui_hooks.editor_did_load_note.append(editor_note_changed)
