import asyncio
import logging
import os
import tornado
from pathlib import Path

import aqt
from aqt.qt import *

from ..util import DEFAULT_PORT

from .hello import MigakuHello
from .migaku_connector import MigakuConnector
from .card_creator import CardCreator
from .card_receiver import CardReceiver
from .audio_condenser import AudioCondenser
from .learning_status_handler import LearningStatusHandler
from .profile_data_provider import ProfileDataProvider
from .program_manager import ProgramManager
from .info_provider import InfoProvider
from .card_send import CardSender
from .search_handler import SearchHandler
from .srs_import import (
    SrsCheckHandler,
    SrsImportInfoHandler,
    SrsSampleCardHandler,
    SrsImportHandler,
)

from .. import config

# Set up logging for connection debugging
logger = logging.getLogger("migaku.connection")


class MigakuServerThread(QThread):
    def __init__(self, server, parent=None):
        super().__init__(parent)

        self.server = server
        self.loop = None
        self.actual_port = None  # Store the port that was successfully bound

    def run(self):
        logger.info("Web server thread starting...")
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            port = config.get("port", DEFAULT_PORT)
            actual_port = port if port else DEFAULT_PORT
            logger.info(f"Attempting to bind to port {actual_port}...")
        except Exception as e:
            logger.error(f"Failed to initialize event loop: {type(e).__name__}: {e}", exc_info=True)
            return

        try:
            self.server.listen(actual_port)
            self.actual_port = actual_port
            logger.info(f"Migaku server started successfully on port {actual_port}")
        except OSError as e:
            # Try to get more diagnostic info about what's using the port
            port_info = self._get_port_info(actual_port)

            error_msg = (
                f"Failed to start Migaku server on port {actual_port}.\n\n"
                f"Error: {str(e)}\n\n"
                f"{port_info}\n"
                f"Possible causes:\n"
                f"• Another Anki instance is already running\n"
                f"• A previous Anki session didn't close properly\n"
                f"• Another application is using port {actual_port}\n\n"
                f"Solutions:\n"
                f"• Close all Anki instances and restart\n"
                f"• Check what's using the port (see instructions below)\n"
                f"• Change the port in Tools → Add-ons → Migaku → Config\n"
                f"• Restart your computer if the problem persists\n\n"
                f"To check what's using the port:\n"
                f"Mac/Linux: Open Terminal and run:\n"
                f"  lsof -i :{actual_port}\n"
                f"Windows: Open Command Prompt and run:\n"
                f"  netstat -ano | findstr :{actual_port}"
            )
            # Schedule the error dialog on the main thread
            aqt.mw.taskman.run_on_main(
                lambda: aqt.utils.showWarning(
                    error_msg,
                    title="Migaku Connection Error",
                    parent=aqt.mw
                )
            )
            logger.error(f"Failed to start Migaku server on port {actual_port}: {e}")
            return

        logger.info("Starting Tornado IOLoop...")
        tornado.ioloop.IOLoop.instance().start()

    def _get_port_info(self, port):
        """Try to get information about what's using the port."""
        try:
            import subprocess
            import platform

            system = platform.system()

            if system == "Darwin" or system == "Linux":
                # Use lsof on Mac/Linux
                result = subprocess.run(
                    ["lsof", "-i", f":{port}"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        # Parse process info from lsof output
                        return f"Port {port} is currently used by:\n{lines[1][:80]}"

            elif system == "Windows":
                # Use netstat on Windows
                result = subprocess.run(
                    ["netstat", "-ano"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.stdout:
                    for line in result.stdout.split('\n'):
                        if f":{port}" in line and "LISTENING" in line:
                            return f"Port {port} is currently in use.\nDetails: {line.strip()[:80]}"

        except Exception as diag_error:
            logger.info(f"Could not get port diagnostic info: {diag_error}")

        return ""


def with_connector_silent(func):
    def decorated(self, *args, **kwargs):
        self.connector_lock.lock()

        if self.connector:
            func(self, *args, **kwargs)
        self.connector_lock.unlock()
        return True

    return decorated


def with_connector_msg_callback(func):
    def decorated(self, *args, **kwargs):
        self.connector_lock.lock()

        msg_id = self._get_msg_id()

        msg_handler = self.MessageHandler(
            on_done=kwargs.get("on_done"),
            on_error=kwargs.get("on_error"),
            on_timeout=kwargs.get("on_timeout"),
            callback_on_main_thread=kwargs.get("callback_on_main_thread", False),
        )

        self.msg_handlers[msg_id] = msg_handler

        timeout = kwargs.get("timeout", None)
        if timeout is not None:
            loop = self.thread.loop
            loop.call_soon_threadsafe(
                loop.call_later, timeout, self._msg_request_timed_out, msg_id
            )

        for strip_arg in [
            "on_done",
            "on_error",
            "on_timeout",
            "callback_on_main_thread",
            "timeout",
        ]:
            kwargs.pop(strip_arg, None)

        kwargs["msg_id"] = msg_id

        if self.connector:
            func(self, *args, **kwargs)
        else:
            msg_handler.error("Browser Extension is not connected.")

        self.connector_lock.unlock()

    return decorated


class MigakuConnection(QObject):
    class MessageHandler:
        def __init__(
            self,
            on_done=None,
            on_error=None,
            on_timeout=None,
            callback_on_main_thread=False,
        ):
            self.on_done = on_done
            self.on_error = on_error
            self.on_timeout = on_timeout
            self.callback_on_main_thread = callback_on_main_thread

        def _call(self, func, *args, **kwargs):
            if func:
                if self.callback_on_main_thread:
                    aqt.mw.taskman.run_on_main(lambda: func(*args, **kwargs))
                else:
                    func(*args, **kwargs)

        def done(self, *args, **kwargs):
            self._call(self.on_done, *args, **kwargs)

        def error(self, *args, **kwargs):
            self._call(self.on_error, *args, **kwargs)

        def timeout(self, *args, **kwargs):
            if self.on_timeout:
                self._call(self.on_timeout, *args, **kwargs)
            else:
                self.error(*args, **kwargs)

    connected = pyqtSignal()
    disconnected = pyqtSignal()

    handlers = [
        ("/anki-hello", MigakuHello),
        ("/anki-connect", MigakuConnector),
        ("/condense", AudioCondenser),
        ("/learning-statuses", LearningStatusHandler),
        ("/create", CardCreator),
        ("/receive", CardReceiver),
        ("/profile-data", ProfileDataProvider),
        ("/info", InfoProvider),
        ("/sendcard", CardSender),
        ("/search", SearchHandler),
        ("/srs-check", SrsCheckHandler),
        ("/srs-import-info", SrsImportInfoHandler),
        ("/srs-sample-card", SrsSampleCardHandler),
        ("/srs-import", SrsImportHandler),
    ]

    PROTOCOL_VERSION = 2

    def __init__(self, parent=None):
        super().__init__(parent)

        logger.info("Initializing Migaku connection...")

        try:
            logger.info("Setting up ffmpeg/ffprobe program managers...")
            self.ffmpeg = ProgramManager("ffmpeg", self)
            self.ffprobe = ProgramManager("ffprobe", self)
            os.environ["PATH"] += os.pathsep + str(Path(self.ffmpeg.program_path).parent)
            os.environ["PATH"] += os.pathsep + str(Path(self.ffprobe.program_path).parent)
            logger.info(f"ffmpeg path: {self.ffmpeg.program_path}")
            logger.info(f"ffprobe path: {self.ffprobe.program_path}")
        except Exception as e:
            logger.warning(f"Failed to set up ffmpeg/ffprobe: {type(e).__name__}: {e}", exc_info=True)

        self.connector_lock = QMutex()
        self.connector = None

        self.msg_id = 0
        self.msg_handlers = {}

        try:
            logger.info("Starting Tornado web server thread...")
            self.server = tornado.web.Application(self.handlers, connection=self)
            self.thread = MigakuServerThread(self.server)
            self.thread.start()
            logger.info("Web server thread started successfully")
        except Exception as e:
            logger.error(f"Failed to start web server: {type(e).__name__}: {e}", exc_info=True)
            raise

    def _get_msg_id(self):
        self.msg_id += 1
        return self.msg_id

    def _set_connector(self, connector):
        self.connector_lock.lock()
        self.connector = connector
        logger.info("Browser extension WebSocket connected")
        self.connected.emit()
        self.connector_lock.unlock()

    def _unset_connector(self, connector):
        self.connector_lock.lock()
        if self.connector == connector:
            self.connector = None
            logger.info("Browser extension WebSocket disconnected")
            for msg_handler in self.msg_handlers.values():
                msg_handler.error("Browser Extension disconnected.")
            self.disconnected.emit()
        self.connector_lock.unlock()

    def _msg_request_timed_out(self, msg_id):
        self.connector_lock.lock()
        if msg_id in self.msg_handlers:
            msg_handler = self.msg_handlers[msg_id]
            del self.msg_handlers[msg_id]
            msg_handler.timeout("Request timed out.")
        self.connector_lock.unlock()

    def _recv_data(self, data):
        if "id" in data and "msg" in data:
            msg_id = data["id"]
            msg = data["msg"]

            if msg_id in self.msg_handlers:
                msg_handler = self.msg_handlers[msg_id]
                del self.msg_handlers[msg_id]

                if msg == "Migaku-Deliver-Syntax":
                    card_data = data.get("data", {}).get("cardArray")
                    msg_handler.done(card_data)

                elif msg == "Migaku-Deliver-Definitions":
                    card_data = data.get("data", {})
                    msg_handler.done(card_data)

    def is_connected(self) -> bool:
        self.connector_lock.lock()
        r = self.connector is not None
        self.connector_lock.unlock()
        return r

    @with_connector_silent
    def open_dict(self) -> None:
        self.connector.send_data({"msg": "Migaku-Open"})

    @with_connector_silent
    def search_dict(self, term: str) -> None:
        self.connector.send_data({"msg": "Migaku-Search", "data": {"term": term}})

    @with_connector_silent
    def set_sentence(self, sentence: str) -> None:
        self.connector.send_data(
            {"msg": "Migaku-Sentence", "data": {"sentence": sentence}}
        )

    @with_connector_silent
    def add_definition(self, definition: str) -> None:
        self.connector.send_data(
            {"msg": "Migaku-Definition", "data": {"definition": definition}}
        )

    @with_connector_silent
    def play_audio(self, lang_code: str, word: str) -> None:
        idx = lang_code.find("_")
        if idx >= 0:
            lang_code = lang_code[:idx]

        self.connector.send_data(
            {
                "msg": "Migaku-Play-Audio",
                "data": {
                    "languageCode": lang_code,
                    "text": word,
                },
                "id": -1,
            }
        )

    @with_connector_silent
    def send_cards(self, cards_data) -> None:
        self.connector.send_data({"msg": "Migaku-Send-Cards", "data": cards_data})

    @with_connector_msg_callback
    def request_syntax(self, data, lang_code, alternate_reading=False, msg_id=None):
        idx = lang_code.find("_")
        if idx >= 0:
            lang_code = lang_code[:idx]

        self.connector.send_data(
            {
                "msg": "Migaku-Syntax",
                "id": msg_id,
                "data": {
                    "languageCode": lang_code,
                    "readingType": alternate_reading,
                    "cardArray": data,
                },
            }
        )

    @with_connector_msg_callback
    def request_definitions(
        self, cards, lang_code, alternate_reading=False, msg_id=None
    ):
        idx = lang_code.find("_")
        if idx >= 0:
            lang_code = lang_code[:idx]

        self.connector.send_data(
            {
                "msg": "Migaku-Request-Definitions",
                "data": {
                    "languageCode": lang_code,
                    "readingType": alternate_reading,
                    "cardIdWords": cards,
                    "syntax": True,
                },
                "id": msg_id,
            }
        )


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
        self.setText("● Browser Extension Connected")
        self.setStyleSheet("color: green")

    def set_disconnected(self):
        self.setText("● Browser Extension Not Connected")
        self.setStyleSheet("color: red")
