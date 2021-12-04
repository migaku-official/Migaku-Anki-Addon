from .migaku_http_handler import MigakuHTTPHandler
from os.path import join, exists
import time
import subprocess
from anki.notes import Note
import json


import re
import aqt

from .. import config
from .. import util
from ..inplace_editor import reviewer_reshow


class CardCreator(MigakuHTTPHandler):

    image_formats = ['jpg', 'gif', 'png']
    audio_formats = ['mp3', 'ogg', 'wav']

    TO_MP3_RE = re.compile(r'\[sound:(.*?)\.(wav|ogg)\]')


    def post(self):

        if not self.check_version():
            self.finish('Card could not be created: Version mismatch')
            return

        msg_id = self.get_body_argument('id', default=None)
        if not msg_id is None:
            try:
                msg_id = int(msg_id)
            except ValueError:
                msg_id = None

        received_audio = self.get_body_argument('Migaku-Deliver-Audio', default=None)
        if received_audio:
            self.handle_audio_delivery(received_audio)
            return

        no_audio_available = self.get_body_argument('Migaku-No-Audio-Found', default=None)
        if no_audio_available:
            self.handle_no_audio_results()
            return

        received_data = self.get_body_argument('Migaku-Accept-Data', default=None)
        if received_data:
            self.handle_data_from_card_creator(received_data)
            return

        note_id = self.get_body_argument('searchNote', default=None)
        if note_id:
            self.search_note_id(note_id)
            return

        card = self.get_body_argument('card', default=None)
        if card:
            self.create_card(card)
            return

        definitions = self.get_body_argument('Migaku-Deliver-Definitions', default=None)
        if definitions and not msg_id is None:
            self.handle_definitions(msg_id, definitions)
            return

        self.finish('Invalid request.')


    def create_card(self, card_data_json):
        card_data = json.loads(card_data_json)

        note_type_id = card_data['noteTypeId']
        note_type = aqt.mw.col.models.get(note_type_id)
        deck_id = card_data['deckId']

        note = Note(aqt.mw.col, note_type)

        convert_to_mp3 = config.get('convert-to-mp3', False)

        for field in card_data['fields']:
            if 'content' in field and field['content']:
                content = field['content']
                field_name = field['name']

                if convert_to_mp3:
                    content = self.convert_to_mp3(content)

                note[field_name] = content

        tags = card_data.get('tags')
        if(tags):
            note.set_tags_from_str(tags)

        note.model()['did'] = int(deck_id)
        aqt.mw.col.addNote(note)
        aqt.mw.col.save()
        aqt.mw.taskman.run_on_main(aqt.mw.reset)

        self.handle_files(self.request.files, convert_to_mp3)

        self.finish(json.dumps({'id': note.id}))


    def handle_definitions(self, msg_id, definition_data):
        definitions = json.loads(definition_data)
        convert_to_mp3 = config.get('convert-to-mp3', False)
        self.handle_files(self.request.files, convert_to_mp3)
        self.connection._recv_data({
            'id': msg_id,
            'msg': 'Migaku-Deliver-Definitions',
            'data': definitions
        })
        self.finish('Received defintions from card creator.')


    def move_file_to_media_dir(self, file_body, filename):
        file_path = util.col_media_path(filename)
        with open(file_path, 'wb') as file_handle:
            file_handle.write(file_body)


    def move_file_to_tmp_dir(self, file_body, filename):
        file_path = util.tmp_path(filename)
        with open(file_path, 'wb') as file_handle:
            file_handle.write(file_body)


    def handle_files(self, file_dict, convert_to_mp3):

        if file_dict:

            for name_internal, sub_file_dicts in file_dict.items():
                sub_file_dict = sub_file_dicts[0]
                file_name = sub_file_dict['filename']
                file_body = sub_file_dict['body']

                suffix = file_name[-3:]

                if suffix in self.image_formats:
                    self.move_file_to_media_dir(file_body, file_name)

                elif suffix in self.audio_formats:
                    self.handleAudioFile(file_body, file_name, suffix, convert_to_mp3)


    def handleAudioFile(self, file, filename, suffix, convert_to_mp3):
        if convert_to_mp3 and suffix != 'mp3':
            print("converting to mp3")
            self.move_file_to_tmp_dir(file, filename)
            audioTempPath = join(self.tempDirectory, filename)
            if not self.checkFileExists(audioTempPath):
                self.alert(filename + " could not be converted to an mp3.")
                return
            filename = filename[0:-3] + "mp3"
            self.moveExtensionMp3ToMediaFolder(audioTempPath, filename)

        else:
            print("moving audio file")
            self.move_file_to_media_dir(file, filename)


    def checkFileExists(self, source):
        now = time.time()
        while True:
            if exists(source):
                return True
            if time.time() - now > 15:
                return False


    def moveExtensionMp3ToMediaFolder(self, source, filename):
        path = join(aqt.mw.col.media.dir(), filename)
        self.connection.ffmpeg.call('-i', source, path)


    def handle_data_from_card_creator(self, jsonData):
        r = self._handle_data_from_card_creator(jsonData)
        self.finish(r)

    def _handle_data_from_card_creator(self, jsonData):
        data = json.loads(jsonData)

        data_type = data.get('dataType')

        if not data_type:
            return 'No data_type'

        text = data['text']
        templates = data['templates']

        convert_to_mp3 = config.get('convert-to-mp3', False)
        if convert_to_mp3:
            text = self.text_sound_to_mp3(text)

        current_note_info = get_current_note_info()

        if not current_note_info:
            return 'No current note.'

        note = current_note_info['note']

        note_type = note.note_type()

        if not note_type:
            return 'Current note has no valid note_type.'

        note_ident = str(note_type.get('id', '')) + str(note_type.get('name', ''))
        note_template = templates.get(note_ident)

        if not note_template:
            return 'No template for current note.'

        field_name = template_find_field_name_for_data_type(note_template, data_type)

        if not field_name:
            return 'No field for data_type found for current note'

        self.handle_files(self.request.files, convert_to_mp3)

        field_contents = note[field_name].rstrip()
        if field_contents:
            field_contents = field_contents + '<br><br>' + text
        else:
            field_contents = text
        note[field_name] = field_contents

        note.flush()
        aqt.mw.col.save()

        if 'editor' in current_note_info:
            current_note_info['editor'].loadNote()
        if 'reviewer' in current_note_info:
            reviewer_reshow(current_note_info['reviewer'], mute=True)

        return 'Added data to note.'


    def handle_audio_delivery(self, text):
        convert_to_mp3 = config.get('convert-to-mp3', False)
        self.handle_files(self.request.files, convert_to_mp3)
        print('Audio was received by anki.')
        print(text)
        self.finish('Audio was received by anki.')


    def handle_no_audio_results(self):
        print("No audio was delivered to anki.")
        self.finish("No audio was delivered to anki.")


    def search_note_id(self, note_id):
        search_str = F'"nid:{note_id}"'
        aqt.mw.taskman.run_on_main(
            lambda: util.open_browser(search_str)
        )

    def text_sound_to_mp3(self, text):
        def conv(match):
            return '[sound:' + match.group(1) + '.mp3]'

        return self.TO_MP3_RE.sub(conv, text)



def template_find_field_name_for_data_type(template, data_type):
    for field_name, field_data in template.items():
        if isinstance(field_data, dict):
            field_data_type = field_data.get('dataType', {}).get('key')
            if field_data_type and field_data_type == data_type:
                return field_name
    return None



# this is dirty...

from anki.hooks import wrap
from aqt.editor import Editor

current_editors = []

def set_current_editor(editor: aqt.editor.Editor):
    global current_editors
    remove_editor(editor)
    current_editors.append(editor)

def remove_editor(editor: aqt.editor.Editor):
    global current_editors
    current_editors = [e for e in current_editors if e != editor]


aqt.gui_hooks.editor_did_init.append(set_current_editor)
Editor.cleanup = wrap(Editor.cleanup, remove_editor, 'before')


def get_current_note_info() -> Note:
    for editor in reversed(current_editors):
        if editor.note:
            return { 'note': editor.note, 'editor': editor }
    if aqt.mw.reviewer and aqt.mw.reviewer.card:
        note = aqt.mw.reviewer.card.note()
        if note:
            return { 'note': note, 'reviewer': aqt.mw.reviewer }
    return None
