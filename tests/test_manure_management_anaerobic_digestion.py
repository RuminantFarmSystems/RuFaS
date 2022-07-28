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
from RUFAS.routines.manure_management.treatments.treatment_classes import AnaerobicDigestion
from RUFAS.routines.manure_management.misc.constants import ManureManagementConstants as Constants
# default_values = default_input_values()
# default_expected=expected_values()
import unittest

def test_get_moisture_content(get_expected_values,ad_fixture):
    ad = ad_fixture
    daily_outputs = ad.update()
    mc =ad.get_moisture_content()
    assert pytest.approx(mc,0.01) == get_expected_values.moisture_content  

def test_pass_handler_data(mock_handler_output,ad_fixture):
    ad = ad_fixture
    daily_outputs = ad.update()
    handler_output = mock_handler_output
    assert(ad.wastewater_volume==handler_output.total_daily_mass)
    assert(ad.total_solids==handler_output.TSd)
    assert(ad.volatile_solids==handler_output.VSd + handler_output.VSnd)


def test_get_minimum_digester_volume(get_expected_values,ad_fixture,mock_init_data):
    ad = ad_fixture
    ad.update()
    expected = get_expected_values
    assert pytest.approx(ad.get_minimum_digester_volume(),0.1) == ad.wastewater_volume*mock_init_data.hydraulic_retention_time

def test_get_top_cover_volume(get_expected_values,ad_fixture,mock_init_data):
    ad = ad_fixture
    minimum_digester_volume=ad.get_minimum_digester_volume()
    expected = get_expected_values
    assert pytest.approx(ad.get_top_cover_volume(minimum_digester_volume),0.1) == minimum_digester_volume*mock_init_data.TOP_COVER_VOLUME_FRACTION  

def test_sav(get_expected_values,ad_fixture,mock_init_data):
    ad = ad_fixture
    ad.update()
    expected = get_expected_values
    assert pytest.approx(ad.get_sav(),0.1) == mock_init_data.SAV_FRACTION*ad.volatile_solids*mock_init_data.sludge_accumulation_period* \
            365/1000

def test_get_effluent_total_solids(get_expected_values,ad_fixture,mock_init_data):
    ad = ad_fixture
    ad.update()
    expected = get_expected_values
    assert pytest.approx(ad.get_effluent_total_solids(),0.1) == (1-mock_init_data.TS_FRACTION) * ad.total_solids

def test_get_effluent_volatile_solids(get_expected_values,ad_fixture,mock_init_data):
    ad = ad_fixture
    ad.update()
    expected = get_expected_values
    assert pytest.approx(ad.get_effluent_volatile_solids(),0.1) == (1-mock_init_data.VS_FRACTION) * ad.volatile_solids


def test_get_evaporated_water(get_expected_values,ad_fixture,mock_init_data):
    ad = ad_fixture
    ad.update()
    expected = get_expected_values
    assert pytest.approx(ad.get_evaporated_water(),0.1) == mock_init_data.EVAPORATION_FRACTION * ad.wastewater_volume  ## m^3/day

def test_get_biogas_generation(get_expected_values,ad_fixture,mock_init_data):
    ad = ad_fixture
    ad.update()
    expected = get_expected_values
    assert pytest.approx(ad.get_biogas_generation(),0.1) == mock_init_data.BIOGAS_GEN_RATIO * ad.volatile_solids

def test_get_methane_generation_volume(get_expected_values,ad_fixture,mock_init_data):
    ad = ad_fixture
    ad.update()
    biogas_generation = ad.get_biogas_generation()
    expected = get_expected_values
    assert pytest.approx(ad.get_methane_generation_volume(biogas_generation),0.1) == biogas_generation * mock_init_data.METHANE_GEN_RATIO

def test_get_methane_volume_using_chen_equation(ad_fixture,mock_init_data):
    ad = ad_fixture
    ad.update()
    assert pytest.approx(ad.get_methane_volume_using_chen_equation(),0.1) == 240*(1-3.1/(mock_init_data.hydraulic_retention_time*0.637+3.1-1)) * ad.effluent_volatile_solids*Constants.GRAMS_TO_KG


def test_get_energy_content(get_expected_values,ad_fixture):
    ad = ad_fixture
    ad.update()
    biogas_generation = ad.get_biogas_generation()
    methane_generation_volume = ad.get_methane_generation_volume(biogas_generation)
    expected = get_expected_values
    assert pytest.approx(ad.get_energy_content(methane_generation_volume),0.1) == methane_generation_volume * Constants.METHANE_DENSITY * Constants.METHANE_ENERGY_DENSITY


@pytest.mark.parametrize("nutrient_fraction",[
    (0.01),
    (0.0)
])
def test_get_nutrient_content(nutrient_fraction,ad_fixture_simple):
    ad = ad_fixture_simple
    ad.update()

    assert pytest.approx(ad.get_nutrient_content(nutrient_fraction,10),0.1) == (1 - nutrient_fraction * (
                100 / ad.total_solids))


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
    assert pytest.approx(ad.calcHeatCapacityManure(T_avg,moisture_content),0.1) == expected  

@pytest.mark.xfail
def test_update(ad_fixture,get_expected_values_update):
    ad = ad_fixture
    daily_output = ad.update()
    assert getattr(get_expected_values_update,'TSd')==getattr(daily_output,'TSd')


