from anki.hooks import wrap
from anki.notes import Note
from aqt.editor import Editor
import aqt
from ..migaku_fields import get_migaku_fields

current_editors = []


def set_current_editor(editor: Editor):
    global current_editors
    remove_editor(editor)
    current_editors.append(editor)


def remove_editor(editor: Editor):
    global current_editors
    current_editors = [e for e in current_editors if e != editor]


def get_current_editor() -> Editor:
    if len(current_editors) > 0:
        return current_editors[-1]
    return None


def get_current_note_info() -> Note:
    for editor in reversed(current_editors):
        if editor.note:
            return {
                "note": editor.note,
                "editor": editor,
            }

    if aqt.mw.reviewer and aqt.mw.reviewer.card:
        note = aqt.mw.reviewer.card.note()
        if note:
            return {
                "note": note,
                "reviewer": aqt.mw.reviewer,
            }
    return None


def get_add_cards() -> Note:
    for editor in reversed(current_editors):
        if editor.addMode:
            return {
                "note": editor.note,
                "editor": editor,
            }

    return None


current_note_type_id = 0
current_deck_id = 0


def get_add_cards_info(defaults=None):
    addcards = get_add_cards()

    if addcards and defaults:
        note = addcards["note"]
        tags = note.tags

        notetype_id = defaults.notetype_id
        notetype = aqt.mw.col.models.get(notetype_id)
        notetype_name = notetype["name"]

        deck_id = defaults.deck_id
        deck = aqt.mw.col.decks.get(deck_id)
        deck_name = deck["name"]

        fields = get_migaku_fields(notetype)

    elif addcards:
        note = addcards["note"]
        tags = note.tags
        notetype = note.note_type()

        fields = get_migaku_fields(notetype)
        notetype_name = notetype["name"]
        notetype_id = notetype["id"]

        deck_id = get_current_deck_id()
        deck = aqt.mw.col.decks.get(deck_id)
        deck_name = deck["name"]

    else:
        notetype_id = aqt.mw.col.get_config("curModel")
        notetype = aqt.mw.col.models.get(notetype_id)
        fields = get_migaku_fields(notetype)
        notetype_name = notetype["name"]

        deck_id = aqt.mw.col.get_config("curDeck")
        deck = aqt.mw.col.decks.get(deck_id)
        deck_name = deck["name"]
        tags = []

    return {
        "fields": fields,
        "notetype": notetype,
        "notetype_name": notetype_name,
        "notetype_id": notetype_id,
        "deck": deck,
        "deck_name": deck_name,
        "deck_id": deck_id,
        "tags": tags,
    }


def on_addcards_did_change_note_type(editor, old_id, new_id):
    global current_note_type_id
    current_note_type_id = new_id


def on_addcards_did_change_deck(new_id):
    global current_deck_id
    current_deck_id = new_id


def get_current_note_type_id():
    return current_note_type_id


def get_current_deck_id():
    return current_deck_id
