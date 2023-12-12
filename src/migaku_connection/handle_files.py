from pydub import AudioSegment
import time
import os

import aqt

from .. import config
from .. import util

image_formats = ["jpg", "gif", "png"]
audio_formats = ["mp3", "ogg", "wav"]


def move_file_to_media_dir(file_body, filename):
    file_path = util.col_media_path(filename)
    with open(file_path, "wb") as file_handle:
        file_handle.write(file_body)


def move_file_to_tmp_dir(file_body, filename):
    file_path = util.tmp_path(filename)
    with open(file_path, "wb") as file_handle:
        file_handle.write(file_body)


def check_file_exists(source):
    now = time.time()
    while True:
        if os.path.exists(source):
            return True
        if time.time() - now > 15:
            return False


def move_extension_mp3_to_media_folder(source, filename):
    path = util.col_media_path(filename)
    aqt.mw.migaku_connection.ffmpeg.call("-i", source, path)


def move_extension_mp3_normalize_to_media_folder(source, filename):
    path = util.col_media_path(filename)

    def match_target_amplitude(sound, target_dBFS):
        change_in_dBFS = target_dBFS - sound.dBFS
        return sound.apply_gain(change_in_dBFS)

    sound = AudioSegment.from_file(source)
    normalized_sound = match_target_amplitude(sound, -25.0)
    with open(path, "wb") as file:
        normalized_sound.export(file, format="mp3")


def alert(msg: str):
    aqt.mw.taskman.run_on_main(util.show_info(msg, "Condensed Audio Export"))


def handle_audio_file(file, filename, suffix):
    if config.get("normalize_audio", True) or (
        config.get("convert_audio_mp3", True) and suffix != "mp3"
    ):
        move_file_to_tmp_dir(file, filename)
        audio_temp_path = util.tmp_path(filename)
        if not check_file_exists(audio_temp_path):
            alert(filename + " could not be converted to an mp3.")
            return
        filename = filename[0:-3] + "mp3"
        if config.get("normalize_audio", True):
            move_extension_mp3_normalize_to_media_folder(audio_temp_path, filename)
        else:
            move_extension_mp3_to_media_folder(audio_temp_path, filename)
    else:
        print("moving audio file")
        move_file_to_media_dir(file, filename)


def handle_files(file_dict, only_move=False):
    if not file_dict:
        return

    for _, sub_file_dicts in file_dict.items():
        sub_file_dict = sub_file_dicts[0]
        file_name = sub_file_dict["filename"]
        file_body = sub_file_dict["body"]

        suffix = file_name[-3:]

        if suffix in image_formats or only_move:
            move_file_to_media_dir(file_body, file_name)
        elif suffix in audio_formats:
            handle_audio_file(file_body, file_name, suffix)
