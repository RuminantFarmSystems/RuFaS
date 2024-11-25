from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from RUFAS.data_structures.crop_soil_to_feed_storage_connection import CropCategory, CropType, StorageType
from RUFAS.routines.field.crop.crop_enum import CropSpecies


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


# This is an arbitrary values to be used until a generalized and appropriate solution can be found for setting
# species-specific dry matter digestibility amounts.
DEFAULT_DRY_MATTER_DIGESTIBILITY: float = 40.0


@dataclass(kw_only=True)
class CropData:
    """
    Data class containing crop variables based on SWAT database.

    Attributes
    ----------
    species : CropSpecies, default None
        The species of the crop.
    name : Optional[str]
        The name of this specific crop instance.
    id : Optional[Any]
        The unique identifier for this crop instance.
    plant_category : Optional[PlantCategory]
        Classification of the plant (Reference SWAT crop.dat file, IDC variable).
    is_perennial : Optional[bool]
        Indicates if this plant is perennial.
    is_nitrogen_fixer : bool
        Indicates if the plant is a nitrogen fixer.
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
    use_heat_scheduling : bool
        If heat unit scheduling is used for harvesting.
    harvest_heat_fraction : float
        Fraction of potential heat units for optimal growth stage for harvest.
    minimum_temperature : float
        Minimum temperature for plant growth (Celsius).
    max_leaf_area_index : float
        Maximum leaf area index for the plant (unitless).
    senescent_heat_fraction : float
        Fraction of potential heat units for plant senescence (unitless).
    minimum_cover_management_factor : float
        Minimum cover and management factor for water erosion (unitless).
    yield_nitrogen_fraction : Optional[float]
        Fraction of nitrogen in yield (unitless).
    leaf_area_index : float
        Leaf area index of the plant (unitless).
    biomass : float
        Total plant biomass (kg/ha).
    growth_factor : float
        Growth factor multiplier for the plant (unitless).
    root_fraction : float
        Proportion of biomass in roots (unitless).
    biomass_growth_max : float, default 0.0
        Upper limit of biomass accumulation for the day (kg/ha).
    above_ground_biomass : float
        Above ground plant biomass excluding roots (kg/ha).
    root_biomass : Optional[float]
        Biomass stored in roots (kg/ha).
    nitrogen : float, default 0.0
        Nitrogen stored in plant biomass (kg/ha).
    optimal_nitrogen : float, default 0.0
        Optimal amount of nitrogen for current growth stage (kg/ha).
    phosphorus : float, default 0.0
        Phosphorus stored in plant biomass (kg/ha).
    optimal_phosphorus : float, default 0.0
        Optimal amount of phosphorus for current growth stage (kg/ha).
    potential_heat_units : float
        Total heat units required for maturity (unitless).
    accumulated_heat_units : float
        Heat units accumulated to date (unitless).
    is_growing : bool
        If the crop is currently growing.
    is_dormant : bool
        If the crop is currently dormant.
    half_mature_heat_fraction : float
        Fraction of potential heat units for half maturity (unitless).
    mature_heat_fraction : float
        Fraction of potential heat units for maturity (unitless).
    root_depth : float
        Current depth of plant roots in soil (mm).
    optimal_nitrogen_fraction : Optional[float]
        Optimal nitrogen proportion in biomass for current stage (unitless).
    total_soil_layers : Optional[int]
        Total number of layers in the soil profile (unitless).
    accessible_soil_layers : Optional[int]
        Number of soil layers accessible to plant roots (unitless).
    inaccessible_soil_layers : Optional[int]
        Number of soil layers inaccessible to plant roots (unitless).
    max_root_depth : float, default 2000
        Maximum depth of roots in the soil (mm).
    cumulative_evaporation : float, default 0.0
        Total water lost to evaporation by the plant during the growing season (mm).
    cumulative_transpiration : float, default 0.0
        Total water lost to transpiration by the plant during the growing season (mm).
    cumulative_potential_evapotranspiration : float, default 0.0
        Total expected maximum water loss by the plant during the growing season (mm).
    water_deficiency : Optional[float], default None
        Water deficiency factor for the plant (unitless).
    max_transpiration : Optional[float], default None
        Maximum transpiration on a given day (mm).
    canopy_water : float, default 0
        Amount of water currently held in the canopy (mm).
    max_canopy_water_capacity : float, default 0.8
        Maximum amount of water that can be trapped in the canopy on a given day when fully developed (mm).
        References: SWAT Theoretical documentation eqn. 2:2.1.1 (see also SWAT Input file .HRU ("CANMX" page 233).
        Note: this default is super arbitrary. It comes from the paper:
            'Holder AJ, Rowe R, McNamara NP, Donnison IS, McCalmont JP. Soil & Water Assessment Tool (SWAT) simulated
            hydrological impacts of land use change from temperate grassland to energy crops: A case study in western
            UK. GCB Bioenergy. 2019;11:1298–1317.  https ://doi.org/10.1111/gcbb.12628'
            which cites the following paper that I could not find:
           'Wang, D., Li, J. S., & Rao, M. J. (2006). Winter wheat canopy interception under sprinkler irrigation.
            Scientia Agricultura Sinica, 39(9), 1859–1864.'
    water_uptake : float, default 0.0
        Total amount of water the plant took from the soil on the current day (mm).
    cumulative_water_uptake : float, default 0.0
        Cumulative sum of water taken up by the plant over the course of its lifetime (mm).
    harvest_efficiency : float, default 1.0
        Efficiency of the harvest operation: the proportion of yield that will be extracted from the field
        (unitless; [0, 1]).
    dry_matter_percentage : float, default 85.689
        Percentage of fresh yield that is dry matter (unitless). This value is the default for Sorghum harvested as a
        grain.
    lignin_dry_matter_percentage : float, default 1.518
        Percentage of dry matter yield that is lignin (unitless). This value is the default for Sorghum harvested as a
        grain.
    crude_protein_percent : float, default 12.481
        Percentage of dry matter mass that is dietary crude protein (unitless).
    non_protein_nitrogen : float, default 2.518
        Percentage of dry matter mass that is non-protein nitrogen (unitless).
    starch : float, default 72.586
        Percentage of dry matter mass that is starch (unitless).
    adf : float, default 3.934
        Percentage of dry matter mass that is acid detergent fiber (unitless).
    ndf : float, default 6.134
        Percentage of dry matter mass that is neutral detergent fiber (unitless).
    sugar : float, default 2.235
        Percentage of dry matter mass that is labile carbohydrate (unitless).
    ash : float, default 2.496
        Percentage of dry matter mass that is ash (unitless).
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
    wet_yield_collected : float, default 0.0
        Amount of the desired crop product to be removed from the field (kg/ha).
    dry_matter_yield_collected : float, default 0.0
        Dry matter mass collected at harvest (kg/ha).
    yield_residue : float, default 0.0
        Amount of dry matter residue created; unharvested yield (kg/ha).
    yield_nitrogen : Optional[float], default None
        Nitrogen contained in the harvested yield (kg/ha).
    yield_phosphorus : Optional[float], default None
        Phosphorus contained in the harvested yield (kg/ha).
    residue_nitrogen : float, default 0.0
        Amount of nitrogen in the residue from this plant (kg/ha).
    residue_phosphorus : float, default 0.0
        Amount of phosphorus in the residue from this plant (kg/ha).
    root_distribution_param_da: float, default 145.0
        Empirical root distribution parameter d_a (mm).
        Reference: Fan, Jianling, et al. "Root distribution by depth for temperate agricultural crops." Field Crops
            Research 189 (2016): 68-74, table 1. Note that the value has been converted to mm.
    root_distribution_param_c: float, default -1.165
        Empirical root distribution parameter c (unitless).
        Reference: Fan, Jianling, et al. "Root distribution by depth for temperate agricultural crops." Field Crops
            Research 189 (2016): 68-74, table 1.
    dormancy_loss_fraction : Optional[float], default None
        Fraction of biomass the crop loses when it goes dormant (unitless). Fraction of biomass the crop loses when it
        goes dormant. Default 0.1 for perennials, 0.3 for trees.
        Reference: SWAT Theoretical 5:1.2, and crop.dat BIO_LEAF description
    minimum_lai_during_dormancy : Optional[float], default 0.75
        Minimum leaf area index for plants (perennials and trees only).
        Note: SWAT Appendix-A section A.1.12 says that the default 0.75 is from pre-2009 versions of SWAT and users are
        now allowed to modify this value. But it does not provide values for any of the listed plant species and gives
        no information about how this value can be measured or calculated.

    The crop quality attributes listed in the base CropData class use the values for Sorghum harvested as a grain.

    """

    # ID variables (SWAT Table A-1 ish)
    species: CropSpecies = None
    name: Optional[str] = "default generic annual crop"
    id: Optional[Any] = None
    plant_category: Optional[PlantCategory] = PlantCategory("cool_annual")
    is_perennial: Optional[bool] = False
    is_nitrogen_fixer: bool = False
    field_proportion: float = 1.0
    is_alive: bool = True

    crop_category: CropCategory = CropCategory.SMALL_GRAIN
    crop_type: CropType = CropType.GRAIN
    storage_type: StorageType = StorageType.DRY

    # Management variables
    planting_year: int = 0
    planting_day: int = 100
    use_heat_scheduling: bool = False
    harvest_heat_fraction: float = 1.10

    # # SWAT Table A-3
    minimum_temperature: float = 0

    # SWAT Table A-4
    max_leaf_area_index: float = 4.0
    senescent_heat_fraction: float = 0.9

    # SWAT Table A-8
    yield_nitrogen_fraction: Optional[float] = 0.2

    # ---- biomass allocation
    leaf_area_index: float = 0.0
    biomass: float = 0
    growth_factor: float = 1.0
    root_fraction: float = 1 / 3
    biomass_growth_max: float = 0.0
    above_ground_biomass: float = 0.1
    root_biomass: Optional[float] = 0.0

    # # ---- growth constraints
    nitrogen: float = 0.0
    optimal_nitrogen: float = 0.0
    phosphorus: float = 0.0
    optimal_phosphorus: float = 0.0

    # ---- heat_units
    potential_heat_units: float = 800
    accumulated_heat_units: float = 0
    is_growing: bool = True
    is_dormant: bool = False

    # ---- leaf area index
    max_canopy_height: float = 2.5

    # ---- nitrogen incorporation
    half_mature_heat_fraction: float = 0.5
    mature_heat_fraction: float = 1.0
    root_depth: float = 1
    optimal_nitrogen_fraction: Optional[float] = None
    total_soil_layers: Optional[int] = None
    accessible_soil_layers: Optional[int] = None
    inaccessible_soil_layers: Optional[int] = None

    # ---- root development
    max_root_depth: float = 2_000

    # ---- water dynamics
    cumulative_evaporation: float = 0.0
    cumulative_transpiration: float = 0.0
    cumulative_potential_evapotranspiration: float = 0.0
    water_deficiency: Optional[float] = None
    max_transpiration: Optional[float] = None
    canopy_water: float = 0
    max_canopy_water_capacity: float = 0.8

    # ---- transpiration
    water_uptake: float = 0.0
    cumulative_water_uptake: float = 0.0

    # ---- yields
    harvest_efficiency: float = 1.0
    dry_matter_percentage: float = 85.689
    lignin_dry_matter_percentage: float = 1.518
    crude_protein_percent: float = 12.481
    non_protein_nitrogen: float = 2.518
    starch: float = 72.586
    adf: float = 3.934
    ndf: float = 6.134
    sugar: float = 2.235
    ash: float = 2.496
    dry_down_fraction: float = 0.2
    optimal_phosphorus_fraction: float = 0.073
    user_harvest_index: Optional[float] = None
    potential_harvest_index: Optional[float] = None
    harvest_index: Optional[float] = None
    cut_biomass: Optional[float] = None
    wet_yield_collected: float = 0.0
    dry_matter_yield_collected: float = 0.0
    yield_residue: float = 0.0
    yield_nitrogen: Optional[float] = None
    yield_phosphorus: Optional[float] = None
    residue_nitrogen: float = 0.0
    residue_phosphorus: float = 0.0
    root_distribution_param_da: float = 145.0
    root_distribution_param_c: float = -1.165

    # ---- dormancy
    dormancy_loss_fraction: Optional[float] = None
    minimum_lai_during_dormancy: Optional[float] = 0.75

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
        if (
            self.plant_category == PlantCategory.PERENNIAL
            or self.plant_category == PlantCategory.PERENNIAL_LEGUME
            or self.plant_category == PlantCategory.TREE
        ):
            self.is_perennial = True

        # set Fixation status
        if (
            self.plant_category == PlantCategory.PERENNIAL_LEGUME
            or self.plant_category == PlantCategory.WARM_ANNUAL_LEGUME
            or self.plant_category == PlantCategory.COOL_ANNUAL_LEGUME
        ):
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
