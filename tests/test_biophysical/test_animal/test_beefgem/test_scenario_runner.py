"""Tests for the beef scenario runner.

Verifies:
- BeefHerdScenario construction, defaults and validation
- The seven named scenarios and the parameter each varies
- Config snapshot and restore, including when the runner raises
- run_scenario replicate handling and seeding
- compare_scenarios frame shape, built from the summary keys
- Common random numbers across scenarios
"""

from __future__ import annotations

import dataclasses
from typing import Generator

import pandas as pd
import pytest

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.beef_scenario_runner import (
    BEEF_SCENARIOS,
    BeefHerdScenario,
    ScenarioComparison,
    ScenarioResult,
    _SCENARIO_FIELD_TO_CONFIG,
    _SNAPSHOT_FIELDS,
    _SNAPSHOT_SOURCE_FIELDS,
    _scenario_config,
    compare_scenarios,
    run_scenario,
)
from RUFAS.biophysical.animal.data_types.animal_enums import (
    BeefPostWeaningDestination,
    FinishingSystem,
    StockerDietSystem,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SUMMARY_KEYS: frozenset[str] = frozenset(
    {
        "calf_crop_pct",
        "mean_calving_interval_days",
        "replacement_rate_pct",
        "mean_cow_bcs",
    }
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _restore_all_snapshot_fields() -> Generator[None, None, None]:
    """Guard the suite itself against leaking any field the runner touches."""
    saved = {name: getattr(AnimalConfig, name) for name in _SNAPSHOT_FIELDS}
    yield
    for name, value in saved.items():
        setattr(AnimalConfig, name, value)


# ---------------------------------------------------------------------------
# Helpers — stub runners standing in for the herd drive
# ---------------------------------------------------------------------------


def _constant_runner(scenario: BeefHerdScenario, years: int, seed: int) -> dict[str, float]:
    """Return a fixed summary, ignoring the scenario."""
    return {
        "calf_crop_pct": 90.0,
        "mean_calving_interval_days": 365.0,
        "replacement_rate_pct": 20.0,
        "mean_cow_bcs": 5.0,
    }


def _seed_echoing_runner(scenario: BeefHerdScenario, years: int, seed: int) -> dict[str, float]:
    """Encode the seed in the output so seeding behaviour is observable."""
    return {
        "calf_crop_pct": float(seed),
        "mean_calving_interval_days": float(seed * 2),
        "replacement_rate_pct": float(years),
        "mean_cow_bcs": 5.0,
    }


def _config_observing_runner(scenario: BeefHerdScenario, years: int, seed: int) -> dict[str, float]:
    """Report the live AnimalConfig values the runner can see."""
    return {
        "calf_crop_pct": AnimalConfig.beef_conception_rate_multiplier,
        "mean_calving_interval_days": AnimalConfig.stocker_limit_feed_pct,
        "replacement_rate_pct": float(AnimalConfig.beef_breeding_season_start_day),
        "mean_cow_bcs": 5.0,
    }


def _raising_runner(scenario: BeefHerdScenario, years: int, seed: int) -> dict[str, float]:
    """Fail, so restoration on the error path can be observed."""
    raise RuntimeError("herd drive failed")


# ---------------------------------------------------------------------------
# C-3.1 — BeefHerdScenario
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_scenario_constructs_with_only_a_name() -> None:
    """Every field but the name must have a default."""
    scenario = BeefHerdScenario(name="baseline")
    assert scenario.name == "baseline"


@pytest.mark.unit
def test_scenario_defaults_come_from_constants() -> None:
    """Defaults must reference the C-1 constants, not inline numbers."""
    scenario = BeefHerdScenario(name="baseline")
    assert scenario.calving_month == AnimalModuleConstants.BEEF_SCENARIO_SPRING_CALVING_MONTH
    assert scenario.weaning_age_days == AnimalModuleConstants.BEEF_DEFAULT_WEANING_AGE_DAYS
    assert scenario.cull_rate == pytest.approx(AnimalModuleConstants.BEEF_ANNUAL_CULL_RATE)
    assert scenario.conception_rate_multiplier == pytest.approx(1.0)


@pytest.mark.unit
def test_scenario_defaults_to_stocker_and_grain_fed() -> None:
    """The baseline routes weaned calves to stocker and finishes on grain."""
    scenario = BeefHerdScenario(name="baseline")
    assert scenario.post_weaning_dest is BeefPostWeaningDestination.STOCKER
    assert scenario.finishing_system is FinishingSystem.GRAIN_FED
    assert scenario.stocker_diet_system is StockerDietSystem.PASTURE


@pytest.mark.unit
@pytest.mark.parametrize("bad_month", [0, 13, -1])
def test_scenario_rejects_invalid_calving_month(bad_month: int) -> None:
    """Calving month outside 1-12 must raise at construction."""
    with pytest.raises(ValueError, match="calving_month"):
        BeefHerdScenario(name="bad", calving_month=bad_month)


@pytest.mark.unit
@pytest.mark.parametrize("bad_multiplier", [0.0, -1.0, float("nan"), float("inf")])
def test_scenario_rejects_invalid_conception_multiplier(bad_multiplier: float) -> None:
    """Non-positive or non-finite conception multipliers must raise."""
    with pytest.raises(ValueError, match="conception_rate_multiplier"):
        BeefHerdScenario(name="bad", conception_rate_multiplier=bad_multiplier)


@pytest.mark.unit
@pytest.mark.parametrize("bad_rate", [-0.1, 1.1, float("nan")])
def test_scenario_rejects_invalid_cull_rate(bad_rate: float) -> None:
    """Cull rate outside 0-1 or non-finite must raise."""
    with pytest.raises(ValueError, match="cull_rate"):
        BeefHerdScenario(name="bad", cull_rate=bad_rate)


@pytest.mark.unit
def test_scenario_rejects_empty_name() -> None:
    """A scenario must be named, since the name keys the comparison frame."""
    with pytest.raises(ValueError, match="name"):
        BeefHerdScenario(name="")


# ---------------------------------------------------------------------------
# C-3.4 — the eight named scenarios
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_there_are_exactly_seven_named_scenarios() -> None:
    """BEEF_SCENARIOS must hold the seven pre-built scenarios.

    Backgrounding duration was removed rather than shipped inert, so the
    extended-backgrounding scenario is gone.
    """
    assert len(BEEF_SCENARIOS) == 7


@pytest.mark.unit
@pytest.mark.parametrize(
    "key",
    [
        "spring_calving_baseline",
        "fall_calving",
        "early_weaning",
        "high_conception_rate",
        "low_conception_rate",
        "aggressive_culling",
        "direct_to_feedlot",
    ],
)
def test_named_scenario_exists_and_is_self_named(key: str) -> None:
    """Each scenario must exist and carry its own dict key as its name."""
    assert BEEF_SCENARIOS[key].name == key


@pytest.mark.unit
def test_fall_calving_differs_from_baseline_only_in_calving_month() -> None:
    """The fall scenario varies calving month and nothing else."""
    baseline = BEEF_SCENARIOS["spring_calving_baseline"]
    fall = BEEF_SCENARIOS["fall_calving"]
    assert fall.calving_month == AnimalModuleConstants.BEEF_SCENARIO_FALL_CALVING_MONTH
    assert fall.calving_month != baseline.calving_month
    assert fall.weaning_age_days == baseline.weaning_age_days
    assert fall.cull_rate == pytest.approx(baseline.cull_rate)


@pytest.mark.unit
def test_early_weaning_varies_weaning_age() -> None:
    """The early-weaning scenario uses the early weaning-age constant."""
    assert (
        BEEF_SCENARIOS["early_weaning"].weaning_age_days == AnimalModuleConstants.BEEF_SCENARIO_EARLY_WEANING_AGE_DAYS
    )


@pytest.mark.unit
def test_backgrounding_duration_is_not_a_scenario_field() -> None:
    """Stocker duration has no config home, so it is not a scenario lever.

    The phase ends on target weight or a maximum-days ceiling, not a
    configured duration. A field here would be inert.
    """
    assert "stocker_mo" not in {f.name for f in dataclasses.fields(BeefHerdScenario)}
    assert "extended_backgrounding" not in BEEF_SCENARIOS


@pytest.mark.unit
def test_conception_scenarios_use_the_multiplier_constants() -> None:
    """High and low conception scenarios use the derived multipliers."""
    high = BEEF_SCENARIOS["high_conception_rate"].conception_rate_multiplier
    low = BEEF_SCENARIOS["low_conception_rate"].conception_rate_multiplier
    assert high == pytest.approx(AnimalModuleConstants.BEEF_SCENARIO_HIGH_CONCEPTION_MULTIPLIER)
    assert low == pytest.approx(AnimalModuleConstants.BEEF_SCENARIO_LOW_CONCEPTION_MULTIPLIER)
    assert high > low


@pytest.mark.unit
def test_aggressive_culling_uses_the_cull_constant() -> None:
    """The aggressive-culling scenario uses the aggressive cull constant."""
    scenario = BEEF_SCENARIOS["aggressive_culling"]
    assert scenario.cull_rate == pytest.approx(AnimalModuleConstants.BEEF_SCENARIO_AGGRESSIVE_CULL_RATE)
    assert scenario.cull_rate > AnimalModuleConstants.BEEF_ANNUAL_CULL_RATE


@pytest.mark.unit
def test_direct_to_feedlot_varies_post_weaning_destination() -> None:
    """The direct-to-feedlot scenario bypasses the stocker phase."""
    scenario = BEEF_SCENARIOS["direct_to_feedlot"]
    assert scenario.post_weaning_dest is BeefPostWeaningDestination.DIRECT_TO_FEEDLOT


# ---------------------------------------------------------------------------
# Config snapshot and restore
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_context_manager_restores_all_snapshot_fields() -> None:
    """Every snapshotted field must return to its prior value on exit."""
    before = {name: getattr(AnimalConfig, name) for name in _SNAPSHOT_FIELDS}
    scenario = BeefHerdScenario(
        name="altered",
        calving_month=10,
        conception_rate_multiplier=1.15,
        stocker_diet_system=StockerDietSystem.LIMIT_FEED,
        stocker_limit_feed_pct=70.0,
        finishing_system=FinishingSystem.GRASS_FED,
    )
    with _scenario_config(scenario):
        pass
    assert {name: getattr(AnimalConfig, name) for name in _SNAPSHOT_FIELDS} == before


@pytest.mark.unit
def test_context_manager_applies_config_inside_the_block() -> None:
    """The scenario's values must be live while the block is open."""
    scenario = BeefHerdScenario(
        name="altered",
        conception_rate_multiplier=1.15,
        stocker_diet_system=StockerDietSystem.LIMIT_FEED,
        finishing_system=FinishingSystem.GRASS_FED,
    )
    with _scenario_config(scenario):
        assert AnimalConfig.beef_conception_rate_multiplier == pytest.approx(1.15)
        assert AnimalConfig.stocker_diet_system is StockerDietSystem.LIMIT_FEED
        assert AnimalConfig.finishing_system is FinishingSystem.GRASS_FED


@pytest.mark.unit
def test_context_manager_restores_when_the_body_raises() -> None:
    """A raising body must not leave scenario config applied."""
    before = AnimalConfig.beef_conception_rate_multiplier
    scenario = BeefHerdScenario(name="altered", conception_rate_multiplier=1.15)
    with pytest.raises(RuntimeError, match="boom"):
        with _scenario_config(scenario):
            raise RuntimeError("boom")
    assert AnimalConfig.beef_conception_rate_multiplier == pytest.approx(before)


@pytest.mark.unit
def test_calving_month_is_applied_through_the_accessor() -> None:
    """Setting calving month must move the breeding season start day."""
    scenario = BeefHerdScenario(name="fall", calving_month=10)
    with _scenario_config(scenario):
        assert AnimalConfig.get_beef_calving_month() == 10


# ---------------------------------------------------------------------------
# The leak this module exists to prevent
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_config_does_not_leak_between_scenarios() -> None:
    """A non-default scenario must not change what the next scenario sees.

    BeefGEM config fields parse conditionally, so re-initialising AnimalConfig
    would not reset them when the input omits the key. Without the snapshot,
    every scenario after the first would run with the previous one's config.
    """
    altered = BeefHerdScenario(name="altered", conception_rate_multiplier=1.15, stocker_limit_feed_pct=70.0)
    plain = BeefHerdScenario(name="plain")

    comparison = compare_scenarios(
        {"altered": altered, "plain": plain},
        years=1,
        runner=_config_observing_runner,
    )
    frame = comparison.to_frame()

    assert frame.loc["altered", "calf_crop_pct"] == pytest.approx(1.15)
    assert frame.loc["altered", "mean_calving_interval_days"] == pytest.approx(70.0)
    assert frame.loc["plain", "calf_crop_pct"] == pytest.approx(1.0)
    assert frame.loc["plain", "mean_calving_interval_days"] == pytest.approx(
        AnimalModuleConstants.STOCKER_DEFAULT_LIMIT_FEED_PCT
    )


@pytest.mark.unit
def test_config_restored_after_a_scenario_runner_raises() -> None:
    """A failing scenario must not poison config for the caller."""
    before = AnimalConfig.beef_conception_rate_multiplier
    scenario = BeefHerdScenario(name="doomed", conception_rate_multiplier=1.15)
    with pytest.raises(RuntimeError, match="herd drive failed"):
        run_scenario(scenario, years=1, runner=_raising_runner)
    assert AnimalConfig.beef_conception_rate_multiplier == pytest.approx(before)


# ---------------------------------------------------------------------------
# C-3.2 — run_scenario
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_run_scenario_returns_a_scenario_result() -> None:
    """run_scenario must return a ScenarioResult carrying the scenario name."""
    result = run_scenario(BeefHerdScenario(name="baseline"), years=1, runner=_constant_runner)
    assert isinstance(result, ScenarioResult)
    assert result.name == "baseline"


@pytest.mark.unit
def test_run_scenario_defaults_to_one_replicate() -> None:
    """The default must be a single replicate, matching the original spec."""
    result = run_scenario(BeefHerdScenario(name="baseline"), years=1, runner=_constant_runner)
    assert len(result.replicates) == 1


@pytest.mark.unit
def test_run_scenario_produces_one_row_per_replicate() -> None:
    """Three replicates must give three rows."""
    result = run_scenario(BeefHerdScenario(name="baseline"), years=1, replicates=3, runner=_constant_runner)
    assert len(result.replicates) == 3


@pytest.mark.unit
def test_replicates_use_distinct_seeds() -> None:
    """Each replicate must draw a different seed, or they are not replicates."""
    result = run_scenario(BeefHerdScenario(name="baseline"), years=1, replicates=3, runner=_seed_echoing_runner)
    seeds = [row["calf_crop_pct"] for row in result.replicates]
    assert len(set(seeds)) == 3


@pytest.mark.unit
def test_same_base_seed_reproduces_identical_results() -> None:
    """The same scenario and base seed run twice must match exactly."""
    scenario = BeefHerdScenario(name="baseline")
    first = run_scenario(scenario, years=1, replicates=3, base_seed=7, runner=_seed_echoing_runner)
    second = run_scenario(scenario, years=1, replicates=3, base_seed=7, runner=_seed_echoing_runner)
    assert first.replicates == second.replicates


@pytest.mark.unit
def test_different_base_seed_changes_results() -> None:
    """A different base seed must produce a different seed sequence."""
    scenario = BeefHerdScenario(name="baseline")
    first = run_scenario(scenario, years=1, base_seed=7, runner=_seed_echoing_runner)
    second = run_scenario(scenario, years=1, base_seed=8, runner=_seed_echoing_runner)
    assert first.replicates != second.replicates


@pytest.mark.unit
def test_run_scenario_rejects_non_positive_replicates() -> None:
    """Zero or negative replicates must raise rather than return an empty result."""
    with pytest.raises(ValueError, match="replicates"):
        run_scenario(BeefHerdScenario(name="baseline"), years=1, replicates=0, runner=_constant_runner)


@pytest.mark.unit
def test_run_scenario_rejects_non_positive_years() -> None:
    """Zero or negative years must raise."""
    with pytest.raises(ValueError, match="years"):
        run_scenario(BeefHerdScenario(name="baseline"), years=0, runner=_constant_runner)


@pytest.mark.unit
def test_summary_averages_across_replicates() -> None:
    """summary() must return the per-key mean over replicates."""
    result = run_scenario(BeefHerdScenario(name="baseline"), years=1, replicates=3, runner=_seed_echoing_runner)
    expected = sum(row["calf_crop_pct"] for row in result.replicates) / 3
    assert result.summary()["calf_crop_pct"] == pytest.approx(expected)


@pytest.mark.unit
def test_summary_of_a_single_replicate_is_that_replicate() -> None:
    """With one replicate the summary is just that row."""
    result = run_scenario(BeefHerdScenario(name="baseline"), years=1, runner=_constant_runner)
    assert result.summary() == result.replicates[0]


# ---------------------------------------------------------------------------
# C-3.3 — compare_scenarios
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_compare_returns_a_scenario_comparison() -> None:
    """compare_scenarios must return the comparison object, not a bare frame."""
    comparison = compare_scenarios(
        {"a": BeefHerdScenario(name="a"), "b": BeefHerdScenario(name="b")},
        years=1,
        runner=_constant_runner,
    )
    assert isinstance(comparison, ScenarioComparison)


@pytest.mark.unit
def test_frame_has_one_row_per_scenario() -> None:
    """Two scenarios give two rows, indexed by scenario key."""
    comparison = compare_scenarios(
        {"a": BeefHerdScenario(name="a"), "b": BeefHerdScenario(name="b")},
        years=1,
        runner=_constant_runner,
    )
    frame = comparison.to_frame()
    assert isinstance(frame, pd.DataFrame)
    assert frame.shape[0] == 2
    assert set(frame.index) == {"a", "b"}


@pytest.mark.unit
def test_frame_columns_come_from_the_summary_keys() -> None:
    """Columns must be derived from the runner's dict, not hard-coded."""
    comparison = compare_scenarios({"a": BeefHerdScenario(name="a")}, years=1, runner=_constant_runner)
    assert set(comparison.to_frame().columns) == _SUMMARY_KEYS


@pytest.mark.unit
def test_frame_adapts_to_an_extra_summary_key() -> None:
    """A runner returning a new key must surface as a new column, unchanged code."""

    def _extra_key_runner(scenario: BeefHerdScenario, years: int, seed: int) -> dict[str, float]:
        return dict(_constant_runner(scenario, years, seed), some_future_metric=1.0)

    comparison = compare_scenarios({"a": BeefHerdScenario(name="a")}, years=1, runner=_extra_key_runner)
    assert "some_future_metric" in comparison.to_frame().columns


@pytest.mark.unit
def test_raw_frame_has_one_row_per_replicate_per_scenario() -> None:
    """Three replicates across two scenarios give six raw rows."""
    comparison = compare_scenarios(
        {"a": BeefHerdScenario(name="a"), "b": BeefHerdScenario(name="b")},
        years=1,
        replicates=3,
        runner=_constant_runner,
    )
    raw = comparison.to_raw_frame()
    assert len(raw) == 6
    assert set(raw["scenario"]) == {"a", "b"}


@pytest.mark.unit
def test_common_random_numbers_pair_the_seed_sequences() -> None:
    """With CRN on, every scenario sees the same seeds, so noise cancels."""
    comparison = compare_scenarios(
        {"a": BeefHerdScenario(name="a"), "b": BeefHerdScenario(name="b")},
        years=1,
        replicates=3,
        common_random_numbers=True,
        runner=_seed_echoing_runner,
    )
    rows_a = comparison.results["a"].replicates
    rows_b = comparison.results["b"].replicates
    assert [r["calf_crop_pct"] for r in rows_a] == [r["calf_crop_pct"] for r in rows_b]


@pytest.mark.unit
def test_without_common_random_numbers_seeds_differ_by_scenario() -> None:
    """With CRN off, each scenario draws its own seed sequence."""
    comparison = compare_scenarios(
        {"a": BeefHerdScenario(name="a"), "b": BeefHerdScenario(name="b")},
        years=1,
        replicates=3,
        common_random_numbers=False,
        runner=_seed_echoing_runner,
    )
    rows_a = comparison.results["a"].replicates
    rows_b = comparison.results["b"].replicates
    assert [r["calf_crop_pct"] for r in rows_a] != [r["calf_crop_pct"] for r in rows_b]


@pytest.mark.unit
def test_compare_rejects_an_empty_scenario_mapping() -> None:
    """Comparing nothing must raise rather than return an empty frame."""
    with pytest.raises(ValueError, match="scenarios"):
        compare_scenarios({}, years=1, runner=_constant_runner)


# ---------------------------------------------------------------------------
# End-to-end
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.skip(
    reason="No production herd runner exists: _default_runner raises NotImplementedError and "
    "no end-to-end scenario drives a beef herd, so nothing covers this path yet. Un-skip "
    "once a runner that drives a real HerdManager is wired."
)
def test_spring_vs_fall_calving_end_to_end() -> None:
    """Spring and fall calving produce differing herd summaries on a real herd."""
    comparison = compare_scenarios(
        {
            "spring": BEEF_SCENARIOS["spring_calving_baseline"],
            "fall": BEEF_SCENARIOS["fall_calving"],
        },
        years=1,
    )
    frame = comparison.to_frame()
    assert set(frame.index) == {"spring", "fall"}
    assert not frame.loc["spring"].equals(frame.loc["fall"])


# ---------------------------------------------------------------------------
# Every declared scenario field must reach AnimalConfig
# ---------------------------------------------------------------------------


def _live_config() -> dict[str, object]:
    """Snapshot every AnimalConfig field a scenario is able to change."""
    return {name: getattr(AnimalConfig, name) for name in _SNAPSHOT_FIELDS}


@pytest.mark.component
@pytest.mark.parametrize("scenario_name", sorted(BEEF_SCENARIOS))
def test_declared_scenario_fields_reach_animal_config(scenario_name: str) -> None:
    """A scenario must change config in exactly the fields it declares.

    Guards the class of bug where a scenario varies a dataclass field that
    _scenario_config never applies: the scenario then runs identically to the
    baseline and the comparison is silently meaningless.
    """
    scenario = BEEF_SCENARIOS[scenario_name]
    baseline = BeefHerdScenario(name="baseline")

    declared = {
        field_name
        for field_name in _SNAPSHOT_SOURCE_FIELDS
        if getattr(scenario, field_name) != getattr(baseline, field_name)
    }

    with _scenario_config(baseline):
        baseline_config = _live_config()
    with _scenario_config(scenario):
        scenario_config = _live_config()

    changed = {name for name, value in scenario_config.items() if baseline_config[name] != value}
    expected = {_SCENARIO_FIELD_TO_CONFIG[field_name] for field_name in declared}

    assert changed == expected, (
        f"{scenario_name} declares {sorted(declared) or ['nothing']} but changed "
        f"config {sorted(changed) or ['nothing']}; expected {sorted(expected) or ['nothing']}"
    )


@pytest.mark.component
def test_every_scenario_field_has_a_config_target() -> None:
    """No dataclass field may exist without a config home.

    A field with nowhere to go is a scenario lever that does nothing.
    """
    declarable = {f.name for f in dataclasses.fields(BeefHerdScenario)} - {"name"}
    assert declarable == set(_SCENARIO_FIELD_TO_CONFIG)


@pytest.mark.component
def test_snapshot_list_matches_what_the_writer_touches() -> None:
    """The snapshot is derived from the writes, so the two cannot drift."""
    assert set(_SNAPSHOT_FIELDS) == set(_SCENARIO_FIELD_TO_CONFIG.values())


@pytest.mark.component
def test_no_varying_scenario_is_inert() -> None:
    """A scenario that varies a field must change configuration.

    spring_calving_baseline is excluded by construction: it declares the
    default values, so producing the baseline configuration is correct for it.
    Any other scenario reaching config unchanged is a lever that does nothing.
    """
    baseline = BeefHerdScenario(name="baseline")
    with _scenario_config(baseline):
        baseline_config = _live_config()

    inert = []
    for name, scenario in BEEF_SCENARIOS.items():
        varies = any(
            getattr(scenario, field_name) != getattr(baseline, field_name) for field_name in _SNAPSHOT_SOURCE_FIELDS
        )
        if not varies:
            continue
        with _scenario_config(scenario):
            if _live_config() == baseline_config:
                inert.append(name)
    assert not inert, f"scenarios varying a field with no effect on configuration: {sorted(inert)}"


@pytest.mark.component
@pytest.mark.regression
def test_baseline_scenario_writes_the_shipped_weaning_default() -> None:
    """The baseline must reproduce the shipped config exactly, not approximate it.

    Weaning age is carried in days rather than months precisely so no
    conversion sits between the scenario and the config value.
    """
    with _scenario_config(BEEF_SCENARIOS["spring_calving_baseline"]):
        assert AnimalConfig.beef_weaning_age_days == AnimalModuleConstants.BEEF_DEFAULT_WEANING_AGE_DAYS
        assert AnimalConfig.beef_weaning_age_days == 207
