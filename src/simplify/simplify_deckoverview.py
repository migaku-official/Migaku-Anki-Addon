"""

In the deck overview webview, remove the Custom Study button

def on_webview_will_set_content(web_content: WebContent, context):
    addon_package = mw.addonManager.addonFromModule(__name__)
    web_content.css.append(
        f"/_addons/{addon_package}/web/my-addon.css")
    web_content.js.append(
        f"/_addons/{addon_package}/web/my-addon.js")


in WebView.stdHtml it fires the gui_hooks.webview_will_set_content hook.

gui_hooks.webview_will_set_content(web_content, context)
context is the instance that was passed to stdHtml().
It can be inspected to check which screen this hook is firing in.

doc='''Used to modify web content before it is rendered.

        Web_content contains the HTML, JS, and CSS the web view will be
        populated with.

        Context is the instance that was passed to stdHtml().
        It can be inspected to check which screen this hook is firing
        in, and to get a reference to the screen. For example, if your
        code wishes to function only in the review screen, you could do:

            def on_webview_will_set_content(web_content: WebContent, context):
                
                if not isinstance(context, aqt.reviewer.Reviewer):
                    # not reviewer, do not modify content
                    return
                
                # reviewer, perform changes to content
                
                context: aqt.reviewer.Reviewer
                
                addon_package = mw.addonManager.addonFromModule(__name__)
                
                web_content.css.append(
                    f"/_addons/{addon_package}/web/my-addon.css")
                web_content.js.append(
                    f"/_addons/{addon_package}/web/my-addon.js")

                web_content.head += "<script>console.log('my-addon')</script>"
                web_content.body += "<div id='my-addon'></div>"
        '''

"""
from os.path import join, dirname

from anki.lang import _
from anki.hooks import wrap
from aqt import gui_hooks, mw
from aqt.webview import WebContent, AnkiWebView
from aqt.overview import Overview, OverviewBottomBar
from aqt.toolbar import BottomBar, BottomToolbar

from .configWrapper import readConfig

mw.addonManager.setWebExports(__name__, r"web/.*(css|js)")
addon_folder = join(
    mw.addonManager.addonsFolder(), dirname(__file__)
)

### Change css/js based on language
# disablejs = '''
# function onload() {
#     let buttons = document.getElementsByTagName("button");
#     for (button in buttons) {
#         if (button.innerText == "%s") {
#             button.disabled = true;
#             button.style.display = "none";
#             break
#         }
#     }
# }

# window.addEventListener("DOMContentLoaded", onload)

# ''' % _("Custom Study")

# with open(join(addon_folder, "web", "disableDeckOverview.js"), "w") as JsFile:
#     JsFile.write(disablejs)


def on_webview_will_set_content(web_content: WebContent, context):

    # if (not isinstance(context, BottomToolbar)) and (not isinstance(context, OverviewBottomBar)):
    #     # not overview bottombar webview so ignore.
    #     print("IGNORE")
    #     return

    if not (isinstance(context, BottomToolbar) or isinstance(context, OverviewBottomBar)):
        # not overview bottombar webview so ignore.
        return

    print(f"\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\non_webview_will_set_content HOOK CALLED. context={context}\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    customStudy: bool = readConfig()["simplifications"]["deckOverview"]["customStudy"]
    print(f"customStudy = {customStudy}")

    ### Why does this not work? None of the js works actually.
#     if (not customStudy):
#         web_content.body += f"""
# <script>
# {disablejs}
# </script>
#             """
    addon_package = mw.addonManager.addonFromModule(__name__)
    print("mw.migakuGuiSimplification and (not customStudy) is ", mw.migakuGuiSimplification and (not customStudy))
    if mw.migakuGuiSimplification and (not customStudy):
        # web_content.js.append(
        #     f"/_addons/{addon_package}/web/disableDeckOverview.js"
        # )
        web_content.css.append(
            f"/_addons/{addon_package}/web/deckoverview.css"
        )
        print(f"disable web_content js appended. web_content.js={web_content.js}")
    else:
        pass


gui_hooks.webview_will_set_content.append(on_webview_will_set_content)

###########################################################################
### For printing out html of webviewpages (but only when you nagigate away)
###########################################################################
# def wrapwebview(self: AnkiWebView, *args):
#     self._page.toHtml(lambda t: print(
#         """
#         ###########################################
#         ### Webview HTML Dump
#         ###########################################

#         """,t,
#         """
#         ###########################################
#         ###########################################
#         """
#         ))

# AnkiWebView.setHtml = wrap(AnkiWebView.setHtml, wrapwebview)