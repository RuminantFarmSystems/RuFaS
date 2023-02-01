"""
RUFAS: Ruminant Farm Systems Model

File name: biomass.py

Author(s): Clay Morrow (morrowcj@outlook.com; Andy Achenreiner (achenreiner@wisc.edu)

Description: This module contains the necessary functions for calculating and
             updating the biomass values of a crop_type. Currently, the only
             function meant to be used outside this file is the allocate_biomass()
             function. The other functions are meant to serve as helper
             functions within this file.

             Note from Clay (28-Sept-2022): At some point, the functions contained within this file need to be moved
             to more appropriate locations. For example, methods that modify crop attributes should belong to the
             Crop (or BaseCrop) class as member functions. Similarly, functions that primarily model
             soil attributes should belong to a soil-related class.
"""

from math import exp


# TODO: These functions should probably be moved to the base_crop class as member functions

def allocate_biomass(crop_type, soil, weather, time) -> None:  # pseudocod: C.9
    """
    Description:
        Called from crop.py, This function updates all biomass information during daily growth

    Args:
        soil: an instance of soil in which the crop is growing
        crop_type: an instance of a crop class
        weather: an instance of the Weather class
        time: an instance of the Time class

    Returns:
        Nothing. Instead, biomass attributes are updated from soil and crop_type.
    """
    incoming_light_energy = weather.radiation[time.year - 1][time.day - 1]
    update_biomass(crop_type, light=incoming_light_energy)
    update_above_ground_biomass(crop_type)
    # TODO: the below functions are water-related and not biomass. Why are they here?
    # TODO: why is annual evapotranspiration being calculated daily??
    update_evapotrans(soil)  # TODO: it seems odd that we're updating soil attributes in a crop method - this could be done better
    update_water_def(crop_type, et=soil.ET_annual, et_max=soil.ET_max_annual)


def update_biomass(crop, light: float) -> None:
    """
    Description: update the biomass attributes of a crop after growth

    Args:
        crop: a BaseCrop class object
        light: the total light radiation available to the plant

    Returns: Nothing. Instead, the following `crop` attributes are updated:
    `d_biomass_max`, `prev_biomass_actual`, `biomass_actual`, and `d_biomass_actual`
    """
    incpt_light = intercept_radiation(daily_radiation=light, light_extinction=crop.kl, lai_actual=crop.LAI_actual)
    crop.d_biomass_max = limit_growth(radiation=incpt_light, efficiency=crop.RUE)
    growth = grow_biomass(start=crop.biomass_actual, growth_factor=crop.gamma_reg, max_growth=crop.d_biomass_max)
    crop.prev_biomass_actual = growth["start"]
    crop.biomass_actual = growth["end"]
    crop.d_biomass_actual = growth["accumulated biomass"]


def limit_growth(radiation: float, efficiency: float) -> float:  # pseudocode: C.9.A.2
    """
    Description: calculates the upper-limit to biomass accumulation during a day

    Args:
        efficiency: crop-specific radiation use efficiency (dg/MJ)
        radiation: intercepted solar radiation for the day (MJ m^-2)

    Returns: the maximum biomass that can be accumulated in a day
    """
    if radiation < 0 or efficiency < 0:
        raise Exception("radiation and efficiency must be positive.")
    return radiation * efficiency


def grow_biomass(start: float, growth_factor: float, max_growth: float) -> dict:  # pseudocode: C.9.A.3
    """
    Description:
        Calculates the biomass accumulated during a day

    Args:
        start: the biomass of the plant at the start of the day
        growth_factor: the growth factor for the plant, which is a value from 0 to 1.
        max_growth: the maximum amount of biomass the plant can accumulate in a day

    Returns:
        a dictionary containing the starting biomass of the plant ("start"), the biomass of the plant at the end of the
        day ("end"), and the total biomass accumulated ("accumulated biomass")
    """
    if growth_factor < 0 or growth_factor > 1:
        raise Exception("growth_factor must be between 0 and 1")
    if start < 0:
        raise Exception("start must be positive")
    actual_growth = max_growth * growth_factor
    end = start + actual_growth
    return {"start": start, "end": end, "accumulated biomass": actual_growth}

def intercept_radiation(daily_radiation: float, light_extinction: float, lai_actual: float) -> float:  # pseudocode: C.9.A.1
    """
    Description:
        Calculates amount of solar radiation intercepted for photosynthesis for a day.

    Args:
        daily_radiation: total solar radiation available for the day (MJ m^-2)
        light_extinction: the light extinction coefficient
        lai_actual: actual leaf area index of the crop

    Returns:
        int: intercepted radiation (MJ m^-2)
    """
    if daily_radiation < 0 or lai_actual < 0:
        raise Exception("daily_radiation and lai_actual must be positive")

    intercepted_radiation = 0.5 * daily_radiation * (1 - exp(-1 * light_extinction * lai_actual))
    return intercepted_radiation


def update_above_ground_biomass(crop) -> None:
    """
    Description: Updates above ground biomass for a crop, using `calc_bio_AG()`

    Args:
        crop: a BaseCrop class object
    """
    crop.bio_AG = calc_above_ground_biomass(fr_root=crop.fr_root, biomass_actual=crop.biomass_actual)


def calc_above_ground_biomass(fr_root: float, biomass_actual: float) -> float:  # pseudocode: C.9.B.1
    """
    Description:
        Calculates above ground biomass.

    Args:
        fr_root: fraction of biomass stored in roots
        biomass_actual: the actual biomass of the plant

    Returns: above ground biomass
    """
    bio_AG = (1 - fr_root) * biomass_actual
    return bio_AG


def update_evapotrans(soil) -> None:  # TODO: belongs in Soil class?
    if soil.ET_max_annual != 0:
        soil.ET_annual = soil.evap_annual + soil.trans_annual


def calc_evapotrans(evap: float, trans: float) -> float:  # TODO: belongs in Soil class?
    #TODO: missing pseudocode? - GitHub Issue #168
    """
    Description: calculate the annual evapotranspiration

    Args:
        evap: annual evaporation
        trans: annual transpiration

    Returns: annual evapotranspiration
    """
    return evap + trans


def update_water_def(crop, et: float, et_max: float) -> None:
    """
    Description: update the water use efficiency attribute of a crop

    Args:
        crop: a BaseCrop instance
        et: annual soil evapotranspiration
        et_max: maximum annual soil evapotranspiration
    """
    crop.gamma_wu = calc_water_def(et, et_max)  # TODO: attribute "gamma_wu" needs a more intuitive name (as do all attributes)


def calc_water_def(et: float, et_max: float) -> float:  # pseudocode: C.9.C.1
    """
    Description: calculate water deficiency factor

    Args:
        et: annual evapotranspiration
        et_max: maximum annual evapotranspiration

    Returns: water deficiency factor
    """
    if et_max != 0:
        return 100 * (et / et_max)
    else:
        return 0
