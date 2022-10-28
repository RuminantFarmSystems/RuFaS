"""
RUFAS: Ruminant Farm Systems Model
File name: test_heat_units.py
Description: Test cases for heat_units.py
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

from RUFAS.routines.field.crop.crop_types.base_crop import BaseCrop
from RUFAS.classes import Weather, Time
from RUFAS.routines.field.crop.heat_units import *
from tests.tests_SoilCrop.mock_classes import *
from unittest.mock import MagicMock
import pytest


@pytest.mark.parametrize(("T_HU_min","T_HU_max","T_base_min"),[
    (15, 23, 16), #arbitrary ints
    (0,0, 0), #zeroes
    (-1,-1, -1), #negatives
    (1, 1, 1), #ones
    (20.5, 25.3, 22.7)#T_base_min greater than T_HU
])
def test_calc_HU(T_HU_min, T_HU_max, T_base_min):
    """
    Description:
        Unit test for the calc_HU function in routines/field/crop/heat_units.py.
        Uses pytest.mark.parametrize to run several test cases at once.
    Args:
        T_HU_min
        T_HU_max
        T_base_min
    
    """
    crop = mock_crop(T_base_min = T_base_min)

    #using pseudocode C.2.A.1/2
    T_HU = (T_HU_min + T_HU_max) / 2

    if T_HU < T_base_min:
        T_HU = 0
    else:
        T_HU -= T_base_min
    
    assert pytest.approx(calc_HU(crop,T_HU_min,T_HU_max)) == T_HU


@pytest.mark.parametrize(("T_max","T_base_max"),[
    (18, 20), #T_base_max larger than T_max
    (0,0), #zeroes
    (1,1), #ones
    (-1,-1), #negatives
    (20,20), #equal
    (24.2, 23.1) #arbitrary floats, T_max larger than T_base_max
])
def test_calc_T_HU_max(T_max,T_base_max):
    """
    Description:
        Unit test for the calc_T_HU_max function in routines/field/crop/heat_units.py.
        Uses pytest.mark.parametrize to run several test cases at once.
    Args:
        T_max
        T_base_max
    """
    crop = mock_crop(T_base_max = T_base_max)

    #from crop pseudocode C.2.A.4
    max_temp = None
    if T_max > T_base_max:
        max_temp = T_base_max
    else:
        max_temp = T_max
    
    assert pytest.approx(calc_T_HU_max(crop,T_max)) == max_temp


@pytest.mark.parametrize(("T_min","T_base_min"),[
    (5, 6), #
    (0,0), #zeroes
    (1,1), #ones
    (-1,-1), #negatives
    (7.8,7.8), #equal
    (14.2, 13.1) #
])
def test_calc_T_HU_min(T_min, T_base_min):
    """
    Description:
        Unit test for the calc_T_HU_min function in routines/field/crop/heat_units.py.
        Uses pytest.mark.parametrize to run several test cases at once.
    Args:
        T_min
        T_base_min
    """
    crop = mock_crop(T_base_min = T_base_min)

    #from crop pseudocode C.2.A.4
    min_temp = None
    if T_min < T_base_min:
        min_temp = T_base_min
    else:
        min_temp = T_min
    
    assert pytest.approx(calc_T_HU_min(crop,T_min)) == min_temp


#for ease of mocking, year and day will remain 1 due 
#to the way they are used to access T_min and T_max in the weather object
@pytest.mark.parametrize(("fr_PHU","PHU","accumulated_HU","T_base_min","T_base_max",\
    "T_min","T_max","year","day"),[
        (.42,8.8,.25,6,19,[[2.5]],[[40]],1,1), #arbitrary numbers
        # (0,0,0,0,0,[[0]],[[0]],1,1), #zeroes
        (1,1,1,1,1,[[1]],[[1]],1,1), #ones
        (.78 ,12.1,.5,3.7,19.7,[[3.8]],[[29]],1,1), #more arbitrary numbers
])
def test_calculate_fr_PHU(fr_PHU, PHU, accumulated_HU,T_base_min,T_base_max, T_min, T_max, year, day):
    """
    Description:
        Unit test for calculate_fr_PHU() in routines/field/crop/heat_units.py.
        Uses pytest.mark.paramtrize to run multiple test cases for a single unittest.
        Any functions used inside of this unit test are assumed to be correct and properly
        tested.
    Args:
        fr_PHU
        PHU
        accumulated_HU
        T_base_min
        T_base_max
        T_min
        T_max
        year
        day
    """
    crop = mock_crop(fr_PHU = fr_PHU, PHU = PHU, accumulated_HU = accumulated_HU,T_base_min = T_base_min,T_base_max = T_base_max)
    weather = mock_weather(T_min = T_min, T_max = T_max)
    time = mock_time(year = year, day = day)

    #based on crop pseudocode C.2.B.1

    min = T_min[year-1][day-1]
    max = T_max[year-1][day-1]

    T_HU_min = calc_T_HU_min(crop,min)
    T_HU_max = calc_T_HU_max(crop,max)
    HU = calc_HU(crop,T_HU_min, T_HU_max)

    prev_accumulated_HU = accumulated_HU
    accumulated_HU += HU
    prev_fr_PHU = fr_PHU
    fr_PHU = accumulated_HU / PHU

    calculate_fr_PHU(crop,weather,time)

    assert pytest.approx([crop.prev_accumulated_HU,crop.accumulated_HU,crop.prev_fr_PHU,crop.fr_PHU])\
        == [prev_accumulated_HU,accumulated_HU,prev_fr_PHU,fr_PHU]


# def test_update_all():
#     pass





