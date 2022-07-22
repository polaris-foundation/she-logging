import logging as pylogging

pylogging.basicConfig(format="%(levelname)s:%(message)s")
pylogging.info("Basic config - info - does not display")
pylogging.warning("Basic config - warning")

from she_logging import logger, logging

logger.debug("she debug message")
logger.info("she info message")
logger.warning("she warning message")

pylogging.debug("pylogging debug message")
pylogging.info("pylogging info message")
pylogging.warning("pylogging warning message")
