from typing import Optional

from RUFAS.biophysical.field.crop.crop_data import CropData
from RUFAS.biophysical.field.crop.non_water_uptake import NonWaterUptake
from RUFAS.biophysical.field.soil.soil_data import SoilData

"""
This module is based upon the 'Phosphorus Uptake" section (5:2.3.2) of of the SWAT model documentation
"""


class PhosphorusUptake(NonWaterUptake):
    """
    A class for managing phosphorus incorporation in crops.

    Parameters
    ----------
    crop_data : CropData, optional
        An instance of `CropData` containing crop specifications and attributes. If not provided, a default
        `CropData` instance is initialized with default values.
    nutrient_distro_param : float, default 10
        Phosphorus uptake distribution parameter (unitless).
    nutrient_shapes : Optional[List[float]], default None
        First and second shape coefficients for the nitrogen uptake equations (unitless).
    previous_nutrient : Optional[float], default None
        Phosphorus value on the previous day (kg/ha).
    total_nutrient_uptake : Optional[float], default None
        Total amount of phosphorus taken up by the plant (kg/ha).
    potential_nutrient_uptake : Optional[float], default None
        Potential phosphorus to be taken up by the plant under ideal circumstances for the current day (kg/ha).
    actual_nutrient_uptakes : Optional[List[float]], default None
        Actual phosphorus to be taken up by the plant from each soil layer (kg/ha).
    layer_nutrient_potentials : Optional[float], default None
        Potential phosphorus uptake from each soil layer (kg/ha).
    unmet_nutrient_demands : Optional[float], default None
        Unmet phosphorus demands by overlaying soil layers (kg/ha).
    nutrient_requests : Optional[float], default None
        Phosphorus requested from each soil layer (kg/ha).


    References
    ----------
    'Phosphorus Uptake' section (5:2.3.2) of the SWAT.

    """

    def __init__(
        self,
        crop_data: Optional[CropData] = None,
        nutrient_distro_param: float = 10.0,
        nutrient_shapes: Optional[list[float]] = None,
        previous_nutrient: Optional[float] = None,
        potential_nutrient_uptake: Optional[float] = None,
        layer_nutrient_potentials: Optional[float] = None,
        unmet_nutrient_demands: Optional[float] = None,
        nutrient_requests: Optional[float] = None,
        actual_nutrient_uptakes: Optional[list[float]] = None,
        total_nutrient_uptake: Optional[float] = None,
    ):
        super().__init__(
            crop_data,
            nutrient_distro_param,
            nutrient_shapes,
            previous_nutrient,
            potential_nutrient_uptake,
            layer_nutrient_potentials,
            unmet_nutrient_demands,
            nutrient_requests,
            actual_nutrient_uptakes,
            total_nutrient_uptake,
        )

    def uptake(self, soil_data: SoilData) -> None:
        """
        Main phosphorus incorporation function - runs all phosphorus processes and stores phosphorus as biomass.

        Parameters
        ----------
        soil_data : SoilData
            The SoilData object that tracks soil properties.

        Notes
        -----
        Calling this function will execute all phosphorus incorporation routines. It determines the amount of
        phosphorus desired by the plant and extracts phosphorus from the accessible soil profile. The extracted
        phosphorus is then added to plant biomass.

        """
        self.uptake_main_process(soil_data, "phosphorus", "labile_inorganic_phosphorus_content")
        self.crop_data.phosphorus = self.determine_stored_nutrient(
            self.total_nutrient_uptake, self.crop_data.phosphorus, 0
        )
