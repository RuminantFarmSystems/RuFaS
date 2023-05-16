import pytest
from unittest.mock import MagicMock
from SC_redesign.Crop_and_Soil.crop.water_dynamics import WaterDynamics
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData


# ---- helper functions tests ----
@pytest.mark.parametrize("evap,trans", [
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 0),
    (-1, 0),
    (0, -1),
    (-1, -1),
    (0.32, 1.357)
])
def test_determine_evapotranspiration(evap, trans):
    """ensure that evapotranspiration is correclty calculated"""
    assert WaterDynamics._determine_evapotranspiration(evap, trans) == evap + trans


@pytest.mark.parametrize("et,max_et", [
    (1, 1),  # all 1
    (0, 0),  # all 0
    (0, 1),  # evapotranspiration = 0
    (1, 0),  # max_evapotrans = 0
    (1, 0.29),  # fractional max_evapotranspiration
    (0.38, 0.29),  # both fractional
    (135.77, 2001.5),  # arbitrary evapotranspiration < max_evapotranspiration
    (821.0, 533.53)  # arbitrary evapotranspiration > max_evapotranspiration

])
def test_determine_water_deficiency(et, max_et):
    """ensure that water deficiency is properly calculated"""
    if max_et == 0:
        expect = 0
    else:
        expect = 100 * (et / max_et)
    assert WaterDynamics._determine_water_deficiency(et, max_et) == expect


@pytest.mark.parametrize("leaf_area_index,potential_evapotrans_adj", [
    (0, 0),
    (1.2, 1.6),
    (3.6, 3.6),
    (2.5, 2.69678),
])
def test_determine_maximum_transpiration(leaf_area_index, potential_evapotrans_adj):
    observe = WaterDynamics._determine_maximum_transpiration(leaf_area_index, potential_evapotrans_adj)
    if leaf_area_index > 3:
        assert observe == potential_evapotrans_adj
    else:
        assert observe == ((leaf_area_index * potential_evapotrans_adj) / 3)


# ---- member function tests ----

@pytest.mark.parametrize("evap,trans,et_max", [
    (50, 50, 100),  # max_evapotranspiration = evap + trans
    (45, 50, 100),  # evap < trans
    (50, 33, 100),  # evap > trans
    (50, 50, 80),  # max_evapotranspiration < evap + trans
    (0.45, 0.50, 0.10),  # fractional
    (132.58, 72.01, 635.2),  # arbitrary
])
def test_cycle_water(evap, trans, et_max):
    """integration test to check that water cycling routines are properly carried out"""
    data = CropData(cumulative_evaporation=0, cumulative_transpiration=0, cumulative_evapotranspiration=0,
                    cumulative_potential_evapotranspiration=0)
    water_dyn = WaterDynamics(data)
    water_dyn.cycle_water(evap, trans, et_max)
    expected = [water_dyn.data.cumulative_evaporation, water_dyn.data.cumulative_transpiration,
                water_dyn.data.cumulative_evapotranspiration, water_dyn.data.cumulative_potential_evapotranspiration,
                water_dyn.data.water_deficiency]
    observed = [evap, trans, evap + trans, et_max, WaterDynamics._determine_water_deficiency(evap + trans, et_max)]
    assert expected == observed


@pytest.mark.parametrize("evapotranspirative_demand,canopy_water,expected_evaporation,expected_water", [
    (13.44, 5.66, 5.66, 0.0),
    (12.334, 12.334, 12.334, 0.0),
    (2.41, 6.5, 2.41, 4.09),
    (0.0, 0.0, 0.0, 0.0),
    (3.5, 0.0, 0.0, 0.0),
    (0.0, 4.8, 0.0, 4.8)
])
def test_evaporate_from_canopy(evapotranspirative_demand: float, canopy_water: float, expected_evaporation: float,
                               expected_water: float) -> None:
    """Tests that the correct amount of water is evaporated from crop canopy and the correct amount of evaporation was
        returned."""
    data = CropData(canopy_water=canopy_water)
    incorp = WaterDynamics(data)

    actual_evaporation = incorp.evaporate_from_canopy(evapotranspirative_demand)
    actual_water = incorp.data.canopy_water

    assert actual_evaporation == expected_evaporation
    assert actual_water == expected_water


@pytest.mark.parametrize("leaf_area_index,potential_evapotranspiration_adjusted", [
    (1.8, 50.44),
    (4.5, 15.556),
    (3.3, 0.0)
])
def test_set_maximum_transpiration(leaf_area_index: float, potential_evapotranspiration_adjusted: float) -> None:
    """Tests that the maximum transpiration of a crop is set correctly."""
    data = CropData(max_transpiration=0, leaf_area_index=leaf_area_index)
    incorp = WaterDynamics(data)
    incorp._determine_maximum_transpiration = MagicMock(return_value=18.5)

    incorp.set_maximum_transpiration(potential_evapotranspiration_adjusted)

    incorp._determine_maximum_transpiration.assert_called_once_with(leaf_area_index,
                                                                    potential_evapotranspiration_adjusted)
    assert incorp.data.max_transpiration == 18.5
