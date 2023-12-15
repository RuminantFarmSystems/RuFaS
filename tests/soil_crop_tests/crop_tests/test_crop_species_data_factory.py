import pytest
from RUFAS.routines.field.crop.species_data_factory import CropSpecies, CropSpeciesDataFactory
from RUFAS.routines.field.crop.crop_data import PlantCategory
from dataclasses import asdict


@pytest.mark.parametrize("species,expected", [
    ("alfalfa_hay", CropSpecies.ALFALFA_HAY),
    ("alfalfa_silage", CropSpecies.ALFALFA_SILAGE),
    ("alfalfa_baleage", CropSpecies.ALFALFA_BALEAGE),
    ("cereal_rye_hay", CropSpecies.CEREAL_RYE_HAY),
    ("cereal_rye_grain", CropSpecies.CEREAL_RYE_GRAIN),
    ("cereal_rye_silage", CropSpecies.CEREAL_RYE_SILAGE),
    ("cereal_rye_baleage", CropSpecies.CEREAL_RYE_BALEAGE),
    ("corn_grain", CropSpecies.CORN_GRAIN),
    ("corn_silage", CropSpecies.CORN_SILAGE),
    ("soybean_hay", CropSpecies.SOYBEAN_HAY),
    ("soybean_grain", CropSpecies.SOYBEAN_GRAIN),
    ("tall_fescue_hay", CropSpecies.TALL_FESCUE_HAY),
    ("tall_fescue_silage", CropSpecies.TALL_FESCUE_SILAGE),
    ("tall_fescue_baleage", CropSpecies.TALL_FESCUE_BALEAGE),
    ("triticale_hay", CropSpecies.TRITICALE_HAY),
    ("triticale_grain", CropSpecies.TRITICALE_GRAIN),
    ("triticale_silage", CropSpecies.TRITICALE_SILAGE),
    ("triticale_baleage", CropSpecies.TRITICALE_BALEAGE),
    ("winter_wheat_hay", CropSpecies.WINTER_WHEAT_HAY),
    ("winter_wheat_grain", CropSpecies.WINTER_WHEAT_GRAIN),
    ("winter_wheat_silage", CropSpecies.WINTER_WHEAT_SILAGE),
    ("winter_wheat_baleage", CropSpecies.WINTER_WHEAT_BALEAGE)
])
def test_crop_species_enum(species, expected):
    """ensure that CropSpecies correctly enumerates the accepted species names"""
    crop_species = CropSpecies(species)
    assert crop_species == expected


@pytest.mark.parametrize("invalid_species", ["fancy_grass", "regular rye", "soy beans"])
def test_invalid_crop_species_enum(invalid_species):
    """ensure that CropSpecies correctly raises an error when invalid species names are given."""
    with pytest.raises(ValueError) as e:
        CropSpecies(invalid_species)
    assert str(e.value) == f"'{invalid_species}' is not a valid CropSpecies"


def test_species_factory_defaults():
    """Ensure that each species come shipped with their factory-default settings. This is a check of the
    CropSpeciesDataFactory.create_species_data() method.
    """
    # ---- default argument crop ----
    generic = CropSpeciesDataFactory.create_species_data()
    assert generic.species == "corn_grain"
    assert generic.name == "corn grain"
    assert generic.id is None
    assert generic.plant_code == "CORN"
    assert generic.scientific_name == "Zea mays"
    assert generic.plant_category == PlantCategory("warm_annual")
    assert generic.is_nitrogen_fixer is False
    assert generic.minimum_temperature == 8.0
    assert generic.optimal_temperature == 25.0
    assert generic.max_leaf_area_index == 3.0
    assert generic.first_heat_fraction_point == 0.15
    assert generic.first_leaf_fraction_point == 0.05
    assert generic.second_heat_fraction_point == 0.50
    assert generic.second_leaf_fraction_point == 0.95
    assert generic.senescent_heat_fraction == 0.9
    assert generic.light_use_efficiency == 39.0
    assert generic.emergence_nitrogen_fraction == 0.0470
    assert generic.half_mature_nitrogen_fraction == 0.0177
    assert generic.mature_nitrogen_fraction == 0.0138
    assert generic.emergence_phosphorus_fraction == 0.0048
    assert generic.half_mature_phosphorus_fraction == 0.0018
    assert generic.mature_phosphorus_fraction == 0.0014
    assert generic.optimal_harvest_index == 0.6
    assert generic.min_harvest_index == 0.4
    assert generic.yield_nitrogen_fraction == 0.014
    assert generic.yield_phosphorus_fraction == 0.00309

    # check that setting the crop ID works and doesn't trigger the "altered" crop name
    generic_id = CropSpeciesDataFactory.create_species_data(CropSpecies("corn_silage"), id=1530)
    assert generic_id.id == 1530
    assert generic_id.name == "corn silage"

    # ---- winter wheat ----
    winter_wheat = CropSpeciesDataFactory.create_species_data(CropSpecies("winter_wheat_hay"), id=1000)
    assert winter_wheat.species == "winter_wheat_hay"
    assert winter_wheat.name == "winter_wheat hay"
    assert winter_wheat.id == 1000
    assert winter_wheat.plant_code == "WWHT"
    assert winter_wheat.scientific_name == "Triticum aestivum"
    assert winter_wheat.plant_category == PlantCategory("cool_annual")
    assert winter_wheat.is_nitrogen_fixer is False
    assert winter_wheat.minimum_temperature == 0.0
    assert winter_wheat.optimal_temperature == 18.0
    assert winter_wheat.max_leaf_area_index == 4.0
    assert winter_wheat.first_heat_fraction_point == 0.05
    assert winter_wheat.first_leaf_fraction_point == 0.05
    assert winter_wheat.second_heat_fraction_point == 0.45
    assert winter_wheat.second_leaf_fraction_point == 0.95
    assert winter_wheat.senescent_heat_fraction == 0.90
    assert winter_wheat.light_use_efficiency == 30.0
    assert winter_wheat.emergence_nitrogen_fraction == 0.0663
    assert winter_wheat.half_mature_nitrogen_fraction == 0.0255
    assert winter_wheat.mature_nitrogen_fraction == 0.0148
    assert winter_wheat.emergence_phosphorus_fraction == 0.0053
    assert winter_wheat.half_mature_phosphorus_fraction == 0.0020
    assert winter_wheat.mature_phosphorus_fraction == 0.0012
    assert winter_wheat.optimal_harvest_index == 0.85
    assert winter_wheat.min_harvest_index == 0.55
    assert winter_wheat.yield_nitrogen_fraction == 0.0158032
    assert winter_wheat.yield_phosphorus_fraction == 0.00233

    # ---- cereal rye ----
    cereal_rye = CropSpeciesDataFactory.create_species_data(CropSpecies("cereal_rye_baleage"), id=123)
    assert cereal_rye.species == "cereal_rye_baleage"
    assert cereal_rye.name == "cereal_rye baleage"
    assert cereal_rye.id == 123
    assert cereal_rye.plant_code == "RYE"
    assert cereal_rye.scientific_name == "Secale cereale"
    assert cereal_rye.plant_category == PlantCategory("cool_annual")
    assert cereal_rye.is_nitrogen_fixer is False
    assert cereal_rye.minimum_temperature == 0.0
    assert cereal_rye.optimal_temperature == 12.5
    assert cereal_rye.max_leaf_area_index == 4.0
    assert cereal_rye.first_heat_fraction_point == 0.15
    assert cereal_rye.first_leaf_fraction_point == 0.01
    assert cereal_rye.second_heat_fraction_point == 0.50
    assert cereal_rye.second_leaf_fraction_point == 0.95
    assert cereal_rye.senescent_heat_fraction == 0.80
    assert cereal_rye.light_use_efficiency == 35.0
    assert cereal_rye.emergence_nitrogen_fraction == 0.0600
    assert cereal_rye.half_mature_nitrogen_fraction == 0.0231
    assert cereal_rye.mature_nitrogen_fraction == 0.0130
    assert cereal_rye.emergence_phosphorus_fraction == 0.0084
    assert cereal_rye.half_mature_phosphorus_fraction == 0.0032
    assert cereal_rye.mature_phosphorus_fraction == 0.0019
    assert cereal_rye.optimal_harvest_index == 0.90
    assert cereal_rye.min_harvest_index == 0.68
    assert cereal_rye.yield_nitrogen_fraction == 0.0230944
    assert cereal_rye.yield_phosphorus_fraction == 0.00371


@pytest.mark.parametrize("species,vars_dict", [
    ("corn_grain", {"minimum_temperature": -2}),  # reduced temp
    ("corn_silage", {"minimum_temperature": 3, "second_leaf_fraction_point": 0.93}),  # two changes
    ("winter_wheat_silage", {"name": "wheat named Susan"}),  # custom name
    ("winter_wheat_baleage", {"optimal_temperature": 28, "optimal_harvest_index": 0.99,  # 3 changes
                              "min_harvest_index": 0.98}),
    ("cereal_rye_hay", {"biomass": 100}),  # change attribute declared only in CropData
    ("cereal_rye_grain", {"name": "fancy barley",  # custom new variety/subspecies
                          "plant_code": "FBAR", "scientific_name": "Hordeum vulgare regalis"}),
    ("tall_fescue_hay", {"plant_category": PlantCategory("perennial")}),  # perennial version of tall fescue
    ("tall_fescue_silage", {"is_nitrogen_fixer": True}),  # magical nitrogen-fixing grass (egads!)
    ("alfalfa_baleage", {"yield_nitrogen_fraction": 0.03}),  # this alfalfa has increased nitrogen in harvest
    ("soybean_grain", {"max_leaf_area_index": 2.4, "light_use_efficiency": 10.8,  # various alterations
                       "emergence_nitrogen_fraction": 0.06}),
    ("triticale_silage", {"growth_factor": 0.8, "mature_phosphorus_fraction": 0.01}),  # mixed alterations
    ("triticale_grain", {"optimal_harvest_index": 1.2}),  # higher tuber yield
])
def test_factory_alterations(species, vars_dict):
    """check that the factory properly creates 'altered' crop species data objects"""
    # setup crop
    crop = CropSpeciesDataFactory.create_species_data(CropSpecies(species), **vars_dict)
    # check that all altered attributes have been correctly set
    for key, val in vars_dict.items():
        assert getattr(crop, key) == val
    # check that all unaltered attributes are equal to their defaults
    unaltered_attributes = asdict(crop).keys() - vars_dict.keys()  # set difference
    default_crop = CropSpeciesDataFactory.create_species_data(CropSpecies(species))
    for key in unaltered_attributes:
        if key != "name":  # ignore the name attribute here
            assert getattr(crop, key) == getattr(default_crop, key)
    # check that the name has been altered to reflect changes to default class
    if "name" not in vars_dict.keys():
        assert "altered" in crop.name


@pytest.mark.parametrize("species,bad_attr", [
    ("cereal_rye_hay", {"color": "red"}),  # generic
    ("corn_silage", {"flavor": "corny"}),  # child class
    ("alfalfa_hay", {"value": 1000, "is_valuable": True}),  # multiple invalids
    ("soybean_grain", {"name": "Bob", "moustache": True}),  # valid with invalid
])
def test_factory_errors(species, bad_attr):
    """check that specifying invalid attributes appropriately raises an error"""
    with pytest.raises(AttributeError) as e:
        CropSpeciesDataFactory.create_species_data(CropSpecies(species), **bad_attr)
    assert "is not a valid attribute" in str(e.value)
