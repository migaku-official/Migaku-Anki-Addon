import sys
from typing import Optional

import pynput.keyboard
from pynput.keyboard import Key

import aqt
from aqt.qt import *
from aqt.utils import isMac, isWin

from . import config


class KeySequence:

    Shift = 1 << 0
    Alt   = 1 << 1
    Ctrl  = 1 << 2
    Meta  = 1 << 3

    def __init__(self, key: str, modifiers: int = 0):
        self.key = key
        self.modifiers = modifiers
    
    def __hash__(self):
        return hash((self.key, self.modifiers))

    def __eq__(self, other):
        return self.key == other.key and self.modifiers == other.modifiers

    def to_user_string(self):
        key_strings = []
        if isMac:
            if self.modifiers & self.Meta:
                key_strings.append('Command')
            if self.modifiers & self.Ctrl:
                key_strings.append('Control')
            if self.modifiers & self.Alt:
                key_strings.append('Option')
            if self.modifiers & self.Shift:
                key_strings.append('Shift')
        else:
            if self.modifiers & self.Ctrl:
                key_strings.append('Ctrl')
            if self.modifiers & self.Alt:
                key_strings.append('Alt')
            if self.modifiers & self.Shift:
                key_strings.append('Shift')
            if self.modifiers & self.Meta:
                key_strings.append('Win' if isWin else 'Meta')

        key_segs = [seg.capitalize() for seg in self.key.split('_')]
        key_strings.append(' '.join(key_segs))

        return '+'.join(key_strings)

    def __repr__(self):
        return F'<{type(self).__name__} {self.to_user_string()}>'


class KeyboardHandler(QObject):

    key_pressed = pyqtSignal(KeySequence)
    key_released = pyqtSignal(KeySequence)

    action_fired = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.block_actions = False
        self.actions = { False: {}, True: {} }

        if isMac:
            self.modifier_map = {
                Key.shift: 1 << 0,
                Key.alt:   1 << 1,
                Key.cmd:   1 << 2,
                Key.ctrl:  1 << 3,
            }
        else:
            self.modifier_map = {
                Key.shift: 1 << 0,
                Key.alt:   1 << 1,
                Key.ctrl:  1 << 2,
                Key.cmd:   1 << 3,
            }

        self.modifiers = 0

        self.listener = pynput.keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.listener.start()

    def on_press(self, raw_key):
        raw_key = self.listener.canonical(raw_key)
        if raw_key in self.modifier_map:
            self.modifiers |= self.modifier_map[raw_key]
        else:
            key = self.parse_raw_key(raw_key)
            sequence = KeySequence(key, self.modifiers)
            self.key_pressed.emit(sequence)
            if not self.block_actions and sequence in self.actions[False]:
                self.action_fired.emit(self.actions[False][sequence])

    def on_release(self, raw_key):    
        raw_key = self.listener.canonical(raw_key)
        if raw_key in self.modifier_map:
            self.modifiers &= ~self.modifier_map[raw_key]
        else:
            key = self.parse_raw_key(raw_key)
            sequence = KeySequence(key, self.modifiers)
            self.key_released.emit(sequence)
            if not self.block_actions and sequence in self.actions[True]:
                self.action_fired.emit(self.actions[True][sequence])

    def add_action(self, action: str, sequnce: KeySequence, on_release: bool = False, remove_existing: bool = False):
        if remove_existing:
            self.remove_action(action)
        self.actions[on_release][sequnce] = action

    def remove_action(self, action):
        for on_release in self.actions:
            for test_sequence, test_action in list(self.actions[on_release].items()):
                if test_action == action:
                    del self.actions[on_release][test_sequence]

    @classmethod
    def parse_raw_key(cls, key):
        raw = str(key)
        if raw.startswith('Key.'):
            raw = raw[4:]
        elif len(raw) >= 3:
            return raw[1:-1]
        return raw



class HotkeyHandler(QObject):

    hotkeys = [
        ('open_dict',       KeySequence('f', KeySequence.Ctrl | KeySequence.Alt), 'Open dictionary'),
        ('search_dict',     KeySequence('d', KeySequence.Ctrl | KeySequence.Alt), 'Search selected text in dictionary'),
        ('set_sentence',    KeySequence('s', KeySequence.Ctrl | KeySequence.Alt), 'Send sentence to card exporter'),
        ('add_definition',  KeySequence('g', KeySequence.Ctrl | KeySequence.Alt), 'Send definition to card exporter'),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)

        self.selected_text_handler = None

        self.keyboard_controller = pynput.keyboard.Controller()

        self.keyboard_handler = KeyboardHandler()
        self.keyboard_handler.action_fired.connect(self.on_action_fired)

        for (action, default_sequence, _) in self.hotkeys:
            sequence_tuple = config.get('hotkey_' + action)
            if sequence_tuple:
                sequence = KeySequence(*sequence_tuple)
            else:
                sequence = default_sequence

            self.keyboard_handler.add_action(action, sequence)

    def on_action_fired(self, action):
        if action == 'open_dict':
            aqt.mw.migaku_connection.open_dict()
        if action in ['search_dict', 'set_sentence', 'add_definition']:
            self.request_seltected_text(action)

    def request_seltected_text(self, action):
        with self.keyboard_controller.pressed(Key.cmd if isMac else Key.ctrl):
            self.keyboard_controller.press('c')
            self.keyboard_controller.release('c')

        self.selected_text_handler = action
        QTimer.singleShot(100, self.handle_selected_text)

    def handle_selected_text(self):
        action = self.selected_text_handler
        if not action:
            return
        text = aqt.mw.app.clipboard().text()

        if action == 'search_dict':
            aqt.mw.migaku_connection.search_dict(text)
        elif action == 'set_sentence':
            aqt.mw.migaku_connection.set_sentence(text)
        elif action == 'add_definition':
            aqt.mw.migaku_connection.add_definition(text)



class HotkeyConfigWidget(QWidget):

    def __init__(self, hotkey_handeler, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.hotkey_handeler = hotkey_handeler

        lyt = QGridLayout()
        self.setLayout(lyt)

        self.current_idx = None
        self.buttons = []
        self.idx_for_button = {}

        i = 0
        for j, (_, _, text) in enumerate(self.hotkey_handeler.hotkeys):
            lyt.addWidget(QLabel(text + ':'), i, 0)
            sequence = self.sequence_for_idx(j)
            btn = QPushButton(sequence.to_user_string())
            btn.setFocusPolicy(Qt.NoFocus)
            btn.clicked.connect(self.on_button_pressed)
            self.idx_for_button[btn] = j
            self.buttons.append(btn)
            lyt.addWidget(btn, i, 1)

            i += 1

        self.hotkey_handeler.keyboard_handler.key_pressed.connect(self.on_key_pressed)

    def __del__(self):
        self.hotkey_handeler.keyboard_handler.block_actions = False


    def sequence_for_idx(self, idx):
        hotkey = self.hotkey_handeler.hotkeys[idx]

        sequence_tuple = config.get('hotkey_' + hotkey[0])
        if sequence_tuple:
            return KeySequence(*sequence_tuple)
        return hotkey[1]


    def on_button_pressed(self):
        self.hotkey_handeler.keyboard_handler.block_actions = False
        btn = self.sender()
        new_idx = self.idx_for_button[btn]

        if self.current_idx is not None or new_idx == self.current_idx:
            text = self.sequence_for_idx(self.current_idx).to_user_string()
            self.buttons[self.current_idx].setText(text)

        if new_idx != self.current_idx:
            btn = self.sender()
            btn.setText('[...]')
            self.hotkey_handeler.keyboard_handler.block_actions = True
            self.current_idx = new_idx
        else:
            self.current_idx = None


    def on_key_pressed(self, sequence):
        if self.current_idx is None:
            return

        self.hotkey_handeler.keyboard_handler.block_actions = False

        btn = self.buttons[self.current_idx]
        btn.setText(sequence.to_user_string())

        hotkey = self.hotkey_handeler.hotkeys[self.current_idx]
        config.set('hotkey_' + hotkey[0], [sequence.key, sequence.modifiers])
        self.hotkey_handeler.keyboard_handler.add_action(hotkey[0], sequence, remove_existing=True)

        self.current_idx = None



hotkey_handeler = HotkeyHandler(aqt.mw)
