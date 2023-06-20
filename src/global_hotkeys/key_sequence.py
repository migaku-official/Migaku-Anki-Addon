from typing import Optional
from anki.utils import is_win, is_mac

class KeySequence:
    Shift = 1 << 0
    Alt = 1 << 1
    Ctrl = 1 << 2
    Meta = 1 << 3

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
            return "Disabled"

        key_strings = []
        if is_mac:
            join_char = ""
            if self.modifiers & self.Ctrl:
                key_strings.append("⌃")
            if self.modifiers & self.Alt:
                key_strings.append("⌥")
            if self.modifiers & self.Shift:
                key_strings.append("⇧")
            if self.modifiers & self.Meta:
                key_strings.append("⌘")
        else:
            join_char = "+"
            if self.modifiers & self.Ctrl:
                key_strings.append("Ctrl")
            if self.modifiers & self.Alt:
                key_strings.append("Alt")
            if self.modifiers & self.Shift:
                key_strings.append("Shift")
            if self.modifiers & self.Meta:
                key_strings.append("Win" if is_win else "Meta")

        key_segs = [seg.capitalize() for seg in self.key.split("_")]
        key_strings.append(" ".join(key_segs))

        return join_char.join(key_strings)

    def __repr__(self):
        return f"<{type(self).__name__} {self.to_user_string()}>"
