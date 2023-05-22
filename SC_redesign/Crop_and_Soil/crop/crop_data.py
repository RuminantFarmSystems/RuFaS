from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

from SC_redesign.Crop_and_Soil.crop.harvest_operations import HarvestOperation


class PlantCategory(Enum):
    """Enum of all plant types supported by RuFaS. Listed for supported plant types in SWAT Appendix A, table A-1"""
    WARM_ANNUAL_LEGUME = "warm_annual_legume"
    COOL_ANNUAL_LEGUME = "cool_annual_legume"
    PERENNIAL_LEGUME = "perennial_legume"
    WARM_ANNUAL = "warm_annual"
    COOL_ANNUAL = "cool_annual"
    PERENNIAL = "perennial"
    TREE = "tree"


@dataclass(kw_only=True)
class CropData:
    """Data class containing crop variables.

    Details:
      The kw_only=True argument of the @dataclass decorator specifies that this class' attributes can only be
      initialized with values other than defaults by explicitly including the keyword (i.e, positional arguments are
      disabled).
      For example CropData() will initialize with the default light_extinction value (0.65),
      CropData(light_extinction=0.7) will initialize with the vallue set to 0.7, but CropData(0.65) will not work.
      The upside is that this facilitates dataclass inheritance. For example, the CornData class inherits from CropData
      but will have its values set to different defaults.
    """
    # ID variables (SWAT Table A-1 ish)
    species: Optional[str] = "generic"
    """the species of the crop"""
    name: Optional[str] = "default generic annual crop"
    """the name of this specific crop instance"""
    id: Optional[int] = 0
    """the numeric identifier for this crop instance"""
    plant_code: Optional[str] = None
    """4-letter plant code (used by SWAT)"""
    scientific_name: Optional[str] = None
    """taxonomic name of the plant"""
    plant_category: Optional[PlantCategory] = PlantCategory("cool_annual")
    """Classification of the plant (Reference SWAT crop.dat file, IDC variable"""
    is_perennial: Optional[bool] = False
    """is this plant perennial?"""
    is_nitrogen_fixer: bool = False
    """is the plant a nitrogen fixer?"""
    priority: int = 1
    """this crop's priority level when accessing shared resources in a field containing multiple crops"""
    field_proportion: float = 1.0
    """the proportion of the field that this crop occupies. Should be 1 when this is the only crop in the field"""
    is_alive: bool = True
    """is the crop currently alive in the field?"""

    # Management variables
    planting_year: int = 0
    """the year that this crop was planted"""
    planting_day: int = 100
    """the (julian) day that this crop was planted"""
    next_harvest_year: int = 0
    """the year in which this crop should be harvested next"""
    next_harvest_day: int = 250
    """the (julian) day on which this crop should be harvested next"""
    use_heat_scheduling: bool = False
    """Status indicating if heat unit scheduling will be used to determine harvesting instead of user-specified
    harvest dates"""
    harvest_heat_fraction: float = 1.10
    """the fraction of potential heat units that denotes the optimal growth stage for harvest"""
    is_harvest_day: bool = False
    """Status indicating if today is the day on which harvest operations should occur for this plant"""
    next_harvest_operation: HarvestOperation = HarvestOperation.HARVEST
    """the specific harvest operation to be executed next for this plant"""

    # SWAT Table A-3
    minimum_temperature: float = 0
    """minimum temperature below which plant growth cannot occur (Celsius)"""
    optimal_temperature: float = 25
    """ideal temperature for maximum plant growth (Celsius)"""

    # SWAT Table A-4
    max_leaf_area_index: float = 4.0
    """maximum leaf area index for the plant (unitless)"""
    first_heat_fraction_point: float = 0.15
    """fraction of the growing season corresponding to the first point on the optimal leaf development
    curve (unitless)"""
    first_leaf_fraction_point: float = 0.01
    """fraction of max leaf area index corresponding to the first point on the optimal leaf development
    curve (unitless)"""
    second_heat_fraction_point: float = 0.50
    """fraction of the growing season corresponding to the second point on the optimal leaf development
    curve (unitless)"""
    second_leaf_fraction_point: float = 0.95
    """fraction of max leaf area index corresponding to the second point on the optimal leaf development
        curve (unitless)"""
    senescent_heat_fraction: float = 0.9
    """the fraction of potential heat units above which the plant goes enters senescence (unitless)"""

    # SWAT Table A-5
    light_use_efficiency: float = 30
    """light use efficiency of the plant (dg/MJ)"""
    # light_use_decline_rate: float  # UNUSED (WAVP, $\Delta rue_{dcl}$)
    # stressed_light_use_efficiency  # UNUSED (BIOEHI, $RUE_{hi}$)
    # carbon_dioxide_stress_level = 660 # UNUSED (CO2HI, $CO_{2hi}$)

    # SWAT Table A-6
    minimum_cover_management_factor: float = 0.2
    """minimum value for cover and management factor for water erosion applicable to land cover/plant (unitless) (SWAT
        Reference: 4:1.1.11)
    """

    # SWAT Table A-7
    emergence_nitrogen_fraction: float = 0.05
    """expected fraction of plant biomass comprised of nitrogen for the plant at emergence (unitless)"""
    half_mature_nitrogen_fraction: float = 0.02
    """expected fraction of plant biomass comprised of nitrogen for the plant at half-maturity (unitless)"""
    mature_nitrogen_fraction: float = 0.01
    """expected fraction of plant biomass comprised of nitrogen for the plant at maturity (unitless)"""
    emergence_phosphorus_fraction: float = 0.005
    """expected fraction of plant biomass comprised of phosphorus for the plant at emergence (unitless)"""
    half_mature_phosphorus_fraction: float = 0.003
    """expected fraction of plant biomass comprised of phosphorus for the plant at half-maturity (unitless)"""
    mature_phosphorus_fraction: float = 0.002
    """expected fraction of plant biomass comprised of phosphorus for the plant at maturity (unitless)"""

    # SWAT Table A-8
    optimal_harvest_index: float = 0.5
    """expected species-specific optimal harvest index for the plant at maturity under ideal
     growth conditions (unitless)"""
    min_harvest_index: float = 0.2
    """expected species-specific harvest index for the plant under drought conditions; represents minimum harvest index
    allowed for the plant (unitless)"""
    yield_nitrogen_fraction: Optional[float] = 0.2
    """crop-specific expected fraction of nitrogen in yield (unitless)"""
    yield_phosphorus_fraction: Optional[float] = 0.003
    """crop-specific expected fraction of phosphorus in yield (unitless)"""

    # ---- biomass allocation
    light_extinction: float = 0.65
    """the light extinction coefficient (unitless)"""
    leaf_area_index: float = 0.0
    """leaf area index of the plant (unitless)"""
    biomass: float = 0
    """total plant biomass (kg/ha)"""
    growth_factor: float = 1.0
    """growth factor multiplier for the plant (unitless; [0, 1])"""
    root_fraction: float = 1 / 3
    """proportion of plant biomass that is stored below ground in roots (unitless)"""
    usable_light: Optional[float] = None
    """solar radiation captured for photosynthesis during the day (MJ/m^2)"""
    biomass_growth_max: Optional[float] = None
    """upper-limit of biomass accumulation for the day (kg/ha)"""
    biomass_growth: Optional[float] = None
    """biomass accumulated by the plant during the day (kg/ha)"""
    previous_biomass: Optional[float] = None
    """biomass accumulated by the plant on the previous day (kg/ha)"""
    above_ground_biomass: Optional[float] = None
    """biomass stored in the above ground portion of the plant; plant biomass excluding roots (kg/ha)"""
    root_biomass: Optional[float] = None
    """biomass stored in roots (kg/ha)"""

    # ---- growth constraints
    water_uptake: float = 18
    """water taken up by the plant for the day (mm)"""
    nitrogen: float = 35
    """nitrogen stored in plant biomass (kg/ha)"""
    optimal_nitrogen: float = 100
    """optimal amount of nitrogen stored in the plant for the current growth stage (kg/ha)"""
    phosphorus: float = 20
    """phosphorus stored in plant biomass (kg/ha)"""
    optimal_phosphorus: float = 80
    """optimal amount of phosphorus stored in the plant for the current growth stage (kg/ha)"""
    water_stress: Optional[float] = None
    """water stress for the day (unitless; [0, 1])"""
    temp_stress: Optional[float] = None
    """temperature stress for the day (unitless; [0, 1])"""
    nitrogen_stress: Optional[float] = None
    """nitrogen stress for the day (unitless; [0, 1])"""
    phosphorus_stress: Optional[float] = None
    """phosphorus stress for the day (unitless; [0, 1])"""

    # ---- heat_units
    maximum_temperature: float = 38
    """maximum temperature above which plant growth cannot occur (Celsius)"""
    potential_heat_units: float = 800
    """total heat units required for the plant to reach maturity (unitless)"""
    accumulated_heat_units: float = 0  # accumulator
    """total heat units accumulated to date (unitless)"""
    is_dormant: bool = False
    """is the crop currently dormant?"""
    use_heat_unit_temperature: bool = False
    """should the alternative heat unit method be used?
    Determines if heat unit temperature will be used for heat unit  accumulation."""
    new_heat_units: Optional[float] = None
    """heat units accumulated on the current day; degrees C above minimum growth temperature (Celsius*)"""
    heat_fraction: Optional[float] = None
    """fraction of potential heat units accumulated to date (unitless)"""
    minimum_heat_unit_temperature: Optional[float] = None
    """minimum temperature used for heat unit calculations during the alternative heat unit method (Celsius)"""
    maximum_heat_unit_temperature: Optional[float] = None
    """maximum temperature used for heat unit calculations during the alternative heat unit method (Celsius)"""
    heat_unit_temperature: Optional[float] = None
    """heat unit temperature used by alternative heat unit method (Celsius)"""
    previous_heat_fraction: Optional[float] = None
    """fraction of potential heat units on the previous day (unitless)"""

    # ---- leaf area index
    max_canopy_height: float = 2.5  # m
    """maximum canopy height for the plant (m)"""
    _lai_shapes: Optional[float] = None
    """shape coefficients used to calculate fraction of max leaf area index (unitless)."""
    optimal_leaf_area_fraction: Optional[float] = None
    """fraction of the plant's maximum leaf area index corresponding to the current heat fraction (unitless)"""
    canopy_height: Optional[float] = None
    """current height of the plant (m)"""
    leaf_area_added: Optional[float] = None
    """leaf area index change during the day; corrected for growth constraints (unitless)"""
    optimal_leaf_area_change: Optional[float] = None
    """leaf area index added under ideal conditions for the day; not corrected for growth constraints (unitless)"""
    previous_leaf_area_index: Optional[float] = None
    """leaf area index on the previous day (unitless)"""
    previous_optimal_leaf_area_fraction: Optional[float] = None
    """optimal leaf area fraction on the previous day (unitless)"""

    # ---- nitrogen incorporation
    half_mature_heat_fraction: float = 0.5
    """expected fraction of potential heat units when the plant is half-way to maturity (unitless)"""
    mature_heat_fraction: float = 1.0
    """fraction of potential heat units accumulated for the plant to date (unitless)"""
    near_mature_nitrogen_fraction: float = 0.02
    """expected fraction of plant biomass comprised of nitrogen for the plant at near-maturity (unitless)"""
    nitrogen_distro_param: float = 10
    """nitrogen uptake distribution parameter (unitless)"""
    root_depth: float = 1  # arbitrary
    """current depth of the plant roots in the soil (mm)"""
    nitrogen_shapes: Optional[List[float]] = None
    """first and second shape coefficients for the nitrogen uptake equations (unitless)"""
    previous_nitrogen: Optional[float] = None
    """nitrogen stored in plant biomass on the previous day (kg/ha)"""
    optimal_nitrogen_fraction: Optional[float] = None
    """optimal proportion of the plant's biomass comprised of nitrogen for the current growth stage (unitless)"""
    potential_nitrogen_uptake: Optional[float] = None
    """potential nitrogen to be taken up by the plant under ideal circumstances for the current day (kg/ha)"""
    total_soil_layers: Optional[int] = None
    """total number of layers in the soil profile (unitless)"""
    accessible_soil_layers: Optional[int] = None
    """number of layers in the soil profile that the plant roots have access to (unitless)"""
    accessible_depths: Optional[List[float]] = None
    """slice of soil layer boundaries to which the plant has access (mm)"""
    inaccessible_soil_layers: Optional[int] = None
    """number of layers in the soil profile that the plant roots do not have access to (unitless)"""
    layer_nitrogen_potentials: Optional[float] = None
    """potential nitrogen uptake from each soil layer (kg/ha)"""
    unmet_nitrogen_demands: Optional[float] = None
    """plant nitrogen demands that remain unmet by the overlaying soil layers (kg/ha)"""
    nitrogen_requests: Optional[float] = None
    """amount of nitrogen requested from each soil layer by the plant (kg/ha)"""
    actual_nitrogen_uptakes: Optional[List[float]] = None
    """actual nitrogen to be taken up by the plant from each soil layer (kg/ha)"""
    total_nitrogen_uptake: Optional[float] = None
    """total nitrogen to be taken up by the plant (kg/ha)"""
    fixed_nitrogen: Optional[float] = None
    """total amount of nitrogen fixed by the plant (kg/ha)"""
    nitrate_factor: Optional[float] = None
    """soil nitrate factor (unitless; [0, 1])"""
    fixation_stage_factor: Optional[float] = None
    """growth stage factor of the nitrogen fixing symbiotes for the current plant growth stage (unitless)"""

    # --- phosphorus incorporation ----
    near_mature_phosphorus_fraction: float = 0.3
    """expected fraction of plant biomass comprised of nitrogen for the plant near maturity (unitless)"""
    phosphorus_distro_param: float = 10
    """phosphorus uptake distribution parameter (unitless)"""
    phosphorus_shapes: Optional[List[float]] = None
    """first and second shape coefficients for the nitrogen uptake equations (unitless)"""
    previous_phosphorus: Optional[float] = None
    """phosphorus value on the previous day (kg/ha)"""
    total_phosphorus_uptake: Optional[float] = None
    """total amount of phosphorus taken up by the plant"""
    potential_phosphorus_uptake: Optional[float] = None
    """potential phosphorus to be taken up by the plant under ideal circumstances for the current day (kg/ha)"""
    actual_phosphorus_uptakes: Optional[List[float]] = None
    """actual phosphorus to be taken up by the plant from each soil layer (kg/ha)"""

    # ---- root development
    max_root_depth: float = 20
    """maximum depth of roots in the soil (mm)"""

    # ---- water dynamics
    cumulative_evaporation: Optional[float] = None
    """total water lost to evaporation by the plant during the growing season (mm)"""
    cumulative_transpiration: Optional[float] = None
    """total water lost to transpiration by the plant during the growing season (mm)"""
    cumulative_evapotranspiration: Optional[float] = None
    """total water lost to evapotranspiration by the plant during the growing season (mm)"""
    cumulative_potential_evapotranspiration: Optional[float] = None
    """total expected maximum water loss by the plant during the growing season (mm)"""
    water_deficiency: Optional[float] = None
    """water deficiency factor for the plant (unitless)"""
    max_transpiration: Optional[float] = None
    """maximum transpiration on a given day (mm)"""
    evapotranspiration_weighting_coefficient: float = 1
    """plant evapotranspiration curve number coefficient (unitless), in the range 0.5 to 2.0 inclusive(?).
        Used in SWAT equation 2:1.1.9, definition in .bsn input data description (named CNCOEF there)"""
    canopy_water: float = 0
    """Amount of water currently held in the canopy (mm)"""
    max_canopy_water_capacity: float = 0.8
    """Maximum amount of water that can be trapped in canopy on a given day when fully developed (mm).
        References: SWAT Theoretical documentation eqn. 2:2.1.1 (see also SWAT Input file .HRU ("CANMX" page 233).
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
    """water-use distribution parameter governing water-uptake from the soil. Defaults to 10 for all crops in SWAT
    (unitless)."""
    potential_water_uptakes: Optional[List[float]] = None
    """the maximum amount of water to be potentially taken up by a crop, from each soil layer (mm)"""
    water_compensation_factor: float = 0.01
    """factor that determines the ability of a plant to draw water from deeper layers when demands are not met
    (unitless). 0 indicates no water can be drawn from deeper than expected and 1 indicates that any and all water
    can be drawn from deeper layers."""
    unmet_water_demands: Optional[List[float]] = None
    """cumulative water demands not met by all previous layers"""
    actual_water_uptakes: Optional[List[float]] = None
    """the actual amount of water to be removed from the soil"""
    total_water_uptake: float = 0
    """Total amount of water the plant took from the soil on the current day (mm)"""

    # ---- yields
    harvest_efficiency: float = 1.0
    """efficiency of the harvest operation: the proportion of yield that will be extracted from the field
    (unitless; [0, 1])"""
    dry_down_fraction: float = 0.2
    """proportion of plant biomass that is lost to dry-down (unitless; [0, 1])"""
    optimal_phosphorus_fraction: float = 0.073
    """optimal proportion of the plant's biomass comprised of nitrogen for the current growth stage (unitless)"""
    user_harvest_index: Optional[float] = None  # TODO: handle user input for this. - GitHub Issue #246
    """a user-specified harvest index (unitless). If given, 'harvest-index-override' is triggered"""
    potential_harvest_index: Optional[float] = None
    """potential harvest index for a given day (unitless)"""
    harvest_index: Optional[float] = None
    """harvest index for a given day; fraction of above-ground plant biomass that is harvestable economic yield
    (unitless)"""
    cut_biomass: Optional[float] = None
    """total amount of the desired crop product (kg/ha)"""
    yield_collected: Optional[float] = None
    """amount of the desired crop product to be removed from the field (kg/ha)"""
    yield_residue: Optional[float] = None
    """amount of residue created; unharvested yield (kg/ha)"""
    yield_nitrogen: Optional[float] = None
    """nitrogen contained in the harvested yield (kg/ha)"""
    yield_phosphorus: Optional[float] = None
    """phosphorus contained in the harvested yield (kg/ha)"""
    residue_nitrogen: Optional[float] = None
    """amount of nitrogen in the residue from this plant (kg/ha)"""
    residue_phosphorus: Optional[float] = None
    """amount of phosphorus in the residue from this plant (kg/ha)"""

    # ---- dormancy
    dormancy_loss_fraction: Optional[float] = None
    """Fraction of biomass the crop loses when it goes dormant. Default 0.1 for perennials, 0.3 for trees
        Reference: SWAT Theoretical 5:1.2, and crop.dat BIO_LEAF description"""
    minimum_lai_during_dormancy: Optional[float] = 0.75
    """Minimum leaf area index for plants (perennials and trees only) during dormancy (unitless)

    Note: SWAT Appendix-A section A.1.12 says that the default 0.75 is from pre-2009 versions of SWAT and users are
    now allowed to modify this value. But it does not provide values for any of the listed plant species and gives no
    information about how this value can be measured or calculated.
    """

    def __post_init__(self):
        """Initialize all attributes with defaults that depend on other attributes"""

        # Set dormancy loss
        if self.plant_category == PlantCategory.PERENNIAL or PlantCategory.PERENNIAL_LEGUME:
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
        """checks if maturity has been reached based on the fraction of potential heat units accumulated

        References
        ----------
        SWAT Theoretical documentation section 5:2.1.4
        """
        return self.heat_fraction >= 1.0

    @property
    def is_growing(self) -> bool:
        """Indicates if the plant is in its growing season.
        """
        return not self.is_mature and not self.is_dormant and self.is_alive

    @property
    def do_harvest_index_override(self) -> bool:
        """was a user-defined harvest index is given? This triggers a harvest index override"""
        return self.user_harvest_index is not None

    @property
    def is_in_senescence(self) -> bool:
        """check if the plant is in senescence"""
        return self.heat_fraction > self.senescent_heat_fraction

    @property
    def water_canopy_storage_capacity(self) -> float:
        """Maximum amount of water that can be held in the canopy (mm).

        References
        ----------
        SWAT Theoretical documentation eqn. 2:2.1.1

        """
        return self.max_canopy_water_capacity * (self.leaf_area_index / self.max_leaf_area_index)


"""
The species child classes provide default configuration for the supported CropSpecies.
Only values that differ from the default CropData need to be declared by default in these species classes.

Users should be able also be able to modify specific variables by including them in the signature when calling
the species classes.

Attribute values are taken from the SWAT database: https://swat.tamu.edu/media/69419/Appendix-A.pdf
This "database" is actually a PDF with tables for broad groupings of paramters. Therefore, the
attributes in this class are grouped in line with those tables, for ease of entering the data.
"""


@dataclass(kw_only=True)
class Corn(CropData):
    """crop data class with default values for corn"""
    species: str = "corn"
    name: str = "default corn"
    plant_code: str = "CORN"
    scientific_name: str = "Zea mays"
    plant_category: PlantCategory = PlantCategory("warm_annual")
    is_nitrogen_fixer: bool = False

    minimum_temperature: float = 8.0
    optimal_temperature: float = 25.0

    max_leaf_area_index: float = 3.0
    first_heat_fraction_point: float = 0.15
    first_leaf_fraction_point: float = 0.05
    second_heat_fraction_point: float = 0.50
    second_leaf_fraction_point: float = 0.95
    senescent_heat_fraction: float = 0.90

    light_use_efficiency: float = 39.0

    emergence_nitrogen_fraction: float = 0.0470
    half_mature_nitrogen_fraction: float = 0.0177
    mature_nitrogen_fraction: float = 0.0138
    emergence_phosphorus_fraction: float = 0.0048
    half_mature_phosphorus_fraction: float = 0.0018
    mature_phosphorus_fraction: float = 0.0014

    optimal_harvest_index: float = 0.50
    min_harvest_index: float = 0.30
    yield_nitrogen_fraction: float = 0.0140
    yield_phosphorus_fraction: float = 0.0016


@dataclass(kw_only=True)
class SpringWheat(CropData):
    """crop data class with default values for spring wheat"""
    species: str = "spring_wheat"
    name: str = "default spring_wheat"
    plant_code: str = "SWHT"
    scientific_name: str = "Triticum aestivum"
    plant_category: PlantCategory = PlantCategory("cool_annual")
    is_nitrogen_fixer: bool = False

    minimum_temperature: float = 0.0
    optimal_temperature: float = 18.0

    max_leaf_area_index: float = 4.0
    first_heat_fraction_point: float = 0.15
    first_leaf_fraction_point: float = 0.05
    second_heat_fraction_point: float = 0.50
    second_leaf_fraction_point: float = 0.95
    senescent_heat_fraction: float = 0.90

    light_use_efficiency: float = 35.0

    emergence_nitrogen_fraction: float = 0.0600
    half_mature_nitrogen_fraction: float = 0.0231
    mature_nitrogen_fraction: float = 0.0134
    emergence_phosphorus_fraction: float = 0.0084
    half_mature_phosphorus_fraction: float = 0.0032
    mature_phosphorus_fraction: float = 0.0019

    optimal_harvest_index: float = 0.42
    min_harvest_index: float = 0.20
    yield_nitrogen_fraction: float = 0.0234
    yield_phosphorus_fraction: float = 0.0033


@dataclass(kw_only=True)
class WinterWheat(CropData):
    """crop data class with default values for winter wheat"""
    species: str = "winter_wheat"
    name: str = "default winter_wheat"
    plant_code: str = "WWHT"
    scientific_name: str = "Triticum aestivum"
    plant_category: PlantCategory = PlantCategory("cool_annual")
    is_nitrogen_fixer: bool = False

    minimum_temperature: float = 0.0
    optimal_temperature: float = 18.0

    max_leaf_area_index: float = 4.0
    first_heat_fraction_point: float = 0.05
    first_leaf_fraction_point: float = 0.05
    second_heat_fraction_point: float = 0.45
    second_leaf_fraction_point: float = 0.95
    senescent_heat_fraction: float = 0.90

    light_use_efficiency: float = 30.0

    emergence_nitrogen_fraction: float = 0.0663
    half_mature_nitrogen_fraction: float = 0.0255
    mature_nitrogen_fraction: float = 0.0148
    emergence_phosphorus_fraction: float = 0.0053
    half_mature_phosphorus_fraction: float = 0.0020
    mature_phosphorus_fraction: float = 0.0012

    optimal_harvest_index: float = 0.40
    min_harvest_index: float = 0.20
    yield_nitrogen_fraction: float = 0.0250
    yield_phosphorus_fraction: float = 0.0022


@dataclass(kw_only=True)
class CerealRye(CropData):
    """crop data class with default values for cereal rye"""
    species: str = "cereal_rye"
    name: str = "default cereal_rye"
    plant_code: str = "RYE"
    scientific_name: str = "Secale cereale"
    plant_category: PlantCategory = PlantCategory("cool_annual")
    is_nitrogen_fixer: bool = False

    minimum_temperature: float = 0
    optimal_temperature: float = 12.5

    max_leaf_area_index: float = 4.0
    first_heat_fraction_point: float = 0.15
    first_leaf_fraction_point: float = 0.01
    second_heat_fraction_point: float = 0.50
    second_leaf_fraction_point: float = 0.95
    senescent_heat_fraction: float = 0.80

    light_use_efficiency: float = 35.0

    emergence_nitrogen_fraction: float = 0.0600
    half_mature_nitrogen_fraction: float = 0.0231
    mature_nitrogen_fraction: float = 0.0130
    emergence_phosphorus_fraction: float = 0.0084
    half_mature_phosphorus_fraction: float = 0.0032
    mature_phosphorus_fraction: float = 0.0019

    optimal_harvest_index: float = 0.40
    min_harvest_index: float = 0.20
    yield_nitrogen_fraction: float = 0.0284
    yield_phosphorus_fraction: float = 0.0042


@dataclass(kw_only=True)
class SpringBarley(CropData):
    """crop data class with default values for spring barley"""
    species: str = "spring_barley"
    name: str = "default spring_barley"
    plant_code: str = "BARL"
    scientific_name: str = "Hordeum vulgare"
    plant_category: PlantCategory = PlantCategory("cool_annual")
    is_nitrogen_fixer: bool = False

    minimum_temperature: float = 0.0
    optimal_temperature: float = 25.0

    max_leaf_area_index: float = 4.0
    first_heat_fraction_point: float = 0.15
    first_leaf_fraction_point: float = 0.01
    second_heat_fraction_point: float = 0.45
    second_leaf_fraction_point: float = 0.95
    senescent_heat_fraction: float = 0.90

    light_use_efficiency: float = 35.0

    emergence_nitrogen_fraction: float = 0.0590
    half_mature_nitrogen_fraction: float = 0.0226
    mature_nitrogen_fraction: float = 0.0131
    emergence_phosphorus_fraction: float = 0.0057
    half_mature_phosphorus_fraction: float = 0.0022
    mature_phosphorus_fraction: float = 0.0013

    optimal_harvest_index: float = 0.54
    min_harvest_index: float = 0.20
    yield_nitrogen_fraction: float = 0.0210
    yield_phosphorus_fraction: float = 0.0017


@dataclass(kw_only=True)
class FallOats(CropData):
    """crop data class with default values for fall oats"""
    species: str = "fall_oats"
    name: str = "default fall_oats"
    plant_code: str = "OATS"
    scientific_name: str = "Avena sativa"
    plant_category: PlantCategory = PlantCategory("cool_annual")
    is_nitrogen_fixer: bool = False

    minimum_temperature: float = 0.0
    optimal_temperature: float = 15.0

    max_leaf_area_index: float = 4.0
    first_heat_fraction_point: float = 0.15
    first_leaf_fraction_point: float = 0.02
    second_heat_fraction_point: float = 0.50
    second_leaf_fraction_point: float = 0.95
    senescent_heat_fraction: float = 0.90

    light_use_efficiency: float = 35.0

    emergence_nitrogen_fraction: float = 0.0600
    half_mature_nitrogen_fraction: float = 0.0231
    mature_nitrogen_fraction: float = 0.0134
    emergence_phosphorus_fraction: float = 0.0084
    half_mature_phosphorus_fraction: float = 0.0032
    mature_phosphorus_fraction: float = 0.0019

    optimal_harvest_index: float = 0.42
    min_harvest_index: float = 0.175
    yield_nitrogen_fraction: float = 0.0316
    yield_phosphorus_fraction: float = 0.0057


@dataclass(kw_only=True)
class TallFescue(CropData):
    """crop data class with default values for tall fescue"""
    species: str = "tall_fescue"
    name: str = "default tall_fescue"
    plant_code: str = "FESC"
    scientific_name: str = "Festuca arundinaceae"
    plant_category: PlantCategory = PlantCategory("perennial")
    is_nitrogen_fixer: bool = False

    minimum_temperature: float = 0.0
    optimal_temperature: float = 15.0

    max_leaf_area_index: float = 4.0
    first_heat_fraction_point: float = 0.15
    first_leaf_fraction_point: float = 0.01
    second_heat_fraction_point: float = 0.50
    second_leaf_fraction_point: float = 0.95
    senescent_heat_fraction: float = 0.80

    light_use_efficiency: float = 30.0

    emergence_nitrogen_fraction: float = 0.0560
    half_mature_nitrogen_fraction: float = 0.0210
    mature_nitrogen_fraction: float = 0.0120
    emergence_phosphorus_fraction: float = 0.0099
    half_mature_phosphorus_fraction: float = 0.0022
    mature_phosphorus_fraction: float = 0.0019

    optimal_harvest_index: float = 0.90
    min_harvest_index: float = 0.90
    yield_nitrogen_fraction: float = 0.0234
    yield_phosphorus_fraction: float = 0.0033


@dataclass(kw_only=True)
class Alfalfa(CropData):
    """crop data class with default values for alfalfa"""
    species: str = "alfalfa"
    name: str = "default alfalfa"
    plant_code: str = "ALFA"
    scientific_name: str = "Medicago sativa"
    plant_category: PlantCategory = PlantCategory("perennial_legume")
    is_nitrogen_fixer: bool = True

    minimum_temperature: float = 4.0
    optimal_temperature: float = 25.0

    max_leaf_area_index: float = 4.0
    first_heat_fraction_point: float = 0.15
    first_leaf_fraction_point: float = 0.01
    second_heat_fraction_point: float = 0.50
    second_leaf_fraction_point: float = 0.95
    senescent_heat_fraction: float = 0.90

    light_use_efficiency: float = 20.0

    emergence_nitrogen_fraction: float = 0.0417
    half_mature_nitrogen_fraction: float = 0.0290
    mature_nitrogen_fraction: float = 0.0200
    emergence_phosphorus_fraction: float = 0.0035
    half_mature_phosphorus_fraction: float = 0.0028
    mature_phosphorus_fraction: float = 0.0020

    optimal_harvest_index: float = 0.90
    min_harvest_index: float = 0.90
    yield_nitrogen_fraction: float = 0.0250
    yield_phosphorus_fraction: float = 0.0035


@dataclass(kw_only=True)
class Soybean(CropData):
    """crop data class with default values for soy bean"""
    species: str = "soybean"
    name: str = "default soybean"
    plant_code: str = "SOYB"
    scientific_name: str = "Glycine max"
    plant_category: PlantCategory = PlantCategory("warm_annual_legume")
    is_nitrogen_fixer: bool = True

    minimum_temperature: float = 10.0
    optimal_temperature: float = 25.0

    max_leaf_area_index: float = 3.0
    first_heat_fraction_point: float = 0.15
    first_leaf_fraction_point: float = 0.05
    second_heat_fraction_point: float = 0.50
    second_leaf_fraction_point: float = 0.95
    senescent_heat_fraction: float = 0.90

    light_use_efficiency: float = 25.0

    emergence_nitrogen_fraction: float = 0.0524
    half_mature_nitrogen_fraction: float = 0.0265
    mature_nitrogen_fraction: float = 0.0258
    emergence_phosphorus_fraction: float = 0.0074
    half_mature_phosphorus_fraction: float = 0.0037
    mature_phosphorus_fraction: float = 0.0035

    optimal_harvest_index: float = 0.31
    min_harvest_index: float = 0.01
    yield_nitrogen_fraction: float = 0.0650
    yield_phosphorus_fraction: float = 0.0091


@dataclass(kw_only=True)
class SugarBeet(CropData):
    """crop data class with default values for sugar beet"""
    species: str = "sugar_beet"
    name: str = "default sugar_beet"
    plant_code: str = "SGBT"
    scientific_name: str = "Beta vulgaris saccharifera"
    plant_category: PlantCategory = PlantCategory("warm_annual")
    is_nitrogen_fixer: bool = False

    minimum_temperature: float = 4.0
    optimal_temperature: float = 18.0

    max_leaf_area_index: float = 5.0
    first_heat_fraction_point: float = 0.05
    first_leaf_fraction_point: float = 0.05
    second_heat_fraction_point: float = 0.50
    second_leaf_fraction_point: float = 0.95
    senescent_heat_fraction: float = 0.90

    light_use_efficiency: float = 30.0

    emergence_nitrogen_fraction: float = 0.0550
    half_mature_nitrogen_fraction: float = 0.0200
    mature_nitrogen_fraction: float = 0.0120
    emergence_phosphorus_fraction: float = 0.0060
    half_mature_phosphorus_fraction: float = 0.0025
    mature_phosphorus_fraction: float = 0.0019

    optimal_harvest_index: float = 2.00
    min_harvest_index: float = 1.10
    yield_nitrogen_fraction: float = 0.0130
    yield_phosphorus_fraction: float = 0.0020


@dataclass(kw_only=True)
class Potato(CropData):
    """crop data class with default values for potato"""
    species: str = "potato"
    name: str = "default potato"
    plant_code: str = "POTA"
    scientific_name: str = "Solanum tuberosum"
    plant_category: PlantCategory = PlantCategory("cool_annual")
    is_nitrogen_fixer: bool = False

    minimum_temperature: float = 7.0
    optimal_temperature: float = 22.0

    max_leaf_area_index: float = 4.0
    first_heat_fraction_point: float = 0.15
    first_leaf_fraction_point: float = 0.01
    second_heat_fraction_point: float = 0.50
    second_leaf_fraction_point: float = 0.95
    senescent_heat_fraction: float = 0.90

    light_use_efficiency: float = 25.0

    emergence_nitrogen_fraction: float = 0.0550
    half_mature_nitrogen_fraction: float = 0.0200
    mature_nitrogen_fraction: float = 0.0120
    emergence_phosphorus_fraction: float = 0.0060
    half_mature_phosphorus_fraction: float = 0.0025
    mature_phosphorus_fraction: float = 0.0019

    optimal_harvest_index: float = 0.95
    min_harvest_index: float = 0.95
    yield_nitrogen_fraction: float = 0.0246
    yield_phosphorus_fraction: float = 0.0023


@dataclass(kw_only=True)
class Triticale(CropData):
    """crop data class with default values for triticale"""
    # TODO: triticale has unknown parameters, since it is not present in SWAT database.
    #     Durum wheat is likely the closest analog.
