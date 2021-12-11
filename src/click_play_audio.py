from typing import Tuple, Any

import aqt
from aqt.reviewer import Reviewer
from aqt.browser.previewer import Previewer

from .note_type_mgr import nt_get_lang


def ctx_get_lang(ctx):

    note = None

    if isinstance(ctx, Reviewer):
        card = ctx.card

    elif isinstance(ctx, Previewer):
        card = ctx.card()
    
    if not card:
        return None
    
    note = card.note()
    if not note:
        return None

    return nt_get_lang(card.note_type())


def handle_js_message(handled: Tuple[bool, Any], message: str, ctx: Any) -> Tuple[bool, Any]:

    if message.startswith('play_audio'):
        lang = ctx_get_lang(ctx)

        if lang:
            word = message[11:]
            aqt.mw.migaku_connection.play_audio(lang.code, word)

        return (True, None)

    return handled

aqt.gui_hooks.webview_did_receive_js_message.append(handle_js_message)
