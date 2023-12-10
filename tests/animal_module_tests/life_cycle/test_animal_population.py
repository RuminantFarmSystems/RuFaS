import random
import sys
from typing import List, Type

import mock
import pytest
from mock.mock import MagicMock

from RUFAS.routines.animal.life_cycle.animal_population import AnimalPopulation
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII


@pytest.fixture
def mock_animal_population() -> AnimalPopulation:
    return AnimalPopulation(calves=[],
                            heiferIs=[],
                            heiferIIs=[],
                            heiferIIIs=[],
                            cows=[],
                            replacement=[])


@pytest.mark.parametrize("starting_animal_id", [
    0,
    1,
    31415,
    sys.maxsize
])
def test_next_id(starting_animal_id: int, mock_animal_population: AnimalPopulation) -> None:
    mock_animal_population.current_animal_id = starting_animal_id

    expected_id = starting_animal_id + 1
    result = mock_animal_population.next_id()

    assert result == expected_id
    assert mock_animal_population.current_animal_id == expected_id


@pytest.mark.parametrize("num_calf, num_heiferI, num_heiferII, num_heiferIII, num_cow, num_replacement", [
    (1, 1, 1, 1, 1, 1),
    (0, 0, 0, 0, 0, 0),
    (8, 44, 38, 5, 100, 500)
])
def test_get_animals(num_calf: int,
                     num_heiferI: int,
                     num_heiferII: int,
                     num_heiferIII: int,
                     num_cow: int,
                     num_replacement: int,
                     mock_animal_population: AnimalPopulation) -> None:
    calves: List[Calf] = [mock.MagicMock(auto_spec=Calf)] * num_calf
    heiferIs: List[HeiferI] = [mock.MagicMock(auto_spec=HeiferI)] * num_heiferI
    heiferIIs: List[HeiferII] = [mock.MagicMock(auto_spec=HeiferII)] * num_heiferII
    heiferIIIs: List[HeiferIII] = [mock.MagicMock(auto_spec=HeiferIII)] * num_heiferIII
    cows: List[Cow] = [mock.MagicMock(auto_spec=Cow)] * num_cow
    replacement: List[Cow] = [mock.MagicMock(auto_spec=Cow)] * num_replacement

    (mock_animal_population.calves,
     mock_animal_population.heiferIs,
     mock_animal_population.heiferIIs,
     mock_animal_population.heiferIIIs,
     mock_animal_population.cows,
     mock_animal_population.replacement) = (calves, heiferIs, heiferIIs, heiferIIIs, cows, replacement)

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
    def __init__(self, num_animal: int, animal_type: Type, starting_id: int = 0) -> None:
        self.num_animal = num_animal
        self.animal_type = animal_type

        self.id_list = list(range(starting_id, starting_id + num_animal))
        self.days_born_list = [random.randint(0, 5000) for _ in range(num_animal)]

        self.days_in_preg_list = [random.randint(0, 365) for _ in range(num_animal)] if animal_type == Cow \
            else [None] * num_animal
        self.days_in_milk_list = [random.randint(0, 365) for _ in range(num_animal)] if animal_type == Cow \
            else [None] * num_animal
        self.calves_list = [random.randint(0, 10) for _ in range(num_animal)] if animal_type == Cow \
            else [None] * num_animal  # Parity
        self.CI_list = [random.randint(180, 540) for _ in range(num_animal)] if animal_type == Cow \
            else [None] * num_animal  # Calving Interval

        self.animals = list(map(self.mock_animal, [animal_type] * num_animal, self.id_list, self.days_born_list,
                                self.days_in_preg_list, self.days_in_milk_list, self.calves_list, self.CI_list))

        self.__post_init__()

    def __post_init__(self):
        self.current_max_id = max(self.id_list) if self.id_list else 0
        self.average_age = sum(animal.days_born for animal in self.animals) / self.num_animal if self.num_animal else 0

        if self.animal_type == Cow:
            self.average_days_in_preg = sum(animal.days_in_preg for animal in self.animals) / self.num_animal \
                if self.num_animal else 0
            self.average_days_in_milk = sum(animal.days_in_milk for animal in self.animals) / self.num_animal \
                if self.num_animal else 0
            self.average_parity = sum(animal.calves for animal in self.animals) / self.num_animal \
                if self.num_animal else 0
            self.average_CI = sum(animal.CI for animal in self.animals) / self.num_animal \
                if self.num_animal else 0

    @staticmethod
    def mock_animal(animal_type: Type, id: int, days_born: int,
                    days_in_preg: int = None, days_in_milk: int = None,
                    calves: int = None, CI: int = None) -> MagicMock:
        dummy_animal = mock.MagicMock(auto_spec=animal_type)
        dummy_animal.id = id
        dummy_animal.days_born = days_born
        dummy_animal.days_in_preg = days_in_preg if days_in_preg is not None else None
        dummy_animal.days_in_milk = days_in_milk if days_in_milk is not None else None
        dummy_animal.calves = calves if calves is not None else None
        dummy_animal.CI = CI if CI is not None else None

        dummy_animal.get_calf_values = MagicMock(return_value={"dummy": "calf"}) if animal_type == Calf \
            else None
        dummy_animal.get_heiferI_values = MagicMock(return_value={"dummy": "heiferI"}) if animal_type == HeiferI \
            else None
        dummy_animal.get_heiferII_values = MagicMock(return_value={"dummy": "heiferII"}) if animal_type == HeiferII \
            else None
        dummy_animal.get_heiferIII_values = MagicMock(return_value={"dummy": "heiferIII"}) if animal_type == HeiferIII \
            else None
        dummy_animal.get_cow_values = MagicMock(return_value={"dummy": "cow"}) if animal_type == Cow \
            else None
        dummy_animal.get_replacement_values = MagicMock(return_value={"dummy": "replacement"}) if animal_type == Cow \
            else None
        return dummy_animal


@pytest.mark.parametrize("num_calf, num_heiferI, num_heiferII, num_heiferIII, num_cow, num_replacement", [
    (1, 1, 1, 1, 1, 1),
    (0, 0, 0, 0, 0, 0),
    (8, 44, 38, 5, 100, 500)
])
def test_get_herd_summary(num_calf: int,
                          num_heiferI: int,
                          num_heiferII: int,
                          num_heiferIII: int,
                          num_cow: int,
                          num_replacement: int,
                          mock_animal_population: AnimalPopulation) -> None:
    mock_calves = MockAnimals(num_animal=num_calf, animal_type=Calf, starting_id=0)
    mock_animal_population.calves = mock_calves.animals

    mock_heiferIs = MockAnimals(num_animal=num_heiferI, animal_type=HeiferI, starting_id=mock_calves.current_max_id + 1)
    mock_animal_population.heiferIs = mock_heiferIs.animals

    mock_heiferIIs = MockAnimals(num_animal=num_heiferII, animal_type=HeiferII,
                                 starting_id=mock_heiferIs.current_max_id + 1)
    mock_animal_population.heiferIIs = mock_heiferIIs.animals

    mock_heiferIIIs = MockAnimals(num_animal=num_heiferIII, animal_type=HeiferIII,
                                  starting_id=mock_heiferIIs.current_max_id + 1)
    mock_animal_population.heiferIIIs = mock_heiferIIIs.animals

    mock_cows = MockAnimals(num_animal=num_cow, animal_type=Cow, starting_id=mock_heiferIIIs.current_max_id + 1)
    mock_animal_population.cows = mock_cows.animals

    mock_replacement = MockAnimals(num_animal=num_replacement, animal_type=Cow,
                                   starting_id=mock_cows.current_max_id + 1)
    mock_animal_population.replacement = mock_replacement.animals

    expected_result = {
        'num_calf': num_calf,
        'num_heiferI': num_heiferI,
        'num_heiferII': num_heiferII,
        'num_heiferIII': num_heiferIII,
        'num_cow': num_cow,
        'num_replacement': num_replacement,

        'avg_calf_age': mock_calves.average_age,
        'avg_heiferI_age': mock_heiferIs.average_age,
        'avg_heiferII_age': mock_heiferIIs.average_age,
        'avg_heiferIII_age': mock_heiferIIIs.average_age,
        'avg_cow_age': mock_cows.average_age,
        'avg_replacement_age': mock_replacement.average_age,

        'cow_avg_days_in_preg': mock_cows.average_days_in_preg,
        'cow_avg_days_in_milk': mock_cows.average_days_in_milk,
        'cow_avg_parity': mock_cows.average_parity,
        'cow_avg_CI': mock_cows.average_CI
    }

    result = mock_animal_population.get_herd_summary()
    assert result == expected_result


@pytest.mark.parametrize("num_calf, num_heiferI, num_heiferII, num_heiferIII, num_cow, num_replacement", [
    (1, 1, 1, 1, 1, 1),
    (0, 0, 0, 0, 0, 0),
    (8, 44, 38, 5, 100, 500)
])
def test_repr(num_calf: int,
              num_heiferI: int,
              num_heiferII: int,
              num_heiferIII: int,
              num_cow: int,
              num_replacement: int,
              mock_animal_population: AnimalPopulation) -> None:
    mock_calves = MockAnimals(num_animal=num_calf, animal_type=Calf, starting_id=0)

    mock_heiferIs = MockAnimals(num_animal=num_heiferI, animal_type=HeiferI, starting_id=mock_calves.current_max_id + 1)

    mock_heiferIIs = MockAnimals(num_animal=num_heiferII, animal_type=HeiferII,
                                 starting_id=mock_heiferIs.current_max_id + 1)

    mock_heiferIIIs = MockAnimals(num_animal=num_heiferIII, animal_type=HeiferIII,
                                  starting_id=mock_heiferIIs.current_max_id + 1)

    mock_cows = MockAnimals(num_animal=num_cow, animal_type=Cow, starting_id=mock_heiferIIIs.current_max_id + 1)

    mock_replacement = MockAnimals(num_animal=num_replacement, animal_type=Cow,
                                   starting_id=mock_cows.current_max_id + 1)

    dummy_animal_population = AnimalPopulation(calves=mock_calves.animals,
                                               heiferIs=mock_heiferIs.animals,
                                               heiferIIs=mock_heiferIIs.animals,
                                               heiferIIIs=mock_heiferIIIs.animals,
                                               cows=mock_cows.animals,
                                               replacement=mock_replacement.animals)

    expected = {
        'calves': [{'dummy': 'calf'}] * num_calf,
        'heiferIs': [{'dummy': 'heiferI'}] * num_heiferI,
        'heiferIIs': [{'dummy': 'heiferII'}] * num_heiferII,
        'heiferIIIs': [{'dummy': 'heiferIII'}] * num_heiferIII,
        'cows': [{'dummy': 'cow'}] * num_cow,
        'replacement': [{'dummy': 'replacement'}] * num_replacement
    }

    actual = dummy_animal_population.__repr__()

    assert actual == expected

@pytest.mark.parametrize("num_calf, num_heiferI, num_heiferII, num_heiferIII, num_cow, num_replacement", [
    (1, 1, 1, 1, 1, 1),
    (0, 0, 0, 0, 0, 0),
    (8, 44, 38, 5, 100, 500)
])
def test_post_init(num_calf: int,
                   num_heiferI: int,
                   num_heiferII: int,
                   num_heiferIII: int,
                   num_cow: int,
                   num_replacement: int) -> None:
    mock_calves = MockAnimals(num_animal=num_calf, animal_type=Calf, starting_id=0)

    mock_heiferIs = MockAnimals(num_animal=num_heiferI, animal_type=HeiferI, starting_id=mock_calves.current_max_id + 1)

    mock_heiferIIs = MockAnimals(num_animal=num_heiferII, animal_type=HeiferII,
                                 starting_id=mock_heiferIs.current_max_id + 1)

    mock_heiferIIIs = MockAnimals(num_animal=num_heiferIII, animal_type=HeiferIII,
                                  starting_id=mock_heiferIIs.current_max_id + 1)

    mock_cows = MockAnimals(num_animal=num_cow, animal_type=Cow, starting_id=mock_heiferIIIs.current_max_id + 1)

    mock_replacement = MockAnimals(num_animal=num_replacement, animal_type=Cow,
                                   starting_id=mock_cows.current_max_id + 1)

    dummy_animal_population = AnimalPopulation(calves=mock_calves.animals,
                                               heiferIs=mock_heiferIs.animals,
                                               heiferIIs=mock_heiferIIs.animals,
                                               heiferIIIs=mock_heiferIIIs.animals,
                                               cows=mock_cows.animals,
                                               replacement=mock_replacement.animals)

    expected = mock_replacement.current_max_id

    actual = dummy_animal_population.current_animal_id
    assert actual == expected
