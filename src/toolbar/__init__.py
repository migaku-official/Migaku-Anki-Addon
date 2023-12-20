import json
import aqt
from ..config import get
from .. import menu

from ..editor.current_editor import (
    get_add_cards_info,
    on_addcards_did_change_deck,
    on_addcards_did_change_note_type,
)
from ..migaku_connection import ConnectionListener
from ..util import addon_path


def activate_migaku_toolbar():
    info = get_add_cards_info()
    menu.set_deck_name(info["deck_name"], info["deck_id"])
    menu.set_type_name(info["notetype_name"], info["notetype_id"])
    menu.activate_deck_type()


def deactivate_migaku_toolbar():
    menu.deactivate_deck_type()


def refresh_migaku_toolbar():
    info = get_add_cards_info()
    menu.set_deck_name(info["deck_name"], info["deck_id"])
    menu.set_type_name(info["notetype_name"], info["notetype_id"])


def refresh_migaku_toolbar_opened_addcards():
    defaults = aqt.mw.col.defaults_for_adding(current_review_card=aqt.mw.reviewer.card)
    info = get_add_cards_info(defaults)

    on_addcards_did_change_deck(defaults.deck_id)
    on_addcards_did_change_note_type(defaults.notetype_id)

    menu.set_deck_name(info["deck_name"], info["deck_id"])
    menu.set_type_name(info["notetype_name"], info["notetype_id"])


def inject_migaku_toolbar(col):
    ConnectionListener(
        lambda: activate_migaku_toolbar(),
        lambda: deactivate_migaku_toolbar(),
    )

    # with open(addon_path("toolbar/toolbar.html"), "r", encoding="utf-8") as file:
    #     html.append(file.read())


def set_deck_type_to_migaku():
    aqt.mw.col.set_config(
        "curDeck", get("migakuDeckId", aqt.mw.col.get_config("curDeck"))
    )
    aqt.mw.col.set_config(
        "curModel", get("migakuNotetypeId", aqt.mw.col.get_config("curModel"))
    )
