from typing import Any
from unittest.mock import Mock, PropertyMock, MagicMock, create_autospec

import numpy as np
import pytest
from pytest_mock import MockerFixture
from scipy.optimize import OptimizeResult

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.bedding.bedding import Bedding
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.bedding_types import BeddingType
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
from RUFAS.biophysical.animal.ration.ration_optimizer import RationOptimizer, RationConfig
from RUFAS.biophysical.animal.ration.ration_manager import RationManager
from RUFAS.biophysical.animal.data_types.animal_manure_excretions import AnimalManureExcretions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream, PenManureData, StreamType
from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID, RequestedFeed, Feed, NutrientStandard
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager


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
def pen(mocker: MockerFixture) -> Pen:
    im = InputManager()
    mocker.patch.object(
        im,
        "get_data",
        return_value=[
            {
                "name": "bedding_1",
                "bedding_type": "sawdust",
                "bedding_mass_per_day": 1.97,
                "bedding_density": 250.0,
                "bedding_dry_matter_content": 0.9,
                "bedding_carbon_fraction": 0.0,
                "bedding_phosphorus_content": 0.0,
                "sand_removal_efficiency": 0.0,
            },
            {
                "name": "bedding_2",
                "bedding_type": "CBPB sawdust",
                "bedding_mass_per_day": 12,
                "bedding_density": 350.0,
                "bedding_dry_matter_content": 0.9,
                "bedding_carbon_fraction": 0.35,
                "bedding_phosphorus_content": 0.0,
                "sand_removal_efficiency": 0.0,
            },
        ],
    )
    return Pen(
        pen_id=1,
        pen_name="Test Pen",
        vertical_dist_to_milking_parlor=12.5,
        horizontal_dist_to_milking_parlor=13.5,
        number_of_stalls=10,
        housing_type="housing_type",
        pen_type="freestall",
        animal_combination=AnimalCombination.LAC_COW,
        max_stocking_density=19.5,
        minutes_away_for_milking=7,
        first_parlor_processor="stream_a",
        parlor_stream_name="test_stream",
        manure_streams=[
            {"stream_name": "general_stream_1", "stream_proportion": 0.6, "bedding_name": "bedding_1"},
            {"stream_name": "general_stream_2", "stream_proportion": 0.4, "bedding_name": "bedding_2"},
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
    assert pen.pen_type == "freestall"
    assert pen.animal_combination == AnimalCombination.LAC_COW
    assert pen.max_stocking_density == 19.5
    assert pen.minutes_away_for_milking == 7
    assert pen.first_parlor_processor == "stream_a"
    assert pen.manure_streams == [
        {"stream_name": "general_stream_1", "stream_proportion": 0.6, "bedding_name": "bedding_1"},
        {"stream_name": "general_stream_2", "stream_proportion": 0.4, "bedding_name": "bedding_2"},
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


def test_total_enteric_methane_sums_animal_emissions(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """total_enteric_methane should return the sum of enteric methane for all animals in the pen."""
    pen.animals_in_pen = animals_in_pen

    result = pen.total_enteric_methane

    expected = 69.4 * len(animals_in_pen)

    assert result == pytest.approx(expected)


def test_total_enteric_methane_zero_when_no_animals(pen: Pen) -> None:
    """total_enteric_methane should be 0.0 when there are no animals in the pen."""
    pen.animals_in_pen = {}

    result = pen.total_enteric_methane

    assert result == 0.0


def test_total_pen_ration_no_animals(pen: Pen) -> None:
    """total_pen_ration should return an empty dict when no animals are housed in the pen."""
    pen.animals_in_pen = {}
    pen.ration = {RUFAS_ID(1): 5.0}

    assert pen.total_pen_ration == {}


def test_total_pen_ration_scales_ration_and_adds_totals(pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """
    Tests that total_pen_ration scales the ration by the number of animals and adds total dry matter
    intake and byproducts.
    """
    pen.animals_in_pen = animals_in_pen
    pen.ration = {RUFAS_ID(1): 5.0, RUFAS_ID(2): 3.0}

    result = pen.total_pen_ration

    expected = {
        "1": 10.0,
        "2": 6.0,
        "dry_matter_intake_total": 16.0,
        "byproducts_total": 40.0,
    }

    assert result == expected


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


def test_initialize_beddings(pen: Pen, mocker: MockerFixture) -> None:
    im = InputManager()
    mock_get_data = mocker.patch.object(
        im,
        "get_data",
        return_value=(
            [
                {
                    "name": "sawdust",
                    "bedding_type": "sawdust",
                    "bedding_mass_per_day": 1.97,
                    "bedding_density": 250.0,
                    "bedding_dry_matter_content": 0.9,
                    "bedding_carbon_fraction": 0.0,
                    "bedding_phosphorus_content": 0.0,
                    "sand_removal_efficiency": 0.0,
                },
                {
                    "name": "CBPB sawdust",
                    "bedding_type": "CBPB sawdust",
                    "bedding_mass_per_day": 12,
                    "bedding_density": 350.0,
                    "bedding_dry_matter_content": 0.9,
                    "bedding_carbon_fraction": 0.35,
                    "bedding_phosphorus_content": 0.0,
                    "sand_removal_efficiency": 0.0,
                },
                {
                    "name": "manure solids",
                    "bedding_type": "manure solids",
                    "bedding_mass_per_day": 2.50,
                    "bedding_density": 400.0,
                    "bedding_dry_matter_content": 0.9,
                    "bedding_carbon_fraction": 0.0,
                    "bedding_phosphorus_content": 0.0,
                    "sand_removal_efficiency": 0.0,
                },
                {
                    "name": "straw",
                    "bedding_type": "straw",
                    "bedding_mass_per_day": 1.97,
                    "bedding_density": 100.0,
                    "bedding_dry_matter_content": 0.9,
                    "bedding_carbon_fraction": 0.35,
                    "bedding_phosphorus_content": 0.0,
                    "sand_removal_efficiency": 0.0,
                },
                {
                    "name": "calf_sand",
                    "bedding_type": "sand",
                    "bedding_mass_per_day": 25.0,
                    "bedding_density": 1500.0,
                    "bedding_dry_matter_content": 0.9,
                    "bedding_carbon_fraction": 0.0,
                    "bedding_phosphorus_content": 0.0,
                    "sand_removal_efficiency": 1.0,
                },
                {
                    "name": "grow_sand",
                    "bedding_type": "sand",
                    "bedding_mass_per_day": 25.0,
                    "bedding_density": 1500.0,
                    "bedding_dry_matter_content": 0.9,
                    "bedding_carbon_fraction": 0.0,
                    "bedding_phosphorus_content": 0.0,
                    "sand_removal_efficiency": 1.0,
                },
                {
                    "name": "closeup_sand",
                    "bedding_type": "sand",
                    "bedding_mass_per_day": 25.0,
                    "bedding_density": 1500.0,
                    "bedding_dry_matter_content": 0.9,
                    "bedding_carbon_fraction": 0.0,
                    "bedding_phosphorus_content": 0.0,
                    "sand_removal_efficiency": 1.0,
                },
                {
                    "name": "lac_sand",
                    "bedding_type": "sand",
                    "bedding_mass_per_day": 25.0,
                    "bedding_density": 1500.0,
                    "bedding_dry_matter_content": 0.9,
                    "bedding_carbon_fraction": 0.0,
                    "bedding_phosphorus_content": 0.0,
                    "sand_removal_efficiency": 1.0,
                },
                {
                    "name": "none",
                    "bedding_type": "none",
                    "bedding_mass_per_day": 0.0,
                    "bedding_density": 0.0,
                    "bedding_dry_matter_content": 0.0,
                    "bedding_carbon_fraction": 0.0,
                    "bedding_phosphorus_content": 0.0,
                    "sand_removal_efficiency": 0.0,
                },
            ]
        ),
    )
    om = OutputManager()
    mock_add_error = mocker.patch.object(om, "add_error")

    dummy_manure_streams: list[dict[str, str | float]] = [
        {"bedding_name": "sawdust", "stream_proportion": 1.0},
        {"bedding_name": "CBPB sawdust", "stream_proportion": 1.0},
        {"bedding_name": "manure solids", "stream_proportion": 1.0},
        {"bedding_name": "straw", "stream_proportion": 1.0},
        {"bedding_name": "calf_sand", "stream_proportion": 1.0},
        {"bedding_name": "grow_sand", "stream_proportion": 1.0},
        {"bedding_name": "closeup_sand", "stream_proportion": 1.0},
        {"bedding_name": "lac_sand", "stream_proportion": 1.0},
        {"bedding_name": "none", "stream_proportion": 1.0},
    ]
    pen.manure_streams = dummy_manure_streams
    pen.beddings = {}

    pen._initialize_beddings()

    mock_add_error.assert_not_called()
    mock_get_data.assert_called_once_with("animal.bedding_configs")
    assert (
        list(pen.beddings.keys()).sort()
        == [manure_stream["bedding_name"] for manure_stream in dummy_manure_streams].sort()
    )


def test_initialize_beddings_key_error(pen: Pen, mocker: MockerFixture) -> None:
    im = InputManager()
    mock_get_data = mocker.patch.object(im, "get_data", return_value=[])
    om = OutputManager()
    mock_add_error = mocker.patch.object(om, "add_error")

    pen.manure_streams = [
        {"bedding_name": "sawdust"},
        {"bedding_name": "CBPB sawdust"},
        {"bedding_name": "manure solids"},
        {"bedding_name": "straw"},
        {"bedding_name": "calf_sand"},
        {"bedding_name": "grow_sand"},
        {"bedding_name": "closeup_sand"},
        {"bedding_name": "lac_sand"},
        {"bedding_name": "none"},
    ]
    pen.beddings = {}

    with pytest.raises(KeyError):
        pen._initialize_beddings()

    mock_add_error.assert_called_once()
    mock_get_data.assert_called_once_with("animal.bedding_configs")


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
    digestive_system = MagicMock(spec=DigestiveSystem)
    digestive_system.configure_mock(
        manure_excretion=AnimalManureExcretions(urine_nitrogen=15), enteric_methane_emission=69.4
    )
    animal_3 = create_autospec(Animal)
    animal_3.configure_mock(
        id=3,
        animal_type=AnimalType.CALF,
        nutrition_supply=mock_supply_1,
        digestive_system=digestive_system,
        feeds_used=[MagicMock(spec=Feed)],
        body_weight=10,
    )
    animal_4 = create_autospec(Animal)
    animal_4.configure_mock(
        id=3,
        animal_type=AnimalType.CALF,
        nutrition_supply=mock_supply_1,
        digestive_system=digestive_system,
        feeds_used=[MagicMock(spec=Feed)],
        body_weight=10,
    )
    animal_3.nutrients = MagicMock(auto_spec=Nutrients)
    animal_4.nutrients = MagicMock(auto_spec=Nutrients)
    mocker.patch.object(animal_3.nutrients, "set_dry_matter_intake")
    mocker.patch.object(animal_3.nutrients, "set_phosphorus_intake")
    mocker.patch.object(animal_4.nutrients, "set_dry_matter_intake")
    mocker.patch.object(animal_4.nutrients, "set_phosphorus_intake")

    new_animals = [animal_3, animal_4]
    pen.animals_in_pen = animals_in_pen
    mock_add = mocker.patch.object(pen, "insert_single_animal_into_animals_in_pen_map")
    mock_supply_2 = MagicMock(auto_spec=NutritionSupply)
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


@pytest.mark.parametrize(
    "animal_combination, manure_streams, expected_result_keys",
    [
        (
            AnimalCombination.LAC_COW,
            [
                {"stream_name": "general_stream_1", "stream_proportion": 0.6, "bedding_name": "bedding_1"},
                {"stream_name": "general_stream_2", "stream_proportion": 0.4, "bedding_name": "bedding_2"},
            ],
            ["test_stream_PEN_1", "general_stream_1_LAC_COW_PEN_1", "general_stream_2_LAC_COW_PEN_1"],
        ),
        (
            AnimalCombination.GROWING,
            [
                {"stream_name": "single_general_stream", "stream_proportion": 1.0, "bedding_name": "bedding_1"},
            ],
            ["single_general_stream_GROWING_PEN_1"],
        ),
        (
            AnimalCombination.GROWING_AND_CLOSE_UP,
            [
                {"stream_name": "single_general_stream", "stream_proportion": 1.0, "bedding_name": "bedding_1"},
            ],
            ["single_general_stream_GROWING_AND_CLOSE_UP_PEN_1"],
        ),
    ],
)
def test_get_manure_streams(
    mocker: MockerFixture,
    animal_combination: AnimalCombination,
    manure_streams: list[dict[str, str | float]],
    expected_result_keys: list[str],
    pen: Pen,
    animals_in_pen: dict[int, Animal],
) -> None:
    """Verify get_manure_streams produces correct keys and calls split_stream with expected args."""

    pen.animals_in_pen = animals_in_pen
    pen.animal_combination = animal_combination
    pen.manure_streams = manure_streams
    pen.first_parlor_processor = "stream_a"
    pen.parlor_stream_name = "test_stream"
    pen.minutes_away_for_milking = 360

    if animal_combination == AnimalCombination.GROWING_AND_CLOSE_UP:
        first_animal = next(iter(animals_in_pen.values()))
        second_animal = list(animals_in_pen.values())[1]
        first_animal.animal_type = AnimalType.HEIFER_I
        second_animal.animal_type = AnimalType.DRY_COW
    apply_bedding_side_effects = [MagicMock(spec=ManureStream) for _ in manure_streams]
    mock_apply_bedding = mocker.patch.object(pen, "_apply_bedding", side_effect=apply_bedding_side_effects)

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

    child_stream = MagicMock(spec=ManureStream)
    child_stream.pen_manure_data = MagicMock(set_first_processor=MagicMock())
    mock_split = mocker.patch.object(
        ManureStream,
        "split_stream",
        autospec=True,
        return_value=child_stream,
    )

    result = pen.get_manure_streams()

    assert list(result.keys()) == expected_result_keys
    assert mock_apply_bedding.call_count == len(manure_streams)

    expected_calls = (
        (1 + len(manure_streams)) if animal_combination == AnimalCombination.LAC_COW else len(manure_streams)
    )
    assert mock_split.call_count == expected_calls

    if animal_combination == AnimalCombination.LAC_COW:
        parlor_call = mock_split.call_args_list[0]
        assert pytest.approx(parlor_call.kwargs["split_ratio"]) == 0.25
        assert parlor_call.kwargs["stream_type"] == StreamType.PARLOR
        assert parlor_call.kwargs["manure_stream_deposition_split"] == 0.0

        non_parlor = 1.0 - 0.25
        for i, call in enumerate(mock_split.call_args_list[1:]):
            prop = float(manure_streams[i]["stream_proportion"])
            expected_split_ratio = prop * non_parlor
            expected_deposition = prop

            assert call.kwargs["stream_type"] == StreamType.GENERAL
            assert pytest.approx(call.kwargs["split_ratio"]) == pytest.approx(expected_split_ratio)
            assert pytest.approx(call.kwargs["manure_stream_deposition_split"]) == pytest.approx(expected_deposition)

    else:
        for i, call in enumerate(mock_split.call_args_list):
            proportion = float(manure_streams[i]["stream_proportion"])
            assert call.kwargs["stream_type"] == StreamType.GENERAL
            assert pytest.approx(call.kwargs["split_ratio"]) == pytest.approx(proportion)
            assert pytest.approx(call.kwargs["manure_stream_deposition_split"]) == pytest.approx(proportion)


@pytest.mark.parametrize(
    "input_manure_stream, bedding_type, expected_result",
    [
        (
            ManureStream(
                water=18.8,
                ammoniacal_nitrogen=23.3,
                nitrogen=15.5,
                phosphorus=8.18,
                potassium=6.6,
                ash=0.88,
                non_degradable_volatile_solids=68.8,
                degradable_volatile_solids=81.8,
                total_solids=258.0,
                volume=12.80,
                methane_production_potential=0.24,
                pen_manure_data=PenManureData(
                    num_animals=10,
                    manure_deposition_surface_area=0.0,
                    animal_combination=AnimalCombination.LAC_COW,
                    pen_type="",
                    manure_urine_mass=0.0,
                    manure_urine_nitrogen=0.0,
                    stream_type=StreamType.GENERAL,
                ),
                bedding_non_degradable_volatile_solids=10,
            ),
            BeddingType.SAND,
            ManureStream(
                water=28.8,
                ammoniacal_nitrogen=23.3,
                nitrogen=15.5,
                phosphorus=35.68,
                potassium=6.6,
                ash=4.02,
                non_degradable_volatile_solids=68.8,
                degradable_volatile_solids=81.8,
                total_solids=261.14,
                volume=15.30,
                methane_production_potential=0.24,
                pen_manure_data=PenManureData(
                    num_animals=10,
                    manure_deposition_surface_area=0.0,
                    animal_combination=AnimalCombination.LAC_COW,
                    pen_type="",
                    manure_urine_mass=0.0,
                    manure_urine_nitrogen=0.0,
                    stream_type=StreamType.GENERAL,
                ),
                bedding_non_degradable_volatile_solids=10,
            ),
        ),
        (
            ManureStream(
                water=18.8,
                ammoniacal_nitrogen=23.3,
                nitrogen=15.5,
                phosphorus=8.18,
                potassium=6.6,
                ash=0.88,
                non_degradable_volatile_solids=68.8,
                degradable_volatile_solids=81.8,
                total_solids=258.0,
                volume=12.80,
                methane_production_potential=0.24,
                pen_manure_data=PenManureData(
                    num_animals=10,
                    manure_deposition_surface_area=0.0,
                    animal_combination=AnimalCombination.LAC_COW,
                    pen_type="",
                    manure_urine_mass=0.0,
                    manure_urine_nitrogen=0.0,
                    stream_type=StreamType.GENERAL,
                ),
                bedding_non_degradable_volatile_solids=10,
            ),
            BeddingType.NONE,
            ManureStream(
                water=28.8,
                ammoniacal_nitrogen=23.3,
                nitrogen=15.5,
                phosphorus=35.68,
                potassium=6.6,
                ash=0.88,
                non_degradable_volatile_solids=68.8,
                degradable_volatile_solids=81.8,
                total_solids=261.14,
                volume=15.30,
                methane_production_potential=0.24,
                pen_manure_data=PenManureData(
                    num_animals=10,
                    manure_deposition_surface_area=0.0,
                    animal_combination=AnimalCombination.LAC_COW,
                    pen_type="",
                    manure_urine_mass=0.0,
                    manure_urine_nitrogen=0.0,
                    stream_type=StreamType.GENERAL,
                ),
                bedding_non_degradable_volatile_solids=10,
            ),
        ),
        (
            ManureStream(
                water=18.8,
                ammoniacal_nitrogen=23.3,
                nitrogen=15.5,
                phosphorus=8.18,
                potassium=6.6,
                ash=0.88,
                non_degradable_volatile_solids=68.8,
                degradable_volatile_solids=81.8,
                total_solids=258.0,
                volume=12.80,
                methane_production_potential=0.24,
                pen_manure_data=PenManureData(
                    num_animals=10,
                    manure_deposition_surface_area=0.0,
                    animal_combination=AnimalCombination.LAC_COW,
                    pen_type="",
                    manure_urine_mass=0.0,
                    manure_urine_nitrogen=0.0,
                    stream_type=StreamType.GENERAL,
                ),
                bedding_non_degradable_volatile_solids=10,
            ),
            BeddingType.CBPB_SAWDUST,
            ManureStream(
                water=28.8,
                ammoniacal_nitrogen=23.3,
                nitrogen=15.5,
                phosphorus=35.68,
                potassium=6.6,
                ash=0.88,
                non_degradable_volatile_solids=68.8,
                degradable_volatile_solids=81.8,
                total_solids=261.14,
                volume=15.30,
                methane_production_potential=0.24,
                pen_manure_data=PenManureData(
                    num_animals=10,
                    manure_deposition_surface_area=0.0,
                    animal_combination=AnimalCombination.LAC_COW,
                    pen_type="",
                    manure_urine_mass=0.0,
                    manure_urine_nitrogen=0.0,
                    stream_type=StreamType.GENERAL,
                ),
                bedding_non_degradable_volatile_solids=10,
            ),
        ),
    ],
)
def test_apply_bedding(
    input_manure_stream: ManureStream,
    bedding_type: BeddingType,
    expected_result: ManureStream,
    pen: Pen,
    mocker: MockerFixture,
) -> None:
    mock_bedding = MagicMock(auto_spec=Bedding)
    mock_bedding.bedding_type = bedding_type
    mock_bedding.bedding_phosphorus_content = 5.5
    pen.beddings = {"dummy_bedding_name": mock_bedding}
    if input_manure_stream.pen_manure_data is not None:
        num_animals = input_manure_stream.pen_manure_data.num_animals

    mock_calculate_bedding_water = mocker.patch.object(mock_bedding, "calculate_bedding_water", return_value=10.0)
    mock_calculate_total_bedding_mass = mocker.patch.object(
        mock_bedding, "calculate_total_bedding_mass", return_value=5.0
    )
    mock_calculate_total_bedding_dry_solids = mocker.patch.object(
        mock_bedding, "calculate_total_bedding_dry_solids", return_value=3.14
    )
    mock_calculate_total_bedding_volume = mocker.patch.object(
        mock_bedding, "calculate_total_bedding_volume", return_value=2.5
    )

    result = pen._apply_bedding(input_manure_stream, "dummy_bedding_name")

    assert pytest.approx(result.water) == expected_result.water
    assert pytest.approx(result.ammoniacal_nitrogen) == expected_result.ammoniacal_nitrogen
    assert pytest.approx(result.nitrogen) == expected_result.nitrogen
    assert pytest.approx(result.phosphorus) == expected_result.phosphorus
    assert pytest.approx(result.potassium) == expected_result.potassium
    assert pytest.approx(result.ash) == expected_result.ash
    assert pytest.approx(result.non_degradable_volatile_solids) == expected_result.non_degradable_volatile_solids
    assert pytest.approx(result.degradable_volatile_solids) == expected_result.degradable_volatile_solids
    assert pytest.approx(result.total_solids) == expected_result.total_solids
    assert pytest.approx(result.volume) == expected_result.volume

    mock_calculate_bedding_water.assert_called_once_with(num_animals)
    mock_calculate_total_bedding_mass.assert_called_once_with(num_animals)
    mock_calculate_total_bedding_volume.assert_called_once_with(num_animals)
    mock_calculate_total_bedding_dry_solids.assert_called_once_with(num_animals)


def test_apply_bedding_value_error(pen: Pen) -> None:
    mock_bedding = MagicMock(auto_spec=Bedding)
    mock_bedding.bedding_type = BeddingType.STRAW
    pen.beddings = {"dummy_bedding_name": mock_bedding}
    manure_stream = ManureStream(
        water=18.8,
        ammoniacal_nitrogen=23.3,
        nitrogen=15.5,
        phosphorus=8.18,
        potassium=6.6,
        ash=0.88,
        non_degradable_volatile_solids=68.8,
        degradable_volatile_solids=81.8,
        total_solids=258.0,
        volume=12.80,
        methane_production_potential=0.24,
        pen_manure_data=None,
        bedding_non_degradable_volatile_solids=10,
    )

    with pytest.raises(ValueError):
        pen._apply_bedding(manure_stream, "dummy_bedding_name")


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
def test_validate_general_manure_stream_proportions(
    manure_streams: list[dict[str, str | float]],
    should_raise: bool,
    pen: Pen,
) -> None:
    pen.manure_streams = manure_streams

    if should_raise:
        with pytest.raises(ValueError, match="Manure stream proportions must sum to 1.0"):
            pen._validate_general_manure_stream_proportions()
    else:
        pen._validate_general_manure_stream_proportions()


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


def _mock_solution(success: bool) -> OptimizeResult:
    """Creates a mock OptimizeResult with specified success status."""
    solution = Mock(spec=OptimizeResult)
    solution.success = success
    solution.x = np.array([1.0])
    return solution


def _mock_feeds() -> list[Feed]:
    return [MagicMock(spec=Feed)]


def test_formulation_lac_cow_success_first_attempt(mocker: MockerFixture, pen: Pen) -> None:
    """LAC_COW: succeeds on first attempt."""
    pen.animal_combination = AnimalCombination.LAC_COW
    pen.ration = {}
    pen.id = 3
    pen.om = MagicMock(spec=OutputManager)

    mocker.patch.object(pen, "reset_milk_production_reduction")
    mocker.patch.object(pen, "_attempt_formulation", return_value=(_mock_solution(True), MagicMock()))
    mocker.patch.object(RationOptimizer, "handle_failed_constraints")
    mocker.patch.object(pen, "_reduce_on_lactation_failure")
    mock_apply = mocker.patch.object(pen, "_apply_successful_solution")

    pen.formulate_optimized_ration(
        True,
        pen_available_feeds=_mock_feeds(),
        temperature=25.0,
        max_daily_feeds={},
        advance_purchase_allowance=MagicMock(),
        total_inventory=MagicMock(),
        simulation_day=1,
    )

    mock_apply.assert_called_once()


def test_formulation_lac_cow_retry_then_success(mocker: MockerFixture, pen: Pen) -> None:
    """LAC_COW: first attempt fails, second succeeds."""
    mocker.patch("RUFAS.biophysical.animal.pen.RationManager.tolerance", 0.0, create=True)

    pen.animal_combination = AnimalCombination.LAC_COW
    pen.ration = {}
    pen.id = 3
    pen.om = MagicMock(spec=OutputManager)

    mocker.patch.object(pen, "reset_milk_production_reduction")
    mocker.patch.object(
        pen,
        "_attempt_formulation",
        side_effect=[(_mock_solution(False), MagicMock()), (_mock_solution(True), MagicMock())],
    )
    mocker.patch.object(pen.ration_optimizer, "handle_failed_constraints")
    mocker.patch.object(pen, "_reduce_on_lactation_failure")
    mock_apply = mocker.patch.object(pen, "_apply_successful_solution")

    pen.formulate_optimized_ration(
        False,
        pen_available_feeds=_mock_feeds(),
        temperature=25.0,
        max_daily_feeds={},
        advance_purchase_allowance=MagicMock(),
        total_inventory=MagicMock(),
        simulation_day=2,
    )

    mock_apply.assert_called_once()


def test_formulation_non_lac_cow_failure_no_previous_ration(mocker: MockerFixture, pen: Pen) -> None:
    """Non-LAC_COW: fails and no previous ration exists, raises error."""
    pen.animal_combination = AnimalCombination.GROWING
    pen.ration = {}
    pen.id = 2
    pen.om = MagicMock(spec=OutputManager)

    mocker.patch.object(pen, "_attempt_formulation", return_value=(_mock_solution(False), MagicMock()))
    mocker.patch.object(pen.ration_optimizer, "handle_failed_constraints")
    mocker.patch.object(pen, "_apply_successful_solution")

    with pytest.raises(ValueError, match="No previous ration available"):
        pen.formulate_optimized_ration(
            False,
            pen_available_feeds=_mock_feeds(),
            temperature=22.0,
            max_daily_feeds={},
            advance_purchase_allowance=MagicMock(),
            total_inventory=MagicMock(),
            simulation_day=3,
        )


def test_formulation_non_lac_cow_failure_with_previous_ration(mocker: MockerFixture, pen: Pen) -> None:
    """Non-LAC_COW: fails but uses previous ration, logs fallback."""
    pen.animal_combination = AnimalCombination.CLOSE_UP
    pen.ration = {1: 2.0}
    pen.id = 3
    pen.om = MagicMock(spec=OutputManager)

    mocker.patch.object(pen, "_attempt_formulation", return_value=(_mock_solution(False), MagicMock()))
    mocker.patch.object(pen.ration_optimizer, "handle_failed_constraints")
    mocker.patch.object(pen, "_apply_successful_solution")

    pen.formulate_optimized_ration(
        False,
        pen_available_feeds=_mock_feeds(),
        temperature=21.0,
        max_daily_feeds={},
        advance_purchase_allowance=MagicMock(),
        total_inventory=MagicMock(),
        simulation_day=4,
    )

    pen.om.add_log.assert_called_once()
    pen.om.add_error.assert_not_called()


def test_formulation_lac_cow_user_defined_dmi_increase_triggers_retry(mocker: MockerFixture, pen: Pen) -> None:
    """LAC_COW + user-defined ration: failed first attempt triggers DMI increase and retry."""
    mocker.patch("RUFAS.biophysical.animal.pen.RationManager.tolerance", 0.0, create=True)

    pen.animal_combination = AnimalCombination.LAC_COW
    pen.ration = {}
    pen.id = 5
    pen.om = MagicMock(spec=OutputManager)
    avg_reqs = MagicMock()
    avg_reqs.dry_matter = 100.0
    avg_reqs.metabolizable_protein = 50.0
    mocker.patch.object(
        type(pen),
        "average_nutrition_requirements",
        new_callable=PropertyMock,
        return_value=avg_reqs,
    )

    mocker.patch.object(pen, "reset_milk_production_reduction")

    failing_solution = _mock_solution(False)
    succeeding_solution = _mock_solution(True)
    mock_attempt = mocker.patch.object(
        pen,
        "_attempt_formulation",
        side_effect=[(failing_solution, MagicMock()), (succeeding_solution, MagicMock())],
    )

    mocker.patch.object(
        pen.ration_optimizer,
        "handle_failed_constraints",
        return_value=["NE_total_constraint"],
    )

    mock_reduce_user_defined = mocker.patch.object(pen, "_reduce_on_lactation_failure_user_defined")
    mock_reduce_auto = mocker.patch.object(pen, "_reduce_on_lactation_failure")
    mock_apply_success = mocker.patch.object(pen, "_apply_successful_solution")
    mock_apply_user_defined = mocker.patch.object(pen, "_apply_user_defined_ration")

    pen.formulate_optimized_ration(
        True,
        pen_available_feeds=_mock_feeds(),
        temperature=25.0,
        max_daily_feeds={},
        advance_purchase_allowance=MagicMock(),
        total_inventory=MagicMock(),
        simulation_day=10,
    )

    assert mock_attempt.call_count == 2
    mock_apply_success.assert_called_once()

    mock_reduce_user_defined.assert_not_called()
    mock_reduce_auto.assert_not_called()
    mock_apply_user_defined.assert_not_called()


def test_formulation_lac_cow_user_defined_reduce_and_fallback_to_user_ration(mocker: MockerFixture, pen: Pen) -> None:
    """
    LAC_COW + user-defined ration: failed formulation triggers user-defined reduce handler,
    then falls back to applying the user-defined ration and logs the event.
    """
    mocker.patch("RUFAS.biophysical.animal.pen.RationManager.tolerance", 0.0, create=True)

    pen.animal_combination = AnimalCombination.LAC_COW
    pen.ration = {}
    pen.id = 6
    pen.om = MagicMock(spec=OutputManager)

    mocker.patch.object(pen, "reset_milk_production_reduction")

    failing_solution = _mock_solution(False)
    mocker.patch.object(
        pen,
        "_attempt_formulation",
        return_value=(failing_solution, MagicMock()),
    )

    mocker.patch.object(
        pen.ration_optimizer,
        "handle_failed_constraints",
        return_value=["some_other_constraint"],
    )

    mock_reduce_user_defined = mocker.patch.object(
        pen,
        "_reduce_on_lactation_failure_user_defined",
        return_value=True,
    )
    mock_reduce_auto = mocker.patch.object(pen, "_reduce_on_lactation_failure")

    mock_apply_success = mocker.patch.object(pen, "_apply_successful_solution")
    mock_apply_user_defined = mocker.patch.object(pen, "_apply_user_defined_ration")

    feeds = _mock_feeds()

    pen.formulate_optimized_ration(
        True,
        pen_available_feeds=feeds,
        temperature=20.0,
        max_daily_feeds={},
        advance_purchase_allowance=MagicMock(),
        total_inventory=MagicMock(),
        simulation_day=11,
    )

    mock_reduce_user_defined.assert_called_once()
    mock_reduce_auto.assert_not_called()
    mock_apply_success.assert_not_called()

    mock_apply_user_defined.assert_called_once()
    (called_feeds,), _ = mock_apply_user_defined.call_args
    assert isinstance(called_feeds, list)
    assert len(called_feeds) == len(feeds)

    pen.om.add_log.assert_called_once()


def test_attempt_formulation(mocker: MockerFixture, pen: Pen, animals_in_pen: dict[int, Animal]) -> None:
    """Tests the function _attempt_formulation"""
    mock_set = mocker.patch.object(pen, "set_animal_nutritional_requirements")
    mock_result = (MagicMock(spec=OptimizeResult), MagicMock(spec=RationConfig))
    mock_attempt = mocker.patch.object(RationOptimizer, "attempt_optimization", return_value=mock_result)
    pen.animals_in_pen = animals_in_pen
    pen.animals_in_pen[1].nutrient_standard = NutrientStandard.NRC
    result = pen._attempt_formulation(
        is_ration_defined_by_user=False,
        pen_feeds=_mock_feeds(),
        temperature=25,
        previous_ration=None,
        initial_dry_matter_requirement=1,
        initial_protein_requirement=1,
    )
    mock_set.assert_called_once()
    mock_attempt.assert_called_once()
    assert result == mock_result


def test_attempt_formulation_user_defined_and_nasem(
    mocker: MockerFixture, pen: Pen, animals_in_pen: dict[int, Animal]
) -> None:
    """Covers user-defined ration path and NASEM nutrient standard averaging."""
    pen.animals_in_pen = animals_in_pen
    for animal in pen.animals_in_pen.values():
        animal.nutrient_standard = NutrientStandard.NASEM

    user_defined_for_combo = {"feed1": 1.0, "feed2": 2.0}
    mocker.patch.object(
        RationManager,
        "user_defined_rations",
        {pen.animal_combination: user_defined_for_combo},
        create=True,
    )
    mocker.patch.object(RationManager, "tolerance", 0.123, create=True)

    avg_reqs = MagicMock()
    avg_reqs.dry_matter = 100.0
    avg_reqs.metabolizable_protein = 50.0
    mocker.patch.object(
        type(pen),
        "average_nutrition_requirements",
        new_callable=PropertyMock,
        return_value=avg_reqs,
    )

    mock_set = mocker.patch.object(pen, "set_animal_nutritional_requirements")
    mock_result = (MagicMock(spec=OptimizeResult), MagicMock(spec=RationConfig))
    mock_attempt = mocker.patch.object(
        RationOptimizer,
        "attempt_optimization",
        return_value=mock_result,
    )

    feeds = _mock_feeds()

    result = pen._attempt_formulation(
        is_ration_defined_by_user=True,
        pen_feeds=feeds,
        temperature=25.0,
        previous_ration={"prev": "ration"},
        initial_dry_matter_requirement=1.5,
        initial_protein_requirement=2.5,
    )

    mock_set.assert_called_once()
    mock_attempt.assert_called_once()
    assert result == mock_result

    _, kwargs = mock_attempt.call_args

    assert kwargs["user_defined_ration_dictionary"] == user_defined_for_combo
    assert kwargs["user_defined_ration_tolerance"] == pytest.approx(0.123)
    assert kwargs["pen_average_enteric_methane"] == pytest.approx(69.4)
    assert kwargs["pen_average_urine_nitrogen"] == pytest.approx(15.0)


def test_apply_successful_solution(mocker: MockerFixture, pen: Pen) -> None:
    """Tests _apply_successful_solution when pen is populated"""
    solution = MagicMock(spec=OptimizeResult)

    mocker.patch.object(pen.ration_optimizer, "make_ration_from_solution", return_value={3: 3.0})
    mocker.patch.object(pen, "set_animal_nutritional_supply")
    mocker.patch.object(NutritionEvaluator, "evaluate_nutrition_supply", return_value=("ignored", "evaluated"))
    mocker.patch.object(NutritionEvaluationResults, "make_empty_evaluation_results")

    mocker.patch.object(type(pen), "average_nutrition_requirements", new_callable=PropertyMock, return_value="req")
    mocker.patch.object(type(pen), "average_nutrition_supply", new_callable=PropertyMock, return_value="supply")
    mocker.patch.object(type(pen), "is_populated", new_callable=PropertyMock, return_value=True)

    pen.animal_combination = AnimalCombination.LAC_COW

    pen._apply_successful_solution(solution, _mock_feeds())

    assert pen.ration == {3: 3.0}
    assert pen.average_nutrition_evaluation == "evaluated"


def test_apply_successful_solution_not_populated(mocker: MockerFixture, pen: Pen) -> None:
    """Tests _apply_successful_solution when pen is not populated"""
    solution = MagicMock(spec=OptimizeResult)

    mocker.patch.object(pen.ration_optimizer, "make_ration_from_solution", return_value="ration")
    mocker.patch.object(pen, "set_animal_nutritional_supply")
    mocker.patch.object(NutritionEvaluator, "evaluate_nutrition_supply", return_value=("ignored", "evaluated"))
    mock_empty = mocker.patch.object(NutritionEvaluationResults, "make_empty_evaluation_results", return_value="empty")

    mocker.patch.object(type(pen), "average_nutrition_requirements", new_callable=PropertyMock, return_value="req")
    mocker.patch.object(type(pen), "average_nutrition_supply", new_callable=PropertyMock, return_value="supply")
    mocker.patch.object(type(pen), "is_populated", new_callable=PropertyMock, return_value=False)

    pen.animal_combination = AnimalCombination.LAC_COW

    pen._apply_successful_solution(solution, _mock_feeds())

    assert str(pen.average_nutrition_evaluation) == "empty"
    mock_empty.assert_called_once()


@pytest.mark.parametrize("is_populated", [True, False])
def test_apply_user_defined_ration_populated_flag_controls_evaluation(
    mocker: MockerFixture, pen: Pen, is_populated: bool
) -> None:
    """_apply_user_defined_ration sets ration, supply, and evaluation depending on is_populated."""
    avg_reqs = MagicMock()
    avg_supply = MagicMock()

    mocker.patch.object(
        type(pen),
        "average_nutrition_requirements",
        new_callable=PropertyMock,
        return_value=avg_reqs,
    )
    mocker.patch.object(
        type(pen),
        "average_nutrition_supply",
        new_callable=PropertyMock,
        return_value=avg_supply,
    )

    mocker.patch.object(type(pen), "is_populated", new_callable=PropertyMock, return_value=is_populated)

    fake_ration = {1: 1.0, 2: 2.0}
    mocker.patch.object(
        RationManager,
        "get_user_defined_ration",
        return_value=fake_ration,
        create=True,
    )

    mock_set_supply = mocker.patch.object(pen, "set_animal_nutritional_supply")

    fake_eval = MagicMock()
    mocker.patch.object(
        NutritionEvaluator,
        "evaluate_nutrition_supply",
        return_value=("ignored", fake_eval),
    )

    feeds = _mock_feeds()

    pen._apply_user_defined_ration(feeds)

    assert pen.ration == fake_ration
    mock_set_supply.assert_called_once_with(feeds_used=feeds, ration_formulation=fake_ration)

    if is_populated:
        assert pen.average_nutrition_evaluation is fake_eval
    else:
        empty_eval = NutritionEvaluationResults.make_empty_evaluation_results()
        assert pen.average_nutrition_evaluation == empty_eval


def test_reduce_on_lactation_failure_low_milk(mocker: MockerFixture, pen: Pen) -> None:
    """Raises error if milk production is below minimum"""
    mock_om = MagicMock()
    mocker.patch.object(type(pen), "average_milk_production", new_callable=PropertyMock, return_value=0.5)
    pen.om = mock_om
    pen.id = 3

    with pytest.raises(ValueError, match="Cannot meet minimum milk production."):
        pen._reduce_on_lactation_failure({"key": "value"})

    mock_om.add_error.assert_called_once_with(
        "Milk production too low", "Check failed_constraint_summary_for_pen_3 to see cause.", {"key": "value"}
    )


def test_reduce_on_lactation_failure_reduction_fails(mocker: MockerFixture, pen: Pen) -> None:
    """Raises error if milk production reduction fails"""
    mock_om = MagicMock()
    mocker.patch.object(
        type(pen),
        "average_milk_production",
        new_callable=PropertyMock,
        return_value=AnimalModuleConstants.MINIMUM_AVG_PEN_MILK + 1,
    )
    mocker.patch.object(pen, "reduce_milk_production", return_value=False)
    pen.om = mock_om
    pen.id = 3

    with pytest.raises(ValueError, match="Milk production reduction limit reached."):
        pen._reduce_on_lactation_failure({"note": "x"})

    mock_om.add_error.assert_called_once_with(
        "Milk production reduction limit reached.",
        "Check failed_constraint_summary_for_pen_3 and consider adjusting input.",
        {"note": "x"},
    )


def test_reduce_on_lactation_failure_success(mocker: MockerFixture, pen: Pen) -> None:
    """No error if milk production is above minimum and reduction succeeds"""
    mocker.patch.object(
        type(pen),
        "average_milk_production",
        new_callable=PropertyMock,
        return_value=AnimalModuleConstants.MINIMUM_AVG_PEN_MILK + 1,
    )
    mocker.patch.object(pen, "reduce_milk_production", return_value=True)
    pen.om = MagicMock()
    pen.id = 2

    pen._reduce_on_lactation_failure({"ok": "yes"})
    pen.om.add_error.assert_not_called()


@pytest.mark.parametrize(
    "avg_milk, reduce_return, expected_return, expected_log_calls",
    [
        # 1. Milk too low → immediate True, one log
        (0.0, None, True, 1),
        # 2. Milk okay but reduce_milk_production() fails → True, one log
        (10.0, False, True, 1),
        # 3. Milk okay + reduction works → False, no logs
        (10.0, True, False, 0),
    ],
    ids=[
        "milk_too_low",
        "reduce_failed",
        "reduce_succeeded",
    ],
)
def test_reduce_on_lactation_failure_user_defined(
    mocker: MockerFixture,
    pen: Pen,
    avg_milk: float,
    reduce_return: bool | None,
    expected_return: bool,
    expected_log_calls: int,
) -> None:
    """Covers all branches of _reduce_on_lactation_failure_user_defined."""
    mocker.patch(
        "RUFAS.biophysical.animal.pen.AnimalModuleConstants.MINIMUM_AVG_PEN_MILK",
        5.0,
    )

    mocker.patch.object(
        type(pen),
        "average_milk_production",
        new_callable=PropertyMock,
        return_value=avg_milk,
    )
    if reduce_return is not None:
        mocker.patch.object(pen, "reduce_milk_production", return_value=reduce_return)

    pen.om = MagicMock()
    info_map = {"class": "Pen"}

    result = pen._reduce_on_lactation_failure_user_defined(info_map)

    assert result == expected_return
    assert pen.om.add_log.call_count == expected_log_calls


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
    mock_get_ration = mocker.patch.object(RationManager, "get_user_defined_ration", return_value={1: 20.3, 2: 40.6})
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


@pytest.mark.parametrize(
    "pen_type, has_cows, expected_area, raises_error",
    [
        ("freestall", True, 3.5, False),
        ("freestall", False, 2.5, False),
        ("tiestall", True, 1.2, False),
        ("tiestall", False, 1.0, False),
        ("bedded pack", True, 5.0, False),
        ("bedded pack", False, 3.0, False),
        ("open lot", True, 5.0, False),
        ("open lot", False, 3.0, False),
        ("dummy", True, None, True),
    ],
)
def test_calculate_manure_surface_area(
    pen: Pen,
    pen_type: str,
    has_cows: bool,
    expected_area: float | None,
    raises_error: bool,
) -> None:
    """Tests _calculate_manure_surface_area() for various pen types and animal combinations."""
    # Arrange
    pen.pen_type = pen_type
    pen.num_stalls = 1
    pen.animal_combination = AnimalCombination.LAC_COW if has_cows else AnimalCombination.GROWING

    # Act & Assert
    if raises_error:
        with pytest.raises(ValueError):
            pen._calculate_manure_surface_area()
    else:
        assert pen._calculate_manure_surface_area() == expected_area
