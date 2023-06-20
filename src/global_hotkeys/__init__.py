from aqt.qt import QGridLayout, QWidget, QLabel, QPushButton, Qt
from aqt import mw

from .. import config

from .hotkey_handler import HotkeyHandler
from .key_sequence import KeySequence


hotkey_handler = HotkeyHandler(mw)


class HotkeyConfigWidget(QWidget):
    def __init__(self, hotkey_handler, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.hotkey_handler = hotkey_handler

        lyt = QGridLayout()
        self.setLayout(lyt)

        self.current_idx = None
        self.buttons = []
        self.idx_for_button = {}

        i = 0
        for j, (_, _, text) in enumerate(self.hotkey_handler.hotkeys):
            lyt.addWidget(QLabel(text + ":"), i, 0)
            sequence = self.sequence_for_idx(j)
            btn = QPushButton(sequence.to_user_string())
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.clicked.connect(self.on_button_pressed)
            self.idx_for_button[btn] = j
            self.buttons.append(btn)
            lyt.addWidget(btn, i, 1)

            i += 1

        self.hotkey_handler.keyboard_handler.key_pressed.connect(self.on_key_pressed)

    def __del__(self):
        self.hotkey_handler.keyboard_handler.block_actions = False

    def sequence_for_idx(self, idx):
        hotkey = self.hotkey_handler.hotkeys[idx]

        sequence_tuple = config.get("hotkey_" + hotkey[0])
        if sequence_tuple:
            return KeySequence(*sequence_tuple)
        return hotkey[1]

    def on_button_pressed(self):
        self.hotkey_handler.keyboard_handler.block_actions = False
        btn = self.sender()
        new_idx = self.idx_for_button[btn]

        if self.current_idx is not None or new_idx == self.current_idx:
            text = self.sequence_for_idx(self.current_idx).to_user_string()
            self.buttons[self.current_idx].setText(text)

        if new_idx != self.current_idx:
            btn = self.sender()
            btn.setText("[...]")
            self.hotkey_handler.keyboard_handler.block_actions = True
            self.current_idx = new_idx
        else:
            self.on_key_pressed(KeySequence(None))

    def on_key_pressed(self, sequence):
        if self.current_idx is None:
            return

        self.hotkey_handler.keyboard_handler.block_actions = False

        btn = self.buttons[self.current_idx]
        btn.setText(sequence.to_user_string())

        hotkey = self.hotkey_handler.hotkeys[self.current_idx]
        config.set("hotkey_" + hotkey[0], [sequence.key, sequence.modifiers])
        self.hotkey_handler.keyboard_handler.add_action(
            hotkey[0], sequence, remove_existing=True
        )

        self.current_idx = None
