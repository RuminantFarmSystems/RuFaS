import pytest
import math

from SC_redesign.Crop_and_Soil.crop.nitrogen_incorporation import *
from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from SC_redesign.Crop_and_Soil.soil.carbon_cycling.decomposition import Decomposition
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData


@pytest.mark.parametrize("temp_average", [
    70,  # lower values
    150,  # higher values
    88.8,  # arbitrary
])
def test_calc_temp_factor(temp_average):
    """ensure that temperature factor was calculated according to the formula in "pseudocode_soil" S.6.A"""
    decomposition_inflection_x = 15.400
    decomposition_inflection_y = 11.750
    max_min_distance = 29.700
    inflection_slope = 0.03
    normalizer = 20.80546
    data = SoilData()
    decomp = Decomposition(data)
    decomp.calc_temp_factor(temp_average)
    assert decomp.calc_temp_factor(temp_average) == max(0.0,
                   (decomposition_inflection_y + (max_min_distance / math.pi) * math.atan(math.pi * inflection_slope * (
                           temp_average - decomposition_inflection_x))) / normalizer)

