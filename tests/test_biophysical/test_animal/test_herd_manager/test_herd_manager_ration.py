from typing import Any

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from tests.test_biophysical.test_animal.test_herd_manager.pytest_fixtures import (
    config_json, animal_json, manure_management_json, feed_json, mock_get_data_side_effect,
    mock_herd_manager, mock_herd
)

assert config_json is not None
assert animal_json is not None
assert manure_management_json is not None
assert feed_json is not None
assert mock_get_data_side_effect is not None
assert mock_herd is not None


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
