import random
import sys
from typing import List

import mock
import pytest
from mock.mock import MagicMock

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.animal_population import AnimalPopulation
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType

ANIMAL_TYPE_COW: list[AnimalType] = [AnimalType.LAC_COW, AnimalType.DRY_COW]


@pytest.fixture
def mock_animal_population() -> AnimalPopulation:
    """InputManager fixture"""
    return AnimalPopulation(calves=[], heiferIs=[], heiferIIs=[], heiferIIIs=[], cows=[], replacement=[])


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
    mock_animal_population: AnimalPopulation,
) -> None:
    """Unit test for get_animals()"""
    calves: List[Animal] = [mock.MagicMock(auto_spec=Animal)] * num_calf
    heiferIs: List[Animal] = [mock.MagicMock(auto_spec=Animal)] * num_heiferI
    heiferIIs: List[Animal] = [mock.MagicMock(auto_spec=Animal)] * num_heiferII
    heiferIIIs: List[Animal] = [mock.MagicMock(auto_spec=Animal)] * num_heiferIII
    cows: List[Animal] = [mock.MagicMock(auto_spec=Animal)] * num_cow
    replacement: List[Animal] = [mock.MagicMock(auto_spec=Animal)] * num_replacement

    (
        mock_animal_population.calves,
        mock_animal_population.heiferIs,
        mock_animal_population.heiferIIs,
        mock_animal_population.heiferIIIs,
        mock_animal_population.cows,
        mock_animal_population.replacement,
    ) = (calves, heiferIs, heiferIIs, heiferIIIs, cows, replacement)

    result_calves = mock_animal_population.get_calves()
    result_heiferIs = mock_animal_population.get_heiferIs()
    result_heiferIIs = mock_animal_population.get_heiferIIs()
    result_heiferIIIs = mock_animal_population.get_heiferIIIs()
    result_cows = mock_animal_population.get_cows()
    result_replacement = mock_animal_population.get_replacement_cows()

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


class MockAnimals:
    def __init__(self, num_animal: int, animal_type: AnimalType, starting_id: int = 0) -> None:
        self.num_animal = num_animal
        self.animal_type = animal_type

        self.id_list = list(range(starting_id, starting_id + num_animal))
        self.days_born_list = [random.randint(0, 5000) for _ in range(num_animal)]

        self.days_in_pregnancy_list: list[int] | list[None] = (
            [random.randint(0, 365) for _ in range(num_animal)] if animal_type in ANIMAL_TYPE_COW else [0] * num_animal
        )
        self.days_in_milk_list = (
            [random.randint(0, 365) for _ in range(num_animal)] if animal_type in ANIMAL_TYPE_COW else [0] * num_animal
        )
        self.calves_list = (
            [random.randint(0, 10) for _ in range(num_animal)] if animal_type in ANIMAL_TYPE_COW else [0] * num_animal
        )  # Parity
        self.calving_interval_list = (
            [random.randint(180, 540) for _ in range(num_animal)] if animal_type in ANIMAL_TYPE_COW
            else [AnimalConfig.calving_interval] * num_animal
        )  # Calving Interval

        self.average_days_in_pregnancy = 0.0
        self.average_days_in_milk = 0.0
        self.average_parity = 0.0
        self.average_calving_interval = 0.0

        self.animals = list(
            map(
                self.mock_animal,
                [animal_type] * num_animal,
                self.id_list,
                self.days_born_list,
                self.days_in_pregnancy_list,
                self.days_in_milk_list,
                self.calves_list,
                self.calving_interval_list,
            )
        )

        self.__post_init__()

    def __post_init__(self) -> None:
        self.current_max_id = max(self.id_list) if self.id_list else 0
        self.average_age = sum(animal.days_born for animal in self.animals) / self.num_animal if self.num_animal else 0

        if self.animal_type in ANIMAL_TYPE_COW:
            self.average_days_in_pregnancy = (
                sum(animal.days_in_pregnancy for animal in self.animals) / self.num_animal if self.num_animal else 0
            )
            self.average_days_in_milk = (
                sum(animal.days_in_milk for animal in self.animals) / self.num_animal if self.num_animal else 0
            )
            self.average_parity = (
                sum(animal.calves for animal in self.animals) / self.num_animal if self.num_animal else 0
            )
            self.average_calving_interval = sum(
                animal.calving_interval for animal in self.animals
            ) / self.num_animal if self.num_animal else 0

    @staticmethod
    def mock_animal(
        animal_type: AnimalType,
        id: int,
        days_born: int,
        days_in_pregnancy: int = 0,
        days_in_milk: int = 0,
        calves: int = 0,
        calving_interval: int = AnimalConfig.calving_interval,
    ) -> Animal:
        dummy_animal = mock.MagicMock(auto_spec=Animal)
        dummy_animal.id = id
        dummy_animal.animal_type = animal_type
        dummy_animal.days_born = days_born
        dummy_animal.days_in_pregnancy = days_in_pregnancy if days_in_pregnancy > 0 else 0
        dummy_animal.days_in_milk = days_in_milk if days_in_milk > 0 else 0
        dummy_animal.calves = calves if calves > 0 else 0
        dummy_animal.calving_interval = calving_interval if calving_interval > 0 else AnimalConfig.calving_interval

        dummy_animal.get_animal_values = MagicMock(return_value={"dummy": "animal"})
        return dummy_animal


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
def test_average(data: List[int | float], mock_animal_population: AnimalPopulation) -> None:
    expected_result = sum(data) / len(data) if len(data) else 0

    actual_result = mock_animal_population._average(data=data)

    assert actual_result == expected_result


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
    mock_animal_population: AnimalPopulation,
) -> None:
    """Unit test for get_herd_summary()"""
    AnimalPopulation.set_current_max_animal_id(0)

    mock_calves = MockAnimals(num_animal=num_calf, animal_type=AnimalType.CALF, starting_id=0)
    mock_animal_population.calves = mock_calves.animals

    mock_heiferIs = MockAnimals(
        num_animal=num_heiferI,
        animal_type=AnimalType.HEIFER_I,
        starting_id=mock_calves.current_max_id + 1,
    )
    mock_animal_population.heiferIs = mock_heiferIs.animals

    mock_heiferIIs = MockAnimals(
        num_animal=num_heiferII,
        animal_type=AnimalType.HEIFER_II,
        starting_id=mock_heiferIs.current_max_id + 1,
    )
    mock_animal_population.heiferIIs = mock_heiferIIs.animals

    mock_heiferIIIs = MockAnimals(
        num_animal=num_heiferIII,
        animal_type=AnimalType.HEIFER_III,
        starting_id=mock_heiferIIs.current_max_id + 1,
    )
    mock_animal_population.heiferIIIs = mock_heiferIIIs.animals

    mock_cows = MockAnimals(
        num_animal=num_cow,
        animal_type=AnimalType.LAC_COW,
        starting_id=mock_heiferIIIs.current_max_id + 1,
    )
    mock_animal_population.cows = mock_cows.animals

    mock_replacement = MockAnimals(
        num_animal=num_replacement,
        animal_type=AnimalType.HEIFER_III,
        starting_id=mock_cows.current_max_id + 1,
    )
    mock_animal_population.replacement = mock_replacement.animals

    expected_result = {
        "num_calf": num_calf,
        "num_heiferI": num_heiferI,
        "num_heiferII": num_heiferII,
        "num_heiferIII": num_heiferIII,
        "num_cow": num_cow,
        "num_replacement": num_replacement,
        "avg_calf_age": mock_calves.average_age,
        "avg_heiferI_age": mock_heiferIs.average_age,
        "avg_heiferII_age": mock_heiferIIs.average_age,
        "avg_heiferIII_age": mock_heiferIIIs.average_age,
        "avg_cow_age": mock_cows.average_age,
        "avg_replacement_age": mock_replacement.average_age,
        "cow_avg_days_in_pregnancy": mock_cows.average_days_in_pregnancy,
        "cow_avg_days_in_milk": mock_cows.average_days_in_milk,
        "cow_avg_parity": mock_cows.average_parity,
        "cow_avg_calving_interval": mock_cows.average_calving_interval,
    }

    result = mock_animal_population.get_herd_summary()
    assert result == expected_result

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
    mock_animal_population: AnimalPopulation,
) -> None:
    """Unit test for __repr__()"""
    AnimalPopulation.set_current_max_animal_id(0)

    mock_calves = MockAnimals(num_animal=num_calf, animal_type=AnimalType.CALF, starting_id=0)

    mock_heiferIs = MockAnimals(
        num_animal=num_heiferI,
        animal_type=AnimalType.HEIFER_I,
        starting_id=mock_calves.current_max_id + 1,
    )

    mock_heiferIIs = MockAnimals(
        num_animal=num_heiferII,
        animal_type=AnimalType.HEIFER_II,
        starting_id=mock_heiferIs.current_max_id + 1,
    )

    mock_heiferIIIs = MockAnimals(
        num_animal=num_heiferIII,
        animal_type=AnimalType.HEIFER_III,
        starting_id=mock_heiferIIs.current_max_id + 1,
    )

    mock_cows = MockAnimals(
        num_animal=num_cow,
        animal_type=AnimalType.LAC_COW,
        starting_id=mock_heiferIIIs.current_max_id + 1,
    )

    mock_replacement = MockAnimals(
        num_animal=num_replacement,
        animal_type=AnimalType.HEIFER_III,
        starting_id=mock_cows.current_max_id + 1,
    )

    dummy_animal_population = AnimalPopulation(
        calves=mock_calves.animals,
        heiferIs=mock_heiferIs.animals,
        heiferIIs=mock_heiferIIs.animals,
        heiferIIIs=mock_heiferIIIs.animals,
        cows=mock_cows.animals,
        replacement=mock_replacement.animals,
    )

    expected = {
        "calves": [{"dummy": "animal"}] * num_calf,
        "heiferIs": [{"dummy": "animal"}] * num_heiferI,
        "heiferIIs": [{"dummy": "animal"}] * num_heiferII,
        "heiferIIIs": [{"dummy": "animal"}] * num_heiferIII,
        "cows": [{"dummy": "animal"}] * num_cow,
        "replacement": [{"dummy": "animal"}] * num_replacement,
    }

    actual = dummy_animal_population.__repr__()

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
) -> None:
    """Unit test for __post_init__()"""
    AnimalPopulation.set_current_max_animal_id(0)
    mock_calves = MockAnimals(num_animal=num_calf, animal_type=AnimalType.CALF, starting_id=0)

    mock_heiferIs = MockAnimals(
        num_animal=num_heiferI,
        animal_type=AnimalType.HEIFER_I,
        starting_id=mock_calves.current_max_id + 1,
    )

    mock_heiferIIs = MockAnimals(
        num_animal=num_heiferII,
        animal_type=AnimalType.HEIFER_II,
        starting_id=mock_heiferIs.current_max_id + 1,
    )

    mock_heiferIIIs = MockAnimals(
        num_animal=num_heiferIII,
        animal_type=AnimalType.HEIFER_III,
        starting_id=mock_heiferIIs.current_max_id + 1,
    )

    mock_cows = MockAnimals(
        num_animal=num_cow,
        animal_type=AnimalType.LAC_COW,
        starting_id=mock_heiferIIIs.current_max_id + 1,
    )

    mock_replacement = MockAnimals(
        num_animal=num_replacement,
        animal_type=AnimalType.HEIFER_III,
        starting_id=mock_cows.current_max_id + 1,
    )

    AnimalPopulation(
        calves=mock_calves.animals,
        heiferIs=mock_heiferIs.animals,
        heiferIIs=mock_heiferIIs.animals,
        heiferIIIs=mock_heiferIIIs.animals,
        cows=mock_cows.animals,
        replacement=mock_replacement.animals,
    )

    expected = max(sum([num_calf, num_heiferI, num_heiferII, num_heiferIII, num_cow, num_replacement]) - 1, 0)

    actual = AnimalPopulation.current_animal_id
    assert actual == expected

    AnimalPopulation.set_current_max_animal_id(0)
