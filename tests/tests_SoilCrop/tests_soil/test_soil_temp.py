"""
RUFAS: Ruminant Farm Systems Model
File name: test_soil_temp.py
Description: Implements test cases
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

from RUFAS.routines.field.soil.soil_temp import *
from RUFAS.routines.field.soil.soil import Soil
from RUFAS.routines.field.crop.crop import Crop
from RUFAS.routines.field.crop.crop_types.base_crop import BaseCrop
from RUFAS.classes import Time, Weather

from unittest.mock import MagicMock
import pytest

from math import *

def mock_soil(soil_albedo = 0.16,profile_bulk_density = 3.5, profile_depth = 200):
    msoil = MagicMock(Soil)

    msoil.soil_albedo = soil_albedo
    msoil.soil_layers = [mock_soil_layer(),mock_soil_layer()]
    msoil.profile_bulk_density = profile_bulk_density
    msoil.profile_depth = profile_depth

    return msoil

def mock_soil_layer(soil_water = 10,temperature = 22.4):
    mlayer = MagicMock(Soil.SoilLayer)

    mlayer.soil_water = soil_water
    mlayer.temperature = temperature

    return mlayer


def mock_crop():
    mcrop = MagicMock(Crop)

    mcrop.current_crop = mock_base_crop()

    return mcrop


def mock_base_crop(bio_AG = 5.0):
    mbase_crop = MagicMock(BaseCrop)

    mbase_crop.bio_AG = bio_AG

    return mbase_crop


def mock_time(year = 1, day = 1):
    """
    Description:
         Creates a Time class mocking object for use as input for functions. It is initialized with the
        arguments provided; arguments are dynamic and can be changed/added to as needed.

    Args:
        year: Time attribute, current year 
        day: Time attribute, current day

    Returns:
        Time class mocking object
    
    """
    mtime = MagicMock(Time)

    mtime.year = year
    mtime.day = day

    return mtime

def mock_weather(radiation = [[3.5]],T_avg = [[20]]):
    """
    Description:
        Creates a Weather class mocking object for use as input for functions. It is initialized with the
        arguments provided; arguments are dynamic and can be changed/added to as needed.

    Args:

    Returns:
        Weather class mocking object
    
    """
    mweather = MagicMock(Weather)
    
    mweather.radiation = radiation
    mweather.T_avg = T_avg

    return mweather



#the following tests are for the calc_bcv() function

#test 1 uses time.day = 250, which would not activate the snow flag
def test_calc_bcv_correctly_calculates_weighing_factor():
    crop = mock_crop()
    time = mock_time(day = 250)

    bcv = 5.0 / (5.0 + exp(7.563 - .0001297 * (-5.0)))
    bcv_snow = (0/ (0+ exp(6.055 - 0.3002 * 0)))

    weigh_factor = calc_bcv(crop,time)
    assert pytest.approx(weigh_factor) == max(bcv,bcv_snow)

#this test uses time.day = 360, which activates the snow flag
def test_calc_bcv_correctly_calculates_weighing_factor_snow():
    crop = mock_crop()
    time = mock_time(day = 360)

    bcv = 5.0 / (5.0 + exp(7.563 - .0001297 * (-5.0)))
    bcv_snow = ((10 * 0.8)/ ((10 * 0.8)+ exp(6.055 - 0.3002 * (10 * 0.8))))

    weigh_factor = calc_bcv(crop,time)
    assert pytest.approx(weigh_factor) == max(bcv,bcv_snow)

def test_calc_bcv_correctly_calculates_all_weighing_factor_scenarios():
    crop = mock_crop()
    time1 = mock_time(day = 250)
    time2 = mock_time(day = 360)

    bcv = 5.0 / (5.0 + exp(7.563 - .0001297 * (-5.0)))
    bcv_snow1 = (0/ (0+ exp(6.055 - 0.3002 * 0)))
    bcv_snow2 = ((10 * 0.8)/ ((10 * 0.8)+ exp(6.055 - 0.3002 * (10 * 0.8))))

    weigh_factor1 = calc_bcv(crop,time1)
    weigh_factor2 = calc_bcv(crop,time2)

    tests = [
       pytest.approx(weigh_factor1) == max(bcv,bcv_snow1),
       pytest.approx(weigh_factor2) == max(bcv,bcv_snow2)
    ]
    assert all(tests)


#the following test is for the calc_albedo() function
def test_calc_albedo_correctly_calculates_albedo():
    soil = mock_soil()
    crop = mock_crop()

    albedo = calc_albedo(soil,crop)

    assert pytest.approx(albedo) == 0.23 * (1- exp(-0.00005 * 5.0)) + 0.16 * exp(-0.00005 * 5.0)



#the following test is for the sum_soil_water() function
def test_sum_soil_water_correctly_calculates_sum():
    soil = mock_soil()
    sum = sum_soil_water(soil)

    assert pytest.approx(sum) == 10 + 10


#the following test is for the calc_dd_max() function
def test_calc_dd_max_correctly_calculates_max_depth():
    soil = mock_soil()

    max_damping_depth = calc_dd_max(soil)

    assert pytest.approx(max_damping_depth) == 1000 + (2500 * 3.5) / (3.5 + 686 * \
                                                    exp(-5.63 * 3.5))


#the following tesst is for the calc_scale() function
def test_calc_scale_correctly_calculates_scaling_factor():
    soil = mock_soil()

    #assumes sum_soil_water() works properly
    sum = sum_soil_water(soil)

    scaling_factor = calc_scale(soil)

    assert pytest.approx(scaling_factor) == sum / ((0.356-0.144 * 3.5) * 200)


#the following test is for the calc_dd() function
def test_calc_dd_correctly_calculates_damping_depth():
    soil = mock_soil()

    #assumes scale() and dd_max() work properly
    scale = calc_scale(soil)
    dd_max = calc_dd_max(soil)

    assert pytest.approx(calc_dd(soil)) == dd_max * exp((log(500/dd_max)) * \
        ((1 - scale) / (1 + scale)) ** 2)
        

#calc_radiate() tests...assumes dependencies work properly
def test_calc_radiate_correctly_calculates_radiation_term():
    soil = mock_soil()
    crop = mock_crop()
    weather = mock_weather()
    time = mock_time()

    albedo = calc_albedo(soil,crop)

    assert pytest.approx(calc_radiate(soil,crop,weather,time)) == (3.5 * (1-albedo)-14) / 20

#calc_T_bare()...assumes dependencies work properly
def test_calc_T_bare_correctly_calculates_theoretical_bare_soil_temp():
    soil = mock_soil()
    crop = mock_crop()
    weather = mock_weather()
    time = mock_time()

    radiate = calc_radiate(soil,crop,weather,time)

    assert pytest.approx(calc_T_bare(soil,crop,weather,time)) == 20 + radiate * 20

#calc_T_surf...assumes dependencies work correctly
def test_calc_T_surf_correctly_calculates_surface_temperature():
    soil = mock_soil()
    crop = mock_crop()
    weather = mock_weather()
    time = mock_time()

    T_bare = calc_T_bare(soil,crop,weather,time)
    bcv = calc_bcv(crop,time)

    calc_T_surf(soil,crop,weather,time)

    assert pytest.approx(soil.T_surf) == (bcv * 22.4) + ((1-bcv) * T_bare)

#calc_T_soil 






