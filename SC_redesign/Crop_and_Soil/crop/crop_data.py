from dataclasses import dataclass
from typing import Optional


@dataclass
class CropData:
    # ---- biomass allocation
    light_extinction: float = 0.65
    leaf_area_index: float = 1.2
    light_conversion: float = 20
    biomass: float = 0
    growth_factor: float = 1.0
    root_fraction: float = 1 / 3
    usable_light: Optional[float] = None
    biomass_growth_max: Optional[float] = None
    biomass_growth: Optional[float] = None
    previous_biomass: Optional[float] = None
    green_biomass: Optional[float] = None
    root_biomass: Optional[float] = None
    
    # ---- growth constraints
    water_uptake: float = 18
    nitrogen: float = 35
    optimal_nitrogen: float = 100
    phosphorus: float = 20
    optimal_phosphorus: float = 80
    minimum_temperature: float = 15
    optimal_temperature: float = 22
    ##growth_factor: float = 1.0  # duplicate
    water_stress: Optional[float] = None
    temp_stress: Optional[float] = None
    nitrogen_stress: Optional[float] = None
    phosphorus_stress: Optional[float] = None
    
    # ---- heat_units
    ##minimum_temperature: float = 20 # duplicate
    maximum_temperature: float = 38
    potential_heat_units: float = 800
    accumulated_heat_units: float = 0  # accumulator
    is_growing: bool = True  # TODO: not currently using; SWAT 5:2.1.4
    use_heat_unit_temperature: bool = False
    """determines if heat unit temperature will be used for heat unit 
    accumulation."""
    new_heat_units: Optional[float] = None
    heat_fraction: Optional[float] = None
    minimum_heat_unit_temperature: Optional[float] = None
    maximum_heat_unit_temperature: Optional[float] = None
    heat_unit_temperature: Optional[float] = None
    previous_heat_fraction: Optional[float] = None
    
    # ---- leaf area index
    # fixed attributes (unchanged during simulations)
    first_heat_fraction_point: float = 0.15
    second_heat_fraction_point: float = 0.50
    first_leaf_fraction_point: float = 0.01
    second_leaf_fraction_point: float = 0.95
    max_canopy_height: float = 2.5  # m
    ##growth_factor = 1.0  #duplicate
    max_leaf_area_index: float = 3.0
    senescent_heat_fraction: float = 0.9
    # variable attributes (change throughout simulations)
    ##leaf_area_index = 0 # duplicate
    ##heat_fraction = 0.73 # duplicate
    # empty variables
    _lai_shapes: Optional[float] = None
    optimal_leaf_area_fraction: Optional[float] = None
    canopy_height: Optional[float] = None
    leaf_area_added: Optional[float] = None
    max_leaf_area_change: Optional[float] = None
    previous_leaf_area_index: Optional[float] = None
    previous_optimal_leaf_area_fraction: Optional[float] = None
    
    # ---- nitrogen incorporation
    # constant declarations with defaults (unchanged during simulations)
    half_mature_heat_fraction: float = 0.5
    mature_heat_fraction: float = 1.0
    emergence_nitrogen_fraction: float = 0.04
    half_mature_nitrogen_fraction: float = 0.03
    near_mature_nitrogen_fraction: float = 0.02
    mature_nitrogen_fraction: float = 0.01
    nitrogen_distro_param: float = 10
    is_nitrogen_fixer: bool = False
    # current declarations with defaults (change throughout simulations)
    # TODO: what module sets/updates these variables?
    ##nitrogen = 0 # duplicate
    ##heat_fraction = 0.73  # duplicate
    ##biomass = 12.5  # duplicate
    ##biomass_growth_max = 100  # duplicate
    root_depth: float = 1  # arbitrary
    # empty declarations
    previous_nitrogen: Optional[float] = None
    shapes_nitrogen_uptake: Optional[float] = None
    optimal_nitrogen_fraction: Optional[float] = None
    ##optimal_nitrogen = None # duplicate
    potential_nitrogen_uptake: Optional[float] = None
    total_soil_layers: Optional[float] = None
    accessible_soil_layers: Optional[float] = None
    inaccessible_soil_layers: Optional[float] = None
    layer_nitrogen_potentials: Optional[float] = None
    unmet_nitrogen_demands: Optional[float] = None
    nitrogen_requests: Optional[float] = None
    actual_nitrogen_uptakes: Optional[float] = None
    total_nitrogen_uptake: Optional[float] = None
    fixed_nitrogen: Optional[float] = None
    nitrate_factor: Optional[float] = None
    fixation_stage_factor: Optional[float] = None

    # ---- root development
    ##heat_fraction = 1 / 3 #duplicate
    max_root_depth: float = 20
    is_perennial: bool = True
    ##root_depth = None # duplicate
    ##root_fraction = None #duplicate
    
    # ---- water dynamics
    evaporation: Optional[float] = None
    transpiration: Optional[float] = None
    evapotranspiration: Optional[float] = None
    evapotranspiration_max: Optional[float] = None
    water_deficiency: Optional[float] = None
    
    # ---- yields
    # constant attributes
    optimal_harvest_index: float = 3.5
    min_harvest_index: float = 0.2
    is_residue_added: bool = False
    harvest_efficiency: float = 1.0
    yield_nitrogen_fraction: float = 0.15
    """crop-specific expected fraction of nitrogen in yield"""
    yield_phosphorus_fraction: float = 0.08
    """crop-specific expected fraction of phosphorus in yield"""

    # temporally variable attributes
    ##heat_fraction = 0.6  # duplicate
    ##water_deficiency = 0.2  # duplicate
    above_ground_biomass: float = 15  # kg
    ##biomass = 25  # duplicate
    dry_down_percent: float = 0.2
    ##nitrogen = 15  # duplicate
    ##phosphorus = 8  # duplicate
    ##biomass = 100  # duplicate
    ##optimal_nitrogen_fraction = 0.162  # duplicate
    optimal_phosphorus_fraction: float = 0.073
    # Empty declarations
    user_harvest_index: Optional[float] = None  # TODO: handle user input for this. - GitHub Issue #246
    potential_harvest_index: Optional[float] = None
    harvest_index: Optional[float] = None
    crop_yield: Optional[float] = None
    """total amount (kg/ha) of the desired crop product"""
    yield_collected: Optional[float] = None
    """amount (kg/ha) of the desired crop product to be removed from the field"""
    residue_created: Optional[float] = None
    """amount (kg/ha) of residue created (yield left in field)"""
    collected_nitrogen: Optional[float] = None
    collected_phosphorus: Optional[float] = None
