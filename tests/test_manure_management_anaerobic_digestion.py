"""
RUFAS: Ruminant Farm Systems Model
File name: test_manure_management_treatments.py
Description: Implements test cases
Author(s): Mike Eaton 
"""
import pytest
from pytest import fixture
from pytest_mock import MockerFixture
from conftest import *
from tests.test_manure_management import assert_two_lists_equal
from dataclasses import dataclass, fields

@pytest.mark.parametrize("T_avg,expected",[
    (0,4),
    (15,15),
])
def test_bound_effluent_temperature(T_avg,expected):
    ad = anaerobic_digestion0()
    assert pytest.approx(ad.bound_effluent_temperature(T_avg),0.1) == expected  


@pytest.mark.parametrize("T_avg,moisture_content,expected",[
    (0,0,0.68298),
    (25,0,1.32451),
    (0,1,1.98898),
    (25,0.8,2.36931)
])
def test_calcHeatCapacityManure(T_avg,moisture_content,expected):
    ad = anaerobic_digestion0()
    assert pytest.approx(ad.calcHeatCapacityManure(T_avg,moisture_content),0.1) == expected  


##TODO: Calculate expected values for parameterization and replace in this function
@pytest.mark.xfail
@pytest.mark.parametrize("T_avg,moisture_content,expected",[
    (4,0,1),
    (25,80,2),

])
def test_calcSpecificInputEnergy(T_avg,expected):
    ad = anaerobic_digestion0()
    sie = ad.calcSpecificInputEnergy(25,1)
    assert sie == expected

@pytest.mark.xfail
def test_update_inits_to_zero():
    ad = anaerobic_digestion0()
    daily_output = ad.update()
    for field in fields(daily_output):
        assert pytest.approx(0,0.1)== getattr(daily_output,field.name)
    
