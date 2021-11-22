import tornado.web

class MigakuHTTPHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def initialize(self):
        self.connection: MigakuConnection = self.application.settings['connection']

    def check_version(self):
        version = int(self.get_body_argument('version', default=False))
        version_match = self.connection.PROTOCOL_VERSION == version
        return version_match
