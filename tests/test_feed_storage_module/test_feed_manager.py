from typing import Dict
import pytest
from RUFAS.routines.feed_storage.feed_manager import FeedManager, StorageType
from RUFAS.routines.feed_storage.harvested_crop import HarvestedCrop
from RUFAS.routines.feed_storage.enums import CropCategory, CropType
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
def harvested_crop(sample_crop_data: Dict[str, float]) -> HarvestedCrop:
    """
    Pytest fixture to create a HarvestedCrop instance for testing.

    Returns
    -------
    HarvestedCrop
        An instance of the HarvestedCrop class.
    """
    category = CropCategory.CORN
    crop_type = CropType.WHOLE_PLANT
    return HarvestedCrop(category=category, type=crop_type, **sample_crop_data)


@pytest.fixture
def feed_manager():
    return FeedManager()


def test_receive_crop_success(feed_manager: FeedManager, harvested_crop: HarvestedCrop):
    try:
        feed_manager.receive_crop(
            harvested_crop=harvested_crop,
            storage_type=StorageType.DRY,
        )
    except ValueError:
        pytest.fail("Unexpected ValueError raised")


def test_receive_crop_error(feed_manager: FeedManager, harvested_crop: HarvestedCrop):
    incompatible_storage = StorageType.PROTECTED_WRAPPED
    with pytest.raises(ValueError) as excinfo:
        feed_manager.receive_crop(
            harvested_crop=harvested_crop,
            storage_type=incompatible_storage,
        )
    assert "is not compatible with storage type" in str(excinfo.value)
