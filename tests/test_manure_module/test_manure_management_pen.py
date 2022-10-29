from typing import Callable
from typing import Dict

import pytest
from pytest import approx
from pytest_mock import MockerFixture

from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.manure.manure.pen_manure import PenManure
from RUFAS.routines.manure.pen.manure_management_pen import ManureManagementPen


def test_manure_management_pen_init(mocker: MockerFixture,
                                    mock_pen: Pen,
                                    mock_cow: Cow,
                                    generate_animal_manure: Callable[[float], Dict[str, float]]) -> None:
    """Unit test for function __init__ in file manure_management_pen.py"""

    mocker.patch('RUFAS.routines.animal.life_cycle.cow.Cow.__init__', return_value=None)
    cow = Cow(mocker.MagicMock(autospec=True))
    mock_pen.animals_in_pen = [cow] * 10

    # Act
    pen = ManureManagementPen(mock_pen)

    # Assert
    assert pen.id == 1
    assert pen.animals_in_pen == [cow] * len(mock_pen.animals_in_pen)
    assert pen.classes_in_pen == {'Cow'}
    assert pen.animal_combination is Pen.AnimalCombination.LAC_COW
    assert pen.housing_type == 'free stall'
    assert pen.bedding_type == 'sawdust'
    assert pen.manure_handler == 'flush system'
    assert pen.manure_separator == 'rotary screen'
    assert pen.manure_treatment == 'slurry storage outdoor'
    assert pen.num_animals == len(mock_pen.animals_in_pen)
    assert pen.num_cows == len(mock_pen.animals_in_pen)
    assert pen.manure_density == 990.0  # kg/m3
    assert pen.manure == PenManure.get_instance(generate_animal_manure(10.0), len(mock_pen.animals_in_pen))
    assert pen.manure_mass == approx(10.0)
    assert pen.manure_volume == approx(10.0 / 990.0)


@pytest.mark.parametrize(
        "has_cows, has_heiferIIs, expected_area",
        [(True, False, 3.5),
         (False, True, 2.5),
         (True, True, 3.5),
         (False, False, 2.0),
         ])
def test_housing_area_for_NH3_emission(has_cows,
                                       has_heiferIIs,
                                       expected_area,
                                       mock_pen: Pen,
                                       mock_calf: Calf,
                                       mock_heiferII: HeiferII,
                                       mock_cow: Cow) -> None:
    """Unit test for property housing_area_for_NH3_emission in file manure_management_pen.py"""

    # Arrange
    animals_in_pen = []
    classes_in_pen = set()

    if has_cows:
        animals_in_pen.append(mock_cow)
        classes_in_pen.add('Cow')
    if has_heiferIIs:
        animals_in_pen.append(mock_heiferII)
        classes_in_pen.add('HeiferII')
    if not has_cows and not has_heiferIIs:
        animals_in_pen.append(mock_calf)
        classes_in_pen.add('Calf')

    mock_pen.animals_in_pen = animals_in_pen
    mock_pen.classes_in_pen = classes_in_pen

    # Act
    mm_pen = ManureManagementPen(mock_pen)

    # Assert
    assert mm_pen.housing_area_for_NH3_emission == approx(expected_area)


@pytest.mark.parametrize(
        "housing_type, has_cows, expected_area",
        [('tie stall', True, 1.2),
         ('tie stall', False, 1.0),
         ('bedded pack', True, 5.0),
         ('bedded pack', False, 3.0),
         ('free stall', True, 3.5),
         ('free stall', False, 2.5),
         ])
def test_barn_area(housing_type,
                   has_cows,
                   expected_area,
                   mock_pen: Pen,
                   mock_cow: Cow,
                   mock_calf: Calf) -> None:
    """Unit test for property barn_area in file manure_management_pen.py"""

    # Arrange
    mock_pen.housing_type = housing_type
    mock_pen.animals_in_pen = [mock_cow] if has_cows else [mock_calf]
    mock_pen.classes_in_pen = {'Cow'} if has_cows else {'Calf'}

    # Act
    mm_pen = ManureManagementPen(mock_pen)

    # Assert
    assert mm_pen.barn_area == approx(expected_area)
