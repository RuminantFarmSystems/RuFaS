from typing import Dict
import pytest
from RUFAS.routines.feed_storage.storage import Storage
from RUFAS.routines.feed_storage.harvested_crop import (
    HarvestedCrop,
    CropCategory,
    CropType,
)
from RUFAS.time import Time
from RUFAS.config import Config


@pytest.fixture
def sample_crop_data() -> Dict[str, float]:
    return {
        "harvest_time": Time(
            Config(
                {
                    "start_date": "1:1",
                    "end_date": "1:10",
                    "set_seed": False,
                    "random_seed": 42,
                }
            )
        ),
        "storage_time": Time(
            Config(
                {
                    "start_date": "1:1",
                    "end_date": "1:10",
                    "set_seed": False,
                    "random_seed": 42,
                }
            )
        ),
        "fresh_mass": 100.0,
        "dry_matter_percentage": 50.0,
        "dry_matter_digestibility": 70.0,
        "crude_protein_percent": 10.0,
        "non_protein_nitrogen": 5.0,
        "starch": 30.0,
        "adf": 7.0,
        "ndf": 15.0,
        "lignin": 3.0,
        "sugar": 20.0,
        "ash": 6.0,
    }


@pytest.fixture
def storage() -> Storage:
    """
    Pytest fixture to create a Storage instance for testing.

    Returns
    -------
    Storage
        An instance of the Storage class.
    """
    return Storage()


@pytest.fixture
def harvested_crop(sample_crop_data: Dict[str, float]) -> HarvestedCrop:
    """
    Pytest fixture to create a HarvestedCrop instance for testing.

    Returns
    -------
    HarvestedCrop
        An instance of the HarvestedCrop class.
    """
    category = CropCategory.SMALL_GRAIN
    crop_type = CropType.WHEAT
    return HarvestedCrop(category=category, type=crop_type, **sample_crop_data)


def test_receive_crop(storage: Storage, harvested_crop: HarvestedCrop):
    """
    Test the receive_crop method of the Storage class.
    """
    pass


def test_process_degradations(storage: Storage):
    """
    Test the process_degradations method of the Storage class.
    """
    pass


def test_give_feed(storage: Storage):
    """
    Test the give_feed method of the Storage class.
    """
    pass


def test_calculate_dry_matter_loss_to_gas(storage: Storage):
    """
    Test the calculate_dry_matter_loss_to_gas method of the Storage class.
    """
    pass


def test_calculate_dry_matter_loss_to_effluent(storage: Storage):
    """
    Test the calculate_dry_matter_loss_to_effluent method of the Storage class.
    """
    pass


def test_calculate_protein_degradation(storage: Storage):
    """
    Test the calculate_protein_degradation method of the Storage class.
    """
    pass


def test_calculate_heat_generated(storage: Storage):
    """
    Test the calculate_heat_generated method of the Storage class.
    """
    pass

