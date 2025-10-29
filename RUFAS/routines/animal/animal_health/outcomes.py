from enum import Enum, unique


@unique
class DiseaseOutcomes(Enum):
    """
    A list of possible outcomes for animals that have developed a disease.

    HEALTHY : str
        Animal is healthy.
    DEAD : str
        Animal dies while sick.
    IN_RECOVERY : str
        Animal is eligible to recover but only after n days.
    CULLED : str
        Animal is removed from the herd (sold).
    DISEASED : str
        Animal continues to be afflicted by the disease.


    """

    HEALTHY = "healthy"
    DEATH = "dead"
    IN_RECOVERY = "in_recovery"
    CULL = "culled"
    DISEASED = "diseased"

    def __str__(self) -> str:
        """
        Returns the value of the enum member as its string representation.
        """

        return self.value
