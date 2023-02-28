from unittest.mock import MagicMock

from SC_redesign.Crop_and_Soil.crop.crop import Crop
from SC_redesign.Crop_and_Soil.field.field import Field


# TODO: all methods in field.py need to be added here

def test_grow_crops():
    assert False


def test_harvest_crops():
    assert False


def test_start_dormancy():
    """Tests that each crop's dormancy method is called"""
    # Initialize objects
    crop = Crop()
    field = Field()
    field.crops = [crop]

    # Mock functions used
    crop.dormancy.go_into_dormancy = MagicMock()

    # Run method being tested
    field.start_dormancy()

    # Check that subroutines were called
    assert crop.dormancy.go_into_dormancy.call_count == 1
