from math import log, exp

class PhosphorusUptake:
    def __init__(self):

        #these attrs DO need initial values
        self.optimal_phosphorus_biomass = None
        self.actual_phosphorus_biomass = None
        self.potential_phosphorus_uptake = None
        self.mature_fractional_phosphorus = None
        self.potential_phosphorus_biomass_increase = None
        


        #these attrs are to be set later, start out as None

    def update_all(soil, crop_type):
        """
        Description:
            Invokes the functions necessary to update phosphorus uptake information
            for the given crop.

        Args:
            soil: an instance of the Soil class specified in soil.py representing
                the current state of the soil profile
            crop_type: an instance of a crop class
        """

        calc_fr_P()
        calc_optimal_phosphorus_biomass()
        calc_potential_phosphorus_uptake()
        calc_act_potential_phosphorus_uptake_each_layer(soil)
        calc_actual_phosphorus_biomass(soil)
        potential_phosphorus_uptaketake(soil)

    def determine_potential_phosphorus_uptake(self):
        self.potential_phosphorus_uptake = calc_potential_phosphorus_uptake(self.optimal_phosphorus_biomass, self.actual_phosphorus_biomass,
                                                            self.mature_fractional_phosphorus, self.potential_phosphorus_biomass_increase)




#TODO: option1/2 need better names
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
    
    











def calc_fr_P(crop_type):
    """
    Description:
        Calculates fraction of phosphorus in the plant biomass.
        "pseudocode_crop" C.6.B.1

    Args:
        crop_type
    """

    p2 = calc_p2(crop_type)
    p1 = calc_p1(crop_type, p2)
    if crop_type.prev_biomass_actual == 0:
        crop_type.fr_P = 0
    else:
        first_term = crop_type.fr_p1 - mature_fractional_phosphorus

        exp_part = exp(p1 - p2 * crop_type.prev_fr_PHU)
        second_term = 1 - (crop_type.prev_fr_PHU / (crop_type.prev_fr_PHU + exp_part))

        crop_type.fr_P = first_term * second_term + mature_fractional_phosphorus


def calc_p2(crop_type):
    """
    Description:
        Calculates the second shape coefficient.
        "pseudocode_crop" C.6.A.1

    Args:
        crop_type

    Returns:
        float: second shape coefficient
    """

    first_term = calc_log_term_of_shape_coefficient(
        crop_type, crop_type.fr_PHU_50, crop_type.fr_p2
    )

    second_term = calc_log_term_of_shape_coefficient(
        crop_type, crop_type.fr_PHU_100, mature_fractional_phosphorusish
    )

    third_term = crop_type.fr_PHU_100 - crop_type.fr_PHU_50

    return (first_term - second_term) / third_term


def calc_p1(crop_type, p2):
    """
    Description:
        Calculates the first shape coefficient.
        "pseudocode_crop" C.6.A.2

    Args:
        crop_type
        p2: second shape coefficient

    Returns:
        float: first shape coefficient
    """

    first_term = calc_log_term_of_shape_coefficient(
        crop_type, crop_type.fr_PHU_50, crop_type.fr_p2
    )

    return first_term + p2 * crop_type.fr_PHU_50


def calc_log_term_of_shape_coefficient(crop_type, fr_PHU_frac, fr_px):
    """
    Description:
        Helper function. Calculates the log term in the shape coefficient calculations
        "pseudocode_crop" C.6.A.2

    Args:
        crop_type
        fr_PHU_frac: the fraction of the fraction of potential heat units
        fr_px: this function is used to calculate the log term in the calculations
            of multiple shape coefficients. The fraction of p shape coefficient x

    Returns:
        float: log term in the calculations
    """

    bottom = 1 - (fr_px - mature_fractional_phosphorus) / (crop_type.fr_p1 - mature_fractional_phosphorus)
    inside = (fr_PHU_frac / bottom) - fr_PHU_frac
    return log(inside)


def calc_optimal_phosphorus_biomass(crop_type):
    """
    Description:
        Calculates optimal mass of phosphorus stored in plant material.
        "pseudocode_crop" C.6.B.2

    Args:
        crop_type
    """

    crop_type.optimal_phosphorus_biomass = crop_type.prev_biomass_actual * crop_type.fr_P




def calc_act_potential_phosphorus_uptake_each_layer(soil, crop_type):
    """
    Description:
        Calculates the actual phosphorus uptake from soil solution in each layer.
        Saves the list containing these values to act_potential_phosphorus_uptake_each_layer attribute.
        The order of the values in the list corresponds with the order of the layers
        in soil.soil_layers. The soil layers in that list need to be in order
        of shallowest to deepest for this to work correctly.
        "pseudocode_crop" C.6.C.4-7

    Args:
        soil
        crop_type
    """

    potential_phosphorus_uptake_each_layer = calc_potential_phosphorus_uptake_each_layer(soil, crop_type)

    # Running total of potential phosphorus uptake in overlying layers
    potential_phosphorus_uptake_over = 0

    # Running total of phosphorus content of soil solution in overlying layers
    P_sol_over = 0

    # Phosphorus uptake demand not met in overlying soil layers
    P_demand = 0

    for pot_potential_phosphorus_uptake, layer in zip(potential_phosphorus_uptake_each_layer, soil.soil_layers):
        # C.6.C.4
        act_potential_phosphorus_uptake = min((pot_potential_phosphorus_uptake + P_demand), layer.labile_P)
        # C.6.C.7
        layer.potential_phosphorus_uptaketake = act_potential_phosphorus_uptake

        # C.6.C.6
        # Update values for next layer
        potential_phosphorus_uptake_over += pot_potential_phosphorus_uptake
        P_sol_over += layer.labile_P
        # C.6.C.5
        P_demand = potential_phosphorus_uptake_over - P_sol_over
        if P_demand < 0:
            P_demand = 0


def calc_potential_phosphorus_uptake_each_layer(soil, crop_type):
    """
    Description:
        Calculates the potential phosphorus uptake from soil solution in each layer.
        Returns a list containing these values. The order of the values in the list
        corresponds with the order of the layers in soil.soil_layers. The soil
        layers in that list need to be in order of shallowest to deepest for this
        to work correctly.
        "pseudocode_crop" C.6.C.3

    Args:
        soil
        crop_type
    """

    potential_phosphorus_uptake_each_layer = []
    potential_phosphorus_uptake_for_top_of_layer = 0
    for layer in soil.soil_layers:
        potential_phosphorus_uptake_for_bottom_of_layer = calc_potential_phosphorus_uptake_z(crop_type, layer.bottom_depth)
        potential_phosphorus_uptake_ly = potential_phosphorus_uptake_for_bottom_of_layer - potential_phosphorus_uptake_for_top_of_layer

        potential_phosphorus_uptake_each_layer.append(potential_phosphorus_uptake_ly)

        # Set the top for next layer equal to bottom of this layer
        potential_phosphorus_uptake_for_top_of_layer = potential_phosphorus_uptake_for_bottom_of_layer

    return potential_phosphorus_uptake_each_layer


def calc_potential_phosphorus_uptake_z(crop_type, z):
    """
    Description:
        Calculates potential phosphorus uptake from soil solution at the surface to
        depth z. This function is used in calc_potential_phosphorus_uptake_each_layer.
        "pseudocode_crop" C.6.C.1

    Args:
        crop_type
        z: the given depth

    Returns:
        float: nitrogen uptake from the surface to a depth
    """

    if crop_type.z_root == 0:
        return 0
    term1 = crop_type.potential_phosphorus_uptake / (1 - exp(-1 * crop_type.beta_p))
    term2 = 1 - exp(-1 * crop_type.beta_p * z / crop_type.z_root)
    return term1 * term2


def calc_actual_phosphorus_biomass(soil, crop_type):
    """
    Description:
        Calculates actual mass of phosphorus stored in plant material.

    Args:
        crop_type
        soil
    """

    for layer in soil.soil_layers:
        crop_type.actual_phosphorus_biomass += layer.potential_phosphorus_uptaketake


def potential_phosphorus_uptaketake(soil):
    for layer in soil.soil_layers:
        layer.labile_P -= layer.potential_phosphorus_uptaketake
