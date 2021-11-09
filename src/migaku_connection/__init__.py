import asyncio
import tornado

import aqt
from aqt.qt import *

from .migaku_connector import MigakuConnector

from .CardCreator import CardCreator
from .AudioCondenser import AudioCondenser
from .LearningStatusHandler import LearningStatusHandler
from .profile_data_provider import ProfileDataProvider


class MigakuServerThread(QThread):

    def __init__(self, server, parent=None):
        super().__init__(parent)

        self.server = server
        self.loop = None

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        self.server.listen(44432)
        tornado.ioloop.IOLoop.instance().start()



def with_connector_silent(func):
    def decorated(self, *args, **kwargs) :
        self.connector_lock.lock()

        if self.connector:
            func(self, *args, **kwargs)
        self.connector_lock.unlock()
        return True
    return decorated

def with_connector_msg_callback(func):
    def null_func(*args, **kwargs):
        pass

    def decorated(self, *args, **kwargs) :
        self.connector_lock.lock()
        
        msg_id = self._get_msg_id()
        self.msg_handlers[msg_id] = (kwargs.get('on_done', null_func), kwargs.get('on_error', null_func))

        if 'on_done' in kwargs:
            del kwargs['on_done']
        if 'on_error' in kwargs:
            del kwargs['on_error']

        kwargs['msg_id'] = msg_id

        if self.connector:
            func(self, *args, **kwargs)
        self.connector_lock.unlock()
        return True
    return decorated


class MigakuConnection(QObject):

    connected = pyqtSignal()
    disconnected = pyqtSignal()

    handlers = [
        ('/anki-connect', MigakuConnector),

        ('/condense', AudioCondenser),
        ('/learning-statuses', LearningStatusHandler),
        ('/create', CardCreator),
        ('/profile-data', ProfileDataProvider),
        ('/create', CardCreator),
    ]

    PROTOCOL_VERSION = 2

    def __init__(self, parent=None):
        super().__init__(parent)

        self.connector_lock = QMutex()
        self.connector = None
        
        self.msg_id = 0
        self.msg_handlers = {}

        self.server = tornado.web.Application(self.handlers, connection=self, PROTOCOL_VERSION=self.PROTOCOL_VERSION)
        self.thread = MigakuServerThread(self.server)
        self.thread.start()

    def _get_msg_id(self):
        self.msg_id += 1
        return self.msg_id

    def _set_connector(self, connector):
        self.connector_lock.lock()
        self.connector = connector
        self.connected.emit()
        self.connector_lock.unlock()

    def _unset_connector(self, connector):
        self.connector_lock.lock()
        if self.connector == connector:
            self.connector = None
            self.disconnected.emit()
        self.connector_lock.unlock()

    def _recv_data(self, data):
        if 'id' in data and 'msg' in data:
            msg_id = data['id']
            msg = data['msg']

            if msg_id in self.msg_handlers:
                on_done, on_error = self.msg_handlers[msg_id]
                del self.msg_handlers[msg_id]

                if msg == 'Migaku-Deliver-Syntax':
                    card_data = data.get('data', {}).get('cardArray')
                    aqt.mw.taskman.run_on_main(
                        lambda: on_done(card_data)
                    )

    def is_connected(self):
        self.connector_lock.lock()
        r = self.connector is not None
        self.connector_lock.unlock()
        return r

    @with_connector_silent
    def open_dict(self):
        self.connector.send_data({ 'msg': 'Migaku-Open' })

    @with_connector_silent
    def search_dict(self, term):
        self.connector.send_data({
            'msg': 'Migaku-Search',
            'data': { 'term': term } 
        })

    @with_connector_silent
    def set_sentence(self, sentence):
        self.connector.send_data({
            'msg': 'Migaku-Sentence',
            'data': { 'sentence': sentence }
        })

    @with_connector_silent
    def add_definition(self, definition):
        self.connector.send_data({
            'msg': 'Migaku-Definition',
            'data': { 'definition': definition }
        })

    @with_connector_msg_callback
    def request_syntax(self, data, lang_code, alternate_reading=False, msg_id=None):
        print('requesting...')
        self.connector.send_data({
            'msg': 'Migaku-Syntax',
            'id': msg_id,
            'data': {
                'languageCode': lang_code,
                'readingType': alternate_reading,
                'cardArray': data
            }
        })


aqt.mw.migaku_connection = MigakuConnection(aqt.mw)


class ConnectionStatusLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        aqt.mw.migaku_connection.connected.connect(self.set_connected)
        aqt.mw.migaku_connection.disconnected.connect(self.set_disconnected)
        self.set_status(aqt.mw.migaku_connection.is_connected())

    def set_status(self, status):
        if status:
            self.set_connected()
        else:
            self.set_disconnected()

    def set_connected(self):
        self.setText('● Connected')
        self.setStyleSheet('color: green')

    def set_disconnected(self):
        self.setText('● Not connected')
        self.setStyleSheet('color: red')
