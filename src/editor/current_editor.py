from anki.hooks import wrap
from anki.notes import Note
from aqt.editor import Editor
import aqt
from ..config import get
from ..card_types import CardFields
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
                "addcards": editor.parentWindow,
                "note": editor.note,
                "editor": editor,
            }

    return None


current_note_type_id = 0
current_deck_id = 0


def add_cards_add_to_history(note):
    addcards = get_add_cards()

    if not addcards:
        return
    print("Adding to history", note.id)

    addcards["addcards"].addHistory(note)


def get_add_cards_info(defaults=None):
    addcards = get_add_cards()

    cur_model = aqt.mw.col.get_config("curModel")
    cur_deck = aqt.mw.col.get_config("curDeck")

    if addcards:
        note = addcards["note"]
        tags = note.tags

        if defaults:
            notetype = aqt.mw.col.models.get(defaults.notetype_id)
            notetype_id = defaults.notetype_id
            deck_id = defaults.deck_id
        else:
            notetype = note.note_type()
            notetype_id = notetype["id"]
            deck_id = get_current_deck_id()

    else:
        notetype_id = int(get("migakuNotetypeId", cur_model))
        notetype = (
            aqt.mw.col.models.get(notetype_id)
            or aqt.mw.col.models.get(cur_model)
            or aqt.mw.col.models.all()[0]
        )
        deck_id = int(get("migakuDeckId", cur_deck))
        tags = []

    deck = aqt.mw.col.decks.get(deck_id) or aqt.mw.col.decks.get(cur_deck)
    deck_name = deck["name"]
    notetype_name = notetype["name"]
    fields = get_migaku_fields(notetype)

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


def map_to_add_cards(card: CardFields):
    addcards = get_add_cards()

    if not addcards:
        return False

    info = get_add_cards_info()
    note = addcards["note"]
    fields = info["fields"]

    for fieldname, type in fields.items():
        if type == "none":
            continue

        note[fieldname] = str(getattr(card, type))

    aqt.mw.taskman.run_on_main(addcards["editor"].loadNoteKeepingFocus)

    return True


def on_addcards_did_change_note_type(new_id):
    global current_note_type_id
    current_note_type_id = new_id


def on_addcards_did_change_deck(new_id):
    global current_deck_id
    current_deck_id = new_id


def get_current_note_type_id():
    return current_note_type_id


def get_current_deck_id():
    return current_deck_id
