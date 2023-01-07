from math import exp
from typing import Optional

"""
This module is based upon the "Crop Yield" section of the SWAT model (5:2.4)
"""

class Yields():
    def __init__(self):
        # constant attributes
        self.optimal_harvest_index: float = 3.5
        """potential harvest index for the plant at maturity under ideal growing conditions (unitless)"""
        self.min_harvest_index: float = 0.2
        """harvest index for the plant in drought conditions; represents minimum harvest index allowed for the plant
        (unitless)"""
        self.harvest_efficiency: float = 1.0
        """efficiency of the harvest operation: the proportion of the yield that will be extracted from the field 
        [0, 1]"""
        self.yield_nitrogen_fraction: float = 0.15
        """crop-specific expected fraction of nitrogen in yield (unitless)"""
        self.yield_phosphorus_fraction: float = 0.08
        """crop-specific expected fraction of phosphorus in yield (unitless)"""
        # temporally variable attributes
        self.heat_fraction: float = 0.6  # also in root_development.py
        """fraction of a plant's potential heat units accumulated to date (unitless)"""
        self.water_deficiency: float = 0.2  # also in water_dynamics.py
        """water deficiency factor for the plant (unitless)"""
        self.above_ground_biomass: float = 15
        """plant biomass excluding roots; shoot biomass (kg/ha)"""
        self.biomass: float = 25  # kg
        """plant biomass (kg/ha)"""
        self.dry_down_fraction: float = 0.2
        """proportion of plant biomass that is lost to dry-down [0, 1]"""
        self.nitrogen: float = 15  # kg
        """nitrogen stored in plant biomass (kg/ha)"""
        self.phosphorus: float = 8  # kg
        """phosphorus stored in plant biomass (kg/ha)"""
        self.optimal_nitrogen_fraction: float = 0.162  # from nitrogen_incorporation
        """optimal fraction of nitrogen in the plant biomass for current growth stage (unitless)"""
        self.optimal_phosphorus_fraction: float = 0.073
        """optimal fraction of phosphorus in the plant biomass for current growth stage (unitless)"""


        # Empty declarations
        self.user_harvest_index: Optional[float] = None  # TODO: handle user input for this. - GitHub Issue #246
        """a user-specified harvest index (unitless); if given, 'harvest-index-override' is triggered"""
        self.potential_harvest_index: Optional[float] = None
        """potential harvest index for a given day (unitless)"""
        self.harvest_index: Optional[float] = None
        """harvest index for a given day; fraction of above-ground plant biomass that is harvestable economic yield
        (unitless)"""
        self.crop_yield: Optional[float] = None
        """total amount of the desired crop product (kg/ha)"""
        self.yield_collected: Optional[float] = None
        """amount of the desired crop product to be removed from the field (kg/ha)"""
        self.yield_residue: Optional[float] = None
        """amount of residue created; unharvested yield (kg/ha)"""
        self.collected_nitrogen: Optional[float] = None
        """nitrogen contained in the harvested yield (kg/ha)"""
        self.collected_phosphorus: Optional[float] = None
        """phosphorus contained in the harvested yield (kg/ha)"""

    # ---- Properties ----
    @property
    def is_mature(self) -> bool:
        """checks if maturity has been reached based on the fraction of potential heat units accumulated"""
        return self.heat_fraction >= 1.0

    @property
    def has_given_harvest_index(self) -> bool:
        """was a user-defined harvest index is given? This triggers a harvest index override"""
        return self.user_harvest_index is not None

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
        if self.has_given_harvest_index:
            self.harvest_index = self.user_harvest_index
        else:
            self.potential_harvest_index = self.determine_potential_harvest_index(self.heat_fraction,
                                                                                  self.optimal_harvest_index)
            self.harvest_index = self.adjust_harvest_index(self.potential_harvest_index, self.min_harvest_index,
                                                           self.water_deficiency)
        # Dry down
        if self.is_mature:
            self.above_ground_biomass = self.adjust_biomass_for_dry_down(self.above_ground_biomass,
                                                                         self.dry_down_fraction)
        # Yield
        if self.harvest_index <= 1.0:
            self.crop_yield = self.determine_yield_from_shoot_biomass(self.above_ground_biomass, self.harvest_index)
        else:
            self.crop_yield = self.determine_yield_from_total_biomass(self.biomass, self.harvest_index)

        # Yield extraction
        self.yield_collected = self.determine_extracted_yield(self.crop_yield, self.harvest_efficiency)

        # Yield nutrient makeup
        if self.has_given_harvest_index:
            self.collected_nitrogen = self.optimal_nitrogen_fraction * self.yield_collected  # SWAT 5:2.4.7
            self.collected_phosphorus = self.optimal_phosphorus_fraction * self.yield_collected  # SWAT 5:2.4.8
        else:
            self.collected_nitrogen = self.yield_nitrogen_fraction * self.yield_collected  # SWAT 5:2.4.5
            self.collected_phosphorus = self.yield_phosphorus_fraction * self.yield_collected  # SWAT 5:2.4.6

        # Yield Not extracted
        self.yield_residue = self.determine_unextracted_yield(self.crop_yield, self.harvest_efficiency)

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
    def determine_potential_harvest_index(heat_fraction: float, optimal_harvest_index: float) -> float:
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
    def adjust_harvest_index(harvest_index: float, min_harvest_index: float, water_deficiency: float) -> float:
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
    def adjust_biomass_for_dry_down(above_ground_biomass: float, dry_down_percent: float) -> float:
        # TODO: stand in for more sophisticated dry down method - GitHub Issue #162
        """ calculates the above ground biomass after water mass is lost in dry-down

        Args:
             above_ground_biomass: plant biomass stored above ground (non-root biomass)
             dry_down_percent: mass lost as water during dry-down, as a percentage of above ground biomass.

        Returns: the above ground biomass, after dry-down
        """
        return above_ground_biomass - (above_ground_biomass * dry_down_percent)

    @staticmethod
    def determine_yield_from_shoot_biomass(above_ground_biomass: float, harvest_index: float) -> float:
        """Calculates maximum crop yield at harvest (in ideal conditions), when harvest index is <= 1.

        SWAT Reference: 5:2.4.2

        Args:
            above_ground_biomass: plant biomass stored above ground (i.e., non-root biomass; kg)
            harvest_index: potential harvest index for a given day

        Details: Yield is calculated as a proportion of above ground biomass

        Returns: crop yield (kg/ha)
        """
        return above_ground_biomass * harvest_index

    @staticmethod
    def determine_yield_from_total_biomass(biomass: float, harvest_index: float) -> float:
        """Calculates maximum crop yield at harvest (in ideal conditions), when harvest index is > 1.

        SWAT Reference: 5:2.4.3

        Args:
            biomass: total plant biomass  (kg)
            harvest_index: potential harvest index for a given day

        Details: Yield is calculated as a proportion of above ground biomass

        Returns: crop yield (kg/ha)
        """
        return biomass * (1 - (1 / (1 + harvest_index)))

    @staticmethod
    def determine_extracted_yield(crop_yield: float, harvest_efficiency: float) -> float:
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
    def determine_unextracted_yield(crop_yield: float, harvest_efficiency: float) -> float:
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
