from typing import Any

from gunicorn import glogging

from . import logging


class Logger(glogging.Logger):
    """Use SHE logging for Gunicorn log messages."""

    def setup(self, cfg: Any) -> None:
        super().setup(cfg)
        logging.init_logging()
