from dataclasses import dataclass
from typing import Union, Optional

# From media.types

AudioInput = Union[str, 'HTMLAudioElement']

@dataclass
class AudioAsset():
  id: str
  title: str
  input: AudioInput
  r2Url: Optional[str]

@dataclass
class ImageAsset():
  id: str
  title: str
  src: str
  alt: str
  r2Url: Optional[str]

@dataclass
class CardFields():
  targetWord: str
  sentence: str
  translation: str
  definitions: str
  sentenceAudio: AudioAsset[]
  wordAudio: AudioAsset[]
  images: ImageAsset[]
  exampleSentences: str
  notes: str
