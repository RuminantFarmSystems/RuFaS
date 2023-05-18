from math import exp
from typing import Optional, List, Dict
from unittest.mock import MagicMock, PropertyMock, patch
import pytest
from SC_redesign.Crop_and_Soil.crop.crop import Crop
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from SC_redesign.Crop_and_Soil.crop.species_data_factory import CropSpecies
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
        assert crop.data.field_proportion == 1 / 5
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
    ([{"species": "corn"}, {"species": "alfalfa"}, {"species": "grass"}], [1 / 3, 1 / 3, 1 / 3])
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


@pytest.mark.parametrize("precipitation,canopy_capacity,first_canopy_amount,second_canopy_amount,expected_return,"
                         "expected_first,expected_second", [
                             (13, 8, 2, 4, 3, 8, 8),  # Fills both pools with some leftover
                             (6, 7, 3, 2, 0, 7, 4),  # Fills one pool, puts some in second, none leftover
                             (14, 5, 7, 1, 12, 5, 5),  # Removes from one pool, fills other, some leftover
                             (3, 6, 8, 9, 8, 6, 6),  # Removes from both pools, lots left over
                             (5, 10, 3, 12, 2, 8, 10)  # Fills one pool as much as possible, removes excess from
                             # another
                         ]
                         )
def test_handle_water_in_crop_canopies(precipitation: float, canopy_capacity: float, first_canopy_amount: float,
                                       second_canopy_amount: float, expected_return: float, expected_first: float,
                                       expected_second: float) -> None:
    """Tests that water is properly added and removed from the crop canopies of field objects."""
    with patch("SC_redesign.Crop_and_Soil.crop.crop_data.CropData.water_canopy_storage_capacity",
               new_callable=PropertyMock, return_value=canopy_capacity):
        crop_data1 = CropData(canopy_water=first_canopy_amount)
        crop1 = Crop(crop_data1)
        crop_data2 = CropData(canopy_water=second_canopy_amount)
        crop2 = Crop(crop_data2)
        field = Field()
        field.crops = [crop1, crop2]

        actual = field._handle_water_in_crop_canopies(precipitation)
        assert actual == expected_return
        assert field.crops[0].data.canopy_water == expected_first
        assert field.crops[1].data.canopy_water == expected_second


@pytest.mark.parametrize("demand,canopy_water_1,canopy_water_2,expected_demand,expected_canopy_water1,"
                         "expected_canopy_water2", [
                             (14.5, 1.8, 2.3, 10.4, 0.0, 0.0),
                             (8.6, 4.7, 4.1, 0.0, 0.0, 0.2),
                             (9.5, 10.8, 5.7, 0.0, 1.3, 5.7)
                         ])
def test_evaporate_from_crop_canopies(demand: float, canopy_water_1: float, canopy_water_2: float,
                                      expected_demand: float, expected_canopy_water1: float,
                                      expected_canopy_water2: float) -> None:
    """Tests that the evapotranspirative demand is correctly reduced by the amounts of water evaporated."""
    data1 = CropData(canopy_water=canopy_water_1)
    crop1 = Crop(data1)
    data2 = CropData(canopy_water=canopy_water_2)
    crop2 = Crop(data2)
    field = Field()
    field.crops = [crop1, crop2]

    actual_demand = field._evaporate_from_crop_canopies(demand)
    assert pytest.approx(actual_demand) == expected_demand
    assert pytest.approx(expected_canopy_water1) == field.crops[0].data.canopy_water
    assert pytest.approx(expected_canopy_water2) == field.crops[1].data.canopy_water


@pytest.mark.parametrize("extraterrestrial_radiation,max_temp,min_temp,avg_temp", [
    (100, 28, 10, 14),
    (568, 20, 14, 18),
    (568, 20, 14, None),
    (80, 14, 0, 8),
    (678.0098, 26.8896, 10.3339, 18.3345),
])
def test_potential_evapotranspiration(extraterrestrial_radiation, max_temp, min_temp, avg_temp):
    with patch("SC_redesign.Crop_and_Soil.field.field.Field._determine_latent_heat_vaporization",
               new_callable=MagicMock, return_value=1.3) as mocked_latent_heat:
        actual = Field._determine_potential_evapotranspiration(extraterrestrial_radiation, max_temp, min_temp, avg_temp)
        if avg_temp is not None:
            expect = (0.0023 * extraterrestrial_radiation * ((max_temp - min_temp) ** (-0.5)) *
                      (avg_temp + 17.8)) / 1.3
        else:
            expect = (0.0023 * extraterrestrial_radiation * ((max_temp - min_temp) ** (-0.5)) *
                      (((max_temp + min_temp) / 2) + 17.8)) / 1.3

        if avg_temp is not None:
            mocked_latent_heat.assert_called_once_with(avg_temp)
        else:
            mocked_latent_heat.assert_called_once_with((max_temp + min_temp) / 2)
        assert actual == expect


@pytest.mark.parametrize("avg_temp", [
    12.86878,
    0,
    (-2.586948),
    20.4486,
])
def test_determine_latent_heat_vaporization(avg_temp):
    observe = Field._determine_latent_heat_vaporization(avg_temp)
    expect = 2.501 - (0.002361 * avg_temp)
    assert expect == observe


@pytest.mark.parametrize("above_ground_biomass,residue,snow_water,potential_evapotrans_adj, transpiration", [
    (800, 40, 0.3, 1.6, 0.9),  # arbitrary
    (1200, 300, 0.433, 2.4, 1.8),  # arbitrary
    (0, 800, 0.03, 0, 3.6),  # after harvest
    (800, 56, 0.84, 0.44, 0.23),  # snowy
    (0, 0, 0.22, 0.69, 0.45),  # empty field
    (400, 150, 0, 0.01, 0),  # dry conditions
    (500, 200, 0, 6.3, 4.5),  # wet conditions
])
def test_determine_soil_evaporation_and_sublimation_adjusted(above_ground_biomass: float, residue: float,
                                                             snow_water: float, potential_evapotrans_adj: float,
                                                             transpiration: float) -> None:
    """Tests that the amount of soil evaporation and sublimation is calculated correctly."""
    with patch("SC_redesign.Crop_and_Soil.field.field.Field._determine_soil_cover_index", new_callable=MagicMock,
               return_value=1.3) as mocked_soil_cover_index:
        actual = Field._determine_soil_evaporation_and_sublimation_adjusted(above_ground_biomass, residue, snow_water,
                                                                            potential_evapotrans_adj, transpiration)
        soil_evaporation = potential_evapotrans_adj * 1.3
        reduced_soil_evaporation = (soil_evaporation * potential_evapotrans_adj) / (soil_evaporation + transpiration)
        expected = min(soil_evaporation, reduced_soil_evaporation)

        mocked_soil_cover_index.assert_called_once_with(above_ground_biomass, residue, snow_water)
        assert actual == expected


@pytest.mark.parametrize("above_ground_biomass,residue,snow_water", [
    (400, 65, 0.3),
    (800, 120, 0),
    (0, 0, 0),
    (1250, 800, 0.4999),
    (990, 200, 0.338),
    (400, 30, 0.51),
])
def test_determine_soil_cover_index(above_ground_biomass: float, residue: float, snow_water: float) -> None:
    """Tests that the soil cover index is correctly calculated."""
    if snow_water > 0.5:
        expect = 0.5
    else:
        expect = exp((-0.00005) * (above_ground_biomass + residue))
    observe = Field._determine_soil_cover_index(above_ground_biomass, residue, snow_water)
    assert expect == observe


@pytest.mark.parametrize("soil_evaporation_adj,snow_water_content", [
    (1.3, 3.2),
    (0, 0),
    (1.3, 0.4),
    (1.8954, 0)
])
def test_determine_maximum_soil_evaporation(soil_evaporation_adj, snow_water_content):
    observe = Field._determine_maximum_soil_evaporation(soil_evaporation_adj, snow_water_content)
    if snow_water_content > soil_evaporation_adj:
        assert 0 == observe
    else:
        assert (soil_evaporation_adj - snow_water_content) == observe


def test_annual_reset() -> None:
    """Tests that all annual reset subroutines are called properly"""
    field = Field()
    field.soil.data.do_annual_reset = MagicMock()
    field.perform_annual_reset()
    field.soil.data.do_annual_reset.assert_called_once()

# TODO: All field methods need to be tested in future PRs.
