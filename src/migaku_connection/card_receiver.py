from pydub import AudioSegment
from pydub import effects
import time
import subprocess
import json
import os
import re

import aqt
from anki.notes import Note
from ..editor.current_editor import get_current_note_info
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

        card = self.get_body_argument("card", default=None)

        if not card:
            self.finish("Invalid request.")

        self.create_card("")
        return

    def create_card(self, card_data_json):
        # card_data = json.loads(card_data_json)
        print("create_card")

        info = get_current_note_info()

        if not info:
            return "No current note."

        note = info["note"]

        note_type = note.note_type()
        if not note_type:
            return "Current note has no valid note_type."

        notetype_name = str(note_type.get("name", ""))
        notetype_id = str(note_type.get("id", "")) + notetype_name

        note_tags = note.tags

        print("note_tags", note_tags, notetype_name, notetype_id)

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
