from collections import defaultdict
import time
import datetime

import aqt
from aqt.qt import QAction
from anki.decks import DeckConfigId

from .scheduler_func import balance, Card, Vacation


SECOND_MS = 1000
DAY_MS = 24 * 60 * 60 * 1000


class BalanceScheduler:
    SCHEDULE_DAYS = 100
    SAFETY_MS = 5 * 1000  # No scheduling if less than 5 seconds from day end

    def __init__(self, col):
        self.col = col

    @staticmethod
    def now_ms():
        return int(time.time() * SECOND_MS)

    def tomorrow_start_ms(self):
        sched = self.col.sched

        # <= 2.1.49
        if hasattr(sched, "dayCutoff"):
            return sched.dayCutoff * SECOND_MS

        return sched.day_cutoff * SECOND_MS

    def today_start_ms(self):
        return self.tomorrow_start_ms() - DAY_MS

    def col_start_ms(self):
        return self.today_start_ms() - self.col.sched.today * DAY_MS

    def ms_to_col_day(self, val):
        return (val - self.col_start_ms()) // DAY_MS

    def ms_to_tomorrow(self):
        return self.tomorrow_start_ms() - self.now_ms()

    def col_week_offset(self):
        ts = self.col_start_ms() / SECOND_MS - time.timezone
        dt = datetime.datetime.fromtimestamp(ts)
        return dt.weekday()

    def rotate_schedule(self, schedule):
        offset = self.col_week_offset() % len(schedule)
        return schedule[offset:] + schedule[:offset]

    def card_recreate_due_day(self, card: Card):
        if card.ivl < 1:
            return None

        last_rev = self.col.db.first(
            "SELECT id, ivl FROM revlog WHERE cid = ? ORDER BY id DESC LIMIT 1", card.id
        )

        if last_rev is None:
            return None

        return self.ms_to_col_day(last_rev[0]) + card.ivl

    def revs_done_today_for_deck(self, deckid):
        return self.col.db.scalar(
            "SELECT count() FROM revlog JOIN cards ON revlog.cid = cards.id "
            "WHERE revlog.id >= ? AND cards.ivl >= 1 AND cards.did = ?",
            self.today_start_ms(),
            deckid,
        )

    def revs_done_today_for_decks(self, deckids):
        return sum(self.revs_done_today_for_deck(did) for did in deckids)

    def find_balance_candidates_for_deck(self, deck_id):
        today = self.col.sched.today

        # Find all aplicable cards due within the next year
        balance_pre_candidates = []
        cards_it = self.col.db.all(
            "SELECT id, due, ivl FROM cards WHERE did = ? AND queue = 2 AND due >= ? AND due < ?",
            deck_id,
            today,
            today + self.SCHEDULE_DAYS,
        )

        for id_, due, ivl in cards_it:
            balance_pre_candidates.append(Card(id_, due, ivl))

        # Only consider cards for which the due day can be reconstructed
        balance_candidates = []
        for card in balance_pre_candidates:
            due_day = self.card_recreate_due_day(card)
            if due_day is None:
                continue

            balance_candidates.append(Card(card.id, due_day, card.ivl))

        return balance_candidates

    def find_balance_candidates_for_decks(self, deck_ids):
        candidates = []
        for deck_id in deck_ids:
            candidates.extend(self.find_balance_candidates_for_deck(deck_id))

        return candidates

    def balance_candiates(
        self, candidates, move_factor, schedule_factors, vacations, revs_done_today
    ):
        r_schedule_factors = self.rotate_schedule(schedule_factors)

        to_balance = balance(
            cards=candidates,
            today=self.col.sched.today,
            num_days=self.SCHEDULE_DAYS,
            move_factor=move_factor,
            schedule_factors=r_schedule_factors,
            vacations=vacations,
            revs_done_today=revs_done_today,
        )

        for card, new_day in to_balance:
            card = self.col.get_card(card.id)
            card.due = new_day
            self.col.update_card(card)

        # self.col.db.executemany(
        #    'UPDATE cards SET due = ? WHERE id = ?',
        #    [(new_day, card.id) for card, new_day in to_balance]
        # )

    def balance_all(self):
        group_decks = defaultdict(list)

        for deck in self.col.decks.all():
            group_id = deck.get("conf")
            if not group_id is None:
                group_id = int(group_id)
                group_decks[group_id].append(deck["id"])

        for group_id, deck_ids in group_decks.items():
            cfg = self.col.decks.get_config(DeckConfigId(group_id))
            if cfg is None:
                continue

            if not cfg.get("scheduling_enabled", False):
                continue

            move_factor = cfg.get("scheduling_move_factor", 0.1)
            schedule_factors = cfg.get("scheduling_week", [1.0] * 7)

            vacations = []
            for vacation_data in cfg.get("scheduling_vacations", []):
                vacation = Vacation(
                    vacation_data["start"],
                    vacation_data["end"],
                    vacation_data["factor"],
                )
                vacations.append(vacation)

            candidates = self.find_balance_candidates_for_decks(deck_ids)
            revs_done_today = self.revs_done_today_for_decks(deck_ids)
            self.balance_candiates(
                candidates, move_factor, schedule_factors, vacations, revs_done_today
            )

        aqt.mw.reset()


def balance_all():
    bsched = BalanceScheduler(aqt.mw.col)
    bsched.balance_all()


action = QAction("Optimize Card Schedule", aqt.mw)
action.triggered.connect(lambda: balance_all())
