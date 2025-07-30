import pytest
from pytest_mock import MockerFixture

from RUFAS.data_structures.pen_manure_data import PenManureData
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.routines.manure.pen_manure.manure_manager_pen import ManureManagerPen
from RUFAS.routines.manure.pen_manure.pen_manure import PenManure


def test_manure_manager_pen_init(mocker: MockerFixture) -> None:
    """Unit test for function __init__ in file manure_manager_pen.py"""

    # Arrange
    mock_pen = PenManureData()
    mock_pen["id"] = expected_pen_id = 1
    mock_pen["num_animals"] = expected_num_animals = 10
    mock_pen["classes_in_pen"] = expected_classes_in_pen = {"Cow"}
    mock_pen["animal_combination"] = AnimalCombination.LAC_COW

    mock_pen["housing_type"] = expected_housing_type = "open air barn"
    mock_pen["pen_type"] = expected_pen_type = "tiestall"
    mock_pen["bedding_type"] = expected_bedding_type = "sawdust"

    mock_pen["manure_handler"] = expected_manure_handler = "manual scraping"
    mock_pen["manure_separator"] = expected_manure_separator = "screw press"
    mock_pen["manure_treatment"] = expected_manure_treatment = "slurry storage outdoor"
    mock_pen["manure_separator_after_digestion"] = expected_after_separator = "none"

    mock_pen["manure"] = mocker.MagicMock(autospec=True)
    expected_pen_manure = mocker.MagicMock(autospec=PenManure)
    patch_for_pen_manure_get_instance = mocker.patch(
        "RUFAS.routines.manure.pen_manure.manure_manager_pen.PenManure.get_instance",
        return_value=expected_pen_manure,
    )
    mock_pen["num_lactating_cows"] = expected_num_lactating_cows = 4
    mock_pen["num_stalls"] = expected_num_stalls = 100

    # Act
    pen = ManureManagerPen(mock_pen)

    # Assert
    assert pen.id == expected_pen_id
    assert pen.num_animals == expected_num_animals
    assert pen.classes_in_pen == expected_classes_in_pen
    assert pen.housing_type == expected_housing_type
    assert pen.pen_type == expected_pen_type
    assert pen.bedding_type == expected_bedding_type
    assert pen.manure_handler == expected_manure_handler
    assert pen.manure_separator == expected_manure_separator
    assert pen.manure_treatment == expected_manure_treatment
    assert pen.manure_separator_after_digestion == expected_after_separator
    patch_for_pen_manure_get_instance.assert_called_once_with(mock_pen["manure"], expected_num_animals)
    assert pen.manure == expected_pen_manure
    assert pen.num_lactating_cows == expected_num_lactating_cows
    assert pen.num_stalls == expected_num_stalls


@pytest.mark.parametrize(
    "pen_type, has_cows, expected_area, raises_error",
    [
        ("freestall", True, 3.5, False),
        ("freestall", False, 2.5, False),
        ("tiestall", True, 1.2, False),
        ("tiestall", False, 1.0, False),
        ("compost bedded pack barn", True, 5.0, False),
        ("compost bedded pack barn", False, 3.0, False),
        ("open lot", True, 5.0, False),
        ("open lot", False, 3.0, False),
        ("dummy", True, None, True),
    ],
)
def test_exposed_manure_surface_area_from_pen_type(
    pen_type: str,
    has_cows: bool,
    expected_area: float | None,
    raises_error: bool,
    mocker: MockerFixture,
):
    """Unit test for exposed_manure_surface_area_from_pen_type property in file manure_manager_pen.py"""

    # Arrange
    mocker.patch(
        "RUFAS.routines.manure.pen_manure.manure_manager_pen.ManureManagerPen.__init__",
        return_value=None,
    )
    mock_pen = ManureManagerPen(mocker.MagicMock())
    mock_pen.pen_type = pen_type
    mock_pen.num_stalls = 1
    mock_pen.classes_in_pen = {"LacCow"} if has_cows else {"Calf"}

    # Act & Assert
    if raises_error:
        with pytest.raises(ValueError):
            mock_pen.exposed_manure_surface_area_from_pen_type
    else:
        assert mock_pen.exposed_manure_surface_area_from_pen_type == expected_area
