import logging
from typing import Optional


logging.basicConfig(level=logging.INFO )
logger = logging.getLogger(__name__)


class Log:
    @staticmethod
    def info(message: str):
        logger.info(message)

    @staticmethod
    def warn(message: str, error: Optional[Exception] = None):
        logger.warning(message)
        if error:
            logger.warning(f"Error details: {error}")

    @staticmethod
    def error(message: str, error: Optional[Exception] = None):
        logger.error(message)
        if error:
            logger.error(f"Error details: {error}")

    @staticmethod
    def debug(message: str):
        logger.debug(message)
