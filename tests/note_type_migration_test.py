import importlib.util
import sys
import types
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


def load_note_type_mgr():
    src_package = types.ModuleType("src")
    src_package.__path__ = [str(ROOT_DIR / "src")]
    sys.modules["src"] = src_package

    aqt = types.ModuleType("aqt")
    aqt.mw = None
    sys.modules["aqt"] = aqt

    anki = types.ModuleType("anki")
    anki_models = types.ModuleType("anki.models")
    anki_models.NotetypeDict = dict
    sys.modules["anki"] = anki
    sys.modules["anki.models"] = anki_models

    util = types.ModuleType("src.util")
    sys.modules["src.util"] = util

    languages = types.ModuleType("src.languages")
    languages.Language = object
    languages.Languages = object
    sys.modules["src.languages"] = languages

    spec = importlib.util.spec_from_file_location(
        "src.note_type_mgr",
        ROOT_DIR / "src" / "note_type_mgr.py",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


note_type_mgr = load_note_type_mgr()

published_back = """
<div>{{editable:Sentence Audio}}</div>
<div class="migaku-card-sentence">
  <div class="field" data-popup="yes" data-furigana="yes" data-pitch-coloring="yes" data-pitch-shapes="yes">{{editable:Sentence}}</div>
</div>
<div>{{editable:Word Audio}}</div>
"""

reordered_back = """
<div>{{editable:Sentence Audio}}</div>
<div>{{editable:Word Audio}}</div>
<div class="migaku-card-sentence">
  <div class="field" data-popup="yes" data-furigana="yes" data-pitch-coloring="yes" data-pitch-shapes="yes">{{editable:Sentence}}</div>
</div>
"""

skewed_back = """
<div>{{editable:Sentence Audio}}</div>
<div class="field" data-popup="yes" data-furigana="yes" data-pitch-coloring="yes" data-pitch-shapes="yes">{{editable:Word Audio}}</div>
<div class="migaku-card-sentence">{{editable:Sentence}}</div>
"""


def assert_migration(current_back):
    note_type = {"tmpls": [{"afmt": reordered_back}]}
    settings_by_name = note_type_mgr.nt_migrate_tmpl_fields_settings(
        current_back,
        reordered_back,
    )
    note_type_mgr.nt_set_tmpl_lang(
        note_type,
        None,
        0,
        "afmt",
        settings_by_name,
        commit=False,
    )

    updated_back = note_type["tmpls"][0]["afmt"]
    assert '<div>{{editable:Word Audio}}</div>' in updated_back
    assert (
        '<div class="field" data-popup="yes" data-furigana="yes" '
        'data-pitch-coloring="yes" data-pitch-shapes="yes">{{editable:Sentence}}</div>'
        in updated_back
    )


assert_migration(published_back)
assert_migration(skewed_back)

print("✓ managed note-type migration preserves and repairs field settings by name")
