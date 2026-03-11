import json
import logging
import tornado.websocket

logger = logging.getLogger("migaku.connection.websocket")


class MigakuConnector(tornado.websocket.WebSocketHandler):
    DEBUG = True

    def open(self):
        self.connection = self.application.settings["connection"]
        logger.info(f"WebSocket connection opened from {self.request.remote_ip}")
        self.connection._set_connector(self)

    def on_close(self):
        logger.info("WebSocket connection closed")
        self.connection._unset_connector(self)

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        try:
            data = json.loads(message)
            if self.DEBUG:
                print("<<<", data)
            logger.debug(f"Received message: {data.get('msg', 'unknown')}")
            self.connection._recv_data(data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode WebSocket message: {e}")
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}", exc_info=True)

    def send_data(self, data):
        if self.DEBUG:
            print(">>>", data)
        self.write_message(json.dumps(data, ensure_ascii=False))
