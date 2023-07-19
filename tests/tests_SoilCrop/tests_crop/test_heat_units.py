"""
RUFAS: Ruminant Farm Systems Model
File name: test_heat_units.py
Description: Implements test cases
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

from RUFAS.routines.field.crop.crop_types.base_crop import BaseCrop
from RUFAS.classes import Weather, Time
from RUFAS.routines.field.crop.heat_units import *
from unittest.mock import MagicMock
import pytest


def mock_crop(T_base_min = 2.5,T_base_max = 40 ,fr_PHU = .42,PHU = 8.8,accumulated_HU= .25):
    """
    Description:
        Creates a BaseCrop class mocking object for use as input for functions. It is initialized with the
        arguments provided; arguments are dynamic and can be changed/added to as needed.

    Args:
        T_base_min (float): BaseCrop attribute, minimum temperature required for crop growth
        T_base_max (float): BaseCrop attribute, maximum temperature required to sustain growth
        fr_PHU (float): BaseCrop attribute, fraction of PHU accumulated including current day
        PHU (float): BaseCrop attribute, total heat units required for maturity
        accumulated_HU (float): BaseCrop attribute, heat units accumulated including current day

    Returns:
        BaseCrop class mocking object
    """
    mcrop = MagicMock(BaseCrop)

    mcrop.T_base_min = T_base_min
    mcrop.T_base_max = T_base_max
    mcrop.fr_PHU = fr_PHU
    mcrop.PHU = PHU
    mcrop.accumulated_HU = accumulated_HU

    return mcrop

def mock_weather(T_min = [[2.5]], T_max = [[40]]):
    """
    Description:
        Creates a Weather class mocking object for use as input for functions. It is initialized with the
        arguments provided; arguments are dynamic and can be changed/added to as needed.

    Args:
        T_min (obj): Weather attribute, nested list  containing the minimum temperature of each day in each year
        T_max (obj): Weather attribute, nested list containing the maximum temperature of each day in each year

    Returns:
        Weather class mocking object
    
    """
    mweather = MagicMock(Weather)

    mweather.T_min = T_min
    mweather.T_max = T_max
    
    return mweather

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



#calc_HU
def test_calc_HU_correctly_calculates_available_heat_units():
    """
    Description:
        Using mocking, tests if the calc_HU() function in RUFAS/routines/field/crop/heat_units.py
        correctly returns the proper available HU given that the average heat units temperature on the
        given day is larger than the T_base_min of the crop.

    """
    crop = mock_crop()

    T_HU_min = 15
    T_HU_max = 23

    assert pytest.approx(calc_HU(crop,T_HU_min,T_HU_max)) == ((T_HU_min + T_HU_max)/2) - 2.5

def test_calc_HU_correctly_returns_zero_for_large_min_HU_temp():
    """
    Description:
        Using mocking, tests if the calc_HU() function in RUFAS/routines/field/crop/heat_units.py
        correctly returns 0 given that the T_base_min of the crop is larger than the average heat units
        temperature on the given day.
        
    """
    crop = mock_crop()

    T_HU_min = 1.5
    T_HU_max = 2.7

    assert pytest.approx(calc_HU(crop,T_HU_min,T_HU_max)) == 0.0


#calc_T_HU_max()
def test_calc_T_HU_max_correctly_calculates_max_HU_temp_larger_T_base_max():
    """
    Description:
        Using mocking, tests if the calc_T_HU_max() function in RUFAS/routines/field/crop/heat_units.py
        correctly returns the correct maximum heat unit temperature given that the crop T_base_max is larger 
        than the maximum HU temperature of the current day

    """
    crop = mock_crop()

    T_max = 30

    assert pytest.approx(calc_T_HU_max(crop,T_max)) == 30

def test_calc_T_HU_max_correctly_calculates_max_HU_temp_smaller_T_base_max():
    """
    Description:
        Using mocking, tests if the calc_T_HU_max() function in RUFAS/routines/field/crop/heat_units.py
        correctly returns the correct maximum heat unit temperature given that the maximum HU temperature
        for the current day is larger than the crop's T_base_max.

    """
    crop = mock_crop(T_base_max=23)

    T_max = 30

    assert pytest.approx(calc_T_HU_max(crop,T_max)) == 23


#calc_T_HU_min
def test_calc_T_HU_min_correctly_calculates_min_HU_temp_larger_T_base_min():
    """
    Description:
        Using mocking, tests if the calc_T_HU_max() function in RUFAS/routines/field/crop/heat_units.py
        correctly returns the correct maximum heat unit temperature given that the crop's T_base_min is 
        larger than the minimum HU temperature on the given day.

    """
    crop = mock_crop()

    T_min = 1.5

    assert pytest.approx(calc_T_HU_min(crop,T_min)) == 2.5


def test_calc_T_HU_min_correctly_calculates_min_HU_temp_smaller_T_base_min():
    """
    Description:
        Using mocking, tests if the calc_T_HU_min() function in RUFAS/routines/field/crop/heat_units.py
        correctly returns the correct minimum heat unit temperature given that the minimum HU temperature
        for the current day is larger than the crop's T_base_min.

    """
    crop = mock_crop(T_base_min = 1.0)

    T_min = 1.5

    assert pytest.approx(calc_T_HU_min(crop,T_min)) == 1.5

#calculate_fr_PHU()
#all tests assume correctness of inner function calls
def test_calculate_fr_PHU_correctly_sets_prev_accumulated_HU():
    """
    Description:
        Tests that the BaseCrop attribute prev_accumulated_HU is set correctly during the 
        execution of the calculate_fr_PHU() function in RUFAS/routines/field/crop/heat_units.py

    """
    crop = mock_crop()
    weather = mock_weather()
    time = mock_time()

    calculate_fr_PHU(crop, weather, time)

    assert pytest.approx(crop.prev_accumulated_HU) == .25

def test_calculate_fr_PHU_correctly_sets_accumulated_HU():
    """
    Description:
        Tests that the BaseCrop attribute accumulated_HU is calculated and set correctly during the 
        execution of the calculate_fr_PHU() function in RUFAS/routines/field/crop/heat_units.py

    """
    crop = mock_crop()
    weather = mock_weather()
    time = mock_time()

    calculate_fr_PHU(crop, weather, time)

    T_min = 2.5
    T_max = 40
    T_HU_min = calc_T_HU_min(crop,T_min)
    T_HU_max = calc_T_HU_max(crop,T_max)
    HU = calc_HU(crop,T_HU_min,T_HU_max)

    assert pytest.approx(crop.accumulated_HU) == HU + .25
    
def test_calculate_fr_PHU_correctly_sets_prev_fr_PHU():
    """
    Description:
        Tests that the BaseCrop attribute prev_fr_PHU is set correctly during the 
        execution of the calculate_fr_PHU() function in RUFAS/routines/field/crop/heat_units.py

    """
    crop = mock_crop()
    weather = mock_weather()
    time = mock_time()

    calculate_fr_PHU(crop, weather, time)

    assert pytest.approx(crop.prev_fr_PHU) == .42

def test_calculate_fr_PHU_correctly_sets_fr_PHU():
    """
    Description:
        Tests that the BaseCrop attribute fr_PHU is calculated and set correctly during the 
        execution of the calculate_fr_PHU() function in RUFAS/routines/field/crop/heat_units.py

    """
    crop = mock_crop()
    weather = mock_weather()
    time = mock_time()

    calculate_fr_PHU(crop, weather, time)

    T_min = 2.5
    T_max = 40
    T_HU_min = calc_T_HU_min(crop,T_min)
    T_HU_max = calc_T_HU_max(crop,T_max)
    HU = calc_HU(crop,T_HU_min,T_HU_max)

    assert pytest.approx(crop.fr_PHU) == (.25 + HU) / 8.8







