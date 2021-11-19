import re
from typing import List, Dict, Optional

import aqt
from anki.models import NotetypeDict

from .languages import Languages, Language


NOTE_TYPE_PREFIX = 'Migaku '
NOTE_TYPE_MARK_CSS = '/* Managed Migaku Note Type */'
NOTE_TYPE_MARK_CSS_COMMENT = '/* Remove the line above to disable automatic note type updating */'

FIELD_RE = re.compile(r'<div class=\"field\" (.*?)>{{(?!#|/|\^|FrontSide|Tags)(.*?)}}</div>|{{(?!#|/|\^|FrontSide|Tags)(.*?)}}')
SETTINGS_RE = re.compile(r'data-(.*?)=\"(.*?)\"')
FORMAT_RE = re.compile(r'<!--###MIGAKU (.*?) SUPPORT JS START###.*?SUPPORT JS END###-->', re.DOTALL)
STYLE_RE = re.compile(r'/\*###MIGAKU (.*?) SUPPORT CSS START###.*?SUPPORT CSS END###\*/', re.DOTALL)


def is_installed(lang: Language) -> bool:
    nt_mgr = aqt.mw.col.models
    nt = nt_mgr.by_name(NOTE_TYPE_PREFIX + lang.name_en)

    if nt is None:
        return False

    return nt['css'].startswith(NOTE_TYPE_MARK_CSS)
    

def install(lang: Language) -> None:
    if is_installed(lang):
        return

    nt_name = NOTE_TYPE_PREFIX + lang.name_en
    nt_mgr = aqt.mw.col.models
    nt = nt_mgr.by_name(nt_name)

    # Legacy note type, rename it
    if not nt is None:
        i = 0
        while True:
            old_name = nt['name'] + ' (old'
            if i > 0:
                old_name += ' ' + str(i)
            old_name += ')'

            if nt_mgr.by_name(old_name) is None:
                break
            i += 1

        nt['name'] = old_name
        nt_mgr.update_dict(nt)

    # Create note type
    nt = nt_mgr.new(nt_name)
    nt_update(nt, lang, commit=False)
    nt_mgr.add(nt)
    nt_mgr.update_dict(nt)


def nt_update(nt: NotetypeDict, lang: Language, commit=True) -> None:
    nt_mgr = aqt.mw.col.models

    nt['name'] = NOTE_TYPE_PREFIX + lang.name_en

    # Assure required fields exist
    def field_exists(name):
        return any([fld['name'] == name for fld in nt['flds']])

    for field_name in lang.fields:
        if not field_exists(field_name):
            field = nt_mgr.new_field(field_name)
            nt_mgr.add_field(nt, field)

    css_path = lang.file_path('card', 'styles.css')
    css_data = open(css_path, 'r', encoding='utf-8').read()

    # Set CSS
    nt['css'] = NOTE_TYPE_MARK_CSS + '\n' + NOTE_TYPE_MARK_CSS_COMMENT + '\n\n' + css_data

    # Get or create template
    template_name = 'Standard'
    template = None
    template_idx = -1

    for i, t in enumerate(nt['tmpls']):
        if t['name'] == template_name:
            template = t
            template_idx = i
            break
    if template is None:
        template = nt_mgr.new_template(template_name)
        nt['tmpls'].append(template)
        template_idx = len(nt['tmpls']) - 1

    # Set template html
    for fmt, html_name in [('qfmt', 'front.html'), ('afmt', 'back.html')]:
        html_path = lang.file_path('card', html_name)
        html = open(html_path, 'r', encoding='utf-8').read()

        fields_settings = nt_get_tmpl_fields_settings(nt, template_idx, fmt)
        nt['tmpls'][template_idx][fmt] = html
        nt_set_tmpl_lang(nt, lang, template_idx, fmt, fields_settings, settings_mismatch_ignore=True, commit=False)

    # Set template css
    nt_set_css_lang(nt, lang, commit=False)

    if commit:
        nt_mgr.update_dict(nt)


def nt_get_lang(nt: NotetypeDict) -> Optional[Language]:
    lang_match = STYLE_RE.search(nt['css'])
    if lang_match:
        found = lang_match.groups()[0].lower()
        for lang in Languages:
            if found in [lang.code.lower(), lang.name_en.lower(), lang.name_native.lower()]:
                return lang
    return None


def nt_set_css_lang(nt: NotetypeDict, lang: Optional[Language], commit=True) -> None:
    # Remove CSS
    css_data = STYLE_RE.sub('', nt['css']).rstrip()

    if lang:
        card_css_path = lang.file_path('card', 'support.css')
        card_css = open(card_css_path, 'r', encoding='utf-8').read()

        css_data += F'\n\n/*###MIGAKU {lang.name_en.upper()} SUPPORT CSS START###*/'
        css_data += card_css
        css_data += F'/*###MIGAKU {lang.name_en.upper()} SUPPORT CSS END###*/'

    nt['css'] = css_data

    if commit:
        nt_mgr = aqt.mw.col.models
        nt_mgr.update_dict(nt)


def nt_set_tmpl_lang(nt: NotetypeDict, lang: Optional[Language], tmpl_idx: int, fmt: str, fields_settings: List[Dict[str, str]], settings_mismatch_ignore=False, commit=True) -> None:
    if not fmt in ['qfmt', 'afmt']:
        raise ValueError('Invalid format')

    fmt_data = nt['tmpls'][tmpl_idx][fmt]

    # Remove Formatting
    fmt_data = FORMAT_RE.sub('', fmt_data).rstrip()
    
    field_count = len(FIELD_RE.findall(fmt_data))

    skip_field_replacement = False

    if len(fields_settings) != field_count:
        if settings_mismatch_ignore:
            skip_field_replacement = True
        else:
            raise ValueError(F'Expected {field_count} fields, got {len(fields_settings)}')

    if not skip_field_replacement:
        field_i = 0
        text_i = 0
        while True:
            match = FIELD_RE.search(fmt_data, text_i)
            if not match:
                break

            d2 = match.group(2)
            d3 = match.group(3)

            if not d3:
                field_name = d2
            else:
                field_name = d3

            field_settings = fields_settings[field_i]

            field_active = len(field_settings) > 0

            if field_active:
                field_replace = '<div class="field"'
                for k, v in field_settings.items():
                    field_replace += ' data-' + k + '="' + v + '"' 
                field_replace += '>{{' + field_name + '}}</div>'
            else:
                field_replace = '{{' + field_name + '}}'
            
            fmt_data = fmt_data[:match.start()] + field_replace + fmt_data[match.end():]
            text_i = match.start() + len(field_replace)
            field_i += 1

    # Insert Formatting
    if lang:
        card_js_path = lang.file_path('card', 'support.html')
        card_js = open(card_js_path, 'r', encoding='utf-8').read()

        fmt_data += F'\n\n<!--###MIGAKU {lang.name_en.upper()} SUPPORT JS START###-->'
        fmt_data += card_js
        fmt_data += F'<!--###MIGAKU {lang.name_en.upper()} SUPPORT JS END###-->'

    nt['tmpls'][tmpl_idx][fmt] = fmt_data

    if commit:
        nt_mgr = aqt.mw.col.models
        nt_mgr.update_dict(nt)


def nt_get_tmpl_fields_settings(nt: NotetypeDict, tmpl_idx: int, fmt: str, field_names: bool = False):

    fmt_data = nt['tmpls'][tmpl_idx][fmt]
    fmt_data = FORMAT_RE.sub('', fmt_data)

    matches = FIELD_RE.findall(fmt_data)

    ret = []

    for (d1, d2, d3) in matches:
        field_settings = {}
        if not d3:
            field_name = d2
            for key, value in SETTINGS_RE.findall(d1):
                field_settings[key] = value
        else:
            field_name = d3

        if field_names:
            ret.append((field_name, field_settings))
        else:
            ret.append(field_settings)

    return ret


def nt_was_installed(nt: NotetypeDict) -> bool:
    lang = nt_get_lang(nt)
    if not lang:
        return False
    return nt['name'] == NOTE_TYPE_PREFIX + lang.name_en


def update_all_installed() -> None:
    nt_mgr = aqt.mw.col.models
    for lang in Languages:
        if is_installed(lang):
            nt = nt_mgr.by_name(NOTE_TYPE_PREFIX + lang.name_en)
            nt_update(nt, lang)

aqt.gui_hooks.profile_did_open.append(update_all_installed)
