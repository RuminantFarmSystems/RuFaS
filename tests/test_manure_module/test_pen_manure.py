from dataclasses import fields

from pytest import approx

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.animal.manure.general_manure import AnimalManureExcretions
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.pen_manure.pen_manure import PenManure


def test_pen_manure_init() -> None:
    """Unit test for function __init__ in file pen_manure.py"""
    # Case 1: Given no arguments, a new PenManure object should have all attributes
    # initially set to 0.

    # Arrange
    pen_manure_attributes = [field.name for field in fields(PenManure)]

    # Act
    manure = PenManure()

    # Assert
    for attr in pen_manure_attributes:
        assert hasattr(manure, attr)
        if type(attr) is float:
            assert getattr(manure, attr) == approx(0.0)

    # --------------------------------------------------------------------------- #

    # Case 2: Given a dictionary of arguments, a new PenManure object should have all attributes
    # initially set to the correct values.

    # Arrange
    manure_data = {
        "urea": 1.0,
        "urine": 2.0,
        "urine_total_ammoniacal_nitrogen": 3.0,
        "manure_total_ammoniacal_nitrogen": 4.0,
        "nitrogen": 5.0,
        "manure_mass": 6.0,
        "total_solids": 7.0,
        "degradable_volatile_solids": 8.0,
        "non_degradable_volatile_solids": 9.0,
        "inorganic_phosphorus_fraction": 10.0,
        "organic_phosphorus_fraction": 11.0,
        "non_water_inorganic_phosphorus_fraction": 12.0,
        "non_water_organic_phosphorus_fraction": 13.0,
        "phosphorus": 14.0,
        "phosphorus_fraction": 15.0,
        "potassium": 16.0,
        "enteric_methane_kg": 17.0,
    }

    # Act
    manure = PenManure(**manure_data)

    # Assert
    assert manure.urea == approx(1.0)
    assert manure.urine == approx(2.0)
    assert manure.urine_total_ammoniacal_nitrogen == approx(3.0)
    assert manure.manure_total_ammoniacal_nitrogen == approx(4.0)
    assert manure.nitrogen == approx(5.0)
    assert manure.manure_mass == approx(6.0)
    assert manure.manure_volume == approx(manure.manure_mass / ManureConstants.MANURE_DENSITY)
    assert manure.total_solids == approx(7.0)
    assert manure.degradable_volatile_solids == approx(8.0)
    assert manure.non_degradable_volatile_solids == approx(9.0)
    assert manure.inorganic_phosphorus_fraction == approx(10.0)
    assert manure.organic_phosphorus_fraction == approx(11.0)
    assert manure.non_water_inorganic_phosphorus_fraction == approx(12.0)
    assert manure.non_water_organic_phosphorus_fraction == approx(13.0)
    assert manure.phosphorus == approx(14.0)
    assert manure.phosphorus_fraction == approx(15.0)
    assert manure.potassium == approx(16.0)

    # --------------------------------------------------------------------------- #

    # Case 3: Given an animal manure data dictionary and number of animals, a PenManure
    # should be returned with internal attributes correctly calculated.

    # Arrange
    urea = 1.0
    urine = 2.0
    total_ammoniacal_nitrogen_concentration = 3.0
    urine_nitrogen = 4.0
    manure_nitrogen = 5.0
    manure_mass = 6.0
    total_solids = 7.0
    degradable_volatile_solids = 8.0
    non_degradable_volatile_solids = 9.0
    inorganic_phosphorus_fraction = 10.0
    organic_phosphorus_fraction = 11.0
    non_water_inorganic_phosphorus_fraction = 12.0
    non_water_organic_phosphorus_fraction = 13.0
    phosphorus = 14.0
    phosphorus_fraction = 15.0
    potassium = 16.0
    enteric_methane_g = 17.0
    animal_manure = AnimalManureExcretions(
        urea=urea,
        urine=urine,
        total_ammoniacal_nitrogen_concentration=total_ammoniacal_nitrogen_concentration,
        urine_nitrogen=urine_nitrogen,
        manure_nitrogen=manure_nitrogen,
        manure_mass=manure_mass,
        total_solids=total_solids,
        degradable_volatile_solids=degradable_volatile_solids,
        non_degradable_volatile_solids=non_degradable_volatile_solids,
        inorganic_phosphorus_fraction=inorganic_phosphorus_fraction,
        organic_phosphorus_fraction=organic_phosphorus_fraction,
        non_water_inorganic_phosphorus_fraction=non_water_inorganic_phosphorus_fraction,
        non_water_organic_phosphorus_fraction=non_water_organic_phosphorus_fraction,
        phosphorus=phosphorus,
        phosphorus_fraction=phosphorus_fraction,
        potassium=potassium,
        enteric_methane_g=enteric_methane_g,
    )
    num_animals = 2
    expected_total_ammoniacal_nitrogen = urine_nitrogen
    expected_urine_ammoniacal_nitrogen = urine_nitrogen

    # Act
    manure = PenManure.get_instance(animal_manure, num_animals)

    # Assert
    assert manure.urea == approx(animal_manure["urea"] / num_animals)
    assert manure.urine == approx(animal_manure["urine"])
    assert manure.urine_nitrogen == approx(animal_manure["urine_nitrogen"])
    assert manure.urine_total_ammoniacal_nitrogen == approx(expected_urine_ammoniacal_nitrogen)
    assert manure.manure_total_ammoniacal_nitrogen == approx(expected_total_ammoniacal_nitrogen)
    assert manure.nitrogen == approx(animal_manure["manure_nitrogen"])
    assert manure.manure_mass == approx(animal_manure["manure_mass"])
    assert manure.total_solids == approx(animal_manure["total_solids"])
    assert manure.degradable_volatile_solids == approx(animal_manure["degradable_volatile_solids"])
    assert manure.non_degradable_volatile_solids == approx(animal_manure["non_degradable_volatile_solids"])
    assert manure.inorganic_phosphorus_fraction == approx(animal_manure["inorganic_phosphorus_fraction"] / num_animals)
    assert manure.organic_phosphorus_fraction == approx(animal_manure["organic_phosphorus_fraction"] / num_animals)
    assert manure.non_water_inorganic_phosphorus_fraction == approx(
        animal_manure["non_water_inorganic_phosphorus_fraction"] / num_animals
    )
    assert manure.non_water_organic_phosphorus_fraction == approx(
        animal_manure["non_water_organic_phosphorus_fraction"] / num_animals
    )
    assert manure.phosphorus == approx(animal_manure["phosphorus"] * GeneralConstants.GRAMS_TO_KG)
    assert manure.phosphorus_fraction == approx(animal_manure["phosphorus_fraction"] / num_animals)
    assert manure.potassium == approx(animal_manure["potassium"] * GeneralConstants.GRAMS_TO_KG)
    assert manure.enteric_methane_kg == approx(animal_manure["enteric_methane_g"] * GeneralConstants.GRAMS_TO_KG)
