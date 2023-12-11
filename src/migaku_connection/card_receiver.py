from pydub import AudioSegment
from pydub import effects
import time
import subprocess
import json
import os
import re

import aqt
from anki.notes import Note
from tornado.web import RequestHandler

from .migaku_http_handler import MigakuHTTPHandler
from .. import config
from .. import util
from ..inplace_editor import reviewer_reshow


class CardReceiver(MigakuHTTPHandler):
    image_formats = ["webp"]
    audio_formats = ["m4a"]

    TO_MP3_RE = re.compile(r"\[sound:(.*?)\.(wav|ogg)\]")
    BR_RE = re.compile(r"<br\s*/?>")

    def post(self: RequestHandler):
        if not self.check_version():
            self.finish("Card could not be created: Version mismatch")
            return

        # card = self.get_body_argument("card", default=None)
        # if card:
        # self.create_card('')

        #     return

        self.finish("Invalid request.")

    def create_card(self, card_data_json):
        # card_data = json.loads(card_data_json)
        print('create_card')

        # note_type_id = card_data["noteTypeId"]
        # note_type = aqt.mw.col.models.get(note_type_id)
        # deck_id = card_data["deckId"]

        # note = Note(aqt.mw.col, note_type)

        # for field in card_data["fields"]:
        #     if "content" in field and field["content"]:
        #         content = field["content"]
        #         field_name = field["name"]
        #         content = self.post_process_text(content, field_name)
        #         note[field_name] = content

        # tags = card_data.get("tags")
        # if tags:
        #     note.set_tags_from_str(tags)

        # note.model()["did"] = int(deck_id)
        # aqt.mw.col.addNote(note)
        # aqt.mw.col.save()
        # aqt.mw.taskman.run_on_main(aqt.mw.reset)

        self.handle_files(self.request.files)

        self.finish(json.dumps({"id": 0}))

    # def move_file_to_media_dir(self, file_body, filename):
    #     file_path = util.col_media_path(filename)
    #     with open(file_path, "wb") as file_handle:
    #         file_handle.write(file_body)
