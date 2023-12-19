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


global_toolbar = None


def open_add_cards():
    aqt.mw.onAddCard()


def activate_migaku_toolbar(toolbar):
    info = get_add_cards_info()
    # toolbar.web.eval(f"MigakuToolbar.activate({json.dumps(info)})")
    # toolbar.link_handlers["openAddCards"] = open_add_cards
    menu.set_deck_name(info["deck_name"], info["deck_id"])
    menu.set_type_name(info["notetype_name"], info["notetype_id"])
    menu.activate_deck_type()


def deactivate_migaku_toolbar(toolbar):
    # toolbar.web.eval("MigakuToolbar.deactivate()")
    menu.deactivate_deck_type()


def refresh_migaku_toolbar():
    info = get_add_cards_info()
    # global_toolbar.web.eval(f"MigakuToolbar.refresh({json.dumps(info)})")
    menu.set_deck_name(info["deck_name"], info["deck_id"])
    menu.set_type_name(info["notetype_name"], info["notetype_id"])


def refresh_migaku_toolbar_opened_addcards():
    defaults = aqt.mw.col.defaults_for_adding(current_review_card=aqt.mw.reviewer.card)
    info = get_add_cards_info(defaults)

    on_addcards_did_change_deck(defaults.deck_id)
    on_addcards_did_change_note_type(defaults.notetype_id)

    # global_toolbar.web.eval(f"MigakuToolbar.refresh({json.dumps(info)})")
    menu.set_deck_name(info["deck_name"], info["deck_id"])
    menu.set_type_name(info["notetype_name"], info["notetype_id"])


def inject_migaku_toolbar(html: str, toolbar):
    global global_toolbar
    global_toolbar = toolbar

    ConnectionListener(
        lambda: activate_migaku_toolbar(toolbar),
        lambda: deactivate_migaku_toolbar(toolbar),
    )

    with open(addon_path("toolbar/toolbar.html"), "r", encoding="utf-8") as file:
        html.append(file.read())


def set_deck_type_to_migaku(parent):
    # aqt.operations.deck.set_current_deck(parent=parent, deck_id=get('migakuDeckId', 0))
    # aqt.mw.col.conf['curModel'] = get('migakuNotetypeId')
    aqt.mw.col.set_config(
        "curDeck", get("migakuDeckId", aqt.mw.col.get_config("curDeck"))
    )
    aqt.mw.col.set_config(
        "curModel", get("migakuNotetypeId", aqt.mw.col.get_config("curModel"))
    )
