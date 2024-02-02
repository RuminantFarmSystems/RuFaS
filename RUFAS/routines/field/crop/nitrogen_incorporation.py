from math import log, exp
from bisect import bisect
from typing import List, Optional
from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.soil.soil_data import SoilData


class NitrogenIncorporation:
    """
    Manages nitrogen incorporation in crops.

    Parameters
    ----------
    crop_data : Optional[CropData], optional
        An instance of `CropData` containing crop specifications and attributes.
        Defaults to a new instance of `CropData` if not provided.

    Attributes
    ----------
    data : CropData
        Reference to the provided `CropData` instance or a new default instance.

    References
    ----------
    'Nitrogen Uptake' section (5:2.3.1) of the SWAT model.

    """
    def __init__(self, crop_data: Optional[CropData] = None):
        self.data = crop_data or CropData()  # initialize with defaults, if not given

    # ---- wrapper functions (main routines) ----
    def incorporate_nitrogen(self, soil_data: SoilData) -> None:
        """
        Main nitrogen incorporation function that runs all nitrogen processes and stores nitrogen as biomass.

        Parameters
        ----------
        soil_data : SoilData
            The SoilData object that tracks soil properties and nitrogen content.

        Notes
        -----
        Calling this function executes all nitrogen incorporation routines. It calculates the amount of nitrogen
        the plant desires based on its current growth stage and the available nitrogen in the soil. The function
        then extracts nitrogen from the accessible soil profile. If there's any unmet nitrogen demand, the plant
        may attempt to fix atmospheric nitrogen. The nitrogen from both extraction and fixation is then added to
        the plant's biomass, contributing to its growth.

        """
        layer_depths = soil_data.get_vectorized_layer_attribute('bottom_depth')
        layer_nitrates = soil_data.get_vectorized_layer_attribute("nitrate_content")
        soil_water_factor = soil_data.soil_water_factor
        # TODO: soil_water_factor should be vectorized (methods need updating) instead of just using the average.
        #   That will require refactoring the subroutines. - GitHub Issue #450

        self.shift_nitrogen_time()
        self.data.nitrogen_shapes = self.determine_nutrient_shape_parameters(
            self.data.half_mature_heat_fraction, self.data.mature_heat_fraction, self.data.emergence_nitrogen_fraction,
            self.data.half_mature_nitrogen_fraction, self.data.mature_nitrogen_fraction
        )
        self.data.optimal_nitrogen_fraction = self.determine_optimal_nutrient_fraction(
            self.data.heat_fraction, self.data.emergence_nitrogen_fraction, self.data.mature_nitrogen_fraction,
            self.data.nitrogen_shapes[0], self.data.nitrogen_shapes[1]
        )
        self.data.optimal_nitrogen = self.determine_optimal_nutrient(
            self.data.optimal_nitrogen_fraction, self.data.biomass
        )
        if self.data.optimal_nitrogen - self.data.previous_nitrogen < 0:
            self.data.potential_nitrogen_uptake = 0
        else:
            self.data.potential_nitrogen_uptake = self.determine_potential_nutrient_uptake(
                self.data.optimal_nitrogen, self.data.previous_nitrogen, self.data.mature_nitrogen_fraction,
                self.data.biomass_growth_max
            )
        self.uptake_nitrogen(layer_nitrates, layer_depths)
        soil_data.set_vectorized_layer_attribute("nitrate_content", layer_nitrates)
        # TODO: the above line is a temporary solution - should be changed with GitHub Issue #450
        total_accessible_nitrates = sum(self.access_layers(layer_nitrates))
        self.try_fixation(total_accessible_nitrates, soil_water_factor)
        # TODO: fixing nitrogen does not increase biomass. Why not?
        self.data.nitrogen = self.determine_stored_nutrient(
            self.data.total_nitrogen_uptake, self.data.nitrogen, self.data.fixed_nitrogen
        )

    def uptake_nitrogen(self, layer_nitrates: List[float], layer_depths: List[float]) -> None:
        """
        Conducts steps necessary to uptake nitrogen from soil.

        Parameters
        ----------
        layer_nitrates : List[float]
            Nitrates contained in each soil layer; updated in place.
        layer_depths : List[float]
            The lowest depth of each soil layer.

        Notes
        -----
        After the actual nitrogen uptake is calculated for each accessible soil layer, that amount is removed
        from the layer_nitrates list given as input to the function.

        """
        self.find_deepest_accessible_soil_layer(layer_depths)
        accessible_depths = self.access_layers(layer_depths)
        accessible_nitrates = self.access_layers(layer_nitrates)
        self.data.layer_nitrogen_potentials = self.determine_layer_nutrient_uptake_potential(
            accessible_depths, self.data.potential_nitrogen_uptake, self.data.root_depth,
            self.data.nitrogen_distro_param)
        self.data.unmet_nitrogen_demands = self.determine_layer_nutrient_demands(
            self.data.layer_nitrogen_potentials, accessible_nitrates)
        self.data.nitrogen_requests = self.determine_layer_nutrient_uptake(
            self.data.unmet_nitrogen_demands, self.data.layer_nitrogen_potentials, accessible_nitrates)
        self.data.actual_nitrogen_uptakes = self.determine_layer_extracted_resource(
            self.data.nitrogen_requests, accessible_nitrates)
        self.extend_nitrate_uptakes_to_full_profile()
        self.extract_nitrogen_from_soil_layers(layer_nitrates)
        self.tally_total_nitrogen_uptake()

    # ---- member functions (setters, internal utility, call sub-routines) ----
    def shift_nitrogen_time(self) -> None:
        """
        Copies the current nitrogen value to previous_nitrogen (for use between time steps).

        """
        self.data.previous_nitrogen = self.data.nitrogen

    def find_deepest_accessible_soil_layer(self, depths: List[float]) -> None:
        """
        Evaluates the accessibility of layers in the soil profile by plant roots.

        Parameters
        ----------
        depths : List[float]
            The maximum depth of each soil layer.

        Notes
        -----
        This method determines the total number of soil layers, identifies the deepest layer accessible to the roots,
        and calculates the number of layers that remain inaccessible to the plant.

        """
        self.data.total_soil_layers = len(depths)
        self.data.accessible_soil_layers = self.determine_deepest_accessible_layer(
            self.data.root_depth, depths)
        self.data.inaccessible_soil_layers = max(len(depths) - self.data.accessible_soil_layers, 0)

    def access_layers(self, layer_list: List[float]) -> List[float]:
        """
        Utility function that removes any inaccessible layers from a list.

        This method filters the input list to include only the layers of the soil profile that are accessible
        to the plant's roots, based on the plant's root depth and the soil layer depths.

        Parameters
        ----------
        layer_list : List[float]
            A list containing a value for each layer of the soil profile.

        Returns
        -------
        List[float]
            A trimmed list with an element for each soil layer that is accessible to the plant's roots.

        """
        return layer_list[0:self.data.accessible_soil_layers]

    def extend_nitrate_uptakes_to_full_profile(self) -> None:
        """
        Determines the actual nitrogen uptakes for the full soil profile, not just the accessible layers.

        Notes
        -----
        Zeros are appended to the list of nitrogen uptakes for each inaccessible soil layer, indicating no nitrogen
        uptake from those layers.

        """
        if self.data.inaccessible_soil_layers > 0:
            self.data.actual_nitrogen_uptakes += [0] * self.data.inaccessible_soil_layers

    def extract_nitrogen_from_soil_layers(self, layer_nitrates: List[float]) -> None:
        """
        Extracts nitrogen from the soil profile by layer.

        Parameters
        ----------
        layer_nitrates : List[float]
            A list of nitrates (in units such as kg/ha) present in each layer of the soil profile, from which nitrates
            will be extracted by the plant.

        Notes
        -----
        The `layer_nitrates` list is updated in place. Actual nitrogen uptake values, calculated by another method,
        are subtracted from the nitrate content of each corresponding soil layer.

        """
        layer_nitrates[:] = [max(src - snk, 0) for src, snk in zip(layer_nitrates, self.data.actual_nitrogen_uptakes)]

    def tally_total_nitrogen_uptake(self) -> None:
        """determines total nitrogen extracted from soil by summing actual uptake from each layer"""
        self.data.total_nitrogen_uptake = sum(self.data.actual_nitrogen_uptakes)

    def try_fixation(self, total_accessible_nitrates: float, soil_water_factor: float) -> None:
        """
        Attempts to fix nitrogen if the plant is capable of nitrogen fixation.

        Parameters
        ----------
        total_accessible_nitrates : float
            The total amount of nitrates accessible to the plant's roots (kg/ha).
        soil_water_factor : float
            A factor representing the availability of water in the soil, affecting the plant's ability to fix nitrogen
            (unitless).

        Notes
        -----
        If the plant species is a nitrogen fixer, this method simulates the fixation of atmospheric nitrogen, enhancing
        the nitrogen content available to the plant. If the plant is not a nitrogen fixer, no action is taken, and the
        method does not affect the plant or soil properties. The humorous note implies that non-nitrogen fixing plants
        do not adversely affect themselves when this method is called.

        """
        if self.data.is_nitrogen_fixer:
            self.update_fixation_attributes(total_accessible_nitrates)
            self.fix_nitrogen(soil_water_factor)
        else:
            self.data.fixed_nitrogen = 0

    def update_fixation_attributes(self, total_accessible_nitrates: float) -> None:
        """
        Updates attributes necessary for nitrogen fixation.

        Parameters
        ----------
        total_accessible_nitrates : float
            The total nitrates accessible to the plant's roots.

        """
        self.data.nitrate_factor = self._determine_nitrate_factor(total_accessible_nitrates)
        self.data.fixation_stage_factor = self._determine_fixation_stage_factor(
            self.data.heat_fraction
        )

    def fix_nitrogen(self, water_factor: float) -> None:
        """
        Fixes nitrogen, based on any remaining demand not met by actual uptake.

        Parameters
        ----------
        water_factor : float
            A factor representing the availability of water in the soil, affecting the efficiency of nitrogen fixation
            (unitless).

        """
        unmet_demand = self.data.potential_nitrogen_uptake - self.data.total_nitrogen_uptake
        if unmet_demand > 0:
            self.data.fixed_nitrogen = self._determine_fixed_nitrogen(
                unmet_demand,
                stage_factor=self.data.fixation_stage_factor,
                water_factor=water_factor,
                nitrate_factor=self.data.nitrate_factor
            )
        else:
            self.data.fixed_nitrogen = 0

    # ---- static methods ----
    @staticmethod
    def determine_nutrient_shape_parameters(half_mature_heat_fraction: float, mature_heat_fraction: float,
                                            emergence_nutrient_fraction: float, half_mature_nutrient_fraction: float,
                                            mature_nutrient_fraction: float) -> List[float]:
        """
        Calculates the shape coefficients for the nitrogen fraction equation.

        Parameters
        ----------
        half_mature_heat_fraction : float
            PHU (Potential Heat Units) fraction at half-maturity.
        mature_heat_fraction : float
            PHU fraction at full maturity.
        emergence_nutrient_fraction : float
            Nitrogen fraction at emergence.
        half_mature_nutrient_fraction : float
            Nitrogen fraction at half-maturity.
        mature_nutrient_fraction : float
            Nitrogen fraction at maturity.

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
        if mature_heat_fraction == half_mature_heat_fraction:  # leads to divide by 0
            raise ValueError("half_mature_heat_fraction must not equal mature_heat_fraction")
        # 1st shape parameter
        log_half = NitrogenIncorporation._determine_shape_log(
            heat_fraction=half_mature_heat_fraction, nitrogen_fraction=half_mature_nutrient_fraction,
            mature_nitrogen_fraction=mature_nutrient_fraction, emergence_nitrogen_fraction=emergence_nutrient_fraction
        )

        assumed_near_mature_nutrient_fraction_difference = 0.00001
        adjusted_near_mature_nutrient_fraction = mature_nutrient_fraction + \
            assumed_near_mature_nutrient_fraction_difference
        log_full = NitrogenIncorporation._determine_shape_log(
            heat_fraction=mature_heat_fraction, nitrogen_fraction=adjusted_near_mature_nutrient_fraction,
            mature_nitrogen_fraction=mature_nutrient_fraction, emergence_nitrogen_fraction=emergence_nutrient_fraction
        )
        s2 = (log_half - log_full) / (mature_heat_fraction - half_mature_heat_fraction)
        # second shape parameter
        log_term = NitrogenIncorporation._determine_shape_log(
            heat_fraction=half_mature_heat_fraction, nitrogen_fraction=half_mature_nutrient_fraction,
            mature_nitrogen_fraction=mature_nutrient_fraction, emergence_nitrogen_fraction=emergence_nutrient_fraction
        )
        s1 = log_term + s2 * half_mature_heat_fraction
        return [s1, s2]

    @staticmethod
    def _determine_shape_log(heat_fraction: float, nitrogen_fraction: float, mature_nitrogen_fraction: float,
                             emergence_nitrogen_fraction: float) -> float:  # pseudocode: C.5.A.1, C.5.A.2
        """
        Calculate the logarithmic component of the shape coefficient formulae for nitrogen uptake.

        Parameters
        ----------
        heat_fraction : float
            PHU (Potential Heat Units) fraction of interest.
        nitrogen_fraction : float
            Nitrogen fraction of interest at a specific point in the growth cycle.
        mature_nitrogen_fraction : float
            Nitrogen fraction at maturity, indicating the nitrogen level when the plant is fully matured.
        emergence_nitrogen_fraction : float
            Nitrogen fraction at emergence, indicating the initial nitrogen level when the plant emerges.

        Returns
        -------
        float
            The logarithmic term of the nitrogen shape coefficients, crucial for calculating the shape coefficients
            used in nitrogen uptake modeling (unitless).

        Raises
        ------
        ValueError
            If any of the nitrogen or heat fractions are outside the range of 0 to 1.
            If `emergence_nitrogen_fraction` is equivalent to `mature_nitrogen_fraction`.
            If `nitrogen_fraction` is equivalent to `emergence_nitrogen_fraction` or `mature_nitrogen_fraction`.
            If `nitrogen_fraction` is greater than or equal to `emergence_nitrogen_fraction`.
            If `nitrogen_fraction` is 0.
            If `heat_fraction` is 0.
            If the calculated denominator is greater than 1.

        References
        ----------
        SWAT 5:2.3.2, 5:2.3.3, 5:2.3.20, 5:2.3.21

        """
        # throw an error if any parameters do not satisfy [0-1]
        if nitrogen_fraction < 0 or nitrogen_fraction > 1 or heat_fraction < 0 or heat_fraction > 1 or \
                mature_nitrogen_fraction < 0 or mature_nitrogen_fraction > 1 or \
                emergence_nitrogen_fraction < 0 or emergence_nitrogen_fraction > 1:
            frac_error_msg = "nitrogen_fraction, heat_fraction, mature_nitrogen_fraction, and" + \
                             " emergence_nitrogen_fraction must all be between 0 and 1"
            raise ValueError(frac_error_msg)
        # raise other errors  # TODO: perhaps rather than throwing errors, we should set values to sensible edge case?
        if emergence_nitrogen_fraction == mature_nitrogen_fraction:  # leads to divide by zero
            raise ValueError("emergence_nitrogen_fraction must not be equivalent to mature_nitrogen_fraction")
        if nitrogen_fraction == emergence_nitrogen_fraction:  # leads to divide by zero
            raise ValueError("nitrogen_fraction must not be equivalent to emergence_nitrogen_fraction")
        if nitrogen_fraction == mature_nitrogen_fraction:  # leads to log(0)
            raise ValueError("nitrogen_fraction must not be equivalent to mature_nitrogen_fraction")
        if nitrogen_fraction > emergence_nitrogen_fraction or \
                nitrogen_fraction == emergence_nitrogen_fraction:  # leads to ln(-y) or divide by 0
            raise ValueError("nitrogen_fraction must be less than emergence_nitrogen_fraction")
        if nitrogen_fraction == 0:  # leads to ln(0)
            raise ValueError("nitrogen_fraction must be greater than 0")
        if heat_fraction == 0:
            raise ValueError("heat_fraction must be greater than 0")

        # calculate first component of formula
        denominator = 1 - ((nitrogen_fraction - mature_nitrogen_fraction) /
                           (emergence_nitrogen_fraction - mature_nitrogen_fraction))

        # additional check
        if denominator > 1:  # leads to log(-y)
            raise ValueError("the quantity (nitrogen_fraction - mature_nitrogen_fraction) /" +
                             " (emergence_nitrogen_fraction - mature_nitrogen_fraction)" +
                             "is negative. \nIs nitrogen_fraction < mature_nitrogen_fraction or" +
                             " emergence_nitrogen_fraction < mature_nitrogen_fraction?")
        # final results
        return log((heat_fraction / denominator) - heat_fraction)

    @staticmethod
    def determine_optimal_nutrient_fraction(heat_fraction: float, emergence_nutrient_fraction: float,
                                            mature_nutrient_fraction: float, shape1: float,
                                            shape2: float) -> float:
        """
        Calculates the optimal fraction of nitrogen in the plant biomass on a given day.

        Parameters
        ----------
        heat_fraction : float
            Fraction of total potential heat units (PHU fraction) accumulated to date.
        emergence_nutrient_fraction : float
            Expected fraction of plant biomass comprised of nitrogen at plant emergence.
        mature_nutrient_fraction : float
            Nitrogen fraction at maturity.
        shape1 : float
            First nitrogen uptake shape parameter.
        shape2 : float
            Second nitrogen uptake shape parameter.

        Returns
        -------
        float
            The calculated optimal nitrogen fraction in the plant biomass for the given day.

        References
        ----------
        SWAT Reference: Equations 5:2.3.1, 5:2.3.19

        """
        ndiff = emergence_nutrient_fraction - mature_nutrient_fraction
        e_term = exp(shape1 + (shape2 * heat_fraction))
        brackets = 1 - (heat_fraction / (heat_fraction + e_term))
        return (ndiff * brackets) + mature_nutrient_fraction

    @staticmethod
    def determine_optimal_nutrient(fraction: float, whole: float) -> float:  # pseudocode: C.5.B.2
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
    def determine_potential_nutrient_uptake(demand: float, nutrient_start: float, mature_nutrient_fraction: float,
                                            max_growth: float) -> float:  # pseudocode: C.5.B.3
        """
        Calculates the potential nitrogen uptake for the day.

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

    @staticmethod
    def determine_deepest_accessible_layer(root_depth: float, layer_bounds: List[float]) -> int:
        """
        Determines the deepest soil layer that is accessible to roots.

        Parameters
        ----------
        root_depth : float
            The root depth of the plant, indicating how deep the roots extend into the soil (mm).
        layer_bounds : List[float]
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
            raise ValueError("root_depth cannot be less than zero")
        elif root_depth == 0.0:
            return 0
        else:
            insert_position = bisect(layer_bounds, root_depth)
            deepest_layer = len(layer_bounds)
            return min(insert_position + 1, deepest_layer)

    @staticmethod
    def determine_layer_nutrient_uptake_potential(layer_bounds: List[float], total_demand: float, root_depth: float,
                                                  nutrient_distribution_parameter: float) -> List[float]:
        """
        Calculates the potential nitrogen uptake from each soil layer based on plant demand and root depth.

        Parameters
        ----------
        layer_bounds : List[float]
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
        List[float]
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
        # check that boundaries are in ascending order
        sorted_boundaries = layer_bounds.copy()
        sorted_boundaries.sort()
        if sorted_boundaries != layer_bounds:
            raise ValueError("boundaries must be in ascending order (deeper layers follow shallower ones)")
        # check that there aren't duplicates (each layer should have a unique depth)
        if len(layer_bounds) != len(set(layer_bounds)):
            raise ValueError("multiple soil boundaries cannot have the same depths. Remove the redundant layer?")
        # calculate results
        boundary_nitrogen = [NitrogenIncorporation._determine_nitrogen_uptake_to_depth(total_demand, x, root_depth,
                                                                                       nutrient_distribution_parameter)
                             for x in layer_bounds]  # N at each boundary
        boundary_nitrogen.insert(0, 0)  # 0 N uptake at soil surface
        layer_nitrogen = [below - above for below, above in
                          zip(boundary_nitrogen[1:], boundary_nitrogen)]  # subtract previous layer
        return layer_nitrogen

    @staticmethod
    def _determine_nitrogen_uptake_to_depth(demand: float, depth: float, root_depth: float,
                                            nitrogen_distribution_parameter: float) -> float:  # pseudocode: C.5.C.1
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
        nitrogen_distribution_parameter : float
            The nitrogen uptake distribution parameter affecting how uptake is allocated with depth.

        Returns
        -------
        float
            The potential amount of nitrogen that can be taken up from the soil surface to the specified depth (kg/ha).

        References
        ----------
        SWAT 5:2.3.6, 5:2.3.24

        """
        # error checks
        if nitrogen_distribution_parameter == 0:
            raise ValueError("nitrogen_distribution_parameter cannot equal 0")
        # calculate results
        if root_depth <= 0:
            return 0
        else:
            first_term = demand / (1 - exp(-nitrogen_distribution_parameter))
            second_term = 1 - exp(-nitrogen_distribution_parameter * (depth / root_depth))
            return first_term * second_term

    @staticmethod
    def determine_layer_nutrient_demands(uptake_potentials: List[float],
                                         nutrient_availabilities: List[float]) -> List[float]:
        """
        Calculates the demand for a nutrient from each soil layer.

        Parameters
        ----------
        uptake_potentials : List[float]
            Maximum uptake of the nutrient by the plant from each soil layer.
        nutrient_availabilities : List[float]
            Available amount of the nutrient in each soil layer.

        Returns
        -------
        List[float]
            Demands for the nutrient from each soil layer.

        References
        ----------
        pseudocode: C.5.C.5

        """
        layer_delta = [desired - available for desired, available in zip(uptake_potentials, nutrient_availabilities)]
        layer_demand = [sum(layer_delta[:i]) for i in range(len(layer_delta))]  # cumulative sum, starting at 0
        return [max(val, 0) for val in layer_demand]  # results constrained to zero

    @staticmethod
    def determine_layer_nutrient_uptake(layer_demands: List[float], layer_uptake_potentials: List[float],
                                        layer_nutrient: List[float]) -> List[float]:  # pseudocode: C.5.C.4
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
        # ensure all list inputs are the same length
        if len(layer_uptake_potentials) != len(layer_demands) or len(layer_uptake_potentials) != len(layer_nutrient):
            raise ValueError("layer_potential, layer_demand, and layer_nitrate must be the same length")
        # calculate results
        layer_desired = [potential + demand for potential, demand in zip(layer_uptake_potentials, layer_demands)]
        return [min(desired, nitrate) for desired, nitrate in zip(layer_desired, layer_nutrient)]

    @staticmethod
    def determine_layer_extracted_resource(requests: List[float], sources: List[float]) -> List[float]:
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
        if len(requests) != len(sources):
            raise ValueError("requests and sources should be the same length")
        return [NitrogenIncorporation._determine_extracted_resource(req, src) for req, src in zip(requests, sources)]

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

    # TODO: method signature
    @staticmethod
    def _determine_nitrate_factor(total_accessible_nitrates: float) -> float:
        """
        Calculates soil nitrate factor.

        Parameters
        ----------
        total_accessible_nitrates : float
            Total nitrates available in the soil layers accessible to roots (kg nitrate / ha).

        Returns
        -------
        float
            The soil nitrate factor, in the range [0.0, 1.0].

        References
        ----------
        SWAT Theoretical documentation equations 5:2.3.15, 5:2.3.16, 5:2.3.17

        Notes
        -----
        Equation 5:2.3.16 in the SWAT Theoretical documentation (and associated SWAT code in the file nfix.f) is
        seemingly wrong. This equation originates from the EPIC model (see line 31 of NFIX.f90). Also note that in EPIC,
        the total accessible nitrates in the soil profile are divided by the amount of residue (`RD(JKK)`), which RuFaS
        does not do.

        """
        if total_accessible_nitrates <= 100:
            return 1
        elif total_accessible_nitrates <= 300:
            return 1.5 - (0.005 * total_accessible_nitrates)
        else:
            return 0

    @staticmethod
    def _determine_fixation_stage_factor(heat_fraction: float) -> float:
        """
        Calculates the fixation symbiotic growth stage factor.

        Parameters
        ----------
        heat_fraction : float
            The accumulated fraction of potential heat units (PHU).

        Returns
        -------
        float
            The growth stage factor for symbiotic organisms involved in nitrogen fixation (unitless).

        Notes
        -----
        The symbiotic organisms that fix nitrogen exist at different densities depending upon the age of the plant. This
        growth stage factor reflects the density and activity level of these symbiotic organisms relative to the plant's
        growth stage.

        References
        ----------
        SWAT 2:2.3.10 - 2:2.3.14

        """
        # piece-wise function:
        if heat_fraction <= 0.15:
            return 0

        elif heat_fraction <= 0.3:
            return (6.67 * heat_fraction) - 1

        elif heat_fraction <= 0.55:
            return 1

        elif heat_fraction <= 0.75:
            return 3.75 - (5 * heat_fraction)

        else:
            return 0

    @staticmethod
    def _determine_fixed_nitrogen(demand: float, stage_factor: float, water_factor: float,
                                  nitrate_factor: float) -> float:
        """
        Calculates the amount of nitrogen fixed by a plant.

        Parameters
        ----------
        demand : float
            Nitrogen demand not met by uptake from soil (kg/ha).
        stage_factor : float
            Growth stage factor, ranging from 0 to 1 (unitless).
        water_factor : float
            Soil water factor, ranging from 0 to 1 (unitless).
        nitrate_factor : float
            Soil nitrate factor, ranging from 0 to 1 (unitless).

        Returns
        -------
        float
            The amount of nitrogen added to plant biomass through fixation, capped at the demand (kg/ha).

        References
        ----------
        SWAT 5:2.3.9

        """
        if not 0 <= stage_factor <= 1:
            raise ValueError("stage_factor must be between 0 and 1")
        if not 0 <= water_factor <= 1:
            raise ValueError("water_factor must be between 0 and 1")
        if not 0 <= nitrate_factor <= 1:
            raise ValueError("nitrate_factor must be between 0 and 1")

        fixed = demand * stage_factor * min(water_factor, nitrate_factor, 1)
        return min(fixed, demand)

    @staticmethod
    def determine_stored_nutrient(uptake: float, previous: float, fixed: float) -> float:  # C.5.E.1
        """
        Calculates the mass of the nutrient stored in plant material after the current day's growth cycle.

        Parameters
        ----------
        uptake : float
            The mass of the nutrient taken up by the plant on the current day (kg/ha).
        previous : float
            The nutrient mass stored in the plant at the end of the previous day (kg/ha).
        fixed : float
            The mass of nutrient fixed by the plant on the current day, applicable only to nitrogen (kg/ha).

        Returns
        -------
        float
            The total mass of the nutrient in the plant at the end of the current day (kg/ha).

        """
        return previous + uptake + fixed
