from typing import List, Optional

from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.crop.nitrogen_incorporation import NitrogenIncorporation
from RUFAS.routines.field.crop.nutrient_uptake import NutrientUptake
from RUFAS.routines.field.soil.soil_data import SoilData

"""
This module is based upon the 'Phosphorus Uptake" section (5:2.3.2) of of the SWAT model documentation

Also: Since much of the functionality is similar to nitrogen (5:2.3.2), many of the static Nitrogen functions are
called directly.
"""


class PhosphorusIncorporation(NutrientUptake):
    """
    A class for managing phosphorus incorporation in crops.

    Parameters
    ----------
    crop_data : CropData, optional
        An instance of `CropData` containing crop specifications and attributes. If not provided, a default
        `CropData` instance is initialized with default values.
    phosphorus_distro_param : float, default 10
        Phosphorus uptake distribution parameter (unitless).
    phosphorus_shapes : Optional[List[float]], default None
        First and second shape coefficients for the nitrogen uptake equations (unitless).
    previous_phosphorus : Optional[float], default None
        Phosphorus value on the previous day (kg/ha).
    total_phosphorus_uptake : Optional[float], default None
        Total amount of phosphorus taken up by the plant (kg/ha).
    potential_phosphorus_uptake : Optional[float], default None
        Potential phosphorus to be taken up by the plant under ideal circumstances for the current day (kg/ha).
    actual_phosphorus_uptakes : Optional[List[float]], default None
        Actual phosphorus to be taken up by the plant from each soil layer (kg/ha).
    layer_phosphorus_potentials : Optional[float], default None
        Potential phosphorus uptake from each soil layer (kg/ha).
    unmet_phosphorus_demands : Optional[float], default None
        Unmet phosphorus demands by overlaying soil layers (kg/ha).
    phosphorus_requests : Optional[float], default None
        Phosphorus requested from each soil layer (kg/ha).

    Attributes
    ----------
    crop_data : CropData
        A reference to the `crop_data` object, used for accessing and updating information related to phosphorus
        uptake and incorporation.
    phosphorus_distro_param : float, default 10
        Phosphorus uptake distribution parameter (unitless).
    phosphorus_shapes : Optional[List[float]], default None
        First and second shape coefficients for the nitrogen uptake equations (unitless).
    previous_phosphorus : Optional[float], default None
        Phosphorus value on the previous day (kg/ha).
    total_phosphorus_uptake : Optional[float], default None
        Total amount of phosphorus taken up by the plant (kg/ha).
    potential_phosphorus_uptake : Optional[float], default None
        Potential phosphorus to be taken up by the plant under ideal circumstances for the current day (kg/ha).
    actual_phosphorus_uptakes : Optional[List[float]], default None
        Actual phosphorus to be taken up by the plant from each soil layer (kg/ha).
    layer_phosphorus_potentials : Optional[float]
        Potential phosphorus uptake from each soil layer (kg/ha).
    unmet_phosphorus_demands : Optional[float]
        Unmet phosphorus demands by overlaying soil layers (kg/ha).
    phosphorus_requests : Optional[float]
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
        phosphorus_distro_param: float = 10,
        phosphorus_shapes: Optional[List[float]] = None,
        previous_phosphorus: Optional[float] = None,
        total_phosphorus_uptake: Optional[float] = None,
        potential_phosphorus_uptake: Optional[float] = None,
        actual_phosphorus_uptakes: Optional[List[float]] = None,
        layer_phosphorus_potentials: Optional[float] = None,
        unmet_phosphorus_demands: Optional[float] = None,
        phosphorus_requests: Optional[float] = None,
    ):
        super().__init__(crop_data, actual_phosphorus_uptakes)

        self.phosphorus_distro_param = phosphorus_distro_param
        self.phosphorus_shapes = phosphorus_shapes
        self.previous_phosphorus = previous_phosphorus
        self.total_phosphorus_uptake = total_phosphorus_uptake
        self.potential_phosphorus_uptake = potential_phosphorus_uptake
        self.layer_phosphorus_potentials = layer_phosphorus_potentials
        self.unmet_phosphorus_demands = unmet_phosphorus_demands
        self.phosphorus_requests = phosphorus_requests

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
        self.phosphorus_shapes = self.determine_nutrient_shape_parameters(
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
            self.phosphorus_shapes[0],
            self.phosphorus_shapes[1],
        )
        self.crop_data.optimal_phosphorus = self.determine_optimal_nutrient(
            self.crop_data.optimal_phosphorus_fraction, self.crop_data.biomass
        )
        if self.crop_data.optimal_phosphorus - self.previous_phosphorus < 0:
            self.potential_phosphorus_uptake = 0
        else:
            self.potential_phosphorus_uptake = self.determine_potential_nutrient_uptake(
                self.crop_data.optimal_phosphorus,
                self.previous_phosphorus,
                self.crop_data.mature_phosphorus_fraction,
                self.crop_data.biomass_growth_max,
            )
        self.uptake_phosphorus(layer_phosphates, layer_depths)
        soil_data.set_vectorized_layer_attribute("labile_inorganic_phosphorus_content", layer_phosphates)
        self.crop_data.phosphorus = self.determine_stored_nutrient(
            self.total_phosphorus_uptake, self.crop_data.phosphorus, 0
        )

    def uptake_phosphorus(self, layer_phosphates: List[float], layer_depths: List[float]) -> None:
        """
        Conducts steps necessary to uptake phosphorus from soil.

        Parameters
        ----------
        layer_phosphates : List[float]
            Phosphates contained in each soil layer.
        layer_depths : List[float]
            The lowest depth of each soil layer.

        Notes
        -----
        After the actual phosphorus uptake is calculated for each accessible soil layer, that amount is removed from
        the layer_phosphates list given as input to the function. This reflects the reduction in soil phosphate levels
        due to plant uptake.

        """
        self.find_deepest_accessible_soil_layer(layer_depths)
        accessible_depths = self.access_layers(layer_depths)
        accessible_phosphates = self.access_layers(layer_phosphates)
        self.layer_phosphorus_potentials = self.determine_layer_nutrient_uptake_potential(
            accessible_depths,
            self.potential_phosphorus_uptake,
            self.crop_data.root_depth,
            self.phosphorus_distro_param,
        )
        self.unmet_phosphorus_demands = NitrogenIncorporation.determine_layer_nutrient_demands(
            self.layer_phosphorus_potentials, accessible_phosphates
        )
        self.phosphorus_requests = NitrogenIncorporation.determine_layer_nutrient_uptake(
            self.unmet_phosphorus_demands,
            self.layer_phosphorus_potentials,
            accessible_phosphates,
        )

        self.actual_nutrient_uptakes = self.determine_layer_extracted_resource(
            self.phosphorus_requests, accessible_phosphates
        )

        self.extend_nutrient_uptakes_to_full_profile()
        self.extract_nutrient_from_soil_layers(layer_phosphates)
        self.total_phosphorus_uptake = self.tally_total_nutrient_uptake()

    # ---- member functions (setters, internal utility, call sub-routines) ----
    def shift_phosphorus_time(self) -> None:
        """
        Copies the current phosphorus value to previous_phosphorus (for use between time steps).

        """
        self.previous_phosphorus = self.crop_data.phosphorus
