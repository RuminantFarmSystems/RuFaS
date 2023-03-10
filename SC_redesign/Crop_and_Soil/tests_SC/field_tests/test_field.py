import warnings
from unittest.mock import MagicMock

import pytest

from SC_redesign.Crop_and_Soil.crop.crop import Crop
from SC_redesign.Crop_and_Soil.field.field import Field


# TODO: all methods in field.py need to be added here

# def test_grow_crops():
#     assert False
#
#
# def test_harvest_crops():
#     assert False


# TODO: make this test more rigorous once a testing pattern has been established for testing Field
@pytest.mark.parametrize("daylength,threshold_daylength", [
    (14, 8),
    (17.20948239, 9.19183294),
    (7.293485893, 8.234850920),
])
def test_start_dormancy(daylength: float, threshold_daylength: float) -> None:
    """Tests that each crop's dormancy method is called"""
    # Initialize objects
    crop = Crop()
    field = Field()
    field.field_data.dormancy_threshold_daylength = threshold_daylength
    field.crops = [crop]

    # Mock functions used
    crop.dormancy.enter_dormancy = MagicMock()

    # Run method being tested
    field.assess_dormancy(daylength)

    # Check that subroutines were called correct number of times
    if daylength <= threshold_daylength:
        assert crop.dormancy.enter_dormancy.call_count == 1


def test_plant_crops():
    assert False


def test_make_crop_from_config_dict():
    assert False


def test_make_supported_crop():
    assert False


def test_make_custom_crop():
    assert False


def test_add_crop():
    assert False

def test_reset_perennial():
    warnings.warn("no method to reset perennials implemented")
