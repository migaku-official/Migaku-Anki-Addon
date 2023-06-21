from aqt.qt import QObject, pyqtSignal
from magicy.keyboard import Key, Listener

from .key_sequence import KeySequence

modifier_map = {
    Key.shift: 1 << 0,
    Key.alt: 1 << 1,
    Key.ctrl: 1 << 2,
    Key.cmd: 1 << 3,
}


class KeyboardHandler(QObject):
    key_pressed = pyqtSignal(KeySequence)
    key_released = pyqtSignal(KeySequence)

    action_fired = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.block_actions = False
        self.actions = {False: {}, True: {}}
        self.modifiers = 0

        self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def is_available(self):
        if hasattr(self.listener, "IS_TRUSTED") and not self.listener.IS_TRUSTED:
            return False
        return True

    def on_press(self, raw_key):
        raw_key = self.listener.canonical(raw_key)

        if raw_key in modifier_map:
            self.modifiers |= modifier_map[raw_key]
        else:
            key = self.parse_raw_key(raw_key)
            sequence = KeySequence(key, self.modifiers)
            self.key_pressed.emit(sequence)
            if not self.block_actions and sequence in self.actions[False]:
                self.action_fired.emit(self.actions[False][sequence])

    def on_release(self, raw_key):
        raw_key = self.listener.canonical(raw_key)

        if raw_key in modifier_map:
            self.modifiers &= ~modifier_map[raw_key]
        else:
            key = self.parse_raw_key(raw_key)
            sequence = KeySequence(key, self.modifiers)
            self.key_released.emit(sequence)
            if not self.block_actions and sequence in self.actions[True]:
                self.action_fired.emit(self.actions[True][sequence])

    def add_action(
        self,
        action: str,
        sequnce: KeySequence,
        on_release: bool = False,
        remove_existing: bool = False,
    ):
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
        if raw.startswith("Key."):
            raw = raw[4:]
        elif len(raw) >= 3:
            return raw[1:-1]
        return raw
