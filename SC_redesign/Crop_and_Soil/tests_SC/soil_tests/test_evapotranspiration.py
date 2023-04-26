from SC_redesign.Crop_and_Soil.soil.evapotranspiration import Evapotranspiration
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData
from math import exp
from mock import MagicMock, patch
import pytest


# --- static function tests ---
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
        expect = (0.0023 * extraterrestrial_radiation * ((max_temp - min_temp) ** (-0.5)) *
                  (avg_temp + 17.8)) / latent_heat
    else:
        latent_heat = Evapotranspiration._determine_latent_heat_vaporization((max_temp + min_temp) / 2)
        expect = (0.0023 * extraterrestrial_radiation * ((max_temp - min_temp) ** (-0.5)) *
                  (((max_temp + min_temp) / 2) + 17.8)) / latent_heat
    assert observe == expect

    # check that _determine_potential_evapotranspiration() actually calls _determine_latent_heat_vaporization once
    # potential_evapotranspiration
    with patch(
            "SC_redesign.Crop_and_Soil.soil.evapotranspiration.Evapotranspiration._determine_latent_heat_vaporization",
            new=MagicMock(return_value=1.3)):
        Evapotranspiration._determine_potential_evapotranspiration(extraterrestrial_radiation, max_temp,
                                                                   min_temp, avg_temp)
        Evapotranspiration._determine_latent_heat_vaporization.assert_called_once()


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
    with patch("SC_redesign.Crop_and_Soil.soil.evapotranspiration.Evapotranspiration._determine_soil_cover_index",
               new=MagicMock(return_value=2.1)):
        Evapotranspiration._determine_soil_evaporation_adjusted(above_ground_biomass, residue, snow_water,
                                                                potential_evapotrans_adj, transpiration)
        Evapotranspiration._determine_soil_cover_index.assert_called_once()


@pytest.mark.parametrize("above_ground_biomass,residue,snow_water", [
    (400, 65, 0.3),
    (800, 120, 0),
    (0, 0, 0),
    (1250, 800, 0.4999),
    (990, 200, 0.338),
    (400, 30, 0.51),
])
def test_determine_soil_cover_index(above_ground_biomass, residue, snow_water):
    if snow_water > 0.5:
        expect = 0.5
    else:
        expect = exp((-0.00005) * (above_ground_biomass + residue))
    observe = Evapotranspiration._determine_soil_cover_index(above_ground_biomass, residue, snow_water)
    assert expect == observe


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


@pytest.mark.parametrize("max_soil_water_evap,depth", [
    (1.1, 0),
    (0, 0),
    (2.3, 4),
    (2.7, 6.3),
    (5.3256, 19),
])
def test_determine_depth_evaporative_demand(max_soil_water_evap, depth):
    observe = Evapotranspiration._determine_depth_evaporative_demand(max_soil_water_evap, depth)
    expect = depth / (depth + exp(2.374 - (0.00713 * depth)))
    expect *= max_soil_water_evap
    assert observe == expect


@pytest.mark.parametrize("max_soil_water_evap,top_depth,bottom_depth,compensation", [
    (1.2, 0, 3, 1),  # defaults
    (0.9, 4, 9, 0.78),  # default water contents, different esco
    (1.1, 2, 8, 1.8,),
    (1.5, 4, 12, 1),
    (2.1, 0, 15, 2.3),
])
def test_determine_layer_evaporative_demand(max_soil_water_evap, top_depth, bottom_depth, compensation):
    observe = Evapotranspiration._determine_layer_evaporative_demand(max_soil_water_evap, top_depth, bottom_depth,
                                                                     compensation)
    expect_top_demand = Evapotranspiration._determine_depth_evaporative_demand(max_soil_water_evap, top_depth)
    expect_bottom_demand = Evapotranspiration._determine_depth_evaporative_demand(max_soil_water_evap, bottom_depth)
    assert (expect_bottom_demand - (expect_top_demand * compensation)) == observe


@pytest.mark.parametrize("max_soil_water_evap,top_depth,bottom_depth,compensation", [
    (1, None, 2, 1),
    (1, -1.2, 4, 1),
    (1, 3, 2, 1),
    (1, 1, None, 1),
])
def test_determine_layer_evaporative_demand_error(max_soil_water_evap, top_depth, bottom_depth, compensation):
    with pytest.raises(Exception):
        Evapotranspiration._determine_layer_evaporative_demand(max_soil_water_evap, top_depth, bottom_depth,
                                                               compensation)


@pytest.mark.parametrize("evap_demand,soil_water,field_water,wilting_water", [
    (0.3, 1.3, 1.5, 0.2),
    (0.8, 1.8, 1.6, 0.9),
    (1.4, 1.1, 2, 1),
    (1.1, 2.3, 2.5, 0.3),
])
def test_determine_evaporative_demand_reduced(evap_demand, soil_water, field_water, wilting_water):
    observe = Evapotranspiration._determine_evaporative_demand_reduced(evap_demand, soil_water, field_water,
                                                                       wilting_water)
    if soil_water < field_water:
        expect = evap_demand * exp((2.5 * (soil_water - field_water)) /
                                   (field_water - wilting_water))
    else:
        expect = evap_demand
    assert expect == observe


@pytest.mark.parametrize("reduced_evap_demand,soil_water,wilting_water", [
    (0.2, 1.3, 0.2),
    (0.5, 1.8, 0.9),
    (1.8, 1.1, 1),
    (1.1, 2.3, 0.3),
])
def test_determine_amount_water_removed(reduced_evap_demand, soil_water, wilting_water):
    observe = Evapotranspiration._determine_amount_water_removed(reduced_evap_demand, soil_water, wilting_water)
    expect = min(reduced_evap_demand, 0.8 * (soil_water - wilting_water))
    assert expect == observe


# --- helper function tests ---
@pytest.mark.parametrize("initial_canopy_water", [
    0.91,
    0,  # zero
    1.35,
    3.99,  # greater than potential evapotranspiration
])
def test_determine_potential_evapotranspiration_adjusted(initial_canopy_water):
    # initialize object
    data = SoilData(transpiration=0.356, field_size=1.05)
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
    data = SoilData(field_size=1.33, transpiration=0.4325,
                    soil_layers=[LayerData(top_depth=0, bottom_depth=50, nitrate=0.5, field_size=1.33),
                                 LayerData(top_depth=50, bottom_depth=80, nitrate=1, field_size=1.33),
                                 LayerData(top_depth=80, bottom_depth=200, nitrate=5, field_size=1.33)])
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
    assert data.annual_potential_evapotranspiration_total == 1.89
    assert data.potential_evapotranspiration_adjusted == 1.354
    assert data.annual_adjusted_potential_evapotranspiration_total == 1.354
    assert data.soil_evaporation_adjusted == 2.845
    assert data.annual_adjusted_soil_evaporation_total == 2.845
    assert data.maximum_soil_evaporation == 2.195
    assert data.annual_maximum_soil_evaporation_total == 2.195


@pytest.mark.parametrize("layers", [
    [LayerData(top_depth=0, bottom_depth=40, soil_water_concentration=1.8, field_capacity_water_concentration=1.6,
               wilting_point_water_concentration=0.9, field_size=1.33),
     LayerData(top_depth=40, bottom_depth=120, soil_water_concentration=0.9, field_capacity_water_concentration=1.2,
               wilting_point_water_concentration=0.8, field_size=1.33),
     LayerData(top_depth=120, bottom_depth=200, soil_water_concentration=0.8, field_capacity_water_concentration=0.8,
               wilting_point_water_concentration=0.3, field_size=1.33)],
    [LayerData(top_depth=0, bottom_depth=30, soil_water_concentration=2.8, field_capacity_water_concentration=2.3,
               wilting_point_water_concentration=1.8, field_size=1.33),
     LayerData(top_depth=30, bottom_depth=150, soil_water_concentration=1.9, field_capacity_water_concentration=1.8,
               wilting_point_water_concentration=0.8, field_size=1.33),
     LayerData(top_depth=150, bottom_depth=220, soil_water_concentration=0.8, field_capacity_water_concentration=1,
               wilting_point_water_concentration=0.2, field_size=1.33)],
    [LayerData(top_depth=0, bottom_depth=80, soil_water_concentration=2.3, field_capacity_water_concentration=2.9,
               wilting_point_water_concentration=1.8, field_size=1.33),
     LayerData(top_depth=80, bottom_depth=200, soil_water_concentration=1.4, field_capacity_water_concentration=1.8,
               wilting_point_water_concentration=0.8, field_size=1.33),
     LayerData(top_depth=200, bottom_depth=220, soil_water_concentration=0.8, field_capacity_water_concentration=1,
               wilting_point_water_concentration=0.6, field_size=1.33)],
])
def test_evaporate_from_soil(layers):
    # initialize objects
    soildata = SoilData(field_size=1.33, maximum_soil_evaporation=0.3, soil_layers=layers)
    assert soildata.maximum_soil_evaporation == 0.3
    assert soildata.soil_layers == layers
    incorp = Evapotranspiration(soildata)

    # mock helper functions
    incorp._determine_layer_evaporative_demand = MagicMock(return_value=0.8)
    incorp._determine_evaporative_demand_reduced = MagicMock(return_value=0.6)
    incorp._determine_amount_water_removed = MagicMock(return_value=0.5)

    # record expected values
    expect = []
    for layer in layers:
        expect.append(layer.water_content - 0.5)

    # run function
    incorp._evaporate_from_soil()

    # make sure values match
    assert incorp._determine_layer_evaporative_demand.call_count == len(layers)
    assert incorp._determine_evaporative_demand_reduced.call_count == len(layers)
    assert incorp._determine_amount_water_removed.call_count == len(layers)
    for i in range(len(layers)):
        assert expect[i] == incorp.data.soil_layers[i].water_content
