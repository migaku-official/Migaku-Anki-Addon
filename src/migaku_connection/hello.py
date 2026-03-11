from .migaku_http_handler import MigakuHTTPHandler


class MigakuHello(MigakuHTTPHandler):
    def get(self):
        # Return the actual port being used (if available)
        connection = self.application.settings.get("connection")
        response = {"status": "connect"}
        
        if connection and hasattr(connection, "thread") and hasattr(connection.thread, "actual_port"):
            response["port"] = connection.thread.actual_port
        
        self.finish(response)
