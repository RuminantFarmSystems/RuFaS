import pytest
from SC_redesign.Crop_and_Soil.crop.species_data_factory import CropSpecies, CropSpeciesDataFactory
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData, PlantTypes
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
    CropSpeciesDataFactory.create_secies_data() method.
    """
    # ---- generic crop ----
    generic = CropSpeciesDataFactory.create_species_data()
    assert generic.species == "generic"
    assert generic.name == "default generic annual crop"
    assert generic.id == 0
    assert generic.plant_code is None
    assert generic.scientific_name is None
    assert generic.plant_type == PlantTypes("cool_annual")
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
    generic_id = CropSpeciesDataFactory.create_species_data(CropSpecies("generic"), id=1530)
    assert generic_id.id == 1530
    assert generic_id.name == "default generic annual crop"

    # ---- corn ----
    corn = CropSpeciesDataFactory.create_species_data(CropSpecies("corn"), id=12)
    assert corn.species == "corn"  
    assert corn.name == "default corn"
    assert corn.id == 12
    assert corn.plant_code == "CORN"
    assert corn.scientific_name == "Zea mays"
    assert corn.plant_type == PlantTypes("warm_annual")
    assert corn.is_nitrogen_fixer is False
    assert corn.minimum_temperature == 8.0
    assert corn.optimal_temperature == 25.0
    assert corn.max_leaf_area_index == 3.0
    assert corn.first_heat_fraction_point == 0.15
    assert corn.first_leaf_fraction_point == 0.05
    assert corn.second_heat_fraction_point == 0.50
    assert corn.second_leaf_fraction_point == 0.95
    assert corn.senescent_heat_fraction == 0.90
    assert corn.light_use_efficiency == 39.0
    assert corn.emergence_nitrogen_fraction == 0.0470
    assert corn.half_mature_nitrogen_fraction == 0.0177
    assert corn.mature_nitrogen_fraction == 0.0138
    assert corn.emergence_phosphorus_fraction == 0.0048
    assert corn.half_mature_phosphorus_fraction == 0.0018
    assert corn.mature_phosphorus_fraction == 0.0014
    assert corn.optimal_harvest_index == 0.50
    assert corn.min_harvest_index == 0.30
    assert corn.yield_nitrogen_fraction == 0.014
    assert corn.yield_phosphorus_fraction == 0.0016

    # ---- spring wheat ----
    spring_wheat = CropSpeciesDataFactory.create_species_data(CropSpecies("spring_wheat"), id=85)
    assert spring_wheat.species == "spring_wheat"  
    assert spring_wheat.name == "default spring_wheat"
    assert spring_wheat.id == 85
    assert spring_wheat.plant_code == "SWHT"
    assert spring_wheat.scientific_name == "Triticum aestivum"
    assert spring_wheat.plant_type == PlantTypes("cool_annual")
    assert spring_wheat.is_nitrogen_fixer is False
    assert spring_wheat.minimum_temperature == 0.0
    assert spring_wheat.optimal_temperature == 18.0
    assert spring_wheat.max_leaf_area_index == 4.0
    assert spring_wheat.first_heat_fraction_point == 0.15
    assert spring_wheat.first_leaf_fraction_point == 0.05
    assert spring_wheat.second_heat_fraction_point == 0.50
    assert spring_wheat.second_leaf_fraction_point == 0.95
    assert spring_wheat.senescent_heat_fraction == 0.90
    assert spring_wheat.light_use_efficiency == 35.0
    assert spring_wheat.emergence_nitrogen_fraction == 0.0600
    assert spring_wheat.half_mature_nitrogen_fraction == 0.0231
    assert spring_wheat.mature_nitrogen_fraction == 0.0134
    assert spring_wheat.emergence_phosphorus_fraction == 0.0084
    assert spring_wheat.half_mature_phosphorus_fraction == 0.0032
    assert spring_wheat.mature_phosphorus_fraction == 0.0019
    assert spring_wheat.optimal_harvest_index == 0.42
    assert spring_wheat.min_harvest_index == 0.20
    assert spring_wheat.yield_nitrogen_fraction == 0.0234
    assert spring_wheat.yield_phosphorus_fraction == 0.0033

    # ---- winter wheat ----
    winter_wheat = CropSpeciesDataFactory.create_species_data(CropSpecies("winter_wheat"), id=1000)
    assert winter_wheat.species == "winter_wheat"  
    assert winter_wheat.name == "default winter_wheat"
    assert winter_wheat.id == 1000
    assert winter_wheat.plant_code == "WWHT"
    assert winter_wheat.scientific_name == "Triticum aestivum"
    assert winter_wheat.plant_type == PlantTypes("cool_annual")
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
    assert winter_wheat.optimal_harvest_index == 0.40
    assert winter_wheat.min_harvest_index == 0.20
    assert winter_wheat.yield_nitrogen_fraction == 0.0250
    assert winter_wheat.yield_phosphorus_fraction == 0.0022

    # ---- cereal rye ----
    cereal_rye = CropSpeciesDataFactory.create_species_data(CropSpecies("cereal_rye"), id=123)
    assert cereal_rye.species == "cereal_rye"  
    assert cereal_rye.name == "default cereal_rye"
    assert cereal_rye.id == 123
    assert cereal_rye.plant_code == "RYE"
    assert cereal_rye.scientific_name == "Secale cereale"
    assert cereal_rye.plant_type == PlantTypes("cool_annual")
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
    assert cereal_rye.optimal_harvest_index == 0.40
    assert cereal_rye.min_harvest_index == 0.20
    assert cereal_rye.yield_nitrogen_fraction == 0.0284
    assert cereal_rye.yield_phosphorus_fraction == 0.0042

    # ---- spring barley ----
    spring_barley = CropSpeciesDataFactory.create_species_data(CropSpecies("spring_barley"), id=42)
    assert spring_barley.species == "spring_barley"  
    assert spring_barley.name == "default spring_barley"
    assert spring_barley.id == 42  # this is everything
    assert spring_barley.plant_code == "BARL"
    assert spring_barley.scientific_name == "Hordeum vulgare"
    assert spring_barley.plant_type == PlantTypes("cool_annual")
    assert spring_barley.is_nitrogen_fixer is False
    assert spring_barley.minimum_temperature == 0.0
    assert spring_barley.optimal_temperature == 25.0
    assert spring_barley.max_leaf_area_index == 4.0
    assert spring_barley.first_heat_fraction_point == 0.15
    assert spring_barley.first_leaf_fraction_point == 0.01
    assert spring_barley.second_heat_fraction_point == 0.45
    assert spring_barley.second_leaf_fraction_point == 0.95
    assert spring_barley.senescent_heat_fraction == 0.90
    assert spring_barley.light_use_efficiency == 35.0
    assert spring_barley.emergence_nitrogen_fraction == 0.0590
    assert spring_barley.half_mature_nitrogen_fraction == 0.0226
    assert spring_barley.mature_nitrogen_fraction == 0.0131
    assert spring_barley.emergence_phosphorus_fraction == 0.0057
    assert spring_barley.half_mature_phosphorus_fraction == 0.0022
    assert spring_barley.mature_phosphorus_fraction == 0.0013
    assert spring_barley.optimal_harvest_index == 0.54
    assert spring_barley.min_harvest_index == 0.20
    assert spring_barley.yield_nitrogen_fraction == 0.0210
    assert spring_barley.yield_phosphorus_fraction == 0.0017

    # ---- fall oats ----
    fall_oats = CropSpeciesDataFactory.create_species_data(CropSpecies("fall_oats"), id=9001)
    assert fall_oats.species == "fall_oats"  
    assert fall_oats.name == "default fall_oats"
    assert fall_oats.id == 9001  # it is, indeed, over 9000
    assert fall_oats.plant_code == "OATS"
    assert fall_oats.scientific_name == "Avena sativa"
    assert fall_oats.plant_type == PlantTypes("cool_annual")
    assert fall_oats.is_nitrogen_fixer is False
    assert fall_oats.minimum_temperature == 0.0
    assert fall_oats.optimal_temperature == 15.0
    assert fall_oats.max_leaf_area_index == 4.0
    assert fall_oats.first_heat_fraction_point == 0.15
    assert fall_oats.first_leaf_fraction_point == 0.02
    assert fall_oats.second_heat_fraction_point == 0.50
    assert fall_oats.second_leaf_fraction_point == 0.95
    assert fall_oats.senescent_heat_fraction == 0.90
    assert fall_oats.light_use_efficiency == 35.0
    assert fall_oats.emergence_nitrogen_fraction == 0.0600
    assert fall_oats.half_mature_nitrogen_fraction == 0.0231
    assert fall_oats.mature_nitrogen_fraction == 0.0134
    assert fall_oats.emergence_phosphorus_fraction == 0.0084
    assert fall_oats.half_mature_phosphorus_fraction == 0.0032
    assert fall_oats.mature_phosphorus_fraction == 0.0019
    assert fall_oats.optimal_harvest_index == 0.42
    assert fall_oats.min_harvest_index == 0.175
    assert fall_oats.yield_nitrogen_fraction == 0.0316
    assert fall_oats.yield_phosphorus_fraction == 0.0057

    # ---- tall fescue ----
    tall_fescue = CropSpeciesDataFactory.create_species_data(CropSpecies("tall_fescue"), id=-1)
    assert tall_fescue.species == "tall_fescue"  
    assert tall_fescue.name == "default tall_fescue"
    assert tall_fescue.id == -1  # who would do this?
    assert tall_fescue.plant_code == "FESC"
    assert tall_fescue.scientific_name == "Festuca arundinaceae"
    assert tall_fescue.plant_type == PlantTypes("perennial")
    assert tall_fescue.is_nitrogen_fixer is False
    assert tall_fescue.minimum_temperature == 0.0
    assert tall_fescue.optimal_temperature == 15.0
    assert tall_fescue.max_leaf_area_index == 4.0
    assert tall_fescue.first_heat_fraction_point == 0.15
    assert tall_fescue.first_leaf_fraction_point == 0.01
    assert tall_fescue.second_heat_fraction_point == 0.50
    assert tall_fescue.second_leaf_fraction_point == 0.95
    assert tall_fescue.senescent_heat_fraction == 0.80
    assert tall_fescue.light_use_efficiency == 30.0
    assert tall_fescue.emergence_nitrogen_fraction == 0.0560
    assert tall_fescue.half_mature_nitrogen_fraction == 0.0210
    assert tall_fescue.mature_nitrogen_fraction == 0.0120
    assert tall_fescue.emergence_phosphorus_fraction == 0.0099
    assert tall_fescue.half_mature_phosphorus_fraction == 0.0022
    assert tall_fescue.mature_phosphorus_fraction == 0.0019
    assert tall_fescue.optimal_harvest_index == 0.90
    assert tall_fescue.min_harvest_index == 0.90
    assert tall_fescue.yield_nitrogen_fraction == 0.0234
    assert tall_fescue.yield_phosphorus_fraction == 0.0033

    # ---- alfalfa ----
    alfalfa = CropSpeciesDataFactory.create_species_data(CropSpecies("alfalfa"), id=7)
    assert alfalfa.species == "alfalfa"  
    assert alfalfa.name == "default alfalfa"
    assert alfalfa.id == 7
    assert alfalfa.plant_code == "ALFA"
    assert alfalfa.scientific_name == "Medicago sativa"
    assert alfalfa.plant_type == PlantTypes("perennial_legume")
    assert alfalfa.is_nitrogen_fixer is True
    assert alfalfa.minimum_temperature == 4.0
    assert alfalfa.optimal_temperature == 25.0
    assert alfalfa.max_leaf_area_index == 4.0
    assert alfalfa.first_heat_fraction_point == 0.15
    assert alfalfa.first_leaf_fraction_point == 0.01
    assert alfalfa.second_heat_fraction_point == 0.50
    assert alfalfa.second_leaf_fraction_point == 0.95
    assert alfalfa.senescent_heat_fraction == 0.90
    assert alfalfa.light_use_efficiency == 20.0
    assert alfalfa.emergence_nitrogen_fraction == 0.0417
    assert alfalfa.half_mature_nitrogen_fraction == 0.0290
    assert alfalfa.mature_nitrogen_fraction == 0.0200
    assert alfalfa.emergence_phosphorus_fraction == 0.0035
    assert alfalfa.half_mature_phosphorus_fraction == 0.0028
    assert alfalfa.mature_phosphorus_fraction == 0.0020
    assert alfalfa.optimal_harvest_index == 0.90
    assert alfalfa.min_harvest_index == 0.90
    assert alfalfa.yield_nitrogen_fraction == 0.0250
    assert alfalfa.yield_phosphorus_fraction == 0.0035

    # ---- soybeans ----
    soybean = CropSpeciesDataFactory.create_species_data(CropSpecies("soybean"), id=999)
    assert soybean.species == "soybean"  
    assert soybean.name == "default soybean"
    assert soybean.id == 999
    assert soybean.plant_code == "SOYB"
    assert soybean.scientific_name == "Glycine max"
    assert soybean.plant_type == PlantTypes("warm_annual_legume")
    assert soybean.is_nitrogen_fixer is True
    assert soybean.minimum_temperature == 10.0
    assert soybean.optimal_temperature == 25.0
    assert soybean.max_leaf_area_index == 3.0
    assert soybean.first_heat_fraction_point == 0.15
    assert soybean.first_leaf_fraction_point == 0.05
    assert soybean.second_heat_fraction_point == 0.50
    assert soybean.second_leaf_fraction_point == 0.95
    assert soybean.senescent_heat_fraction == 0.90
    assert soybean.light_use_efficiency == 25.0
    assert soybean.emergence_nitrogen_fraction == 0.0524
    assert soybean.half_mature_nitrogen_fraction == 0.0265
    assert soybean.mature_nitrogen_fraction == 0.0258
    assert soybean.emergence_phosphorus_fraction == 0.0074
    assert soybean.half_mature_phosphorus_fraction == 0.0037
    assert soybean.mature_phosphorus_fraction == 0.0035
    assert soybean.optimal_harvest_index == 0.31
    assert soybean.min_harvest_index == 0.01
    assert soybean.yield_nitrogen_fraction == 0.0650
    assert soybean.yield_phosphorus_fraction == 0.0091

    # ---- sugar beet ----
    sugar_beet = CropSpeciesDataFactory.create_species_data(CropSpecies("sugar_beet"), id=5)
    assert sugar_beet.species == "sugar_beet"  
    assert sugar_beet.name == "default sugar_beet"
    assert sugar_beet.id == 5
    assert sugar_beet.plant_code == "SGBT"
    assert sugar_beet.scientific_name == "Beta vulgaris saccharifera"
    assert sugar_beet.plant_type == PlantTypes("warm_annual")
    assert sugar_beet.is_nitrogen_fixer is False
    assert sugar_beet.minimum_temperature == 4.0
    assert sugar_beet.optimal_temperature == 18.0
    assert sugar_beet.max_leaf_area_index == 5.0
    assert sugar_beet.first_heat_fraction_point == 0.05
    assert sugar_beet.first_leaf_fraction_point == 0.05
    assert sugar_beet.second_heat_fraction_point == 0.50
    assert sugar_beet.second_leaf_fraction_point == 0.95
    assert sugar_beet.senescent_heat_fraction == 0.90
    assert sugar_beet.light_use_efficiency == 30.0
    assert sugar_beet.emergence_nitrogen_fraction == 0.0550
    assert sugar_beet.half_mature_nitrogen_fraction == 0.0200
    assert sugar_beet.mature_nitrogen_fraction == 0.0120
    assert sugar_beet.emergence_phosphorus_fraction == 0.0060
    assert sugar_beet.half_mature_phosphorus_fraction == 0.0025
    assert sugar_beet.mature_phosphorus_fraction == 0.0019
    assert sugar_beet.optimal_harvest_index == 2.00
    assert sugar_beet.min_harvest_index == 1.10
    assert sugar_beet.yield_nitrogen_fraction == 0.0130
    assert sugar_beet.yield_phosphorus_fraction == 0.0020

    # ---- potato ----
    potato = CropSpeciesDataFactory.create_species_data(CropSpecies("potato"), id=2)
    assert potato.species == "potato"  
    assert potato.name == "default potato"
    assert potato.id == 2
    assert potato.plant_code == "POTA"
    assert potato.scientific_name == "Solanum tuberosum"
    assert potato.plant_type == PlantTypes("cool_annual")
    assert potato.is_nitrogen_fixer is False
    assert potato.minimum_temperature == 7.0
    assert potato.optimal_temperature == 22.0
    assert potato.max_leaf_area_index == 4.0
    assert potato.first_heat_fraction_point == 0.15
    assert potato.first_leaf_fraction_point == 0.01
    assert potato.second_heat_fraction_point == 0.50
    assert potato.second_leaf_fraction_point == 0.95
    assert potato.senescent_heat_fraction == 0.90
    assert potato.light_use_efficiency == 25.0
    assert potato.emergence_nitrogen_fraction == 0.0550
    assert potato.half_mature_nitrogen_fraction == 0.0200
    assert potato.mature_nitrogen_fraction == 0.0120
    assert potato.emergence_phosphorus_fraction == 0.0060
    assert potato.half_mature_phosphorus_fraction == 0.0025
    assert potato.mature_phosphorus_fraction == 0.0019
    assert potato.optimal_harvest_index == 0.95
    assert potato.min_harvest_index == 0.95
    assert potato.yield_nitrogen_fraction == 0.0246
    assert potato.yield_phosphorus_fraction == 0.0023

    # ---- Triticale ----
    # TODO: omitting triticale test, since it does not have non-default values at present


def test_manual_custom_crop_data():
    """checks (and demonstrates) the alternate way of customizing a crop"""
    # setup custom crop
    aspen = CropData(name="custom crop: aspen", species="aspen", scientific_name="Populus tremuloides",
                     plant_code="PTREM", plant_type=PlantTypes("tree"), is_nitrogen_fixer=False, max_leaf_area_index=5.0)

    # check that each attribute is set appropriately
    assert aspen.name == "custom crop: aspen"
    assert aspen.species == "aspen"
    assert aspen.scientific_name == "Populus tremuloides"
    assert aspen.plant_code == "PTREM"
    assert aspen.plant_type == PlantTypes("tree")
    # assert aspen.is_perennial is True
    assert aspen.is_nitrogen_fixer is False
    assert aspen.max_leaf_area_index == 5.0


@pytest.mark.parametrize("species,vars_dict", [
    ("generic", {"minimum_temperature": -2}),  # reduced temp
    ("corn", {"minimum_temperature": 3, "second_leaf_fraction_point": 0.93}),  # two changes
    ("spring_wheat", {"name": "wheat named Susan"}),  # custom name
    ("winter_wheat", {"optimal_temperature": 28, "optimal_harvest_index": 0.99,  # 3 changes
                      "min_harvest_index": 0.98}),
    ("cereal_rye", {"biomass": 100}),  # change attribute declared only in CropData
    ("spring_barley", {"name": "fancy barley",  # custom new variety/subspecies
                       "plant_code": "FBAR", "scientific_name" : "Hordeum vulgare regalis"}),
    ("fall_oats", {"plant_type": PlantTypes("perennial")}),  # perennial version of oats
    ("tall_fescue", {"is_nitrogen_fixer": True}),  # magical nitrogen-fixing grass (egads!)
    ("alfalfa", {"yield_nitrogen_fraction": 0.03}),  # this alfalfa has increased nitrogen in harvest
    ("soybean", {"max_leaf_area_index": 2.4, "light_use_efficiency": 10.8,  # various alterations
                 "emergence_nitrogen_fraction": 0.06}),
    ("sugar_beet", {"growth_factor": 0.8, "mature_phosphorus_fraction": 0.01}),  # mixed alterations
    ("potato", {"optimal_harvest_index": 1.2}),  # higher tuber yield
    # ("triticale", {})
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
    ("generic", {"color": "red"}),  # generic
    ("corn", {"flavor": "corny"}),  # child class
    ("alfalfa", {"value": 1000, "is_valuable": True}),  # multiple invalids
    ("soybean", {"name": "Bob", "moustache": True}),  # valid with invalid
])
def test_factory_errors(species, bad_attr):
    """check that specifying invalid attributes appropriately raises an error"""
    with pytest.raises(AttributeError) as e:
        CropSpeciesDataFactory.create_species_data(CropSpecies(species), **bad_attr)
    assert "is not a valid attribute" in str(e.value)


# --- Test @property methods ---
@pytest.mark.parametrize("plant_type", [
    PlantTypes.PERENNIAL,
    PlantTypes.PERENNIAL_LEGUME,
    PlantTypes.TREE,
    PlantTypes.WARM_ANNUAL,
    PlantTypes.WARM_ANNUAL_LEGUME,
    PlantTypes.COOL_ANNUAL,
    PlantTypes.COOL_ANNUAL_LEGUME,
])
def test_is_perennial(plant_type: PlantTypes) -> None:
    """Tests that is_perennial() correctly determines whether a plant is a perennial"""
    # Initialize CropData object
    crop = CropData(plant_type=plant_type)

    # Determine observed and expected results
    observe = crop.is_perennial
    perennial_set = {PlantTypes.PERENNIAL, PlantTypes.PERENNIAL_LEGUME}
    expect = type in perennial_set

    # Check results
    assert observe == expect

