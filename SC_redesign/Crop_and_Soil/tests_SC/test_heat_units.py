import pytest

from SC_redesign.Crop_and_Soil.crop.heat_units import *
from pytest_mock import MockerFixture

# ---- test helper functions ----
@pytest.mark.parametrize("temp,min_t", [
    (0, 0),  # all zero
    (1, 1),  # all 1
    (1, 0),  # temp > min_t
    (0, 1),  # min_t > temp
    (23.59, 18.4),  # arbitrary
    (13.77, 29.9),  # arbitrary
])
def test_calc_new_heat_units(temp, min_t):
    """check that new heat units are correctly calculated by calc_new_heat_units()"""
    diff = temp - min_t
    if diff < 0:
        expect = 0
    else:
        expect = diff
    assert calc_new_heat_units(temp, min_t) == expect

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

@pytest.mark.parametrize("use_alt,meant,min_t,max_t", [
    (False, None, 18, 20),
    (True, 13.6, None, None),
    (True, 18.9, 20.6, None),
    (True, 22.4, None, 1.5),
    (True, None, None, None),
    (False, None, None, None)
])
def test_check_absorb_heat_for_input_errors(use_alt, meant, min_t, max_t):
    """check that errors are thrown when improper input is given, using _check_absorb_heat_for_input_errors"""
    heat = init_heat(use_heat_unit_temperature=use_alt)
    with pytest.raises(ValueError):
        heat._check_absorb_heat_for_input_errors(meant, min_t, max_t)

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
    heat = init_heat(minimum_temperature=crop_min, maximum_temperature=crop_max)
    heat.determine_heat_unit_temperature(air_min, air_max)
    assert heat.minimum_heat_unit_temperature == obs_min
    assert heat.maximum_heat_unit_temperature == obs_max
    assert heat.heat_unit_temperature == ((obs_min + obs_max) / 2)

@pytest.mark.parametrize("temp", [0, 20.5, None])
def test_accumulate_heat_units(temp, mocker: MockerFixture):
    """check that accumulate_heat_units() calls the right functions"""
    patch_a = mocker.patch("SC_redesign.Crop_and_Soil.crop.heat_units.HeatUnits.assign_new_heat_units")
    patch_b = mocker.patch("SC_redesign.Crop_and_Soil.crop.heat_units.HeatUnits.add_heat_units")
    heat = init_heat()
    heat.accumulate_heat_units(temp)
    assert patch_a.assert_called_once
    assert patch_b.assert_called_once

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

@pytest.mark.parametrize("now,max_t,expect", [
    (1, 2, 0.5),
    (1, 1, 1),
    (0.25, 100, 0.0025),
    (133.59, 99.63, 133.59/99.63)
])
def test_determine_heat_fraction(now, max_t, expect):
    """check that heat fraction is properly calculated"""
    heat = init_heat(accumulated_heat_units=now, potential_heat_units=max_t)
    heat.determine_heat_fraction()
    assert heat.heat_fraction == expect


@pytest.mark.parametrize("now", [0, 0.5, 1, 100, 35.399, -1])
def test_shift_heat_unit_time(now):
    """check that heat unit time is properly shifted"""
    heat = init_heat(heat_fraction=now)
    heat.shift_heat_unit_time()
    assert heat.previous_heat_fraction == now
