"""
RUFAS: Ruminant Farm Systems Model

File name: growth_constraints.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu
           Jacob Johnson, jacob8399@gmail.com

Description: This module contains the necessary functions for calculating and
             updating the growth constraints of a crop_type. Currently the only
             function meant to be used outside of this file is the update_all()
             function. The other functions are meant to serve as helper
             functions within this file.

CropType attribute definitions:

    bio_N = Actual mass of nitrogen stored in plant material (kg N/ha)

    bio_N_opt = Optimal mass of nitrogen stored in plant material for current
                growth stage (kg N/ha)

    phi_N = Scaling factor for nitrogen stress

    bio_P = Actual mass of phosphorus stored in plant material (kg P/ha)

    bio_P_opt = Optimal mass of phosphorus stored in plant material for current
                growth stage (kg P/ha)

    phi_P = scaling factor for phosphorus stress

    wstrs = Water stress for a given day

    tstrs = Temperature stress for a given day

    nstrs = Nitrogen strss for a given day

    pstrs = Phosphorus stress for a given day

    gamma_reg = Plant growth factor


CropType values updated by update_all():

    gamma_reg

"""

from math import exp


def update_all(crop_type, time, weather, soil):
    """This function updates all information for growth constraints

    Inputs:
        crop_type
        time
        weather
        soil
    """

    # update gamma_reg value
    calc_gamma_reg(crop_type, time, weather, soil)


def calc_gamma_reg(crop_type, time, weather, soil):
    """Calculates plant growth factor (AKA gamma_reg).
       "pseudocode_crop" C.7

    Inputs:
        crop_type
        time
        weather
        soil
    """

    wstrs = calc_wstrs(crop_type, soil)
    tstrs = calc_tstrs(crop_type, time, weather)
    nstrs = calc_nstrs(crop_type)
    pstrs = calc_pstrs(crop_type)

    # C.7.E.1
    crop_type.gamma_reg = 1.0 - max(wstrs, tstrs, nstrs, pstrs)


"""
The following functions comprise the "Growth Constraints".
This includes the water, temperature, nitrogen, and phosphorus stress
for a given day. These values are needed to calculate the gamma_reg value.
They do not modify the values of any State class.
"""


def calc_wstrs(crop_type, soil):
    """Calculates water stress for a given day.
       "pseudocode_crop" C.7.A.1

    Inputs:
        crop_type
        soil
    Returns:
        float: water stress
    """

    if soil.trans_max == 0:
        return 0
    wstrs = 1.0 - (crop_type.water_act_up / soil.trans_max)
    if wstrs < 0:
        return 0
    else:
        return min(0.99, wstrs)


def calc_tstrs(crop_type, time, weather):
    """Calculates temperature stress for a given day.
       "pseudocode_crop" C.7.B.1-4

    Inputs:
        crop_type
        time
        weather
    Returns;
        float: temperature stress
    """

    # C.7.B.1
    T_avg = weather.T_avg[time.year - 1][time.day - 1]
    T_opt = crop_type.T_opt
    T_base_min = crop_type.T_base_min
    MAX = 0.99

    if T_avg <= T_base_min:
        tstrs = MAX

    # C.7.B.2
    elif T_base_min < T_avg <= T_opt:
        top_half_eq = -0.1054 * (T_opt - T_avg) ** 2
        bottom_half_eq = (T_avg - T_base_min) ** 2
        tstrs = 1 - exp(top_half_eq / bottom_half_eq)

    # C.7.B.3
    elif T_opt < T_avg <= (2 * T_opt - T_base_min):
        top_half_eq = -0.1054 * (T_opt - T_avg) ** 2
        bottom_half_eq = ((2 * T_opt - T_avg) - T_base_min) ** 2
        tstrs = 1 - exp(top_half_eq / bottom_half_eq)

    # C.7.B.4
    else:  # T_avg > (2*T_opt - T_base_min):
        tstrs = MAX

    return min(tstrs, MAX)


def calc_nstrs(crop_type):
    """Calculates nitrogen stress for a given day.
       "pseudocode_crop" C.7.C.2

    Inputs:
        crop_type
    Returns:
        float: nitrogen stress
    """

    if crop_type.bio_N_opt == 0:
        return 0
    phi_n = calc_phi_N(crop_type)
    nstrs = 1 - phi_n / (phi_n + exp(3.535 - 0.02597 * phi_n))
    return min(0.99, nstrs)


def calc_phi_N(crop_type):
    """Calculates nitrogen stress scaling factor.
       "pseudocode_crop" C.7.C.1

    Inputs:
        crop_type
    Returns:
        float: scaling factor
    """

    if crop_type.bio_N_opt == 0:
        return 300
    else:
        phi_n = 200 * ((crop_type.bio_N / crop_type.bio_N_opt) - 0.5)
        return max(0, phi_n)


def calc_pstrs(crop_type):
    """Calculates phosphorus stress for a given day.
       "pseudocode_crop" C.7.D.2

    Inputs:
        crop_type
    Returns:
        float: phosphorus stress
    """

    if crop_type.bio_P_opt == 0:
        return 0
    phi_p = calc_phi_P(crop_type)
    pstrs = 1 - phi_p / (phi_p + exp(3.535 - 0.02597 * phi_p))
    return min(0.99, pstrs)


def calc_phi_P(crop_type):
    """Calculates phosphorus stress scaling factor.
       "pseudocode_crop" C.7.D.1

    Inputs:
        crop_type
    Returns:
        float: scaling factor
    """

    if crop_type.bio_P_opt == 0:
        return 300
    else:
        phi_p = 200 * ((crop_type.bio_P / crop_type.bio_P_opt) - 0.5)
        return max(0, phi_p)
