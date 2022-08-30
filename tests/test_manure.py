from pytest import approx, fixture
from pytest_mock import MockerFixture

from RUFAS.routines import AnimalManagement
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.pen import Pen
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


def test_housing_area_for_NH3_emission(mock_pen: Pen,
                                       mock_calf: Calf,
                                       mock_heiferII: HeiferII,
                                       mock_cow: Cow) -> None:
    """Unit test for property housing_area_for_NH3_emission in file manure_management_pen.py"""

    # Case 1: Pen contains only cows.
    # Arrange
    mock_pen.animals_in_pen = [mock_cow]
    mock_pen.classes_in_pen = {'Cow'}
    mm_pen = ManureManagementPen(mock_pen)

    # Assert
    assert mm_pen.housing_area_for_NH3_emission == approx(3.5)
    # --------------------------------------------------------------------------

    # Case 2: Pen contains only heiferIIs.
    # Arrange
    mock_pen.animals_in_pen = [mock_heiferII]
    mock_pen.classes_in_pen = {'HeiferII'}
    mm_pen = ManureManagementPen(mock_pen)

    # Assert
    assert mm_pen.housing_area_for_NH3_emission == approx(2.5)
    # --------------------------------------------------------------------------

    # Case 3: Pen contains cows and heiferIIs, but cows take precedence.
    # Arrange
    mock_pen.animals_in_pen = [mock_heiferII, mock_cow]
    mock_pen.classes_in_pen = {'HeiferII', 'Cow'}
    mm_pen = ManureManagementPen(mock_pen)

    # Assert
    assert mm_pen.housing_area_for_NH3_emission == approx(3.5)
    # --------------------------------------------------------------------------

    # Case 4: Pen contains neither cows nor heiferIIs.
    # Arrange
    mock_pen.animals_in_pen = [mock_calf]
    mock_pen.classes_in_pen = {'Calf'}
    mm_pen = ManureManagementPen(mock_pen)

    # Assert
    assert mm_pen.housing_area_for_NH3_emission == approx(2.0)


def test_barn_area(mock_pen: Pen) -> None:
    """Unit test for property barn_area in file manure_management_pen.py"""

    # Case 1: Housing type == tie stall, and cows are present.
    # Arrange
    mock_pen.housing_type = 'tie stall'
    mock_pen.animals_in_pen = [mock_cow]
    mock_pen.classes_in_pen = {'Cow'}
    mm_pen = ManureManagementPen(mock_pen)

    # Assert
    assert mm_pen.barn_area == approx(1.2)
    # --------------------------------------------------------------------------

    # Case 2: Housing type == tie stall, and cows are not present.
    # Arrange
    mock_pen.housing_type = 'tie stall'
    mock_pen.animals_in_pen = [mock_calf]
    mock_pen.classes_in_pen = {'Calf'}
    mm_pen = ManureManagementPen(mock_pen)

    # Assert
    assert mm_pen.barn_area == approx(1.0)
    # --------------------------------------------------------------------------

    # Case 3: Housing type == bedded pack, and cows are present.
    # Arrange
    mock_pen.housing_type = 'bedded pack'
    mock_pen.animals_in_pen = [mock_cow]
    mock_pen.classes_in_pen = {'Cow'}
    mm_pen = ManureManagementPen(mock_pen)

    # Assert
    assert mm_pen.barn_area == approx(5.0)
    # --------------------------------------------------------------------------

    # Case 4: Housing type == bedded pack, and cows are not present.
    # Arrange
    mock_pen.housing_type = 'bedded pack'
    mock_pen.animals_in_pen = [mock_calf]
    mock_pen.classes_in_pen = {'Calf'}
    mm_pen = ManureManagementPen(mock_pen)

    # Assert
    assert mm_pen.barn_area == approx(3.0)
    # --------------------------------------------------------------------------

    # Case 5: Housing type == free stall, and cows are present.
    # Arrange
    mock_pen.housing_type = 'free stall'
    mock_pen.animals_in_pen = [mock_cow]
    mock_pen.classes_in_pen = {'Cow'}
    mm_pen = ManureManagementPen(mock_pen)

    # Assert
    assert mm_pen.barn_area == approx(3.5)
    # --------------------------------------------------------------------------

    # Case 6: Housing type == free stall, and cows are not present.
    # Arrange
    mock_pen.housing_type = 'free stall'
    mock_pen.animals_in_pen = [mock_calf]
    mock_pen.classes_in_pen = {'Calf'}
    mm_pen = ManureManagementPen(mock_pen)

    # Assert
    assert mm_pen.barn_area == approx(2.5)
    # --------------------------------------------------------------------------
