from enum import Enum
from typing import Any

POOL_ELEMENT_TYPE = dict[str, Any]


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
