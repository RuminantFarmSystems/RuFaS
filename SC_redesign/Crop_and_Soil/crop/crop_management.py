from math import exp
from typing import Optional
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from SC_redesign.Crop_and_Soil.crop.harvest_operations import HarvestOperation

"""
This module is primarily based upon the "Crop Yield" (5:2.4) and "General Management" (6:1) sections of the SWAT model
"""


class CropManagement:
    def __init__(self, crop_data: Optional[CropData] = None):
        """Create a crop management object from CropData

        Parameters
        ----------
        crop_data: CropData
            the data class containing crop specifications and tracked attributes

        Attributes
        ----------
        data: a reference to crop_data, on which crop management operations will be conducted
        """
        self.data = crop_data or CropData()  # initialize with defaults, if not given

    # ---- Main Methods ----
    def manage_harvest(self, harvest_op: HarvestOperation):
        self.determine_harvest_index()

        if harvest_op == HarvestOperation.HARVEST:
            self.cut_crop(collected_fraction=self.data.harvest_efficiency)
            self.kill()

        if harvest_op == HarvestOperation.HARVEST_NOKILL:
            self.cut_crop(collected_fraction=self.data.harvest_efficiency)

    def graze(self):  # TODO: implement grazing method (SWAT 6:1.3)
        pass

    # ---- Sub Methods ----
    def collect_cut_yield(self, collected_fraction):  # TODO: implement for in-field drying - needed? GitHub Issue #162
        """collect yield that has been previously cut and left in the field"""
        pass

    def kill(self) -> None:
        """kills the plant, preventing it from growing, and converts all biomass to residue

        Details:
            Swat says that "a kill operation converts all biomass to residue"

            A kill operation is executed after a harvest (when specified), or at the end of the growing season for
            annual plants.
        """
        self.data.is_alive = False
        self.data.yield_residue += self.data.biomass

    def determine_harvest_index(self):
        """sets the crop's harvest index

        SWAT References: 5:2.4, 5:3.3,

        Details:
            If a custom harvest index is provided by the user (harvest index override), that value is used. Otherwise,
            the harvest index is calculated from the crop's accumulated heat fraction, the crop-specific optimal
            harvest index. It also adjusts the harvest index based on the crop's water deficiency.
        """
        if self.data.do_harvest_index_override:
            self.data.harvest_index = self.data.user_harvest_index  # SWAT 5:3.3.1
        else:
            self.data.potential_harvest_index = self._determine_potential_harvest_index(self.data.heat_fraction,
                                                                                        self.data.optimal_harvest_index)
            self.data.harvest_index = self._adjust_harvest_index(self.data.potential_harvest_index,
                                                                 self.data.min_harvest_index,
                                                                 self.data.water_deficiency)

    def dry_down(self):
        """adjusts crop biomass for water loss during dry-down process

        Details:
            If the crop remains uncut after maturity, this method reduces the crop's biomass based on
            species-specific water content.
        """
        # TODO: stand in for more sophisticated dry down method - GitHub Issue #162
        #   The dry down method is not currently used
        self.data.above_ground_biomass -= (self.data.above_ground_biomass * self.data.dry_down_fraction)

    def cut_crop(self, collected_fraction: float = 0) -> None:
        """performs a cut operation on the crop and, optionally, collects yield

        Args:
            collected_fraction: The fraction of the cut biomass that is collected. The remaining portion remains
                in the field (between 0 and 1, inclusive).

        SWAT Reference: 5:2.4

        Raises: a ValueError if collected_fraction is not between 0 and 1

        Details: The proportion of a crop that is cut is determined by the harvest index. A harvest index < 1 is the
            typical scenario and indicates that a proportion of biomass equal to the harvest index will be removed
            from the above-ground biomass of the plant. A harvest index > 1 will cut into below ground biomass as well.

            The cut biomass is removed from the plant's total biomass and the amount collected as yield is determined
            by the collected fraction. The remaining portion is left in the field. Cut operations without a harvest
            are conducted by setting collected_fraction = 0 (the default).

            In addition to total biomass, the nutrient content for both the collected and uncollected portions are
            updated. If the simulation is using the internally-derived harvest index for cutting, then nutrients are
            determined with the crop-specific yield nutrient fractions. Otherwise, (harvest index override), the
            optimal nutrient values are used.

            Note that, because above-ground biomass is calculated daily as a function of the total biomass and the root
            fraction (biomass_allocation.py, root_development.py), it does not make sense to alter the above-ground
            biomass here directly, even though that is more realistic. The current process should produce effective
            estimates over the growing season

            This method is meant to be called from one of the various harvest operations.
        """
        if not 0 <= collected_fraction <= 1.0:
            raise ValueError(
                f"Expected collected_fraction to be between 0 and 1 (inclusive), received '{collected_fraction}'."
            )

        # Biomass removed from plant
        if self.data.harvest_index <= 1.0:
            self.data.cut_biomass = self.data.above_ground_biomass * self.data.harvest_index  # SWAT 5:2.4.2
        else:
            self.data.cut_biomass = self.determine_biomass_cut_from_whole_plant(self.data.biomass,
                                                                                self.data.harvest_index)
        fraction_cut = self.data.cut_biomass / self.data.biomass
        self.data.biomass -= self.data.cut_biomass

        # Reset some growth parameters (SWAT 6:1.2)
        self.data.leaf_area_index = self.data.leaf_area_index * (1 - fraction_cut)
        self.data.accumulated_heat_units = self.data.accumulated_heat_units * (1 - fraction_cut)

        # Biomass collected as yield, and its nutrient content
        self.data.yield_collected = self.data.cut_biomass * collected_fraction  # SWAT 5:3.3.4
        if self.data.do_harvest_index_override:
            self.data.yield_nitrogen = self.data.optimal_nitrogen_fraction * self.data.yield_collected  # SWAT 5:2.4.7
            self.data.yield_phosphorus = self.data.optimal_phosphorus_fraction * \
                self.data.yield_collected  # SWAT 5:2.4.8
        else:
            self.data.yield_nitrogen = self.data.yield_nitrogen_fraction * self.data.yield_collected  # SWAT 5:2.4.5
            self.data.yield_phosphorus = self.data.yield_phosphorus_fraction * self.data.yield_collected  # SWAT 5:2.4.6

        # Uncollected biomass and nutrients
        self.data.yield_residue = self.data.cut_biomass * (1 - collected_fraction)  # SWAT 5:3.3.5
        if self.data.do_harvest_index_override:
            self.data.residue_nitrogen = self.data.optimal_nitrogen_fraction * self.data.yield_residue
            self.data.residue_phosphorus = self.data.optimal_phosphorus_fraction * self.data.yield_residue
        else:
            self.data.residue_nitrogen = self.data.yield_nitrogen_fraction * self.data.yield_residue
            self.data.residue_phosphorus = self.data.yield_phosphorus_fraction * self.data.yield_residue

        # TODO: residue needs to be accumulated in the soil (Soil class) - GitHub Issue #245

        # TODO: are above- and below-ground lignin residue (percent) needed?
        #   in the old version, they were both hard-coded to 17 - GitHub Issue #163

    # ---- Harvest Scheduling ----

    def check_harvest_schedule(self, current_day, current_year):
        """checks if the crop should be harvested today and sets the corresponding is_harvest_day attribute.

        If the heat unit scheduling is used for this crop (`use_heat_scheduling = True`), then the current heat
        fraction is used to decide if the crop should be harvested today. Otherwise, we simply check if the current
        day is the day on which the harvest is scheduled.

        References
        ----------
        SWAT 5:1.1.1 (Heat Unit Scheduling)

        Parameters
        ----------
        current_day : int
            the current (julian) day
        current_year : int
            the current year
        """
        if self.data.use_heat_scheduling:
            self.data.is_harvest_day = self.data.heat_fraction >= self.data.harvest_heat_fraction
        else:
            is_harvest_year = current_day == self.data.next_harvest_day
            is_harvest_day = current_year == self.data.next_harvest_year
            self.data.is_harvest_day = is_harvest_year & is_harvest_day

    # ---- Helper Methods ----
    @staticmethod
    def _determine_potential_harvest_index(heat_fraction: float, optimal_harvest_index: float) -> float:
        """calculates the potential harvest index for a plant on a given day

        Args:
            heat_fraction: fraction of potential heat units accumulated to date
            optimal_harvest_index: species-specific optimal harvest index for the plant at maturity under ideal
                conditions

        SWAT Reference: 5:2.4.1

        Details: Harvest Index is the ratio of grain to total shoot dry matter

        Returns: potential harvest index for the day (unitless)
        """
        heat_percent = 100 * heat_fraction
        return optimal_harvest_index * heat_percent / (heat_percent + exp(11.1 - 10 * heat_fraction))

    @staticmethod
    def _adjust_harvest_index(harvest_index: float, min_harvest_index: float, water_deficiency: float) -> float:
        """calculates the actual harvest index for a given day, adjusted for water deficiency

        Args:
            min_harvest_index: harvest index in drought conditions; minimum possible harvest index for the plant,
                (unitless, must be positive)
            harvest_index: potential harvest index for the day, (unitless, must be greater than min_harvest_index)
            water_deficiency: water deficiency factor for the plant (unitless)

        Details: values of min_harvest_index and harvest_index are input below their bounds, they are updated to
        equal their lower bounds.

        SWAT Reference: 5:3.3.1

        Returns: actual harvest index, adjusted for water deficiency (unitless)
        """
        harvest_index = max(harvest_index, 0)
        harvest_index = max(harvest_index, min_harvest_index)

        adj_harvest_index = (harvest_index - min_harvest_index) * water_deficiency / \
                            (water_deficiency + exp(6.13 - 0.883 * water_deficiency)) + min_harvest_index
        return max(adj_harvest_index, 0)

    @staticmethod
    def determine_biomass_cut_from_whole_plant(biomass: float, harvest_index: float) -> float:
        """Calculates maximum crop yield at harvest (in ideal conditions), when harvest index is > 1.

        SWAT Reference: 5:2.4.3

        Args:
            biomass: total plant biomass  (kg)
            harvest_index: harvest index for a given day

        Details: Yield is calculated as a proportion of above ground biomass

        Returns: crop yield (kg/ha)
        """
        return biomass * (1 - (1 / (1 + harvest_index)))
