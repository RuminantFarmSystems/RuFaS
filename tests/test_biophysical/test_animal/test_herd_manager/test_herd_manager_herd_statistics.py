from random import randint, uniform

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import SoldAnimalTypedDict, StillbornCalfTypedDict
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.herd_manager import HerdManager

from tests.test_biophysical.test_animal.test_herd_manager.pytest_fixtures import (
    config_json,
    animal_json,
    feed_json,
    mock_get_data_side_effect,
    mock_herd,
    herd_manager,
    mock_animal,
    mock_sold_animal_typed_dict,
    mock_stillborn_animal_typed_dict,
)

assert config_json is not None
assert animal_json is not None
assert feed_json is not None
assert mock_get_data_side_effect is not None
assert mock_herd is not None
assert herd_manager is not None
assert mock_sold_animal_typed_dict is not None
assert mock_stillborn_animal_typed_dict is not None


def mock_cows_with_specific_parity(number_of_cows: int, parity: int) -> tuple[list[Animal], dict[str, float]]:
    """Mock cows with specific parity for testing _update_cow_parity_statistics()"""
    cows = [
        mock_animal(
            animal_type=AnimalType.LAC_COW,
            calves=parity,
            days_born=randint(0, 5000),
            calving_to_pregnancy_time=randint(0, 500),
            most_recent_new_birth_age=randint(0, 3000),
        )
        for _ in range(number_of_cows)
    ]
    expected_average_age = sum([cow.days_born for cow in cows]) / number_of_cows if number_of_cows > 0 else 0

    cow_calving_ages = [cow.events.get_most_recent_date(animal_constants.NEW_BIRTH) for cow in cows]
    cow_calving_ages = [calving_age for calving_age in cow_calving_ages if calving_age > 0]
    expected_average_age_for_calving = sum(cow_calving_ages) / number_of_cows if number_of_cows > 0 else 0

    calving_to_pregnancy_times = [cow.reproduction.reproduction_statistics.calving_to_pregnancy_time for cow in cows]
    calving_to_pregnancy_times = [
        calving_to_pregnancy_time
        for calving_to_pregnancy_time in calving_to_pregnancy_times
        if calving_to_pregnancy_time > 0
    ]
    expected_average_calving_to_pregnancy_time = (
        sum(calving_to_pregnancy_times) / number_of_cows if number_of_cows > 0 else 0
    )

    return cows, {
        "average_age": expected_average_age,
        "average_age_for_calving": expected_average_age_for_calving,
        "average_calving_to_pregnancy_time": expected_average_calving_to_pregnancy_time,
    }


def test_update_herd_statistics(
    herd_manager: HerdManager,
    mocker: MockerFixture,
) -> None:
    """Unit test for update_herd_statistics()"""
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


def test_calculate_herd_percentages(herd_manager: HerdManager, mock_herd: dict[str, list[Animal]]) -> None:
    """Unit test for _calculate_herd_percentages()"""
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

    assert herd_manager.herd_statistics.calf_percent == pytest.approx(len(herd_manager.calves) / len(animals) * 100)
    assert herd_manager.herd_statistics.heiferI_percent == pytest.approx(
        len(herd_manager.heiferIs) / len(animals) * 100
    )
    assert herd_manager.herd_statistics.heiferII_percent == pytest.approx(
        len(herd_manager.heiferIIs) / len(animals) * 100
    )
    assert herd_manager.herd_statistics.heiferIII_percent == pytest.approx(
        len(herd_manager.heiferIIIs) / len(animals) * 100
    )
    assert herd_manager.herd_statistics.cow_percent == pytest.approx(len(herd_manager.cows) / len(animals) * 100)


def test_calculate_cow_percentages(herd_manager: HerdManager, mock_herd: dict[str, list[Animal]]) -> None:
    """Unit test for _calculate_cow_percentages()"""

    herd_manager.herd_statistics.cow_num = len(herd_manager.cows)
    herd_manager.herd_statistics.dry_cow_num = len(mock_herd["dry_cows"])
    herd_manager.herd_statistics.milking_cow_num = len(mock_herd["lac_cows"])
    herd_manager.herd_statistics.preg_cow_num = len([cow for cow in herd_manager.cows if cow.is_pregnant])
    herd_manager.herd_statistics.open_cow_num = len([cow for cow in herd_manager.cows if not cow.is_pregnant])

    herd_manager._calculate_cow_percentages()

    assert herd_manager.herd_statistics.dry_cow_percent == pytest.approx(
        herd_manager.herd_statistics.dry_cow_num / herd_manager.herd_statistics.cow_num * 100
    )
    assert herd_manager.herd_statistics.milking_cow_percent == pytest.approx(
        herd_manager.herd_statistics.milking_cow_num / herd_manager.herd_statistics.cow_num * 100
    )
    assert herd_manager.herd_statistics.preg_cow_percent == pytest.approx(
        herd_manager.herd_statistics.preg_cow_num / herd_manager.herd_statistics.cow_num * 100
    )
    assert herd_manager.herd_statistics.non_preg_cow_percent == pytest.approx(
        herd_manager.herd_statistics.open_cow_num / herd_manager.herd_statistics.cow_num * 100
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
    herd_manager: HerdManager,
) -> None:
    """Unit test for _calculate_cull_reason_percentages()"""
    herd_manager.herd_statistics.cow_herd_exit_num = cow_herd_exit_num
    herd_manager.herd_statistics.cull_reason_stats = cull_reason_stats

    herd_manager._calculate_cull_reason_percentages()

    for key, value in herd_manager.herd_statistics.cull_reason_stats_percent.items():
        assert value == pytest.approx(expected_cull_reason_stats_percent[key])


@pytest.mark.parametrize(
    "number_of_parity_1_cows, number_of_parity_2_cows, number_of_parity_3_cows, "
    "number_of_parity_4_cows, number_of_parity_5_cows, number_of_parity_6_or_more_cows",
    [(0, 0, 0, 0, 0, 0), (10, 8, 15, 10, 10, 8)],
)
def test_update_cow_parity_statistics(
    number_of_parity_1_cows: int,
    number_of_parity_2_cows: int,
    number_of_parity_3_cows: int,
    number_of_parity_4_cows: int,
    number_of_parity_5_cows: int,
    number_of_parity_6_or_more_cows: int,
    herd_manager: HerdManager,
) -> None:
    """Unit test for _update_cow_parity_statistics()"""
    total_number_of_cows = (
        number_of_parity_1_cows
        + number_of_parity_2_cows
        + number_of_parity_3_cows
        + number_of_parity_4_cows
        + number_of_parity_5_cows
        + number_of_parity_6_or_more_cows
    )
    number_of_parity_greater_than5_cows = number_of_parity_6_or_more_cows
    parity_1_cows, parity_1_stats = mock_cows_with_specific_parity(number_of_parity_1_cows, parity=1)
    parity_2_cows, parity_2_stats = mock_cows_with_specific_parity(number_of_parity_2_cows, parity=2)
    parity_3_cows, parity_3_stats = mock_cows_with_specific_parity(number_of_parity_3_cows, parity=3)
    parity_4_cows, parity_4_stats = mock_cows_with_specific_parity(number_of_parity_4_cows, parity=4)
    parity_5_cows, parity_5_stats = mock_cows_with_specific_parity(number_of_parity_5_cows, parity=5)
    parity_6_or_more_cows, parity_6_or_more_stats = mock_cows_with_specific_parity(
        number_of_parity_6_or_more_cows, parity=6
    )

    expected_num_cow_for_parity = {
        "1": number_of_parity_1_cows,
        "2": number_of_parity_2_cows,
        "3": number_of_parity_3_cows,
        "4": number_of_parity_4_cows,
        "5": number_of_parity_5_cows,
        "greater_than_5": number_of_parity_greater_than5_cows,
    }
    expected_parity_percent = {
        "1": number_of_parity_1_cows / total_number_of_cows * 100 if total_number_of_cows > 0 else 0.0,
        "2": number_of_parity_2_cows / total_number_of_cows * 100 if total_number_of_cows > 0 else 0.0,
        "3": number_of_parity_3_cows / total_number_of_cows * 100 if total_number_of_cows > 0 else 0.0,
        "4": number_of_parity_4_cows / total_number_of_cows * 100 if total_number_of_cows > 0 else 0.0,
        "5": number_of_parity_5_cows / total_number_of_cows * 100 if total_number_of_cows > 0 else 0.0,
        "greater_than_5": (
            number_of_parity_greater_than5_cows / total_number_of_cows * 100 if total_number_of_cows > 0 else 0.0
        ),
    }

    herd_manager.herd_statistics.cow_num = total_number_of_cows
    herd_manager.cows = (
        parity_1_cows + parity_2_cows + parity_3_cows + parity_4_cows + parity_5_cows + parity_6_or_more_cows
    )
    herd_manager.herd_statistics.reset_parity()
    herd_manager._update_cow_parity_statistics()

    assert herd_manager.herd_statistics.num_cow_for_parity == expected_num_cow_for_parity
    assert herd_manager.herd_statistics.percent_cow_for_parity == expected_parity_percent
    assert herd_manager.herd_statistics.avg_age_for_parity == pytest.approx(
        {
            "1": parity_1_stats["average_age"],
            "2": parity_2_stats["average_age"],
            "3": parity_3_stats["average_age"],
            "4": parity_4_stats["average_age"],
            "5": parity_5_stats["average_age"],
            "greater_than_5": parity_6_or_more_stats["average_age"],
        }
    )
    assert herd_manager.herd_statistics.avg_age_for_calving == pytest.approx(
        {
            "1": parity_1_stats["average_age_for_calving"],
            "2": parity_2_stats["average_age_for_calving"],
            "3": parity_3_stats["average_age_for_calving"],
            "4": parity_4_stats["average_age_for_calving"],
            "5": parity_5_stats["average_age_for_calving"],
            "greater_than_5": parity_6_or_more_stats["average_age_for_calving"],
        }
    )
    assert herd_manager.herd_statistics.avg_calving_to_preg_time == pytest.approx(
        {
            "1": parity_1_stats["average_calving_to_pregnancy_time"],
            "2": parity_2_stats["average_calving_to_pregnancy_time"],
            "3": parity_3_stats["average_calving_to_pregnancy_time"],
            "4": parity_4_stats["average_calving_to_pregnancy_time"],
            "5": parity_5_stats["average_calving_to_pregnancy_time"],
            "greater_than_5": parity_6_or_more_stats["average_calving_to_pregnancy_time"],
        }
    )


def test_update_cow_milking_statistics_value_error(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    """Unit test for _update_cow_milking_statistics()"""
    mock_om_add_error = mocker.patch.object(herd_manager.om, "add_error")
    info_map = {
        "class": herd_manager.__class__.__name__,
        "function": herd_manager._update_cow_milking_statistics.__name__,
    }
    lactating_cows = [
        mock_animal(
            AnimalType.LAC_COW,
            days_in_milk=randint(1, 500),
            daily_milk_produced=uniform(0, 100),
            milk_fat_content=uniform(0, 25),
            milk_protein_content=uniform(0, 25),
        )
        for _ in range(randint(0, 100))
    ]
    dry_cows = [
        mock_animal(
            AnimalType.DRY_COW,
            days_in_milk=0,
            daily_milk_produced=5,
            milk_fat_content=1,
            milk_protein_content=1,
        )
        for _ in range(randint(0, 100))
    ]
    all_cows = lactating_cows + dry_cows
    herd_manager.cows = all_cows
    herd_manager.herd_statistics.reset_daily_stats()
    with pytest.raises(ValueError):
        herd_manager._update_cow_milking_statistics()
        mock_om_add_error.assert_called_once_with("Dry cow milking error", "Unexpected milking from dry cows", info_map)


def test_update_cow_milking_statistics(herd_manager: HerdManager) -> None:
    """Unit test for _update_cow_milking_statistics()"""
    lactating_cows = [
        mock_animal(
            AnimalType.LAC_COW,
            days_in_milk=randint(1, 500),
            daily_milk_produced=uniform(0, 100),
            milk_fat_content=uniform(0, 25),
            milk_protein_content=uniform(0, 25),
        )
        for _ in range(randint(0, 100))
    ]
    dry_cows = [
        mock_animal(
            AnimalType.DRY_COW,
            days_in_milk=0,
        )
        for _ in range(randint(0, 100))
    ]
    all_cows = lactating_cows + dry_cows
    vwp_cows = [cow for cow in all_cows if cow.days_in_milk < AnimalConfig.voluntary_waiting_period]

    expected_milking_cow_num, expected_dry_cow_num, expected_vwp_cow_num = (
        len(lactating_cows),
        len(dry_cows),
        len(vwp_cows),
    )

    expected_average_days_in_milk = (
        sum(cow.days_in_milk for cow in lactating_cows) / expected_milking_cow_num
        if expected_milking_cow_num > 0
        else 0.0
    )
    expected_daily_milk_production = sum([cow.milk_production.daily_milk_produced for cow in lactating_cows])
    expected_fat_kg = sum([cow.milk_production.fat_content for cow in lactating_cows])
    expected_protein_kg = sum([cow.milk_production.true_protein_content for cow in lactating_cows])
    expected_fat_percent = (
        expected_fat_kg / expected_daily_milk_production * 100 if expected_daily_milk_production > 0 else 0.0
    )
    expected_protein_percent = (
        expected_protein_kg / expected_daily_milk_production * 100 if expected_daily_milk_production > 0 else 0.0
    )

    herd_manager.cows = all_cows
    herd_manager.herd_statistics.reset_daily_stats()
    herd_manager._update_cow_milking_statistics()

    assert herd_manager.herd_statistics.milking_cow_num == expected_milking_cow_num
    assert herd_manager.herd_statistics.dry_cow_num == expected_dry_cow_num
    assert herd_manager.herd_statistics.vwp_cow_num == expected_vwp_cow_num

    assert herd_manager.herd_statistics.avg_days_in_milk == expected_average_days_in_milk
    assert herd_manager.herd_statistics.daily_milk_production == expected_daily_milk_production
    assert herd_manager.herd_statistics.herd_milk_fat_kg == expected_fat_kg
    assert herd_manager.herd_statistics.herd_milk_protein_kg == expected_protein_kg
    assert herd_manager.herd_statistics.herd_milk_fat_percent == expected_fat_percent
    assert herd_manager.herd_statistics.herd_milk_protein_percent == expected_protein_percent


def test_update_cow_pregnancy_statistics(herd_manager: HerdManager) -> None:
    """Unit test for _update_cow_pregnancy_statistics()"""
    num_preg_lac_cows, num_open_lac_cows, num_preg_dry_cows, num_open_dry_cows = (
        randint(1, 100),
        randint(1, 100),
        randint(1, 100),
        randint(1, 100),
    )
    pregnant_lac_cows = [
        mock_animal(AnimalType.LAC_COW, days_in_pregnancy=randint(1, 500)) for _ in range(num_preg_lac_cows)
    ]
    open_lac_cows = [mock_animal(AnimalType.LAC_COW, days_in_pregnancy=0) for _ in range(num_open_lac_cows)]
    pregnant_dry_cows = [
        mock_animal(AnimalType.DRY_COW, days_in_pregnancy=randint(1, 500)) for _ in range(num_preg_dry_cows)
    ]
    open_dry_cows = [mock_animal(AnimalType.DRY_COW, days_in_pregnancy=0) for _ in range(num_open_dry_cows)]

    expected_preg_cow_num = num_preg_lac_cows + num_preg_dry_cows
    expected_open_cow_num = num_open_lac_cows + num_open_dry_cows
    expected_avg_days_in_preg = (
        sum([cow.days_in_pregnancy for cow in pregnant_lac_cows + pregnant_dry_cows]) / expected_preg_cow_num
        if expected_preg_cow_num > 0
        else 0.0
    )

    herd_manager.cows = pregnant_lac_cows + open_lac_cows + pregnant_dry_cows + open_dry_cows
    herd_manager.herd_statistics.reset_daily_stats()
    herd_manager._update_cow_pregnancy_statistics()

    assert herd_manager.herd_statistics.preg_cow_num == expected_preg_cow_num
    assert herd_manager.herd_statistics.open_cow_num == expected_open_cow_num
    assert herd_manager.herd_statistics.avg_days_in_preg == expected_avg_days_in_preg


def test_update_sold_and_died_cow_statistics(
    mock_sold_animal_typed_dict: SoldAnimalTypedDict, herd_manager: HerdManager, mocker: MockerFixture
) -> None:
    """Unit test for _update_sold_and_died_cow_statistics()"""
    cull_reasons = [
        animal_constants.LOW_PROD_CULL,
        animal_constants.LAMENESS_CULL,
        animal_constants.INJURY_CULL,
        animal_constants.MASTITIS_CULL,
        animal_constants.DISEASE_CULL,
        animal_constants.UDDER_CULL,
        animal_constants.UNKNOWN_CULL,
    ]

    num_sold_cows, num_dead_cows = randint(1, 100), randint(1, 100)

    sold_cows = [
        mock_animal(
            AnimalType.LAC_COW,
            id=i,
            days_born=randint(1, 3000),
            sold_at_day=randint(1, 3000),
            dead_at_day=None,
            body_weight=uniform(0.0, 750),
            cull_reason=cull_reasons[randint(0, len(cull_reasons) - 1)],
            days_in_milk=randint(1, 500),
            calves=randint(1, 8),
        )
        for i in range(num_sold_cows)
    ]
    died_cows = [
        mock_animal(
            AnimalType.LAC_COW,
            id=i,
            days_born=randint(1, 3000),
            sold_at_day=None,
            dead_at_day=randint(1, 3000),
            body_weight=uniform(0.0, 750),
            cull_reason=animal_constants.DEATH_CULL,
            days_in_milk=randint(1, 500),
            calves=randint(1, 8),
        )
        for i in range(num_sold_cows, num_sold_cows + num_dead_cows)
    ]
    sold_and_died_cows = sold_cows + died_cows
    num_total_sold_and_died_cows = len(sold_and_died_cows)

    total_sold_and_died_cows_age = sum([cow.days_born for cow in sold_and_died_cows])
    current_avg_cow_culling_age, current_cow_herd_exit_num = uniform(0.0, 3000), randint(0, 1000)
    herd_manager.herd_statistics.avg_cow_culling_age = current_avg_cow_culling_age
    herd_manager.herd_statistics.cow_herd_exit_num = current_cow_herd_exit_num
    expected_cow_herd_exit_num = current_cow_herd_exit_num + num_total_sold_and_died_cows
    expected_average_cow_culling_age = (
        (current_avg_cow_culling_age * current_cow_herd_exit_num + total_sold_and_died_cows_age)
        / expected_cow_herd_exit_num
        if expected_cow_herd_exit_num > 0
        else 0.0
    )

    current_sold_and_died_cows_info = [mock_sold_animal_typed_dict for _ in range(current_cow_herd_exit_num)]
    herd_manager.herd_statistics.sold_and_died_cows_info = current_sold_and_died_cows_info
    expected_sold_and_died_cows_info = current_sold_and_died_cows_info + [
        SoldAnimalTypedDict(
            id=cow.id,
            animal_type=cow.animal_type.value,
            sold_at_day=cow.sold_at_day if cow.sold_at_day is not None else cow.dead_at_day,
            body_weight=cow.body_weight,
            cull_reason=cow.cull_reason,
            days_in_milk=cow.days_in_milk,
            parity=cow.reproduction.calves,
        )
        for cow in sold_and_died_cows
    ]

    current_cull_reason_stats = {
        animal_constants.DEATH_CULL: randint(0, num_total_sold_and_died_cows),
        animal_constants.LOW_PROD_CULL: randint(0, num_total_sold_and_died_cows),
        animal_constants.LAMENESS_CULL: randint(0, num_total_sold_and_died_cows),
        animal_constants.INJURY_CULL: randint(0, num_total_sold_and_died_cows),
        animal_constants.MASTITIS_CULL: randint(0, num_total_sold_and_died_cows),
        animal_constants.DISEASE_CULL: randint(0, num_total_sold_and_died_cows),
        animal_constants.UDDER_CULL: randint(0, num_total_sold_and_died_cows),
        animal_constants.UNKNOWN_CULL: randint(0, num_total_sold_and_died_cows),
    }
    herd_manager.herd_statistics.cull_reason_stats = current_cull_reason_stats
    expected_cull_reason_stats = {
        animal_constants.DEATH_CULL: current_cull_reason_stats[animal_constants.DEATH_CULL]
        + len([cow for cow in sold_and_died_cows if cow.cull_reason == animal_constants.DEATH_CULL]),
        animal_constants.LOW_PROD_CULL: current_cull_reason_stats[animal_constants.LOW_PROD_CULL]
        + len([cow for cow in sold_and_died_cows if cow.cull_reason == animal_constants.LOW_PROD_CULL]),
        animal_constants.LAMENESS_CULL: current_cull_reason_stats[animal_constants.LAMENESS_CULL]
        + len([cow for cow in sold_and_died_cows if cow.cull_reason == animal_constants.LAMENESS_CULL]),
        animal_constants.INJURY_CULL: current_cull_reason_stats[animal_constants.INJURY_CULL]
        + len([cow for cow in sold_and_died_cows if cow.cull_reason == animal_constants.INJURY_CULL]),
        animal_constants.MASTITIS_CULL: current_cull_reason_stats[animal_constants.MASTITIS_CULL]
        + len([cow for cow in sold_and_died_cows if cow.cull_reason == animal_constants.MASTITIS_CULL]),
        animal_constants.DISEASE_CULL: current_cull_reason_stats[animal_constants.DISEASE_CULL]
        + len([cow for cow in sold_and_died_cows if cow.cull_reason == animal_constants.DISEASE_CULL]),
        animal_constants.UDDER_CULL: current_cull_reason_stats[animal_constants.UDDER_CULL]
        + len([cow for cow in sold_and_died_cows if cow.cull_reason == animal_constants.UDDER_CULL]),
        animal_constants.UNKNOWN_CULL: current_cull_reason_stats[animal_constants.UNKNOWN_CULL]
        + len([cow for cow in sold_and_died_cows if cow.cull_reason == animal_constants.UNKNOWN_CULL]),
    }

    current_sold_cow_num = randint(0, current_cow_herd_exit_num)
    herd_manager.herd_statistics.sold_cow_num = current_sold_cow_num
    expected_sold_cow_num = current_sold_cow_num + num_sold_cows

    current_sold_cows_info = [mock_sold_animal_typed_dict for _ in range(current_sold_cow_num)]
    herd_manager.herd_statistics.sold_cows_info = current_sold_cows_info
    expected_sold_cows_info = current_sold_cows_info + [
        SoldAnimalTypedDict(
            id=cow.id,
            animal_type=cow.animal_type.value,
            sold_at_day=cow.sold_at_day,
            body_weight=cow.body_weight,
            cull_reason=cow.cull_reason,
            days_in_milk=cow.days_in_milk,
            parity=cow.reproduction.calves,
        )
        for cow in sold_cows
    ]

    current_parity_culling_stats_range = {
        "1": randint(0, num_total_sold_and_died_cows),
        "2": randint(0, num_total_sold_and_died_cows),
        "3": randint(0, num_total_sold_and_died_cows),
        "4": randint(0, num_total_sold_and_died_cows),
        "5": randint(0, num_total_sold_and_died_cows),
        "greater_than_5": randint(0, num_total_sold_and_died_cows),
    }
    herd_manager.herd_statistics.parity_culling_stats_range = current_parity_culling_stats_range
    expected_parity_culling_stats_range = current_parity_culling_stats_range.copy()
    for cow in sold_and_died_cows:
        if cow.calves > 5:
            expected_parity_culling_stats_range["greater_than_5"] += 1
        else:
            expected_parity_culling_stats_range[str(cow.calves)] += 1

    mock_calculate_cull_reason_percentages = mocker.patch.object(herd_manager, "_calculate_cull_reason_percentages")

    herd_manager._update_sold_and_died_cow_statistics(sold_and_died_cows)

    mock_calculate_cull_reason_percentages.assert_called_once_with()
    assert herd_manager.herd_statistics.avg_cow_culling_age == expected_average_cow_culling_age
    assert herd_manager.herd_statistics.cow_herd_exit_num == expected_cow_herd_exit_num
    assert herd_manager.herd_statistics.sold_and_died_cows_info == expected_sold_and_died_cows_info
    assert herd_manager.herd_statistics.cull_reason_stats == expected_cull_reason_stats
    assert herd_manager.herd_statistics.sold_cows_info == expected_sold_cows_info
    assert herd_manager.herd_statistics.sold_cow_num == expected_sold_cow_num
    assert herd_manager.herd_statistics.parity_culling_stats_range == expected_parity_culling_stats_range


def test_update_sold_heiferII_statistics(
    mock_sold_animal_typed_dict: SoldAnimalTypedDict, herd_manager: HerdManager
) -> None:
    """Unit test for _update_sold_heiferII_statistics()"""
    num_sold_heiferIIs = randint(0, 100)
    sold_heiferIIs = [
        mock_animal(
            animal_type=AnimalType.HEIFER_II,
            id=i,
            sold_at_day=randint(0, 600),
            body_weight=uniform(0.0, 500),
            days_born=randint(0, 600),
        )
        for i in range(num_sold_heiferIIs)
    ]

    current_average_heifer_culling_age = uniform(0, 500)
    current_sold_heiferII_num = randint(0, 500)
    current_sold_heiferII_info = [mock_sold_animal_typed_dict for _ in range(current_sold_heiferII_num)]

    herd_manager.herd_statistics.avg_heifer_culling_age = current_average_heifer_culling_age
    herd_manager.herd_statistics.sold_heiferII_num = current_sold_heiferII_num
    herd_manager.herd_statistics.sold_heiferIIs_info = current_sold_heiferII_info

    expected_sold_heiferII_num = current_sold_heiferII_num + num_sold_heiferIIs
    sum_heifer_culling_age = current_average_heifer_culling_age * current_sold_heiferII_num + sum(
        [heiferII.days_born for heiferII in sold_heiferIIs]
    )
    expected_average_heifer_culling_age = (
        sum_heifer_culling_age / expected_sold_heiferII_num if expected_sold_heiferII_num > 0 else 0
    )
    expected_sold_heiferII_info = current_sold_heiferII_info + [
        SoldAnimalTypedDict(
            id=heiferII.id,
            animal_type=heiferII.animal_type.value,
            sold_at_day=heiferII.sold_at_day,
            body_weight=heiferII.body_weight,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        )
        for heiferII in sold_heiferIIs
    ]

    herd_manager._update_sold_heiferII_statistics(sold_heiferIIs)

    assert herd_manager.herd_statistics.sold_heiferII_num == expected_sold_heiferII_num
    assert herd_manager.herd_statistics.sold_heiferIIs_info == expected_sold_heiferII_info
    assert herd_manager.herd_statistics.avg_heifer_culling_age == expected_average_heifer_culling_age


def test_update_sold_newborn_calf_statistics(
    mock_sold_animal_typed_dict: SoldAnimalTypedDict, herd_manager: HerdManager
) -> None:
    """Unit test for _update_sold_newborn_calf_statistics()"""
    num_sold_calves = randint(0, 100)
    sold_calves = [
        mock_animal(
            animal_type=AnimalType.CALF,
            id=i,
            sold_at_day=randint(0, 200),
            body_weight=uniform(0.0, 350),
            days_born=randint(0, 200),
        )
        for i in range(num_sold_calves)
    ]

    current_sold_calf_num = randint(0, 500)
    current_sold_calves_info = [mock_sold_animal_typed_dict for _ in range(current_sold_calf_num)]

    herd_manager.herd_statistics.sold_calf_num = current_sold_calf_num
    herd_manager.herd_statistics.sold_calves_info = current_sold_calves_info

    expected_sold_calf_num = current_sold_calf_num + num_sold_calves
    expected_sold_calves_info = current_sold_calves_info + [
        SoldAnimalTypedDict(
            id=calf.id,
            animal_type=calf.animal_type.value,
            sold_at_day=calf.sold_at_day,
            body_weight=calf.body_weight,
            cull_reason="NA",
            days_in_milk="NA",
            parity="NA",
        )
        for calf in sold_calves
    ]

    herd_manager._update_sold_newborn_calf_statistics(sold_calves)

    assert herd_manager.herd_statistics.sold_calf_num == expected_sold_calf_num
    assert herd_manager.herd_statistics.sold_calves_info == expected_sold_calves_info


def test_update_stillborn_calf_statistics(
    mock_stillborn_animal_typed_dict: StillbornCalfTypedDict, herd_manager: HerdManager
) -> None:
    """Unit test for _update_stillborn_newborn_calf_statistics()"""
    num_stillborn_calves = randint(0, 100)
    stillborn_calves = [
        mock_animal(animal_type=AnimalType.CALF, id=i, stillborn_day=randint(0, 200), body_weight=uniform(0.0, 350))
        for i in range(num_stillborn_calves)
    ]

    current_stillborn_calf_num = randint(0, 500)
    current_stillborn_calves_info = [mock_stillborn_animal_typed_dict for _ in range(current_stillborn_calf_num)]

    herd_manager.herd_statistics.stillborn_calf_num = current_stillborn_calf_num
    herd_manager.herd_statistics.stillborn_calf_info = current_stillborn_calves_info

    expected_stillborn_calf_num = current_stillborn_calf_num + num_stillborn_calves
    expected_stillborn_calves_info = current_stillborn_calves_info + [
        StillbornCalfTypedDict(id=calf.id, birth_weight=calf.birth_weight, stillborn_day=calf.stillborn_day)
        for calf in stillborn_calves
    ]

    herd_manager._update_stillborn_calf_statistics(stillborn_calves)

    assert herd_manager.herd_statistics.stillborn_calf_num == expected_stillborn_calf_num
    assert herd_manager.herd_statistics.stillborn_calf_info == expected_stillborn_calves_info


def test_update_cow_reproduction_statistics(herd_manager: HerdManager) -> None:
    """Unit test for _update_cow_reproduction_statistics()"""
    cows = [
        mock_animal(
            animal_type=AnimalType.LAC_COW,
            GnRH_injections=randint(0, 10),
            PGF_injections=randint(0, 10),
            CIDR_count=randint(0, 10),
            pregnancy_diagnoses=randint(0, 10),
            semen_number=randint(0, 10),
            AI_times=randint(0, 10),
            calving_interval=randint(100, 500),
        )
        for _ in range(randint(0, 100))
    ]
    num_cows = len(cows)

    expected_GnRH_injections = sum([animal.reproduction.reproduction_statistics.GnRH_injections for animal in cows])
    expected_PGF_injections = sum([animal.reproduction.reproduction_statistics.PGF_injections for animal in cows])
    expected_CIDR_count = sum([animal.reproduction.reproduction_statistics.CIDR_injections for animal in cows])
    expected_preg_check = sum([animal.reproduction.reproduction_statistics.pregnancy_diagnoses for animal in cows])
    expected_semen_num = sum([animal.reproduction.reproduction_statistics.semen_number for animal in cows])
    expected_ai_num = sum([animal.reproduction.reproduction_statistics.AI_times for animal in cows])
    expected_average_calving_interval = (
        sum([animal.reproduction.calving_interval for animal in cows]) / num_cows if num_cows > 0 else 0.0
    )

    herd_manager.cows = cows
    herd_manager._update_cow_reproduction_statistics()

    assert herd_manager.herd_statistics.GnRH_injection_num == expected_GnRH_injections
    assert herd_manager.herd_statistics.PGF_injection_num == expected_PGF_injections
    assert herd_manager.herd_statistics.CIDR_count == expected_CIDR_count
    assert herd_manager.herd_statistics.preg_check_num == expected_preg_check
    assert herd_manager.herd_statistics.semen_num == expected_semen_num
    assert herd_manager.herd_statistics.ai_num == expected_ai_num
    assert herd_manager.herd_statistics.avg_calving_interval == expected_average_calving_interval


def test_update_heifer_reproduction_statistics(herd_manager: HerdManager) -> None:
    """Unit test for _update_heifer_reproduction_statistics()"""
    heiferIIs = [
        mock_animal(
            animal_type=AnimalType.HEIFER_II,
            GnRH_injections=randint(0, 10),
            PGF_injections=randint(0, 10),
            CIDR_count=randint(0, 10),
            pregnancy_diagnoses=randint(0, 10),
            semen_number=randint(0, 10),
            AI_times=randint(0, 10),
            ED_days=randint(0, 200),
            breeding_to_preg_time=randint(0, 300),
            days_in_pregnancy=randint(0, 100),
        )
        for _ in range(randint(0, 100))
    ]

    expected_GnRH_injections = sum(
        [animal.reproduction.reproduction_statistics.GnRH_injections for animal in heiferIIs]
    )
    expected_PGF_injections = sum([animal.reproduction.reproduction_statistics.PGF_injections for animal in heiferIIs])
    expected_CIDR_count = sum([animal.reproduction.reproduction_statistics.CIDR_injections for animal in heiferIIs])
    expected_preg_check = sum([animal.reproduction.reproduction_statistics.pregnancy_diagnoses for animal in heiferIIs])
    expected_semen_num = sum([animal.reproduction.reproduction_statistics.semen_number for animal in heiferIIs])
    expected_ai_num = sum([animal.reproduction.reproduction_statistics.AI_times for animal in heiferIIs])
    expected_ed_period = len(
        [
            animal.reproduction.reproduction_statistics.ED_days
            for animal in heiferIIs
            if animal.reproduction.reproduction_statistics.ED_days > 0
        ]
    )
    pregnant_heiferIIs = [animal for animal in heiferIIs if animal.is_pregnant]
    expected_average_breeding_to_preg_time = (
        sum([animal.reproduction.breeding_to_preg_time for animal in pregnant_heiferIIs]) / len(pregnant_heiferIIs)
        if len(pregnant_heiferIIs) > 0
        else 0.0
    )

    herd_manager.heiferIIs = heiferIIs
    herd_manager._update_heifer_reproduction_statistics()

    assert herd_manager.herd_statistics.GnRH_injection_num_h == expected_GnRH_injections
    assert herd_manager.herd_statistics.PGF_injection_num_h == expected_PGF_injections
    assert herd_manager.herd_statistics.CIDR_count == expected_CIDR_count
    assert herd_manager.herd_statistics.preg_check_num_h == expected_preg_check
    assert herd_manager.herd_statistics.semen_num_h == expected_semen_num
    assert herd_manager.herd_statistics.ai_num_h == expected_ai_num
    assert herd_manager.herd_statistics.ed_period_h == expected_ed_period
    assert herd_manager.herd_statistics.avg_breeding_to_preg_time == expected_average_breeding_to_preg_time


def test_update_average_mature_body_weight(herd_manager: HerdManager) -> None:
    """Unit test for _update_average_mature_body_weight()"""
    num_calves, num_heiferIs, num_heiferIIs, num_heiferIIIs, num_cows = (
        randint(0, 100),
        randint(0, 100),
        randint(0, 100),
        randint(0, 100),
        randint(0, 100),
    )
    total_animal_num = num_calves + num_heiferIs + num_heiferIIs + num_heiferIIIs + num_cows

    calves = [mock_animal(animal_type=AnimalType.CALF, mature_body_weight=uniform(0, 1000)) for _ in range(num_calves)]
    heiferIs = [
        mock_animal(animal_type=AnimalType.HEIFER_I, mature_body_weight=uniform(0, 1000)) for _ in range(num_heiferIs)
    ]
    heiferIIs = [
        mock_animal(animal_type=AnimalType.HEIFER_II, mature_body_weight=uniform(0, 1000)) for _ in range(num_heiferIIs)
    ]
    heiferIIIs = [
        mock_animal(animal_type=AnimalType.HEIFER_III, mature_body_weight=uniform(0, 1000))
        for _ in range(num_heiferIIIs)
    ]
    cows = [mock_animal(animal_type=AnimalType.LAC_COW, mature_body_weight=uniform(0, 1000)) for _ in range(num_cows)]
    all_animals = calves + heiferIs + heiferIIs + heiferIIIs + cows

    expected_average_mature_body_weight = (
        sum([animal.mature_body_weight for animal in all_animals]) / total_animal_num if total_animal_num > 0 else 0.0
    )

    herd_manager.calves, herd_manager.heiferIs, herd_manager.heiferIIs, herd_manager.heiferIIIs, herd_manager.cows = (
        calves,
        heiferIs,
        heiferIIs,
        heiferIIIs,
        cows,
    )

    herd_manager.herd_statistics.reset_daily_stats()
    herd_manager._update_average_mature_body_weight()

    assert herd_manager.herd_statistics.avg_mature_body_weight == pytest.approx(expected_average_mature_body_weight)


def test_update_average_cow_body_weight(herd_manager: HerdManager) -> None:
    """Unit test for _update_average_cow_body_weight()"""
    herd_manager.cows = [
        mock_animal(animal_type=AnimalType.LAC_COW, body_weight=uniform(0, 1000)) for _ in range(randint(0, 1000))
    ]
    expected_average_body_weight = (
        sum([cow.body_weight for cow in herd_manager.cows]) / len(herd_manager.cows)
        if len(herd_manager.cows) > 0
        else 0.0
    )

    herd_manager.herd_statistics.reset_daily_stats()
    herd_manager._update_average_cow_body_weight()
    assert herd_manager.herd_statistics.avg_cow_body_weight == pytest.approx(expected_average_body_weight)


def test_update_average_cow_parity(herd_manager: HerdManager) -> None:
    """Unit test for _update_average_cow_parity()"""
    parity_1_cow_num, parity_2_cow_num, parity_3_cow_num, parity_4_cow_num, parity_5_cow_num, parity_6_cow_num = (
        randint(0, 100),
        randint(0, 100),
        randint(0, 100),
        randint(0, 100),
        randint(0, 100),
        randint(0, 100),
    )
    total_cow_num = (
        parity_1_cow_num + parity_2_cow_num + parity_3_cow_num + parity_4_cow_num + parity_5_cow_num + parity_6_cow_num
    )

    herd_manager.cows = (
        mock_cows_with_specific_parity(parity_1_cow_num, parity=1)[0]
        + mock_cows_with_specific_parity(parity_2_cow_num, parity=2)[0]
        + mock_cows_with_specific_parity(parity_3_cow_num, parity=3)[0]
        + mock_cows_with_specific_parity(parity_4_cow_num, parity=4)[0]
        + mock_cows_with_specific_parity(parity_5_cow_num, parity=5)[0]
        + mock_cows_with_specific_parity(parity_6_cow_num, parity=6)[0]
    )

    expected_average_cow_parity = (
        (sum([cow.calves for cow in herd_manager.cows]) / total_cow_num) if total_cow_num > 0 else 0.0
    )

    herd_manager.herd_statistics.cow_num = total_cow_num
    herd_manager.herd_statistics.reset_daily_stats()
    herd_manager._update_average_cow_parity()

    assert herd_manager.herd_statistics.avg_parity_num == pytest.approx(expected_average_cow_parity)


def test_update_total_enteric_methane_merges_and_accumulates(herd_manager: HerdManager) -> None:
    """_update_total_enteric_methane should merge and accumulate emissions by animal type and gas key."""
    herd_manager.herd_statistics.total_enteric_methane = {AnimalType.LAC_COW: {"CH4": 10.0, "CO2": 5.0}}

    digestive_outputs = [
        {
            AnimalType.LAC_COW: {
                "CH4": 2.5,
                "N2O": 1.0,
            }
        },
        {
            AnimalType.HEIFER_I: {
                "CH4": 3.0,
            }
        },
        {
            AnimalType.LAC_COW: {
                "CO2": 4.0,
            }
        },
    ]

    herd_manager._update_total_enteric_methane(digestive_outputs)

    totals = herd_manager.herd_statistics.total_enteric_methane[AnimalType.LAC_COW]

    assert totals["CH4"] == pytest.approx(12.5)
    assert totals["CO2"] == pytest.approx(9.0)
    assert totals["N2O"] == pytest.approx(1.0)

    assert AnimalType.HEIFER_I not in herd_manager.herd_statistics.total_enteric_methane
