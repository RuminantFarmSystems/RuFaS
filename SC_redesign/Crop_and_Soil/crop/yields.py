from math import exp
from typing import Optional
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData

"""
This module is based upon the "Crop Yield" section of the SWAT model (5:2.4)
"""

class Yields():
    def __init__(self, crop_data: Optional[CropData] = None):
        self.data = crop_data or CropData()  # initialize with defaults, if not given

    # ---- Main Method ----
    def obtain_yields(self) -> None:
        """Main yields function; determines the season's cumulative crop yield on a given day

        Details: Although this method can be called on any day, it is most useful when called on a harvest or cutting
            day. The total yield (i.e., the desired crop product) is calculated and partitioned into "yield_collected"
            (the portion that will be extracted from the field) and "residue_created" (the portion that will remain in
            the field). This partitioning is determined by the "harvest_efficiency" - a perfect harvest efficiency (1.0)
            will collect all yield and leave no residue.

            If the plant is in maturity ("heat_fraction" >= 1.0), then the above-ground (shoot) biomass is adjusted
            for the dry-down process.

            Yield is a function of the "harvest_index" parameter, which is calculated normally calculated internally.
            However, the "harvest_index" value can be set manually via the "user_harvest_index" attribute, which will
            cause the harvest index override mode ("given_harvest_index" = True) wherein a slightly different set of
            parameters are used in the calculations (as in SWAT).
        """
        # Harvest Index
        if self.data.has_custom_harvest_index:
            self.data.harvest_index = self.data.user_harvest_index
        else:
            self.data.potential_harvest_index = self._determine_potential_harvest_index(self.data.heat_fraction,
                                                                                        self.data.optimal_harvest_index)
            self.data.harvest_index = self._adjust_harvest_index(self.data.potential_harvest_index,
                                                                 self.data.min_harvest_index,
                                                                 self.data.water_deficiency)
        # Dry down
        if self.data.is_mature:
            self.data.above_ground_biomass = self._adjust_biomass_for_dry_down(self.data.above_ground_biomass,
                                                                               self.data.dry_down_fraction)
        # Yield
        if self.data.harvest_index <= 1.0:
            self.data.crop_yield = self._determine_yield_from_shoot_biomass(self.data.above_ground_biomass,
                                                                            self.data.harvest_index)
        else:
            self.data.crop_yield = self._determine_yield_from_total_biomass(self.data.biomass, self.data.harvest_index)

        # Yield extraction
        self.data.yield_collected = self._determine_extracted_yield(self.data.crop_yield, self.data.harvest_efficiency)

        # Yield nutrient makeup
        if self.data.has_custom_harvest_index:
            self.data.collected_nitrogen = self.data.optimal_nitrogen_fraction * self.data.yield_collected  # SWAT 5:2.4.7
            self.data.collected_phosphorus = self.data.optimal_phosphorus_fraction * self.data.yield_collected  # SWAT 5:2.4.8
        else:
            self.data.collected_nitrogen = self.data.yield_nitrogen_fraction * self.data.yield_collected  # SWAT 5:2.4.5
            self.data.collected_phosphorus = self.data.yield_phosphorus_fraction * self.data.yield_collected  # SWAT 5:2.4.6

        # Yield Not extracted
        self.data.yield_residue = self._determine_unextracted_yield(self.data.crop_yield, self.data.harvest_efficiency)

        # Biomass update

        # TODO: total residue also needs to be calculated and accumulated in the soil (Soil class) - GitHub Issue #245

        # TODO: are above- and below-ground lignin residue (percent) needed?
        #   in the old version, they were both hard-coded to 17 - GitHub Issue #163

        # TODO: Need to make sure that harvest (SWAT 6:1.2), grazing (6:1.3), and harvest and kill (6:1.4), and
        #  Kill/end of growing season (6:1.5) operations are implemented in the Crop (or Field) class.

    # ---- Other Methods ----
    def assess_grown_feed_quality(self):
        """assess the quality of the crop as a feed for animals"""
        # TODO: need method. Better suited for feed module? - GitHub Issue #237
        #   The old method calc_quality_assessment() (RUFAS/routines/field/crop/yields.py)  assigned a "feed_id" based
        #   on the "harvest_quality" attribute, but only for corn. It also set the "NDF_harvest_percent" attribute to
        #   a hard-coded value.
        pass

    # ---- Static Methods ----

    @staticmethod
    def _determine_potential_harvest_index(heat_fraction: float, optimal_harvest_index: float) -> float:
        """calculates the potential harvest index for a plant on a given day

        Args:
            heat_fraction: fraction of potential heat units accumulated to date
            optimal_harvest_index: species-specific optimal harvest index for the plant at maturity under ideal
                conditions

        SWAT Reference: 5:2.4.1

        Details: Harvest Index is the ratio of grain to total shoot dry matter

        Returns: potential harvest index for the day
        """
        heat_percent = 100 * heat_fraction
        return optimal_harvest_index * heat_percent / (heat_percent + exp(11.1 - 10 * heat_fraction))

    @staticmethod
    def _adjust_harvest_index(harvest_index: float, min_harvest_index: float, water_deficiency: float) -> float:
        """calculates the actual harvest index for a given day, adjusted for water deficiency

        Args:
            min_harvest_index: harvest index in drought conditions; minimum possible harvest index for the plant,
                [0, Inf)
            harvest_index: potential harvest index for the day, [min_harvest_index, Inf)
            water_deficiency: water deficiency factor for the plant

        Details: values of min_harvest_index and harvest_index are input below their bounds, they are updated to
        equal their lower bounds.

        SWAT Reference: 5:3.3.1

        Returns: actual harvest index, adjusted for water deficiency
        """
        harvest_index = max(harvest_index, 0)  # bound to zero
        harvest_index = max(harvest_index, min_harvest_index)  # prevent harvest_index < min_harvest_index

        adj_harvest_index = (harvest_index - min_harvest_index) * water_deficiency / \
                            (water_deficiency + exp(6.13 - 0.883 * water_deficiency)) + min_harvest_index
        return max(adj_harvest_index, 0)  # bounded at zero

    @staticmethod
    def _adjust_biomass_for_dry_down(above_ground_biomass: float, dry_down_percent: float) -> float:
        # TODO: stand in for more sophisticated dry down method - GitHub Issue #162
        """ calculates the above ground biomass after water mass is lost in dry-down

        Args:
             above_ground_biomass: plant biomass stored above ground (non-root biomass)
             dry_down_percent: mass lost as water during dry-down, as a percentage of above ground biomass.

        Returns: the above ground biomass, after dry-down
        """
        return above_ground_biomass - (above_ground_biomass * dry_down_percent)

    @staticmethod
    def _determine_yield_from_shoot_biomass(above_ground_biomass: float, harvest_index: float) -> float:
        """Calculates maximum crop yield at harvest (in ideal conditions), when harvest index is <= 1.

        SWAT Reference: 5:2.4.2

        Args:
            above_ground_biomass: plant biomass stored above ground (i.e., non-root biomass; kg)
            harvest_index: harvest index for a given day

        Details: Yield is calculated as a proportion of above ground biomass

        Returns: crop yield (kg/ha)
        """
        return above_ground_biomass * harvest_index

    @staticmethod
    def _determine_yield_from_total_biomass(biomass: float, harvest_index: float) -> float:
        """Calculates maximum crop yield at harvest (in ideal conditions), when harvest index is > 1.

        SWAT Reference: 5:2.4.3

        Args:
            biomass: total plant biomass  (kg)
            harvest_index: harvest index for a given day

        Details: Yield is calculated as a proportion of above ground biomass

        Returns: crop yield (kg/ha)
        """
        return biomass * (1 - (1 / (1 + harvest_index)))

    @staticmethod
    def _determine_extracted_yield(crop_yield: float, harvest_efficiency: float) -> float:
        """calculates crop yield extracted at harvest, adjusted for harvest efficiency

        SWAT Reference: 5:3.3.4

        Args:
            crop_yield: total crop yield
            harvest_efficiency: efficiency of the harvest operation: the proportion of the yield that will be extracted
                from the field

        Returns: biomass of yield extracted (kg/ha)
        """
        if not 0 <= harvest_efficiency <= 1.0:
            raise ValueError("harvest_efficiency must be between 0 and 1 (inclusive)")

        return crop_yield * harvest_efficiency

    @staticmethod
    def _determine_unextracted_yield(crop_yield: float, harvest_efficiency: float) -> float:
        """calculates crop yield not extracted at harvest

        SWAT Reference: 5:3.3.5

        Args:
            crop_yield: total crop yield
            harvest_efficiency: efficiency of the harvest operation: the proportion of the yield that will be extracted
                from the field

        Returns: biomass of yield not extracted (kg/ha)
        """
        if not 0 <= harvest_efficiency <= 1:
            raise ValueError("harvest_efficiency must be between 0 and 1 (inclusive)")

        return crop_yield * (1 - harvest_efficiency)
