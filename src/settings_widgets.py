import aqt
from aqt.qt import *

from .version import VERSION_STRING
from . import config
from . import util
from .languages import Languages
from . import note_type_mgr
from .migaku_connection import ConnectionStatusLabel
from .global_hotkeys import HotkeyConfigWidget, hotkey_handeler


class SettingsWidget(QWidget):

    class WizardPage(QWizardPage):
        
        def __init__(self, widget_cls, parent=None, is_tutorial=True):
            super().__init__(parent)
            self.widget = widget_cls(is_tutorial=is_tutorial)
            if self.widget.TITLE:
                self.setTitle(self.widget.TITLE)
            if self.widget.SUBTITLE:
                self.setSubTitle(self.widget.SUBTITLE)
            if self.widget.PIXMAP:
                self.setPixmap(QWizard.WatermarkPixmap, util.make_pixmap(self.widget.PIXMAP))
            self.lyt = QVBoxLayout()
            self.lyt.setContentsMargins(0, 0, 0, 0)
            self.lyt.addWidget(self.widget)
            self.setLayout(self.lyt)

        def save(self):
            self.widget.save()

    TITLE = None
    SUBTITLE = None
    PIXMAP = None
    BOTTOM_STRETCH = True

    def __init__(self, parent=None, is_tutorial=False):
        super().__init__(parent)

        self.is_tutorial = is_tutorial
    
        self.lyt = QVBoxLayout()
        self.setLayout(self.lyt)
        self.init_ui()
        if self.BOTTOM_STRETCH:
            self.lyt.addStretch()

    def init_ui(self) -> None:
        pass

    def save(self) -> None:
        pass
    
    @classmethod
    def wizard_page(cls, parent=None, is_tutorial=True) -> WizardPage:
        return cls.WizardPage(cls, parent, is_tutorial)

    @classmethod
    def make_label(cls, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextBrowserInteraction)
        lbl.linkActivated.connect(aqt.utils.openLink)
        return lbl

    def add_label(self, text: str) -> QLabel:
        lbl = self.make_label(text)
        self.lyt.addWidget(lbl)
        return lbl


class AboutWidget(SettingsWidget):

    TITLE = 'About'

    def init_ui(self):

        lbl = QLabel(
           F'<h2>Migaku Anki - {VERSION_STRING}</h2>'

            '<h3>License</h3>'
            '<p><a href="https://github.com/migaku-official/Migaku-Anki">Migaku Anki</a> is copyright © 2021 Migaku Ltd. and released under the <a href="https://github.com/migaku-official/Migaku-Anki/blob/main/COPYING">GNU General Public License</a>.</p>'

            '<h3>Third-Party Libraries</h3>'
            '<p>Migaku Anki uses several third-party libraries to function. Below are links to homepages and licenses of these:</p>'
            '<p><a href="https://foosoft.net/projects/yomichan/">Yomichan</a> is used for distributing furigana, and is copyright © 2016-2021 Yomichan Authors and released under the <a href="https://github.com/FooSoft/yomichan/blob/master/LICENSE">GNU General Public License</a>.</p>'
        )
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextBrowserInteraction)
        lbl.linkActivated.connect(aqt.utils.openLink)

        self.lyt.addWidget(lbl)


class WelcomeWidget(SettingsWidget):

    TITLE = 'Welcome!'
    SUBTITLE = 'This is the first time you are using the Migaku Anki add-on.'
    PIXMAP = 'migaku_side.png'

    def init_ui(self):
        welcome_lbl = QLabel('Migaku Anki provieds all features you need to optimally learn languages with Anki and Migaku.<br><br>'
                             'This setup will give you a quick overview over the featureset and explain how to use it.<br><br>'
                             'Let\'s go!<br><br>'
                             'You can always later see this guide and the settings by clicking <i>Migaku > Settings/Help</i>.')
        welcome_lbl.setWordWrap(True)
        self.lyt.addWidget(welcome_lbl)


class LanguageWidget(SettingsWidget):

    TITLE = 'Language Selection'

    def init_ui(self):
        lbl1 = QLabel('Migaku allows you to learn all of the following languages. Please select all the ones you want to learn:')
        lbl1.setWordWrap(True)
        self.lyt.addWidget(lbl1)

        self.lang_list = QListWidget()
        self.lang_list.setFocusPolicy(Qt.NoFocus)
        self.lyt.addWidget(self.lang_list)

        lbl2 = QLabel('Note: This will create a note type for every selected language. '
                      'If you want to uninstall a language, remove the correspending note type with <i>Tools &gt; Manage Note Types</i>.')
        lbl2.setWordWrap(True)
        self.lyt.addWidget(lbl2)

        self.setup_langs()

    def setup_langs(self):
        self.lang_list.clear()

        for lang in Languages:
            is_installed = note_type_mgr.is_installed(lang)
            text = lang.name_en
            if lang.name_native and lang.name_native != lang.name_en:
                text += F' ({lang.name_native})'
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, lang.code)
            item.setCheckState(Qt.Checked if is_installed else Qt.Unchecked)
            if is_installed:
                item.setFlags(item.flags() & ~(Qt.ItemIsEnabled | Qt.ItemIsSelectable))
            self.lang_list.addItem(item)

    def save(self):
        for i in range(self.lang_list.count()):
            item = self.lang_list.item(i)
            lang_code = item.data(Qt.UserRole)
            if item.checkState() == Qt.Checked:
                lang = Languages[lang_code]
                note_type_mgr.install(lang)
        self.setup_langs()


class ExtensionWidget(SettingsWidget):

    TITLE = 'Browser Extension'

    EXTENSION_URL = 'https://www.migaku.io/todo'

    BOTTOM_STRETCH = False

    def init_ui(self, parent=None):

        lbl1 = QLabel('Migaku Anki uses the Migaku Browser Extension as a dictionary, to add syntax to your cards and several other features.<br><br>'
                     F'Make sure to install the extension for your browser to use this functionality. See <a href="{self.EXTENSION_URL}">here</a> for instructinos.<br><br>'
                      'If the browser extension is installed and running, the status below will reflect so.')
        lbl1.setWordWrap(True)
        lbl1.setTextInteractionFlags(Qt.TextBrowserInteraction)
        lbl1.linkActivated.connect(aqt.utils.openLink)
        self.lyt.addWidget(lbl1)
        
        self.lyt.addStretch()
        
        self.lyt.addWidget(ConnectionStatusLabel())


class GlobalHotkeysWidget(SettingsWidget):

    TITLE = 'Global Hotkeys'

    BOTTOM_STRETCH = False

    def init_ui(self, parent=None):

        lbl1 = QLabel('You can use the following hotkeys to interact with the browser extension while it is connected:')
        lbl1.setWordWrap(True)
        self.lyt.addWidget(lbl1)

        self.hotkey_config = HotkeyConfigWidget(hotkey_handeler)
        self.lyt.addWidget(self.hotkey_config)

        lbl2 = QLabel('You can press the buttons on the right and press a new key combination if you want to change it.')
        lbl2.setWordWrap(True)
        self.lyt.addWidget(lbl2)

        self.lyt.addStretch()

        self.lyt.addWidget(ConnectionStatusLabel())

    def save(self):
        config.write()


class SyntaxWidget(SettingsWidget):

    TITLE = 'Language Syntax'

    def init_ui(self, parent=None):

        lbl1 = QLabel('Migaku Anki offers card syntax that can be used in fields to add information to your flashcard fields. '
                      'This information includes (depending on the language): Readings, tone/pitch/gender coloring, '
                      'part of speech and more.<br><br>'
                      'Generally the syntax is added after words, enclosed in square brackets like this:')
        lbl1.setWordWrap(True)
        self.lyt.addWidget(lbl1)

        lbl2 = QLabel('This[this,pron,ðɪs;ðɪs] is[be,aux,ɪz;ɪz] a[a,x,ʌ;eɪ] test[test,noun,test].')
        lbl2.setStyleSheet('background-color:#202020; color:#F8F8F8;')
        lbl2.setWordWrap(True)
        self.lyt.addWidget(lbl2)

        lbl3 = QLabel('<br>On your cards the information in the brackets is displayed in a popup over the word, as ruby text or changes the color of the word, depdning on the language:')
        lbl3.setWordWrap(True)
        self.lyt.addWidget(lbl3)

        lbl4 = QLabel()
        lbl4.setPixmap(util.make_pixmap('syntax_displayed_small_example.png'))
        self.lyt.addWidget(lbl4)


class SyntaxAddRemoveWidget(SettingsWidget):

    TITLE = 'Add/Remove Language Syntax'

    def init_ui(self):        

        lbl1 = QLabel('To add or update syntax of your cards go to any editor window in Anki, select a field and press F2 or press this button (icons vary depending on language:')
        lbl1.setWordWrap(True)
        self.lyt.addWidget(lbl1)

        lbl2 = QLabel()
        lbl2.setPixmap(util.make_pixmap('syntax_buttons_example.png'))
        self.lyt.addWidget(lbl2)

        lbl3 = QLabel('<br>Make sure the browser extension is connected when using these features.<br><br>'
                      'To remove syntax either press F4 or press the right button.')
        lbl3.setWordWrap(True)
        self.lyt.addWidget(lbl3)


class InplaceEditorWidget(SettingsWidget):

    TITLE = 'Inplace Editor'

    def init_ui(self):

        self.add_label(
            'With Migaku Anki you can edit your flash cards during your reviews.<br><br>'
            'To do so simply double click any field on your card. A cursor will appear and you can freely edit the field and even paste images and audio files. '
            'Simply click out of the field to finish editing.<br><br>'
            'If you want to add editing support to your own note types add the "editable" filter before the field names:'
        )

        lbl = QLabel('{{ExampleField}} -> {{editable:ExampleField}}')
        lbl.setStyleSheet('background-color:#202020; color:#F8F8F8;')
        lbl.setWordWrap(True)
        self.lyt.addWidget(lbl)

        self.add_label('')

        self.add_label('By enabling the following option you can also edit empty fields on your cards:')

        show_empty_fields = QCheckBox('Show empty fields')
        show_empty_fields.setChecked(config.get('inplace_editor_show_empty_fields', False))
        show_empty_fields.stateChanged.connect(lambda state: config.set('inplace_editor_show_empty_fields', state == Qt.Checked))
        self.lyt.addWidget(show_empty_fields)

    def save(self):
        from .inplace_editor import update_show_empty_fields
        update_show_empty_fields()


class ReviewWidget(SettingsWidget):

    TITLE = 'Review Settings'

    def init_ui(self):

        self.add_label(
            'By default Anki allows grading cards as Again, Hard, Good and Easy.<br>'
            'The hard and easy buttons can lead to unnecessarily long grading descision times as well to permanently seeing cards too often/little.<br>'
            'Enabling Pass/Fail will remove those buttons.'
        )

        pass_fail = QCheckBox('Enable Pass/Fail (Recommended)')
        pass_fail.setChecked(config.get('reviewer_pass_fail', True))
        pass_fail.stateChanged.connect(lambda state: config.set('reviewer_pass_fail', state == Qt.Checked))
        self.lyt.addWidget(pass_fail)

        self.add_label('<hr>')

        self.add_label(
            'The negative effects of the ease factor can be prevented by fixing the ease factor (how difficult a card is considered) in place.<br>'
            'This option will prevent those effects if you want to use the Easy/Hard buttons and fixes negative effects caused in the past.'
        )

        pass_fail = QCheckBox('Maintain Ease Factor (Recommended)')
        pass_fail.setChecked(config.get('maintain_ease', True))
        pass_fail.stateChanged.connect(lambda state: config.set('maintain_ease', state == Qt.Checked))
        self.lyt.addWidget(pass_fail)

        self.add_label('<hr>')

        colored_buttons = QCheckBox('Colored Grading Buttons')
        colored_buttons.setChecked(config.get('reviewer_button_coloring', True))
        colored_buttons.stateChanged.connect(lambda state: config.set('reviewer_button_coloring', state == Qt.Checked))
        self.lyt.addWidget(colored_buttons)

    def save(self):
        config.write()


class MediaFileWidget(SettingsWidget):

    TITLE = 'Media Files'

    def init_ui(self):
        self.add_label(
            'Audio files imported via the Browser Extension can be in many formats, some of which cannot be played by some versions of Anki or have a very large file size.<br>'
            'The option below will convert all media files exported from the Browser Extension to the MP3 format.'
        )

        convert_audio_mp3 = QCheckBox('Convert audio files to MP3 (Recommended)')
        convert_audio_mp3.setChecked(config.get('convert_audio_mp3', True))
        convert_audio_mp3.stateChanged.connect(lambda state: config.set('convert_audio_mp3', state == Qt.Checked))
        self.lyt.addWidget(convert_audio_mp3)


class CondensedAudioWidget(SettingsWidget):

    TITLE = 'Condensed Audio'

    def init_ui(self):
        self.add_label(
            'Condensed audio exported from the Browser Extension will be exported to the following folder:'
        )

        self.dir_label = QLabel(config.get('condensed_audio_dir', 'None'))
        self.lyt.addWidget(self.dir_label)

        btn = QPushButton('Change')
        btn.clicked.connect(self.change_dir)
        self.lyt.addWidget(btn)

        self.add_label('<hr>')

        self.add_label(
            'By enabling the following option you can keep using Anki while condensed audio is being exported. '
            'Keep in mind that the condensing process will be cancelled when closing Anki.'
        )

        condensed_audio_messages_disabled = QCheckBox('Disable progress and completion messages.')
        condensed_audio_messages_disabled.setChecked(config.get('condensed_audio_messages_disabled', False))
        condensed_audio_messages_disabled.stateChanged.connect(lambda state: config.set('condensed_audio_messages_disabled', state == Qt.Checked))
        self.lyt.addWidget(condensed_audio_messages_disabled)

    def change_dir(self):
        new_dir = QFileDialog.getExistingDirectory(self, 'Choose Directory')
        if new_dir:
            config.set('condensed_audio_dir', new_dir)
            self.dir_label.setText(new_dir)


SETTINGS_WIDGETS = [
    AboutWidget,
    LanguageWidget,
    ExtensionWidget,
    GlobalHotkeysWidget,
    SyntaxWidget,
    SyntaxAddRemoveWidget,
    InplaceEditorWidget,
    ReviewWidget,
    MediaFileWidget,
    CondensedAudioWidget,
]

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