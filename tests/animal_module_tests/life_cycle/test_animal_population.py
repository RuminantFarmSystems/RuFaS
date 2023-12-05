import sys
from typing import List

import mock
import pytest

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


@pytest.mark.parametrize("num_animal", [
    0,
    1,
    10,
    500,
    10000
])
def test_get_animals(num_animal: int, mock_animal_population: AnimalPopulation) -> None:
    calves: List[Calf] = [mock.MagicMock(auto_spec=Calf)] * num_animal
    heiferIs: List[HeiferI] = [mock.MagicMock(auto_spec=HeiferI)] * num_animal
    heiferIIs: List[HeiferII] = [mock.MagicMock(auto_spec=HeiferII)] * num_animal
    heiferIIIs: List[HeiferIII] = [mock.MagicMock(auto_spec=HeiferIII)] * num_animal
    cows: List[Cow] = [mock.MagicMock(auto_spec=Cow)] * num_animal
    replacement: List[Cow] = [mock.MagicMock(auto_spec=Cow)] * num_animal

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
    assert len(result_calves) == num_animal

    assert result_heiferIs == heiferIs
    assert len(result_heiferIs) == num_animal

    assert result_heiferIIs == heiferIIs
    assert len(result_heiferIIs) == num_animal

    assert result_heiferIIIs == heiferIIIs
    assert len(result_heiferIIIs) == num_animal

    assert result_cows == cows
    assert len(result_cows) == num_animal

    assert result_replacement == replacement
    assert len(result_replacement) == num_animal
