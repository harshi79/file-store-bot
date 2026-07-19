import logging
import os
import sys


def env_int(name: str, default: int) -> int:
    """Read an integer environment variable and fail early on invalid values."""
    value = os.getenv(name, str(default))
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer, got {value!r}") from exc


PORT = env_int("PORT", 10000)  # Render supplies PORT automatically.
MAX_BATCH_SIZE = env_int("MAX_BATCH_SIZE", 200)


def LOGGER(name: str, client_name: str) -> logging.Logger:
    """Return a configured console logger without adding duplicate handlers."""
    logger = logging.getLogger(f"filestore.{client_name}.{name}")
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
    logger.propagate = False
    return logger
