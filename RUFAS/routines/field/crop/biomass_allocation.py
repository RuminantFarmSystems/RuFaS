from math import exp
from typing import Optional
from RUFAS.routines.field.crop.crop_data import CropData


class BiomassAllocation:
    """
    This module primarily follows the Biomass Production section of the SWAT model (5:2.1.1)
    and some components from the Crop Yield section (5:2.4)

    Parameters
    ----------
    crop_data : Optional[CropData]
        The data object used for biomass calculation. Stores information
        about the plant's growth and environmental factors.

    Attributes
    ----------
    data : CropData
        The data object used for biomass calculation. Stores information
        about the plant's growth and environmental factors.

    Methods
    -------
    allocate_biomass(light: float) -> None
        Allocate a plant's accumulated biomass based on the day's light exposure.
    photosynthesize(light: float) -> None
        Simulate the photosynthesis process by converting light energy into biomass.
    partition_biomass() -> None
        Partitions the accumulated biomass into above and below ground components.
    _intercept_radiation(radiation: float, extinction: float, lai: float) -> float
        Calculates the amount of solar radiation intercepted for photosynthesis.
    _determine_max_accumulation(energy: float, efficiency: float) -> float
        Determines the upper limit of biomass accumulation in a day.
    _determine_accumulated_biomass(growth_factor: float, max_growth: float) -> float
        Calculates the actual biomass accumulated during a day.
    _determine_above_ground_biomass(root_frac: float, biomass: float) -> float
        Calculates the above ground biomass of a plant.
    _determine_below_ground_biomass(root_frac: float, biomass: float) -> float
        Calculates the below ground biomass of a plant.
    """

    def __init__(self, crop_data: Optional[CropData] = None):
        self.data = crop_data or CropData()  # initialize with defaults, if not given

    def allocate_biomass(self, light: float):
        """
        Allocate a plant's accumulated biomass during the day's growth.

        Parameters
        ----------
        light : float
            light radiation energy (MJ/m).

        Returns
        -------
        None
        """
        self.photosynthesize(light)
        self.partition_biomass()

    def photosynthesize(self, light: float):
        """
        Convert the day's incoming light energy into plant biomass.

        Parameters
        ----------
        light : float
            light radiation energy (MJ/m).
        """

        # intercept light
        self.data.usable_light = self._intercept_radiation(light, self.data.light_extinction, self.data.leaf_area_index)
        # accumulate biomass
        self.data.biomass_growth_max = self._determine_max_accumulation(self.data.usable_light,
                                                                        self.data.light_use_efficiency)
        self.data.previous_biomass = self.data.biomass
        self.data.biomass_growth = self._determine_accumulated_biomass(self.data.growth_factor,
                                                                       self.data.biomass_growth_max)
        self.data.biomass += self.data.biomass_growth

    def partition_biomass(self):
        """
        Partition the accumulated biomass into above ground and below ground portions.

        Returns
        -------
        None
        """
        self.data.above_ground_biomass = self._determine_above_ground_biomass(self.data.root_fraction,
                                                                              self.data.biomass)
        self.data.root_biomass = self._determine_below_ground_biomass(self.data.root_fraction, self.data.biomass)

    @staticmethod
    def _intercept_radiation(radiation: float, extinction: float, lai: float) -> float:  # pseudocode: C.9.A.1
        """
        Calculate the amount of solar radiation intercepted for photosynthesis during the day.

        Parameters
        ----------
        radiation : float
            Total solar radiation available for the day (MJ/m^2).
        extinction : float
            The light extinction coefficient (unitless).
        lai : float
            Current leaf area index of the crop (unitless).

        Returns
        -------
        float
            Intercepted radiation energy (MJ/m^2).
        """
        intercepted_radiation = 0.5 * radiation * (1 - exp(-1 * extinction * lai))
        return intercepted_radiation

    @staticmethod
    def _determine_max_accumulation(energy: float, efficiency: float) -> float:  # pseudocode: C.9.A.2
        """
        Calculate the upper limit to biomass accumulation during a day.

        Parameters
        ----------
        energy : float
            Intercepted energy from solar radiation for the day (MJ/m^2).
        efficiency : float
            Crop-specific radiation use efficiency (dg/MJ).

        Returns
        -------
        float
            The maximum biomass that can be accumulated in a day (kg/ha).
        """
        return energy * efficiency

    @staticmethod
    def _determine_accumulated_biomass(growth_factor: float, max_growth: float) -> float:  # pseudocode: C.9.A.3
        """
        Calculate the biomass accumulated during the day.

        Parameters
        ----------
        growth_factor : float
            The growth factor for the plant, which is a value from 0 to 1 (unitless).
        max_growth : float
            The maximum amount of biomass the plant can accumulate in a day (kg/ha).

        Returns
        -------
        float
            Biomass accumulated in a day (kg/ha).
        """
        growth = max_growth * growth_factor
        return growth

    @staticmethod
    def _determine_above_ground_biomass(root_frac: float, biomass: float) -> float:  # pseudocode: C.9.B.1
        """
        Calculate above ground plant biomass.

        Parameters
        ----------
        root_frac : float
            Fraction of biomass stored in roots (unitless).
        biomass : float
            The current total biomass of the plant (kg/ha).

        Returns
        -------
        float
            Above ground biomass (kg/ha).

        References
        ----------
        SWAT 5:2.4.4
        """
        return (1 - root_frac) * biomass

    @staticmethod
    def _determine_below_ground_biomass(root_frac: float, biomass: float) -> float:
        """
        Calculate below ground plant biomass.

        Parameters
        ----------
        root_frac : float
            Fraction of biomass stored in roots (unitless).
        biomass : float
            The current total biomass of the plant (kg/ha).

        Returns
        -------
        float
            Below ground biomass (kg/ha).
        """
        return root_frac * biomass
