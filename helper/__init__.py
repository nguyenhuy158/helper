"""Helper CLI tool."""

from importlib.metadata import version, PackageNotFoundError

# Expose command modules for library usage
from . import commands
from .commands import disk, system_info, all_info, arch, internal_ip, public_ip, speed

try:
    __version__ = version("helper-cli")
except PackageNotFoundError:
    # If running in development mode without installation
    __version__ = "dev"
