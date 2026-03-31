import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.field.crop.crop_data import CropData
from RUFAS.biophysical.field.crop.heat_units import HeatUnits

from tests.test_biophysical.test_crop_soil_field.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


@pytest.fixture
def mock_crop_data() -> CropData:
    return CropData(**SAMPLE_CROP_CONFIGURATION)


# ---- test helper functions ----
@pytest.mark.parametrize(
    "temp,min_t",
    [
        (0, 0),  # all zero
        (1, 1),  # all 1
        (1, 0),  # temp > min_t
        (0, 1),  # min_t > temp
        (23.59, 18.4),  # arbitrary
        (13.77, 29.9),  # arbitrary
    ],
)
def test_determine_new_heat_units(temp: float, min_t: float) -> None:
    """check that new heat units are correctly calculated by calc_new_heat_units()"""
    diff = temp - min_t
    if diff < 0:
        expect = 0
    else:
        expect = diff
    assert HeatUnits._determine_new_heat_units(temp, min_t) == expect


@pytest.mark.parametrize("air,plant", [(100, 50), (50, 100), (100, 100)])
def test_determine_minimum_heat_unit_temperature(air: float, plant: float) -> None:
    """check that minimum heat units are properly calculated by calc_minimum_heat_unit_temperature()"""
    if air < plant:
        expect = plant
    else:
        expect = air
    assert HeatUnits._determine_minimum_heat_unit_temperature(air, plant) == expect


@pytest.mark.parametrize("air,plant", [(100, 50), (50, 100), (100, 100)])
def test_determine_maximum_heat_unit_temperature(air: float, plant: float) -> None:
    """check that maximum heat units are properly calculated by calc_maximum_heat_unit_temperature()"""
    if air > plant:
        expect = plant
    else:
        expect = air
    assert HeatUnits._determine_maximum_heat_unit_temperature(air, plant) == expect


@pytest.mark.parametrize("temp", [0, 20.5, None])
def test_accumulate_heat_units(mock_crop_data: CropData, temp: float | None, mocker: MockerFixture) -> None:
    """check that accumulate_heat_units() calls the right functions"""
    patch_a = mocker.patch("RUFAS.biophysical.field.crop.heat_units.HeatUnits.assign_new_heat_units")
    patch_b = mocker.patch("RUFAS.biophysical.field.crop.heat_units.HeatUnits.add_heat_units")

    heat = HeatUnits(mock_crop_data)
    expect = HeatUnits(mock_crop_data)

    heat.accumulate_heat_units(temp)
    expect.assign_new_heat_units(temp)
    expect.add_heat_units()

    assert heat.data.accumulated_heat_units == expect.data.accumulated_heat_units
    assert patch_a.assert_called_once
    assert patch_b.assert_called_once


@pytest.mark.parametrize(
    "use_alt,temp",
    [(True, 12), (True, 18), (True, 30), (True, None), (False, 12), (False, 18), (False, 30), (False, None)],
)
def test_assign_new_heat_units(mock_crop_data: CropData, use_alt: bool, temp: float | None) -> None:
    """check that assign_new_heat_units properly assigns heat units"""
    mock_crop_data.minimum_temperature = 15.0
    heat = HeatUnits(mock_crop_data, use_heat_unit_temperature=use_alt, heat_unit_temperature=25)
    heat.assign_new_heat_units(temp)
    if use_alt or (temp is None):
        assert heat.new_heat_units == HeatUnits._determine_new_heat_units(25, 15)
    else:
        assert heat.new_heat_units == HeatUnits._determine_new_heat_units(temp, 15)


@pytest.mark.parametrize("start,new", [(0, 0), (0, 1), (1, 1), (0, 135.6), (18.55, 1002.5)])
def test_add_heat_units(mock_crop_data: CropData, start: float, new: float) -> None:
    """check that heat units are accumulated properly"""
    mock_crop_data.accumulated_heat_units = start
    heat = HeatUnits(mock_crop_data, new_heat_units=new)
    heat.add_heat_units()
    assert mock_crop_data.accumulated_heat_units == start + new


@pytest.mark.parametrize(
    "mean,mint,maxt,use_heat_unit_temp",
    [
        (25, 21, 28, True),
        (25, 21, 28, False),
        (None, 21, 28, True),
        (None, 0, 17, True),
        (18, -3, 33, True),
        (18, -2, 36, False),
        (None, -6, 20, True),
        (27, 18, 23, False),  # Mean outside of min-max range
        (27, 18, 23, True),  # Same as above
        (None, 18, 13, True),  # Min greater than max
        (26, 18, 14, False),  # Same as above
    ],
)
def test_absorb_heat_units(
    mock_crop_data: CropData, mean: float | None, mint: float, maxt: float, use_heat_unit_temp: bool
) -> None:
    """Test that heat units are absorbed by a crop correctly."""
    mock_crop_data.minimum_temperature = 20.0
    mock_crop_data.potential_heat_units = (potential_heat_units := 800)
    heat = HeatUnits(mock_crop_data, use_heat_unit_temperature=use_heat_unit_temp, maximum_temperature=38)
    heat.absorb_heat_units(mean, mint, maxt)
    assert heat.use_heat_unit_temperature == use_heat_unit_temp

    expect_heat_unit_temp = None  # declaration
    if use_heat_unit_temp:
        expect_max_heat_unit_temp = HeatUnits._determine_maximum_heat_unit_temperature(maxt, 38)
        assert expect_max_heat_unit_temp == heat.maximum_heat_unit_temperature
        expect_min_heat_unit_temp = HeatUnits._determine_minimum_heat_unit_temperature(mint, 20)  # x
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
    assert expect_is_growing == mock_crop_data.is_growing

    if use_heat_unit_temp or (mean is None):
        expect_new_heat_units = HeatUnits._determine_new_heat_units(expect_heat_unit_temp, 20)
    else:
        expect_new_heat_units = HeatUnits._determine_new_heat_units(mean, 20)
    assert heat.use_heat_unit_temperature == use_heat_unit_temp
    assert expect_new_heat_units == mock_crop_data.accumulated_heat_units
    expect_heat_fraction = expect_new_heat_units / potential_heat_units
    assert expect_heat_fraction == mock_crop_data.heat_fraction
