import pytest

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.herd_statistics import HerdStatistics


@pytest.fixture
def herd_statistics() -> HerdStatistics:
    """Fixture providing a fresh instance of HerdStatistics."""
    return HerdStatistics()


def test_initialization(herd_statistics: HerdStatistics) -> None:
    """Test that HerdStatistics initializes with correct default values."""
    assert herd_statistics.avg_calving_to_preg_time == {
        "1": 0.0,
        "2": 0.0,
        "3": 0.0,
        "4": 0.0,
        "5": 0.0,
        "greater_than_5": 0.0,
    }
    assert herd_statistics.cull_reason_stats is not None
    assert all(value == 0 for value in herd_statistics.cull_reason_stats.values())
    assert herd_statistics.sold_calves_info == []
    assert herd_statistics.sold_cows_info == []
    assert herd_statistics.herd_num == 0
    assert herd_statistics.calf_num == 0


def test_reset_daily_stats(herd_statistics: HerdStatistics) -> None:
    """Test that reset_daily_stats resets every daily-related attribute to its zero value."""
    # --- population counts ---
    herd_statistics.calf_num = 3
    herd_statistics.heiferI_num = 4
    herd_statistics.heiferII_num = 5
    herd_statistics.heiferIII_num = 6
    herd_statistics.cow_num = 20

    # --- event counts ---
    herd_statistics.stillborn_calf_num = 1
    herd_statistics.sold_calf_num = 2
    herd_statistics.sold_cow_oversupply_num = 3
    herd_statistics.bought_heifer_num = 4
    herd_statistics.sold_heiferII_num = 5
    herd_statistics.cow_herd_exit_num = 6
    herd_statistics.sold_cow_num = 7
    herd_statistics.born_calf_num = 8

    # --- percentages ---
    herd_statistics.calf_percent = 10.0
    herd_statistics.heiferI_percent = 11.0
    herd_statistics.heiferII_percent = 12.0
    herd_statistics.heiferIII_percent = 13.0
    herd_statistics.cow_percent = 14.0

    # --- reproduction procedure counts ---
    herd_statistics.CIDR_count = 2
    herd_statistics.preg_check_num_h = 3
    herd_statistics.preg_check_num = 4
    herd_statistics.GnRH_injection_num_h = 5
    herd_statistics.GnRH_injection_num = 6
    herd_statistics.PGF_injection_num_h = 7
    herd_statistics.PGF_injection_num = 8
    herd_statistics.ai_num_h = 9
    herd_statistics.ai_num = 10
    herd_statistics.semen_num_h = 11
    herd_statistics.semen_num = 12
    herd_statistics.ed_period_h = 13
    herd_statistics.ed_period = 14

    # --- cow status counts ---
    herd_statistics.open_cow_num = 5
    herd_statistics.preg_cow_num = 6
    herd_statistics.vwp_cow_num = 7
    herd_statistics.milking_cow_num = 8
    herd_statistics.dry_cow_num = 9

    # --- deaths by stage ---
    herd_statistics.animals_deaths_by_stage = {
        AnimalType.CALF: 1,
        AnimalType.HEIFER_I: 2,
        AnimalType.HEIFER_II: 3,
        AnimalType.HEIFER_III: 4,
        AnimalType.LAC_COW: 5,
        AnimalType.DRY_COW: 6,
    }

    # --- cow status percentages ---
    herd_statistics.preg_cow_percent = 40.0
    herd_statistics.dry_cow_percent = 20.0
    herd_statistics.milking_cow_percent = 60.0
    herd_statistics.non_preg_cow_percent = 30.0

    # --- averages ---
    herd_statistics.avg_days_in_milk = 120.0
    herd_statistics.avg_days_in_preg = 90.0
    herd_statistics.avg_cow_body_weight = 650.0
    herd_statistics.avg_parity_num = 2.5
    herd_statistics.avg_calving_interval = 400.0
    herd_statistics.avg_breeding_to_preg_time = 55.0
    herd_statistics.avg_heifer_culling_age = 800.0
    herd_statistics.avg_cow_culling_age = 1500.0
    herd_statistics.avg_mature_body_weight = 700.0

    # --- milk ---
    herd_statistics.daily_milk_production = 350.0
    herd_statistics.herd_milk_fat_kg = 14.0
    herd_statistics.herd_milk_fat_percent = 4.0
    herd_statistics.herd_milk_protein_kg = 11.0
    herd_statistics.herd_milk_protein_percent = 3.2

    # --- heifer ADG by pen (new) ---
    herd_statistics.heifer_average_daily_gain_by_pen = {"1": 1.5, "2": 1.2}
    herd_statistics.heifer_average_daily_gain_by_animal_type = {
        AnimalType.HEIFER_I: 0.8,
        AnimalType.HEIFER_II: 0.9,
        AnimalType.HEIFER_III: 1.0,
    }

    herd_statistics.reset_daily_stats()

    # --- population counts ---
    assert herd_statistics.calf_num == 0
    assert herd_statistics.heiferI_num == 0
    assert herd_statistics.heiferII_num == 0
    assert herd_statistics.heiferIII_num == 0
    assert herd_statistics.cow_num == 0

    # --- event counts ---
    assert herd_statistics.stillborn_calf_num == 0
    assert herd_statistics.sold_calf_num == 0
    assert herd_statistics.sold_cow_oversupply_num == 0
    assert herd_statistics.bought_heifer_num == 0
    assert herd_statistics.sold_heiferII_num == 0
    assert herd_statistics.cow_herd_exit_num == 0
    assert herd_statistics.sold_cow_num == 0
    assert herd_statistics.born_calf_num == 0

    # --- percentages ---
    assert herd_statistics.calf_percent == 0.0
    assert herd_statistics.heiferI_percent == 0.0
    assert herd_statistics.heiferII_percent == 0.0
    assert herd_statistics.heiferIII_percent == 0.0
    assert herd_statistics.cow_percent == 0.0

    # --- reproduction procedure counts ---
    assert herd_statistics.CIDR_count == 0
    assert herd_statistics.preg_check_num_h == 0
    assert herd_statistics.preg_check_num == 0
    assert herd_statistics.GnRH_injection_num_h == 0
    assert herd_statistics.GnRH_injection_num == 0
    assert herd_statistics.PGF_injection_num_h == 0
    assert herd_statistics.PGF_injection_num == 0
    assert herd_statistics.ai_num_h == 0
    assert herd_statistics.ai_num == 0
    assert herd_statistics.semen_num_h == 0
    assert herd_statistics.semen_num == 0
    assert herd_statistics.ed_period_h == 0
    assert herd_statistics.ed_period == 0

    # --- cow status counts ---
    assert herd_statistics.open_cow_num == 0
    assert herd_statistics.preg_cow_num == 0
    assert herd_statistics.vwp_cow_num == 0
    assert herd_statistics.milking_cow_num == 0
    assert herd_statistics.dry_cow_num == 0

    # --- deaths by stage: all zeroed, keys preserved ---
    assert all(v == 0 for v in herd_statistics.animals_deaths_by_stage.values())
    assert set(herd_statistics.animals_deaths_by_stage.keys()) == {
        AnimalType.CALF,
        AnimalType.HEIFER_I,
        AnimalType.HEIFER_II,
        AnimalType.HEIFER_III,
        AnimalType.LAC_COW,
        AnimalType.DRY_COW,
    }

    # --- cow status percentages ---
    assert herd_statistics.preg_cow_percent == 0.0
    assert herd_statistics.dry_cow_percent == 0.0
    assert herd_statistics.milking_cow_percent == 0.0
    assert herd_statistics.non_preg_cow_percent == 0.0

    # --- averages ---
    assert herd_statistics.avg_days_in_milk == 0.0
    assert herd_statistics.avg_days_in_preg == 0.0
    assert herd_statistics.avg_cow_body_weight == 0.0
    assert herd_statistics.avg_parity_num == 0.0
    assert herd_statistics.avg_calving_interval == 0.0
    assert herd_statistics.avg_breeding_to_preg_time == 0.0
    assert herd_statistics.avg_heifer_culling_age == 0.0
    assert herd_statistics.avg_cow_culling_age == 0.0
    assert herd_statistics.avg_mature_body_weight == 0.0

    # --- milk ---
    assert herd_statistics.daily_milk_production == 0.0
    assert herd_statistics.herd_milk_fat_kg == 0.0
    assert herd_statistics.herd_milk_fat_percent == 0.0
    assert herd_statistics.herd_milk_protein_kg == 0.0
    assert herd_statistics.herd_milk_protein_percent == 0.0

    # --- heifer ADG by pen: existing keys set to None, keys preserved ---
    assert set(herd_statistics.heifer_average_daily_gain_by_pen.keys()) == {"1", "2"}
    assert herd_statistics.heifer_average_daily_gain_by_pen["1"] is None
    assert herd_statistics.heifer_average_daily_gain_by_pen["2"] is None

    # --- heifer ADG by animal type: all None ---
    assert herd_statistics.heifer_average_daily_gain_by_animal_type[AnimalType.HEIFER_I] is None
    assert herd_statistics.heifer_average_daily_gain_by_animal_type[AnimalType.HEIFER_II] is None
    assert herd_statistics.heifer_average_daily_gain_by_animal_type[AnimalType.HEIFER_III] is None


def test_reset_parity(herd_statistics: HerdStatistics) -> None:
    """Test that reset_parity resets parity-based attributes correctly."""
    # Set non-zero values
    herd_statistics.num_cow_for_parity["1"] = 5
    herd_statistics.avg_calving_to_preg_time["2"] = 45.0
    herd_statistics.percent_cow_for_parity["3"] = 75.0
    herd_statistics.avg_age_for_parity["1"] = 24.0
    herd_statistics.avg_age_for_calving["2"] = 30.0

    herd_statistics.reset_parity()

    assert all(value == 0 for value in herd_statistics.num_cow_for_parity.values())
    assert all(value == 0 for value in herd_statistics.avg_calving_to_preg_time.values())
    assert all(value == 0.0 for value in herd_statistics.percent_cow_for_parity.values())
    assert all(value == 0.0 for value in herd_statistics.avg_age_for_parity.values())
    assert all(value == 0.0 for value in herd_statistics.avg_age_for_calving.values())


def test_reset_cull_reason_stats(herd_statistics: HerdStatistics) -> None:
    """Test that reset_cull_reason_stats resets cull reason-based attributes correctly."""
    # Set non-zero values
    herd_statistics.cull_reason_stats[animal_constants.DEATH_CULL] = 3
    herd_statistics.cull_reason_stats_percent[animal_constants.LAMENESS_CULL] = 40.5

    herd_statistics.reset_cull_reason_stats()

    assert all(value == 0 for value in herd_statistics.cull_reason_stats.values())
    assert all(value == 0.0 for value in herd_statistics.cull_reason_stats_percent.values())
