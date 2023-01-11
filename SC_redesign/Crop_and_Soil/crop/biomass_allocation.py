from math import exp
from typing import Optional
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData

# TODO - Refactor this class to match others - GitHub Issue #257
class BiomassAllocation:
    def __init__(self, crop_data: Optional[CropData] = None):
        self.data = crop_data or CropData()  # initialize with defaults, if not given

    def allocate_biomass(self, light):
        """allocate a plant's accumulated biomass during the day's growth"""
        self.photosynthesize(light)
        self.partition_biomass()

    def photosynthesize(self, light):
        """convert the day's incoming light energy into plant biomass

        Args: total available solar radiation for the day (MJ/m^2)
        """

        # intercept light
        self.data.usable_light = self._intercept_radiation(light, self.data.light_extinction, self.data.leaf_area_index)
        # accumulate biomass
        self.data.biomass_growth_max = self._determine_max_accumulation(self.data.usable_light,
                                                                        self.data.light_conversion)
        self.data.previous_biomass = self.data.biomass
        self.data.biomass_growth = self._determine_accumulated_biomass(self.data.growth_factor,
                                                                       self.data.biomass_growth_max)
        self.data.biomass += self.data.biomass_growth

    def partition_biomass(self):
        """partition the accumulated biomass into above ground and below grown portions"""
        self.data.above_ground_biomass = self._determine_above_ground_biomass(self.data.root_fraction,
                                                                              self.data.biomass)
        self.data.root_biomass = self._determine_below_ground_biomass(self.data.root_fraction, self.data.biomass)

    @staticmethod
    def _intercept_radiation(radiation: float, extinction: float, lai: float) -> float:  # pseudocode: C.9.A.1
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

    @staticmethod
    def _determine_max_accumulation(energy: float, efficiency: float) -> float:  # pseudocode: C.9.A.2
        """
        Description: calculates the upper-limit to biomass accumulation during a day

        Args:
            efficiency: crop-specific radiation use efficiency (dg/MJ)
            energy: intercepted energy from solar radiation for the day (MJ m^-2)

        Returns: the maximum biomass that can be accumulated in a day
        """
        return energy * efficiency

    @staticmethod
    def _determine_accumulated_biomass(growth_factor: float, max_growth: float) -> float:  # pseudocode: C.9.A.3
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

    @staticmethod
    def _determine_above_ground_biomass(root_frac: float, biomass: float) -> float:  # pseudocode: C.9.B.1
        """
        Description: calculates above ground plant biomass.

        SWAT Reference: 5:2.4.4

        Args:
            root_frac: fraction of biomass stored in roots
            biomass: the current total biomass of the plant

        Returns: above ground biomass
        """
        return (1 - root_frac) * biomass


    @staticmethod
    def _determine_below_ground_biomass(root_frac: float, biomass: float) -> float:
        """Description: calculates below ground plant biomass

        Args:
            root_frac: fraction of biomass stored in roots
            biomass: the current total biomass of the plant

        Returns: below ground biomass
        """
        return root_frac * biomass
