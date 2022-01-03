import aqt
from . import util
from . import global_hotkeys

def webview_search_dict(web_view):
    text = web_view.selectedText()
    aqt.mw.migaku_connection.search_dict(text)
    global_hotkeys.hotkey_handeler.focus_dictionary()

def webview_search_collection(web_view):
    text = web_view.selectedText()
    util.open_browser(text)

def on_webview_context_menu(webview, menu):
    dict_action = menu.addAction('Search')
    dict_action.triggered.connect(lambda: webview_search_dict(webview))
    collection_action = menu.addAction('Search Collection')
    collection_action.triggered.connect(lambda: webview_search_collection(webview))

aqt.gui_hooks.webview_will_show_context_menu.append(on_webview_context_menu)
aqt.gui_hooks.editor_will_show_context_menu.append(on_webview_context_menu)
