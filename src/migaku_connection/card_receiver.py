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
            self.finish({"success": False, "error": f"Invalid request: {str(e)}."})

        return

    def create_card(self, card: CardFields):
        if get("migakuIntercept", False) and map_to_add_cards(card):
            print("Tryied to map to add cards.")
            aqt.mw.taskman.run_on_main(
                lambda: aqt.utils.tooltip("Mapped Migaku fields to Add cards window.")
            )
            self.finish(
                json.dumps(
                    {
                        "success": True,
                        "created": False,
                    }
                )
            )
            return

        info = get_add_cards_info()

        note = Note(aqt.mw.col, info["notetype"])
        fields = info["fields"]

        if not any([type != "none" for (fieldname, type) in fields.items()]):
            print("No fields to map to.")
            aqt.mw.taskman.run_on_main(
                lambda: aqt.utils.tooltip(
                    "Could not create Migaku Card: No fields to map to."
                )
            )
            self.finish(
                {
                    "success": False,
                    "error": "No fields to map to.",
                }
            )
            return

        addcards_note = info["note"] if "note" in info else None

        for fieldname, type in fields.items():
            note[fieldname] = (
                str(getattr(card, type))
                if type != "none"
                else addcards_note[fieldname]
                if addcards_note
                else ""
            )

        note.tags = info["tags"]
        note.model()["did"] = int(info["deck_id"])

        aqt.mw.col.addNote(note)
        aqt.mw.col.save()
        aqt.mw.taskman.run_on_main(aqt.mw.reset)
        aqt.mw.taskman.run_on_main(lambda: aqt.utils.tooltip("Migaku Card created"))
        aqt.mw.taskman.run_on_main(lambda: add_cards_add_to_history(note))
        print(f"Card created. ID: {note.id}.")

        self.finish(
            json.dumps(
                {
                    "success": True,
                    "created": True,
                    "id": note.id,
                }
            )
        )
