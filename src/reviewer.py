from enum import Enum

import aqt
from aqt.utils import tr

from . import config


class Grading(Enum):
    Again = 0
    Hard = 1
    Good = 2
    Easy = 3

    def button_color(self):
        return {
            Grading.Again: "#e60000",
            Grading.Hard: "#e65c00",
            Grading.Good: "#00802B",
            Grading.Easy: "#005ce6",
        }[self]

    def button_text(self):
        text = {
            self.Again: tr.studying_again(),
            self.Hard: tr.studying_hard(),
            self.Good: tr.studying_good(),
            self.Easy: tr.studying_easy(),
        }[self]

        if config.get("reviewer_button_coloring", True):
            return f'<span style="color: {self.button_color()};">{text}</span>'
        return text


def init_reviewer_buttons(buttons_tuple, reviewer, card):
    button_count = reviewer.mw.col.sched.answerButtons(card)

    pass_fail = config.get("reviewer_pass_fail", True)

    if button_count == 2:
        buttons_tuple = (
            (1, Grading.Again.button_text()),
            (2, Grading.Good.button_text()),
        )
    elif button_count == 3:
        if pass_fail:
            buttons_tuple = (
                (1, Grading.Again.button_text()),
                (2, Grading.Good.button_text()),
            )
        else:
            buttons_tuple = (
                (1, Grading.Again.button_text()),
                (2, Grading.Good.button_text()),
                (3, Grading.Easy.button_text()),
            )
    else:
        if pass_fail:
            buttons_tuple = (
                (1, Grading.Again.button_text()),
                (3, Grading.Good.button_text()),
            )
        else:
            buttons_tuple = (
                (1, Grading.Again.button_text()),
                (2, Grading.Hard.button_text()),
                (3, Grading.Good.button_text()),
                (4, Grading.Easy.button_text()),
            )

    return buttons_tuple


aqt.gui_hooks.reviewer_will_init_answer_buttons.append(init_reviewer_buttons)


def reviewer_mod_answer_ease(self, ease):
    button_count = self.mw.col.sched.answerButtons(self.card)

    pass_fail = config.get("reviewer_pass_fail", True)

    if pass_fail:
        if button_count == 3:
            if ease > 1:
                ease = 2
        if button_count == 4:
            if ease > 1:
                ease = 3

    Reviewer_answerCard(self, ease)


Reviewer_answerCard = aqt.reviewer.Reviewer._answerCard
aqt.reviewer.Reviewer._answerCard = reviewer_mod_answer_ease


def card_reset_ease_factor(card):
    if config.get("maintain_ease", True):
        card.factor = int(config.get("maintain_ease_factor", 2.5) * 1000)


aqt.gui_hooks.reviewer_did_show_question.append(card_reset_ease_factor)
aqt.gui_hooks.reviewer_did_show_answer.append(card_reset_ease_factor)
