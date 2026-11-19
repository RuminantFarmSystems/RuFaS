# RuFaS BeefGEM Management Implementation Plan (Single PR)

**Scope:** BeefGEM management enhancement layer — all 4 phases in one PR
**PR strategy:** Single branch `feature/beef-beefgem-management`, single review cycle
**Prerequisite:** ALL three native segments merged to dev-msf:
- Feedlot → PR #32 ✅
- Cow-Calf → PRs #33–#36 ✅
- Stocker/Backgrounding → PR #47 (merge before starting this plan)

**BeefGEM source:** `RuFaS_BeefGEM_Management_Implementation_Plan.docx`
**Plan version:** 1.0 — single-PR structure; RuFaS style guidelines v1.0 applied

---

## Why Single PR

- All 4 phases share the same architectural patterns now established across PRs #32–#47
- The reviewer (post-Jules) will see the full BeefGEM story in one coherent diff
- Phase dependencies are internal — Phase D builds on Phase B which builds on Phase A —
  splitting into multiple PRs creates rebase cascades with no benefit
- Estimated diff: ~60–80 files, ~6,000–8,000 insertions — larger than stocker but
  reviewable in 2–3 sessions with a well-structured PR description

**Risk mitigation:** Run `/challenge plan` across all 8 steps before writing any code.
Apply the full pre-review checklist before requesting review. Each phase has its own
test checkpoint — problems surface within the phase, not at the end.

---

## Internal Phase Dependency Order

```
Phase A (finishing_system flag)
    ↓ (extends feedlot code)
Phase B (stocker enhancements: limit-feeding + NASEM CH4)
    ↓ (extends stocker code)
Phase C (scenario runner: depends on all 3 segments + Phase B)
    ↓ (depends on scenario runner for stress modifiers)
Phase D (heat stress + compensatory gain)
```

Implement in this exact order. Do not start Phase C until Phases A and B pass
their test checkpoints. Do not start Phase D until Phase C passes its checkpoint.

---

## RuFaS Style Rules (non-negotiable — apply from first commit)

Same rules as the stocker plan. The three highest-recurrence:

**Rule 1 — Enum members, never string literals**
```python
# WRONG:
if AnimalConfig.finishing_system == "grain_fed":
# CORRECT:
if AnimalConfig.finishing_system is FinishingSystem.GRAIN_FED:
```
Before any PR: `git diff dev-msf -- '*.py' | grep -E '"grain_fed"|"grass_fed"|"limit_feed"'`
Must return zero matches.

**Rule 2 — copy.deepcopy with direct attribute access for ClassVar dicts**
```python
# CORRECT for fixtures:
saved = copy.deepcopy(RationManager.beef_stocker_pasture_ration)
# Scalars (int/float/bool/enum): direct assignment, no deepcopy
saved_system = AnimalConfig.finishing_system
```

**Rule 3 — Scoped formatting only**
```bash
black RUFAS/biophysical/animal/ \
      tests/test_biophysical/test_animal/test_beefgem/
# NEVER: black .
```

---

## Step Summary Table

| Phase | Step | Title | Key files | Effort |
|-------|------|-------|-----------|--------|
| A | A-1 | Finishing system flag + finishing CH4 routing | `animal_config.py`, `animal_enums.py`, `animal_module_constants.py`, `beef_nrc_requirements_calculator.py`, `animal_module_reporter.py` | 0.5 day |
| B | B-1 | Limit-feeding diet system for stocker | `animal_config.py`, `ration_manager.py`, `beef_stocker_requirements_calculator.py` | 1 day |
| B | B-2 | NASEM 2016 stocker CH4 enteric equation | `beef_stocker_requirements_calculator.py`, `animal_module_constants.py`, `animal_module_reporter.py` | 1 day |
| C | C-1 | BeefHerdScenario config dataclass | `animal_config.py`, `animal_module_constants.py`, `animal_typed_dicts.py` | 1 day |
| C | C-2 | Herd population summary reporter | `animal_module_reporter.py`, `herd_manager.py` | 1.5 days |
| C | C-3 | Scenario runner and comparison output | `beef_scenario_runner.py` (NEW) | 1 day |
| D | D-1 | Heat stress — THI-based DMI and NEm | `beef_nrc_requirements_calculator.py`, `beef_stocker_requirements_calculator.py`, `animal_module_constants.py`, `animal_config.py` | 1 day |
| D | D-2 | Compensatory gain after restriction | `animal.py`, `beef_nrc_requirements_calculator.py`, `animal_module_constants.py`, `animal_config.py` | 1.5 days |

**Total estimated effort: 8.5 developer-days**

---

## PHASE A — Production System Flag

### Step A-1: `finishing_system` flag

**Files:** `animal_config.py`, `animal_module_constants.py`, `animal_enums.py`,
`beef_nrc_requirements_calculator.py`, `animal_module_reporter.py`,
`data_validator.py`

### A-1.1 Add `FinishingSystem` enum

```python
class FinishingSystem(Enum):
    """Production system for beef finishing cattle."""
    GRAIN_FED = "grain_fed"     # conventional feedlot (default — no behavior change)
    GRASS_FED = "grass_fed"     # grass-finished, uses the linear grass-fed CH4 model
```

Add to `animal_enums.py` alongside `StockerDietSystem` and `BeefPostWeaningDestination`.
Plain `Enum` — NOT `str, Enum` (house rule enforced by Jules on PR #47).

### A-1.2 Add to `AnimalConfig`

```python
# In the feedlot section:
finishing_system: FinishingSystem = FinishingSystem.GRAIN_FED
```

Parse from `feedlot_cfg.get("finishing_system")` using walrus operator pattern:
```python
if (raw := feedlot_cfg.get("finishing_system")) is not None:
    cls.finishing_system = FinishingSystem(str(raw))
```

Validate in `DataValidator.validate_feedlot_config`:
```python
if "finishing_system" in config and config["finishing_system"] is not None:
    system = str(config["finishing_system"])
    valid = {s.value for s in FinishingSystem}
    if system not in valid:
        raise ValueError(
            f"finishing_system must be one of {sorted(valid)}, got '{system}'"
        )
```

### A-1.3 Regression guard

The default `FinishingSystem.GRAIN_FED` must produce identical output to the
current feedlot module. Add a regression test:
```python
def test_grain_fed_default_unchanged():
    """finishing_system=GRAIN_FED produces identical NEm/NEg as before Phase A."""
    # Compare BeefNRCRequirementsCalculator output at grain_fed vs previous baseline
```

### A-1.4 Grass-fed enteric CH4 constants

`calculate_enteric_ch4_grass_fed()` is added in Phase A, so the constants it
reads must land in Phase A as well. Add to `animal_module_constants.py`:

```python
# ===== BEEF FINISHING ENTERIC CH4 CONSTANTS (NRC 2016 Ch.16) =====

BEEF_CH4_GRASS_FED_INTERCEPT: float = 8.25
"""
Linear enteric CH4 model for grass-finished beef: intercept (g CH4/d). Distinct
from the Mitscherlich Model 3 curve (MITS_PARAMETER_A/_B, Mills et al. 2003)
already in animal_constants.py, despite the source document referring to this
as "Mits3". Provenance for these coefficients is the BeefGEM source document;
no NRC 2016 equation number has been identified for them.
"""

BEEF_CH4_GRASS_FED_SLOPE: float = 31.2
"""
Linear enteric CH4 model for grass-finished beef: slope (g CH4 per kg DMI/d).
Same provenance caveat as the intercept above.
"""
```

The constants are deliberately named `BEEF_CH4_*`, not `MITS_*`. The name
`Mits3` in the source document collides with `MITS_PARAMETER_A` / `MITS_PARAMETER_B`
in `animal_constants.py`, which parameterise a different equation — the
exponential Mitscherlich Model 3 of Mills et al. (2003).

Note: at DMI 8 kg/d these coefficients give 257.85 g/d. NRC 2016
Ch.16 reports 87-252 g/d for grazing beef cattle, so the pinned value
sits just above the published range. Values are pinned by the source
document and retained for traceability, but this should be raised
with the reviewer before the grass-fed path is used in anger.

Record the published range alongside the coefficients so the discrepancy
is checkable rather than only described:

```python
BEEF_CH4_GRASS_FED_VALIDATION_RANGE_G_D: tuple[float, float] = (87.0, 252.0)
"""
Reported range of enteric CH4 for grazing beef cattle, NRC 2016
Ch.16. Used as a plausibility check on calculate_enteric_ch4_grass_fed
output, not as a clamp.
"""
```

The suite pins the discrepancy directly, asserting that the grass-fed
equation exceeds the published upper bound at DMI 8 kg/d. That test is a
tripwire, not an endorsement: it should fail and be rewritten if the
coefficients are ever re-sourced.

The stocker forage pair (`BEEF_CH4_STOCKER_FORAGE_INTERCEPT` / `BEEF_CH4_STOCKER_FORAGE_SLOPE`)
is stocker-only and stays in Phase B — see B-2.1.

### A-1.5 Finishing CH4 calculation methods

A `finishing_system` flag that routes to nothing is untestable, so both
finishing equations land in Phase A alongside the flag.

In `BeefNRCRequirementsCalculator` (used by feedlot):
```python
@classmethod
def calculate_enteric_ch4_grass_fed(cls, dmi: float) -> float:
    """Linear enteric CH4 for grass-finished beef (g/d)."""
    return (AnimalModuleConstants.BEEF_CH4_GRASS_FED_INTERCEPT
            + AnimalModuleConstants.BEEF_CH4_GRASS_FED_SLOPE * dmi)

@classmethod
def calculate_enteric_ch4_grain_fed(cls, dmi: float) -> float:
    """Enteric CH4 for grain-finished feedlot cattle (g/d).

    IPCC Tier 2 with Ym = 3.0% of gross energy intake, offered by
    NRC 2016 Table 16-2 for cases where diet composition is not
    available at the call site.
    """
    gross_energy_intake_mj = dmi * AnimalModuleConstants.BEEF_GROSS_ENERGY_MJ_PER_KG_DM
    methane_energy_mj = gross_energy_intake_mj * AnimalModuleConstants.BEEF_CH4_YM_FRACTION
    return methane_energy_mj / AnimalModuleConstants.BEEF_CH4_ENERGY_MJ_PER_G
```

Both guard `dmi` with `math.isfinite` and reject negatives. The three IPCC
constants go in `animal_module_constants.py` alongside the grass-fed pair:
`BEEF_CH4_YM_FRACTION` (0.030), `BEEF_GROSS_ENERGY_MJ_PER_KG_DM` (18.45),
`BEEF_CH4_ENERGY_MJ_PER_G` (0.05565). Do not hardcode the conversion.

At DMI 9 kg/d this yields 89.51 g/d, inside the 36-145 g/d range NRC 2016
Ch.16 reports for finishing cattle.

**Eq. 16-9 deferred** - NRC 2016 Eq. 16-9 is the primary feedlot
enteric CH4 equation and requires six inputs including ration
composition, which is not reachable from the reporter today. Phase A
uses the IPCC Tier 2 fallback that NRC Table 16-2 offers for this
case. Upgrading to Eq. 16-9 requires threading ration composition to
the reporter and belongs in its own step.

The stocker equation (`calculate_enteric_ch4_stocker()`, NASEM Eq.6.8) is
Phase B — see B-2.2.

### A-1.6 Route the finishing CH4 equation in the reporter

In `AnimalModuleReporter.report_feedlot_performance()`:
```python
if AnimalConfig.finishing_system is FinishingSystem.GRASS_FED:
    ch4 = BeefNRCRequirementsCalculator.calculate_enteric_ch4_grass_fed(dmi)
else:
    ch4 = BeefNRCRequirementsCalculator.calculate_enteric_ch4_grain_fed(dmi)
om.add_variable("feedlot_mean_daily_enteric_ch4_g_d", ch4, ...)
```

Mark changelog `[OutputChange]` — new output variable `feedlot_mean_daily_enteric_ch4_g_d`.

### Phase A Test Checkpoint

Write `tests/test_biophysical/test_animal/test_beefgem/test_finishing_system.py`:
- `FinishingSystem` enum exists with GRAIN_FED and GRASS_FED members
- Invalid string raises `ValueError` at config load
- Default is GRAIN_FED
- `BEEF_CH4_GRASS_FED_INTERCEPT == 8.25` and `BEEF_CH4_GRASS_FED_SLOPE == 31.2`
- Mits3 grass-fed: at DMI=8 kg/d → CH4 = 8.25 + 31.2×8 = 257.85 g/d (exact)
- `finishing_system=GRAIN_FED` routes to the grain-fed equation
- `finishing_system=GRASS_FED` routes to the Mits3 equation
- Regression: GRAIN_FED output matches pre-Phase-A baseline (no behavior change)

---

## PHASE B — Stocker Enhancements

### Step B-1: Limit-Feeding Diet System

**Files:** `animal_config.py`, `ration_manager.py`, `beef_stocker_requirements_calculator.py`

### B-1.1 Extend `StockerDietSystem`

Add `LIMIT_FEED` to the existing enum:
```python
class StockerDietSystem(Enum):
    PASTURE      = "pasture"
    DRYLOT_FORAGE = "drylot_forage"
    LIMIT_FEED   = "limit_feed"    # NEW — BeefGEM Phase B
```

### B-1.2 Add limit-feed config to `AnimalConfig`

```python
# In stocker section:
stocker_limit_feed_pct: float = 85.0    # % of ad libitum DMI when limit-feeding
```

Validate: `0 < stocker_limit_feed_pct <= 100`, math.isfinite.

### B-1.3 DMI adjustment in `BeefStockerRequirementsCalculator`

Applied as a single guarded block at the end of `_calculate_dmi`, after the
ad libitum value is computed:
```python
if diet_system is StockerDietSystem.LIMIT_FEED:
    return ad_libitum_dmi * (limit_feed_pct / 100.0)
return ad_libitum_dmi
```

The calculator receives `diet_system` and `limit_feed_pct` through
`StockerRequirementsInputs` rather than reading `AnimalConfig`. Both are
defaulted so existing call sites are unaffected; `animal.py` supplies
them from `AnimalConfig`. This keeps `BeefStockerRequirementsCalculator`
free of config imports, consistent with how `mud_condition`,
`temperature_c` and every other input is already handled, and keeps the
DMI cap testable without patching global state.

### B-1.4 Add ration and constraints

```python
# RationManager:
beef_stocker_limit_feed_ration: ClassVar[dict[RUFAS_ID, float]] = {}
```

Update `get_beef_stocker_ration()` to handle `LIMIT_FEED`.
Update `_select_constraints` AND `handle_failed_constraints` in same commit.

### B-1.5 Track restricted intake days on Animal

```python
# New instance attributes (set in _initialize_stocker_animal):
self.days_on_restricted_intake: int = 0
self.is_on_restricted_intake: bool = False
```

In `_stocker_daily_routines()`:
```python
if AnimalConfig.stocker_diet_system is StockerDietSystem.LIMIT_FEED:
    self.is_on_restricted_intake = True
    self.days_on_restricted_intake += 1
```

### Phase B-1 Test Checkpoint

Write `test_beefgem/test_limit_feeding.py`:
- DMI reduced by correct fraction when LIMIT_FEED active
- days_on_restricted_intake increments correctly
- Ration constraints consistent between _select_constraints and handle_failed_constraints
- NaN/inf stocker_limit_feed_pct raises ValueError at config load

---

### Step B-2: NASEM 2016 CH4 Enteric Equation

**Files:** `beef_nrc_requirements_calculator.py`, `beef_stocker_requirements_calculator.py`,
`animal_module_reporter.py`, `animal_module_constants.py`

### B-2.1 Stocker forage CH4 constants

Add to `animal_module_constants.py`:
```python
# Linear enteric CH4 for stocker cattle on forage.
# See the provenance note below — no NRC 2016 equation number identified.
BEEF_CH4_STOCKER_FORAGE_INTERCEPT: float = 10.04
"""Intercept of the stocker forage enteric CH4 model (g CH4/d)."""

BEEF_CH4_STOCKER_FORAGE_SLOPE: float = 23.7
"""Slope of the stocker forage enteric CH4 model (g CH4 per kg DMI/d)."""
```

The constants carry the `BEEF_CH4_` prefix used by the rest of this family,
not `NASEM_`, because the `NASEM_` prefix asserts a provenance that does not
hold — see below.

**Two BeefGEM coefficient sets could not be traced to NRC 2016.**

Grass-fed (`BEEF_CH4_GRASS_FED_*`, 8.25 / 31.2): give 257.85 g/d at
8 kg DM/d, above the 87-252 g/d NRC Ch.16 reports for grazing cattle.
Pinned in the suite as a tripwire.

Stocker forage (`BEEF_CH4_STOCKER_FORAGE_*`, 10.04 / 23.7): the source
document labels these "NASEM 2016, eq 6.8". NRC Ch.6 is protein and
amino acids; enteric methane is Ch.16, Eq. 16-8 and 16-9. Neither
coefficient appears anywhere in the BeefGEM source document, whose own
backgrounding rule R-CH4-ENT-003 uses the four-input Eq. 16-8 form
(71.5 + 0.12*BW + 0.10*DMI^3 - 244.8*fat). Output values do fall
inside the NRC range across the working intake band, but the equation
itself has no identified source.

Both are implemented as pinned, for traceability. Neither should be
treated as NRC-sourced without re-derivation.

**Note:** the grass-fed pair (`BEEF_CH4_GRASS_FED_INTERCEPT` = 8.25,
`BEEF_CH4_GRASS_FED_SLOPE` = 31.2) was already added in Phase A step A-1.4,
because `calculate_enteric_ch4_grass_fed()` is a Phase A deliverable. Do not
add them again here. Only the two forage constants above are new in Phase B.

### B-2.2 Implement the stocker CH4 calculation method

**Note:** the two finishing methods (`calculate_enteric_ch4_grain_fed()` and
`calculate_enteric_ch4_grass_fed()`) and the `finishing_system` reporter
routing were added in Phase A, steps A-1.5 and A-1.6. B-2 adds only the
stocker path.

In `BeefStockerRequirementsCalculator` (used by stocker):
```python
@classmethod
def calculate_enteric_ch4_stocker(cls, dmi: float) -> float:
    """NASEM 2016 Eq.6.8 enteric CH4 for stocker/backgrounding on forage (g/d)."""
    return (AnimalModuleConstants.BEEF_CH4_STOCKER_FORAGE_INTERCEPT
            + AnimalModuleConstants.BEEF_CH4_STOCKER_FORAGE_SLOPE * dmi)
```

### B-2.3 Report the stocker CH4 output

In `AnimalModuleReporter.report_stocker_performance()`:
```python
ch4 = BeefStockerRequirementsCalculator.calculate_enteric_ch4_stocker(dmi)
om.add_variable("stocker_mean_daily_enteric_ch4_g_d", ch4, ...)
```

Mark changelog `[OutputChange]` — new output variable `stocker_mean_daily_enteric_ch4_g_d`.

### Phase B-2 Test Checkpoint

Write `test_beefgem/test_enteric_ch4.py`:
- NASEM Eq.6.8 stocker: at DMI=10 kg/d → CH4 = 10.04 + 23.7×10 = 247.04 g/d (exact)
- `stocker_mean_daily_enteric_ch4_g_d` appears in the stocker reporter output
- Feedlot CH4 routing is unchanged from Phase A (regression guard)

---

## PHASE C — Herd Population Dynamics

### Step C-0: COW_CALF_STOCKER_FEEDLOT grouping scenario

**Files:** `RUFAS/biophysical/animal/animal_grouping_scenarios.py`

**Context:** `BEEF_STOCKER_ONLY` (delivered by PR #47) supports stocker-only
simulations. `COW_CALF_STOCKER_FEEDLOT` enables the full cow-calf → stocker →
feedlot production chain. It is a prerequisite for the C-3 scenario runner and
was deferred from the stocker module as a named scope boundary.

**BeefGEM source:** `herd_dynamics.py` — `LIVE = ('cows', 'calves',
'young_heifers', 'yearling_heifers', 'stockers', 'finishing')`

Add to `animal_grouping_scenarios.py` after `BEEF_STOCKER_ONLY`:

```python
COW_CALF_STOCKER_FEEDLOT = {
    AnimalCombination.BEEF_COW_CALF_PAIR: [
        AnimalType.BEEF_COW, AnimalType.BEEF_CALF,
    ],
    AnimalCombination.BEEF_GESTATING:    [AnimalType.BEEF_COW],
    AnimalCombination.BEEF_REPLACEMENT:  [AnimalType.BEEF_HEIFER_REPLACEMENT],
    AnimalCombination.BEEF_BULL_BATTERY: [AnimalType.BEEF_BULL],
    AnimalCombination.BEEF_STOCKER: [
        AnimalType.BEEF_STOCKER_STEER, AnimalType.BEEF_STOCKER_HEIFER,
    ],
    AnimalCombination.FEEDLOT_FINISHING: [
        AnimalType.FEEDLOT_STEER, AnimalType.FEEDLOT_HEIFER,
    ],
}
```

No new `AnimalCombination` member is required. The source document's
`BEEF_COW_CALF` was a planning simplification written before the
cow-calf module existed; the merged code partitions cow-calf into
four combinations because each needs a different ration constraint
set. Reusing them is both zero-cost and scientifically correct.

`BEEF_COW` appears under both `BEEF_COW_CALF_PAIR` and `BEEF_GESTATING`,
matching `BEEF_COW_CALF_HERD`. The static
`_animal_combination_by_animal_type` dict resolves this last-write-wins
to `BEEF_GESTATING`, and `find_animal_combination` raises
`NotImplementedError` for `BEEF_COW` — runtime dispatch on live
reproduction state is the Step 7 hook, not C-0's scope. C-0 must not
attempt to resolve it.

Every combination reachable by the ration optimiser needs a branch in
`_select_constraints`. All six here already have one, so C-0 adds no
optimiser risk.

### Phase C-0 Test Checkpoint

Write `tests/test_biophysical/test_animal/test_beefgem/test_grouping_scenario.py`:

- `COW_CALF_STOCKER_FEEDLOT` exists in `AnimalGroupingScenario`
- The scenario uses six combinations: the four from `BEEF_COW_CALF_HERD`
  plus `BEEF_STOCKER` and `FEEDLOT_FINISHING`
- `BEEF_COW` maps to both `BEEF_COW_CALF_PAIR` and `BEEF_GESTATING`,
  consistent with `BEEF_COW_CALF_HERD` (this is expected, not a defect)
- `find_animal_combination` raises `NotImplementedError` for `BEEF_COW`
  (Step 7 scope — not C-0)
- All eight expected types are present across the six combinations
  (`BEEF_COW`, `BEEF_CALF`, `BEEF_HEIFER_REPLACEMENT`, `BEEF_BULL`,
  `BEEF_STOCKER_STEER`, `BEEF_STOCKER_HEIFER`, `FEEDLOT_STEER`, `FEEDLOT_HEIFER`)
- `BEEF_STOCKER_ONLY` is unaffected (regression guard)

---

### Step C-1: BeefHerdScenario Config Dataclass

**Files:** `animal_config.py`, `animal_module_constants.py`

### C-1.1 Named scenario constants

```python
# ===== BEEFGEM NAMED SCENARIO DEFAULTS (Phase C) =====

BEEF_SCENARIO_SPRING_CALVING_MONTH: int = 4      # April calving
BEEF_SCENARIO_FALL_CALVING_MONTH: int = 10       # October calving
BEEF_SCENARIO_EARLY_WEANING_AGE_DAYS: int = 150  # round figure; no day-based source
BEEF_SCENARIO_HIGH_CONCEPTION_MULTIPLIER: float = 1.15
BEEF_SCENARIO_LOW_CONCEPTION_MULTIPLIER: float = 0.625
BEEF_SCENARIO_AGGRESSIVE_CULL_RATE: float = 0.22
```

These are named-scenario defaults — the management choices being compared —
not measured biological values. Their docstrings say so and carry no NRC or
USDA citation.

The two conception constants are multipliers on the calibrated base daily
probability, derived rather than assumed linear. At the calibration reference
point (BCS 5, 25:1 bull ratio) both adjustment factors are 1.0, so the seasonal
rate over the 63-day season is `1 - (1 - 0.0404 x m)^63`. Inverting for a target
gives 1.15 for 95% and 0.625 for 80%; the baseline 1.0 yields 92.56%.

**The plan previously described 0.855 as a "USDA reference conception
rate". It is not.** BEEF_CALF_CROP_WEANED_RATE = 0.855 is USDA NASS
calf crop weaned per cow exposed, downstream of conception,
stillbirth and preweaning mortality. The conception-equivalent figure
is 91.5%, which BEEF_CONCEPTION_BASE_DAILY_PROB is already calibrated
against. The BeefGEM source document conflates the two.

### C-1.2 Scenario parameter fields on `AnimalConfig`

Add to beef cow-calf section:
```python
beef_conception_rate_multiplier: float = 1.0   # > 0, finite; 1.0 = calibrated baseline
```

plus a calving-month accessor pair over the existing
`beef_breeding_season_start_day`:

```python
AnimalConfig.get_beef_calving_month() -> int
AnimalConfig.set_beef_calving_month(month: int) -> None
```

Implemented as a classmethod pair rather than a property. AnimalConfig
is never instantiated — it is a class-level namespace of ClassVar
fields with classmethod accessors — so a plain property would return
the property object rather than a value, and making one work would
require adding the animal subsystem's only metaclass to its most
widely imported config class. The classmethod pair gives the same
guarantee against desynchronisation, since only
beef_breeding_season_start_day is ever stored.

Month-to-day is one-to-many. The setter maps month M to the first
day of M, so month -> day -> month round-trips losslessly, while
day -> month -> day snaps to the month start. Expected behaviour for
a coarsening accessor.

**The shipped default is not a spring-calving herd.**
`BEEF_DEFAULT_BREEDING_SEASON_START_DAY` is 90 and gestation is 283 days, so
calving falls on day 373, wrapping to 8 January — month 1, not the month 4 that
`BEEF_SCENARIO_SPRING_CALVING_MONTH` pins. The breeding default is deliberately
left at 90; April calving is a scenario override, not the default. A test pins
`get_beef_calving_month() == 1` at the shipped default so a later change to the
breeding default fails loudly and says what it did.

`beef_conception_rate_multiplier` is a scenario lever, not a target rate. The
cow-calf module derives calf crop from daily conception draws conditioned on BCS,
bull ratio and days postpartum — it is an emergent outcome. A stored calving-rate
field would be a second, conflicting source of truth, so the lever scales the
calibrated base daily probability instead and defaults to 1.0.

conception_rate_multiplier is threaded through
`calculate_seasonal_conception_probability` as a parameter rather than
read from AnimalConfig inside it. The module previously imported only
AnimalModuleConstants — frozen values, not simulation state — so
importing config would have made it the first dependency on mutable
global state, and would have required a save/restore fixture in every
test touching the function. There is one production call site, in
`animal.py`, where AnimalConfig is already in scope and already
supplying the adjacent bull-ratio argument. Same reasoning as the
stocker calculator, which takes `diet_system` and `limit_feed_pct`
through its inputs dataclass for identical reasons.

### Phase C-1 Test Checkpoint

- All 8 named scenario constants exist with correct values
- `beef_calving_month` validates 1–12
- `beef_conception_rate_multiplier` validates > 0 and `math.isfinite`

---

### Step C-2: Herd Population Summary Reporter

**Files:** `animal_module_reporter.py`, `herd_manager.py`

### C-2.1 Summary metrics

Add `get_beef_herd_summary()` to `AnimalModuleReporter`:

```python
@classmethod
def get_beef_herd_summary(cls, herd_manager: HerdManager,
                          simulation_day: int) -> dict[str, float]:
    """Return a summary dict for scenario comparison.

    Returns
    -------
    dict[str, float]
        Keys: calf_crop_pct, mean_calving_interval_days, replacement_rate_pct,
        mean_cow_bcs
    """
```

Four metrics ship. Four originally specified are **cut**, not returned as 0.0 —
a zero would be indistinguishable from a real measurement. Each is recorded as
a scope boundary in the module README and carries a deferred task.

**Exit-performance metrics are not summarised.** Stocker and feedlot
average daily gain and days on feed are emitted per animal at exit
and written to the output manager, but nothing retains them across a
run. Summarising them at herd level requires an accumulator that does
not currently exist.

**Feedlot exit reporting is not wired.** `report_feedlot_performance`
exists but is never called in production. The call belongs in a
feedlot daily-update path that has not been built, so no feedlot
animal currently reaches the reporter. This is a pre-existing gap,
not introduced here.

**Beef cattle produce no enteric methane in the herd totals.**
Digestion supports dairy animal types only, so beef animals never
contribute to the herd methane total. The enteric methane
calculations in this module are computed at exit as mean-daily values
and written directly to output, not accumulated. A herd-level methane
total requires per-day beef methane, which is a modelling gap rather
than a plumbing one.

### C-2.2 Metrics to compute

| Metric | Source | Formula |
|--------|--------|---------|
| `calf_crop_pct` | `herd_manager.beef_cows` | sum(times_calved) / len(beef_cows) × 100 — survivors only, biased upward |
| `mean_calving_interval_days` | cow event history | mean days between consecutive calvings |
| `replacement_rate_pct` | `beef_replacement_heifers` | heifers / cows × 100 |
| `mean_cow_bcs` | `beef_cows` | mean `body_condition_score_9` |
| ~~`mean_stocker_adg_kg_d`~~ | CUT — no accumulator exists | deferred |
| ~~`mean_feedlot_adg_kg_d`~~ | CUT — no accumulator, reporter unwired | deferred |
| ~~`mean_feedlot_days_on_feed`~~ | CUT — no accumulator, reporter unwired | deferred |
| ~~`total_enteric_ch4_g_d`~~ | CUT — beef produce no daily methane | deferred |

### Phase C-2 Test Checkpoint

Write `test_beefgem/test_herd_summary_reporter.py`:
- `get_beef_herd_summary` returns 4 keys (see the CUT rows above)
- `calf_crop_pct` computes correctly from mock herd state
- Empty herd returns zeros not errors

---

### Step C-3: Scenario Runner

**File:** `beef_scenario_runner.py` (NEW — in `RUFAS/biophysical/animal/`)

### C-3.1 Scenario configuration dataclass

```python
@dataclass
class BeefHerdScenario:
    """Configuration for a single beef herd simulation scenario."""
    name: str
    calving_month: int = AnimalModuleConstants.BEEF_SCENARIO_SPRING_CALVING_MONTH
    weaning_age_days: int = AnimalModuleConstants.BEEF_DEFAULT_WEANING_AGE_DAYS
    conception_rate_multiplier: float = 1.0
    cull_rate: float = AnimalModuleConstants.BEEF_ANNUAL_CULL_RATE
    post_weaning_dest: BeefPostWeaningDestination = BeefPostWeaningDestination.STOCKER
    finishing_system: FinishingSystem = FinishingSystem.GRAIN_FED
```

### C-3.2 Runner functions

```python
def run_scenario(scenario: BeefHerdScenario,
                 years: int = 3) -> dict[str, float]:
    """Run a single BeefHerdScenario and return summary dict."""
    # Apply scenario params to AnimalConfig
    # Run HerdManager._process_daily_herd_updates for years*365 days
    # Return AnimalModuleReporter.get_beef_herd_summary(...)

def compare_scenarios(scenarios: dict[str, BeefHerdScenario],
                      years: int = 3) -> "pd.DataFrame":
    """Run multiple named scenarios and return comparison DataFrame.

    Returns
    -------
    pd.DataFrame
        One row per scenario name, columns = summary metric names.
    """
    import pandas as pd
    results = {name: run_scenario(s, years) for name, s in scenarios.items()}
    return pd.DataFrame(results).T
```

Backgrounding duration is not a scenario variable. The stocker phase ends on
target weight or on a maximum-days ceiling, not a configured duration, so a
scenario cannot vary it. The extended-backgrounding scenario was removed rather
than shipped with no effect.

### C-3.3 Pre-built named scenarios

```python
BEEF_SCENARIOS: dict[str, BeefHerdScenario] = {
    "spring_calving_baseline": BeefHerdScenario(
        name="spring_calving_baseline", calving_month=4),
    "fall_calving": BeefHerdScenario(
        name="fall_calving", calving_month=10),
    "early_weaning": BeefHerdScenario(
        name="early_weaning", calving_month=4, weaning_age_days=150),
    "high_conception_rate": BeefHerdScenario(
        name="high_conception_rate",
        conception_rate_multiplier=AnimalModuleConstants.BEEF_SCENARIO_HIGH_CONCEPTION_MULTIPLIER),
    "low_conception_rate": BeefHerdScenario(
        name="low_conception_rate",
        conception_rate_multiplier=AnimalModuleConstants.BEEF_SCENARIO_LOW_CONCEPTION_MULTIPLIER),
    "aggressive_culling": BeefHerdScenario(
        name="aggressive_culling",
        cull_rate=AnimalModuleConstants.BEEF_SCENARIO_AGGRESSIVE_CULL_RATE),
    "direct_to_feedlot": BeefHerdScenario(
        name="direct_to_feedlot",
        post_weaning_dest=BeefPostWeaningDestination.DIRECT_TO_FEEDLOT),
}
```

### Phase C-3 Test Checkpoint

Write `test_beefgem/test_scenario_runner.py`:
```python
@pytest.mark.integration
def test_spring_vs_fall_calving_scenarios():
    """Spring and fall calving shift the month of peak calf counts."""
    df = compare_scenarios({"spring": BEEF_SCENARIOS["spring_calving_baseline"],
                            "fall": BEEF_SCENARIOS["fall_calving"]}, years=1)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 4)  # 2 scenarios × 4 metrics
    assert set(df.index) == {"spring", "fall"}
    assert set(df.columns) == {"calf_crop_pct", "mean_calving_interval_days",
                               "replacement_rate_pct", "mean_cow_bcs"}
```

The frame has four columns, not eight. `get_beef_herd_summary` returns four
keys; the other four were cut in C-2 because nothing retains the state they
would summarise. C-3 consumes the summary by key, so it inherits whatever
`get_beef_herd_summary` returns — do not hard-code the column count in the
runner itself.

---

## PHASE D — Environmental Stress and Performance Modifiers

The combined cow-calf, stocker and feedlot grouping scenario is defined and
correct but cannot be selected for a simulation run. A replacement heifer
promoting to cow on first calving reaches pen assignment, which cannot resolve a
beef cow to a pen combination without dispatching on her live reproduction
state. That dispatch does not exist. The scenario is rejected at selection
rather than failing part-way through a run.

### Step D-1: Heat Stress (THI-Based DMI and NEm Reduction)

**Files:** `beef_nrc_requirements_calculator.py`, `beef_stocker_requirements_calculator.py`,
`animal_module_constants.py`, `animal_config.py`

**Humidity source — resolved: static configuration value**

`relative_humidity_pct` is a static `AnimalConfig` field, not a daily
weather input.

```python
relative_humidity_pct: float | None = None
```

Validation: if present and not None, `0.0 <= value <= 100.0` and
`math.isfinite`. `None` disables heat stress entirely, preserving
backward compatibility.

Rationale: extending `CurrentDayConditions` and the weather input
schema would touch `weather.py`, `data_validator.py` and the
CI-protected input fixtures — the same fixtures that trigger the
protected-files check on every merge, and files with large upstream
deltas pending sync. Out of proportion to Phase D.

**Response shape — resolved: piecewise-linear**

The BeefGEM source reports a four-class step function. A single
linear coefficient understates the mild and moderate classes; the
raw step function produces discontinuities in daily output.
Piecewise-linear interpolation between anchor points is continuous
across the whole THI range and reproduces the moderate and severe
class values exactly at their thresholds.

THI 72 is treated as the *onset* of stress — the point at which the
multiplier begins to depart from 1.00 — rather than as the point at which
the mild class value takes effect.

The source's mild-class values (DMI 0.95, NEm 1.07) are not used as
anchors. Pinning them at THI 72 would create a step at the onset —
a 5-point DMI cliff between 71.9 and 72.1 — which produces sawtooth
artefacts in daily output as animals cross the boundary. Anchoring
at 1.00 instead means the mild values are reached around THI 75-77,
within the mild class rather than at its edge. The moderate and
severe class values are reproduced exactly at 80 and 90.

Precisely: the source DMI mild value of 0.95 falls out of the
interpolation at THI 75.33, and the NEm mild value of 1.07 at THI 76.67.
Both sit inside the 72-80 mild band, which is the intended reading.

### D-1.1 THI calculation and threshold constants

```python
# ===== HEAT STRESS CONSTANTS (BeefGEM Phase D) =====

BEEF_THI_BREAKPOINTS: tuple[float, ...] = (72.0, 80.0, 90.0)
"""
THI anchor points for beef cattle heat stress interpolation. 72 is
the onset of stress, 80 the moderate class value, 90 the severe.
BeefGEM source document; NRC 2016 Ch.11.
"""

BEEF_HEAT_STRESS_DMI_MULTIPLIERS: tuple[float, ...] = (1.00, 0.88, 0.75)
"""
DMI multiplier at each THI anchor point. Below 72 no reduction
applies; above 90 the value is clamped. The source document reports
these as discrete classes; they are interpolated linearly between
anchors here so daily output is continuous and animals crossing a
threshold do not produce step artefacts.
"""

BEEF_HEAT_STRESS_NEm_MULTIPLIERS: tuple[float, ...] = (1.00, 1.12, 1.20)
"""
Maintenance energy multiplier at each THI anchor point. Same
interpolation treatment as the DMI multipliers.
"""
```

All three tuples are the same length and pair one-to-one:
`BEEF_HEAT_STRESS_*_MULTIPLIERS[i]` is the multiplier at
`BEEF_THI_BREAKPOINTS[i]`. Adding an anchor without adding the matching
multiplier would otherwise fail silently, so the interpolator asserts the
lengths match.

### D-1.2 THI calculation

```python
@staticmethod
def calculate_thi(temperature_c: float, relative_humidity_pct: float) -> float:
    """Temperature-Humidity Index for beef cattle heat stress.

    Parameters
    ----------
    temperature_c : float
        Dry-bulb air temperature (°C).
    relative_humidity_pct : float
        Relative humidity (0-100%).

    Returns
    -------
    float
        THI value. Values > 72 indicate mild heat stress.

    Notes
    -----
    Formula: THI = (1.8 × T + 32) − (0.55 − 0.0055 × RH) × (1.8 × T − 26)
    Source: NRC 2016 Ch.11; BeefGEM physiology.py.
    """
    t_f = 1.8 * temperature_c + 32
    return t_f - (0.55 - 0.0055 * relative_humidity_pct) * (1.8 * temperature_c - 26)
```

Note: the second bracket is `(1.8 × T − 26)`, NOT `(t_f − 26)`. These
differ by 32 and the wrong form understates THI by roughly 3.5 units
at 30 °C / 80% RH, which would silently suppress heat stress
throughout. Verified: at 30 °C / 80% RH this yields 82.92.

### D-1.3 Apply heat stress modifiers

In `BeefNRCRequirementsCalculator.calculate_requirements()` and
`BeefStockerRequirementsCalculator.calculate_requirements()`:

```python
@staticmethod
def _interpolate_heat_stress(thi: float,
                             multipliers: tuple[float, ...]) -> float:
    """Piecewise-linear multiplier for a given THI.

    Below the first anchor returns 1.0; above the last returns the
    final multiplier; between anchors interpolates linearly.
    """
    bps = AnimalModuleConstants.BEEF_THI_BREAKPOINTS
    if len(multipliers) != len(bps):
        raise ValueError(
            f"heat stress multipliers must pair one-to-one with "
            f"BEEF_THI_BREAKPOINTS: got {len(multipliers)} multipliers "
            f"for {len(bps)} anchors"
        )
    if thi <= bps[0]:
        return multipliers[0]
    if thi >= bps[-1]:
        return multipliers[-1]
    for i in range(len(bps) - 1):
        if bps[i] <= thi < bps[i + 1]:
            frac = (thi - bps[i]) / (bps[i + 1] - bps[i])
            return multipliers[i] + frac * (multipliers[i + 1] - multipliers[i])
    return multipliers[-1]
```

Applied after base DMI and NEm are computed:

```python
if inputs.temperature_c is not None and inputs.relative_humidity_pct is not None:
    thi = cls.calculate_thi(inputs.temperature_c, inputs.relative_humidity_pct)
    dmi *= cls._interpolate_heat_stress(
        thi, AnimalModuleConstants.BEEF_HEAT_STRESS_DMI_MULTIPLIERS
    )
    ne_m *= cls._interpolate_heat_stress(
        thi, AnimalModuleConstants.BEEF_HEAT_STRESS_NEm_MULTIPLIERS
    )
```

No `max(dmi, 0.0)` floor is needed: every multiplier is positive and the
interpolation is bounded by the tuple, so DMI cannot go negative.

`relative_humidity_pct` is read from `AnimalConfig` (see the humidity
decision above) and threaded into both input dataclasses as
`float | None = None`. When `None`, no heat stress is applied.

### Phase D-1 Test Checkpoint

Write `test_beefgem/test_heat_stress.py`:

- THI at 30°C / 80% RH = 82.92 (±0.01) — guards the `(1.8 × T − 26)` bracket
- All three tuples are the same length; a mismatched length raises ValueError
- Interpolation reproduces the moderate and severe class values exactly at
  their anchors: DMI 0.88 at THI 80 and 0.75 at THI 90; NEm 1.12 and 1.20
- Interpolation at the midpoints: DMI 0.94 at THI 76, 0.815 at THI 85;
  NEm 1.06 and 1.16
- Below and at THI 72: multipliers are 1.00 (no reduction)
- Above THI 90: multipliers clamp to 0.75 and 1.20
- Monotonicity: DMI multiplier never increases as THI rises; NEm never decreases
- Continuity at the onset — no step at THI 72:

```python
@pytest.mark.unit
def test_heat_stress_continuous_at_onset() -> None:
    """No step at THI 72 — the response rises from 1.0 continuously."""
    just_below = _interpolate_heat_stress(71.999, DMI_MULTIPLIERS)
    just_above = _interpolate_heat_stress(72.001, DMI_MULTIPLIERS)
    assert just_above == pytest.approx(just_below, abs=1e-4)
```

- `relative_humidity_pct=None`: no heat stress applied (backward compat)

---

### Step D-2: Compensatory Gain After Nutritional Restriction

An intake-fraction threshold was specified but removed: restriction is tracked
by diet system rather than measured intake, so nothing read it. A future step
needing an intake threshold should derive one rather than inherit an unused
constant.

**Files:** `animal.py`, `beef_nrc_requirements_calculator.py`,
`animal_module_constants.py`, `animal_config.py`

### D-2.1 Compensatory gain constants

```python
# ===== COMPENSATORY GAIN CONSTANTS (BeefGEM Phase D) =====

CG_RESTRICTION_THRESHOLD_DAYS: int = 21
"""Minimum days of restricted intake before compensatory gain triggers."""

CG_MAX_ADG_MULTIPLIER: float = 1.25
"""Ceiling on compensatory gain ADG multiplier (biological plausibility)."""

CG_DECAY_RATE_PER_DAY: float = 0.02
"""CG advantage declines 2% per day after restriction ends."""
```

### D-2.2 Config gate

```python
# In AnimalConfig stocker section:
enable_compensatory_gain: bool = False  # opt-in, not default
```

Default `False` — backward compatible, no behavior change unless explicitly enabled.

### D-2.3 Tracking restricted days in stocker

In `_stocker_daily_routines()` (already has `is_on_restricted_intake` from Phase B-1):

```python
if AnimalConfig.enable_compensatory_gain:
    if self.is_on_restricted_intake:
        self.days_on_restricted_intake += 1
    else:
        # CG decay when restriction ends
        if self.compensatory_gain_factor > 1.0:
            self.compensatory_gain_factor = max(
                1.0,
                self.compensatory_gain_factor
                - AnimalModuleConstants.CG_DECAY_RATE_PER_DAY
            )
```

### D-2.4 Setting CG factor on stocker exit / feedlot entry

In `_stocker_life_stage_update()` before transitioning to feedlot:

```python
if (AnimalConfig.enable_compensatory_gain
        and self.days_on_restricted_intake
        > AnimalModuleConstants.CG_RESTRICTION_THRESHOLD_DAYS):
    raw = 1.0 + (self.days_on_restricted_intake
                 - AnimalModuleConstants.CG_RESTRICTION_THRESHOLD_DAYS) * 0.005
    self.compensatory_gain_factor = min(
        raw, AnimalModuleConstants.CG_MAX_ADG_MULTIPLIER
    )
```

### D-2.5 Apply CG factor in growth calculation

In `BeefNRCRequirementsCalculator` and `BeefStockerRequirementsCalculator`:

```python
# Modify target_adg by CG factor before NEg calculation:
effective_adg = inputs.target_adg * inputs.compensatory_gain_factor
effective_adg = min(effective_adg,
                    inputs.target_adg * AnimalModuleConstants.CG_MAX_ADG_MULTIPLIER)
```

Add `compensatory_gain_factor: float = 1.0` to both input dataclasses.

### D-2.6 CG decay in feedlot

In `_feedlot_daily_routines()` (already exists):

```python
if self.compensatory_gain_factor > 1.0:
    self.compensatory_gain_factor = max(
        1.0,
        self.compensatory_gain_factor
        - AnimalModuleConstants.CG_DECAY_RATE_PER_DAY
    )
```

### Phase D-2 Test Checkpoint

Write `test_beefgem/test_compensatory_gain.py`:
- 30 days restricted → CG factor > 1.0 at stocker exit
- CG factor ≤ CG_MAX_ADG_MULTIPLIER regardless of restriction length
- CG decay after restriction ends (factor approaches 1.0)
- `enable_compensatory_gain=False` → factor always 1.0 (regression guard)
- NEg higher with CG factor > 1.0 than without

---

## Documentation and Changelog (After All 4 Phases Pass)

**Files:** `docs/beef_module/beefgem/README.md` (NEW), `changelog.md`, `CLAUDE.md`

### `docs/beef_module/beefgem/README.md`

Document what BeefGEM adds and what remains out of scope:

**What this module adds:**
1. `finishing_system` flag (grain vs grass-fed)
2. Limit-feeding diet system for stocker
3. NASEM 2016 CH4 enteric equation (stocker on forage + grass-fed feedlot)
4. Herd population summary reporter (4 metrics)
5. Scenario runner with 8 named pre-built scenarios
6. Heat stress THI-based DMI and NEm modifiers
7. Compensatory gain after nutritional restriction (opt-in)

**Remaining scope boundaries (not in this module):**
1. No pasture growth model — forage quality remains a static config input
2. No genetic improvement simulation — breed constants only
3. No economic output — physical performance metrics only
4. No sexed-pen management — steers and heifers managed together
5. **Static humidity** — Heat stress uses a single configured relative
   humidity rather than daily values, so seasonal variation in humidity
   is not represented. Threading humidity through `CurrentDayConditions`
   and the weather input schema is a future-PR candidate.
6. **Unverified grass-fed CH4 coefficients** — The grass-fed intercept and
   slope come from the BeefGEM source document. No NRC 2016 equation number
   has been identified for them, and at 8 kg DM/d they give 257.85 g/d,
   above the 87-252 g/d NRC 2016 Ch.16 reports for grazing cattle. Pinned
   for traceability; a candidate for re-sourcing against NRC Eq.16-8.

**Named future-PR gaps (BeefGEM source mapping, Section 10):**
7. Brody growth curve for stocker body weight (`physiology.py` CSBW model) —
   NRC 2016 daily equations used instead; Brody curve is a separate enhancement PR
8. Pasture DMI supply-driven grazing fraction (`grazing_capacity_fraction`) —
   requires pasture DM availability from the crop module
9. Ionophore (monensin) DMI reduction, 3–5% — BeefGEM documents but does not
   quantify; add `monensin_dmi_reduction_pct` to `AnimalConfig` in a future PR
10. Implant ADG factor quantification — BeefGEM documents but does not quantify
   the multiplier; needs product-label or USDA data mapping
11. Explicit BCS effect on reproduction — the `conception_rate_multiplier`
   lever captures it implicitly; explicit BCS tracking is needed for the
   reproduction module

**No "Lesson X" references anywhere in this file.**

### `changelog.md`

Tag as `[OutputChange]` — new variables: `feedlot_mean_daily_enteric_ch4_g_d`,
`stocker_mean_daily_enteric_ch4_g_d`. get_beef_herd_summary is not an
output variable — it has no production call site and is never written
via om.add_variable; it is consumed directly by the scenario runner.

---

## Integration Test (After All 4 Phases)

**File:** `tests/test_biophysical/test_animal/test_beefgem/test_beefgem_integration.py`

```python
@pytest.mark.integration
def test_beefgem_full_simulation():
    """Full BeefGEM simulation: spring calving baseline scenario, 1 year."""
    df = compare_scenarios(
        {"spring": BEEF_SCENARIOS["spring_calving_baseline"]}, years=1
    )
    row = df.loc["spring"]
    assert 60.0 <= row["calf_crop_pct"] <= 100.0
    assert row["mean_cow_bcs"] > 0

@pytest.mark.integration
def test_two_scenarios_differ():
    """Spring and fall calving produce different reporter outputs."""
    df = compare_scenarios({
        "spring": BEEF_SCENARIOS["spring_calving_baseline"],
        "fall": BEEF_SCENARIOS["fall_calving"],
    }, years=1)
    assert df.shape[0] == 2
    # The two scenarios must differ on at least one metric
    assert not df.iloc[0].equals(df.iloc[1])
```

---

## Test Marker Taxonomy

All BeefGEM tests must use the markers registered in `pyproject.toml`.
Five markers apply to this PR — use them consistently:

| Marker | Scope | Examples in this plan |
| --- | --- | --- |
| `@pytest.mark.unit` | Equation-level: single function, no I/O | THI calculation, CG factor, CH4 g/d |
| `@pytest.mark.component` | Lifecycle events: single class, no multi-module wiring | stocker-to-feedlot transfer, weaning dispatch |
| `@pytest.mark.integration` | Multi-module herd simulation | Phase C-2 herd reporter, C-3 scenario runner |
| `@pytest.mark.regression` | Backward-compatibility guard: default config unchanged | GRAIN_FED default, `enable_compensatory_gain=False` |
| `@pytest.mark.nrc2016` | NRC 2016 benchmark validation | CH4 Eq.6.8 pinned values, THI formula check |

**Note:** `nrc2016` is registered as "Specifically validates against NRC 2016 Chapter 20"
but is used across all NRC 2016 chapters in the beef module. Apply it to any test that
pins a value directly from the NRC 2016 text (equations, tables, or examples).

---

## Pre-Review Checklist (Run Before Requesting Review)

After any rebase, re-check `changelog.md`. It is set to `merge=union` in
`.gitattributes`, so the merge keeps every line from both sides. Adding a line
is safe across a rebase; editing or deleting one is not — the old line returns
and the edit appears to have been reverted. Confirm each entry appears exactly
once.

```bash
# 1. Branch current
git fetch origin
git log HEAD..origin/dev-msf --oneline  # must be empty

# 1b. changelog.md survived the rebase (merge=union keeps both sides)
grep -c "<your entry's distinguishing phrase>" changelog.md   # must be 1
grep -c "<phrase from any entry you replaced>" changelog.md   # must be 0

# 2. No string literals where enums exist
git diff dev-msf -- '*.py' | \
grep -E '"grain_fed"|"grass_fed"|"limit_feed"|"pasture"|"drylot_forage"' | \
grep -v "^Binary\|enum\|Enum\|value\|pytest\|match=\|get(\|parametrize"
# Must be zero

# 3. No stray files
git diff dev-msf --stat
# Only BeefGEM-relevant files

# 4. No internal references in docs/changelog
grep -rn "Lesson\|PR #[0-9]* round\|Step [A-D]-[0-9]" \
docs/beef_module/beefgem/ changelog.md
# Must be zero

# 5. No bad fixture patterns
grep -rn "copy.deepcopy(getattr\|saved = {\|dict(RationManager" \
tests/test_biophysical/test_animal/test_beefgem/
# Must be zero

# 6. Ruff (scoped)
ruff check RUFAS/biophysical/animal/ \
           tests/test_biophysical/test_animal/test_beefgem/

# 7. Black (scoped — NOT black .)
black --check RUFAS/biophysical/animal/ \
              tests/test_biophysical/test_animal/test_beefgem/

# 8. Full test suite
pytest tests/ -x --tb=short -q
```

---

## Claude Code Kickoff Message

```
I am implementing the BeefGEM management enhancement layer for RuFaS.
This is a SINGLE PR covering all 4 phases (A, B, C, D).

Prerequisites — confirm all merged to dev-msf before starting:
git log --oneline origin/dev-msf | head -5
(PR #32 feedlot, PRs #33-#36 cow-calf, PR #47 stocker must all be present)

Branch:
git checkout dev-msf
git pull origin dev-msf
git checkout -b feature/beef-beefgem-management

Plan reference: docs/beef_module/beefgem/RuFaS_BeefGEM_Implementation_Plan.md
Read this file completely before writing any code.

BeefGEM source document: RuFaS_BeefGEM_Management_Implementation_Plan.docx
Read Phase A, B, C, D sections for full context before Step A-1.

RuFaS style rules (apply from first commit):
1. Plain Enum not str,Enum (enforced on PR #47)
2. copy.deepcopy(ClassName.attr) for ClassVar dicts — no getattr wrapper
3. Scoped formatting only — never ruff check . or black .
4. mocker.patch.object for class state — never hasattr/setattr/delattr
5. math.isfinite from first draft on ALL new numeric config fields
6. No internal references in docs/changelog (no "Phase X step Y")
7. Explicit named fixture saves — no dict loops, no setattr loops
8. Reporter called from herd_manager, never from animal.py

PHASE ORDER — implement strictly in sequence:
Phase A → Phase B → Phase C → Phase D

Run /challenge plan on all 8 steps before writing any code.

After /challenge plan, implement Phase A only:
- Write test_finishing_system.py FIRST, confirm red
- Implement FinishingSystem enum + AnimalConfig + DataValidator
- Confirm green, run ruff+black (scoped), run full suite
- Report back before Phase B

Do not proceed to Phase B until Phase A gate passes and I confirm.
```

---

*Plan version: 1.0 — single-PR structure; all 4 BeefGEM phases*
*Source: RuFaS_BeefGEM_Management_Implementation_Plan.docx*
*McGill University · July 2026*
