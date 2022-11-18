"""
RUFAS: Ruminant Farm Systems Model
File name: test_heat_units.py
Description: Implements test cases
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

import pytest
from SC_redesign.Crop_and_Soil.crop.heat_units import *

# ---- test helper functions ----
@pytest.mark.parametrize("temp,min", [
    (0, 0),  # all zero
    (1, 1),  # all 1
    (1, 0),  # temp > min
    (0, 1),  # min > temp
    (23.59, 18.4),  # arbitrary
    (13.77, 29.9),  # arbitrary
])
def test_calc_new_heat_units(temp, min):
    """check that new heat units are correctly calculated by calc_new_heat_units()"""
    diff = temp - min
    if diff < 0:
        expect = 0
    else:
        expect = diff
    assert calc_new_heat_units(temp, min) == expect

@pytest.mark.parametrize("air,plant", [
    (100, 50),
    (50, 100),
    (100, 100)
])
def test_calc_minimum_heat_unit_temperature(air, plant):
    """check that minimum heat units are properly calculated by calc_minimum_heat_unit_temperature()"""
    if air < plant:
        expect = plant
    else:
        expect = air
    assert calc_minimum_heat_unit_temperature(air, plant) == expect

@pytest.mark.parametrize("air,plant", [
    (100, 50),
    (50, 100),
    (100, 100)
])
def test_calc_maximum_heat_unit_temperature(air, plant):
    """check that maximum heat units are properly calculated by calc_maximum_heat_unit_temperature()"""
    if air > plant:
        expect = plant
    else:
        expect = air
    assert calc_maximum_heat_unit_temperature(air, plant) == expect

# ---- initializer function ----
def init_heat(**kwargs):
    """helper function to create HeatUnits instance, with specified attributes"""
    heat = HeatUnits()
    for key, val in kwargs.items():
        setattr(heat, key, val)
    return heat

@pytest.mark.parametrize("use_alt,temp", [
    (False, 12.6),  # main method
    (False, 18.9),  # main method
    (False, 35.5),  # alt method
    (False, None),  # main method, no temp
    (True, 9.4),  # alt method
    (True, 25.3),  # alt method
    (True, 32.0),  # alt method
    (True, None),  # alt method, no temp
])
def test_check_growth_conditions(use_alt, temp):
    """check that the is_growing flag is properly set according to heat units"""
    heat = init_heat(use_heat_unit_temperature=use_alt, minimum_temperature=15.6, maximum_temperature=30.1,
                     heat_unit_temperature=22.4)
    heat.check_growth_conditions(temp)
    if use_alt or temp is None:
        above = 22.4 >= 15.6
        below = 22.4 <= 30.1
    else:
        above = temp >= 15.6
        below = temp <= 30.1
    assert heat.is_growing == (above and below)

@pytest.mark.parametrize("yes", [True, False])
def test_decide_to_use_heat_unit_temperature(yes):
    """check that the flag to use alternative heat unit accumulation method is correctly set"""
    heat = init_heat()
    heat.decide_to_use_heat_unit_temperature(yes)
    assert heat.use_heat_unit_temperature == yes

@pytest.mark.parametrize("use_alt,meant,mint,maxt",[
    (False, None, 18, 20),
    (True, 13.6, None, None),
    (True, 18.9, 20.6, None),
    (True, 22.4, None, 1.5),
    (True, None, None, None),
    (False, None, None, None)
])
def test_check_absorb_heat_for_input_errors(use_alt, meant, mint, maxt):
    """check that errors are thrown when improper input is given, using _check_absorb_heat_for_input_errors"""
    heat = init_heat(use_heat_unit_temperature=use_alt)
    with pytest.raises(ValueError):
        heat._check_absorb_heat_for_input_errors(meant, mint, maxt)

@pytest.mark.parametrize("air_min,air_max,crop_min,crop_max", [
    (1, 1, 1, 1),
    (0, 0, 0, 0),
    (0, 1, 0, 1),
    (0, 3, 1, 2),
    (1, 2, 0, 3),
    # arbitrary
    (18.25, 33.4, 15.0, 35.0),  # air within crop
    (12.31, 33.4, 15.0, 35.0),  # air_min < crop_min
    (18.25, 40.7, 15.0, 35.0),  # air_max > crop_max
    (12.31, 40.7, 15.0, 35.0),  # crop within air
])
def test_determine_heat_unit_temperature(air_min, air_max, crop_min, crop_max):
    """check that heat unit temperature sets variables correctly"""
    obs_min = calc_minimum_heat_unit_temperature(air_min, crop_min)
    obs_max = calc_maximum_heat_unit_temperature(air_max, crop_max)
    heat = init_heat(minimum_temperature = crop_min, maximum_temperature=crop_max)
    heat.determine_heat_unit_temperature(air_min, air_max)
    assert heat.minimum_heat_unit_temperature == obs_min
    assert heat.maximum_heat_unit_temperature == obs_max
    assert heat.heat_unit_temperature == ((obs_min + obs_max) / 2)

def test_accumulate_heat_units():
    """check that accumulate_heat_units() is doing what it is supposed to"""
    raise ValueError("test that assign_new_heat_units() and add_heat_units() are both called once")

@pytest.mark.parametrize("use_alt,temp", [
    (True, 12),
    (True, 18),
    (True, 30),
    (True, None),
    (False, 12),
    (False, 18),
    (False, 30),
    (False, None),
])
def test_assign_new_heat_units(use_alt, temp):
    """check that assign_new_heat_units properly assigns heat units"""
    heat = init_heat(use_heat_unit_temperature=use_alt, heat_unit_temperature=25,
                     minimum_temperature=15)
    heat.assign_new_heat_units(temp)
    if use_alt or (temp is None):
        assert heat.new_heat_units == calc_new_heat_units(25, 15)
    else:
        assert heat.new_heat_units == calc_new_heat_units(temp, 15)

@pytest.mark.parametrize("start,new", [
    (0, 0),
    (0, 1),
    (1, 1),
    (0, 135.6),
    (18.55, 1002.5)
])
def test_add_heat_units(start, new):
    """check that heat units are accumulated properly"""
    heat = init_heat(accumulated_heat_units=start, new_heat_units=new)
    heat.add_heat_units()
    assert heat.accumulated_heat_units == start + new

@pytest.mark.parametrize("now,max,expect", [
    (1, 2, 0.5),
    (1, 1, 1),
    (0.25, 100, 0.0025),
    (133.59, 99.63, 133.59/99.63)
])
def test_determine_heat_fraction(now, max, expect):
    """check that heat fraction is properly calculated"""
    heat = init_heat(accumulated_heat_units=now, potential_heat_units=max)
    heat.determine_heat_fraction()
    assert heat.heat_fraction == expect

@pytest.mark.parametrize("frac,expect", [
    (0, False),
    (0.5, False),
    (1, True),
    (1.5, True)
])
def test_check_maturity(frac, expect):
    """check that check_maturity_by_heat_units is properly assigning maturity by heat fraction"""
    heat = init_heat(heat_fraction=frac)
    heat.check_maturity_by_heat_units()
    assert heat.is_mature == expect

@pytest.mark.parametrize("now", [0, 0.5, 1, 100, 35.399, -1])
def test_shift_heat_unit_time(now):
    """check that heat unit time is properly shifted"""
    heat = init_heat(heat_fraction=now)
    heat.shift_heat_unit_time()
    assert heat.previous_heat_fraction == now

# ---- test member functions ----
# @pytest.mark.parametrize("air,plant", [
#     (100, 50),
#     (50, 100),
# ])
# def test_determine_minimum_heat_units(air, plant):
#     hu = init_heat(min_growth_temp=plant)
#     hu.set_minimum_heat_unit_temperature(air)
#     assert hu.minimum_heat_unit_temperature == calc_minimum_heat_unit_temperature(air, plant)


# --- OLDER

# def mock_crop(T_base_min = 2.5,T_base_max = 40 ,fr_PHU = .42,PHU = 8.8,accumulated_HU= .25):
#     """
#     Description:
#         Creates a BaseCrop class mocking object for use as input for functions. It is initialized with the
#         arguments provided; arguments are dynamic and can be changed/added to as needed.
#
#     Args:
#         T_base_min (float): BaseCrop attribute, minimum temperature required for crop growth
#         T_base_max (float): BaseCrop attribute, maximum temperature required to sustain growth
#         fr_PHU (float): BaseCrop attribute, fraction of PHU accumulated including current day
#         PHU (float): BaseCrop attribute, total heat units required for maturity
#         accumulated_HU (float): BaseCrop attribute, heat units accumulated including current day
#
#     Returns:
#         BaseCrop class mocking object
#     """
#     mcrop = MagicMock(BaseCrop)
#
#     mcrop.T_base_min = T_base_min
#     mcrop.T_base_max = T_base_max
#     mcrop.fr_PHU = fr_PHU
#     mcrop.PHU = PHU
#     mcrop.accumulated_HU = accumulated_HU
#
#     return mcrop
#
# def mock_weather(T_min = [[2.5]], T_max = [[40]]):
#     """
#     Description:
#         Creates a Weather class mocking object for use as input for functions. It is initialized with the
#         arguments provided; arguments are dynamic and can be changed/added to as needed.
#
#     Args:
#         T_min (obj): Weather attribute, nested list  containing the minimum temperature of each day in each year
#         T_max (obj): Weather attribute, nested list containing the maximum temperature of each day in each year
#
#     Returns:
#         Weather class mocking object
#
#     """
#     mweather = MagicMock(Weather)
#
#     mweather.T_min = T_min
#     mweather.T_max = T_max
#
#     return mweather
#
# def mock_time(year = 1, day = 1):
#     """
#     Description:
#          Creates a Time class mocking object for use as input for functions. It is initialized with the
#         arguments provided; arguments are dynamic and can be changed/added to as needed.
#
#     Args:
#         year: Time attribute, current year
#         day: Time attribute, current day
#
#     Returns:
#         Time class mocking object
#
#     """
#     mtime = MagicMock(Time)
#
#     mtime.year = year
#     mtime.day = day
#
#     return mtime
#
#
#
# #calc_new_heat_units
# def test_calc_HU_correctly_calculates_available_heat_units():
#     """
#     Description:
#         Using mocking, tests if the calc_new_heat_units() function in RUFAS/routines/field/crop/heat_units.py
#         correctly returns the proper available HU given that the average heat units temperature on the
#         given day is larger than the T_base_min of the crop.
#
#     """
#     crop = mock_crop()
#
#     T_HU_min = 15
#     T_HU_max = 23
#
#     assert pytest.approx(calc_new_heat_units(crop,T_HU_min,T_HU_max)) == ((T_HU_min + T_HU_max)/2) - 2.5
#
# def test_calc_HU_correctly_returns_zero_for_large_min_HU_temp():
#     """
#     Description:
#         Using mocking, tests if the calc_new_heat_units() function in RUFAS/routines/field/crop/heat_units.py
#         correctly returns 0 given that the T_base_min of the crop is larger than the average heat units
#         temperature on the given day.
#
#     """
#     crop = mock_crop()
#
#     T_HU_min = 1.5
#     T_HU_max = 2.7
#
#     assert pytest.approx(calc_new_heat_units(crop,T_HU_min,T_HU_max)) == 0.0
#
#
# #calc_T_HU_max()
# def test_calc_T_HU_max_correctly_calculates_max_HU_temp_larger_T_base_max():
#     """
#     Description:
#         Using mocking, tests if the calc_T_HU_max() function in RUFAS/routines/field/crop/heat_units.py
#         correctly returns the correct maximum heat unit temperature given that the crop T_base_max is larger
#         than the maximum HU temperature of the current day
#
#     """
#     crop = mock_crop()
#
#     T_max = 30
#
#     assert pytest.approx(calc_T_HU_max(crop,T_max)) == 30
#
# def test_calc_T_HU_max_correctly_calculates_max_HU_temp_smaller_T_base_max():
#     """
#     Description:
#         Using mocking, tests if the calc_T_HU_max() function in RUFAS/routines/field/crop/heat_units.py
#         correctly returns the correct maximum heat unit temperature given that the maximum HU temperature
#         for the current day is larger than the crop's T_base_max.
#
#     """
#     crop = mock_crop(T_base_max=23)
#
#     T_max = 30
#
#     assert pytest.approx(calc_T_HU_max(crop,T_max)) == 23
#
#
# #calc_T_HU_min
# def test_calc_T_HU_min_correctly_calculates_min_HU_temp_larger_T_base_min():
#     """
#     Description:
#         Using mocking, tests if the calc_T_HU_max() function in RUFAS/routines/field/crop/heat_units.py
#         correctly returns the correct maximum heat unit temperature given that the crop's T_base_min is
#         larger than the minimum HU temperature on the given day.
#
#     """
#     crop = mock_crop()
#
#     T_min = 1.5
#
#     assert pytest.approx(calc_T_HU_min(crop,T_min)) == 2.5
#
#
# def test_calc_T_HU_min_correctly_calculates_min_HU_temp_smaller_T_base_min():
#     """
#     Description:
#         Using mocking, tests if the calc_T_HU_min() function in RUFAS/routines/field/crop/heat_units.py
#         correctly returns the correct minimum heat unit temperature given that the minimum HU temperature
#         for the current day is larger than the crop's T_base_min.
#
#     """
#     crop = mock_crop(T_base_min = 1.0)
#
#     T_min = 1.5
#
#     assert pytest.approx(calc_T_HU_min(crop,T_min)) == 1.5
#
# #calculate_fr_PHU()
# #all tests assume correctness of inner function calls
# def test_calculate_fr_PHU_correctly_sets_prev_accumulated_HU():
#     """
#     Description:
#         Tests that the BaseCrop attribute prev_accumulated_HU is set correctly during the
#         execution of the calculate_fr_PHU() function in RUFAS/routines/field/crop/heat_units.py
#
#     """
#     crop = mock_crop()
#     weather = mock_weather()
#     time = mock_time()
#
#     calculate_fr_PHU(crop, weather, time)
#
#     assert pytest.approx(crop.prev_accumulated_HU) == .25
#
# def test_calculate_fr_PHU_correctly_sets_accumulated_HU():
#     """
#     Description:
#         Tests that the BaseCrop attribute accumulated_HU is calculated and set correctly during the
#         execution of the calculate_fr_PHU() function in RUFAS/routines/field/crop/heat_units.py
#
#     """
#     crop = mock_crop()
#     weather = mock_weather()
#     time = mock_time()
#
#     calculate_fr_PHU(crop, weather, time)
#
#     T_min = 2.5
#     T_max = 40
#     T_HU_min = calc_T_HU_min(crop,T_min)
#     T_HU_max = calc_T_HU_max(crop,T_max)
#     HU = calc_new_heat_units(crop,T_HU_min,T_HU_max)
#
#     assert pytest.approx(crop.accumulated_HU) == HU + .25
#
# def test_calculate_fr_PHU_correctly_sets_prev_fr_PHU():
#     """
#     Description:
#         Tests that the BaseCrop attribute prev_fr_PHU is set correctly during the
#         execution of the calculate_fr_PHU() function in RUFAS/routines/field/crop/heat_units.py
#
#     """
#     crop = mock_crop()
#     weather = mock_weather()
#     time = mock_time()
#
#     calculate_fr_PHU(crop, weather, time)
#
#     assert pytest.approx(crop.prev_fr_PHU) == .42
#
# def test_calculate_fr_PHU_correctly_sets_fr_PHU():
#     """
#     Description:
#         Tests that the BaseCrop attribute fr_PHU is calculated and set correctly during the
#         execution of the calculate_fr_PHU() function in RUFAS/routines/field/crop/heat_units.py
#
#     """
#     crop = mock_crop()
#     weather = mock_weather()
#     time = mock_time()
#
#     calculate_fr_PHU(crop, weather, time)
#
#     T_min = 2.5
#     T_max = 40
#     T_HU_min = calc_T_HU_min(crop,T_min)
#     T_HU_max = calc_T_HU_max(crop,T_max)
#     HU = calc_new_heat_units(crop,T_HU_min,T_HU_max)
#
#     assert pytest.approx(crop.fr_PHU) == (.25 + HU) / 8.8
#
#
#
#
#
#
#
