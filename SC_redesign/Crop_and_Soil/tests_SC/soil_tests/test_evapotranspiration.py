import pytest

from SC_redesign.Crop_and_Soil.soil.evapotranspiration import *


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
        expect = (0.0023 * extraterrestrial_radiation * ((max_temp - min_temp) ** (-0.5)) * (avg_temp + 17.8)) / \
                 latent_heat
    else:
        latent_heat = Evapotranspiration._determine_latent_heat_vaporization((max_temp + min_temp) / 2)
        expect = (0.0023 * extraterrestrial_radiation * ((max_temp - min_temp) ** (-0.5)) * (((max_temp + min_temp) / 2)
                                                                                             + 17.8)) / latent_heat
    assert observe == expect


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
    observe = Evapotranspiration._determine_soil_evaporation(above_ground_biomass, residue, snow_water,
                                                             potential_evapotrans_adj, transpiration)
    assert actual_soil_evaporation == observe


@pytest.mark.parametrize("above_ground_biomass,residue,snow_water", [
    (400, 65, 0.3),
    (800, 120, 0),
    (0, 0, 0),
    (1250, 800, 0.4999),
    (990, 200, 0.338),
    (400, 30, 0.51),
])
def test_determine_soil_cover_index(above_ground_biomass, residue, snow_water):
    expect = None
    if snow_water > 0.5:
        expect = 0.5
    else:
        expect = exp((-0.00005) * (above_ground_biomass + residue))
    observe = Evapotranspiration._determine_soil_cover_index(above_ground_biomass, residue, snow_water)
    assert expect == observe
