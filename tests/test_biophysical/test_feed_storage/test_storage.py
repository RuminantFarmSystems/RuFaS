from copy import copy
from dataclasses import replace
from datetime import date, datetime, timedelta
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.general_constants import GeneralConstants
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import CropCategory, CropType, HarvestedCrop
from RUFAS.biophysical.feed_storage.storage import Storage
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits
from RUFAS.weather import Weather

from .sample_crop_data import sample_crop_data


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
def harvested_crop() -> HarvestedCrop:
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


@pytest.fixture
def time() -> Time:
    """
    Pytest fixture to create a Time instance for testing.

    Returns
    -------
    Time
        An instance of the Time class.
    """
    return Time(datetime(2022, 12, 20), datetime(2025, 3, 7), datetime(2025, 3, 3))


@pytest.fixture
def weather(mocker: MockerFixture, time: Time) -> Weather:
    """Creates a Weather instance for testing."""
    mocker.patch.object(Weather, "__init__", return_value=None)
    return Weather({}, time)


def test_stored_mass(storage: Storage, harvested_crop: HarvestedCrop) -> None:
    storage.acceptable_crops = [CropCategory.SMALL_GRAIN]
    assert storage.stored_mass == 0.0  # Initially empty
    storage.receive_crop(harvested_crop)
    storage.receive_crop(harvested_crop)
    assert storage.stored_mass == 200.0  # After adding a crop


def test_successful_receive_crop(storage: Storage, harvested_crop: HarvestedCrop) -> None:
    storage.acceptable_crops = [CropCategory.SMALL_GRAIN]
    storage.receive_crop(harvested_crop)
    assert len(storage.stored) == 1
    assert storage.stored[0].fresh_mass == harvested_crop.fresh_mass
    assert storage.stored[0].storage_time.day == harvested_crop.storage_time.day
    assert storage.stored[0].storage_time.year == harvested_crop.storage_time.year


def test_receive_crop_exceeds_capacity(storage: Storage, harvested_crop: HarvestedCrop) -> None:
    storage.acceptable_crops = [CropCategory.SMALL_GRAIN]
    storage.capacity = 50.0  # Set a smaller capacity
    with pytest.raises(Exception) as excinfo:
        storage.receive_crop(harvested_crop)
    assert "exceeds the storage capacity" in str(excinfo.value)


def test_receive_unacceptable_crop(storage: Storage) -> None:
    storage.acceptable_crops = [CropCategory.ALFALFA]
    incompatible_crop = HarvestedCrop(
        category=CropCategory.SMALL_GRAIN, type=CropType.WHEAT, **sample_crop_data
    )
    with pytest.raises(ValueError):
        storage.receive_crop(incompatible_crop)


def test_receive_crop_without_acceptable_crops(storage: Storage, harvested_crop: HarvestedCrop) -> None:
    storage.acceptable_crops = []

    with pytest.raises(NotImplementedError) as excinfo:
        storage.receive_crop(harvested_crop)
    assert "Storage.acceptable_crops is not populated" in str(excinfo.value)


@pytest.mark.parametrize(
    "loss,percentage,expected_loss",
    [
        (20.0, 5.0, 40.0),
        (15.0, 6.0, 30.0),
        (0.0, 0.0, 0.0),
    ],
)
def test_process_degradations(
    storage: Storage, time: Time, mocker: MockerFixture, loss: float, percentage: float, expected_loss: float
) -> None:
    """
    Test the process_degradations method of the Storage class.
    """
    expected_info_map = {
        "class": storage.__class__.__name__,
        "function": storage.process_degradations.__name__,
        "units": MeasurementUnits.KILOGRAMS,
    }
    mock_weather = mocker.MagicMock(autospec=Weather)
    mock_conditions = [mocker.MagicMock(autospec=CurrentDayConditions)] * 3

    mock_first_crop = mocker.MagicMock(autospec=HarvestedCrop)
    mock_second_crop = mocker.MagicMock(autospec=HarvestedCrop)
    storage.stored = [mock_first_crop, mock_second_crop]
    mock_get_conditions = mocker.patch.object(storage, "_get_conditions", return_value=mock_conditions)
    mock_dry_matter_loss = mocker.patch.object(storage, "calculate_dry_matter_loss_to_gas", return_value=loss)
    mock_recalc_percentage = mocker.patch.object(storage, "recalculate_nutrient_percentage", return_value=percentage)
    mock_add_var = mocker.patch.object(storage.om, "add_variable")
    mass_values = {"fresh_mass": 5000.0, "dry_matter_percentage": 10.0}
    mock_recalc_mass = mocker.patch.object(storage, "_calculate_mass_attributes_after_loss", return_value=mass_values)
    mock_record = mocker.patch.object(storage, "record_stored_crops")
    expected_get_conditions_calls = [
        call(mock_first_crop.last_time_degraded, time, mock_weather),
        call(mock_second_crop.last_time_degraded, time, mock_weather),
    ]
    expected_dry_mass_loss_calls = [
        call(mock_first_crop, mock_conditions, time),
        call(mock_second_crop, mock_conditions, time),
    ]

    storage.process_degradations(mock_weather, time)

    expected_recalculate_percentage_call_count = len(storage.stored) * 6
    expected_reset_mass_calls = [
        call(mock_first_crop, loss, moisture_loss=0.0),
        call(mock_second_crop, loss, moisture_loss=0.0),
    ]

    mock_get_conditions.assert_has_calls(expected_get_conditions_calls)
    mock_dry_matter_loss.assert_has_calls(expected_dry_mass_loss_calls)
    assert mock_recalc_percentage.call_count == expected_recalculate_percentage_call_count
    # assert time.call_count == 3
    mock_recalc_mass.assert_has_calls(expected_reset_mass_calls)
    mock_add_var.assert_called_once_with("gaseous_dry_matter_loss", loss * len(storage.stored), expected_info_map)
    mock_record.assert_called_once()
    assert mock_first_crop.crude_protein_percent == percentage
    assert mock_first_crop.starch == percentage
    assert mock_first_crop.adf == percentage
    assert mock_first_crop.ndf == percentage
    assert mock_first_crop.lignin == percentage
    assert mock_first_crop.ash == percentage
    assert mock_second_crop.crude_protein_percent == percentage
    assert mock_second_crop.starch == percentage
    assert mock_second_crop.adf == percentage
    assert mock_second_crop.ndf == percentage
    assert mock_second_crop.lignin == percentage
    assert mock_second_crop.ash == percentage


def test_project_degradations(
    storage: Storage, harvested_crop: HarvestedCrop, time: Time, weather: Weather, mocker: MockerFixture
) -> None:
    """Test that degradations are projected correctly."""
    loss_values = {
        "gaseous_dry_matter_loss": 100.0,
        "crude_protein_percent": 2.0,
        "starch": 2.1,
        "adf": 2.2,
        "ndf": 2.3,
        "lignin": 2.4,
        "ash": 2.5,
        "fresh_mass": 900.0,
        "dry_matter_percentage": 33.0,
        "last_time_degraded": date(2025, 3, 4),
    }
    expected_loss = {
        "crude_protein_percent": 2.0,
        "starch": 2.1,
        "adf": 2.2,
        "ndf": 2.3,
        "lignin": 2.4,
        "ash": 2.5,
        "fresh_mass": 900.0,
        "dry_matter_percentage": 33.0,
    }
    expected_last_time_degraded = date(2025, 3, 4)
    storage.stored = [replace(harvested_crop) for _ in range(3)]
    degraded_crops = [replace(crop, **expected_loss) for crop in storage.stored]
    for crop in degraded_crops:
        crop.last_time_degraded = expected_last_time_degraded
    calculate_moisture_loss = mocker.patch.object(
        storage, "_calculate_degradation_values", side_effect=[copy(loss_values) for _ in range(3)]
    )

    actual = storage.project_degradations(storage.stored, time, weather)

    assert actual == degraded_crops
    calculate_moisture_loss.assert_has_calls([mocker.call(crop, time, weather) for crop in storage.stored])


@pytest.mark.parametrize(
    "masses, expected_crop_num", [([100.0, 200.0, 300.0], 3), ([], 0), ([0.0], 0), ([150.0, 0.0], 1)]
)
def test_remove_empty_crops(
    storage: Storage, harvested_crop: HarvestedCrop, masses: list[float], expected_crop_num: int
) -> None:
    """Tests that crops with no mass left are removed from a storage."""
    storage.stored = [replace(harvested_crop, fresh_mass=mass) for mass in masses]

    storage.remove_empty_crops()

    assert len(storage.stored) == expected_crop_num


@pytest.mark.parametrize(
    "dry_loss,water_loss,fresh,percentage,expected_fresh,expected_percentage",
    [
        (50.0, 0.0, 1000.0, 15.0, 950.0, 10.526316),
        (200.0, 50.0, 500.0, 50.0, 250.0, 20.0),
        (150.0, 0.0, 150.0, 100.0, 0.0, 0.0),
        (0.0, 0.0, 200.0, 10.0, 200.0, 10.0),
        (0.0, 100.0, 1000.0, 10.0, 900.0, 11.11111),
    ],
)
def test_calculate_mass_attributes_after_loss(
    storage: Storage,
    harvested_crop: HarvestedCrop,
    dry_loss: float,
    water_loss: float,
    fresh: float,
    percentage: float,
    expected_fresh: float,
    expected_percentage: float,
) -> None:
    """Test _calculate_mass_attributes_after_loss method of Storage class."""
    harvested_crop.fresh_mass = fresh
    harvested_crop.dry_matter_percentage = percentage

    actual = storage._calculate_mass_attributes_after_loss(harvested_crop, dry_loss, water_loss)

    assert pytest.approx(actual) == {"fresh_mass": expected_fresh, "dry_matter_percentage": expected_percentage}


def test_record_stored_crops(storage: Storage, mocker: MockerFixture) -> None:
    """Test record_stored_crops method of Storage class."""
    mock_stored_mass = mocker.patch(
        "RUFAS.biophysical.feed_storage.storage.Storage.stored_mass", new_callable=mocker.PropertyMock
    )
    mock_total_amount = mocker.patch.object(storage, "_get_total_nutritive_amount")
    mock_add_var = mocker.patch.object(storage.om, "add_variable")
    expected_get_total_amount_call_count = 9
    expected_add_var_call_count = 11

    storage.record_stored_crops()

    mock_stored_mass.assert_called_once()
    assert mock_total_amount.call_count == expected_get_total_amount_call_count
    assert mock_add_var.call_count == expected_add_var_call_count


@pytest.mark.parametrize(
    "nutrient,dry_mass,percentages,expected",
    [
        ("crude_protein_percent", 100, [10.0, 20.0, 30.0], 60.0),
        ("adf", 45.0, [3.0, 0.0, 5.3], 3.735),
        ("ndf", 60.0, [0.0, 0.0, 0.0], 0.0),
    ],
)
def test_get_total_nutritive_amount(
    storage: Storage,
    mocker: MockerFixture,
    harvested_crop: HarvestedCrop,
    nutrient: str,
    dry_mass: float,
    percentages: list[float],
    expected: float,
) -> None:
    """Test _get_total_nutritive_amount in Storage class."""
    storage.stored = [harvested_crop] * len(percentages)
    mock_dry_matter_mass = mocker.patch(
        "RUFAS.data_structures.crop_soil_to_feed_storage_connection.HarvestedCrop.dry_matter_mass",
        new_callable=mocker.PropertyMock,
        return_value=dry_mass,
    )
    mock_getattr = mocker.patch("RUFAS.biophysical.feed_storage.storage.getattr", side_effect=percentages)
    expected_getattr_calls = [call(crop, nutrient) for crop in storage.stored]

    actual = storage._get_total_nutritive_amount(nutrient)

    assert pytest.approx(actual) == expected
    assert mock_dry_matter_mass.call_count == len(percentages)
    mock_getattr.assert_has_calls(expected_getattr_calls)


@pytest.mark.parametrize(
    "dry_matter,percentage,category,temps,expected",
    [
        (100.0, 25.0, CropCategory.ALFALFA, [20.0] * 3, 4.286303394879),
        (40.0, 20.0, CropCategory.ALFALFA, [6.0, 4.0, 6.0], 0.624),
        (150.0, 19.0, CropCategory.ALFALFA, [10.0] * 4, 0.0),
        (200.0, 23.0, CropCategory.ALFALFA, [46.0, 44.0, 46.0], 2.9016),
        (140.0, 15.0, CropCategory.CORN, [30.0, 28.0, 29.0], 1.2096),
        (80.0, 17.0, CropCategory.CORN, [30.0] * 20, 2.019438),
        (55.0, 66.0, CropCategory.GRASS, [25.0] * 2, 0.0),
        (120.0, 4.0, CropCategory.SMALL_GRAIN, [15.0], 0.0),
        (100.0, 24.0, CropCategory.GRASS, [], 0.0),
    ],
)
def test_calculate_dry_matter_loss_to_gas(
    storage: Storage,
    harvested_crop: HarvestedCrop,
    mocker: MockerFixture,
    dry_matter: float,
    percentage: float,
    category: CropCategory,
    temps: list[float],
    expected: float,
) -> None:
    """Tests calculate_dry_matter_loss_to_gas in Storage."""
    mocker.patch(
        "RUFAS.data_structures.crop_soil_to_feed_storage_connection.HarvestedCrop.dry_matter_mass",
        new_callable=mocker.PropertyMock,
        return_value=dry_matter,
    )
    harvested_crop.dry_matter_percentage = percentage
    harvested_crop.category = category
    mock_time = mocker.MagicMock()

    mock_conditions = []
    for temp in temps:
        condition = mocker.MagicMock(autospec=CurrentDayConditions)
        condition.mean_air_temperature = temp
        mock_conditions.append(condition)

    actual = storage.calculate_dry_matter_loss_to_gas(harvested_crop, mock_conditions, mock_time)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize("curr_day,last_day,expected_offset", [(1, 1, None), (13, 30, None), (10, 9, 0), (100, 1, -98)])
def test_get_conditions(
    storage: Storage,
    time: Time,
    mocker: MockerFixture,
    curr_day: int,
    last_day: int,
    expected_offset: int,
) -> None:
    """Tests _get_conditions in Storage."""
    mock_last_degradation_time = time.current_date.date() + timedelta(days=last_day)
    time.current_date += timedelta(days=curr_day)
    returned_conditions = [mocker.MagicMock(autospec=CurrentDayConditions)]
    mock_weather = mocker.MagicMock(autospec=Weather)
    mock_weather.get_conditions_series.return_value = returned_conditions

    actual = storage._get_conditions(mock_last_degradation_time, time, mock_weather)

    if expected_offset is None:
        assert actual == []
        mock_weather.get_conditions_series.assert_not_called()
    else:
        assert actual == returned_conditions
        mock_weather.get_conditions_series.assert_called_once_with(time, expected_offset, 0)


@pytest.mark.parametrize(
    "days,fresh_mass,moisture,expected_loss",
    [
        (1, 1_000.0, 24.0, 4.0),
        (3, 1_000.0, 24.0, 12.0),
        (6, 20_000.0, 30.0, 720.0),
        (40, 10_000.0, 80.0, 6_800.0),
        (20, 6_000.0, 10.0, 0.0),
    ],
)
def test_process_moisture_loss(
    storage: Storage,
    harvested_crop: HarvestedCrop,
    time: Time,
    mocker: MockerFixture,
    days: int,
    fresh_mass: float,
    moisture: float,
    expected_loss: float,
) -> None:
    """Tests _process_moisture_loss in Storage."""
    expected_info_map = {
        "class": storage.__class__.__name__,
        "function": storage.process_degradations.__name__,
        "units": MeasurementUnits.KILOGRAMS,
    }
    harvested_crop.initial_dry_matter_percentage = 100.0 - moisture
    harvested_crop.initial_dry_matter_mass = (
        fresh_mass * harvested_crop.initial_dry_matter_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION
    )
    harvested_crop.fresh_mass = fresh_mass
    harvested_crop.storage_time = time.current_date.date()
    harvested_crop.last_time_degraded = time.current_date.date()
    time.current_date += timedelta(days=days)
    storage.stored = [harvested_crop]
    mock_add_var = mocker.patch.object(storage.om, "add_variable")

    storage._process_moisture_loss(time, 30, 12.0)

    mock_add_var.assert_called_once_with("total_moisture_loss", expected_loss, expected_info_map)
    assert harvested_crop.fresh_mass == fresh_mass - expected_loss


def test_project_moisture_loss(
    storage: Storage,
    harvested_crop: HarvestedCrop,
    time: Time,
    mocker: MockerFixture,
) -> None:
    """Test that mooisture loss is projected correctly."""
    moisture_loss_values = {"fresh_mass": 900.0, "dry_matter_percentage": 33.0, "moisture_loss": 20.0}
    expected_moisture_loss = {"fresh_mass": 900.0, "dry_matter_percentage": 33.0}
    storage.stored = [replace(harvested_crop) for _ in range(3)]
    crops_with_moisture_loss = [replace(crop, **expected_moisture_loss) for crop in storage.stored]
    calculate_moisture_loss = mocker.patch.object(
        storage, "_calculate_values_after_moisture_loss", side_effect=[copy(moisture_loss_values) for _ in range(3)]
    )

    actual = storage._project_moisture_loss(storage.stored, time, loss_period := 10, final_moisture := 12.0)

    assert actual == crops_with_moisture_loss
    calculate_moisture_loss.assert_has_calls(
        [mocker.call(crop, time, loss_period, final_moisture) for crop in storage.stored]
    )


@pytest.mark.parametrize(
    "days,initial_moisture,expected",
    [
        (0, 60.0, 0.0),
        (3, 60.0, 48.0),
        (10, 60.0, 160.0),
        (30, 60.0, 480.0),
        (40, 60.0, 480.0),
        (10, 12.0, 0.0),
        (10, 8.0, 0.0),
    ],
)
def test_calculate_moisture_loss(
    storage: Storage,
    time: Time,
    harvested_crop: HarvestedCrop,
    days: int,
    initial_moisture: float,
    expected: float,
) -> None:
    """Tests that moisture losses from a hayed crop are calculated correctly."""
    harvested_crop.storage_time = time.current_date.date()
    harvested_crop.initial_dry_matter_percentage = 100.0 - initial_moisture
    harvested_crop.initial_dry_matter_mass = 400.0
    time.current_date += timedelta(days=days)

    actual = storage._calculate_moisture_loss(harvested_crop, time.current_date.date(), 30, 12.0)

    assert actual == expected


@pytest.mark.parametrize(
    "nutrients,loss_coefficient,dry_matter_loss,dry_matter,expected,warned",
    [
        (8.0, 0.4, 20.0, 100.0, 0.0, True),
        (4.0, 0.17, 21.0, 150.0, 1.88372, False),
        (6.0, 0.0, 10.0, 100.0, 6.666667, False),
        (0.5, 0.7, 100.0, 200.0, 0.0, True),
        (3.4, 0.8, 0.0, 200.0, 3.4, False),
        (5.8, 0.08, 100.0, 100.0, 0.0, False),
    ],
)
def test_recalculate_nutrient_percentage(
    storage: Storage,
    mocker: MockerFixture,
    nutrients: float,
    loss_coefficient: float,
    dry_matter_loss: float,
    dry_matter: float,
    expected: float,
    warned: bool,
) -> None:
    """
    Test the recalculate_nutrient_percentage method of the Storage class.
    """
    mock_warn = mocker.patch.object(storage.om, "add_warning")
    actual = storage.recalculate_nutrient_percentage(nutrients, loss_coefficient, dry_matter_loss, dry_matter)

    assert pytest.approx(actual) == expected
    if warned:
        mock_warn.assert_called_once()
    else:
        mock_warn.assert_not_called()


def test_give_feed(storage: Storage) -> None:
    storage.give_feed(100.0, CropType.ALFALFA)
