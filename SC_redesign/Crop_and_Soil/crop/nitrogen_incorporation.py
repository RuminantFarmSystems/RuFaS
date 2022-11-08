from math import log, exp

from SC_redesign.Crop_and_Soil.soil.soil import Soil
from bisect import bisect


class NitrogenIncorporation:
    def __init__(self):
        self.emergence_nfrac = 0.04
        self.half_mature_nfrac = 0.03
        self.near_mature_nfrac = 0.02
        self.mature_nfrac = 0.02
        self.half_mature_heatfrac = 0.5
        self.mature_heatfrac = 1.0
        self.heat_fraction = 800
        self.biomass = 12.5
        self.biomass_growth_max = 100
        self.nitrogen = 0
        self.nitrogen_distro_param = 10
        self.root_depth = 0
        self.is_nitrogen_fixer = False

        self.optimal_nitrogen_fraction = None
        self.shapes_nitrogen_uptake = None
        self.optimal_nitrogen = None
        self.previous_nitrogen = None
        self.potential_nitrogen_uptake = None # demand
        self.layer_nitrogen_potentials = None
        self.layer_nitrogen_demands = None
        self.layer_nitrogen_uptakes = None
        self.total_nitrogen_uptake = None
        self.fixed_nitrogen = None
        self.fixation_stage_factor = None
        self.deepest_accessible_layer = None

    def incorporate_nitrogen(self, soil: Soil) -> None:
        """main nitrogen incorporation function - runs all nitrogen processes and stores nitrogen as biomass"""
        self.determine_nitrogen_fraction()
        self.determine_optimal_nitrogen()
        self.determine_potential_nitrogen_uptake()
        self.uptake_nitrogen(soil)
        self.try_fixation()
        self.store_nitrogen_biomass()

    def uptake_nitrogen(self, soil: Soil) -> None:
        self.stratify_potential_nitrogen_uptake(soil.lower_boundaries)
        self.stratify_nitrogen_demand(soil.nitrates)
        self.stratify_nitrogen_uptake(soil.nitrates)
        self.reassess_nitrogen_availability(soil.nitrates)
        self.extract_nitrogen_from_soil(soil)
        # ...

    def determine_nfrac_shape_parameters(self) -> None:
        """obtain the shape parameters for use in calculating nitrogen fraction"""
        self.shapes_nitrogen_uptake = calc_shape_parameters(self.half_mature_heatfrac, self.mature_heatfrac,
                                                            self.emergence_nfrac, self.half_mature_nfrac,
                                                            self.near_mature_nfrac, self.mature_nfrac)

    def determine_nitrogen_fraction(self) -> None:
        """evaluate the plant's nitrogen fraction, using the shape parameters"""
        self.optimal_nitrogen_fraction = calc_nitrogen_fraction(self.heat_fraction, self.emergence_nfrac,
                                                                self.mature_nfrac,
                                                                self.shapes_nitrogen_uptake[0],
                                                                self.shapes_nitrogen_uptake[1])

    def determine_optimal_nitrogen(self) -> None:
        """ determines the optimal nitrogen based on its current biomass and nitrogen fraction"""
        self.optimal_nitrogen = calc_mass_from_fraction(self.optimal_nitrogen_fraction, self.biomass)

    # def shift_nitrogen_time(self) -> None:
    #     self.previous_nitrogen = self.nitrogen

    def determine_potential_nitrogen_uptake(self) -> None:
        if self.optimal_nitrogen - self.previous_nitrogen < 0:
            self.potential_nitrogen_uptake = 0
        else:
            self.potential_nitrogen_uptake = calc_potential_nitrogen_uptake(self.optimal_nitrogen,
                                                                            self.previous_nitrogen,
                                                                            self.mature_nfrac,
                                                                            self.biomass_growth_max)

    def stratify_potential_nitrogen_uptake(self, layer_bounds: list[float]) -> None:
        self.layer_nitrogen_potentials = calc_layer_nitrogen_uptake_potential(layer_bounds,
                                                                              self.potential_nitrogen_uptake,
                                                                              self.root_depth,
                                                                              self.nitrogen_distro_param)

    def stratify_nitrogen_demand(self, layer_nitrates: list[float]) -> None:
        self.layer_nitrogen_demands = calc_layer_nitrogen_demands(self.layer_nitrogen_potentials, layer_nitrates)

    def stratify_nitrogen_uptake(self, layer_nitrates: list[float]) -> None:
        self.layer_nitrogen_uptakes = calc_layer_nitrogen_uptake(self.layer_nitrogen_demands,
                                                                 self.layer_nitrogen_potentials, layer_nitrates)

    def reassess_nitrogen_availability(self, layer_nitrates):
        """
        check that nitrogen uptake requests can be met by the nitrogen pools in the soil layers. This ensures that
        nitrogen that is not available cannot be extracted.
        """
        self.layer_nitrogen_uptakes = calc_layer_extracted_resource(self.layer_nitrogen_uptakes, layer_nitrates)
        self.total_nitrogen_uptake = sum(self.layer_nitrogen_uptakes)

    def extract_nitrogen_from_soil(self, soil: Soil) -> None:  # TODO: better in a separate ResourceTransfer class?
        """extract nitrogen from soil layers"""
        soil.layer_extracted_nitrogen = self.layer_nitrogen_uptakes
        soil.total_extracted_nitrogen = self.total_nitrogen_uptake
        soil.nitrates = [available - drawn for available, drawn in zip(soil.nitrates, self.layer_nitrogen_uptakes)]
        self.nitrogen += self.total_nitrogen_uptake

    def store_nitrogen_biomass(self) -> None:
        """updates the nitrogen biomass stored within a crop at the end of the day's growth cycle"""
        self.nitrogen = calc_stored_nitrogen(self.total_nitrogen_uptake, self.nitrogen, self.fixed_nitrogen)

    def try_fixation(self) -> None:
        if self.is_nitrogen_fixer:
            self.fix_nitrogen()
        else:
            self.fixed_nitrogen = 0

    def determine_fixation_stage_factor(self):
        self.fixation_stage_factor = calc_fixation_stage_factor(self.heat_fraction)

    # TODO: need to make sure that nutrients are only uptaken from accessible root zone and that fixation
    #   only occurs for any **unmet** nitrogen demands
    def fix_nitrogen(self, water_factor: float, nitrate_factor: float) -> None:
        """fix nitrogen, based on any remaining demand not met by uptake"""
        unmet_demand = self.potential_nitrogen_uptake - self.total_nitrogen_uptake
        if unmet_demand > 0:
            self.fixed_nitrogen = calc_fixed_nitrogen(unmet_demand, stage_factor=self.fixation_stage_factor,
                                                      water_factor=water_factor, nitrate_factor=nitrate_factor)
        else:
            self.fixed_nitrogen = 0

    def determine_deepest_accessible_soil_layer(self, depths: list[float]) -> None:
        self.deepest_accessible_layer = calc_deepest_accessible_layer(self.root_depth, depths)
        
    def access_layers(self, resource_profile: list) -> list:
        """
        Details: obtains the list of resources accessible by roots, from a full list of layer resources

        Args:
            resource_profile: a list containing the amount of a resource present in each layer of the soil profile

        Returns: a trimmed resource list with an element for each soil layer that is accessible to the plant's roots
        """
        return resource_profile[slice(self.deepest_accessible_layer)]



# ---- helper functions ----
def calc_nitrogen_fraction(heat_fraction: float, emergence_nfrac: float, mature_nfrac: float, shape1: float,
                           shape2: float) -> float:  # pseudocode: C.5.B.1
    """
    Description: calculates the fraction of nitrogen in the plant biomass on a given day

    Args:
        heat_fraction: fraction of total potential heat units (PHU fraction) accumulated to date
        emergence_nfrac: expected fraction of plant biomass comprised of nitrogen (nitrogen fraction) at plant emergence
        mature_nfrac: nitrogen fraction at maturity
        shape1: first nitrogen uptake shape parameter
        shape2: second nitrogen uptake shape parameter
    """
    ndiff = emergence_nfrac - mature_nfrac
    e_term = exp(shape1 + (shape2 * heat_fraction))
    brackets = 1 - (heat_fraction / (heat_fraction + e_term))
    return (ndiff * brackets) + mature_nfrac


def calc_shape_parameters(half_mature_heatfrac: float, mature_heatfrac: float, emergence_nfrac: float,
                          half_mature_nfrac: float, near_mature_nfrac: float, mature_nfrac: float) -> list[
    float]:  # pseudocode: C.5.A.1, C.5.A.2
    """
    Description: calculates the shape coefficients for the nitrogen fraction equation

    Args:
        half_mature_heatfrac: PHU fraction at half-maturity
        mature_heatfrac: PHU fraction at full-maturity
        emergence_nfrac: nitrogen fraction at emergence
        half_mature_nfrac: nitrogen fraction at half-maturity
        near_mature_nfrac: nitrogen fraction *near* maturity
        mature_nfrac: nitrogen fraction *at* maturity

    Returns: list of the first and second shape coefficients, respectively
    """
    if mature_heatfrac == half_mature_heatfrac:  # leads to divide by 0
        raise ValueError("heatfrac_half must not equal heatfrac_full")
    # 1st shape parameter
    log_half = calc_shape_log(heat_fraction=half_mature_heatfrac, nitrogen_fraction=half_mature_nfrac,
                              mature_nfrac=mature_nfrac, emergence_nfrac=emergence_nfrac)
    log_full = calc_shape_log(heat_fraction=mature_heatfrac, nitrogen_fraction=near_mature_nfrac,
                              mature_nfrac=mature_nfrac, emergence_nfrac=emergence_nfrac)
    s2 = (log_half - log_full) / (mature_heatfrac - half_mature_heatfrac)
    # second shape parameter
    log_term = calc_shape_log(heat_fraction=half_mature_heatfrac, nitrogen_fraction=half_mature_nfrac,
                              emergence_nfrac=emergence_nfrac, mature_nfrac=mature_nfrac)
    s1 = log_term + s2 * half_mature_heatfrac
    return [s1, s2]


def calc_shape_log(heat_fraction: float, nitrogen_fraction: float, mature_nfrac: float,
                   emergence_nfrac: float) -> float:  # pseudocode: C.5.A.1, C.5.A.2
    """
    Description: calculate the log component of shape coefficient formulae

    Args:
        heat_fraction: PHU fraction of interest
        nitrogen_fraction: nitrogen fraction of interest
        mature_nfrac: nitrogen fraction at maturity
        emergence_nfrac: nitrogen fraction at emergence

    Returns: the log term of nitrogen shape coefficients
    """
    # throw an error if any parameters do not satisfy [0-1]
    if nitrogen_fraction < 0 or nitrogen_fraction > 1 or heat_fraction < 0 or heat_fraction > 1 or mature_nfrac < 0 or \
            mature_nfrac > 1 or emergence_nfrac < 0 or emergence_nfrac > 1:
        frac_error_msg = "nitrogen_fraction, heat_fraction, mature_nfrac, and emergence_nfrac" + \
                         "must all be between 0 and 1"
        raise ValueError(frac_error_msg)
    # raise other errors  # TODO: perhaps rather than throwing errors, we should set values to sensible edge case?
    if emergence_nfrac == mature_nfrac:  # leads to divide by zero
        raise ValueError("emergence_nfrac must not be equivalent to mature_nfrac")
    if nitrogen_fraction == emergence_nfrac:  # leads to divide by zero
        raise ValueError("nitrogen_fraction must not be equivalent to emergence_nfrac")
    if nitrogen_fraction == mature_nfrac:  # leads to log(0)
        raise ValueError("nitrogen_fraction must not be equivalent to mature_nfrac")
    if nitrogen_fraction > emergence_nfrac or nitrogen_fraction == emergence_nfrac:  # leads to ln(-y) or divide by 0
        raise ValueError("nitrogen_fraction must be less than emergence_nfrac")
    if nitrogen_fraction == 0:  # leads to ln(0)
        raise ValueError("nitrogen_fraction must be greater than 0")
    if heat_fraction == 0:
        raise ValueError("heat_fraction must be greater than 0")

    # calculate first component of formula
    denominator = 1 - ((nitrogen_fraction - mature_nfrac) / (emergence_nfrac - mature_nfrac))

    # additional check
    if denominator > 1:  # leads to log(-y)
        raise ValueError("the quantity (nitrogen_fraction - mature_nfrac) / (emergence_nfrac - mature_nfrac)" +
                         "is negative. \nIs nitrogen_fraction < mature_nfrac or emergence_nfrac < mature_nfrac?")
    # final results
    return log((heat_fraction / denominator) - heat_fraction)


def calc_mass_from_fraction(fraction: float, whole: float) -> float:  # pseudocode: C.5.B.2
    """calculate mass of a constituent from the fractional mass of the whole

    Args:
      fraction: proportion of the whole made up of the constituent
      whole: total mass of the whole

    Returns: mass of the constituent
    """
    return fraction * whole


def calc_potential_nitrogen_uptake(demand: float, nitrogen_start: float, mature_nfrac: float,
                                   max_growth: float) -> float:  # pseudocode: C.5.B.3
    """
    Description: calculates potential nitrogen uptake for the day

    Args:
        demand: maximum/optimal nitrogen uptake of the plant on a given day
        nitrogen_start: nitrogen biomass at the end of the previous day
        mature_nfrac: nitrogen fraction at maturity
        max_growth: maximum potential biomass the plant can gain on a given day

    Returns: the potential nitrogen uptake for the day
    """
    return min(demand - nitrogen_start, 4 * mature_nfrac * max_growth)


def calc_layer_nitrogen_uptake(layer_demands: list[float], layer_uptake_potentials: list[float],
                               layer_nitrates: list[float]) -> list[float]:  # pseudocode: C.5.C.4
    """
    Description: calculates nitrogen uptake from each soil layer

    Args:
        layer_demands: list of nitrogen demands from each soil layer not met by the above layers
        layer_uptake_potentials: list of maximum nitrogen uptake from each soil layer
        layer_nitrates: list of nitrates present in each soil layer

    Returns: a list of nitrogen mass taken up from each soil layer
    """
    # ensure all list inputs are the same length
    if len(layer_uptake_potentials) != len(layer_demands) or len(layer_uptake_potentials) != len(layer_nitrates):
        raise ValueError("layer_potential, layer_demand, and layer_nitrate must be the same length")
    # calculate results
    layer_desired = [potential + demand for potential, demand in zip(layer_uptake_potentials, layer_demands)]
    return [min(desired, nitrate) for desired, nitrate in zip(layer_desired, layer_nitrates)]


def calc_layer_nitrogen_demands(uptake_potentials: list[float], nitrate_availabilities: list[float]) -> list[
    float]:  # pseudocode: C.5.C.5
    """
    Description: calculates nitrogen demand of the plant from each soil layer

    Args:
        uptake_potentials: maximum nitrogen uptake by the plant from each soil layer
        nitrate_availabilities: available nitrates (NO3) in each soil layer

    Returns: a list of nitrogen demands from each soil layer
    """
    layer_delta = [desired - available for desired, available in zip(uptake_potentials, nitrate_availabilities)]
    layer_demand = [sum(layer_delta[:i]) for i in range(len(layer_delta))]  # cumulative sum, starting at 0
    return [max(val, 0) for val in layer_demand]  # results constrained to zero


def calc_nitrogen_uptake_to_depth(demand: float, depth: float, root_depth: float,
                                  ndistro: float) -> float:  # pseudocode: C.5.C.1
    """
    Description: calculates potential nitrogen uptake from the soil surface to a specified depth

    Args:
        demand: the current nitrogen demand
        depth: the depth to which nitrogen uptake is calculated
        root_depth: the current root depth
        ndistro: the nitrogen uptake distribution parameter

    Returns: the potential amount of nitrogen taken up
    """
    # error checks
    if ndistro == 0:
        raise ValueError("ndistro cannot equal 0")
    # calculate results
    if root_depth <= 0:
        return 0
    else:
        first_term = demand / (1 - exp(-ndistro))
        second_term = 1 - exp(-ndistro * (depth / root_depth))
        return first_term * second_term


def calc_layer_nitrogen_uptake_potential(layer_bounds: list[float], total_demand: float,
                                         root_depth: float, ndistro_param: float) -> list[
    float]:  # pseudocode: C.5.C.2, C.5.C.3
    """
    Description: calculates potential nitrogen uptake from each soil layer

    Args:
        layer_bounds: list of lower boundaries for each soil layer, in ascending order (i.e., increasing depths)
        total_demand: total nitrogen demand of the plant
        root_depth: current depth of the plant roots
        ndistro_param: nitrogen uptake distribution parameter

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
    boundary_nitrogen = [calc_nitrogen_uptake_to_depth(total_demand, x, root_depth, ndistro_param) for x in
                         layer_bounds]  # N at each boundary
    boundary_nitrogen.insert(0, 0)  # 0 N uptake at soil surface
    layer_nitrogen = [below - above for below, above in
                      zip(boundary_nitrogen[1:], boundary_nitrogen)]  # subtract previous layer
    return layer_nitrogen


def calc_extracted_resource(request: float, source: float) -> float:
    """
    Description: calculates the amount of a resource that can be drawn from a source, based on a request

    Args:
        request: requested amount of the resource
        source: amount of the resource available at the source

    Returns: the amount of the resource to be extracted
    """
    return min(request, max(0.0, source))


def calc_layer_extracted_resource(requests: list[float], sources: list[float]) -> list[float]:
    if len(requests) != len(sources):
        raise ValueError("requests and pools should be the same length")

    return [calc_extracted_resource(req, src) for req, src in zip(requests, sources)]


def calc_stored_nitrogen(uptake: float, previous: float, fixed: float = 0) -> float:  # C.5.E.1
    """
    Description: calculates nitrogen mass stored in plant material after the current day's growth cycle

    Args:
        uptake: the mass of the nitrogen taken up by the plant on the current day
        previous: the nitrogen mass stored in the plant at the end of the previous day
        fixed: the mass of nitrogen fixed by the plant on the current day

    Returns: the total mass of nitrogen in the plant at the end of current day
    """
    return previous + uptake + fixed


def calc_fixed_nitrogen(demand: float, stage_factor: float, water_factor: float, nitrate_factor: float):
    """
    Description: calculate the amount of nitrogen fixed by a plant

    Args:
        demand: nitrogen demand not met by uptake from soil
        stage_factor: growth stage factor [0, 1]
        water_factor: soil water factor [0, 1]
        nitrate_factor: soil nitrate factor [0, 1]

    Returns: the amount of nitrogen added to plant biomass through fixation, capped at demand.
    """
    if 0 > stage_factor > 1:
        raise ValueError("stage_factor must be between 0 and 1")
    if 0 > water_factor > 1:
        raise ValueError("water_factor must be between 0 and 1")
    if 0 > nitrate_factor > 1:
        raise ValueError("nitrate_factor must be between 0 and 1")

    fixed = demand * stage_factor * min(water_factor, nitrate_factor, 1)
    return min(fixed, demand)


def calc_fixation_stage_factor(heatfrac: float) -> float:
    """
    Description: calculates plant growth stage factor

    Args:
        heatfrac: the accumulated fraction of potential heat units

    Returns: growth stage factor
    """
    # piece-wise function:
    if heatfrac <= 0.15:
        return 0

    elif heatfrac <= 0.3:
        return (6.67 * heatfrac) - 1

    elif heatfrac <= 0.55:
        return 1

    elif heatfrac <= 0.75:
        return 3.75 - (5 * heatfrac)

    else:
        return 0


def calc_nitrate_factor(accessible_nitrates):
    """
    Description: calculates soil nitrate factor

    Args:
        accessible_nitrates: total nitrates available in the soil layers accessible to roots

    Returns: the nitrate factor
    """
    if accessible_nitrates <= 100:
        return 1
    elif accessible_nitrates <= 300:
        return 1.5 - (0.0005 * accessible_nitrates)
    else:
        return 0


def calc_soil_water_factor(available_water: float, capacity_water: float) -> float:  # pseudocode: C.5.D.5
    """
    Description: calculates soil water factor

    Args:
        available_water: the water available in the soil profile (mm)
        capacity_water: the water accessible at field capacity (mm)

    Returns: soil water factor
    """
    return available_water / 0.85 * capacity_water

def calc_deepest_accessible_layer(root_depth: float, layer_bounds: list[float]) -> int:
    """
    Description:
        Determines the deepest soil layer that is accessible to roots.

    Args:
        root_depth: the root depth of a plant
        layer_bounds: the depths of the lower boundaries of each soil layer

    Returns:
        an integer indicating the deepest soil layer that the roots can access
    """

    if root_depth <= 0:  # handle no roots
        raise ValueError("root_depth cannot be less than zero")
    else:
        insert_position = bisect(layer_bounds, root_depth)
        deepest_layer = len(layer_bounds) - 1
        return min(insert_position, deepest_layer)
        # if insert_position >= deepest_layer:  # handle roots deeper than soil
        #     Warning("root_depth is deeper than the lowest soil layer")
        #     return deepest_layer
        # else:
        #     return insert_position



# TODO: Nitrogen fixation still needs to be updated
## -- OLD --
# from RUFAS.routines.field.crop.nitrogen_fixation import fix_nitrogen

# def reallocate_nitrogen(crop, soil) -> None:
#     """
#     Description: updates nitrogen uptake information for the given crop (and soil) during the daily growth cycle
#
#     Args:
#         crop: an instance of a crop class for which nitrogen should be updated
#         soil: an instance of a soil class, from which to draw nitrogen
#     """
#     update_nitrogen_fraction(crop)
#     update_optimal_nitrogen(crop)
#     update_potential_nitrogen_uptake(crop)
#     uptake_nitrogen(crop, soil)
#     if crop.is_nitrogen_fixer:
#         fix_nitrogen(crop, soil)
#     store_nitrogen_biomass(crop)


# def uptake_nitrogen(crop, soil) -> None:
#     """
#     Description: uptake nitrogen from the soil and reallocate it into the crop
#
#     Args:
#         crop: an instance of the BaseCrop class
#         soil: an instance of the Soil class, from which nitrogen will be transferred
#
#     Returns:
#         Nothing. Instead, nitrogen attributes are updated in crop and soil
#     """
#     # pre-uptake conditions
#     layer_bounds = [layer.bottom_depth for layer in soil.soil_layers]
#     layer_nitrates = [layer.NO3 for layer in soil.soil_layers]
#     # calculate layer values
#     potentials = calc_layer_nitrogen_uptake_potential(layer_bounds=layer_bounds, total_demand=crop.N_up,
#                                                       root_depth=crop.z_root,
#                                                       ndistro_param=crop.beta_n)
#     demands = calc_layer_nitrogen_demands(uptake_potentials=potentials, nitrate_availabilities=layer_nitrates)
#     uptakes = calc_layer_nitrogen_uptake(layer_demands=demands, layer_uptake_potentials=potentials,
#                                          layer_nitrates=layer_nitrates)
#     # update attributes
#     crop.pot_N_up_each_layer = potentials  # todo: needed?
#     crop.act_N_up_each_layer = uptakes  # todo: needed?
#     for uptake, layer in zip(uptakes, soil.soil_layers):
#         layer.N_uptake = uptake
#         layer.NO3 -= uptake  # remove from soil
#     crop.N_act_up = sum(uptakes)  # give to crop
