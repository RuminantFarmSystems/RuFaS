"""Unit tests for CalfRetentionPolicy (issue #3055).

Covers both retention methods that the policy consolidates:
* ``"rate"`` (Option 1): per-calf probabilistic keep/sell, preserving legacy behavior.
* ``"count"`` (Option 2): annual keep-tag target spread across the year, with a year-end
  warning when too few female calves are born to meet it.
"""

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
    UNFULFILLED_TAG_WARNING_FRACTION,
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
        AnimalConfig.keep_female_calf_num_annual,
        AnimalConfig.keep_female_calf_rate,
    )
    yield
    (
        AnimalConfig.calf_retention_method,
        AnimalConfig.keep_female_calf_num_annual,
        AnimalConfig.keep_female_calf_rate,
    ) = saved


# --------------------------------------------------------------------------- rate method
def test_rate_method_keeps_female_when_draw_at_or_below_rate(mocker: MockerFixture) -> None:
    AnimalConfig.calf_retention_method = RETENTION_METHOD_RATE
    AnimalConfig.keep_female_calf_rate = 0.5
    mocker.patch(RANDOM_PATH, return_value=0.3)
    policy = CalfRetentionPolicy()

    calf = _calf(sex=Sex.FEMALE)
    policy.apply(calf, simulation_day=10)

    assert calf.sold_at_day is None  # kept


def test_rate_method_sells_female_when_draw_above_rate(mocker: MockerFixture) -> None:
    AnimalConfig.calf_retention_method = RETENTION_METHOD_RATE
    AnimalConfig.keep_female_calf_rate = 0.5
    mocker.patch(RANDOM_PATH, return_value=0.7)
    policy = CalfRetentionPolicy()

    calf = _calf(sex=Sex.FEMALE)
    policy.apply(calf, simulation_day=10)

    assert calf.sold_at_day == 10  # sold


def test_rate_method_always_sells_males_without_drawing(mocker: MockerFixture) -> None:
    AnimalConfig.calf_retention_method = RETENTION_METHOD_RATE
    AnimalConfig.keep_female_calf_rate = 1.0
    mock_random = mocker.patch(RANDOM_PATH)
    policy = CalfRetentionPolicy()

    calf = _calf(sex=Sex.MALE)
    policy.apply(calf, simulation_day=7)

    assert calf.sold_at_day == 7
    mock_random.assert_not_called()  # short-circuits before drawing, matching legacy behavior


def test_apply_rate_based_classmethod(mocker: MockerFixture) -> None:
    # Used during herd initialization regardless of the configured method.
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT  # should be ignored by apply_rate_based
    AnimalConfig.keep_female_calf_rate = 1.0
    mocker.patch(RANDOM_PATH, return_value=0.99)

    kept = _calf(sex=Sex.FEMALE)
    CalfRetentionPolicy.apply_rate_based(kept, simulation_day=3)
    assert kept.sold_at_day is None  # rate 1.0 keeps every live female

    AnimalConfig.keep_female_calf_rate = 0.0
    sold = _calf(sex=Sex.FEMALE)
    CalfRetentionPolicy.apply_rate_based(sold, simulation_day=3)
    assert sold.sold_at_day == 3


# -------------------------------------------------------------------------- count method
def test_count_method_fulfills_tags_then_sells(mocker: MockerFixture) -> None:
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    # random must never be consulted in count mode.
    mock_random = mocker.patch(RANDOM_PATH)
    policy = CalfRetentionPolicy()
    policy._outstanding_tags = 2

    first = _calf(sex=Sex.FEMALE)
    second = _calf(sex=Sex.FEMALE)
    third = _calf(sex=Sex.FEMALE)
    policy.apply(first, simulation_day=5)
    policy.apply(second, simulation_day=5)
    policy.apply(third, simulation_day=5)

    assert first.sold_at_day is None  # tag consumed -> kept
    assert second.sold_at_day is None  # tag consumed -> kept
    assert third.sold_at_day == 5  # no tags left -> sold
    assert policy._outstanding_tags == 0
    assert policy._tags_fulfilled_this_year == 2
    mock_random.assert_not_called()


def test_count_method_males_and_stillborn_never_consume_tags() -> None:
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    policy = CalfRetentionPolicy()
    policy._outstanding_tags = 1

    male = _calf(sex=Sex.MALE)
    stillborn_female = _calf(sex=Sex.FEMALE, stillborn=True)
    policy.apply(male, simulation_day=9)
    policy.apply(stillborn_female, simulation_day=9)

    assert male.sold_at_day == 9
    assert stillborn_female.sold_at_day == 9
    assert policy._outstanding_tags == 1  # tag preserved for a live female


# ------------------------------------------------------------------ schedule generation
def test_schedule_sums_to_target_over_full_year() -> None:
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    AnimalConfig.keep_female_calf_num_annual = 500
    policy = CalfRetentionPolicy()

    schedule = policy._build_year_schedule(_time(year_start_day=1, year_end_day=365, calendar_year=2023))

    assert sum(schedule.values()) == 500  # exact, deterministic
    assert len(schedule) > 1  # spread across the year, not dumped on one day
    assert max(schedule.values()) <= 2  # ~500/365 -> at most 2 per day


def test_schedule_sums_to_target_over_leap_year() -> None:
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    AnimalConfig.keep_female_calf_num_annual = 366
    policy = CalfRetentionPolicy()

    schedule = policy._build_year_schedule(_time(year_start_day=1, year_end_day=366, calendar_year=2024))

    assert sum(schedule.values()) == 366
    assert all(count == 1 for count in schedule.values())  # one tag per day in a 366/366 case


def test_schedule_prorates_partial_year() -> None:
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    AnimalConfig.keep_female_calf_num_annual = 400
    policy = CalfRetentionPolicy()

    # Simulation starts mid-year on Julian day 183 of a non-leap year (183 days available).
    schedule = policy._build_year_schedule(_time(year_start_day=183, year_end_day=365, calendar_year=2023))

    days_available = 365 - 183 + 1
    assert sum(schedule.values()) == round(400 * days_available / 365)
    assert sum(schedule.values()) < 400  # fewer than a full year's target
    assert min(schedule) >= 183  # tags only on simulated days


def test_schedule_empty_when_target_zero() -> None:
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    AnimalConfig.keep_female_calf_num_annual = 0
    policy = CalfRetentionPolicy()

    assert policy._build_year_schedule(_time()) == {}


# ----------------------------------------------------------------------- per-day hooks
def test_begin_day_releases_scheduled_tags() -> None:
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    AnimalConfig.keep_female_calf_num_annual = 365  # 1 tag/day over a full non-leap year
    policy = CalfRetentionPolicy()

    policy.begin_day(_time(sim_year=1, julian_day=1, year_end_day=365, calendar_year=2023))
    assert policy._outstanding_tags == 1

    policy.begin_day(_time(sim_year=1, julian_day=2, year_end_day=365, calendar_year=2023))
    assert policy._outstanding_tags == 2


def test_year_rollover_rebuilds_schedule_and_resets_ledger() -> None:
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    AnimalConfig.keep_female_calf_num_annual = 365
    policy = CalfRetentionPolicy()

    policy.begin_day(_time(sim_year=1, julian_day=5, year_end_day=365, calendar_year=2023))
    assert policy._scheduled_year == 1
    policy._outstanding_tags += 50  # pretend some tags accumulated unfulfilled
    policy._tags_fulfilled_this_year = 7

    # Roll into a new simulation year (non-leap, so 365 tags spread one-per-day).
    policy.begin_day(_time(sim_year=2, julian_day=1, year_end_day=365, calendar_year=2025))
    assert policy._scheduled_year == 2
    assert policy._outstanding_tags == 1  # ledger reset to 0, then day-1 release of the new year
    assert policy._tags_fulfilled_this_year == 0  # fulfilled counter reset for the new year


def test_finalize_day_warns_when_target_unmet(mocker: MockerFixture) -> None:
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    policy = CalfRetentionPolicy()
    mock_om = mocker.patch.object(policy, "om")
    policy._scheduled_year = 1
    policy._target_tags_this_year = 100
    policy._outstanding_tags = 20  # 20 > 5% of 100

    policy.finalize_day(_time(sim_year=1, julian_day=365, year_end_day=365))

    assert mock_om.add_warning.called, "expected a year-end warning for unfulfilled tags"


def test_finalize_day_no_warning_when_target_met(mocker: MockerFixture) -> None:
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    policy = CalfRetentionPolicy()
    mock_om = mocker.patch.object(policy, "om")
    policy._scheduled_year = 1
    policy._target_tags_this_year = 100
    policy._outstanding_tags = int(100 * UNFULFILLED_TAG_WARNING_FRACTION)  # exactly at threshold, not above

    policy.finalize_day(_time(sim_year=1, julian_day=365, year_end_day=365))

    assert not mock_om.add_warning.called


def test_finalize_day_no_warning_before_year_end(mocker: MockerFixture) -> None:
    AnimalConfig.calf_retention_method = RETENTION_METHOD_COUNT
    policy = CalfRetentionPolicy()
    mock_om = mocker.patch.object(policy, "om")
    policy._target_tags_this_year = 100
    policy._outstanding_tags = 99

    policy.finalize_day(_time(sim_year=1, julian_day=200, year_end_day=365))

    assert not mock_om.add_warning.called


def test_hooks_are_noops_under_rate_method(mocker: MockerFixture) -> None:
    AnimalConfig.calf_retention_method = RETENTION_METHOD_RATE
    AnimalConfig.keep_female_calf_num_annual = 365
    policy = CalfRetentionPolicy()
    mock_om = mocker.patch.object(policy, "om")

    policy.begin_day(_time(sim_year=1, julian_day=1, year_end_day=365))
    policy.finalize_day(_time(sim_year=1, julian_day=365, year_end_day=365))

    assert policy._outstanding_tags == 0
    assert policy._scheduled_year is None
    assert not mock_om.add_warning.called
