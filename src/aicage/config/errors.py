__all__ = ["ConfigError"]


class ConfigError(Exception):
    """Raised when configuration cannot be loaded or saved."""
