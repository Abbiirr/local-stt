from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from .config import config_dir


LOGGER_NAME = "local_dictation"


def setup_logging() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if any(isinstance(handler, RotatingFileHandler) for handler in logger.handlers):
        return logger

    target_dir = config_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        target_dir / "app.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)
    logger.info("Logging initialized.")
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)
