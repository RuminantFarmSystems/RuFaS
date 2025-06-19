import pytest
from pytest_mock import MockerFixture

from RUFAS.input_manager import InputManager
from RUFAS.routines.feed_storage.baleage import Baleage, INITIAL_LOSS_PERIOD
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import CropCategory, CropType, HarvestedCrop
from RUFAS.rufas_time import RufasTime

from .sample_crop_data import sample_crop_data


@pytest.fixture
def baleage() -> Baleage:
    """
    Pytest fixture to create a Baleage instance for testing.

    Returns
    -------
    Baleage
        An instance of the Baleage class.
    """
    return Baleage()


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


def test_acceptable_crops(baleage: Baleage) -> None:
    """Tests that Baleage has acceptable_crops set correctly."""
    assert baleage.acceptable_crops == [
        CropCategory.ALFALFA,
        CropCategory.GRASS,
        CropCategory.SMALL_GRAIN,
    ]


def test_process_degradations(
    harvested_crop: HarvestedCrop,
    mocker: MockerFixture,
) -> None:
    """Tests process_degradations in Hay."""
    im = InputManager()
    mocker.patch.object(im, "get_data", return_value=45)
    baleage = Baleage()
    mock_time = mocker.MagicMock(autospec=RufasTime)
    baleage.stored = [harvested_crop]
    mock_moisture_loss = mocker.patch.object(baleage, "_process_moisture_loss")
    mock_storage_process_degradations = mocker.patch("RUFAS.routines.feed_storage.storage.Storage.process_degradations")
    mock_weather = mocker.MagicMock()

    baleage.process_degradations(mock_weather, mock_time)

    mock_moisture_loss.assert_called_once_with(mock_time, INITIAL_LOSS_PERIOD, 45)
    mock_storage_process_degradations.assert_called_once_with(mock_weather, mock_time)
