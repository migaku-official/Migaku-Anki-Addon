from dataclasses import dataclass
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
    targetWord: str
    sentence: str
    translation: str
    definitions: str
    sentenceAudio: list[AudioAsset]
    wordAudio: list[AudioAsset]
    images: list[ImageAsset]
    exampleSentences: str
    notes: str
