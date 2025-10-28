from unittest.mock import MagicMock

import pytest
from pytest_mock import MockFixture

from RUFAS.biophysical.field.crop.crop_data import CropData
from RUFAS.biophysical.field.crop.water_dynamics import WaterDynamics

from tests.test_biophysical.test_crop_soil_field.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


@pytest.fixture
def mock_crop_data() -> CropData:
    return CropData(**SAMPLE_CROP_CONFIGURATION)


# ---- helper functions tests ----
@pytest.mark.parametrize(
    "evap,trans",
    [(0, 0), (0, 1), (1, 0), (1, 0), (-1, 0), (0, -1), (-1, -1), (0.32, 1.357)],
)
def test_determine_evapotranspiration(evap: float, trans: float) -> None:
    """ensure that evapotranspiration is correclty calculated"""
    assert WaterDynamics._determine_evapotranspiration(evap, trans) == evap + trans


@pytest.mark.parametrize(
    "et,max_et",
    [
        (1, 1),  # all 1
        (0, 0),  # all 0
        (0, 1),  # evapotranspiration = 0
        (1, 0),  # max_evapotrans = 0
        (1, 0.29),  # fractional max_evapotranspiration
        (0.38, 0.29),  # both fractional
        (135.77, 2001.5),  # arbitrary evapotranspiration < max_evapotranspiration
        (821.0, 533.53),  # arbitrary evapotranspiration > max_evapotranspiration
    ],
)
def test_determine_water_deficiency(et: float, max_et: float) -> None:
    """ensure that water deficiency is properly calculated"""
    if max_et == 0:
        expect = 0
    else:
        expect = 100 * (et / max_et)
    assert WaterDynamics._determine_water_deficiency(et, max_et) == expect


@pytest.mark.parametrize(
    "leaf_area_index,potential_evapotrans_adj",
    [
        (0, 0),
        (1.2, 1.6),
        (3.6, 3.6),
        (2.5, 2.69678),
    ],
)
def test_determine_maximum_transpiration(leaf_area_index: float, potential_evapotrans_adj: float) -> None:
    observe = WaterDynamics._determine_maximum_transpiration(leaf_area_index, potential_evapotrans_adj)
    if leaf_area_index > 3:
        assert observe == potential_evapotrans_adj
    else:
        assert observe == ((leaf_area_index * potential_evapotrans_adj) / 3)


# ---- member function tests ----


@pytest.mark.parametrize(
    "evap,trans,et_max",
    [
        (50, 50, 100),  # max_evapotranspiration = evap + trans
        (45, 50, 100),  # evap < trans
        (50, 33, 100),  # evap > trans
        (50, 50, 80),  # max_evapotranspiration < evap + trans
        (0.45, 0.50, 0.10),  # fractional
        (132.58, 72.01, 635.2),  # arbitrary
    ],
)
def test_cycle_water(mocker: MockFixture, mock_crop_data: CropData, evap: float, trans: float, et_max: float) -> None:
    """Integration test to check that water cycling routines are properly carried out."""
    mock_crop_data.cumulative_evaporation = 0
    mock_crop_data.cumulative_transpiration = 0
    mock_crop_data.cumulative_potential_evapotranspiration = 0
    mock_crop_data.cumulative_water_uptake = 10.0
    water_dyn = WaterDynamics(mock_crop_data, cumulative_evapotranspiration=0)
    water_deficiency = mocker.patch.object(water_dyn, "_determine_water_deficiency", return_value=0.8)

    water_dyn.cycle_water(evap, trans, et_max)

    water_deficiency.assert_called_once_with(10.0, et_max)
    actual = [
        water_dyn.data.cumulative_evaporation,
        water_dyn.data.cumulative_transpiration,
        water_dyn.cumulative_evapotranspiration,
        water_dyn.data.cumulative_potential_evapotranspiration,
        water_dyn.data.water_deficiency,
    ]
    expected = [evap, trans, evap + trans, et_max, 0.8]
    assert actual == expected


@pytest.mark.parametrize(
    "evapotranspirative_demand,canopy_water,expected_evaporation,expected_water",
    [
        (13.44, 5.66, 5.66, 0.0),
        (12.334, 12.334, 12.334, 0.0),
        (2.41, 6.5, 2.41, 4.09),
        (0.0, 0.0, 0.0, 0.0),
        (3.5, 0.0, 0.0, 0.0),
        (0.0, 4.8, 0.0, 4.8),
    ],
)
def test_evaporate_from_canopy(
    mock_crop_data: CropData,
    evapotranspirative_demand: float,
    canopy_water: float,
    expected_evaporation: float,
    expected_water: float,
) -> None:
    """Tests that the correct amount of water is evaporated from crop canopy and the correct amount of evaporation was
    returned."""
    mock_crop_data.canopy_water = canopy_water
    incorp = WaterDynamics(mock_crop_data)

    actual_evaporation = incorp.evaporate_from_canopy(evapotranspirative_demand)
    actual_water = incorp.data.canopy_water

    assert actual_evaporation == expected_evaporation
    assert actual_water == expected_water


@pytest.mark.parametrize(
    "leaf_area_index,potential_evapotranspiration_adjusted",
    [(1.8, 50.44), (4.5, 15.556), (3.3, 0.0)],
)
def test_set_maximum_transpiration(
    mock_crop_data: CropData, leaf_area_index: float, potential_evapotranspiration_adjusted: float
) -> None:
    """Tests that the maximum transpiration of a crop is set correctly."""
    mock_crop_data.max_transpiration = 0
    mock_crop_data.leaf_area_index = leaf_area_index
    incorp = WaterDynamics(mock_crop_data)
    incorp._determine_maximum_transpiration = MagicMock(return_value=18.5)

    incorp.set_maximum_transpiration(potential_evapotranspiration_adjusted)

    incorp._determine_maximum_transpiration.assert_called_once_with(
        leaf_area_index, potential_evapotranspiration_adjusted
    )
    assert incorp.data.max_transpiration == 18.5
