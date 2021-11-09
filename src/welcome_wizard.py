import aqt
from aqt.qt import *

from . import util
from . import config
from .langauges import Languages
from . import note_type_mgr
from .migaku_connection import ConnectionStatusLabel
from .global_hotkeys import HotkeyConfigWidget, hotkey_handeler
from . import config


class WelcomeWizard(QWizard):

    INITIAL_SIZE = (625, 440)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Welcome! - Migaku Anki')
        self.setWindowIcon(util.default_icon())

        self.setMinimumSize(*self.INITIAL_SIZE)
        self.resize(*self.INITIAL_SIZE)

        self.addPage(WelcomePage())

        self.lang_page = LanguagePage()
        self.addPage(self.lang_page)

        self.addPage(ExtensionPage())

        self.hotkey_page = HotkeyPage()
        self.addPage(self.hotkey_page)

        self.addPage(SyntaxPage())
        self.addPage(SyntaxAddRemovePage())

        self.addPage(InplaceEditorPage())

        self.finished.connect(self.save)

    def save(self):
        self.lang_page.save()
        config.set('first_run', False)
        config.write()  # HotkeyConfigWidget does not save automatically

    @classmethod
    def check_show_modal(cls):
        if config.get('first_run', True) or aqt.mw.app.queryKeyboardModifiers() & Qt.ControlModifier:
            wizard = cls()
            return wizard.exec_()


class WelcomePage(QWizardPage):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Welcome!')
        self.setSubTitle('This is the first time you are using the Migaku Anki add-on.')

        self.setPixmap(QWizard.WatermarkPixmap, util.make_pixmap('migaku_side.png'))

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        welcome_lbl = QLabel('Migaku Anki provieds all features you need to optimally learn languages with Anki and Migaku.<br><br>'
                             'This setup will give you a quick overview over the featureset and explain how to use it.<br><br>'
                             'Let\'s go!<br>')
        welcome_lbl.setWordWrap(True)
        lyt.addWidget(welcome_lbl)

        lyt.addStretch()


class LanguagePage(QWizardPage):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Language Selection')

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        lbl1 = QLabel('Migaku allows you to learn all of the following languages. Please select all the ones you want to learn:')
        lbl1.setWordWrap(True)
        lyt.addWidget(lbl1)

        self.lang_list = QListWidget()
        self.lang_list.setFocusPolicy(Qt.NoFocus)
        lyt.addWidget(self.lang_list)

        lbl2 = QLabel('Note: This will create a note type for every selected language. '
                      'You can also later add Migaku note types under Tools > Mangage Note Types > Add Migaku Note Types. '
                      'If you want to use your own note types you can add Migaku language support to them under Tools > Mangage Note Types > Migaku Options.')
        lbl2.setWordWrap(True)
        lyt.addWidget(lbl2)

        lyt.addStretch()

        self.setup_langs()

    def setup_langs(self):
        self.lang_list.clear()

        for lang in Languages:
            text = lang.name_en
            if lang.name_native and lang.name_native != lang.name_en:
                text += F' ({lang.name_native})'
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, lang.code)
            item.setCheckState(Qt.Unchecked)
            self.lang_list.addItem(item)

    def save(self):
        for i in range(self.lang_list.count()):
            item = self.lang_list.item(i)
            lang_code = item.data(Qt.UserRole)
            if item.checkState() == Qt.Checked:
                lang = Languages[lang_code]
                note_type_mgr.install(lang)


class ExtensionPage(QWizardPage):

    EXTENSION_URL = 'https://www.migaku.io/todo'

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Browser Extension')

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        lbl1 = QLabel('Migaku Anki uses the Migaku Browser Extension as a dictionary, to add syntax to your cards and several other features.<br><br>'
                     F'Make sure to install the extension for your browser to use this functionality. See <a href="{self.EXTENSION_URL}">here</a> for instructinos.<br><br>'
                      'If the browser extension is installed and running, the status below will reflect so.')
        lbl1.setWordWrap(True)
        lbl1.setTextInteractionFlags(Qt.TextBrowserInteraction)
        lbl1.linkActivated.connect(aqt.utils.openLink)
        lyt.addWidget(lbl1)

        lyt.addStretch()

        lyt.addWidget(ConnectionStatusLabel())


class HotkeyPage(QWizardPage):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Global Hotkeys')

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        lbl1 = QLabel('You can use the following hotkeys to interact with the browser extension while it is connected:')
        lbl1.setWordWrap(True)
        lyt.addWidget(lbl1)

        self.hotkey_config = HotkeyConfigWidget(hotkey_handeler)
        lyt.addWidget(self.hotkey_config)

        lbl2 = QLabel('You can press the buttons on the right and press a new key combination if you want to change it.')
        lbl2.setWordWrap(True)
        lyt.addWidget(lbl2)

        lyt.addStretch()

        lyt.addWidget(ConnectionStatusLabel())


class SyntaxPage(QWizardPage):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Language Syntax')

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        lbl1 = QLabel('Migaku Anki offers card syntax that can be used in fields to add information to your flashcard fields. '
                      'This information includes (depending on the language): Readings, tone/pitch/gender coloring, '
                      'part of speech and more.<br><br>'
                      'Generally the syntax is added after words, enclosed in square brackets like this:')
        lbl1.setWordWrap(True)
        lyt.addWidget(lbl1)

        lbl2 = QLabel('This[this,pron,ðɪs;ðɪs] is[be,aux,ɪz;ɪz] a[a,x,ʌ;eɪ] test[test,noun,test].')
        lbl2.setStyleSheet('background-color:#202020; color:#F8F8F8;')
        lbl2.setWordWrap(True)
        lyt.addWidget(lbl2)

        lbl3 = QLabel('<br>On your cards the information in the brackets is displayed in a popup over the word, as ruby text or changes the color of the word, depdning on the language:')
        lbl3.setWordWrap(True)
        lyt.addWidget(lbl3)

        lbl4 = QLabel()
        lbl4.setPixmap(util.make_pixmap('syntax_displayed_small_example.png'))
        lyt.addWidget(lbl4)


class SyntaxAddRemovePage(QWizardPage):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Add/Remove Language Syntax')

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        lbl1 = QLabel('To add or update syntax of your cards go to any editor window in Anki, select a field and press F2 or press this button (icons vary depending on language:')
        lbl1.setWordWrap(True)
        lyt.addWidget(lbl1)

        lbl2 = QLabel()
        lbl2.setPixmap(util.make_pixmap('syntax_buttons_example.png'))
        lyt.addWidget(lbl2)

        lbl3 = QLabel('<br>Make sure the browser extension is connected when using this features.<br><br>'
                      'To remove syntax either press F4 or press the right button.')
        lbl3.setWordWrap(True)
        lyt.addWidget(lbl3)


class InplaceEditorPage(QWizardPage):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Inplace Editor')

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        lbl1 = QLabel('With Migaku Anki you can edit your flash cards during your reviews.<br><br>'
                      'To do so simply double click any field on your card. A cursor will appear and you can freely edit the field and even paste images and audio files. '
                      'Simply click out of the field to finish editing.<br><br>'
                      'If you want to add editing support to your own note types add the "editing" filter before the field names:')
        lbl1.setWordWrap(True)
        lyt.addWidget(lbl1)

        lbl2 = QLabel('{{ExampleField}} -> {{editable:ExampleField}}')
        lbl2.setStyleSheet('background-color:#202020; color:#F8F8F8;')
        lbl2.setWordWrap(True)
        lyt.addWidget(lbl2)


aqt.gui_hooks.profile_did_open.append(WelcomeWizard.check_show_modal)
