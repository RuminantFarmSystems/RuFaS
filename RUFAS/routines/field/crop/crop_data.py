from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Any

from RUFAS.routines.feed_storage.enums import CropCategory, CropType
from RUFAS.routines.feed_storage.feed_manager import StorageType
from RUFAS.routines.field.crop.harvest_operations import HarvestOperation


class PlantCategory(Enum):
    """
    Enumeration of all plant types supported by RuFaS.

    Attributes
    ----------
    WARM_ANNUAL_LEGUME : str
        Represents warm climate annual legumes.
    COOL_ANNUAL_LEGUME : str
        Represents cool climate annual legumes.
    PERENNIAL_LEGUME : str
        Represents perennial legumes.
    WARM_ANNUAL : str
        Represents warm climate annual non-legume plants.
    COOL_ANNUAL : str
        Represents cool climate annual non-legume plants.
    PERENNIAL : str
        Represents perennial non-legume plants.
    TREE : str
        Represents tree-type plants.

    """
    WARM_ANNUAL_LEGUME = "warm_annual_legume"
    COOL_ANNUAL_LEGUME = "cool_annual_legume"
    PERENNIAL_LEGUME = "perennial_legume"
    WARM_ANNUAL = "warm_annual"
    COOL_ANNUAL = "cool_annual"
    PERENNIAL = "perennial"
    TREE = "tree"


DEFAULT_CROP_QUALITIES = {
    "dry_matter_digestibility": 40.0,
    "crude_protein_percent": 15.0,
    "non_protein_nitrogen": 13.0,
    "starch": 5.0,
    "adf": 10.0,
    "ndf": 6.0,
    "sugar": 10.0,
    "ash": 2.0
}


@dataclass(kw_only=True)
class CropData:
    """
    Data class containing crop variables based on SWAT database.

    Attributes
    ----------
    species : Optional[str]
        The species of the crop.
    name : Optional[str]
        The name of this specific crop instance.
    id : Optional[Any]
        The unique identifier for this crop instance.
    plant_code : Optional[str]
        4-letter plant code (used by SWAT).
    scientific_name : Optional[str]
        Taxonomic name of the plant.
    plant_category : Optional[PlantCategory]
        Classification of the plant (Reference SWAT crop.dat file, IDC variable).
    is_perennial : Optional[bool]
        Indicates if this plant is perennial.
    is_nitrogen_fixer : bool
        Indicates if the plant is a nitrogen fixer.
    priority : int
        Crop's priority level for shared resources in a field with multiple crops.
    field_proportion : float
        Proportion of the field occupied by this crop.
    is_alive : bool
        Indicates if the crop is currently alive in the field.
    crop_category : CropCategory
        Broad category into which this crop type falls.
    crop_type : CropType
        Sub type of this crop.
    storage_type : StorageType
        Method of storage for this crop when harvested.
    planting_year : int
        Year of planting for this crop.
    planting_day : int
        Julian day of planting for this crop.
    next_harvest_year : int
        Year for the next harvest.
    next_harvest_day : int
        Julian day for the next harvest.
    use_heat_scheduling : bool
        If heat unit scheduling is used for harvesting.
    harvest_heat_fraction : float
        Fraction of potential heat units for optimal growth stage for harvest.
    is_harvest_day : bool
        If today is the harvest day for this plant.
    next_harvest_operation : HarvestOperation
        Specific harvest operation to be executed next.
    minimum_temperature : float
        Minimum temperature for plant growth (Celsius).
    optimal_temperature : float
        Ideal temperature for maximum plant growth (Celsius).
    max_leaf_area_index : float
        Maximum leaf area index for the plant (unitless).
    first_heat_fraction_point : float
        Fraction of growing season for the first point on leaf development curve (unitless).
    first_leaf_fraction_point : float
        Fraction of max leaf area index at first point on leaf development curve (unitless).
    second_heat_fraction_point : float
        Fraction of growing season for the second point on leaf development curve (unitless).
    second_leaf_fraction_point : float
        Fraction of max leaf area index at second point on leaf development curve (unitless).
    senescent_heat_fraction : float
        Fraction of potential heat units for plant senescence (unitless).
    light_use_efficiency : float
        Light use efficiency of the plant (dg/MJ).
    minimum_cover_management_factor : float
        Minimum cover and management factor for water erosion (unitless).
    emergence_nitrogen_fraction : float
        Nitrogen fraction of biomass at emergence (unitless).
    half_mature_nitrogen_fraction : float
        Nitrogen fraction of biomass at half-maturity (unitless).
    mature_nitrogen_fraction : float
        Nitrogen fraction of biomass at maturity (unitless).
    emergence_phosphorus_fraction : float
        Phosphorus fraction of biomass at emergence (unitless).
    half_mature_phosphorus_fraction : float
        Phosphorus fraction of biomass at half-maturity (unitless).
    mature_phosphorus_fraction : float
        Phosphorus fraction of biomass at maturity (unitless).
    optimal_harvest_index : float
        Optimal harvest index under ideal growth conditions (unitless).
    min_harvest_index : float
        Minimum harvest index under drought conditions (unitless).
    yield_nitrogen_fraction : Optional[float]
        Fraction of nitrogen in yield (unitless).
    yield_phosphorus_fraction : Optional[float]
        Fraction of phosphorus in yield (unitless).
    light_extinction : float
        Light extinction coefficient (unitless).
    leaf_area_index : float
        Leaf area index of the plant (unitless).
    biomass : float
        Total plant biomass (kg/ha).
    growth_factor : float
        Growth factor multiplier for the plant (unitless).
    root_fraction : float
        Proportion of biomass in roots (unitless).
    usable_light : Optional[float]
        Solar radiation captured for photosynthesis (MJ/m^2).
    biomass_growth_max : Optional[float]
        Upper limit of biomass accumulation for the day (kg/ha).
    biomass_growth : Optional[float]
        Biomass accumulated during the day (kg/ha).
    previous_biomass : Optional[float]
        Biomass accumulated on the previous day (kg/ha).
    above_ground_biomass : float
        Above ground plant biomass excluding roots (kg/ha).
    root_biomass : Optional[float]
        Biomass stored in roots (kg/ha).
    nitrogen : float
        Nitrogen stored in plant biomass (kg/ha).
    optimal_nitrogen : float
        Optimal amount of nitrogen for current growth stage (kg/ha).
    phosphorus : float
        Phosphorus stored in plant biomass (kg/ha).
    optimal_phosphorus : float
        Optimal amount of phosphorus for current growth stage (kg/ha).
    water_stress : float
        Water stress for the day (unitless).
    temp_stress : Optional[float]
        Temperature stress for the day (unitless).
    nitrogen_stress : Optional[float]
        Nitrogen stress for the day (unitless).
    phosphorus_stress : Optional[float]
        Phosphorus stress for the day (unitless).
    maximum_temperature : float
        Maximum temperature for plant growth (Celsius).
    potential_heat_units : float
        Total heat units required for maturity (unitless).
    accumulated_heat_units : float
        Heat units accumulated to date (unitless).
    is_growing : bool
        If the crop is currently growing.
    is_dormant : bool
        If the crop is currently dormant.
    use_heat_unit_temperature : bool
        If alternative heat unit method is used.
    new_heat_units : Optional[float]
        Heat units accumulated on the current day (Celsius*).
    minimum_heat_unit_temperature : Optional[float]
        Minimum temperature for heat unit calculations (Celsius).
    maximum_heat_unit_temperature : Optional[float]
        Maximum temperature for heat unit calculations (Celsius).
    heat_unit_temperature : Optional[float]
        Heat unit temperature for alternative method (Celsius).
    max_canopy_height : float
        Maximum canopy height for the plant (m).
    _lai_shapes : Optional[float]
        Shape coefficients for calculating leaf area index (unitless).
    optimal_leaf_area_fraction : Optional[float]
        Fraction of max leaf area index for current heat fraction (unitless).
    canopy_height : Optional[float]
        Current height of the plant (m).
    leaf_area_added : Optional[float]
        Leaf area index change during the day (unitless).
    optimal_leaf_area_change : Optional[float]
        Leaf area index added under ideal conditions (unitless).
    previous_leaf_area_index : Optional[float]
        Leaf area index on the previous day (unitless).
    previous_optimal_leaf_area_fraction : Optional[float]
        Optimal leaf area fraction on the previous day (unitless).
    half_mature_heat_fraction : float
        Fraction of potential heat units for half maturity (unitless).
    mature_heat_fraction : float
        Fraction of potential heat units for maturity (unitless).
    near_mature_nitrogen_fraction : float
        Nitrogen fraction of biomass near maturity (unitless).
    nitrogen_distro_param : float
        Nitrogen uptake distribution parameter (unitless).
    root_depth : float
        Current depth of plant roots in soil (mm).
    nitrogen_shapes : Optional[List[float]]
        Shape coefficients for nitrogen uptake equations (unitless).
    previous_nitrogen : Optional[float]
        Nitrogen in biomass on the previous day (kg/ha).
    optimal_nitrogen_fraction : Optional[float]
        Optimal nitrogen proportion in biomass for current stage (unitless).
    potential_nitrogen_uptake : Optional[float]
        Potential nitrogen uptake under ideal conditions (kg/ha).
    total_soil_layers : Optional[int]
        Total number of layers in the soil profile (unitless).
    accessible_soil_layers : Optional[int]
        Number of soil layers accessible to plant roots (unitless).
    accessible_depths : Optional[List[float]]
        Soil layer boundaries accessible to plant (mm).
    inaccessible_soil_layers : Optional[int]
        Number of soil layers inaccessible to plant roots (unitless).
    layer_nitrogen_potentials : Optional[float]
        Potential nitrogen uptake from each soil layer (kg/ha).
    unmet_nitrogen_demands : Optional[float]
        Unmet nitrogen demands by overlaying soil layers (kg/ha).
    nitrogen_requests : Optional[float]
        Nitrogen requested from each soil layer (kg/ha).
    actual_nitrogen_uptakes : Optional[List[float]]
        Actual nitrogen uptake from each soil layer (kg/ha).
    total_nitrogen_uptake : Optional[float]
        Total nitrogen uptake by the plant (kg/ha).
    fixed_nitrogen : Optional[float]
        Total nitrogen fixed by the plant (kg/ha).
    nitrate_factor : Optional[float]
        Soil nitrate factor (unitless).
    fixation_stage_factor : Optional[float]
        Growth stage factor for nitrogen-fixing symbiotes
    near_mature_phosphorus_fraction : float, default 0.3
        Expected fraction of plant biomass comprised of nitrogen for the plant near maturity (unitless).
    phosphorus_distro_param : float, default 10
        Phosphorus uptake distribution parameter (unitless).
    phosphorus_shapes : Optional[List[float]], default None
        First and second shape coefficients for the nitrogen uptake equations (unitless).
    previous_phosphorus : Optional[float], default None
        Phosphorus value on the previous day (kg/ha).
    total_phosphorus_uptake : Optional[float], default None
        Total amount of phosphorus taken up by the plant (kg/ha).
    potential_phosphorus_uptake : Optional[float], default None
        Potential phosphorus to be taken up by the plant under ideal circumstances for the current day (kg/ha).
    actual_phosphorus_uptakes : Optional[List[float]], default None
        Actual phosphorus to be taken up by the plant from each soil layer (kg/ha).
    max_root_depth : float, default 2000
        Maximum depth of roots in the soil (mm).
    cumulative_evaporation : float, default 0.0
        Total water lost to evaporation by the plant during the growing season (mm).
    cumulative_transpiration : float, default 0.0
        Total water lost to transpiration by the plant during the growing season (mm).
    cumulative_evapotranspiration : float, default 0.0
        Total water lost to evapotranspiration by the plant during the growing season (mm).
    cumulative_potential_evapotranspiration : float, default 0.0
        Total expected maximum water loss by the plant during the growing season (mm).
    water_deficiency : Optional[float], default None
        Water deficiency factor for the plant (unitless).
    max_transpiration : Optional[float], default None
        Maximum transpiration on a given day (mm).
    evapotranspiration_weighting_coefficient : float, default 1
        Plant evapotranspiration curve number coefficient (unitless), in the range 0.5 to 2.0 inclusive.
    canopy_water : float, default 0
        Amount of water currently held in the canopy (mm).
    max_canopy_water_capacity : float, default 0.8
        Maximum amount of water that can be trapped in the canopy on a given day when fully developed (mm).
    water_distro_parameter : float, default 10
        Water-use distribution parameter governing water-uptake from the soil (unitless).
    potential_water_uptakes : Optional[List[float]], default None
        The maximum amount of water to be potentially taken up by a crop, from each soil layer (mm).
    water_compensation_factor : float, default 0.01
        Factor that determines the ability of a plant to draw water from deeper layers when demands are not met
        (unitless).
    unmet_water_demands : Optional[List[float]], default None
        Cumulative water demands not met by all previous layers (mm).
    actual_water_uptakes : Optional[List[float]], default None
        The actual amount of water to be removed from the soil (mm).
    water_uptake : float, default 0.0
        Total amount of water the plant took from the soil on the current day (mm).
    cumulative_water_uptake : float, default 0.0
        Cumulative sum of water taken up by the plant over the course of its lifetime (mm).
    harvest_efficiency : float, default 1.0
        Efficiency of the harvest operation: the proportion of yield that will be extracted from the field
        (unitless; [0, 1]).
    dry_matter_percentage : float, default 85.689
        Percentage of fresh yield that is dry matter (unitless).
    lignin_dry_matter_percentage : float, default 1.518
        Percentage of dry matter yield that is lignin (unitless).
    dry_down_fraction : float, default 0.2
        Proportion of plant biomass that is lost to dry-down (unitless; [0, 1]).
    optimal_phosphorus_fraction : float, default 0.073
        Optimal proportion of the plant's biomass comprised of nitrogen for the current growth stage (unitless).
    user_harvest_index : Optional[float], default None
        A user-specified harvest index (unitless). If given, 'harvest-index-override' is triggered.
    potential_harvest_index : Optional[float], default None
        Potential harvest index for a given day (unitless).
    harvest_index : Optional[float], default None
        Harvest index for a given day; fraction of above-ground plant biomass that is harvestable economic yield
        (unitless).
    cut_biomass : Optional[float], default None
        Total amount of the desired crop product (kg/ha).
    wet_yield_collected : Optional[float], default None
        Amount of the desired crop product to be removed from the field (kg/ha).
    dry_matter_yield_collected : Optional[float], default None
        Dry matter mass collected at harvest (kg/ha).
    yield_residue : Optional[float], default None
        Amount of dry matter residue created; unharvested yield (kg/ha).
    yield_nitrogen : Optional[float], default None
        Nitrogen contained in the harvested yield (kg/ha).
    yield_phosphorus : Optional[float], default None
        Phosphorus contained in the harvested yield (kg/ha).
    residue_nitrogen : Optional[float], default None
        Amount of nitrogen in the residue from this plant (kg/ha).
    residue_phosphorus : Optional[float], default None
        Amount of phosphorus in the residue from this plant (kg/ha).
    dormancy_loss_fraction : Optional[float], default None
        Fraction of biomass the crop loses when it goes dormant (unitless).
    minimum_lai_during_dormancy : Optional[float], default 0.75
        Minimum leaf area index for plants (perennials and trees only).

    """
    # ID variables (SWAT Table A-1 ish)
    species: Optional[str] = "generic"
    name: Optional[str] = "default generic annual crop"
    id: Optional[Any] = None
    plant_code: Optional[str] = None
    scientific_name: Optional[str] = None
    plant_category: Optional[PlantCategory] = PlantCategory("cool_annual")
    is_perennial: Optional[bool] = False
    is_nitrogen_fixer: bool = False
    priority: int = 1
    field_proportion: float = 1.0
    is_alive: bool = True

    crop_category: CropCategory = CropCategory.SMALL_GRAIN
    crop_type: CropType = CropType.GRAIN
    storage_type: StorageType = StorageType.DRY

    # Management variables
    planting_year: int = 0
    planting_day: int = 100
    next_harvest_year: int = 0
    next_harvest_day: int = 250
    use_heat_scheduling: bool = False
    harvest_heat_fraction: float = 1.10
    is_harvest_day: bool = False
    next_harvest_operation: HarvestOperation = HarvestOperation.HARVEST_KILL

    # SWAT Table A-3
    minimum_temperature: float = 0
    optimal_temperature: float = 25

    # SWAT Table A-4
    max_leaf_area_index: float = 4.0
    first_heat_fraction_point: float = 0.15
    first_leaf_fraction_point: float = 0.01
    second_heat_fraction_point: float = 0.50
    second_leaf_fraction_point: float = 0.95
    senescent_heat_fraction: float = 0.9

    # SWAT Table A-5
    light_use_efficiency: float = 30
    # light_use_decline_rate: float  # UNUSED (WAVP, $\Delta rue_{dcl}$)
    # stressed_light_use_efficiency  # UNUSED (BIOEHI, $RUE_{hi}$)
    # carbon_dioxide_stress_level = 660 # UNUSED (CO2HI, $CO_{2hi}$)

    # SWAT Table A-6
    minimum_cover_management_factor: float = 0.2

    # SWAT Table A-7
    emergence_nitrogen_fraction: float = 0.05
    half_mature_nitrogen_fraction: float = 0.02
    mature_nitrogen_fraction: float = 0.01
    emergence_phosphorus_fraction: float = 0.005
    half_mature_phosphorus_fraction: float = 0.003
    mature_phosphorus_fraction: float = 0.002

    # SWAT Table A-8
    optimal_harvest_index: float = 0.5
    min_harvest_index: float = 0.2
    yield_nitrogen_fraction: Optional[float] = 0.2
    yield_phosphorus_fraction: Optional[float] = 0.003

    # ---- biomass allocation
    light_extinction: float = 0.65
    leaf_area_index: float = 0.0
    biomass: float = 0
    growth_factor: float = 1.0
    root_fraction: float = 1 / 3
    usable_light: Optional[float] = None
    biomass_growth_max: Optional[float] = None
    biomass_growth: Optional[float] = None
    previous_biomass: Optional[float] = None
    above_ground_biomass: float = 0.1
    root_biomass: Optional[float] = 0.0

    # ---- growth constraints
    nitrogen: float = 35
    optimal_nitrogen: float = 100
    phosphorus: float = 20
    optimal_phosphorus: float = 80
    water_stress: float = 0.0
    temp_stress: Optional[float] = None
    nitrogen_stress: Optional[float] = None
    phosphorus_stress: Optional[float] = None

    # ---- heat_units
    maximum_temperature: float = 38
    potential_heat_units: float = 800
    accumulated_heat_units: float = 0
    is_growing: bool = True
    is_dormant: bool = False
    use_heat_unit_temperature: bool = False
    new_heat_units: Optional[float] = None
    minimum_heat_unit_temperature: Optional[float] = None
    maximum_heat_unit_temperature: Optional[float] = None
    heat_unit_temperature: Optional[float] = None

    # ---- leaf area index
    max_canopy_height: float = 2.5
    _lai_shapes: Optional[float] = None
    optimal_leaf_area_fraction: Optional[float] = None
    canopy_height: Optional[float] = None
    leaf_area_added: Optional[float] = None
    optimal_leaf_area_change: Optional[float] = None
    previous_leaf_area_index: Optional[float] = None
    previous_optimal_leaf_area_fraction: Optional[float] = None

    # ---- nitrogen incorporation
    half_mature_heat_fraction: float = 0.5
    mature_heat_fraction: float = 1.0
    near_mature_nitrogen_fraction: float = 0.02
    nitrogen_distro_param: float = 10
    root_depth: float = 1
    nitrogen_shapes: Optional[List[float]] = None
    previous_nitrogen: Optional[float] = None
    optimal_nitrogen_fraction: Optional[float] = None
    potential_nitrogen_uptake: Optional[float] = None
    total_soil_layers: Optional[int] = None
    accessible_soil_layers: Optional[int] = None
    accessible_depths: Optional[List[float]] = None
    inaccessible_soil_layers: Optional[int] = None
    layer_nitrogen_potentials: Optional[float] = None
    unmet_nitrogen_demands: Optional[float] = None
    nitrogen_requests: Optional[float] = None
    actual_nitrogen_uptakes: Optional[List[float]] = None
    total_nitrogen_uptake: Optional[float] = None
    fixed_nitrogen: Optional[float] = None
    nitrate_factor: Optional[float] = None
    fixation_stage_factor: Optional[float] = None

    # --- phosphorus incorporation ----
    near_mature_phosphorus_fraction: float = 0.3
    phosphorus_distro_param: float = 10
    phosphorus_shapes: Optional[List[float]] = None
    previous_phosphorus: Optional[float] = None
    total_phosphorus_uptake: Optional[float] = None
    potential_phosphorus_uptake: Optional[float] = None
    actual_phosphorus_uptakes: Optional[List[float]] = None

    # ---- root development
    max_root_depth: float = 2_000

    # ---- water dynamics
    cumulative_evaporation: float = 0.0
    cumulative_transpiration: float = 0.0
    cumulative_evapotranspiration: float = 0.0
    cumulative_potential_evapotranspiration: float = 0.0
    water_deficiency: Optional[float] = None
    max_transpiration: Optional[float] = None
    evapotranspiration_weighting_coefficient: float = 1
    """Used in SWAT equation 2:1.1.9, definition in .bsn input data description (named CNCOEF there)"""
    canopy_water: float = 0
    max_canopy_water_capacity: float = 0.8
    """References: SWAT Theoretical documentation eqn. 2:2.1.1 (see also SWAT Input file .HRU ("CANMX" page 233).
        Note: this default is super arbitrary. It comes from the paper:
            'Holder AJ, Rowe R, McNamara NP, Donnison IS, McCalmont JP. Soil & Water Assessment Tool (SWAT) simulated
            hydrological impacts of land use change from temperate grassland to energy crops: A case study in western
            UK. GCB Bioenergy. 2019;11:1298–1317.  https ://doi.org/10.1111/gcbb.12628'
        which cites the following paper that I could not find:
           'Wang, D., Li, J. S., & Rao, M. J. (2006). Winter wheat canopy interception under sprinkler irrigation.
            Scientia Agricultura Sinica, 39(9), 1859–1864.'
    """

    # ---- transpiration
    water_distro_parameter: float = 10
    potential_water_uptakes: Optional[List[float]] = None
    water_compensation_factor: float = 0.01
    """0 indicates no water can be drawn from deeper than expected and 1 indicates that any and all water
    can be drawn from deeper layers."""
    unmet_water_demands: Optional[List[float]] = None
    actual_water_uptakes: Optional[List[float]] = None
    water_uptake: float = 0.0
    cumulative_water_uptake: float = 0.0

    # ---- yields
    harvest_efficiency: float = 1.0
    dry_matter_percentage: float = 85.689
    """Note: this value is the default for Sorghum harvested as a grain."""
    lignin_dry_matter_percentage: float = 1.518
    """Note: this value is the default for Sorghum harvested as a grain."""
    dry_down_fraction: float = 0.2
    optimal_phosphorus_fraction: float = 0.073
    user_harvest_index: Optional[float] = None
    potential_harvest_index: Optional[float] = None
    harvest_index: Optional[float] = None
    cut_biomass: Optional[float] = None
    wet_yield_collected: Optional[float] = None
    dry_matter_yield_collected: Optional[float] = None
    yield_residue: Optional[float] = None
    yield_nitrogen: Optional[float] = None
    yield_phosphorus: Optional[float] = None
    residue_nitrogen: Optional[float] = None
    residue_phosphorus: Optional[float] = None

    # ---- dormancy
    dormancy_loss_fraction: Optional[float] = None
    """Fraction of biomass the crop loses when it goes dormant. Default 0.1 for perennials, 0.3 for trees
        Reference: SWAT Theoretical 5:1.2, and crop.dat BIO_LEAF description"""
    minimum_lai_during_dormancy: Optional[float] = 0.75
    """
    Note: SWAT Appendix-A section A.1.12 says that the default 0.75 is from pre-2009 versions of SWAT and users are
    now allowed to modify this value. But it does not provide values for any of the listed plant species and gives no
    information about how this value can be measured or calculated.
    """

    def __post_init__(self):
        """
        Initialize all attributes with defaults that depend on other attributes after the object has been initialized.
        """
        # Set dormancy loss
        if self.plant_category == PlantCategory.PERENNIAL or self.plant_category == PlantCategory.PERENNIAL_LEGUME:
            self.dormancy_loss_fraction = 0.1
        elif self.plant_category == PlantCategory.TREE:
            self.dormancy_loss_fraction = 0.3

        # Set perennial status
        if self.plant_category == PlantCategory.PERENNIAL or self.plant_category == PlantCategory.PERENNIAL_LEGUME or \
                self.plant_category == PlantCategory.TREE:
            self.is_perennial = True

        # set Fixation status
        if self.plant_category == PlantCategory.PERENNIAL_LEGUME or \
                self.plant_category == PlantCategory.WARM_ANNUAL_LEGUME or \
                self.plant_category == PlantCategory.COOL_ANNUAL_LEGUME:
            self.is_nitrogen_fixer = True

    @property
    def is_mature(self) -> bool:
        """
        Checks if maturity has been reached based on the fraction of potential heat units accumulated.

        References
        ----------
        SWAT Theoretical documentation section 5:2.1.4

        """
        return self.heat_fraction >= 1.0

    @property
    def in_growing_season(self) -> bool:
        """
        Indicates if the plant is in its growing season.

        Returns
        -------
        bool
            True if the plant is in its growing season, False otherwise.

        """
        return not self.is_mature and not self.is_dormant and self.is_alive and self.is_growing

    @property
    def do_harvest_index_override(self) -> bool:
        """
        Checks if a user-defined harvest index is given, which triggers a harvest index override.

        Returns
        -------
        bool
            True if a user-defined harvest index is given, False otherwise.

        """
        return self.user_harvest_index is not None

    @property
    def is_in_senescence(self) -> bool:
        """
        Check if the plant is in senescence.

        Returns
        -------
        bool
            True if the plant is in senescence, False otherwise.

        """
        return self.heat_fraction > self.senescent_heat_fraction

    @property
    def water_canopy_storage_capacity(self) -> float:
        """
        Calculate the maximum amount of water that can be held in the canopy.

        Returns
        -------
        float
            Maximum water storage capacity of the canopy, measured in millimeters (mm).

        References
        ----------
        SWAT Theoretical documentation eqn. 2:2.1.1

        """
        return self.max_canopy_water_capacity * (self.leaf_area_index / self.max_leaf_area_index)

    @property
    def heat_fraction(self) -> float:
        """
        Calculate the fraction of potential heat units accumulated by the plant.

        Returns
        -------
        float
            Fraction of potential heat units accumulated (unitless).

        References
        ----------
        SWAT Theoretical documentation section 5:2.1.4

        """
        return self.accumulated_heat_units / self.potential_heat_units
