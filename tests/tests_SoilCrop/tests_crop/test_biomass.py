"""
RUFAS: Ruminant Farm Systems Model
File name: test_biomass.py
Description: Implements test cases
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

from RUFAS.routines.field.crop.crop_types import base_crop
from RUFAS.routines.field.soil import soil
from RUFAS.classes import Weather, Time
from RUFAS import *
from RUFAS.routines.field.crop.biomass import *

from unittest.mock import MagicMock
import pytest

from math import gamma


def mock_crop(fr_root=.38, biomass_actual=4.6, kl=2.1, LAI_actual=3.4, RUE=1.5, gamma_reg=.7):
    """
    Description: 
        Creates a BaseCrop class mocking object for use as input for functions. It is initialized with the
        arguments provided; arguments are dynamic and can be changed/added to as needed.

    Args:
        fr_root (float): BaseCrop fr_root attribute
        biomass_actual (float): BaseCrop biomass_actual attribute
        kl (float): BaseCrop kl attribute
        LAI_actual (float): BaseCrop LAI_actual attribute
        RUE (float): BaseCrop RUE attribute
        gamma_reg (float): BaseCrop gamma_reg attribute

    Return:
        a BaseCrop mocking object instantiated with the provided arguments 
    """

    mcrop = MagicMock(base_crop.BaseCrop)

    mcrop.fr_root = fr_root
    mcrop.biomass_actual = biomass_actual
    mcrop.kl = kl
    mcrop.LAI_actual = LAI_actual
    mcrop.RUE = RUE
    mcrop.gamma_reg = gamma_reg

    return mcrop


def mock_weather(radiation = [[3.5]]):
    """
    Description: 
        Creates a Weather class mocking object for use as input for functions. It is initialized with the
        arguments provided; arguments are dynamic and can be changed/added to as needed.

    Args:
        radiation (float): Weather attribute, measured amount of radiation

    Return:
        a Time mocking object instantiated with the provided arguments 
    """
    mweather = MagicMock(Weather)

    mweather.radiation = radiation
    
    return mweather



def mock_time(day = 1, year = 1):
    """
    Description: 
        Creates a Time class mocking object for use as input for functions. It is initialized with the
        arguments provided; arguments are dynamic and can be changed/added to as needed.

    Args:
        year (int): Time attribute, current year in simulation
        day (int): Time attribute, current day in the simulation

    Return:
        a Time mocking object instantiated with the provided arguments 
    """
    mtime = MagicMock(Time)

    mtime.year = year
    mtime.day = day

    return mtime


def mock_soil(ET_max_annual=1.5, evap_annual=2.1, trans_annual=1.3):
    """
        Description:
            Creates a Soil class mocking object for use as input for functions. It is initialized with the
            arguments provided; arguments are dynamic and can be changed/added to as needed.

        Args:
            ET_max_annual (float): Soil ET_max_annual attribute
            evap_annual (float): Soil evap_annual attribute
            trans_annual (float): Soil trans_annual attribute

        Return:
            A Soil class mocking object instantiated with the provided arguments
    """

    msoil = MagicMock(soil.Soil)

    msoil.ET_max_annual = ET_max_annual
    msoil.evap_annual = evap_annual
    msoil.trans_annual = trans_annual

    return msoil


# the following tests are for the calc_bio_AG() function
def test_calc_bio_AG_sets_bio_AG_correctly():
    """
    Description:
        Unittest for calc_bio_AG() in routines/field/crop/biomass.py. Checks that the
        BaseCrop attribute bio_AG is correctly set
    """

    crop = mock_crop()
    calc_bio_AG(crop)

    assert pytest.approx(crop.bio_AG) == (1 - .38) * 4.6


# the following tests are for the calc_gamma_wu() function
def test_calc_gamma_wu_sets_ET_annual_correctly_ET_max_nonzero():
    """
    Description:
        Unittest for calc_gamma_wu in routines/field/crop/biomass.py. Checks that the
        Soil attribute ET_max_annual is correctly set when it is initially a non-zero value.

    """
    crop = mock_crop()
    soil = mock_soil()
    calc_gamma_wu(soil, crop)

    assert pytest.approx(soil.ET_annual) == 2.1 + 1.3


def test_calc_gamma_wu_sets_gamma_wu_correctly_ET_max_nonzero():
    """
    Description:
        Unittest for calc_gamma_wu in routines/field/crop/biomass.py. Checks that the
        Soil attribute gamma_wu is correctly set when soil.ET_max_annual is initially a non-zero value.

    """

    crop = mock_crop()
    soil = mock_soil()
    calc_gamma_wu(soil, crop)

    assert pytest.approx(crop.gamma_wu) == 100 * ((2.1 + 1.3) / 1.5)


def test_calc_gamma_wu_sets_all_correctly_ET_max_nonzero():
    """
    Description:
        Blanket test to check that all values set in calc_gamma_wu() are set appropriately
        when soil.ET_max_annual is initially a non-zero value.

    """
    crop = mock_crop()
    soil = mock_soil()
    calc_gamma_wu(soil, crop)

    test_list = [
        pytest.approx(soil.ET_annual) == 2.1 + 1.3,
        pytest.approx(crop.gamma_wu) == 100 * ((2.1 + 1.3) / 1.5)
    ]

    assert all(test_list)


def test_calc_gamma_wu_returns_zero_with_ET_max_as_zero():
    """
    Description:
        Unittest for calc_gamma_wu() in routines/field/crop/biomass.py. Checks that
        the function returns 0 if the Soil attribute ET_max_annual is initially set to zero.
    """
    crop = mock_crop()
    soil = mock_soil(ET_max_annual=0.0)

    assert pytest.approx(calc_gamma_wu(soil, crop)) == 0


#calc_intercepted_radiation()
def test_calc_intercepted_radiation_correctly_calculates_active_radiation():
    """
    Description:
        Unittest for calc_intercepted_radiation() in routines/field/crop/biomass.py. Checks
        that the function calculates and returns the correct value for intercepted radiation
        on the provided day and year of the simulation
    """
    crop = mock_crop()
    weather = mock_weather()
    time = mock_time()

    assert pytest.approx(calc_intercepted_radiation(crop,weather,time)) \
                     == 0.5 * 3.5 * (1 - exp(-1 * 2.1 * 3.4))

#calc_act_biomass()...assumes dependencies work properly
def test_calc_act_biomass_correctly_calculates_d_biomass_max():
    """
    Description:
        Unittest for calc_act_biomass in routines/field/crop/biomass.py. Checks
        that the function correctly updates the BaseCrop attribute d_biomass_max.
    """
    crop = mock_crop()
    weather = mock_weather()
    time = mock_time()

    H_phosyn = calc_intercepted_radiation(crop,weather,time)

    calc_act_biomass(crop,weather,time)

    assert pytest.approx(crop.d_biomass_max) == 1.5 * H_phosyn

def test_calc_act_biomass_correctly_calculates_d_biomass_actual():
    """
    Description:
        Unittest for calc_act_biomass in routines/field/crop/biomass.py. Checks
        that the function correctly updates the BaseCrop attribute d_biomass_actual.
    """
    crop = mock_crop()
    weather = mock_weather()
    time = mock_time()

    H_phosyn = calc_intercepted_radiation(crop,weather,time)

    calc_act_biomass(crop,weather,time)

    assert pytest.approx(crop.d_biomass_actual) == (1.5 * H_phosyn) * .7

def test_calc_act_biomass_correctly_calculates_prev_biomass_actual():
    """
    Description:
        Unittest for calc_act_biomass in routines/field/crop/biomass.py. Checks
        that the function correctly updates the BaseCrop attribute pre_biomass_actual.
    """
    crop = mock_crop()
    weather = mock_weather()
    time = mock_time()

    calc_act_biomass(crop,weather,time)

    assert pytest.approx(crop.prev_biomass_actual) == 4.6

def test_calc_biomass_correctly_calculates_biomass_actual():
    """
    Description:
        Unittest for calc_act_biomass in routines/field/crop/biomass.py. Checks
        that the function correctly updates the BaseCrop attribute biomass_actual.
    """
    crop = mock_crop()
    weather = mock_weather()
    time = mock_time()

    H_phosyn = calc_intercepted_radiation(crop,weather,time)

    calc_act_biomass(crop,weather,time)

    assert pytest.approx(crop.biomass_actual) == 4.6 + (1.5 * H_phosyn) * .7



