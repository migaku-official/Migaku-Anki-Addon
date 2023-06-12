from anki.notes import Note
import aqt
from aqt import AnkiQt
from aqt.qt import *
from aqt.clayout import CardLayout

from .note_type_mgr import nt_was_installed
from . import util


def CardLayout_init_hook(self, mw: AnkiQt, note: Note, *args, **kwargs):
    if note:
        note_type = note.note_type()
        if (
            nt_was_installed(note_type)
            and not mw.app.queryKeyboardModifiers() & Qt.ControlModifier
        ):
            parent = kwargs.get("parent", mw)
            util.show_info(
                "The default Migaku note types cannot be edited because they are automatically updated and your changes would be lost.\n\n"
                f'You can customize the note type by adding a new note type and selecting "Clone: {note_type["name"]}" and editing the copy.\n\n'
                "Please note that the language styling code may break depending on the changes you make. Happy hacking!",
                parent=parent,
            )
            return
    return CardLayout_init(self, mw, note, *args, **kwargs)


CardLayout_init = CardLayout.__init__
CardLayout.__init__ = CardLayout_init_hook
