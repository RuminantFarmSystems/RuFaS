from math import exp
from typing import List, Optional

from RUFAS.biophysical.field.crop.crop_data import CropData
from RUFAS.biophysical.field.crop.nutrient_uptake import NutrientUptake
from RUFAS.biophysical.field.soil.soil_data import SoilData


class WaterUptake(NutrientUptake):
    """
    This module is responsible for all water uptake routines for a crop in a day.

    Parameters
    ----------
    crop_data : CropData, optional
        An instance of `CropData` containing specific crop parameters and states. If not provided, a default
        instance with generic crop parameters is created.
    water_distro_parameter : float, default 10
        Water-use distribution parameter governing water-uptake from the soil (unitless).
    potential_water_uptakes : Optional[List[float]], default None
        The maximum amount of water to be potentially taken up by a crop, from each soil layer (mm).
    water_compensation_factor : float, default 0.01
        Factor that determines the ability of a plant to draw water from deeper layers when demands are not met
        (unitless). 0 indicates no water can be drawn from deeper than expected and 1 indicates that any and all water
        can be drawn from deeper layers.
    unmet_water_demands : Optional[List[float]], default None
        Cumulative water demands not met by all previous layers (mm).
    actual_water_uptakes : Optional[List[float]], default None
        The actual amount of water to be removed from the soil (mm).

    Attributes
    ----------
    crop_data : CropData
        Stores and provides access to crop-related data influencing root development, including parameters
        like root depth, growth rates, and environmental conditions affecting root expansion.
    water_distro_parameter : float
        Water-use distribution parameter governing water-uptake from the soil (unitless).
    potential_water_uptakes : Optional[List[float]]
        The maximum amount of water to be potentially taken up by a crop, from each soil layer (mm).
    water_compensation_factor : float
        Factor that determines the ability of a plant to draw water from deeper layers when demands are not met
        (unitless). 0 indicates no water can be drawn from deeper than expected and 1 indicates that any and all water
        can be drawn from deeper layers.
    unmet_water_demands : Optional[List[float]]
        Cumulative water demands not met by all previous layers (mm).
    actual_water_uptakes : Optional[List[float]]
        The actual amount of water to be removed from the soil (mm).

    References
    ----------
    "Water Uptake By Plants" section of SWAT (5:2.2.1)

    """

    def __init__(
        self,
        crop_data: Optional[CropData] = None,
        water_distro_parameter: float = 10,
        potential_water_uptakes: Optional[List[float]] = None,
        water_compensation_factor: float = 0.01,
        unmet_water_demands: Optional[List[float]] = None,
        actual_water_uptakes: Optional[List[float]] = None,
    ):
        super().__init__(crop_data)
        self.water_distro_parameter = water_distro_parameter
        self.potential_water_uptakes = potential_water_uptakes
        self.water_compensation_factor = water_compensation_factor
        self.unmet_water_demands = unmet_water_demands
        self.actual_water_uptakes = actual_water_uptakes

    def uptake(self, soil_data: SoilData) -> None:
        """
        Main method that conducts all water uptake routines for a crop in a day.

        Parameters
        ----------
        soil_data : SoilData
            object tracking soil, from which water will be extracted.

        """
        top_depths = soil_data.get_vectorized_layer_attribute("top_depth")
        bottom_depths = soil_data.get_vectorized_layer_attribute("bottom_depth")
        water_availabilities = soil_data.get_vectorized_layer_attribute("water_content")
        water_capacities = soil_data.get_vectorized_layer_attribute("available_water_capacity")
        wilting_points = soil_data.get_vectorized_layer_attribute("wilting_point_content")

        self.potential_water_uptakes = self._find_stratified_max_water_uptakes(
            root_depth=self.crop_data.root_depth,
            max_transpiration=self.crop_data.max_transpiration,
            upper_depths=top_depths,
            lower_depths=bottom_depths,
            water_distro_parameter=self.water_distro_parameter,
        )
        self.unmet_water_demands = self.determine_layer_nutrient_demands(
            uptake_potentials=self.potential_water_uptakes,
            nutrient_availabilities=water_availabilities,
        )
        self.potential_water_uptakes = self._adjust_water_uptakes(
            potential_uptakes=self.potential_water_uptakes,
            unmet_demands=self.unmet_water_demands,
            uptake_compensation=self.water_compensation_factor,
        )
        self.potential_water_uptakes = self._reduce_efficiency_of_uptake(
            potential_uptakes=self.potential_water_uptakes,
            water_availabilities=water_availabilities,
            available_capacities=water_capacities,
        )
        self.actual_water_uptakes = self._take_up_water(
            potential_uptakes=self.potential_water_uptakes,
            water_availabilities=water_availabilities,
            wilting_points=wilting_points,
        )

        self.extract_water_from_soil(soil_data)

        self.crop_data.water_uptake = self.tally_total_nutrient_uptake(self.actual_water_uptakes)
        self.crop_data.cumulative_water_uptake += self.crop_data.water_uptake

    def extract_water_from_soil(self, soil_data: SoilData) -> None:
        """
        Transfers the current day's water uptake from soil layers to the crop.

        Parameters
        ----------
        soil_data : SoilData
            the object that tracks soil properties, from which to extract water.

        Raises
        ------
        Exception
            If the lengths of `soil_data.soil_layers` and `self.actual_water_uptakes` aren't equal.

        Notes
        -----
        The module removes the smaller of the previously calculated "actual uptake" and the available
        water in each layer. The actual uptake is updated, if relevant, and the equivalent amount is removed from the
        layers in the SoilData object.

        """
        if len(soil_data.soil_layers) != len(self.actual_water_uptakes):
            raise Exception("actual_water_uptakes should be the same length as the number of soil layers")

        available_water = soil_data.get_vectorized_layer_attribute("water_content")
        zipped = zip(available_water, self.actual_water_uptakes)
        extracts = [min(avail, request) for avail, request in zipped]
        zipped = zip(available_water, extracts)
        leftovers = [avail - extract for avail, extract in zipped]
        soil_data.set_vectorized_layer_attribute("water_content", leftovers)
        self.actual_water_uptakes = extracts

    @classmethod
    def _take_up_water(
        cls,
        potential_uptakes: List[float],
        water_availabilities: List[float],
        wilting_points: List[float],
    ) -> List[float]:
        """
        Calculates the actual water taken up by the plant for each soil layer.

        Returns
        -------
        uptakes: list[float]
            the actual water uptake from each layer of soil (mm)

        Raises
        ------
        Exception
            If the lengths of `potential_uptakes`, `water_availabilities`, and `wilting_points` are not all equal.

        Notes
        -----
        This method is a wrapper that applies _determine_actual_layer_uptake() to each layer.

        """
        if not len(potential_uptakes) == len(water_availabilities) == len(wilting_points):
            raise Exception("potential_uptakes, water_availabilities, and wilting_points must be of equal length")

        zipped = zip(potential_uptakes, water_availabilities, wilting_points)
        return [cls._determine_actual_layer_uptake(pot, avail, wilt) for pot, avail, wilt in zipped]

    @staticmethod
    def _determine_actual_layer_uptake(potential: float, available_water: float, wilting_point_water: float) -> float:
        """
        Calculates the actual water taken up by the plant for a soil layer.

        Parameters
        ----------
        potential : float
            the (adjusted and corrected) potential water uptake for a soil layer on the current day (mm)
        available_water : float
            the water available in a soil layer (mm)
        wilting_point_water : float
            the water content of the layer at the wilting point (mm)

        Returns
        -------
        uptake : float
            the actual water that the plant will uptake from the layer (mm)

        """
        return min(potential, available_water - wilting_point_water)

    @staticmethod
    def _reduce_efficiency_of_uptake(
        potential_uptakes: List[float],
        water_availabilities: List[float],
        available_capacities: List[float],
    ) -> List[float]:
        """
        Returns the potential water uptake for each layer after correcting for availability-dependent uptake
        efficiency.

        Parameters
        ----------
        potential_uptakes : list[float]
            The unadjusted potential water uptakes for each soil layer (mm).
        water_availabilities : list[float]
            The crop's water availabilities for each soil layer (mm).
        available_capacities : float
            Available water capacity for each soil layer (mm).

        Returns
        -------
        corrected_potentials : list[float]
            A list of corrected potential water that can be taken up from each layer by the crop on the current day.

        Raises
        ------
        Exception
            If `potential_uptakes`, `water_availabilities`, and `available_capacities` are not all equal lengths.

        Notes
        -----
        This method is a wrapper that applies _correct_layer_for_efficiency() to each layer.

        """
        if not len(potential_uptakes) == len(water_availabilities) == len(available_capacities):
            raise Exception("potential_uptakes, water_availabilities, and available_capacities must be of equal length")

        zipped = zip(potential_uptakes, water_availabilities, available_capacities)
        return [WaterUptake._correct_layer_for_efficiency(pot, avail, cap) for pot, avail, cap in zipped]

    @staticmethod
    def _correct_layer_for_efficiency(
        potential_uptake: float, available_water: float, available_capacity: float
    ) -> float:
        """
        Adjusts the potential water uptake from a layer by the uptake efficiency that is concentration-dependent.

        Parameters
        ----------
        potential_uptake : float
            The (adjusted) potential water uptake from this layer by the crop on the current day (mm).
        available_water : float
            The amount of water actual available for uptake in this layer on the current day (mm).
        available_capacity : float
            Available water capacity (not already holding water) for this layer on the current day (mm).

        Returns
        -------
        corrected_potential: float
            The maximum water able to be taken up from this layer, based on the initial concentration of water in the
            soil layer (mm).

        References
        ----------
        SWAT 5:2.2.4, 5:2.2.5

        """
        if available_water < available_capacity * 0.25:
            fraction = available_water / (0.25 * available_capacity)
            return potential_uptake * exp(5 * (fraction - 1))
        # else
        return potential_uptake

    @staticmethod
    def _adjust_water_uptakes(
        potential_uptakes: List[float],
        unmet_demands: List[float],
        uptake_compensation: float,
    ) -> List[float]:
        """
        Adjusts the potential water uptakes for each layer based on drawing from deeper layers when possible.

        Parameters
        ----------
        potential_uptakes : list[float]
            The unadjusted potential water uptakes for each soil layer (mm).
        unmet_demands : list[float]
            The crop's water demands for each soil layer (mm).
        uptake_compensation : float
            Water uptake compensation factor: the proportion of a crop's water demand from a given layer that can be
            drawn from the underlying layer when insufficient water exists in the desired layer.

        Returns
        -------
        adjusted : list[float]
            The adjusted potential water to be taken up from each layer (mm).

        Raises
        ------
        Exception
            If the lengths of `potential_uptakes` and `unmet_demands` are not equal.

        References
        ----------
        SWAT 5:2.2.3

        """
        if not len(potential_uptakes) == len(unmet_demands):
            raise Exception("potential_uptakes and unmet_demands must be the same length.")

        adjusted = [uptake + (demand * uptake_compensation) for uptake, demand in zip(potential_uptakes, unmet_demands)]

        return adjusted

    @staticmethod
    def _find_stratified_max_water_uptakes(
        root_depth: float,
        max_transpiration: float,
        water_distro_parameter: float,
        upper_depths: List[float],
        lower_depths: List[float],
    ) -> List[float]:
        """
        Calculates the crop's maximum water uptake from each soil layer during the current day.

        Parameters
        ----------
        root_depth : float
            The current depth of the crop root development (mm).
        max_transpiration : float
            The maximum potential water lost to crop transpiration for the current day (mm).
        water_distro_parameter : float
            The water-use distribution parameter of the crop (unitless).
        upper_depths : list[float]
            Depths to the top of each soil layer (mm).
        lower_depths : list[float]
            Depths to the bottom of each soil layer (mm).

        Returns
        -------
        potential_uptakes : list[float]
            The crop's maximum potential water uptake for each soil layer (mm) during the current day.

        Raises
        ------
        Exception
            If the lengths of `upper_depths` and `lower_depths` are not equal.

        References
        ----------
        SWAT 5:2.2.2

        """
        if len(upper_depths) != len(lower_depths):
            raise Exception("upper_depths and lower_depths must be the same length")

        potential_uptakes = []
        for upper, lower in zip(upper_depths, lower_depths):
            top_potential = WaterUptake._determine_max_water_uptake_to_depth(
                root_depth, upper, max_transpiration, water_distro_parameter
            )
            bottom_potential = WaterUptake._determine_max_water_uptake_to_depth(
                root_depth, lower, max_transpiration, water_distro_parameter
            )
            potential_uptakes.append(bottom_potential - top_potential)

        return potential_uptakes

    @staticmethod
    def _determine_max_water_uptake_to_depth(
        root_depth: float,
        depth: float,
        max_transpiration: float,
        water_distro_parameter: float,
    ) -> float:
        """
        Calculate the amount of maximum amount water that can possibly be taken up by the plant under ideal
        conditions.

        Parameters
        ----------
        root_depth : float
            Current depth of root roots (mm).
        depth : float
            Depth from the soil surface (mm).
        max_transpiration : float
            Maximum transpiration possible for the plant during the current day (mm).
        water_distro_parameter : float
            Water use distribution parameter (unitless).

        Returns
        -------
        water : float
            Maximum amount of water potentially taken up by the plant (mm).

        References
        ----------
        SWAT 5:2.2.1

        """
        if root_depth <= 0:
            return 0

        term1 = max_transpiration / (1 - exp(-water_distro_parameter))
        term2 = 1 - exp(-water_distro_parameter * depth / root_depth)
        return term1 * term2
