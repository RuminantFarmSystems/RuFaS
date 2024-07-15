from enum import Enum
from typing import List


class Modifiability(Enum):
    """
    Enum class representing the modifiability status of a variable.

    This Enum defines various levels of modifiability for a variable, indicating whether a variable is required at
    initialization and if it can be modified during runtime.

    Attributes
    ----------
    REQUIRED_LOCKED : str
        Indicates the variable must be initialized with a value and cannot be modified thereafter.
    REQUIRED_UNLOCKED : str
        Indicates the variable must be initialized with a value but can be modified during runtime.
    UNREQUIRED_UNLOCKED : str
        Indicates the variable does not need to be initialized with a value and can be modified during runtime.
    """

    REQUIRED_LOCKED: str = "required locked"
    REQUIRED_UNLOCKED: str = "required unlocked"
    UNREQUIRED_UNLOCKED: str = "unrequired unlocked"

    @classmethod
    def values(cls) -> List[str]:
        """
        Provides a list of the string values of the enum members.

        Returns
        -------
        List[str]
            A list containing the string values of the enum members.
        """
        return list(map(lambda c: c.value, cls))

    @classmethod
    def get_required_during_initialization(cls) -> List["Modifiability"]:
        return [Modifiability.REQUIRED_LOCKED, Modifiability.REQUIRED_UNLOCKED]

    @classmethod
    def get_modifiable_at_runtime(cls) -> List["Modifiability"]:
        return [Modifiability.REQUIRED_UNLOCKED, Modifiability.UNREQUIRED_UNLOCKED]