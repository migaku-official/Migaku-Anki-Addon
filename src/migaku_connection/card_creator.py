import json
import re

import aqt
from anki.notes import Note


from .. import config
from .. import util
from ..inplace_editor import reviewer_reshow
from ..editor.current_editor import get_current_note_info

from .migaku_http_handler import MigakuHTTPHandler
from .handle_files import handle_files


class CardCreator(MigakuHTTPHandler):
    TO_MP3_RE = re.compile(r"\[sound:(.*?)\.(wav|ogg)\]")
    BR_RE = re.compile(r"<br\s*/?>")

    def post(self):
        if not self.check_version():
            self.finish("Card could not be created: Version mismatch")
            return

        msg_id = self.get_body_argument("id", default=None)
        if not msg_id is None:
            try:
                msg_id = int(msg_id)
            except ValueError:
                msg_id = None

        received_audio = self.get_body_argument("Migaku-Deliver-Audio", default=None)
        if received_audio:
            self.handle_audio_delivery(received_audio)
            return

        no_audio_available = self.get_body_argument(
            "Migaku-No-Audio-Found", default=None
        )
        if no_audio_available:
            self.handle_no_audio_results()
            return

        received_data = self.get_body_argument("Migaku-Accept-Data", default=None)
        if received_data:
            self.handle_data_from_card_creator(received_data)
            return

        note_id = self.get_body_argument("searchNote", default=None)
        if note_id:
            self.search_note_id(note_id)
            return

        card = self.get_body_argument("card", default=None)
        if card:
            self.create_card(card)
            return

        definitions = self.get_body_argument("Migaku-Deliver-Definitions", default=None)
        if definitions and not msg_id is None:
            self.handle_definitions(msg_id, definitions)
            return

        self.finish("Invalid request.")

    def create_card(self, card_data_json):
        card_data = json.loads(card_data_json)

        note_type_id = card_data["noteTypeId"]
        note_type = aqt.mw.col.models.get(note_type_id)
        deck_id = card_data["deckId"]

        note = Note(aqt.mw.col, note_type)

        for field in card_data["fields"]:
            if "content" in field and field["content"]:
                content = field["content"]
                field_name = field["name"]
                content = self.post_process_text(content, field_name)
                note[field_name] = content

        tags = card_data.get("tags")
        if tags:
            note.set_tags_from_str(tags)

        note.model()["did"] = int(deck_id)
        aqt.mw.col.addNote(note)
        aqt.mw.col.save()
        aqt.mw.taskman.run_on_main(aqt.mw.reset)

        handle_files(self.request.files)

        self.finish(json.dumps({"id": note.id}))

    def handle_definitions(self, msg_id, definition_data):
        definitions = json.loads(definition_data)
        handle_files(self.request.files)
        self.connection._recv_data(
            {"id": msg_id, "msg": "Migaku-Deliver-Definitions", "data": definitions}
        )
        self.finish("Received defintions from card creator.")

    def handle_data_from_card_creator(self, jsonData):
        r = self._handle_data_from_card_creator(jsonData)
        self.finish(r)

    def _handle_data_from_card_creator(self, jsonData):
        data = json.loads(jsonData)

        data_type = data.get("dataType")

        if not data_type:
            return "No data_type"

        templates = data["templates"]
        default_templates = data["defaultTemplates"]

        info = get_current_note_info()

        if not info:
            return "No current note."

        note = info["note"]

        note_type = note.note_type()

        if not note_type:
            return "Current note has no valid note_type."

        note_name = str(note_type.get("name", ""))
        note_ident = str(note_type.get("id", "")) + note_name
        note_template = templates.get(note_ident)
        if not note_template:
            note_template = default_templates.get(note_name)

        if not note_template:
            return "No template for current note."

        field_name, syntax = template_find_field_name_and_syntax_for_data_type(
            note_template, data_type
        )

        if field_name is None or syntax is None:
            return "No field name or syntax for data type."

        if syntax:
            text = data["parsed"]
        else:
            text = data["text"]
        text = self.post_process_text(text, field_name)

        if not field_name:
            return "No field for data_type found for current note"

        handle_files(self.request.files)

        field_contents = note[field_name].rstrip()
        if field_contents:
            field_contents = field_contents + "<br><br>" + text
        else:
            field_contents = text
        note[field_name] = field_contents

        def update():
            # runs GUI code, so it needs to run on main thread
            if "editor" in info:
                editor = info["editor"]
                editor.loadNote()
                if not editor.addMode:
                    editor._save_current_note()

            if "reviewer" in info:
                # NOTE: cannot use aqt.operations.update_note as it invalidates mw
                note.flush()
                aqt.mw.col.save()
                reviewer_reshow(info["reviewer"], mute=True)

        aqt.mw.taskman.run_on_main(update)
        return "Added data to note."

    def handle_audio_delivery(self, text):
        handle_files(self.request.files)
        print("Audio was received by anki.")
        print(text)
        self.finish("Audio was received by anki.")

    def handle_no_audio_results(self):
        print("No audio was delivered to anki.")
        self.finish("No audio was delivered to anki.")

    def search_note_id(self, note_id):
        search_str = f'"nid:{note_id}"'
        aqt.mw.taskman.run_on_main(lambda: util.open_browser(search_str))

    def post_process_text(self, text, field_name):
        def conv_mp3(match):
            return "[sound:" + match.group(1) + ".mp3]"

        if config.get("convert_audio_mp3", True):
            text = self.TO_MP3_RE.sub(conv_mp3, text)

        if (
            config.get("remove_sentence_linebreaks", False)
            and "sentence" in field_name.lower()
        ):
            repl = config.get("sentence_linebreak_replacement", "")
            text = self.BR_RE.sub(repl, text)

        for data in config.get("field_regex", []):
            if field_name in data["field_names"]:
                regex = data["regex"]
                repl = data["replacement"]
                text = re.sub(regex, repl, text)

        return text


def template_find_field_name_and_syntax_for_data_type(template, data_type):
    for field_name, field_data in template.items():
        if isinstance(field_data, dict):
            field_data_type = field_data.get("dataType", {}).get("key")
            if field_data_type and field_data_type == data_type:
                syntax = field_data.get("syntax", False)
                return field_name, syntax
    return None, None
