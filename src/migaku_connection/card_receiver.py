import json
import re

import aqt
from anki.notes import Note
from ..card_types import CardFields, card_fields_from_dict
from ..editor.current_editor import add_cards_add_to_history, get_add_cards_info
from tornado.web import RequestHandler

from .migaku_http_handler import MigakuHTTPHandler


class CardReceiver(MigakuHTTPHandler):
    image_formats = ["webp"]
    audio_formats = ["m4a"]

    TO_MP3_RE = re.compile(r"\[sound:(.*?)\.(wav|ogg)\]")
    BR_RE = re.compile(r"<br\s*/?>")

    def post(self: RequestHandler):
        try:
            body = json.loads(self.request.body)
            print("body", body)
            card = card_fields_from_dict(body)
            print("card", card)
            self.create_card(card)
        except Exception as e:
            self.finish(f"Invalid request: {str(e)}")

        return

    def create_card(self, card: CardFields):
        info = get_add_cards_info()
        note = Note(aqt.mw.col, info["notetype"])
        fields = info["fields"]

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

        self.finish(json.dumps({"id": note.id}))
