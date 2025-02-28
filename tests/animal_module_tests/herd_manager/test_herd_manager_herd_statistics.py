from typing import Any

import pytest
from numpy.ma.testutils import approx
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.herd_manager import HerdManager

from tests.animal_module_tests.herd_manager.pytest_fixtures import (
    config_json, animal_json, manure_management_json, feed_json, mock_get_data_side_effect,
    mock_herd_manager, mock_herd, herd_manager
)
assert config_json
assert animal_json
assert manure_management_json
assert feed_json
assert mock_get_data_side_effect

def test_update_herd_statistics(
    herd_manager: HerdManager, mocker: MockerFixture,
) -> None:
    mock_calculate_herd_percentages = mocker.patch.object(herd_manager, "_calculate_herd_percentages")
    mock_update_heifer_reproduction_statistics = mocker.patch.object(
        herd_manager, "_update_heifer_reproduction_statistics"
    )
    mock_update_cow_reproduction_statistics = mocker.patch.object(herd_manager, "_update_cow_reproduction_statistics")
    mock_update_cow_milking_statistics = mocker.patch.object(herd_manager, "_update_cow_milking_statistics")
    mock_update_cow_pregnancy_statistics = mocker.patch.object(herd_manager, "_update_cow_pregnancy_statistics")
    mock_update_cow_parity_statistics = mocker.patch.object(herd_manager, "_update_cow_parity_statistics")
    mock_calculate_cow_percentages = mocker.patch.object(herd_manager, "_calculate_cow_percentages")
    mock_update_average_mature_body_weight = mocker.patch.object(herd_manager, "_update_average_mature_body_weight")
    mock_update_average_cow_body_weight = mocker.patch.object(herd_manager, "_update_average_cow_body_weight")
    mock_update_average_cow_parity = mocker.patch.object(herd_manager, "_update_average_cow_parity")

    herd_manager.update_herd_statistics()

    assert herd_manager.herd_statistics.calf_num == len(herd_manager.calves)
    assert herd_manager.herd_statistics.heiferI_num == len(herd_manager.heiferIs)
    assert herd_manager.herd_statistics.heiferII_num == len(herd_manager.heiferIIs)
    assert herd_manager.herd_statistics.heiferIII_num == len(herd_manager.heiferIIIs)
    assert herd_manager.herd_statistics.cow_num == len(herd_manager.cows)

    mock_calculate_herd_percentages.assert_called_once_with()
    mock_update_heifer_reproduction_statistics.assert_called_once_with()
    mock_update_cow_reproduction_statistics.assert_called_once_with()
    mock_update_cow_milking_statistics.assert_called_once_with()
    mock_update_cow_pregnancy_statistics.assert_called_once_with()
    mock_update_cow_parity_statistics.assert_called_once_with()
    mock_calculate_cow_percentages.assert_called_once_with()
    mock_update_average_mature_body_weight.assert_called_once_with()
    mock_update_average_cow_body_weight.assert_called_once_with()
    mock_update_average_cow_parity.assert_called_once_with()


def test_calculate_herd_percentages(
    herd_manager: HerdManager, mock_herd: dict[str, list[Animal]]
) -> None:
    animals = (
        mock_herd["calves"]
        + mock_herd["heiferIs"]
        + mock_herd["heiferIIs"]
        + mock_herd["heiferIIIs"]
        + mock_herd["dry_cows"]
        + mock_herd["lac_cows"]
    )

    herd_manager.herd_statistics.calf_num = len(herd_manager.calves)
    herd_manager.herd_statistics.heiferI_num = len(herd_manager.heiferIs)
    herd_manager.herd_statistics.heiferII_num = len(herd_manager.heiferIIs)
    herd_manager.herd_statistics.heiferIII_num = len(herd_manager.heiferIIIs)
    herd_manager.herd_statistics.cow_num = len(herd_manager.cows)

    herd_manager._calculate_herd_percentages()

    assert approx(herd_manager.herd_statistics.calf_percent, len(herd_manager.calves) / len(animals) * 100)
    assert approx(herd_manager.herd_statistics.heiferI_percent, len(herd_manager.heiferIs) / len(animals) * 100)
    assert approx(herd_manager.herd_statistics.heiferII_percent, len(herd_manager.heiferIIs) / len(animals) * 100)
    assert approx(herd_manager.herd_statistics.heiferIII_percent, len(herd_manager.heiferIIIs) / len(animals) * 100)
    assert approx(herd_manager.herd_statistics.cow_percent, len(herd_manager.cows) / len(animals) * 100)


def test_calculate_cow_percentages(
    herd_manager: HerdManager, mock_herd: dict[str, list[Animal]]
) -> None:

    herd_manager.herd_statistics.cow_num = len(herd_manager.cows)
    herd_manager.herd_statistics.dry_cow_num = len(mock_herd["dry_cows"])
    herd_manager.herd_statistics.milking_cow_num = len(mock_herd["lac_cows"])
    herd_manager.herd_statistics.preg_cow_num = len([cow for cow in herd_manager.cows if cow.is_pregnant])
    herd_manager.herd_statistics.open_cow_num = len([cow for cow in herd_manager.cows if not cow.is_pregnant])

    herd_manager._calculate_cow_percentages()

    assert approx(
        herd_manager.herd_statistics.dry_cow_percent,
        (herd_manager.herd_statistics.dry_cow_num / herd_manager.herd_statistics.cow_num * 100),
    )
    assert approx(
        herd_manager.herd_statistics.milking_cow_percent,
        (herd_manager.herd_statistics.milking_cow_num / herd_manager.herd_statistics.cow_num * 100),
    )
    assert approx(
        herd_manager.herd_statistics.preg_cow_percent,
        (herd_manager.herd_statistics.preg_cow_num / herd_manager.herd_statistics.cow_num * 100),
    )
    assert approx(
        herd_manager.herd_statistics.non_preg_cow_percent,
        (herd_manager.herd_statistics.open_cow_num / herd_manager.herd_statistics.cow_num * 100),
    )


@pytest.mark.parametrize(
    "cull_reason_stats, cow_herd_exit_num, expected_cull_reason_stats_percent",
    [
        # 1. All zeros with cow_herd_exit_num = 0 -> denominator=1, all 0.0%
        (
            {
                animal_constants.DEATH_CULL: 0,
                animal_constants.LOW_PROD_CULL: 0,
                animal_constants.LAMENESS_CULL: 0,
                animal_constants.INJURY_CULL: 0,
                animal_constants.MASTITIS_CULL: 0,
                animal_constants.DISEASE_CULL: 0,
                animal_constants.UDDER_CULL: 0,
                animal_constants.UNKNOWN_CULL: 0,
            },
            0,
            {
                animal_constants.DEATH_CULL: 0.0,
                animal_constants.LOW_PROD_CULL: 0.0,
                animal_constants.LAMENESS_CULL: 0.0,
                animal_constants.INJURY_CULL: 0.0,
                animal_constants.MASTITIS_CULL: 0.0,
                animal_constants.DISEASE_CULL: 0.0,
                animal_constants.UDDER_CULL: 0.0,
                animal_constants.UNKNOWN_CULL: 0.0,
            },
        ),
        # 2. One reason has all culls, matches exit_num -> 100% that reason
        (
            {
                animal_constants.DEATH_CULL: 5,
                animal_constants.LOW_PROD_CULL: 0,
                animal_constants.LAMENESS_CULL: 0,
                animal_constants.INJURY_CULL: 0,
                animal_constants.MASTITIS_CULL: 0,
                animal_constants.DISEASE_CULL: 0,
                animal_constants.UDDER_CULL: 0,
                animal_constants.UNKNOWN_CULL: 0,
            },
            5,
            {
                animal_constants.DEATH_CULL: 100.0,
                animal_constants.LOW_PROD_CULL: 0.0,
                animal_constants.LAMENESS_CULL: 0.0,
                animal_constants.INJURY_CULL: 0.0,
                animal_constants.MASTITIS_CULL: 0.0,
                animal_constants.DISEASE_CULL: 0.0,
                animal_constants.UDDER_CULL: 0.0,
                animal_constants.UNKNOWN_CULL: 0.0,
            },
        ),
        # 3. Multiple reasons evenly split
        # Suppose total exit = 10, death=5, low_prod=5 -> each 50%
        (
            {
                animal_constants.DEATH_CULL: 5,
                animal_constants.LOW_PROD_CULL: 5,
                animal_constants.LAMENESS_CULL: 0,
                animal_constants.INJURY_CULL: 0,
                animal_constants.MASTITIS_CULL: 0,
                animal_constants.DISEASE_CULL: 0,
                animal_constants.UDDER_CULL: 0,
                animal_constants.UNKNOWN_CULL: 0,
            },
            10,
            {
                animal_constants.DEATH_CULL: 50.0,
                animal_constants.LOW_PROD_CULL: 50.0,
                animal_constants.LAMENESS_CULL: 0.0,
                animal_constants.INJURY_CULL: 0.0,
                animal_constants.MASTITIS_CULL: 0.0,
                animal_constants.DISEASE_CULL: 0.0,
                animal_constants.UDDER_CULL: 0.0,
                animal_constants.UNKNOWN_CULL: 0.0,
            },
        ),
        # 4. Partial distribution
        # total exit = 10, death=3, low=2, others=0 -> death=30%, low=20%
        (
            {
                animal_constants.DEATH_CULL: 3,
                animal_constants.LOW_PROD_CULL: 2,
                animal_constants.LAMENESS_CULL: 0,
                animal_constants.INJURY_CULL: 0,
                animal_constants.MASTITIS_CULL: 0,
                animal_constants.DISEASE_CULL: 0,
                animal_constants.UDDER_CULL: 0,
                animal_constants.UNKNOWN_CULL: 0,
            },
            10,
            {
                animal_constants.DEATH_CULL: 30.0,
                animal_constants.LOW_PROD_CULL: 20.0,
                animal_constants.LAMENESS_CULL: 0.0,
                animal_constants.INJURY_CULL: 0.0,
                animal_constants.MASTITIS_CULL: 0.0,
                animal_constants.DISEASE_CULL: 0.0,
                animal_constants.UDDER_CULL: 0.0,
                animal_constants.UNKNOWN_CULL: 0.0,
            },
        ),
        # 5. Non-zero exit, some reasons zero
        # total exit=10, death=2, disease=8
        # death=(2/10)*100=20%, disease=(8/10)*100=80%, rest=0%
        (
            {
                animal_constants.DEATH_CULL: 2,
                animal_constants.LOW_PROD_CULL: 0,
                animal_constants.LAMENESS_CULL: 0,
                animal_constants.INJURY_CULL: 0,
                animal_constants.MASTITIS_CULL: 0,
                animal_constants.DISEASE_CULL: 8,
                animal_constants.UDDER_CULL: 0,
                animal_constants.UNKNOWN_CULL: 0,
            },
            10,
            {
                animal_constants.DEATH_CULL: 20.0,
                animal_constants.LOW_PROD_CULL: 0.0,
                animal_constants.LAMENESS_CULL: 0.0,
                animal_constants.INJURY_CULL: 0.0,
                animal_constants.MASTITIS_CULL: 0.0,
                animal_constants.DISEASE_CULL: 80.0,
                animal_constants.UDDER_CULL: 0.0,
                animal_constants.UNKNOWN_CULL: 0.0,
            },
        ),
    ],
)
def test_calculate_cull_reason_stats_percent(
    cull_reason_stats: dict[str, int],
    cow_herd_exit_num: int,
    expected_cull_reason_stats_percent: dict[str, float],
    herd_manager: HerdManager
) -> None:
    herd_manager.herd_statistics.cow_herd_exit_num = cow_herd_exit_num
    herd_manager.herd_statistics.cull_reason_stats = cull_reason_stats

    herd_manager._calculate_cull_reason_percentages()

    for key, value in herd_manager.herd_statistics.cull_reason_stats_percent.items():
        assert approx(value, expected_cull_reason_stats_percent[key])