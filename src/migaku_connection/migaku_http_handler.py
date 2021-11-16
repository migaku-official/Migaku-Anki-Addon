import tornado.web
from os.path import join, dirname
from anki.utils import isWin

from .. import config


def dummy_func(*args, **kwargs):
    pass


class MigakuHTTPHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def initialize(self):
        self.mw = self.application.settings.get('mw')
        self.addonDirectory = dirname(__file__)
        self.tempDirectory = join(self.addonDirectory, "temp")
        self.alert = dummy_func
        self.searchNote = dummy_func
        self.addCondensedAudioInProgressMessage = dummy_func
        self.removeCondensedAudioInProgressMessage = dummy_func
        suffix = ''
        if isWin:
            suffix = '.exe'
        self.ffmpeg = join(self.addonDirectory, 'user_files',
                           'ffmpeg', 'ffmpeg' + suffix)

    def checkVersion(self):
        version = int(self.get_body_argument("version", default=False))
        version_match = self.application.settings["PROTOCOL_VERSION"] == version
        print('VERSION MATCH:', version_match)

        return version_match

    def getConfig(self):
        return config
