import pytest
from SC_redesign.Crop_and_Soil.crop.water_dynamics import *


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

@pytest.mark.parametrize("evap,trans,et_max,potential_evapotrans_adj", [
    (50, 50, 100, 1.3),  # max_evapotranspiration = evap + trans
    (45, 50, 100, 2.4),  # evap < trans
    (50, 33, 100, 0.83),  # evap > trans
    (50, 50, 80, 1.22),  # max_evapotranspiration < evap + trans
    (0.45, 0.50, 0.10, 0),  # fractional
    (132.58, 72.01, 635.2, 2.01),  # arbitrary
])
def test_cycle_water(evap, trans, et_max, potential_evapotrans_adj):
    """integration test to check that water cycling routines are properly carried out"""
    data = CropData(cumulative_evaporation=0, cumulative_transpiration=0, cumulative_evapotranspiration=0,
                    cumulative_potential_evapotranspiration=0)
    water_dyn = WaterDynamics(data)
    water_dyn.cycle_water(evap, trans, et_max, potential_evapotrans_adj)
    expected = [water_dyn.data.cumulative_evaporation, water_dyn.data.cumulative_transpiration, water_dyn.data.cumulative_evapotranspiration,
                water_dyn.data.cumulative_potential_evapotranspiration, water_dyn.data.water_deficiency, water_dyn.data.max_transpiration]
    observed = [evap, trans, evap + trans, et_max, WaterDynamics._determine_water_deficiency(evap + trans, et_max),
                WaterDynamics._determine_maximum_transpiration(water_dyn.data.leaf_area_index, potential_evapotrans_adj)]
    assert expected == observed
