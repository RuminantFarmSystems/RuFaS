"""
RUFAS: Ruminant Farm Systems Model

File name: infiltration.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating water infiltration into the soil on a given day using the
             curve number approach. Currently the only function meant to be
             used outside of this file is the update_all() function. The other
             functions are meant to serve as helper functions within this file.

Soil attribute definitions

    runoff = daily runoff (mm H2O)

    R = daily rainfall depth (mm H2O)

    S = retention parameter (mm H2O)

    CN1 = Curve Number 1 (empirical value used to determine the retention
                            parameter S)

    CN2 = Curve Number 2

    CN3 = Curve Number 3

    S_max = maximum value for S on any given day (mm H2O)

    SW = soil water content of entire profile, excluding water held at wilting
            point (mm H2O)

    w1 = shape coefficient

    w2 = shape coefficient

    FC = amount of water in soil profile at field capacity (mm H2O)

    SAT = amount of water in soil profile at saturation (mm H2O)

    S_frz = retention parameter when the top layer of soil is frozen
"""

from math import exp, log


def update_all(soil, weather, time):
    """
    Definition:
        This function calls all the necessary functions to update information related
        to infiltration

    Args:
        soil: instance of the Soil class specified in soil.py
        weather: instance of the Weather class specified in classes.py
        time: instance of the Time class specified in classes.py
    """

    calc_runoff(soil, weather, time)

    calc_daily_infiltration(soil, weather, time)


def calc_runoff(soil, weather, time):
    """
    Definition:
        Calculates the daily runoff (mm H2O)
        "pseudocode_soil" S.2.A.1

    Args:
        soil
        weather
        time
    """

    R = weather.rainfall[time.year-1][time.day-1]
    S = calc_S(soil)

    # modifies S if the top layer of soil is frozen
    # "pseudocode_soil" S.2.A.9
    if soil.soil_layers[0].temperature <= 2:
        S_max = calc_S_max(soil)
        exp_part = exp(-0.000862 * S)
        S = S_max * (1 - exp_part)

    runoff = 0.0
    if R > 0.2 * S:
        runoff = ((R - 0.2 * S) ** 2) / (R + 0.8 * S)

    soil.runoff = runoff


def calc_S(soil):
    """
    Definition:
        Calculates the retention parameter S (mm H2O) for use in calculating daily
        runoff (mm H2O)
        "pseudocode_soil" S.2.A.4

    Args:
        soil

    Returns:
        int: S, retention parameter (mm H2O)
    """

    CN3 = calc_CN3(soil)

    S_max = calc_S_max(soil)
    w2 = calc_w2(soil, S_max, CN3)
    w1 = calc_w1(soil, S_max, CN3, w2)

    SW_available = sum_SW(soil) - sum_WW(soil)

    S_exp = exp(w1 - (w2 * SW_available))

    return S_max * (1 - (SW_available / (SW_available + S_exp)))


def calc_CN1(soil):
    """
    Definition:
        Calculates Curve Number 1 for use in calculating S_max
        "pseudocode_soil" S.2.A.2

    Args:
        soil

    Returns:
        int: CN1, unitless Curve Number 1 for use in calculating S_max
    """

    CN2 = soil.CN2
    CN1_exp = exp(2.533 - 0.0636 * (100 - CN2))
    return CN2 - (20 * (100 - CN2)) / (100 - CN2 + CN1_exp)


def calc_CN3(soil):
    """
    Definition:
        Calculates Curve Number 3 for use in calculating S3
        "pseudocode_soil" S.2.A.3

    Args:
        soil

    Returns:
        int: CN3, unitless Curve Number 3 for use in calculating S3
    """

    CN2 = soil.CN2
    CN3_exp = exp(0.00673 * (100 - CN2))
    return CN2 * CN3_exp


def calc_S_max(soil):
    """
    Definition:
        Calculates S_max, the maximum value for S on the current given day (mm H2O)
        "pseudocode_soil" S.2.A.5

    Args:
        soil

    Returns:
        int: S_max, the maximum value for retention parameter S on the current day (mm H2O)
    """

    CN1 = calc_CN1(soil)
    return 25.4 * ((1000 / CN1) - 10)


def calc_w1(soil, S_max, CN3, w2):
    """
    Description:
        Calculates the shape coefficient w1
        "pseudocode_soil" S.2.A.6

    Args:
        soil
        S_max: Maximum value for retention parameter S on a given day
        CN3: unitless Curve Number 3
        w2: shape coefficient w2

    Returns:
        int: w1, unitless shape coefficient
    """

    FC = soil.profile_depth * soil.soil_layers[0].field_capacity

    S3 = calc_S3(CN3)

    log_part = log(FC / (1 - S3 * (1 / S_max)) - FC)

    return log_part + (w2 * FC)


def calc_w2(soil, S_max, CN3):
    """
    Definition:
        Calculates the shape coefficient w2
        "pseudocode_soil" S.2.A.7

    Args:
        soil
        S_max: Maximum value for the retention parameter S on a given day
        CN3: Curve Number 3. Calculated above

    Returns:
        int: w2, unitless shape coefficient
    """

    FC = soil.profile_depth * soil.soil_layers[0].field_capacity

    SAT = soil.profile_depth * soil.soil_layers[0].saturation

    S3 = calc_S3(CN3)

    L1 = log(FC / (1 - S3 * (1 / S_max)) - FC)
    L2 = log(SAT / (1 - 2.54 * (1 / S_max)) - SAT)

    return (L1 - L2) / (SAT - FC)


def calc_S3(CN3):
    """
    Definition:
        Calculates S3 for use in calculating shape coefficients w1/w2
        "pseudocode_soil" S. 2.A.8

    Args:
        CN3: Curve Number 3

    Returns:
        int: S3, used in calculating unitless shape coefficients w1, w2
    """

    return 25.4 * ((1000 / CN3) - 10)


def sum_SW(soil):
    """
    Description:
        Calculates soil water content of the entire profile for use in calculating S
        "pseudocode_soil" S.2.A.4

    Args:
        soil

    Returns:
        int: SW, the total soil water content of the profile (mm H2O)
    """

    SW = 0.0
    for layer in soil.soil_layers:
        SW += layer.soil_water
    return SW


def sum_WW(soil):
    """
    Description:
        Calculates the quantity of water held at wilting point in the entire profile
        for use in calculating S
        "pseudocode_soil" S.2.A.4

    Args:
        soil

    Returns:
        int: WW, the total quantity of water held at wilting point for the profile (mm H2O)
    """

    WW = 0.0
    for layer in soil.soil_layers:
        WW += layer.wilting_water
    return WW


def calc_daily_infiltration(soil, weather, time):
    """
    Description:
        Calculates and updates daily infiltration as rainfall - runoff
        "pseudocode_soil" S.2.A.10

    Args:
        soil
        weather
        time
    """

    R = weather.rainfall[time.year-1][time.day-1]
    runoff = soil.runoff
    soil.infiltration = R - runoff
