import json

import aqt

from .migaku_http_handler import MigakuHTTPHandler
from .. import util


class CardSender(MigakuHTTPHandler):

    def post(self):
        data = json.loads(self.request.body)

        def make_url(file):
            if not file:
                return None
            return F'http://127.0.0.1:{aqt.mw.mediaServer.getPort()}/{file}'

        card_data = {
            'sentence':             data.get('sentence'),
            'sentence_translation': data.get('sentence_translation'),
            'unknown_words':        data.get('unknown_words'),
            'image_url':            make_url(data.get('image')),
            'sentence_audio_url':   make_url(data.get('audio')),
            'is_media_local':       True,   # Extension won't send back files
            'batch_count':          data.get('batch_count', 1),
            'batch_id':             data.get('batch_id', 0),
        }

        self.connection.send_cards(
            [card_data]
        )

        r_data = {
            'status': 'ok',
        }

        self.write(json.dumps(r_data))
