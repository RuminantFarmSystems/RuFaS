from typing import Optional, List
from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.crop.nitrogen_incorporation import NitrogenIncorporation
from RUFAS.routines.field.soil.soil_data import SoilData

# TODO: Phosphorus has identical methods to NitrogenIncorporation, excluding nitrogen fixation. They
#  should be combined into one class (NutrientIncorporation) and simplified. Issue #450

"""
This module is based upon the 'Phosphorus Uptake" section (5:2.3.2) of of the SWAT model documentation

Also: Since much of the functionality is similar to nitrogen (5:2.3.2), many of the static Nitrogen functions are
called directly.
"""


class PhosphorusIncorporation:
    """
    A class for managing phosphorus incorporation in crops.

    Parameters
    ----------
    crop_data : Optional[CropData], optional
        An instance of `CropData` containing crop specifications and attributes. If not provided, a default
        `CropData` instance is initialized with default values.

    Attributes
    ----------
    data : CropData
        A reference to the `crop_data` object, used for accessing and updating information related to phosphorus
        uptake and incorporation.

    References
    ----------
    'Phosphorus Uptake' section (5:2.3.2) of the SWAT.

    Notes
    -----
    Since much of the functionality is similar to nitrogen (5:2.3.2), many of the static Nitrogen functions are
    called directly.

    """
    def __init__(self, crop_data: Optional[CropData] = None):
        self.data = crop_data or CropData()  # initialize with defaults, if not given

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
        self.data.phosphorus_shapes = NitrogenIncorporation.determine_nutrient_shape_parameters(
            self.data.half_mature_heat_fraction, self.data.mature_heat_fraction,
            self.data.emergence_phosphorus_fraction, self.data.half_mature_phosphorus_fraction,
            self.data.mature_phosphorus_fraction
        )
        self.data.optimal_phosphorus_fraction = NitrogenIncorporation.determine_optimal_nutrient_fraction(
            self.data.heat_fraction, self.data.emergence_phosphorus_fraction, self.data.mature_phosphorus_fraction,
            self.data.phosphorus_shapes[0], self.data.phosphorus_shapes[1]
        )
        self.data.optimal_phosphorus = NitrogenIncorporation.determine_optimal_nutrient(
            self.data.optimal_phosphorus_fraction, self.data.biomass
        )
        if self.data.optimal_phosphorus - self.data.previous_phosphorus < 0:
            self.data.potential_phosphorus_uptake = 0
        else:
            self.data.potential_phosphorus_uptake = NitrogenIncorporation.determine_potential_nutrient_uptake(
                self.data.optimal_phosphorus, self.data.previous_phosphorus, self.data.mature_phosphorus_fraction,
                self.data.biomass_growth_max
            )
        self.uptake_phosphorus(layer_phosphates, layer_depths)
        soil_data.set_vectorized_layer_attribute("labile_inorganic_phosphorus_content", layer_phosphates)
        # TODO: the above line is a temporary solution - should be changed with GitHub Issue #450
        self.data.phosphorus = NitrogenIncorporation.determine_stored_nutrient(
            self.data.total_phosphorus_uptake, self.data.phosphorus, 0
        )

    def uptake_phosphorus(self, layer_phosphates: List[float], layer_depths: List[float]):
        """conducts steps necessary to uptake phosphorus from soil

        Args:
            layer_phosphates: phosphates contained in each soil layer; updated in place
            layer_depths: the lowest depth of each soil layer.

        Details: after the actual phosphorus uptake is calculated for each accessible soil layer, that amount is removed
        from the layer_phosphates list given as input to the function.
        """
        self.find_deepest_accessible_soil_layer(layer_depths)
        accessible_depths = self.access_layers(layer_depths)
        accessible_phosphates = self.access_layers(layer_phosphates)
        self.data.layer_phosphorus_potentials = NitrogenIncorporation.determine_layer_nutrient_uptake_potential(
            accessible_depths, self.data.potential_phosphorus_uptake, self.data.root_depth,
            self.data.phosphorus_distro_param
        )
        self.data.unmet_phosphorus_demands = NitrogenIncorporation.determine_layer_nutrient_demands(
            self.data.layer_phosphorus_potentials, accessible_phosphates
        )
        self.data.phosphorus_requests = NitrogenIncorporation.determine_layer_nutrient_uptake(
            self.data.unmet_phosphorus_demands, self.data.layer_phosphorus_potentials, accessible_phosphates
        )
        self.data.actual_phosphorus_uptakes = NitrogenIncorporation.determine_layer_extracted_resource(
            self.data.phosphorus_requests, accessible_phosphates
        )
        self.extend_phosphate_uptakes_to_full_profile()
        self.extract_phosphorus_from_soil_layers(layer_phosphates)
        self.tally_total_phosphorus_uptake()

    # ---- member functions (setters, internal utility, call sub-routines) ----
    def shift_phosphorus_time(self) -> None:
        """copies the current phosphorus value to previous_phosphorus (for use between time steps)"""
        self.data.previous_phosphorus = self.data.phosphorus

    def find_deepest_accessible_soil_layer(self, depths: List[float]) -> None:
        """evaluates the accessibility of layers in the soil profile by plant roots

        Args:
            depths: the maximum depth of each soil layer

        Details: gets the total number of soil layers, the deepest layer accessible to the roots,
        and the number of layers that remain inaccessible to the plant.
        """
        self.data.total_soil_layers = len(depths)
        self.data.accessible_soil_layers = NitrogenIncorporation.determine_deepest_accessible_layer(
            self.data.root_depth, depths
        )
        self.data.inaccessible_soil_layers = max(len(depths) - self.data.accessible_soil_layers, 0)

    def access_layers(self, layer_list: List[float]) -> List[float]:
        """utility function that removes any inaccessible layers from a list

        Args:
            layer_list: a list containing a value for each layer of the soil profile

        Returns: a trimmed resource list with an element for each soil layer that is accessible to the plant's roots
        """
        return layer_list[0:self.data.accessible_soil_layers]

    def extend_phosphate_uptakes_to_full_profile(self) -> None:
        """determines the actual phosphorus uptakes for the full soil profile, not just accessible layers

        Details: zeros are appended to the list of phosphorus uptakes for each inaccessible soil layer
        """
        if self.data.inaccessible_soil_layers > 0:
            self.data.actual_phosphorus_uptakes += [0] * self.data.inaccessible_soil_layers

    def extract_phosphorus_from_soil_layers(self, layer_phosphates: List[float]) -> None:
        """extracts phosphorus from the soil profile by layer.

        Args:
            layer_phosphates: a list of phosphates in each layer of the soil profile, from which phosphates will be
            extracted by the plant.

        Details: the layer_phosphates list is updated in place. Actual phosphorus uptake values are subtracted from
        each layer
        """
        layer_phosphates[:] = [max(src - snk, 0) for src, snk in zip(layer_phosphates,
                                                                     self.data.actual_phosphorus_uptakes)]

    def tally_total_phosphorus_uptake(self) -> None:
        """determines total phosphorus extracted from soil by summing actual uptake from each layer"""
        self.data.total_phosphorus_uptake = sum(self.data.actual_phosphorus_uptakes)
