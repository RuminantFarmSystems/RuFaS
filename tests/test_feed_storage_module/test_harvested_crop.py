import pytest
from pytest_mock import MockerFixture
import copy
from RUFAS.routines.feed_storage.harvested_crop import HarvestedCrop
from RUFAS.routines.feed_storage.enums import CropCategory, CropType
from .sample_crop_data import sample_crop_data


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


def test_attributes(mocker: MockerFixture) -> None:
    mock_effluent = mocker.patch.object(HarvestedCrop, "_estimate_maximum_effluent", return_value=10.0)
    mock_deepcopy = mocker.patch("RUFAS.routines.feed_storage.harvested_crop.deepcopy")
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
    assert crop.estimated_maximum_effluent == 10.0
    mock_effluent.assert_called_once()
    mock_deepcopy.assert_called_once_with(crop.storage_time)


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


@pytest.mark.parametrize("dry_matter,mass,expected", ((30.0, 100.0, 0.0), (15.0, 200.0, 30.0), (35.0, 150.0, 0.0)))
def test_estimate_maximum_effluent(dry_matter: float, mass: float, expected: float) -> None:
    """Tests _estimate_maximum_effluent in HarvestedCrop."""
    crop = HarvestedCrop(
        category=CropCategory.SMALL_GRAIN, type=CropType.WHEAT, **sample_crop_data  # type: ignore[arg-type]
    )
    crop.dry_matter_percentage = dry_matter
    crop.fresh_mass = mass

    actual = crop._estimate_maximum_effluent()

    assert pytest.approx(actual) == expected
