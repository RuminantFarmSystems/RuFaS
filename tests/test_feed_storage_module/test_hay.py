import pytest
from pytest_mock import MockerFixture

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.routines.feed_storage.enums import CropCategory, CropType
from RUFAS.routines.feed_storage.harvested_crop import HarvestedCrop
from RUFAS.routines.feed_storage.hay import (
    PROTECTED_TARPED_ADDITIONAL_LOSS_COEFFICIENT,
    PROTECTED_WRAPPED_ADDITIONAL_LOSS_COEFFICIENT,
    UNPROTECTED_OUTDOOR_ADDITIONAL_LOSS_COEFFICIENT,
    Hay,
    ProtectedTarped,
    ProtectedWrapped,
    Unprotected,
)
from RUFAS.general_constants import GeneralConstants
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits

from .sample_crop_data import sample_crop_data


@pytest.fixture
def hay() -> Hay:
    """
    Pytest fixture to create a Hay instance for testing.

    Returns
    -------
    Hay
        An instance of the Hay class.
    """
    return Hay()


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
    return HarvestedCrop(category=category, type=crop_type, **sample_crop_data)  # type: ignore[arg-type]


def test_acceptable_crops(hay: Hay) -> None:
    """Tests that Hay's acceptable crops are initialized correctly."""
    assert hay.acceptable_crops == [
        CropCategory.ALFALFA,
        CropCategory.GRASS,
        CropCategory.SMALL_GRAIN,
    ]


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
def test_process_degradations(
    hay: Hay,
    harvested_crop: HarvestedCrop,
    mocker: MockerFixture,
    days: int,
    fresh_mass: float,
    moisture: float,
    expected_loss: float,
) -> None:
    """Tests process_degradations in Hay."""
    expected_info_map = {
        "class": hay.__class__.__name__,
        "function": hay.process_degradations.__name__,
        "units": MeasurementUnits.KILOGRAMS,
    }
    harvested_crop.initial_dry_matter_percentage = 100.0 - moisture
    harvested_crop.initial_dry_matter_mass = (
        fresh_mass * harvested_crop.initial_dry_matter_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION
    )
    harvested_crop.fresh_mass = fresh_mass
    harvested_crop.storage_time = mocker.MagicMock(autospec=Time)
    setattr(harvested_crop.storage_time, "simulation_day", 0)
    harvested_crop.last_time_degraded = mocker.MagicMock(autospec=Time)
    setattr(harvested_crop.last_time_degraded, "simulation_day", 0)
    mock_time = mocker.MagicMock(autospec=Time)
    setattr(mock_time, "simulation_day", days)
    hay.stored = [harvested_crop]
    mock_storage_process_degradations = mocker.patch("RUFAS.routines.feed_storage.storage.Storage.process_degradations")
    mock_add_var = mocker.patch.object(hay.om, "add_variable")
    mock_weather = mocker.MagicMock()

    hay.process_degradations(mock_weather, mock_time)

    mock_add_var.assert_called_once_with("total_moisture_loss", expected_loss, expected_info_map)
    assert harvested_crop.fresh_mass == fresh_mass - expected_loss
    mock_storage_process_degradations.assert_called_once_with(mock_weather, mock_time)


@pytest.mark.parametrize("stored_day,current_day,expect_loss", [(1, 1, False), (1, 10, True)])
def test_calculate_dry_matter_loss_to_gas(
    hay: Hay, harvested_crop: HarvestedCrop, mocker: MockerFixture, stored_day: int, current_day: int, expect_loss: bool
) -> None:
    """Tests calculate_dry_matter_loss_to_gas in Hay."""
    mock_storage_time = mocker.MagicMock(autospec=Time)
    mock_storage_time.simulation_day = stored_day
    harvested_crop.storage_time = mock_storage_time
    mock_current_time = mocker.MagicMock(autospec=Time)
    mock_current_time.simulation_day = current_day
    mock_initial_loss = mocker.patch.object(hay, "_calculate_initial_dry_matter_loss_to_gas", side_effect=[10.0, 20.0])
    mock_subsequent_loss = mocker.patch.object(
        hay, "_calculate_subsequent_dry_matter_loss_to_gas", side_effect=[5.0, 10.0]
    )
    mock_additional_loss = mocker.patch.object(hay, "_calculate_additional_dry_matter_loss", return_value=3.0)
    expected_loss = 18.0 if expect_loss else 0.0
    expected_call_count = 2 if expect_loss else 0

    actual = hay.calculate_dry_matter_loss_to_gas(harvested_crop, [], mock_current_time)

    assert actual == expected_loss
    assert mock_initial_loss.call_count == expected_call_count
    assert mock_subsequent_loss.call_count == expected_call_count
    assert mock_additional_loss.call_count == (1 if expect_loss else 0)


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
    hay: Hay, mocker: MockerFixture, harvested_crop: HarvestedCrop, days: int, expected: float
) -> None:
    """Tests _calculate_initial_dry_matter_loss in Hay."""
    harvested_crop.storage_time = mocker.MagicMock(autospec=Time)
    harvested_crop.storage_time.simulation_day = 1
    harvested_crop.initial_dry_matter_percentage = 20.0
    harvested_crop.initial_dry_matter_mass = 1_000.0
    harvested_crop.total_sensible_heat_generated = 500.0
    mock_time = mocker.MagicMock(autospec=Time)
    mock_time.simulation_day = days + 1

    actual = hay._calculate_initial_dry_matter_loss_to_gas(harvested_crop, mock_time)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize("days,expected", [(15, 0.0), (30, 0.0), (31, 0.0001), (35, 0.0005), (130, 0.01)])
def test_calculate_subsequent_dry_matter_loss(
    hay: Hay, mocker: MockerFixture, harvested_crop: HarvestedCrop, days: int, expected: float
) -> None:
    """Tests _calculate_subsequent_dry_matter_loss in Hay."""
    harvested_crop.storage_time = mocker.MagicMock(autospec=Time)
    harvested_crop.storage_time.simulation_day = 1
    mock_time = mocker.MagicMock(autospec=Time)
    mock_time.simulation_day = days + 1

    actual = hay._calculate_subsequent_dry_matter_loss_to_gas(harvested_crop, mock_time)

    assert actual == expected


@pytest.mark.parametrize(
    "loss_coeff,rain,max_temp,min_temp,density,size,expected",
    [
        (0.0, [], [], [], 200.0, 1.2, 0.0),
        (0.000_01, [0.0, 10.0, 4.5], [18.0, 17.0, 18.0], [15.0, 11.0, 12.0], 215.0, 1.5, 0.000_003_257_267),
        (0.000_02, [0.0, 0.0, 3.2], [6.0, 3.0, 1.0], [2.0, -10.0, -3.0], 300.0, 1.9, 0.0),
    ],
)
def test_calculate_additional_dry_matter_loss(
    hay: Hay,
    mocker: MockerFixture,
    harvested_crop: HarvestedCrop,
    loss_coeff: float,
    rain: list[float],
    max_temp: list[float],
    min_temp: list[float],
    density: float,
    size: float,
    expected: float,
) -> None:
    """Tests _calculate_additional_dry_matter_loss in Hay."""
    mock_conditions = []
    for i in range(len(rain)):
        mock_conditions.append(mocker.MagicMock(autospec=CurrentDayConditions))
        mock_conditions[i].rainfall = rain[i]
        mock_conditions[i].max_air_temperature = max_temp[i]
        mock_conditions[i].min_air_temperature = min_temp[i]
    hay.additional_dry_matter_loss_coefficient = loss_coeff
    mocker.patch.object(Hay, "bale_size", new_callable=mocker.PropertyMock, return_value=size)
    harvested_crop.bale_density = density

    actual = hay._calculate_additional_dry_matter_loss(harvested_crop, mock_conditions)

    assert pytest.approx(actual) == expected


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
    hay: Hay, mocker: MockerFixture, harvested_crop: HarvestedCrop, days: int, initial_moisture: float, expected: float
) -> None:
    """Tests that moisture losses from a hayed crop are calculated correctly."""
    harvested_crop.storage_time = mocker.MagicMock(autospec=Time)
    harvested_crop.storage_time.simulation_day = 1
    harvested_crop.initial_dry_matter_percentage = 100.0 - initial_moisture
    harvested_crop.initial_dry_matter_mass = 400.0
    mock_time = mocker.MagicMock(autospec=Time)
    mock_time.simulation_day = days + 1

    actual = hay._calculate_moisture_loss(harvested_crop, mock_time)

    assert actual == expected


def test_protected_wrapped_init() -> None:
    """Tests that ProtectedWrapped hay instances are initialized correctly."""
    protected_wrapped = ProtectedWrapped()
    assert protected_wrapped.additional_dry_matter_loss_coefficient == PROTECTED_WRAPPED_ADDITIONAL_LOSS_COEFFICIENT


def test_protected_tarped_init() -> None:
    """Tests that ProtectedTarped hay instances are initialized correctly."""
    protected_tarped = ProtectedTarped()
    assert protected_tarped.additional_dry_matter_loss_coefficient == PROTECTED_TARPED_ADDITIONAL_LOSS_COEFFICIENT


def test_outdoor_unprotected_init() -> None:
    """Tests that Unprotected hay instances are initialized correctly."""
    unprotected = Unprotected()
    assert unprotected.additional_dry_matter_loss_coefficient == UNPROTECTED_OUTDOOR_ADDITIONAL_LOSS_COEFFICIENT
