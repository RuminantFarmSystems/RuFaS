import pytest
from pytest_mock import MockerFixture

from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.crop.phosphorus_uptake import PhosphorusUptake
from RUFAS.routines.field.soil.soil_data import SoilData
from tests.soil_crop_tests.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


@pytest.fixture
def mock_crop_data() -> CropData:
    return CropData(**SAMPLE_CROP_CONFIGURATION)


def test_uptake(mocker: MockerFixture, mock_crop_data: CropData) -> None:
    """Check that uptake() correctly called functions and variables were updated as expected."""
    uptake = PhosphorusUptake(mock_crop_data)
    soil = SoilData(field_size=10)
    mock_main_uptake = mocker.patch.object(uptake, "uptake_main_process")
    mock_determine_stored = mocker.patch.object(uptake, "determine_stored_nutrient", return_value=1)

    uptake.uptake(soil)

    mock_main_uptake.assert_called_once()
    mock_determine_stored.assert_called_once()
    assert mock_crop_data.phosphorus == 1
