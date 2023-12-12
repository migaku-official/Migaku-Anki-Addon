import json

from ..editor.current_editor import get_add_cards_info
from ..migaku_connection import ConnectionListener
from ..util import addon_path


global_toolbar = None


def activate_migaku_toolbar(toolbar):
    info = get_add_cards_info()
    toolbar.web.eval(f"MigakuToolbar.activate({json.dumps(info)})")


def refresh_migaku_toolbar():
    info = get_add_cards_info()
    print("hey", global_toolbar)
    global_toolbar.web.eval(f"MigakuToolbar.refresh({json.dumps(info)})")


def deactivate_migaku_toolbar(toolbar):
    toolbar.web.eval("MigakuToolbar.deactivate()")


def inject_migaku_toolbar(html: str, toolbar):
    global global_toolbar
    global_toolbar = toolbar

    ConnectionListener(
        lambda: activate_migaku_toolbar(toolbar),
        lambda: deactivate_migaku_toolbar(toolbar),
    )

    with open(addon_path("toolbar/toolbar.html"), "r", encoding="utf-8") as file:
        html.append(file.read())
