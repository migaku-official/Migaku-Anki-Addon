import tornado.websocket
import json

import aqt


class MigakuConnector(tornado.websocket.WebSocketHandler):

    def open(self):
        self.connection = self.application.settings['connection']
        self.connection._set_connector(self)

    def on_close(self):
        self.connection._unset_connector(self)

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        data = json.loads(message)
        print('<<<', data)
        self.connection._recv_data(data)

    def send_data(self, data):
        print('>>>', data)
        self.write_message(json.dumps(data, ensure_ascii=False))
