import math
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

        self.r_total = 0
        self.r_removed = 0
        self.r_suspended = 0
        self.r_tagged = 0
        self.r_moved = 0

        self.p_total = 0
        self.p_type_changed = 0
        self.p_tagged = 0
        self.p_moved = 0

        self.noteids_removed = set()
        self.notes_modified = []
        self.cards_modified = []


    def check(self, card: Card, note: Note = None) -> None:
        if not note:
            note = card.note()

        d_conf = self.col.decks.config_dict_for_deck_id(card.did)
        r_int = d_conf.get('retirement_interval')
        p_int = d_conf.get('promotion_interval')

        if r_int and card.ivl > r_int:

            r_delete = d_conf.get('retirement_delete', False)
            r_suspend = d_conf.get('retirement_suspend', False)
            r_tag = d_conf.get('retirement_tag')
            r_deck = d_conf.get('retirement_deck')

            handled = False

            if r_delete:
                self.noteids_removed.add(note.id)
                self.r_removed += 1
                handled = True
            else:
                if r_suspend:
                    if card.queue != -1:
                        card.queue = -1
                        self.cards_modified.append(card)
                        self.r_suspended += 1
                        handled = True

                if r_tag:
                    if not note.has_tag(r_tag):
                        note.add_tag(r_tag)
                        self.notes_modified.append(note)
                        self.r_tagged += 1
                        handled = True

                if r_deck:
                    new_did = self.col.decks.id(r_deck)
                    if new_did is not None:
                        if card.did != new_did:
                            card.did = new_did
                            self.cards_modified.append(card)
                            self.r_moved += 1
                            handled = True

            if handled:
                self.r_total += 1


        elif p_int and card.ivl > p_int:

            p_tag_required = d_conf.get('promotion_required_tag')
            p_tag_forbidden = d_conf.get('promotion_forbidden_tag')

            if (not p_tag_required or note.has_tag(p_tag_required)) and \
               (not p_tag_forbidden or not note.has_tag(p_tag_forbidden)):

                p_type = d_conf.get('promotion_type')
                p_tag = d_conf.get('promotion_tag')
                p_deck = d_conf.get('promotion_deck')
                p_ivl_factor = d_conf.get('promotion_ivl_factor', 1.0)

                handled = False
                type_changed = False
                card_modified = False

                if p_type:
                    # Check if type is possible for card (prevent blank front)
                    # Pass for non note types with non standard field names
                    type_change_ok = True

                    if p_type == 's':
                        if 'Sentence' in note and not note['Sentence']:
                            type_change_ok = False
                    elif p_type == 'v':
                        if 'Target Word' in note and not note['Target Word']:
                            type_change_ok = False
                    elif p_type == 'as':
                        if 'Sentence Audio' in note and not note['Sentence Audio']:
                            type_change_ok = False
                    elif p_type == 'av':
                        if 'Word Audio' in note and not note['Word Audio']:
                            type_change_ok = False

                    # Change field values accordingly and update note
                    if type_change_ok:
                        if 'Is Vocabulary Card' in note:
                            old_val = 'x' if note['Is Vocabulary Card'] else ''
                            new_val = 'x' if 'v' in p_type else ''
                            if old_val != new_val:
                                note['Is Vocabulary Card'] = new_val
                                type_changed = True
                        if 'Is Audio Card' in note:
                            old_val = 'x' if note['Is Audio Card'] else ''
                            new_val = 'x' if 'a' in p_type else ''
                            if old_val != new_val:
                                note['Is Audio Card'] = new_val
                                type_changed = True

                    if type_changed:
                        self.notes_modified.append(note)
                        self.p_type_changed += 1
                        handled = True

                if p_tag:
                    if not note.has_tag(p_tag):
                        note.add_tag(p_tag)
                        if not type_changed:
                            self.notes_modified.append(note)
                        self.p_tagged += 1
                        handled = True

                if p_deck:
                    new_did = self.col.decks.id(p_deck)
                    if new_did is not None:
                        if card.did != new_did:
                            card.did = new_did
                            card_modified = True
                            self.p_moved += 1
                            handled = True

                # Only change the factor if anything else happened
                if handled and p_ivl_factor != 1.0 and card.ivl > 1 and card.queue == 2:
                    card.ivl = math.ceil(card.ivl * p_ivl_factor)
                    until_rev = card.due - self.col.sched.today
                    if until_rev > 0:
                        new_until_rev = math.ceil(until_rev * p_ivl_factor)
                        card.due = max(self.col.sched.today + new_until_rev, self.col.sched.today + 1)
                    card_modified = True

                if card_modified:
                    self.cards_modified.append(card)

                if handled:
                    self.p_total += 1

    
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

        if self.r_total < 1 and self.p_total < 1:
            _on_done()
        else:
            if self.r_total and self.p_total:
                msg = F'Retire/Promote {self.r_total} Cards'
            elif self.r_total:
                if self.r_total == 1:
                    msg = 'Retire Card'
                else:
                    msg = F'Retire {self.r_total} Cards'
            else:
                if self.p_total == 1:
                    msg = 'Promote Card'
                else:
                    msg = F'Promote {self.p_total} Cards'

            self.checkpoint_id = self.col.add_custom_undo_entry(msg)
            update_notes()


def check_all():

    aqt.mw.progress.start(immediate=True, label='Checking card retirement/promotion...')

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

            msg_parts = []

            if config.get('retirement_notify', True):
                r_msg_parts = []
                if handler.r_suspended > 0:
                    r_msg_parts.append(F'{handler.r_suspended} card(s) suspended')
                if handler.r_tagged > 0:
                    r_msg_parts.append(F'{handler.r_tagged} notes(s) tagged')
                if handler.r_moved > 0:
                    r_msg_parts.append(F'{handler.r_moved} card(s) moved')
                if handler.r_removed > 0:
                    r_msg_parts.append(F'{handler.r_removed} card(s) removed')
                if r_msg_parts:
                    msg_parts.append(
                        F'{handler.r_total} card(s) have been retired:<br><br>- ' + '<br>- '.join(r_msg_parts)
                    )

            if config.get('promotion_notify', True):
                p_msg_parts = []
                if handler.p_type_changed > 0:
                    p_msg_parts.append(F'{handler.p_type_changed} note(s) type changed')
                if handler.p_tagged > 0:
                    p_msg_parts.append(F'{handler.p_tagged} note(s) tagged')
                if handler.p_moved > 0:
                    p_msg_parts.append(F'{handler.p_moved} card(s) moved')
                if p_msg_parts:
                    msg_parts.append(
                        F'{handler.p_total} card(s) have been promoted:<br><br>- ' + '<br>- '.join(p_msg_parts)
                    )

            if msg_parts:
                aqt.utils.showInfo('<br><br>'.join(msg_parts))

        handler.execute(aqt.mw, on_done=finalize, on_failure=finalize)

    aqt.mw.taskman.run_in_background(loop_cards, on_done=execute)


def answer_hook(rev: Reviewer, card: Card, ease: Literal[1, 2, 3, 4]) -> None:
    handler = RetirementHandler()
    handler.check(card)
    handler.execute(rev.mw)
    if handler.r_total > 0 and config.get('retirement_notify', True):
        aqt.utils.tooltip('Card retired.')
    elif handler.p_total > 0 and config.get('promotion_notify', True):
        aqt.utils.tooltip('Card promoted.')

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

# aqt.gui_hooks.deck_options_did_load.append(on_deck_options_did_load)


action = QAction('Check Card Retirement/Promotion', aqt.mw)
action.triggered.connect(lambda: check_all())
