import pytest
from SC_redesign.Crop_and_Soil.crop.species_data_factory import CropSpecies, CropSpeciesDataFactory
from dataclasses import asdict

@pytest.mark.parametrize("species,expected", [
    ("generic", CropSpecies.GENERIC),
    ("corn", CropSpecies.CORN),
    ("spring_wheat", CropSpecies.SPRING_WHEAT),
    ("winter_wheat", CropSpecies.WINTER_WHEAT),
    ("cereal_rye", CropSpecies.CEREAL_RYE),
    ("spring_barley", CropSpecies.SPRING_BARLEY),
    ("fall_oats", CropSpecies.FALL_OATS),
    ("tall_fescue", CropSpecies.TALL_FESCUE),
    ("alfalfa", CropSpecies.ALFALFA),
    ("soybean", CropSpecies.SOYBEAN),
    ("sugar_beet", CropSpecies.SUGAR_BEET),
    ("potato", CropSpecies.POTATO),
    ("triticale", CropSpecies.TRITICALE),
])
def test_crop_species_enum(species, expected):
    """test that CropSpecies correctly enumerates the accepted species names"""
    crop_species = CropSpecies(species)
    assert crop_species == expected

@pytest.mark.parametrize("invalid_species", ["fancy_grass", "regular rye", "soy beans"])
def test_invalid_crop_species_enum(invalid_species):
    """test that CropSpecies correctly raises an error when invalid species names are given."""
    with pytest.raises(ValueError) as e:
        CropSpecies(invalid_species)
    assert str(e.value) == f"'{invalid_species}' is not a valid CropSpecies"

def test_factory_defaults():
    # generic
    generic = CropSpeciesDataFactory.create_species_data()
    assert generic.species == "generic"
    assert generic.name == "default generic annual crop"
    assert generic.id == 0
    assert generic.plant_code is None
    assert generic.scientific_name is None
    assert generic.is_perennial is False
    assert generic.is_nitrogen_fixer is False
    assert generic.minimum_temperature == 0
    assert generic.optimal_temperature == 25
    assert generic.max_leaf_area_index == 4.0
    assert generic.first_heat_fraction_point == 0.15
    assert generic.first_leaf_fraction_point == 0.01
    assert generic.second_heat_fraction_point == 0.50
    assert generic.second_leaf_fraction_point == 0.95
    assert generic.senescent_heat_fraction == 0.9
    assert generic.light_use_efficiency == 30
    assert generic.emergence_nitrogen_fraction == 0.05
    assert generic.half_mature_nitrogen_fraction == 0.02
    assert generic.mature_nitrogen_fraction == 0.01
    assert generic.emergence_phosphorus_fraction == 0.005
    assert generic.half_mature_phosphorus_fraction == 0.003
    assert generic.mature_phosphorus_fraction == 0.002
    assert generic.optimal_harvest_index == 0.5
    assert generic.min_harvest_index == 0.2
    assert generic.yield_nitrogen_fraction == 0.2
    assert generic.yield_phosphorus_fraction == 0.003

    # check that setting the crop ID works and doesn't trigger the "altered" crop name
    generic_id = CropSpeciesDataFactory.create_species_data(id=1530)
    assert generic_id.id == 1530
    assert generic_id.name == "default generic annual crop"

    assert False  # need to replicate the above assertions for all species


@pytest.mark.parametrize("species,vars_dict", [
    ("generic", {"minimum_temperature": -2}),
    ("corn", {"minimum_temperature": 3, "second_leaf_fraction_point": 0.93}),
    ("soybean", {"max_leaf_area_index": 2.4, "light_use_efficiency": 10.8, "emergence_nitrogen_fraction": 0.06}),
    ("winter_wheat", {"optimal_temperature": 28, "optimal_harvest_index": 0.99, "min_harvest_index": 0.98}),
])
def test_factory_alterations(species, vars_dict):
    """check that the factory properly creates altered crop species data objects"""
    # setup crop
    crop = CropSpeciesDataFactory.create_species_data(CropSpecies(species), **vars_dict)
    # check that all altered attributes have been correctly set
    for key, val in vars_dict.items():
        assert getattr(crop, key) == val
    # check that all unaltered attributes are equal to their defaults
    unaltered_attributes = asdict(crop).keys() - vars_dict.keys()  # set difference
    default_crop = CropSpeciesDataFactory.create_species_data()
    for key in unaltered_attributes:
        if key != "name":  # ignore the name attribute here
            assert getattr(crop, key) == getattr(default_crop, key)
    # check that the name has been altered to reflect changes to default class
    if "name" not in vars_dict.keys():
        assert "altered" in crop.name

def test_factory_errors():
    """check that specifying invalid attributes appropriately raises an error"""
    assert False
