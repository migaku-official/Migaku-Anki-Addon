import aqt
from aqt.qt import *
from aqt.browser import Browser

from .add_remove_syntax_dialog import AddRemoveSyntaxDialog
from .card_type_change_dialog import CardTypeChangeDialog
from .definition_add_dialog import DefinitionAddDialog

def setup_browser_menu(browser: Browser):

    add_syntax_action = QAction('Add Language Syntax To Cards', browser)
    add_syntax_action.triggered.connect(
        lambda: AddRemoveSyntaxDialog.show_modal(browser.selectedNotes(), False, browser)
    )

    remove_syntax_action = QAction('Remove Language Syntax From Cards', browser)
    remove_syntax_action.triggered.connect(
        lambda: AddRemoveSyntaxDialog.show_modal(browser.selectedNotes(), True, browser)
    )

    card_type_action = QAction('Change Card Type (Sentence/Vocabulary/Audio)', browser)
    card_type_action.triggered.connect(
        lambda: CardTypeChangeDialog.show_modal(browser.selectedNotes(), browser)
    )


    definitions_action = QAction('Generate Definitions', browser)
    definitions_action.triggered.connect(
        lambda: DefinitionAddDialog.show_modal(browser.selectedNotes(), browser)
    )

    # Menu bar
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(add_syntax_action)
    browser.form.menuEdit.addAction(remove_syntax_action)
    browser.form.menuEdit.addAction(card_type_action)
    browser.form.menuEdit.addAction(definitions_action)

    # Context menu
    browser.form.menu_Notes.insertAction(browser.form.actionManage_Note_Types, add_syntax_action)
    browser.form.menu_Notes.insertAction(browser.form.actionManage_Note_Types, remove_syntax_action)
    browser.form.menu_Notes.insertAction(browser.form.actionManage_Note_Types, card_type_action)
    browser.form.menu_Notes.insertAction(browser.form.actionManage_Note_Types, definitions_action)
    browser.form.menu_Notes.insertSeparator(browser.form.actionManage_Note_Types)


aqt.gui_hooks.browser_menus_did_init.append(setup_browser_menu)
