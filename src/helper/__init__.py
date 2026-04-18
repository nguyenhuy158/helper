import importlib.metadata

# Expose command modules for library usage
from . import commands as commands
from .commands import (
    all_info as all_info,
    arch as arch,
    disk as disk,
    internal_ip as internal_ip,
    public_ip as public_ip,
    speed as speed,
    system_info as system_info,
)

try:
    __version__ = importlib.metadata.version("helper-cli")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"
