from importlib import metadata

try:
    from ._version import __version__
except ImportError:
    try:
        __version__ = metadata.version("aicage")
    except metadata.PackageNotFoundError:
        __version__ = "0.0.0"

__all__ = ["__version__"]
