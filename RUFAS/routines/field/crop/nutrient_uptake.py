from bisect import bisect
from math import exp
from typing import Optional

from RUFAS.output_manager import OutputManager
from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.soil.soil_data import SoilData


class NutrientUptake:
    def __int__(self, crop_data: Optional[CropData], soil_data: Optional[SoilData]):
        self.crop_data = crop_data or CropData()
        self.soil_Data = soil_data or SoilData()

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
    def determine_potential_nutrient_uptake(
        demand: float,
        nutrient_start: float,
        mature_nutrient_fraction: float,
        max_growth: float,
    ) -> float:  # pseudocode: C.5.B.3
        """
        Calculates the potential nutrient uptake for the day.

        Parameters
        ----------
        demand : float
            The maximum or optimal nitrogen uptake of the plant on a given day (kg/ha).
        nutrient_start : float
            Nitrogen biomass at the end of the previous day (kg/ha).
        mature_nutrient_fraction : float
            Nitrogen fraction at plant maturity (unitless).
        max_growth : float
            Maximum potential biomass the plant can gain on a given day (kg/ha).

        Returns
        -------
        float
            The potential nitrogen uptake for the day (kg/ha).

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
            "class": NutrientUptake.__class__.__name__,
            "function": NutrientUptake.determine_layer_extracted_resource.__name__,
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

    @staticmethod
    def _determine_deepest_accessible_layer(root_depth: float, layer_bounds: list[float]) -> int:
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
                "class": NutrientUptake.__class__.__name__,
                "function": NutrientUptake._determine_deepest_accessible_layer.__name__,
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
            represents the depth to the bottom of the layer.
        total_demand : float
            The total nitrogen demand of the plant, indicating how much nitrogen the plant needs to meet its growth
            requirements (kg/ha).
        root_depth : float
            The current depth of the plant's roots, determining which soil layers are accessible for nitrogen uptake
            (mm).
        nutrient_distribution_parameter : float
            A parameter that influences the distribution of nitrogen uptake across the accessible soil layers, affecting
            how uptake is allocated among the layers (unitless).

        Returns
        -------
        list[float]
            A list of potential nitrogen uptake values from each layer, with the uptake from inaccessible layers set to
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
            "class": NutrientUptake.__class__.__name__,
            "function": NutrientUptake.determine_layer_nutrient_uptake_potential.__name__,
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
            cls._determine_nitrogen_uptake_to_depth(total_demand, x, root_depth, nutrient_distribution_parameter)
            for x in layer_bounds
        ]
        boundary_nutrient.insert(0, 0)
        layer_nitrogen = [below - above for below, above in zip(boundary_nutrient[1:], boundary_nutrient)]
        return layer_nitrogen

    @staticmethod
    def _determine_nitrogen_uptake_to_depth(
        demand: float,
        depth: float,
        root_depth: float,
        nutrient_distribution_parameter: float,
    ) -> float:
        """
        Calculates the potential nitrogen uptake from the soil surface to a specified depth.

        Parameters
        ----------
        demand : float
            The current nitrogen demand of the plant (kg/ha).
        depth : float
            The depth (in the same units as root_depth, typically centimeters or meters) to which nitrogen uptake is
            calculated (mm).
        root_depth : float
            The current depth of the plant's roots (mm).
        nutrient_distribution_parameter : float
            The nitrogen uptake distribution parameter affecting how uptake is allocated with depth.

        Returns
        -------
        float
            The potential amount of nitrogen that can be taken up from the soil surface to the specified depth (kg/ha).

        References
        ----------
        SWAT 5:2.3.6, 5:2.3.24

        """
        info_map = {
            "class": NutrientUptake.__class__.__name__,
            "function": NutrientUptake._determine_nitrogen_uptake_to_depth.__name__,
        }
        om = OutputManager()
        if nutrient_distribution_parameter == 0:
            om.add_error(
                "Invalid nitrogen_distribution_parameter.",
                "Received invalid value 0 for nitrogen_distribution_parameter. 0 nitrogen_distribution_parameter"
                " will lead to exp(0) calculation.",
                info_map,
            )
            raise ValueError("nitrogen_distribution_parameter cannot equal 0")
        if root_depth <= 0:
            return 0
        else:
            first_term = demand / (1 - exp(-nutrient_distribution_parameter))
            second_term = 1 - exp(-nutrient_distribution_parameter * (depth / root_depth))
            return first_term * second_term
