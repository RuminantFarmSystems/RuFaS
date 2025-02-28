from typing import Any

from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType

from tests.animal_module_tests.herd_manager.pytest_fixtures import (
    config_json, animal_json, manure_management_json, feed_json, mock_get_data_side_effect,
    mock_herd_manager, mock_herd, mock_animal
)
assert config_json
assert animal_json
assert manure_management_json
assert feed_json
assert mock_get_data_side_effect


def test_sort_cows_before_allocation(
    mock_get_data_side_effect: list[Any], mocker: MockerFixture, mock_herd: dict[str, list[Animal]]
) -> None:
    cow_a = mock_animal(AnimalType.LAC_COW, mocker, days_in_milk=10)
    cow_b = mock_animal(AnimalType.LAC_COW, mocker, days_in_milk=5)
    cow_c = mock_animal(AnimalType.LAC_COW, mocker, days_in_milk=15)
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

