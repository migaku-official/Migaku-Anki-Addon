import json
from typing import Literal

from anki.collection import Card, Note, Collection
import aqt
from aqt.qt import QWidget, QAction
from aqt.reviewer import Reviewer
from aqt.operations import CollectionOp

from . import config
from . import util


class RetirementHandler:

    def __init__(self, col: Collection=None):
        self.col = aqt.mw.col

        self.total = 0
        self.removed = 0
        self.suspended = 0
        self.tagged = 0
        self.moved = 0
        self.noteids_removed = set()
        self.notes_modified = []
        self.cards_modified = []


    def check(self, card: Card, note: Note = None) -> None:
        if not note:
            note = card.note()

        d_conf = self.col.decks.config_dict_for_deck_id(card.did)
        r_int = d_conf.get('retirement_interval')

        if not r_int:
            return

        r_delete = d_conf.get('retirement_delete', False)
        r_suspend = d_conf.get('retirement_suspend', False)
        r_tag = d_conf.get('retirement_tag')
        r_deck = d_conf.get('retirement_deck')

        if card.ivl > r_int:
            handled = False

            if r_delete:
                self.noteids_removed.add(note.id)
                self.removed += 1
                handled = True
            else:
                if r_suspend:
                    if card.queue != -1:
                        card.queue = -1
                        self.cards_modified.append(card)
                        self.suspended += 1
                        handled = True

                if r_tag:
                    if not note.has_tag(r_tag):
                        note.add_tag(r_tag)
                        self.notes_modified.append(note)
                        self.tagged += 1
                        handled = True

                if r_deck:
                    new_did = self.col.decks.id(r_deck)
                    if new_did is not None:
                        if card.did != new_did:
                            card.did = new_did
                            self.cards_modified.append(card)
                            self.moved += 1
                            handled = True

            if handled:
                self.total += 1

    
    def execute(self, parent: QWidget, on_done=None, on_failure=None) -> None:

        def _on_done():
            if not self.checkpoint_id is None:
                aqt.mw.col.merge_undo_entries(self.checkpoint_id)
                self.checkpoint_id = None
            if on_done:
                on_done()

        def _on_failure(exc):
            if on_failure:
                on_failure(exc)

        def remove_notes():
            CollectionOp(
                parent,
                lambda col: col.remove_notes(list(self.noteids_removed))
            ).success(lambda _: _on_done()).failure(_on_failure).run_in_background()

        def update_cards():
            CollectionOp(
                parent,
                lambda col: col.update_cards(self.cards_modified)
            ).success(lambda _: remove_notes()).failure(_on_failure).run_in_background()

        def update_notes():
            CollectionOp(
                parent,
                lambda col: col.update_notes(self.notes_modified)
            ).success(lambda _: update_cards()).failure(_on_failure).run_in_background()

        self.checkpoint_id = None

        if self.total < 1:
            _on_done()
        else:
            if self.total == 1:
                msg = 'Retire Card'
            else:
                msg = F'Retire {self.total} Cards'

            self.checkpoint_id = self.col.add_custom_undo_entry(msg)
            update_notes()


def check_all():

    aqt.mw.progress.start(immediate=True, label='Checking card retirement...')

    handler = RetirementHandler()
    cardids = aqt.mw.col.find_cards('')

    def loop_cards():
        for cardid in cardids:
            card = aqt.mw.col.get_card(cardid)
            if card.ivl != 0:
                handler.check(card)

    def execute(_):
        def finalize():
            aqt.mw.progress.finish()

            if config.get('retirement_notify', True):
                msg_parts = []
                if handler.suspended > 0:
                    msg_parts.append(F'{handler.suspended} card(s) suspended')
                if handler.tagged > 0:
                    msg_parts.append(F'{handler.tagged} notes(s) tagged')
                if handler.moved > 0:
                    msg_parts.append(F'{handler.moved} card(s) moved')
                if handler.removed > 0:
                    msg_parts.append(F'{handler.removed} card(s) removed')
                if msg_parts:
                    util.show_info(F'{handler.total} card(s) have been retired:<br><br>- ' + '<br>- '.join(msg_parts))

        handler.execute(aqt.mw, on_done=finalize, on_failure=finalize)

    aqt.mw.taskman.run_in_background(loop_cards, on_done=execute)


def answer_hook(rev: Reviewer, card: Card, ease: Literal[1, 2, 3, 4]) -> None:
    handler = RetirementHandler()
    handler.check(card)
    handler.execute(rev.mw)
    if handler.total > 0 and config.get('retirement_notify', True):
        aqt.utils.tooltip('Card retired.')

aqt.gui_hooks.reviewer_did_answer_card.append(answer_hook)


with open(util.addon_path('retirement.html')) as f:
    retirement_html = f.read()

with open(util.addon_path('retirement.js')) as f:
    retirement_js = f.read()

def on_deck_options_did_load(dialog):
    from aqt.qt import Qt
    dialog.setWindowModality(Qt.NonModal)

    dialog.web.eval(
        retirement_js.replace(
            'HTML_CONTENT',
            json.dumps(retirement_html)
        )
    )

aqt.gui_hooks.deck_options_did_load.append(on_deck_options_did_load)


action = QAction('Check card retirement', aqt.mw)
action.triggered.connect(lambda: check_all())
