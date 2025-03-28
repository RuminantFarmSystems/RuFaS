from RUFAS.biophysical.animal.bedding.bedding import Bedding
from RUFAS.biophysical.animal.data_types.bedding_config import BeddingConfig


class Sand(Bedding):
    """
    Abstract base class for all organic bedding types.

    This class extends the BaseBedding class and provides a method to calculate the total
    amount of bedding needed for all animals in a pen.

    """

    def __init__(self, name: str, bedding_config: BeddingConfig) -> None:
        super().__init__(name, bedding_config)
        self.sand_removal_efficiency = bedding_config.sand_removal_efficiency

    def calculate_total_bedding_mass(self, num_animals: int) -> float:
        """
        Calculate the total amount of bedding needed for all animals in the given pen.

        Parameters
        ----------
        num_animals : int
            The number of animals in the pen.

        Returns
        -------
        float
            Total amount of bedding needed for all animals in the given pen (kg/day).

        """
        bedding_mass = super().calculate_total_bedding_mass(num_animals)
        return bedding_mass * (1 - self.sand_removal_efficiency)
