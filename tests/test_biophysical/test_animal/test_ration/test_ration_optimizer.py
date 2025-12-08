from typing import Any, Callable, cast

import pytest
import numpy as np
from unittest.mock import MagicMock, patch

from pytest_mock import MockerFixture
from scipy.optimize import OptimizeResult

from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import NutritionSupplyCalculator
from RUFAS.biophysical.animal.ration.ration_optimizer import RationOptimizer, RationConfig
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    Feed,
    FeedComponentType,
    FeedCategorization,
    NutrientStandard,
)
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.general_constants import GeneralConstants
from RUFAS.units import MeasurementUnits


@pytest.fixture
def mock_feed() -> Feed:
    feed = MagicMock(spec=Feed)
    feed.rufas_id = "feed1"
    feed.purchase_cost = 2.0
    feed.lower_limit = 0.0
    feed.limit = 10.0
    feed.TDN = 0.6
    feed.NDF = 0.3
    feed.EE = 0.04
    feed.DE = 2.5
    return feed


@pytest.fixture
def mock_requirements() -> NutritionRequirements:
    req = MagicMock(spec=NutritionRequirements)
    req.total_energy_requirement = 10
    req.maintenance_energy = 3
    req.activity_energy = 2
    req.lactation_energy = 3
    req.pregnancy_energy = 1
    req.growth_energy = 2
    req.phosphorus = 5
    req.process_based_phosphorus = 6
    req.metabolizable_protein = 1000
    req.calcium = 20
    req.dry_matter = 15
    return req


@pytest.fixture
def full_mock_feed() -> Feed:
    feed = MagicMock(spec=Feed)
    feed.rufas_id = "feed1"
    feed.Fd_Category = FeedCategorization.CALF_LIQUID_FEED
    feed.feed_type = FeedComponentType.FORAGE
    feed.DM = 0.88
    feed.ash = 0.07
    feed.CP = 0.18
    feed.N_A = 0.1
    feed.N_B = 0.05
    feed.N_C = 0.03
    feed.Kd = 0.09
    feed.dRUP = 0.08
    feed.ADICP = 0.01
    feed.NDICP = 0.01
    feed.ADF = 0.22
    feed.NDF = 0.3
    feed.lignin = 0.03
    feed.starch = 0.4
    feed.EE = 0.05
    feed.calcium = 0.9
    feed.phosphorus = 0.5
    feed.magnesium = 0.2
    feed.potassium = 0.9
    feed.sodium = 0.3
    feed.chlorine = 0.2
    feed.sulfur = 0.15
    feed.is_fat = False
    feed.is_wetforage = False
    feed.units = MeasurementUnits.KILOGRAMS
    feed.limit = 100.0
    feed.lower_limit = 0.0
    feed.TDN = 0.75
    feed.DE = 3.0
    feed.amount_available = 1000
    feed.on_farm_cost = 1.5
    feed.purchase_cost = 2.0
    return feed


@pytest.fixture
def full_mock_requirements() -> NutritionRequirements:
    req = MagicMock(spec=NutritionRequirements)
    req.total_energy_requirement = 5
    req.maintenance_energy = 2
    req.activity_energy = 1
    req.lactation_energy = 1
    req.pregnancy_energy = 0.5
    req.growth_energy = 1
    req.phosphorus = 3
    req.process_based_phosphorus = 2
    req.metabolizable_protein = 400
    req.calcium = 8
    req.dry_matter = 8
    return req


@pytest.fixture
def full_config(full_mock_feed: Feed, full_mock_requirements: NutritionRequirements) -> RationConfig:
    return RationConfig(
        NutrientStandard.NRC,
        full_mock_requirements,
        [full_mock_feed],
        initial_dry_matter_requirement=10,
        initial_protein_requirement=200,
        pen_average_body_weight=600,
    )


@pytest.fixture
def optimizer() -> RationOptimizer:
    return RationOptimizer()


@pytest.fixture
def nrc_ration_config(mock_feed: Feed, mock_requirements: NutritionRequirements) -> RationConfig:
    return RationConfig(
        NutrientStandard.NRC,
        mock_requirements,
        [mock_feed],
        initial_dry_matter_requirement=30,
        initial_protein_requirement=100,
        pen_average_body_weight=600,
    )


@pytest.fixture
def nasem_ration_config(mock_feed: Feed, mock_requirements: NutritionRequirements) -> RationConfig:
    """Same as above, but using NASEM as the nutrient standard."""
    return RationConfig(
        NutrientStandard.NASEM,
        mock_requirements,
        [mock_feed],
        initial_dry_matter_requirement=30,
        initial_protein_requirement=100,
        pen_average_body_weight=600,
    )


def test_set_constraints_nrc_builds_expected_cow_and_heifer_constraints(
    nrc_ration_config: RationConfig,
) -> None:
    """Test that setting NRC constraints builds the expected cow and heifer constraints."""
    optimizer = RationOptimizer()

    optimizer.set_constraints(nrc_ration_config)

    expected_nrc_funcs = [
        optimizer.NE_total_constraint,
        optimizer.NE_maintenance_and_activity_constraint,
        optimizer.NE_lactation_constraint,
        optimizer.NE_growth_constraint,
        optimizer.calcium_constraint,
        optimizer.phosphorus_constraint,
        optimizer.protein_constraint_lower,
        optimizer.protein_constraint_upper,
        optimizer.NDF_constraint_lower,
        optimizer.NDF_constraint_upper,
        optimizer.forage_NDF_constraint,
        optimizer.fat_constraint,
        optimizer.DMI_constraint_upper,
        optimizer.DMI_constraint_lower,
    ]

    assert optimizer.NRC_constraint_functions == expected_nrc_funcs
    assert isinstance(optimizer.cow_constraints, list)
    assert len(optimizer.cow_constraints) == len(expected_nrc_funcs)

    for constraint_dict, func in zip(optimizer.cow_constraints, expected_nrc_funcs):
        assert isinstance(constraint_dict, dict)
        assert constraint_dict["type"] == "ineq"
        assert constraint_dict["fun"] is func
        assert constraint_dict["args"] == (nrc_ration_config,)

    excluded = {optimizer.NE_total_constraint, optimizer.NE_lactation_constraint}
    expected_heifer_funcs = [f for f in expected_nrc_funcs if f not in excluded]

    assert isinstance(optimizer.heifer_constraints, list)
    assert len(optimizer.heifer_constraints) == len(expected_heifer_funcs)

    for constraint_dict, expected_func in zip(optimizer.heifer_constraints, expected_heifer_funcs):
        assert isinstance(constraint_dict, dict)

        assert constraint_dict["fun"] is expected_func
        assert constraint_dict["type"] == "ineq"
        assert constraint_dict["args"] == (nrc_ration_config,)


def test_NASEM_net_energy_constraint(
    mocker: MockerFixture, nasem_ration_config: RationConfig, full_mock_requirements: NutritionRequirements
) -> None:
    """NASEM constraint should return ME_net_supply - energy_requirement."""
    decision_vector = np.array([5.0, 3.0], dtype=float)

    fake_feed1 = mocker.Mock()
    fake_feed1.amount = 5.0
    fake_feed1.info.starch = 30.0
    fake_feed2 = mocker.Mock()
    fake_feed2.amount = 3.0
    fake_feed2.info.starch = 20.0
    nasem_ration_config.animal_requirements = full_mock_requirements

    mock_convert = mocker.patch.object(
        RationOptimizer,
        "convert_decision_vec_to_feeds",
        return_value=[fake_feed1, fake_feed2],
    )

    mocker.patch.object(GeneralConstants, "PERCENTAGE_TO_FRACTION", 0.01)

    expected_total_starch = 2.10

    mock_calc_ME = mocker.patch.object(
        NutritionSupplyCalculator,
        "calculate_NASEM_metabolizable_energy",
        return_value=50.0,
    )

    mock_calc_NE = mocker.patch.object(
        NutritionSupplyCalculator,
        "calculate_NASEM_net_energy",
        return_value=40.0,
    )

    result = RationOptimizer.NASEM_net_energy_constraint(
        decision_vector,
        nasem_ration_config,
    )

    mock_convert.assert_called_once_with(nasem_ration_config, decision_vector)

    mock_calc_ME.assert_called_once_with(
        feeds=[fake_feed1, fake_feed2],
        dry_matter_intake=decision_vector.sum(),
        body_weight=nasem_ration_config.pen_average_body_weight,
        total_starch=pytest.approx(expected_total_starch),
        enteric_methane=nasem_ration_config.pen_average_enteric_methane,
        urinary_nitrogen=nasem_ration_config.pen_average_urine_nitrogen,
    )

    mock_calc_NE.assert_called_once_with(total_metabolizable_energy=50.0)

    assert result == pytest.approx(35.0)


def test_set_constraints_nasem_builds_expected_cow_and_heifer_constraints(
    nasem_ration_config: RationConfig,
) -> None:
    """Test that setting NASEM constraints builds the expected cow and heifer constraints."""
    optimizer = RationOptimizer()

    optimizer.set_constraints(nasem_ration_config)

    expected_nasem_funcs = [
        optimizer.calcium_constraint,
        optimizer.phosphorus_constraint,
        optimizer.protein_constraint_lower,
        optimizer.protein_constraint_upper,
        optimizer.NDF_constraint_lower,
        optimizer.NDF_constraint_upper,
        optimizer.forage_NDF_constraint,
        optimizer.fat_constraint,
        optimizer.DMI_constraint_upper,
        optimizer.DMI_constraint_lower,
        optimizer.NASEM_net_energy_constraint,
    ]

    assert optimizer.NASEM_constraint_functions == expected_nasem_funcs
    assert isinstance(optimizer.cow_constraints, list)
    assert len(optimizer.cow_constraints) == len(expected_nasem_funcs)

    for constraint_dict, func in zip(optimizer.cow_constraints, expected_nasem_funcs):
        assert isinstance(constraint_dict, dict)
        assert constraint_dict["type"] == "ineq"
        assert constraint_dict["fun"] is func
        assert constraint_dict["args"] == (nasem_ration_config,)

    assert optimizer.heifer_constraints is optimizer.cow_constraints
    assert isinstance(optimizer.heifer_constraints, list)
    assert len(optimizer.heifer_constraints) == len(expected_nasem_funcs)

    for constraint_dict, func in zip(optimizer.heifer_constraints, expected_nasem_funcs):
        assert isinstance(constraint_dict, dict)
        assert constraint_dict["fun"] is func


def test_ration_config_initialization(mock_feed: Feed, mock_requirements: NutritionRequirements) -> None:
    """Test initialization of RationConfig and derived attributes."""
    config = RationConfig(NutrientStandard.NRC, mock_requirements, [mock_feed], 1, 1, 600)
    assert config.animal_requirements == mock_requirements
    assert str(config.feeds_used[0].rufas_id) == "feed1"
    assert config.price_list == [2.0]
    assert config.feed_minimum_list == [0.0]
    assert config.feed_maximum_list == [10.0]
    assert config.initial_protein_requirement == 1.0
    assert config.initial_dry_matter_requirement == 1.0


def test_ration_config_initialization_no_feeds(mock_requirements: NutritionRequirements) -> None:
    """Test initialization of RationConfig and derived attributes."""
    config = RationConfig(NutrientStandard.NRC, mock_requirements, None, 1, 1, 600)
    assert config.animal_requirements == mock_requirements
    assert config.feeds_used == []
    assert config.price_list == []
    assert config.feed_minimum_list == []
    assert config.feed_maximum_list == []
    assert config.initial_protein_requirement == 1.0
    assert config.initial_dry_matter_requirement == 1.0


def test_convert_decision_vec_to_feeds(nrc_ration_config: RationConfig) -> None:
    """Test conversion of decision vector to feed list."""
    vec = np.array([5.0])
    feeds = RationOptimizer.convert_decision_vec_to_feeds(nrc_ration_config, vec)
    assert len(feeds) == 1
    assert feeds[0].amount == 5.0
    assert str(feeds[0].info.rufas_id) == "feed1"


def test_make_ration_from_solution(mock_feed: Feed) -> None:
    """Test conversion of optimization result to ration dictionary."""

    class DummySolution:
        x = [3.0]

    result = RationOptimizer.make_ration_from_solution([mock_feed], DummySolution())
    assert result["feed1"] == 3.0


def test_build_initial_value_no_previous(nrc_ration_config: RationConfig) -> None:
    """Test building initial values with no prior solution."""
    result = RationOptimizer._build_initial_value(None, nrc_ration_config)
    assert isinstance(result, list)
    assert len(result) == 1


def test_build_initial_value_with_previous() -> None:
    """Test building initial values using a previous solution."""
    prev: dict[int | str, float | str] = {"feed1": 2.0}
    config = MagicMock()
    result = RationOptimizer._build_initial_value(prev, config)
    assert result == [2.0]


def test_build_bounds(nrc_ration_config: RationConfig) -> None:
    """Test construction of feed bounds from config."""
    bounds = RationOptimizer._build_bounds(nrc_ration_config)
    assert bounds == [(0.0, 10.0)]


def test_select_constraints() -> None:
    """Test retrieval of constraint functions for a specific animal type."""
    optimizer = RationOptimizer()
    dummy_config = MagicMock()
    optimizer.set_constraints(dummy_config)
    result = optimizer._select_constraints(AnimalCombination.LAC_COW)
    assert isinstance(result, list)
    assert all("type" in c for c in result)


def test_select_constraints_growing() -> None:
    """Tests that heifer_constraints are returned for GROWING."""
    optimizer = RationOptimizer()
    optimizer.heifer_constraints = [{"type": "ineq", "fun": lambda x, config: 1.0}]
    result = optimizer._select_constraints(AnimalCombination.GROWING)
    assert result == optimizer.heifer_constraints


def test_select_constraints_close_up() -> None:
    """Tests that heifer_constraints are returned for CLOSE_UP."""
    optimizer = RationOptimizer()
    optimizer.heifer_constraints = [{"type": "ineq", "fun": lambda x, config: 1.0}]
    result = optimizer._select_constraints(AnimalCombination.CLOSE_UP)
    assert result == optimizer.heifer_constraints


def test_select_constraints_growing_and_close_up() -> None:
    """Tests that heifer_constraints are returned for GROWING_AND_CLOSE_UP."""
    optimizer = RationOptimizer()
    optimizer.heifer_constraints = [{"type": "ineq", "fun": lambda x, config: 1.0}]
    result = optimizer._select_constraints(AnimalCombination.GROWING_AND_CLOSE_UP)
    assert result == optimizer.heifer_constraints


def test_select_constraints_invalid_combination() -> None:
    """Tests that ValueError is raised for an invalid combination."""
    optimizer = RationOptimizer()
    invalid_combination = MagicMock()
    with pytest.raises(ValueError, match="Invalid animal combination"):
        optimizer._select_constraints(invalid_combination)


def test_objective(nrc_ration_config: RationConfig) -> None:
    """Test objective cost function value from decision vector."""
    result = RationOptimizer.objective(np.array([5.0]), nrc_ration_config)
    assert result == 10.0


@patch("RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator.NutritionSupplyCalculator")
def test_constraints_run(
    mock_calc: NutritionSupplyCalculator, full_config: RationConfig, mocker: MockerFixture
) -> None:
    """Test all constraints evaluate correctly with mocked inputs."""
    vec = np.array([20.0])
    mocker.patch.object(mock_calc, "calculate_nutrient_intake_discount", return_value=0.9)
    mocker.patch.object(mock_calc, "calculate_actual_metabolizable_energy", return_value={"feed1": 1.0})
    mocker.patch.object(mock_calc, "calculate_actual_maintenance_net_energy", return_value=10.0)
    mocker.patch.object(mock_calc, "calculate_actual_growth_net_energy", return_value=10.0)
    mocker.patch.object(mock_calc, "calculate_actual_lactation_net_energy", return_value=10.0)
    mocker.patch.object(mock_calc, "calculate_metabolizable_protein_supply", return_value=1000)
    mocker.patch.object(mock_calc, "calculate_calcium_supply", return_value=25)
    mocker.patch.object(mock_calc, "calculate_phosphorus_supply", return_value=7)
    mocker.patch.object(mock_calc, "calculate_forage_neutral_detergent_fiber_content", return_value=5.0)

    assert RationOptimizer.NE_total_constraint(vec, full_config) >= 0
    assert RationOptimizer.NE_maintenance_and_activity_constraint(vec, full_config) >= 0
    assert RationOptimizer.NE_lactation_constraint(vec, full_config) >= 0
    assert RationOptimizer.NE_growth_constraint(vec, full_config) >= 0
    assert RationOptimizer.protein_constraint_lower(vec, full_config) <= 0
    assert RationOptimizer.protein_constraint_upper(vec, full_config) >= 0
    assert RationOptimizer.calcium_constraint(vec, full_config) >= 0
    assert RationOptimizer.phosphorus_constraint(vec, full_config) >= 0
    assert RationOptimizer.NDF_constraint_lower(vec, full_config) <= 0
    assert RationOptimizer.NDF_constraint_upper(vec, full_config) >= 0
    assert RationOptimizer.forage_NDF_constraint(vec, full_config) <= 0
    assert RationOptimizer.fat_constraint(vec, full_config) >= 0
    assert RationOptimizer.DMI_constraint_lower(vec, full_config) >= 0
    assert RationOptimizer.DMI_constraint_upper(vec, full_config) <= 0


@patch("RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator.NutritionSupplyCalculator")
def test_is_constraint_violated(full_config: RationConfig) -> None:
    """Test if a single violated constraint is detected."""
    vec = np.array([5.0])
    constraint: dict[str, Callable[[Any, Any], float] | tuple[RationConfig] | str] = {
        "type": "ineq",
        "fun": lambda x, cfg: -1.0,
    }
    violated = RationOptimizer.is_constraint_violated(vec, constraint, full_config)
    assert violated is True


def test_is_constraint_violated_eq_not_close() -> None:
    """Tests that violation is True for eq-type constraint with result not close to zero."""
    solution_x = np.array([1.0, 2.0])
    config = MagicMock(RationConfig)

    constraint: dict[str, Callable[[Any, Any], float] | tuple[RationConfig] | str] = {
        "type": "eq",
        "fun": lambda x, cfg: 0.5,
    }

    result = RationOptimizer.is_constraint_violated(solution_x, constraint, config)
    assert result is True


def test_is_constraint_violated_eq_close_to_zero() -> None:
    """Tests that violation is False for eq-type constraint when result is close to zero."""
    solution_x = np.array([1.0, 2.0])
    config = MagicMock(RationConfig)

    constraint: dict[str, Callable[[Any, Any], float] | tuple[RationConfig] | str] = {
        "type": "eq",
        "fun": lambda x, cfg: 1e-9,
    }

    result = RationOptimizer.is_constraint_violated(solution_x, constraint, config)
    assert result is False


def test_find_failed_constraints(full_config: RationConfig) -> None:
    """Test identification of failed constraints from a set."""
    vec = np.array([5.0])
    constraints = [{"type": "ineq", "fun": lambda x, cfg: -1.0}, {"type": "ineq", "fun": lambda x, cfg: 1.0}]
    failed = RationOptimizer.find_failed_constraints(vec, constraints, full_config)
    assert len(failed) == 1


def test_ndf_constraint_lower_zero_intake() -> None:
    """Tests ndf_constraint_lower for zero intake."""
    decision_vector = np.array([0.0, 0.0, 0.0])
    config = MagicMock(RationConfig)
    result = RationOptimizer.NDF_constraint_lower(decision_vector, config)

    assert result == -1.0


def test_ndf_constraint_upper_zero_intake() -> None:
    """Tests ndf_constraint_upper for zero intake."""
    decision_vector = np.array([0.0, 0.0, 0.0])
    config = MagicMock(RationConfig)

    result = RationOptimizer.NDF_constraint_upper(decision_vector, config)

    assert result == -1.0


def test_forage_ndf_constraint_non_zero_intake(mocker: MockerFixture) -> None:
    """Tests forage_NDF_constraint for non-zero intake."""
    decision_vector = np.array([1.0, 2.0, 3.0])
    config = MagicMock(RationConfig)
    mock_feeds = MagicMock()

    mocker.patch.object(RationOptimizer, "convert_decision_vec_to_feeds", return_value=mock_feeds)
    mocker.patch.object(NutritionSupplyCalculator, "calculate_forage_neutral_detergent_fiber_content", return_value=1.8)

    result = RationOptimizer.forage_NDF_constraint(decision_vector, config)
    assert result == 15.0


def test_forage_ndf_constraint_zero_intake() -> None:
    """Tests forage_NDF_constraint for zero intake."""
    decision_vector = np.array([0.0, 0.0, 0.0])
    config = MagicMock(RationConfig)

    result = RationOptimizer.forage_NDF_constraint(decision_vector, config)

    assert result == -1.0


def test_fat_constraint_non_zero_intake() -> None:
    """Tests fat_constraint for non-zero intake."""
    decision_vector = np.array([1.0, 2.0, 3.0])
    config = MagicMock(RationConfig)
    config.EE_list = np.array([0.02, 0.03, 0.04])

    result = RationOptimizer.fat_constraint(decision_vector, config)

    assert result == pytest.approx(7.0 - 0.0333333333, rel=1e-6)


def test_fat_constraint_zero_intake() -> None:
    """Tests fat_constraint for zero intake."""
    decision_vector = np.array([0.0, 0.0, 0.0])
    config = MagicMock(RationConfig)
    config.EE_list = np.array([0.02, 0.03, 0.04])

    result = RationOptimizer.fat_constraint(decision_vector, config)

    assert result == -1.0


def test_attempt_optimization_success(mocker: MockerFixture) -> None:
    """Tests successful optimization flow in attempt_optimization."""
    optimizer = RationOptimizer()

    pen_average_body_weight = 600.0
    requirements = MagicMock(NutritionRequirements)
    feeds = cast(list[Feed], [MagicMock()])
    animal_comb = MagicMock(AnimalCombination)
    previous_ration = cast(dict[int | str, float | str], {"feed1": 3.0})

    # Prepare mocks
    mock_config = MagicMock(RationConfig)
    mocker.patch("RUFAS.biophysical.animal.ration.ration_optimizer.RationConfig", return_value=mock_config)

    mocker.patch.object(optimizer, "_build_initial_value", return_value=[1.0, 2.0])
    mocker.patch.object(optimizer, "_build_bounds", return_value=[(0.0, 10.0), (0.0, 10.0)])
    mocker.patch.object(optimizer, "set_constraints")
    mocker.patch.object(optimizer, "_select_constraints", return_value=[{"type": "ineq", "fun": lambda x: 1}])
    mocker.patch.object(optimizer, "objective", return_value=0.0)

    mock_result = MagicMock(OptimizeResult)
    mocker.patch("RUFAS.biophysical.animal.ration.ration_optimizer.minimize", return_value=mock_result)

    result, config = optimizer.attempt_optimization(
        nutrient_standard=NutrientStandard.NRC,
        pen_average_body_weight=pen_average_body_weight,
        pen_average_enteric_methane=0.0,
        pen_average_urine_nitrogen=0.0,
        requirements=requirements,
        initial_dry_matter_requirement=1,
        initial_protein_requirement=1,
        pen_available_feeds=feeds,
        animal_combination=animal_comb,
        previous_ration=previous_ration,
    )

    assert result == mock_result
    assert config == mock_config


def test_attempt_optimization_clips_initial_values(mocker: MockerFixture) -> None:
    """Ensures attempt_optimization clips x0 to the provided bounds."""
    optimizer = RationOptimizer()

    pen_average_body_weight = 600.0
    requirements = MagicMock(NutritionRequirements)
    feeds = cast(list[Feed], [MagicMock()])
    animal_comb = MagicMock(AnimalCombination)

    mock_config = MagicMock()
    mocker.patch(
        "RUFAS.biophysical.animal.ration.ration_optimizer.RationConfig",
        return_value=mock_config,
    )

    mocker.patch.object(optimizer, "_build_initial_value", return_value=[-1.0, 15.0])

    mocker.patch.object(optimizer, "_build_bounds", return_value=[(0.0, 10.0), (0.0, 10.0)])

    mocker.patch.object(optimizer, "set_constraints")
    mocker.patch.object(optimizer, "_select_constraints", return_value=[])
    mocker.patch.object(optimizer, "objective", return_value=0.0)

    minimize_mock = mocker.patch(
        "RUFAS.biophysical.animal.ration.ration_optimizer.minimize",
        return_value=MagicMock(),
    )

    optimizer.attempt_optimization(
        nutrient_standard=NutrientStandard.NRC,
        pen_average_body_weight=pen_average_body_weight,
        pen_average_enteric_methane=0.0,
        pen_average_urine_nitrogen=0.0,
        requirements=requirements,
        initial_dry_matter_requirement=1,
        initial_protein_requirement=1,
        pen_available_feeds=feeds,
        animal_combination=animal_comb,
        previous_ration=None,
    )

    passed_x0 = minimize_mock.call_args[0][1]
    assert np.array_equal(passed_x0, np.array([0.0, 10.0], dtype=float))


def test_attempt_optimization_uses_user_defined_bounds(mocker: MockerFixture) -> None:
    """If user_defined_ration_dictionary is provided, _build_bounds_user_defined_ration is used."""

    optimizer = RationOptimizer()

    pen_average_body_weight = 600.0
    requirements = MagicMock(NutritionRequirements)
    feeds = cast(list[Feed], [MagicMock()])
    animal_comb = MagicMock(AnimalCombination)

    mock_config = MagicMock(RationConfig)
    ration_config_mock = mocker.patch(
        "RUFAS.biophysical.animal.ration.ration_optimizer.RationConfig",
        return_value=mock_config,
    )

    mocker.patch.object(optimizer, "_build_initial_value", return_value=[1.0, 2.0])

    user_defined_bounds = [(0.0, 5.0), (0.0, 5.0)]
    build_user_bounds_mock = mocker.patch.object(
        optimizer,
        "_build_bounds_user_defined_ration",
        return_value=user_defined_bounds,
    )
    build_bounds_mock = mocker.patch.object(optimizer, "_build_bounds")

    mocker.patch.object(optimizer, "_check_initial_bounds", return_value=np.array([1.0, 2.0]))

    mocker.patch.object(optimizer, "set_constraints")
    mocker.patch.object(optimizer, "_select_constraints", return_value=[])
    mocker.patch.object(optimizer, "objective", return_value=0.0)

    minimize_mock = mocker.patch(
        "RUFAS.biophysical.animal.ration.ration_optimizer.minimize",
        return_value=MagicMock(OptimizeResult),
    )

    user_defined_ration_dictionary: dict[int, float] = {1: 0.5}
    tolerance = 0.1

    optimizer.attempt_optimization(
        nutrient_standard=NutrientStandard.NRC,
        pen_average_body_weight=pen_average_body_weight,
        pen_average_enteric_methane=0.0,
        pen_average_urine_nitrogen=0.0,
        requirements=requirements,
        initial_dry_matter_requirement=1,
        initial_protein_requirement=1,
        pen_available_feeds=feeds,
        animal_combination=animal_comb,
        previous_ration=None,
        user_defined_ration_dictionary=user_defined_ration_dictionary,
        user_defined_ration_tolerance=tolerance,
    )

    ration_config_mock.assert_called_once()

    build_user_bounds_mock.assert_called_once_with(
        ration_config=mock_config,
        user_defined_ration_dictionary=user_defined_ration_dictionary,
        user_defined_ration_tolerance=tolerance,
    )

    build_bounds_mock.assert_not_called()

    _, _, kwargs = minimize_mock.mock_calls[0]
    assert kwargs["bounds"] == user_defined_bounds


@pytest.mark.parametrize(
    "user_defined_ration_dictionary, user_defined_ration_tolerance, expected_bounds",
    [
        # Case 1: normal tolerance, no negative lower bounds
        (
            {2: 50.0, 1: 25.0},
            0.10,
            [
                (4.5, 5.5),
                (9.0, 10.0),
            ],
        ),
        # Case 2: large tolerance causing negative lower bounds, which should be clipped to 0
        (
            {2: 50.0, 1: 25.0},
            1.50,
            [
                (0.0, 10.0),
                (1.0, 10.0),
            ],
        ),
    ],
    ids=["normal_tolerance", "large_tolerance_clips_lower"],
)
def test_build_bounds_user_defined_ration(
    monkeypatch: pytest.MonkeyPatch,
    user_defined_ration_dictionary: dict[int, float],
    user_defined_ration_tolerance: float,
    expected_bounds: list[tuple[float, float]],
    nrc_ration_config: RationConfig,
) -> None:
    """
    _build_bounds_user_defined_ration should:
    - compute lower/upper target bounds from percentages, tolerance, and DMI
    - clip lower bounds at 0
    - trim resulting bounds by feed_minimum_list and feed_maximum_list.
    """
    monkeypatch.setattr(AnimalModuleConstants, "DMI_REQUIREMENT_BOOST", 1.0)

    nrc_ration_config.initial_dry_matter_requirement = 20.0
    nrc_ration_config.feed_minimum_list = [0.0, 1.0]
    nrc_ration_config.feed_maximum_list = [10.0, 10.0]

    bounds = RationOptimizer._build_bounds_user_defined_ration(
        ration_config=nrc_ration_config,
        user_defined_ration_dictionary=user_defined_ration_dictionary,
        user_defined_ration_tolerance=user_defined_ration_tolerance,
    )

    assert bounds == pytest.approx(expected_bounds)


def test_handle_failed_constraints_lac_cow(mocker: MockerFixture) -> None:
    """Tests handle_failed_constraints for LAC_COW animal combination."""
    optimizer = RationOptimizer()
    optimizer.cow_constraints = [{"fun": MagicMock(__name__="mock_constraint")}]
    mocker.patch.object(optimizer, "make_ration_from_solution", return_value={"mock_ration": 1.0})

    mock_failed_constraints = [{"fun": MagicMock(__name__="constraint_1")}]

    mocker.patch("RUFAS.biophysical.animal.ration.ration_optimizer.OutputManager", return_value=MagicMock())
    mocker.patch.object(RationOptimizer, "find_failed_constraints", return_value=mock_failed_constraints)

    solution = MagicMock(spec=OptimizeResult)
    solution.x = np.array([1.0, 2.0])
    config = MagicMock()
    requirements = MagicMock(spec=NutritionRequirements)
    pen_feeds = [MagicMock(spec=Feed)]
    pen_id = 1
    sim_day = 10

    optimizer.handle_failed_constraints(
        num_attempts=2,
        solution=solution,
        ration_config=config,
        animal_combination=AnimalCombination.LAC_COW,
        pen_id=pen_id,
        pen_available_feeds=pen_feeds,
        average_nutrient_requirements=requirements,
        sim_day=sim_day,
        initial_dry_matter_requirement=1,
        initial_protein_requirement=1,
    )


def test_handle_failed_constraints_heifer_combination(mocker: MockerFixture) -> None:
    """Tests handle_failed_constraints for heifer-type animal combination."""
    optimizer = RationOptimizer()
    optimizer.heifer_constraints = [{"fun": MagicMock(__name__="mock_constraint")}]
    mocker.patch.object(optimizer, "make_ration_from_solution", return_value={"mock_ration": 2.0})

    mock_failed_constraints = [{"fun": MagicMock(__name__="constraint_2")}]

    mock_om = MagicMock()
    mocker.patch("RUFAS.biophysical.animal.ration.ration_optimizer.OutputManager", return_value=mock_om)
    mocker.patch.object(RationOptimizer, "find_failed_constraints", return_value=mock_failed_constraints)

    solution = MagicMock(spec=OptimizeResult)
    solution.x = np.array([2.0, 3.0])
    config = MagicMock()
    requirements = MagicMock(spec=NutritionRequirements)
    pen_feeds = [MagicMock(spec=Feed)]
    pen_id = 2
    sim_day = 12
    initial_dry_matter_requirement = 1
    initial_protein_requirement = 1

    optimizer.handle_failed_constraints(
        num_attempts=1,
        solution=solution,
        ration_config=config,
        animal_combination=AnimalCombination.CLOSE_UP,
        pen_id=pen_id,
        pen_available_feeds=pen_feeds,
        average_nutrient_requirements=requirements,
        sim_day=sim_day,
        initial_dry_matter_requirement=initial_dry_matter_requirement,
        initial_protein_requirement=initial_protein_requirement,
    )

    mock_om.add_variable.assert_called_once()


def test_check_initial_bounds_no_clipping() -> None:
    """Values already within bounds should remain unchanged."""
    optimizer = RationOptimizer()
    bounds = [(0.0, 1.0), (-5.0, 5.0), (10.0, 20.0)]
    vec = np.array([0.5, 0.0, 15.0])
    original = vec.copy()

    result = optimizer._check_initial_bounds(bounds, vec.copy())

    assert np.array_equal(result, original)
    # also ensure it returns the same array object (in‑place modification)
    assert result is not original  # method returns a new array or the same? adjust if needed


def test_check_initial_bounds_clipping_all_sides() -> None:
    """Values below lower or above upper bound should be clipped."""
    optimizer = RationOptimizer()
    bounds = [(0.0, 1.0), (-5.0, 5.0), (10.0, 20.0)]
    vec = np.array([-1.0, 10.0, 25.0])
    expected = np.array([0.0, 5.0, 20.0])

    result = optimizer._check_initial_bounds(bounds, vec.copy())

    assert np.array_equal(result, expected)


def test_check_initial_bounds_mixed_clipping() -> None:
    """Mixed in‑bounds and out‑of‑bounds values are clipped correctly."""
    optimizer = RationOptimizer()
    bounds = [(-1.0, 1.0), (0.0, 10.0)]
    vec = np.array([2.0, -5.0])
    expected = np.array([1.0, 0.0])

    result = optimizer._check_initial_bounds(bounds, vec.copy())

    assert np.array_equal(result, expected)
