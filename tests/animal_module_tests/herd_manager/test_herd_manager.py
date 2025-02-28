from collections import defaultdict
from datetime import datetime
from typing import Any, Callable

import pytest
from mock.mock import MagicMock, call
from numpy.ma.testutils import approx
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus, Breed
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import NewBornCalfValuesTypedDict
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.daily_routines_output import DailyRoutinesOutput
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.biophysical.feed.feed import Feed
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.feed_storage_to_animal_connection import TotalInventory
from RUFAS.enums import AnimalCombination
from RUFAS.biophysical.animal.data_types.animal_population import AnimalPopulation
from RUFAS.time import Time
from RUFAS.weather import Weather
from tests.animal_module_tests.herd_manager.pytest_fixtures import (
    config_json, animal_json, manure_management_json, feed_json, mock_get_data_side_effect,
    mock_herd_manager, mock_herd, mock_animal, mock_pen
)
from tests.animal_module_tests.test_animal import cow_a, mock_available_feeds
from tests.test_weather import mock_current_day_conditions



@pytest.mark.parametrize(
    "simulation_day, formulation_interval, expected",
    [
        # simulation_day == 0 scenario
        (0, 10, True),  # day=0 -> True regardless of interval
        # formulation_interval == 1 scenario
        (5, 1, True),  # interval=1 -> True for any simulation_day
        (10, 1, True),
        # simulation_day % formulation_interval == 1 scenario
        (7, 3, True),  # 7 % 3 = 1 -> True
        (1, 10, True),  # 1 % 10 = 1 -> True
        # None of the conditions met (should return False)
        (2, 2, False),  # 2 % 2 = 0, interval=2 != 1, day=2 !=0
        (10, 5, False),  # 10 % 5 = 0, interval=5 != 1, day=10 !=0
        (3, 4, False),  # 3 % 4 = 3, not 1; interval=4 != 1; day=3 !=0
    ],
)
def test_end_ration_interval(
    simulation_day: int,
    formulation_interval: int,
    expected: bool,
    mock_get_data_side_effect: list[Any],
    mocker: MockerFixture,
    mock_herd: dict[str, list[Animal]],
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect,
    )
    herd_manager.formulation_interval = formulation_interval

    result = herd_manager.end_ration_interval(simulation_day=simulation_day)

    assert result == expected
