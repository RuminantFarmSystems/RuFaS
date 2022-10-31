from math import exp


class BiomassAllocation:
    def __init__(self):
        self.light_extinction = 0.65
        self.leaf_area_index = 1.2
        self.light_conversion = 20
        self.biomass = 0
        self.growth_factor = 1.0
        self.root_frac = 1 / 3

        self.usable_light = None
        self.biomass_growth_max = None
        self.biomass_growth = None
        self.previous_biomass = None
        self.green_biomass = None
        self.root_biomass = None

    def allocate_biomass(self, light):
        """allocate a plant's accumulated biomass during the day's growth"""
        self.photosynthesize(light)
        self.partition_biomass()

    def photosynthesize(self, light):
        """convert the day's incoming light energy into plant biomass"""
        self.intercept_radiation(light)
        self.determine_max_growth()
        self.accumulate_biomass()

    def intercept_radiation(self, light):
        """capture usable energy from the day's incoming solar radiation (light)"""
        self.usable_light = calc_intercepted_radiation(light, self.light_extinction, self.leaf_area_index)

    def determine_max_growth(self):
        """determine how much the plant can grow under ideal circumstance, from the light captured"""
        self.biomass_growth_max = calc_max_accumulation(self.usable_light, self.light_conversion)

    def accumulate_biomass(self):
        """accumulate plant biomass during the day's growth"""
        self.previous_biomass = self.biomass
        self.biomass_growth = calc_biomass_accumulation(self.growth_factor, self.biomass_growth_max)
        self.biomass += self.biomass_growth

    def partition_biomass(self):
        """partition the accumulated biomass into above ground and below grown portions"""
        self.green_biomass = calc_above_ground_biomass(self.root_frac, self.biomass)
        self.root_biomass = calc_below_ground_biomass(self.root_frac, self.biomass)


def calc_intercepted_radiation(radiation: float, extinction: float, lai: float) -> float:  # pseudocode: C.9.A.1
    """
    Description:
        calculates amount of solar radiation intercepted for photosynthesis during the day

    Args:
        radiation: total solar radiation available for the day (MJ m^-2)
        extinction: the light extinction coefficient
        lai: current leaf area index of the crop

    Returns:
        intercepted radiation energy (MJ m^-2)
    """
    intercepted_radiation = 0.5 * radiation * (1 - exp(-1 * extinction * lai))
    return intercepted_radiation


def calc_max_accumulation(energy: float, efficiency: float) -> float:  # pseudocode: C.9.A.2
    """
    Description: calculates the upper-limit to biomass accumulation during a day

    Args:
        efficiency: crop-specific radiation use efficiency (dg/MJ)
        energy: intercepted energy from solar radiation for the day (MJ m^-2)

    Returns: the maximum biomass that can be accumulated in a day
    """
    return energy * efficiency


def calc_biomass_accumulation(growth_factor: float, max_growth: float) -> float:  # pseudocode: C.9.A.3
    """
    Description:
        Calculates the biomass accumulated during the day

    Args:
        growth_factor: the growth factor for the plant, which is a value from 0 to 1.
        max_growth: the maximum amount of biomass the plant can accumulate in a day

    Returns:
        a dictionary containing the starting biomass of the plant ("start"), the biomass of the plant at the end of the
        day ("end"), and the total biomass accumulated ("accumulated biomass")
    """
    growth = max_growth * growth_factor
    return growth


def calc_above_ground_biomass(root_frac: float, biomass: float) -> float:  # pseudocode: C.9.B.1
    """
    Description: calculates above ground plant biomass.

    Args:
        root_frac: fraction of biomass stored in roots
        biomass: the current total biomass of the plant

    Returns: above ground biomass
    """
    return (1 - root_frac) * biomass


def calc_below_ground_biomass(root_frac: float, biomass: float) -> float:
    """Description: calculates below ground plant biomass

    Args:
        root_frac: fraction of biomass stored in roots
        biomass: the current total biomass of the plant

    Returns: below ground biomass
    """
    return root_frac * biomass
