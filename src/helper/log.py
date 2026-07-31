"""Loguru-based logging shared across commands."""

import sys

from loguru import logger

_LEVELS = {0: "ERROR", 1: "WARNING", 2: "INFO"}

logger.remove()
_handler_id = logger.add(sys.stderr, level="ERROR")


def set_level(verbose: int) -> None:
    """Reconfigure the stderr sink for the given verbosity (0-3+)."""
    global _handler_id
    logger.remove(_handler_id)
    _handler_id = logger.add(sys.stderr, level=_LEVELS.get(verbose, "DEBUG"))
