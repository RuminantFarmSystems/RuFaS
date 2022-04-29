"""
Collection of miscellaneous helper functions.
"""
from __future__ import annotations

from enum import Enum


class ExtendedEnum(Enum):
    """
    An extended version of the built-in Enum class that allows searching
    for the member that matches or partially matches a search pattern.

    Notes:
        Declare a DEFAULT member is recommended in case of an unsuccessful search.
        The DEFAULT member should act as an alias for another member
        (e.g., `DEFAULT = A_PREVIOUS_MEMBER`).

    """

    @classmethod
    def get_enum(cls, query_str: str) -> ExtendedEnum:
        """Return the first enum member whose name contains the query string.

        Args:
            query_str: name of the desired enum member

        Returns:
            The first enum member whose name contains the query string.
                Otherwise, return the DEFAULT member.

        """

        for e in cls:  # Iterate through each enum member
            if query_str.strip().lower() in e.name.lower():
                return e

        return cls.get_default_enum()

    @classmethod
    def get_default_enum(cls) -> ExtendedEnum:
        """Return the DEFAULT member if there is one declared.

        If this method is invoked and the DEFAULT member does not exist,
        an `AttributeError` is raised.

        Notes:
            If DEFAULT has some other contextual meaning, please override this method.

        Returns:
            The DEFAULT member of this enum class.

        """

        return getattr(cls, 'DEFAULT')
