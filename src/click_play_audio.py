from typing import Tuple, Any

import aqt
from aqt.reviewer import Reviewer

from .note_type_mgr import nt_get_lang


def reviewer_play_audio(reviewer: Reviewer, word: str):

    card = reviewer.card

    if not card:
        return

    note = card.note()

    if not note:
        return

    lang = nt_get_lang(card.note_type())
    if lang is None:
        return

    aqt.mw.migaku_connection.play_audio(lang.code, word)


def handle_js_message(handled: Tuple[bool, Any], message: str, ctx: Any) -> Tuple[bool, Any]:

    if not isinstance(ctx, Reviewer):
        return handled

    reviewer: Reviewer = ctx
    
    if message.startswith('play_audio'):
        reviewer_play_audio(reviewer, message[11:])
        return (True, None)

    return handled

aqt.gui_hooks.webview_did_receive_js_message.append(handle_js_message)
