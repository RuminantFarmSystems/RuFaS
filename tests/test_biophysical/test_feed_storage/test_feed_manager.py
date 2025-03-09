from unittest.mock import MagicMock, call

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
    FeedComponentType, Feed, PlanningCycleAllowance, RuntimePurchaseAllowance, RequestedFeed,
)
from RUFAS.biophysical.feed_storage.feed_manager import FeedManager
from RUFAS.biophysical.feed_storage.grain import Dry
from RUFAS.biophysical.feed_storage.silage import Pile
from RUFAS.biophysical.feed_storage.purchased_feed_storage import PurchasedFeed, PurchasedFeedStorage
from RUFAS.output_manager import OutputManager
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
def mock_available_feeds() -> list[Feed]:
    feed_1, feed_2, feed_3, feed_4, feed_5 = (MagicMock(auto_spec=Feed) for _ in range(5))
    feed_1.rufas_id, feed_2.rufas_id, feed_3.rufas_id, feed_4.rufas_id, feed_5.rufas_id = 1, 2, 3, 4, 5
    return [feed_1, feed_2, feed_3, feed_4, feed_5]


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


def test_feed_manager_init(mocker: MockerFixture) -> None:
    """Test that Feed Manager is initialized correctly."""
    feed_1, feed_2 = MagicMock(auto_spec=Feed), MagicMock(auto_spec=Feed)
    feed_1.rufas_id, feed_2.rufas_id = 1, 2
    mock_setup_available_feeds = mocker.patch(
        "RUFAS.biophysical.feed_storage.feed_manager.FeedManager._setup_available_feeds",
        return_value=(mock_available_feeds := [feed_1, feed_2]),
    )
    mock_planning_cycle_allowance_init = mocker.patch.object(
        PlanningCycleAllowance, "__init__", return_value=None)
    mock_runtime_purchase_allowance_init = mocker.patch.object(
        RuntimePurchaseAllowance, "__init__", return_value=None)
    mock_select_rufas_id_for_harvested_crop = mocker.patch(
        "RUFAS.biophysical.feed_storage.feed_manager.FeedManager._select_rufas_id_for_harvested_crop",
        side_effect=[1, None],
    )

    feed_manager = FeedManager(
        feed_config=(mock_feed_config := {"allowances": []}),
        nutrient_standard=(mock_nutrient_standard := NutrientStandard.NASEM),
        crop_to_rufas_ids_mapping={"corn": [1, 2, 3], "alfalfa": [4, 5, 6]},
    )

    assert feed_manager.active_storages == {}
    mock_setup_available_feeds.assert_called_once_with(mock_feed_config, mock_nutrient_standard)
    assert feed_manager.available_feeds == mock_available_feeds
    mock_planning_cycle_allowance_init.assert_called_once_with(mock_feed_config["allowances"])
    mock_runtime_purchase_allowance_init.assert_called_once_with(mock_feed_config["allowances"])
    assert mock_select_rufas_id_for_harvested_crop.call_args_list == [
        call([1, 2, 3], [1, 2]), call([4, 5, 6], [1, 2]),
    ]


def test_available_feeds(feed_manager: FeedManager) -> None:
    """Test for FeedManager available_feeds property."""
    feed_manager._available_feeds = (mock_available_feeds := [MagicMock(auto_spec=Feed), MagicMock(auto_spec=Feed)])
    assert feed_manager.available_feeds == mock_available_feeds


def test_update_available_feed_amounts(
        feed_manager: FeedManager, mock_available_feeds: list[Feed], mocker: MockerFixture
) -> None:
    """Test that amounts of available feeds in Feed Manager are updated correctly."""
    feed_manager._available_feeds = mock_available_feeds
    mock_query_available_feed_totals = mocker.patch.object(
        feed_manager,
        "_query_available_feed_totals",
        return_value=(expected_feeds_amount_available := {1: 1.1, 2: 2.2, 3: 3.3, 4: 4.4, 5: 5.5})
    )

    feed_manager.update_available_feed_amounts()

    mock_query_available_feed_totals.assert_called_once_with([feed.rufas_id for feed in mock_available_feeds])
    assert ({feed.rufas_id: feed.amount_available for feed in feed_manager.available_feeds} ==
            expected_feeds_amount_available)


def test_translate_crop_config_name_to_rufas_id(
        feed_manager: FeedManager, mock_available_feeds: list[Feed], mocker: MockerFixture
) -> None:
    """Test that crop config names are correctly translated to RuFaS IDs."""
    feed_manager.crop_to_rufas_id = {"corn": 8, "alfalfa": 9}
    expected_next_harvest_dates_rufas_ids = {8: datetime.today().date()}

    result = feed_manager.translate_crop_config_name_to_rufas_id(
        next_harvest_dates={"corn": datetime.today().date(), "alfalfa": None}
    )

    assert result == expected_next_harvest_dates_rufas_ids


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


def test_give_feed(feed_manager: FeedManager) -> None:
    """Tests give_feed in the FeedManager."""
    feed_manager.give_feed(0.0, CropType.GRAIN)


def test_execute_daily_routines(feed_manager: FeedManager, mocker: MockerFixture) -> None:
    """Test that the Feed Manager's daily routine is executed correctly."""
    mock_report_stored_feeds = mocker.patch.object(feed_manager, "report_stored_feeds")

    feed_manager.execute_daily_routine((mock_time := MagicMock(auto_spec=Time)))

    mock_report_stored_feeds.assert_called_once_with(mock_time)


def test_report_stored_feeds(feed_manager: FeedManager, mock_available_feeds: list[Feed], mocker: MockerFixture) -> None:
    """Test that the Feed Manager reports stored feeds correctly."""
    mock_time = MagicMock(auto_spec=Time)
    mock_time.simulation_day = 100
    info_map = {
        "class": feed_manager.__class__.__name__,
        "function": feed_manager.execute_daily_routine.__name__,
        "simulation_day": mock_time.simulation_day,
        "units": MeasurementUnits.DRY_KILOGRAMS,
    }

    feed_manager._available_feeds = mock_available_feeds

    feed_manager._om = (mock_om := MagicMock(auto_spec=OutputManager))
    mock_om_add_variable = mocker.patch.object(mock_om, "add_variable", return_value=None)

    mock_create_consolidated_feed_report = mocker.patch.object(
        feed_manager.purchased_feed_storage,
        "create_consolidated_feed_report",
        return_value={1: 1.1, 3: 3.3, 5: 5.5}
    )

    mock_crop_1, mock_crop_2, mock_crop_3, mock_crop_4, mock_crop_5 = (
        MagicMock(auto_spec=HarvestedCrop) for _ in range(5))
    mock_crop_1.rufas_ids = [1, 6, 8]
    setattr(mock_crop_1, "dry_matter_mass", 10.0)
    mock_crop_2.rufas_ids = [2, 5, 7]
    setattr(mock_crop_2, "dry_matter_mass", 10.0)
    mock_crop_3.rufas_ids = [9, 18, 27]
    setattr(mock_crop_3, "dry_matter_mass", 10.0)
    mock_crop_4.rufas_ids = [3, 5, 10]
    setattr(mock_crop_4, "dry_matter_mass", 10.0)
    mock_crop_5.rufas_ids = [144, 233, 158]
    setattr(mock_crop_5, "dry_matter_mass", 10.0)
    mock_storage_1, mock_storage_2 = (MagicMock(auto_spec=Dry), MagicMock(auto_spec=Pile))
    mock_storage_1.stored, mock_storage_2.stored = [mock_crop_1, mock_crop_2], [mock_crop_3, mock_crop_4, mock_crop_5]
    feed_manager.active_storages = {StorageType.DRY: mock_storage_1, StorageType.PILE: mock_storage_2}

    feed_manager.report_stored_feeds(mock_time)

    mock_create_consolidated_feed_report.assert_called_once()
    expected_feed_report = {1: 11.1, 3: 13.3, 5: 5.5, 2: 10.0}
    expected_om_add_variable_calls = [
        call(
            f"stored_feed_{rufas_id}", mass, {**info_map, "rufas_id": rufas_id, "mass": mass}
        ) for rufas_id, mass in expected_feed_report.items()
    ]
    assert mock_om_add_variable.call_args_list == expected_om_add_variable_calls


def test_manage_daily_feed_request() -> None:
    """Test that the daily request for feed is executed correctly."""
    pass


def test_get_total_inventory() -> None:
    """Test that the total inventory is collected correctly."""
    pass


def test_manage_planning_cycle_purchases() -> None:
    """Test that requests for feed made at beginning of a planning cycle are handled correctly."""
    pass


def test_manage_ration_interval_purchases(feed_manager: FeedManager, mocker: MockerFixture) -> None:
    """Test that requests for feed made at beginning of a ration interval are handled correctly."""
    mock_purchase_feed = mocker.patch.object(feed_manager, "purchase_feed", return_value=None)

    feed_manager.manage_ration_interval_purchases(
        requested_feeds=(mock_requested_feeds := MagicMock(auto_spec=RequestedFeed)),
        time=(mock_time := MagicMock(auto_spec=Time))
    )

    mock_purchase_feed.assert_called_once_with(mock_requested_feeds.requested_feed, mock_time)


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
