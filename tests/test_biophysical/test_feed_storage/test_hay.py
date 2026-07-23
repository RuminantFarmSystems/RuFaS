from unittest.mock import MagicMock

import pytest
from dataclasses import replace
from datetime import datetime, date, timedelta
from pytest_mock import MockerFixture

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
from RUFAS.input_manager import InputManager
from RUFAS.biophysical.feed_storage.hay import (
    FINAL_MOISTURE_PERCENTAGE,
    INITIAL_LOSS_PERIOD,
    PROTECTED_TARPED_ADDITIONAL_LOSS_COEFFICIENT,
    PROTECTED_WRAPPED_ADDITIONAL_LOSS_COEFFICIENT,
    UNPROTECTED_OUTDOOR_ADDITIONAL_LOSS_COEFFICIENT,
    Hay,
    ProtectedTarped,
    ProtectedWrapped,
    Unprotected,
)
from RUFAS.rufas_time import RufasTime
from RUFAS.weather import Weather

from .sample_crop_data import sample_crop_data


@pytest.fixture
def mock_storage_config() -> dict[str, str | float | list[str]]:
    """Fixture to provide a mock storage configuration dictionary."""
    return {
        "name": "hay",
        "rufas_id": 1,
        "field_names": ["field_1"],
        "crop_name": "corn",
        "initial_storage_dry_matter": 300.0,
        "bale_size": 1.2,
        "target_dry_matter": 85.0,
        "capacity": 1_000_000.0,
    }


@pytest.fixture
def hay(mock_storage_config: dict[str, str | float | list[str]]) -> Hay:
    """
    Pytest fixture to create a Hay instance for testing.

    Returns
    -------
    Hay
        An instance of the Hay class.
    """
    mock_storage_config["additional_dry_matter_loss_coefficient"] = 0.0
    return Hay(config=mock_storage_config)


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
def weather(mocker: MockerFixture) -> Weather:
    """
    Pytest fixture to create a Weather instance for testing.

    Returns
    -------
    Weather
        An instance of the Weather class.

    """
    mocker.patch.object(Weather, "__init__", return_value=None)
    return Weather({}, MagicMock(auto_spec=RufasTime))


def test_process_degradations(
    hay: Hay,
    harvested_crop: HarvestedCrop,
    time: RufasTime,
    weather: Weather,
    mocker: MockerFixture,
) -> None:
    """Tests process_degradations in Hay."""
    hay.stored = [harvested_crop]
    mock_moisture_loss = mocker.patch.object(hay, "_process_moisture_loss")
    mock_storage_process_degradations = mocker.patch(
        "RUFAS.biophysical.feed_storage.storage.Storage.process_degradations"
    )

    hay.process_degradations(weather, time)

    assert hay.crude_protein_loss_coefficient == 0.0
    mock_moisture_loss.assert_called_once_with(time, INITIAL_LOSS_PERIOD, FINAL_MOISTURE_PERCENTAGE)
    mock_storage_process_degradations.assert_called_once_with(weather, time)


def test_project_degradations(
    hay: Hay,
    harvested_crop: HarvestedCrop,
    time: RufasTime,
    weather: Weather,
    mocker: MockerFixture,
) -> None:
    """Tests project_degradations in Hay."""
    hay.stored = [replace(harvested_crop, dry_matter_mass=1000.0) for _ in range(3)]
    crops_with_moisture_loss = [replace(crop, dry_matter_mass=900.0) for crop in hay.stored]
    crops_with_all_loss = [replace(crop, dry_matter_mass=800.0) for crop in hay.stored]
    project_moisture_loss = mocker.patch.object(hay, "_project_moisture_loss", return_value=crops_with_moisture_loss)
    project_degradations = mocker.patch(
        "RUFAS.biophysical.feed_storage.storage.Storage.project_degradations", return_value=crops_with_all_loss
    )

    actual = hay.project_degradations(hay.stored, weather, time)

    assert actual == crops_with_all_loss
    project_moisture_loss.assert_called_once_with(hay.stored, time, INITIAL_LOSS_PERIOD, FINAL_MOISTURE_PERCENTAGE)
    project_degradations.assert_called_once_with(crops_with_moisture_loss, weather, time)


def test_calculate_dry_matter_loss_to_gas_caps_loss_and_warns(
    hay: Hay,
    harvested_crop: HarvestedCrop,
    time: RufasTime,
    mocker: MockerFixture,
) -> None:
    """Tests that hay dry matter loss is capped and a warning is logged when raw loss exceeds available dry matter."""
    harvested_crop.storage_time = date(2024, 6, 1)
    harvested_crop.last_time_degraded = date(2024, 6, 1)
    harvested_crop.dry_matter_mass = 12.0
    harvested_crop.config_name = "test_hay"
    harvested_crop.field_name = "test_field"
    time.current_date = datetime(2024, 6, 10)

    mocker.patch.object(hay, "_calculate_initial_dry_matter_loss_to_gas", side_effect=[0.0, 20.0])
    mocker.patch.object(hay, "_calculate_subsequent_dry_matter_loss_to_gas", side_effect=[0.0, 10.0])
    mocker.patch.object(hay, "_calculate_additional_dry_matter_loss", return_value=5.0)
    mock_add_warning = mocker.patch.object(hay.om, "add_warning")

    actual = hay.calculate_dry_matter_loss_to_gas(harvested_crop, [], time)

    assert actual == 12.0
    mock_add_warning.assert_called_once_with(
        "Hay dry matter loss capped",
        (
            "Calculated dry matter loss (35.00 kg) exceeded the remaining dry matter "
            "(12.00 kg) for crop 'test_hay' in field "
            "'test_field'. Capping loss to the remaining dry matter."
        ),
        info_map={
            "class": hay.__class__.__name__,
            "function": hay.calculate_dry_matter_loss_to_gas.__name__,
        },
    )


def test_calculate_dry_matter_loss_to_gas_floors_negative_loss(
    hay: Hay,
    harvested_crop: HarvestedCrop,
    time: RufasTime,
    mocker: MockerFixture,
) -> None:
    """Tests that negative calculated hay dry matter loss is floored at zero."""
    harvested_crop.storage_time = date(2024, 6, 1)
    harvested_crop.last_time_degraded = date(2024, 6, 1)
    harvested_crop.dry_matter_mass = 100.0
    time.current_date = datetime(2024, 6, 10)

    mocker.patch.object(hay, "_calculate_initial_dry_matter_loss_to_gas", side_effect=[20.0, 5.0])
    mocker.patch.object(hay, "_calculate_subsequent_dry_matter_loss_to_gas", side_effect=[10.0, 2.0])
    mocker.patch.object(hay, "_calculate_additional_dry_matter_loss", return_value=0.0)
    mock_add_warning = mocker.patch.object(hay.om, "add_warning")

    actual = hay.calculate_dry_matter_loss_to_gas(harvested_crop, [], time)
    assert actual == 0.0
    mock_add_warning.assert_not_called()


def test_calculate_dry_matter_loss_to_gas_returns_zero_when_stored_today(
    hay: Hay,
    harvested_crop: HarvestedCrop,
    time: RufasTime,
    mocker: MockerFixture,
) -> None:
    """Tests that no dry matter loss is calculated on the crop storage date."""
    harvested_crop.storage_time = date(2024, 6, 1)
    time.current_date = datetime(2024, 6, 1)

    mock_initial_loss = mocker.patch.object(hay, "_calculate_initial_dry_matter_loss_to_gas")
    mock_subsequent_loss = mocker.patch.object(hay, "_calculate_subsequent_dry_matter_loss_to_gas")
    mock_additional_loss = mocker.patch.object(hay, "_calculate_additional_dry_matter_loss")
    mock_add_warning = mocker.patch.object(hay.om, "add_warning")

    actual = hay.calculate_dry_matter_loss_to_gas(harvested_crop, [], time)

    assert actual == 0.0
    mock_initial_loss.assert_not_called()
    mock_subsequent_loss.assert_not_called()
    mock_additional_loss.assert_not_called()
    mock_add_warning.assert_not_called()


@pytest.mark.parametrize(
    "days,expected",
    [
        (0, 0.0),
        (1, 24.5374614),
        (10, 245.374614),
        (20, 490.749228),
        (30, 736.123842),
        (40, 736.123842),
        (100, 736.123842),
    ],
)
def test_calculate_initial_dry_matter_loss(
    hay: Hay, harvested_crop: HarvestedCrop, days: int, expected: float
) -> None:
    """Tests _calculate_initial_dry_matter_loss in Hay."""
    harvested_crop.storage_time = (storage_date := date(2024, 6, 1))
    harvested_crop.initial_dry_matter_percentage = 20.0
    harvested_crop.initial_dry_matter_mass = 1_000.0
    harvested_crop.total_sensible_heat_generated = 500.0
    current_date = storage_date + timedelta(days=days)

    actual = hay._calculate_initial_dry_matter_loss_to_gas(harvested_crop, current_date)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize("initial_dry_matter_percentage", [0.0, -1.0])
def test_calculate_initial_dry_matter_loss_zero_or_negative_denominator(
    hay: Hay,
    harvested_crop: HarvestedCrop,
    initial_dry_matter_percentage: float,
) -> None:
    """Tests that initial dry matter loss is zero when the denominator is not positive."""
    harvested_crop.storage_time = date(2024, 6, 1)
    harvested_crop.initial_dry_matter_percentage = initial_dry_matter_percentage
    harvested_crop.initial_dry_matter_mass = 1_000.0
    harvested_crop.total_sensible_heat_generated = 500.0
    current_date = harvested_crop.storage_time + timedelta(days=10)

    actual = hay._calculate_initial_dry_matter_loss_to_gas(harvested_crop, current_date)

    assert actual == 0.0


@pytest.mark.parametrize("days,expected", [(15, 0.0), (30, 0.0), (31, 0.0001), (35, 0.0005), (130, 0.01)])
def test_calculate_subsequent_dry_matter_loss(
    hay: Hay, mocker: MockerFixture, harvested_crop: HarvestedCrop, days: int, expected: float
) -> None:
    """Tests _calculate_subsequent_dry_matter_loss in Hay."""
    harvested_crop.storage_time = (storage_date := date(2024, 6, 1))
    current_date = storage_date + timedelta(days=days)

    actual = hay._calculate_subsequent_dry_matter_loss_to_gas(harvested_crop, current_date)

    assert actual == expected


@pytest.mark.parametrize(
    "loss_coeff,rain,max_temp,min_temp,density,size,expected",
    [
        (0.0, [], [], [], 200.0, 1.2, 0.0),
        (0.000_01, [0.0, 10.0, 4.5], [18.0, 17.0, 18.0], [15.0, 11.0, 12.0], 215.0, 1.5, 1.66772093023e-06),
        (0.000_02, [0.0, 0.0, 3.2], [6.0, 3.0, 1.0], [2.0, -10.0, -3.0], 300.0, 1.9, 0.0),
    ],
)
def test_calculate_additional_dry_matter_loss(
    mocker: MockerFixture,
    harvested_crop: HarvestedCrop,
    loss_coeff: float,
    rain: list[float],
    max_temp: list[float],
    min_temp: list[float],
    density: float,
    size: float,
    expected: float,
    hay: Hay,
) -> None:
    """Tests _calculate_additional_dry_matter_loss in Hay."""
    im = InputManager()
    mocker.patch.object(im, "get_data", return_value=size)
    mock_conditions = []
    for i in range(len(rain)):
        mock_conditions.append(mocker.MagicMock(autospec=CurrentDayConditions))
        mock_conditions[i].rainfall = rain[i]
        mock_conditions[i].max_air_temperature = max_temp[i]
        mock_conditions[i].min_air_temperature = min_temp[i]
    hay.additional_dry_matter_loss_coefficient = loss_coeff

    harvested_crop.bale_density = density

    actual = hay._calculate_additional_dry_matter_loss(harvested_crop, mock_conditions)

    assert pytest.approx(actual) == expected


def test_protected_wrapped_init(mock_storage_config: dict[str, str | float | list[str]]) -> None:
    """Tests that ProtectedWrapped hay instances are initialized correctly."""
    mock_storage_config["additional_dry_matter_loss_coefficient"] = 0.0
    protected_wrapped = ProtectedWrapped(config=mock_storage_config)
    assert protected_wrapped.additional_dry_matter_loss_coefficient == PROTECTED_WRAPPED_ADDITIONAL_LOSS_COEFFICIENT


def test_protected_tarped_init(mock_storage_config: dict[str, str | float | list[str]]) -> None:
    """Tests that ProtectedTarped hay instances are initialized correctly."""
    mock_storage_config["additional_dry_matter_loss_coefficient"] = 0.0
    protected_tarped = ProtectedTarped(config=mock_storage_config)
    assert protected_tarped.additional_dry_matter_loss_coefficient == PROTECTED_TARPED_ADDITIONAL_LOSS_COEFFICIENT


def test_outdoor_unprotected_init(mock_storage_config: dict[str, str | float | list[str]]) -> None:
    """Tests that Unprotected hay instances are initialized correctly."""
    mock_storage_config["additional_dry_matter_loss_coefficient"] = 0.0
    unprotected = Unprotected(config=mock_storage_config)
    assert unprotected.additional_dry_matter_loss_coefficient == UNPROTECTED_OUTDOOR_ADDITIONAL_LOSS_COEFFICIENT
