from enum import Enum
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any


LOGGER_NAME = "RUFAS"

LOG_FORMAT = "[%(asctime)s][%(levelname)s][%(rufas_name)s] %(message)s"
DATE_FORMAT = "%d-%b-%Y_%a_%H-%M-%S"


class LogVerbosity(Enum):
    """
    The different types of logs printed by ``OutputManager``. Set by the ``verbose`` gnu arg in main.py.

    Attributes
    ----------
    NONE : str
        Selecting ``NONE`` will tell ``OutputManager`` not to print out anything during a simulation.
    CREDITS : str
        Selecting ``CREDITS`` will tell ``OutputManager`` to only print out the credits.
    ERRORS : str
        Selecting ``ERRORS`` will tell ``OutputManager`` to print out all credits and errors added during a simulation.
    WARNINGS : str
        Selecting ``WARNINGS`` will tell ``OutputManager`` to print out the credits as well as warnings and errors added
        during a simulation.
    LOGS : str
        Selecting ``LOGS`` will tell ``OutputManager`` to print out the credits as well as logs, warnings, and errors
        added during a simulation.

    Notes
    -----
    ``CREDITS`` is the default setting.
    """

    NONE = "none"
    CREDITS = "credits"
    ERRORS = "errors"
    WARNINGS = "warnings"
    LOGS = "logs"

    def __le__(self, other: "LogVerbosity") -> bool:
        order = {
            LogVerbosity.NONE: 0,
            LogVerbosity.CREDITS: 1,
            LogVerbosity.ERRORS: 2,
            LogVerbosity.WARNINGS: 3,
            LogVerbosity.LOGS: 4,
        }

        if other == LogVerbosity.NONE and self != LogVerbosity.NONE:
            return False

        return order[self] <= order[other]

    def __str__(self) -> str:
        if self.value == "none":
            return "NONE"
        return self.value[:-1].upper()


LOG_LEVELS: dict[LogVerbosity, int] = {
    LogVerbosity.LOGS: logging.INFO,
    LogVerbosity.WARNINGS: logging.WARNING,
    LogVerbosity.ERRORS: logging.ERROR,
}


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
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(log_level)
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        defaults={"rufas_name": ""},
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if write_log_file:
        log_directory.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_directory / f"{output_prefix}.log",
            maxBytes=10_000_000,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


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
