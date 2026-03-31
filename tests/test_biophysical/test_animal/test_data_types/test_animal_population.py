import random
import sys
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.animal_enums import Breed
from RUFAS.biophysical.animal.data_types.animal_population import AnimalPopulation, AnimalPopulationStatistics
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType

ANIMAL_TYPE_COW: list[AnimalType] = [AnimalType.LAC_COW, AnimalType.DRY_COW]


def mock_animal(animal_type: AnimalType, id: int, mocker: MockerFixture) -> Animal:
    animal = MagicMock(auto_spec=Animal)
    animal.breed = Breed.HO
    animal.id = id
    animal.type = animal_type
    animal.days_born = random.randint(0, 2000)
    animal.body_weight = random.uniform(40, 900)
    animal.days_in_pregnancy = (
        random.randint(0, 500) if animal_type not in [AnimalType.CALF, AnimalType.HEIFER_I] else 0
    )
    animal.days_in_milk = random.randint(0, 2000) if animal_type.is_cow else 0
    animal.is_milking = True if animal.days_in_milk > 0 else False
    animal.calves = random.randint(0, 10) if animal_type.is_cow else 0
    animal.calving_interval = random.randint(250, 1000) if animal_type.is_cow else AnimalConfig.calving_interval

    mocker.patch.object(animal, "get_animal_values", return_value={"dummy": "animal"})

    return animal


def mock_cow(
    mocker: MockerFixture,
    id_: int,
    parity: int,
    is_milking: bool,
    days_born: int,
) -> Animal:
    cow = MagicMock(spec=Animal)
    cow.id = id_
    cow.calves = parity
    cow.is_milking = is_milking
    cow.days_born = days_born
    cow.type = AnimalType.LAC_COW
    mocker.patch.object(cow, "get_animal_values", return_value={"dummy": "animal"})
    return cow


def average(data: list[float | int]) -> float:
    return sum(data) / len(data) if len(data) > 0 else 0.0


def mock_herd(
    num_calf: int,
    num_heiferI: int,
    num_heiferII: int,
    num_heiferIII: int,
    num_cow: int,
    num_replacement: int,
    mocker: MockerFixture,
) -> tuple[list[Animal], list[Animal], list[Animal], list[Animal], list[Animal], list[Animal]]:
    starting_id = 0
    mock_calves: list[Animal] = [mock_animal(AnimalType.CALF, i, mocker) for i in range(num_calf)]
    starting_id += num_calf

    mock_heiferIs: list[Animal] = [
        mock_animal(AnimalType.HEIFER_I, i, mocker) for i in range(starting_id, starting_id + num_heiferI)
    ]
    starting_id += num_heiferI

    mock_heiferIIs: list[Animal] = [
        mock_animal(AnimalType.HEIFER_II, i, mocker) for i in range(starting_id, starting_id + num_heiferII)
    ]
    starting_id += num_heiferII

    mock_heiferIIIs: list[Animal] = [
        mock_animal(AnimalType.HEIFER_III, i, mocker) for i in range(starting_id, starting_id + num_heiferIII)
    ]
    starting_id += num_heiferIII

    mock_cows: list[Animal] = [
        mock_animal(AnimalType.LAC_COW, i, mocker) for i in range(starting_id, starting_id + num_cow)
    ]
    starting_id += num_cow

    mock_replacement: list[Animal] = [
        mock_animal(AnimalType.HEIFER_III, i, mocker) for i in range(starting_id, starting_id + num_replacement)
    ]

    return mock_calves, mock_heiferIs, mock_heiferIIs, mock_heiferIIIs, mock_cows, mock_replacement


@pytest.mark.parametrize("starting_animal_id", [0, 1, 31415, sys.maxsize])
def test_next_id(starting_animal_id: int) -> None:
    """Unit test for next_id()"""
    AnimalPopulation.set_current_max_animal_id(starting_animal_id)

    expected_id = starting_animal_id + 1
    result = AnimalPopulation.next_id()

    assert result == expected_id
    assert AnimalPopulation.current_animal_id == expected_id
    AnimalPopulation.set_current_max_animal_id(0)


@pytest.mark.parametrize("current_animal_id", [0, 1, 31415, sys.maxsize])
def test_set_current_max_animal_id(current_animal_id: int) -> None:
    """Unit test for next_id()"""
    AnimalPopulation.set_current_max_animal_id(current_animal_id)

    assert AnimalPopulation.current_animal_id == current_animal_id
    AnimalPopulation.set_current_max_animal_id(0)


@pytest.mark.parametrize(
    "num_calf, num_heiferI, num_heiferII, num_heiferIII, num_cow, num_replacement",
    [(1, 1, 1, 1, 1, 1), (0, 0, 0, 0, 0, 0), (8, 44, 38, 5, 100, 500)],
)
def test_get_animals(
    num_calf: int,
    num_heiferI: int,
    num_heiferII: int,
    num_heiferIII: int,
    num_cow: int,
    num_replacement: int,
    mocker: MockerFixture,
) -> None:
    """Unit test for get_animals()"""
    (
        calves,
        heiferIs,
        heiferIIs,
        heiferIIIs,
        cows,
        replacement,
    ) = mock_herd(num_calf, num_heiferI, num_heiferII, num_heiferIII, num_cow, num_replacement, mocker)

    animal_population = AnimalPopulation(
        calves=calves, heiferIs=heiferIs, heiferIIs=heiferIIs, heiferIIIs=heiferIIIs, cows=cows, replacement=replacement
    )

    result_calves = animal_population.get_calves()
    result_heiferIs = animal_population.get_heiferIs()
    result_heiferIIs = animal_population.get_heiferIIs()
    result_heiferIIIs = animal_population.get_heiferIIIs()
    result_cows = animal_population.get_cows()
    result_replacement = animal_population.get_replacement_cows()

    assert result_calves == calves
    assert len(result_calves) == num_calf

    assert result_heiferIs == heiferIs
    assert len(result_heiferIs) == num_heiferI

    assert result_heiferIIs == heiferIIs
    assert len(result_heiferIIs) == num_heiferII

    assert result_heiferIIIs == heiferIIIs
    assert len(result_heiferIIIs) == num_heiferIII

    assert result_cows == cows
    assert len(result_cows) == num_cow

    assert result_replacement == replacement
    assert len(result_replacement) == num_replacement

    AnimalPopulation.set_current_max_animal_id(0)


@pytest.mark.parametrize(
    "data",
    [
        ([1, 1, 1, 1, 1, 1]),
        ([0, 0, 0, 0, 0, 0]),
        ([-1, -2, -3, -4, -5, -6, -7, -8]),
        ([-5, -3, -1, 1, 9, 8]),
        ([8, 44, 38, 5, 100, 500]),
        ([0.0, 0.0, 0.0]),
        ([1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9]),
        ([-1.1, -2.2, -3.3]),
        ([-9.9, -345.4, -13, 1436, 495.324]),
        ([]),
    ],
)
def test_average(data: list[int | float]) -> None:
    """Unit test for _average()"""
    expected_result = sum(data) / len(data) if len(data) else 0

    animal_population = AnimalPopulation(calves=[], heiferIs=[], heiferIIs=[], heiferIIIs=[], cows=[], replacement=[])
    actual_result = animal_population._average(data=data)

    assert actual_result == expected_result


@pytest.mark.parametrize(
    "data, variable_name, bins, expected_average, expected_distribution",
    [
        (
            [1, 2, 3, 4, 5],
            "numbers",
            2,
            3.0,
            {"numbers_1.0_to_3.0": 2, "numbers_3.0_to_5.0": 3},
        ),
        (
            [10, 20, 20, 30, 40],
            "test",
            3,
            24.0,
            {
                "test_10.0_to_20.0": 1,  # 10
                "test_20.0_to_30.0": 2,  # 20, 20 (20 goes in [20,30))
                "test_30.0_to_40.0": 2,  # 30, 40
            },
        ),
        (
            [-1, -2, 3, 10, 11],
            "mixed",
            3,
            (-1 + -2 + 3 + 10 + 11) / 5,  # which is 4.2
            {
                # Edges likely: [-2., 2.3, 6.7, 11.]
                "mixed_-2.0_to_2.3": 2,  # -2, -1
                "mixed_2.3_to_6.7": 1,  # 3
                "mixed_6.7_to_11.0": 2,  # 10, 11
            },
        ),
        (
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "ten",
            5,
            5.5,  # average of 1..10
            {
                # With bins=5 from data range 1..10,
                # Edges might be [1., 2.8, 4.6, 6.4, 8.2, 10.]
                "ten_1.0_to_2.8": 2,  # 1,2
                "ten_2.8_to_4.6": 2,  # 3,4
                "ten_4.6_to_6.4": 2,  # 5,6
                "ten_6.4_to_8.2": 2,  # 7,8
                "ten_8.2_to_10.0": 2,  # 9,10
            },
        ),
    ],
)
def test_find_distribution(
    data: list[int | float],
    variable_name: str,
    bins: int,
    expected_average: float,
    expected_distribution: dict[str, int],
) -> None:
    """Unit test for find_distribution()"""
    actual_average, actual_distribution = AnimalPopulation.find_distribution(data, variable_name, num_bins=bins)
    assert actual_average == expected_average
    assert actual_distribution == expected_distribution


@pytest.mark.parametrize(
    "num_calf, num_heiferI, num_heiferII, num_heiferIII, num_cow, num_replacement",
    [(1, 1, 1, 1, 1, 1), (0, 0, 0, 0, 0, 0), (8, 44, 38, 5, 100, 500)],
)
def test_get_herd_summary(
    num_calf: int,
    num_heiferI: int,
    num_heiferII: int,
    num_heiferIII: int,
    num_cow: int,
    num_replacement: int,
    mocker: MockerFixture,
) -> None:
    """Unit test for get_herd_summary()"""
    AnimalPopulation.set_current_max_animal_id(0)

    (
        calves,
        heiferIs,
        heiferIIs,
        heiferIIIs,
        cows,
        replacements,
    ) = mock_herd(num_calf, num_heiferI, num_heiferII, num_heiferIII, num_cow, num_replacement, mocker)
    mock_find_distribution = mocker.patch.object(AnimalPopulation, "find_distribution", return_value=(1.23, {}))

    animal_population = AnimalPopulation(
        calves=calves,
        heiferIs=heiferIs,
        heiferIIs=heiferIIs,
        heiferIIIs=heiferIIIs,
        cows=cows,
        replacement=replacements,
    )
    expected_breed = (
        {"Holstein"} if num_calf + num_heiferI + num_heiferII + num_heiferIII + num_cow + num_replacement > 0 else set()
    )
    expected_result = AnimalPopulationStatistics(
        breed=expected_breed,
        number_of_calves=num_calf,
        number_of_heiferIs=num_heiferI,
        number_of_heiferIIs=num_heiferII,
        number_of_heiferIIIs=num_heiferIII,
        number_of_cows=num_cow,
        number_of_replacement_heiferIIIS=num_replacement,
        number_of_lactating_cows=len([cow for cow in cows if cow.is_milking]),
        number_of_dry_cows=len([cow for cow in cows if not cow.is_milking]),
        number_of_parity_1_cows=len([cow for cow in cows if cow.calves == 1]),
        number_of_parity_2_cows=len([cow for cow in cows if cow.calves == 2]),
        number_of_parity_3_cows=len([cow for cow in cows if cow.calves == 3]),
        number_of_parity_4_cows=len([cow for cow in cows if cow.calves == 4]),
        number_of_parity_5_cows=len([cow for cow in cows if cow.calves == 5]),
        number_of_parity_6_or_more_cows=len([cow for cow in cows if cow.calves >= 6]),
        average_calf_age=1.23,
        average_heiferI_age=1.23,
        average_heiferII_age=1.23,
        average_heiferIII_age=1.23,
        average_cow_age=1.23,
        average_replacement_age=1.23,
        calf_age_distribution={},
        heiferI_age_distribution={},
        heiferII_age_distribution={},
        heiferIII_age_distribution={},
        cow_age_distribution={},
        replacement_age_distribution={},
        average_calf_body_weight=average([calf.body_weight for calf in calves]),
        average_heiferI_body_weight=average([heiferI.body_weight for heiferI in heiferIs]),
        average_heiferII_body_weight=average([heiferII.body_weight for heiferII in heiferIIs]),
        average_heiferIII_body_weight=average([heiferIII.body_weight for heiferIII in heiferIIIs]),
        average_cow_body_weight=average([cow.body_weight for cow in cows]),
        average_replacement_body_weight=average([replacement.body_weight for replacement in replacements]),
        average_cow_days_in_pregnancy=average([cow.days_in_pregnancy for cow in cows]),
        average_cow_days_in_milk=average([cow.days_in_milk for cow in cows]),
        average_cow_parity=average([cow.calves for cow in cows]),
        average_cow_calving_interval=average([cow.calving_interval for cow in cows]),
    )

    result = animal_population.get_herd_summary()
    assert result == expected_result
    assert mock_find_distribution.call_count == 6

    AnimalPopulation.set_current_max_animal_id(0)


@pytest.mark.parametrize(
    "num_calf, num_heiferI, num_heiferII, num_heiferIII, num_cow, num_replacement",
    [(1, 1, 1, 1, 1, 1), (0, 0, 0, 0, 0, 0), (8, 44, 38, 5, 100, 500)],
)
def test_repr(
    num_calf: int,
    num_heiferI: int,
    num_heiferII: int,
    num_heiferIII: int,
    num_cow: int,
    num_replacement: int,
    mocker: MockerFixture,
) -> None:
    """Unit test for __repr__()"""
    AnimalPopulation.set_current_max_animal_id(0)

    (
        calves,
        heiferIs,
        heiferIIs,
        heiferIIIs,
        cows,
        replacement,
    ) = mock_herd(num_calf, num_heiferI, num_heiferII, num_heiferIII, num_cow, num_replacement, mocker)

    animal_population = AnimalPopulation(
        calves=calves, heiferIs=heiferIs, heiferIIs=heiferIIs, heiferIIIs=heiferIIIs, cows=cows, replacement=replacement
    )

    for cow in cows:
        cow.calves = 1
        cow.days_in_milk = 1
    expected = {
        "calves": [{"dummy": "animal"}] * num_calf,
        "heiferIs": [{"dummy": "animal"}] * num_heiferI,
        "heiferIIs": [{"dummy": "animal"}] * num_heiferII,
        "heiferIIIs": [{"dummy": "animal"}] * num_heiferIII,
        "cows": [{"dummy": "animal"}] * num_cow,
        "cows_parity_1_milking": [{"dummy": "animal"}] * num_cow,
        "cows_parity_2_milking": [],
        "cows_parity_3_milking": [],
        "cows_parity_4_milking": [],
        "cows_parity_5_milking": [],
        "cows_parity_1_not_milking": [],
        "cows_parity_2_not_milking": [],
        "cows_parity_3_not_milking": [],
        "cows_parity_4_not_milking": [],
        "cows_parity_5_not_milking": [],
        "replacement": [{"dummy": "animal"}] * num_replacement,
    }

    actual = animal_population.__repr__()

    assert actual == expected

    AnimalPopulation.set_current_max_animal_id(0)


@pytest.mark.parametrize(
    "num_calf, num_heiferI, num_heiferII, num_heiferIII, num_cow, num_replacement",
    [(1, 1, 1, 1, 1, 1), (0, 0, 0, 0, 0, 0), (8, 44, 38, 5, 100, 500)],
)
def test_post_init(
    num_calf: int,
    num_heiferI: int,
    num_heiferII: int,
    num_heiferIII: int,
    num_cow: int,
    num_replacement: int,
    mocker: MockerFixture,
) -> None:
    """Unit test for __post_init__()"""
    AnimalPopulation.set_current_max_animal_id(0)

    (
        calves,
        heiferIs,
        heiferIIs,
        heiferIIIs,
        cows,
        replacement,
    ) = mock_herd(num_calf, num_heiferI, num_heiferII, num_heiferIII, num_cow, num_replacement, mocker)

    AnimalPopulation(
        calves=calves, heiferIs=heiferIs, heiferIIs=heiferIIs, heiferIIIs=heiferIIIs, cows=cows, replacement=replacement
    )

    expected = max(sum([num_calf, num_heiferI, num_heiferII, num_heiferIII, num_cow, num_replacement]) - 1, 0)

    actual = AnimalPopulation.current_animal_id
    assert actual == expected

    AnimalPopulation.set_current_max_animal_id(0)


@pytest.mark.parametrize(
    "parity, is_milking, days_born_filter, expected_ids",
    [
        (1, True, 0, [0]),  # cow0
        (1, False, 0, [1]),  # cow1
        (2, False, 100, [2]),  # cow2
        (3, True, 400, [3]),  # cow3
        (3, True, 0, [3, 4]),  # cow3 and cow4
        (2, True, 1000, []),  # none
    ],
)
def test_filter_cow_status(
    parity: int,
    is_milking: bool,
    days_born_filter: int,
    expected_ids: list[int],
    mocker: MockerFixture,
) -> None:
    """Unit test for filter_cow_status() with expected result control"""
    AnimalPopulation.set_current_max_animal_id(0)

    cows = [
        mock_cow(mocker, 0, 1, True, 50),  # cow0
        mock_cow(mocker, 1, 1, False, 50),  # cow1
        mock_cow(mocker, 2, 2, False, 150),  # cow2
        mock_cow(mocker, 3, 3, True, 600),  # cow3
        mock_cow(mocker, 4, 3, True, 200),  # cow4
        mock_cow(mocker, 5, 3, False, 700),  # cow5
        mock_cow(mocker, 6, 2, True, 50),  # cow6
    ]

    population = AnimalPopulation(calves=[], heiferIs=[], heiferIIs=[], heiferIIIs=[], cows=cows, replacement=[])

    result = population.filter_cow_status(parity, is_milking, days_born_filter)
    result_ids = [cow.id for cow in result]

    assert sorted(result_ids) == sorted(expected_ids)

    AnimalPopulation.set_current_max_animal_id(0)
