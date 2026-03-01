from typing import Any, cast
from unittest.mock import MagicMock, call

from RUFAS.biophysical.feed_storage.storage import Storage
import pytest
from datetime import date, datetime, timedelta
from pytest_mock import MockerFixture

from RUFAS.data_structures.crop_soil_to_feed_storage_connection import (
    HarvestedCrop,
)
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    NASEMFeed,
    NRCFeed,
    NutrientStandard,
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
    return HarvestedCrop(**sample_crop_data)


@pytest.fixture
def alfalfa_crop() -> HarvestedCrop:
    return HarvestedCrop(**sample_crop_data_no_mass, fresh_mass=50)


@pytest.fixture
def corn_crop() -> HarvestedCrop:
    return HarvestedCrop(**sample_crop_data_no_mass, fresh_mass=150)


@pytest.fixture
def grass_crop() -> HarvestedCrop:
    return HarvestedCrop(**sample_crop_data_no_mass, fresh_mass=100)


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
def mock_feed() -> dict[str, Any]:
    """Values of a mock Feed instance."""

    return {
        "rufas_id": 1,
        "Fd_Category": FeedCategorization.ENERGY_SOURCE,
        "feed_type": FeedComponentType.CONC,
        "DM": 90.0,
        "ash": 0.0,
        "CP": 0.11,
        "N_A": 0.12,
        "N_B": 0.13,
        "N_C": 0.14,
        "Kd": 0.15,
        "dRUP": 0.16,
        "ADICP": 0.17,
        "NDICP": 0.18,
        "ADF": 0.19,
        "NDF": 0.2,
        "lignin": 0.21,
        "starch": 0.22,
        "EE": 0.23,
        "calcium": 0.24,
        "phosphorus": 0.25,
        "magnesium": 0.26,
        "potassium": 0.27,
        "sodium": 0.28,
        "chlorine": 0.29,
        "sulfur": 0.30,
        "is_fat": False,
        "is_wetforage": False,
        "units": MeasurementUnits.KILOGRAMS,
        "limit": 0.31,
        "lower_limit": 0.0,
        "TDN": 0.33,
        "DE": 0.34,
        "amount_available": 0.35,
        "on_farm_cost": 0.36,
        "purchase_cost": 0.37,
    }


@pytest.fixture
def mock_NASEM_feed() -> dict[str, Any]:
    """Values of a mock NASEM feed instance."""

    return {
        "Name": "NASEM Feed",
        "RUP": 0.4,
        "sol_prot": 0.41,
        "NDF48": 0.42,
        "WSC": 0.43,
        "FA": 0.44,
        "DE_Base": 0.45,
        "copper": 0.46,
        "iron": 0.47,
        "manganese": 0.48,
        "zinc": 0.49,
        "molibdenum": 0.5,
        "chromium": 0.51,
        "cobalt": 0.52,
        "iodine": 0.53,
        "selenium": 0.54,
        "arginine": 0.55,
        "histidine": 0.56,
        "isoleucine": 0.57,
        "leucine": 0.58,
        "lysine": 0.59,
        "methionine": 0.6,
        "phenylalanine": 0.61,
        "threonine": 0.62,
        "triptophan": 0.63,
        "valine": 0.64,
        "C120_FA": 0.65,
        "C140_FA": 0.66,
        "C160_FA": 0.67,
        "C161_FA": 0.68,
        "C180_FA": 0.69,
        "C181t_FA": 0.7,
        "C181c_FA": 0.71,
        "C182_FA": 0.72,
        "C183_FA": 0.73,
        "otherFA_FA": 0.74,
        "NPN_source": 0.75,
        "starch_digested": 0.76,
        "FA_dig": 0.77,
        "P_inorg": 0.78,
        "P_org": 0.79,
        "B_Carotene": 0.8,
        "biotin": 0.81,
        "choline": 0.82,
        "niacin": 0.83,
        "Vit_A": 0.84,
        "Vit_D": 0.85,
        "Vit_E": 0.86,
        "Abs_calcium": 0.87,
        "Abs_phosphorus": 0.88,
        "Abs_sodium": 0.89,
        "Abs_chloride": 0.9,
        "Abs_potassium": 0.91,
        "Abs_copper": 0.92,
        "Abs_iron": 0.93,
        "Abs_magnesium": 0.94,
        "Abs_manganesum": 0.95,
        "Abs_zinc": 0.96,
        "buffer": 0.0,
    }


@pytest.fixture
def mock_NRC_feed() -> dict[str, Any]:
    """Values of a mock NRC feed instance."""

    return {"non_fiber_carb": 0.97, "PAF": 0.98, "buffer": 0.0}


@pytest.fixture
def feed_manager(mocker: MockerFixture, mock_available_feeds: list[Feed]) -> FeedManager:
    """Pytest fixture to create a FeedManager instance for testing."""
    mocker.patch.object(FeedManager, "__init__", return_value=None)
    feed_manager = FeedManager.__new__(FeedManager)
    feed_manager._available_feeds = mock_available_feeds
    feed_manager._cumulative_feed_requests = {feed.rufas_id: 0.0 for feed in mock_available_feeds}
    feed_manager._cumulative_purchased_feeds_fed = {feed.rufas_id: 0.0 for feed in mock_available_feeds}
    feed_manager._cumulative_farmgrown_feeds_fed = {feed.rufas_id: 0.0 for feed in mock_available_feeds}
    feed_manager._cumulative_purchased_feeds = {feed.rufas_id: 0.0 for feed in mock_available_feeds}
    mock_pile_config: dict[str, str | float | list[str]] = {
        "name": "silage",
        "rufas_id": 1,
        "field_names": ["field_1"],
        "crop_name": "corn",
        "initial_storage_dry_matter": 500.0,
        "size": 1000.0,
        "capacity": 1_000_000.0,
    }

    feed_manager.active_storages = {"example_pile": Pile(config=mock_pile_config)}
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


@pytest.fixture
def storage() -> Storage:
    """
    Pytest fixture to create a Storage instance for testing.

    Returns
    -------
    Storage
        An instance of the Storage class.
    """
    mock_storage_config: dict[str, str | float | list[str]] = {
        "name": "Test Storage",
        "field_names": ["Test Field"],
        "crop_name": "corn_silage",
        "rufas_id": 1,
        "initial_storage_dry_matter": 50.0,
        "capacity": 1_000_000.0,
    }
    return Storage(storage_config=mock_storage_config)


def test_feed_manager_init(mocker: MockerFixture, storage: Storage) -> None:
    """Test that Feed Manager is initialized correctly."""
    feed_1, feed_2 = MagicMock(auto_spec=Feed), MagicMock(auto_spec=Feed)
    feed_1.rufas_id, feed_2.rufas_id = 1, 2
    mock_setup_available_feeds = mocker.patch(
        "RUFAS.biophysical.feed_storage.feed_manager.FeedManager._setup_available_feeds",
        return_value=(mock_available_feeds := [feed_1, feed_2]),
    )
    mock_planning_cycle_allowance_init = mocker.patch.object(PlanningCycleAllowance, "__init__", return_value=None)
    mock_runtime_purchase_allowance_init = mocker.patch.object(RuntimePurchaseAllowance, "__init__", return_value=None)
    mock_create_all_storages = mocker.patch.object(
        FeedManager,
        "_create_all_storages",
        autospec=True,
    )
    mock_create_all_storages.side_effect = lambda self, *_a, **_k: setattr(
        self, "active_storages", {"Test Storage": storage}
    )

    feed_manager = FeedManager(
        feed_config=(mock_feed_config := {"allowances": [{"purchased_feed": 1}]}),
        nutrient_standard=(mock_nutrient_standard := NutrientStandard.NASEM),
        feed_storage_configs={"type": "pile", "rufas_id": 1, "field_name": "field_1", "crop_name": "corn"},
        feed_storage_instances={"Test Storage": ["instance_1"]},
    )

    assert feed_manager.active_storages == {"Test Storage": storage}
    mock_setup_available_feeds.assert_called_once_with(mock_feed_config, mock_nutrient_standard)
    assert feed_manager.available_feeds == mock_available_feeds
    mock_planning_cycle_allowance_init.assert_called_once_with(mock_feed_config["allowances"])
    mock_runtime_purchase_allowance_init.assert_called_once_with(mock_feed_config["allowances"])
    assert mock_create_all_storages.call_count == 1
    assert feed_manager.crop_to_rufas_id == {"corn_silage": 1}


@pytest.mark.parametrize(
    "feed_storage_configs,feed_storage_instances,available_ids,expected_keys,expected_warning_calls,raises_error",
    [
        (
            {
                "Pile": [
                    {
                        "name": "S1",
                        "storage_type": "Pile",
                        "rufas_id": 1,
                        "crop_name": "corn",
                        "field_names": ["F1"],
                        "initial_storage_dry_matter": 0.0,
                        "capacity": 1_000.0,
                        "size": 500.0,
                    },
                ],
                "Bag": [
                    {
                        "name": "S2",
                        "storage_type": "Bag",
                        "rufas_id": 2,
                        "crop_name": "alfalfa",
                        "field_names": ["F2"],
                        "initial_storage_dry_matter": 0.0,
                        "capacity": 1_000.0,
                        "size": 200.0,
                    },
                ],
            },
            {"Pile": ["S1"], "Bag": ["S2"]},
            [1, 2],
            {"S1", "S2"},
            0,
            False,
        ),
        (
            {
                "Pile": [
                    {
                        "name": "S1",
                        "storage_type": "Pile",
                        "rufas_id": 1,
                        "crop_name": "corn",
                        "field_names": ["F1"],
                        "initial_storage_dry_matter": 0.0,
                        "capacity": 1_000.0,
                        "size": 500.0,
                    },
                ],
                "Bag": [
                    {
                        "name": "S1",
                        "storage_type": "Bag",
                        "rufas_id": 2,
                        "crop_name": "alfalfa",
                        "field_names": ["F2"],
                        "initial_storage_dry_matter": 0.0,
                        "capacity": 1_000.0,
                        "size": 200.0,
                    },
                ],
            },
            {"Pile": ["S1"], "Bag": ["S2"]},
            [1, 2],
            {"S1", "S2"},
            0,
            True,
        ),
        (
            {
                "Pile": [
                    {
                        "name": "S1",
                        "storage_type": "Pile",
                        "rufas_id": 99,
                        "crop_name": "corn",
                        "field_names": ["F1"],
                        "initial_storage_dry_matter": 0.0,
                        "capacity": 1_000.0,
                        "size": 500.0,
                    }
                ]
            },
            {"Pile": ["S1"]},
            [1, 2],
            {"S1"},
            1,
            False,
        ),
    ],
)
def test_create_all_storages(
    mocker: MockerFixture,
    feed_storage_configs: dict[str, Any],
    feed_storage_instances: dict[str, list[str]],
    available_ids: list[int],
    expected_keys: set[str],
    expected_warning_calls: int,
    raises_error: bool,
) -> None:
    """Test FeedManager._create_all_storages using real StorageType classes."""
    mock_feed_manager = FeedManager.__new__(FeedManager)
    mock_feed_manager.active_storages = {}
    mock_feed_manager._om = mocker.Mock()
    add_warning = mocker.patch.object(mock_feed_manager._om, "add_warning")

    mock_feed_manager._available_feeds = [MagicMock(rufas_id=i) for i in available_ids]

    if raises_error:
        with pytest.raises(KeyError):
            mock_feed_manager._create_all_storages(feed_storage_configs, feed_storage_instances)
        assert add_warning.call_count == 0
        return

    mock_feed_manager._create_all_storages(feed_storage_configs, feed_storage_instances)

    assert set(mock_feed_manager.active_storages.keys()) == expected_keys
    for storage in mock_feed_manager.active_storages.values():
        assert isinstance(storage, Storage)
        assert hasattr(storage, "rufas_feed_id")
        assert hasattr(storage, "storage_name")

    assert add_warning.call_count == expected_warning_calls


def test_validate_crop_field_mapping_all_unique(feed_manager: FeedManager, mocker: MockerFixture) -> None:
    """No error is raised when all feed storage config (crop_name, field_name) combos are unique."""
    all_configs = [
        {
            "name": "storage_1",
            "crop_name": "alfalfa_hay",
            "field_names": ["field_1"],
        },
        {
            "name": "storage_2",
            "crop_name": "alfalfa_hay",
            "field_names": ["field_2"],
        },
        {
            "name": "storage_3",
            "crop_name": "corn_silage",
            "field_names": ["field_1"],
        },
    ]
    add_error = mocker.patch.object(feed_manager._om, "add_error")

    feed_manager._validate_crop_field_mapping(all_configs)
    add_error.assert_not_called()


def test_validate_crop_field_mapping_raises_on_duplicate_combo(
    feed_manager: FeedManager, mocker: MockerFixture
) -> None:
    """Raises ValueError when the same (crop_name, field_name) combo is used by multiple storage configs."""
    all_configs = [
        {
            "name": "triticale_hay_storage_1",
            "crop_name": "winter_wheat_hay",
            "field_names": ["field_1"],
        },
        {
            "name": "winter_wheat_hay_storage_1",
            "crop_name": "winter_wheat_hay",
            "field_names": ["field_1"],
        },
    ]
    add_error = mocker.patch.object(feed_manager._om, "add_error")
    with pytest.raises(ValueError) as excinfo:
        feed_manager._validate_crop_field_mapping(all_configs)

    msg = str(excinfo.value)
    assert "Duplicate (crop_name, field_name) combinations found" in msg
    assert "Combination ('winter_wheat_hay', 'field_1')" in msg
    assert "triticale_hay_storage_1" in msg
    assert "winter_wheat_hay_storage_1" in msg
    add_error.assert_called_once()


def test_validate_storage_config_names_all_unique(feed_manager: FeedManager, mocker: MockerFixture) -> None:
    """Should NOT raise when all storage config names are unique."""
    configs = [
        {"name": "S1", "other": 1},
        {"name": "S2", "other": 2},
        {"name": "S3", "other": 3},
    ]
    add_error = mocker.patch.object(feed_manager._om, "add_error")

    feed_manager._validate_storage_config_names(configs)
    add_error.assert_not_called()


def test_validate_storage_config_unique_name_duplicate_other(feed_manager: FeedManager, mocker: MockerFixture) -> None:
    """Should not raise ValueError if two storage configs share a duplicate other."""
    configs = [
        {"name": "S1", "other": 1},
        {"name": "S2", "other": 1},
        {"name": "S3", "other": 2},
    ]
    add_error = mocker.patch.object(feed_manager._om, "add_error")
    feed_manager._validate_storage_config_names(configs)
    add_error.assert_not_called()


def test_validate_storage_config_names_duplicate_raises(feed_manager: FeedManager, mocker: MockerFixture) -> None:
    """Should raise ValueError if two storage configs share the same name."""
    configs = [
        {"name": "S1"},
        {"name": "S1"},
        {"name": "S2"},
    ]
    add_error = mocker.patch.object(feed_manager._om, "add_error")
    with pytest.raises(ValueError) as excinfo:
        feed_manager._validate_storage_config_names(configs)

    msg = str(excinfo.value)
    assert "Duplicate storage config names found" in msg
    assert "['S1']" in msg
    add_error.assert_called_once()


def test_available_feeds(feed_manager: FeedManager, mock_available_feeds: list[Feed]) -> None:
    """Test for FeedManager available_feeds property."""
    feed_manager._available_feeds = mock_available_feeds
    assert feed_manager.available_feeds == mock_available_feeds


def test_update_available_feed_amounts(
    feed_manager: FeedManager, mock_available_feeds: list[Feed], mocker: MockerFixture
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


def test_receive_crop_routes_to_matching_storage(
    mocker: MockerFixture, feed_manager: FeedManager, harvested_crop: HarvestedCrop
) -> None:
    """Tests that receive_crop routes to the correct storage, and warns if no match."""
    storage = next(iter(feed_manager.active_storages.values()))
    storage.crop_name = harvested_crop.config_name
    storage.field_names = [harvested_crop.field_name]

    mocked_receive = mocker.patch.object(storage, "receive_crop")

    mock_add_warning = mocker.patch.object(feed_manager._om, "add_warning")

    feed_manager.receive_crop(harvested_crop, simulation_day=15)

    mocked_receive.assert_called_once_with(harvested_crop, 15)
    mock_add_warning.assert_not_called()


def test_receive_crop_warns_when_no_matching_storage(
    mocker: MockerFixture, feed_manager: FeedManager, harvested_crop: HarvestedCrop
) -> None:
    """Tests that receive_crop warns when no storage matches the crop."""
    for s in feed_manager.active_storages.values():
        s.crop_name = "not-" + harvested_crop.config_name
        s.field_names = ["not-" + harvested_crop.field_name]
        mocker.patch.object(s, "receive_crop")

    mock_add_warning = mocker.patch.object(feed_manager._om, "add_warning")

    feed_manager.receive_crop(harvested_crop, simulation_day=42)

    for s in feed_manager.active_storages.values():
        cast(MagicMock, s.receive_crop).assert_not_called()

    mock_add_warning.assert_called_once()
    title, message, info = mock_add_warning.call_args.args
    assert title == "No matching storage for crop"
    assert harvested_crop.config_name in message
    assert harvested_crop.field_name in message
    assert info["class"] == feed_manager.__class__.__name__
    assert info["function"] == feed_manager.receive_crop.__name__
    assert info["simulation_day"] == 42


def test_process_degradations(feed_manager: FeedManager, mocker: MockerFixture) -> None:
    """Tests process_degradations in the FeedManager."""
    mock_time = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    dry_storage = mocker.MagicMock(autospec=Dry)
    pile_storage = mocker.MagicMock(autospec=Pile)
    feed_manager.active_storages = {"example_dry": dry_storage, "example_pile": pile_storage}

    feed_manager.process_degradations(mock_weather, mock_time)

    dry_storage.process_degradations.assert_called_once_with(mock_weather, mock_time)
    pile_storage.process_degradations.assert_called_once_with(mock_weather, mock_time)


def test_report_feed_storage_levels(feed_manager: FeedManager, mocker: MockerFixture) -> None:
    """Test that the Feed Manager's report_feed_storage_levels function is executed correctly."""
    mock_report_stored_feeds = mocker.patch.object(feed_manager, "report_stored_farmgrown_feeds")

    feed_manager.report_feed_storage_levels((mock_time := MagicMock(auto_spec=RufasTime)), "mock_suffix")

    mock_report_stored_feeds.assert_called_once_with(mock_time, "mock_suffix")


def test_report_cumulative_purchased_feeds(
    feed_manager: FeedManager, mock_available_feeds: list[Feed], mocker: MockerFixture
) -> None:
    """Test that the Feed Manager reports cumulative purchased feeds correctly."""
    simulation_day = 100
    feed_manager._om = (mock_om := MagicMock(auto_spec=OutputManager))
    mock_om_add_variable = mocker.patch.object(mock_om, "add_variable", return_value=None)
    feed_manager._cumulative_purchased_feeds = {
        1: 100.0,
        2: 200.0,
        3: 0.0,
        4: 50.5,
        5: 300.25,
    }

    feed_manager.report_cumulative_purchased_feeds(simulation_day)
    number_of_feeds_reported = len(mock_available_feeds)
    number_of_feeds_fed_reported = len(mock_available_feeds)
    assert mock_om_add_variable.call_count == number_of_feeds_reported + number_of_feeds_fed_reported


def test_report_stored_farmgrown_feeds(
    feed_manager: FeedManager, mock_available_feeds: list[Feed], mocker: MockerFixture
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
    for crop in (mock_crop_1, mock_crop_2, mock_crop_3, mock_crop_4, mock_crop_5):
        crop.dry_matter_mass = 10.0
        crop.fresh_mass = 20.0

    mock_storage_1, mock_storage_2 = (MagicMock(auto_spec=Dry), MagicMock(auto_spec=Pile))
    mock_storage_1.rufas_feed_id = 1
    mock_storage_2.rufas_feed_id = 999
    mock_storage_1.stored = [mock_crop_1, mock_crop_2]
    mock_storage_2.stored = [mock_crop_3, mock_crop_4, mock_crop_5]

    feed_manager.active_storages = {"example_dry": mock_storage_1, "example_pile": mock_storage_2}

    feed_manager.report_stored_farmgrown_feeds(mock_time, "mock_suffix")

    assert mock_om_add_variable.call_count == 2 * len(feed_manager.active_storages)


def test_manage_daily_feed_request(feed_manager: FeedManager, mocker: MockerFixture) -> None:
    """Test that daily feed requests are managed correctly."""
    mocker.patch.object(feed_manager._om, "add_variable")

    mock_query_available_feed_totals = mocker.patch.object(
        feed_manager,
        "_query_available_feed_totals",
        return_value={1: 1.1, 2: 2.2, 3: 3.3, 4: 4.4, 5: 5.5},
    )
    mock_purchase_feed = mocker.patch.object(feed_manager, "purchase_feed")
    mock_deduct_feeds_from_inventory = mocker.patch.object(
        feed_manager, "_deduct_feeds_from_inventory", return_value={}
    )
    mocker.patch.object(feed_manager, "report_stored_farmgrown_feeds")

    requested_feed = RequestedFeed(requested_feed={1: 0.8, 3: 3.3, 5: 7.5})
    mock_time = mocker.Mock(spec=RufasTime)
    mock_time.simulation_day = 123

    expected_feeds_to_purchase = {1: 0.0, 3: 0.0, 5: 2.0}
    expected_inventory_deduction = {1: 0.8, 3: 3.3, 5: 7.5}

    result = feed_manager.manage_daily_feed_request(requested_feed=requested_feed, time=mock_time)

    assert result == (True, {})
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

    assert result == (False, {})
    mock_query_available_feed_totals.assert_called_once_with(list(requested_feed.requested_feed.keys()))
    mock_purchase_feed.assert_not_called()
    mock_deduct_feeds_from_inventory.assert_not_called()


def test_get_total_projected_inventory(
    feed_manager: FeedManager, mock_available_feeds: list[Feed], mocker: MockerFixture
) -> None:
    """Test that the total projected inventory is collected correctly."""
    storage_1, storage_2, storage_3 = (MagicMock(auto_spec=Dry), MagicMock(auto_spec=Pile), MagicMock(auto_spec=Bag))
    storage_1.rufas_feed_id = 1
    storage_2.rufas_feed_id = 2
    storage_3.rufas_feed_id = 3

    feed_manager.active_storages = {"example_dry": storage_1, "example_pile": storage_2, "example_bag": storage_3}
    feed_manager._available_feeds = mock_available_feeds

    s1_crops = [MagicMock(auto_spec=HarvestedCrop)]
    s1_crops[0].dry_matter_mass = 10.0

    s2_crops = [MagicMock(auto_spec=HarvestedCrop) for _ in range(3)]
    for i, dm in enumerate([20.0, 30.0, 5.0]):
        s2_crops[i].dry_matter_mass = dm

    s3_crops = [MagicMock(auto_spec=HarvestedCrop)]
    s3_crops[0].dry_matter_mass = 7.5

    mocker.patch.object(storage_1, "project_degradations", return_value=s1_crops)
    mocker.patch.object(storage_2, "project_degradations", return_value=s2_crops)
    mocker.patch.object(storage_3, "project_degradations", return_value=s3_crops)

    expected_projected_crops = {
        1: 10.0,
        2: 20.0 + 30.0 + 5.0,
        3: 7.5,
    }

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
    feed_manager: FeedManager, mock_available_feeds: list[Feed], mocker: MockerFixture
) -> None:
    """Test that the total projected inventory is collected correctly when the requested inventory date
    is the current date."""
    storage_1, storage_2, storage_3 = (MagicMock(auto_spec=Dry), MagicMock(auto_spec=Pile), MagicMock(auto_spec=Bag))
    feed_manager.active_storages = {"example_dry": storage_1, "example_pile": storage_2, "example_bag": storage_3}
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
    feed_manager: FeedManager, mocker: MockerFixture, mock_available_feeds: list[Feed]
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


def test_query_available_feed_totals(feed_manager: FeedManager, mock_available_feeds: list[Feed]) -> None:
    """Totals are farmgrown(projected dict) + purchased storage."""
    feed_manager.purchased_feed_storage = PurchasedFeedStorage(mock_available_feeds)
    feed_manager.purchased_feed_storage.receive_feed(
        PurchasedFeed(rufas_id=2, dry_matter_mass=2.2, storage_time=datetime.today().date())
    )
    feed_manager.purchased_feed_storage.receive_feed(
        PurchasedFeed(rufas_id=5, dry_matter_mass=5.5, storage_time=datetime.today().date())
    )

    projected_farmgrown = {1: 1.1, 2: 2.2}

    expected = {1: 1.1, 2: 2.2 + 2.2, 3: 0.0}

    result = feed_manager._query_available_feed_totals([1, 2, 3], projected_farmgrown)

    assert result == expected


def test_query_available_feed_totals_no_stored_crops_input(
    feed_manager: FeedManager, mock_available_feeds: list[Feed]
) -> None:
    """Test that totals of available feeds are calculated correctly when user did not specify the stored_crops input."""
    feed_1, feed_2, feed_3 = (MagicMock(auto_spec=HarvestedCrop) for _ in range(3))
    feed_1.dry_matter_mass, feed_2.dry_matter_mass, feed_3.dry_matter_mass = (1.1, 2.2, 3.3)

    storage_1, storage_2 = (MagicMock(auto_spec=Dry), MagicMock(auto_spec=Pile))
    storage_1.rufas_feed_id, storage_2.rufas_feed_id = 1, 2
    storage_1.stored, storage_2.stored = [feed_1], [feed_2, feed_3]
    feed_manager.active_storages = {"example_dry": storage_1, "example_pile": storage_2}

    feed_manager.purchased_feed_storage = PurchasedFeedStorage(mock_available_feeds)
    feed_manager.purchased_feed_storage.receive_feed(
        PurchasedFeed(rufas_id=2, dry_matter_mass=2.2, storage_time=datetime.today().date())
    )
    feed_manager.purchased_feed_storage.receive_feed(
        PurchasedFeed(rufas_id=5, dry_matter_mass=5.5, storage_time=datetime.today().date())
    )

    expected_feed_totals = {1: 1.1, 2: 7.7, 3: 0.0}

    result = feed_manager._query_available_feed_totals([1, 2, 3], None)

    assert result == expected_feed_totals


def test_purchase_feed(feed_manager: FeedManager, mock_available_feeds: list[Feed], mocker: MockerFixture) -> None:
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
    feed_manager: FeedManager, mock_available_feeds: list[Feed], mocker: MockerFixture
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
        (50.0, date(2024, 6, 2), 50.0, date(2024, 6, 1), 0.0, 25.0),
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
    harvested_crop.dry_matter_mass, harvested_crop.dry_matter_percentage = grown_amount, 100.0
    harvested_crop.storage_time = grown_date
    harvested_crop.config_name = "corn"
    purchased_feed.rufas_id, purchased_feed.dry_matter_mass = 1, purchased_amount
    purchased_feed.storage_time = purchased_date
    bag_config: dict[str, str | float | list[str]] = {
        "name": "silage",
        "rufas_id": 1,
        "field_names": ["field_1"],
        "crop_name": "corn",
        "initial_storage_dry_matter": 500.0,
        "size": 1000.0,
        "capacity": 1_000_000.0,
    }
    feed_manager.active_storages["example_bag"] = Bag(config=bag_config)
    feed_manager.active_storages["example_bag"].stored = [harvested_crop]
    feed_manager.purchased_feed_storage.stored = [purchased_feed]
    feed_manager.crop_to_rufas_id = {"corn": 1}
    feed_manager.active_storages["example_bag"].crop_name = "corn"
    feed_manager.active_storages["example_bag"].rufas_feed_id = 1
    feeds_to_deduct = {1: 75.0}
    mock_time = MagicMock(auto_spec=RufasTime)
    mock_simulation_day = 15
    mock_time.simulation_day = mock_simulation_day

    feed_manager._deduct_feeds_from_inventory(feeds_to_deduct, mock_simulation_day)

    assert harvested_crop.dry_matter_mass == expected_grown
    assert purchased_feed.dry_matter_mass == expected_purchased


def test_deduct_feeds_from_inventory_error(
    feed_manager: FeedManager, harvested_crop: HarvestedCrop, purchased_feed: PurchasedFeed, mocker: MockerFixture
) -> None:
    """Test that an error is raised correctly when too much feed is deducted from inventory."""
    harvested_crop.dry_matter_mass, harvested_crop.dry_matter_percentage = 100.0, 100.0
    harvested_crop.storage_time = date(2024, 6, 1)
    harvested_crop.config_name = "corn"
    purchased_feed.rufas_id, purchased_feed.dry_matter_mass = 1, 0.0
    purchased_feed.storage_time = date(2024, 6, 1)
    bag_config: dict[str, str | float | list[str]] = {
        "name": "silage",
        "rufas_id": 1,
        "field_names": ["field_1"],
        "crop_name": "corn",
        "initial_storage_dry_matter": 500.0,
        "size": 1000.0,
        "capacity": 1_000_000.0,
    }
    feed_manager.active_storages["example_bag"] = Bag(config=bag_config)
    feed_manager.active_storages["example_bag"].stored = [harvested_crop]
    feed_manager.purchased_feed_storage.stored = [purchased_feed]
    feed_manager.crop_to_rufas_id = {"corn": 1}
    feed_manager.active_storages["example_bag"].crop_name = "corn"
    feed_manager.active_storages["example_bag"].rufas_feed_id = 1
    feeds_to_deduct = {1: 1000.0}
    mock_time = MagicMock(auto_spec=RufasTime)
    mock_simulation_day = 15
    mock_time.simulation_day = mock_simulation_day
    mock_om = MagicMock(auto_spec=OutputManager)
    mock_om_add_variable = mocker.patch.object(mock_om, "add_variable")
    feed_manager._om = mock_om

    with pytest.raises(ValueError):
        feed_manager._deduct_feeds_from_inventory(feeds_to_deduct, mock_simulation_day)
        assert mock_om_add_variable.call_count == 10


def test_deduct_from_storage_farmgrown_basic_fifo_updates_cumulative(
    feed_manager: "FeedManager",
) -> None:
    """Farmgrown: removes in FIFO order, updates cumulative dict, returns (remaining, deducted)."""
    feed_id = next(iter(feed_manager._cumulative_farmgrown_feeds_fed.keys()))

    fg1 = MagicMock(spec=HarvestedCrop)
    fg1.dry_matter_mass = 300.0
    fg1.remove_feed_mass = MagicMock()

    fg2 = MagicMock(spec=HarvestedCrop)
    fg2.dry_matter_mass = 200.0
    fg2.remove_feed_mass = MagicMock()

    deducted = feed_manager._deduct_from_storage(
        feed_id=feed_id,
        remaining=450.0,
        feed_storages=[fg1, fg2],
    )

    fg1.remove_feed_mass.assert_called_once_with(300.0)
    fg2.remove_feed_mass.assert_called_once_with(150.0)

    assert deducted == pytest.approx(450.0)
    assert feed_manager._cumulative_farmgrown_feeds_fed[feed_id] == pytest.approx(450.0)


def test_deduct_from_storage_purchased_skips_tiny_and_updates_cumulative(
    feed_manager: "FeedManager",
) -> None:
    """Purchased: skips storages with <=1e-3 available, deducts from next, updates cumulative dict."""
    feed_id = next(iter(feed_manager._cumulative_purchased_feeds_fed.keys()))

    p1 = MagicMock()
    p1.dry_matter_mass = 5e-4
    p1.remove_dry_matter_mass = MagicMock()

    p2 = MagicMock()
    p2.dry_matter_mass = 100.0
    p2.remove_dry_matter_mass = MagicMock()

    deducted = feed_manager._deduct_from_storage(
        feed_id=feed_id,
        remaining=50.0,
        feed_storages=[p1, p2],
    )

    p1.remove_dry_matter_mass.assert_not_called()
    p2.remove_dry_matter_mass.assert_called_once_with(50.0)

    assert deducted == pytest.approx(50.0)
    assert feed_manager._cumulative_purchased_feeds_fed[feed_id] == pytest.approx(50.0)


def test_deduct_from_storage_breaks_early_when_remaining_met(feed_manager: "FeedManager") -> None:
    """Covers the early break when remaining <= 1e-3 before processing all storages."""
    feed_id = next(iter(feed_manager._cumulative_farmgrown_feeds_fed.keys()))

    s1 = MagicMock(spec=HarvestedCrop)
    s1.dry_matter_mass = 100.0
    s1.remove_feed_mass = MagicMock()

    s2 = MagicMock(spec=HarvestedCrop)
    s2.dry_matter_mass = 200.0
    s2.remove_feed_mass = MagicMock()

    deducted = feed_manager._deduct_from_storage(
        feed_id=feed_id,
        remaining=50.0,
        feed_storages=[s1, s2],
    )

    s1.remove_feed_mass.assert_called_once_with(50.0)
    s2.remove_feed_mass.assert_not_called()

    assert deducted == pytest.approx(50.0)
    assert feed_manager._cumulative_farmgrown_feeds_fed[feed_id] == pytest.approx(50.0)


def test_lookup_storage_rufas_id(feed_manager: FeedManager) -> None:
    """Test that the storage rufas_id lookup works correctly."""
    storage_1, storage_2 = (MagicMock(auto_spec=Dry), MagicMock(auto_spec=Pile))
    storage_1.crop_name = "corn"
    storage_2.crop_name = "hay"
    storage_1.rufas_feed_id, storage_2.rufas_feed_id = 1, 2
    feed_manager.active_storages = {"example_dry": storage_1, "example_pile": storage_2}

    assert feed_manager._lookup_storage_rufas_id("corn") == 1
    assert feed_manager._lookup_storage_rufas_id("hay") == 2


def test_lookup_storage_rufas_id_error(feed_manager: FeedManager) -> None:
    """Test that an error is raised when looking up a non-existent storage."""
    storage_1 = MagicMock(auto_spec=Dry)
    storage_1.crop_name = "corn"
    storage_1.rufas_feed_id = 1
    feed_manager.active_storages = {"example_dry": storage_1}
    with pytest.raises(ValueError, match="No rufas id found for crop name 'non_existent_storage'."):
        feed_manager._lookup_storage_rufas_id("non_existent_storage")


def test_gather_available_feeds_by_id_groups_and_sorts() -> None:
    """Test that available feeds are gathered by rufas_id, grouped and sorted correctly."""
    fm = FeedManager.__new__(FeedManager)
    fm.crop_to_rufas_id = {"corn": 1, "alfalfa": 2}

    fm._available_feeds = [
        MagicMock(spec=["rufas_id"], rufas_id=1),
        MagicMock(spec=["rufas_id"], rufas_id=2),
    ]

    s1 = MagicMock(spec=["rufas_feed_id", "stored"])
    s1.rufas_feed_id = 1
    older = MagicMock(spec=["dry_matter_mass", "storage_time"])
    older.dry_matter_mass = 10.0
    older.storage_time = date(2024, 6, 1)
    newer = MagicMock(spec=["dry_matter_mass", "storage_time"])
    newer.dry_matter_mass = 5.0
    newer.storage_time = date(2024, 6, 5)
    zero = MagicMock(spec=["dry_matter_mass", "storage_time"])
    zero.dry_matter_mass = 0.0
    zero.storage_time = date(2024, 6, 3)
    s1.stored = [newer, older, zero]

    s2 = MagicMock(spec=["rufas_feed_id", "stored"])
    s2.rufas_feed_id = 2
    c2 = MagicMock(spec=["dry_matter_mass", "storage_time"])
    c2.dry_matter_mass = 8.0
    c2.storage_time = date(2024, 6, 2)
    s2.stored = [c2]

    s3 = MagicMock(spec=["rufas_feed_id", "stored"])
    s3.rufas_feed_id = 99
    c3 = MagicMock(spec=["dry_matter_mass", "storage_time"])
    c3.dry_matter_mass = 12.0
    c3.storage_time = date(2024, 6, 1)
    s3.stored = [c3]

    fm.active_storages = {"s1": s1, "s2": s2, "s3": s3}

    p1 = MagicMock(spec=["dry_matter_mass", "rufas_id"])
    p1.dry_matter_mass = 4.0
    p1.rufas_id = 1

    p1b = MagicMock(spec=["dry_matter_mass", "rufas_id"])
    p1b.dry_matter_mass = 2.0
    p1b.rufas_id = 1

    p2 = MagicMock(spec=["dry_matter_mass", "rufas_id"])
    p2.dry_matter_mass = 7.0
    p2.rufas_id = 2

    p_zero = MagicMock(spec=["dry_matter_mass", "rufas_id"])
    p_zero.dry_matter_mass = 1e-9
    p_zero.rufas_id = 1

    fm.purchased_feed_storage = MagicMock(spec=["stored"])
    fm.purchased_feed_storage.stored = [p1, p_zero, p2, p1b]

    farmgrown_by_id, purchased_by_id = fm._gather_available_feeds_by_id()

    assert set(farmgrown_by_id.keys()) == {1, 2}
    assert farmgrown_by_id[1] == [older, newer]
    assert farmgrown_by_id[2] == [c2]
    assert set(purchased_by_id.keys()) == {1, 2}
    assert purchased_by_id[1] == [p1, p1b]
    assert purchased_by_id[2] == [p2]


@pytest.mark.parametrize("standard, feed_cls", [(NutrientStandard.NASEM, NASEMFeed), (NutrientStandard.NRC, NRCFeed)])
def test_setup_available_feeds_using_real_feed_objects(
    feed_manager: FeedManager,
    mocker: MockerFixture,
    standard: NutrientStandard,
    feed_cls: type[NASEMFeed] | type[NRCFeed],
    mock_feed: dict[str, Any],
    mock_NASEM_feed: dict[str, Any],
    mock_NRC_feed: dict[str, Any],
) -> None:
    def nutritive_props_for(rufas_id: int) -> dict[str, Any]:
        base = dict(mock_feed)
        base["rufas_id"] = rufas_id

        if standard is NutrientStandard.NASEM:
            base |= dict(mock_NASEM_feed)
        else:
            base |= dict(mock_NRC_feed)

        for k in ("rufas_id", "amount_available", "on_farm_cost", "purchase_cost", "buffer"):
            base.pop(k, None)

        return base

    feed_lib = {
        1: nutritive_props_for(1),
        2: nutritive_props_for(2),
    }

    mocker.patch.object(feed_manager, "_process_feed_library", return_value=feed_lib)

    feed_config = {
        "purchased_feeds": [
            {"purchased_feed": 2, "purchased_feed_cost": 2.0, "buffer": 0.0},
            {"purchased_feed": 1, "purchased_feed_cost": 1.0, "buffer": 0.0},
        ]
    }

    result = feed_manager._setup_available_feeds(feed_config, standard)

    assert [f.rufas_id for f in result] == [1, 2]
    assert all(isinstance(f, feed_cls) for f in result)
    assert result[0].purchase_cost == 1.0
    assert result[0].on_farm_cost == pytest.approx(0.01)
    assert result[1].purchase_cost == 2.0
    assert result[1].on_farm_cost == pytest.approx(0.02)


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
