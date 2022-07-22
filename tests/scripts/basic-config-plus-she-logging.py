import logging as pylogging

pylogging.basicConfig(format="%(levelname)s:%(message)s", level=pylogging.DEBUG)
pylogging.debug("Basic config")

from she_logging import logger, logging

logging.init_logging()
logger.debug("she debug message")
logger.info("she info message")
logger.warning("she warning message")

pylogging.debug("pylogging debug message")
pylogging.info("pylogging info message")
pylogging.warning("pylogging warning message")
