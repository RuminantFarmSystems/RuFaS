import pytest
from datetime import date, datetime
from pytest_mock import MockerFixture

from RUFAS.data_structures.crop_soil_to_feed_storage_connection import (
    CropCategory,
    CropType,
    HarvestedCrop,
    StorageType,
)
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    NASEMFeed,
    NRCFeed,
    NutrientStandard,
    RUFAS_ID,
    FeedCategorization,
    FeedComponentType,
)
from RUFAS.biophysical.feed_storage.feed_manager import FeedManager
from RUFAS.biophysical.feed_storage.grain import Dry
from RUFAS.biophysical.feed_storage.silage import Pile
from RUFAS.biophysical.feed_storage.purchased_feed_storage import PurchasedFeed, PurchasedFeedStorage
from RUFAS.units import MeasurementUnits
from RUFAS.input_manager import InputManager
from RUFAS.time import Time

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
def purchased_feed() -> PurchasedFeed:
    """PurchasedFeed fixture for testing."""
    return PurchasedFeed(rufas_id=1, dry_matter_mass=100.0, storage_time=date(year=2025, month=3, day=6))


@pytest.fixture
def feed_manager(mocker: MockerFixture) -> FeedManager:
    """Pytest fixture to create a FeedManager instance for testing."""
    mocker.patch.object(FeedManager, "__init__", return_value=None)
    feed_manager = FeedManager(
        feed_config={},
        nutrient_standard=NutrientStandard.NASEM,
        crop_to_rufas_ids_mapping={"corn": [1, 2, 3], "alfalfa": [4, 5, 6]},
    )
    feed_manager.active_storages = {StorageType.PILE: Pile()}
    feed_manager.purchased_feed_storage = PurchasedFeedStorage()
    return feed_manager


@pytest.fixture
def time() -> Time:
    """Time fixture for testing."""
    return Time(datetime(2022, 12, 20), datetime(2025, 3, 7), datetime(2025, 3, 6))


def test_feed_manager_init() -> None:
    """Test that Feed Manager is initialized correctly."""
    pass


def test_update_available_feed_amounts() -> None:
    """Test that amounts of available feeds in Feed Manager are updated correctly."""
    pass


def test_translate_crop_config_name_to_rufas_id() -> None:
    """Test that crop config names are correctly translated to RuFaS IDs."""
    pass


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


def test_execute_daily_routines() -> None:
    """Test that the Feed Manager's daily routine is executed correctly."""
    pass


def test_report_stored_feeds() -> None:
    """Test that the Feed Manager reports stored feeds correctly."""
    pass


def test_manage_daily_feed_request() -> None:
    """Test that the daily request for feed is executed correctly."""
    pass


def test_get_total_inventory() -> None:
    """Test that the total inventory is collected correctly."""
    pass


def test_manage_planning_cycle_purchases() -> None:
    """Test that requests for feed made at beginning of a planning cycle are handled correctly."""
    pass


def test_manage_ration_interval_purchases() -> None:
    """Test that requests for feed made at beginning of a ration interval are handled correctly."""
    pass


def test_query_available_feed_totals() -> None:
    """Test that totals of available feeds are calculated correctly."""
    pass


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


def test_purchase_feed() -> None:
    """Test that feeds are purchased correctly."""
    pass


def test_purchase_feed_error() -> None:
    """Test that trying to purchase an unavailable feed raises an error."""
    pass


def test_store_purchsed_feed(feed_manager: FeedManager, time: Time, mocker: MockerFixture) -> None:
    """Test that purchased feeds are stored correctly."""
    purchased_feed_init = mocker.patch.object(PurchasedFeed, "__init__", return_value=None)
    receive_feed = mocker.patch.object(feed_manager.purchased_feed_storage, "receive_feed", return_value=None)
    expected_date = time.current_date.date()

    feed_manager._store_purchased_feed(rufas_id=1, purchase_amount=100.0, time=time)

    purchased_feed_init.assert_called_once_with(1, 100.0, expected_date)
    receive_feed.assert_called_once()


@pytest.mark.parametrize(
    "grown_amount, grown_date, purchased_amount, purchased_date, expected_grown, expected_purchased",
    [
        (50.0, date(2024, 6, 1), 50.0, date(2024, 6, 2), 0.0, 25.0),
        (50.0, date(2024, 6, 2), 50.0, date(2024, 6, 1), 25.0, 0.0),
        (75.0, date(2024, 6, 1), 50.0, date(2024, 6, 1), 0.0, 50.0),
        (25.0, date(2024, 6, 1), 50.0, date(2024, 6, 1), 0.0, 0.0),
        (0.0, date(2024, 6, 1), 75.0, date(2024, 6, 1), 0.0, 0.0),
    ],
)
def test_deduct_feeds_from_inventory(
    feed_manager: FeedManager,
    harvested_crop: HarvestedCrop,
    purchased_feed: PurchasedFeed,
    grown_amount: float,
    grown_date: date,
    purchased_amount: float,
    purchased_date: date,
    expected_grown: float,
    expected_purchased: float,
) -> None:
    """Test that feeds are removed correctly from inventory."""
    harvested_crop.rufas_ids, harvested_crop.fresh_mass, harvested_crop.dry_matter_percentage = [1], grown_amount, 100.0
    harvested_crop.storage_time = grown_date
    purchased_feed.rufas_id, purchased_feed.dry_matter_mass = 1, purchased_amount
    purchased_feed.storage_time = purchased_date
    feed_manager.active_storages[StorageType.PILE].stored = [harvested_crop]
    feed_manager.purchased_feed_storage.stored = [purchased_feed]
    feeds_to_deduct = {1: 75.0}

    feed_manager._deduct_feeds_from_inventory(feeds_to_deduct)

    assert harvested_crop.dry_matter_mass == expected_grown
    assert purchased_feed.dry_matter_mass == expected_purchased


def test_deduct_feeds_from_inventory_error(feed_manager: FeedManager, harvested_crop: HarvestedCrop) -> None:
    """Test that an error is raised correctly when too much feed is deducted from inventory."""
    harvested_crop.rufas_ids, harvested_crop.fresh_mass, harvested_crop.dry_matter_percentage = [1], 100.0, 100.0
    feed_manager.active_storages[StorageType.PILE].stored = [harvested_crop]
    feeds_to_deduct = {1: 120.0}

    with pytest.raises(ValueError):
        feed_manager._deduct_feeds_from_inventory(feeds_to_deduct)


@pytest.mark.parametrize(
    "crop_ids, feed_ids, expected", [([1, 2, 3], [4, 5, 6], None), ([1, 2, 3], [3, 4, 5], 3), ([2, 1], [2, 1], 1)]
)
def test_select_rufas_id_for_harvested_crop(
    feed_manager: FeedManager, crop_ids: list[RUFAS_ID], feed_ids: list[RUFAS_ID], expected: RUFAS_ID | None
) -> None:
    """Test that a HarvestedCrop is correctly mapped to a RuFaS ID."""
    actual = feed_manager._select_rufas_id_for_harvested_crop(crop_ids, feed_ids)

    assert actual == expected


@pytest.mark.parametrize("standard, feed_rep", [(NutrientStandard.NASEM, NASEMFeed), (NutrientStandard.NRC, NRCFeed)])
def test_setup_available_feeds(
    feed_manager: FeedManager,
    mocker: MockerFixture,
    standard: NutrientStandard,
    feed_rep: type[NASEMFeed] | type[NRCFeed],
) -> None:
    """Test that the available feeds are setup correctly."""
    feed_lib = {
        1: {
            "feed_type": FeedComponentType.FORAGE,
            "Fd_Category": FeedCategorization.GRASS_LEGUME_FORAGE,
            "units": MeasurementUnits.KILOGRAMS,
        },
        2: {
            "feed_type": FeedComponentType.CONC,
            "Fd_Category": FeedCategorization.FAT_SUPPLEMENT,
            "units": MeasurementUnits.KILOGRAMS,
        },
    }
    mocker.patch.object(feed_manager, "_process_feed_library", return_value=feed_lib)
    feed_config = {
        "purchased_feeds": [
            {"purchased_feed": 1, "purchased_feed_cost": 1.0},
            {"purchased_feed": 2, "purchased_feed_cost": 2.0},
        ]
    }
    first_expected_call_args = {
        "rufas_id": 1,
        "amount_available": 0.0,
        "on_farm_cost": 0.01,
        "purchase_cost": 1.0,
    } | feed_lib[1]
    second_expected_call_args = {
        "rufas_id": 2,
        "amount_available": 0.0,
        "on_farm_cost": 0.02,
        "purchase_cost": 2.0,
    } | feed_lib[2]
    expected_calls = [mocker.call(**first_expected_call_args), mocker.call(**second_expected_call_args)]
    feed_rep_init = mocker.patch.object(feed_rep, "__init__", return_value=None)

    feed_manager._setup_available_feeds(feed_config, standard)

    feed_rep_init.assert_has_calls(expected_calls)


def test_setup_available_feeds_error(feed_manager: FeedManager, mocker: MockerFixture) -> None:
    """Test that an error is thrown when a non-existent feed is listed."""
    feed_lib = {
        1: {
            "feed_type": FeedComponentType.FORAGE,
            "Fd_Category": FeedCategorization.GRASS_LEGUME_FORAGE,
            "units": MeasurementUnits.KILOGRAMS,
        },
        2: {
            "feed_type": FeedComponentType.CONC,
            "Fd_Category": FeedCategorization.FAT_SUPPLEMENT,
            "units": MeasurementUnits.KILOGRAMS,
        },
    }
    mocker.patch.object(feed_manager, "_process_feed_library", return_value=feed_lib)
    feed_config = {"purchased_feeds": [{"purchased_feed": 3, "purchased_feed_cost": 1.0}]}

    with pytest.raises(KeyError):
        feed_manager._setup_available_feeds(feed_config, NutrientStandard.NASEM)


@pytest.mark.parametrize(
    "standard, expected", [(NutrientStandard.NASEM, "NASEM_Comp"), (NutrientStandard.NRC, "NRC_Comp")]
)
def test_process_feed_library(
    feed_manager: FeedManager, mocker: MockerFixture, standard: NutrientStandard, expected: str
) -> None:
    """Test that the feed library is processed correctly."""
    feed_data = {
        "rufas_id": [1, 2],
        "feed_type": ["Forage", "Conc"],
        "Fd_Category": ["Grass/Legume Forage", "Fat Supplement"],
        "units": ["kg", "kg"],
    }
    get_data = mocker.patch.object(InputManager, "get_data", return_value=feed_data)

    actual = feed_manager._process_feed_library(standard)

    assert actual == {
        1: {
            "feed_type": FeedComponentType.FORAGE,
            "Fd_Category": FeedCategorization.GRASS_LEGUME_FORAGE,
            "units": MeasurementUnits.KILOGRAMS,
        },
        2: {
            "feed_type": FeedComponentType.CONC,
            "Fd_Category": FeedCategorization.FAT_SUPPLEMENT,
            "units": MeasurementUnits.KILOGRAMS,
        },
    }
    get_data.assert_called_once_with(expected)
