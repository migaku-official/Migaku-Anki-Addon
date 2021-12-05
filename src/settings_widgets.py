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

    def init_ui(self):
        pass

    def save(self):
        pass
    
    @classmethod
    def wizard_page(cls, parent=None, is_tutorial=True):
        return cls.WizardPage(cls, parent, is_tutorial)



class AboutWidget(SettingsWidget):

    TITLE = 'About'

    def init_ui(self):
        lbl = QLabel(
            F'<h2>Migaku Anki - {VERSION_STRING}</h2>'

            '<h3>Third-Party Libraries</h3>'
            '<p>Migaku Anki uses several third-party libraries to function. Below are links to homepages and licenses of these:</p>'
            '<p><a href="https://foosoft.net/projects/yomichan/">Yomichan</a> is used for distributing furigana, and is copyright © 2016-2021 Yomichan Authors and released under the <a href="https://github.com/FooSoft/yomichan/blob/master/LICENSE">GNU General Public License</a>.</p>'

            '<h3>License</h3>'
            '<p><a href="https://github.com/migaku-official/Migaku-Anki">Migaku Anki</a> is copyright © 2021 Migaku Ltd. and released under the <a href="https://github.com/migaku-official/Migaku-Anki/blob/main/LICENCE">GNU General Public License v3.0</a>.</p>'
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
                             'Let\'s go!<br>')
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
            text = lang.name_en
            if lang.name_native and lang.name_native != lang.name_en:
                text += F' ({lang.name_native})'
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, lang.code)
            item.setCheckState(Qt.Checked if note_type_mgr.is_installed(lang) else Qt.Unchecked)
            self.lang_list.addItem(item)

    def save(self):
        for i in range(self.lang_list.count()):
            item = self.lang_list.item(i)
            lang_code = item.data(Qt.UserRole)
            if item.checkState() == Qt.Checked:
                lang = Languages[lang_code]
                note_type_mgr.install(lang)


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

        lbl3 = QLabel('<br>Make sure the browser extension is connected when using this features.<br><br>'
                      'To remove syntax either press F4 or press the right button.')
        lbl3.setWordWrap(True)
        self.lyt.addWidget(lbl3)


class InplaceEditorWidget(SettingsWidget):

    TITLE = 'Inplace Editor'

    def init_ui(self):  

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        lbl1 = QLabel('With Migaku Anki you can edit your flash cards during your reviews.<br><br>'
                      'To do so simply double click any field on your card. A cursor will appear and you can freely edit the field and even paste images and audio files. '
                      'Simply click out of the field to finish editing.<br><br>'
                      'If you want to add editing support to your own note types add the "editable" filter before the field names:')
        lbl1.setWordWrap(True)
        self.lyt.addWidget(lbl1)

        lbl2 = QLabel('{{ExampleField}} -> {{editable:ExampleField}}')
        lbl2.setStyleSheet('background-color:#202020; color:#F8F8F8;')
        lbl2.setWordWrap(True)
        self.lyt.addWidget(lbl2)


class ReviewWidget(SettingsWidget):

    TITLE = 'Review Settings'

    def init_ui(self):  

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        lbl1 = QLabel('TODO')
        lbl1.setWordWrap(True)
        self.lyt.addWidget(lbl1)

        pass_fail = QCheckBox('Pass/Fail')
        pass_fail.setChecked(config.get('review_pass_fail', True))
        pass_fail.stateChanged.connect(lambda state: config.set('review_pass_fail', state == Qt.Checked))
        self.lyt.addWidget(pass_fail)

        colored_buttons = QCheckBox('Colored Grading Buttons')
        colored_buttons.setChecked(config.get('reviewer_button_coloring', True))
        colored_buttons.stateChanged.connect(lambda state: config.set('reviewer_button_coloring', state == Qt.Checked))
        self.lyt.addWidget(colored_buttons)

    def save(self):
        config.write()


SETTINGS_WIDGETS = [
    AboutWidget,
    LanguageWidget,
    ExtensionWidget,
    GlobalHotkeysWidget,
    SyntaxWidget,
    SyntaxAddRemoveWidget,
    InplaceEditorWidget,
    ReviewWidget,
]

TUTORIAL_WIDGETS = [
    WelcomeWidget,
    LanguageWidget,
    ExtensionWidget,
    GlobalHotkeysWidget,
    SyntaxWidget,
    SyntaxAddRemoveWidget,
    InplaceEditorWidget,
]