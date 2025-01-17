from __future__ import annotations

import math
import re

import pytest
from pytest_mock import MockerFixture

from RUFAS.routines.manure.manure_nutrients.manure_nutrient_manager import ManureNutrientManager
from RUFAS.routines.manure.manure_nutrients.manure_nutrients import ManureNutrients
from RUFAS.data_structures.manure_to_crop_soil_connection import NutrientRequest, NutrientRequestResults
from RUFAS.data_structures.manure_types import ManureType


@pytest.mark.parametrize("manure_type", [ManureType.LIQUID, ManureType.SOLID])
def test_add_nutrients(manure_type: ManureType) -> None:
    """
    Unit test for the add_nutrients() method of the ManureNutrientManager class
    in the manure_nutrient_manager.py file.

    This test verifies that the add_nutrients() method adds ManureNutrients objects
    to the internal data of a ManureNutrientManager object by manure type.

    """
    # Arrange
    manager = ManureNutrientManager()
    nutrients = ManureNutrients(
        nitrogen=1,
        phosphorus=1,
        total_manure_mass=2,
        dry_matter=2,
        manure_type=manure_type,
    )

    # Act
    manager.add_nutrients(nutrients)

    # Assert
    assert manager.get_values(manure_type) == nutrients


@pytest.mark.parametrize(
    "eval_return, manure_request_fulfilled, use_supplemental_manure, supplemental_manure, expected_result,"
    "remove_called, supplemental_called",
    [
        # Case 1: Request fulfilled completely, no supplemental manure needed
        (
            NutrientRequestResults(
                nitrogen=1,
                phosphorus=1,
                total_manure_mass=2,
                dry_matter=2,
                dry_matter_fraction=0.5,
            ),
            True,
            False,
            None,
            NutrientRequestResults(
                nitrogen=1,
                phosphorus=1,
                total_manure_mass=2,
                dry_matter=2,
                dry_matter_fraction=0.5,
            ),
            True,
            False,
        ),
        # Case 2: Request not fulfilled, supplemental manure needed and used
        (
            NutrientRequestResults(
                nitrogen=0.5,
                phosphorus=0.5,
                total_manure_mass=1,
                dry_matter=1,
                dry_matter_fraction=0.5,
            ),
            False,
            True,
            NutrientRequestResults(
                nitrogen=0.5,
                phosphorus=0.5,
                total_manure_mass=1,
                dry_matter=1,
                dry_matter_fraction=0.5,
            ),
            NutrientRequestResults(
                nitrogen=0.5,
                phosphorus=0.5,
                total_manure_mass=1,
                dry_matter=1,
                dry_matter_fraction=0.5,
            ),
            True,
            True,
        ),
        # Case 3: Request cannot be fulfilled, no supplemental manure allowed
        (
            None,
            False,
            False,
            None,
            None,
            False,
            False,
        ),
    ],
)
def test_request_nutrients(
    mocker: MockerFixture,
    eval_return: NutrientRequestResults,
    manure_request_fulfilled: bool,
    use_supplemental_manure: bool,
    supplemental_manure: NutrientRequestResults,
    expected_result: NutrientRequestResults,
    remove_called: bool,
    supplemental_called: bool,
) -> None:
    """
    Unit test for the request_nutrients() method of the ManureNutrientManager class.

    This test verifies that the method behaves as expected for various combinations of
    evaluated results, request fulfillment, and supplemental manure use.
    """
    # Arrange
    manager = ManureNutrientManager()
    dummy_manure_type = ManureType.LIQUID
    nutrient_request = NutrientRequest(
        nitrogen=1, phosphorus=1, manure_type=dummy_manure_type, use_supplemental_manure=use_supplemental_manure
    )

    manager.field_manure_supplier = mocker.Mock()
    patch_for_evaluate_nutrient_request = mocker.patch.object(
        manager, "_evaluate_nutrient_request", return_value=(eval_return, manure_request_fulfilled)
    )
    patch_for_remove_nutrients = mocker.patch.object(manager, "_remove_nutrients")
    patch_for_calculate_supplemental_manure = mocker.patch.object(
        manager, "_calculate_supplemental_manure_needed", return_value=supplemental_manure
    )
    patch_for_request_supplemental_manure = mocker.patch.object(
        manager.field_manure_supplier, "request_manure", return_value=supplemental_manure
    )
    patch_for_logging = mocker.patch.object(manager.om, "add_log")

    # Act
    actual_result = manager.request_nutrients(nutrient_request)

    # Assert
    patch_for_evaluate_nutrient_request.assert_called_once_with(nutrient_request)

    if remove_called:
        patch_for_remove_nutrients.assert_called_once_with(eval_return, dummy_manure_type)
    else:
        patch_for_remove_nutrients.assert_not_called()

    if supplemental_called:
        patch_for_calculate_supplemental_manure.assert_called_once_with(eval_return, nutrient_request)
        patch_for_request_supplemental_manure.assert_called_once_with(supplemental_manure)
        patch_for_logging.assert_any_call(
            "Supplemental manure used",
            f"Amount: {supplemental_manure.total_manure_mass}",
            {"class": "ManureNutrientManager", "function": "request_nutrients"},
        )
    else:
        patch_for_calculate_supplemental_manure.assert_not_called()
        patch_for_request_supplemental_manure.assert_not_called()

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
        "_calculate_projected_manure_mass",
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
            "Projected manure mass is zero",
            {"class": "ManureNutrientManager", "function": "_evaluate_nutrient_request"},
        )
    elif projected_manure_mass <= current_nutrient_values.total_manure_mass:
        patch_for_create_nutrient_request_results.assert_called_once_with(projected_manure_mass, manure_type)
        patch_for_add_log.assert_called_once_with(
            "Request fulfilled",
            f"Projected manure mass: {projected_manure_mass}",
            {"class": "ManureNutrientManager", "function": "_evaluate_nutrient_request"},
        )
    else:
        patch_for_create_nutrient_request_results.assert_called_once_with(
            current_nutrient_values.total_manure_mass, manure_type
        )
        patch_for_add_warning.assert_called_once_with(
            "Partial request fulfilled",
            "Not adequate manure on farm to fulfill request. " f"Projected manure mass: {projected_manure_mass}",
            {"class": "ManureNutrientManager", "function": "_evaluate_nutrient_request"},
        )

    assert actual_result == expected_request_result
    assert actual_fulfilled == expected_fulfilled


@pytest.mark.parametrize(
    "first_request, second_request, expected_result",
    [
        # Scenario: Combining two requests with valid fractions
        (
            NutrientRequestResults(
                nitrogen=8,
                phosphorus=6,
                total_manure_mass=10,
                organic_nitrogen_fraction=0.4,
                inorganic_nitrogen_fraction=0.6,
                ammonium_nitrogen_fraction=0.3,
                organic_phosphorus_fraction=0.5,
                inorganic_phosphorus_fraction=0.5,
                dry_matter=2,
                dry_matter_fraction=0.1,
            ),
            NutrientRequestResults(
                nitrogen=12,
                phosphorus=9,
                total_manure_mass=20,
                organic_nitrogen_fraction=0.5,
                inorganic_nitrogen_fraction=0.5,
                ammonium_nitrogen_fraction=0.4,
                organic_phosphorus_fraction=0.4,
                inorganic_phosphorus_fraction=0.6,
                dry_matter=3,
                dry_matter_fraction=0.15,
            ),
            NutrientRequestResults(
                nitrogen=20,
                phosphorus=15,
                total_manure_mass=30,
                organic_nitrogen_fraction=0.4667,
                inorganic_nitrogen_fraction=0.5333,
                ammonium_nitrogen_fraction=0.3667,
                organic_phosphorus_fraction=0.4333,
                inorganic_phosphorus_fraction=0.5667,
                dry_matter=5,
                dry_matter_fraction=0.1333,
            ),
        ),
        # Scenario: One request has zero total manure mass
        (
            NutrientRequestResults(
                nitrogen=0,
                phosphorus=0,
                total_manure_mass=0,
                organic_nitrogen_fraction=0.7,
                inorganic_nitrogen_fraction=0.3,
                ammonium_nitrogen_fraction=0.5,
                organic_phosphorus_fraction=0.6,
                inorganic_phosphorus_fraction=0.4,
                dry_matter=0,
                dry_matter_fraction=0.0,
            ),
            NutrientRequestResults(
                nitrogen=10,
                phosphorus=5,
                total_manure_mass=15,
                organic_nitrogen_fraction=0.6,
                inorganic_nitrogen_fraction=0.4,
                ammonium_nitrogen_fraction=0.3,
                organic_phosphorus_fraction=0.5,
                inorganic_phosphorus_fraction=0.5,
                dry_matter=3,
                dry_matter_fraction=0.2,
            ),
            NutrientRequestResults(
                nitrogen=10,
                phosphorus=5,
                total_manure_mass=15,
                organic_nitrogen_fraction=0.6,
                inorganic_nitrogen_fraction=0.4,
                ammonium_nitrogen_fraction=0.3,
                organic_phosphorus_fraction=0.5,
                inorganic_phosphorus_fraction=0.5,
                dry_matter=3,
                dry_matter_fraction=0.2,
            ),
        ),
    ],
)
def test_combine_manure_request_results(first_request, second_request, expected_result):
    """
    Unit test for the _combine_manure_request_results static method.
    """
    # Act
    actual_result = ManureNutrientManager._combine_manure_request_results(first_request, second_request)

    # Assert
    assert actual_result.nitrogen == expected_result.nitrogen
    assert actual_result.phosphorus == expected_result.phosphorus
    assert actual_result.total_manure_mass == expected_result.total_manure_mass
    assert math.isclose(
        actual_result.organic_nitrogen_fraction, expected_result.organic_nitrogen_fraction, abs_tol=1e-4
    )
    assert math.isclose(
        actual_result.inorganic_nitrogen_fraction, expected_result.inorganic_nitrogen_fraction, abs_tol=1e-4
    )
    assert math.isclose(
        actual_result.ammonium_nitrogen_fraction, expected_result.ammonium_nitrogen_fraction, abs_tol=1e-4
    )
    assert math.isclose(
        actual_result.organic_phosphorus_fraction, expected_result.organic_phosphorus_fraction, abs_tol=1e-4
    )
    assert math.isclose(
        actual_result.inorganic_phosphorus_fraction, expected_result.inorganic_phosphorus_fraction, abs_tol=1e-4
    )
    assert actual_result.dry_matter == expected_result.dry_matter
    assert math.isclose(actual_result.dry_matter_fraction, expected_result.dry_matter_fraction, abs_tol=1e-4)


@pytest.mark.parametrize(
    "on_farm_manure, nutrient_request, expected_result",
    [
        # Scenario: No supplemental manure needed (on-farm manure fully satisfies the request)
        (
            NutrientRequestResults(
                nitrogen=10,
                phosphorus=5,
                total_manure_mass=15,
                organic_nitrogen_fraction=0.6,
                inorganic_nitrogen_fraction=0.4,
                ammonium_nitrogen_fraction=0.3,
                organic_phosphorus_fraction=0.5,
                inorganic_phosphorus_fraction=0.5,
                dry_matter=3,
                dry_matter_fraction=0.2,
            ),
            NutrientRequest(
                nitrogen=8,
                phosphorus=4,
                manure_type=ManureType.LIQUID,
                use_supplemental_manure=False,
            ),
            NutrientRequest(
                nitrogen=0.0,
                phosphorus=0.0,
                manure_type=ManureType.LIQUID,
                use_supplemental_manure=True,
            ),
        ),
        # Scenario: Partial supplemental manure needed (on-farm manure partially satisfies the request)
        (
            NutrientRequestResults(
                nitrogen=5,
                phosphorus=2,
                total_manure_mass=10,
                organic_nitrogen_fraction=0.7,
                inorganic_nitrogen_fraction=0.3,
                ammonium_nitrogen_fraction=0.5,
                organic_phosphorus_fraction=0.6,
                inorganic_phosphorus_fraction=0.4,
                dry_matter=2,
                dry_matter_fraction=0.1,
            ),
            NutrientRequest(
                nitrogen=8,
                phosphorus=5,
                manure_type=ManureType.LIQUID,
                use_supplemental_manure=False,
            ),
            NutrientRequest(
                nitrogen=3.0,
                phosphorus=3.0,
                manure_type=ManureType.LIQUID,
                use_supplemental_manure=True,
            ),
        ),
        # Scenario: All supplemental manure needed (on-farm manure provides nothing)
        (
            None,
            NutrientRequest(
                nitrogen=10,
                phosphorus=6,
                manure_type=ManureType.LIQUID,
                use_supplemental_manure=False,
            ),
            NutrientRequest(
                nitrogen=10.0,
                phosphorus=6.0,
                manure_type=ManureType.LIQUID,
                use_supplemental_manure=True,
            ),
        ),
    ],
)
def test_calculate_supplemental_manure_needed(on_farm_manure, nutrient_request, expected_result):
    """
    Unit test for the _calculate_supplemental_manure_needed static method.
    """
    # Act
    actual_result = ManureNutrientManager._calculate_supplemental_manure_needed(on_farm_manure, nutrient_request)

    # Assert
    print(actual_result)
    print(expected_result)
    assert math.isclose(actual_result.nitrogen, expected_result.nitrogen, abs_tol=1e-6)
    assert math.isclose(actual_result.phosphorus, expected_result.phosphorus, abs_tol=1e-6)
    assert actual_result.manure_type == expected_result.manure_type
    assert actual_result.use_supplemental_manure == expected_result.use_supplemental_manure


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
    actual_result = ManureNutrientManager._calculate_projected_manure_mass(request_nutrient, nutrient_composition)

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
        ManureNutrientManager._calculate_projected_manure_mass(request_nutrient, nutrient_composition)


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
    "projected_manure_mass, nutrients, expected_exception, expected_error_msg",
    [
        # Scenario when projected manure mass is negative
        (
            -2.0,
            ManureNutrients(manure_type=ManureType.LIQUID),
            ValueError,
            "Projected manure mass cannot be negative: -2.0",
        ),
    ],
)
def test_create_nutrient_request_results_exceptions(
    projected_manure_mass: float,
    nutrients: ManureNutrients,
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
    manager.add_nutrients(nutrients)

    # Act & Assert
    with pytest.raises(expected_exception, match=expected_error_msg):
        manager._create_nutrient_request_results(projected_manure_mass, manure_type=ManureType.LIQUID)


@pytest.mark.parametrize(
    "manure_type, initial_nutrients, nutrients_to_remove, expected_nutrients",
    [
        # Scenario when removing zero nutrients
        (
            ManureType.SOLID,
            ManureNutrients(
                nitrogen=1,
                phosphorus=2,
                total_manure_mass=3,
                dry_matter=1,
                manure_type=ManureType.SOLID,
            ),
            NutrientRequestResults(
                nitrogen=0,
                phosphorus=0,
                total_manure_mass=0,
                dry_matter=0,
                dry_matter_fraction=0.5,
            ),
            ManureNutrients(
                nitrogen=1,
                phosphorus=2,
                total_manure_mass=3,
                dry_matter=1,
                manure_type=ManureType.SOLID,
            ),
        ),
        # Scenario when removing some nutrients
        (
            ManureType.LIQUID,
            ManureNutrients(
                nitrogen=5,
                phosphorus=10,
                total_manure_mass=15,
                dry_matter=5,
                manure_type=ManureType.LIQUID,
            ),
            NutrientRequestResults(
                nitrogen=1,
                phosphorus=2,
                total_manure_mass=3,
                dry_matter=1,
                dry_matter_fraction=0.5,
            ),
            ManureNutrients(
                nitrogen=4,
                phosphorus=8,
                total_manure_mass=12,
                dry_matter=4,
                manure_type=ManureType.LIQUID,
            ),
        ),
        # Scenario when removing all nutrients
        (
            ManureType.LIQUID,
            ManureNutrients(
                nitrogen=1,
                phosphorus=2,
                total_manure_mass=3,
                dry_matter=1,
                manure_type=ManureType.LIQUID,
            ),
            NutrientRequestResults(
                nitrogen=1,
                phosphorus=2,
                total_manure_mass=3,
                dry_matter=1,
                dry_matter_fraction=0.5,
            ),
            ManureNutrients(
                nitrogen=0,
                phosphorus=0,
                total_manure_mass=0,
                dry_matter=0,
                manure_type=ManureType.LIQUID,
            ),
        ),
    ],
)
def test_remove_nutrients(
    manure_type: ManureType,
    initial_nutrients: ManureNutrients,
    nutrients_to_remove: NutrientRequestResults,
    expected_nutrients: ManureNutrients,
) -> None:
    """
    Unit test for the _remove_nutrients() method of the ManureNutrientManager class.

    This test verifies that the _remove_nutrients() method correctly removes the specified amount of nutrients
    from the manager by manure_type.

    """

    # Arrange
    manager = ManureNutrientManager()
    manager.add_nutrients(initial_nutrients)

    # Act
    manager._remove_nutrients(nutrients_to_remove, manure_type=manure_type)

    # Assert
    assert manager._nutrients_by_manure_type[manure_type] == expected_nutrients


@pytest.mark.parametrize(
    "manure_type, initial_nutrients, nutrients_to_remove, exceeding_nutrient_type",
    [
        (
            ManureType.LIQUID,
            ManureNutrients(
                nitrogen=1,
                phosphorus=2,
                total_manure_mass=3,
                dry_matter=1,
                manure_type=ManureType.LIQUID,
            ),
            NutrientRequestResults(
                nitrogen=2,
                phosphorus=2,
                total_manure_mass=3,
                dry_matter=1,
                dry_matter_fraction=0.5,
            ),
            "nitrogen",
        ),
        (
            ManureType.LIQUID,
            ManureNutrients(
                nitrogen=1,
                phosphorus=2,
                total_manure_mass=3,
                dry_matter=1,
                manure_type=ManureType.LIQUID,
            ),
            NutrientRequestResults(
                nitrogen=1,
                phosphorus=3,
                total_manure_mass=3,
                dry_matter=1,
                dry_matter_fraction=0.5,
            ),
            "phosphorus",
        ),
        (
            ManureType.SOLID,
            ManureNutrients(
                nitrogen=1,
                phosphorus=2,
                total_manure_mass=3,
                dry_matter=1,
                manure_type=ManureType.SOLID,
            ),
            NutrientRequestResults(
                nitrogen=1,
                phosphorus=2,
                total_manure_mass=4,
                dry_matter=1,
                dry_matter_fraction=0.5,
            ),
            "total_manure_mass",
        ),
        (
            ManureType.SOLID,
            ManureNutrients(
                nitrogen=1,
                phosphorus=2,
                total_manure_mass=3,
                dry_matter=1,
                manure_type=ManureType.SOLID,
            ),
            NutrientRequestResults(
                nitrogen=1,
                phosphorus=2,
                total_manure_mass=3,
                dry_matter=2,
                dry_matter_fraction=0.5,
            ),
            "dry_matter",
        ),
        (
            "InvalidManureType",
            None,
            NutrientRequestResults(
                nitrogen=1,
                phosphorus=2,
                total_manure_mass=3,
                dry_matter=1,
                dry_matter_fraction=0.5,
            ),
            None,
        ),
    ],
)
def test_remove_nutrients_more_than_available(
    manure_type: ManureType,
    initial_nutrients: ManureNutrients,
    nutrients_to_remove: NutrientRequestResults,
    exceeding_nutrient_type: str,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for the _remove_nutrients() method of the ManureNutrientManager class in exception scenarios.

    This test verifies that the _remove_nutrients() method adds a warning to the OM when trying to remove
    more nutrients than available in the manager.

    """
    # Arrange
    manager = ManureNutrientManager()
    if initial_nutrients:
        manager.add_nutrients(initial_nutrients)
    patch_for_om_add_warning = mocker.patch.object(manager.om, "add_warning")

    # Act & Assert
    if isinstance(manure_type, ManureType):
        manager._remove_nutrients(nutrients_to_remove, manure_type=manure_type)
        removed_amount = getattr(nutrients_to_remove, exceeding_nutrient_type)
        available_amount = getattr(initial_nutrients, exceeding_nutrient_type)
        patch_for_om_add_warning.assert_called_once_with(
            "Remove more nutrients than available",
            f"Requested {exceeding_nutrient_type} ({removed_amount}) is more than available "
            f"({float(available_amount)})",
            {
                "class": "ManureNutrientManager",
                "function": "_remove_nutrients",
            },
        )
    else:
        with pytest.raises(ValueError) as exc_info:
            manager._remove_nutrients(nutrients_to_remove, manure_type=manure_type)
        assert str(exc_info.value) == f"Invalid manure type: {manure_type}. Supported types are: {ManureType}"
