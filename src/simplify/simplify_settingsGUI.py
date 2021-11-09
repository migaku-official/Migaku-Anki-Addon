from os.path import dirname, join
import json

from anki.lang import _
from anki.utils import noBundledLibs
from aqt.utils import openLink

from aqt.qt import *
from aqt import mw
from aqt import gui_hooks

from .configWrapper import Simplifications, readConfig, configKey2ConfigInfoMap, writeConfig
from .miutils import miAsk, miAsk_no_exec_, miInfo
from .simplify_main_menubar import runSimplification

addon_path = dirname(__file__)

def sortDictByType(d: dict):
    ### sort the tree so that items where value is str are first
	### key: if val is string return True (1), and sort in reverse order
    ### returns the sorted keys for the dict.
    return sorted(
        d, key=lambda key: isinstance(d[key], str), reverse=True
    )

def openSimplifySetttings():
    SimplifySettingsGUI(mw).exec_()

### When someone clicks the config button in anki it opens our settings.
mw.addonManager.setConfigAction(__name__, openSimplifySetttings)

class SimplifySettingsGUI(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent=parent)
        self.setBaseSize(
            QSize(800, 1600)
        )
        self.setWindowIcon(
            QIcon(
                join(addon_path, "img", "migaku_200.png")
            )
        )
        self.setWindowTitle("Migaku Simplification Settings")
        self.setupUI()
        self.populateTree()


    def setupUI(self):
        self.outerLayout = QVBoxLayout(self)
        self.setLayout(self.outerLayout)

        ### Add a 2nd column in treewidget for checkboxes.
        self.treeWidget = QTreeWidget(self)
        self.treeWidget.setColumnCount(2)
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.header().setStretchLastSection(False)
        self.treeWidget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        ### We will keep all the checkableItems in here,
        ### and then use it when saving config.
        self.key2treeitemMap = dict()
        self.outerLayout.addWidget(self.treeWidget)

        #################
        ### Button Box
        #################
        self.buttonBox = QDialogButtonBox()
        self.outerLayout.addWidget(self.buttonBox) 
        self.rejectButton = self.buttonBox.addButton("Close", QDialogButtonBox.RejectRole)
        self.acceptButton = self.buttonBox.addButton("Apply", QDialogButtonBox.AcceptRole)
        self.helpButton = self.buttonBox.addButton("Help", QDialogButtonBox.HelpRole)
        self.restoreDefaultsButton = self.buttonBox.addButton("Restore Defaults", QDialogButtonBox.ResetRole)
        self.buttonBox.clicked.connect(self.onClicked)

    def onClicked(self, button: QAbstractButton):
        if button == self.rejectButton:
            self.reject()
        elif button == self.acceptButton:
            self.onApply()
        elif button == self.helpButton:
            self.onHelp()
        elif button == self.restoreDefaultsButton:
            self.onRestoreDefaults()

    def onRestoreDefaults(self):
        ### open config.json: this contains the default config.
        ### Changes to the config are written to meta.json
        
        ### Show warning
        msgBox = miAsk_no_exec_(
            "<h3 style=\" align: center \">"+"Do you want to restore defaults?"+"</h3>"
            )
        msgBox.setInformativeText("""
        <p style="align: justify">
            <b>This will reset all changes that you have made.</b>
        </p>""")
        if msgBox.exec_() == QMessageBox.Yes:
            configPath = join(addon_path, "config.json")
            with open(configPath, "r") as JsonFile:
                defaultConfig = json.load(JsonFile)

            writeConfig(defaultConfig)
        
        ### refresh widgetTree
        self.treeWidget.clear()
        self.populateTree()
        
    def onHelp(self):
        openLink("https://www.migaku.io/coming-soon")

    def onApply(self):
        """
        Called when the Apply button is pressed.

        TODO: save the new config etc.
        """

        newConfig = readConfig()
        self.iterModifyConfig(newConfig["simplifications"])
        from pprint import pprint
        print("Final modified config file is")
        pprint(newConfig)

        ### Save config
        writeConfig(newConfig)

        runSimplification()
        #miInfo("You may need to restart Anki for these changes to take effect.")

        super().close()

    def iterModifyConfig(self, config: Union[Simplifications, dict]):
        """
        More recursion because of the nested dictionaries / json

        for key val in config (dict),
        If the val is a bool, update that bool by getting the associated
            treewidget item from self.key2treeitemMap[key] and set True if
            item is checked, False if not.
        If the val is another dict, recurse to keep going.
        """
        for key,val in config.items():
            if isinstance(val, bool):
                item: QTreeWidgetItem = self.key2treeitemMap[key]
                config[key] = True if item.checkState(1) == 2 else False
            elif isinstance(val, dict):
                self.iterModifyConfig(val)
            
    
    def populateTree(self):
        simplifications = readConfig()["simplifications"]
        self._populate(simplifications, self.treeWidget) # type: ignore (it doesn't think Simplifications is a dict)

    def _populate(self, dictroot: dict, treeroot: Union[QTreeWidget, QTreeWidgetItem]):
        
        for key in sortDictByType(dictroot):
            val = dictroot[key]

            configInfo = configKey2ConfigInfoMap[key]

            
            if isinstance(val, dict):
                #then key is a menu
                #add the menu;
                # recurse on children (ie val [which is a dict])
                item = QTreeWidgetItem(treeroot,[configInfo.displayString])
                self._populate(val, item)
            elif isinstance(val, bool):
                # Then key is an item
                # Already added the item;
                ### add the item, and add it to self.treeWidget by key name
                ### eg actionReposition item can be accessed as self.treeWidget.actionReposition
                item = QTreeWidgetItem(treeroot, [configInfo.displayString])
                ### TODO: adjust other properties based on ConfigInfo.
                item.setToolTip(1, configInfo.tooltipMsg())
                #QtCore.Qt.Checked = 2
                #QtCore.Qt.UnChecked = 0
                #QtCore.Qt.isUserCheckable = 16
                item.setCheckState(1, 2 if val else 0) #type:ignore
                
                self.key2treeitemMap[key] = item
            else:
                raise Exception("val ({val}) wasn't dict or bool. Has the config been messed with?")