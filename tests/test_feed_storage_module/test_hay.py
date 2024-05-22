import pytest
from pytest_mock import MockerFixture
from RUFAS.time import Time
from RUFAS.routines.feed_storage.harvested_crop import HarvestedCrop
from RUFAS.routines.feed_storage.hay import Hay
from RUFAS.routines.feed_storage.enums import CropCategory, CropType
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
    assert hay.acceptable_crops == [
        CropCategory.ALFALFA,
        CropCategory.GRASS,
        CropCategory.SMALL_GRAIN,
    ]


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
    expected_loss = 15.0 if expect_loss else 0.0
    expected_call_count = 2 if expect_loss else 0

    actual = hay.calculate_dry_matter_loss_to_gas(harvested_crop, [], mock_current_time)

    assert actual == expected_loss
    assert mock_initial_loss.call_count == expected_call_count
    assert mock_subsequent_loss.call_count == expected_call_count


@pytest.mark.parametrize(
    "days,expected",
    [
        (0, 0.0),
        (1, 950.665050408),
        (10, 950.670114831),
        (20, 950.676225724),
        (30, 950.682926336),
        (40, 950.682926336),
        (100, 950.682926336),
    ],
)
def test_calculate_initial_dry_matter_loss(
    hay: Hay, mocker: MockerFixture, harvested_crop: HarvestedCrop, days: int, expected: float
) -> None:
    """Tests _calculate_initial_dry_matter_loss in Hay."""
    harvested_crop.storage_time = mocker.MagicMock(autospec=Time)
    harvested_crop.storage_time.simulation_day = 1
    harvested_crop.initial_dry_matter_percentage = 20.0
    harvested_crop.total_sensible_heat_generated = 950.0
    mock_time = mocker.MagicMock(autospec=Time)
    mock_time.simulation_day = days + 1

    actual = hay._calculate_initial_dry_matter_loss_to_gas(harvested_crop, mock_time)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize("days,expected", [(15, 0.0), (30, 0.0), (1, 0.0001), (5, 0.0005), (100, 0.001)])
def test_calculate_subsequent_dry_matter_loss(
    hay: Hay, mocker: MockerFixture, harvested_crop: HarvestedCrop, days: int, expected: float
) -> None:
    """Tests _calculate_subsequent_dry_matter_loss in Hay."""
    harvested_crop.storage_time = mocker.MagicMock(autospec=Time)
    harvested_crop.storage_time.simulation_day = 1
    harvested_crop.initial_dry_matter_percentage = 20.0
    harvested_crop.total_sensible_heat_generated = 950.0
    mock_time = mocker.MagicMock(autospec=Time)
    mock_time.simulation_day = days + 1
