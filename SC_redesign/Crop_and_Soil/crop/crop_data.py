from dataclasses import dataclass
from typing import Optional, List


@dataclass
class CropData:
    # ---- biomass allocation
    light_extinction: float = 0.65
    """the light extinction coefficient (unitless)"""
    leaf_area_index: float = 1.2
    """leaf area index of the plant (unitless)"""
    light_use_efficiency: float = 20
    """light use efficiency of the plant (dg/MJ)"""
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
    minimum_temperature: float = 15
    """minimum temperature below which plant growth cannot occur (Celsius)"""
    optimal_temperature: float = 22
    """ideal temperature for maximum plant growth (Celsius)"""
    ##growth_factor: float = 1.0  # duplicate
    water_stress: Optional[float] = None
    """water stress for the day (unitless; [0, 1])"""
    temp_stress: Optional[float] = None
    """temperature stress for the day (unitless; [0, 1])"""
    nitrogen_stress: Optional[float] = None
    """nitrogen stress for the day (unitless; [0, 1])"""
    phosphorus_stress: Optional[float] = None
    """phosphorus stress for the day (unitless; [0, 1])"""
    
    # ---- heat_units
    ##minimum_temperature: float = 20 # duplicate
    maximum_temperature: float = 38
    """maximum temperature above which plant growth cannot occur (Celsius)"""
    potential_heat_units: float = 800
    """total heat units required for the plant to reach maturity (unitless)
    """
    accumulated_heat_units: float = 0  # accumulator
    """total heat units accumulated to date (unitless)"""
    is_growing: bool = True  # TODO: not currently using; SWAT 5:2.1.4
    """is the crop currently growing?"""
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
    # fixed attributes (unchanged during simulations)
    first_heat_fraction_point: float = 0.15
    """fraction of the growing season corresponding to the first point on the optimal leaf development 
    curve (unitless)"""
    second_heat_fraction_point: float = 0.50
    """fraction of the growing season corresponding to the second point on the optimal leaf development 
    curve (unitless)"""
    first_leaf_fraction_point: float = 0.01
    """fraction of max leaf area index corresponding to the first point on the optimal leaf development 
    curve (unitless)"""
    second_leaf_fraction_point: float = 0.95
    """fraction of max leaf area index corresponding to the second point on the optimal leaf development 
        curve (unitless)"""
    max_canopy_height: float = 2.5  # m
    """maximum canopy height for the plant (m)"""
    ##growth_factor = 1.0  #duplicate
    max_leaf_area_index: float = 3.0
    """maximum leaf area index for the plant (unitless)"""
    senescent_heat_fraction: float = 0.9
    """the fraction of potential heat units above which the plant goes enters senescence (unitless)"""
    # variable attributes (change throughout simulations)
    ##leaf_area_index = 0 # duplicate
    ##heat_fraction = 0.73 # duplicate
    # empty variables
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
    # constant declarations with defaults (unchanged during simulations)
    half_mature_heat_fraction: float = 0.5
    """expected fraction of potential heat units when the plant is half-way to maturity (unitless)"""
    mature_heat_fraction: float = 1.0
    """fraction of potential heat units accumulated for the plant to date (unitless)"""
    emergence_nitrogen_fraction: float = 0.04
    """expected fraction of plant biomass comprised of nitrogen for the plant at emergence (unitless)"""
    half_mature_nitrogen_fraction: float = 0.03
    """expected fraction of plant biomass comprised of nitrogen for the plant at half-maturity (unitless)"""
    near_mature_nitrogen_fraction: float = 0.02
    """expected fraction of plant biomass comprised of nitrogen for the plant at near-maturity (unitless)"""
    mature_nitrogen_fraction: float = 0.01
    """expected fraction of plant biomass comprised of nitrogen for the plant at maturity (unitless)"""
    nitrogen_distro_param: float = 10
    """nitrogen uptake distribution parameter (unitless)"""
    is_nitrogen_fixer: bool = False
    """is the planta nitrogen fixer?"""
    # current declarations with defaults (change throughout simulations)
    # TODO: what module sets/updates these variables?
    ##nitrogen = 0 # duplicate
    ##heat_fraction = 0.73  # duplicate
    ##biomass = 12.5  # duplicate
    ##biomass_growth_max = 100  # duplicate
    root_depth: float = 1  # arbitrary
    """current depth of the plant roots in the soil (mm)"""
    # empty declarations
    _nitrogen_shapes: Optional[List[float]] = None
    """first and second shape coefficients for the nitrogen uptake equations (unitless)"""
    previous_nitrogen: Optional[float] = None
    """nitrogen stored in plant biomass on the previous day (kg/ha)"""
    optimal_nitrogen_fraction: Optional[float] = None
    """optimal proportion of the plant's biomass comprised of nitrogen for the current growth stage (unitless)"""
    ##optimal_nitrogen = None # duplicate
    potential_nitrogen_uptake: Optional[float] = None
    """potential nitrogen to be taken up by the plant under ideal circumstances for the current day (kg/ha)"""
    total_soil_layers: Optional[int] = None
    """total number of layers in the soil profile (unitless)"""
    accessible_soil_layers: Optional[int] = None
    """number of layers in the soil profile that the plant roots have access to (unitless)"""
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

    # ---- root development
    ##heat_fraction = 1 / 3 #duplicate
    max_root_depth: float = 20
    """maximum depth of roots in the soil (mm)"""
    is_perennial: bool = True
    """is the plant perennial?"""
    ##root_depth = None # duplicate
    ##root_fraction = None #duplicate
    
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
    
    # ---- yields
    # constant attributes
    optimal_harvest_index: float = 3.5
    """expected species-specific optimal harvest index for the plant at maturity under ideal
     growth conditions (unitless)"""
    min_harvest_index: float = 0.2
    """expected species-specific harvest index for the plant under drought conditions; represents minimum harvest index
    allowed for the plant (unitless)"""
    # is_residue_added: bool = False ## not needed?
    harvest_efficiency: float = 1.0
    """efficiency of the harvest operation: the proportion of yield that will be extracted from the field 
    (unitless; [0, 1])"""
    yield_nitrogen_fraction: float = 0.15
    """crop-specific expected fraction of nitrogen in yield (unitless)"""
    yield_phosphorus_fraction: float = 0.08
    """crop-specific expected fraction of phosphorus in yield (unitless)"""

    # temporally variable attributes
    ##heat_fraction = 0.6  # duplicate
    ##water_deficiency = 0.2  # duplicate
    ##above_ground_biomass: float = 15  # kg
    ##biomass = 25  # duplicate
    dry_down_fraction: float = 0.2
    """proportion of plant biomass that is lost to dry-down (unitless; [0, 1])"""
    ##nitrogen = 15  # duplicate
    ##phosphorus = 8  # duplicate
    ##biomass = 100  # duplicate
    ##optimal_nitrogen_fraction = 0.162  # duplicate
    optimal_phosphorus_fraction: float = 0.073
    """optimal proportion of the plant's biomass comprised of nitrogen for the current growth stage (unitless)"""
    # Empty declarations
    user_harvest_index: Optional[float] = None  # TODO: handle user input for this. - GitHub Issue #246
    """a user-specified harvest index (unitless). If given, 'harvest-index-override' is triggered"""
    potential_harvest_index: Optional[float] = None
    """potential harvest index for a given day (unitless)"""
    harvest_index: Optional[float] = None
    """harvest index for a given day; fraction of above-ground plant biomass that is harvestable economic yield
    (unitless)"""
    crop_yield: Optional[float] = None
    """total amount of the desired crop product (kg/ha)"""
    yield_collected: Optional[float] = None
    """amount of the desired crop product to be removed from the field (kg/ha)"""
    yield_residue: Optional[float] = None
    """amount of residue created; unharvested yield (kg/ha)"""
    collected_nitrogen: Optional[float] = None
    """nitrogen contained in the harvested yield (kg/ha)"""
    collected_phosphorus: Optional[float] = None
    """phosphorus contained in the harvested yield (kg/ha)"""

    @property
    def is_mature(self) -> bool:
        """checks if maturity has been reached based on the fraction of potential heat units accumulated"""
        return self.heat_fraction >= 1.0

    @property
    def has_given_harvest_index(self) -> bool:
        """was a user-defined harvest index is given? This triggers a harvest index override"""
        return self.user_harvest_index is not None

    @property
    def is_in_senescence(self) -> bool:
        """check if the plant is in senescence"""
        return self.heat_fraction > self.senescent_heat_fraction
