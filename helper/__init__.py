from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("helper-cli")
except PackageNotFoundError:
    # If running in development mode without installation
    __version__ = "dev"
