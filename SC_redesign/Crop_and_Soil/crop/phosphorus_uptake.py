from math import log, exp
from typing import List
from SC_redesign.Crop_and_Soil.soil.soil import Soil

class PhosphorusUptake:
    def __init__(self):

        #these attrs DO need initial values
        self.actual_phosphorus_biomass = None       #bio_P
        self.potential_phosphorus_uptake = None     #P_up
        self.mature_fractional_phosphorus = None    #fr_p3
        self.potential_phosphorus_biomass_increase = None  #d_biomass_max    ##i think clay has a diff name for this
        self.previous_actual_biomass = None         #prev_biomass_actual
        self.emergent_fractional_phosphorus = None  #fr_p1
        self.previous_fraction_potential_heat_units = None #prev_fr_PHU
        self.fraction_potential_heat_units_half_maturity = None #fr_PHU_50
        self.half_mature_fractional_phosphorus = None #fr_p2
        self.fraction_potential_heat_units_full_maturity = None #fr_PHU_100
        self.near_mature_fractional_phosphorus = None #fr_p3ish


        #these attrs are to be set later, start out as None
        self.fractional_biomass_phosphorus = None   #fr_P
        self.optimal_phosphorus_biomass = None      #bio_P_opt


    def phosphorus_uptake_driver(self,soil: Soil):
        """
        Description:
            Invokes the functions necessary to update phosphorus uptake information
            for the given crop.

        Args:
            soil: an instance of the Soil class specified in soil.py representing
                the current state of the soil profile
            crop_type: an instance of a crop class
        """

        self.determine_fractional_biomass_phosphorus() #fr_P
        self.determine_optimal_phosphorus_biomass()    #bio_P_opt
        self.determine_potential_phosphorus_uptake()   #P_up
        self.determine_actual_phosphorus_uptake_each_layer()
        self.determine_actual_phosphorus_biomass()
        #self.determine_actual_uptake_per_layer()
        #self.determine_actual_phosphorus_biomass()


        # calc_potential_phosphorus_uptake()
        # calc_act_potential_phosphorus_uptake_each_layer(soil)
        # calc_actual_phosphorus_biomass(soil)
        # potential_phosphorus_uptake(soil)

    def determine_fractional_biomass_phosphorus(self) -> None:
        """determine the fraction of phosphorus in the plant biomass"""

        second = calc_second_shape_coefficient(self.fraction_potential_heat_units_half_maturity,self.half_mature_fractional_phosphorus,
                        self.fraction_potential_heat_units_full_maturity,self.near_mature_fractional_phosphorus)
        first = calc_first_shape_coefficient(second,self.fraction_potential_heat_units_half_maturity,self.half_mature_fractional_phosphorus)

        self.fraction_biomass_phosphorus = calculate_fractional_biomass_phosphorus(first, second, self.previous_actual_biomass, 
                    self.emergent_fractional_phosphorus, self.mature_fractional_phosphorus,self.previous_fraction_potential_heat_units)


    def determine_potential_phosphorus_uptake(self) -> None:
        """determine the plants potential phosphorus uptake"""
        self.potential_phosphorus_uptake = calc_potential_phosphorus_uptake(self.optimal_phosphorus_biomass, self.actual_phosphorus_biomass,
                                                            self.mature_fractional_phosphorus, self.potential_phosphorus_biomass_increase)


    def determine_optimal_phosphorus_biomass(self) -> None:
        """determine optimal biomass of phosphorus stored in plant material"""
        self.optimal_phosphorus_biomass = calc_optimal_phosphorus_biomass(self.previous_actual_biomass, self.fraction_biomass_phosphorus)


    def determine_actual_phosphorus_uptake_each_layer(self,soil: Soil) -> None:
        """determine actual phosphorus uptake for each soil layer"""
        pass

    def determine_actual_phosphorus_biomass(self,soil: Soil) -> None:
        """determine the actual phosphorus biomass in the plant"""
        self.actual_phosphorus_biomass += calc_actual_phosphorus_biomass(soil.phosphorus_uptake)



def calc_second_shape_coefficient(fraction_potential_heat_units_half_maturity: float, half_mature_fractional_phosphorus: float,
                            fraction_potential_heat_units_full_maturity: float, near_mature_fractional_phosphorus: float) -> float:
    """Description:
            Calculates the second shape coefficient

        Args:
            fraction_potential_heat_units_half_mature: fractional potential heat units at 50% maturity
            half_mature_fractional_phosphorus: fraction of phosphorus in the biomass at 50% maturity
            fraction_potential_heat_units_full_maturity: fractional potential heat unit at 100% maturity
            near_mature_fractional_phosphorus: fraction of phosphorus in the biomass at near 100% maturity

        Returns:
            the second shape coefficient
    """

    first_term = calc_logarithmic_term_of_coefficient(fraction_potential_heat_units_half_maturity,half_mature_fractional_phosphorus)
    second_term = calc_logarithmic_term_of_coefficient(fraction_potential_heat_units_full_maturity,near_mature_fractional_phosphorus)

    third_term = fraction_potential_heat_units_full_maturity - fraction_potential_heat_units_half_maturity
    return (first_term - second_term) / third_term


def calc_first_shape_coefficient(second_shape_coefficient: float,fraction_potential_heat_units_half_maturity: float,
                                half_mature_fractional_phosphorus: float) -> float:
    """Description:
            Calculates the first shape coefficient

        Args:
            second_shape_coeffiient: 
            fraction_potential_heat_units_half_mature: fractional potential heat units at 50% maturity
            half_mature_fractional_phosphorus: fraction of phosphorus in the biomass at 50% maturity

        Returns:
            the first shape coefficient

    """
    
    first_term = calc_logarithmic_term_of_coefficient(fraction_potential_heat_units_half_maturity, half_mature_fractional_phosphorus)

    return first_term + second_shape_coefficient * fraction_potential_heat_units_half_maturity


def calculate_fractional_biomass_phosphorus(first_shape_coefficient: float,second_shape_coefficient: float,
                    previous_actual_biomass: float, emergent_fractional_biomass: float, mature_fractional_biomass: float,
                    previous_fraction_potential_heat_units: float) -> None:

    if previous_actual_biomass == 0:
        return 0
    first_term = emergent_fractional_biomass - mature_fractional_biomass
    exponent_part = exp(first_shape_coefficient - second_shape_coefficient * previous_fraction_potential_heat_units)
    second_term = 1 - (previous_fraction_potential_heat_units / (previous_fraction_potential_heat_units + exponent_part))

    return first_term * second_term + mature_fractional_biomass



#TODO: option1/2 need better names
#calc_P_up
def calc_potential_phosphorus_uptake(optimal_phosphorus_biomass: float, actual_phosphorus_biomass: float,
                                mature_fractional_phosphorus: float ,potential_phosphorus_biomass_increase: float) -> float:
    """
    Description:
        Calculates potential phosphorus uptake

    Args:
        optimal_phosphorus_biomass: optimal mass of phosphorus stored in plant material (kg P/ha)
        actual_phosphorus_biomass: actual mass of phosphorus stored in plant material (kg P/ha)
        mature_fractional_phosphorus: fraction of phosphorus in the plant biomass at maturity
        potential_phosphorus_biomass_increase: maximum potential increase in biomass for a given day

    Returns:
        potential phosphorus uptake
    """

    if optimal_phosphorus_biomass < actual_phosphorus_biomass:
        return 0
    else:
        option1 = optimal_phosphorus_biomass - actual_phosphorus_biomass
        option2 = 4 * mature_fractional_phosphorus * potential_phosphorus_biomass_increase
        return 1.5 * min(option1, option2)


#TODO term1 and term2 need better names
#calc_P_up_z
def calc_depth_dependent_potential_phosphorus_uptake(bottom_depth: float, soil_development_depth: float, 
                        potential_phosphorus_uptake: float, phosphorus_uptake_distribution_param: float) -> float:
    """
    Description: 
        Calculates potential phosphorus uptake given the depth of the soil layer

    Args:
        bottom_depth: the depth of the layer
        soil_development_depth: depth of soil development on a given day (mm)
        potential_phosphorus_uptake: potential phosphorus uptake of the crop (kg P/ha)
        phosphorus_uptake_distribution_param: //////////need description

    Returns: depth dependent potential phosphorus uptake

    """

    if soil_development_depth == 0:
        return 0

    term1 = potential_phosphorus_uptake / (1 - exp(-1 * phosphorus_uptake_distribution_param))
    term2 = 1 - exp(-1 * phosphorus_uptake_distribution_param * bottom_depth / soil_development_depth)
    
    return term1 * term2



#calc_bio_P_opt
def calc_optimal_phosphorus_biomass(previous_actual_biomass: float, fraction_biomass_phosphorus: float) -> float:
    """calculates the optimal biomass of phosphorus in the plant"""
    
    return previous_actual_biomass * fraction_biomass_phosphorus




#fr_PHU_frac, fr_px.... fr_PHU_frac needs better name, also need clarity on what fr_PHU_frac actually represents
#TODO: bottom and inside need better name
def calc_logarithmic_term_of_coefficient(fractional_potential_heat_units: float, fractional_x_coefficient: float,
                mature_fractional_phosphorus: float, emergent_fractional_phosphorus: float):
    """helper function used to calculate the logarithmic portion of the shape coefficient"""

    bottom = 1 - (fractional_x_coefficient - mature_fractional_phosphorus) / (emergent_fractional_phosphorus - mature_fractional_phosphorus)
    return log((fractional_potential_heat_units/bottom) - fractional_potential_heat_units)


#calc_bio_P
def calc_actual_phosphorus_biomass(uptake: list) -> float:
    """
    Description:
        Calculates the actual mass of phosphorus stored in the plant material

    Args:
        uptake: list of phosphorus uptake values from an instance of a Soil object

    Returns:
        the total phosphorus stored in plant material
    """
    actual_phos = 0

    for uptake_val in uptake:
        actual_phos += uptake_val

    return actual_phos



#P_uptake
def calc_layer_phosphorus_uptake(layer_labile_phosphorus: List[float], layer_phosphorus_uptake: List[float]) -> List[float]:
    """
    Description:

    Args:
        layer_labile_phosphorus: list of labile phosphorus values, one for each soil layer
        layer_phosphorus_uptake: list of phosphorus_uptake values, one for each soil layer

    Returns:
        list of per layer labile phosphorus updated to reflect phosphorus uptake
    
    
    """
    updated_labile_phosphorus = []
    for labile,uptake in zip(layer_labile_phosphorus,layer_phosphorus_uptake):
        updated_labile_phosphorus.append(labile - uptake)

    return updated_labile_phosphorus


#needs depth_dependent_potential_phosphorus_uptake
def calc_potential_phosphorus_uptake_each_layer(bottom_depths: List[float], soil_development_depth: float,
                potential_phosphorus_uptake: float, phosphorus_uptake_distribution_param) -> List[float]:
    
    uptake_each_layer = []
    top_layer_uptake = 0

    for depth in bottom_depths:
        bottom_layer_uptake = calc_depth_dependent_potential_phosphorus_uptake(depth, soil_development_depth, 
            potential_phosphorus_uptake,phosphorus_uptake_distribution_param)
        phos_uptake_layer = bottom_layer_uptake - top_layer_uptake

        uptake_each_layer.append(phos_uptake_layer)


        top_layer_uptake = bottom_layer_uptake

    return uptake_each_layer



#list of bottom depths (soil),
def calc_actual_phosphorus_uptake_each_layer(layer_bottom_depths: List[float], layer_labile_phosphorus: List[float], 
        soil_development_depth, potential_phosphorus_uptake, phosphorus_uptake_distribution_param):
    
    each_layer_uptake = calc_potential_phosphorus_uptake_each_layer(layer_bottom_depths, soil_development_depth,potential_phosphorus_uptake,phosphorus_uptake_distribution_param)
    
    phos_uptake_overlying = 0

    phos_soil_solution_overlying = 0

    phos_uptake_demand = 0

    actual_phosphorus_uptake = []

    if len(layer_bottom_depths) != len(each_layer_uptake):
        raise Exception("mismatching number of layers")

    for layer in range(len(each_layer_uptake)):
        actual_uptake = min((each_layer_uptake[layer] + phos_uptake_demand), layer_labile_phosphorus[layer])

        actual_phosphorus_uptake.append(actual_uptake)

        phos_uptake_overlying += each_layer_uptake[layer]
        phos_soil_solution_overlying += layer_labile_phosphorus[layer]

        phos_uptake_demand = phos_uptake_overlying - phos_soil_solution_overlying
        if phos_uptake_demand < 0:
            phos_uptake_demand = 0

    return actual_phosphorus_uptake



##########################################################################################################################
##########################################################################################################################
##########################################################################################################################
##########################################################################################################################



