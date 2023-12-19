import json
import re

import aqt
from anki.notes import Note
from ..config import get
from ..card_types import CardFields, card_fields_from_dict
from ..editor.current_editor import (
    add_cards_add_to_history,
    get_add_cards_info,
    map_to_add_cards,
)
from tornado.web import RequestHandler

from .migaku_http_handler import MigakuHTTPHandler


class CardReceiver(MigakuHTTPHandler):
    def post(self: RequestHandler):
        try:
            body = json.loads(self.request.body)
            card = card_fields_from_dict(body)
            self.create_card(card)
        except Exception as e:
            self.finish({"error": f"Invalid request: {str(e)}."})

        return

    def create_card(self, card: CardFields):
        if get("migakuIntercept", False) and map_to_add_cards(card):
            print('Tryied to map to add cards.')
            self.finish(json.dumps({"id": 0, "created": False}))
            return

        info = get_add_cards_info()

        note = Note(aqt.mw.col, info["notetype"])
        fields = info["fields"]

        if not any([type != "none" for (fieldname, type) in fields.items()]):
            print('No fields to map to.')
            self.finish({"error": "No fields to map to."})
            return

        for fieldname, type in fields.items():
            if type == "none":
                continue

            note[fieldname] = str(getattr(card, type))

        note.tags = info["tags"]
        note.model()["did"] = int(info["deck_id"])

        aqt.mw.col.addNote(note)
        aqt.mw.col.save()
        aqt.mw.taskman.run_on_main(aqt.mw.reset)
        aqt.mw.taskman.run_on_main(lambda: aqt.utils.tooltip("Migaku Card created"))
        aqt.mw.taskman.run_on_main(lambda: add_cards_add_to_history(note))
        print(f'Card created. ID: {note.id}.')

        self.finish(json.dumps({"id": note.id, "created": True}))
