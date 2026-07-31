"""Loguru-based logging shared across commands."""

import shlex
import subprocess
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
    if verbose >= 3:
        _enable_subprocess_tracing()


def _enable_subprocess_tracing() -> None:
    """Log every external command the CLI spawns (DEBUG level).

    Patches subprocess.Popen.__init__ once; run/check_output/check_call
    all funnel through Popen, so this covers every call site.
    """
    if getattr(subprocess.Popen.__init__, "_helper_traced", False):
        return

    original_init = subprocess.Popen.__init__

    def traced_init(self, *args, **kwargs):
        cmd = kwargs.get("args", args[0] if args else None)
        if isinstance(cmd, (list, tuple)):
            cmd = " ".join(shlex.quote(str(part)) for part in cmd)
        logger.debug(f"$ {cmd}")
        original_init(self, *args, **kwargs)

    traced_init._helper_traced = True
    subprocess.Popen.__init__ = traced_init
