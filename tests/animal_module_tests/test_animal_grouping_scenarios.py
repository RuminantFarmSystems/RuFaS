from unittest.mock import patch

from pytest_mock import MockerFixture

from RUFAS.enums import AnimalCombination
from RUFAS.routines.animal.animal_grouping_scenarios import AnimalGroupingScenario
from RUFAS.routines.animal.animal_types import AnimalType
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII


def test_constructor() -> None:
    """Unit test for constructor in file routines/animal/animal_grouping_scenarios.py"""
    grouping_scenario = AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW
    expected_values = {
        AnimalCombination.CALF: [AnimalType.CALF],
        AnimalCombination.GROWING: [AnimalType.HEIFER_I, AnimalType.HEIFER_II],
        AnimalCombination.CLOSE_UP: [AnimalType.HEIFER_III, AnimalType.DRY_COW],
        AnimalCombination.LAC_COW: [AnimalType.LAC_COW],
    }
    inverted_dict = {v: k for k, lst in expected_values.items() for v in lst}
    assert grouping_scenario._value_ == expected_values
    assert grouping_scenario._animal_combination_by_animal_type == inverted_dict


def test_get_calf_type(mocker: MockerFixture) -> None:
    """Unit test for _get_calf_type() in file routines/animal/animal_grouping_scenarios.py"""
    mock_calf = mocker.MagicMock(autospec=Calf)
    assert AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW._get_calf_type(mock_calf) == AnimalType.CALF


def test_get_heiferI_type(mocker: MockerFixture) -> None:
    """Unit test for _get_heiferI_type() in file routines/animal/animal_grouping_scenarios.py"""
    mock_heiferI = mocker.MagicMock(autospec=HeiferI)
    assert AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW._get_heiferI_type(mock_heiferI) == AnimalType.HEIFER_I


def test_get_heiferII_type(mocker: MockerFixture) -> None:
    """Unit test for _get_heiferII_type() in file routines/animal/animal_grouping_scenarios.py"""
    mock_heiferII = mocker.MagicMock(autospec=HeiferII)
    assert (
        AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW._get_heiferII_type(mock_heiferII) == AnimalType.HEIFER_II
    )


def test_get_heiferIII_type(mocker: MockerFixture) -> None:
    """Unit test for _get_heiferIII_type() in file routines/animal/animal_grouping_scenarios.py"""
    mock_heiferIII = mocker.MagicMock(autospec=HeiferIII)
    assert (
        AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW._get_heiferIII_type(mock_heiferIII)
        == AnimalType.HEIFER_III
    )


def test_mock_get_cow_type(mocker: MockerFixture) -> None:
    """Unit test for _get_cow_type() in file routines/animal/animal_grouping_scenarios.py"""
    mock_cow = mocker.MagicMock(autospec=Cow)
    scenarios = [
        AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW,
        AnimalGroupingScenario.CALF__GROWING_AND_CLOSE_UP__LACCOW,
    ]
    for scenario in scenarios:
        mock_cow.is_lactating = True
        assert scenario._get_cow_type(mock_cow) == AnimalType.LAC_COW
        mock_cow.is_lactating = False
        assert scenario._get_cow_type(mock_cow) == AnimalType.DRY_COW


def test_get_animal_type(mocker: MockerFixture) -> None:
    """Unit test for get_animal_type() in file routines/animal/animal_grouping_scenarios.py"""
    data = [
        (mocker.MagicMock(autospec=Calf), Calf, AnimalType.CALF),
        (mocker.MagicMock(autospec=HeiferI), HeiferI, AnimalType.HEIFER_I),
        (mocker.MagicMock(autospec=HeiferII), HeiferII, AnimalType.HEIFER_II),
        (mocker.MagicMock(autospec=HeiferIII), HeiferIII, AnimalType.HEIFER_III),
    ]
    for animal, type_name, expected_type in data:
        with patch("builtins.type", return_value=type_name):
            assert AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW.get_animal_type(animal) == expected_type


def test_find_animal_combination() -> None:
    """Unit test for find_animal_combination() in file routines/animal/animal_grouping_scenarios.py"""
    scenario = AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW
    data = [
        (Calf, AnimalCombination.CALF),
        (HeiferI, AnimalCombination.GROWING),
        (HeiferII, AnimalCombination.GROWING),
        (HeiferIII, AnimalCombination.CLOSE_UP),
    ]
    for animal, expected_combination in data:
        with patch("builtins.type", return_value=animal):
            assert scenario.find_animal_combination(animal) == expected_combination
