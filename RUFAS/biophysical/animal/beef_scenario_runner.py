"""Beef herd scenario comparison — run named management scenarios and compare outcomes.

A scenario is a set of management choices (calving month, weaning age, conception
rate, cull rate, post-weaning destination, finishing system). This module applies
one to AnimalConfig, drives a herd, collects the herd summary, and assembles the
results of several scenarios into a comparison frame.

Driving a full simulation requires a populated InputManager, the
weather and feed subsystems, and the ration formulation cycle — most
of RuFaS. This module therefore takes the herd drive as an injectable
callable rather than owning it. Unit tests inject a stub. No production
runner exists yet: the default runner raises, and no simulation entry
point calls this module.

Results are held per replicate rather than pre-averaged. The cow-calf module
draws conception stochastically, so repeat runs of the same scenario differ;
collapsing to a single point would discard that spread. Replicates default to 1,
so nothing is slower than a single-run design, but the return type does not have
to change when more are wanted.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field

import pandas as pd

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_enums import (
    BeefPostWeaningDestination,
    FinishingSystem,
    StockerDietSystem,
)

MONTHS_IN_YEAR: int = 12
"""Calendar months per year, for calving-month validation."""

DEFAULT_SCENARIO_YEARS: int = 3
"""Simulated years per scenario when the caller does not say otherwise."""

DEFAULT_BASE_SEED: int = 42
"""Seed the per-replicate sequence starts from, so runs are reproducible."""

_SCENARIO_FIELD_TO_CONFIG: dict[str, str] = {
    "calving_month": "beef_breeding_season_start_day",
    "weaning_age_days": "beef_weaning_age_days",
    "conception_rate_multiplier": "beef_conception_rate_multiplier",
    "cull_rate": "beef_cow_cull_rate_annual",
    "post_weaning_dest": "beef_post_weaning_destination",
    "finishing_system": "finishing_system",
    "stocker_diet_system": "stocker_diet_system",
    "stocker_limit_feed_pct": "stocker_limit_feed_pct",
}
"""Every BeefHerdScenario field and the AnimalConfig ClassVar it drives.

A scenario field absent from this map is a lever that does nothing, so the
suite asserts the map covers the dataclass exactly.
"""

_SNAPSHOT_SOURCE_FIELDS: tuple[str, ...] = tuple(_SCENARIO_FIELD_TO_CONFIG)
"""The scenario-side field names, in map order."""

_SNAPSHOT_FIELDS: tuple[str, ...] = tuple(_SCENARIO_FIELD_TO_CONFIG.values())
"""AnimalConfig ClassVars a scenario may change, snapshotted around every run.

Four of these parse conditionally from input and so survive a re-initialisation
when the input file omits the key. beef_breeding_season_start_day does reset on
its own, but is snapshotted alongside them so that a later change to how it is
assigned cannot silently reintroduce the leak.
"""


@dataclass
class BeefHerdScenario:
    """A named set of beef herd management choices to simulate.

    Attributes
    ----------
    name : str
        Identifier, used as the row key in a comparison frame.
    calving_month : int
        Calendar month (1-12) the calving season opens.
    weaning_age_days : int
        Calf age at weaning, in days.
    conception_rate_multiplier : float
        Scenario lever scaling the calibrated base daily conception probability.
        1.0 leaves calibrated behaviour untouched.
    cull_rate : float
        Annual cow cull fraction.
    post_weaning_dest : BeefPostWeaningDestination
        Where calves go at weaning.
    finishing_system : FinishingSystem
        Grain or grass finishing, which selects the enteric methane pathway.
    stocker_diet_system : StockerDietSystem
        Pasture, drylot forage, or limit-feeding during backgrounding.
    stocker_limit_feed_pct : float
        Intake ceiling as a percentage of ad libitum, used under limit-feeding.

    Raises
    ------
    ValueError
        If the name is empty, or any numeric field is outside its valid range
        or non-finite.

    """

    name: str
    calving_month: int = AnimalModuleConstants.BEEF_SCENARIO_SPRING_CALVING_MONTH
    weaning_age_days: int = AnimalModuleConstants.BEEF_DEFAULT_WEANING_AGE_DAYS
    conception_rate_multiplier: float = 1.0
    cull_rate: float = AnimalModuleConstants.BEEF_ANNUAL_CULL_RATE
    post_weaning_dest: BeefPostWeaningDestination = BeefPostWeaningDestination.STOCKER
    finishing_system: FinishingSystem = FinishingSystem.GRAIN_FED
    stocker_diet_system: StockerDietSystem = StockerDietSystem.PASTURE
    stocker_limit_feed_pct: float = AnimalModuleConstants.STOCKER_DEFAULT_LIMIT_FEED_PCT

    def __post_init__(self) -> None:
        """Validate every field, so an invalid scenario cannot reach a run."""
        if not self.name:
            raise ValueError("scenario name must be a non-empty string")
        if self.calving_month < 1 or self.calving_month > MONTHS_IN_YEAR:
            raise ValueError(f"calving_month must be in 1-12, got {self.calving_month}")
        if self.weaning_age_days <= 0:
            raise ValueError(f"weaning_age_days must be positive, got {self.weaning_age_days}")
        if not math.isfinite(self.conception_rate_multiplier) or self.conception_rate_multiplier <= 0.0:
            raise ValueError(
                f"conception_rate_multiplier must be positive and finite, got {self.conception_rate_multiplier}"
            )
        if not math.isfinite(self.cull_rate) or not 0.0 <= self.cull_rate <= 1.0:
            raise ValueError(f"cull_rate must be in 0.0-1.0 and finite, got {self.cull_rate}")
        if not math.isfinite(self.stocker_limit_feed_pct) or not 0.0 < self.stocker_limit_feed_pct <= 100.0:
            raise ValueError(
                f"stocker_limit_feed_pct must be in (0, 100] and finite, got {self.stocker_limit_feed_pct}"
            )


HerdRunner = Callable[[BeefHerdScenario, int, int], dict[str, float]]
"""Drives one replicate: takes a scenario, simulated years and a seed; returns a herd summary."""


@dataclass
class ScenarioResult:
    """One scenario's replicates, held raw rather than pre-averaged.

    Attributes
    ----------
    name : str
        The scenario's name.
    scenario : BeefHerdScenario
        The scenario that produced these replicates.
    replicates : list[dict[str, float]]
        One herd summary per replicate, in seed order.

    """

    name: str
    scenario: BeefHerdScenario
    replicates: list[dict[str, float]] = field(default_factory=list)

    def summary(self) -> dict[str, float]:
        """Return the per-key mean across replicates.

        Returns
        -------
        dict[str, float]
            Mean of each metric. An empty result returns an empty dict.

        """
        if not self.replicates:
            return {}
        keys = self.replicates[0].keys()
        count = len(self.replicates)
        return {key: sum(row[key] for row in self.replicates) / count for key in keys}


@dataclass
class ScenarioComparison:
    """Several scenarios' results, with frames built on demand.

    Attributes
    ----------
    results : dict[str, ScenarioResult]
        Per-scenario results, keyed as the caller keyed the scenarios.

    Notes
    -----
    The raw replicate rows are retained rather than only the aggregate, so that
    serialising a comparison for cross-commit or cross-version checking is a
    method someone adds later rather than a reshape of lost data.

    """

    results: dict[str, ScenarioResult] = field(default_factory=dict)

    def to_frame(self) -> pd.DataFrame:
        """Return one row per scenario, columns taken from the summary keys.

        Returns
        -------
        pd.DataFrame
            Indexed by scenario key. Columns are whatever keys the herd summary
            returned, so a metric added upstream appears here without a change.

        """
        return pd.DataFrame({name: result.summary() for name, result in self.results.items()}).T

    def to_raw_frame(self) -> pd.DataFrame:
        """Return one row per replicate, with scenario and replicate columns.

        Returns
        -------
        pd.DataFrame
            Long-form rows carrying ``scenario`` and ``replicate`` alongside the
            summary metrics, for inspecting spread rather than only means.

        """
        rows: list[dict[str, float | str | int]] = []
        for name, result in self.results.items():
            for index, replicate in enumerate(result.replicates):
                rows.append({"scenario": name, "replicate": index, **replicate})
        return pd.DataFrame(rows)


@contextmanager
def _scenario_config(scenario: BeefHerdScenario) -> Iterator[None]:
    """Apply a scenario's config, restoring prior values on exit.

    BeefGEM config fields parse conditionally — if key is not None —
    so re-initialising AnimalConfig does not reset them when the
    input file omits the key, which it does. Without this,
    configuration from one scenario leaks into the next and
    compare_scenarios silently returns wrong numbers for every
    scenario after the first.

    Parameters
    ----------
    scenario : BeefHerdScenario
        The scenario whose configuration to apply for the duration of the block.

    Yields
    ------
    None
        Control returns to the caller with the scenario's config live.

    """
    saved = {name: getattr(AnimalConfig, name) for name in _SNAPSHOT_FIELDS}
    try:
        AnimalConfig.set_beef_calving_month(scenario.calving_month)
        AnimalConfig.beef_weaning_age_days = scenario.weaning_age_days
        AnimalConfig.beef_conception_rate_multiplier = scenario.conception_rate_multiplier
        AnimalConfig.beef_cow_cull_rate_annual = scenario.cull_rate
        AnimalConfig.beef_post_weaning_destination = scenario.post_weaning_dest
        AnimalConfig.finishing_system = scenario.finishing_system
        AnimalConfig.stocker_diet_system = scenario.stocker_diet_system
        AnimalConfig.stocker_limit_feed_pct = scenario.stocker_limit_feed_pct
        yield
    finally:
        for name, value in saved.items():
            setattr(AnimalConfig, name, value)


def _default_runner(scenario: BeefHerdScenario, years: int, seed: int) -> dict[str, float]:
    """Drive a real herd for one replicate.

    Parameters
    ----------
    scenario : BeefHerdScenario
        The scenario being run. Its config is already applied by the caller.
    years : int
        Simulated years.
    seed : int
        Replicate seed.

    Raises
    ------
    NotImplementedError
        Always. Driving a herd needs a populated InputManager, the weather and
        feed subsystems and the ration cycle, none of which this module owns.
        Callers supply a runner that closes over an already-constructed herd.

    """
    raise NotImplementedError(
        "beef_scenario_runner does not construct a herd. Pass a runner that drives "
        "an already-constructed HerdManager and returns "
        "AnimalModuleReporter.get_beef_herd_summary(herd)."
    )


def run_scenario(
    scenario: BeefHerdScenario,
    years: int = DEFAULT_SCENARIO_YEARS,
    replicates: int = 1,
    base_seed: int = DEFAULT_BASE_SEED,
    runner: HerdRunner | None = None,
) -> ScenarioResult:
    """Run one scenario for the given number of replicates.

    Parameters
    ----------
    scenario : BeefHerdScenario
        The scenario to run.
    years : int
        Simulated years per replicate. Must be positive.
    replicates : int
        Independent runs. Must be positive. Defaults to 1.
    base_seed : int
        Seed the replicate sequence starts from; replicate i uses base_seed + i.
    runner : HerdRunner | None
        Herd drive. Defaults to one that raises, since this module does not
        construct a herd — see the module docstring.

    Returns
    -------
    ScenarioResult
        The scenario's replicate rows, unaveraged.

    Raises
    ------
    ValueError
        If ``years`` or ``replicates`` is not positive.

    Notes
    -----
    The scenario's configuration is applied inside a context manager, so prior
    AnimalConfig values are restored even when the runner raises.

    """
    if years <= 0:
        raise ValueError(f"years must be positive, got {years}")
    if replicates <= 0:
        raise ValueError(f"replicates must be positive, got {replicates}")

    drive: HerdRunner = runner if runner is not None else _default_runner
    rows: list[dict[str, float]] = []
    with _scenario_config(scenario):
        for index in range(replicates):
            rows.append(drive(scenario, years, base_seed + index))
    return ScenarioResult(name=scenario.name, scenario=scenario, replicates=rows)


def compare_scenarios(
    scenarios: Mapping[str, BeefHerdScenario],
    years: int = DEFAULT_SCENARIO_YEARS,
    replicates: int = 1,
    common_random_numbers: bool = True,
    base_seed: int = DEFAULT_BASE_SEED,
    runner: HerdRunner | None = None,
) -> ScenarioComparison:
    """Run several scenarios and collect their results for comparison.

    Parameters
    ----------
    scenarios : Mapping[str, BeefHerdScenario]
        Scenarios to run, keyed by the name to index results under.
    years : int
        Simulated years per replicate.
    replicates : int
        Independent runs per scenario.
    common_random_numbers : bool
        When True (the default) every scenario uses the same seed sequence.
    base_seed : int
        Seed the sequences start from.
    runner : HerdRunner | None
        Herd drive, passed through to run_scenario.

    Returns
    -------
    ScenarioComparison
        Per-scenario results, with frames built on demand.

    Raises
    ------
    ValueError
        If ``scenarios`` is empty.

    Notes
    -----
    Common random numbers matter more than they look. Giving every scenario the
    same seed sequence means a paired difference between two scenarios cancels
    the noise they share, so a real management effect is visible at far fewer
    replicates than independent sampling would need. Turn it off only when
    scenarios must be statistically independent.

    """
    if not scenarios:
        raise ValueError("scenarios must not be empty")

    results: dict[str, ScenarioResult] = {}
    for offset, (key, scenario) in enumerate(scenarios.items()):
        seed = base_seed if common_random_numbers else base_seed + offset * replicates
        results[key] = run_scenario(
            scenario,
            years=years,
            replicates=replicates,
            base_seed=seed,
            runner=runner,
        )
    return ScenarioComparison(results=results)


BEEF_SCENARIOS: dict[str, BeefHerdScenario] = {
    "spring_calving_baseline": BeefHerdScenario(
        name="spring_calving_baseline",
        calving_month=AnimalModuleConstants.BEEF_SCENARIO_SPRING_CALVING_MONTH,
    ),
    "fall_calving": BeefHerdScenario(
        name="fall_calving",
        calving_month=AnimalModuleConstants.BEEF_SCENARIO_FALL_CALVING_MONTH,
    ),
    "early_weaning": BeefHerdScenario(
        name="early_weaning",
        calving_month=AnimalModuleConstants.BEEF_SCENARIO_SPRING_CALVING_MONTH,
        weaning_age_days=AnimalModuleConstants.BEEF_SCENARIO_EARLY_WEANING_AGE_DAYS,
    ),
    "high_conception_rate": BeefHerdScenario(
        name="high_conception_rate",
        conception_rate_multiplier=AnimalModuleConstants.BEEF_SCENARIO_HIGH_CONCEPTION_MULTIPLIER,
    ),
    "low_conception_rate": BeefHerdScenario(
        name="low_conception_rate",
        conception_rate_multiplier=AnimalModuleConstants.BEEF_SCENARIO_LOW_CONCEPTION_MULTIPLIER,
    ),
    "aggressive_culling": BeefHerdScenario(
        name="aggressive_culling",
        cull_rate=AnimalModuleConstants.BEEF_SCENARIO_AGGRESSIVE_CULL_RATE,
    ),
    "direct_to_feedlot": BeefHerdScenario(
        name="direct_to_feedlot",
        post_weaning_dest=BeefPostWeaningDestination.DIRECT_TO_FEEDLOT,
    ),
}
"""The seven pre-built comparison scenarios, each varying one management choice."""
