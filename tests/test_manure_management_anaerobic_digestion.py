"""
RUFAS: Ruminant Farm Systems Model
File name: test_manure_management_anaerobic_digestion.py
Description: Implements test cases
Author(s): Mike Eaton 
"""
import pytest
from pytest import fixture
from pytest_mock import MockerFixture
from .conftest import *
from tests.test_manure_management import assert_two_lists_equal
from dataclasses import dataclass, fields
from unittest.mock import patch
from RUFAS.routines.manure_management.misc.constants import ManureManagementConstants as Constants

def test_get_moisture_content(get_expected_values_anaerobic_digestion,ad_fixture):
    ad = ad_fixture
    daily_outputs = ad.update()
    mc =ad.get_moisture_content()
    assert pytest.approx(mc,0.01) == get_expected_values_anaerobic_digestion.moisture_content  

def test_pass_handler_data(mock_handler_output,ad_fixture):
    ad = ad_fixture
    daily_outputs = ad.update()
    handler_output = mock_handler_output
    assert(ad.wastewater_volume==handler_output.total_daily_mass)
    assert(ad.total_solids==handler_output.TSd)
    assert(ad.volatile_solids==handler_output.VSd + handler_output.VSnd)

def test_get_minimum_digester_volume(ad_fixture,mock_ad_init_data):
    ad = ad_fixture
    ad.update()
    assert pytest.approx(ad.get_minimum_digester_volume(),0.1) == ad.wastewater_volume*mock_ad_init_data.hydraulic_retention_time

def test_get_top_cover_volume(ad_fixture,mock_ad_init_data):
    ad = ad_fixture
    minimum_digester_volume=ad.get_minimum_digester_volume()
    assert pytest.approx(ad.get_top_cover_volume(minimum_digester_volume),0.1) == minimum_digester_volume*mock_ad_init_data.top_cover_volume_fraction

def test_sav(ad_fixture,mock_ad_init_data):
    ad = ad_fixture
    ad.update()
    assert pytest.approx(ad.get_sav(),0.1) == mock_ad_init_data.SAV_fraction * ad.volatile_solids * mock_ad_init_data.sludge_accumulation_period * \
           365 / 1000

def test_get_effluent_total_solids(ad_fixture,mock_ad_init_data):
    ad = ad_fixture
    ad.update()
    assert pytest.approx(ad.get_effluent_total_solids(),0.1) == (1-mock_ad_init_data.VS_removal_efficiency) * ad.total_solids

def test_get_effluent_volatile_solids(ad_fixture,mock_ad_init_data):
    ad = ad_fixture
    ad.update()
    assert pytest.approx(ad.get_effluent_volatile_solids(),0.1) == (1-mock_ad_init_data.VS_removal_efficiency) * ad.volatile_solids

def test_get_evaporated_water(ad_fixture,mock_ad_init_data):
    ad = ad_fixture
    ad.update()
    assert pytest.approx(ad.get_evaporated_water(),0.1) == mock_ad_init_data.evaporation_fraction * ad.wastewater_volume  ## m^3/day

def test_get_biogas_generation(ad_fixture,mock_ad_init_data):
    ad = ad_fixture
    ad.update()
    assert pytest.approx(ad.get_biogas_generation(),0.1) == mock_ad_init_data.biogas_gen_ratio * ad.volatile_solids

def test_get_methane_generation_volume(ad_fixture,mock_ad_init_data):
    ad = ad_fixture
    ad.update()
    biogas_generation = ad.get_biogas_generation()
    assert pytest.approx(ad.get_methane_generation_volume(biogas_generation),0.1) == biogas_generation * mock_ad_init_data.methane_gen_ratio

def test_get_methane_volume_using_chen_equation(ad_fixture,mock_ad_init_data):
    ad = ad_fixture
    ad.update()
    assert pytest.approx(ad.get_methane_volume_using_chen_equation(),0.1) == 240*(1-3.1/(mock_ad_init_data.hydraulic_retention_time*0.637+3.1-1)) * ad.effluent_volatile_solids*Constants.GRAMS_TO_KG

def test_get_energy_content(ad_fixture):
    ad = ad_fixture
    ad.update()
    biogas_generation = ad.get_biogas_generation()
    methane_generation_volume = ad.get_methane_generation_volume(biogas_generation)
    assert pytest.approx(ad.get_energy_content(methane_generation_volume),0.1) == methane_generation_volume * Constants.METHANE_DENSITY * Constants.METHANE_ENERGY_DENSITY


@pytest.mark.parametrize("nutrient_fraction",[
    (0.0)
])
def test_get_nutrient_content(nutrient_fraction,ad_fixture):
    ad = ad_fixture
    daily_output = ad.update()
    test_value = ad.get_nutrient_content(nutrient_fraction,getattr(daily_output,'manure_nitrogen'))
    expected_value = 0.0
    assert pytest.approx(test_value,0.1) == expected_value


@pytest.mark.parametrize("T_avg,expected",[
    (0,4),
    (15,15),
])
def test_bound_influent_temperature(T_avg,expected,ad_fixture):
    ad = ad_fixture
    assert pytest.approx(ad.bound_influent_temperature(T_avg),0.1) == expected  

@pytest.mark.parametrize("T_avg,moisture_content,expected",[
    (0,0,0.68298),
    (25,0,1.32451),
    (0,1,1.98898),
    (25,0.8,2.36931)
])
def test_calcHeatCapacityManure(T_avg,moisture_content,expected,ad_fixture):
    ad = ad_fixture
    assert pytest.approx(ad.calc_heat_capacity_manure(T_avg, moisture_content), 0.1) == expected

# @pytest.mark.xfail
def test_ad_update(ad_fixture,get_expected_values_anaerobic_digestion):
    ad = ad_fixture
    daily_output = ad.update()
    assert pytest.approx(getattr(get_expected_values_anaerobic_digestion,'TSd'),0.1)==getattr(daily_output,'TSd')
    assert pytest.approx(getattr(get_expected_values_anaerobic_digestion,'VSd'),0.1)==getattr(daily_output,'VSd')
    assert pytest.approx(getattr(get_expected_values_anaerobic_digestion,'VSnd'),0.1)==getattr(daily_output,'VSnd')
    assert pytest.approx(getattr(get_expected_values_anaerobic_digestion,'VS_total'),0.1)==getattr(daily_output,'VS_total')
    assert getattr(get_expected_values_anaerobic_digestion,'p_excrt_manure')==getattr(daily_output,'p_excrt_manure')
    assert getattr(get_expected_values_anaerobic_digestion,'K_manure')==getattr(daily_output,'K_manure')
    assert getattr(get_expected_values_anaerobic_digestion,'manure_nitrogen')==getattr(daily_output,'manure_nitrogen')
    assert getattr(get_expected_values_anaerobic_digestion,'total_daily_mass')==getattr(daily_output,'total_daily_mass')
    # assert getattr(get_expected_values_update,'final_volume')==getattr(daily_output,'final_volume')


# @pytest.mark.xfail
def test_AL_update(al_fixture,get_expected_values_anaerobic_lagoon):
    al = al_fixture
    daily_output = al.update()
    assert pytest.approx(getattr(get_expected_values_anaerobic_lagoon,'TSd'),0.1)==getattr(daily_output,'TSd')
    assert pytest.approx(getattr(get_expected_values_anaerobic_lagoon,'VS_total'),0.1)==getattr(daily_output,'VS_total')
    assert getattr(get_expected_values_anaerobic_lagoon,'p_excrt_manure')==getattr(daily_output,'p_excrt_manure')
    assert getattr(get_expected_values_anaerobic_lagoon,'K_manure')==getattr(daily_output,'K_manure')
    assert getattr(get_expected_values_anaerobic_lagoon,'manure_nitrogen')==getattr(daily_output,'manure_nitrogen')
    assert getattr(get_expected_values_anaerobic_lagoon,'total_daily_mass')==getattr(daily_output,'total_daily_mass')
    # assert getattr(get_expected_values_update,'final_volume')==getattr(daily_output,'final_volume')

def test_AL_sizing(al_fixture,get_expected_values_anaerobic_lagoon):
    al = al_fixture
    daily_output = al.update()
    abc = al.calc_abc()

    #assert pytest.approx(getattr(get_expected_values_anaerobic_lagoon,'volume_needed'),0.1)==al.volume_needed
    assert pytest.approx(getattr(get_expected_values_anaerobic_lagoon,'flushing_recycled'),0.1)==al.flushing_recycled
    assert pytest.approx(getattr(get_expected_values_anaerobic_lagoon,'reduced_volume'),0.1)==al.reduced_volume
    assert pytest.approx(getattr(get_expected_values_anaerobic_lagoon,'minimum_treatment_volume'),0.01)==al.minimum_treatment_volume
    assert pytest.approx(getattr(get_expected_values_anaerobic_lagoon,'sludge_accumulation_volume'),0.01)==al.sludge_accumulation_volume
    assert pytest.approx(getattr(get_expected_values_anaerobic_lagoon,'a'),0.1)==abc[0]
    assert pytest.approx(getattr(get_expected_values_anaerobic_lagoon,'b'),0.1)==abc[1]
    assert pytest.approx(getattr(get_expected_values_anaerobic_lagoon,'c'),0.1)==abc[2]
    assert pytest.approx(getattr(get_expected_values_anaerobic_lagoon,'lagoon_width'),0.1)==al.lagoon_width
    assert pytest.approx(getattr(get_expected_values_anaerobic_lagoon,'lagoon_length'),0.1)==al.lagoon_width*3
    assert pytest.approx(getattr(get_expected_values_anaerobic_lagoon,'lagoon_surface_area'),0.1)==al.lagoon_surface_area
    assert pytest.approx(getattr(get_expected_values_anaerobic_lagoon,'total_lagoon_volume'),0.1)==al.total_lagoon_volume



# @pytest.mark.xfail
def test_SSUF_update(ssuf_fixture,get_expected_values_ssuf):
    ssuf = ssuf_fixture
    daily_output = ssuf.update()
    assert pytest.approx(getattr(get_expected_values_ssuf,'TSd'),0.1)==getattr(daily_output,'TSd')
    assert pytest.approx(getattr(get_expected_values_ssuf,'VS_total'),0.1)==getattr(daily_output,'VS_total')
    assert getattr(get_expected_values_ssuf,'p_excrt_manure')==getattr(daily_output,'p_excrt_manure')
    assert getattr(get_expected_values_ssuf,'K_manure')==getattr(daily_output,'K_manure')
    assert getattr(get_expected_values_ssuf,'manure_nitrogen')==getattr(daily_output,'manure_nitrogen')
    assert getattr(get_expected_values_ssuf,'total_daily_mass')==getattr(daily_output,'total_daily_mass')
    # assert getattr(get_expected_values_update,'final_volume')==getattr(daily_output,'final_volume')


# def test_SSUF_sizing(ssuf_fixture,get_expected_values_ssuf):
#     ssuf = ssuf_fixture
#     daily_output = ssuf.update()
#     abc = ssuf.calc_abc()

#     #assert pytest.approx(getattr(get_expected_values_anaerobic_lagoon,'volume_needed'),0.1)==al.volume_needed
#     assert pytest.approx(getattr(get_expected_values_ssuf,'minimum_treatment_volume'),0.01)==ssuf.minimum_treatment_volume
#     assert pytest.approx(getattr(get_expected_values_ssuf,'sludge_accumulation_volume'),0.01)==ssuf.sludge_accumulation_volume
#     assert pytest.approx(getattr(get_expected_values_ssuf,'a'),0.1)==abc[0]
#     assert pytest.approx(getattr(get_expected_values_ssuf,'b'),0.1)==abc[1]
#     assert pytest.approx(getattr(get_expected_values_ssuf,'c'),0.1)==abc[2]
#     assert pytest.approx(getattr(get_expected_values_ssuf,'lagoon_width'),0.1)==ssuf.lagoon_width
#     assert pytest.approx(getattr(get_expected_values_ssuf,'lagoon_length'),0.1)==ssuf.lagoon_width*3
#     assert pytest.approx(getattr(get_expected_values_ssuf,'lagoon_surface_area'),0.1)==ssuf.lagoon_surface_area
#     assert pytest.approx(getattr(get_expected_values_ssuf,'total_lagoon_volume'),0.1)==ssuf.total_lagoon_volume

