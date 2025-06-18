from __future__ import annotations

import re
from typing import Any

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.manure_nutrient_manager import ManureNutrientManager
from RUFAS.data_structures.manure_nutrients import ManureNutrients
from RUFAS.data_structures.manure_to_crop_soil_connection import NutrientRequest, NutrientRequestResults
from RUFAS.data_structures.manure_types import ManureType


@pytest.mark.parametrize(
    "eval_return, is_nutrient_request_fulfilled, expected_result",
    [
        # Case 1: Request fulfilled completely
        (
            NutrientRequestResults(
                nitrogen=1,
                phosphorus=1,
                total_manure_mass=2,
                dry_matter=2,
                dry_matter_fraction=0.5,
            ),
            True,
            (
                NutrientRequestResults(
                    nitrogen=1,
                    phosphorus=1,
                    total_manure_mass=2,
                    dry_matter=2,
                    dry_matter_fraction=0.5,
                ),
                True,
            ),
        ),
        # Case 2: Request partially fulfilled
        (
            NutrientRequestResults(
                nitrogen=0.5,
                phosphorus=0.5,
                total_manure_mass=1,
                dry_matter=1,
                dry_matter_fraction=0.5,
            ),
            False,
            (
                NutrientRequestResults(
                    nitrogen=0.5,
                    phosphorus=0.5,
                    total_manure_mass=1,
                    dry_matter=1,
                    dry_matter_fraction=0.5,
                ),
                False,
            ),
        ),
        # Case 3: Request cannot be fulfilled
        (None, False, (None, False)),
    ],
)
def test_request_nutrients(
    mocker: MockerFixture,
    eval_return: NutrientRequestResults,
    is_nutrient_request_fulfilled: bool,
    expected_result: tuple[NutrientRequestResults | None, bool],
) -> None:
    """
    Unit test for the request_nutrients() method of the ManureNutrientManager class.

    This test verifies that the method behaves as expected for various combinations of
    evaluated results and request fulfillment.
    """
    # Arrange
    manager = ManureNutrientManager()
    dummy_manure_type = ManureType.LIQUID
    nutrient_request = NutrientRequest(
        nitrogen=1, phosphorus=1, manure_type=dummy_manure_type, use_supplemental_manure=False
    )

    patch_for_evaluate_nutrient_request = mocker.patch.object(
        manager, "_evaluate_nutrient_request", return_value=(eval_return, is_nutrient_request_fulfilled)
    )

    # Act
    actual_result = manager.handle_nutrient_request(nutrient_request)

    # Assert
    patch_for_evaluate_nutrient_request.assert_called_once_with(nutrient_request)

    assert actual_result == expected_result


@pytest.mark.parametrize(
    "projected_manure_mass, manure_type, current_nutrient_values, expected_no_results, expected_fulfilled",
    [
        # Scenario when there is no projected manure mass
        (0, ManureType.LIQUID, ManureNutrients(manure_type=ManureType.LIQUID), True, False),
        # Scenario when projected manure mass is greater than the total manure mass
        (
            10,
            ManureType.LIQUID,
            ManureNutrients(
                nitrogen=2,
                phosphorus=2,
                total_manure_mass=5,
                dry_matter=1,
                manure_type=ManureType.LIQUID,
            ),
            False,
            False,
        ),
        # Scenario when projected manure mass is less than the total manure mass
        (
            2,
            ManureType.SOLID,
            ManureNutrients(
                nitrogen=1,
                phosphorus=1,
                total_manure_mass=3,
                dry_matter=1,
                manure_type=ManureType.SOLID,
            ),
            False,
            True,
        ),
        # Scenario when projected manure mass is equal to the total manure mass
        (
            5,
            ManureType.SOLID,
            ManureNutrients(
                nitrogen=2,
                phosphorus=2,
                total_manure_mass=5,
                dry_matter=1,
                manure_type=ManureType.SOLID,
            ),
            False,
            True,
        ),
    ],
)
def test_evaluate_nutrient_request(
    mocker: MockerFixture,
    projected_manure_mass: float,
    manure_type: ManureType,
    current_nutrient_values: ManureNutrients,
    expected_no_results: bool,
    expected_fulfilled: bool,
) -> None:
    """
    Updated unit test for the _evaluate_nutrient_request() method of the ManureNutrientManager class.
    """
    # Arrange
    manager = ManureNutrientManager()
    manager.add_nutrients(current_nutrient_values)

    nitrogen_derived_manure_mass = mocker.MagicMock()
    phosphorus_derived_manure_mass = mocker.MagicMock()
    patch_for_calculate_projected_manure_mass = mocker.patch.object(
        manager,
        "calculate_projected_manure_mass",
        side_effect=[nitrogen_derived_manure_mass, phosphorus_derived_manure_mass],
    )

    patch_for_select_projected_manure_mass = mocker.patch.object(
        manager, "_select_projected_manure_mass", return_value=projected_manure_mass
    )
    expected_request_result = mocker.MagicMock() if not expected_no_results else None
    patch_for_create_nutrient_request_results = mocker.patch.object(
        manager,
        "_create_nutrient_request_results",
        return_value=expected_request_result,
    )
    patch_for_add_warning = mocker.patch.object(manager.om, "add_warning")
    patch_for_add_log = mocker.patch.object(manager.om, "add_log")

    mock_nutrient_request = mocker.MagicMock()
    mock_nutrient_request.nitrogen = requested_nitrogen = 1
    mock_nutrient_request.phosphorus = requested_phosphorus = 1
    mock_nutrient_request.manure_type = manure_type

    # Act
    actual_result, actual_fulfilled = manager._evaluate_nutrient_request(mock_nutrient_request)

    # Assert
    patch_for_calculate_projected_manure_mass.assert_any_call(
        requested_nitrogen, current_nutrient_values.nitrogen_composition
    )
    patch_for_calculate_projected_manure_mass.assert_any_call(
        requested_phosphorus, current_nutrient_values.phosphorus_composition
    )

    patch_for_select_projected_manure_mass.assert_called_once_with(
        [nitrogen_derived_manure_mass, phosphorus_derived_manure_mass]
    )

    if expected_no_results:
        patch_for_create_nutrient_request_results.assert_not_called()
        patch_for_add_warning.assert_called_once_with(
            "Unable to fulfill request with on-farm manure",
            "Projected manure mass is zero kg.",
            {"class": "ManureNutrientManager", "function": "_evaluate_nutrient_request"},
        )
    elif projected_manure_mass <= current_nutrient_values.total_manure_mass:
        patch_for_create_nutrient_request_results.assert_called_once_with(projected_manure_mass, manure_type)
        patch_for_add_log.assert_called_once_with(
            "Request fulfilled",
            f"Projected manure mass: {projected_manure_mass} kg.",
            {"class": "ManureNutrientManager", "function": "_evaluate_nutrient_request"},
        )
    else:
        patch_for_create_nutrient_request_results.assert_called_once_with(
            current_nutrient_values.total_manure_mass, manure_type
        )
        patch_for_add_warning.assert_called_once_with(
            "Partial request fulfilled",
            f"Not adequate manure on farm to fulfill request. Projected manure mass: {projected_manure_mass} kg.",
            {"class": "ManureNutrientManager", "function": "_evaluate_nutrient_request"},
        )

    assert actual_result == expected_request_result
    assert actual_fulfilled == expected_fulfilled


@pytest.mark.parametrize(
    "request_nutrient, nutrient_composition, expected_result",
    [
        # Scenario when nutrient composition > 0 and request > 0
        (2.0, 0.5, 4.0),
        # Scenario when nutrient composition > 0 and request = 0
        (0, 0.5, 0),
        # Scenario when nutrient composition = 0
        (2.0, 0, 0),
    ],
)
def test_calculate_projected_manure_mass(
    request_nutrient: float, nutrient_composition: float, expected_result: float
) -> None:
    """
    Test for the method _calculate_projected_manure_mass() of the ManureNutrientManager class in the
    manure_nutrient_manager.py file.

    Verifies that the _calculate_projected_manure_mass() method correctly calculates
    the projected manure mass based on different combinations of nutrient request and nutrient composition.

    """
    # Act
    actual_result = ManureNutrientManager.calculate_projected_manure_mass(request_nutrient, nutrient_composition)

    # Assert
    assert actual_result == expected_result


@pytest.mark.parametrize(
    "request_nutrient, nutrient_composition, expected_exception, expected_error_msg",
    [
        # Scenario when request_nutrient is negative
        (-2.0, 0.5, ValueError, "Request for nutrient cannot be negative: -2.0"),
        # Scenario when nutrient composition is negative
        (
            2.0,
            -1.0,
            ValueError,
            "Nutrient composition must be between 0 and 1 (inclusive): -1.0",
        ),
        # Scenario when nutrient composition and request are both negative
        (-2.0, -1.0, ValueError, "Request for nutrient cannot be negative: -2.0"),
        # Scenario when nutrient composition is above 1
        (
            2.0,
            1.5,
            ValueError,
            "Nutrient composition must be between 0 and 1 (inclusive): 1.5",
        ),
    ],
)
def test_calculate_projected_manure_mass_exceptions(
    request_nutrient: float,
    nutrient_composition: float,
    expected_exception: type[Exception],
    expected_error_msg: str,
) -> None:
    """
    Unit test for the method _calculate_projected_manure_mass() of the ManureNutrientManager class in the
    manure_nutrient_manager.py file.

    This test verifies that the _calculate_projected_manure_mass() method raises appropriate exceptions
    with correct messages for negative values and for nutrient composition values not in the range [0, 1].

    """
    # Act & Assert
    with pytest.raises(expected_exception, match=re.escape(expected_error_msg)):
        ManureNutrientManager.calculate_projected_manure_mass(request_nutrient, nutrient_composition)


@pytest.mark.parametrize(
    "projected_manure_masses, expected_result",
    [
        # Scenario when all masses are positive
        ([330, 315, 300], 300),
        # Scenario when one mass is zero
        ([330, 315, 0], 315),
        # Scenario when all masses are zero
        ([0, 0, 0], 0),
    ],
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
    "projected_manure_masses, expected_exception, expected_error_msg",
    [
        # Scenario when one mass is negative
        (
            [330, 315, -300],
            ValueError,
            "Projected manure mass cannot be negative: -300",
        ),
    ],
)
def test_select_projected_manure_mass_exceptions(
    projected_manure_masses: list[float],
    expected_exception: type[Exception],
    expected_error_msg: str,
) -> None:
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
    "projected_manure_mass, manure_type, nutrients",
    [
        # Scenario when projected manure mass is zero
        (
            0.0,
            ManureType.LIQUID,
            ManureNutrients(
                nitrogen=1,
                phosphorus=1,
                total_manure_mass=2,
                dry_matter=1,
                manure_type=ManureType.LIQUID,
            ),
        ),
        # Scenario when projected manure mass is very small
        (
            1e-8,
            ManureType.LIQUID,
            ManureNutrients(
                nitrogen=1,
                phosphorus=1,
                total_manure_mass=2,
                dry_matter=1,
                manure_type=ManureType.LIQUID,
            ),
        ),
        # Scenario when projected manure mass is large
        (
            1e6,
            ManureType.LIQUID,
            ManureNutrients(
                nitrogen=1,
                phosphorus=1,
                total_manure_mass=2,
                dry_matter=1,
                manure_type=ManureType.LIQUID,
            ),
        ),
        # Scenario when nutrient compositions are zero
        (
            2.0,
            ManureType.SOLID,
            ManureNutrients(
                nitrogen=0,
                phosphorus=0,
                total_manure_mass=0,
                dry_matter=0,
                manure_type=ManureType.SOLID,
            ),
        ),
        # Scenario when nutrient values are large
        (
            2.0,
            ManureType.SOLID,
            ManureNutrients(
                nitrogen=1e6,
                phosphorus=1e6,
                total_manure_mass=1e6,
                dry_matter=1e6,
                manure_type=ManureType.SOLID,
            ),
        ),
        # Normal scenario when projected manure mass is > 0
        (
            2.0,
            ManureType.SOLID,
            ManureNutrients(
                nitrogen=1,
                phosphorus=2,
                total_manure_mass=4,
                dry_matter=1,
                manure_type=ManureType.SOLID,
            ),
        ),
    ],
)
def test_create_nutrient_request_results(
    projected_manure_mass: float, manure_type: ManureType, nutrients: ManureNutrients
) -> None:
    """
    Unit test for the _create_nutrient_request_results() method of the ManureNutrientManager class in the
    manure_nutrient_manager.py file.

    This test verifies that the _create_nutrient_request_results() method correctly creates a NutrientRequestResults
    object based on the projected manure mass and manure type.

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
    "projected_manure_mass, expected_exception, expected_error_msg",
    [
        # Scenario when projected manure mass is negative
        (
            -2.0,
            ValueError,
            "Projected manure mass cannot be negative: -2.0",
        ),
    ],
)
def test_create_nutrient_request_results_exceptions(
    projected_manure_mass: float,
    expected_exception: type[Exception],
    expected_error_msg: str,
) -> None:
    """
    Test the _create_nutrient_request_results() method of the ManureNutrientManager class for expected
    exception scenarios.

    This test verifies that the _create_nutrient_request_results() method raises appropriate exceptions
    with correct messages for negative values.
    """

    # Arrange
    manager = ManureNutrientManager()

    # Act & Assert
    with pytest.raises(expected_exception, match=expected_error_msg):
        manager._create_nutrient_request_results(projected_manure_mass, manure_type=ManureType.LIQUID)


@pytest.mark.parametrize(
    "removal_details",
    [
        {
            "manure_type": ManureType.LIQUID,
            "nitrogen": 1,
            "phosphorus": 2,
            "potassium": 3,
            "total_manure_mass": 4,
            "total_solids": 5,
            "water": 4,
            "random": 5000,
        }
    ],
)
def test_remove_nutrients(removal_details: dict[str, Any]) -> None:
    """Tests the function remove_nutrients()."""
    manure_nutrient_manager = ManureNutrientManager()
    original_liquid_nutrients = ManureNutrients(
        manure_type=ManureType.LIQUID,
        nitrogen=10,
        phosphorus=10,
        potassium=10,
        dry_matter=10,
        total_manure_mass=10,
    )
    original_solid_nutrients = ManureNutrients(
        manure_type=ManureType.SOLID,
        nitrogen=10,
        phosphorus=10,
        potassium=10,
        dry_matter=10,
        total_manure_mass=10,
    )
    manure_nutrient_manager.add_nutrients(original_solid_nutrients)
    manure_nutrient_manager.add_nutrients(original_liquid_nutrients)

    manure_nutrient_manager.remove_nutrients(removal_details)

    assert manure_nutrient_manager.nutrients_by_manure_category[ManureType.LIQUID] == ManureNutrients(
        manure_type=ManureType.LIQUID,
        nitrogen=9.0,
        phosphorus=8.0,
        potassium=7.0,
        dry_matter=5.0,
        total_manure_mass=1.0,
    )
