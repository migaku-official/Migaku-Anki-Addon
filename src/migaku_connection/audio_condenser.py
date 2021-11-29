import os
import shutil
import re

import aqt

from .migaku_http_handler import MigakuHTTPHandler

from .. import config
from .. import util



class AudioCondenser(MigakuHTTPHandler):

    def get(self):
        self.finish('ImportHandler')


    def can_condense(self):
        return self.connection.ffmpeg.is_available()


    def condense_audio(self, filename, timestamp):
        segments_dir = util.tmp_path(timestamp)
        if os.path.exists(segments_dir):
            condensed_dir = config.get('condensed-audio-dir')
            
            segment_names = [f for f in os.listdir(segments_dir)]
            segment_names.sort()

            segment_list_path = os.path.join(segments_dir, 'list.txt')
            with open(segment_list_path, 'w+') as f:
                for s in segment_names:
                    f.write('file \'{}\'\n'.format(os.path.join(segments_dir, s)))

            out_filename = self.clean_filename(filename + '\n') + '-condensed.mp3'
            out_path = os.path.join(condensed_dir, out_filename)

            self.connection.ffmpeg.call(
                '-y', '-f', 'concat', '-safe', '0', '-i', segment_list_path, '-write_xing', '0', out_path
            )

            shutil.rmtree(segments_dir, ignore_errors=True)

            if not config.get('disable-condensed-audio-messages', False):
                alert('A Condensed Audio File has been generated.\n\n The file: ' + out_filename + '\nhas been created in dir: ' + condensed_dir)


    def clean_filename(self, filename):
        return re.sub(r'[\n:\'\":/\|?*><!]', '', filename).strip()


    def post(self):
        if self.check_version():
            timestamp = str(self.get_body_argument('timestamp', default=0))
            finished = self.get_body_argument('finished', default=False)

            if finished:
                filename = self.get_body_argument('filename', default=None)
                if not filename:
                    filename = timestamp
                self.condense_audio(filename, timestamp)
                removeCondensedAudioInProgressMessage()
                self.finish('Condensing finished.')
                return

            else:
                condensed_dir = config.get('condensed-audio-dir')
                if not condensed_dir:
                    alert('You must specify a Condensed Audio Save Location.\n\nYou can do this by:\n1. Navigating to Migaku->Dictionary Settings in Anki\'s menu bar.\n2. Clicking \'Choose Directory\' for the \'Condensed Audio Save Location\'  in the bottom right of the settings window.')
                    removeCondensedAudioInProgressMessage()
                    self.finish('Save location not set.')
                elif self.can_condense():
                    self.handle_request_audio_file(self.copy_file_to_condensed_audio_dir, timestamp)
                    add_condensed_audio_progress_msg()
                    self.finish('Exporting Condensed Audio')
                else:
                    alert('The FFMPEG media encoder must be installed in order to export condensedAudio.\n\nIn order to install FFMPEG please enable MP3 Conversion in the Dictionary Settings window and click \'Apply\'.\nFFMPEG will then be downloaded and installed automatically.')
                    removeCondensedAudioInProgressMessage()
                    self.finish('FFMPEG not installed.')
                return

        self.finish('Invalid Request')


    def handle_request_audio_file(self, copy_file_func, timestamp):
        if 'audio' in self.request.files:
            audio_file = self.request.files['audio'][0]
            audio_file_name = audio_file['filename']
            copy_file_func(audio_file, audio_file_name, timestamp)


    def copy_file_to_condensed_audio_dir(self, file, filename, timestamp):
        directory_path = util.tmp_path(timestamp)
        os.makedirs(directory_path, exist_ok=True)
        file_path = os.path.join(directory_path, filename)
        with open(file_path, 'wb') as f:
            f.write(file['body'])


def alert(msg: str):
    aqt.mw.taskman.run_on_main(
        util.show_into(msg, 'Condensed Audio Export')
    )


def add_condensed_audio_progress_msg():
    aqt.mw.taskman.run_on_main(
        lambda: aqt.mw.progress.start(
            label='Exporting Condensed Audio',
        )
    )

def removeCondensedAudioInProgressMessage():
    aqt.mw.taskman.run_on_main(
        lambda: aqt.mw.progress.finish()
    )
