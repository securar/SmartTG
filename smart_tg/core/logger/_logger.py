import sys

from loguru import logger

from smart_tg.core.logger._config import DEFAULT_FORMAT


def create_logger(name: str):
    logger.remove()  # Remove default loguru logger to avoid conflicts
    logger.add(sink=sys.stdout, format=DEFAULT_FORMAT, enqueue=True)
    return logger.bind(name=name)
