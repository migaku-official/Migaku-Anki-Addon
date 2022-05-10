import aqt
from aqt.qt import *

from .version import VERSION_STRING
from . import config
from . import util
from .languages import Languages
from . import note_type_mgr
from .migaku_connection import ConnectionStatusLabel
from .global_hotkeys import HotkeyConfigWidget, hotkey_handler
from .balance_scheduler_vacation_window import BalanceSchedulerVacationWindow


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
                if hasattr(QWizard, 'WizardPixmap'):
                    QWizard_WatermarkPixmap = QWizard.WizardPixmap.WatermarkPixmap
                else:
                    QWizard_WatermarkPixmap = QWizard.WatermarkPixmap
                self.setPixmap(QWizard_WatermarkPixmap,
                               util.make_pixmap(self.widget.PIXMAP))
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
        self.toggle_advanced(False)
        if self.BOTTOM_STRETCH:
            self.lyt.addStretch()

    def init_ui(self) -> None:
        pass

    def toggle_advanced(self, state: bool) -> None:
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

        self.add_label(
            F'<h2>Migaku Anki - {VERSION_STRING}</h2>'

            '<h3>License</h3>'
            '<p><a href="https://github.com/migaku-official/Migaku-Anki">Migaku Anki</a> is copyright © 2022 Migaku Ltd. and released under the <a href="https://github.com/migaku-official/Migaku-Anki/blob/main/COPYING">GNU General Public License</a>.</p>'

            '<h3>Third-Party Libraries</h3>'
            '<p>Migaku Anki uses several third-party libraries to function. Below are links to homepages and licenses of these:</p>'
            '<p><a href="https://foosoft.net/projects/yomichan/">Yomichan</a> is used for distributing furigana, and is copyright © 2016-2022 Yomichan Authors and released under the <a href="https://github.com/FooSoft/yomichan/blob/master/LICENSE">GNU General Public License</a>.</p>'
        )

        self.add_label('<hr>')

        self.advanced_toggle = QCheckBox('Show advanced settings')
        self.advanced_toggle.setChecked(config.get('show_advanced', False))
        self.advanced_toggle.stateChanged.connect(self.on_toggle_advanced)

        self.lyt.addWidget(self.advanced_toggle)

    def on_toggle_advanced(self) -> None:
        state = self.advanced_toggle.isChecked()
        config.set('show_advanced', state)

        if hasattr(self, 'settings_window'):
            self.settings_window.toggle_advanced(state)


class WelcomeWidget(SettingsWidget):

    TITLE = 'Welcome!'
    SUBTITLE = 'This is the first time you are using the Migaku Anki add-on.'
    PIXMAP = 'migaku_side.png'

    def init_ui(self):
        welcome_lbl = QLabel('Migaku Anki provides all features you need to optimally learn languages with Anki and Migaku.<br><br>'
                             'This setup will give you a quick overview over the feature-set and explain how to use it.<br><br>'
                             'Let\'s go!<br><br>'
                             'You can always later see this guide and the settings by clicking <i>Migaku > Settings/Help</i>.')
        welcome_lbl.setWordWrap(True)
        self.lyt.addWidget(welcome_lbl)


class LanguageWidget(SettingsWidget):

    TITLE = 'Language Selection'

    def init_ui(self):
        lbl1 = QLabel(
            'Migaku allows you to learn all of the following languages. Please select all the ones you want to learn:')
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
                item.setFlags(item.flags() & ~(
                    Qt.ItemIsEnabled | Qt.ItemIsSelectable))
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
                      F'Make sure to install the extension for your browser to use this functionality. See <a href="{self.EXTENSION_URL}">here</a> for instructions.<br><br>'
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

        if not hotkey_handler.is_available():
            self.add_label(
                'For Migaku global hotkeys to work, you must allow Anki to monitor keyboard inputs.\n\n'
                'To do this, go to System Preferences > Security & Privacy > Privacy. Then for both "Accessibility" and "Input Monitoring" check the box for "Anki".\n\n'
                'These permissions are required to detect when the specified shortcuts are pressend and are required to copy the selected text'
                'Finally restart Anki.'
            )
            return

        self.add_label(
            'You can use the following hotkeys to interact with the browser extension while it is connected:'
        )

        self.hotkey_config = HotkeyConfigWidget(hotkey_handler)
        self.lyt.addWidget(self.hotkey_config)

        self.add_label(
            'To set new key combinations click the buttons on the right and press a new key combination. '
            'To disable a hotkey click the button again without pressing a new key combination.'
        )

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

        lbl2 = QLabel(
            'This[this,pron,ðɪs;ðɪs] is[be,aux,ɪz;ɪz] a[a,x,ʌ;eɪ] test[test,noun,test].')
        lbl2.setStyleSheet('background-color:#202020; color:#F8F8F8;')
        lbl2.setWordWrap(True)
        self.lyt.addWidget(lbl2)

        lbl3 = QLabel('<br>On your cards the information in the brackets is displayed in a popup over the word, as ruby text or changes the color of the word, depending on the language:')
        lbl3.setWordWrap(True)
        self.lyt.addWidget(lbl3)

        lbl4 = QLabel()
        lbl4.setPixmap(util.make_pixmap('syntax_displayed_small_example.png'))
        self.lyt.addWidget(lbl4)


class SyntaxAddRemoveWidget(SettingsWidget):

    TITLE = 'Add/Remove Language Syntax'

    def init_ui(self):

        lbl1 = QLabel(
            'To add or update syntax of your cards go to any editor window in Anki, select a field and press F2 or press this button (icons vary depending on language:')
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

        self.add_label(
            'By enabling the following option you can also edit empty fields on your cards:')

        show_empty_fields = QCheckBox('Show empty fields')
        show_empty_fields.setChecked(config.get(
            'inplace_editor_show_empty_fields', False))
        show_empty_fields.toggled.connect(lambda checked: config.set(
            'inplace_editor_show_empty_fields', checked)
        )
        self.lyt.addWidget(show_empty_fields)

    def save(self):
        from .inplace_editor import update_show_empty_fields
        update_show_empty_fields()


class CardTypeWidget(SettingsWidget):

    TITLE = 'Card Type Changing'

    def init_ui(self):

        self.add_label(
            'While reviewing a Migaku card you can change it\'s type by using these multiple choice buttons at the bottom of it\'s back side.'
        )

        img_lbl = QLabel()
        img_lbl.setPixmap(util.make_pixmap('card_types_example.png'))
        self.lyt.addWidget(img_lbl)

        self.add_label(
            '"Card Type" refers to what content you are questioned about on the front of your card.'
        )

        self.add_label('<br>')

        self.add_label(
            'If you wish to add a specific tag when changing the card type, you can enter it in the following field. This can be useful in combination with the "Card Promotion" feature.'
        )

        tag = QLineEdit()
        tag.setPlaceholderText('Tag to add when changing card type')
        tag.setText(config.get('card_type_tag', ''))
        tag.textChanged.connect(lambda text: config.set('card_type_tag', text))
        self.lyt.addWidget(tag)


class ReviewWidget(SettingsWidget):

    TITLE = 'Review Settings'

    def init_ui(self):

        self.add_label(
            'By default Anki allows grading cards as Again, Hard, Good and Easy.<br>'
            'The hard and easy buttons can lead to unnecessarily long grading decision times as well as permanently seeing cards too often/little.<br>'
            'Enabling Pass/Fail will remove those buttons.'
        )

        pass_fail = QCheckBox('Enable Pass/Fail (Recommended)')
        pass_fail.setChecked(config.get('reviewer_pass_fail', True))
        pass_fail.toggled.connect(lambda checked: config.set('reviewer_pass_fail', checked))
        self.lyt.addWidget(pass_fail)

        self.add_label('<hr>')

        self.add_label(
            'The negative effects of the ease factor can be prevented by fixing the ease factor (how difficult a card is considered) in place.<br>'
            'This option will prevent those effects if you want to use the Easy/Hard buttons and fixes negative effects caused in the past.'
        )

        pass_fail = QCheckBox('Maintain Ease Factor (Recommended)')
        pass_fail.setChecked(config.get('maintain_ease', True))
        pass_fail.toggled.connect(lambda checked: config.set('maintain_ease', checked))
        self.lyt.addWidget(pass_fail)

        self.add_label('If you review cards on mobile devices your ease factor will not be maintained. '
                       'To reset it press "Reset Ease Factor" from the Migaku menu. Note that this action will force a full sync.')

        self.add_label('<hr>')

        colored_buttons = QCheckBox('Colored Grading Buttons')
        colored_buttons.setChecked(config.get('reviewer_button_coloring', True))
        colored_buttons.toggled.connect(lambda checked: config.set('reviewer_button_coloring', checked))
        self.lyt.addWidget(colored_buttons)

    def save(self):
        config.write()


class SchedulingWidget(SettingsWidget):

    TITLE = 'Review Scheduling (Beta)'

    def init_ui(self):
        self.is_loading = False

        self.info_lbl = self.add_label('')
        self.add_label('<hr>')

        configs = aqt.mw.col.decks.all_config()
        config_names = [c['name'] for c in configs]

        top_lyt = QHBoxLayout()
        self.lyt.addLayout(top_lyt)

        top_lyt.addWidget(QLabel('Options Group:'))

        self.selector = QComboBox()
        self.selector.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.selector.addItems(config_names)
        top_lyt.addWidget(self.selector)

        self.add_label('<hr>')

        self.weekday_sliders = []

        self.enabled = QCheckBox('Enable Migaku Scheduling')
        self.enabled.stateChanged.connect(self.save)
        self.lyt.addWidget(self.enabled)

        balance_factor_lyt = QHBoxLayout()
        self.lyt.addLayout(balance_factor_lyt)

        self.move_factor_lbl = QLabel('Balance Strength')
        balance_factor_lyt.addWidget(self.move_factor_lbl)
        self.move_factor = QSlider(Qt.Horizontal)
        self.move_factor.setMinimum(0)
        self.move_factor.setMaximum(1000)
        self.move_factor.valueChanged.connect(self.save)
        balance_factor_lyt.addWidget(self.move_factor)

        self.week_box = QGroupBox('Weekly Schedule')
        self.lyt.addWidget(self.week_box)

        week_box_lyt = QGridLayout()
        self.week_box.setLayout(week_box_lyt)

        for i, weekday in enumerate(('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')):
            lbl = QLabel(weekday)
            week_box_lyt.addWidget(lbl, i, 0)
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(1000)
            slider.valueChanged.connect(self.save)
            week_box_lyt.addWidget(slider, i, 1)
            self.weekday_sliders.append(slider)

        self.add_label('<hr>')
        
        manage_vacations = QPushButton('Manage Vacations')
        manage_vacations.clicked.connect(self.manage_vacations)
        self.lyt.addWidget(manage_vacations)

        self.selector.currentIndexChanged.connect(self.load)
        self.load(self.selector.currentIndex())

    def toggle_advanced(self, state):
        if not state:
            self.info_lbl.setText(
                'Once you enable Migaku Scheduling, all cards within the selected options group will be balanced '
                'so that you roughly have the same amount of reviews each day.<br>'
                'The weekday sliders can be used to control the amount of cards you want to see in relation on a specific day (left: 0%, right: 100%).'
            )
        else:
            self.info_lbl.setText(
                'Once you enable Migaku Scheduling, all cards within the selected options group will be balanced '
                'with the selected balance strength (left: 0%, right: 20% derivation from optimal interval).<br>'
                'The weekday sliders can be used to control the amount of cards you want to see in relation on a specific day (left: 0%, right: 100%).'
            )
        self.move_factor_lbl.setVisible(state)
        self.move_factor.setVisible(state)

    def load(self, idx):
        if idx < 0:
            return

        self.is_loading = True

        c = aqt.mw.col.decks.all_config()[idx]

        self.enabled.setChecked(c.get('scheduling_enabled', False))
        self.move_factor.setValue(round(c.get('scheduling_move_factor', 0.1) * 5000))

        week_schedule = c.get('scheduling_week', [1.0] * 7)
        for slider, value in zip(self.weekday_sliders, week_schedule):
            slider.setValue(int(value * 1000))

        self.is_loading = False

    def save(self):
        if self.is_loading:
            return

        idx = self.selector.currentIndex()
        c = aqt.mw.col.decks.all_config()[idx]

        c['scheduling_enabled'] = self.enabled.isChecked()
        c['scheduling_move_factor'] = self.move_factor.value() / 5000
        c['scheduling_week'] = [slider.value() / 1000 for slider in self.weekday_sliders]

        aqt.mw.col.decks.update_config(c)

    def manage_vacations(self):
        BalanceSchedulerVacationWindow(self).exec_()


class RetirementWidget(SettingsWidget):

    TITLE = 'Card Retirement'

    def init_ui(self):
        self.is_loading = False

        configs = aqt.mw.col.decks.all_config()
        config_names = [c['name'] for c in configs]

        top_lyt = QHBoxLayout()
        self.lyt.addLayout(top_lyt)

        top_lyt.addWidget(QLabel('Options Group:'))

        self.selector = QComboBox()
        self.selector.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.selector.addItems(config_names)
        top_lyt.addWidget(self.selector)

        self.add_label('<hr>')

        sub_lyt = QGridLayout()
        self.lyt.addLayout(sub_lyt)

        sub_lyt.addWidget(QLabel('Retirement Interval:'), 0, 0)

        interval_lyt = QHBoxLayout()
        sub_lyt.addLayout(interval_lyt, 0, 1)
        self.interval = QSpinBox()
        self.interval.setFixedWidth(75)
        self.interval.setMinimum(0)
        self.interval.setMaximum(99999)
        interval_lyt.addWidget(self.interval)
        interval_lyt.addWidget(QLabel('days (0 = disabled)'))
        interval_lyt.addStretch()

        actions_box = QGroupBox('Actions')
        sub_lyt.addWidget(actions_box, 1, 0, 1, 2)
        actions_lyt = QGridLayout()
        actions_box.setLayout(actions_lyt)

        self.delete = QCheckBox('Delete')
        actions_lyt.addWidget(self.delete, 0, 0, 1, 2)

        self.suspend = QCheckBox('Suspend')
        actions_lyt.addWidget(self.suspend, 1, 0, 1, 2)

        actions_lyt.addWidget(QLabel('Tag'), 2, 0)
        self.tag = QLineEdit()
        self.tag.setPlaceholderText('None')
        actions_lyt.addWidget(self.tag, 2, 1)

        actions_lyt.addWidget(QLabel('Move'), 3, 0)
        self.deck = QComboBox()
        self.deck.addItem('<Do not move>')
        for deck in aqt.mw.col.decks.all_names_and_ids():
            self.deck.addItem(deck.name)
        actions_lyt.addWidget(self.deck, 3, 1)

        self.add_label(
            'After a card reaches the retirement interval the selected actions will be performed.')

        self.add_label('<hr>')

        notify = QCheckBox('Show notifications when cards are retired')
        notify.setChecked(config.get('retirement_notify', True))
        notify.toggled.connect(lambda checked: config.set('retirement_notify', checked))
        self.lyt.addWidget(notify)

        self.interval.valueChanged.connect(self.save)
        self.tag.textChanged.connect(self.save)
        self.deck.currentIndexChanged.connect(self.save)
        self.delete.stateChanged.connect(self.save)
        self.suspend.stateChanged.connect(self.save)

        self.selector.currentIndexChanged.connect(self.load)
        self.load(self.selector.currentIndex())

    def load(self, idx):
        if idx < 0:
            return

        self.is_loading = True

        c = aqt.mw.col.decks.all_config()[idx]
        self.interval.setValue(c.get('retirement_interval', 0))
        self.tag.setText(c.get('retirement_tag', ''))
        deck_index = 0
        r_deck = c.get('retirement_deck')
        if r_deck:
            deck_index = max(self.deck.findText(r_deck), 0)
        self.deck.setCurrentIndex(deck_index)
        self.delete.setChecked(c.get('retirement_delete', False))
        self.suspend.setChecked(c.get('retirement_suspend', False))
        self.is_loading = False

    def save(self):
        if self.is_loading:
            return

        idx = self.selector.currentIndex()
        c = aqt.mw.col.decks.all_config()[idx]

        c['retirement_interval'] = self.interval.value()
        c['retirement_tag'] = self.tag.text().strip()
        c['retirement_deck'] = self.deck.currentText(
        ) if self.deck.currentIndex() > 0 else None
        c['retirement_delete'] = self.delete.isChecked()
        c['retirement_suspend'] = self.suspend.isChecked()

        aqt.mw.col.decks.update_config(c)


class PromotionWidget(SettingsWidget):

    TITLE = 'Card Promotion'

    def init_ui(self):
        self.is_loading = False

        configs = aqt.mw.col.decks.all_config()
        config_names = [c['name'] for c in configs]

        top_lyt = QHBoxLayout()
        self.lyt.addLayout(top_lyt)

        top_lyt.addWidget(QLabel('Options Group:'))

        self.selector = QComboBox()
        self.selector.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.selector.addItems(config_names)
        top_lyt.addWidget(self.selector)

        self.add_label('<hr>')

        sub_lyt = QGridLayout()
        self.lyt.addLayout(sub_lyt)

        sub_lyt.addWidget(QLabel('Promotion Interval:'), 0, 0)

        interval_lyt = QHBoxLayout()
        sub_lyt.addLayout(interval_lyt, 0, 1)
        self.interval = QSpinBox()
        self.interval.setFixedWidth(75)
        self.interval.setMinimum(0)
        self.interval.setMaximum(99999)
        interval_lyt.addWidget(self.interval)
        interval_lyt.addWidget(QLabel('days (0 = disabled)'))
        interval_lyt.addStretch()

        actions_box = QGroupBox('Actions')
        sub_lyt.addWidget(actions_box, 1, 0, 1, 2)
        actions_lyt = QGridLayout()
        actions_box.setLayout(actions_lyt)

        actions_lyt.addWidget(QLabel('Set Type'), 2, 0)
        self.type = QComboBox()
        self.type.addItem('<Don\'t change>', '')
        self.type.addItem('Sentence', 's')
        self.type.addItem('Vocabulary', 'v')
        self.type.addItem('Audio Sentence', 'as')
        self.type.addItem('Audio Vocabulary', 'av')
        actions_lyt.addWidget(self.type, 2, 1)

        actions_lyt.addWidget(QLabel('Tag'), 3, 0)
        self.tag = QLineEdit()
        self.tag.setPlaceholderText('None')
        actions_lyt.addWidget(self.tag, 3, 1)

        actions_lyt.addWidget(QLabel('Move'), 4, 0)
        self.deck = QComboBox()
        self.deck.addItem('<Do not move>')
        for deck in aqt.mw.col.decks.all_names_and_ids():
            self.deck.addItem(deck.name)
        actions_lyt.addWidget(self.deck, 4, 1)

        tag_lyt = QGridLayout()
        self.lyt.addLayout(tag_lyt)

        tag_lyt.addWidget(QLabel('Required Tag'), 0, 0)
        self.required_tag = QLineEdit()
        self.required_tag.setPlaceholderText('None')
        tag_lyt.addWidget(self.required_tag, 0, 1)

        tag_lyt.addWidget(QLabel('Forbidden Tag'), 1, 0)
        self.forbidden_tag = QLineEdit()
        self.forbidden_tag.setPlaceholderText('None')
        tag_lyt.addWidget(self.forbidden_tag, 1, 1)

        self.add_label(
            'After a card reaches the promotion interval the selected actions will be performed ' \
            'if the required tag is present or empty and the forbidden tag is not present or empty.'
        )

        self.add_label('<hr>')

        notify = QCheckBox('Show notifications when cards are promoted')
        notify.setChecked(config.get('promotion_notify', True))
        notify.toggled.connect(lambda checked: config.set('promotion_notify', checked))
        self.lyt.addWidget(notify)

        self.interval.valueChanged.connect(self.save)
        self.type.currentIndexChanged.connect(self.save)
        self.tag.textChanged.connect(self.save)
        self.deck.currentIndexChanged.connect(self.save)
        self.required_tag.textChanged.connect(self.save)
        self.forbidden_tag.textChanged.connect(self.save)

        self.selector.currentIndexChanged.connect(self.load)
        self.load(self.selector.currentIndex())

    def load(self, idx):
        if idx < 0:
            return

        self.is_loading = True

        c = aqt.mw.col.decks.all_config()[idx]
        self.interval.setValue(c.get('promotion_interval', 0))
        self.type.setCurrentIndex(
            max(self.type.findData(c.get('promotion_type', '')), 0)
        )
        self.tag.setText(c.get('promotion_tag', ''))
        self.required_tag.setText(c.get('promotion_required_tag', ''))
        self.forbidden_tag.setText(c.get('promotion_forbidden_tag', ''))
        deck_index = 0
        p_deck = c.get('promotion_deck')
        if p_deck:
            deck_index = max(self.deck.findText(p_deck), 0)
        self.deck.setCurrentIndex(deck_index)
        self.is_loading = False

    def save(self):
        if self.is_loading:
            return

        idx = self.selector.currentIndex()
        c = aqt.mw.col.decks.all_config()[idx]

        c['promotion_interval'] = self.interval.value()
        c['promotion_type'] = self.type.currentData()
        c['promotion_tag'] = self.tag.text().strip()
        c['promotion_required_tag'] = self.required_tag.text().strip()
        c['promotion_forbidden_tag'] = self.forbidden_tag.text().strip()
        c['promotion_deck'] = self.deck.currentText(
        ) if self.deck.currentIndex() > 0 else None

        aqt.mw.col.decks.update_config(c)


class MediaFileWidget(SettingsWidget):

    TITLE = 'Media Files'

    def init_ui(self):
        self.add_label(
            'Audio files imported via the Browser Extension can be in many formats, some of which cannot be played by some versions of Anki or have a very large file size.<br>'
            'The option below will convert all media files exported from the Browser Extension to the MP3 format.'
        )

        convert_audio_mp3 = QCheckBox(
            'Convert audio files to MP3 (Recommended)')
        convert_audio_mp3.setChecked(config.get('convert_audio_mp3', True))
        convert_audio_mp3.toggled.connect(lambda checked: config.set('convert_audio_mp3', checked))
        self.lyt.addWidget(convert_audio_mp3)

        self.add_label(
            'Audio files imported via the Browser Extension may vary in volume which can be distracting during reviews.<br>'
            'The option below will normalize the volume of all imported audio files to approximately the same level.'
        )

        normalize_audio = QCheckBox('Normalize audio volume (Recommended)')
        normalize_audio.setChecked(config.get('normalize_audio', True))
        normalize_audio.toggled.connect(lambda checked: config.set('normalize_audio', checked))
        self.lyt.addWidget(normalize_audio)


class FieldSettingsWidget(SettingsWidget):

    TITLE = 'Field Settings'

    def init_ui(self):

        self.regex_del_buttons = []

        br_lyt = QHBoxLayout()
        self.lyt.addLayout(br_lyt)

        br_box = QCheckBox('Remove line breaks from sentences')
        br_box.setChecked(config.get('remove_sentence_linebreaks', False))
        br_box.toggled.connect(
            lambda checked: config.set('remove_sentence_linebreaks', checked)
        )
        br_lyt.addWidget(br_box)

        br_lyt.addStretch()

        br_lyt.addWidget(QLabel('(Replace with:'))

        br_txt = QLineEdit()
        br_txt.setText(config.get('sentence_linebreak_replacement', ''))
        br_txt.textChanged.connect(
            lambda text: config.set('sentence_linebreak_replacement', text)
        )
        br_txt.setMaximumWidth(50)
        br_lyt.addWidget(br_txt)

        br_lyt.addWidget(QLabel(')'))


        self.regex_widget = QWidget()
        self.lyt.addWidget(self.regex_widget)

        regex_lyt = QVBoxLayout()
        regex_lyt.setContentsMargins(0, 0, 0, 0)
        self.regex_widget.setLayout(regex_lyt)

        regex_lyt.addWidget(QLabel('<hr>'))

        regex_lyt.addWidget(self.make_label(
            'This option will substitute the field contents of the selected fields (comma separated) '
            'when creating cards using the specified regular expression and replacement string. '
            'Refer to <a href="https://docs.python.org/3/library/re.html#regular-expression-syntax">this</a> '
            'for the regular expression syntax.'
        ))

        self.regex_table = QTableWidget()
        regex_lyt.addWidget(self.regex_table)
        self.regex_table.setRowCount(0)
        self.regex_table.setColumnCount(4)
        self.regex_table.setHorizontalHeaderLabels(['Field Names', 'Regex', 'Replacement', ''])
        self.regex_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.regex_table.horizontalHeader().resizeSection(3, 25)
        self.regex_table.verticalHeader().setVisible(False)

        regex_btn_lyt = QHBoxLayout()
        regex_add = QPushButton('Add')
        regex_add.clicked.connect(lambda: self.add_regex())
        regex_btn_lyt.addWidget(regex_add)
        regex_btn_lyt.addStretch()
        regex_lyt.addLayout(regex_btn_lyt)

        self.add_label('<hr>')
        self.add_label('Note that these settings only apply to cards created from the browser extension.')

        for data in config.get('field_regex', []):
            self.add_regex(data)

    def toggle_advanced(self, state):
        self.regex_widget.setVisible(state)

    def save(self):
        datas = []
        for row in range(self.regex_table.rowCount()):
            data = {}
            field_names_raw = self.regex_table.cellWidget(row, 0).text()
            field_names = [x.strip() for x in field_names_raw.split(',')]
            data['field_names'] = field_names
            data['regex'] = self.regex_table.cellWidget(row, 1).text()
            data['replacement'] = self.regex_table.cellWidget(row, 2).text()
            datas.append(data)
        config.set('field_regex', datas)

    def add_regex(self, data=None):
        if data is None:
            data = {}

        row = self.regex_table.rowCount()
        self.regex_table.setRowCount(row + 1)

        fields_edit = QLineEdit()
        fields_edit.setText(', '.join(data.get('field_names', [])))
        self.regex_table.setCellWidget(row, 0, fields_edit)

        regex_edit = QLineEdit()
        regex_edit.setText(data.get('regex', ''))
        self.regex_table.setCellWidget(row, 1, regex_edit)

        replacement_edit = QLineEdit()
        replacement_edit.setText(data.get('replacement', ''))
        self.regex_table.setCellWidget(row, 2, replacement_edit)

        btn_del = QPushButton('✖')
        btn_del.clicked.connect(self.remove_regex)
        self.regex_del_buttons.append(btn_del)
        self.regex_table.setCellWidget(row, 3, btn_del)

    def remove_regex(self):
        del_btn = self.sender()
        row = self.regex_del_buttons.index(del_btn)
        if row < 0:
            return
        self.regex_table.removeRow(row)
        del self.regex_del_buttons[row]


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

        condensed_audio_messages_disabled = QCheckBox(
            'Disable progress and completion messages.'
        )
        condensed_audio_messages_disabled.setChecked(
            config.get('condensed_audio_messages_disabled', False)
        )
        condensed_audio_messages_disabled.toggled.connect(
            lambda checked: config.set('condensed_audio_messages_disabled', checked)
        )
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
    SchedulingWidget,
    CardTypeWidget,
    RetirementWidget,
    PromotionWidget,
    MediaFileWidget,
    FieldSettingsWidget,
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
