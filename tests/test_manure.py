from enum import auto

import pytest
from pytest import approx
from pytest import fixture
from pytest_mock import MockerFixture

from RUFAS.routines import AnimalManagement
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.manure.constants.constants import ManureManagementConstants
from RUFAS.routines.manure.extended_enum.extended_enum import ExtendedEnum
from RUFAS.routines.manure.manure.manure import Manure
from RUFAS.routines.manure.manure_management import ManureManagement
from RUFAS.routines.manure.ManureManagementPen.manure_management_pen import ManureManagementPen


@fixture
def mock_calf(mocker: MockerFixture) -> Calf:
    """Returns a Calf mocker object"""

    return mocker.MagicMock(autospec=Calf)


@fixture
def mock_heiferI(mocker: MockerFixture) -> HeiferI:
    """Returns a HeiferI mocker object"""

    return mocker.MagicMock(autospec=HeiferI)


@fixture
def mock_heiferII(mocker: MockerFixture) -> HeiferII:
    """Returns a HeiferII mocker object"""

    return mocker.MagicMock(autospec=HeiferII)


@fixture
def mock_heiferIII(mocker: MockerFixture) -> HeiferIII:
    """Returns a HeiferIII mocker object"""

    return mocker.MagicMock(autospec=HeiferIII)


@fixture
def mock_cow(mocker: MockerFixture) -> Cow:
    """Returns a Cow mocker object"""

    return mocker.MagicMock(autospec=Cow)


@fixture
def mock_pen(mocker: MockerFixture,
             mock_calf: Calf,
             mock_heiferI: HeiferI,
             mock_heiferII: HeiferII,
             mock_heiferIII: HeiferIII,
             mock_cow: Cow) -> Pen:
    """Returns a Pen mocker object"""

    mock_pen: Pen = mocker.MagicMock(autospec=Pen)
    mock_pen.id = 1
    mock_pen.animals_in_pen = [mock_calf, mock_heiferI, mock_heiferII, mock_heiferIII, mock_cow]
    mock_pen.classes_in_pen = {'Calf', 'HeiferI', 'HeiferII', 'HeiferIII', 'Cow'}
    mock_pen.housing_type = 'free stall'
    mock_pen.bedding_type = 'sand'
    mock_pen.manure_handling = 'manual_scraping'
    mock_pen.manure_separator = 'sand_lane'
    mock_pen.manure_storage = 'storage_pit'
    return mock_pen


@fixture
def mock_animal_management(mocker: MockerFixture) -> AnimalManagement:
    """Returns a AnimalManagement fixture object"""

    return mocker.MagicMock(autospec=AnimalManagement)

    # return AnimalManagement(
    #         data=mocker.MagicMock(autospec=True),
    #         config=mocker.MagicMock(autospec=Config),
    #         weather=mocker.MagicMock(autospec=Weather),
    #         feed=mocker.MagicMock(autospec=Feed),
    #         time=mocker.MagicMock(autospec=True)
    # )


class DummyExtendedEnum(ExtendedEnum):
    SUCCESS = auto()
    FAILURE = auto()
    DEFAULT = SUCCESS


def test_get_type() -> None:
    assert DummyExtendedEnum.get_default_type() is DummyExtendedEnum.SUCCESS
    assert DummyExtendedEnum.get_type('success') is DummyExtendedEnum.SUCCESS
    assert DummyExtendedEnum.get_type('failure') is DummyExtendedEnum.FAILURE


def test_manure_init() -> None:
    """Unit test for function __init__ in file manure.py"""

    # Given no arguments, a new Manure object should have all attributes
    # initially set to 0.
    manure = Manure()
    assert manure.U == approx(0.0)
    assert manure.TAN_s == approx(0.0)
    assert manure.MN == approx(0.0)
    assert manure.Mkg == approx(0.0)
    assert manure.TSd == approx(0.0)
    assert manure.VSd == approx(0.0)
    assert manure.VSnd == approx(0.0)
    assert manure.WIP_frac == approx(0.0)
    assert manure.WOP_frac == approx(0.0)
    assert manure.p_excrt_manure == approx(0.0)
    assert manure.p_frac == approx(0.0)
    assert manure.K_manure == approx(0.0)
    assert manure.CH4_manure == approx(0.0)

    # Given some arguments, a new Manure object should either set the corresponding
    # attributes to the given values or do some calculations.
    manure = Manure(
            # The following attributes should be modified.
            U=1.0,
            TAN_s=1.0,
            MN=1.0,
            VSd=1.0,
            VSnd=1.0,
            p_excrt_manure=1.0,
            K_manure=1.0,

            # The following attributes should stay the same.
            # Only pick two as an example.
            Mkg=10.0,
            CH4_manure=10.0
    )
    constants = ManureManagementConstants
    assert manure.U == approx(constants.UREA_MOLAR_MASS)
    assert manure.TAN_s == approx(constants.TAN_MOLAR_MASS)
    assert manure.MN == approx(constants.GRAMS_TO_KG)
    assert manure.VSd == approx(constants.GRAMS_TO_KG)
    assert manure.VSnd == approx(constants.GRAMS_TO_KG)
    assert manure.p_excrt_manure == approx(constants.GRAMS_TO_KG)
    assert manure.K_manure == approx(constants.GRAMS_TO_KG)

    assert manure.Mkg == approx(10.0)
    assert manure.CH4_manure == approx(10.0)

    # Attributes that are not set to anything should be set to the default value of 0.
    assert manure.TSd == approx(0.0)
    assert manure.WIP_frac == approx(0.0)
    assert manure.WOP_frac == approx(0.0)
    assert manure.p_frac == approx(0.0)


# Test ManureManagement class
def test_manure_management_init(mocker: MockerFixture, mock_animal_management: AnimalManagement) -> None:
    """Unit test for function __init__ in file manure_management.py"""

    # Arrange
    mock_set_up_components = mocker.patch('RUFAS.routines.manure.manure_management.ManureManagement'
                                          '._setup_manure_management_components', return_value=None)

    # Act
    manure_management = ManureManagement(mock_animal_management)

    # Assert
    assert manure_management.manure_handlers == {}
    assert manure_management.reception_pits == {}
    assert manure_management.manure_separators == {}
    assert manure_management.manure_treatments == {}
    assert manure_management.all_data == {}
    mock_set_up_components.assert_called_once_with(mock_animal_management)


def test_setup_manure_management_components(mocker: MockerFixture,
                                            mock_animal_management: AnimalManagement) -> None:
    """Unit test for function _setup_manure_management_components in file manure_management.py"""

    # Arrange
    num_pens = 3
    mock_pens = [mocker.MagicMock(autospec=Pen) for _ in range(num_pens)]
    for i in range(num_pens):
        mock_pens[i].id = i
    mock_animal_management.all_pens = mock_pens

    # Act
    manure_management = ManureManagement(mock_animal_management)

    # Assert
    assert len(manure_management.manure_handlers) == num_pens
    assert len(manure_management.reception_pits) == num_pens
    assert len(manure_management.manure_separators) == num_pens
    assert len(manure_management.manure_treatments) == num_pens


def test_manure_management_update(mocker: MockerFixture,
                                  mock_animal_management: AnimalManagement) -> None:
    """Unit test for function update in file manure_management.py"""

    # Arrange
    num_pens = 3
    mock_pens = [mocker.MagicMock(autospec=Pen) for _ in range(num_pens)]
    for i in range(num_pens):
        mock_pens[i].id = i
    mock_animal_management.all_pens = mock_pens

    # Act
    manure_management = ManureManagement(mock_animal_management)
    manure_management.update(mock_animal_management)

    # Assert
    assert len(manure_management.manure_handlers) == num_pens
    assert len(manure_management.reception_pits) == num_pens
    assert len(manure_management.manure_separators) == num_pens
    assert len(manure_management.manure_treatments) == num_pens
    assert len(manure_management.all_data) == num_pens


# Test ManureManagementPen class


def test_manure_management_pen_init(mock_pen: Pen,
                                    mock_calf: Calf,
                                    mock_heiferI: HeiferI,
                                    mock_heiferII: HeiferII,
                                    mock_heiferIII: HeiferIII,
                                    mock_cow: Cow) -> None:
    """Unit test for function __init__ in file manure_management_pen.py"""

    # Act
    mm_pen = ManureManagementPen(mock_pen)

    # Assert
    assert mm_pen.id == 1
    assert mm_pen.animals_in_pen == [mock_calf, mock_heiferI, mock_heiferII, mock_heiferIII, mock_cow]
    assert mm_pen.classes_in_pen == {'Calf', 'HeiferI', 'HeiferII', 'HeiferIII', 'Cow'}
    assert mm_pen.housing_type == 'free stall'
    assert mm_pen.bedding_type == 'sand'
    assert mm_pen.manure_handler == 'manual_scraping'
    assert mm_pen.manure_separator == 'sand_lane'
    assert mm_pen.manure_treatment == 'storage_pit'
    assert mm_pen.num_animals == 5


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
