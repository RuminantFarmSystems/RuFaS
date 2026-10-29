from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import sys
from RUFAS.output_manager import LogVerbosity
from pathlib import Path
from typing import Any

LOGGER_NAME = "RUFAS"

LOG_FORMAT = "[%(asctime)s][%(levelname)s][%(rufas_metadata_prefix)s] %(message)s"
DATE_FORMAT = "%d-%b-%Y_%a_%H-%M-%S"


class RufasContextFilter(logging.Filter):
    """Adds simulation context to RuFaS log records."""

    def __init__(self, metadata_prefix: str = "") -> None:
        super().__init__()
        self.metadata_prefix = metadata_prefix

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "rufas_metadata_prefix"):
            record.rufas_metadata_prefix = self.metadata_prefix

        return True


class RufasLogFormatter(logging.Formatter):
    """Formats RuFaS log messages with timestamps, metadata, and optional console colors."""

    COLORS = {
        logging.INFO: "\033[92m",
        logging.WARNING: "\033[93m",
        logging.ERROR: "\033[91m",
        logging.CRITICAL: "\033[95m",
    }

    RESET_COLOR = "\033[0m"

    def __init__(self, use_colors: bool = False) -> None:
        super().__init__(
            fmt=LOG_FORMAT,
            datefmt=DATE_FORMAT,
            defaults={"rufas_metadata_prefix": ""},
        )
        self.use_colors = use_colors

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        timestamp = datetime.fromtimestamp(record.created)
        return timestamp.strftime(DATE_FORMAT) + f".{timestamp.microsecond:06d}"

    def format(self, record: logging.LogRecord) -> str:
        formatted_message = super().format(record)

        if self.use_colors:
            color = self.COLORS.get(record.levelno, "")
            if color:
                return f"{color}{formatted_message}{self.RESET_COLOR}"

        return formatted_message


def get_log_level(verbosity: LogVerbosity) -> int:
    log_levels = {
        LogVerbosity.NONE: logging.CRITICAL + 1,
        LogVerbosity.CREDITS: logging.CRITICAL + 1,
        LogVerbosity.ERRORS: logging.ERROR,
        LogVerbosity.WARNINGS: logging.WARNING,
        LogVerbosity.LOGS: logging.INFO,
    }

    return log_levels[verbosity]


def configure_logging(
    log_directory: Path,
    log_level: int = logging.INFO,
    output_prefix: str = "rufas",
    write_log_file: bool = True,
    metadata_prefix: str = "",
) -> None:
    """
    Configures the RuFaS logging system.

    Parameters
    ----------
    log_directory : Path
        Directory in which log files should be written.
    log_level : int, default=logging.INFO
        Minimum logging level that will be emitted.
    output_prefix : str, default="rufas"
        Prefix used for the generated log file.
    write_log_file : bool, default=True
        Indicates whether logs should be written to a file.
    metadata_prefix : str
        The metadata prefix.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    context_filter = RufasContextFilter(metadata_prefix)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(RufasLogFormatter(use_colors=True))
    console_handler.addFilter(context_filter)
    logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Gets a RuFaS logger.

    Parameters
    ----------
    name : str
        Name of the logger.

    Returns
    -------
    logging.Logger
        A child logger of the main RuFaS logger.
    """
    if name == LOGGER_NAME or name.startswith(f"{LOGGER_NAME}."):
        return logging.getLogger(name)

    return logging.getLogger(f"{LOGGER_NAME}.{name}")


def log(
    logger: logging.Logger,
    level: int,
    name: str,
    message: str,
    info_map: dict[str, Any] | None = None,
) -> None:
    """
    Logs a RuFaS message with its associated metadata.

    Parameters
    ----------
    logger : logging.Logger
        Logger used to emit the message.
    level : int
        Python logging level for the message.
    name : str
        Descriptive name of the logged event.
    message : str
        Detailed log message.
    info_map : dict[str, Any] | None, default=None
        Additional RuFaS metadata associated with the message.
    """
    logger.log(
        level,
        message,
        extra={
            "rufas_name": name,
            "rufas_info_map": info_map or {},
        },
    )
