"""
Control logging for the app
"""

import datetime
import json
import logging
import os
import sys
import threading
from logging import LogRecord
from logging.handlers import RotatingFileHandler

from pymitter import EventEmitter

from ..appconfig import AppConfig
from .baseservice import BaseService


class EventstreamLogHandler(logging.Handler):
    """
    Logging handler to emit events to eventstream;
    to be displayed in console.log on browser frontend
    """

    def __init__(self, evtbus: EventEmitter):
        self._evtbus = evtbus

        self._initlogrecords_emitted = False
        self._initlogrecords = []

        self._evtbus.on("publishSSE/initial", self._emit_initlogs)

        logging.Handler.__init__(self)

    def _emit_initlogs(self):
        for logrecord in self._initlogrecords:
            self._evtbus.emit("publishSSE", sse_event="logrecord", sse_data=json.dumps(logrecord))
        # stop adding new records
        self._initlogrecords_emitted = True

        # self._initlogrecords = []

    def emit(self, record: LogRecord):
        logrecord = {
            "time": datetime.datetime.fromtimestamp(record.created).strftime("%d.%b.%y %H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }

        if not self._initlogrecords_emitted and len(self._initlogrecords) < 50:
            # after logrecords were first time emitted to client via eventstream,
            # not add any new records to array.
            # only log first 50 messgaes to not pollute the sse queue
            self._initlogrecords.append(logrecord)

        self._evtbus.emit("publishSSE", sse_event="logrecord", sse_data=json.dumps(logrecord))


class LoggingService(BaseService):
    """_summary_"""

    debug_level = logging.DEBUG

    def __init__(self, evtbus: EventEmitter, config: AppConfig):
        """Setup logger

        Args:
            evtbus (EventEmitter): _description_
        """
        super().__init__(evtbus=evtbus, config=config)

        ## formatter ##
        fmt = "%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)"
        log_formatter = logging.Formatter(fmt=fmt)

        ## basic configuration
        # latest basicConfig adds a streamHandler output to console if not automatically called
        # earlier by some .warn .info or other
        # force=False because otherwise the pytest console logger stream handler gets deleted
        logging.basicConfig(level=logging.DEBUG, format=fmt, force=False)
        logging.debug("loggingservice __init__ basicConfig set")
        logging.debug("loggingservice __init__ started")

        self.debug_level = config.common.DEBUG_LEVEL.value

        ## logger
        # default logger (root = None or "")
        # root logger also to be the template for all other loggers,
        # that are created in the app at a later time during run
        root_logger = logging.getLogger(name=None)

        # set level based on users config
        root_logger.setLevel(self.debug_level)

        ## handler
        # create rotatingFileHandler
        os.makedirs("log", exist_ok=True)
        self.rotatingfile_handler = RotatingFileHandler(
            filename="./log/photobooth.log", maxBytes=1024**2, backupCount=10, delay=True, encoding="utf-8"
        )
        self.rotatingfile_handler.setFormatter(log_formatter)

        # create rotatingFileHandler
        self.eventstream_handler = EventstreamLogHandler(evtbus=evtbus)
        self.eventstream_handler.setFormatter(log_formatter)

        ## wire logger and handler ##
        root_logger.addHandler(self.rotatingfile_handler)
        root_logger.addHandler(self.eventstream_handler)

        ## mute other loggers
        self.other_loggers()

        ## add the exepthooks
        sys.excepthook = self._handle_sys_exception
        threading.excepthook = self._handle_threading_exception
        # no solution to handle exceptions in sep processes yet...

        logging.debug("loggingservice __init__ finished")
        logging.debug(f"registered handlers: {logging.root.handlers}")

    def other_loggers(self):
        """mute some logger by rasing their log level"""

        for name in [
            "picamera2.picamera2",
            "sse_starlette.sse",
            "PIL.PngImagePlugin",
            "PIL.TiffImagePlugin",
        ]:
            # mute some other logger, by raising their debug level to INFO
            lgr = logging.getLogger(name=name)
            lgr.setLevel(logging.INFO)
            lgr.propagate = True

        for name in [
            "pywifi",
        ]:
            # mute some other logger, by raising their debug level to INFO
            lgr = logging.getLogger(name=name)
            lgr.setLevel(logging.WARNING)
            lgr.propagate = True

        os.environ["OPENCV_LOG_LEVEL"] = "ERROR"

    def uvicorn(self):
        """_summary_"""

        for name in [
            "uvicorn.error",
            "uvicorn.access",
            "uvicorn",
        ]:
            lgr = logging.getLogger(name=name)
            lgr.setLevel(self.debug_level)
            lgr.propagate = True
            lgr.handlers = [
                self.rotatingfile_handler,
                self.eventstream_handler,
            ]

    @staticmethod
    def _handle_sys_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logging.getLogger(name="__main__").exception(
            f"Uncaught exception: {exc_type} {exc_value}",
            exc_info=(exc_type, exc_value, exc_traceback),
        )

    @staticmethod
    def _handle_threading_exception(args: threading.ExceptHookArgs):
        # report the failure
        logging.getLogger(name="__main__").exception(
            f"Uncaught exception in thread {args.thread}: {args.exc_type} {args.exc_value}",
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )
