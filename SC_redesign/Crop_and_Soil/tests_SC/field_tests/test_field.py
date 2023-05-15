from typing import Optional, List, Dict
from unittest.mock import MagicMock
import pytest
from SC_redesign.Crop_and_Soil.crop.crop import Crop
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from SC_redesign.Crop_and_Soil.crop.species_data_factory import CropSpecies
from SC_redesign.Crop_and_Soil.field.field import Field
from SC_redesign.Crop_and_Soil.field.field_data import FieldData
from SC_redesign.Crop_and_Soil.crop_and_soil_constants import LITERS_TO_CUBIC_MILLIMETERS, \
    HECTARES_TO_SQUARE_MILLIMETERS


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


@pytest.mark.parametrize("config_list,coverages", [
    ([{"species": "corn"}], None),
    ([{"species": "alfalfa", "minimum_temperature": -2.0}, {"species": "triticale"}], None),
    ([{"species": "alfalfa", "minimum_temperature": -2.0}, {"species": "grass"}], None),
    ([{"species": "corn"}, {"species": "alfalfa"}, {"species": "grass"}], [1/3, 1/3, 1/3])
])
def test_plant_crops(config_list: List[Dict], coverages: Optional[List[float]]):
    field = Field()
    field.plant_crops(config_list, coverages)
    assert len(field.crops) == len(config_list)


def test_check_harvest_schedules():
    """ensure that harvest schedules are checked for all crops"""
    field = Field()
    crop1, crop2, crop3 = Crop(), Crop(), Crop()
    crop1.crop_management.check_harvest_schedule = MagicMock()
    crop2.crop_management.check_harvest_schedule = MagicMock()
    crop3.crop_management.check_harvest_schedule = MagicMock()
    field.crops = [crop1, crop2, crop3]
    field.check_harvest_schedules(100, 0)
    crop1.crop_management.check_harvest_schedule.assert_called_once_with(current_day=100, current_year=0)
    crop2.crop_management.check_harvest_schedule.assert_called_once_with(current_day=100, current_year=0)
    crop3.crop_management.check_harvest_schedule.assert_called_once_with(current_day=100, current_year=0)


def test_harvest_scheduled_crops():
    """ensure that crops are harvested when appropriate"""
    field = Field()
    crop1, crop2, crop3 = Crop(CropData(is_harvest_day=True)), Crop(CropData(is_harvest_day=False)), \
        Crop(CropData(is_harvest_day=True))
    crop1.crop_management.manage_harvest = MagicMock()
    crop2.crop_management.manage_harvest = MagicMock()
    crop3.crop_management.manage_harvest = MagicMock()
    field.crops = [crop1, crop2, crop3]
    field.harvest_scheduled_crops()
    crop1.crop_management.manage_harvest.assert_called_once()
    crop2.crop_management.manage_harvest.assert_not_called()
    crop3.crop_management.manage_harvest.assert_called_once()


def test_amend_soil() -> None:
    """Tests that amend_soil() properly calls all the subroutines that add nutrients to the field"""
    field = Field()
    field.soil.phosphorus_cycling.fertilizer.add_fertilizer_phosphorus = MagicMock()
    field.amend_soil()
    field.soil.phosphorus_cycling.fertilizer.add_fertilizer_phosphorus.assert_called_once_with(0)


@pytest.mark.parametrize("rainfall,days_into_interval,water_deficit,watering_occurs", [
    (3.4, 3, 1.5, False),       # No watering because water_occurs is False
    (3.1, 5, 2.3, True),        # No watering because rainfall takes care of watering
    (0.2, 5, 3.6, True),        # Watering occurs because water deficit has not been met
    (0.19, 4, 2.8, True)        # No watering occurs because interval has not been met
])
def test_determine_watering_amount(rainfall: float, days_into_interval: int, water_deficit: float,
                                   watering_occurs: float) -> None:
    """Tests that the correct amount of water to be used to water is field is calculated, and that the counters and
        totals are updated correctly."""
    data = FieldData(watering_amount_in_liters=50_000, watering_interval=5,
                     days_into_watering_interval=days_into_interval)
    data.watering_amount_in_mm = 5.0
    data.watering_occurs = watering_occurs
    data.current_water_deficit = water_deficit
    incorp = Field(field_data=data)

    actual = incorp._determine_watering_amount(rainfall)

    if not watering_occurs:
        assert actual == 0.0
        assert incorp.field_data.days_into_watering_interval == days_into_interval
        assert incorp.field_data.annual_irrigation_water_use_total == 0
    elif days_into_interval == incorp.field_data.watering_interval:
        assert actual == max(0.0, water_deficit - rainfall)
        assert incorp.field_data.days_into_watering_interval == 0
        assert incorp.field_data.current_water_deficit == 5.0
        assert incorp.field_data.annual_irrigation_water_use_total == actual
    else:
        assert actual == 0.0
        assert incorp.field_data.days_into_watering_interval == days_into_interval + 1
        assert incorp.field_data.current_water_deficit == max(0.0, water_deficit - rainfall)
        assert incorp.field_data.annual_irrigation_water_use_total == 0


def test_annual_reset() -> None:
    """Tests that all annual reset subroutines are called properly"""
    field = Field()
    field.soil.data.do_annual_reset = MagicMock()
    field.field_data.perform_annual_field_reset = MagicMock()

    field.perform_annual_reset()

    field.soil.data.do_annual_reset.assert_called_once()
    field.field_data.perform_annual_field_reset.assert_called_once()

# TODO: All field methods need to be tested in future PRs.


# --- Test FieldData methods ---
@pytest.mark.parametrize("liters,area", [
    (100, 2.3),
    (356, 4.556),
    (60, 1.8)
])
def test_liters_to_millimeters(liters: float, area: float) -> None:
    """Tests that the conversion from liters for evenly distributed millimeters is performed correctly."""
    actual = FieldData.convert_liters_to_millimeters(liters, area)
    expected = (liters * LITERS_TO_CUBIC_MILLIMETERS) / (area * HECTARES_TO_SQUARE_MILLIMETERS)
    assert actual == expected
