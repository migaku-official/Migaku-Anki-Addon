from anki.hooks import wrap
from anki.notes import Note
from aqt.editor import Editor
import aqt

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
