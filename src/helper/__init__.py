"""Helper library - system info functions usable programmatically.

Submodules are loaded lazily (PEP 562) so `import helper` stays cheap:

    import helper
    helper.disk.get_usage()
    helper.system_info.get_info()
"""

import importlib
import importlib.metadata

# Command modules exposed as helper.<name> for library usage
_LIBRARY_MODULES = {
    "all_info",
    "arch",
    "disk",
    "internal_ip",
    "public_ip",
    "speed",
    "system_info",
}

try:
    __version__ = importlib.metadata.version("helper-cli")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"


def __getattr__(name):
    if name == "commands":
        return importlib.import_module(".commands", __name__)
    if name in _LIBRARY_MODULES:
        return importlib.import_module(f".commands.{name}", __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | _LIBRARY_MODULES | {"commands"})
