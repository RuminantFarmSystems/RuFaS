from copy import copy
from dataclasses import replace
from datetime import date, datetime, timedelta
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.general_constants import GeneralConstants
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
from RUFAS.biophysical.feed_storage.storage import HIGH_MOISTURE_LOSS_COEFFICIENT, Storage
from RUFAS.rufas_time import RufasTime
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
    mock_storage_config: dict[str, str | float | list[str]] = {
        "name": "Test Storage",
        "field_names": ["Test Field"],
        "crop_name": "corn_silage",
        "rufas_id": 1,
        "initial_storage_dry_matter": 50.0,
        "capacity": 1_000_000.0,
    }
    return Storage(storage_config=mock_storage_config)


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
def time() -> RufasTime:
    """
    Pytest fixture to create a RufasTime instance for testing.

    Returns
    -------
    RufasTime
        An instance of the RufasTime class.
    """
    return RufasTime(datetime(2022, 12, 20), datetime(2025, 3, 7), datetime(2025, 3, 3))


@pytest.fixture
def weather(mocker: MockerFixture, time: RufasTime) -> Weather:
    """Creates a Weather instance for testing."""
    mocker.patch.object(Weather, "__init__", return_value=None)
    return Weather({}, time)


def test_stored_mass(storage: Storage, harvested_crop: HarvestedCrop) -> None:
    """Tests the stored_mass property of Storage."""
    assert storage.stored_mass == 0.0  # Initially empty
    storage.receive_crop(harvested_crop, 15)
    storage.receive_crop(harvested_crop, 15)
    assert storage.stored_mass == 400.0  # After adding a crop


def test_successful_receive_crop(storage: Storage, harvested_crop: HarvestedCrop) -> None:
    """Tests that a crop is successfully received into storage."""
    storage.receive_crop(harvested_crop, 15)
    assert len(storage.stored) == 1
    assert storage.stored[0].fresh_mass == harvested_crop.fresh_mass
    assert storage.stored[0].storage_time.day == harvested_crop.storage_time.day
    assert storage.stored[0].storage_time.year == harvested_crop.storage_time.year


def test_receive_crop_exceeds_capacity(storage: Storage, harvested_crop: HarvestedCrop) -> None:
    """Tests that receiving a crop exceeding capacity raises an exception."""
    storage.capacity = 50.0  # Set a smaller capacity
    with pytest.raises(Exception) as excinfo:
        storage.receive_crop(harvested_crop, 15)
    assert "exceeds the storage capacity" in str(excinfo.value)


def test_receive_crop_high_moisture_triggers_loss(storage: Storage, mocker: MockerFixture) -> None:
    """Ensure HIGH_MOISTURE crop triggers dry matter loss logic and records storage."""

    crop = HarvestedCrop(
        harvest_time=date(2025, 3, 7),
        storage_time=date(2025, 3, 7),
        field_name="Test Field",
        config_name="corn_high_moisture",
        dry_matter_mass=100.0,
        dry_matter_percentage=50.0,
        dry_matter_digestibility=70.0,
        crude_protein_percent=10.0,
        non_protein_nitrogen=5.0,
        starch=30.0,
        adf=7.0,
        ndf=15.0,
        lignin=3.0,
        sugar=20.0,
        ash=6.0,
    )

    mock_remove_dm = mocker.spy(crop, "remove_dry_matter_mass")
    mock_record = mocker.patch.object(storage, "_record_stored_crops")

    storage.receive_crop(crop, simulation_day=20)

    expected_dm_removed = 100.0 * HIGH_MOISTURE_LOSS_COEFFICIENT
    mock_remove_dm.assert_called_once_with(expected_dm_removed)
    assert mock_record.call_count == 2
    assert crop in storage.stored


@pytest.mark.parametrize(
    "loss,percentage,expected_loss",
    [
        (20.0, 5.0, 40.0),
        (15.0, 6.0, 30.0),
        (0.0, 0.0, 0.0),
    ],
)
def test_process_degradations(
    storage: Storage, time: RufasTime, mocker: MockerFixture, loss: float, percentage: float, expected_loss: float
) -> None:
    """
    Test the process_degradations method of the Storage class.
    """
    expected_info_map = {
        "class": storage.__class__.__name__,
        "function": storage.process_degradations.__name__,
        "units": MeasurementUnits.KILOGRAMS,
        "prefix": "Feed.object.Storage.Test Storage",
    }
    mock_weather = mocker.MagicMock(autospec=Weather)
    mock_conditions = [mocker.MagicMock(autospec=CurrentDayConditions)] * 3

    mock_first_crop = mocker.MagicMock(spec=HarvestedCrop)
    mock_first_crop.last_time_degraded = date(2025, 1, 1)
    mock_first_crop.config_name = "alfalfa_hay"

    mock_second_crop = mocker.MagicMock(spec=HarvestedCrop)
    mock_second_crop.last_time_degraded = date(2025, 1, 2)
    mock_second_crop.config_name = "alfalfa_silage"

    mock_grain_crop = mocker.MagicMock(spec=HarvestedCrop)
    mock_grain_crop.last_time_degraded = date(2025, 1, 3)
    mock_grain_crop.config_name = "corn_grain"

    storage.stored = [mock_first_crop, mock_second_crop, mock_grain_crop]

    mocker.patch.object(storage, "_get_conditions", return_value=mock_conditions)
    mocker.patch.object(storage, "calculate_dry_matter_loss_to_gas", return_value=loss)
    mocker.patch.object(storage, "recalculate_nutrient_percentage", return_value=percentage)
    mock_add_var = mocker.patch.object(storage.om, "add_variable")
    mass_values = {"dry_matter_mass": 5000.0, "dry_matter_percentage": 10.0}
    mocker.patch.object(storage, "_calculate_mass_attributes_after_loss", return_value=mass_values)
    mock_record = mocker.patch.object(storage, "_record_stored_crops")
    mock_degradation = mocker.patch.object(
        storage,
        "_calculate_degradation_values",
        return_value={
            "gaseous_dry_matter_loss": loss,
            "crude_protein_percent": percentage,
            "starch": percentage,
            "adf": percentage,
            "ndf": percentage,
            "lignin": percentage,
            "ash": percentage,
            "last_time_degraded": time.current_date,
            "dry_matter_mass": mass_values["dry_matter_mass"],
            "dry_matter_percentage": mass_values["dry_matter_percentage"],
        },
    )

    original_values = {
        attr: getattr(mock_grain_crop, attr, None)
        for attr in [
            "crude_protein_percent",
            "starch",
            "adf",
            "ndf",
            "lignin",
            "ash",
            "dry_matter_mass",
            "dry_matter_percentage",
            "last_time_degraded",
        ]
    }

    storage.process_degradations(mock_weather, time)

    assert mock_degradation.call_count == 2
    mock_degradation.assert_has_calls(
        [
            call(mock_first_crop, mock_weather, time),
            call(mock_second_crop, mock_weather, time),
        ]
    )
    assert mock_grain_crop not in [call_args[0][0] for call_args in mock_degradation.call_args_list]

    mock_add_var.assert_called_once_with("gaseous_dry_matter_loss", expected_loss, expected_info_map)

    mock_record.assert_called_once_with(time.simulation_day)

    for crop in [mock_first_crop, mock_second_crop]:
        assert crop.crude_protein_percent == percentage
        assert crop.starch == percentage
        assert crop.adf == percentage
        assert crop.ndf == percentage
        assert crop.lignin == percentage
        assert crop.ash == percentage
        assert crop.dry_matter_mass == mass_values["dry_matter_mass"]
        assert crop.dry_matter_percentage == mass_values["dry_matter_percentage"]
        assert crop.last_time_degraded == time.current_date

    assert mock_grain_crop not in [call_args[0][0] for call_args in mock_degradation.call_args_list]

    for attr, original_value in original_values.items():
        assert getattr(mock_grain_crop, attr, None) == original_value


def test_project_degradations(
    storage: Storage, harvested_crop: HarvestedCrop, time: RufasTime, weather: Weather, mocker: MockerFixture
) -> None:
    """Test that degradations are projected correctly, and GRAIN crops are skipped."""
    loss_values: dict[str, float] = {
        "gaseous_dry_matter_loss": 100.0,
        "crude_protein_percent": 2.0,
        "starch": 2.1,
        "adf": 2.2,
        "ndf": 2.3,
        "lignin": 2.4,
        "ash": 2.5,
        "dry_matter_mass": 900.0,
        "dry_matter_percentage": 33.0,
        "last_time_degraded": 25,
    }
    expected_last_time_degraded = 25

    degradable_crops = [replace(harvested_crop) for _ in range(2)]
    grain_crop = replace(harvested_crop)
    for crop in degradable_crops:
        object.__setattr__(crop, "config_name", "not_grain")

    object.__setattr__(grain_crop, "config_name", "corn_grain")
    storage.stored = degradable_crops + [grain_crop]

    expected_degraded = [
        replace(
            crop,
            crude_protein_percent=loss_values["crude_protein_percent"],
            starch=loss_values["starch"],
            adf=loss_values["adf"],
            ndf=loss_values["ndf"],
            lignin=loss_values["lignin"],
            ash=loss_values["ash"],
            dry_matter_mass=loss_values["dry_matter_mass"],
            dry_matter_percentage=loss_values["dry_matter_percentage"],
        )
        for crop in degradable_crops
    ]
    for crop in expected_degraded:
        object.__setattr__(crop, "last_time_degraded", expected_last_time_degraded)

    mock_degradation = mocker.patch.object(
        storage, "_calculate_degradation_values", side_effect=[copy(loss_values) for _ in range(2)]
    )

    actual = storage.project_degradations(storage.stored, weather, time)

    assert actual == expected_degraded

    mock_degradation.assert_has_calls([mocker.call(crop, weather, time) for crop in degradable_crops])

    assert grain_crop not in actual


@pytest.mark.parametrize(
    "masses, expected_crop_num", [([100.0, 200.0, 300.0], 3), ([], 0), ([0.0], 0), ([150.0, 0.0], 1)]
)
def test_remove_empty_crops(
    storage: Storage, harvested_crop: HarvestedCrop, masses: list[float], expected_crop_num: int
) -> None:
    """Tests that crops with no mass left are removed from a storage."""
    storage.stored = [replace(harvested_crop, dry_matter_mass=mass) for mass in masses]

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
    harvested_crop.dry_matter_mass = fresh * percentage / 100
    harvested_crop.dry_matter_percentage = percentage

    actual = storage._calculate_mass_attributes_after_loss(harvested_crop, dry_loss, water_loss)

    assert pytest.approx(actual) == {
        "dry_matter_mass": fresh * percentage / 100 - dry_loss,
        "dry_matter_percentage": expected_percentage,
    }


def test_record_stored_crops(storage: Storage, mocker: MockerFixture) -> None:
    """Test record_stored_crops method of Storage class."""
    mock_stored_mass = mocker.patch(
        "RUFAS.biophysical.feed_storage.storage.Storage.stored_mass", new_callable=mocker.PropertyMock
    )
    mock_total_amount = mocker.patch.object(storage, "_get_total_nutritive_amount")
    mock_add_var = mocker.patch.object(storage.om, "add_variable")
    expected_get_total_amount_call_count = 9
    expected_add_var_call_count = 13

    storage._record_stored_crops(15)

    assert mock_stored_mass.call_count == 3
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
    harvested_crop.dry_matter_mass = dry_mass
    mock_getattr = mocker.patch("RUFAS.biophysical.feed_storage.storage.getattr", side_effect=percentages)
    expected_getattr_calls = [call(crop, nutrient) for crop in storage.stored]

    actual = storage._get_total_nutritive_amount(nutrient)

    assert pytest.approx(actual) == expected
    mock_getattr.assert_has_calls(expected_getattr_calls)


@pytest.mark.parametrize(
    "dry_matter,percentage,temps,expected",
    [
        (100.0, 25.0, [20.0] * 3, 0.1379672649553659),
        (40.0, 20.0, [6.0, 4.0, 6.0], 0.0208),
        (150.0, 19.0, [10.0] * 4, 0.0),
        (200.0, 23.0, [46.0, 44.0, 46.0], 0.09671999999999999),
        (55.0, 66.0, [25.0] * 2, 0.0),
        (120.0, 4.0, [15.0], 0.0),
        (100.0, 24.0, [], 0.0),
    ],
)
def test_calculate_dry_matter_loss_to_gas(
    storage: Storage,
    harvested_crop: HarvestedCrop,
    mocker: MockerFixture,
    dry_matter: float,
    percentage: float,
    temps: list[float],
    expected: float,
) -> None:
    """Tests calculate_dry_matter_loss_to_gas in Storage."""
    harvested_crop.dry_matter_percentage = percentage
    harvested_crop.dry_matter_mass = dry_matter
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
    time: RufasTime,
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
    "days,dry_mass,moisture,expected_loss",
    [
        (1, 500.0, 24.0, 2.0),
        (3, 500.0, 24.0, 6.0),
        (6, 10_000.0, 30.0, 360.0),
        (40, 5_000.0, 80.0, 3400.0),
        (20, 3_000.0, 10.0, 0.0),
    ],
)
def test_process_moisture_loss(
    storage: Storage,
    harvested_crop: HarvestedCrop,
    time: RufasTime,
    mocker: MockerFixture,
    days: int,
    dry_mass: float,
    moisture: float,
    expected_loss: float,
) -> None:
    """Tests _process_moisture_loss in Storage."""
    expected_info_map = {
        "class": storage.__class__.__name__,
        "function": storage._process_moisture_loss.__name__,
        "units": MeasurementUnits.KILOGRAMS,
        "prefix": "Feed.object.Storage.Test Storage",
    }
    harvested_crop.initial_dry_matter_percentage = 100.0 - moisture
    harvested_crop.initial_dry_matter_mass = (
        dry_mass * harvested_crop.initial_dry_matter_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION
    )
    harvested_crop.dry_matter_mass = dry_mass
    harvested_crop.storage_time = time.current_date.date()
    harvested_crop.last_time_degraded = time.current_date.date()
    time.current_date += timedelta(days=days)
    storage.stored = [harvested_crop]
    mock_add_var = mocker.patch.object(storage.om, "add_variable")

    storage._process_moisture_loss(time, 30, 12.0)

    mock_add_var.assert_called_once_with("total_moisture_loss", expected_loss, expected_info_map)
    assert pytest.approx(harvested_crop.fresh_mass) == dry_mass * 2 - expected_loss


def test_project_moisture_loss(
    storage: Storage,
    harvested_crop: HarvestedCrop,
    time: RufasTime,
    mocker: MockerFixture,
) -> None:
    """Test that mooisture loss is projected correctly."""
    moisture_loss_values = {"dry_matter_mass": 900.0, "dry_matter_percentage": 33.0, "moisture_loss": 20.0}
    expected_moisture_loss: dict[str, float] = {
        "fresh_mass": 900.0,
        "dry_matter_percentage": 33.0,
    }
    storage.stored = [replace(harvested_crop) for _ in range(3)]
    crops_with_moisture_loss = [
        replace(
            crop,
            dry_matter_mass=expected_moisture_loss["fresh_mass"],
            dry_matter_percentage=expected_moisture_loss["dry_matter_percentage"],
        )
        for crop in storage.stored
    ]
    for crop in crops_with_moisture_loss:
        object.__setattr__(crop, "dry_matter_mass", expected_moisture_loss["fresh_mass"])
        object.__setattr__(crop, "dry_matter_percentage", expected_moisture_loss["dry_matter_percentage"])
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
    time: RufasTime,
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


def test_calculate_degradation_values(storage: Storage, mocker: MockerFixture) -> None:
    """Test degradation value calculation for a harvested crop."""
    mock_crop = mocker.MagicMock(spec=HarvestedCrop)
    mock_crop.last_time_degraded = date(2025, 1, 1)
    mock_crop.dry_matter_mass = 300.0
    mock_crop.crude_protein_percent = 10.0
    mock_crop.starch = 15.0
    mock_crop.adf = 20.0
    mock_crop.ndf = 25.0
    mock_crop.lignin = 5.0
    mock_crop.ash = 8.0

    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_time.current_date.date.return_value = date(2025, 6, 10)

    mock_conditions = mocker.MagicMock()
    mocker.patch.object(storage, "_get_conditions", return_value=mock_conditions)
    mocker.patch.object(storage, "calculate_dry_matter_loss_to_gas", return_value=50.0)

    mock_recalc = mocker.patch.object(
        storage, "recalculate_nutrient_percentage", side_effect=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    )
    mocker.patch.object(
        storage,
        "_calculate_mass_attributes_after_loss",
        return_value={
            "dry_matter_mass": 900.0,
            "dry_matter_percentage": 32.0,
        },
    )

    result = storage._calculate_degradation_values(mock_crop, mock_weather, mock_time)

    assert result == {
        "gaseous_dry_matter_loss": 50.0,
        "crude_protein_percent": 1.0,
        "starch": 2.0,
        "adf": 3.0,
        "ndf": 4.0,
        "lignin": 5.0,
        "ash": 6.0,
        "dry_matter_mass": 900.0,
        "dry_matter_percentage": 32.0,
        "last_time_degraded": date(2025, 6, 10),
    }

    expected_calls = [
        mocker.call(mock_crop.crude_protein_percent, storage.crude_protein_loss_coefficient, 50.0, 300.0),
        mocker.call(mock_crop.starch, storage.starch_loss_coefficient, 50.0, 300.0),
        mocker.call(mock_crop.adf, storage.adf_loss_coefficient, 50.0, 300.0),
        mocker.call(mock_crop.ndf, storage.ndf_loss_coefficient, 50.0, 300.0),
        mocker.call(mock_crop.lignin, storage.lignin_loss_coefficient, 50.0, 300.0),
        mocker.call(mock_crop.ash, storage.ash_loss_coefficient, 50.0, 300.0),
    ]
    mock_recalc.assert_has_calls(expected_calls)
