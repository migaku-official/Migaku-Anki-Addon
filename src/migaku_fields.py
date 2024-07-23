import re
from typing import Literal

from .config import get
import anki


def infer_migaku_type(
    name: str,
) -> Literal[
    "none",
    "sentence",
    "targetWord",
    "translation",
    "sentenceAudio",
    "wordAudio",
    "images",
    "definitions",
    "exampleSentences",
    "notes",
]:
    if re.search(
        r"(audio|音声|音频|오디오|audio|áudio|audio|audio|áudio)", name, re.IGNORECASE
    ):
        if re.search(
            r"(Is Audio Card|音声カード|音频卡|오디오 카드|tarjeta de audio|cartão de áudio|carte audio|audio karte|cartão de áudio)",
            name,
            re.IGNORECASE,
        ):
            return "none"
        elif re.search(
            r"(sentence|文|句|문장|frase|phrase|satz|frase)", name, re.IGNORECASE
        ):
            return "sentenceAudio"
        else:
            return "wordAudio"

    if re.search(
        r"(word|単語|单词|단어|palabra|palavra|mot|wort|palavra)", name, re.IGNORECASE
    ):
        return "targetWord"

    if re.search(
        r"(image|画像|图片|이미지|imagen|imagem|image|bild|imagem)", name, re.IGNORECASE
    ):
        return "restImages"
    if re.search(
        r"(screenshot|スクリーンショット|截图|스크린샷|capturas de pantalla|capturas de tela|captures d'écran|bildschirmfotos|capturas de tela)",
        name,
        re.IGNORECASE,
    ):
        return "firstImage"

    if re.search(
        r"(example|例|例句|例子|예|ejemplo|exemplo|exemple|beispiel|exemplo)",
        name,
        re.IGNORECASE,
    ):
        return "exampleSentences"

    if re.search(r"(sentence|文|句|문장|frase|phrase|satz|frase)", name, re.IGNORECASE):
        return "sentence"

    if re.search(
        r"(translation|訳|译|번역|traducción|traduction|übersetzung|tradução)",
        name,
        re.IGNORECASE,
    ):
        return "translation"

    if re.search(
        r"(definition|定義|定义|정의|definición|definição|définition|definition|definição)",
        name,
        re.IGNORECASE,
    ):
        return "definitions"
    if re.search(r"(note|ノート|笔记|노트|nota|nota|note|notiz|nota)", name, re.IGNORECASE):
        return "notes"
    return "none"


def get_migaku_fields(nt: anki.models.NoteType):
    migaku_fields = get("migakuFields", {})
    data = migaku_fields.get(str(nt["id"]), {})

    field_names = [field["name"] for field in nt["flds"]]

    for field_name in field_names:
        if field_name not in data:
            data[field_name] = infer_migaku_type(field_name)

    for field_name in list(data.keys()):
        if field_name not in field_names:
            del data[field_name]

    return data
