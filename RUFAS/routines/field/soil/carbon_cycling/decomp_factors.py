import math


def update_all(soil, weather, time):
    """
    Description: calculates temperature and moisture decomposition factors for
        Carbon based on weather and soil profile.
        "pseudocode_soil" S.6.A
    Args:
        soil: an instance of the Soil class defined in soil.py
        weather: an instance of the Weather class defined in classes.py
        time: an instance of the Time class defined in classes.py
    """
    temp_factor(soil, weather, time)

    moisture_factor(soil)


def temp_factor(soil, weather, time):
    """
    Description: calculates the Temperature factor for carbon decomposition
        "pseudocode_soil" S.6.A.1
        defaults drawn from defac: course soil
    Args:
        soil
        weather
        time
    """
    teff_1 = 15.400
    teff_2 = 11.750
    teff_3 = 29.700
    teff_4 = 0.03
    normalizer = 20.80546

    # S.6.A.4
    soil.T_d = max(0.0, (teff_2 + (teff_3 / math.pi) * math.atan(math.pi * teff_4 * (
            weather.T_avg[time.year - 1][time.day - 1] - teff_1))) / normalizer)


def moisture_factor(soil):
    """
    Description: calculates the moisture factor for carbon decomposition
        "pseudocode_soil" S.6.A.2
        defaults drawn from defac: course soil
    Args:
        soil
    """
    a = 0.55
    b = 1.7
    c = -0.007
    e1 = 6.648115
    e2 = 3.22

    for layer in soil.soil_layers:
        # S.6.A.5
        base_1 = (layer.water_fac - b) / (a - b)
        base_2 = (layer.water_fac - c) / (a - c)
        layer.M_d = (base_1 ** e1) * (base_2 ** e2)
