# -*- coding: utf-8 -*-
"""Shared logging interface

This module provides a single consistent interface for logging.
It works inside a flask application but does not require flask.


The logger defaults to INFO level, which can be overridden using the
LOG_LEVEL OS environment entry.

To use, just import logger from simple_logger and log as usual:

    logger.debug('Something happened!')

The class uses sensible defaults:

- logger name: simple_logger
- log level: INFO
- log format: '[%(asctime)s] %(levelname)s in %(module)s:%(lineno)s: %(message)s'
- output: sys.stdout

Log level may be overriden (environment variable LOG_LEVEL, default INFO)
Log format may be overridden (environment variable LOG_FORMAT, default JSON, other options COLOURED, PLAIN)

"""
import datetime
import json
import logging.config
import sys
from logging import Logger, root, warning
from pathlib import Path
from typing import Any, Dict, Optional, Union

import json_log_formatter
import yaml
from environs import Env

from .request_id import current_request_id

try:
    import rich

    HAVE_RICH: bool = bool(rich)
except:
    HAVE_RICH = False

try:
    from flask import request
except ImportError:
    request = None  # type: ignore


env = Env()
LOG_LEVEL = env.str("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = env.str("LOG_FORMAT", "JSON").upper()
LOG_LOCALS = env.bool("LOG_LOCALS", True)

HANDLERS = {
    "JSON": "json",
    "COLOUR": "colour" if HAVE_RICH else "plaintext",
    "COLOR": "colour" if HAVE_RICH else "plaintext",
    "PLAIN": "plaintext",
}
LOG_HANDLER = HANDLERS.get(LOG_FORMAT, "json")

# According to the Python docs getLogRecordFactory and setLogRecordFactory get and set callables that create a
# LogRecord, however in practice they return the LogRecord class and using a function instead of a class fails with
# coloredlogs.
ORIGINAL_LOG_RECORD_CLASS: Any = logging.getLogRecordFactory()

_STACKLEVEL: Dict = {"stacklevel": 3} if sys.version_info >= (3, 7) else {}
_initialised: bool = False


@logging.setLogRecordFactory
class RecordFactory(ORIGINAL_LOG_RECORD_CLASS):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.requestID = current_request_id()


class SheLogRecord(logging.LogRecord):
    requestID: str


class SafeJsonEncoder(json.JSONEncoder):
    def default(self, obj: object) -> Any:
        try:
            if isinstance(obj, (datetime.datetime, datetime.date)):
                return obj.isoformat()

            return json.JSONEncoder.default(self, obj)
        except Exception as e:
            return f"{e} {repr(obj)}"


class SafeJson:
    def dumps(self, data: object) -> str:
        return json.dumps(data, cls=SafeJsonEncoder)


class CustomisedJSONFormatter(json_log_formatter.JSONFormatter):
    json_lib = SafeJson()

    def json_record(self, message: str, extra: dict, record: SheLogRecord) -> dict:
        super().json_record(message, extra, record)

        extra.update(
            {
                "timestamp": extra.pop("time"),
                "message": message,
                "severity": record.levelname,
                "pathname": record.pathname,
                "lineno": record.lineno,
                "requestID": record.requestID,
            }
        )

        if request:
            header_keys = ["X-Client", "X-Version"]
            for key in header_keys:
                if key in request.headers:
                    extra[key] = request.headers[key]

        return extra


SIMPLE_FORMAT = (
    "[%(asctime)s] %(levelname)s [%(requestID)s] in %(module)s:%(lineno)s: %(message)s"
)
RICH_FORMAT = "[%(requestID)s] %(message)s"

RICH_HANDLER = {
    "class": "rich.logging.RichHandler",
    "formatter": "rich",
    "rich_tracebacks": True,
    "tracebacks_show_locals": LOG_LOCALS,
    "tracebacks_word_wrap": False,
}
PLAINTEXT_HANDLER = {
    "class": "logging.StreamHandler",
    "stream": "ext://sys.stdout",
    "formatter": "simple",
}
if not HAVE_RICH:
    RICH_HANDLER = PLAINTEXT_HANDLER

SHE_LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": CustomisedJSONFormatter},
        "simple": {"format": SIMPLE_FORMAT},
        "rich": {"format": RICH_FORMAT},
    },
    "handlers": {
        "json": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "json",
        },
        "plaintext": PLAINTEXT_HANDLER,
        "colour": RICH_HANDLER,
    },
    "root": {"level": LOG_LEVEL, "handlers": [LOG_HANDLER]},
    "loggers": {
        "she-logging": {"level": "WARNING"},
        "connexion": {"level": env.str("LOG_LEVEL_CONNEXION", "INFO")},
        "neobolt": {"level": env.str("LOG_LEVEL_NEOBOLT", "INFO")},
        "neo4j": {"level": env.str("LOG_LEVEL_NEO4J", "WARNING")},
        "openapi_spec_validator": {
            "level": env.str("LOG_LEVEL_OPENAPI_SPEC_VALIDATOR", "INFO")
        },
        "pika": {"level": env.str("LOG_LEVEL_PIKA", "INFO")},
        "gunicorn": {"level": env.str("LOG_LEVEL_GUNICORN", "INFO")},
        "uvicorn": {"level": env.str("LOG_LEVEL_UVICORN", "INFO")},
        "uvicorn.access": {
            "level": env.str("LOG_LEVEL_UVICORN_ACCESS", "INFO"),
            "propagate": False,
        },
        "uvicorn.error": {"level": env.str("LOG_LEVEL_UVICORN_ERROR", "INFO")},
    },
}


class LogProxy:
    _logger: Optional[Logger] = None
    _name: str

    def __init__(self, name: str = "root") -> None:
        self._name = name

    def __getattr__(self, item: str) -> Any:
        if self._logger is None:
            self._logger = getLogger(self._name)
        attr = getattr(self._logger, item)
        setattr(self, item, attr)
        return attr


logger = LogProxy("root")


def init_logging(config: Union[str, Path, Dict, None] = None) -> bool:
    global _initialised

    if "she-logging" in logging.Logger.manager.loggerDict:  # type:ignore
        # she-logging configuration has already been applied, don't overwrite it
        _initialised = True
        return False

    if _initialised:
        warning(
            "she_logging.init_logging was called but logging is already initialised - skipped",
            **_STACKLEVEL,
        )
        return False
    elif len(root.handlers):
        if root.handlers[0].__class__.__name__ == "LogCaptureHandler":
            # Running under pytest, don't try to reconfigure the capture log.
            _initialised = True
            return False
        warning("she-logging overwriting existing logging configuration", **_STACKLEVEL)

    _initialised = True
    log_config: Dict = SHE_LOGGING_CONFIG

    if isinstance(config, Dict):
        log_config = config
    elif isinstance(config, (str, Path)):
        with Path(config).open() as file:
            log_config = yaml.safe_load(file)

    logging.config.dictConfig(log_config)

    return True


def getLogger(name: str = "root") -> Logger:
    if not _initialised:
        init_logging()
    return logging.getLogger(name)
