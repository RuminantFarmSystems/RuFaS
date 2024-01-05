from typing import Dict
import pytest
from RUFAS.routines.feed_storage.feed_manager import FeedManager, StorageType
from RUFAS.routines.feed_storage.harvested_crop import HarvestedCrop
from RUFAS.routines.feed_storage.enums import CropCategory, CropType

from .sample_crop_data import sample_crop_data  # noqa F401


@pytest.fixture
def harvested_crop(sample_crop_data: Dict[str, float]) -> HarvestedCrop:  # noqa F811
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


def test_receive_crop_multiple(
    feed_manager: FeedManager, harvested_crop: HarvestedCrop
):
    try:
        feed_manager.receive_crop(
            harvested_crop=harvested_crop,
            storage_type=StorageType.DRY,
        )
        feed_manager.receive_crop(
            harvested_crop=harvested_crop,
            storage_type=StorageType.DRY,
        )
        feed_manager.receive_crop(
            harvested_crop=harvested_crop,
            storage_type=StorageType.BUNKER,
        )
        assert StorageType.DRY in feed_manager.active_storages.keys()
        assert StorageType.BUNKER in feed_manager.active_storages.keys()
        assert len(feed_manager.active_storages[StorageType.BUNKER].stored) == 1
        len(feed_manager.active_storages[StorageType.DRY].stored) == 2
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


def test_query_with_specific_crops(
    feed_manager: FeedManager, sample_crop_data: Dict[str, float]  # noqa F811
):
    feed_manager.receive_crop(
        harvested_crop=HarvestedCrop(
            category=CropCategory.ALFALFA, type=CropType.ALFALFA, **sample_crop_data
        ),
        storage_type=StorageType.PROTECTED_INDOORS,
    )
    feed_manager.receive_crop(
        harvested_crop=HarvestedCrop(
            category=CropCategory.ALFALFA, type=CropType.ALFALFA, **sample_crop_data
        ),
        storage_type=StorageType.PILE,
    )
    feed_manager.receive_crop(
        harvested_crop=HarvestedCrop(
            category=CropCategory.CORN, type=CropType.WHOLE_PLANT, **sample_crop_data
        ),
        storage_type=StorageType.BUNKER,
    )
    queryable_crops = [CropType.ALFALFA]
    result = feed_manager.query_available_feeds(queryable_crops)
    assert result == {CropType.ALFALFA: 200.0}