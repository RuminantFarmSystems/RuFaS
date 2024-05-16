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


def test_acceptable_crops(hay: Hay):
    assert hay.acceptable_crops == [
        CropCategory.ALFALFA,
        CropCategory.GRASS,
        CropCategory.SMALL_GRAIN,
    ]


@pytest.mark.parametrize("stored_day,current_day,expect_loss", [(1, 1, False), (1, 10, True)])
def test_calculate_dry_matter_loss_to_gas(hay: Hay, harvested_crop: HarvestedCrop, mocker: MockerFixture, stored_day: int, current_day: int, expect_loss: bool) -> None:
    """Tests calculate_dry_matter_loss_to_gas in Hay."""
    mock_storage_time = mocker.MagicMock(autospec=Time)
    mock_storage_time.simulation_day = stored_day
    harvested_crop.storage_time = mock_storage_time
    mock_current_time = mocker.MagicMock(autospec=Time)
    mock_current_time.simulation_day = current_day
    mock_initial_loss = mocker.patch.object(hay, "_calculate_initial_dry_matter_loss_to_gas", return_value=20.0)
    mock_subsequent_loss = mocker.patch.object(hay, "_calculate_subsequent_dry_matter_loss_to_gas", return_value=10.0)
    expected_loss = (30.0 if expect_loss else 0.0)
    expected_call_count = (1 if expect_loss else 0)

    actual = hay.calculate_dry_matter_loss_to_gas(harvested_crop, [], mock_current_time)

    assert actual == expected_loss
    assert mock_initial_loss.call_count == expected_call_count
    assert mock_subsequent_loss.call_count == expected_call_count
