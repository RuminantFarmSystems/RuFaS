import pytest

from RUFAS.biophysical.animal import animal_constants
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
    assert herd_statistics.avg_daily_cow_milking == 0.0


def test_reset_daily_stats(herd_statistics: HerdStatistics) -> None:
    """Test that reset_daily_stats resets daily-related attributes to zero."""
    # Set non-zero values
    herd_statistics.calf_num = 5
    herd_statistics.milking_cow_num = 10
    herd_statistics.daily_milk_production = 25.0
    herd_statistics.avg_cow_body_weight = 650.0

    herd_statistics.reset_daily_stats()

    assert herd_statistics.calf_num == 0
    assert herd_statistics.milking_cow_num == 0
    assert herd_statistics.daily_milk_production == 0.0
    assert herd_statistics.avg_cow_body_weight == 0.0


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
