from collections.abc import Generator
from types import SimpleNamespace
from typing import cast

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.calf_retention_policy import (
    CalfRetentionPolicy,
    RETENTION_METHOD_COUNT,
    RETENTION_METHOD_RATE,
    UNFULFILLED_TAG_ERROR_FRACTION,
)
from RUFAS.biophysical.animal.data_types.animal_enums import Sex
from RUFAS.rufas_time import RufasTime

RANDOM_PATH = "RUFAS.biophysical.animal.calf_retention_policy.random"


def _calf(sex: Sex = Sex.FEMALE, stillborn: bool = False) -> Animal:
    """A minimal stand-in for an Animal carrying only the attributes the policy touches."""
    return cast(Animal, SimpleNamespace(sex=sex, stillborn=stillborn, sold_at_day=None))


def _time(
    sim_year: int = 1,
    julian_day: int = 1,
    year_start_day: int = 1,
    year_end_day: int = 365,
    calendar_year: int = 2023,
    simulation_day: int = 0,
) -> RufasTime:
    """A minimal stand-in for RufasTime exposing only the properties the policy reads."""
    return cast(
        RufasTime,
        SimpleNamespace(
            current_simulation_year=sim_year,
            current_julian_day=julian_day,
            year_start_day=year_start_day,
            year_end_day=year_end_day,
            current_calendar_year=calendar_year,
            simulation_day=simulation_day,
        ),
    )


@pytest.fixture(autouse=True)
def restore_retention_config() -> Generator[None, None, None]:
    """Snapshot and restore the AnimalConfig fields the policy reads (global class state)."""
    saved = (
        AnimalConfig.calf_retention_method,
        AnimalConfig.annual_keep_female_calf_num,
        AnimalConfig.keep_female_calf_rate,
    )
    yield
    (
        AnimalConfig.calf_retention_method,
        AnimalConfig.annual_keep_female_calf_num,
        AnimalConfig.keep_female_calf_rate,
    ) = saved


def test_rate_method_keeps_female_when_draw_at_or_below_rate(mocker: MockerFixture) -> None:
    """Rate method keeps a live female calf when the random draw is at or below the retention rate."""
    AnimalConfig.calf_retention_method = RETENTION_METHOD_RATE
    AnimalConfig.keep_female_calf_rate = 0.5
    mocker.patch(RANDOM_PATH, return_value=0.3)
    policy = CalfRetentionPolicy()

    calf = _calf(sex=Sex.FEMALE)
    policy.apply_retention_decision(calf, simulation_day=10)

    assert calf.sold_at_day is None


def test_rate_method_sells_female_when_draw_above_rate(mocker: MockerFixture) -> None:
    """Rate method sells a female calf when the random draw exceeds the retention rate."""
    AnimalConfig.calf_retention_method = RETENTION_METHOD_RATE
    AnimalConfig.keep_female_calf_rate = 0.5
    mocker.patch(RANDOM_PATH, return_value=0.7)
    policy = CalfRetentionPolicy()

    calf = _calf(sex=Sex.FEMALE)
    policy.apply_retention_decision(calf, simulation_day=10)

    assert calf.sold_at_day == 10


def test_rate_method_always_sells_males_without_drawing(mocker: MockerFixture) -> None:
    """Rate method sells every male calf without consuming a random draw."""
    AnimalConfig.calf_retention_method = RETENTION_METHOD_RATE
    AnimalConfig.keep_female_calf_rate = 1.0
    mock_random = mocker.patch(RANDOM_PATH)
    policy = CalfRetentionPolicy()

    calf = _calf(sex=Sex.MALE)
    policy.apply_retention_decision(calf, simulation_day=7)

    assert calf.sold_at_day == 7
    mock_random.assert_not_called()


def test_apply_rate_based_retention_classmethod(mocker: MockerFixture) -> None:
    """apply_rate_based_retention keeps or sells by rate regardless of the configured method."""
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    AnimalConfig.keep_female_calf_rate = 1.0
    mocker.patch(RANDOM_PATH, return_value=0.99)

    kept = _calf(sex=Sex.FEMALE)
    CalfRetentionPolicy.apply_rate_based_retention(kept, simulation_day=3)
    assert kept.sold_at_day is None

    AnimalConfig.keep_female_calf_rate = 0.0
    sold = _calf(sex=Sex.FEMALE)
    CalfRetentionPolicy.apply_rate_based_retention(sold, simulation_day=3)
    assert sold.sold_at_day == 3


def test_count_method_fulfills_tags_then_sells(mocker: MockerFixture) -> None:
    """Count method keeps female calves while tags remain, then sells once tags are exhausted."""
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    mock_random = mocker.patch(RANDOM_PATH)
    policy = CalfRetentionPolicy()
    policy._outstanding_tags = 2

    first = _calf(sex=Sex.FEMALE)
    second = _calf(sex=Sex.FEMALE)
    third = _calf(sex=Sex.FEMALE)
    policy.apply_retention_decision(first, simulation_day=5)
    policy.apply_retention_decision(second, simulation_day=5)
    policy.apply_retention_decision(third, simulation_day=5)

    assert first.sold_at_day is None
    assert second.sold_at_day is None
    assert third.sold_at_day == 5
    assert policy._outstanding_tags == 0
    assert policy._tags_fulfilled_this_year == 2
    mock_random.assert_not_called()


def test_count_method_males_and_stillborn_never_consume_tags() -> None:
    """Count method sells males and stillborn calves without consuming a keep tag."""
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    policy = CalfRetentionPolicy()
    policy._outstanding_tags = 1

    male = _calf(sex=Sex.MALE)
    stillborn_female = _calf(sex=Sex.FEMALE, stillborn=True)
    policy.apply_retention_decision(male, simulation_day=9)
    policy.apply_retention_decision(stillborn_female, simulation_day=9)

    assert male.sold_at_day == 9
    assert stillborn_female.sold_at_day == 9
    assert policy._outstanding_tags == 1


def test_schedule_sums_to_target_over_full_year() -> None:
    """The yearly tag schedule sums exactly to the target over a full non-leap year."""
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    AnimalConfig.annual_keep_female_calf_num = 500
    policy = CalfRetentionPolicy()

    schedule = policy._build_year_schedule(_time(year_start_day=1, year_end_day=365, calendar_year=2023))

    assert sum(schedule.values()) == 500
    assert len(schedule) > 1
    assert max(schedule.values()) <= 2


def test_schedule_sums_to_target_over_leap_year() -> None:
    """The yearly tag schedule sums exactly to the target over a full leap year."""
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    AnimalConfig.annual_keep_female_calf_num = 366
    policy = CalfRetentionPolicy()

    schedule = policy._build_year_schedule(_time(year_start_day=1, year_end_day=366, calendar_year=2024))

    assert sum(schedule.values()) == 366
    assert all(count == 1 for count in schedule.values())


def test_schedule_prorates_partial_year() -> None:
    """The tag target is prorated across the simulated days of a partial year."""
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    AnimalConfig.annual_keep_female_calf_num = 400
    policy = CalfRetentionPolicy()

    schedule = policy._build_year_schedule(_time(year_start_day=183, year_end_day=365, calendar_year=2023))

    days_available = 365 - 183 + 1
    assert sum(schedule.values()) == round(400 * days_available / 365)
    assert sum(schedule.values()) < 400
    assert min(schedule) >= 183


def test_schedule_empty_when_target_zero() -> None:
    """A target of zero produces an empty tag schedule."""
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    AnimalConfig.annual_keep_female_calf_num = 0
    policy = CalfRetentionPolicy()

    assert policy._build_year_schedule(_time()) == {}


def test_begin_day_releases_scheduled_tags() -> None:
    """begin_day adds each day's scheduled tags to the outstanding pool."""
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    AnimalConfig.annual_keep_female_calf_num = 365
    policy = CalfRetentionPolicy()

    policy.begin_day(_time(sim_year=1, julian_day=1, year_end_day=365, calendar_year=2023))
    assert policy._outstanding_tags == 1

    policy.begin_day(_time(sim_year=1, julian_day=2, year_end_day=365, calendar_year=2023))
    assert policy._outstanding_tags == 2


def test_year_rollover_rebuilds_schedule_and_resets_ledger() -> None:
    """A new simulation year rebuilds the schedule and resets the tag ledger."""
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    AnimalConfig.annual_keep_female_calf_num = 365
    policy = CalfRetentionPolicy()

    policy.begin_day(_time(sim_year=1, julian_day=5, year_end_day=365, calendar_year=2023))
    assert policy._scheduled_year == 1
    policy._outstanding_tags += 50
    policy._tags_fulfilled_this_year = 7

    policy.begin_day(_time(sim_year=2, julian_day=1, year_end_day=365, calendar_year=2025))
    assert policy._scheduled_year == 2
    assert policy._outstanding_tags == 1
    assert policy._tags_fulfilled_this_year == 0


def test_finalize_day_warns_on_any_leftover_below_error_threshold(mocker: MockerFixture) -> None:
    """A shortfall below the error threshold logs a warning but does not stop the simulation."""
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    policy = CalfRetentionPolicy()
    mock_om = mocker.patch.object(policy, "om")
    policy._scheduled_year = 1
    policy._target_tags_this_year = 100
    policy._outstanding_tags = round(100 * UNFULFILLED_TAG_ERROR_FRACTION) - 1

    policy.finalize_day(_time(sim_year=1, julian_day=365, year_end_day=365))

    assert mock_om.add_warning.called
    assert not mock_om.add_error.called


def test_finalize_day_warns_on_a_single_leftover_tag(mocker: MockerFixture) -> None:
    """Even a single unfulfilled tag triggers the year-end warning."""
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    policy = CalfRetentionPolicy()
    mock_om = mocker.patch.object(policy, "om")
    policy._scheduled_year = 1
    policy._target_tags_this_year = 100
    policy._outstanding_tags = 1

    policy.finalize_day(_time(sim_year=1, julian_day=365, year_end_day=365))

    assert mock_om.add_warning.called
    assert not mock_om.add_error.called


def test_finalize_day_no_message_when_target_fully_met(mocker: MockerFixture) -> None:
    """No warning or error is emitted when every keep tag is fulfilled."""
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    policy = CalfRetentionPolicy()
    mock_om = mocker.patch.object(policy, "om")
    policy._scheduled_year = 1
    policy._target_tags_this_year = 100
    policy._outstanding_tags = 0

    policy.finalize_day(_time(sim_year=1, julian_day=365, year_end_day=365))

    assert not mock_om.add_warning.called
    assert not mock_om.add_error.called


@pytest.mark.parametrize("fraction", [UNFULFILLED_TAG_ERROR_FRACTION, 0.5, 1.0])
def test_finalize_day_errors_and_stops_when_shortfall_reaches_threshold(mocker: MockerFixture, fraction: float) -> None:
    """A shortfall at or above the error threshold logs an error and stops the simulation."""
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    policy = CalfRetentionPolicy()
    mock_om = mocker.patch.object(policy, "om")
    policy._scheduled_year = 1
    policy._target_tags_this_year = 100
    policy._outstanding_tags = round(100 * fraction)

    with pytest.raises(RuntimeError):
        policy.finalize_day(_time(sim_year=1, julian_day=365, year_end_day=365))

    assert mock_om.add_error.called
    assert not mock_om.add_warning.called


def test_finalize_day_no_action_before_year_end(mocker: MockerFixture) -> None:
    """The year-end check does nothing on days that are not the last day of the year."""
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    policy = CalfRetentionPolicy()
    mock_om = mocker.patch.object(policy, "om")
    policy._target_tags_this_year = 100
    policy._outstanding_tags = 99

    policy.finalize_day(_time(sim_year=1, julian_day=200, year_end_day=365))

    assert not mock_om.add_warning.called
    assert not mock_om.add_error.called


def test_hooks_are_noops_under_rate_method(mocker: MockerFixture) -> None:
    """begin_day and finalize_day are no-ops under the rate method."""
    AnimalConfig.calf_retention_method = RETENTION_METHOD_RATE
    AnimalConfig.annual_keep_female_calf_num = 365
    policy = CalfRetentionPolicy()
    mock_om = mocker.patch.object(policy, "om")

    policy.begin_day(_time(sim_year=1, julian_day=1, year_end_day=365))
    policy.finalize_day(_time(sim_year=1, julian_day=365, year_end_day=365))

    assert policy._outstanding_tags == 0
    assert policy._scheduled_year is None
    assert not mock_om.add_warning.called
    assert not mock_om.add_error.called
