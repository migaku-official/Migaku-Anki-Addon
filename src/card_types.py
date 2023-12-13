from base64 import b64decode
from dataclasses import dataclass, field
from typing import Optional

from .migaku_connection.handle_files import move_file_to_media_dir


@dataclass
class AudioAsset:
    id: str
    title: str
    input: str
    r2Url: Optional[str]


@dataclass
class ImageAsset:
    id: str
    title: str
    src: str
    alt: str
    r2Url: Optional[str]


@dataclass
class CardFields:
    targetWord: str = ""
    sentence: str = ""
    translation: str = ""
    definitions: str = ""
    sentenceAudio: str = ""
    wordAudio: str = ""
    images: str = ""
    exampleSentences: str = ""
    notes: str = ""


def process_image_asset(image: ImageAsset):
    data = image.src.split(",", 1)[1]
    name = f"{image.title}-{image.id}.webp"
    move_file_to_media_dir(b64decode(data), name)
    return f"<img src='{name}' alt='{image.alt}' />"


def process_audio_asset(audio: AudioAsset):
    data = audio.input.split(",", 1)[1]
    name = f"{audio.title}-{audio.id}.m4a"
    move_file_to_media_dir(b64decode(data), name)
    return f"[sound:{name}]"


def card_fields_from_dict(d: dict[str, any]):
    br = "\n<br>\n"
    sentenceAudios = br.join(
        [process_audio_asset(AudioAsset(**a)) for a in d.get("sentenceAudio", [])]
    )
    wordAudios = br.join(
        [process_audio_asset(AudioAsset(**a)) for a in d.get("wordAudio", [])]
    )
    imagess = br.join(
        [process_image_asset(ImageAsset(**a)) for a in d.get("images", [])]
    )

    return CardFields(
        targetWord=d.get("targetWord", ""),
        sentence=d.get("sentence", ""),
        translation=d.get("translation", ""),
        definitions=d.get("definitions", ""),
        sentenceAudio=sentenceAudios,
        wordAudio=wordAudios,
        images=imagess,
        exampleSentences=d.get("exampleSentences", ""),
        notes=d.get("notes", ""),
    )
