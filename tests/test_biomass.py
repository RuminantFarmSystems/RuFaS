"""
RUFAS: Ruminant Farm Systems Model
File name: test_biomass.py
Description: Implements test cases
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""


from math import gamma
from RUFAS.routines.field.crop.crop_types import base_crop
from RUFAS.routines.field.soil import soil
from RUFAS import *
from RUFAS.routines.field.crop.biomass import * 
from unittest.mock import MagicMock
import pytest

def mock_crop(fr_root = .38,biomass_actual = 4.6,kl = 2.1, LAI_actual = 3.4, RUE = 1.5, gamma_reg = .7):
    
    mcrop = MagicMock(base_crop.BaseCrop)
    mcrop.fr_root = fr_root
    mcrop.biomass_actual = biomass_actual
    mcrop.kl = kl
    mcrop.LAI_actual = LAI_actual
    mcrop.RUE = RUE
    mcrop.gamma_reg = gamma_reg

    return mcrop

def mock_weather():
    pass
def mock_time():
    pass
def mock_soil(ET_max_annual = 1.5,evap_annual = 2.1, trans_annual = 1.3):

    msoil = MagicMock(soil.Soil)
    msoil.ET_max_annual = ET_max_annual
    msoil.evap_annual = evap_annual
    msoil.trans_annual = trans_annual

    return msoil


#the following tests are for the calc_bio_AG() function
def test_calc_bio_AG_sets_bio_AG_correctly():
    crop = mock_crop()
    calc_bio_AG(crop)

    assert pytest.approx(crop.bio_AG) == (1 - .38) * 4.6

#the following tests are for the calc_gamma_wu() function
#case 1 is with soil.ET_max_annual being non-zero, case 2 is it is zero
def test_calc_gamma_wu_sets_ET_annual_correctly_ET_max_nonzero():
    crop = mock_crop()
    soil = mock_soil()
    calc_gamma_wu(soil,crop)

    assert pytest.approx(soil.ET_annual) == 2.1 + 1.3

def test_calc_gamma_wu_sets_gamma_wu_correctly_ET_max_nonzero():
    crop = mock_crop()
    soil = mock_soil()
    calc_gamma_wu(soil,crop)

    assert pytest.approx(crop.gamma_wu) == 100 * ((2.1 + 1.3) / 1.5)


def test_calc_gamma_wu_sets_all_correctly_ET_max_nonzero():
    crop = mock_crop()
    soil = mock_soil()
    calc_gamma_wu(soil,crop)

    test_list = [
        pytest.approx(soil.ET_annual) == 2.1 + 1.3,
        pytest.approx(crop.gamma_wu) == 100 * ((2.1 + 1.3) / 1.5)
    ]

    assert all(test_list)

def test_calc_gamma_wu_returns_zero_with_ET_max_as_zero():
    crop = mock_crop()
    soil = mock_soil(ET_max_annual=0.0)
    assert pytest.approx(calc_gamma_wu(soil,crop)) == 0









