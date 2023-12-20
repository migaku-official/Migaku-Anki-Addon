import aqt
from aqt.qt import *

from .settings_widget import SettingsWidget
from .languages import Languages
from .migaku_connection import ConnectionStatusLabel
from .global_hotkeys import HotkeyConfigWidget, hotkey_handler

from . import config, util, note_type_mgr


class WelcomeWidget(SettingsWidget):
    TITLE = "Welcome!"
    SUBTITLE = "This is the first time you are using the Migaku Anki add-on."
    PIXMAP = "migaku_side.png"

    def init_ui(self):
        welcome_lbl = QLabel(
            "Migaku Anki provides all features you need to optimally learn languages with Anki and Migaku.<br><br>"
            "This setup will give you a quick overview over the feature-set and explain how to use it.<br><br>"
            "Let's go!<br><br>"
            "You can always later see this guide and the settings by clicking <i>Migaku > Settings/Help</i>."
        )
        welcome_lbl.setWordWrap(True)
        self.lyt.addWidget(welcome_lbl)


class LanguageWidget(SettingsWidget):
    TITLE = "Language Selection"

    def init_ui(self):
        lbl1 = QLabel(
            "Migaku allows you to learn all of the following languages. Please select all the ones you want to learn:"
        )
        lbl1.setWordWrap(True)
        self.lyt.addWidget(lbl1)

        self.lang_list = QListWidget()
        self.lang_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.lyt.addWidget(self.lang_list)

        lbl2 = QLabel(
            "Note: This will create a note type for every selected language. "
            "If you want to uninstall a language, remove the correspending note type with <i>Tools &gt; Manage Note Types</i>."
        )
        lbl2.setWordWrap(True)
        self.lyt.addWidget(lbl2)

        self.setup_langs()

    def setup_langs(self):
        self.lang_list.clear()

        for lang in Languages:
            is_installed = note_type_mgr.is_installed(lang)
            text = lang.name_en
            if lang.name_native and lang.name_native != lang.name_en:
                text += f" ({lang.name_native})"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, lang.code)
            item.setCheckState(
                Qt.CheckState.Checked if is_installed else Qt.CheckState.Unchecked
            )
            if is_installed:
                item.setFlags(
                    item.flags()
                    & ~(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                )
            self.lang_list.addItem(item)

    def save(self):
        for i in range(self.lang_list.count()):
            item = self.lang_list.item(i)
            lang_code = item.data(Qt.ItemDataRole.UserRole)
            if item.checkState() == Qt.CheckState.Checked:
                lang = Languages[lang_code]
                note_type_mgr.install(lang)
        self.setup_langs()


class ExtensionWidget(SettingsWidget):
    TITLE = "Browser Extension"

    EXTENSION_URL = "https://www.migaku.io/todo"

    BOTTOM_STRETCH = False

    def init_ui(self, parent=None):
        lbl1 = QLabel(
            "Migaku Anki uses the Migaku Browser Extension as a dictionary, to add syntax to your cards and several other features.<br><br>"
            f'Make sure to install the extension for your browser to use this functionality. See <a href="{self.EXTENSION_URL}">here</a> for instructions.<br><br>'
            "If the browser extension is installed and running, the status below will reflect so."
        )
        lbl1.setWordWrap(True)
        lbl1.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        lbl1.linkActivated.connect(aqt.utils.openLink)
        self.lyt.addWidget(lbl1)

        # Information on changing port
        self.custom_port_hr = self.add_label("<hr>")
        self.custom_port_info = self.add_label(
            "In some cases, you might want to have Anki and the browser extension communicate on a custom port, because another application is already using the default port. <b>You need to set the same port in the browser extension settings!</b> You need to restart Anki after changing the port. "
        )

        self.custom_port = QLineEdit(config.get("port", ""))
        self.custom_port.setPlaceholderText(str(util.DEFAULT_PORT))
        self.custom_port.textChanged.connect(
            lambda text: config.set("port", text if len(text) else None)
        )

        self.lyt.addWidget(self.custom_port)

        self.lyt.addStretch()
        self.lyt.addWidget(ConnectionStatusLabel())

    def toggle_advanced(self, state: bool) -> None:
        if not state:
            self.custom_port_hr.hide()
            self.custom_port_info.hide()
            self.custom_port.hide()

        else:
            self.custom_port_hr.show()
            self.custom_port_info.show()
            self.custom_port.show()


class GlobalHotkeysWidget(SettingsWidget):
    TITLE = "Global Hotkeys"

    BOTTOM_STRETCH = False

    def init_ui(self, parent=None):
        if not hotkey_handler.is_available():
            self.add_label(
                "For Migaku global hotkeys to work, you must allow Anki to monitor keyboard inputs.\n\n"
                'To do this, go to System Preferences > Security & Privacy > Privacy. Then for both "<b>Accessibility</b>" and "<b>Input Monitoring</b>" check the box for "Anki".\n\n'
                "These permissions are required to detect when the specified shortcuts are pressend and are required to copy the selected text. "
                "Finally restart Anki."
            )
            return

        self.add_label(
            "You can use the following hotkeys to interact with the browser extension while it is connected:"
        )

        self.hotkey_config = HotkeyConfigWidget(hotkey_handler)
        self.lyt.addWidget(self.hotkey_config)

        self.add_label(
            "To set new key combinations click the buttons on the right and press a new key combination. "
            "To disable a hotkey click the button again without pressing a new key combination."
        )
        self.add_label("<hr>")
        self.add_label(
            "If you are using the new extension, hotkeys require the Migaku App window to be open."
        )

        self.lyt.addStretch()
        self.lyt.addWidget(ConnectionStatusLabel())

    def save(self):
        config.write()


class SyntaxWidget(SettingsWidget):
    TITLE = "Language Syntax"

    def init_ui(self, parent=None):
        lbl1 = QLabel(
            "Migaku Anki offers card syntax that can be used in fields to add information to your flashcard fields. "
            "This information includes (depending on the language): Readings, tone/pitch/gender coloring, "
            "part of speech and more.<br><br>"
            "Generally the syntax is added after words, enclosed in square brackets like this:"
        )
        lbl1.setWordWrap(True)
        self.lyt.addWidget(lbl1)

        lbl2 = QLabel(
            "This[this,pron,ðɪs;ðɪs] is[be,aux,ɪz;ɪz] a[a,x,ʌ;eɪ] test[test,noun,test]."
        )
        lbl2.setStyleSheet("background-color:#202020; color:#F8F8F8;")
        lbl2.setWordWrap(True)
        self.lyt.addWidget(lbl2)

        lbl3 = QLabel(
            "<br>On your cards the information in the brackets is displayed in a popup over the word, as ruby text or changes the color of the word, depending on the language:"
        )
        lbl3.setWordWrap(True)
        self.lyt.addWidget(lbl3)

        lbl4 = QLabel()
        lbl4.setPixmap(util.make_pixmap("syntax_displayed_small_example.png"))
        self.lyt.addWidget(lbl4)


class SyntaxAddRemoveWidget(SettingsWidget):
    TITLE = "Add/Remove Language Syntax"

    def init_ui(self):
        lbl1 = QLabel(
            "To add or update syntax of your cards go to any editor window in Anki, select a field and press F2 or press this button (icons vary depending on language:"
        )
        lbl1.setWordWrap(True)
        self.lyt.addWidget(lbl1)

        lbl2 = QLabel()
        lbl2.setPixmap(util.make_pixmap("syntax_buttons_example.png"))
        self.lyt.addWidget(lbl2)

        lbl3 = QLabel(
            "<br>Make sure the browser extension is connected when using these features.<br><br>"
            "To remove syntax either press F4 or press the right button."
        )
        lbl3.setWordWrap(True)
        self.lyt.addWidget(lbl3)


class InplaceEditorWidget(SettingsWidget):
    TITLE = "Inplace Editor"

    def init_ui(self):
        self.add_label(
            "With Migaku Anki you can edit your flash cards during your reviews.<br><br>"
            "To do so simply double click any field on your card. A cursor will appear and you can freely edit the field and even paste images and audio files. "
            "Simply click out of the field to finish editing.<br><br>"
            'If you want to add editing support to your own note types add the "editable" filter before the field names:'
        )

        lbl = QLabel("{{ExampleField}} -> {{editable:ExampleField}}")
        lbl.setStyleSheet("background-color:#202020; color:#F8F8F8;")
        lbl.setWordWrap(True)
        self.lyt.addWidget(lbl)

        self.add_label("")

        self.add_label(
            "By enabling the following option you can also edit empty fields on your cards:"
        )

        show_empty_fields = QCheckBox("Show empty fields")
        show_empty_fields.setChecked(
            config.get("inplace_editor_show_empty_fields", False)
        )
        show_empty_fields.toggled.connect(
            lambda checked: config.set("inplace_editor_show_empty_fields", checked)
        )
        self.lyt.addWidget(show_empty_fields)

    def save(self):
        from .inplace_editor import update_show_empty_fields

        update_show_empty_fields()


class ReviewWidget(SettingsWidget):
    TITLE = "Review Settings"

    def init_ui(self):
        self.add_label(
            "By default Anki allows grading cards as Again, Hard, Good and Easy.<br>"
            "The hard and easy buttons can lead to unnecessarily long grading decision times as well as permanently seeing cards too often/little.<br>"
            "Enabling Pass/Fail will remove those buttons."
        )

        pass_fail = QCheckBox("Enable Pass/Fail (Recommended)")
        pass_fail.setChecked(config.get("reviewer_pass_fail", True))
        pass_fail.toggled.connect(
            lambda checked: config.set("reviewer_pass_fail", checked)
        )
        self.lyt.addWidget(pass_fail)

        self.add_label("<hr>")

        self.add_label(
            "The negative effects of the ease factor can be prevented by fixing the ease factor (how difficult a card is considered) in place.<br>"
            "This option will prevent those effects if you want to use the Easy/Hard buttons and fixes negative effects caused in the past."
        )

        pass_fail = QCheckBox("Maintain Ease Factor (Recommended)")
        pass_fail.setChecked(config.get("maintain_ease", True))
        pass_fail.toggled.connect(lambda checked: config.set("maintain_ease", checked))
        self.lyt.addWidget(pass_fail)

        self.add_label(
            "If you review cards on mobile devices your ease factor will not be maintained. "
            'To reset it press "Reset Ease Factor" from the Migaku menu. Note that this action will force a full sync.'
        )

        self.add_label("<hr>")

        colored_buttons = QCheckBox("Colored Grading Buttons")
        colored_buttons.setChecked(config.get("reviewer_button_coloring", True))
        colored_buttons.toggled.connect(
            lambda checked: config.set("reviewer_button_coloring", checked)
        )
        self.lyt.addWidget(colored_buttons)

    def save(self):
        config.write()


TUTORIAL_WIDGETS = [
    WelcomeWidget,
    LanguageWidget,
    ExtensionWidget,
    GlobalHotkeysWidget,
    SyntaxWidget,
    SyntaxAddRemoveWidget,
    InplaceEditorWidget,
    ReviewWidget,
]
