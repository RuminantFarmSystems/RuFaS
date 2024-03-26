import pytest
from pytest_mock import MockerFixture
import copy
from RUFAS.time import Time
from RUFAS.routines.feed_storage.harvested_crop import HarvestedCrop
from RUFAS.routines.feed_storage.enums import CropCategory, CropType
from RUFAS.output_manager import OutputManager
from .sample_crop_data import sample_crop_data

om = OutputManager()


@pytest.mark.parametrize(
    "category, crop_type",
    [
        (CropCategory.SMALL_GRAIN, CropType.WHEAT),
        (CropCategory.SMALL_GRAIN, CropType.RYE),
        (CropCategory.SMALL_GRAIN, CropType.OAT),
        (CropCategory.SMALL_GRAIN, CropType.RICE),
        (CropCategory.CORN, CropType.HIGH_MOISTURE),
        (CropCategory.CORN, CropType.SILAGE),
        (CropCategory.CORN, CropType.WHOLE_PLANT),
        (CropCategory.CORN, CropType.GRAIN),
        (CropCategory.SOY, CropType.FORAGE),
        (CropCategory.SOY, CropType.GRAIN),
        (CropCategory.ALFALFA, CropType.ALFALFA),
        (CropCategory.GRASS, CropType.RYEGRASS),
        (CropCategory.GRASS, CropType.ORCHARDGRASS),
        (CropCategory.GRASS, CropType.FINE_FESCUE),
        (CropCategory.GRASS, CropType.TALL_FESCUE),
        (CropCategory.GRASS, CropType.MEADOW_FESCUE),
    ],
)
def test_valid_category_type_combinations(category: CropCategory, crop_type: CropType) -> None:
    try:
        HarvestedCrop(category=category, type=crop_type, **sample_crop_data)  # type: ignore[arg-type]
    except ValueError:
        pytest.fail(f"Unexpected ValueError with {category} and {crop_type}")


@pytest.mark.parametrize(
    "category, crop_type",
    [
        (CropCategory.CORN, CropType.WHEAT),
        (CropCategory.ALFALFA, CropType.SILAGE),
        (CropCategory.GRASS, CropType.RICE),
        (CropCategory.SOY, CropType.HIGH_MOISTURE),
    ],
)
def test_invalid_category_type_combinations(category: CropCategory, crop_type: CropType) -> None:
    with pytest.raises(ValueError):
        HarvestedCrop(category=category, type=crop_type, **sample_crop_data)  # type: ignore[arg-type]


def test_attributes() -> None:
    crop = HarvestedCrop(
        category=CropCategory.SMALL_GRAIN, type=CropType.WHEAT, **sample_crop_data  # type: ignore[arg-type]
    )
    assert crop.fresh_mass == sample_crop_data["fresh_mass"]
    assert crop.dry_matter_percentage == sample_crop_data["dry_matter_percentage"]
    assert crop.dry_matter_digestibility == sample_crop_data["dry_matter_digestibility"]
    assert crop.crude_protein_percent == sample_crop_data["crude_protein_percent"]
    assert crop.non_protein_nitrogen == sample_crop_data["non_protein_nitrogen"]
    assert crop.starch == sample_crop_data["starch"]
    assert crop.adf == sample_crop_data["adf"]
    assert crop.ndf == sample_crop_data["ndf"]
    assert crop.lignin == sample_crop_data["lignin"]
    assert crop.sugar == sample_crop_data["sugar"]
    assert crop.ash == sample_crop_data["ash"]
    assert crop.stored_fresh_mass == sample_crop_data["fresh_mass"]
    assert crop.stored_dry_matter_percentage == sample_crop_data["dry_matter_percentage"]


@pytest.mark.parametrize(
    "mass,percentage,expected",
    [
        (100.0, 25.0, 25.0),
        (230.0, 22.0, 50.6),
        (145.0, 100.0, 145.0),
        (20.4, 0.0, 0.0),
        (0.0, 0.0, 0.0),
    ],
)
def test_dry_matter_mass(mass: float, percentage: float, expected: float) -> None:
    """Test dry_matter_mass property in Harvested Crop."""
    crop_data = copy.deepcopy(sample_crop_data)
    crop_data["fresh_mass"] = mass
    crop_data["dry_matter_percentage"] = percentage
    crop = HarvestedCrop(category=CropCategory.SMALL_GRAIN, type=CropType.WHEAT, **crop_data)  # type: ignore[arg-type]

    actual = crop.dry_matter_mass

    assert actual == expected


@pytest.mark.parametrize(
    "current,stored,expected",
    [
        (10, 10, 0),
        (100, 40, 60),
    ],
)
def test_days_stored(mocker: MockerFixture, current: int, stored: int, expected: int) -> None:
    """Tests the days_stored method in HarvestedCrop class."""
    mock_current_time = mocker.MagicMock(autospec=Time)
    setattr(mock_current_time, "index", current)
    mock_stored_time = mocker.MagicMock(autospec=Time)
    setattr(mock_stored_time, "index", stored)
    crop = HarvestedCrop(
        category=CropCategory.SMALL_GRAIN, type=CropType.WHEAT, **sample_crop_data  # type: ignore[arg-type]
    )
    crop.storage_time = mock_stored_time

    actual = crop.days_stored(mock_current_time)

    assert actual == expected


def test_error_days_stored(mocker: MockerFixture) -> None:
    """Tests that days_stored method in HarvestedCrop class handles error case."""
    mock_add_error = mocker.patch.object(om, "add_error")
    mock_current_time = mocker.MagicMock(autospec=Time)
    setattr(mock_current_time, "index", 1)
    mock_stored_time = mocker.MagicMock(autospec=Time)
    setattr(mock_stored_time, "index", 2)
    crop = HarvestedCrop(
        category=CropCategory.SMALL_GRAIN, type=CropType.WHEAT, **sample_crop_data  # type: ignore[arg-type]
    )
    crop.storage_time = mock_stored_time

    with pytest.raises(ValueError):
        crop.days_stored(mock_current_time)

    mock_add_error.assert_called_once()
