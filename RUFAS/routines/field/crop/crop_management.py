from math import exp
from typing import Optional
from RUFAS.routines.feed_storage.feed_manager import FeedManager
from RUFAS.routines.feed_storage.harvested_crop import HarvestedCrop
from RUFAS.routines.field.crop.crop_data import CropData, DEFAULT_CROP_QUALITIES
from RUFAS.routines.field.crop.harvest_operations import HarvestOperation
from RUFAS.routines.field.soil.soil_data import SoilData
from RUFAS.time import Time
from RUFAS.output_manager import OutputManager

om = OutputManager()


class CropManagement:
    """
    A class for managing crop operations based on crop data.

    This class is designed to handle various crop management operations using data provided by the `CropData` class.
    It is primarily based upon the "Crop Yield" (5:2.4) and "General Management" (6:1) sections of the SWAT model.

    Parameters
    ----------
    crop_data : Optional[CropData], optional
        The data class containing crop specifications and tracked attributes.
        If not provided, default CropData will be used.

    Attributes
    ----------
    data : CropData
        A reference to `crop_data`, on which crop management operations will be conducted.
    """
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
    def manage_harvest(
            self,
            harvest_op: HarvestOperation,
            field_name: str,
            field_size: float,
            time: Time,
            soil_data: SoilData,
            feed_manager: FeedManager,
    ) -> None:
        """
        Executes the harvest operation passed on the crop that contains this module.

        Parameters
        ----------
        harvest_op : HarvestOperation
            The operation to be executed on this crop.
        field_name : str
            The name of the field that contains this crop.
        field_size : float
            Size of the field that contains this crop (ha)
        time : Time
            Time instance containing the current time of the simulation.
        soil_data : SoilData
            The object tracking the attributes of the soil profile.
        feed_manager : FeedManager
            Instance of the FeedManager that receives harvested crops.

        """
        self.determine_harvest_index()

        if harvest_op in (HarvestOperation.HARVEST_KILL, HarvestOperation.HARVEST_ONLY):
            self.cut_crop(collected_fraction=self.data.harvest_efficiency)
            self._store_harvested_crop(time, field_size, feed_manager)

        if harvest_op in (HarvestOperation.KILL_ONLY, HarvestOperation.HARVEST_KILL):
            self.kill()

        self._record_yield(field_name, field_size, time.calendar_year, time.day)
        self._transfer_residue(soil_data, not self.data.is_alive)

    # ---- Sub Methods ----
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
        """
        Performs a cut operation on the crop and, optionally, collects yield.

        Parameters
        ----------
        collected_fraction: The fraction of the cut biomass that is collected. The remaining portion remains
            in the field (between 0 and 1, inclusive).

        References
        ----------
        SWAT Theoretical documentation section 5:2.4 and section 6:1.2

        Raises
        ------
        ValueError
            If collected_fraction is not between 0 and 1.

        Notes
        -----
        The proportion of a crop that is cut is determined by the harvest index. A harvest index < 1 is the typical
        scenario and indicates that a proportion of biomass equal to the harvest index will be removed from the
        above-ground biomass of the plant. A harvest index > 1 will cut into below ground biomass as well.

        The cut biomass is removed from the plant's total biomass and the amount collected as yield is determined by the
        collected fraction. The remaining portion is left in the field. Cut operations without a harvest are conducted
        by setting collected_fraction = 0 (the default).

        In addition to total biomass, the nutrient content for both the collected and uncollected portions are updated.
        If the simulation is using the internally-derived harvest index for cutting, then nutrients are determined with
        the crop-specific yield nutrient fractions. Otherwise, (harvest index override), the optimal nutrient values are
        used.

        Note that, because above-ground biomass is calculated daily as a function of the total biomass and the root
        fraction (biomass_allocation.py, root_development.py), it does not make sense to alter the above-ground biomass
        here directly, even though that is more realistic. The current process should produce effective estimates over
        the growing season

        This method is meant to be called from one of the various harvest operations.

        """
        if not 0 <= collected_fraction <= 1.0:
            raise ValueError(
                f"Expected collected_fraction to be between 0 and 1 (inclusive), received '{collected_fraction}'."
            )

        roots_harvested = self.data.harvest_index > 1.0
        if not roots_harvested:
            self.data.cut_biomass = self.data.above_ground_biomass * self.data.harvest_index
        else:
            self.data.cut_biomass = self.determine_biomass_cut_from_whole_plant(self.data.biomass,
                                                                                self.data.harvest_index)
        fraction_cut = self.data.cut_biomass / self.data.biomass
        self.data.biomass -= self.data.cut_biomass
        self._recalculate_biomass_distribution(roots_harvested)

        self.data.leaf_area_index = self.data.leaf_area_index * (1 - fraction_cut)
        self.data.accumulated_heat_units = self.data.accumulated_heat_units * (1 - fraction_cut)

        self.data.wet_yield_collected = self.data.cut_biomass * collected_fraction
        self.data.dry_matter_yield_collected = self.data.wet_yield_collected * (self.data.dry_matter_percentage / 100)

        self.data.yield_residue = \
            self.data.cut_biomass * (1 - collected_fraction) * (self.data.dry_matter_percentage / 100)

        if self.data.do_harvest_index_override:
            self.data.yield_nitrogen = self.data.optimal_nitrogen_fraction * self.data.wet_yield_collected
            self.data.yield_phosphorus = self.data.optimal_phosphorus_fraction * \
                self.data.wet_yield_collected
            self.data.residue_nitrogen = self.data.optimal_nitrogen_fraction * self.data.yield_residue
            self.data.residue_phosphorus = self.data.optimal_phosphorus_fraction * self.data.yield_residue
        else:
            self.data.yield_nitrogen = self.data.yield_nitrogen_fraction * self.data.dry_matter_yield_collected
            self.data.yield_phosphorus = self.data.yield_phosphorus_fraction * self.data.dry_matter_yield_collected
            self.data.residue_nitrogen = self.data.yield_nitrogen_fraction * self.data.yield_residue
            self.data.residue_phosphorus = self.data.yield_phosphorus_fraction * self.data.yield_residue

    def _recalculate_biomass_distribution(self, roots_harvested: bool) -> None:
        """
        Recalculates how much biomass is stored above ground and how much is stored in the roots.

        Parameters
        ----------
        roots_harvested : bool
            Whether the roots were harvested.

        Notes
        -----
        SWAT does not specifically state how biomass should be redistributed after a harvest event. It has equation
        5:2.4.4, but does not specify if this equation is used to calculate biomass distributions pre- or post-harvest.

        If roots are not harvested, then the amount of biomass cut in the harvest operation is removed from the above
        ground biomass and the fraction of biomass that is below ground is recalculated directly. If roots are
        harvested, no biomass is left above ground and the fraction of biomass that is below ground is set to 1.0.

        """
        if not roots_harvested:
            self.data.above_ground_biomass -= self.data.cut_biomass
            self.data.root_fraction = self.data.root_biomass / self.data.biomass
        else:
            root_biomass_removed = self.data.cut_biomass - self.data.above_ground_biomass
            self.data.root_biomass -= root_biomass_removed
            self.data.above_ground_biomass = 0.0
            self.data.root_fraction = 1.0

    def _store_harvested_crop(self, time: Time, field_size: float, feed_manager: FeedManager) -> None:
        """
        Compiles the details of a harvest of this crop into a HarvestedCrop instance and passes it to the Feed Manager.

        Parameters
        ----------
        time : Time
            Time instance containing the current time of the simulation.
        field_size: float
            Size of the field from which this crop was harvested (ha).
        feed_manager: FeedManager
            Instance of the FeedManager which will receive the harvested crop.

        Returns
        -------
        HarvestedCrop
            HarvestedCrop instance containing all the details of this harvest event.

        Notes
        -----
        It is assumed that the wet yield is recorded in kg / ha for crops, but stored in the FeedManager as kg.

        """
        harvested_crop = HarvestedCrop(
            category=self.data.crop_category,
            type=self.data.crop_type,
            harvest_time=time,
            storage_time=time,
            fresh_mass=self.data.wet_yield_collected * field_size,
            dry_matter_percentage=self.data.dry_matter_percentage,
            dry_matter_digestibility=DEFAULT_CROP_QUALITIES.get("dry_matter_digestibility"),
            crude_protein_percent=DEFAULT_CROP_QUALITIES.get("crude_protein_percent"),
            non_protein_nitrogen=DEFAULT_CROP_QUALITIES.get("non_protein_nitrogen"),
            starch=DEFAULT_CROP_QUALITIES.get("starch"),
            adf=DEFAULT_CROP_QUALITIES.get("adf"),
            ndf=DEFAULT_CROP_QUALITIES.get("ndf"),
            sugar=DEFAULT_CROP_QUALITIES.get("sugar"),
            lignin=self.data.lignin_dry_matter_percentage,
            ash=DEFAULT_CROP_QUALITIES.get("ash"),
        )
        feed_manager.receive_crop(harvested_crop, self.data.storage_type)

    def _record_yield(self, field_name: str, field_size: float, year: int, day: int) -> None:
        """
        Records the mass and nutrients collected in an individual harvest and sends them to the OutputManager.

        Parameters
        ----------
        field_name : str
            Name of the field that contains this crop.
        field_size : float
            Size of the field that contains this crop (ha)
        year : int
            Year in which this harvest occurred.
        day : int
            Julian day on which this harvest occurred.

        """
        wet_yield_collected = self.data.wet_yield_collected
        dry_yield_collected = self.data.dry_matter_yield_collected
        nitrogen_harvested = self.data.yield_nitrogen
        phosphorus_harvested = self.data.yield_phosphorus
        info_map = {"class": self.__class__.__name__, "function": self._record_yield.__name__,
                    "prefix": f"field='{field_name}'", "field_size": field_size,
                    "species": f"'{self.data.species}'"}
        value = {"crop": self.data.name, "wet_yield": wet_yield_collected, "dry_yield": dry_yield_collected,
                 "nitrogen": nitrogen_harvested, "phosphorus": phosphorus_harvested,
                 "planting_date": {"year": self.data.planting_year, "day": self.data.planting_day},
                 "harvest_date": {"year": year, "day": day}}
        om.add_variable("harvest_yield", value, info_map)

    def _transfer_residue(self, soil_data: SoilData, killed: bool) -> None:
        """
        Transfers residue from harvest to SoilData that tracks how that residue is degraded and assimilated into the
        soil.

        Parameters
        ----------
        soil_data : SoilData
            Object that tracks the attributes of the soil profile that contains this crop.
        killed : bool
            Indicates whether the crop was killed by the harvest.

        Notes
        -----
        If a crop is harvested but not killed, then there is only residue added to the surface. If it is harvested and
        killed, then both surface and root residue is added to the soil profile.

        """
        soil_data.crop_yield_nitrogen = self.data.residue_nitrogen
        soil_data.plant_residue_lignin_composition = self.data.lignin_dry_matter_percentage / 100
        dry_matter_root_biomass = self.data.root_biomass * (self.data.dry_matter_percentage / 100)
        if killed:
            soil_data.plant_surface_residue = self.data.yield_residue - self.data.root_biomass
            soil_data.plant_root_residue = dry_matter_root_biomass
            soil_data.crop_root_depth = self.data.root_depth
        else:
            soil_data.plant_surface_residue = self.data.yield_residue
            soil_data.plant_root_residue = 0
            soil_data.crop_root_depth = 0

        soil_data.soil_layers[0].fresh_organic_nitrogen_content += self.data.residue_nitrogen

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
