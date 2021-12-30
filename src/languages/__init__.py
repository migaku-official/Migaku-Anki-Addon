from collections import OrderedDict
from typing import List
import re
import importlib

from .. util import addon_path, addon_web_uri


class FieldOption:

    def __init__(self, value: str, label: str):
        self.value = value
        self.label = label


class FieldSetting:

    def __init__(self, name: str, label: str, options: List[FieldOption]):
        self.name = name
        self.label = label
        self.options = options


class Language:

    BRACKET_REMOVE_RE = re.compile(r'\[(?!sound:).*?\]')

    def __init__(self, code: str, name_en: str, name_native: str, fields: List[str], field_settings: List[FieldSetting]):
        self.code = code
        self.name_en = name_en
        self.name_native = name_native
        self.fields = fields
        self.field_settings = field_settings

        try:
            self.util = importlib.import_module(F'.{self.code}', __name__)
        except ImportError:
            self.util = None

        if hasattr(self.util, 'remove_syntax'):
            self.remove_syntax_func = self.util.remove_syntax
        else:
            self.remove_syntax_func = self._remove_syntax_brackets

    def __repr__(self):
        return F'<Language {self.code}>'

    def file_path(self, *path_parts):
        return addon_path('languages', self.code, *path_parts)

    def web_uri(self, *path_parts):
        return addon_web_uri('languages', self.code, *path_parts)

    def add_syntax(self, text, on_done):
        raise NotImplementedError

    def remove_syntax(self, text):
        return self.remove_syntax_func(text)

    @classmethod
    def _remove_syntax_brackets(cls, text):
        return cls.BRACKET_REMOVE_RE.sub('', text)


class LanguagesMeta(type):

    def __new__(mcls, name, bases, attrs):
        mcls.entries = OrderedDict()

        for name, lang in attrs.items():
            if isinstance(lang, Language):
                mcls.entries[lang.code] = lang

        return super().__new__(mcls, name, bases, attrs)

    def __iter__(mcls):
        return (mcls.entries[code] for code in mcls.entries.keys())

    def __getitem__(mcls, key):
        return mcls.entries[key]

    def __len__(mcls):
        return len(mcls.entries)


class Languages(metaclass=LanguagesMeta):

    Cantonese = Language(
        name_en='Cantonese',
        name_native='粵語',
        code='yue',
        fields=[
            'Sentence',
            'Translation',
            'Target Word',
            'Definitions',
            'Screenshot',
            'Sentence Audio',
            'Word Audio',
            'Images',
            'Example Sentences',
            'Alternate Sentence',
            'Is Vocabulary Card',
            'Is Audio Card',
        ],
        field_settings=[
            FieldSetting('reading', 'Reading', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
                FieldOption('hover', 'On Hover'),
                FieldOption('hidden', 'Hidden'),
            ]),
            FieldSetting('tone-coloring', 'Tone Coloring', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
                FieldOption('hover', 'On Hover'),
            ]),
        ],
    )

    ChineseSimplified = Language(
        name_en='Chinese Simplified',
        name_native='汉语',
        code='zh_CN',
        fields=[
            'Sentence',
            'Translation',
            'Target Word',
            'Definitions',
            'Screenshot',
            'Sentence Audio',
            'Word Audio',
            'Images',
            'Example Sentences',
            'Alternate Sentence',
            'Is Vocabulary Card',
            'Is Audio Card',
        ],
        field_settings=[
            FieldSetting('reading', 'Reading', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
                FieldOption('hover', 'On Hover'),
                FieldOption('hidden', 'Hidden'),
            ]),
            FieldSetting('reading-type', 'Reading Type', [
                FieldOption('pinyin', 'Pinyin'),
                FieldOption('bopomofo', 'Bopomofo'),
            ]),
            FieldSetting('tone-coloring', 'Tone Coloring', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
                FieldOption('hover', 'On Hover'),
            ]),
        ],
    )

    ChineseTraditional = Language(
        name_en='Chinese Traditional',
        name_native='漢語',
        code='zh_TW',
        fields=[
            'Sentence',
            'Translation',
            'Target Word',
            'Definitions',
            'Screenshot',
            'Sentence Audio',
            'Word Audio',
            'Images',
            'Example Sentences',
            'Alternate Sentence',
            'Is Vocabulary Card',
            'Is Audio Card',
        ],
        field_settings=[
            FieldSetting('popup', 'Popup', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
            ]),
            FieldSetting('reading', 'Reading', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
                FieldOption('hover', 'On Hover'),
                FieldOption('hidden', 'Hidden'),
            ]),
            FieldSetting('reading-type', 'Reading Type', [
                FieldOption('bopomofo', 'Bopomofo'),
                FieldOption('pinyin', 'Pinyin'),
            ]),
            FieldSetting('tone-coloring', 'Tone Coloring', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
                FieldOption('hover', 'On Hover'),
            ]),
        ],
    )

    English = Language(
        name_en='English',
        name_native='English',
        code='en',
        fields=[
            'Sentence',
            'Translation',
            'Target Word',
            'Definitions',
            'Screenshot',
            'Sentence Audio',
            'Word Audio',
            'Images',
            'Example Sentences',
            'Is Vocabulary Card',
            'Is Audio Card',
        ],
        field_settings=[
            FieldSetting('popup', 'Popup', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
            ])
        ],
    )

    French = Language(
        name_en='French',
        name_native='Français',
        code='fr',
        fields=[
            'Sentence',
            'Translation',
            'Target Word',
            'Definitions',
            'Screenshot',
            'Sentence Audio',
            'Word Audio',
            'Images',
            'Example Sentences',
            'Is Vocabulary Card',
            'Is Audio Card',
        ],
        field_settings=[
            FieldSetting('popup', 'Popup', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
            ]),
            FieldSetting('gender-coloring', 'Gender Coloring', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
                FieldOption('hover', 'On Hover'),
            ])
        ],
    )

    German = Language(
        name_en='German',
        name_native='Deutsch',
        code='de',
        fields=[
            'Sentence',
            'Translation',
            'Target Word',
            'Definitions',
            'Screenshot',
            'Sentence Audio',
            'Word Audio',
            'Images',
            'Example Sentences',
            'Is Vocabulary Card',
            'Is Audio Card',
        ],
        field_settings=[
            FieldSetting('popup', 'Popup', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
            ]),
            FieldSetting('gender-coloring', 'Gender Coloring', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
                FieldOption('hover', 'On Hover'),
            ])
        ],
    )

    Japanese = Language(
        name_en='Japanese',
        name_native='日本語',
        code='ja',
        fields=[
            'Sentence',
            'Translation',
            'Target Word',
            'Definitions',
            'Screenshot',
            'Sentence Audio',
            'Word Audio',
            'Images',
            'Example Sentences',
            'Is Vocabulary Card',
            'Is Audio Card',
        ],
        field_settings=[
            FieldSetting('popup', 'Popup', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
            ]),
            FieldSetting('furigana', 'Furigana', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
                FieldOption('hover', 'On Hover'),
                FieldOption('hidden', 'Hidden'),
            ]),
            FieldSetting('pitch-coloring', 'Pitch Coloring', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
                FieldOption('hover', 'On Hover'),
            ]),
            FieldSetting('pitch-shapes', 'Pitch Shapes', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
                FieldOption('hover', 'On Hover'),
            ]),
        ],
    )

    Korean = Language(
        name_en='Korean',
        name_native='한국어',
        code='ko',
        fields=[
            'Sentence',
            'Translation',
            'Target Word',
            'Definitions',
            'Screenshot',
            'Sentence Audio',
            'Word Audio',
            'Images',
            'Example Sentences',
            'Is Vocabulary Card',
            'Is Audio Card',
        ],
        field_settings=[
            FieldSetting('popup', 'Popup', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
            ])
        ],
    )

    Portuguese = Language(
        name_en='Portuguese',
        name_native='Português',
        code='pt',
        fields=[
            'Sentence',
            'Translation',
            'Target Word',
            'Definitions',
            'Screenshot',
            'Sentence Audio',
            'Word Audio',
            'Images',
            'Example Sentences',
            'Is Vocabulary Card',
            'Is Audio Card',
        ],
        field_settings=[
            FieldSetting('popup', 'Popup', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
            ]),
            FieldSetting('gender-coloring', 'Gender Coloring', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
                FieldOption('hover', 'On Hover'),
            ])
        ],
    )

    Spanish = Language(
        name_en='Spanish',
        name_native='Español',
        code='es',
        fields=[
            'Sentence',
            'Translation',
            'Target Word',
            'Definitions',
            'Screenshot',
            'Sentence Audio',
            'Word Audio',
            'Images',
            'Example Sentences',
            'Is Vocabulary Card',
            'Is Audio Card',
        ],
        field_settings=[
            FieldSetting('popup', 'Popup', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
            ]),
            FieldSetting('gender-coloring', 'Gender Coloring', [
                FieldOption('no', 'Disabled'),
                FieldOption('yes', 'Enabled'),
                FieldOption('hover', 'On Hover'),
            ])
        ],
    )

    @classmethod
    def by_idx(cls, idx):
        return list(cls)[idx]
