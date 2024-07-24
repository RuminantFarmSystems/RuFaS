from math import exp
from typing import Optional
from ....general_constants import GeneralConstants
from RUFAS.units import MeasurementUnits
from RUFAS.routines.feed_storage.feed_manager import FeedManager
from RUFAS.routines.feed_storage.harvested_crop import HarvestedCrop
from RUFAS.routines.field.crop.crop_data import (
    CropData,
    DEFAULT_DRY_MATTER_DIGESTIBILITY,
)
from RUFAS.routines.field.crop.harvest_operations import HarvestOperation
from RUFAS.routines.field.soil.soil_data import SoilData
from RUFAS.time import Time
from RUFAS.output_manager import OutputManager

om = OutputManager()


class CropManagement:
    """
    A class for managing crop operations based on crop data.

    Parameters
    ----------
    crop_data : Optional[CropData], optional
        The data class containing crop specifications and tracked attributes.
        If not provided, default CropData will be used.

    Attributes
    ----------
    data : CropData
        A reference to `crop_data`, on which crop management operations will be conducted.

    Notes
    -----
    This class is designed to handle various crop management operations using data provided by the `CropData` class.
    It is primarily based upon the "Crop Yield" (5:2.4) and "General Management" (6:1) sections of the SWAT model.

    """

    def __init__(self, crop_data: Optional[CropData] = None):
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

        self._record_yield(field_name, field_size, time.current_calendar_year, time.current_julian_day)
        self._transfer_residue(soil_data, not self.data.is_alive)

    # ---- Sub Methods ----
    def kill(self) -> None:
        """
        Kills the plant, preventing it from growing further, and converts all biomass to residue.

        Notes
        -----
        This operation is based on the SWAT model's guidelines, where a kill operation converts all biomass of
        the plant to residue. It is typically executed after a harvest (when specified) or at the end of the
        growing season for annual plants.

        """
        self.data.is_alive = False
        self.data.yield_residue += self.data.biomass
        self.data.residue_nitrogen = self.data.yield_residue * self.data.yield_nitrogen_fraction
        self.data.residue_phosphorus = self.data.yield_residue * self.data.yield_phosphorus_fraction

    def determine_harvest_index(self) -> None:
        """
        Sets the crop's harvest index based on various conditions.

        Notes
        -----
        If a custom harvest index is provided by the user (harvest index override), that value is used. Otherwise,
        the harvest index is calculated based on the crop's accumulated heat fraction and the crop-specific optimal
        harvest index. The method also adjusts the harvest index based on the crop's water deficiency.

        References
        ----------
        SWAT 5:2.4, 5:3.3
        """
        if self.data.do_harvest_index_override:
            self.data.harvest_index = self.data.user_harvest_index  # SWAT 5:3.3.1
        else:
            self.data.potential_harvest_index = self._determine_potential_harvest_index(
                self.data.heat_fraction, self.data.optimal_harvest_index
            )
            self.data.harvest_index = self._adjust_harvest_index(
                self.data.potential_harvest_index,
                self.data.min_harvest_index,
                self.data.water_deficiency,
            )

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
            self.data.cut_biomass = self.determine_biomass_cut_from_whole_plant(
                self.data.biomass, self.data.harvest_index
            )

        try:
            fraction_cut = self.data.cut_biomass / self.data.biomass
        except ZeroDivisionError:
            info_map = {"class": self.__class__.__name__, "function": self.cut_crop.__name__}
            warning_name = "Zero division error in crop management"
            warning_message = (
                f"A zero division error occurred in the harvesting process of crop management when calculating "
                f"fraction cut."
                f"The variable 'biomass' in CropData has an invalid value: '{self.data.biomass}'. "
            )

            om.add_warning(warning_name, warning_message, info_map)
            return None

        self.data.biomass -= self.data.cut_biomass
        self._recalculate_biomass_distribution(roots_harvested)

        self.data.leaf_area_index = self.data.leaf_area_index * (1 - fraction_cut)
        self.data.accumulated_heat_units = self.data.accumulated_heat_units * (1 - fraction_cut)

        self.data.dry_matter_yield_collected = self.data.cut_biomass * collected_fraction
        self.data.wet_yield_collected = self.data.dry_matter_yield_collected / (self.data.dry_matter_percentage / 100)

        self.data.yield_residue = self.data.cut_biomass * (1 - collected_fraction)

        if self.data.do_harvest_index_override:
            self.data.yield_nitrogen = self.data.optimal_nitrogen_fraction * self.data.wet_yield_collected
            self.data.yield_phosphorus = self.data.optimal_phosphorus_fraction * self.data.wet_yield_collected
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
            dry_matter_digestibility=DEFAULT_DRY_MATTER_DIGESTIBILITY,
            crude_protein_percent=self.data.crude_protein_percent,
            non_protein_nitrogen=self.data.non_protein_nitrogen,
            starch=self.data.starch,
            adf=self.data.adf,
            ndf=self.data.ndf,
            sugar=self.data.sugar,
            lignin=self.data.lignin_dry_matter_percentage,
            ash=self.data.ash,
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
        units = {
            "crop": MeasurementUnits.UNITLESS,
            "wet_yield": MeasurementUnits.WET_KILOGRAMS_PER_HECTARE,
            "dry_yield": MeasurementUnits.DRY_KILOGRAMS_PER_HECTARE,
            "nitrogen": MeasurementUnits.KILOGRAMS_PER_HECTARE,
            "phosphorus": MeasurementUnits.KILOGRAMS_PER_HECTARE,
            "yield_residue": MeasurementUnits.DRY_KILOGRAMS_PER_HECTARE,
            "harvest_index": MeasurementUnits.UNITLESS,
            "planting_year": MeasurementUnits.CALENDAR_YEAR,
            "planting_day": MeasurementUnits.ORDINAL_DAY,
            "harvest_year": MeasurementUnits.CALENDAR_YEAR,
            "harvest_day": MeasurementUnits.ORDINAL_DAY,
            "field_size": MeasurementUnits.HECTARE,
            "field_name": MeasurementUnits.UNITLESS,
        }
        wet_yield_collected = self.data.wet_yield_collected
        dry_yield_collected = self.data.dry_matter_yield_collected
        nitrogen_harvested = self.data.yield_nitrogen
        phosphorus_harvested = self.data.yield_phosphorus
        info_map = {
            "class": self.__class__.__name__,
            "function": self._record_yield.__name__,
            "suffix": f"field='{field_name}'",
            "units": units,
        }
        value = {
            "crop": self.data.species,
            "wet_yield": wet_yield_collected,
            "dry_yield": dry_yield_collected,
            "nitrogen": nitrogen_harvested,
            "phosphorus": phosphorus_harvested,
            "yield_residue": self.data.yield_residue,
            "harvest_index": self.data.harvest_index,
            "planting_year": self.data.planting_year,
            "planting_day": self.data.planting_day,
            "harvest_year": year,
            "harvest_day": day,
            "field_size": field_size,
            "field_name": field_name,
        }
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
        killed, then both surface and root residue is added to the soil profile. After transferring residue to the soil
        profile, the residue pools are reset to zero.

        """
        soil_data.crop_yield_nitrogen = self.data.residue_nitrogen
        soil_data.plant_residue_lignin_composition = (
            self.data.lignin_dry_matter_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION
        )
        if killed:
            self._distribute_residue_nutrients(soil_data)
        else:
            soil_data.soil_layers[0].plant_residue = self.data.yield_residue
            soil_data.soil_layers[0].fresh_organic_nitrogen_content += self.data.residue_nitrogen
            soil_data.soil_layers[0].labile_inorganic_phosphorus_content += self.data.residue_phosphorus
        self.data.yield_residue = 0.0
        self.data.residue_nitrogen = 0.0
        self.data.residue_phosphorus = 0.0

    def _distribute_residue_nutrients(self, soil_data: SoilData) -> None:
        """
        Distributes nutrients from plant residue into the soil profile.

        Parameters
        ----------
        soil_data : SoilData
            Object that tracks the attributes of the soil profile that contains this crop.
        root_residue_mass : float
            Dry matter mass of residue that is roots (kg / ha).

        """
        surface_layer = soil_data.soil_layers[0]
        surface_fraction = (self.data.yield_residue - self.data.root_biomass) / self.data.yield_residue
        surface_layer.plant_residue = self.data.yield_residue * surface_fraction
        surface_layer.fresh_organic_nitrogen_content += self.data.residue_nitrogen * surface_fraction
        surface_layer.labile_inorganic_phosphorus_content += self.data.residue_phosphorus * surface_fraction

        subsurface_residue = self.data.yield_residue * (1 - surface_fraction)
        subsurface_nitrogen = self.data.residue_nitrogen * (1 - surface_fraction)
        subsurface_phosphorus = self.data.residue_phosphorus * (1 - surface_fraction)

        root_frac_to_top_depth = self._calculate_root_mass_distribution(surface_layer.top_depth)
        root_frac_to_bottom_depth = self._calculate_root_mass_distribution(surface_layer.bottom_depth)
        layer_fraction = root_frac_to_bottom_depth - root_frac_to_top_depth
        surface_layer.plant_residue += subsurface_residue * layer_fraction
        surface_layer.fresh_organic_nitrogen_content += subsurface_nitrogen * layer_fraction
        surface_layer.labile_inorganic_phosphorus_content += subsurface_phosphorus * layer_fraction

        for layer in soil_data.soil_layers[1:]:
            root_frac_to_top_depth = self._calculate_root_mass_distribution(layer.top_depth)
            root_frac_to_bottom_depth = self._calculate_root_mass_distribution(layer.bottom_depth)
            layer_fraction = root_frac_to_bottom_depth - root_frac_to_top_depth
            layer.plant_residue = subsurface_residue * layer_fraction
            layer.active_organic_nitrogen_content += subsurface_nitrogen * layer_fraction
            layer.labile_inorganic_phosphorus_content += subsurface_phosphorus * layer_fraction

    def _calculate_root_mass_distribution(self, bottom_depth: float) -> float:
        """
        Calculates the fraction of total root biomass that is contained within each soil layer.

        Parameters
        ----------
        bottom_depth : float
            The bottom depth of the soil layer for which the root distribution is being calculated for (mm).

        Returns
        -------
        float
            Fraction of root biomass that is at or above the passed soil depth (unitless).

        References
        ----------
        .. [1] Fan, Jianling, et al. "Root distribution by depth for temperate agricultural crops." Field Crops Research
                189 (2016): 68-74, equation (2).

        Notes
        -----
        If the bottom depth of a soil layer extends past the maximum depth of the roots, then that soil layer contains
        all of the crop's root mass. If the bottom depth of the soil layer is 0 (i.e. it is the soil surface) then it
        will not contain any of the crop's root mass.

        """
        if bottom_depth >= self.data.max_root_depth:
            return 1.0
        if bottom_depth == 0.0:
            return 0.0

        first_term = 1 / (
            1 + (bottom_depth / self.data.root_distribution_param_da) ** self.data.root_distribution_param_c
        )
        second_term = 1 - 1 / (
            1 + (self.data.max_root_depth / self.data.root_distribution_param_da) ** self.data.root_distribution_param_c
        )
        third_term = bottom_depth / self.data.max_root_depth

        return first_term + second_term * third_term

    # ---- Helper Methods ----
    @staticmethod
    def _determine_potential_harvest_index(heat_fraction: float, optimal_harvest_index: float) -> float:
        """
        Calculates the potential harvest index for a plant on a given day.

        Parameters
        ----------
        heat_fraction : float
            Fraction of potential heat units accumulated to date (unitless).
        optimal_harvest_index : float
            Species-specific optimal harvest index for the plant at maturity under ideal conditions (unitless).

        Returns
        -------
        float
            Potential harvest index for the day (unitless).

        Notes
        -----
        The harvest index is the ratio of grain to total shoot dry matter. This calculation takes into
        account the fraction of potential heat units accumulated to date and the species-specific optimal
        harvest index for the plant at maturity under ideal conditions.

        References
        ----------
        SWAT documentation section 5:2.4.1

        """
        heat_percent = 100 * heat_fraction
        return optimal_harvest_index * heat_percent / (heat_percent + exp(11.1 - 10 * heat_fraction))

    @staticmethod
    def _adjust_harvest_index(harvest_index: float, min_harvest_index: float, water_deficiency: float) -> float:
        """
        Calculates the actual harvest index for a given day, adjusted for water deficiency.

        Parameters
        ----------
        min_harvest_index : float
            Harvest index in drought conditions; minimum possible harvest index for the plant. Must be positive and
            unitless.
        harvest_index : float
            Potential harvest index for the day. Must be greater than min_harvest_index and unitless.
        water_deficiency : float
            Water deficiency factor for the plant (unitless).

        Returns
        -------
        float
            Actual harvest index for the day, adjusted for water deficiency (unitless).

        Notes
        -----
        The method takes into consideration the minimum harvest index under drought conditions, the potential harvest
        index for the day, and the water deficiency factor of the plant. If values of min_harvest_index and
        harvest_index are input below their bounds, they are updated to equal their lower bounds.

        References
        ----------
        SWAT 5:3.3.1

        """
        harvest_index = max(harvest_index, 0)
        harvest_index = max(harvest_index, min_harvest_index)

        adj_harvest_index = (harvest_index - min_harvest_index) * water_deficiency / (
            water_deficiency + exp(6.13 - 0.883 * water_deficiency)
        ) + min_harvest_index
        return max(adj_harvest_index, 0)

    @staticmethod
    def determine_biomass_cut_from_whole_plant(biomass: float, harvest_index: float) -> float:
        """
        Calculates the maximum crop yield at harvest under ideal conditions, applicable when the harvest index is
        greater than 1.

        Parameters
        ----------
        biomass : float
            Total plant biomass, measured in kilograms (kg).
        harvest_index : float
            Harvest index for a given day, indicating the ratio of grain to total shoot dry matter.

        Returns
        -------
        float
            Crop yield, measured in kilograms per hectare (kg/ha).

        Notes
        -----
        The yield is calculated as a proportion of the above-ground biomass. This method is based on the SWAT model's
        guidelines for crop yield calculation.

        References
        ----------
        SWAT 5:2.4.3

        """
        return biomass * (1 - (1 / (1 + harvest_index)))
