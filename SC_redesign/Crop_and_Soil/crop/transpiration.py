from math import exp
from typing import Optional, List
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from SC_redesign.Crop_and_Soil.crop.nitrogen_incorporation import NitrogenIncorporation
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData

# TODO These functions belone in either water_dynamics.py or as soil process methods


# TODO: these methods do not currently account for whether or not the roots can reach a layer. See Nitrogen module.
class WaterUptake:
    def __init__(self, crop_data: Optional[CropData] = None):
        self.crop_data = crop_data or CropData()

    def uptake_water(self, soil_data: SoilData):
        top_depths = soil_data.get_vectorized_layer_attribute("top_depth")
        bottom_depths = soil_data.get_vectorized_layer_attribute("bottom_depth")
        water_availabilities = soil_data.get_vectorized_layer_attribute("water_content")
        water_capacities = soil_data.get_vectorized_layer_attribute("available_water_capacity")
        wilting_points = soil_data.get_vectorized_layer_attribute("wilting_point_content")

        self.crop_data.potential_water_uptakes = self._find_stratified_max_water_uptakes(
            root_depth=self.crop_data.root_depth, max_transpiration=self.crop_data.max_transpiration,
            upper_depths=top_depths, lower_depths=bottom_depths,
            water_distro_parameter=self.crop_data.water_distro_parameter
        )
        self.data.unmet_water_demands = NitrogenIncorporation.determine_layer_nutrient_demands(
            uptake_potentials=self.crop_data.potential_water_uptakes,
            nutrient_availabilities=water_availabilities
        )
        self.crop_data.potential_water_uptakes = self._adjust_water_uptakes(
            potential_uptakes=self.crop_data.potential_water_uptakes, unmet_demands=self.crop_data.unmet_water_demands,
            uptake_compensation=self.crop_data.water_compensation_factor)
        self.crop_data.potential_water_uptakes = self._reduce_efficiency_of_uptake(
            potential_uptakes=self.crop_data.potential_water_uptakes,
            water_availabilities=water_availabilities,
            available_capacities=water_capacities
        )
        self.crop_data.actual_water_uptakes = self._take_up_water(
            potential_uptakes=self.crop_data.potential_water_uptakes, water_availabilities=water_availabilities,
            wilting_points=wilting_points)

        self.extract_water_from_soil()

    def extract_water_from_soil(self, soil_data: SoilData):
        if len(soil_data.soil_layers) != len(self.crop_data.actual_water_uptakes):
            raise Exception("actual_water_uptakes should be the same length as the number of soil layers")

        available_water = soil_data.get_vectorized_layer_attribute("water_content")
        diffs = [avail - request for avail, request in zip(available_water, self.crop_data.actual_water_uptakes)]



    @staticmethod
    def _take_up_water(potential_uptakes: List[float], water_availabilities: List[float],
                       wilting_points: List[float]) -> List[float]:
        """calculates the actual water taken up by the plant for each soil layer

        This method is a wrapper that applies _determine_actual_layer_uptake() to each layer.

        Returns
        -------
        uptakes: list[float]
            the actual water uptake from each layer of soil (mm)
        """
        if not len(potential_uptakes) == len(water_availabilities) == len(wilting_points):
            raise Exception("potential_uptakes, water_availabilities, and wilting_points must be of equal length")

        zipped = zip(potential_uptakes, water_availabilities, wilting_points)
        return [WaterUptake._determine_actual_layer_uptake(pot, avail, wilt) for pot, avail, wilt in zipped]

    @staticmethod
    def _determine_actual_layer_uptake(potential: float, available_water: float, wilting_point_water: float) -> float:
        """calculates the actual water taken up by the plant for a soil layer.

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
    def _reduce_efficiency_of_uptake(potential_uptakes: List[float], water_availabilities: List[float],
                                     available_capacities: List[float]):
        """Returns the potential water uptake for each layer after correcting for availability-dependent uptake
        efficiency.

        This method is a wrapper that applies _correct_layer_for_efficiency() to each layer.

        Returns
        -------
        corrected_potentials : list[float]
            a list of corrected potential water that can be taken up from each layer by the crop on the current day.
        """
        if not len(potential_uptakes) == len(water_availabilities) == len(available_capacities):
            raise Exception("potential_uptakes, water_availabilities, and available_capacities must be of equal length")

        zipped = zip(potential_uptakes, water_availabilities, available_capacities)
        return [WaterUptake._correct_layer_for_efficiency(pot, avail, cap) for pot, avail, cap in zipped]

    @staticmethod
    def _correct_layer_for_efficiency(potential_uptake: float, available_water: float,
                                      available_capacity: float) -> float:
        """adjusts the potential water uptake from a layer by the uptake efficiency that is concentration-dependent

        SWAT Equation: 5:2.2.4, 5:2.2.5

        Parameters
        ----------
        potential_uptake : float
            the (adjusted) potential water uptake from this layer by the crop on the current day (mm)
        available_water : float
            the amount of water actual available for uptake in this layer on the current day (mm)
        available_capacity : float
            available water capacity (not already holding water) for this layer on the current day (mm)

        Returns
        -------
        corrected_potential: float
            The maximum water able to be taken up from this layer, based on the initial concentration of water in the
            soil layer
        """
        if available_water < available_capacity*0.25:
            fraction = available_water / (0.25 * available_capacity)
            return potential_uptake * exp(5 * (fraction - 1))
        # else
        return potential_uptake

    @staticmethod
    def _adjust_water_uptakes(potential_uptakes: List[float], water_availabilities: List[float],
                              unmet_demands: List[float], uptake_compensation: float):
        """adjusts the potential water uptakes from each layer based by drawing from deeper layeres when possible.

        SWAT equation: 5:2.2.3

        Parameters
        ----------
        potential_uptakes : list[float]
            the unadjusted potential water uptakes for each soil layer (mm)
        unmet_demands : list[float]
            the crop's water demands for each soil layer (mm)
        uptake_compensation : float
            water uptake compensation factor: the proportion of a crop's water demand from a given layer that can be
            drawn from the underlying layer when insufficient water exists in the desired layer.

        Returns
        -------

        """
        if len(potential_uptakes) != len(unmet_demands):
            raise Exception("potential_uptakes and demands must be the same length.")

        adjusted = [uptake + (demand * uptake_compensation) for uptake, demand in zip(potential_uptakes, unmet_demands)]

        return adjusted

    @staticmethod
    def _find_stratified_max_water_uptakes(root_depth: float, max_transpiration: float, water_distro_parameter: float,
                                           upper_depths: List[float], lower_depths: List[float]) -> List[float]:
        """calculates the crop's maximum water uptake from each soil layer during the current day.

        SWAT Equation: 5:2.2.2

        Parameters
        ----------
        root_depth : float
            the current depth of the crop root development (mm)
        max_transpiration : float
            the maximum potential water lost to crop transpiration for the current day (mm)
        water_distro_parameter : float
            the water-use distribution parameter of the crop (unitless)
        upper_depths : list[float]
            depths to the top of each soil layer (mm)
        lower_depths : list[float]
            depths to the bottom of each soil layer (mm)

        Returns
        -------
        potential_uptakes : list[float]
            the crop's maximum potential water uptake for each soil layer (mm) during the current day
        """
        if len(upper_depths) != len(lower_depths):
            raise Exception("upper_depths and lower_depths must be the same length")

        potential_uptakes = []
        for upper, lower in zip(upper_depths, lower_depths):
            top_potential = WaterUptake._determine_max_water_uptake_to_depth(root_depth, upper, max_transpiration,
                                                                             water_distro_parameter)
            bottom_potential = WaterUptake._determine_max_water_uptake_to_depth(root_depth, lower, max_transpiration,
                                                                                water_distro_parameter)
            potential_uptakes.append(bottom_potential - top_potential)

        return potential_uptakes

    @staticmethod
    def _determine_max_water_uptake_to_depth(root_depth: float, depth: float, max_transpiration: float,
                                             water_distro_parameter: float) -> float:
        """Calculate the amount of maximum amount water that can possibly be taken up by the plant under ideal
        conditions.

        SWAT Equation: 5:2.2.1

        Parameters
        ----------
        root_depth : float
            current depth of root roots (mm)
        depth : float
            depth from the soil surface (mm)
        max_transpiration : float
            maximum transpiration possible for the plant during the current day (mm)
        water_distro_parameter : float
            water use distribution parameter (unitless)

        Returns
        -------
        water : float
            maximum amount of water potentially taken up by the plant (mm)
        """
        # TODO: Note that this method is identical to NitrogenIncorporation._determine_nitrogen_uptake_to_depth()
        if root_depth <= 0:
            return 0

        term1 = max_transpiration / (1 - exp(-water_distro_parameter))
        term2 = 1 - exp(-water_distro_parameter * depth / root_depth)
        return term1 * term2


# ------------
