import os
from typing import List

import aqt
from aqt.editor import Editor

from .langauges import Languages, Language
from . import note_type_mgr
from .util import addon_path


def editor_get_lang(editor: Editor):
    if editor.note:
        nt = editor.note.note_type()
        if nt:
            return note_type_mgr.nt_get_lang(nt)
    return None


editor_js = open(addon_path('editor.js'), 'r', encoding='utf-8').read()


def editor_generate_syntax(editor: Editor):
    if editor.currentField is None or editor.note is None:
        return

    lang = editor_get_lang(editor)
    if lang is None:
        return

    note_id = editor.note.id

    def handle_text(text):
        if text is None:
            return

        
        def handle_syntax(syntax_data):
            print(syntax_data)
            return

            text = lang.add_syntax(text, syntax)
            editor.web.eval(editor_js + F'\nset_text("{text}");')


        print('requesting...')
        aqt.mw.migaku_connection.request_syntax(
            [{ note_id: text }],
            lang.code,
            on_done = handle_syntax,
        )

        # print(F'STUB PARSE - lang: {lang.code}, text: {text}')
        #text += '-PARSED-STUB'

        #text = text.replace('"', '\\"')
        # editor.web.eval(editor_js + F'\nset_text("{text}");')
    
    editor.web.evalWithCallback(editor_js + '\nfetch_text();', handle_text)



def editor_remove_syntax(editor: Editor):
    if editor.currentField is None or editor.note is None:
        return
    
    lang = editor_get_lang(editor)
    if lang is None:
        return

    def handle_text(text):
        if text is None:
            return

        text = lang.remove_syntax(text)
        editor.web.eval(editor_js + F'\nset_text("{text}");')

    editor.web.evalWithCallback(editor_js + '\nfetch_text();', handle_text)


def setup_editor_buttons(buttons: List[str], editor: Editor):
    added_buttons = [
        editor.addButton(
            icon='tmp',
            id='migaku_btn_syntax_generate',
            cmd='migaku_syntax_generate',
            func=editor_generate_syntax,
            tip='Generate syntax (F2)',
            keys='F2',
        ),
        editor.addButton(
            icon='tmp',
            id='migaku_btn_syntax_remove',
            cmd='migaku_syntax_remove',
            func=editor_remove_syntax,
            tip='Remove syntax (F4)',
            keys='F4',
        )
    ]

    buttons[0:0] = added_buttons
    return buttons

aqt.gui_hooks.editor_did_init_buttons.append(setup_editor_buttons)


def editor_note_changed(editor: Editor):
    lang = editor_get_lang(editor)
    if lang is None:
        js = '''
            $('#migaku_btn_syntax_generate').hide();
            $('#migaku_btn_syntax_remove').hide();
        '''
    else:
        add_icon_path = lang.web_uri('icons', 'generate.svg')
        remove_icon_path = lang.web_uri('icons', 'remove.svg')
        no_icon_invert = os.path.exists(lang.file_path('icons', 'no_invert'))
        img_filter = 'invert(0)' if no_icon_invert else ''

        js = F'''
            $('#migaku_btn_syntax_generate img').attr('src', '{add_icon_path}');
            $('#migaku_btn_syntax_generate img').css('filter', '{img_filter}');
            $('#migaku_btn_syntax_remove img').attr('src', '{remove_icon_path}');
            $('#migaku_btn_syntax_remove img').css('filter', '{img_filter}');
            $('#migaku_btn_syntax_generate').show();
            $('#migaku_btn_syntax_remove').show();
        '''
    editor.web.eval(js)

aqt.gui_hooks.editor_did_load_note.append(editor_note_changed)
