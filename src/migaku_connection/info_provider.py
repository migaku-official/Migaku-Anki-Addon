import json

from .migaku_http_handler import MigakuHTTPHandler
from .. import util


class InfoProvider(MigakuHTTPHandler):

    def get(self):
        r = {
            'protocol_version': self.connection.PROTOCOL_VERSION,
            'col_media_path':   util.col_media_path(),
            'tmp_path':         util.tmp_path(),
        }

        self.write(json.dumps(r))
