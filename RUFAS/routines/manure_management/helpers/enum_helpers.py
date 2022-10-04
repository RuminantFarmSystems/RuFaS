"""
Collection of miscellaneous helper functions.
"""
from __future__ import annotations

from enum import Enum


class DefaultEnum(Enum):
    """
    An extended version of the built-in Enum class that allows searching
    for the member that matches or partially matches a search pattern.

    Notes:
        Declare a DEFAULT member is recommended in case of an unsuccessful search.
        The DEFAULT member should act as an alias for another member
        (e.g., `DEFAULT = A_PREVIOUS_MEMBER`).

    """

    @classmethod
    def get_type(cls, member_name: str) -> DefaultEnum:
        """Return the enum member that matches the given name.
        Args:
            member_name: name of the desired enum member.
        Returns:
            The enum member that matches the given name.
                Otherwise, return the default type.
        """

        for member in cls:
            if member.name.upper() == member_name.strip().upper():
                return member

        return cls.get_default_type()

    @classmethod
    def get_default_type(cls, *args) -> DefaultEnum:
        """Return either the DEFAULT member if it exists or the first member.

        Returns:
            The DEFAULT member of this enum class if it exists. Otherwise, the
                first member is returned.
        """

        if hasattr(cls, 'DEFAULT'):
            return getattr(cls, 'DEFAULT')

        return list(cls)[0]
