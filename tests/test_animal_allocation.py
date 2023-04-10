# Unit tests for the pen allocation part of animal management
from typing import List

import pytest
from pytest import approx

from RUFAS.routines import AnimalManagement


@pytest.mark.parametrize(
    'num_animals, num_spaces',
    [
        (0, 1),
        (-1, 1),
        (1, 1),
        (1, -1),
        (1, 0),
        (1, 2),
        (2, 1),
    ]
)
def test_calc_density(num_animals: int, num_spaces: int) -> None:
    """Unit test for _calc_density() in animal_management.py"""
    if num_animals < 0 or num_spaces <= 0:
        # Act and Assert
        with pytest.raises(ValueError):
            AnimalManagement._calc_density(num_animals, num_spaces)
    else:
        # Act
        density = AnimalManagement._calc_density(num_animals, num_spaces)

        # Assert
        assert density == approx(num_animals / num_spaces)


@pytest.mark.parametrize("num_animals, max_spaces_in_pens, expected_allocation", [
    (90, [50, 30, 20], [45, 27, 18]),
    (70, [50, 30, 20], [35, 21, 14]),
    (47, [50, 30, 20], [22, 15, 10]),
    (0, [50, 30, 20], [0, 0, 0]),
    (100, [100], [100]),
])
def test_plan_animal_allocation(num_animals: int,
                                max_spaces_in_pens: List[int],
                                expected_allocation: List[int]
                                ) -> None:
    """
    Unit test for function plan_animal_allocation() in file my_module.py.
    """
    # Arrange

    # Act
    allocation_result = AnimalManagement.plan_animal_allocation(num_animals, max_spaces_in_pens)

    # Assert
    assert allocation_result == expected_allocation
