import pytest

from SC_redesign.Crop_and_Soil.soil.evapotranspiration import *
from unittest.mock import patch, MagicMock


# --- static function tests ---
@pytest.mark.parametrize("avg_temp", [
    12.86878,
    0,
    (-2.586948),
    20.4486,
])
def test_determine_latent_heat_vaporization(avg_temp):
    observe = Evapotranspiration._determine_latent_heat_vaporization(avg_temp)
    expect = 2.501 - (0.002361 * avg_temp)
    assert expect == observe


@pytest.mark.parametrize("extraterrestrial_radiation,max_temp,min_temp,avg_temp", [
    (100, 28, 10, 14),
    (568, 20, 14, 18),
    (568, 20, 14, None),
    (80, 14, 0, 8),
    (678.0098, 26.8896, 10.3339, 18.3345),
])
def test_potential_evapotranspiration(extraterrestrial_radiation, max_temp, min_temp, avg_temp):
    observe = Evapotranspiration._determine_potential_evapotranspiration(extraterrestrial_radiation, max_temp, min_temp,
                                                                         avg_temp)
    if avg_temp is not None:
        latent_heat = Evapotranspiration._determine_latent_heat_vaporization(avg_temp)
        expect = (0.0023 * extraterrestrial_radiation * ((max_temp - min_temp) ** (-0.5)) * (avg_temp + 17.8)) / \
                 latent_heat
    else:
        latent_heat = Evapotranspiration._determine_latent_heat_vaporization((max_temp + min_temp) / 2)
        expect = (0.0023 * extraterrestrial_radiation * ((max_temp - min_temp) ** (-0.5)) * (((max_temp + min_temp) / 2)
                                                                                             + 17.8)) / latent_heat
    assert observe == expect

    # check that _determine_potential_evapotranspiration() actually calls _determine_latent_heat_vaporization once
    # @TODO: make this patch work, throws AttributeError. Currently tests pass because heat_vaporization is before
    # potential_evapotranspiration
    # p = patch("SC_redesign.Crop_and_Soil.soil.evapotranspiration._determine_latent_heat_vaporization",
    #           new=MagicMock(return_value=1.3))
    # p.start()
    Evapotranspiration._determine_latent_heat_vaporization = MagicMock(return_value=1.3)
    throwaway = Evapotranspiration._determine_potential_evapotranspiration(extraterrestrial_radiation, max_temp,
                                                                           min_temp, avg_temp)
    Evapotranspiration._determine_latent_heat_vaporization.assert_called_once()
    # p.stop()


@pytest.mark.parametrize("above_ground_biomass,residue,snow_water", [
    (400, 65, 0.3),
    (800, 120, 0),
    (0, 0, 0),
    (1250, 800, 0.4999),
    (990, 200, 0.338),
    (400, 30, 0.51),
])
def test_determine_soil_cover_index(above_ground_biomass, residue, snow_water):
    # expect = None
    if snow_water > 0.5:
        expect = 0.5
    else:
        expect = exp((-0.00005) * (above_ground_biomass + residue))
    observe = Evapotranspiration._determine_soil_cover_index(above_ground_biomass, residue, snow_water)
    assert expect == observe


@pytest.mark.parametrize("above_ground_biomass,residue,snow_water,potential_evapotrans_adj, transpiration", [
    (800, 40, 0.3, 1.6, 0.9),  # arbitrary
    (1200, 300, 0.433, 2.4, 1.8),  # arbitrary
    (0, 800, 0.03, 0, 3.6),  # after harvest
    (800, 56, 0.84, 0.44, 0.23),  # snowy
    (0, 0, 0.22, 0.69, 0.45),  # empty field
    (400, 150, 0, 0.01, 0),  # dry conditions
    (500, 200, 0, 6.3, 4.5),  # wet conditions
])
def test_determine_soil_evaporation(above_ground_biomass, residue, snow_water, potential_evapotrans_adj, transpiration):
    soil_cover_index = Evapotranspiration._determine_soil_cover_index(above_ground_biomass, residue, snow_water)
    soil_evaporation = potential_evapotrans_adj * soil_cover_index
    reduced_soil_evaporation = (soil_evaporation * potential_evapotrans_adj) / (soil_evaporation + transpiration)
    actual_soil_evaporation = min(soil_evaporation, reduced_soil_evaporation)
    observe = Evapotranspiration._determine_soil_evaporation_adjusted(above_ground_biomass, residue, snow_water,
                                                                      potential_evapotrans_adj, transpiration)
    assert actual_soil_evaporation == observe
    # Check that _determine_soil_cover_index() is being called once
    # @TODO: write this mock test as a patch so that it can run independent of order, same as above
    Evapotranspiration._determine_soil_cover_index = MagicMock(return_value=2.1)
    throwaway = Evapotranspiration._determine_soil_evaporation_adjusted(above_ground_biomass, residue, snow_water,
                                                                        potential_evapotrans_adj, transpiration)
    Evapotranspiration._determine_soil_cover_index.assert_called_once()


@pytest.mark.parametrize("soil_evaporation_adj,snow_water_content", [
    (1.3, 3.2),
    (0, 0),
    (1.3, 0.4),
    (1.8954, 0)
])
def test_determine_maximum_soil_evaporation(soil_evaporation_adj, snow_water_content):
    observe = Evapotranspiration._determine_maximum_soil_evaporation(soil_evaporation_adj, snow_water_content)
    if snow_water_content > soil_evaporation_adj:
        assert 0 == observe
    else:
        assert (soil_evaporation_adj - snow_water_content) == observe


@pytest.mark.parametrize("max_soil_water_evap,layer_data", [
    (1.2, LayerData(top_depth=0, bottom_depth=3)),  # defaults
    (0.9, LayerData(top_depth=4, bottom_depth=9, esco=0.78)),  # default water contents, different esco
    (1.1, LayerData(top_depth=2, bottom_depth=8, soil_water_content=1.8, field_capacity_water_content=1.6,
                    wilting_point_water_content=0.9)),
    (1.5, LayerData(top_depth=4, bottom_depth=12, soil_water_content=1.1, field_capacity_water_content=2,
                    wilting_point_water_content=1)),
    (2.1, LayerData(top_depth=0, bottom_depth=15, soil_water_content=2.3, field_capacity_water_content=2.5,
                    wilting_point_water_content=0.3, esco=0.6)),
])
def test_determine_evaporative_demand(max_soil_water_evap, layer_data):
    observe = Evapotranspiration._determine_evaporative_demand(max_soil_water_evap, layer_data)
    expect_top_demand = max_soil_water_evap * (layer_data.top_depth /
                                               (layer_data.top_depth + exp(2.374 - (0.00713 * layer_data.top_depth))))
    expect_bottom_demand = max_soil_water_evap * (layer_data.bottom_depth /
                                                  (layer_data.bottom_depth +
                                                   exp(2.374 - (0.00713 * layer_data.bottom_depth))))
    assert (expect_bottom_demand - (expect_top_demand * layer_data.esco)) == observe

@pytest.mark.parametrize("max_soil_water_evap, layer_data", [
    (1, LayerData(top_depth=None, bottom_depth=2)),
    (1, LayerData(top_depth=-1.2, bottom_depth=4)),
    (1, LayerData(top_depth=3, bottom_depth=2)),
    (1, LayerData(top_depth=1, bottom_depth=None)),
])
def test_determine_evaporative_demand_error(max_soil_water_evap, layer_data):
    with pytest.raises(Exception):
        Evapotranspiration._determine_evaporative_demand(max_soil_water_evap, layer_data)

# --- helper function tests ---
@pytest.mark.parametrize("initial_canopy_water", [
    0.91,
    0,  # zero
    1.35,
    3.99,  # greater than potential evapotranspiration
])
def test_determine_potential_evapotranspiration_adjusted(initial_canopy_water):
    # initialize object
    data = SoilData(transpiration=0.356)
    assert data.transpiration == 0.356
    incorp = Evapotranspiration(data)

    # set needed data field inside object
    incorp.data.potential_evapotranspiration = 1.4

    # run method
    observe = incorp._determine_potential_evapotranspiration_adjusted(initial_canopy_water)
    if initial_canopy_water > 1.4:
        assert observe == 0
    else:
        assert observe == (1.4 - initial_canopy_water)


# --- integration tests ---
@pytest.mark.parametrize(
    "extraterrestrial_radiation,max_temp,min_temp,avg_temp,above_ground_mass,residue,snow_water,initial_canopy_water",
    [
        (500, 24, 18, 20, 1000, 200, 0.12, 1.01),
        (600.398, 28.33, 12.0119, 20.1134, 856, 120, 0.6, 1.03),  # snowy
        (1100, 20.334, 8.933, 15.808, 789, 103, 0.08, 1.3),
        (300, 10, 0, 3, 0, 0, 0, 0),  # empty field, no snow
    ])
def test_evapotranspirate(extraterrestrial_radiation, max_temp, min_temp, avg_temp, above_ground_mass, residue,
                          snow_water, initial_canopy_water):
    # initialize objects
    data = SoilData(transpiration=0.4325)
    assert data.transpiration == 0.4325
    incorp = Evapotranspiration(data)

    # mock helper functions
    incorp._determine_potential_evapotranspiration = MagicMock(return_value=1.89)
    incorp._determine_potential_evapotranspiration_adjusted = MagicMock(return_value=1.354)
    incorp._determine_soil_evaporation_adjusted = MagicMock(return_value=2.845)
    incorp._determine_maximum_soil_evaporation = MagicMock(return_value=2.195)

    # run method
    incorp.evapotranspirate(extraterrestrial_radiation, max_temp, min_temp, avg_temp, above_ground_mass, residue,
                            snow_water, initial_canopy_water)

    # check results
    incorp._determine_potential_evapotranspiration.assert_called_once()
    incorp._determine_potential_evapotranspiration_adjusted.assert_called_once()
    incorp._determine_soil_evaporation_adjusted.assert_called_once()
    incorp._determine_maximum_soil_evaporation.assert_called_once()
    assert data.potential_evapotranspiration == 1.89
    assert data.potential_evapotranspiration_adjusted == 1.354
    assert data.soil_evaporation_adjusted == 2.845
    assert data.maximum_soil_evaporation == 2.195
