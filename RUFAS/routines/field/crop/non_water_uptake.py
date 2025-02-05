from abc import ABC
from typing import Optional

from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.crop.nutrient_uptake import NutrientUptake
from RUFAS.routines.field.soil.soil_data import SoilData


class NonWaterUptake(NutrientUptake, ABC):
    """
    Manages non-water uptakes in crops.

    Parameters
    ----------
    crop_data : Optional[CropData], optional
        An instance of `CropData` containing crop specifications and attributes.
        Defaults to a new instance of `CropData` if not provided.
    nutrient_distro_param : float, default 10.0
        Nutrient uptake distribution parameter (unitless).
    nutrient_shapes : Optional[List[float]], default None
        Shape coefficients for nitrogen uptake equations (unitless).
    previous_nutrient: Optional[float], default None
        Nutrient in biomass on the previous day (kg/ha).
    potential_nutrient_uptake : Optional[float], default None
        Potential nutrient uptake under ideal conditions (kg/ha).
    layer_nutrient_potentials : Optional[float], default None
        Potential nutrient uptake from each soil layer (kg/ha).
    unmet_nutrient_demands : Optional[float], default None
        Unmet nutrient demands by overlaying soil layers (kg/ha).
    nutrient_requests : Optional[float], default None
        Nutrient requested from each soil layer (kg/ha).
    actual_nutrient_uptakes : Optional[List[float]], default None
        Actual nutrient uptake from each soil layer (kg/ha).
    total_nutrient_uptake : Optional[float], default None
        Total nutrient uptake by the plant (kg/ha).

    Attributes
    ----------
    nutrient_distro_param : float
        Nutrient uptake distribution parameter (unitless).
    nutrient_shapes : Optional[List[float]]
        Shape coefficients for nutrient uptake equations (unitless).
    previous_nutrient : Optional[float]
        Nutrient in biomass on the previous day (kg/ha).
    potential_nutrient_uptake : Optional[float]
        Potential nutrient uptake under ideal conditions (kg/ha).
    layer_nutrient_potentials : Optional[float]
        Potential nutrient uptake from each soil layer (kg/ha).
    unmet_nutrient_demands : Optional[float]
        Unmet nutrient demands by overlaying soil layers (kg/ha).
    nutrient_requests : Optional[float]
        Nutrient requested from each soil layer (kg/ha).
    actual_nutrient_uptakes : Optional[List[float]]
        Actual nutrient uptake from each soil layer (kg/ha).
    total_nutrient_uptake : Optional[float]
        Total nutrient uptake by the plant (kg/ha).

    """

    def __init__(
        self,
        crop_data: Optional[CropData],
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
        super().__init__(crop_data)
        self.nutrient_distro_param = nutrient_distro_param
        self.nutrient_shapes = nutrient_shapes
        self.previous_nutrient = previous_nutrient
        self.potential_nutrient_uptake = potential_nutrient_uptake
        self.layer_nutrient_potentials = layer_nutrient_potentials
        self.unmet_nutrient_demands = unmet_nutrient_demands
        self.nutrient_requests = nutrient_requests
        self.actual_nutrient_uptakes = actual_nutrient_uptakes
        self.total_nutrient_uptake = total_nutrient_uptake

    def uptake_main_process(self, soil_data: SoilData, nutrient_name: str, soil_layer_attr: str) -> None:
        """
        Generic nutrient uptake routine that extracts nutrient from the soil and updates crop_data.
        """

        layer_depths = soil_data.get_vectorized_layer_attribute("bottom_depth")
        layer_nutrient = soil_data.get_vectorized_layer_attribute(soil_layer_attr)

        self.shift_nutrient_time(getattr(self.crop_data, nutrient_name))
        self.nutrient_shapes = self.determine_nutrient_shape_parameters(
            self.crop_data.half_mature_heat_fraction,
            self.crop_data.mature_heat_fraction,
            getattr(self.crop_data, f"emergence_{nutrient_name}_fraction"),
            getattr(self.crop_data, f"half_mature_{nutrient_name}_fraction"),
            getattr(self.crop_data, f"mature_{nutrient_name}_fraction"),
        )

        optimal_fraction = self.determine_optimal_nutrient_fraction(
            self.crop_data.heat_fraction,
            getattr(self.crop_data, f"emergence_{nutrient_name}_fraction"),
            getattr(self.crop_data, f"mature_{nutrient_name}_fraction"),
            self.nutrient_shapes[0],
            self.nutrient_shapes[1],
        )
        setattr(self.crop_data, f"optimal_{nutrient_name}_fraction", optimal_fraction)

        optimal_nutrient = self.determine_optimal_nutrient(optimal_fraction, self.crop_data.biomass)
        setattr(self.crop_data, f"optimal_{nutrient_name}", optimal_nutrient)

        if optimal_nutrient - self.previous_nutrient < 0:
            self.potential_nutrient_uptake = 0
        else:
            self.potential_nutrient_uptake = self.determine_potential_nutrient_uptake(
                optimal_nutrient,
                self.previous_nutrient,
                getattr(self.crop_data, f"mature_{nutrient_name}_fraction"),
                self.crop_data.biomass_growth_max,
            )

        self.uptake_nutrient(layer_nutrient, layer_depths)
        soil_data.set_vectorized_layer_attribute(soil_layer_attr, layer_nutrient)

    def uptake_nutrient(self, layer_nutrient: list[float], layer_depths: list[float]) -> None:
        """
        Conducts steps necessary to uptake nutrient from soil.

        Parameters
        ----------
        layer_nutrient : List[float]
            Nutrients contained in each soil layer; updated in place.
        layer_depths : List[float]
            The lowest depth of each soil layer.

        Notes
        -----
        After the actual nutrient uptake is calculated for each accessible soil layer, that amount is removed
        from the layer_nutrient list given as input to the function.

        """
        self.find_deepest_accessible_soil_layer(layer_depths)
        accessible_depths = self.access_layers(layer_depths)
        accessible_nitrates = self.access_layers(layer_nutrient)
        self.layer_nutrient_potentials = self.determine_layer_nutrient_uptake_potential(
            accessible_depths,
            self.potential_nutrient_uptake,
            self.crop_data.root_depth,
            self.nutrient_distro_param,
        )
        self.unmet_nutrient_demands = self.determine_layer_nutrient_demands(
            self.layer_nutrient_potentials, accessible_nitrates
        )
        self.nutrient_requests = self.determine_layer_nutrient_uptake(
            self.unmet_nutrient_demands,
            self.layer_nutrient_potentials,
            accessible_nitrates,
        )

        self.actual_nutrient_uptakes = self.determine_layer_extracted_resource(
            self.nutrient_requests, accessible_nitrates
        )

        self.extend_nutrient_uptakes_to_full_profile(self.actual_nutrient_uptakes)
        self.extract_nutrient_from_soil_layers(layer_nutrient, self.actual_nutrient_uptakes)
        self.total_nutrient_uptake = self.tally_total_nutrient_uptake(self.actual_nutrient_uptakes)

    def shift_nutrient_time(self, nutrient: float) -> None:
        """Copies the current nutrient value to previous_nitrogen (for use between time steps)."""
        self.previous_nutrient = nutrient
