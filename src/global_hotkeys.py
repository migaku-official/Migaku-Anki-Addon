import sys
from typing import Optional

import pynput.keyboard
from pynput.keyboard import Key

import anki
import aqt
from aqt.qt import *
from anki.utils import isMac, isWin, isLin

from . import config
from . import util


class KeySequence:

    Shift = 1 << 0
    Alt   = 1 << 1
    Ctrl  = 1 << 2
    Meta  = 1 << 3

    def __init__(self, key: Optional[str] = None, modifiers: int = 0):
        self.key = key
        self.modifiers = modifiers

    def __hash__(self):
        return hash((self.key, self.modifiers))

    def __eq__(self, other):
        return self.key == other.key and self.modifiers == other.modifiers

    def is_disabled(self):
        return self.key is None

    def to_user_string(self):
        if self.is_disabled():
            return 'Disabled'

        key_strings = []
        if isMac:
            join_char = ''
            if self.modifiers & self.Ctrl:
                key_strings.append('⌃')
            if self.modifiers & self.Alt:
                key_strings.append('⌥')
            if self.modifiers & self.Shift:
                key_strings.append('⇧')
            if self.modifiers & self.Meta:
                key_strings.append('⌘')
        else:
            join_char = '+'
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

        return join_char.join(key_strings)

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

    def is_available(self):
        if hasattr(self.listener, 'IS_TRUSTED') and not self.listener.IS_TRUSTED:
            return False
        return True

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



class HotkeyHandlerBase(QObject):

    hotkeys = [
        ('open_dict',         KeySequence('f', KeySequence.Ctrl | KeySequence.Alt), 'Open dictionary'),
        ('search_dict',       KeySequence('d', KeySequence.Ctrl | KeySequence.Alt), 'Search selected text in dictionary'),
        ('set_sentence',      KeySequence('s', KeySequence.Ctrl | KeySequence.Alt), 'Send sentence to card creator'),
        ('add_definition',    KeySequence('g', KeySequence.Ctrl | KeySequence.Alt), 'Send definition to card creator'),
        ('search_collection', KeySequence('b', KeySequence.Ctrl | KeySequence.Alt), 'Search selected text in card collection'),
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
                self.keyboard_handler.add_action(action, sequence)
            else:
                sequence = default_sequence
                self.keyboard_handler.add_action(action, sequence)

    def is_available(self):
        return self.keyboard_handler.is_available()

    def on_action_fired(self, action):
        if action == 'open_dict':
            aqt.mw.migaku_connection.open_dict()
            self.focus_dictionary()
        if action in ['search_dict', 'set_sentence', 'add_definition', 'search_collection']:
            self.request_seltected_text(action)

    def request_seltected_text(self, action):

        modifier_keys = [
            Key.alt_gr,
            Key.alt, Key.alt_l, Key.alt_r,
            Key.cmd, Key.cmd_l, Key.cmd_r,
            Key.ctrl, Key.ctrl_l, Key.ctrl_r,
            Key.shift, Key.shift_l, Key.shift_r
        ]

        if not isLin:
            for key in modifier_keys:
                self.keyboard_controller.release(key)

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
            self.focus_dictionary()
        elif action == 'set_sentence':
            aqt.mw.migaku_connection.set_sentence(text)
            self.focus_dictionary()
        elif action == 'add_definition':
            aqt.mw.migaku_connection.add_definition(text)
            self.focus_dictionary()
        elif action == 'search_collection':
            util.open_browser(text)

    def focus_dictionary(self):
        # Implemented in derived classes if required
        pass


if isMac:

    class HotkeyHandlerMac(HotkeyHandlerBase):

        hotkeys = [
            ('open_dict',         KeySequence(), 'Open dictionary'),
            ('search_dict',       KeySequence(), 'Search selected text in dictionary'),
            ('set_sentence',      KeySequence(), 'Send sentence to card creator'),
            ('add_definition',    KeySequence(), 'Send definition to card creator'),
            ('search_collection', KeySequence(), 'Search selected text in card collection'),
        ]

    HotkeyHandler = HotkeyHandlerMac


elif isWin:

    import ctypes

    class HotkeyHandlerWindows(HotkeyHandlerBase):

        def focus_dictionary(self, retry_count=5):
            enum_windows_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.POINTER(ctypes.c_int))

            did_focus = False

            def foreach_window(hWnd, lParam):
                nonlocal did_focus
                title_length = ctypes.windll.user32.GetWindowTextLengthW(hWnd)
                title_buff = ctypes.create_unicode_buffer(title_length + 1)
                ctypes.windll.user32.GetWindowTextW(hWnd, title_buff, title_length + 1)
                title = title_buff.value
                if title == 'Migaku Dictionary':
                    ctypes.windll.user32.SetForegroundWindow(hWnd)
                    did_focus = True
                return True

            ctypes.windll.user32.EnumWindows(enum_windows_proc(foreach_window), 0)

            if retry_count > 0 and not did_focus:
                QTimer.singleShot(100, lambda: self.focus_dictionary(retry_count - 1))

            return did_focus

    HotkeyHandler = HotkeyHandlerWindows

else:
    # Dictionary focus not required
    HotkeyHandler = HotkeyHandlerBase



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
            lyt.addWidget(QLabel(text + ':'), i, 0)
            sequence = self.sequence_for_idx(j)
            btn = QPushButton(sequence.to_user_string())
            btn.setFocusPolicy(Qt.NoFocus)
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

        sequence_tuple = config.get('hotkey_' + hotkey[0])
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
            btn.setText('[...]')
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
        config.set('hotkey_' + hotkey[0], [sequence.key, sequence.modifiers])
        self.hotkey_handler.keyboard_handler.add_action(hotkey[0], sequence, remove_existing=True)

        self.current_idx = None



hotkey_handler = HotkeyHandler(aqt.mw)
