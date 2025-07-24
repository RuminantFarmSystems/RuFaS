from unittest.mock import MagicMock, call

import pytest
from datetime import date, datetime, timedelta
from pytest_mock import MockerFixture

from RUFAS.data_structures.crop_soil_to_feed_storage_connection import (
    CropCategory,
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
    Feed,
    PlanningCycleAllowance,
    RuntimePurchaseAllowance,
    RequestedFeed,
    IdealFeeds,
)
from RUFAS.biophysical.feed_storage.feed_manager import FeedManager
from RUFAS.biophysical.feed_storage.grain import Dry
from RUFAS.biophysical.feed_storage.silage import Pile, Bag
from RUFAS.biophysical.feed_storage.purchased_feed_storage import PurchasedFeed, PurchasedFeedStorage
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits
from RUFAS.input_manager import InputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.weather import Weather

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
    return HarvestedCrop(category=category, **sample_crop_data)


@pytest.fixture
def alfalfa_crop() -> HarvestedCrop:
    return HarvestedCrop(CropCategory.ALFALFA, **sample_crop_data_no_mass, fresh_mass=50)


@pytest.fixture
def corn_crop() -> HarvestedCrop:
    return HarvestedCrop(CropCategory.CORN, **sample_crop_data_no_mass, fresh_mass=150)


@pytest.fixture
def grass_crop() -> HarvestedCrop:
    return HarvestedCrop(CropCategory.GRASS, **sample_crop_data_no_mass, fresh_mass=100)


@pytest.fixture
def purchased_feed() -> PurchasedFeed:
    """PurchasedFeed fixture for testing."""
    return PurchasedFeed(rufas_id=1, dry_matter_mass=100.0, storage_time=date(year=2025, month=3, day=6))


@pytest.fixture
def mock_available_feeds() -> list[Feed]:
    feed_1, feed_2, feed_3, feed_4, feed_5 = (MagicMock(auto_spec=Feed) for _ in range(5))
    feed_1.rufas_id, feed_2.rufas_id, feed_3.rufas_id, feed_4.rufas_id, feed_5.rufas_id = 1, 2, 3, 4, 5
    feed_1.buffer, feed_2.buffer, feed_3.buffer, feed_4.buffer, feed_5.buffer = 1, 2, 3, 4, 5
    return [feed_1, feed_2, feed_3, feed_4, feed_5]


@pytest.fixture
def feed_manager(mocker: MockerFixture, mock_available_feeds: list[NASEMFeed | NRCFeed]) -> FeedManager:
    """Pytest fixture to create a FeedManager instance for testing."""
    mocker.patch.object(FeedManager, "__init__", return_value=None)
    feed_manager = FeedManager.__new__(FeedManager)

    # Manually set required attributes (mirroring __init__)
    feed_manager._available_feeds = mock_available_feeds
    feed_manager._cumulative_feed_requests = {feed.rufas_id: 0.0 for feed in mock_available_feeds}
    feed_manager._cumulative_purchased_feeds_fed = {feed.rufas_id: 0.0 for feed in mock_available_feeds}
    feed_manager._cumulative_farmgrown_feeds_fed = {feed.rufas_id: 0.0 for feed in mock_available_feeds}
    feed_manager._cumulative_purchased_feeds = {feed.rufas_id: 0.0 for feed in mock_available_feeds}

    feed_manager.active_storages = {StorageType.PILE: Pile()}
    feed_manager.purchased_feed_storage = PurchasedFeedStorage(mock_available_feeds)
    feed_manager._om = mocker.Mock(spec=OutputManager)
    feed_manager.runtime_purchase_allowance = RuntimePurchaseAllowance(
        [{"purchased_feed": feed.rufas_id, "runtime_purchase_allowance": 10.0} for feed in mock_available_feeds]
    )

    return feed_manager


@pytest.fixture
def time() -> RufasTime:
    """RufasTime fixture for testing."""
    return RufasTime(datetime(2022, 12, 20), datetime(2025, 3, 7), datetime(2025, 3, 6))


def test_feed_manager_init(mocker: MockerFixture) -> None:
    """Test that Feed Manager is initialized correctly."""
    feed_1, feed_2 = MagicMock(auto_spec=Feed), MagicMock(auto_spec=Feed)
    feed_1.rufas_id, feed_2.rufas_id = 1, 2
    mock_setup_available_feeds = mocker.patch(
        "RUFAS.biophysical.feed_storage.feed_manager.FeedManager._setup_available_feeds",
        return_value=(mock_available_feeds := [feed_1, feed_2]),
    )
    mock_planning_cycle_allowance_init = mocker.patch.object(PlanningCycleAllowance, "__init__", return_value=None)
    mock_runtime_purchase_allowance_init = mocker.patch.object(RuntimePurchaseAllowance, "__init__", return_value=None)
    mock_select_rufas_id_for_harvested_crop = mocker.patch(
        "RUFAS.biophysical.feed_storage.feed_manager.FeedManager._select_rufas_id_for_harvested_crop",
        side_effect=[1, None],
    )

    feed_manager = FeedManager(
        feed_config=(mock_feed_config := {"allowances": [{"runtime": 1.1}]}),
        nutrient_standard=(mock_nutrient_standard := NutrientStandard.NASEM),
        crop_to_rufas_ids_mapping={"corn": [1, 2, 3], "alfalfa": [4, 5, 6]},
    )

    assert feed_manager.active_storages == {}
    mock_setup_available_feeds.assert_called_once_with(mock_feed_config, mock_nutrient_standard)
    assert feed_manager.available_feeds == mock_available_feeds
    mock_planning_cycle_allowance_init.assert_called_once_with(mock_feed_config["allowances"])
    mock_runtime_purchase_allowance_init.assert_called_once_with(mock_feed_config["allowances"])
    assert mock_select_rufas_id_for_harvested_crop.call_args_list == [
        call([1, 2, 3], [1, 2]),
        call([4, 5, 6], [1, 2]),
    ]


def test_available_feeds(feed_manager: FeedManager, mock_available_feeds: list[NASEMFeed | NRCFeed]) -> None:
    """Test for FeedManager available_feeds property."""
    feed_manager._available_feeds = mock_available_feeds
    assert feed_manager.available_feeds == mock_available_feeds


def test_update_available_feed_amounts(
    feed_manager: FeedManager, mock_available_feeds: list[NASEMFeed | NRCFeed], mocker: MockerFixture
) -> None:
    """Test that amounts of available feeds in Feed Manager are updated correctly."""
    feed_manager._available_feeds = mock_available_feeds
    mock_query_available_feed_totals = mocker.patch.object(
        feed_manager,
        "_query_available_feed_totals",
        return_value=(expected_feeds_amount_available := {1: 1.1, 2: 2.2, 3: 3.3, 4: 4.4, 5: 5.5}),
    )

    feed_manager.update_available_feed_amounts()

    mock_query_available_feed_totals.assert_called_once_with([feed.rufas_id for feed in mock_available_feeds])
    assert {
        feed.rufas_id: feed.amount_available for feed in feed_manager.available_feeds
    } == expected_feeds_amount_available


def test_report_feed_manager_balance(
    feed_manager: FeedManager,
    mocker: MockerFixture,
) -> None:
    """Test that feed manager reports correct balance data."""
    feed_manager._cumulative_feed_requests = {1: 10.0, 2: 20.0}
    feed_manager._cumulative_purchased_feeds_fed = {1: 5.0, 2: 15.0}
    feed_manager._cumulative_farmgrown_feeds_fed = {1: 3.0, 2: 4.0}
    feed_manager._cumulative_purchased_feeds = {1: 12.0, 2: 22.0}

    add_var = mocker.patch.object(feed_manager._om, "add_variable")
    mock_report_levels = mocker.patch.object(feed_manager, "report_feed_storage_levels")

    simulation_day = 123
    info_map = {
        "class": "FeedManager",
        "function": "report_feed_manager_balance",
        "simulation_day": simulation_day,
        "units": MeasurementUnits.KILOGRAMS,
    }

    feed_manager.report_feed_manager_balance(simulation_day)

    expected_calls = [
        call("feed_1_requested_to_date", 10.0, info_map),
        call("feed_2_requested_to_date", 20.0, info_map),
        call("purchased_feed_1_fed_to_date", 5.0, info_map),
        call("purchased_feed_2_fed_to_date", 15.0, info_map),
        call("farmgrown_feed_1_fed_to_date", 3.0, info_map),
        call("farmgrown_feed_2_fed_to_date", 4.0, info_map),
        call("purchased_feed_1_purchased_to_date", 12.0, info_map),
        call("purchased_feed_2_purchased_to_date", 22.0, info_map),
    ]

    add_var.assert_has_calls(expected_calls, any_order=True)
    mock_report_levels.assert_called_once_with(simulation_day, "balance_storage_levels")


def test_translate_crop_config_name_to_rufas_id(
    feed_manager: FeedManager,
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
            simulation_day=15,
        )
    except ValueError:
        pytest.fail("Unexpected ValueError raised")


def test_receive_crop_multiple(feed_manager: FeedManager, harvested_crop: HarvestedCrop) -> None:
    try:
        feed_manager.receive_crop(
            harvested_crop=harvested_crop,
            storage_type=StorageType.DRY,
            simulation_day=15,
        )
        feed_manager.receive_crop(
            harvested_crop=harvested_crop,
            storage_type=StorageType.DRY,
            simulation_day=15,
        )
        feed_manager.receive_crop(
            harvested_crop=harvested_crop,
            storage_type=StorageType.BUNKER,
            simulation_day=15,
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
            simulation_day=15,
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


def test_report_feed_storage_levels(feed_manager: FeedManager, mocker: MockerFixture) -> None:
    """Test that the Feed Manager's report_feed_storage_levels function is executed correctly."""
    mock_report_stored_feeds = mocker.patch.object(feed_manager, "report_stored_farmgrown_feeds")

    feed_manager.report_feed_storage_levels((mock_time := MagicMock(auto_spec=RufasTime)), "mock_suffix")

    mock_report_stored_feeds.assert_called_once_with(mock_time, "mock_suffix")


def test_report_stored_farmgrown_feeds(
    feed_manager: FeedManager, mock_available_feeds: list[NASEMFeed | NRCFeed], mocker: MockerFixture
) -> None:
    """Test that the Feed Manager reports stored feeds correctly."""
    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = 100

    feed_manager._available_feeds = mock_available_feeds

    feed_manager._om = (mock_om := MagicMock(auto_spec=OutputManager))
    mock_om_add_variable = mocker.patch.object(mock_om, "add_variable", return_value=None)

    mock_crop_1, mock_crop_2, mock_crop_3, mock_crop_4, mock_crop_5 = (
        MagicMock(auto_spec=HarvestedCrop) for _ in range(5)
    )
    mock_crop_1.rufas_ids = [1, 6, 8]
    setattr(mock_crop_1, "dry_matter_mass", 10.0)
    mock_crop_2.rufas_ids = [1, 2, 5, 7]
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

    feed_manager.report_stored_farmgrown_feeds(mock_time, "mock_suffix")

    assert mock_om_add_variable.call_count == 5


def test_manage_daily_feed_request(feed_manager: FeedManager, mocker: MockerFixture) -> None:
    """Test that daily feed requests are managed correctly."""
    mocker.patch.object(feed_manager._om, "add_variable")

    mock_query_available_feed_totals = mocker.patch.object(
        feed_manager,
        "_query_available_feed_totals",
        return_value={1: 1.1, 2: 2.2, 3: 3.3, 4: 4.4, 5: 5.5},
    )
    mock_purchase_feed = mocker.patch.object(feed_manager, "purchase_feed")
    mock_deduct_feeds_from_inventory = mocker.patch.object(feed_manager, "_deduct_feeds_from_inventory")
    mocker.patch.object(feed_manager, "report_stored_farmgrown_feeds")

    requested_feed = RequestedFeed(requested_feed={1: 0.8, 3: 3.3, 5: 7.5})
    mock_time = mocker.Mock(spec=RufasTime)
    mock_time.simulation_day = 123

    expected_feeds_to_purchase = {1: 0.0, 3: 0.0, 5: 2.0}
    expected_inventory_deduction = {1: 0.8, 3: 3.3, 5: 7.5}

    result = feed_manager.manage_daily_feed_request(requested_feed=requested_feed, time=mock_time)

    assert result is True
    mock_query_available_feed_totals.assert_called_once_with(list(requested_feed.requested_feed.keys()))
    mock_purchase_feed.assert_called_once_with(
        pytest.approx(expected_feeds_to_purchase), mock_time, purchase_type="daily_feed_request"
    )
    mock_deduct_feeds_from_inventory.assert_called_once_with(
        pytest.approx(expected_inventory_deduction), mock_time.simulation_day
    )


def test_manage_daily_feed_request_unfulfillable(feed_manager: FeedManager, mocker: MockerFixture) -> None:
    """Test that daily feed requests that cannot be fulfilled are handled correctly."""
    mock_om = MagicMock(auto_spec=OutputManager)
    feed_manager._om = mock_om
    feed_manager._om.add_variable = mocker.patch.object(feed_manager._om, "add_variable")

    mock_query_available_feed_totals = mocker.patch.object(
        feed_manager,
        "_query_available_feed_totals",
        return_value={1: 1.1, 2: 2.2, 3: 3.3, 4: 4.4, 5: 5.5, 6: 6.6},
    )

    requested_feed = RequestedFeed(requested_feed={1: 0.8, 3: 3.3, 5: 7.5, 6: 16.6})

    feed_manager.runtime_purchase_allowance = RuntimePurchaseAllowance(
        [{"purchased_feed": i, "runtime_purchase_allowance": 0.0} for i in range(1, 7)]
    )

    mock_purchase_feed = mocker.patch.object(feed_manager, "purchase_feed", return_value=None)
    mock_deduct_feeds_from_inventory = mocker.patch.object(
        feed_manager, "_deduct_feeds_from_inventory", return_value=None
    )

    mock_time = mocker.Mock(spec=RufasTime)
    mock_time.simulation_day = 123

    result = feed_manager.manage_daily_feed_request(requested_feed=requested_feed, time=mock_time)

    assert result is False
    mock_query_available_feed_totals.assert_called_once_with(list(requested_feed.requested_feed.keys()))
    mock_purchase_feed.assert_not_called()
    mock_deduct_feeds_from_inventory.assert_not_called()


def test_get_total_projected_inventory(
    feed_manager: FeedManager, mock_available_feeds: list[NASEMFeed | NRCFeed], mocker: MockerFixture
) -> None:
    """Test that the total projected inventory is collected correctly."""
    storage_1, storage_2, storage_3 = (MagicMock(auto_spec=Dry), MagicMock(auto_spec=Pile), MagicMock(auto_spec=Bag))
    feed_manager.active_storages = {StorageType.DRY: storage_1, StorageType.PILE: storage_2, StorageType.BAG: storage_3}
    feed_manager._available_feeds = mock_available_feeds

    mocker.patch.object(
        storage_1,
        "project_degradations",
        return_value=(storage_1_projected_crops := [MagicMock(auto_spec=HarvestedCrop)]),
    )
    mocker.patch.object(
        storage_2,
        "project_degradations",
        return_value=(storage_2_projected_crops := [MagicMock(auto_spec=HarvestedCrop) for _ in range(3)]),
    )
    mocker.patch.object(
        storage_3,
        "project_degradations",
        return_value=(storage_3_projected_crops := [MagicMock(auto_spec=HarvestedCrop)]),
    )
    expected_projected_crops = storage_1_projected_crops + storage_2_projected_crops + storage_3_projected_crops

    mock_query_available_feed_totals = mocker.patch.object(
        feed_manager, "_query_available_feed_totals", return_value={1: 1.1, 2: 2.2, 3: 3.3, 4: 4.4, 5: 5.5}
    )
    expected_available_feed_rufas_ids = [feed.rufas_id for feed in mock_available_feeds]

    expected_inventory = {1: 1.1, 2: 2.2, 3: 3.3, 4: 4.4, 5: 5.5}

    expected_days_in_the_future = 3
    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.current_date = datetime.today()
    result = feed_manager.get_total_projected_inventory(
        inventory_date=(inventory_date := datetime.today().date() + timedelta(days=expected_days_in_the_future)),
        weather=MagicMock(auto_spec=Weather),
        time=mock_time,
    )

    mock_query_available_feed_totals.assert_called_once_with(
        expected_available_feed_rufas_ids, expected_projected_crops
    )
    assert result.available_feeds == expected_inventory
    assert result.inventory_date == inventory_date


def test_get_total_projected_inventory_zero_day_in_the_future(
    feed_manager: FeedManager, mock_available_feeds: list[NASEMFeed | NRCFeed], mocker: MockerFixture
) -> None:
    """Test that the total projected inventory is collected correctly when the requested inventory date
    is the current date."""
    storage_1, storage_2, storage_3 = (MagicMock(auto_spec=Dry), MagicMock(auto_spec=Pile), MagicMock(auto_spec=Bag))
    feed_manager.active_storages = {StorageType.DRY: storage_1, StorageType.PILE: storage_2, StorageType.BAG: storage_3}
    feed_manager._available_feeds = mock_available_feeds

    mocker.patch.object(storage_1, "project_degradations", return_value=[MagicMock(auto_spec=HarvestedCrop)])
    mocker.patch.object(
        storage_2, "project_degradations", return_value=[MagicMock(auto_spec=HarvestedCrop) for _ in range(3)]
    )
    mocker.patch.object(storage_3, "project_degradations", return_value=[MagicMock(auto_spec=HarvestedCrop)])
    expected_projected_crops = None

    mock_query_available_feed_totals = mocker.patch.object(
        feed_manager, "_query_available_feed_totals", return_value={1: 1.1, 2: 2.2, 3: 3.3, 4: 4.4, 5: 5.5}
    )
    expected_available_feed_rufas_ids = [feed.rufas_id for feed in mock_available_feeds]

    expected_inventory = {1: 1.1, 2: 2.2, 3: 3.3, 4: 4.4, 5: 5.5}

    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.current_date = datetime.today()
    result = feed_manager.get_total_projected_inventory(
        inventory_date=(inventory_date := datetime.today().date()), weather=MagicMock(auto_spec=Weather), time=mock_time
    )

    mock_query_available_feed_totals.assert_called_once_with(
        expected_available_feed_rufas_ids, expected_projected_crops
    )
    assert result.available_feeds == expected_inventory
    assert result.inventory_date == inventory_date


def test_get_total_projected_inventory_value_error(feed_manager: FeedManager) -> None:
    """Test that get_total_projected_inventory correctly raises a ValueError when the inventory_date is in the past."""
    expected_days_in_the_future = -3
    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.current_date = datetime.today()
    with pytest.raises(ValueError):
        feed_manager.get_total_projected_inventory(
            inventory_date=(datetime.today().date() + timedelta(days=expected_days_in_the_future)),
            weather=MagicMock(auto_spec=Weather),
            time=mock_time,
        )


def test_manage_planning_cycle_purchases(feed_manager: FeedManager, mocker: MockerFixture) -> None:
    """Test that requests for feed made at beginning of a planning cycle are handled correctly."""
    feed_manager.planning_cycle_allowance = PlanningCycleAllowance(
        [
            {"purchased_feed": 1, "planning_cycle_allowance": 1.1},
            {"purchased_feed": 2, "planning_cycle_allowance": 2.2},
            {"purchased_feed": 3, "planning_cycle_allowance": 3.3},
        ]
    )

    mock_purchase_feed = mocker.patch.object(feed_manager, "purchase_feed", return_value=None)

    mock_ideal_feeds = IdealFeeds(ideal_feeds={1: 1.8, 2: 1.6, 3: 3.3, 4: 8.8})
    expected_feeds_to_purchase = {1: 1.1, 2: 1.6, 3: 3.3, 4: 0.0}
    feed_manager.manage_planning_cycle_purchases(mock_ideal_feeds, time=(mock_time := MagicMock(auto_spec=RufasTime)))

    mock_purchase_feed.assert_called_once_with(expected_feeds_to_purchase, mock_time, purchase_type="planning_cycle")


def test_manage_ration_interval_purchases(
    feed_manager: FeedManager, mocker: MockerFixture, mock_available_feeds: list[NASEMFeed | NRCFeed]
) -> None:
    """Test that requests for feed made at beginning of a ration interval are handled correctly."""
    mock_purchase_feed = mocker.patch.object(feed_manager, "purchase_feed")
    mocker.patch.object(
        feed_manager,
        "_query_available_feed_totals",
        return_value={1: 0.0, 2: 0.0},
    )
    feed_manager._available_feeds = mock_available_feeds

    requested = RequestedFeed(requested_feed={1: 3.0, 2: 5.0})
    mock_time = mocker.Mock(spec=RufasTime)

    feed_manager.manage_ration_interval_purchases(requested_feeds=requested, time=mock_time)

    mock_purchase_feed.assert_called_once_with({1: 6.0, 2: 15.0}, mock_time, purchase_type="ration_interval")


def test_query_available_feed_totals(
    feed_manager: FeedManager, mocker: MockerFixture, mock_available_feeds: list[NASEMFeed | NRCFeed]
) -> None:
    """Test that totals of available feeds are calculated correctly."""
    mock_all_farmgrown_feeds_held: list[HarvestedCrop] = [
        feed_1 := MagicMock(auto_spec=HarvestedCrop),
        feed_2 := MagicMock(auto_spec=HarvestedCrop),
        feed_3 := MagicMock(auto_spec=HarvestedCrop),
    ]
    feed_1.rufas_ids, feed_2.rufas_ids, feed_3.rufas_ids = ([1, 5, 7], [2, 4, 6], [3, 8, 10])
    feed_1.dry_matter_mass, feed_2.dry_matter_mass, feed_3.dry_matter_mass = (1.1, 2.2, 3.3)

    mocker.patch.object(feed_manager, "_select_rufas_id_for_harvested_crop", side_effect=[1, 2, None])

    feed_manager.purchased_feed_storage = PurchasedFeedStorage(mock_available_feeds)
    feed_manager.purchased_feed_storage.receive_feed(
        PurchasedFeed(rufas_id=2, dry_matter_mass=2.2, storage_time=datetime.today().date())
    )
    feed_manager.purchased_feed_storage.receive_feed(
        PurchasedFeed(rufas_id=5, dry_matter_mass=5.5, storage_time=datetime.today().date())
    )

    expected_feed_totals = {1: 1.1, 2: 4.4, 3: 0.0}

    result = feed_manager._query_available_feed_totals([1, 2, 3], mock_all_farmgrown_feeds_held)

    assert result == expected_feed_totals


def test_query_available_feed_totals_no_stored_crops_input(
    feed_manager: FeedManager, mocker: MockerFixture, mock_available_feeds: list[NASEMFeed | NRCFeed]
) -> None:
    """Test that totals of available feeds are calculated correctly when user did not specify the stored_crops input."""
    feed_1, feed_2, feed_3 = (MagicMock(auto_spec=HarvestedCrop) for _ in range(3))
    feed_1.rufas_ids, feed_2.rufas_ids, feed_3.rufas_ids = ([1, 5, 7], [2, 4, 6], [3, 8, 10])
    feed_1.dry_matter_mass, feed_2.dry_matter_mass, feed_3.dry_matter_mass = (1.1, 2.2, 3.3)

    storage_1, storage_2 = (MagicMock(auto_spec=Dry), MagicMock(auto_spec=Pile))
    storage_1.stored, storage_2.stored = [feed_1], [feed_2, feed_3]
    feed_manager.active_storages = {StorageType.DRY: storage_1, StorageType.PILE: storage_2}

    mocker.patch.object(feed_manager, "_select_rufas_id_for_harvested_crop", side_effect=[1, 2, None])

    feed_manager.purchased_feed_storage = PurchasedFeedStorage(mock_available_feeds)
    feed_manager.purchased_feed_storage.receive_feed(
        PurchasedFeed(rufas_id=2, dry_matter_mass=2.2, storage_time=datetime.today().date())
    )
    feed_manager.purchased_feed_storage.receive_feed(
        PurchasedFeed(rufas_id=5, dry_matter_mass=5.5, storage_time=datetime.today().date())
    )

    expected_feed_totals = {1: 1.1, 2: 4.4, 3: 0.0}

    result = feed_manager._query_available_feed_totals([1, 2, 3], None)

    assert result == expected_feed_totals


def test_query_available_feeds_no_parameters(
    feed_manager: FeedManager, alfalfa_crop: HarvestedCrop, corn_crop: HarvestedCrop
) -> None:
    feed_manager.receive_crop(alfalfa_crop, StorageType.PROTECTED_INDOORS, simulation_day=15)
    feed_manager.receive_crop(corn_crop, StorageType.DRY, simulation_day=15)
    feed_manager.receive_crop(corn_crop, StorageType.DRY, simulation_day=15)
    results = feed_manager.query_available_feeds()
    assert len(results) == 2
    assert results[0]["feed"] == CropCategory.ALFALFA
    assert results[1]["feed"] == CropCategory.CORN


def test_query_available_feeds_specific_crop_categories(
    feed_manager: FeedManager, alfalfa_crop: HarvestedCrop, corn_crop: HarvestedCrop
) -> None:
    feed_manager.receive_crop(alfalfa_crop, StorageType.PROTECTED_INDOORS, simulation_day=15)
    feed_manager.receive_crop(corn_crop, StorageType.DRY, simulation_day=15)
    feed_manager.receive_crop(corn_crop, StorageType.DRY, simulation_day=15)
    results = feed_manager.query_available_feeds(query_crop_categories=[CropCategory.CORN])
    assert len(results) == 1
    assert results[0]["feed"] == CropCategory.CORN
    assert results[0]["amount"] == 300


def test_query_available_feeds_specific_storage_types(
    feed_manager: FeedManager, alfalfa_crop: HarvestedCrop, corn_crop: HarvestedCrop
) -> None:
    feed_manager.receive_crop(alfalfa_crop, StorageType.PROTECTED_INDOORS, simulation_day=15)
    feed_manager.receive_crop(corn_crop, StorageType.DRY, simulation_day=15)
    feed_manager.receive_crop(corn_crop, StorageType.DRY, simulation_day=15)
    feed_manager.receive_crop(corn_crop, StorageType.BUNKER, simulation_day=15)
    results = feed_manager.query_available_feeds(query_storage_types=[StorageType.DRY])
    assert len(results) == 1
    assert results[0]["feed"] == CropCategory.CORN
    assert results[0]["amount"] == 300


def test_query_available_feeds_empty_storage(feed_manager: FeedManager) -> None:
    results = feed_manager.query_available_feeds()
    assert len(results) == 0


def test_query_available_feeds_combinations(
    feed_manager: FeedManager,
    alfalfa_crop: HarvestedCrop,
    corn_crop: HarvestedCrop,
    grass_crop: HarvestedCrop,
) -> None:
    feed_manager.receive_crop(alfalfa_crop, StorageType.PROTECTED_INDOORS, simulation_day=15)
    feed_manager.receive_crop(corn_crop, StorageType.DRY, simulation_day=15)
    feed_manager.receive_crop(corn_crop, StorageType.DRY, simulation_day=15)
    feed_manager.receive_crop(corn_crop, StorageType.BUNKER, simulation_day=15)
    feed_manager.receive_crop(grass_crop, StorageType.BALEAGE, simulation_day=15)
    results = feed_manager.query_available_feeds(
        query_crop_categories=[CropCategory.CORN, CropCategory.GRASS],
        query_storage_types=[StorageType.DRY, StorageType.BALEAGE],
    )
    assert len(results) == 2
    assert results[0]["feed"] == CropCategory.CORN
    assert results[0]["amount"] == 300


def test_purchase_feed(
    feed_manager: FeedManager, mock_available_feeds: list[NASEMFeed | NRCFeed], mocker: MockerFixture
) -> None:
    """Test that feeds are purchased correctly."""
    feeds_to_purchase = {1: 1.1, 2: 2.2, 3: 3.3, 4: 4.4, 5: 5.5}
    feed_manager._available_feeds = mock_available_feeds
    feed_manager._om = MagicMock(auto_spec=OutputManager)

    mock_om_add_variable = mocker.patch.object(feed_manager._om, "add_variable")
    mock_store_purchased_feed = mocker.patch.object(feed_manager, "_store_purchased_feed")

    feed_manager.purchase_feed(
        feeds_to_purchase, MagicMock(auto_spec=RufasTime, simulation_day=42), purchase_type="daily_feed_request"
    )

    assert mock_om_add_variable.call_count == 10
    assert mock_store_purchased_feed.call_count == 5


def test_purchase_feed_error(
    feed_manager: FeedManager, mock_available_feeds: list[NASEMFeed | NRCFeed], mocker: MockerFixture
) -> None:
    """Test that trying to purchase an unavailable feed raises an error."""
    feeds_to_purchase = {1: 1.1, 2: 2.2, 7: 7.7}
    feed_manager._available_feeds = mock_available_feeds
    feed_manager._om = MagicMock(auto_spec=OutputManager)

    mocker.patch.object(feed_manager._om, "add_variable")
    mocker.patch.object(feed_manager, "_store_purchased_feed")

    with pytest.raises(ValueError, match="Trying to purchase unavailable feed 7"):
        feed_manager.purchase_feed(
            feeds_to_purchase, MagicMock(auto_spec=RufasTime, simulation_day=42), purchase_type="daily_feed_request"
        )


@pytest.mark.parametrize(
    "purchase_type, expected_dry_matter_mass",
    [
        ("test_purchase", 100.0),
        ("ration_interval", 100.0),
    ],
)
def test_store_purchased_feed(
    feed_manager: FeedManager,
    time: RufasTime,
    purchase_type: str,
    expected_dry_matter_mass: float,
    mocker: MockerFixture,
) -> None:
    """Test that purchased feeds are stored correctly."""
    receive_feed = mocker.patch.object(feed_manager.purchased_feed_storage, "receive_feed", return_value=None)
    expected_date = time.current_date.date()
    mock_om = MagicMock(auto_spec=OutputManager)
    feed_manager._om = mock_om

    feed_manager._store_purchased_feed(rufas_id=1, purchase_amount=100.0, time=time)

    received_feed = receive_feed.call_args.args[0]
    assert received_feed.rufas_id == 1
    assert received_feed.storage_time == expected_date
    assert received_feed.dry_matter_mass == pytest.approx(expected_dry_matter_mass)


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
    mock_time = MagicMock(auto_spec=RufasTime)
    mock_simulation_day = 15
    mock_time.simulation_day = mock_simulation_day

    feed_manager._deduct_feeds_from_inventory(feeds_to_deduct, mock_simulation_day)

    assert harvested_crop.dry_matter_mass == expected_grown
    assert purchased_feed.dry_matter_mass == expected_purchased


def test_deduct_feeds_from_inventory_error(
    feed_manager: FeedManager, harvested_crop: HarvestedCrop, mocker: MockerFixture
) -> None:
    """Test that an error is raised correctly when too much feed is deducted from inventory."""
    harvested_crop.rufas_ids, harvested_crop.fresh_mass, harvested_crop.dry_matter_percentage = [1], 100.0, 100.0
    feed_manager.active_storages[StorageType.PILE].stored = [harvested_crop]
    feeds_to_deduct = {1: 120.0}
    mock_om = MagicMock(auto_spec=OutputManager)
    mock_om_add_variable = mocker.patch.object(mock_om, "add_variable")
    feed_manager._om = mock_om
    mock_time = MagicMock(auto_spec=RufasTime)
    mock_simulation_day = 15
    mock_time.simulation_day = mock_simulation_day

    with pytest.raises(ValueError):
        feed_manager._deduct_feeds_from_inventory(feeds_to_deduct, mock_simulation_day)
        assert mock_om_add_variable.call_count == 0


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
            {"purchased_feed": 1, "purchased_feed_cost": 1.0, "buffer": 0.0},
            {"purchased_feed": 2, "purchased_feed_cost": 2.0, "buffer": 0.0},
        ]
    }
    first_expected_call_args = {
        "rufas_id": 1,
        "amount_available": 0.0,
        "on_farm_cost": 0.01,
        "purchase_cost": 1.0,
        "buffer": 0.0,
    } | feed_lib[1]
    second_expected_call_args = {
        "rufas_id": 2,
        "amount_available": 0.0,
        "on_farm_cost": 0.02,
        "purchase_cost": 2.0,
        "buffer": 0.0,
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
    im = InputManager()
    get_data = mocker.patch.object(im, "get_data", return_value=feed_data)

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
