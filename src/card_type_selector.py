# Allows changing card conditional types

# To enable for a note types
# - Add the fields 'Is Vocabulary Card' and/or 'Is Audio Card' to the note type
# - Use these fields for conditional formatting on the note type
# - Call pycmd('update_card_type|x') from the JS of the note type to update the field values
#     'Is Vocabulary Card' is set if 'x' contains 'v'
#     'Is Audio Card' is set if 'x' contains 'a'


import anki
import aqt
from aqt.reviewer import Reviewer
from aqt.browser.previewer import Previewer
from aqt.operations.note import update_note

from . import config


def handle_cmd(cmd, note: anki.collection.Note, no_refresh: bool = False):
    card_type = cmd.split("|")[1]

    is_vocabulary_card = "v" in card_type
    is_audio_card = "a" in card_type

    if "Is Vocabulary Card" in note:
        note["Is Vocabulary Card"] = "x" if is_vocabulary_card else ""
    if "Is Audio Card" in note:
        note["Is Audio Card"] = "x" if is_audio_card else ""

    tag = config.get("card_type_tag", "")
    if tag:
        note.add_tag(tag)

    if no_refresh:
        note.flush()
    else:
        update_note(parent=aqt.mw, note=note).run_in_background()


def reviewer_link_handler(self: Reviewer, url: str):
    if url.startswith("update_card_type|"):
        handle_cmd(url, self.card.note(), no_refresh=True)
        return

    Reviewer_linkHandler(self, url)


Reviewer_linkHandler = Reviewer._linkHandler
Reviewer._linkHandler = reviewer_link_handler


def previewer_on_bridge_cmd(self: Previewer, cmd: str):
    if cmd.startswith("update_card_type|"):
        handle_cmd(cmd, self.card().note())
        return

    Previewer_on_bridge_cmd(self, cmd)


Previewer_on_bridge_cmd = Previewer._on_bridge_cmd
Previewer._on_bridge_cmd = previewer_on_bridge_cmd


def reviewer_rev_html(self: Reviewer):
    return (
        Reviewer_revHtml(self)
        + "<script>document.getElementById('qa').classList.add('card-typeselect-available');</script>"
    )


Reviewer_revHtml = Reviewer.revHtml
Reviewer.revHtml = reviewer_rev_html
