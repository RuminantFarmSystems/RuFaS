import pytest
from pytest_mock import MockerFixture

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import CropCategory, CropType, HarvestedCrop
from RUFAS.input_manager import InputManager
from RUFAS.routines.feed_storage.hay import (
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


def test_process_degradations(
    hay: Hay,
    harvested_crop: HarvestedCrop,
    mocker: MockerFixture,
) -> None:
    """Tests process_degradations in Hay."""
    mock_time = mocker.MagicMock(autospec=RufasTime)
    hay.stored = [harvested_crop]
    mock_moisture_loss = mocker.patch.object(hay, "_process_moisture_loss")
    mock_storage_process_degradations = mocker.patch("RUFAS.routines.feed_storage.storage.Storage.process_degradations")
    mock_weather = mocker.MagicMock()

    hay.process_degradations(mock_weather, mock_time)

    assert hay.crude_protein_loss_coefficient == 0.04
    mock_moisture_loss.assert_called_once_with(mock_time, INITIAL_LOSS_PERIOD, FINAL_MOISTURE_PERCENTAGE)
    mock_storage_process_degradations.assert_called_once_with(mock_weather, mock_time)


@pytest.mark.parametrize("stored_day,current_day,expect_loss", [(1, 1, False), (1, 10, True)])
def test_calculate_dry_matter_loss_to_gas(
    hay: Hay, harvested_crop: HarvestedCrop, mocker: MockerFixture, stored_day: int, current_day: int, expect_loss: bool
) -> None:
    """Tests calculate_dry_matter_loss_to_gas in Hay."""
    mock_storage_time = mocker.MagicMock(autospec=RufasTime)
    mock_storage_time.simulation_day = stored_day
    harvested_crop.storage_time = mock_storage_time
    mock_current_time = mocker.MagicMock(autospec=RufasTime)
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
    harvested_crop.storage_time = mocker.MagicMock(autospec=RufasTime)
    setattr(harvested_crop.storage_time, "simulation_day", 1)
    harvested_crop.initial_dry_matter_percentage = 20.0
    harvested_crop.initial_dry_matter_mass = 1_000.0
    harvested_crop.total_sensible_heat_generated = 500.0
    mock_time = mocker.MagicMock(autospec=RufasTime)
    mock_time.simulation_day = days + 1

    actual = hay._calculate_initial_dry_matter_loss_to_gas(harvested_crop, mock_time)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize("days,expected", [(15, 0.0), (30, 0.0), (31, 0.0001), (35, 0.0005), (130, 0.01)])
def test_calculate_subsequent_dry_matter_loss(
    hay: Hay, mocker: MockerFixture, harvested_crop: HarvestedCrop, days: int, expected: float
) -> None:
    """Tests _calculate_subsequent_dry_matter_loss in Hay."""
    harvested_crop.storage_time = mocker.MagicMock(autospec=RufasTime)
    setattr(harvested_crop.storage_time, "simulation_day", 1)
    mock_time = mocker.MagicMock(autospec=RufasTime)
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
    im = InputManager()
    mocker.patch.object(im, "get_data", return_value=size)
    hay = Hay()
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
