import warnings
from unittest.mock import MagicMock
import pytest
from SC_redesign.Crop_and_Soil.crop.crop import Crop
from SC_redesign.Crop_and_Soil.crop.species_data_factory import CropSpeciesDataFactory, CropSpecies
from SC_redesign.Crop_and_Soil.field.field import Field


@pytest.mark.parametrize("daylength,threshold_daylength", [
    (14, 8),
    (17.20948239, 9.19183294),
    (7.293485893, 8.234850920),
])
def test_start_dormancy(daylength: float, threshold_daylength: float) -> None:
    """Tests that each crop's dormancy method is called"""
    # Initialize objects
    crop = Crop()
    field = Field()
    field.field_data.dormancy_threshold_daylength = threshold_daylength
    field.crops = [crop]

    # Mock functions used
    crop.dormancy.enter_dormancy = MagicMock()

    # Run method being tested
    field.assess_dormancy(daylength)

    # Check that subroutines were called correct number of times
    if daylength <= threshold_daylength:
        assert crop.dormancy.enter_dormancy.call_count == 1


@pytest.mark.parametrize("species,specs", [
    ("corn", {}),  # no additional arguments
    ("alfalfa", {"minimum_temperature": -2.1, "id": 123})  # supported species, with alteration
])
def test_make_supported_crop(species: str, specs: dict):
    """ensure that supported crops are properly created."""
    # check that attributes are correct
    crop = Field.make_supported_crop(species, **specs)
    assert crop.data.species == species
    for key, val in specs.items():
        assert getattr(crop.data, key) == val

    if len(specs) > 0:
        assert "altered" in crop.data.name
    else:
        assert "default" in crop.data.name

    # failing cases
    with pytest.raises(Exception):
        Field.make_supported_crop("fake_crop")
    with pytest.raises(Exception):
        Field.make_supported_crop("corn", bad_attr=17.35)


@pytest.mark.parametrize("config", [
    {"species": "grass"},  # custom species, with generic defaults
    {"species": "cottonwood", "is_perennial": True},  # custom species and attribute
    {"minimum_temperature": -10},  # no species name
])
def test_make_custom_crop(config: dict):
    """checks that custom crop attributes are set correctly"""
    crop = Field.make_custom_crop(**config)
    for key, val in config.items():
        assert getattr(crop.data, key) == val


def test_add_crop():
    """checks that crops are added to the field properly"""
    field = Field()

    # --- first case: no cover specification ----
    for i in range(5):
        crop = Crop()
        field.add_crop(crop)
        assert type(field.crops[i]) is Crop
    for crop in field.crops:
        assert crop.data.field_proportion == 1/5
    assert len(field.crops) == 5

    # ---- second case: specific covers
    new_field = Field()
    new_field.add_crop(Crop(), 0.10)
    new_field.add_crop(Crop(), 0.20)
    new_field.add_crop(Crop(), 0.33)
    assert new_field.crops[0].data.field_proportion == 0.10
    assert new_field.crops[1].data.field_proportion == 0.20
    assert new_field.crops[2].data.field_proportion == 0.33

    # --- failing cases ---
    newer_field = Field()
    with pytest.raises(Exception):
        newer_field.add_crop(Crop(), 1.1)  # over 1
        new_field.add_crop(Crop(), 0.5)  # total is over 1


@pytest.mark.parametrize("config", [
    {"species": "corn"},  # supported species
    {"species": "corn", "minimum_temperature": -2.0, "is_perennial": True},  # supported species, with alterations
    {"species": "grass"},  # unsupported species, generic attributes
    {"species": "cottonwood", "is_perennial": True},  # custom species and attributes
    {"minimum_temperature": -2.0},  # generic custom crop, with alterations
])
def test_make_crop_from_config_dict(config: dict):
    supported_crops = set(item.value for item in CropSpecies)
    has_supported_species = "species" in config.keys() and str(config["species"]) in supported_crops
    Field.make_supported_crop = MagicMock()
    Field.make_custom_crop = MagicMock()

    Field.make_crop_from_config_dict(config)

    if has_supported_species:
        Field.make_supported_crop.assert_called_once()
        Field.make_custom_crop.assert_not_called()
    else:
        Field.make_supported_crop.assert_not_called()
        Field.make_custom_crop.assert_called_once()



def test_plant_crops():
   assert False

# TODO: All field methods need to be tested in future PRs.
