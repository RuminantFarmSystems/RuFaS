from enum import Enum, unique


@unique
class DiseaseOutcome(Enum):
    """
    A list of possible outcomes for animals that have developed a disease.

    DEATH : str
        Animal dies while sick.
    RECOVERY : str
        Animal is eligible to recover but only after n days.
    CULL : str
        Animal is removed from the herd (sold).
    REMAIN_DISEASED : str
        Animal continues to be afflicted by the disease.


    """

    DEATH = "death"
    RECOVERY = "recovery"
    CULL = "cull"
    REMAIN_DISEASED = "remain_diseased"

    def __str__(self) -> str:
        """
        Returns the value of the enum member as its string representation.
        """

        return self.value
