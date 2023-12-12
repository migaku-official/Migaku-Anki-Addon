from dataclasses import dataclass, field
from typing import Optional

# From media.types


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
    sentenceAudio: list[AudioAsset] = field(default_factory=lambda: [])
    wordAudio: list[AudioAsset] = field(default_factory=lambda: [])
    images: list[ImageAsset] = field(default_factory=lambda: [])
    exampleSentences: str = ""
    notes: str = ""


def card_fields_from_dict(d: dict[str, any]):
    sentenceAudios = [AudioAsset(**a) for a in d.get("sentenceAudio", [])]

    for audio in sentenceAudios:
        print("audio", audio)

    return CardFields(
        targetWord=d.get("targetWord", ""),
        sentence=d.get("sentence", ""),
        translation=d.get("translation", ""),
        definitions=d.get("definitions", ""),
        sentenceAudio=[sentenceAudios],
        wordAudio=[AudioAsset(**a) for a in d.get("wordAudio", [])],
        images=[ImageAsset(**a) for a in d.get("images", [])],
        exampleSentences=d.get("exampleSentences", ""),
        notes=d.get("notes", ""),
    )
