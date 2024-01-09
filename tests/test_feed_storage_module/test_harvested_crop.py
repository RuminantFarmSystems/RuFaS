import pytest
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
def test_valid_category_type_combinations(
    category: CropCategory, crop_type: CropType
) -> None:
    try:
        HarvestedCrop(category=category, type=crop_type, **sample_crop_data)
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
def test_invalid_category_type_combinations(
    category: CropCategory, crop_type: CropType
) -> None:
    with pytest.raises(ValueError):
        HarvestedCrop(category=category, type=crop_type, **sample_crop_data)


def test_attributes() -> None:
    crop = HarvestedCrop(
        category=CropCategory.SMALL_GRAIN, type=CropType.WHEAT, **sample_crop_data
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
