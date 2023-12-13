import os
import re
import json
from typing import List

import aqt
import anki
from aqt.editor import Editor

from ..config import get, set
from ..languages import Language
from ..note_type_mgr import nt_get_lang
from ..util import addon_path, show_critical
from ..migaku_fields import get_migaku_fields


def editor_get_lang(editor: Editor):
    if editor.note:
        nt = editor.note.note_type()
        if nt:
            return nt_get_lang(nt)
    return None


def editor_generate_syntax(editor: Editor):
    if editor.currentField is None or editor.note is None:
        return

    lang = editor_get_lang(editor)
    if lang is None:
        return

    if not aqt.mw.migaku_connection.is_connected():
        show_critical("Anki is not connected to the Browser Extension.")
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
            on_error=lambda msg: show_critical(msg, parent=editor.parentWindow),
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


def toggle_migaku_mode(editor: Editor):
    data = get_migaku_fields(editor.note.note_type())
    editor.web.eval(f"MigakuEditor.toggleMode({json.dumps(data)});")


def setup_editor_buttons(buttons: List[str], editor: Editor):
    added_buttons = [
        editor.addButton(
            label="Migaku Mode",
            icon=None,
            id="migaku_btn_toggle_mode",
            cmd="migaku_toggle_mode",
            toggleable=True,
            disables=False,
            func=toggle_migaku_mode,
        ),
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


def editor_get_js_by_lang(lang: Language):
    add_icon_path = lang.web_uri("icons", "generate.svg")
    remove_icon_path = lang.web_uri("icons", "remove.svg")
    no_icon_invert = os.path.exists(lang.file_path("icons", "no_invert"))
    img_filter = "invert(0)" if no_icon_invert else ""

    return f"MigakuEditor.initButtons('{add_icon_path}', '{remove_icon_path}', '{img_filter}');"


def editor_did_load_note(editor: Editor):
    lang = editor_get_lang(editor)
    js = "MigakuEditor.hideButtons();" if lang is None else editor_get_js_by_lang(lang)

    editor.web.eval(js)


def on_migaku_bridge_cmds(self: Editor, cmd: str, _old):
    if cmd.startswith("migakuSelectChange"):
        (_, migaku_type, field_name) = cmd.split(":", 2)
        migakuFields = get("migakuFields", {})

        set(
            "migakuFields",
            {
                **migakuFields,
                self.note.mid: {
                    **(
                        migakuFields[self.note.mid]
                        if self.note.mid in migakuFields
                        else {}
                    ),
                    field_name: migaku_type,
                },
            },
            do_write=True,
        )
    else:
        _old(self, cmd)


def editor_did_init(editor: Editor):
    with open(addon_path("editor/editor.js"), "r", encoding="utf-8") as editor_file:
        editor.web.eval(editor_file.read())


def reset_migaku_mode(editor: Editor):
    editor.web.eval(f"MigakuEditor.resetMigakuEditor();")
