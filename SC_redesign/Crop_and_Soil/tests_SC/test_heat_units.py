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
def test_determine_new_heat_units(temp, min_t):
    """check that new heat units are correctly calculated by calc_new_heat_units()"""
    diff = temp - min_t
    if diff < 0:
        expect = 0
    else:
        expect = diff
    assert HeatUnits.determine_new_heat_units(temp, min_t) == expect


@pytest.mark.parametrize("air,plant", [
    (100, 50),
    (50, 100),
    (100, 100)
])
def test_determine_minimum_heat_unit_temperature(air, plant):
    """check that minimum heat units are properly calculated by calc_minimum_heat_unit_temperature()"""
    if air < plant:
        expect = plant
    else:
        expect = air
    assert HeatUnits.determine_minimum_heat_unit_temperature(air, plant) == expect


@pytest.mark.parametrize("air,plant", [
    (100, 50),
    (50, 100),
    (100, 100)
])
def test_determine_maximum_heat_unit_temperature(air, plant):
    """check that maximum heat units are properly calculated by calc_maximum_heat_unit_temperature()"""
    if air > plant:
        expect = plant
    else:
        expect = air
    assert HeatUnits.determine_maximum_heat_unit_temperature(air, plant) == expect


# ---- initializer function ----
def init_heat(**kwargs):
    """helper function to create HeatUnits instance, with specified attributes"""
    heat = HeatUnits()
    for key, val in kwargs.items():
        setattr(heat, key, val)
    return heat


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


@pytest.mark.parametrize("temp", [0, 20.5, None])
def test_accumulate_heat_units(temp, mocker: MockerFixture):
    """check that accumulate_heat_units() calls the right functions"""
    patch_a = mocker.patch("SC_redesign.Crop_and_Soil.crop.heat_units.HeatUnits.assign_new_heat_units")
    patch_b = mocker.patch("SC_redesign.Crop_and_Soil.crop.heat_units.HeatUnits.add_heat_units")
    heat = init_heat()
    expect = init_heat()
    heat.accumulate_heat_units(temp)
    expect.assign_new_heat_units(temp)
    expect.add_heat_units()
    assert heat.accumulated_heat_units == expect.accumulated_heat_units
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
        assert heat.new_heat_units == HeatUnits.determine_new_heat_units(25, 15)
    else:
        assert heat.new_heat_units == HeatUnits.determine_new_heat_units(temp, 15)


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


@pytest.mark.parametrize("mean,min,max,use_heat_unit_temp", [
    (25, 21, 28, True),
    (25, 21, 28, False),
    (None, 21, 28, True),
    (None, 0, 17, True),
    (18, -3, 33, True),
    (18, -2, 36, False),
    (None, -6, 20, True),
    (27, 18, 23, False),    # Mean outside of min-max range
    (27, 18, 23, True),     # Same as above
    (None, 18, 13, True),   # Min greater than max
    (26, 18, 14, False)     # Same as above
])
def test_absorb_heat_units(mean, min, max, use_heat_unit_temp):
    heat = init_heat(use_heat_unit_temperature=use_heat_unit_temp)
    heat.absorb_heat_units(mean, min, max)
    assert heat.use_heat_unit_temperature == use_heat_unit_temp
    if use_heat_unit_temp:
        expect_max_heat_unit_temp = HeatUnits.determine_maximum_heat_unit_temperature(max, 38)
        assert expect_max_heat_unit_temp == heat.maximum_heat_unit_temperature
        expect_min_heat_unit_temp = HeatUnits.determine_minimum_heat_unit_temperature(min, 20)
        assert expect_min_heat_unit_temp == heat.minimum_heat_unit_temperature
        expect_heat_unit_temp = (expect_min_heat_unit_temp / 2) + (expect_max_heat_unit_temp / 2)
        assert expect_heat_unit_temp == heat.heat_unit_temperature
    if use_heat_unit_temp or mean is None:
        use_temp = expect_heat_unit_temp
    else:
        use_temp = mean
    if 20 <= use_temp <= 38:
        expect_is_growing = True
    else:
        expect_is_growing = False
    assert expect_is_growing == heat.is_growing
    if use_heat_unit_temp or (mean is None):
        expect_new_heat_units = HeatUnits.determine_new_heat_units(expect_heat_unit_temp, 20)
    else:
        expect_new_heat_units = HeatUnits.determine_new_heat_units(mean, 20)
    assert heat.use_heat_unit_temperature == use_heat_unit_temp
    assert expect_new_heat_units == heat.accumulated_heat_units
    assert heat.previous_heat_fraction is None
    expect_heat_fraction = expect_new_heat_units / 800
    assert expect_heat_fraction == heat.heat_fraction
    assert heat.is_mature == (expect_heat_fraction >= 1)
