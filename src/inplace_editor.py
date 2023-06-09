import re
from typing import Tuple, Any, List, Optional, Match
import base64
import html
import urllib.error
import urllib.parse
import urllib.request
import requests
import warnings
import bs4
from bs4 import BeautifulSoup
import json

import anki
from anki.collection import Config
from anki.utils import namedtmp, checksum
from anki.httpclient import HttpClient
import aqt
from aqt.reviewer import Reviewer
from aqt.sound import av_player
from aqt.qt import *
from aqt.utils import KeyboardModifiersPressed, tr, showWarning

from .note_type_mgr import nt_get_lang
from . import util
from .util import addon_path, addon_web_uri
from . import config

from aqt.operations.note import update_note


# Apply div around editable fields

def apply_edit_filter(field_content: str, field_name: str, field_filter: str, ctx: anki.template.TemplateRenderContext) -> str:
    if field_filter != 'editable' or not config.get('inplace_editor_enabled', True):
        return field_content

    field_content_b64_b = base64.b64encode(field_content.encode('utf-8'))
    field_content_b64 = str(field_content_b64_b, 'utf-8')

    return F'<div class="editable-field" data-field-name="{field_name}" data-content="{field_content_b64}">{field_content}</div>'


anki.hooks.field_filter.append(apply_edit_filter)


# Inject JS into reviewer and init editable fields when card side is shown

def show_empty_fields_js():
    show_empty_fields = config.get('inplace_editor_show_empty_fields', False)
    value = 'true' if show_empty_fields else 'false'
    return F'try {{ document.querySelector("#qa").classList.toggle("show-empty-editable-field", {value}); }} catch (e) {{ }}'

def update_show_empty_fields():
    aqt.mw.reviewer.web.eval(show_empty_fields_js())

inplace_editor_css_uri = addon_web_uri('inplace_editor.css')
inplace_editor_js = F'var inplace_editor_css_path = "{inplace_editor_css_uri}";\n'

with open(addon_path('inplace_editor.js'), 'r', encoding='utf-8') as file:
    inplace_editor_js += file.read()

def init_reviewer_web(reviewer: Reviewer) -> None:
    reviewer.web.eval(inplace_editor_js + '\n' + show_empty_fields_js())

def init_reviewer_fields(*args, **kwargs) -> None:
    reviewer = aqt.mw.reviewer
    reviewer.web.eval('init_editable_fields();\n' + show_empty_fields_js())

Reviewer._initWeb = anki.hooks.wrap(Reviewer._initWeb, init_reviewer_web)
aqt.gui_hooks.reviewer_did_show_question.append(init_reviewer_fields)
aqt.gui_hooks.reviewer_did_show_answer.append(init_reviewer_fields)


# Manage edited field content

def handle_inplace_edit(reviewer: Reviewer, message: str):
    card = reviewer.card

    if not card:
        return 

    note = card.note()

    if not note:
        return

    message_parts = message.split('|')

    command = message_parts[0]
    field_name = message_parts[1]
    field_content_b64 = message_parts[2]
    field_content = base64.b64decode(field_content_b64).decode('utf-8')
    should_reload = True

    def maybe_reshow_card():
        if reviewer.mw.state == 'review' and reviewer.card:
            reviewer.card.load()

            if should_reload or config.get('inplace_editor_always_reload', False):
                reviewer_reshow(reviewer, mute=True, reload_card=False)

    def set_content(new_field_content, checkpoint_name=None):
        if field_name == 'Tags':
            note.tags = new_field_content
            note.tags = aqt.mw.col.tags.split(new_field_content)
        else:
            if note[field_name] == new_field_content:
                maybe_reshow_card()
                return
            note[field_name] = new_field_content

        if checkpoint_name:
            checkpoint_id = aqt.mw.col.add_custom_undo_entry(checkpoint_name)
        else:
            checkpoint_id = None

        def on_note_flushed(_ret):
            if not checkpoint_id is None:
                aqt.mw.col.merge_undo_entries(checkpoint_id)
            maybe_reshow_card()

        update_note(parent=aqt.mw, note=note).success(on_note_flushed).run_in_background()

    def on_syntax_delivery(result):
        set_content(result[0][field_name], F'Add {lang.name_en} Syntax')
        aqt.mw.progress.finish()

    def on_syntax_error(msg):
        aqt.mw.progress.finish()
        util.show_critical(msg)
        maybe_reshow_card()

    if command == 'inplace-edit-submit':
        should_reload = message_parts[3] == 'true'
        set_content(field_content, 'Edit Field')
    elif command == 'inplace-edit-syntax-add':
        lang = nt_get_lang(card.note_type())
        if lang is None:
            return
        if not aqt.mw.migaku_connection.is_connected():
            util.show_critical('Anki is not connected to the Browser Extension.')
            return
        aqt.mw.progress.start(label=F'Adding {lang.name_en} syntax to field...')
        field_content = lang.remove_syntax(field_content)
        aqt.mw.migaku_connection.request_syntax(
            [{ field_name: field_content }],
            lang.code,
            on_done = on_syntax_delivery,
            on_error = on_syntax_error,
            callback_on_main_thread = True,
            timeout=20,
        )
    elif command == 'inplace-edit-syntax-remove':
        lang = nt_get_lang(card.note_type())
        if lang is None:
            return
        field_content = lang.remove_syntax(field_content)
        set_content(field_content, F'Remove {lang.name_en} Syntax')
    else:
        raise ValueError('Invalid inplace edit')


def handle_js_message(handled: Tuple[bool, Any], message: str, ctx: Any) -> Tuple[bool, Any]:

    if not isinstance(ctx, Reviewer):
        return handled

    reviewer: Reviewer = ctx
    
    if message.startswith('inplace-edit'):
        handle_inplace_edit(reviewer, message)
        return (True, None)

    elif message == 'inplace-paste':
        js = 'inplace_' + paste_handler.onPaste()
        reviewer.web.eval(js)
        return (True, None)

    return handled

aqt.gui_hooks.webview_did_receive_js_message.append(handle_js_message)


def reviewer_reshow(reviewer: Reviewer, mute=False, reload_card=True) -> None:
    if reviewer.mw.state != 'review':
        return

    if reviewer.card and reload_card:
        reviewer.card.load()

    elif reviewer.state == 'question':
        reviewer._showQuestion()
    if reviewer.state == 'answer':
        reviewer._showAnswer()

    if mute:
        av_player.stop_and_clear_queue()



# Copied from aqt.editor.Editor and aqt.editor.EditorWebView with minimal changes

class PasteHandler:

    pics = (
        "jpg",
        "jpeg",
        "png",
        "tif",
        "tiff",
        "gif",
        "svg",
        "webp",
        "ico"
    )

    audio = (
        "3gp",
        "avi",
        "flac",
        "flv",
        "m4a",
        "mkv",
        "mov",
        "mp3",
        "mp4",
        "mpeg",
        "mpg",
        "oga",
        "ogg",
        "ogv",
        "ogx",
        "opus",
        "spx",
        "swf",
        "wav",
        "webm",
    )

    def __init__(self, mw: aqt.AnkiApp):
        self.mw = mw

    def onPaste(self) -> None:
        return self._onPaste(QClipboard.Clipboard)

    def _wantsExtendedPaste(self) -> bool:
        strip_html = self.mw.col.get_config_bool(
            Config.Bool.PASTE_STRIPS_FORMATTING
        )
        if KeyboardModifiersPressed().shift:
            strip_html = not strip_html
        return not strip_html

    def _onPaste(self, mode: QClipboard.Mode) -> None:
        extended = self._wantsExtendedPaste()
        mime = self.mw.app.clipboard().mimeData(mode=mode)
        html, internal = self._processMime(mime, extended)
        if not html:
            return
        return self.doPaste(html, internal, extended)

    def doPaste(self, html: str, internal: bool, extended: bool = False) -> None:
        html = self._pastePreFilter(html, internal)
        if extended:
            ext = "true"
        else:
            ext = "false"
        return f"pasteHTML({json.dumps(html)}, {json.dumps(internal)}, {ext});"

    # returns (html, isInternal)
    def _processMime(self, mime: QMimeData, extended: bool = False) -> Tuple[str, bool]:
        # print("html=%s image=%s urls=%s txt=%s" % (
        #     mime.hasHtml(), mime.hasImage(), mime.hasUrls(), mime.hasText()))
        # print("html", mime.html())
        # print("urls", mime.urls())
        # print("text", mime.text())

        # try various content types in turn
        html, internal = self._processHtml(mime)
        if html:
            return html, internal

        # favour url if it's a local link
        if mime.hasUrls() and mime.urls()[0].toString().startswith("file://"):
            types = (self._processUrls, self._processImage, self._processText)
        else:
            types = (self._processImage, self._processUrls, self._processText)

        for fn in types:
            html = fn(mime, extended)
            if html:
                return html, True
        return "", False

    def _processHtml(self, mime: QMimeData) -> Tuple[Optional[str], bool]:
        if not mime.hasHtml():
            return None, False
        html = mime.html()

        # no filtering required for internal pastes
        if html.startswith("<!--anki-->"):
            return html[11:], True

        return html, False

    def _processUrls(self, mime: QMimeData, extended: bool = False) -> Optional[str]:
        if not mime.hasUrls():
            return None

        buf = ""
        for qurl in mime.urls():
            url = qurl.toString()
            # chrome likes to give us the URL twice with a \n
            url = url.splitlines()[0]
            buf += self.urlToLink(url) or ""

        return buf

    def _processImage(self, mime: QMimeData, extended: bool = False) -> Optional[str]:
        if not mime.hasImage():
            return None
        im = QImage(mime.imageData())
        uname = namedtmp("paste")
        if self.mw.col.get_config_bool(Config.Bool.PASTE_IMAGES_AS_PNG):
            ext = ".png"
            im.save(uname + ext, None, 50)
        else:
            ext = ".jpg"
            im.save(uname + ext, None, 80)

        # invalid image?
        path = uname + ext
        if not os.path.exists(path):
            return None

        with open(path, "rb") as file:
            data = file.read()
        fname = self._addPastedImage(data, ext)
        if fname:
            return self.fnameToLink(fname)
        return None

    def _processText(self, mime: QMimeData, extended: bool = False) -> Optional[str]:
        if not mime.hasText():
            return None

        txt = mime.text()
        processed = []
        lines = txt.split("\n")

        for line in lines:
            for token in re.split(r"(\S+)", line):
                # inlined data in base64?
                if extended and token.startswith("data:image/"):
                    processed.append(self.inlinedImageToLink(token))
                elif extended and self.isURL(token):
                    # if the user is pasting an image or sound link, convert it to local
                    link = self.urlToLink(token)
                    if link:
                        processed.append(link)
                    else:
                        # not media; add it as a normal link
                        link = '<a href="{}">{}</a>'.format(
                            token, html.escape(urllib.parse.unquote(token))
                        )
                        processed.append(link)
                else:
                    token = html.escape(token).replace("\t", " " * 4)
                    # if there's more than one consecutive space,
                    # use non-breaking spaces for the second one on
                    def repl(match: Match) -> str:
                        return f"{match.group(1).replace(' ', '&nbsp;')} "

                    token = re.sub(" ( +)", repl, token)
                    processed.append(token)

            processed.append("<br>")
        # remove last <br>
        processed.pop()
        return "".join(processed)

    # Audio/video/images
    ######################################################################

    def _addMedia(self, path: str, canDelete: bool = False) -> str:
        """Add to media folder and return local img or sound tag."""
        # copy to media folder
        fname = self.mw.col.media.addFile(path)
        # return a local html link
        return self.fnameToLink(fname)

    def _addMediaFromData(self, fname: str, data: bytes) -> str:
        return self.mw.col.media.writeData(fname, data)

    # Media downloads
    ######################################################################

    def urlToLink(self, url: str) -> Optional[str]:
        fname = self.urlToFile(url)
        if not fname:
            return None
        return self.fnameToLink(fname)

    def fnameToLink(self, fname: str) -> str:
        ext = fname.split(".")[-1].lower()
        if ext in self.pics:
            name = urllib.parse.quote(fname.encode("utf8"))
            return f'<img src="{name}">'
        else:
            av_player.play_file(fname)
            return f"[sound:{html.escape(fname, quote=False)}]"

    def urlToFile(self, url: str) -> Optional[str]:
        l = url.lower()
        for suffix in self.pics + self.audio:
            if l.endswith(f".{suffix}"):
                return self._retrieveURL(url)
        # not a supported type
        return None

    def isURL(self, s: str) -> bool:
        s = s.lower()
        return (
            s.startswith("http://")
            or s.startswith("https://")
            or s.startswith("ftp://")
            or s.startswith("file://")
        )

    def inlinedImageToFilename(self, txt: str) -> str:
        prefix = "data:image/"
        suffix = ";base64,"
        for ext in ("jpg", "jpeg", "png", "gif"):
            fullPrefix = prefix + ext + suffix
            if txt.startswith(fullPrefix):
                b64data = txt[len(fullPrefix) :].strip()
                data = base64.b64decode(b64data, validate=True)
                if ext == "jpeg":
                    ext = "jpg"
                return self._addPastedImage(data, f".{ext}")

        return ""

    def inlinedImageToLink(self, src: str) -> str:
        fname = self.inlinedImageToFilename(src)
        if fname:
            return self.fnameToLink(fname)

        return ""

    # ext should include dot
    def _addPastedImage(self, data: bytes, ext: str) -> str:
        # hash and write
        csum = checksum(data)
        fname = f"paste-{csum}{ext}"
        return self._addMediaFromData(fname, data)

    def _retrieveURL(self, url: str) -> Optional[str]:
        "Download file into media folder and return local filename or None."
        # urllib doesn't understand percent-escaped utf8, but requires things like
        # '#' to be escaped.
        url = urllib.parse.unquote(url)
        if url.lower().startswith("file://"):
            url = url.replace("%", "%25")
            url = url.replace("#", "%23")
            local = True
        else:
            local = False
        # fetch it into a temporary folder
        self.mw.progress.start(immediate=not local, parent=self.mw)
        content_type = None
        error_msg: Optional[str] = None
        try:
            if local:
                req = urllib.request.Request(
                    url, None, {"User-Agent": "Mozilla/5.0 (compatible; Anki)"}
                )
                with urllib.request.urlopen(req) as response:
                    filecontents = response.read()
            else:
                with HttpClient() as client:
                    client.timeout = 30
                    with client.get(url) as response:
                        if response.status_code != 200:
                            error_msg = tr.qt_misc_unexpected_response_code(
                                val=response.status_code,
                            )
                            return None
                        filecontents = response.content
                        content_type = response.headers.get("content-type")
        except (urllib.error.URLError, requests.exceptions.RequestException) as e:
            error_msg = tr.editing_an_error_occurred_while_opening(val=str(e))
            return None
        finally:
            self.mw.progress.finish()
            if error_msg:
                showWarning(error_msg)
        # strip off any query string
        url = re.sub(r"\?.*?$", "", url)
        fname = os.path.basename(urllib.parse.unquote(url))
        if not fname.strip():
            fname = "paste"
        if content_type:
            fname = self.mw.col.media.add_extension_based_on_mime(fname, content_type)

        return self.mw.col.media.write_data(fname, filecontents)

    # Paste/drag&drop
    ######################################################################

    removeTags = ["script", "iframe", "object", "style"]

    def _pastePreFilter(self, html: str, internal: bool) -> str:
        # https://anki.tenderapp.com/discussions/ankidesktop/39543-anki-is-replacing-the-character-by-when-i-exit-the-html-edit-mode-ctrlshiftx
        if html.find(">") < 0:
            return html

        with warnings.catch_warnings() as w:
            warnings.simplefilter("ignore", UserWarning)
            doc = BeautifulSoup(html, "html.parser")

        tag: bs4.element.Tag
        if not internal:
            for tag in self.removeTags:
                for node in doc(tag):
                    node.decompose()

            # convert p tags to divs
            for node in doc("p"):
                node.name = "div"

        for tag in doc("img"):
            try:
                src = tag["src"]
            except KeyError:
                # for some bizarre reason, mnemosyne removes src elements
                # from missing media
                continue

            # in internal pastes, rewrite mediasrv references to relative
            if internal:
                m = re.match(r"http://127.0.0.1:\d+/(.*)$", src)
                if m:
                    tag["src"] = m.group(1)
            else:
                # in external pastes, download remote media
                if self.isURL(src):
                    fname = self._retrieveURL(src)
                    if fname:
                        tag["src"] = fname
                elif src.startswith("data:image/"):
                    # and convert inlined data
                    tag["src"] = self.inlinedImageToFilename(src)

        html = str(doc)
        return html


paste_handler = PasteHandler(aqt.mw)
