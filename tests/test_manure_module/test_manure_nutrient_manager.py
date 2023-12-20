from __future__ import annotations

import re

import pytest
from pytest_mock import MockerFixture
from RUFAS.routines.manure.manure_treatments.manure_types import ManureType

from RUFAS.routines.manure.manure_nutrients.manure_nutrient_manager import ManureNutrientManager
from RUFAS.routines.manure.manure_nutrients.manure_nutrients import ManureNutrients
from RUFAS.routines.manure.manure_nutrients.nutrient_request import NutrientRequest
from RUFAS.routines.manure.manure_nutrients.nutrient_request_results import NutrientRequestResults


@pytest.mark.parametrize('manure_type', [
    ManureType.LIQUID,
    ManureType.SOLID
])
def test_add_nutrients(manure_type: ManureType) -> None:
    """
    Unit test for the add_nutrients() method of the ManureNutrientManager class
    in the manure_nutrient_manager.py file.

    This test verifies that the add_nutrients() method adds a ManureNutrients object
    to the internal data of a ManureNutrientManager object.

    """
    # Arrange
    manager = ManureNutrientManager()
    nutrients = ManureNutrients(nitrogen=1, phosphorus=1, total_manure_mass=2, dry_matter=2,
                                manure_type=manure_type)

    # Act
    manager.add_nutrients(nutrients)

    # Assert
    assert manager.get_values(manure_type) == nutrients


@pytest.mark.parametrize('eval_return, expected_result, remove_called', [
    (NutrientRequestResults(nitrogen=1, phosphorus=1, total_manure_mass=2, dry_matter=2, dry_matter_fraction=0.5),
     NutrientRequestResults(nitrogen=1, phosphorus=1, total_manure_mass=2, dry_matter=2, dry_matter_fraction=0.5),
     True),
    (None, None, False)
])
def test_request_nutrients(mocker: MockerFixture, eval_return: NutrientRequestResults,
                           expected_result: NutrientRequestResults, remove_called: bool) -> None:
    """
    Unit test for the request_nutrients() method of the ManureNutrientManager class in the
    manure_nutrient_manager.py file.

    This test verifies that the request_nutrients() method calls the _evaluate_nutrient_request()
    method and the _remove_nutrients() method when the _evaluate_nutrient_request() method returns
    a NutrientRequestResults object.

    It also verifies that the request_nutrients() method does not
    call the _remove_nutrients() method when the _evaluate_nutrient_request() method returns None.

    """
    # Arrange
    manager = ManureNutrientManager()
    dummy_manure_type = ManureType.LIQUID
    nutrient_request = NutrientRequest(nitrogen=1, phosphorus=1, manure_type=dummy_manure_type)

    patch_for_evaluate_nutrient_request = mocker.patch.object(
        manager, '_evaluate_nutrient_request', return_value=eval_return)
    patch_for_remove_nutrients = mocker.patch.object(manager, '_remove_nutrients')

    # Act
    actual_result = manager.request_nutrients(nutrient_request)

    # Assert
    patch_for_evaluate_nutrient_request.assert_called_once_with(nutrient_request)

    if remove_called:
        patch_for_remove_nutrients.assert_called_once_with(expected_result, dummy_manure_type)
    else:
        patch_for_remove_nutrients.assert_not_called()

    assert actual_result == expected_result


@pytest.mark.parametrize(
    'projected_manure_mass, manure_type, current_nutrient_values, expected_no_results',
    [
        # Scenario when there is no projected manure mass
        (0, ManureType.LIQUID, ManureNutrients(manure_type=ManureType.LIQUID), True),

        # Scenario when projected manure mass is greater than the total manure mass
        (10, ManureType.LIQUID, ManureNutrients(nitrogen=2, phosphorus=2, total_manure_mass=5, dry_matter=1,
                                                manure_type=ManureType.LIQUID), False),

        # Scenario when projected manure mass is less than the total manure mass
        (2, ManureType.SOLID, ManureNutrients(nitrogen=1, phosphorus=1, total_manure_mass=3, dry_matter=1,
                                              manure_type=ManureType.SOLID), False),

        # Scenario when projected manure mass is equal to the total manure mass
        (5, ManureType.SOLID, ManureNutrients(nitrogen=2, phosphorus=2, total_manure_mass=5, dry_matter=1,
                                              manure_type=ManureType.SOLID), False)
    ]
)
def test_evaluate_nutrient_request(mocker: MockerFixture, projected_manure_mass: float,
                                   manure_type: ManureType,
                                   current_nutrient_values: ManureNutrients,
                                   expected_no_results: bool) -> None:
    """
    Unit test for the _evaluate_nutrient_request() method of the ManureNutrientManager class in the
    manure_nutrient_manager.py file.

    This test verifies that the _evaluate_nutrient_request() method correctly calls the
    _calculate_projected_manure_mass(), _select_projected_manure_mass() and _create_nutrient_request_results()
    methods and returns the expected results based on different combinations of projected_manure_mass
    and current_nutrient_values.

    """
    # Arrange
    manager = ManureNutrientManager()
    manager.add_nutrients(current_nutrient_values)

    nitrogen_derived_manure_mass = mocker.MagicMock()
    phosphorus_derived_manure_mass = mocker.MagicMock()
    patch_for_calculate_projected_manure_mass = mocker.patch.object(
        manager, '_calculate_projected_manure_mass',
        side_effect=[nitrogen_derived_manure_mass, phosphorus_derived_manure_mass])

    patch_for_select_projected_manure_mass = mocker.patch.object(
        manager, '_select_projected_manure_mass', return_value=projected_manure_mass)
    expected_request_result = mocker.MagicMock() if not expected_no_results else None
    patch_for_create_nutrient_request_results = mocker.patch.object(
        manager, '_create_nutrient_request_results',
        return_value=expected_request_result)

    mock_nutrient_request = mocker.MagicMock()
    mock_nutrient_request.nitrogen = requested_nitrogen = 1
    mock_nutrient_request.phosphorus = requested_phosphorus = 1
    mock_nutrient_request.manure_type = manure_type

    # Act
    actual_result = manager._evaluate_nutrient_request(mock_nutrient_request)

    # Assert
    patch_for_calculate_projected_manure_mass.assert_any_call(requested_nitrogen,
                                                              current_nutrient_values.nitrogen_composition)
    patch_for_calculate_projected_manure_mass.assert_any_call(requested_phosphorus,
                                                              current_nutrient_values.phosphorus_composition)

    patch_for_select_projected_manure_mass.assert_called_once_with(
        [nitrogen_derived_manure_mass, phosphorus_derived_manure_mass])

    if expected_no_results:
        patch_for_create_nutrient_request_results.assert_not_called()
    elif projected_manure_mass <= current_nutrient_values.total_manure_mass:
        patch_for_create_nutrient_request_results.assert_called_once_with(projected_manure_mass, manure_type)
    else:
        patch_for_create_nutrient_request_results.assert_called_once_with(current_nutrient_values.total_manure_mass,
                                                                          manure_type)

    assert actual_result == expected_request_result


@pytest.mark.parametrize(
    'request_nutrient, nutrient_composition, expected_result',
    [
        # Scenario when nutrient composition > 0 and request > 0
        (2.0, 0.5, 4.0),

        # Scenario when nutrient composition > 0 and request = 0
        (0, 0.5, 0),

        # Scenario when nutrient composition = 0
        (2.0, 0, 0),
    ]
)
def test_calculate_projected_manure_mass(request_nutrient: float, nutrient_composition: float,
                                         expected_result: float) -> None:
    """
    Unit test for the method _calculate_projected_manure_mass() of the ManureNutrientManager class in the
    manure_nutrient_manager.py file.

    This test verifies that the _calculate_projected_manure_mass() method correctly calculates
    the projected manure mass based on different combinations of nutrient request and nutrient composition.

    """
    # Act
    actual_result = ManureNutrientManager._calculate_projected_manure_mass(
        request_nutrient, nutrient_composition)

    # Assert
    assert actual_result == expected_result


@pytest.mark.parametrize(
    'request_nutrient, nutrient_composition, expected_exception, expected_error_msg',
    [
        # Scenario when request_nutrient is negative
        (-2.0, 0.5, ValueError, 'Request for nutrient cannot be negative: -2.0'),

        # Scenario when nutrient composition is negative
        (2.0, -1.0, ValueError, 'Nutrient composition must be between 0 and 1 (inclusive): -1.0'),

        # Scenario when nutrient composition and request are both negative
        (-2.0, -1.0, ValueError, 'Request for nutrient cannot be negative: -2.0'),

        # Scenario when nutrient composition is above 1
        (2.0, 1.5, ValueError, 'Nutrient composition must be between 0 and 1 (inclusive): 1.5'),
    ]
)
def test_calculate_projected_manure_mass_exceptions(request_nutrient: float, nutrient_composition: float,
                                                    expected_exception: type[Exception],
                                                    expected_error_msg: str) -> None:
    """
    Unit test for the method _calculate_projected_manure_mass() of the ManureNutrientManager class in the
    manure_nutrient_manager.py file.

    This test verifies that the _calculate_projected_manure_mass() method raises appropriate exceptions
    with correct messages for negative values and for nutrient composition values not in the range [0, 1].

    """
    # Act & Assert
    with pytest.raises(expected_exception, match=re.escape(expected_error_msg)):
        ManureNutrientManager._calculate_projected_manure_mass(request_nutrient, nutrient_composition)


@pytest.mark.parametrize(
    'projected_manure_masses, expected_result',
    [
        # Scenario when all masses are positive
        ([330, 315, 300], 300),

        # Scenario when one mass is zero
        ([330, 315, 0], 315),

        # Scenario when all masses are zero
        ([0, 0, 0], 0),
    ]
)
def test_select_projected_manure_mass(projected_manure_masses: list[float], expected_result: float) -> None:
    """
    Unit test for the method _select_projected_manure_mass() of the ManureNutrientManager class in the
    manure_nutrient_manager.py file.

    This test verifies that the _select_projected_manure_mass() method correctly selects
    the smallest positive mass or zero if all masses are zero.

    """
    # Act
    actual_result = ManureNutrientManager._select_projected_manure_mass(projected_manure_masses)

    # Assert
    assert actual_result == expected_result


@pytest.mark.parametrize(
    'projected_manure_masses, expected_exception, expected_error_msg',
    [
        # Scenario when one mass is negative
        ([330, 315, -300], ValueError, 'Projected manure mass cannot be negative: -300'),
    ]
)
def test_select_projected_manure_mass_exceptions(projected_manure_masses: list[float],
                                                 expected_exception: type[Exception],
                                                 expected_error_msg: str) -> None:
    """
    Unit test for the method _select_projected_manure_mass() of the ManureNutrientManager class in the
    manure_nutrient_manager.py file.

    This test verifies that the _select_projected_manure_mass() method raises appropriate exceptions
    with correct messages for negative masses.

    """
    # Act & Assert
    with pytest.raises(expected_exception, match=expected_error_msg):
        ManureNutrientManager._select_projected_manure_mass(projected_manure_masses)


@pytest.mark.parametrize(
    'projected_manure_mass, manure_type, nutrients',
    [
        # Scenario when projected manure mass is zero
        (0.0, ManureType.LIQUID, ManureNutrients(nitrogen=1, phosphorus=1, total_manure_mass=2, dry_matter=1,
                                                 manure_type=ManureType.LIQUID)),

        # Scenario when projected manure mass is very small
        (1e-8, ManureType.LIQUID, ManureNutrients(nitrogen=1, phosphorus=1, total_manure_mass=2, dry_matter=1,
                                                  manure_type=ManureType.LIQUID)),

        # Scenario when projected manure mass is large
        (1e6, ManureType.LIQUID, ManureNutrients(nitrogen=1, phosphorus=1, total_manure_mass=2, dry_matter=1,
                                                 manure_type=ManureType.LIQUID)),

        # Scenario when nutrient compositions are zero
        (2.0, ManureType.SOLID, ManureNutrients(nitrogen=0, phosphorus=0, total_manure_mass=0, dry_matter=0,
                                                manure_type=ManureType.SOLID)),

        # Scenario when nutrient values are large
        (2.0, ManureType.SOLID, ManureNutrients(nitrogen=1e6, phosphorus=1e6, total_manure_mass=1e6, dry_matter=1e6,
                                                manure_type=ManureType.SOLID)),

        # Normal scenario when projected manure mass is > 0
        (2.0, ManureType.SOLID, ManureNutrients(nitrogen=1, phosphorus=2, total_manure_mass=4, dry_matter=1,
                                                manure_type=ManureType.SOLID)),
    ]
)
def test_create_nutrient_request_results(projected_manure_mass: float, manure_type: ManureType, nutrients: ManureNutrients) -> None:
    """
    Unit test for the _create_nutrient_request_results() method of the ManureNutrientManager class in the
    manure_nutrient_manager.py file.

    This test verifies that the _create_nutrient_request_results() method correctly creates a NutrientRequestResults
    object based on the projected manure mass.

    """
    # Arrange
    manager = ManureNutrientManager()
    manager.add_nutrients(nutrients)

    # Act
    actual_results = manager._create_nutrient_request_results(projected_manure_mass, manure_type)

    # Assert
    assert actual_results.nitrogen == projected_manure_mass * nutrients.nitrogen_composition
    assert actual_results.phosphorus == projected_manure_mass * nutrients.phosphorus_composition
    assert actual_results.total_manure_mass == projected_manure_mass
    assert actual_results.dry_matter == projected_manure_mass * nutrients.dry_matter_fraction
    assert actual_results.dry_matter_fraction == nutrients.dry_matter_fraction


@pytest.mark.parametrize(
    'projected_manure_mass, nutrients, expected_exception, expected_error_msg',
    [
        # Scenario when projected manure mass is negative
        (-2.0, ManureNutrients(manure_type=ManureType.LIQUID), ValueError,
         'Projected manure mass cannot be negative: -2.0'),
    ]
)
def test_create_nutrient_request_results_exceptions(projected_manure_mass: float, nutrients: ManureNutrients,
                                                    expected_exception: type[Exception],
                                                    expected_error_msg: str) -> None:
    """
    Test the _create_nutrient_request_results() method of the ManureNutrientManager class for expected
    exception scenarios.

    This test verifies that the _create_nutrient_request_results() method raises appropriate exceptions
    with correct messages for negative values.
    """

    # Arrange
    manager = ManureNutrientManager()
    manager.add_nutrients(nutrients)

    # Act & Assert
    with pytest.raises(expected_exception, match=expected_error_msg):
        manager._create_nutrient_request_results(projected_manure_mass, manure_type=ManureType.LIQUID)


@pytest.mark.parametrize(
    'manure_type, initial_nutrients, nutrients_to_remove, expected_nutrients',
    [
        # Scenario when removing zero nutrients
        (ManureType.SOLID,
         ManureNutrients(nitrogen=1, phosphorus=2, total_manure_mass=3, dry_matter=1, manure_type=ManureType.SOLID),
         NutrientRequestResults(nitrogen=0, phosphorus=0, total_manure_mass=0, dry_matter=0, dry_matter_fraction=0.5),
         ManureNutrients(nitrogen=1, phosphorus=2, total_manure_mass=3, dry_matter=1, manure_type=ManureType.SOLID)),

        # Scenario when removing some nutrients
        (ManureType.LIQUID,
         ManureNutrients(nitrogen=5, phosphorus=10, total_manure_mass=15, dry_matter=5, manure_type=ManureType.LIQUID),
         NutrientRequestResults(nitrogen=1, phosphorus=2, total_manure_mass=3, dry_matter=1, dry_matter_fraction=0.5),
         ManureNutrients(nitrogen=4, phosphorus=8, total_manure_mass=12, dry_matter=4, manure_type=ManureType.LIQUID)),

        # Scenario when removing all nutrients
        (ManureType.LIQUID,
         ManureNutrients(nitrogen=1, phosphorus=2, total_manure_mass=3, dry_matter=1, manure_type=ManureType.LIQUID),
         NutrientRequestResults(nitrogen=1, phosphorus=2, total_manure_mass=3, dry_matter=1, dry_matter_fraction=0.5),
         ManureNutrients(nitrogen=0, phosphorus=0, total_manure_mass=0, dry_matter=0, manure_type=ManureType.LIQUID)),
    ]
)
def test_remove_nutrients(manure_type: ManureType, initial_nutrients: ManureNutrients,
                          nutrients_to_remove: NutrientRequestResults, expected_nutrients: ManureNutrients) -> None:
    """
    Unit test for the _remove_nutrients() method of the ManureNutrientManager class.

    This test verifies that the _remove_nutrients() method correctly removes the specified amount of nutrients
    from the manager.

    """

    # Arrange
    manager = ManureNutrientManager()
    manager.add_nutrients(initial_nutrients)

    # Act
    manager._remove_nutrients(nutrients_to_remove, manure_type=manure_type)

    # Assert
    assert manager._nutrients_by_manure_type[manure_type] == expected_nutrients


@pytest.mark.parametrize(
    'manure_type, initial_nutrients, nutrients_to_remove, exceeding_nutrient_type',
    [
        (ManureType.LIQUID,
         ManureNutrients(nitrogen=1, phosphorus=2, total_manure_mass=3, dry_matter=1, manure_type=ManureType.LIQUID),
         NutrientRequestResults(nitrogen=2, phosphorus=2, total_manure_mass=3, dry_matter=1, dry_matter_fraction=0.5),
         'nitrogen'),
        (ManureType.LIQUID,
         ManureNutrients(nitrogen=1, phosphorus=2, total_manure_mass=3, dry_matter=1, manure_type=ManureType.LIQUID),
         NutrientRequestResults(nitrogen=1, phosphorus=3, total_manure_mass=3, dry_matter=1, dry_matter_fraction=0.5),
         'phosphorus'),
        (ManureType.SOLID,
         ManureNutrients(nitrogen=1, phosphorus=2, total_manure_mass=3, dry_matter=1, manure_type=ManureType.SOLID),
         NutrientRequestResults(nitrogen=1, phosphorus=2, total_manure_mass=4, dry_matter=1, dry_matter_fraction=0.5),
         'total_manure_mass'),
        (ManureType.SOLID,
         ManureNutrients(nitrogen=1, phosphorus=2, total_manure_mass=3, dry_matter=1, manure_type=ManureType.SOLID),
         NutrientRequestResults(nitrogen=1, phosphorus=2, total_manure_mass=3, dry_matter=2, dry_matter_fraction=0.5),
         'dry_matter'),
    ]
)
def test_remove_nutrients_exceptions(manure_type: ManureType, initial_nutrients: ManureNutrients,
                                     nutrients_to_remove: NutrientRequestResults, exceeding_nutrient_type: str):
    """
    Unit test for the _remove_nutrients() method of the ManureNutrientManager class in exception scenarios.

    This test verifies that the _remove_nutrients() method raises appropriate exceptions when trying to remove
    more nutrients than available in the manager.

    """
    # Arrange
    manager = ManureNutrientManager()
    manager.add_nutrients(initial_nutrients)

    # Act & Assert
    with pytest.raises(ValueError, match=f'Remove more nutrients than available: {exceeding_nutrient_type}'):
        manager._remove_nutrients(nutrients_to_remove, manure_type=manure_type)
