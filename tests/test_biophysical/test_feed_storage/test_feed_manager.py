import pytest
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
    FeedCategorization,
    FeedComponentType,
)
from RUFAS.biophysical.feed_storage.feed_manager import FeedManager
from RUFAS.biophysical.feed_storage.grain import Dry
from RUFAS.biophysical.feed_storage.silage import Pile
from RUFAS.units import MeasurementUnits
from RUFAS.input_manager import InputManager

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
def feed_manager(mocker: MockerFixture) -> FeedManager:
    """Pytest fixture to create a FeedManager instance for testing."""
    mocker.patch.object(FeedManager, "__init__", return_value=None)
    feed_manager = FeedManager(
        feed_config={},
        nutrient_standard=NutrientStandard.NASEM,
        crop_to_rufas_ids_mapping={"corn": [1, 2, 3], "alfalfa": [4, 5, 6]},
    )
    feed_manager.active_storages = {}
    return feed_manager


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


def test_store_purchsed_feed() -> None:
    """Test that purchased feeds are stored correctly."""
    pass


def test_deduct_feeds_from_inventory() -> None:
    """Test that feeds are removed correctly from inventory."""
    pass


def test_select_rufas_id_for_harvested_crop() -> None:
    """Test that a HarvestedCrop is correctly mapped to a RuFaS ID."""
    pass


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
