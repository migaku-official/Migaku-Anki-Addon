import os
import uuid
import re
import ssl
import urllib3
import requests
import time
import urllib.parse
import subprocess
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
import tornado.ioloop
import shutil

import aqt
from anki.utils import is_mac

from .. import note_type_mgr
from ..languages import Languages
from ..util import tmp_path

# supports both src="" and src=''
IMG_RE = re.compile(r"<img (.*?)src=(?:\"|')(.*?)(?:\"|')(.*?)>", re.IGNORECASE)
SOUND_RE = re.compile(r"\[sound:(.*?)\]")


auto_field_map = [
    ("Sentence", "Sentence"),
    ("Translation", "Translated Sentence"),
    ("Target Word", "Word"),
    ("Definitions", "Definitions"),
    ("Screenshot", "Images"),
    ("Sentence Audio", "Sentence Audio"),
    ("Word Audio", "Word Audio"),
    ("Images", "Images"),
    ("Example Sentences", "Example Sentences"),
]


async def build_syntax_cache(entries):
    if not aqt.mw.migaku_connection.is_connected() or not entries:
        return {}

    entries_list = list(entries)
    lang = entries_list[0][0]

    t = time.time()

    lock = Lock()

    result = {}

    def on_done(syntax_data):
        nonlocal result
        if isinstance(syntax_data, list) and len(syntax_data) == len(entries_list):
            result = {e: syntax_data[i]["42"] for i, e in enumerate(entries_list)}
        lock.release()

    def on_error():
        lock.release()

    # beautiful
    def do_request():
        def do_main():
            aqt.mw.migaku_connection.request_syntax(
                [{"42": e[1]} for e in entries_list],
                lang,
                on_done=on_done,
                on_error=on_error,
            )

        lock.acquire()
        aqt.mw.taskman.run_on_main(do_main)
        lock.acquire()

    await tornado.ioloop.IOLoop.current().run_in_executor(None, do_request)

    print("syntax took", time.time() - t)

    return result


async def get_syntax(lang, text):
    if not aqt.mw.migaku_connection.is_connected():
        return None

    t = time.time()

    lock = Lock()

    result = None

    def on_done(syntax_data):
        nonlocal result
        if isinstance(syntax_data, list) and len(syntax_data) == 1:
            result = syntax_data[0].get("42")
        lock.release()

    def on_error():
        lock.release()

    # beautiful
    def do_request():
        def do_main():
            aqt.mw.migaku_connection.request_syntax(
                [{"42": text}], lang, on_done=on_done, on_error=on_error
            )

        lock.acquire()
        aqt.mw.taskman.run_on_main(do_main)
        lock.acquire()

    await tornado.ioloop.IOLoop.current().run_in_executor(None, do_request)

    print("syntax took", time.time() - t)

    return result


upload_host = "https://file-sync-worker-api.migaku.com/data/SRSMEDIA"
upload_num_threads = 25
upload_data_size = 0

# THe bundled version of requests on macOS causes issues with SSL :/
ssl_verify = False
ssl_warnings_disabled = False

use_curl = None
curl_path = None


def request_retry(method, url, **kwargs):
    global ssl_warnings_disabled

    if not ssl_verify and not ssl_warnings_disabled:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        ssl_warnings_disabled = True

    sleep_time = 0.25
    timeout_time = 10

    max_retries = kwargs.pop("max_retries", 5)

    for i in range(max_retries):
        try:
            r = requests.request(
                method=method,
                url=url,
                timeout=timeout_time,
                verify=ssl.CERT_NONE if not ssl_verify else None,
                **kwargs,
            )
        except requests.exceptions.Timeout:
            print(f"Request timeout ({i+1}): {method} {url}")
            time.sleep(sleep_time)
            sleep_time *= 2
            timeout_time *= 1.5
            continue

        if r.ok:
            return r

        # no point in retrying on client errors
        if r.status_code >= 400 and r.status_code < 500:
            print(f"Request failed (client error): {method} {url} -> {r.status_code}")
            return r

        print(f"Request failed ({i+1}): {method} {url} -> {r.status_code}")
        time.sleep(sleep_time)
        sleep_time *= 2

    return r


def put_with_curl(url, data):
    tmp = tmp_path(uuid.uuid4().hex)

    with open(tmp, "wb") as f:
        f.write(data)

    cmd = [curl_path, "-X", "PUT", "-T", tmp, url]
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    os.remove(tmp)

    return r.returncode


def _upload_media_single_attempt(fname, user_token, is_audio=False):
    global curl_path
    global use_curl

    if use_curl is None:
        use_curl = False
        if is_mac:
            curl_path = shutil.which("curl")
            if curl_path:
                use_curl = True

    headers = {"Authorization": f"Bearer {user_token}"}

    if fname.startswith("http"):
        r = request_retry("GET", fname, max_retries=2)
        if not r.ok:
            # ignore remote media that doesn't download correctly
            return None
        data = r.content
        url = urllib.parse.urlparse(fname)
        fname = os.path.basename(url.path)
    else:
        media_dir = aqt.mw.col.media.dir()
        path = os.path.join(media_dir, fname)
        if not os.path.exists(path):
            # ignore missing media
            return None
        with open(path, "rb") as file:
            data = file.read()

    in_path = tmp_path(fname)
    with open(in_path, "wb") as file:
        file.write(data)

    try:
        if fname.endswith(".webp") or fname.endswith(".m4a"):
            # if file is already in target format, use it directly
            with open(in_path, "rb") as file:
                data = file.read()
        elif is_audio:
            fname = os.path.splitext(fname)[0] + ".m4a"
            out_path = tmp_path(fname)
            # The arguments to ffmpeg are the same as in MM
            r = aqt.mw.migaku_connection.ffmpeg.call(
                "-y",
                "-i",
                in_path,
                "-vn",
                "-b:a",
                "128k",
                out_path,
            )
            if r != 0:
                # ignore failed conversions, most likely bad audio
                return None

            with open(out_path, "rb") as file:
                data = file.read()

        else:
            # We assume that if something is not audio, it is a picture
            fname = os.path.splitext(fname)[0] + ".webp"
            out_path = tmp_path(fname)

            # The arguments to ffmpeg are the same as in MM
            r = aqt.mw.migaku_connection.ffmpeg.call(
                "-y",
                "-i",
                in_path,
                "-vf",
                "scale='min(800,iw)':-1",
                out_path,
            )
            if r != 0:
                # ignore failed conversions, most likely bad audio
                return None

            with open(out_path, "rb") as file:
                data = file.read()
    except Exception as e:
        print(f"File conversion failed: {e}")
        # use original file in case of error
        with open(in_path, "rb") as file:
            data = file.read()

    quoted = urllib.parse.quote(fname)
    r = request_retry(
        "PUT",
        f"{upload_host}/{quoted}",
        headers=headers,
        data=data,
    )

    if not r.ok:
        raise Exception(f"upload failed, requests, {r.status_code}, {r.text}")

    upload_info = r.json()
    file_path = upload_info["filePath"]

    global upload_data_size
    upload_data_size += len(data)

    return "r2://" + file_path


def _upload_media(fname, user_token, is_audio=False, max_attempts=5):
    sleep_time = 0.25

    for i in range(max_attempts):
        try:
            return _upload_media_single_attempt(fname, user_token, is_audio)
        except Exception as e:
            print(f"WARNING: Upload failed ({i +1}):", e)

            if i == max_attempts - 1:
                # RIP
                raise e

            time.sleep(sleep_time)
            sleep_time *= 2

    return None


async def upload_media(fname, user_token, is_audio=False):
    return await tornado.ioloop.IOLoop.current().run_in_executor(
        None, _upload_media, fname, user_token, is_audio
    )


def _build_media_cache(media, user_token):
    r = {}

    def do_upload(fname, is_audio):
        r[fname] = _upload_media(fname, user_token, is_audio)

    with ThreadPoolExecutor(upload_num_threads) as executor:
        futures = []

        for fname, is_audio in media:
            futures.append(executor.submit(do_upload, fname, is_audio))

        for future in futures:
            future.result()

    return r


async def build_media_cache(media, user_token):
    return await tornado.ioloop.IOLoop.current().run_in_executor(
        None, _build_media_cache, media, user_token
    )


def nt_migaku_lang(nt):
    if not nt["name"].startswith(note_type_mgr.NOTE_TYPE_PREFIX):
        return None
    if not nt["css"].startswith(note_type_mgr.NOTE_TYPE_MARK_CSS):
        return None
    lang = note_type_mgr.nt_get_lang(nt)
    if not lang:
        return None
    nt_flds = nt["flds"]
    if len(lang.fields) != len(nt_flds):
        return None
    for fld_name in lang.fields:
        if not any(f["name"] == fld_name for f in nt_flds):
            return None
    return lang


async def handle_card(
    cid,
    user_token=None,
    srs_today=None,
    lang=None,
    mappings=None,
    card_types=None,
    preview=False,
    gather_media=None,
    gather_syntax=None,
    media_cache=None,
    syntax_cache=None,
):
    if not mappings:
        mappings = []
    if not card_types:
        card_types = []

    if not media_cache:
        media_cache = {}
    if not syntax_cache:
        syntax_cache = {}

    card = aqt.mw.col.get_card(cid)
    note = card.note()
    note_type = note.note_type()

    dst_id = None
    field_map = None

    # try to use automatic mapping
    nt_lang = nt_migaku_lang(note_type)  # only set if note type is a Migaku note type
    if nt_lang:
        sub_id = 0
        try:
            if note["Is Vocabulary Card"]:
                sub_id += 1
            if note["Is Audio Card"]:
                sub_id += 2
        except KeyError:
            pass
        for ctype in card_types:
            if (
                ctype["lang"] == nt_lang.code.split("_")[0]
                and ctype["id"] & 0xF == sub_id
            ):
                dst_id = ctype["id"]
                field_map = []
                for src, dst in auto_field_map:
                    for i, field in enumerate(note_type["flds"]):
                        if field["name"] == src:
                            src_idx = i
                            break
                    else:
                        continue
                    for i, field in enumerate(ctype["fields"]):
                        if field["name"] == dst:
                            dst_idx = i
                            break
                    else:
                        continue
                    field_map.append(
                        {
                            "srcIdx": src_idx,
                            "dstIdx": dst_idx,
                        }
                    )
                break

    # Also set if note type is not a Migaku note type but has the JS applied
    lang_obj = nt_lang or note_type_mgr.nt_get_lang(note_type)
    if lang_obj:
        if lang_obj.code.split("_")[0] != lang:
            print(
                f"skipped {card.id}: note type language does not match current language",
                lang_obj.code,
                lang,
            )
            return None
    if lang_obj is None:
        for lang_candidate in Languages:
            if lang_candidate.code.split("_")[0] == lang:
                lang_obj = lang_candidate
                break
    if lang_obj is None:
        print(f"skipped {card.id}: no anki side language found")
        return None

    # try to use manual mapping
    if not dst_id:
        # get the correct mapping
        src_id = f"{note.mid}\u001f{card.ord}"

        for mapping in mappings:
            if mapping["srcId"] == src_id:
                field_map = mapping["fields"]
                dst_id = mapping["dstId"]
                break

    # no usable mapping found
    if not dst_id:
        print(f"skipped {card.id}: no mapping for {src_id}")
        return None

    # get the correct card type
    for ctype in card_types:
        if ctype["id"] == dst_id:
            card_type = ctype
            break
    else:
        print(f"skipped {card.id}: no card type for {dst_id}")
        return None

    data = [""] * len(card_type["fields"])

    for fm in field_map:
        src_idx = fm["srcIdx"]
        dst_idx = fm["dstIdx"]
        if data[dst_idx]:
            data[dst_idx] += "<br>"
        data[dst_idx] += note.fields[src_idx].strip()

    # recovered audio/images get appended to the first fitting field
    recovered_audio_src = []
    recovered_images_src = []

    for i, field in enumerate(card_type["fields"]):
        if not field["type"].startswith("IMAGE"):
            for _, src, _ in IMG_RE.findall(data[i]):
                recovered_images_src.append(src)
            data[i] = IMG_RE.sub("", data[i])
        if not field["type"].startswith("AUDIO"):
            for src in SOUND_RE.findall(data[i]):
                recovered_audio_src.append(src)
            data[i] = SOUND_RE.sub("", data[i])

    # upload media, including recovered, format as required by field type
    for i, field in enumerate(card_type["fields"]):
        if field["type"].startswith("IMAGE"):
            hashes = []
            srcs = [src for _, src, _ in IMG_RE.findall(data[i])] + recovered_images_src
            recovered_images_src = []
            for src in srcs:
                if preview:
                    hashes.append(aqt.mw.serverURL() + src)
                else:
                    if gather_media is None:
                        hash_ = media_cache.get(src)
                        if hash_ is None:
                            hash_ = await upload_media(src, user_token)
                        if hash_:
                            hashes.append(hash_)
                    else:
                        gather_media.add((src, False))
            if hashes:
                data[i] = "|".join(hashes)

        elif field["type"].startswith("AUDIO"):
            hashes = []
            srcs = SOUND_RE.findall(data[i]) + recovered_audio_src
            recovered_audio_src = []
            for src in srcs:
                if preview:
                    hashes.append(aqt.mw.serverURL() + src)
                else:
                    if gather_media is None:
                        hash_ = media_cache.get(src)
                        if hash_ is None:
                            hash_ = await upload_media(src, user_token, is_audio=True)
                        if hash_:
                            hashes.append(hash_)
                    else:
                        gather_media.add((src, True))
            if hashes:
                data[i] = "|".join(hashes)

        elif field["type"] == "SYNTAX":
            if data[i].strip() and not "[" in data[i]:
                if gather_syntax is None:
                    syntax = syntax_cache.get((lang, data[i]))
                    if syntax is None:
                        # proc = await get_syntax(lang, data[i])
                        # print('proc', proc)

                        # We do the syntax processing in the core now
                        syntax = data[i]
                        # print('unproc', data[i])
                    if syntax:
                        data[i] = syntax
                else:
                    gather_syntax.add((lang, data[i]))
        else:
            data[i] = lang_obj.remove_syntax(data[i])

    if (not gather_syntax is None) or (not gather_media is None):
        return None


    card_data = {
        "deckId": 0,  # set by core
        "typeId": dst_id,
        "fields": data,
    }

    # preview cards are not supplied with any scheduling data
    if preview:
        return card_data

    # New or learning
    if card.queue == 0 or card.queue == 1:
        due = 0
        interval = 0

    # Review
    elif card.queue == 2 or card.queue == 3:
        offset = max(0, card.due - aqt.mw.col.sched.today)
        due = srs_today + offset
        interval = max(1, card.ivl)

    else:
        print(f"skipped {card.id}: unsupported queue {card.queue}")
        return None

    return {
        "first": card_data,
        "second": {
            "due": due,
            "interval": interval,
        },
    }
