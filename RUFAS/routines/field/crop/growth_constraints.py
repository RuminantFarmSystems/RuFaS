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

    phi_N = scaling factor for nitrogen stress

    bio_P = Actual mass of phosphorus stored in plant material (kg P/ha)

    bio_P_opt = Optimal mass of phosphorus stored in plant material for current
                growth stage (kg P/ha)

    phi_P = scaling factor for phosphorus stress

    w_stress = Water stress for a given day

    t_stress = Temperature stress for a given day

    n_stress = Nitrogen stress for a given day

    p_stress = Phosphorus stress for a given day

    gamma_reg = Plant growth factor


CropType values updated by update_all():

    gamma_reg

"""

from math import exp


def update_all(soil, crop_type, weather, time):
    """
    Description:
        Updates crop information relevant to growth constraints

    Args:
        soil: an instance of the Soil class specified in soil.py representing
            the current state of the soil profile
        crop_type: an instance of a crop class
            containing environmental information
        weather: an instance of the Weather class specified in classes.py
            containing environmental information
        time: an instance of the Time class specified in classes.py

    """

    # update gamma_reg value
    calc_gamma_reg(soil, crop_type, weather, time)


def calc_gamma_reg(soil, crop_type, weather, time):
    """
    Description:
        Calculates plant growth factor (AKA gamma_reg).
        "pseudocode_crop" C.7

    Args:
        crop_type
        time
        weather
        soil
    """

    w_stress = calc_w_stress(soil, crop_type)
    t_stress = calc_t_stress(crop_type, weather, time)
    n_stress = calc_n_stress(crop_type)
    p_stress = calc_p_stress(crop_type)

    # C.7.E.1
    crop_type.gamma_reg = 1.0 - max(w_stress, t_stress, n_stress, p_stress)


"""
The following functions comprise the "Growth Constraints".
This includes the water, temperature, nitrogen, and phosphorus stress
for a given day. These values are needed to calculate the gamma_reg value.
They do not modify the values of any State class.
"""


def calc_w_stress(soil, crop_type):
    """
    Description:
        Calculates water stress for a given day.
        "pseudocode_crop" C.7.A.1

    Args:
        crop_type
        soil
    Returns:
        float: water stress
    """

    if soil.trans_max == 0:
        return 0
    w_stress = 1.0 - (crop_type.water_act_up / soil.trans_max)
    if w_stress < 0:
        return 0
    else:
        return min(0.99, w_stress)


def calc_t_stress(crop_type, weather, time):
    """
    Description:
        Calculates temperature stress for a given day.
        "pseudocode_crop" C.7.B.1-4

    Args:
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
        t_stress = MAX

    # C.7.B.2
    elif T_base_min < T_avg <= T_opt:
        top_half_eq = -0.1054 * (T_opt - T_avg) ** 2
        bottom_half_eq = (T_avg - T_base_min) ** 2
        t_stress = 1 - (0 if bottom_half_eq == 0 else exp(top_half_eq / bottom_half_eq))

    # C.7.B.3
    elif T_opt < T_avg <= (2 * T_opt - T_base_min):
        top_half_eq = -0.1054 * (T_opt - T_avg) ** 2
        bottom_half_eq = ((2 * T_opt - T_avg) - T_base_min) ** 2
        t_stress = 1 - (0 if bottom_half_eq == 0 else exp(top_half_eq / bottom_half_eq))

    # C.7.B.4
    else:  # T_avg > (2*T_opt - T_base_min):
        t_stress = MAX

    return min(t_stress, MAX)


def calc_n_stress(crop_type):
    """
    Description:
        Calculates nitrogen stress for a given day.
        "pseudocode_crop" C.7.C.2

    Args:
        crop_type
    Returns:
        float: nitrogen stress
    """

    if crop_type.bio_N_opt == 0:
        return 0
    phi_n = calc_phi_N(crop_type)
    n_stress = 1 - phi_n / (phi_n + exp(3.535 - 0.02597 * phi_n))
    return min(0.99, n_stress)


def calc_phi_N(crop_type):
    """
    Description:
        Calculates nitrogen stress scaling factor.
        "pseudocode_crop" C.7.C.1

    Args:
        crop_type
    Returns:
        float: scaling factor
    """

    if crop_type.bio_N_opt == 0:
        return 300
    else:
        phi_n = 200 * ((crop_type.bio_N / crop_type.bio_N_opt) - 0.5)
        return max(0, phi_n)


def calc_p_stress(crop_type):
    """
    Description:
        Calculates phosphorus stress for a given day.
        "pseudocode_crop" C.7.D.2

    Args:
        crop_type
    Returns:
        float: phosphorus stress
    """

    if crop_type.bio_P_opt == 0:
        return 0
    phi_p = calc_phi_P(crop_type)
    p_stress = 1 - phi_p / (phi_p + exp(3.535 - 0.02597 * phi_p))
    return min(0.99, p_stress)


def calc_phi_P(crop_type):
    """
    Description:
        Calculates phosphorus stress scaling factor.
        "pseudocode_crop" C.7.D.1

    Args:
        crop_type
    Returns:
        float: phosphorous stress scaling factor, phi_p
    """

    if crop_type.bio_P_opt == 0:
        return 300
    else:
        phi_p = 200 * ((crop_type.bio_P / crop_type.bio_P_opt) - 0.5)
        return max(0, phi_p)
