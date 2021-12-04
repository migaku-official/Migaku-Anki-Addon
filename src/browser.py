import aqt
from aqt.qt import *
from aqt.browser import Browser

from .add_remove_syntax_dialog import AddRemoveSyntaxDialog
from .card_type_change_dialog import CardTypeChangeDialog
from .definition_add_dialog import DefinitionAddDialog

def setup_browser_menu(browser: Browser):
    browser.form.menuEdit.addSeparator()

    add_syntax_action = QAction('Add Language Syntax To Cards', browser)
    add_syntax_action.triggered.connect(
        lambda: AddRemoveSyntaxDialog.show_modal(browser.selectedNotes(), False, browser)
    )
    browser.form.menuEdit.addAction(add_syntax_action)

    remove_syntax_action = QAction('Remove Language Syntax From Cards', browser)
    remove_syntax_action.triggered.connect(
        lambda: AddRemoveSyntaxDialog.show_modal(browser.selectedNotes(), True, browser)
    )
    browser.form.menuEdit.addAction(remove_syntax_action)

    card_type_action = QAction('Change Card Type (Sentence/Vocabulary/Audio)', browser)
    card_type_action.triggered.connect(
        lambda: CardTypeChangeDialog.show_modal(browser.selectedNotes(), browser)
    )
    browser.form.menuEdit.addAction(card_type_action)

    definitions_action = QAction('Generate Definitions', browser)
    definitions_action.triggered.connect(
        lambda: DefinitionAddDialog.show_modal(browser.selectedNotes(), browser)
    )
    browser.form.menuEdit.addAction(definitions_action)



aqt.gui_hooks.browser_menus_did_init.append(setup_browser_menu)
