from .migaku_http_handler import MigakuHTTPHandler


class MigakuHello(MigakuHTTPHandler):
    def get(self):
        self.finish("connect")
