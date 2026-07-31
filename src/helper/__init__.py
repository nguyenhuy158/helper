import importlib.metadata

# Expose command modules for library usage
from . import commands as commands
from .commands import (
    all_info as all_info,
)
from .commands import (
    arch as arch,
)
from .commands import (
    disk as disk,
)
from .commands import (
    internal_ip as internal_ip,
)
from .commands import (
    public_ip as public_ip,
)
from .commands import (
    speed as speed,
)
from .commands import (
    system_info as system_info,
)

try:
    __version__ = importlib.metadata.version("helper-cli")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"
