import pytest
from pytest_mock import MockerFixture

from RUFAS.data_structures.crop_soil_to_feed_storage_connection import (
    CropCategory,
    CropType,
    HarvestedCrop,
    StorageType,
)
from RUFAS.routines.feed_storage.feed_manager import FeedManager
from RUFAS.routines.feed_storage.grain import Dry
from RUFAS.routines.feed_storage.silage import Pile

from .sample_crop_data import sample_crop_data, sample_crop_data_no_mass


@pytest.fixture
def harvested_crop() -> HarvestedCrop:
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
def alfalfa_crop() -> HarvestedCrop:
    return HarvestedCrop(CropCategory.ALFALFA, CropType.ALFALFA, **sample_crop_data_no_mass, fresh_mass=50)


@pytest.fixture
def corn_crop() -> HarvestedCrop:
    return HarvestedCrop(CropCategory.CORN, CropType.GRAIN, **sample_crop_data_no_mass, fresh_mass=150)


@pytest.fixture
def grass_crop() -> HarvestedCrop:
    return HarvestedCrop(CropCategory.GRASS, CropType.TALL_FESCUE, **sample_crop_data_no_mass, fresh_mass=100)


@pytest.fixture
def feed_manager() -> FeedManager:
    return FeedManager()


def test_receive_crop_success(feed_manager: FeedManager, harvested_crop: HarvestedCrop) -> None:
    try:
        feed_manager.receive_crop(
            harvested_crop=harvested_crop,
            storage_type=StorageType.DRY,
        )
    except ValueError:
        pytest.fail("Unexpected ValueError raised")


def test_receive_crop_multiple(feed_manager: FeedManager, harvested_crop: HarvestedCrop) -> None:
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


def test_receive_crop_error(feed_manager: FeedManager, harvested_crop: HarvestedCrop) -> None:
    incompatible_storage = StorageType.PROTECTED_WRAPPED
    with pytest.raises(ValueError) as excinfo:
        feed_manager.receive_crop(
            harvested_crop=harvested_crop,
            storage_type=incompatible_storage,
        )
    assert "is not compatible with storage type" in str(excinfo.value)


def test_process_degradations(feed_manager: FeedManager, mocker: MockerFixture) -> None:
    """Tests process_degradations in the FeedManager."""
    mock_time = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    dry_storage = mocker.MagicMock(autospec=Dry)
    pile_storage = mocker.MagicMock(autospec=Pile)
    feed_manager.active_storages = {StorageType.DRY: dry_storage, StorageType.PILE: pile_storage}

    feed_manager.process_degradations(mock_weather, mock_time)

    dry_storage.process_degradations.assert_called_once_with(mock_weather, mock_time)
    pile_storage.process_degradations.assert_called_once_with(mock_weather, mock_time)


def test_query_available_feeds_no_parameters(
    feed_manager: FeedManager, alfalfa_crop: HarvestedCrop, corn_crop: HarvestedCrop
) -> None:
    feed_manager.receive_crop(alfalfa_crop, StorageType.PROTECTED_INDOORS)
    feed_manager.receive_crop(corn_crop, StorageType.DRY)
    feed_manager.receive_crop(corn_crop, StorageType.DRY)
    results = feed_manager.query_available_feeds()
    assert len(results) == 2
    assert results[0]["type"] == CropType.ALFALFA
    assert results[1]["type"] == CropType.GRAIN
    assert results[0]["category"] == CropCategory.ALFALFA
    assert results[1]["category"] == CropCategory.CORN
    assert sum(result["amount"] for result in results) == 350.0


def test_query_available_feeds_specific_crop_types(
    feed_manager: FeedManager, alfalfa_crop: HarvestedCrop, corn_crop: HarvestedCrop
) -> None:
    feed_manager.receive_crop(alfalfa_crop, StorageType.PROTECTED_INDOORS)
    feed_manager.receive_crop(corn_crop, StorageType.DRY)
    feed_manager.receive_crop(corn_crop, StorageType.DRY)
    results = feed_manager.query_available_feeds(query_crop_types=[CropType.GRAIN])
    assert len(results) == 1
    assert results[0]["type"] == CropType.GRAIN
    assert results[0]["category"] == CropCategory.CORN
    assert results[0]["amount"] == 300.0


def test_query_available_feeds_specific_crop_categories(
    feed_manager: FeedManager, alfalfa_crop: HarvestedCrop, corn_crop: HarvestedCrop
) -> None:
    feed_manager.receive_crop(alfalfa_crop, StorageType.PROTECTED_INDOORS)
    feed_manager.receive_crop(corn_crop, StorageType.DRY)
    feed_manager.receive_crop(corn_crop, StorageType.DRY)
    results = feed_manager.query_available_feeds(query_crop_categories=[CropCategory.CORN])
    assert len(results) == 1
    assert results[0]["type"] == CropType.GRAIN
    assert results[0]["category"] == CropCategory.CORN
    assert results[0]["amount"] == 300.0


def test_query_available_feeds_specific_storage_types(
    feed_manager: FeedManager, alfalfa_crop: HarvestedCrop, corn_crop: HarvestedCrop
) -> None:
    feed_manager.receive_crop(alfalfa_crop, StorageType.PROTECTED_INDOORS)
    feed_manager.receive_crop(corn_crop, StorageType.DRY)
    feed_manager.receive_crop(corn_crop, StorageType.DRY)
    feed_manager.receive_crop(corn_crop, StorageType.BUNKER)
    results = feed_manager.query_available_feeds(query_storage_types=[StorageType.DRY])
    assert len(results) == 1
    assert results[0]["type"] == CropType.GRAIN
    assert results[0]["category"] == CropCategory.CORN
    assert results[0]["amount"] == 300.0


def test_query_available_feeds_empty_storage(feed_manager: FeedManager) -> None:
    results = feed_manager.query_available_feeds()
    assert len(results) == 0


def test_query_available_feeds_non_existing_crop_types(
    feed_manager: FeedManager, alfalfa_crop: HarvestedCrop, corn_crop: HarvestedCrop
) -> None:
    feed_manager.receive_crop(alfalfa_crop, StorageType.PROTECTED_INDOORS)
    feed_manager.receive_crop(corn_crop, StorageType.DRY)
    feed_manager.receive_crop(corn_crop, StorageType.DRY)
    feed_manager.receive_crop(corn_crop, StorageType.BUNKER)
    results = feed_manager.query_available_feeds(query_crop_types=[CropType.RICE])
    assert len(results) == 0


def test_query_available_feeds_combinations(
    feed_manager: FeedManager,
    alfalfa_crop: HarvestedCrop,
    corn_crop: HarvestedCrop,
    grass_crop: HarvestedCrop,
) -> None:
    feed_manager.receive_crop(alfalfa_crop, StorageType.PROTECTED_INDOORS)
    feed_manager.receive_crop(corn_crop, StorageType.DRY)
    feed_manager.receive_crop(corn_crop, StorageType.DRY)
    feed_manager.receive_crop(corn_crop, StorageType.BUNKER)
    feed_manager.receive_crop(grass_crop, StorageType.BALEAGE)
    results = feed_manager.query_available_feeds(
        query_crop_types=[CropType.GRAIN, CropType.ALFALFA],
        query_crop_categories=[CropCategory.CORN, CropCategory.GRASS],
        query_storage_types=[StorageType.DRY, StorageType.BALEAGE],
    )
    assert len(results) == 1
    assert results[0]["type"] == CropType.GRAIN
    assert results[0]["category"] == CropCategory.CORN
    assert results[0]["amount"] == 300.0
