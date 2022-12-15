from __future__ import annotations

from enum import Enum


class DefaultEnum(Enum):
    """An Enum-derived class that helps find members or returns a default type as fallback.

    For any subclass that extends from this class, declaring a DEFAULT member is
    recommended in case of an unsuccessful lookup. The DEFAULT member should act
    as an alias for another member (i.e., `DEFAULT = AN_EXISTING_MEMBER`).

    Also note how this class does not declare any members, because it is meant
    to be subclassed.

    """

    @classmethod
    def get_type(cls, lookup_name: str) -> DefaultEnum:
        """Returns the enum member that matches the given name, case-insensitive.

        Args:
            lookup_name: name of the lookup enum member.

        Returns:
            The enum member that matches the given name. If no match is found,
            the DEFAULT member is returned.

        """
        for member in cls:
            if member.name.upper() == lookup_name.strip().upper():
                return member
            elif type(member.value) == str and member.value.upper() == lookup_name.strip().upper():
                return member

        return cls.get_default_type()

    @classmethod
    def get_default_type(cls) -> DefaultEnum:
        """Returns either the DEFAULT member if it exists or the first member.

        Raises:
            IndexError: If the enum has no members.

        Returns:
            The DEFAULT member of this enum class if it exists. Otherwise, the
                first member is returned.

        """
        if hasattr(cls, 'DEFAULT'):
            return getattr(cls, 'DEFAULT')

        try:
            return list(cls)[0]
        except IndexError:
            raise IndexError(f'Enum {cls.__name__} has no members.')
