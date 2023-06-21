from aqt.qt import QObject, QTimer
from aqt import mw
from magicy.keyboard import Key, Controller
from anki.utils import is_mac, is_win, is_lin

from .. import config
from .. import util

from .key_sequence import KeySequence
from .keyboard import KeyboardHandler


class HotkeyHandlerBase(QObject):
    hotkeys = [
        (
            "open_dict",
            KeySequence("f", KeySequence.Ctrl | KeySequence.Alt),
            "Open dictionary",
        ),
        (
            "search_dict",
            KeySequence("d", KeySequence.Ctrl | KeySequence.Alt),
            "Search selected text in dictionary",
        ),
        (
            "set_sentence",
            KeySequence("s", KeySequence.Ctrl | KeySequence.Alt),
            "Send sentence to card creator",
        ),
        (
            "add_definition",
            KeySequence("g", KeySequence.Ctrl | KeySequence.Alt),
            "Send definition to card creator",
        ),
        (
            "search_collection",
            KeySequence("b", KeySequence.Ctrl | KeySequence.Alt),
            "Search selected text in card collection",
        ),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)

        self.selected_text_handler = None

        self.keyboard_controller = Controller()

        self.keyboard_handler = KeyboardHandler()
        self.keyboard_handler.action_fired.connect(self.on_action_fired)

        for action, default_sequence, _ in self.hotkeys:
            sequence_tuple = config.get("hotkey_" + action)
            if sequence_tuple:
                sequence = KeySequence(*sequence_tuple)
                self.keyboard_handler.add_action(action, sequence)
            else:
                sequence = default_sequence
                self.keyboard_handler.add_action(action, sequence)

    def is_available(self):
        return self.keyboard_handler.is_available()

    def on_action_fired(self, action):
        if action == "open_dict":
            mw.migaku_connection.open_dict()
            self.focus_dictionary()
        if action in [
            "search_dict",
            "set_sentence",
            "add_definition",
            "search_collection",
        ]:
            self.request_selected_text(action)

    def request_selected_text(self, action):
        modifier_keys = [
            Key.alt_gr,
            Key.alt,
            Key.alt_l,
            Key.alt_r,
            Key.cmd,
            Key.cmd_l,
            Key.cmd_r,
            Key.ctrl,
            Key.ctrl_l,
            Key.ctrl_r,
            Key.shift,
            Key.shift_l,
            Key.shift_r,
        ]

        if not is_lin:
            for key in modifier_keys:
                self.keyboard_controller.release(key)

        with self.keyboard_controller.pressed(Key.cmd if is_mac else Key.ctrl):
            self.keyboard_controller.press("c")
            self.keyboard_controller.release("c")

        self.selected_text_handler = action
        QTimer.singleShot(100, self.handle_selected_text)

    def handle_selected_text(self):
        action = self.selected_text_handler
        if not action:
            return
        text = mw.app.clipboard().text()

        if action == "search_dict":
            mw.migaku_connection.search_dict(text)
            self.focus_dictionary()
        elif action == "set_sentence":
            mw.migaku_connection.set_sentence(text)
            self.focus_dictionary()
        elif action == "add_definition":
            mw.migaku_connection.add_definition(text)
            self.focus_dictionary()
        elif action == "search_collection":
            util.open_browser(text)

    def focus_dictionary(self):
        # Implemented in derived classes if required
        pass


if is_win:
    import ctypes

    class HotkeyHandler(HotkeyHandlerBase):
        def focus_dictionary(self, retry_count=5):
            enum_windows_proc = ctypes.WINFUNCTYPE(
                ctypes.c_bool, ctypes.c_int, ctypes.POINTER(ctypes.c_int)
            )

            did_focus = False

            # window_handle: hwnd
            def foreach_window(window_handle: int, _lparam):
                if not ctypes.windll.user32.IsWindowVisible(window_handle):
                    return True

                nonlocal did_focus
                title_length = ctypes.windll.user32.GetWindowTextLengthW(window_handle)
                title_buff = ctypes.create_unicode_buffer(title_length + 1)
                ctypes.windll.user32.GetWindowTextW(
                    window_handle, title_buff, title_length + 1
                )

                title = title_buff.value
                if title == "Migaku Dictionary":
                    ctypes.windll.user32.SetForegroundWindow(window_handle)
                    did_focus = True
                    return False
                return True

            ctypes.windll.user32.EnumWindows(enum_windows_proc(foreach_window), 0)

            if retry_count > 0 and not did_focus:
                QTimer.singleShot(100, lambda: self.focus_dictionary(retry_count - 1))

            return did_focus

elif is_mac:

    class HotkeyHandler(HotkeyHandlerBase):
        hotkeys = [
            ("open_dict", KeySequence(), "Open dictionary"),
            ("search_dict", KeySequence(), "Search selected text in dictionary"),
            ("set_sentence", KeySequence(), "Send sentence to card creator"),
            ("add_definition", KeySequence(), "Send definition to card creator"),
            (
                "search_collection",
                KeySequence(),
                "Search selected text in card collection",
            ),
        ]

else:
    # Dictionary focus not required
    class HotkeyHandler(HotkeyHandlerBase):
        pass
