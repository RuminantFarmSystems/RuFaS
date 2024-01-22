import math
from typing import List

import pytest
from pytest import approx
from pytest_mock import MockerFixture

from RUFAS.routines.animal.animal_manager import AnimalManager
from RUFAS.routines.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.animal.animal_combinations import AnimalCombination


def test_get_dry_cows(mocker: MockerFixture) -> None:
    """Unit test for function _get_dry_cows in file animal_manager.py"""
    # Arrange
    num_cows = 10
    num_dry_cows = 5
    cows: List[Cow] = []
    for i in range(num_cows):
        cow = mocker.MagicMock(spec=Cow)
        cow.is_dry = i % 2 == 1
        cows.append(cow)

    # Act
    dry_cows = AnimalManager._get_dry_cows(cows)

    # Assert
    assert len(dry_cows) == num_dry_cows
    for i in range(num_dry_cows):
        assert dry_cows[i] == cows[i * 2 + 1]


def test_get_lactating_cows(mocker: MockerFixture) -> None:
    """Unit test for function _get_lactating_cows in file animal_manager.py"""
    # Arrange
    num_cows = 10
    num_lactating_cows = 5
    cows: List[Cow] = []
    for i in range(num_cows):
        cow = mocker.MagicMock(spec=Cow)
        cow.is_lactating = i % 2 == 0
        cows.append(cow)

    # Act
    lactating_cows = AnimalManager._get_lactating_cows(cows)

    # Assert
    assert len(lactating_cows) == num_lactating_cows
    for i in range(num_lactating_cows):
        assert lactating_cows[i] == cows[i * 2]


def test_group_pens_by_animal_combination(mocker: MockerFixture) -> None:
    """Unit test for function group_pens_by_animal_combination in file routines/animal/animal_manager.py"""
    # Arrange
    pens: List[Pen] = []
    animal_combinations = [
        AnimalCombination.CALF,
        AnimalCombination.GROWING,
        AnimalCombination.GROWING_AND_CLOSE_UP,
        AnimalCombination.LAC_COW,
        AnimalCombination.CLOSE_UP,
    ]
    num_groups = len(animal_combinations)
    num_pens_per_group = 3
    num_pens = num_groups * num_pens_per_group
    for i in range(num_pens):
        pen = mocker.MagicMock(spec=Pen)
        pen.animal_combination = animal_combinations[i % num_groups]
        pens.append(pen)

    # Act
    pen_groups = AnimalManager._group_pens_by_animal_combination(pens)

    # Assert
    assert len(pen_groups) == num_groups
    for i in range(num_groups):
        assert len(pen_groups[animal_combinations[i]]) == num_pens_per_group
        for j in range(num_pens_per_group):
            assert pen_groups[animal_combinations[i]][j] == pens[j * num_groups + i]


@pytest.mark.parametrize(
    'num_stalls, max_stocking_density, expected_max_animal_spaces',
    [
        (1, 1, 1),
        (1, 0, 0),
        (0, 1, 0),
        (1, -1, None),
        (-1, 1, None),
        (1, 1.5, 1),
        (2, 1.5, 3),
    ]
)
def test_calc_max_animal_spaces_per_pen(num_stalls: int,
                                        max_stocking_density: float,
                                        expected_max_animal_spaces: int
                                        ) -> None:
    """Unit test for function _calc_max_animal_spaces_per_pen() in file animal_manager.py"""

    if num_stalls < 0 or max_stocking_density < 0:
        with pytest.raises(ValueError):
            AnimalManager._calc_max_animal_spaces_per_pen(num_stalls, max_stocking_density)
    else:
        # Act
        max_animal_spaces = AnimalManager._calc_max_animal_spaces_per_pen(num_stalls, max_stocking_density)

        # Assert
        assert max_animal_spaces == expected_max_animal_spaces


def test_calc_animal_space_shortage(mocker: MockerFixture) -> None:
    """Unit test for function _calc_animal_space_shortage() in file animal_manager.py"""
    # Arrange
    num_animals = 70
    num_pens = 10
    num_stalls_per_pen = 5
    max_stocking_density_per_pen = 1.2
    max_animal_spaces_per_pen = int(num_stalls_per_pen * max_stocking_density_per_pen)
    pens: List[Pen] = []
    for i in range(num_pens):
        pen = mocker.MagicMock(spec=Pen)
        pen.num_stalls = num_stalls_per_pen
        pen.max_stocking_density = max_stocking_density_per_pen
        pens.append(pen)
    patch_for_calc_max_animal_spaces_per_pen = mocker.patch.object(
        AnimalManager,
        '_calc_max_animal_spaces_per_pen',
        return_value=max_animal_spaces_per_pen
    )
    expected_shortage = num_animals - num_pens * max_animal_spaces_per_pen

    # Act
    shortage = AnimalManager._calc_animal_space_shortage(num_animals, pens)

    # Assert
    assert shortage == expected_shortage
    assert patch_for_calc_max_animal_spaces_per_pen.call_count == num_pens
    for i in range(num_pens):
        assert patch_for_calc_max_animal_spaces_per_pen.call_args_list[i] == mocker.call(num_stalls_per_pen,
                                                                                         max_stocking_density_per_pen)


@pytest.mark.parametrize(
    'animal_combination',
    [
        AnimalCombination.CALF,
        AnimalCombination.GROWING,
        AnimalCombination.CLOSE_UP,
        AnimalCombination.LAC_COW
    ]
)
def test_create_default_pen(animal_combination: AnimalCombination,
                            mocker: MockerFixture) -> None:
    """Unit test for function _create_default_pen() in file animal_manager.py"""
    # Arrange
    num_stalls = 10
    max_stocking_density = 1.2
    pen_id = 1

    mock_pen = mocker.MagicMock(spec=Pen)
    patch_for_pen_init = mocker.patch(
        'RUFAS.routines.animal.animal_manager.Pen',
        return_value=mock_pen
    )

    # Act
    pen = AnimalManager._create_default_pen(
        pen_id=pen_id,
        animal_combination=animal_combination,
        num_stalls=num_stalls,
        max_stocking_density=max_stocking_density
    )

    # Assert
    assert pen == mock_pen
    patch_for_pen_init.assert_called_once_with(
        pen_id=pen_id,
        vertical_dist_to_milking_parlor=AnimalModuleConstants.VERTICAL_DIST_TO_MILKING_PARLOR,
        horizontal_dist_to_milking_parlor=AnimalModuleConstants.HORIZONTAL_DIST_TO_MILKING_PARLOR,
        number_of_stalls=num_stalls,
        housing_type=AnimalModuleConstants.DEFAULT_HOUSING_TYPE,
        bedding_type=AnimalModuleConstants.DEFAULT_BEDDING_TYPE,
        pen_type=AnimalModuleConstants.DEFAULT_PEN_TYPE,
        manure_handling=AnimalModuleConstants.DEFAULT_MANURE_HANDLER,
        manure_separator=AnimalModuleConstants.DEFAULT_MANURE_SEPARATOR,
        manure_storage=AnimalModuleConstants.DEFAULT_MANURE_STORAGE,
        animal_combination=animal_combination,
        max_stocking_density=max_stocking_density
    )


@pytest.mark.parametrize(
    'animal_combination',
    [
        AnimalCombination.CALF,
        AnimalCombination.GROWING,
        AnimalCombination.CLOSE_UP,
        AnimalCombination.LAC_COW
    ]
)
def test_create_default_pens_for_potential_space_shortage(animal_combination: AnimalCombination,
                                                          mocker: MockerFixture) -> None:
    """Unit test for function _create_default_pens_for_potential_space_shortage() in file animal_manager.py"""
    # Arrange
    num_animals = 100
    mock_pens = mocker.MagicMock(spec=List[Pen])
    space_shortage = 24
    patch_for_calc_animal_space_shortage = mocker.patch.object(
        AnimalManager,
        '_calc_animal_space_shortage',
        return_value=space_shortage
    )
    num_stalls_per_pen = 5
    max_stocking_density_per_pen = 1.2

    num_stalls_per_pen_before = AnimalManager.DEFAULT_NUM_STALLS_BY_COMBINATION[animal_combination]
    AnimalManager.DEFAULT_NUM_STALLS_BY_COMBINATION[animal_combination] = num_stalls_per_pen
    max_stocking_density_per_pen_before = AnimalModuleConstants.DEFAULT_MAX_STOCKING_DENSITY
    AnimalModuleConstants.DEFAULT_MAX_STOCKING_DENSITY = max_stocking_density_per_pen

    num_new_default_pens = math.ceil(space_shortage / int(num_stalls_per_pen * max_stocking_density_per_pen))
    start_pen_id = 13
    mock_new_default_pens: List[Pen] = []
    for i in range(num_new_default_pens):
        new_default_pen = mocker.MagicMock(spec=Pen)
        mock_new_default_pens.append(new_default_pen)
    patch_for_create_default_pen = mocker.patch.object(
        AnimalManager,
        '_create_default_pen',
        side_effect=mock_new_default_pens
    )

    mocker.patch('RUFAS.routines.animal.animal_manager.AnimalManager.__init__',
                 return_value=None)
    animal_manager = AnimalManager(data=mocker.MagicMock(),
                                   config=mocker.MagicMock(),
                                   feed=mocker.MagicMock(),
                                   weather=mocker.MagicMock(),
                                   time=mocker.MagicMock()
                                   )

    # Act
    new_default_pens = animal_manager._create_default_pens_for_potential_space_shortage(
        num_animals=num_animals,
        pens=mock_pens,
        animal_combination=animal_combination,
        start_pen_id=start_pen_id
    )

    # Assert
    assert new_default_pens == mock_new_default_pens
    patch_for_calc_animal_space_shortage.assert_called_once_with(
        num_animals=num_animals,
        pens=mock_pens
    )
    patch_for_create_default_pen.assert_has_calls(
        [
            mocker.call(
                pen_id=start_pen_id + i,
                animal_combination=animal_combination,
                num_stalls=num_stalls_per_pen,
                max_stocking_density=max_stocking_density_per_pen
            )
            for i in range(num_new_default_pens)
        ]
    )

    # Clean up
    AnimalManager.DEFAULT_NUM_STALLS_BY_COMBINATION[animal_combination] = num_stalls_per_pen_before
    AnimalModuleConstants.DEFAULT_MAX_STOCKING_DENSITY = max_stocking_density_per_pen_before


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
    """Unit test for _calc_density() in animal_manager.py"""
    if num_animals < 0 or num_spaces <= 0:
        # Act and Assert
        with pytest.raises(ValueError):
            AnimalManager._calc_density(num_animals, num_spaces)
    else:
        # Act
        density = AnimalManager._calc_density(num_animals, num_spaces)

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
    allocation_result = AnimalManager.plan_animal_allocation(num_animals, max_spaces_in_pens)

    # Assert
    assert allocation_result == expected_allocation


@pytest.mark.parametrize('num_animals, allocation_plan', [
    (90, [45, 27, 18]),
    (70, [35, 21, 14]),
    (47, [22, 15, 10]),
    (0, [0, 0, 0]),
    (100, [100]),
])
def test_execute_allocation_plan(num_animals: int, allocation_plan: List[int],
                                 mocker: MockerFixture) -> None:
    """Unit test for function execute_allocation_plan() in file my_module.py."""
    # Arrange
    animal_combination = AnimalCombination.LAC_COW
    animals = []
    for i in range(num_animals):
        animal = mocker.MagicMock()
        animal.temp_id = i
        animals.append(animal)
    mock_pens = []
    for i in range(len(allocation_plan)):
        pen = mocker.MagicMock(spec=Pen)
        pen.animal_combination = animal_combination
        pen.update_animals.return_value = None
        mock_pens.append(pen)

    # Act
    AnimalManager.execute_allocation_plan(
        allocation_plan=allocation_plan,
        animals=animals,
        animal_pens=mock_pens
    )

    # Assert
    for i in range(len(allocation_plan)):
        mock_pens[i].update_animals.assert_called_once_with(
            animals[:allocation_plan[i]],
            animal_combination
        )
        animals = animals[allocation_plan[i]:]


@pytest.mark.parametrize(
    'allocation_plan, num_animals, num_pens',
    [
        ([10, 20], 30, 3),
        ([10, 20], 31, 2),
    ]
)
def test_execute_allocation_plan_error_cases(allocation_plan: List[int],
                                             num_animals: int,
                                             num_pens: int,
                                             mocker: MockerFixture) -> None:
    """Unit test for function execute_allocation_plan() in file animal_manager.py."""
    # Arrange
    mock_animals = [mocker.MagicMock() for _ in range(num_animals)]
    mock_pens = [mocker.MagicMock() for _ in range(num_pens)]

    # Act and Assert
    with pytest.raises(ValueError):
        AnimalManager.execute_allocation_plan(
            allocation_plan=allocation_plan,
            animals=mock_animals,
            animal_pens=mock_pens
        )


@pytest.mark.parametrize(
    'num_animals, num_pens, num_stalls_per_pen, max_stocking_density_per_pen',
    # num_animals <= num_pens * num_stalls_per_pen * max_stocking_density_per_pen
    [
        (20, 4, 5, 1.2),
        (10, 4, 5, 1.2),
    ]
)
def test_allocate_animals_to_pens_helper(num_animals: int,
                                         num_pens: int,
                                         num_stalls_per_pen: int,
                                         max_stocking_density_per_pen: float,
                                         mocker: MockerFixture
                                         ) -> None:
    # Arrange
    mock_animals = [mocker.MagicMock() for _ in range(num_animals)]
    mock_pens = []
    for i in range(num_pens):
        mock_pen = mocker.MagicMock()
        mock_pen.num_stalls = num_stalls_per_pen
        mock_pen.max_stocking_density = max_stocking_density_per_pen
        mock_pens.append(mock_pen)
    max_animal_spaces = int(num_stalls_per_pen * max_stocking_density_per_pen)
    patch_for_calc_max_animal_spaces_per_pen = mocker.patch.object(
        AnimalManager,
        '_calc_max_animal_spaces_per_pen',
        return_value=max_animal_spaces
    )
    dummy_allocation_plan = [-1] * num_pens
    patch_for_plan_animal_allocation = mocker.patch.object(
        AnimalManager,
        'plan_animal_allocation',
        return_value=dummy_allocation_plan
    )
    patch_for_execute_allocation_plan = mocker.patch.object(
        AnimalManager,
        'execute_allocation_plan'
    )

    # Act
    AnimalManager._allocate_animals_to_pens_helper(
        animals=mock_animals,
        pens=mock_pens
    )

    # Assert
    assert patch_for_calc_max_animal_spaces_per_pen.call_count == num_pens
    patch_for_plan_animal_allocation.assert_called_once_with(
        num_animals=num_animals,
        max_spaces_in_pens=[max_animal_spaces] * num_pens
    )
    patch_for_execute_allocation_plan.assert_called_once_with(
        allocation_plan=dummy_allocation_plan,
        animals=mock_animals,
        animal_pens=mock_pens
    )


def test_allocate_animals_to_pens(mocker: MockerFixture) -> None:
    """Unit test for function allocate_animals_to_pens() in file animal_manager.py."""
    mock_pens = []
    pens_by_animal_combination = {}
    num_calves = 20
    num_heiferIs = 30
    num_heiferIIs = 40
    num_heiferIIIs = 50
    num_dry_cows = 60
    num_lac_cows = 70
    calves = [mocker.MagicMock() for _ in range(num_calves)]
    heiferIs = [mocker.MagicMock() for _ in range(num_heiferIs)]
    heiferIIs = [mocker.MagicMock() for _ in range(num_heiferIIs)]
    heiferIIIs = [mocker.MagicMock() for _ in range(num_heiferIIIs)]
    dry_cows = [mocker.MagicMock() for _ in range(num_dry_cows)]
    lac_cows = [mocker.MagicMock() for _ in range(num_lac_cows)]
    cows = dry_cows + lac_cows
    animals_by_combination = {
        AnimalCombination.CALF: calves,
        AnimalCombination.GROWING: heiferIs + heiferIIs,
        AnimalCombination.CLOSE_UP: heiferIIIs + dry_cows,
        AnimalCombination.LAC_COW: lac_cows
    }
    for animal_combination in animals_by_combination:
        mock_pen = mocker.MagicMock()
        mock_pen.animal_combination = animal_combination
        mock_pens.append(mock_pen)
        pens_by_animal_combination[animal_combination] = [mock_pen]
    patch_for_group_pens_by_animal_combination = mocker.patch(
        'RUFAS.routines.animal.animal_manager.AnimalManager._group_pens_by_animal_combination',
        return_value=pens_by_animal_combination
    )

    num_new_default_pens = 10
    dummy_new_default_pens = [mocker.MagicMock() for _ in range(num_new_default_pens)]
    mocker.patch(
        'RUFAS.routines.animal.animal_manager.AnimalManager'
        '._create_default_pens_for_potential_space_shortage',
        return_value=dummy_new_default_pens
    )
    patch_for_allocate_animals_to_pens_helper = mocker.patch.object(
        AnimalManager,
        '_allocate_animals_to_pens_helper',
        return_value=None
    )
    patch_for_fully_update_animal_to_pen_id_map = mocker.patch(
        'RUFAS.routines.animal.animal_manager.AnimalManager.fully_update_animal_to_pen_id_map',
        return_value=None
    )
    mocker.patch(
        'RUFAS.routines.animal.animal_manager.AnimalManager.__init__',
        return_value=None
    )
    animal_manager = AnimalManager(
        data=mocker.MagicMock(),
        config=mocker.MagicMock(),
        feed=mocker.MagicMock(),
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),

    )
    animal_manager.calves = calves
    animal_manager.heiferIs = heiferIs
    animal_manager.heiferIIs = heiferIIs
    animal_manager.heiferIIIs = heiferIIIs
    animal_manager.cows = cows
    animal_manager.all_pens = mock_pens
    animal_manager.ANIMAL_GROUPING_SCENARIO = mocker.MagicMock()

    patch_for_sort_animals_before_allocation = mocker.patch.object(
        AnimalManager,
        '_sort_animals_before_allocation',
        return_value=None
    )

    animal_manager.ANIMAL_GROUPING_SCENARIO.find_animal_combination = mocker.MagicMock(
        'animal_manager.ANIMAL_GROUPING_SCENARIO.find_animal_combination',
        side_effect=lambda animal: AnimalCombination.CALF
        if animal in calves
        else AnimalCombination.GROWING
        if animal in heiferIs + heiferIIs
        else AnimalCombination.CLOSE_UP
        if animal in heiferIIIs + dry_cows
        else AnimalCombination.LAC_COW)

    # Act
    animal_manager.allocate_animals_to_pens()

    # Assert
    patch_for_group_pens_by_animal_combination.assert_called_once_with(mock_pens)

    assert animal_manager.all_pens[-(num_new_default_pens * len(animals_by_combination)):] == \
        dummy_new_default_pens * len(animals_by_combination)
    for animal_combination in animals_by_combination:
        assert pens_by_animal_combination[animal_combination][-num_new_default_pens:] == dummy_new_default_pens

    assert patch_for_allocate_animals_to_pens_helper.call_count == len(animals_by_combination)
    patch_for_fully_update_animal_to_pen_id_map.assert_called_once()
    patch_for_sort_animals_before_allocation.assert_called_once()


def test_set_animal_grouping_scenario(mocker: MockerFixture):
    """Unit test for function set_animal_grouping_scenario() in file animal_manager.py."""
    scenario = mocker.MagicMock()
    mocker.patch(
        'RUFAS.routines.animal.animal_manager.AnimalManager.__init__',
        return_value=None
    )
    animal_manager = AnimalManager(
        data=mocker.MagicMock(),
        config=mocker.MagicMock(),
        feed=mocker.MagicMock(),
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
    )
    # act
    animal_manager.set_animal_grouping_scenario(scenario)

    # assert
    assert animal_manager.ANIMAL_GROUPING_SCENARIO == scenario
