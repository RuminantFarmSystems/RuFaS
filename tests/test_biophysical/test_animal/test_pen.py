from unittest.mock import Mock, PropertyMock, MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionSupply, NutritionRequirements, \
    NutritionEvaluationResults
from RUFAS.biophysical.animal.data_types.pen_statistics import PenStatistics
from RUFAS.biophysical.animal.digestive_system.digestive_system import DigestiveSystem
from RUFAS.biophysical.animal.growth.growth import Growth
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.biophysical.animal.nutrients.nutrients import Nutrients
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements
from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions
from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID
from RUFAS.enums import AnimalCombination


@pytest.fixture
def animals_in_pen() -> dict[int, Animal]:
    milk_production = MagicMock(spec=MilkProduction)
    milk_production.configure_mock(daily_milk_produced=42)
    nutrients = Nutrients()
    nutrients.phosphorus_requirement = 15
    requirements = NutritionRequirements(
        maintenance_energy=1,
        growth_energy=2,
        pregnancy_energy=3,
        lactation_energy=4,
        metabolizable_protein=5,
        calcium=6,
        phosphorus=7,
        process_based_phosphorus=8,
        dry_matter=9,
        activity_energy=10,
        essential_amino_acids=EssentialAminoAcidRequirements(
            histidine=0.0,
            isoleucine=0.0,
            leucine=0.0,
            lysine=0.0,
            methionine=0.0,
            phenylalanine=0.0,
            threonine=0.0,
            thryptophan=0.0,
            valine=0.0,
        ),
    )
    digestive_system = MagicMock(spec=DigestiveSystem)
    digestive_system.configure_mock(manure_excretion=AnimalManureExcretions(urine_nitrogen=15))
    growth = MagicMock(spec=Growth)
    growth.configure_mock(daily_growth=10)
    animal_1 = MagicMock(spec=Animal)
    animal_1.configure_mock(animal_type=AnimalType.LAC_COW, growth=growth, digestive_system=digestive_system,
                            nutrition_requirements=requirements, nutrients=nutrients, body_weight=50,
                            milk_production=milk_production)
    animal_2 = MagicMock(spec=Animal)
    animal_2.configure_mock(animal_type=AnimalType.CALF, growth=growth, digestive_system=digestive_system,
                            nutrition_requirements=requirements, nutrients=nutrients, body_weight=50)
    return {1: animal_1,
            2: animal_2}


@pytest.fixture
def pen() -> Pen:
    return Pen(
        1,
        "Test Pen",
        12.5,
        13.5,
        10,
        "housing_type",
        "bedding_type",
        "pen_type",
        "manure_handling",
        "manure_separator",
        "manure_separator_after_digestion",
        "manure_storage",
        AnimalCombination.LAC_COW,
        19.5
    )


def test_pen_init(pen: Pen) -> None:
    """Tests the initialization of pen class."""
    assert pen.id == 1
    assert pen.pen_name == "Test Pen"
    assert pen.vertical_dist_to_parlor == 12.5
    assert pen.horizontal_dist_to_parlor == 13.5
    assert pen.num_stalls == 14
    assert pen.housing_type == "housing_type"
    assert pen.bedding_type == "bedding_type"
    assert pen.pen_type == "pen_type"
    assert pen.manure_handling == "manure_handling"
    assert pen.manure_separator == "manure_separator"
    assert pen.manure_separator_after_digestion == "manure_separator_after_digestion"
    assert pen.manure_storage == "manure_storage"
    assert pen.animal_combination == AnimalCombination.LAC_COW
    assert pen.max_stocking_density == 19.5
    assert isinstance(pen.pen_statistics, PenStatistics)
    assert isinstance(pen.average_nutrition_supply, NutritionSupply)
    assert isinstance(pen.average_nutrition_requirements, NutritionRequirements)
    assert isinstance(pen.average_nutrition_evaluation, NutritionEvaluationResults)
    assert pen.animals_in_pen == {}
    assert pen.ration == {}
    assert pen.allocated_feeds == set()


def test_current_stocking_density(pen: Pen, mocker: MockerFixture) -> None:
    """Tests the calculation of current stocking density."""
    pen.animals_in_pen = {
        1: mocker.Mock(),
        2: mocker.Mock(),
        3: mocker.Mock()
    }
    assert pen.current_stocking_density == 0.3


@pytest.mark.parametrize(
    "animals_in_pen,expected",
    [({
          1: Mock(),
          2: Mock(),
          3: Mock()
      }, True),
        ({}, False)]
)
def test_is_populated(pen: Pen, animals_in_pen: dict[int, Animal], expected: bool) -> None:
    """Tests the pen's population status."""
    pen.animals_in_pen = animals_in_pen
    assert pen.is_populated == expected


@pytest.mark.parametrize(
    "ration, is_populated, expected",
    [({}, True, True),
     ({}, False, False),
     ({3: 2.5}, True, False)]
)
def test_needs_ration_formulation(ration: dict[RUFAS_ID, float], is_populated: bool, expected: bool, pen: Pen,
                                  mocker: MockerFixture) -> None:
    """Tests if the pen needs a ration formulated."""
    mocker.patch.object(
        Pen, "is_populated", new_callable=PropertyMock, return_value=is_populated
    )
    pen.ration = ration
    assert pen.needs_ration_formulation == expected


def test_animal_types_in_pen(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the set of animal types currently in the pen."""
    pen.animals_in_pen = animals_in_pen
    assert pen.animal_types_in_pen == {AnimalType.LAC_COW, AnimalType.CALF}


def test_number_of_lactating_cows_in_pen(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the number of lactating cows."""
    pen.animals_in_pen = animals_in_pen
    assert pen.number_of_lactating_cows_in_pen == 1


def test_cows_in_pen(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the numbers of all cows in pen"""
    pen.animals_in_pen = animals_in_pen
    assert pen.cows_in_pen == [animals_in_pen.get(1)]


def test_average_growth(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the calculation of average animal growth."""
    pen.animals_in_pen = animals_in_pen
    assert pen.average_growth == 10


def test_total_manure_excretion(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the aggregation of manure excretion."""
    pen.animals_in_pen = animals_in_pen
    assert pen.total_manure_excretion.urine_nitrogen == 30


def test_average_animal_requirements(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the average nutritional requirements for all animals in a pen."""
    pen.animals_in_pen = animals_in_pen
    assert pen.average_animal_requirements == NutritionRequirements(
        maintenance_energy=1,
        growth_energy=2,
        pregnancy_energy=3,
        lactation_energy=4,
        metabolizable_protein=5,
        calcium=6,
        phosphorus=7,
        process_based_phosphorus=8,
        dry_matter=9,
        activity_energy=10,
        essential_amino_acids=EssentialAminoAcidRequirements(
            histidine=0.0,
            isoleucine=0.0,
            leucine=0.0,
            lysine=0.0,
            methionine=0.0,
            phenylalanine=0.0,
            threonine=0.0,
            thryptophan=0.0,
            valine=0.0,
        ),
    )


def test_average_animal_requirements_no_animals(pen: Pen) -> None:
    """Tests the average nutritional requirements whe no animals in pen."""
    pen.animals_in_pen = {}
    assert pen.average_animal_requirements == NutritionRequirements(
        maintenance_energy=0,
        growth_energy=0,
        pregnancy_energy=0,
        lactation_energy=0,
        metabolizable_protein=0,
        calcium=0,
        phosphorus=0,
        process_based_phosphorus=0,
        dry_matter=0,
        activity_energy=0,
        essential_amino_acids=EssentialAminoAcidRequirements(
            histidine=0.0,
            isoleucine=0.0,
            leucine=0.0,
            lysine=0.0,
            methionine=0.0,
            phenylalanine=0.0,
            threonine=0.0,
            thryptophan=0.0,
            valine=0.0,
        ),
    )


def test_average_phosphorus_requirements(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the average phosphorus requirements for all animals in pen."""
    pen.animals_in_pen = animals_in_pen
    assert pen.average_phosphorus_requirements == 15


def test_average_phosphorus_requirements_no_animals(pen: Pen) -> None:
    """Tests the average phosphorus requirements whe no animals in pen."""
    pen.animals_in_pen = {}
    assert pen.average_phosphorus_requirements == 0


def test_average_body_weight(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the calculated average body weight of animals in the pen."""
    pen.animals_in_pen = animals_in_pen
    assert pen.average_body_weight == 50


def test_average_average_body_weight_no_animals(pen: Pen) -> None:
    """Tests the case when there's no animal."""
    pen.animals_in_pen = {}
    assert pen.average_phosphorus_requirements == 0


def test_average_milk_production(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the calculation of average milk production."""
    pen.animals_in_pen = animals_in_pen
    assert pen.average_milk_production == 42


def test_average_milk_production_non_LAC(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the calculation of average milk production when animal combination is not lac cow."""
    pen.animals_in_pen = animals_in_pen
    pen.animal_combination = AnimalCombination.CALF
    assert pen.average_milk_production == 0


def test_average_milk_production_no_cows(pen: Pen, animals_in_pen: dict[int, Animal], mocker: MockerFixture) -> None:
    """Tests the calculation of average milk production when animal combination is not lac cow."""
    pen.animals_in_pen = animals_in_pen
    mocker.patch.object(
        Pen, "cows_in_pen", new_callable=PropertyMock, return_value=[]
    )
    assert pen.average_milk_production == 0
