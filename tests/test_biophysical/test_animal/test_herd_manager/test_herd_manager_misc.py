from random import randint, uniform
from typing import Any
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_grouping_scenarios import AnimalGroupingScenario
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.data_structures.feed_storage_to_animal_connection import RequestedFeed

from tests.test_biophysical.test_animal.test_herd_manager.pytest_fixtures import (
    config_json,
    animal_json,
    feed_json,
    mock_get_data_side_effect,
    mock_herd_manager,
    mock_herd,
    mock_animal,
    herd_manager,
)

assert config_json is not None
assert animal_json is not None
assert feed_json is not None
assert mock_get_data_side_effect is not None
assert mock_herd is not None
assert herd_manager is not None


def test_sort_cows_before_allocation(
    mock_get_data_side_effect: list[Any], mocker: MockerFixture, mock_herd: dict[str, list[Animal]]
) -> None:
    """Unit test for _sort_cows_before_allocation()"""
    cow_a = mock_animal(AnimalType.LAC_COW, days_in_milk=10)
    cow_b = mock_animal(AnimalType.LAC_COW, days_in_milk=5)
    cow_c = mock_animal(AnimalType.LAC_COW, days_in_milk=15)
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + [cow_a, cow_b, cow_c],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect,
    )

    expected_cow_order = mock_herd["dry_cows"] + [cow_b, cow_a, cow_c]

    herd_manager._sort_cows_before_allocation()

    assert herd_manager.cows == expected_cow_order


def test_collect_daily_feed_request(herd_manager: HerdManager) -> None:
    """Unit test for collect_daily_feed_request()"""
    expected_total_requested_feed = RequestedFeed({})
    for pen in herd_manager.all_pens:
        pen.ration = {randint(0, 100): uniform(0.0, 100.0)}
        expected_total_requested_feed += RequestedFeed(pen.ration) * len(pen.animals_in_pen.values())

    result = herd_manager.collect_daily_feed_request()
    assert result == expected_total_requested_feed


def test_print_herd_snapshot(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    """Unit test for print_herd_snapshot()"""
    mock_print = mocker.patch("builtins.print")
    herd_manager.print_herd_snapshot("dummy_text")
    assert mock_print.call_count == 1
    assert mock_print.call_args == call(
        f"{'dummy_text'}\tcalves: {len(herd_manager.calves)}\t"
        f"heiferIs: {len(herd_manager.heiferIs)}\t"
        f"heiferIIs: {len(herd_manager.heiferIIs)}\t"
        f"heiferIIIs: {len(herd_manager.heiferIIIs)}\t"
        f"cows: {len(herd_manager.cows)}\t"
    )


@pytest.mark.parametrize(
    "herd_data, simulate_animals",
    [
        ({"calf_num": 0, "heiferI_num": 0, "heiferII_num": 0, "heiferIII_num_springers": 0, "cow_num": 0}, False),
        ({"calf_num": 1, "heiferI_num": 0, "heiferII_num": 0, "heiferIII_num_springers": 0, "cow_num": 0}, False),
        ({"calf_num": 0, "heiferI_num": 2, "heiferII_num": 0, "heiferIII_num_springers": 0, "cow_num": 0}, False),
        ({"calf_num": 0, "heiferI_num": 0, "heiferII_num": 3, "heiferIII_num_springers": 0, "cow_num": 0}, False),
        ({"calf_num": 0, "heiferI_num": 0, "heiferII_num": 0, "heiferIII_num_springers": 4, "cow_num": 0}, False),
        ({"calf_num": 0, "heiferI_num": 0, "heiferII_num": 0, "heiferIII_num_springers": 0, "cow_num": 5}, False),
        ({"calf_num": 8, "heiferI_num": 10, "heiferII_num": 5, "heiferIII_num_springers": 9, "cow_num": 5}, True),
        ({"calf_num": 5, "heiferI_num": 8, "heiferII_num": 3, "heiferIII_num_springers": 0, "cow_num": 0}, False),
        ({"calf_num": 0, "heiferI_num": 0, "heiferII_num": 2, "heiferIII_num_springers": 4, "cow_num": 0}, False),
        ({"calf_num": 8, "heiferI_num": 8, "heiferII_num": 8, "heiferIII_num_springers": 5, "cow_num": 5}, False),
        ({"calf_num": 5, "heiferI_num": 8, "heiferII_num": 8, "heiferIII_num_springers": 8, "cow_num": 0}, False),
    ],
)
def test_print_animal_num_warnings(
    herd_data: dict[str, int], simulate_animals: bool, herd_manager: HerdManager, mocker: MockerFixture
) -> None:
    """Unit test for _print_animal_num_warnings()"""
    herd_manager.simulate_animals = simulate_animals

    mock_om_add_log = mocker.patch.object(herd_manager.om, "add_log")
    mock_om_add_warning = mocker.patch.object(herd_manager.om, "add_warning")

    animal_keys = {
        "calf_num",
        "heiferI_num",
        "heiferII_num",
        "heiferIII_num_springers",
        "cow_num",
    }
    info_map = {
        "class": herd_manager.__class__.__name__,
        "function": HerdManager._print_animal_num_warnings.__name__,
        "simulate_animals": simulate_animals,
        "herd_data_animal_nums": {key: herd_data[key] for key in animal_keys},
    }

    herd_manager._print_animal_num_warnings(herd_data)

    if simulate_animals:
        mock_om_add_log.assert_called_once_with("simulate_animals_flag", "simulate_animals is true", info_map)
        mock_om_add_warning.assert_not_called()
    else:
        expected_add_warning_counts = len([value for value in herd_data.values() if value > 0])
        assert mock_om_add_warning.call_count == expected_add_warning_counts
        mock_om_add_log.assert_called_once_with(
            "num_warnings_associated_with_simulate_animals",
            f"{expected_add_warning_counts} warnings were associated with simulate_animals",
            info_map,
        )


@pytest.mark.parametrize(
    "original_grouping_scenario, new_grouping_scenario",
    [
        (
            AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW,
            AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW,
        ),
        (
            AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW,
            AnimalGroupingScenario.CALF__GROWING_AND_CLOSE_UP__LACCOW,
        ),
        (
            AnimalGroupingScenario.CALF__GROWING_AND_CLOSE_UP__LACCOW,
            AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW,
        ),
        (
            AnimalGroupingScenario.CALF__GROWING_AND_CLOSE_UP__LACCOW,
            AnimalGroupingScenario.CALF__GROWING_AND_CLOSE_UP__LACCOW,
        ),
    ],
)
def test_set_animal_grouping_scenario(
    original_grouping_scenario: AnimalGroupingScenario, new_grouping_scenario: AnimalGroupingScenario
) -> None:
    """Unit test for set_animal_grouping_scenario()"""
    HerdManager.ANIMAL_GROUPING_SCENARIO = original_grouping_scenario
    assert HerdManager.ANIMAL_GROUPING_SCENARIO == original_grouping_scenario

    HerdManager.set_animal_grouping_scenario(new_grouping_scenario)
    assert HerdManager.ANIMAL_GROUPING_SCENARIO == new_grouping_scenario
