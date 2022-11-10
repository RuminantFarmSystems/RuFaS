"""
Author(s): Clay Morrow (morrowcj@outlook.com); Andy Achenreiner (achenreiner@wisc.edu);
           Jacob Johnson (jacob8399@gmail.com)

Description: This module contains the necessary functions for calculating and
             updating the growth constraints of a crop.
"""

from math import exp


def update_growth_factor(crop, soil, weather, time) -> None:
    """
    Description: Updates the crop growth factor

    Args:
        crop: an instance of BaseCrop
        soil: an instance of Soil
        weather: an instance of Weather
        time: an instance of Time

    Returns:
        Noting. Instead, the crop.gamma_reg attribute is updated
    """
    #  TODO: plant transpiration should be an attribute of the crop, not the soil
    w_stress = calc_water_stress(water_uptake=crop.water_act_up, max_transpiration=soil.trans_max)
    w_stress=0
    avg_air_temp = weather.T_avg[time.year - 1][time.day - 1]
    t_stress = calc_temperature_stress(air_temp=avg_air_temp, min_temp=crop.T_base_min, optimal_temp=crop.T_opt)

    n_stress_factor = calc_nutrient_stress_scaling_factor(stored=crop.bio_N, optimal=crop.bio_N_opt)
    #print('n_stress', n_stress_factor)
    #print('bio_n:',crop.bio_N,'bio_n_opt',crop.bio_N_opt)
    #n_stress_factor = 100
    n_stress = calc_nutrient_stress(optimal=crop.bio_N_opt, stress_factor=n_stress_factor)
    #print('n_stress', n_stress)
    p_stress_factor = calc_nutrient_stress_scaling_factor(stored=crop.bio_P, optimal=crop.bio_P_opt)
    p_stress = calc_nutrient_stress(optimal=crop.bio_P_opt, stress_factor=p_stress_factor)
   # print([w_stress, t_stress, n_stress, p_stress])
    crop.gamma_reg = calc_growth_factor(w_stress, t_stress, n_stress, p_stress)
    #crop.gamma_reg =1


def calc_growth_factor(water_stress, temperature_stress, nitrogen_stress, phosphorus_stress) -> float:  # pseudocode: C.7.E.1
    """
    Description: Calculates plant growth factor

    Args:
        water_stress: plant water stress
        temperature_stress: plant temperature stress
        nitrogen_stress: plant nitrogen stress
        phosphorus_stress: plant phosphorus stress

    Returns: plant growth factor
    """
    # TODO: all the stress values seem like they should be constrained to [0, 1]
    return 1.0 - max(water_stress, temperature_stress, nitrogen_stress, phosphorus_stress)


def calc_water_stress(water_uptake: float, max_transpiration: float) -> float:  # pseudocode: C.7.A.1
    """
    Description: Calculates water stress for a given day.

    Args:
        water_uptake: the water taken up by the plant from the soil
        max_transpiration: the maximum plant transpiration on a given day

    Returns: the plant's water stress
    """
    #print(max_transpiration)
    #print(water_uptake)
    if max_transpiration == 0:  # avoid division by zero
        return 0
    water_uptake
    stress = 1 - (water_uptake / max_transpiration)
    stress = max(0., stress)  # constrain to 0
    stress = min(1., stress)  # constrain to 1
    # todo - old code also constrained stress to 0.99, but why? (not in pseudocode)
    # stress = min(0.99, stress)

    return stress


def calc_temperature_stress(air_temp: float, min_temp: float, optimal_temp: float) -> float:  # pseudocode C.7.B.
    """
    Description: Calculates temperature stress for a given day.

    Args:
        air_temp: average air temperature (Celsius)
        min_temp: minimum temperature for plant growth (Celsius)
        optimal_temp: optimal temperature for plant growth (Celsius)

    Returns: the plant's temperature stress
    """

    numerator = -0.1054 * (optimal_temp - air_temp)**2
    double_diff = 2*optimal_temp - min_temp

    if min_temp < air_temp <= optimal_temp:
        stress = 1 - exp(numerator / (air_temp - min_temp)**2)

    elif optimal_temp < air_temp <= double_diff:
        stress = 1 - exp(numerator / (double_diff - min_temp)**2)

    else:
        stress = 1
    return stress


def calc_nutrient_stress(optimal: float, stress_factor) -> float:  # pseudocode C.7.C.2
    """
    Description: Calculates plant nutrient stress for the day.

    Args:
        optimal: the optimal mass of the nutrient stored in the plant
        stress_factor: the stress scaling factor of the nutrient

    Returns: nutrient stress
    """
    if optimal == 0:
        # TODO - Why was the stress factor set to 300 if it doesn't get used in this case.
        #   Also, why is there no stress in this case?
        stress = 0
    else:
        stress = 1 - stress_factor / (stress_factor + exp(3.535 - 0.02597 * stress_factor))
    return min(1, stress)


def calc_nutrient_stress_scaling_factor(stored: float, optimal: float) -> float:  # pseudocode C.7.C.1
    """
    Description: Calculates nutrient stress scaling factor.

    Args:
        stored: amount of the nutrient stored in the plant
        optimal: optimal amount of the nutrient stored

    Returns: nutrient scaling factor
    """
    if optimal == 0:
        stress_factor = 300
    else:
        stress_factor = 200*(stored / optimal - 0.5)

    return max(0, stress_factor)
