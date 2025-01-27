from typing import Optional

from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.crop.non_water_uptake import NonWaterUptake
from RUFAS.routines.field.soil.soil_data import SoilData

"""
This module is based upon the 'Phosphorus Uptake" section (5:2.3.2) of of the SWAT model documentation

Also: Since much of the functionality is similar to nitrogen (5:2.3.2), many of the static Nitrogen functions are
called directly.
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

    Notes
    -----
    Since much of the functionality is similar to nitrogen (5:2.3.2), many of the static Nitrogen functions are
    called directly.

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
        super().__init__(crop_data,
                         nutrient_distro_param,
                         nutrient_shapes,
                         previous_nutrient,
                         potential_nutrient_uptake,
                         layer_nutrient_potentials,
                         unmet_nutrient_demands,
                         nutrient_requests,
                         actual_nutrient_uptakes,
                         total_nutrient_uptake)

    def incorporate_phosphorus(self, soil_data: SoilData) -> None:
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
        layer_depths = soil_data.get_vectorized_layer_attribute("bottom_depth")
        layer_phosphates = soil_data.get_vectorized_layer_attribute("labile_inorganic_phosphorus_content")

        self.shift_phosphorus_time()
        self.nutrient_shapes = self.determine_nutrient_shape_parameters(
            self.crop_data.half_mature_heat_fraction,
            self.crop_data.mature_heat_fraction,
            self.crop_data.emergence_phosphorus_fraction,
            self.crop_data.half_mature_phosphorus_fraction,
            self.crop_data.mature_phosphorus_fraction,
        )
        self.crop_data.optimal_phosphorus_fraction = self.determine_optimal_nutrient_fraction(
            self.crop_data.heat_fraction,
            self.crop_data.emergence_phosphorus_fraction,
            self.crop_data.mature_phosphorus_fraction,
            self.nutrient_shapes[0],
            self.nutrient_shapes[1],
        )
        self.crop_data.optimal_phosphorus = self.determine_optimal_nutrient(
            self.crop_data.optimal_phosphorus_fraction, self.crop_data.biomass
        )
        if self.crop_data.optimal_phosphorus - self.previous_nutrient < 0:
            self.potential_nutrient_uptake = 0
        else:
            self.potential_nutrient_uptake = self.determine_potential_nutrient_uptake(
                self.crop_data.optimal_phosphorus,
                self.previous_nutrient,
                self.crop_data.mature_phosphorus_fraction,
                self.crop_data.biomass_growth_max,
            )
        self.uptake_nutrient(layer_phosphates, layer_depths)
        soil_data.set_vectorized_layer_attribute("labile_inorganic_phosphorus_content", layer_phosphates)
        self.crop_data.phosphorus = self.determine_stored_nutrient(
            self.total_nutrient_uptake, self.crop_data.phosphorus, 0
        )

    def shift_phosphorus_time(self) -> None:
        """
        Copies the current phosphorus value to previous_phosphorus (for use between time steps).

        """
        self.previous_nutrient = self.crop_data.phosphorus
