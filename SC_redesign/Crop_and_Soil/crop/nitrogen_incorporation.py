from math import log, exp
from bisect import bisect
from typing import List, Optional
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

"""
This module is based upon the 'Nitrogen Uptake" section (5:2.3.1) of of the SWAT model documentation
"""


class NitrogenIncorporation:
    def __init__(self, crop_data: Optional[CropData] = None):
        self.data = crop_data or CropData()  # initialize with defaults, if not given

    # ---- wrapper functions (main routines) ----
    def incorporate_nitrogen(self, soil_data: SoilData) -> None:
        """main nitrogen incorporation function - runs all nitrogen processes and stores nitrogen as biomass

        Args:
            soil_data: the SoilData object that tracks soil properties

        Details: calling this function will execute all nitrogen incorporation routines. It determines the amount of
        nitrogen desired by the plant, extracts nitrogen from the accessible soil profile, and tries to fix nitrogen
        for any unmet demand. Nitrogen from extraction and fixation are added to plant biomass.
        """
        # TODO: @isgotkowitz, would you double check that these are the correct layer attributes? If so, we should
        #   be able to delete the attributes in `SoilData` (but not in the `LayerData`s)
        layer_depths = soil_data.get_vectorized_layer_attribute('bottom_depth')
        layer_nitrates = soil_data.get_vectorized_layer_attribute("nitrate")
        soil_water_factor = soil_data.soil_water_factor  # should this be vectorized as well?

        self.shift_nitrogen_time()
        self.data.nitrogen_shapes = self.determine_nutrient_shape_parameters(
            self.data.half_mature_heat_fraction, self.data.mature_heat_fraction, self.data.emergence_nitrogen_fraction,
            self.data.half_mature_nitrogen_fraction, self.data.near_mature_nitrogen_fraction,
            self.data.mature_nitrogen_fraction
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
        soil_data.set_vectorized_layer_attribute("nitrate", layer_nitrates)
        # TODO: the above line is a temporary solution - should be changed with GitHub Issue #450
        total_accessible_nitrates = sum(self.access_layers(layer_nitrates))
        self.try_fixation(total_accessible_nitrates, soil_water_factor)
        # TODO: fixing nitrogen does not increase biomass. Why not?
        self.data.nitrogen = NitrogenIncorporation.determine_stored_nutrient(
            self.data.total_nitrogen_uptake, self.data.nitrogen, self.data.fixed_nitrogen
        )

    def uptake_nitrogen(self, layer_nitrates: List[float], layer_depths: List[float]):
        """conducts steps necessary to uptake nitrogen from soil

        Args:
            layer_nitrates: nitrates contained in each soil layer; updated in place
            layer_depths: the lowest depth of each soil layer.

        Details: after the actual nitrogen uptake is calculated for each accessible soil layer, that amount is removed
        from the layer_nitrates list given as input to the function.
        """
        self.find_deepest_accessible_soil_layer(layer_depths)
        accessible_depths = self.access_layers(layer_depths)
        accessible_nitrates = self.access_layers(layer_nitrates)
        self.data.layer_nitrogen_potentials = NitrogenIncorporation.determine_layer_nutrient_uptake_potential(
            accessible_depths, self.data.potential_nitrogen_uptake, self.data.root_depth,
            self.data.nitrogen_distro_param)
        self.data.unmet_nitrogen_demands = NitrogenIncorporation.determine_layer_nutrient_demands(
            self.data.layer_nitrogen_potentials, accessible_nitrates)
        self.data.nitrogen_requests = NitrogenIncorporation.determine_layer_nutrient_uptake(
            self.data.unmet_nitrogen_demands, self.data.layer_nitrogen_potentials, accessible_nitrates)
        self.data.actual_nitrogen_uptakes = NitrogenIncorporation.determine_layer_extracted_resource(
            self.data.nitrogen_requests, accessible_nitrates)
        self.extend_nitrate_uptakes_to_full_profile()
        self.extract_nitrogen_from_soil_layers(layer_nitrates)
        self.tally_total_nitrogen_uptake()

    # ---- member functions (setters, internal utility, call sub-routines) ----
    def shift_nitrogen_time(self) -> None:
        """copies the current nitrogen value to previous_nitrogen (for use between time steps)"""
        self.data.previous_nitrogen = self.data.nitrogen

    def find_deepest_accessible_soil_layer(self, depths: List[float]) -> None:
        """evaluates the accessibility of layers in the soil profile by plant roots

        Args:
            depths: the maximum depth of each soil layer

        Details: gets the total number of soil layers, the deepest layer accessible to the roots,
        and the number of layers that remain inaccessible to the plant.
        """
        self.data.total_soil_layers = len(depths)
        self.data.accessible_soil_layers = NitrogenIncorporation.determine_deepest_accessible_layer(
            self.data.root_depth, depths)
        self.data.inaccessible_soil_layers = max(len(depths) - self.data.accessible_soil_layers, 0)

    def access_layers(self, layer_list: List[float]) -> List[float]:
        """utility function that removes any inaccessible layers from a list

        Args:
            layer_list: a list containing a value for each layer of the soil profile

        Returns: a trimmed resource list with an element for each soil layer that is accessible to the plant's roots
        """
        return layer_list[0:self.data.accessible_soil_layers]

    def extend_nitrate_uptakes_to_full_profile(self) -> None:
        """determines the actual nitrogen uptakes for the full soil profile, not just accessible layers

        Details: zeros are appended to the list of nitrogen uptakes for each inaccessible soil layer
        """
        if self.data.inaccessible_soil_layers > 0:
            self.data.actual_nitrogen_uptakes += [0] * self.data.inaccessible_soil_layers

    def extract_nitrogen_from_soil_layers(self, layer_nitrates: List[float]) -> None:
        """extracts nitrogen from the soil profile by layer.

        Args:
            layer_nitrates: a list of nitrates in each layer of the soil profile, from which nitrates will be extracted
            by the plant.

        Details: the layer_nitrates list is updated in place. Actual nitrogen uptake values are subtracted from
        each layer
        """
        layer_nitrates[:] = [max(src - snk, 0) for src, snk in zip(layer_nitrates, self.data.actual_nitrogen_uptakes)]

    def tally_total_nitrogen_uptake(self) -> None:
        """determines total nitrogen extracted from soil by summing actual uptake from each layer"""
        self.data.total_nitrogen_uptake = sum(self.data.actual_nitrogen_uptakes)

    def try_fixation(self, total_accessible_nitrates: float, soil_water_factor: float) -> None:
        """tries to fix nitrogen

        Args:
            total_accessible_nitrates: the total nitrates accessible to roots
            soil_water_factor: the soil water factor

        Details: If the plant is a nitrogen fixer, it will fix nitrogen. Otherwise, it will hurt itself in its confusion
        (not really - nothing happens)
        """
        if self.data.is_nitrogen_fixer:
            self.update_fixation_attributes(total_accessible_nitrates)
            self.fix_nitrogen(soil_water_factor)
        else:
            self.data.fixed_nitrogen = 0

    def update_fixation_attributes(self, total_accessible_nitrates: float) -> None:
        """updates attributes necessary for nitrogen fixation
        Args:
            total_accessible_nitrates: the total nitrates accessible to roots
        """
        self.data.nitrate_factor = NitrogenIncorporation._determine_nitrate_factor(total_accessible_nitrates)
        self.data.fixation_stage_factor = NitrogenIncorporation._determine_fixation_stage_factor(
            self.data.heat_fraction
        )

    def fix_nitrogen(self, water_factor: float) -> None:
        """fix nitrogen, based on any remaining demand not met by actual uptake"""
        unmet_demand = self.data.potential_nitrogen_uptake - self.data.total_nitrogen_uptake
        if unmet_demand > 0:
            self.data.fixed_nitrogen = NitrogenIncorporation._determine_fixed_nitrogen(
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
                                            near_mature_nutrient_fraction: float,
                                            mature_nutrient_fraction: float) -> List[float]:
        # pseudocode: C.5.A.1, C.5.A.2
        """
        Description: calculates the shape coefficients for the nitrogen fraction equation

        Args:
            half_mature_heat_fraction: PHU fraction at half-maturity
            mature_heat_fraction: PHU fraction at full-maturity
            emergence_nutrient_fraction: nitrogen fraction at emergence
            half_mature_nutrient_fraction: nitrogen fraction at half-maturity
            near_mature_nutrient_fraction: nitrogen fraction *near* maturity
            mature_nutrient_fraction: nitrogen fraction *at* maturity

        SWAT Reference: Equations 5:2.3.2, 5:2.3.3, 5:2.3.20, 5:2.3.21

        Returns: list of the first and second shape coefficients, respectively
        """
        if mature_heat_fraction == half_mature_heat_fraction:  # leads to divide by 0
            raise ValueError("half_mature_heat_fraction must not equal mature_heat_fraction")
        # 1st shape parameter
        log_half = NitrogenIncorporation._determine_shape_log(
            heat_fraction=half_mature_heat_fraction, nitrogen_fraction=half_mature_nutrient_fraction,
            mature_nitrogen_fraction=mature_nutrient_fraction, emergence_nitrogen_fraction=emergence_nutrient_fraction
        )
        log_full = NitrogenIncorporation._determine_shape_log(
            heat_fraction=mature_heat_fraction, nitrogen_fraction=near_mature_nutrient_fraction,
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
        Description: calculate the log component of shape coefficient formulae

        Args:
            heat_fraction: PHU fraction of interest
            nitrogen_fraction: nitrogen fraction of interest
            mature_nitrogen_fraction: nitrogen fraction at maturity
            emergence_nitrogen_fraction: nitrogen fraction at emergence

        SWAT Reference: Equations 5:2.3.2, 5:2.3.3, 5:2.3.20, 5:2.3.21

        Returns: the log term of nitrogen shape coefficients
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
                                            shape2: float) -> float:  # pseudocode: C.5.B.1
        """
        Description: calculates the optimal fraction of nitrogen in the plant biomass on a given day

        SWAT Reference: Equations 5:2.3.1, 5:2.3.19

        Args:
            heat_fraction: fraction of total potential heat units (PHU fraction) accumulated to date
            emergence_nutrient_fraction: expected fraction of plant biomass comprised of nitrogen (nitrogen fraction) at
                plant emergence
            mature_nutrient_fraction: nitrogen fraction at maturity
            shape1: first nitrogen uptake shape parameter
            shape2: second nitrogen uptake shape parameter
        """
        ndiff = emergence_nutrient_fraction - mature_nutrient_fraction
        e_term = exp(shape1 + (shape2 * heat_fraction))
        brackets = 1 - (heat_fraction / (heat_fraction + e_term))
        return (ndiff * brackets) + mature_nutrient_fraction

    @staticmethod
    def determine_optimal_nutrient(fraction: float, whole: float) -> float:  # pseudocode: C.5.B.2
        """calculate mass of a constituent from the fractional mass of the whole

        Args:
          fraction: proportion of the whole made up of the constituent
          whole: total mass of the whole

        SWAT Reference: Equations 5:2.3.4, 5:2.3.22

        Returns: mass of the constituent
        """
        return fraction * whole

    @staticmethod
    def determine_potential_nutrient_uptake(demand: float, nutrient_start: float, mature_nutrient_fraction: float,
                                            max_growth: float) -> float:  # pseudocode: C.5.B.3
        """
        Description: calculates potential nitrogen uptake for the day

        Args:
            demand: maximum/optimal nitrogen uptake of the plant on a given day
            nutrient_start: nitrogen biomass at the end of the previous day
            mature_nutrient_fraction: nitrogen fraction at maturity
            max_growth: maximum potential biomass the plant can gain on a given day

        SWAT Reference: Equations 5:2.3.5, 5:2.3.23

        Returns: the potential nitrogen uptake for the day
        """
        return min(demand - nutrient_start, 4 * mature_nutrient_fraction * max_growth)

    @staticmethod
    def determine_deepest_accessible_layer(root_depth: float, layer_bounds: List[float]) -> int:
        """
        Description:
            Determines the deepest soil layer that is accessible to roots.

        Args:
            root_depth: the root depth of a plant
            layer_bounds: the depths of the lower boundaries of each soil layer

        Returns:
            an integer indicating the deepest soil layer that the roots can access

            example: return of 1 means only the first layer is accessible (i.e., accessible_depths[:1]) and a return of
            2 means the first and second layers are accessible (i.e., accessible_depths[:2])
        """
        if root_depth <= 0:  # handle no roots
            raise ValueError("root_depth cannot be less than zero")
        else:
            insert_position = bisect(layer_bounds, root_depth)
            deepest_layer = len(layer_bounds)
            return min(insert_position + 1, deepest_layer)

    @staticmethod
    def determine_layer_nutrient_uptake_potential(layer_bounds: List[float], total_demand: float, root_depth: float,
                                                  nutrient_distribution_parameter: float) -> List[float]:
        # pseudocode: C.5.C.2, C.5.C.3
        """
        Description: calculates potential nitrogen uptake from each soil layer

        Args:
            layer_bounds: list of lower boundaries for each soil layer, in ascending order (i.e., increasing depths)
            total_demand: total nitrogen demand of the plant
            root_depth: current depth of the plant roots
            nutrient_distribution_parameter: nitrogen uptake distribution parameter

        Returns: a list of potential nitrogen uptake from each layer
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
        Description: calculates potential nitrogen uptake from the soil surface to a specified depth

        Args:
            demand: the current nitrogen demand
            depth: the depth to which nitrogen uptake is calculated
            root_depth: the current root depth
            nitrogen_distribution_parameter: the nitrogen uptake distribution parameter

        SWAT Reference: Equations 5:2.3.6, 5:2.3.24

        Returns: the potential amount of nitrogen taken up
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
                                         nutrient_availabilities: List[float]) -> List[float]:  # pseudocode: C.5.C.5
        """
        Description: calculates demand for a nutrient of the plant from each soil layer

        Args:
            uptake_potentials: maximum uptake of the nutrient by the plant from each soil layer
            nutrient_availabilities: available amount of the nutrient in each soil layer

        Returns: a list of demands for the nutrient from each soil layer
        """
        layer_delta = [desired - available for desired, available in zip(uptake_potentials, nutrient_availabilities)]
        layer_demand = [sum(layer_delta[:i]) for i in range(len(layer_delta))]  # cumulative sum, starting at 0
        return [max(val, 0) for val in layer_demand]  # results constrained to zero

    @staticmethod
    def determine_layer_nutrient_uptake(layer_demands: List[float], layer_uptake_potentials: List[float],
                                        layer_nutrient: List[float]) -> List[float]:  # pseudocode: C.5.C.4
        """
        Description: calculates nutrient amount uptaken from each soil layer

        Args:
            layer_demands: list of demands from each soil layer not met by the above layers, for the nutrient
            layer_uptake_potentials: list of maximum uptake of the nutrient from each soil layer
            layer_nutrient: list of nutrient amounts present in each soil layer

        SWAT Reference: 5:2.3.1, 5:2.3.2 (see paragraphs below equations 5:2.3.8 and 5:2.3.26)

        Returns: a list of nitrogen mass taken up from each soil layer
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
        Description: calculates the amount of a resource actually extracted from each layer of the soil

        Args:
            requests: desired amount of the resource from each layer
            sources: the pool of available resources in each layer

        SWAT Reference: Equations 5:2.3.8, 5:2.3.26

        Returns: The actual amounts of a resource to be extracted from the soil layers

        """
        if len(requests) != len(sources):
            raise ValueError("requests and sources should be the same length")
        return [NitrogenIncorporation._determine_extracted_resource(req, src) for req, src in zip(requests, sources)]

    @staticmethod
    def _determine_extracted_resource(request: float, source: float) -> float:
        """
        Description: calculates the amount of a resource that can be drawn from a source, based on a request

        Args:
            request: requested amount of the resource
            source: amount of the resource available at the source

        SWAT Reference: Equations 5:2.3.8, 5:2.3.26

        Returns: the amount of the resource to be extracted
        """
        return min(request, max(0.0, source))

    # TODO: method signature
    @staticmethod
    def _determine_nitrate_factor(total_accessible_nitrates: float) -> float:
        """
        Description: calculates soil nitrate factor

        Args:
            total_accessible_nitrates: total nitrates available in the soil layers accessible to roots

        SWAT Reference: Equations 5:2.3.15, 5:2.3.16, 5:2.3.17

        Returns: the nitrate factor
        """
        if total_accessible_nitrates <= 100:
            return 1
        elif total_accessible_nitrates <= 300:
            return 1.5 - (0.0005 * total_accessible_nitrates)
        else:
            return 0

    @staticmethod
    def _determine_fixation_stage_factor(heat_fraction: float) -> float:
        """
        Description: calculates fixation symbiotic growth stage factor

        Args:
            heat_fraction: the accumulated fraction of potential heat units

        SWAT Reference: Equations 2:2.3.10 - 2:2.3.14

        Returns: growth stage factor

        Details: the symbiotic organisms that fix nitrogen exist at different densities depending upon the age of the
            plant. The growth stage factor exemplifies that relationship.
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
        Description: calculate the amount of nitrogen fixed by a plant

        Args:
            demand: nitrogen demand not met by uptake from soil
            stage_factor: growth stage factor [0, 1]
            water_factor: soil water factor [0, 1]
            nitrate_factor: soil nitrate factor [0, 1]

        SWAT Reference: Equation 5:2.3.9

        Returns: the amount of nitrogen added to plant biomass through fixation, capped at demand.
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
        Description: calculates mass of the nutrient stored in plant material after the current day's growth cycle

        Args:
            uptake: the mass of the nutrient taken up by the plant on the current day
            previous: the nutrient mass stored in the plant at the end of the previous day
            fixed: the mass of nutrient fixed by the plant on the current day (only applies to nitrogen)

        Returns: the total mass of the nutrient in the plant at the end of current day
        """
        return previous + uptake + fixed
