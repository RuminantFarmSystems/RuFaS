"""
RUFAS: Ruminant Farm Systems Model

File name: nitrogen_uptake.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the nitrogen uptake information of a crop_type. Currently the only
             function meant to be used outside of this file is the update_all()
             function. The other functions are meant to serve as helper
             functions within this file.

CropType attribute definitions:

    fr_n1 = Normal fraction of nitrogen in the plant biomass at emergence

    fr_n2 = Normal fraction of nitrogen in the plant biomass at 50% maturity

    fr_n3 = Normal fraction of nitrogen in the plant biomass at maturity

    fr_n3ish = Normal fraction of nitrogen in the plant biomass near maturity

    fr_N = Fraction of nitrogen in the plant biomass on a given day

    bio_N_opt = Optimal mass of nitrogen stored in plant biomass (kg N ha^-1)

    N_up = Potential nitrogen uptake (kg N ha^-1)

    beta_n = Nitrogen uptake distribution parameter

    act_N_up_each_layer = List of actual nitrogen uptakes from each soil layer.

    N_act_up = Actual amount of nitrogen removed from the soil solution
                  on a given day (kg N ha^-1)

    bio_N = Actual mass of nitrogen stored in plant material (kg N ha^-1)


CropType values updated by calling update_all():

    fr_N
    bio_N_opt
    N_up
    act_N_up_each_layer
    N_act_up
    bio_N
"""
###############################################################################

from math import log, exp
from .nitrogen_fixation import calc_N_fixation


#
# This function updates all of a crop's nitrogen uptake information.
#
def update_all(crop_type, soil):
    calc_fr_N(crop_type)
    calc_bio_N_opt(crop_type)
    calc_N_up(crop_type)
    calc_act_N_up_each_layer(crop_type, soil)
    crop_type.N_act_up = sum(crop_type.act_N_up_each_layer)
    calc_bio_N(crop_type, soil)


#
# Calculates the fraction of nitrogen in the plant biomass on a given day.
# "pseudocode_crop" C.5.B.1
#
def calc_fr_N(crop_type):
    n2 = calc_n2(crop_type)
    n1 = calc_n1(crop_type, n2)

    if crop_type.prev_biomass_actual == 0:
        crop_type.fr_N = 0
    else:
        term1 = crop_type.fr_n1 - crop_type.fr_n3

        exp_part = exp(n1 + n2 * crop_type.prev_fr_PHU)
        term2 = 1 - crop_type.prev_fr_PHU / (crop_type.prev_fr_PHU + exp_part)

        crop_type.fr_N = term1 * term2 + crop_type.fr_n3


#
# Calculates the second shape coefficient.
# "pseudocode_crop" C.5.A.1
#
def calc_n2(crop_type):
    term1 = calc_log_term_of_shape_coeff(
        crop_type, crop_type.fr_PHU_50, crop_type.fr_n2
    )

    term2 = calc_log_term_of_shape_coeff(
        crop_type, crop_type.fr_PHU_100, crop_type.fr_n3ish
    )

    term3 = crop_type.fr_PHU_100 - crop_type.fr_PHU_50

    return (term1 - term2) / term3


#
# Calculates the first shape coefficient.
# "pseudocode_crop" C.5.A.2
#
def calc_n1(crop_type, n2):
    term1 = calc_log_term_of_shape_coeff(
        crop_type, crop_type.fr_PHU_50, crop_type.fr_n2
    )

    return term1 + n2 * crop_type.fr_PHU_50


#
# Helper function. Calculates the log term in the shape coefficient calculations
#
def calc_log_term_of_shape_coeff(crop_type, fr_PHU_fract, fr_n_):
    bottom = 1 - (fr_n_ - crop_type.fr_n3) / (crop_type.fr_n1 - crop_type.fr_n3)
    inside = (fr_PHU_fract / bottom) - fr_PHU_fract

    return log(inside)


#
# Calculates the optimal mass of nitrogen stored in plant biomass.
# "pseudocode_crop" C.5.B.2
#
def calc_bio_N_opt(crop_type):
    crop_type.bio_N_opt = crop_type.fr_N * crop_type.biomass_actual


#
# Calculates potential nitrogen uptake.
# "pseudocode_crop" C.5.B.3
#
def calc_N_up(crop_type):
    if crop_type.bio_N_opt - crop_type.bio_N < 0:
        crop_type.N_up = 0
    else:
        option1 = crop_type.bio_N_opt - crop_type.bio_N
        option2 = 4 * crop_type.fr_n3 * crop_type.dBiomass_max

        crop_type.N_up = min(option1, option2)


#
# Calculates the actual nitrogen uptake from soil solution in each layer.
# Saves the list containing these values to act_N_up_each_layer attribute.
# The order of the values in the list corresponds with the order of the layers
# in soil.soil_layers. The soil layers in that list need to be in order
# of shallowest to deepest for this to work correctly.
# "pseudocode_crop" C.5.C.4/5/6/7
#
def calc_act_N_up_each_layer(crop_type, soil):
    N_up_each_layer = calc_N_up_each_layer(crop_type, soil)
    act_N_up_each_layer = []

    # Running total of potential nitrogen uptake in overlying layers
    N_up_over = 0

    # Running total of nitrate in overlying soil layers
    NO3_over = 0

    # Nitrogen uptake demand not met in overlying soil layers
    N_demand = 0

    for pot_N_up, soilLayer in zip(N_up_each_layer, soil.soil_layers):

        # C.5.C.4
        act_N_up = min((pot_N_up + N_demand), soilLayer.NO3)

        # C.5.C.7
        act_N_up_each_layer.append(act_N_up)

        # Update values so ready for the next layer
        N_up_over += pot_N_up

        # C.5.C.6
        NO3_over += soilLayer.NO3

        # C.5.C.5
        N_demand = N_up_over - NO3_over

        if N_demand < 0:
            N_demand = 0

    crop_type.act_N_up_each_layer = act_N_up_each_layer


#
# Calculates the potential nitrogen uptake from soil solution in each layer.
# Returns a list containing these values. The order of the values in the list
# corresponds with the order of the layers in soil.soil_layers. The soil
# layers in that list need to be in order of shallowest to deepest for this
# to work correctly.
# "pseudocode_crop" C.5.C.2/3
#
def calc_N_up_each_layer(crop_type, soil):
    N_up_each_layer = []

    N_up_for_top_of_layer = 0
    for layer in soil.soil_layers:
        N_up_for_bottom_of_layer = calc_N_up_z(crop_type, layer.bottom_depth)

        # C.5.C.3
        N_up_ly = N_up_for_bottom_of_layer - N_up_for_top_of_layer

        N_up_each_layer.append(N_up_ly)

        # Set the top for next layer equal to bottom of this layer
        N_up_for_top_of_layer = N_up_for_bottom_of_layer

    return N_up_each_layer


#
# Calculates potential nitrogen uptake from soil solution at the surface to
# depth z. This function is used in calc_N_up_each_layer.
# "pseudocode_crop" C.5.C.1
#
def calc_N_up_z(crop_type, z):
    if crop_type.z_root == 0:
        return 0
    term1 = crop_type.N_up / (1 - exp(-1 * crop_type.beta_n))
    term2 = 1 - exp(-1 * crop_type.beta_n * z / crop_type.z_root)
    return term1 * term2


#
# Calculates actual mass of nitrogen stored in plant material.
# "pseudocode_crop" C.5.E.1
#
def calc_bio_N(crop_type, soil):
    N_fix = calc_N_fixation(crop_type, soil)

    crop_type.bio_N = crop_type.bio_N + crop_type.N_act_up + N_fix
