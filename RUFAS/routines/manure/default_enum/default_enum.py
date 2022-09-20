from __future__ import annotations

from enum import Enum


class DefaultEnum(Enum):
    """An Enum-derived class that helps find members or returns default type as fallback.

    For any subclass that extends from this class, declare a DEFAULT member is
    recommended in case of an unsuccessful lookup. The DEFAULT member could act
    as an alias for another member (i.e., `DEFAULT = A_PREVIOUS_MEMBER`).

    Also note how this class does not declare any members, because it is meant
    to be subclassed.

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
    def get_default_type(cls) -> DefaultEnum:
        """Return either the DEFAULT member if it exists or the first member.

        Returns:
            The DEFAULT member of this enum class if it exists. Otherwise, the
                first member is returned.

        """

        if hasattr(cls, 'DEFAULT'):
            return getattr(cls, 'DEFAULT')

        return list(cls)[0]
