import re
import os
import shutil
from typing import List, Dict, Optional

import aqt
from anki.models import NotetypeDict

from . import util
from .languages import Languages, Language


NOTE_TYPE_PREFIX = "Migaku "
NOTE_TYPE_MARK_CSS = "/* Managed Migaku Note Type */"

FIELD_RE = re.compile(
    r"<div class=\"field\" (.*?)>{{(?!#|/|\^|FrontSide|Tags)(.*?)}}</div>|{{(?!#|/|\^|FrontSide|Tags)(.*?)}}"
)
SETTINGS_RE = re.compile(r"data-(.*?)=\"(.*?)\"")
FORMAT_RE = re.compile(
    r"<!--###MIGAKU (.*?) SUPPORT JS STARTS###.*?SUPPORT JS ENDS###.*-->", re.DOTALL
)
STYLE_RE = re.compile(
    r"/\*###MIGAKU (.*?) SUPPORT CSS STARTS###.*?SUPPORT CSS ENDS###.*\*/", re.DOTALL
)


def is_installed(lang: Language) -> bool:
    nt_mgr = aqt.mw.col.models
    nt = nt_mgr.by_name(NOTE_TYPE_PREFIX + lang.name_en)

    if nt is None:
        return False

    return nt["css"].startswith(NOTE_TYPE_MARK_CSS)


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
            old_name = nt["name"] + " (old"
            if i > 0:
                old_name += " " + str(i)
            old_name += ")"

            if nt_mgr.by_name(old_name) is None:
                break
            i += 1

        nt["name"] = old_name
        nt_mgr.update_dict(nt)

    # Create note type
    nt = nt_mgr.new(nt_name)
    nt_update(nt, lang, commit=False)
    nt_mgr.add(nt)
    nt_mgr.update_dict(nt)


def nt_update(nt: NotetypeDict, lang: Language, commit=True) -> None:
    # It is the reserved, read-only note type, e.g. "Migaku Japanese".
    # Custom notetypes are cloned from this one.
    is_base_tmpl = nt["name"] == NOTE_TYPE_PREFIX + lang.name_en
    nt_mgr = aqt.mw.col.models

    # Assure required fields exist
    def field_exists(name):
        return any([fld["name"] == name for fld in nt["flds"]])

    if is_base_tmpl:
        # Assure fields
        for field_name in lang.fields:
            if field_exists(field_name):
                continue

            field = nt_mgr.new_field(field_name)
            nt_mgr.add_field(nt, field)

        # Set CSS
        css_path = lang.file_path("card", "styles.css")
        with open(css_path, "r", encoding="utf-8") as file:
            css_data = file.read()

        nt["css"] = NOTE_TYPE_MARK_CSS + "\n\n" + css_data

    # Assure standard template
    template_name = "Standard"
    template = None
    template_idx = -1

    for idx, tmpl in enumerate(nt["tmpls"]):
        if tmpl["name"] == template_name:
            template = tmpl
            template_idx = idx
            break

    if is_base_tmpl and not template:
        template = nt_mgr.new_template(template_name)
        nt["tmpls"].append(template)
        template_idx = len(nt["tmpls"]) - 1

    # Set template html
    if template:
        for fmt, html_name in [("qfmt", "front.html"), ("afmt", "back.html")]:
            fields_settings = nt_get_tmpl_fields_settings(nt, template_idx, fmt)

            # The base template is always reset to the default:
            # User may not change it, except for setting Migaku Options which are applied by the nt_set_tmpl_lang call below
            if is_base_tmpl:
                html_path = lang.file_path("card", html_name)
                with open(html_path, "r", encoding="utf-8") as file:
                    html = file.read()
                nt["tmpls"][template_idx][fmt] = html

            nt_set_tmpl_lang(
                nt,
                lang,
                template_idx,
                fmt,
                fields_settings,
                settings_mismatch_ignore=True,
                commit=False,
            )

    # Set template css
    nt_set_css_lang(nt, lang, commit=False)

    # Copy media files
    media_dir = lang.file_path("card", "media")
    if os.path.exists(media_dir):
        for fname in os.listdir(media_dir):
            shutil.copy(os.path.join(media_dir, fname), util.col_media_path(fname))

    if commit:
        nt_mgr.update_dict(nt)


def nt_get_lang(nt: NotetypeDict) -> Optional[Language]:
    lang_match = STYLE_RE.search(nt["css"])
    if lang_match:
        found = lang_match.groups()[0].lower()
        for lang in Languages:
            if found in [
                lang.code.lower(),
                lang.name_en.lower(),
                lang.name_native.lower(),
            ]:
                return lang
    return None


def nt_set_css_lang(nt: NotetypeDict, lang: Optional[Language], commit=True) -> None:
    # User CSS
    css_data = STYLE_RE.sub("", nt["css"]).rstrip()

    if lang:
        card_css_path = lang.file_path("card", "support.css")

        with open(card_css_path, "r", encoding="utf-8") as file:
            card_css = file.read()

        css_data += f"\n\n/*###MIGAKU {lang.name_en.upper()} SUPPORT CSS STARTS###*/"
        css_data += card_css
        css_data += f"/*###MIGAKU {lang.name_en.upper()} SUPPORT CSS ENDS###*/"

    nt["css"] = css_data

    if commit:
        nt_mgr = aqt.mw.col.models
        nt_mgr.update_dict(nt)


def nt_set_tmpl_lang(
    nt: NotetypeDict,
    lang: Optional[Language],
    tmpl_idx: int,
    fmt: str,
    fields_settings: List[Dict[str, str]],
    settings_mismatch_ignore=False,
    commit=True,
) -> None:
    if not fmt in ["qfmt", "afmt"]:
        raise ValueError("Invalid format")

    fmt_data = nt["tmpls"][tmpl_idx][fmt]

    # Remove Formatting
    fmt_data = FORMAT_RE.sub("", fmt_data).rstrip()

    field_count = len(FIELD_RE.findall(fmt_data))

    skip_field_replacement = False

    if len(fields_settings) != field_count:
        if settings_mismatch_ignore:
            skip_field_replacement = True
        else:
            raise ValueError(
                f"Expected {field_count} fields, got {len(fields_settings)}"
            )

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
                    field_replace += " data-" + k + '="' + v + '"'
                field_replace += ">{{" + field_name + "}}</div>"
            else:
                field_replace = "{{" + field_name + "}}"

            fmt_data = (
                fmt_data[: match.start()] + field_replace + fmt_data[match.end() :]
            )
            text_i = match.start() + len(field_replace)
            field_i += 1

    # Insert Formatting
    if lang:
        card_js_path = lang.file_path("card", "support.html")
        with open(card_js_path, "r", encoding="utf-8") as file:
            card_js = file.read()

        fmt_data += f"\n\n<!--###MIGAKU {lang.name_en.upper()} SUPPORT JS STARTS###-->"
        fmt_data += card_js
        fmt_data += f"<!--###MIGAKU {lang.name_en.upper()} SUPPORT JS ENDS###-->"

    nt["tmpls"][tmpl_idx][fmt] = fmt_data

    if commit:
        nt_mgr = aqt.mw.col.models
        nt_mgr.update_dict(nt)


def nt_get_tmpl_fields_settings(
    nt: NotetypeDict, tmpl_idx: int, fmt: str, field_names: bool = False
):
    fmt_data = nt["tmpls"][tmpl_idx][fmt]
    fmt_data = FORMAT_RE.sub("", fmt_data)

    matches = FIELD_RE.findall(fmt_data)

    ret = []

    for d1, d2, d3 in matches:
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
    return nt["name"] == NOTE_TYPE_PREFIX + lang.name_en


def update_all_installed() -> None:
    notetypes = aqt.mw.col.models.all()

    for nt in notetypes:
        lang = nt_get_lang(nt)

        if not lang or not is_installed(lang):
            continue

        nt_update(nt, lang)
