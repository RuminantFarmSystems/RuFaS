from abc import abstractmethod, ABC
from typing import Optional
from RUFAS.biophysical.field.crop.crop_data import CropData
from RUFAS.biophysical.field.soil.soil_data import SoilData


class NutrientUptake(ABC):
    """
    Manages overlapping logic for nitrogen, phosphorus, and water uptake in crops.

    Parameters
    ----------
    crop_data : Optional[CropData], optional
        An instance of `CropData` containing crop specifications and attributes.
        Defaults to a new instance of `CropData` if not provided.

    """

    def __init__(self, crop_data: Optional[CropData]):
        self.crop_data = crop_data or CropData()

    @abstractmethod
    def uptake(self, soil_data: SoilData) -> None:
        """Abstract method for nutrient uptake."""
        pass

    @staticmethod
    def determine_layer_nutrient_demands(
        uptake_potentials: list[float], nutrient_availabilities: list[float]
    ) -> list[float]:
        """
        Calculates the demand for a nutrient from each soil layer.

        Parameters
        ----------
        uptake_potentials : list[float]
            Maximum uptake of the nutrient by the plant from each soil layer.
        nutrient_availabilities : list[float]
            Available amount of the nutrient in each soil layer.

        Returns
        -------
        list[float]
            Demands for the nutrient from each soil layer.

        References
        ----------
        pseudocode: C.5.C.5

        """
        layer_delta = [desired - available for desired, available in zip(uptake_potentials, nutrient_availabilities)]
        layer_demand = [sum(layer_delta[:i]) for i in range(len(layer_delta))]
        return [max(val, 0) for val in layer_demand]

    @staticmethod
    def tally_total_nutrient_uptake(actual_nutrient_uptakes: list[float]) -> float:
        """
        Determines total nutrient extracted from soil by summing actual uptake from each layer.

        Parameters
        ----------
        actual_nutrient_uptakes : Optional[List[float]]
            Actual nutrient uptake from each soil layer (kg/ha or mm).

        """
        return sum(actual_nutrient_uptakes)
