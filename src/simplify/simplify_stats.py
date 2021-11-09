from anki.hooks import wrap
from aqt import gui_hooks
from aqt.stats import NewDeckStats
from aqt.webview import AnkiWebPage, AnkiWebView, WebContent
from aqt.qt import *


def onStatsShow(self: NewDeckStats, *args):
    """
    This code is ran AFTER the NewDeckStats.refresh()
    It hides the graph-ease portion of the stats window.
    """


    webView: AnkiWebView = self.form.web

    code = """
    var ease_elem = document.querySelector('#main > div > div:nth-child(9)');
    if (ease_elem) {
        ease_elem.style.display = 'none';
    }
    """

    webView.eval(code)
    print("ran js on stats window")


NewDeckStats.refresh = wrap(NewDeckStats.refresh, onStatsShow)