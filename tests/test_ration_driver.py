from __future__ import annotations

import pytest
from pytest_mock import MockFixture

from RUFAS.routines.animal.ration.animal_requirements import AnimalRequirements
from RUFAS.routines.animal.ration.ration_driver import RationManager
from RUFAS.routines.animal.ration.ration_optimizer import RationOptimizer


@pytest.mark.parametrize(
    "udr_or_not", [
        True,
        False
    ])
def test_formulate_ration(mocker: MockFixture, udr_or_not: bool) -> None:
    """
    Unit test for formulate_ration() method in RationManager class.
    """

    # Arrange
    ration_optimizer = RationOptimizer()
    mock_pen = mocker.MagicMock()
    mock_available_feeds = mocker.MagicMock()
    mock_animal_grouping_scenario = mocker.MagicMock()

    mocker.patch("RUFAS.routines.animal.ration.ration_driver.udrm.udr_or_not", udr_or_not)
    mock_requirements = mocker.MagicMock()
    mocked_get_or_update_animal_requirements = mocker.patch.object(RationManager, '_get_or_update_animal_requirements',
                                                                   return_value=mock_requirements)
    mock_user_defined_ration = mocker.MagicMock()
    mocked_get_user_defined_ration = mocker.patch.object(RationManager, 'get_user_defined_ration',
                                                         return_value=mock_user_defined_ration)
    mock_solution = mocker.MagicMock()
    mock_ration_vals = mocker.MagicMock()
    mocked_attempt_ration_optimization = mocker.patch.object(RationManager, '_attempt_ration_optimization',
                                                             return_value=(mock_solution, mock_ration_vals))
    mock_final_ration = mocker.MagicMock()
    mocked_decide_final_ration = mocker.patch.object(RationManager, '_decide_final_ration',
                                                     return_value=mock_final_ration)

    # Act
    result = RationManager.formulate_ration(ration_optimizer, mock_pen, mock_available_feeds,
                                            mock_animal_grouping_scenario)

    # Assert
    mocked_get_or_update_animal_requirements.assert_called_once()

    if udr_or_not:
        mocked_get_user_defined_ration.assert_called_once()
        assert result == mock_user_defined_ration
    else:
        mocked_get_user_defined_ration.assert_not_called()
        mocked_attempt_ration_optimization.assert_called_once()
        mocked_decide_final_ration.assert_called_once()
        assert result == (mock_final_ration, mock_ration_vals)


@pytest.mark.parametrize("given_req", [
    None,
    AnimalRequirements()
])
def test_get_or_update_animal_requirements(mocker: MockFixture, given_req: AnimalRequirements | None):
    """
    Unit test for the _get_or_update_animal_requirements method in RationManager class.

    This test verifies that the method correctly retrieves or updates the animal requirements
    based on whether a previous instance of AnimalRequirements is provided or not.
    """

    # Arrange
    mock_pen = mocker.MagicMock()
    mock_animal_grouping_scenario = mocker.MagicMock()
    mock_animal_requirements = mocker.MagicMock()

    if given_req:
        mocked_set_requirements = mocker.patch.object(given_req, 'set_requirements')
    else:
        mocker.patch('RUFAS.routines.animal.ration.ration_driver.AnimalRequirements',
                     return_value=mock_animal_requirements)
        mocked_set_requirements = mock_animal_requirements.set_requirements

    # Act
    result = RationManager._get_or_update_animal_requirements(mock_pen, mock_animal_grouping_scenario, given_req)

    # Assert
    if given_req:
        assert result == given_req
    else:
        assert result == mock_animal_requirements
    mocked_set_requirements.assert_called_once()


@pytest.mark.parametrize("initial_success, animal_combination_name, reattempt_success", [
    (True, "LAC_COW", None),
    (True, "OTHER_ANIMAL", None),
    (False, "LAC_COW", True),
    (False, "LAC_COW", False),
    (False, "OTHER_ANIMAL", None),
    (False, "OTHER_ANIMAL", None),
])
def test_attempt_ration_optimization(mocker: MockFixture,
                                     initial_success: bool,
                                     animal_combination_name: str,
                                     reattempt_success: bool | None) -> None:
    """
    Unit test for the _attempt_ration_optimization method in RationManager class.

    This test verifies that the method:
    1. Returns the correct solution when the optimization is successful.
    2. Doesn't attempt re-optimization for animals other than 'LAC_COW'.
    3. Retries optimization for 'LAC_COW' if the initial attempt fails.
    """

    # Arrange
    mock_ration_optimizer = mocker.MagicMock()
    mock_req = mocker.MagicMock()
    mock_pen = mocker.MagicMock()
    mock_available_feeds = mocker.MagicMock()
    mock_animal_grouping_scenario = mocker.MagicMock()

    mock_pen.animal_combination.name = animal_combination_name

    mock_solution = mocker.MagicMock()
    mock_solution.success = initial_success
    mock_initial_ration_vals = mocker.MagicMock()
    mock_ration_config = mocker.MagicMock()
    mock_ration_optimizer.attempt_optimization.return_value = (
        mock_solution, mock_initial_ration_vals, mock_ration_config)

    mock_reattempt_solution = mocker.MagicMock()
    mock_reattempt_solution.success = reattempt_success
    mock_subsequent_ration_vals = mocker.MagicMock()
    mocked_reattempt_optimization = mocker.patch \
        .object(RationManager, '_reattempt_ration_optimization_for_lactating_cows',
                return_value=(mock_reattempt_solution, mock_subsequent_ration_vals))

    # Act
    result_solution, result_ration_vals = RationManager._attempt_ration_optimization(
        mock_ration_optimizer, mock_req, mock_pen, mock_available_feeds, mock_animal_grouping_scenario)

    # Assert
    mock_ration_optimizer.attempt_optimization.assert_called_once()

    if not initial_success and animal_combination_name == "LAC_COW":
        assert result_solution == mock_reattempt_solution
        assert result_ration_vals == mock_subsequent_ration_vals
        mocked_reattempt_optimization.assert_called_once()
    else:
        assert result_solution == mock_solution
        assert result_ration_vals == mock_initial_ration_vals


@pytest.mark.parametrize("successful_attempts, max_retries", [
    ([False, False, False, False, False], 5),  # All reattempts fail
    ([False, False, True], 5),  # Succeeds on the third attempt
    ([True], 5)  # Succeeds on the first reattempt
])
def test_reattempt_ration_optimization_for_lactating_cows(mocker: MockFixture,
                                                          successful_attempts: list[bool],
                                                          max_retries: int):
    """
    Unit test for the _reattempt_ration_optimization_for_lactating_cows() method in RationManager class.
    """

    # Arrange
    mock_ration_optimizer = mocker.MagicMock()
    mock_pen = mocker.MagicMock()
    mock_available_feeds = mocker.MagicMock()
    mock_animal_grouping_scenario = mocker.MagicMock()
    mock_req = mocker.MagicMock()
    mock_solution = mocker.MagicMock()
    mock_solution.success = False  # Initial solution is always a failure
    mock_ration_config = mocker.MagicMock()
    mock_reattempt_solutions = [mocker.MagicMock(success=success) for success in successful_attempts]
    mock_ration_vals = mocker.MagicMock()

    mocker.patch.object(RationManager, "MAX_OPT_REATTEMPTS", max_retries)
    mock_failed_constraint_names = mocker.MagicMock()
    mocked_find_failed_constraint_names = mocker.patch \
        .object(RationManager, "_find_failed_constraint_names", return_value=mock_failed_constraint_names)
    mocked_log_failed_attempt = mocker.patch.object(RationManager, "_log_failed_ration_optimization_attempt")
    mocked_handle_failure = mocker.patch \
        .object(RationManager,
                "_handle_failed_ration_optimization_attempt_for_lactating_cows",
                side_effect=[(mock_reattempt_solutions[i], mock_ration_vals) for i in
                             range(len(successful_attempts))])

    # Act
    result_solution, result_ration_vals = RationManager._reattempt_ration_optimization_for_lactating_cows(
        mock_ration_optimizer, mock_pen, mock_available_feeds, mock_animal_grouping_scenario, mock_req, mock_solution,
        mock_ration_config)

    # Assert
    assert mocked_find_failed_constraint_names.call_count == len(successful_attempts)
    assert mocked_log_failed_attempt.call_count == len(successful_attempts)
    assert mocked_handle_failure.call_count == len(successful_attempts)
    assert result_ration_vals == mock_ration_vals
    if any(successful_attempts):
        assert result_solution.success
        assert result_solution == mock_reattempt_solutions[successful_attempts.index(True)]
    else:
        assert not result_solution.success
        assert result_solution == mock_reattempt_solutions[-1]


def test_handle_failed_ration_optimization_attempt_for_lactating_cows(mocker: MockFixture):
    """
    Unit test the _handle_failed_ration_optimization_attempt_for_lactating_cows() method in RationManager class.
    """

    # Arrange
    mock_ration_optimizer = mocker.MagicMock()
    mock_pen = mocker.MagicMock()
    mock_available_feeds = mocker.MagicMock()
    mock_animal_grouping_scenario = mocker.MagicMock()
    mock_req = mocker.MagicMock()

    mock_solution = mocker.MagicMock()
    mock_ration_vals = mocker.MagicMock()
    mock_new_req = mocker.MagicMock()

    mocked_reduce_milk_production = mocker.patch.object(RationManager, "reduce_milk_production")
    mocked_get_or_update_animal_requirements = mocker.patch.object(
        RationManager, "_get_or_update_animal_requirements", return_value=mock_new_req)
    mock_ration_optimizer.attempt_optimization.return_value = (mock_solution, mock_ration_vals, mocker.MagicMock())

    # Act
    result_solution, result_ration_vals = RationManager._handle_failed_ration_optimization_attempt_for_lactating_cows(
        mock_ration_optimizer, mock_pen, mock_available_feeds, mock_animal_grouping_scenario, mock_req)

    # Assert
    mocked_reduce_milk_production.assert_called_once()
    mocked_get_or_update_animal_requirements.assert_called_once()
    mock_ration_optimizer.attempt_optimization.assert_called_once()
    assert result_solution == mock_solution
    assert result_ration_vals == mock_ration_vals


@pytest.mark.parametrize(
    "failed_constraints_names, expected_result",
    [
        (["constraint_name_1", "constraint_name_2"], ["constraint_name_1", "constraint_name_2"]),
        ([], []),
        (["constraint_name_1"], ["constraint_name_1"])
    ]
)
def test_find_failed_constraint_names(mocker: MockFixture, failed_constraints_names, expected_result):
    """
    Unit test for the _find_failed_constraint_names() method in RationManager class.
    """

    # Arrange
    mock_ration_optimizer = mocker.MagicMock()
    mock_solution = mocker.MagicMock()
    mock_ration_config = mocker.MagicMock()

    failed_constraints = [{"fun": mocker.MagicMock(__name__=name)} for name in failed_constraints_names]

    mock_ration_optimizer.find_failed_constraints.return_value = failed_constraints

    # Act
    result = RationManager._find_failed_constraint_names(mock_ration_optimizer, mock_solution, mock_ration_config)

    # Assert
    mock_ration_optimizer.find_failed_constraints.assert_called_once()
    assert result == expected_result


@pytest.mark.parametrize(
    "sim_day, reattempt_number, constraint_names, pen_id",
    [
        (5, 1, ["constraint_name_1"], 42),
        (10, 3, ["constraint_name_1", "constraint_name_2"], 7),
        (20, 2, [], 15)
    ]
)
def test_log_failed_ration_optimization_attempt(mocker: MockFixture,
                                                sim_day: int, reattempt_number: int,
                                                constraint_names: list[str], pen_id: int):
    """
    Unit test for the _log_failed_ration_optimization_attempt() method in RationManager class.
    """

    # Arrange
    mock_ration_optimizer = mocker.MagicMock()
    mock_avg_nutrient_rqmts = mocker.MagicMock()
    mock_pen = mocker.MagicMock(id=pen_id, avg_nutrient_rqmts=mock_avg_nutrient_rqmts)
    mock_solution = mocker.MagicMock()
    mock_available_feeds = mocker.MagicMock()

    body_weight_history_mock = mocker.MagicMock(simulation_day=sim_day)
    mock_pen.animals_in_pen = [mocker.MagicMock(body_weight_history=[body_weight_history_mock])]

    mock_ration_string = "mocked_ration"
    mocked_make_ration_from_solution = mocker.patch.object(
        RationManager, "make_ration_from_solution", return_value=mock_ration_string)
    mocked_add_variable = mocker.patch("RUFAS.routines.animal.ration.ration_driver.OutputManager.add_variable")

    # Act
    RationManager._log_failed_ration_optimization_attempt(
        mock_ration_optimizer, mock_pen, reattempt_number, constraint_names, mock_solution, mock_available_feeds)

    # Assert
    expected_fail_summary = {
        'simulation day': sim_day,
        'reattempt number': reattempt_number,
        'constraints_failed_dict': constraint_names,
        'ration_attempted': mock_ration_string,
        'pen requirements': mock_pen.avg_nutrient_rqmts
    }
    expected_info_map = {
        "class": "RationManager",
        "function": "_log_failed_ration_optimization_attempt"
    }
    mocked_add_variable.assert_called_once_with(
        f'failed_constraint_summary_for_pen_{pen_id}', expected_fail_summary, expected_info_map)


@pytest.mark.parametrize(
    "solution_provided",
    [
        True,
        False
    ]
)
def test_decide_final_ration(mocker: MockFixture, solution_provided: bool) -> None:
    """
    Unit test for the _decide_final_ration() method in RationManager class.
    """

    # Arrange
    mock_ration_optimizer = mocker.MagicMock()
    mock_previous_ration = mocker.MagicMock()
    mock_pen = mocker.MagicMock(ration=mock_previous_ration)
    mock_available_feeds = mocker.MagicMock()
    mock_solution = mocker.MagicMock() if solution_provided else None
    mocked_ration_from_solution = mocker.MagicMock()
    if solution_provided:
        mocked_make_ration_from_solution = mocker.patch.object(
            RationManager, "make_ration_from_solution", return_value=mocked_ration_from_solution)

    # Act
    result = RationManager._decide_final_ration(mock_ration_optimizer, mock_pen, mock_available_feeds, mock_solution)

    # Assert
    if solution_provided:
        mocked_make_ration_from_solution.assert_called_once()
        assert result == mocked_ration_from_solution
    else:
        assert result == mock_previous_ration
