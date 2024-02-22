from base64 import b64decode
from dataclasses import dataclass, field
import re
from typing import Optional
import requests

from .migaku_connection.handle_files import move_file_to_media_dir


@dataclass
class AudioAsset:
    id: str
    title: str
    input: str
    r2Url: Optional[str] = None


@dataclass
class ImageAsset:
    id: str
    title: str
    src: str
    alt: str
    r2Url: Optional[str] = None


@dataclass
class CardFields:
    targetWord: str = ""
    targetWordNoSyntax: str = ""
    sentence: str = ""
    sentenceNoSyntax: str = ""
    translation: str = ""
    definitions: str = ""
    sentenceAudio: str = ""
    wordAudio: str = ""
    images: str = ""
    firstImage: str = ""
    restImages: str = ""
    exampleSentences: str = ""
    notes: str = ""


def process_image_asset(image: ImageAsset):
    name = f"{image.id}.webp"

    if image.src.startswith("data:image/webp;base64,"):
        data = image.src.split(",", 1)[1]
        move_file_to_media_dir(b64decode(data), name)
    elif image.input.startswith("http"):
        data = requests.get(image.src, allow_redirects=True)
        move_file_to_media_dir(data.content, name)

    return f"<img src='{name}' />"


def process_audio_asset(audio: AudioAsset):
    name = f"{audio.id}.m4a"

    if audio.input.startswith("data:audio/mp4;base64,"):
        data = audio.input.split(",", 1)[1]
        move_file_to_media_dir(b64decode(data), name)
    elif audio.input.startswith("http"):
        data = requests.get(audio.input, allow_redirects=True)
        move_file_to_media_dir(data.content, name)

    return f"[sound:{name}]"

REMOVE_RE_EURO = re.compile(r"(\[(?!sound:).*?\])(?![^{]*})")
REMOVE_RE_CJK = re.compile(r"( +|\[(?!sound:).*?\])(?![^{]*})")

def remove_syntax(text: str, has_cjk: bool):
    return REMOVE_RE_CJK.sub("", text) if has_cjk else REMOVE_RE_EURO.sub("", text)

def card_fields_from_dict(data: dict[str, any]):
    br = "\n<br>\n"

    sentenceAudios = br.join(
        [
            process_audio_asset(AudioAsset(**audio))
            for audio in data.get("sentenceAudio", [])
        ]
    )
    wordAudios = br.join(
        [
            process_audio_asset(AudioAsset(**audio))
            for audio in data.get("wordAudio", [])
        ]
    )

    images = [process_image_asset(ImageAsset(**img)) for img in data.get("images", [])]

    firstImage = images[0] if images else ""
    restImages = br.join(images[1:])
    imagess = br.join(images)

    targetWord = data.get("targetWord", "")
    cjk_found = len(re.findall(r'[\u2e80-\u9fff\uac00-\ud7ff]', targetWord)) > 0
    print('foo', cjk_found, targetWord)

    targetWordNoSyntax = remove_syntax(targetWord, cjk_found)

    sentence = data.get("sentence", "")
    sentenceNoSyntax = remove_syntax(sentence, cjk_found)

    return CardFields(
        targetWord=targetWord,
        targetWordNoSyntax=targetWordNoSyntax,
        sentence=sentence,
        sentenceNoSyntax=sentenceNoSyntax,
        translation=data.get("translation", ""),
        definitions=data.get("definitions", ""),
        sentenceAudio=sentenceAudios,
        wordAudio=wordAudios,
        images=imagess,
        firstImage=firstImage,
        restImages=restImages,
        exampleSentences=data.get("exampleSentences", ""),
        notes=data.get("notes", ""),
    )
