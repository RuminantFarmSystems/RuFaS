from typing import Any
from unittest.mock import Mock, PropertyMock, MagicMock, create_autospec

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import (
    NutritionSupply,
    NutritionRequirements,
    NutritionEvaluationResults,
)
from RUFAS.biophysical.animal.digestive_system.digestive_system import DigestiveSystem
from RUFAS.biophysical.animal.growth.growth import Growth
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.biophysical.animal.nutrients.nutrients import Nutrients
from RUFAS.biophysical.animal.nutrients.nutrition_evaluator import NutritionEvaluator
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import NutritionSupplyCalculator
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements
from RUFAS.biophysical.animal.ration.user_defined_ration_manager import UserDefinedRationManager
from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    RUFAS_ID,
    RequestedFeed,
    Feed,
    AdvancePurchaseAllowance,
    TotalInventory,
)
from RUFAS.data_structures.pen_manure_data import PenManureData
from RUFAS.enums import AnimalCombination


@pytest.fixture
def animals_in_pen() -> dict[int, Animal]:
    milk_production = MagicMock(spec=MilkProduction)
    milk_production.configure_mock(daily_milk_produced=42, milk_production_reduction=215)
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
    nutrition_supply = NutritionSupply(
        metabolizable_energy=1.0,
        maintenance_energy=2.0,
        lactation_energy=3.0,
        growth_energy=4.0,
        metabolizable_protein=5.0,
        calcium=6.0,
        phosphorus=7.0,
        dry_matter=8.0,
        wet_matter=9.0,
        ndf_supply=10.0,
        forage_ndf_supply=11.0,
        fat_supply=12.0,
        crude_protein=13.0,
        adf_supply=1.0,
        digestible_energy_supply=14.0,
        tdn_supply=15.0,
        lignin_supply=16.0,
        ash_supply=17.0,
        potassium_supply=18.0,
        starch_supply=19.0,
        byproduct_supply=20.0,
    )
    digestive_system = MagicMock(spec=DigestiveSystem)
    digestive_system.configure_mock(
        manure_excretion=AnimalManureExcretions(urine_nitrogen=15), enteric_methane_emission=69.4
    )
    growth = MagicMock(spec=Growth)
    growth.configure_mock(daily_growth=10)
    animal_1 = MagicMock(spec=Animal)
    animal_1.configure_mock(
        id=1,
        animal_type=AnimalType.LAC_COW,
        growth=growth,
        digestive_system=digestive_system,
        nutrition_requirements=requirements,
        nutrients=nutrients,
        body_weight=50,
        milk_production=milk_production,
        daily_distance=10,
        nutrition_supply=nutrition_supply,
    )
    animal_2 = MagicMock(spec=Animal)
    animal_2.configure_mock(
        id=2,
        animal_type=AnimalType.CALF,
        growth=growth,
        digestive_system=digestive_system,
        nutrition_requirements=requirements,
        nutrients=nutrients,
        body_weight=50,
        daily_distance=10,
        nutrition_supply=nutrition_supply,
    )
    return {1: animal_1, 2: animal_2}


@pytest.fixture
def pen() -> Pen:
    return Pen(
        pen_id=1,
        pen_name="Test Pen",
        vertical_dist_to_milking_parlor=12.5,
        horizontal_dist_to_milking_parlor=13.5,
        number_of_stalls=10,
        housing_type="housing_type",
        bedding_type="bedding_type",
        pen_type="pen_type",
        manure_handling="manure_handling",
        manure_separator="manure_separator",
        manure_separator_after_digestion="manure_separator_after_digestion",
        manure_storage="manure_storage",
        animal_combination=AnimalCombination.LAC_COW,
        max_stocking_density=19.5,
        minutes_away_for_milking=7,
        parlor_stream_assignment="stream_a",
        manure_streams=[
            {"stream_name": "general_stream_1", "stream_proportion": 0.6},
            {"stream_name": "general_stream_2", "stream_proportion": 0.4},
        ],
    )


def test_pen_init(pen: Pen) -> None:
    """Tests the initialization of Pen class."""
    assert pen.id == 1
    assert pen.pen_name == "Test Pen"
    assert pen.vertical_dist_to_parlor == 12.5
    assert pen.horizontal_dist_to_parlor == 13.5
    assert pen.num_stalls == 10
    assert pen.housing_type == "housing_type"
    assert pen.bedding_type == "bedding_type"
    assert pen.pen_type == "pen_type"
    assert pen.manure_handling == "manure_handling"
    assert pen.manure_separator == "manure_separator"
    assert pen.manure_separator_after_digestion == "manure_separator_after_digestion"
    assert pen.manure_storage == "manure_storage"
    assert pen.animal_combination == AnimalCombination.LAC_COW
    assert pen.max_stocking_density == 19.5
    assert pen.minutes_away_for_milking == 7
    assert pen.parlor_stream_assignment == "stream_a"
    assert pen.manure_streams == [
        {"stream_name": "general_stream_1", "stream_proportion": 0.6},
        {"stream_name": "general_stream_2", "stream_proportion": 0.4},
    ]
    assert isinstance(pen.average_nutrition_evaluation, NutritionEvaluationResults)
    assert pen.animals_in_pen == {}
    assert pen.ration == {}
    assert pen.allocated_feeds == set()


def test_current_stocking_density(pen: Pen, mocker: MockerFixture) -> None:
    """Tests the calculation of current stocking density."""
    pen.animals_in_pen = {1: mocker.Mock(), 2: mocker.Mock(), 3: mocker.Mock()}
    assert pen.current_stocking_density == 0.3


@pytest.mark.parametrize("animals_in_pen,expected", [({1: Mock(), 2: Mock(), 3: Mock()}, True), ({}, False)])
def test_is_populated(pen: Pen, animals_in_pen: dict[int, Animal], expected: bool) -> None:
    """Tests the pen's population status."""
    pen.animals_in_pen = animals_in_pen
    assert pen.is_populated == expected


@pytest.mark.parametrize(
    "ration, is_populated, expected", [({}, True, True), ({}, False, False), ({3: 2.5}, True, False)]
)
def test_needs_ration_formulation(
    ration: dict[RUFAS_ID, float], is_populated: bool, expected: bool, pen: Pen, mocker: MockerFixture
) -> None:
    """Tests if the pen needs a ration formulated."""
    mocker.patch.object(Pen, "is_populated", new_callable=PropertyMock, return_value=is_populated)
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


def test_average_growth_empty_pen(pen: Pen) -> None:
    """Tests the calculation of average animal growth when there are no animals in the pen."""
    pen.animals_in_pen = {}
    assert pen.average_growth == 0.0


def test_total_manure_excretion(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the aggregation of manure excretion."""
    pen.animals_in_pen = animals_in_pen
    assert pen.total_manure_excretion.urine_nitrogen == 30


def test_average_animal_requirements(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the average nutritional requirements for all animals in a pen."""
    pen.animals_in_pen = animals_in_pen
    assert pen.average_nutrition_requirements == NutritionRequirements(
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
    assert pen.average_nutrition_requirements == NutritionRequirements(
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


def test_average_nutrition_supply(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the average nutritional supplies for all animals in a pen."""
    pen.animals_in_pen = animals_in_pen
    assert pen.average_nutrition_supply == NutritionSupply(
        metabolizable_energy=1.0,
        maintenance_energy=2.0,
        lactation_energy=3.0,
        growth_energy=4.0,
        metabolizable_protein=5.0,
        calcium=6.0,
        phosphorus=7.0,
        dry_matter=8.0,
        wet_matter=9.0,
        ndf_supply=10.0,
        forage_ndf_supply=11.0,
        fat_supply=12.0,
        crude_protein=13.0,
        adf_supply=1.0,
        digestible_energy_supply=14.0,
        tdn_supply=15.0,
        lignin_supply=16.0,
        ash_supply=17.0,
        potassium_supply=18.0,
        starch_supply=19.0,
        byproduct_supply=20.0,
    )


def test_average_nutrition_supply_no_animals(pen: Pen) -> None:
    """Tests the average nutritional supplies whe no animals in pen."""
    pen.animals_in_pen = {}
    assert pen.average_nutrition_supply == NutritionSupply(
        metabolizable_energy=0.0,
        maintenance_energy=0.0,
        lactation_energy=0.0,
        growth_energy=0.0,
        metabolizable_protein=0.0,
        calcium=0.0,
        phosphorus=0.0,
        dry_matter=0.0,
        wet_matter=0.0,
        ndf_supply=0.0,
        forage_ndf_supply=0.0,
        fat_supply=0.0,
        crude_protein=0.0,
        adf_supply=0.0,
        digestible_energy_supply=0.0,
        tdn_supply=0.0,
        lignin_supply=0.0,
        ash_supply=0.0,
        potassium_supply=0.0,
        starch_supply=0.0,
        byproduct_supply=0.0,
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


def test_average_body_weight_empty_pen(pen: Pen) -> None:
    """Tests the calculated average body weight of animals when there are no animals in the pen."""
    pen.animals_in_pen = {}
    assert pen.average_body_weight == 0.0


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
    """Tests the calculation of average milk production when there is no cow in pen."""
    pen.animals_in_pen = animals_in_pen
    mocker.patch.object(Pen, "cows_in_pen", new_callable=PropertyMock, return_value=[])
    assert pen.average_milk_production == 0


def test_average_milk_production_reduction(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the calculation of average milk production reduction."""
    pen.animals_in_pen = animals_in_pen
    assert pen.average_milk_production_reduction == 215


def test_average_milk_production_reduction_no_cows(
    pen: Pen, animals_in_pen: dict[int, Animal], mocker: MockerFixture
) -> None:
    """Tests the calculation of average milk production reduction when there is no cow in pen."""
    pen.animals_in_pen = animals_in_pen
    mocker.patch.object(Pen, "cows_in_pen", new_callable=PropertyMock, return_value=[])
    assert pen.average_milk_production_reduction == 0


def test_total_enteric_methane(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the calculation of total enteric methane."""
    pen.animals_in_pen = animals_in_pen
    assert pen.total_enteric_methane == 138.8


@pytest.mark.parametrize(
    "reduce_milk_production_result, expected_output",
    [([True, False], True), ([True, True], True), ([False, False], False)],
)
def test_reduce_milk_production(
    reduce_milk_production_result: list[bool],
    expected_output: bool,
    pen: Pen,
    animals_in_pen: dict[int, Animal],
    mocker: MockerFixture,
) -> None:
    """Tests the execution of milk production reduction."""
    pen.animals_in_pen = animals_in_pen
    mock_reduce = mocker.patch.object(
        animals_in_pen[1], "reduce_milk_production", return_value=reduce_milk_production_result[0]
    )
    mock_reduce_2 = mocker.patch.object(
        animals_in_pen[2], "reduce_milk_production", return_value=reduce_milk_production_result[1]
    )
    result = pen.reduce_milk_production()

    assert result == expected_output
    mock_reduce.assert_called_once()
    mock_reduce_2.assert_called_once()


@pytest.mark.parametrize("removal_list", [[], [1], [1, 2]])
def test_remove_animals_by_ids(pen: Pen, animals_in_pen: dict[int, Animal], removal_list: list[Any]) -> None:
    """Tests the removal of animals by id."""
    pen.animals_in_pen = animals_in_pen
    pen.remove_animals_by_ids(removal_list)
    if removal_list == [1]:
        assert pen.animals_in_pen[2].id == 2
    elif not removal_list:
        assert len(pen.animals_in_pen) == 2
    else:
        assert len(pen.animals_in_pen) == 0


def test_update_animals(pen: Pen, animals_in_pen: dict[int, Animal], mocker: MockerFixture) -> None:
    """Test animal update routines."""
    pen.animals_in_pen = animals_in_pen
    mock_add = mocker.patch.object(Pen, "_add_new_animals")
    mock_update = mocker.patch.object(Pen, "update_animal_combination")

    pen.update_animals([animals_in_pen[1]], AnimalCombination.LAC_COW, [MagicMock(Feed)])

    mock_update.assert_called_once()
    mock_add.assert_called_once()


def test_add_new_animals(pen: Pen, animals_in_pen: dict[int, Animal], mocker: MockerFixture) -> None:
    """Tests the function to adda list of animals into the pen."""
    mock_supply_1 = MagicMock(spec=NutritionSupply)
    animal_3 = create_autospec(Animal)
    animal_3.configure_mock(
        id=3,
        animal_type=AnimalType.CALF,
        nutrition_supply=mock_supply_1,
        feeds_used=[MagicMock(spec=Feed)],
        body_weight=10,
    )
    animal_4 = create_autospec(Animal)
    animal_4.configure_mock(
        id=3,
        animal_type=AnimalType.CALF,
        nutrition_supply=mock_supply_1,
        feeds_used=[MagicMock(spec=Feed)],
        body_weight=10,
    )

    new_animals = [animal_3, animal_4]
    pen.animals_in_pen = animals_in_pen
    mock_add = mocker.patch.object(pen, "insert_single_animal_into_animals_in_pen_map")
    mock_supply_2 = MagicMock(spec=NutritionSupply)
    mock_set_nutrition_requirements_4 = mocker.patch.object(animal_4, "set_nutrition_requirements")
    mock_set_nutrition_requirements_3 = mocker.patch.object(animal_3, "set_nutrition_requirements")
    mock_calculate = mocker.patch.object(
        NutritionSupplyCalculator, "calculate_nutrient_supply", return_value=mock_supply_2
    )

    pen._add_new_animals(new_animals, [MagicMock(spec=Feed)])

    for animal in new_animals:
        assert animal.nutrition_supply == mock_supply_2
    assert mock_calculate.call_count == 2
    assert mock_add.call_count == 2
    mock_set_nutrition_requirements_4.assert_called_once()
    mock_set_nutrition_requirements_3.assert_called_once()


def test_insert_animals_into_animals_in_pen_map(
    pen: Pen, animals_in_pen: dict[int, Animal], mocker: MockerFixture
) -> None:
    """Tests adding a list of new animals in the animals_in_pen map."""
    pen.animals_in_pen = animals_in_pen
    animal_3 = create_autospec(Animal)
    animal_4 = create_autospec(Animal)
    new_animals = [animal_3, animal_4]
    mock_insert = mocker.patch.object(pen, "insert_single_animal_into_animals_in_pen_map")
    pen.insert_animals_into_animals_in_pen_map(new_animals)
    assert mock_insert.call_count == 2


@pytest.mark.parametrize("is_cow", [True, False])
def test_insert_animal_into_animals_in_pen_map(
    pen: Pen, animals_in_pen: dict[int, Animal], is_cow: bool, mocker: MockerFixture
) -> None:
    """Tests adding an animal in the animals_in_pen map."""
    pen.animals_in_pen = animals_in_pen
    animal_3 = MagicMock(spec=Animal)
    mock_set = mocker.patch.object(animal_3, "set_daily_walking_distance")
    if is_cow:
        animal_3.configure_mock(id=3, animal_type=AnimalType.LAC_COW)
        pen.insert_single_animal_into_animals_in_pen_map(animal_3)
        mock_set.assert_called_once()
    else:
        animal_3.configure_mock(id=3, animal_type=AnimalType.CALF)
        pen.insert_single_animal_into_animals_in_pen_map(animal_3)
        mock_set.assert_not_called()
    assert pen.animals_in_pen.get(3) == animal_3


def test_update_animal_combination(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the update of pen's animal combination"""
    pen.animals_in_pen = animals_in_pen
    mock_combination = MagicMock(spec=AnimalCombination)

    pen.update_animal_combination(mock_combination)

    assert pen.animal_combination == mock_combination


@pytest.mark.parametrize(
    "animal_types_in_pen,is_cow",
    [
        ({AnimalType.LAC_COW, AnimalType.CALF}, True),
        ({AnimalType.DRY_COW, AnimalType.CALF}, True),
        ({AnimalType.CALF}, False),
    ],
)
def test_update_daily_walking_distance(
    pen: Pen,
    animals_in_pen: dict[int, Animal],
    animal_types_in_pen: set[AnimalType],
    is_cow: bool,
    mocker: MockerFixture,
) -> None:
    """Tests the update of daily walking distance for cows in pen"""
    pen.animals_in_pen = animals_in_pen
    mocker.patch.object(Pen, "animal_types_in_pen", new_callable=PropertyMock, return_value=animal_types_in_pen)
    mock_set = mocker.patch.object(animals_in_pen[1], "set_daily_walking_distance")
    pen.update_daily_walking_distance()
    if is_cow:
        mock_set.assert_called_once()
    else:
        mock_set.assert_not_called()


def test_clear(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the pen animal clearing method."""
    pen.animals_in_pen = animals_in_pen
    pen.clear()
    assert pen.animals_in_pen == {}


def test_get_manure_data(mocker: MockerFixture, pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the getter for manure data, including manure streams."""
    pen.animals_in_pen = animals_in_pen
    expected_streams = [{"solid": MagicMock(spec=ManureStream)}, {"liquid": MagicMock(spec=ManureStream)}]
    mocker.patch.object(pen, "get_manure_streams", return_value=expected_streams)

    result = pen.get_manure_data()

    assert set(result.keys()) == {"pen_manure_data", "manure_streams"}
    assert result["pen_manure_data"] == PenManureData(
        id=1,
        num_animals=2,
        classes_in_pen={AnimalType.LAC_COW, AnimalType.CALF},
        animal_combination=AnimalCombination.LAC_COW,
        housing_type="housing_type",
        pen_type="pen_type",
        bedding_type="bedding_type",
        manure_handler="manure_handling",
        manure_separator="manure_separator",
        manure_separator_after_digestion="manure_separator_after_digestion",
        manure_treatment="manure_storage",
        manure=AnimalManureExcretions(
            urea=0.0,
            urine=0.0,
            manure_total_ammoniacal_nitrogen=0.0,
            urine_nitrogen=30.0,
            manure_nitrogen=0.0,
            manure_mass=0.0,
            total_solids=0.0,
            degradable_volatile_solids=0.0,
            non_degradable_volatile_solids=0.0,
            inorganic_phosphorus_fraction=0.0,
            organic_phosphorus_fraction=0.0,
            non_water_inorganic_phosphorus_fraction=0.0,
            non_water_organic_phosphorus_fraction=0.0,
            phosphorus=0.0,
            phosphorus_fraction=0.0,
            potassium=0.0,
        ),
        num_lactating_cows=1,
        num_stalls=10,
    )

    assert result["manure_streams"] == expected_streams


@pytest.mark.parametrize(
    "animal_combination, manure_streams, expected_result_keys, expect_parlor",
    [
        (
            AnimalCombination.LAC_COW,
            [
                {"stream_name": "general_stream_1", "stream_proportion": 0.6},
                {"stream_name": "general_stream_2", "stream_proportion": 0.4},
            ],
            ["stream_a", "general_stream_1", "general_stream_2"],  # Parlor comes first
            True,
        ),
        (
            AnimalCombination.GROWING,
            [
                {"stream_name": "single_general_stream", "stream_proportion": 1.0},  # add default
            ],
            ["single_general_stream"],
            False,
        ),
    ],
)
def test_get_manure_streams(
    mocker: MockerFixture,
    animal_combination: AnimalCombination,
    manure_streams: list[dict[str, str | float]],
    expected_result_keys: list[str],
    expect_parlor: bool,
    pen: Pen,
    animals_in_pen: dict[int, Animal],
) -> None:
    """Tests get_manure_streams() with both custom and fallback logic."""
    pen.animals_in_pen = animals_in_pen
    pen.animal_combination = animal_combination
    pen.manure_streams = manure_streams
    pen.parlor_stream_assignment = "stream_a"
    pen.minutes_away_for_milking = 360

    mock_excretion = AnimalManureExcretions(
        urea=0.0,
        urine=50.0,
        manure_total_ammoniacal_nitrogen=2.5,
        urine_nitrogen=5.0,
        manure_nitrogen=10.0,
        manure_mass=100.0,
        total_solids=25.0,
        degradable_volatile_solids=5.0,
        non_degradable_volatile_solids=2.5,
        inorganic_phosphorus_fraction=0.0,
        organic_phosphorus_fraction=0.0,
        non_water_inorganic_phosphorus_fraction=0.0,
        non_water_organic_phosphorus_fraction=0.0,
        phosphorus=1.0,
        phosphorus_fraction=0.0,
        potassium=0.5,
    )

    for animal in animals_in_pen.values():
        mocker.patch.object(animal.digestive_system, "manure_excretion", new=mock_excretion)

    mock_split = mocker.patch.object(
        ManureStream,
        "split_stream",
        side_effect=lambda split_ratio, stream_type: MagicMock(
            spec=ManureStream,
            pen_manure_data=MagicMock(set_first_processor=MagicMock())
        ),
    )

    result = pen.get_manure_streams()

    actual_keys = [list(entry.keys())[0] for entry in result]
    assert actual_keys == expected_result_keys
    assert mock_split.call_count == len(expected_result_keys)


@pytest.mark.parametrize(
    "manure_streams, should_raise",
    [
        (
            [
                {"stream_name": "stream1", "stream_proportion": 0.6},
                {"stream_name": "stream2", "stream_proportion": 0.4},
            ],
            False,
        ),
        (
            [
                {"stream_name": "stream1", "stream_proportion": 0.3},
                {"stream_name": "stream2", "stream_proportion": 0.4},
            ],
            True,
        ),
        (
            [
                {"stream_name": "stream1", "stream_proportion": 0.8},
                {"stream_name": "stream2", "stream_proportion": 0.3},
            ],
            True,
        ),
        (
            [
                {"stream_name": "stream1", "stream_proportion": 0.333333},
                {"stream_name": "stream2", "stream_proportion": 0.333333},
                {"stream_name": "stream3", "stream_proportion": 0.333334},
            ],
            False,
        ),
    ],
)
def test_validate_manure_stream_proportions(
    manure_streams: list[dict[str, float]],
    should_raise: bool,
    pen: Pen,
) -> None:
    pen.manure_streams = manure_streams

    if should_raise:
        with pytest.raises(ValueError, match="Manure stream proportions must sum to 1.0"):
            pen.validate_manure_stream_proportions()
    else:
        pen.validate_manure_stream_proportions()


def test_get_requested_feed(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the getter for the requested feed."""
    pen.animals_in_pen = animals_in_pen
    pen.ration = {1: 16.5, 2: 9.24}
    assert pen.get_requested_feed(3) == RequestedFeed(requested_feed={1: 99.0, 2: 55.44})


def test_set_animal_nutritional_requirements(
    pen: Pen, animals_in_pen: dict[int, Animal], mocker: MockerFixture
) -> None:
    """Tests setting the nutritional requirements for all animals in the pen."""
    pen.animals_in_pen = animals_in_pen
    mock_set = mocker.patch.object(animals_in_pen[1], "set_nutrition_requirements")
    mock_set_2 = mocker.patch.object(animals_in_pen[2], "set_nutrition_requirements")
    pen.set_animal_nutritional_requirements(16, [MagicMock(Feed)])

    assert mock_set.call_count == 1
    assert mock_set_2.call_count == 1


def test_set_animal_nutritional_supply(pen: Pen, animals_in_pen: dict[int, Animal], mocker: MockerFixture) -> None:
    """Tests setting the nutritional supplies for all animals in the pen."""
    pen.animals_in_pen = animals_in_pen
    mock_set = mocker.patch.object(NutritionSupplyCalculator, "calculate_nutrient_supply")
    pen.set_animal_nutritional_supply([], {})

    assert mock_set.call_count == 2


def test_formulate_optimized_ration(pen: Pen) -> None:
    pen.formulate_optimized_ration(
        available_feeds=[],
        max_daily_feeds={},
        advance_purchase_allowance=MagicMock(autospec=AdvancePurchaseAllowance),
        total_inventory=MagicMock(autospec=TotalInventory),
    )


@pytest.mark.parametrize(
    "adequate, animal_combination, average_milk_production, reduce_milk_production",
    [
        (True, AnimalCombination.CALF, 0, False),
        (False, AnimalCombination.CALF, 0, False),
        (True, AnimalCombination.LAC_COW, 18, False),
        (False, AnimalCombination.LAC_COW, 18, True),
        (False, AnimalCombination.LAC_COW, 12, False),
        (False, AnimalCombination.LAC_COW, 12, True),
    ],
)
def test_use_user_defined_ration(
    pen: Pen,
    animals_in_pen: dict[int, Animal],
    mocker: MockerFixture,
    adequate: bool,
    animal_combination: AnimalCombination,
    average_milk_production: float,
    reduce_milk_production: bool,
) -> None:
    """Tests the calculation of new ration for the pen based on the number of animals in the pen."""
    animals_in_pen = {1: animals_in_pen[1]}
    pen.animals_in_pen = animals_in_pen
    pen.animal_combination = animal_combination
    mocker.patch.object(Pen, "average_milk_production", new_callable=PropertyMock, return_value=average_milk_production)
    mocker.patch.object(
        Pen,
        "average_nutrition_requirements",
        new_callable=PropertyMock,
        return_value=MagicMock(auto_spec=NutritionRequirements),
    )
    mocker.patch.object(
        Pen, "average_nutrition_supply", new_callable=PropertyMock, return_value=MagicMock(auto_spec=NutritionSupply)
    )
    mock_reduce = mocker.patch.object(pen, "reduce_milk_production", return_value=reduce_milk_production)
    mock_get_ration = mocker.patch.object(
        UserDefinedRationManager, "get_user_defined_ration", return_value={1: 20.3, 2: 40.6}
    )
    mock_set_animal_requirements = mocker.patch.object(pen, "set_animal_nutritional_requirements")
    mock_set_animal_supplies = mocker.patch.object(pen, "set_animal_nutritional_supply")

    mock_supply_eval = mocker.patch.object(
        NutritionEvaluator,
        "evaluate_nutrition_supply",
        side_effect=[
            (
                adequate,
                NutritionEvaluationResults(
                    total_energy=12.0,
                    maintenance_energy=0.0,
                    lactation_energy=0.0,
                    growth_energy=0.0,
                    metabolizable_protein=0.0,
                    calcium=0.0,
                    phosphorus=0.0,
                    dry_matter=0.0,
                    ndf_percent=0.0,
                    forage_ndf_percent=0.0,
                    fat_percent=0.0,
                ),
            ),
            (
                True,
                NutritionEvaluationResults(
                    total_energy=12.0,
                    maintenance_energy=0.0,
                    lactation_energy=0.0,
                    growth_energy=0.0,
                    metabolizable_protein=0.0,
                    calcium=0.0,
                    phosphorus=0.0,
                    dry_matter=0.0,
                    ndf_percent=0.0,
                    forage_ndf_percent=0.0,
                    fat_percent=0.0,
                ),
            ),
        ],
    )
    pen.use_user_defined_ration([MagicMock(Feed)], 15)
    if (
        not adequate
        and reduce_milk_production
        and average_milk_production >= AnimalModuleConstants.MINIMUM_AVG_PEN_MILK
    ):
        assert mock_set_animal_supplies.call_count == 2
        assert mock_set_animal_requirements.call_count == 2
        assert mock_supply_eval.call_count == 2
        assert mock_get_ration.call_count == 2
    else:
        assert mock_set_animal_supplies.call_count == 1
        assert mock_set_animal_requirements.call_count == 1
        assert mock_supply_eval.call_count == 1
        assert mock_get_ration.call_count == 1
    assert pen.average_nutrition_evaluation == NutritionEvaluationResults(
        total_energy=12.0,
        maintenance_energy=0.0,
        lactation_energy=0.0,
        growth_energy=0.0,
        metabolizable_protein=0.0,
        calcium=0.0,
        phosphorus=0.0,
        dry_matter=0.0,
        ndf_percent=0.0,
        forage_ndf_percent=0.0,
        fat_percent=0.0,
    )
    if adequate:
        mock_reduce.assert_not_called()
    elif animal_combination == AnimalCombination.LAC_COW:
        mock_reduce.assert_called_once()
    assert pen.ration == {1: 20.3, 2: 40.6}
