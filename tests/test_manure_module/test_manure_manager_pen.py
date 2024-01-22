import pytest
from pytest_mock import MockerFixture

from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.manure.pen_manure.pen_manure import PenManure
from RUFAS.routines.manure.pen_manure.manure_manager_pen import ManureManagerPen
from RUFAS.routines.animal.animal_combinations import AnimalCombination


def test_manure_manager_pen_init(mocker: MockerFixture) -> None:
    """Unit test for function __init__ in file manure_manager_pen.py"""

    # Arrange
    mock_pen: Pen = mocker.MagicMock(autospec=Pen)
    mock_pen.id = expected_pen_id = 1
    expected_num_animals = 10
    animals = expected_animals_in_pen = [
        mocker.MagicMock(autospec=Cow) for _ in range(expected_num_animals)
    ]
    mock_pen.animals_in_pen = {}
    Pen.add_new_animals(mock_pen, animals)
    print(len(mock_pen.animals_in_pen))
    mock_pen.classes_in_pen = expected_classes_in_pen = {Cow}
    mock_pen.animal_combination = AnimalCombination.LAC_COW

    mock_pen.housing_type = expected_housing_type = "open air barn"
    mock_pen._pen_type = expected_pen_type = "tiestall"
    mock_pen.bedding_type = expected_bedding_type = "sawdust"

    mock_pen.manure_handling = expected_manure_handler = "manual scraping"
    mock_pen.manure_separator = expected_manure_separator = "screw press"
    mock_pen.manure_storage = expected_manure_treatment = "slurry storage outdoor"

    mock_pen.manure = mocker.MagicMock(autospec=True)
    expected_pen_manure = mocker.MagicMock(autospec=PenManure)
    patch_for_pen_manure_get_instance = mocker.patch(
        "RUFAS.routines.manure.pen_manure.manure_manager_pen.PenManure.get_instance",
        return_value=expected_pen_manure,
    )
    patch_for_count_lactating_cows = mocker.patch(
        "RUFAS.routines.manure.pen_manure.manure_manager_pen.ManureManagerPen.count_lactating_cows",
        return_value=expected_num_animals,
    )

    # Act
    pen = ManureManagerPen(mock_pen)

    # Assert
    assert pen.id == expected_pen_id
    assert list(pen.animals_in_pen.values()) == expected_animals_in_pen
    assert pen.num_animals == expected_num_animals
    assert pen.classes_in_pen == expected_classes_in_pen
    assert pen.housing_type == expected_housing_type
    assert pen.pen_type == expected_pen_type
    assert pen.bedding_type == expected_bedding_type
    assert pen.manure_handler == expected_manure_handler
    assert pen.manure_separator == expected_manure_separator
    assert pen.manure_treatment == expected_manure_treatment
    patch_for_pen_manure_get_instance.assert_called_once_with(
        mock_pen.manure, expected_num_animals
    )
    assert pen.manure == expected_pen_manure
    patch_for_count_lactating_cows.assert_called_once_with(
        mock_pen.animal_combination, list(mock_pen.animals_in_pen.values())
    )
    assert pen.num_lactating_cows == expected_num_animals


# TODO: Fill in the remaining combinations
@pytest.mark.parametrize(
    "animal_combination, expected_num_lactating_cows",
    [
        (AnimalCombination.LAC_COW, 10),
        (AnimalCombination.CALF, 0),
        (AnimalCombination.GROWING, 0),
    ],
)
def test_count_lactating_cows(
    mocker: MockerFixture,
    animal_combination: AnimalCombination,
    expected_num_lactating_cows: int,
) -> None:
    """Unit test for function count_lactating_cows in file manure_manager_pen.py"""

    # Arrange
    mocker.patch("RUFAS.routines.animal.life_cycle.cow.Cow.__init__", return_value=None)
    mock_cows = [Cow(args=mocker.MagicMock()) for _ in range(10)]

    # Act
    actual_num_lactating_cows = ManureManagerPen.count_lactating_cows(
        animal_combination, mock_cows
    )

    # Assert
    assert actual_num_lactating_cows == expected_num_lactating_cows


@pytest.mark.parametrize(
    "pen_type, has_cows, expected_area",
    [
        ("tiestall", True, 1.2),
        ("tiestall", False, 1.0),
        ("bedded pack", True, 5.0),
        ("bedded pack", False, 3.0),
        ("freestall", True, 3.5),
        ("freestall", False, 2.5),
        ("dummy", True, 3.5),
        ("dummy", False, 2.5),
    ],
)
def test_barn_area_from_pen_type(
    pen_type: str, has_cows: bool, expected_area: float, mocker: MockerFixture
) -> None:
    """Unit test for function barn_area_from_pen_type in file manure_manager_pen.py"""

    # Arrange
    mocker.patch(
        "RUFAS.routines.manure.pen_manure.manure_manager_pen.ManureManagerPen.__init__",
        return_value=None,
    )
    mock_pen = ManureManagerPen(mocker.MagicMock(autospec=Pen))
    mock_pen.pen_type = pen_type
    mock_pen.classes_in_pen = {"Cow"} if has_cows else {"Calf"}

    # Assert
    assert mock_pen.barn_area_from_pen_type == expected_area
