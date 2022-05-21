import json

import aqt

from .migaku_http_handler import MigakuHTTPHandler
from .. import util


class SearchHandler(MigakuHTTPHandler):

    def post(self):

        data = json.loads(self.request.body)

        terms = data.get('terms', [])

        if terms:
            for term in terms:
                self.connection.search_dict(term)
        else:
            self.connection.open_dict()

        r_data = {
            'status': 'ok',
        }

        self.write(json.dumps(r_data))
