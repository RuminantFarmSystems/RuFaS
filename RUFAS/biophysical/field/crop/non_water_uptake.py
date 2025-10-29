from bisect import bisect
from math import exp, log
from typing import Optional

from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.field.crop.crop_data import CropData
from RUFAS.biophysical.field.crop.nutrient_uptake import NutrientUptake
from RUFAS.biophysical.field.soil.soil_data import SoilData


class NonWaterUptake(NutrientUptake):
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
        Shape coefficients for nutrient uptake equations (unitless).
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

        Parameters
        ----------
        soil_data : SoilData
            The SoilData object that tracks soil properties and nutrient content.
        nutrient_name : str
            The name of the nutrient.
        soil_layer_attr : str
            The soil layer attribute of the nutrient.

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
        """Copies the current nutrient value to previous_nutrient (for use between time steps)."""
        self.previous_nutrient = nutrient

    @staticmethod
    def determine_potential_nutrient_uptake(
        demand: float,
        nutrient_start: float,
        mature_nutrient_fraction: float,
        max_growth: float,
    ) -> float:
        """
        Calculates the potential nutrient uptake for the day.

        Parameters
        ----------
        demand : float
            The maximum or optimal nutrient uptake of the plant on a given day (kg/ha).
        nutrient_start : float
            Nutrient biomass at the end of the previous day (kg/ha).
        mature_nutrient_fraction : float
            Nutrient fraction at plant maturity (unitless).
        max_growth : float
            Maximum potential biomass the plant can gain on a given day (kg/ha).

        Returns
        -------
        float
            The potential nutrient uptake for the day (kg/ha).

        References
        ----------
        SWAT 5:2.3.5, 5:2.3.23

        """
        return min(demand - nutrient_start, 4 * mature_nutrient_fraction * max_growth)

    @classmethod
    def determine_layer_extracted_resource(cls, requests: list[float], sources: list[float]) -> list[float]:
        """
        Calculates the amount of a resource actually extracted from each layer of the soil.

        Parameters
        ----------
        requests : List[float]
            Desired amount of the resource from each layer.
        sources : List[float]
            The pool of available resources in each layer.

        Returns
        -------
        List[float]
            The actual amounts of a resource extracted from the soil layers.

        References
        ----------
        SWAT 5:2.3.8, 5:2.3.26

        """
        info_map = {
            "class": cls.__name__,
            "function": cls.determine_layer_extracted_resource.__name__,
        }
        om = OutputManager()
        if len(requests) != len(sources):
            om.add_error(
                "Invalid requests and sources length.",
                f"The length of requests({len(requests)}) and sources({len(sources)}) are unequal.",
                info_map,
            )
            raise ValueError("requests and sources should be the same length")
        return [cls._determine_extracted_resource(req, src) for req, src in zip(requests, sources)]

    @staticmethod
    def _determine_extracted_resource(request: float, source: float) -> float:
        """
        Calculates the amount of a resource that can be drawn from a source, based on a request.

        Parameters
        ----------
        request : float
            Requested amount of the resource (kg/ha).
        source : float
            Amount of the resource available at the source (kg/ha).

        Returns
        -------
        float
            The amount of the resource to be extracted, considering the request and source availability (kg/ha).

        References
        ----------
        SWAT 5:2.3.8, 5:2.3.26

        """
        return min(request, max(0.0, source))

    def find_deepest_accessible_soil_layer(self, depths: list[float]) -> None:
        """
        Evaluates the accessibility of layers in the soil profile by plant roots.

        Parameters
        ----------
        depths : list[float]
            The maximum depth of each soil layer.

        Notes
        -----
        This function determines the total number of soil layers, identifies the deepest layer accessible to the roots,
        and calculates the number of layers that remain inaccessible to the plant. It provides insight into how deep
        the plant can potentially draw nutrients and water from the soil profile.

        """
        self.crop_data.total_soil_layers = len(depths)
        self.crop_data.accessible_soil_layers = self._determine_deepest_accessible_layer(
            self.crop_data.root_depth, depths
        )
        self.crop_data.inaccessible_soil_layers = max(len(depths) - self.crop_data.accessible_soil_layers, 0)

    @classmethod
    def _determine_deepest_accessible_layer(cls, root_depth: float, layer_bounds: list[float]) -> int:
        """
        Determines the deepest soil layer that is accessible to roots.

        Parameters
        ----------
        root_depth : float
            The root depth of the plant, indicating how deep the roots extend into the soil (mm).
        layer_bounds : list[float]
            A list containing the depths (in centimeters or meters) of the lower boundaries of each soil layer.

        Returns
        -------
        int
            An integer indicating the deepest soil layer that the roots can access. For example, a return of 1 means
            only the first layer is accessible (i.e., layer_bounds[:1]), and a return of 2 means the first and second
            layers are accessible (i.e., layer_bounds[:2]).

        Raises
        ------
        ValueError
            Negative root depth is provided.

        Notes
        -----
        This method assumes that if there are no roots (root depth of 0), then none of the soil layers are accessible
        for nutrient uptake by the crop.

        """
        if root_depth < 0.0:
            info_map = {
                "class": cls.__name__,
                "function": cls._determine_deepest_accessible_layer.__name__,
            }
            om = OutputManager()
            om.add_error(
                "Invalid root depth.", f"Root depth must be >= 0, provided root depth is {root_depth}.", info_map
            )
            raise ValueError("root_depth cannot be less than zero")
        elif root_depth == 0.0:
            return 0
        else:
            insert_position = bisect(layer_bounds, root_depth)
            deepest_layer = len(layer_bounds)
            return min(insert_position + 1, deepest_layer)

    def access_layers(self, layer_list: list[float]) -> list[float]:
        """
        Utility function that removes any inaccessible layers from a list.

        This method filters the input list to include only the layers of the soil profile that are accessible
        to the plant's roots, based on the plant's root depth and the soil layer depths.

        Parameters
        ----------
        layer_list : list[float]
            A list containing a value for each layer of the soil profile.

        Returns
        -------
        List[float]
            A trimmed list with an element for each soil layer that is accessible to the plant's roots.

        """
        return layer_list[0 : self.crop_data.accessible_soil_layers]

    @classmethod
    def determine_layer_nutrient_uptake_potential(
        cls,
        layer_bounds: list[float],
        total_demand: float,
        root_depth: float,
        nutrient_distribution_parameter: float,
    ) -> list[float]:
        """
        Calculates the potential nutrient uptake from each soil layer based on plant demand and root depth.

        Parameters
        ----------
        layer_bounds : list[float]
            A list of lower boundaries for each soil layer, in ascending order (i.e., increasing depths). Each entry
            represents the depth to the bottom of the layer (mm).
        total_demand : float
            The total nutrient demand of the plant, indicating how much nutrient the plant needs to meet its growth
            requirements (kg/ha).
        root_depth : float
            The current depth of the plant's roots, determining which soil layers are accessible for nutrient uptake
            (mm).
        nutrient_distribution_parameter : float
            A parameter that influences the distribution of nutrient uptake across the accessible soil layers, affecting
            how uptake is allocated among the layers (unitless).

        Returns
        -------
        list[float]
            A list of potential nutrient uptake values from each layer, with the uptake from inaccessible layers set to
            zero.

        Raises
        ------
        ValueError
            If the boundaries are not in ascending order (deeper layers should follow shallower ones).
            If there are duplicate depths, indicating multiple soil layers at the same depth.

        References
        ----------
        pseudocode: C.5.C.2, C.5.C.3

        """
        info_map = {
            "class": cls.__name__,
            "function": cls.determine_layer_nutrient_uptake_potential.__name__,
        }
        om = OutputManager()
        sorted_boundaries = layer_bounds.copy()
        sorted_boundaries.sort()
        if sorted_boundaries != layer_bounds:
            om.add_error(
                "Invalid layer boundaries order.",
                f"Boundaries must be in ascending order (deeper layers follow shallower ones),"
                f" received {layer_bounds}.",
                info_map,
            )
            raise ValueError("boundaries must be in ascending order (deeper layers follow shallower ones)")

        if len(layer_bounds) != len(set(layer_bounds)):
            om.add_error(
                "Invalid layer boundaries depth.",
                f"Boundaries all have different depth, received {layer_bounds}.",
                info_map,
            )
            raise ValueError("multiple soil boundaries cannot have the same depths. Remove the redundant layer?")

        boundary_nutrient = [
            cls._determine_nutrient_uptake_to_depth(total_demand, x, root_depth, nutrient_distribution_parameter)
            for x in layer_bounds
        ]
        boundary_nutrient.insert(0, 0)
        layer_nutrient = [below - above for below, above in zip(boundary_nutrient[1:], boundary_nutrient)]
        return layer_nutrient

    @classmethod
    def _determine_nutrient_uptake_to_depth(
        cls,
        demand: float,
        depth: float,
        root_depth: float,
        nutrient_distribution_parameter: float,
    ) -> float:
        """
        Calculates the potential nutrient uptake from the soil surface to a specified depth.

        Parameters
        ----------
        demand : float
            The current nutrient demand of the plant (kg/ha).
        depth : float
            The depth (in the same units as root_depth, typically centimeters or meters) to which nutrient uptake is
            calculated (mm).
        root_depth : float
            The current depth of the plant's roots (mm).
        nutrient_distribution_parameter : float
            The nutrient uptake distribution parameter affecting how uptake is allocated with depth.

        Returns
        -------
        float
            The potential amount of nutrient that can be taken up from the soil surface to the specified depth (kg/ha).

        References
        ----------
        SWAT 5:2.3.6, 5:2.3.24

        """
        info_map = {
            "class": cls.__name__,
            "function": cls._determine_nutrient_uptake_to_depth.__name__,
        }
        om = OutputManager()
        if nutrient_distribution_parameter == 0:
            om.add_error(
                "Invalid nutrient_distribution_parameter.",
                "Received invalid value 0 for nutrient_distribution_parameter. 0 nutrient_distribution_parameter"
                " will lead to exp(0) calculation.",
                info_map,
            )
            raise ValueError("nutrient_distribution_parameter cannot equal 0")
        if root_depth <= 0:
            return 0
        else:
            first_term = demand / (1 - exp(-nutrient_distribution_parameter))
            second_term = 1 - exp(-nutrient_distribution_parameter * (depth / root_depth))
            return first_term * second_term

    @staticmethod
    def extract_nutrient_from_soil_layers(layer_nutrients: list[float], actual_nutrient_uptakes: list[float]) -> None:
        """
        Extracts nutrient from the soil profile by layer.

        Parameters
        ----------
        actual_nutrient_uptakes : Optional[List[float]]
            Actual nutrient uptake from each soil layer (kg/ha).
        layer_nutrients : list[float]
            A list of nutrients (in units such as kg/ha) present in each layer of the soil profile, from which nutrients
            will be extracted by the plant.

        Notes
        -----
        The `layer_nutrients` list is updated in place. Actual nutrient uptake values, calculated by another method,
        are subtracted from the nitrate content of each corresponding soil layer.

        """
        layer_nutrients[:] = [max(src - snk, 0) for src, snk in zip(layer_nutrients, actual_nutrient_uptakes)]

    def extend_nutrient_uptakes_to_full_profile(self, actual_nutrient_uptakes: list[float]) -> None:
        """
        Determines the actual nutrient uptakes for the full soil profile, not just the accessible layers.

        Parameters
        ----------
        actual_nutrient_uptakes : Optional[List[float]]
            Actual nutrient uptake from each soil layer (kg/ha).

        Notes
        -----
        Zeros are appended to the list of nutrient uptakes for each inaccessible soil layer, indicating no nutrient
        uptake from those layers.

        """
        if self.crop_data.inaccessible_soil_layers > 0:
            actual_nutrient_uptakes += [0] * self.crop_data.inaccessible_soil_layers

    @classmethod
    def determine_nutrient_shape_parameters(
        cls,
        half_mature_heat_fraction: float,
        mature_heat_fraction: float,
        emergence_nutrient_fraction: float,
        half_mature_nutrient_fraction: float,
        mature_nutrient_fraction: float,
    ) -> list[float]:
        """
        Calculates the shape coefficients for the nutrient fraction equation.

        Parameters
        ----------
        half_mature_heat_fraction : float
            PHU (Potential Heat Units) fraction at half-maturity.
        mature_heat_fraction : float
            PHU fraction at full maturity.
        emergence_nutrient_fraction : float
            Nutrient fraction at emergence.
        half_mature_nutrient_fraction : float
            Nutrient fraction at half-maturity.
        mature_nutrient_fraction : float
            Nutrient fraction at maturity.

        Returns
        -------
        List[float]
            A list containing the first and second shape coefficients, respectively.

        Notes
        -----
        SWAT assumes that the difference between the nutrient fraction near maturity and the nutrient fraction at
        maturity in the crop is equal to 0.00001 (as per SWAT theoretical documentation pages 331 and 336, top
        paragraphs of both). Therefore, the near mature nutrient fraction is adjusted to meet that assumption in this
        calculation.

        References
        ----------
        SWAT 5:2.3.2, 5:2.3.3, 5:2.3.20, 5:2.3.21

        Raises
        ------
        ValueError
            If half_mature_heat_fraction equals mature_heat_fraction.

        """
        if mature_heat_fraction == half_mature_heat_fraction:
            info_map = {
                "class": cls.__name__,
                "function": cls.determine_nutrient_shape_parameters.__name__,
            }
            om = OutputManager()
            om.add_error(
                "A crop's half mature heat fraction and mature heat fraction are equal.",
                f"Half mature heat fraction and mature heat fraction are both {mature_heat_fraction},"
                f" this results in a division by zero error.",
                info_map,
            )
            raise ValueError("half_mature_heat_fraction must not equal mature_heat_fraction")

        log_half = cls._determine_shape_log(
            heat_fraction=half_mature_heat_fraction,
            nutrient_fraction=half_mature_nutrient_fraction,
            mature_nutrient_fraction=mature_nutrient_fraction,
            emergence_nutrient_fraction=emergence_nutrient_fraction,
        )

        assumed_near_mature_nutrient_fraction_difference = 0.00001
        adjusted_near_mature_nutrient_fraction = (
            mature_nutrient_fraction + assumed_near_mature_nutrient_fraction_difference
        )
        log_full = cls._determine_shape_log(
            heat_fraction=mature_heat_fraction,
            nutrient_fraction=adjusted_near_mature_nutrient_fraction,
            mature_nutrient_fraction=mature_nutrient_fraction,
            emergence_nutrient_fraction=emergence_nutrient_fraction,
        )
        s2 = (log_half - log_full) / (mature_heat_fraction - half_mature_heat_fraction)
        log_term = cls._determine_shape_log(
            heat_fraction=half_mature_heat_fraction,
            nutrient_fraction=half_mature_nutrient_fraction,
            mature_nutrient_fraction=mature_nutrient_fraction,
            emergence_nutrient_fraction=emergence_nutrient_fraction,
        )
        s1 = log_term + s2 * half_mature_heat_fraction
        return [s1, s2]

    @classmethod
    def _determine_shape_log(
        cls,
        heat_fraction: float,
        nutrient_fraction: float,
        mature_nutrient_fraction: float,
        emergence_nutrient_fraction: float,
    ) -> float:
        """
        Calculate the logarithmic component of the shape coefficient formulae for nutrient uptake.

        Parameters
        ----------
        heat_fraction : float
            PHU (Potential Heat Units) fraction of interest.
        nutrient_fraction : float
            Nutrient fraction of interest at a specific point in the growth cycle.
        mature_nutrient_fraction : float
            Nutrient fraction at maturity, indicating the nutrient level when the plant is fully matured.
        emergence_nutrient_fraction : float
            Nutrient fraction at emergence, indicating the initial nutrient level when the plant emerges.

        Returns
        -------
        float
            The logarithmic term of the nutrient shape coefficients, crucial for calculating the shape coefficients
            used in nutrient uptake modeling (unitless).

        Raises
        ------
        ValueError
            If any of the nutrient or heat fractions are outside the range of 0 to 1.
            If `emergence_nutrient_fraction` is equivalent to `mature_nutrient_fraction`.
            If `nutrient_fraction` is equivalent to `emergence_nutrient_fraction` or `mature_nutrient_fraction`.
            If `nutrient_fraction` is greater than or equal to `emergence_nutrient_fraction`.
            If `nutrient_fraction` is 0.
            If `heat_fraction` is 0.
            If the calculated denominator is greater than 1.

        References
        ----------
        SWAT 5:2.3.2, 5:2.3.3, 5:2.3.20, 5:2.3.21

        """
        info_map = {
            "class": cls.__name__,
            "function": cls._determine_shape_log.__name__,
        }
        om = OutputManager()
        if (
            nutrient_fraction < 0
            or nutrient_fraction > 1
            or heat_fraction < 0
            or heat_fraction > 1
            or mature_nutrient_fraction < 0
            or mature_nutrient_fraction > 1
            or emergence_nutrient_fraction < 0
            or emergence_nutrient_fraction > 1
        ):
            om.add_error(
                "Received invalid fractional value",
                f"All following values must be in the range (0, 1), received {nutrient_fraction=}, {heat_fraction=}"
                f", {mature_nutrient_fraction=}, {emergence_nutrient_fraction=}.",
                info_map,
            )
            frac_error_msg = (
                "nutrient_fraction, heat_fraction, mature_nutrient_fraction, and"
                + " emergence_nutrient_fraction must all be between 0 and 1"
            )
            raise ValueError(frac_error_msg)
        if emergence_nutrient_fraction == mature_nutrient_fraction:
            om.add_error(
                "A crop's emergence_nutrient_fraction and mature_nutrient_fraction are equal.",
                f"The emergence_nutrient_fraction and mature_nutrient_fraction are both"
                f" {emergence_nutrient_fraction}, this results in a divide by zero error.",
                info_map,
            )
            raise ValueError("emergence_nutrient_fraction must not be equivalent to mature_nutrient_fraction")
        if nutrient_fraction == emergence_nutrient_fraction:
            om.add_error(
                "A crop's emergence_nutrient_fraction and nutrient_fraction are equal.",
                f"The emergence_nutrient_fraction andnutrient_fraction are both"
                f" {emergence_nutrient_fraction}, this results in a divide by zero error.",
                info_map,
            )
            raise ValueError("nutrient_fraction must not be equivalent to emergence_nutrient_fraction")
        if nutrient_fraction == mature_nutrient_fraction:
            om.add_error(
                "A crop's nutrient_fraction and mature_nutrient_fraction are equal.",
                f"The nutrient_fraction and mature_nutrient_fraction are both"
                f" {mature_nutrient_fraction}, this results in a divide by zero error.",
                info_map,
            )
            raise ValueError("nutrient_fraction must not be equivalent to mature_nutrient_fraction")
        if nutrient_fraction > emergence_nutrient_fraction:
            om.add_error(
                "A crop's nutrient_fraction is greater than emergence_nutrient_fraction.",
                f"The nutrient_fraction is greater than mature_nutrient_fraction,"
                f" nutrient_fraction is {mature_nutrient_fraction} and mature_nutrient_fraction is"
                f" {emergence_nutrient_fraction}, this results in ln(-y) calculation.",
                info_map,
            )
            raise ValueError("nutrient_fraction must be less than emergence_nutrient_fraction")
        if nutrient_fraction == 0:
            om.add_error("Invalid nutrient_fraction.", "nutrient_fraction can not be 0.", info_map)
            raise ValueError("nutrient_fraction must be greater than 0")
        if heat_fraction == 0:
            om.add_error("Invalid heat_fraction.", "heat_fraction can not be 0.", info_map)
            raise ValueError("heat_fraction must be greater than 0")

        denominator = 1 - (
            (nutrient_fraction - mature_nutrient_fraction) / (emergence_nutrient_fraction - mature_nutrient_fraction)
        )

        if denominator > 1:
            om.add_error(
                "Invalid value pair for nutrient_fraction and mature_nutrient_fraction or"
                " emergence_nutrient_fraction and mature_nutrient_fraction or both pairs.",
                "the quantity (nutrient_fraction - mature_nutrient_fraction) /"
                " (emergence_nutrient_fraction - mature_nutrient_fraction)"
                f"is negative, which will leads to log(-y) calculation. \nIs nutrient_fraction({nutrient_fraction}) <"
                f" mature_nutrient_fraction({mature_nutrient_fraction}) or"
                f" emergence_nutrient_fraction({emergence_nutrient_fraction}) <"
                f" mature_nutrient_fraction({mature_nutrient_fraction})?",
                info_map,
            )
            raise ValueError(
                "the quantity (nutrient_fraction - mature_nutrient_fraction) /"
                + " (emergence_nutrient_fraction - mature_nutrient_fraction)"
                + "is negative. \nIs nutrient_fraction < mature_nutrient_fraction or"
                + " emergence_nutrient_fraction < mature_nutrient_fraction?"
            )
        return log((heat_fraction / denominator) - heat_fraction)

    @staticmethod
    def determine_optimal_nutrient_fraction(
        heat_fraction: float,
        emergence_nutrient_fraction: float,
        mature_nutrient_fraction: float,
        shape1: float,
        shape2: float,
    ) -> float:
        """
        Calculates the optimal fraction of nutrient in the plant biomass on a given day.

        Parameters
        ----------
        heat_fraction : float
            Fraction of total potential heat units (PHU fraction) accumulated to date.
        emergence_nutrient_fraction : float
            Expected fraction of plant biomass comprised of nutrient at plant emergence.
        mature_nutrient_fraction : float
            Nutrient fraction at maturity.
        shape1 : float
            First nutrient uptake shape parameter.
        shape2 : float
            Second nutrient uptake shape parameter.

        Returns
        -------
        float
            The calculated optimal nutrient fraction in the plant biomass for the given day.

        References
        ----------
        SWAT Reference: Equations 5:2.3.1, 5:2.3.19

        """
        ndiff = emergence_nutrient_fraction - mature_nutrient_fraction
        e_term = exp(shape1 - (shape2 * heat_fraction))
        brackets = 1 - (heat_fraction / (heat_fraction + e_term))
        return (ndiff * brackets) + mature_nutrient_fraction

    @staticmethod
    def determine_optimal_nutrient(fraction: float, whole: float) -> float:
        """
        Calculate the mass of a nutrient as a constituent from the fractional mass of the whole.

        Parameters
        ----------
        fraction : float
            Proportion of the whole made up of the nutrient (unitless).
        whole : float
            Total mass of the whole in which the nutrient is a part (kg/ha).

        Returns
        -------
        float
            Mass of the nutrient as a constituent of the whole (kg/ha).

        References
        ----------
        SWAT 5:2.3.4, 5:2.3.22

        """
        return fraction * whole

    @staticmethod
    def determine_stored_nutrient(uptake: float, previous: float, fixed: float) -> float:
        """
        Calculates the mass of the nutrient stored in plant material after the current day's growth cycle.

        Parameters
        ----------
        uptake : float
            The mass of the nutrient taken up by the plant on the current day (kg/ha).
        previous : float
            The nutrient mass stored in the plant at the end of the previous day (kg/ha).
        fixed : float
            The mass of nutrient fixed by the plant on the current day, applicable only to nutrient (kg/ha).

        Returns
        -------
        float
            The total mass of the nutrient in the plant at the end of the current day (kg/ha).

        """
        return previous + uptake + fixed

    @classmethod
    def determine_layer_nutrient_uptake(
        cls,
        layer_demands: list[float],
        layer_uptake_potentials: list[float],
        layer_nutrient: list[float],
    ) -> list[float]:
        """
        Calculates nutrient amount uptaken from each soil layer.

        Parameters
        ----------
        layer_demands : List[float]
            List of demands for the nutrient from each soil layer not met by the above layers.
        layer_uptake_potentials : List[float]
            List of maximum potential uptake of the nutrient from each soil layer.
        layer_nutrient : List[float]
            List of nutrient amounts available in each soil layer.

        Returns
        -------
        List[float]
            Amount of nutrient mass taken up from each soil layer.

        References
        ----------
        SWAT 5:2.3.1, 5:2.3.2 (see paragraphs below equations 5:2.3.8 and 5:2.3.26)

        """
        info_map = {
            "class": cls.__name__,
            "function": cls.determine_layer_nutrient_uptake.__name__,
        }
        om = OutputManager()
        if len(layer_uptake_potentials) != len(layer_demands) or len(layer_uptake_potentials) != len(layer_nutrient):
            om.add_error(
                "Invalid layer_potential, layer_demand, and layer_nitrate length.",
                "layer_potential, layer_demand, and layer_nitrate length do not have equal length,"
                f"length of layer_potential, layer_demand, and layer_nitrate are"
                f" {len(layer_uptake_potentials)}, {len(layer_demands)} and {len(layer_nutrient)}.",
                info_map,
            )
            raise ValueError("layer_potential, layer_demand, and layer_nitrate must be the same length")
        layer_desired = [potential + demand for potential, demand in zip(layer_uptake_potentials, layer_demands)]
        return [min(desired, nitrate) for desired, nitrate in zip(layer_desired, layer_nutrient)]
