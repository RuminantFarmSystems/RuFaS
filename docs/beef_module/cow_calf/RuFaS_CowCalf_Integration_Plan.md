# RuFaS Beef Module
# Cow-Calf Production System — Integration Plan

*Scope: Cow-Calf Breeding Herd | Management & Nutrition | NASEM 2021 (Dairy-pattern) + NRC 2016 (Beef)*

Companion document to the Beef Feedlot Module Implementation Plan (PR #32, merged)

---

## Table of Contents

- [Overview and How to Use This Document](#overview-and-how-to-use-this-document)
  - [Step Summary Table](#step-summary-table)
- [Lessons Learned from the Feedlot Module (PR #32) — Applied Up Front](#lessons-learned-from-the-feedlot-module-pr-32--applied-up-front)
  - [Lesson 1 — Don't pool sub-types when reporting needs to be class-specific](#lesson-1--dont-pool-sub-types-when-reporting-needs-to-be-class-specific)
  - [Lesson 2 — Guard input config shape, not just truthiness](#lesson-2--guard-input-config-shape-not-just-truthiness)
  - [Lesson 3 — Validate config invariants, including non-finite values](#lesson-3--validate-config-invariants-including-non-finite-values)
  - [Lesson 4 — Test the actual routing, not just the output shape](#lesson-4--test-the-actual-routing-not-just-the-output-shape)
  - [Lesson 5 — Isolate shared class state between tests](#lesson-5--isolate-shared-class-state-between-tests)
  - [Lesson 6 — Don't change the original code's error semantics while fixing something else](#lesson-6--dont-change-the-original-codes-error-semantics-while-fixing-something-else)
  - [Lesson 7 — Scope discipline: don't defer integration wiring as an afterthought](#lesson-7--scope-discipline-dont-defer-integration-wiring-as-an-afterthought)
  - [Lesson 8 — Verify integration points exist before assuming they need to be built](#lesson-8--verify-integration-points-exist-before-assuming-they-need-to-be-built)
- [Architecture Overview](#architecture-overview)
- [STEP 1 — Extend the Enums](#step-1--extend-the-enums)
  - [1.1 animal_types.py — Add Cow-Calf Animal Types](#11-animal_typespy--add-cow-calf-animal-types)
  - [1.2 animal_enums.py — No new Breed members needed](#12-animal_enumspy--no-new-breed-members-needed)
  - [1.3 animal_combination.py — Add Cow-Calf Combinations](#13-animal_combinationpy--add-cow-calf-combinations)
  - [1.4 animal_grouping_scenarios.py — Add BEEF_COW_CALF_HERD Scenario](#14-animal_grouping_scenariospy--add-beef_cow_calf_herd-scenario)
  - [Step 1 Test Checkpoint](#step-1-test-checkpoint)
- [STEP 2 — Add Cow-Calf Constants and Configuration](#step-2--add-cow-calf-constants-and-configuration)
  - [2.1 animal_module_constants.py — Cow-Calf Biological Defaults](#21-animal_module_constantspy--cow-calf-biological-defaults)
  - [2.2 animal_config.py — Cow-Calf Configuration Parameters](#22-animal_configpy--cow-calf-configuration-parameters)
  - [2.3 animal_constants.py — Event Strings](#23-animal_constantspy--event-strings)
  - [Step 2 Test Checkpoint](#step-2-test-checkpoint)
- [STEP 3 — Build BeefCowCalfRequirementsCalculator](#step-3--build-beefcowcalfrequirementscalculator)
  - [3.1 File Structure](#31-file-structure)
  - [3.2 Maintenance Energy (NEm) — Use the Verified Inventory Equation Directly](#32-maintenance-energy-nem--use-the-verified-inventory-equation-directly)
  - [3.3 Lactation Energy and Protein (Suckling, Not Milking)](#33-lactation-energy-and-protein-suckling-not-milking)
  - [3.4 Gestation Energy and Protein](#34-gestation-energy-and-protein)
  - [3.5 Growth Energy (Replacement Heifers and Calves)](#35-growth-energy-replacement-heifers-and-calves)
  - [3.6 Calcium and Phosphorus](#36-calcium-and-phosphorus)
  - [3.7 Dry Matter Intake (DMI)](#37-dry-matter-intake-dmi)
  - [3.8 Validation Targets and Tolerances](#38-validation-targets-and-tolerances)
  - [3.9 Dairy and Feedlot Guards](#39-dairy-and-feedlot-guards)
  - [Step 3 Test Checkpoint](#step-3-test-checkpoint)
- [STEP 4 — Extend the Animal Class — Cow-Calf Lifecycle](#step-4--extend-the-animal-class--cow-calf-lifecycle)
  - [4.1 New Instance Attributes](#41-new-instance-attributes)
  - [4.2 Extending daily_reproduction_update()](#42-extending-daily_reproduction_update)
  - [4.3 Suckling Instead of Milking](#43-suckling-instead-of-milking)
  - [4.4 Weaning and Life-Stage Update](#44-weaning-and-life-stage-update)
  - [4.5 Daily Routine Dispatch](#45-daily-routine-dispatch)
  - [Step 4 Test Checkpoint](#step-4-test-checkpoint)
- [STEP 5 — Extend Reproduction — Beef Breeding Season](#step-5--extend-reproduction--beef-breeding-season)
  - [5.1 repro_protocol_enums.py — Add Beef Protocol](#51-repro_protocol_enumspy--add-beef-protocol)
  - [5.2 AnimalConfig — Wire the Protocol Selection](#52-animalconfig--wire-the-protocol-selection)
  - [5.3 Conception Probability Model](#53-conception-probability-model)
  - [Step 5 Test Checkpoint](#step-5-test-checkpoint)
- [STEP 6 — Wire Ration Management — Seasonal Forage Diets](#step-6--wire-ration-management--seasonal-forage-diets)
  - [6.1 RationManager — Seasonal Ration Registration](#61-rationmanager--seasonal-ration-registration)
  - [6.2 RationManager — Seasonal Ration Selection Method](#62-rationmanager--seasonal-ration-selection-method)
  - [6.3 RationOptimizer — Beef Constraint Set](#63-rationoptimizer--beef-constraint-set)
  - [Step 6 Test Checkpoint](#step-6-test-checkpoint)
- [STEP 7 — Extend Herd, Pen, and Reporter Infrastructure](#step-7--extend-herd-pen-and-reporter-infrastructure)
  - [7.1 HerdManager — Per-Class Cohort Lists (Lesson 1, applied from the start)](#71-herdmanager--per-class-cohort-lists-lesson-1-applied-from-the-start)
  - [7.2 HerdFactory — Cow-Calf Herd Initialization](#72-herdfactory--cow-calf-herd-initialization)
  - [7.3 Pen.py — Pasture/Paddock Considerations](#73-penpy--pasturepaddock-considerations)
  - [7.4 nutrients.py — Routing for Cow-Calf](#74-nutrientspy--routing-for-cow-calf)
  - [7.5 data_validator.py — Cow-Calf Config Validation](#75-data_validatorpy--cow-calf-config-validation)
  - [7.6 AnimalModuleReporter — Cow-Calf Performance Reporting](#76-animalmodulereporter--cow-calf-performance-reporting)
  - [Step 7 Test Checkpoint](#step-7-test-checkpoint)
- [STEP 8 — Wire Weaned Calf Hand-Off](#step-8--wire-weaned-calf-hand-off)
  - [8.1 Weaning Dispatch Logic](#81-weaning-dispatch-logic)
  - [8.2 HerdManager List Membership on Hand-Off](#82-herdmanager-list-membership-on-hand-off)
  - [Step 8 Test Checkpoint](#step-8-test-checkpoint)
- [STEP 9 — Documentation, Constants Audit, and Changelog](#step-9--documentation-constants-audit-and-changelog)
  - [Step 9 Test Checkpoint](#step-9-test-checkpoint)
- [STEP 10 — Integration Test — Multi-Year Herd Simulation](#step-10--integration-test--multi-year-herd-simulation)
  - [10.1 Test Configuration](#101-test-configuration)
  - [10.2 Assertions to Verify](#102-assertions-to-verify)
  - [Step 10 Test Checkpoint](#step-10-test-checkpoint)
- [STEP 11 — Validation Against NASEM/NRC Reference Benchmarks](#step-11--validation-against-nasemnrc-reference-benchmarks)
  - [Step 11 Test Checkpoint](#step-11-test-checkpoint)
- [Branching and PR Strategy — Applying Lesson 7 at the Process Level](#branching-and-pr-strategy--applying-lesson-7-at-the-process-level)
- [Appendix — Message to Feed Claude Code to Begin Step 1](#appendix--message-to-feed-claude-code-to-begin-step-1)

---

## Overview and How to Use This Document

This plan guides the implementation of the cow-calf breeding herd module inside the locally cloned RuFaS repository. It follows the exact format and discipline established by the Beef Feedlot Module plan: every step names the file to open, the class or method to touch, and the precise code to add. Steps are ordered so each one compiles and passes its own tests before the next begins.

Unlike the feedlot module — which was a one-way finishing process bolted onto the dairy lifecycle with simple additive guards — the cow-calf system is structurally closer to the existing dairy herd. It has real reproduction, a real gestation/calving cycle, real lactation (suckling instead of milking), and a perpetual multi-generational herd (cows are bred again after weaning their calf, year after year, until culled). This means more of the existing dairy infrastructure can be reused directly, but it also means the "add a guard and dispatch elsewhere" pattern that worked for feedlot is not sufficient on its own — reproduction, weaning, and culling logic need genuine beef-specific branches, not just bypasses.

The plan covers 9 major implementation steps, followed by an integration test step and a final validation step against NASEM/NRC reference benchmarks. Each step includes the files involved, the precise code changes, the rationale, and a test checkpoint to confirm correctness before moving on.

### Step Summary Table

| Step | Title | Files Touched | Effort |
|------|-------|---------------|--------|
| 1 | Extend enums — cow-calf animal types, breeds, combinations, grouping scenario | `animal_types.py`, `animal_enums.py`, `animal_combination.py`, `animal_grouping_scenarios.py` | 0.5 day |
| 2 | Add cow-calf constants and config parameters | `animal_module_constants.py`, `animal_config.py`, `animal_constants.py` | 1 day |
| 3 | Build `BeefCowCalfRequirementsCalculator` — maintenance, lactation, gestation, growth | `beef_cow_calf_requirements_calculator.py` (new), `nrc_requirements_calculator.py`, `nasem_requirements_calculator.py` | 3–4 days |
| 4 | Extend Animal class — cow-calf lifecycle, suckling, weaning, rebreeding | `animal.py` | 2–3 days |
| 5 | Extend reproduction module — beef breeding season + natural service | reproduction (existing module), `repro_protocol_enums.py`, `animal_config.py` | 2 days |
| 6 | Wire ration management — forage-based seasonal diets + creep feed | `ration_manager.py`, `ration_optimizer.py` | 1.5 days |
| 7 | Extend Herd, Pen, and Reporter infrastructure | `herd_manager.py`, `herd_factory.py`, `pen.py`, `animal_module_reporter.py`, `nutrients.py`, `data_validator.py` | 1.5 days |
| 8 | Wire weaned calf hand-off to existing CALF/stocker path | `herd_manager.py`, `animal.py`, `herd_factory.py` | 1 day |
| 9 | Documentation, constants audit, and changelog | `CLAUDE.md`, `docs/beef_module/`, `changelog.md` | 0.5 day |
| 10 | Integration test — multi-year cow-calf herd simulation | All files above | 1 day |
| 11 | Validation against NASEM/NRC reference benchmarks | `BeefCowCalfRequirementsCalculator` unit tests | 1 day |

---

## Lessons Learned from the Feedlot Module (PR #32) — Applied Up Front

The feedlot module went through two full rounds of review (human reviewer @jrobichaud plus CodeRabbitAI) before merge. Several of those findings were genuine bugs, not style nits, and they map directly onto risks in a cow-calf implementation, which is more complex (real reproduction state, real multi-cohort herd splitting, real seasonal config). Each lesson below is written as a rule for this plan, with a pointer to where it applies.

### Lesson 1 — Don't pool sub-types when reporting needs to be class-specific

> **What happened in PR #32:**
>
> `AnimalType.FEEDLOT_STEER` and `AnimalType.FEEDLOT_HEIFER` both pointed to the same `self.feedlot_animals` list in `HerdManager.animals_by_type`, so `phosphorus_concentration_by_animal_class` computed identical pooled values for both classes instead of class-specific concentrations. Caught by CodeRabbitAI in round 2, after the human reviewer had already approved round 1.

**Rule for this plan:** the cow-calf herd has at minimum four concurrent classes in HerdManager at any time — lactating cow with calf at side, dry/pregnant cow, replacement heifer, and suckling calf. Step 7 explicitly requires filtered list-comprehension mappings per `AnimalType`, never a single shared list reused across multiple `AnimalType` keys. This is written into the Step 7 test checklist as a named test case.

### Lesson 2 — Guard input config shape, not just truthiness

> **What happened in PR #32:**
>
> `HerdFactory` checked `if not feedlot_cfg: return []` but never verified `feedlot_cfg` was actually a dict before calling `.get()` on it. A non-dict truthy value (list, string) from `InputManager.get_data()` would raise `AttributeError` and abort herd initialization.

**Rule for this plan:** every new HerdFactory cow-calf initializer (Step 7) must use `if not isinstance(cfg, dict) or not cfg: return []` from the first draft, not as a follow-up fix. Cow-calf configs are more complex than feedlot configs (breeding season dates, calving distribution, weaning age, creep feed flags) so there are more opportunities for malformed nested config to slip through.

### Lesson 3 — Validate config invariants, including non-finite values

> **What happened in PR #32:**
>
> Two rounds of fixes were needed in `data_validator.py` and `ration_manager.py`: first to check that `entry_weight < slaughter_weight`, then to reject NaN/inf values that bypass numeric comparisons, then to reject negative ration percentages, then to make the validation atomic (state was being partially mutated before validation completed).

**Rule for this plan:** Step 7's `validate_cow_calf_config()` must, from the first draft, include `math.isfinite()` checks on every weight/age/day parameter, reject negative percentages anywhere ratios are used (creep feed %, weaning age distribution), and stage all RationManager/HerdFactory mutations in local variables before committing to class state — exactly the atomic-commit pattern already proven in `ration_manager.py`'s `set_ration_feeds()`.

### Lesson 4 — Test the actual routing, not just the output shape

> **What happened in PR #32:**
>
> `test_calculate_nutrition_requirements_routes_to_beef_calculator` originally only checked that the returned object was the right type. It could still pass even if dispatch silently fell through to the wrong calculator. Fixed by adding a `mocker.patch` spy and asserting it was actually called.

**Rule for this plan:** every dispatch test in Steps 3–8 (cow-calf animal routes to `BeefCowCalfRequirementsCalculator`, not `NASEMRequirementsCalculator` or `BeefNRCRequirementsCalculator`) must assert the spy was called, from the first draft of the test.

### Lesson 5 — Isolate shared class state between tests

> **What happened in PR #32:**
>
> Tests mutated `RationManager` class-level attributes (`feedlot_starter_ration` etc.) without restoring them afterward, creating order-dependent flakiness risk across the whole ration test suite, not just the feedlot tests.

**Rule for this plan:** any new test file that touches `RationManager` or `HerdManager` class-level state must define an autouse fixture that deep-copies state before each test and restores it after, from the first draft — not added reactively after CodeRabbit flags it.

### Lesson 6 — Don't change the original code's error semantics while fixing something else

> **What happened in PR #32:**
>
> A defensive fix for `animal.py`'s `birth_weight` changed `args.get("birth_weight")` to `args["birth_weight"]`, silently switching the failure mode from `TypeError` to `KeyError` when the field is missing for dairy/non-target animals — an unintended behavior change the human reviewer had to catch.

**Rule for this plan:** wherever cow-calf logic adds a guard in front of existing dairy code (e.g. `if self.animal_type.is_cow_calf: ... else: <original dairy line, byte-for-byte>`), the original line must be copied verbatim into the else-branch, never re-typed or "cleaned up" in the same change.

### Lesson 7 — Scope discipline: don't defer integration wiring as an afterthought

> **What happened after PR #32:**
>
> HerdFactory wiring, `nutrients.py` phosphorus routing, and `data_validator.py` rules were initially left out of the 8-step feedlot plan and had to be added in a follow-up round, because the original plan focused on the calculator and lifecycle but didn't explicitly schedule the "make it reachable from a real simulation run" work.

**Rule for this plan:** HerdFactory initialization, `data_validator` rules, and the weaned-calf hand-off to the existing CALF pipeline are first-class steps in this plan (Steps 7 and 8), not implied follow-up work. Step 10's integration test explicitly requires the herd to be creatable via the normal `HerdFactory.initialize_herd()` entry point, not via manual `Animal()` construction in a test fixture.

### Lesson 8 — Verify integration points exist before assuming they need to be built

> **What happened after PR #32:**
>
> Weather/temperature wiring was listed as a known limitation requiring new code, but a codebase trace showed `CurrentDayConditions.mean_air_temperature` already flows through to the feedlot calculator via the existing `animal.py` dispatch chain — zero new code was actually needed.

**Rule for this plan:** before writing any "new" wiring in Steps 4–8, Claude Code must first trace whether the dairy code path already does it (e.g. seasonal/environmental adjustments, herd statistics aggregation, culling event logging) and reuse it, rather than assuming beef-specific code is required. This is called out explicitly at the start of each relevant step below as a "Trace first" note.

---

## Architecture Overview

The design principle carried over from the feedlot module: existing dairy dispatch maps and conditionals gain cow-calf branches through standard `if is_cow_calf` / `if is_beef_cow` guards, keeping each function's cyclomatic complexity within the flake8 limit. Where the dairy logic is structurally identical (e.g. daily growth update, general life-stage dispatch pattern), the cow-calf branch reuses the same method shape rather than duplicating it.

```
AnimalType.BEEF_COW / BEEF_HEIFER_REPLACEMENT / BEEF_CALF / BEEF_BULL
 │
 │  is_beef_cow_calf = True
 ▼
Animal._initialize_beef_cow_calf_animal()
 │
 │  daily loop (existing daily_routines() — branches added, not replaced)
 ▼
Animal._beef_cow_calf_daily_routines(time)
 ├── daily_growth_update(time)          # REUSED from dairy, no change
 ├── daily_reproduction_update(time)    # EXTENDED: beef breeding season + natural service
 ├── daily_suckling_update(time)        # NEW: replaces daily_milking_update for beef cows
 └── animal_life_stage_update(time)
      └── _beef_cow_calf_life_stage_update()  # NEW: weaning, rebreeding, culling

Animal.calculate_nutrition_requirements()
 └── [is_beef_cow_calf guard]
      └── BeefCowCalfRequirementsCalculator.calculate_requirements()
           ├── _calculate_maintenance_energy()       NASEM-pattern Eq. (grazing-adjusted)
           ├── _calculate_lactation_energy()         NRC 2016 Ch.13 (suckling, not milking)
           ├── _calculate_gestation_energy()         NRC 2016 Ch.13 (reused gestation curve shape)
           ├── _calculate_growth_energy()            NRC 2016 Ch.12 (replacement heifers / calves)
           ├── _calculate_metabolizable_protein()    NRC 2016 Ch.6
           ├── _calculate_calcium() / _calculate_phosphorus()  NRC 2016 Table 19-3
           └── _calculate_dmi()                      NRC 2016 forage-based DMI equation

HerdManager.beef_cows / beef_replacement_heifers / beef_calves / beef_bulls
 ──► animals_by_type[BEEF_COW / BEEF_HEIFER_REPLACEMENT / BEEF_CALF / BEEF_BULL]
 ──► EACH mapped to its own filtered list — Lesson 1 applied

RationManager.get_beef_seasonal_ration(season, requirements)
 └── reads beef_breeding_season_ration / beef_gestation_ration / beef_lactation_ration dicts
 └── reads creep_feed_ration for nursing calves (optional, config-gated)

RationOptimizer._select_constraints(BEEF_COW_CALF)
 └── returns beef_cow_calf_constraints (high-forage minimum, no finishing NDF ceiling)

Animal._beef_weaning_event(time)
 └── hands weaned calf off into the EXISTING CALF → HEIFER_I pipeline (Step 8)
 └── OR into AnimalType.FEEDLOT_STEER / FEEDLOT_HEIFER for direct-to-feedlot operations (config flag)

AnimalModuleReporter.report_cow_calf_performance(animal, simulation_day)
 └── logs days_in_pregnancy, calf_weaning_weight, calving_interval, cow_body_condition_score
```

> **Trace-first note (Lesson 8):** before implementing `daily_suckling_update`, growth curve methods, and herd reproduction statistics aggregation, Claude Code must trace the existing dairy `daily_milking_update`, `growth.evaluate_body_weight_change`, and `HerdReproductionStatistics` to determine how much is directly reusable versus needing a beef-specific branch. The existing `GrowthInputs`/`GrowthOutputs` dataclasses and the growth module itself are strong reuse candidates since frame growth and conceptus weight calculations are not dairy-specific.

---

## STEP 1 — Extend the Enums

**Files:** `animal_types.py` | `animal_enums.py` | `animal_combination.py` | `animal_grouping_scenarios.py`

These four files form the identity layer of RuFaS, exactly as in the feedlot plan. Every conditional branch, every ration mapping, and every pen allocation pivots on the values declared here. No logic lives here — only declarations and the boolean convenience properties other code will guard on.

### 1.1 animal_types.py — Add Cow-Calf Animal Types

Open `RUFAS/biophysical/animal/data_types/animal_types.py`. The `FEEDLOT_STEER` and `FEEDLOT_HEIFER` members already exist from PR #32. Add four new members for the cow-calf system, and an `is_beef_cow_calf` property.

```python
class AnimalType(Enum):
    # EXISTING (do not change):
    CALF                   = 'Calf'
    HEIFER_I               = 'HeiferI'
    HEIFER_II              = 'HeiferII'
    HEIFER_III             = 'HeiferIII'
    DRY_COW                = 'DryCow'
    LAC_COW                = 'LacCow'
    FEEDLOT_STEER          = 'FeedlotSteer'
    FEEDLOT_HEIFER         = 'FeedlotHeifer'

    # ADD THESE FOUR NEW LINES:
    BEEF_CALF                  = 'BeefCalf'
    BEEF_HEIFER_REPLACEMENT    = 'BeefHeiferReplacement'
    BEEF_COW                   = 'BeefCow'
    BEEF_BULL                  = 'BeefBull'

    # EXISTING properties (do not change):
    @property
    def is_heifer(self) -> bool:
        return self in (AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III)

    @property
    def is_cow(self) -> bool:
        return self in (AnimalType.DRY_COW, AnimalType.LAC_COW)

    @property
    def is_feedlot(self) -> bool:
        return self in (AnimalType.FEEDLOT_STEER, AnimalType.FEEDLOT_HEIFER)

    # ADD THIS NEW PROPERTY:
    @property
    def is_beef_cow_calf(self) -> bool:
        """True if the animal belongs to the cow-calf breeding herd system."""
        return self in (
            AnimalType.BEEF_CALF,
            AnimalType.BEEF_HEIFER_REPLACEMENT,
            AnimalType.BEEF_COW,
            AnimalType.BEEF_BULL,
        )
```

> **Why four types instead of reusing CALF/HEIFER/COW directly?**
>
> The dairy `CALF`/`HEIFER`/`COW` types carry dairy-specific assumptions throughout the codebase (milk production, dairy reproduction protocols, dairy growth curves keyed to Holstein/Jersey). Reusing them for beef would require auditing every dairy-only branch for a beef exception, which is exactly the kind of broad, high-risk change the 8-step feedlot plan avoided by introducing `FEEDLOT_STEER`/`FEEDLOT_HEIFER` as new types instead of overloading existing ones. The same reasoning applies here, with `BEEF_BULL` as a new addition since neither dairy nor feedlot needed a breeding bull type.

### 1.2 animal_enums.py — No new Breed members needed

The `Breed` enum already gained `AN`/`HE`/`SI`/`CH`/`LM`/`BR`/`XB` in PR #32 for feedlot. These are the same breeds typically run in cow-calf operations, so no new Breed members are required. Confirm this assumption against the breed list in `Beef NRC Management.docx` during Step 1's test checkpoint — if a cow-calf-specific breed is needed (e.g. a maternal composite breed not in the feedlot list), add it here following the same pattern.

The `Sex` enum already has `MALE`, `FEMALE`, and `STEER` from PR #32. No changes needed — bulls use `MALE`, cows and replacement heifers use `FEMALE`.

### 1.3 animal_combination.py — Add Cow-Calf Combinations

```python
class AnimalCombination(Enum):
    # EXISTING (do not change):
    CALF                    = 'calf'
    GROWING                 = 'growing'
    CLOSE_UP                = 'close_up'
    LAC_COW                 = 'lac_cow'
    GROWING_AND_CLOSE_UP    = 'growing and close_up'
    FEEDLOT_FINISHING       = 'feedlot_finishing'

    # ADD:
    BEEF_COW_CALF_PAIR   = 'beef_cow_calf_pair'   # lactating cow + calf at side, same pen
    BEEF_GESTATING       = 'beef_gestating'        # dry, pregnant cow — no calf at side
    BEEF_REPLACEMENT     = 'beef_replacement'      # weaned heifer being developed for breeding
    BEEF_BULL_BATTERY    = 'beef_bull_battery'     # breeding bulls, managed separately most of the year
```

Four combinations instead of one reflects how cow-calf herds are actually managed: a bull battery is penned separately outside the breeding season; gestating dry cows are fed a maintenance-level winter ration distinct from lactating cow-calf pairs on pasture; and replacement heifers are developed on their own targeted-gain diet, exactly as described in the NRC reference material (target weight 55-65% of mature weight by first breeding, 80% of mature weight by first calving).

### 1.4 animal_grouping_scenarios.py — Add BEEF_COW_CALF_HERD Scenario

```python
class AnimalGroupingScenario(Enum):
    # EXISTING scenarios (do not change):
    CALF__GROWING__CLOSE_UP__LACCOW    = { ... }
    CALF__GROWING_AND_CLOSE_UP__LACCOW = { ... }
    FEEDLOT_ONLY                        = { ... }

    # ADD:
    BEEF_COW_CALF_HERD = {
        AnimalCombination.BEEF_COW_CALF_PAIR: [
            AnimalType.BEEF_COW,
            AnimalType.BEEF_CALF,
        ],
        AnimalCombination.BEEF_GESTATING: [
            AnimalType.BEEF_COW,
        ],
        AnimalCombination.BEEF_REPLACEMENT: [
            AnimalType.BEEF_HEIFER_REPLACEMENT,
        ],
        AnimalCombination.BEEF_BULL_BATTERY: [
            AnimalType.BEEF_BULL,
        ],
    }
```

> **Note on `AnimalType.BEEF_COW` appearing in two combinations:**
>
> Unlike the feedlot scenario where each `AnimalType` maps to exactly one `AnimalCombination`, `BEEF_COW` legitimately appears under both `BEEF_COW_CALF_PAIR` and `BEEF_GESTATING` because the same cow moves between these two states across the production year (lactating-with-calf after calving, then dry-and-pregnant after weaning). The `AnimalGroupingScenario._animal_combination_by_animal_type` lookup built in `__init__` takes the LAST mapping found for a given `AnimalType` when duplicates exist. Step 4 must NOT rely on this lookup table alone to decide a cow's current pen — it must use the cow's actual `is_lactating`/`is_pregnant` state at runtime, with the static scenario table only used for initial herd setup validation. Write this as an explicit unit test: confirm that pen assignment after the first weaning event correctly reflects the cow's live reproduction state, not a stale scenario-table lookup.

### Step 1 Test Checkpoint

> **Run this before proceeding to Step 2:**
>
> ```
> python -c "from RUFAS.biophysical.animal.data_types.animal_types import AnimalType; print(AnimalType.BEEF_COW.is_beef_cow_calf)"
> ```
> → expected output: `True`
>
> ```
> python -c "from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination; print(AnimalCombination.BEEF_COW_CALF_PAIR)"
> ```
> → expected output: `AnimalCombination.BEEF_COW_CALF_PAIR`
>
> Write and run `test_beef_cow_calf_enums.py` FIRST (TDD), confirm it fails before the enum changes exist, then confirm it passes after. Also re-run the full `test_data_types/` regression suite — a single dairy or feedlot enum test failure means something was broken.

---

## STEP 2 — Add Cow-Calf Constants and Configuration

**Files:** `animal_module_constants.py` | `animal_config.py` | `animal_constants.py`

Constants and configuration set the biological and management defaults driving the new calculator and life-stage transitions. This step is larger than the feedlot equivalent because cow-calf management has more moving parts: a breeding season window, a calving distribution, a weaning age/weight target, and an optional creep-feeding flag.

### 2.1 animal_module_constants.py — Cow-Calf Biological Defaults

Open `RUFAS/biophysical/animal/animal_module_constants.py`. Add cow-calf constants at the bottom of the `AnimalModuleConstants` class, clearly separated from dairy and feedlot constants with a comment header, following the same separation pattern PR #32 used for feedlot constants.

```python
class AnimalModuleConstants:
    # ... existing dairy constants ...
    # ... existing feedlot constants (PR #32) ...

    # ===== COW-CALF CONSTANTS (NRC 2016 Beef Ch.13, Beef NRC Management reference) =====

    # Reproduction / calving
    BEEF_GESTATION_LENGTH_DAYS: int = 283           # NRC 2016 average beef gestation
    BEEF_CALF_CROP_WEANED_RATE: float = 0.855       # USDA average calf crop weaned per cow exposed
    BEEF_STILLBIRTH_RATE: float = 0.035             # 96.5% born live (USDA, 2009a)
    BEEF_PREWEANING_SURVIVAL_RATE: float = 0.968    # 96.8% of live calves survive to weaning

    # Weaning
    BEEF_DEFAULT_WEANING_AGE_DAYS: int = 207             # USDA average weaning age
    BEEF_DEFAULT_WEANING_WEIGHT_KG: float = 240.0        # USDA average weaning weight
    BEEF_PREWEANING_ADG_KG_D: float = 1.0                # NRC reference preweaning calf gain
    BEEF_CALF_BIRTH_WEIGHT_KG: float = 35.0              # NRC reference average birth weight

    # Cow body weight and condition
    BEEF_DEFAULT_MATURE_COW_WEIGHT_KG: float = 520.0      # USDA average mature cow weight at weaning
    BEEF_COW_FORAGE_DMI_PCT_BW: float = 0.0225            # 2.25% of BW in forage DM/d (moderate condition)
    BEEF_PREWEANING_CALF_DMI_PCT_BW: float = 0.0125       # 1.25% of BW, preweaning forage intake

    # Replacement heifer development targets (NRC reference)
    BEEF_HEIFER_TARGET_BREEDING_PCT_MATURE: float = 0.60   # 55-65% of mature weight at first breeding
    BEEF_HEIFER_TARGET_CALVING_PCT_MATURE: float = 0.80    # ~80% of mature weight at first calving
    BEEF_HEIFER_TARGET_ADG_KG_D: float = 0.675             # midpoint of 0.45-0.90 kg/d target range
    BEEF_HEIFER_FIRST_CALVING_AGE_DAYS: int = 690          # 22-24 months, midpoint ~23 mo

    # Culling
    BEEF_ANNUAL_CULL_RATE: float = 0.175             # midpoint of 15-20% national average
    BEEF_COW_MAX_AGE_DAYS: int = 5475                # 15 years, conservative longevity ceiling

    # Breeding season (default; overridable via AnimalConfig)
    BEEF_DEFAULT_BREEDING_SEASON_LENGTH_DAYS: int = 63   # standard 9-week (63-day) breeding season
```

> **Source discipline (continuing Lesson 3 / coding guideline):**
>
> Every numeric constant above has a one-line comment citing its source (NRC 2016 chapter/table or USDA survey year) — this mirrors the existing feedlot constants and is required by the repository's "no magic numbers, constants must live in dedicated `*_constants.py` modules per domain" guideline that CodeRabbit enforced twice during the feedlot PR review.

### 2.2 animal_config.py — Cow-Calf Configuration Parameters

Open `RUFAS/biophysical/animal/animal_config.py`. Add a cow-calf section mirroring the structure of the existing heifer/cow reproduction parameters already in this file (`heifer_breed_start_day`, `calving_interval`, `dry_off_day_of_pregnancy`, etc. — these are the dairy patterns to follow stylistically).

```python
class AnimalConfig:
    # ... existing dairy attributes ...
    # ... existing feedlot attributes (PR #32): feedlot_entry_weight, feedlot_slaughter_weight,
    #     feedlot_max_days_on_feed, feedlot_mud_condition ...

    # ADD cow-calf attributes:
    beef_breeding_season_start_day: int    # day-of-year breeding season opens (config-driven, spring/fall)
    beef_breeding_season_length: int       # length in days, default BEEF_DEFAULT_BREEDING_SEASON_LENGTH_DAYS
    beef_weaning_age_days: int             # target weaning age, default BEEF_DEFAULT_WEANING_AGE_DAYS
    beef_weaning_weight_kg: float          # target weaning weight (whichever threshold hits first), nullable
    beef_creep_feeding_enabled: bool       # whether nursing calves get supplemental creep feed
    beef_post_weaning_destination: str     # 'replacement_heifer' | 'stocker' | 'direct_to_feedlot' | 'sell'
    beef_mature_cow_weight_kg: float       # default BEEF_DEFAULT_MATURE_COW_WEIGHT_KG, overridable per breed
    beef_natural_service_bull_ratio: int   # cows per bull, typical range 20-30:1, used for breeding success rate
    beef_cow_cull_rate_annual: float       # default BEEF_ANNUAL_CULL_RATE, overridable
```

Each new attribute needs a one-line docstring entry in the `AnimalConfig` class docstring's `Attributes` section, following the exact style of the existing dairy attributes documented there (see the existing `wean_day`, `calving_interval` entries for the pattern to copy).

### 2.3 animal_constants.py — Event Strings

Open `RUFAS/biophysical/animal/animal_constants.py` (the event-string constants file, distinct from `animal_module_constants.py`'s biological constants). Add cow-calf event strings following the existing pattern used for feedlot's `SLAUGHTER_WEIGHT_REACHED` / `MAX_DAYS_ON_FEED_REACHED`.

```python
# ADD:
CALF_WEANED                                 = 'calf_weaned'
COW_REBRED                                  = 'cow_rebred'
COW_OPEN_AT_PREGNANCY_CHECK                 = 'cow_open_at_pregnancy_check'  # failed to conceive, cull candidate
COW_CULLED_AGE                              = 'cow_culled_age'
COW_CULLED_OPEN                             = 'cow_culled_open'
REPLACEMENT_HEIFER_REACHED_BREEDING_WEIGHT  = 'replacement_heifer_reached_breeding_weight'
REPLACEMENT_HEIFER_PROMOTED_TO_COW          = 'replacement_heifer_promoted_to_cow'
STILLBIRTH                                  = 'stillbirth'
```

### Step 2 Test Checkpoint

> **Run before proceeding to Step 3:**
>
> Write `test_beef_cow_calf_constants.py` FIRST (TDD) asserting each new `AnimalModuleConstants` value matches its documented NRC/USDA source value exactly. Write `test_beef_cow_calf_config.py` asserting `AnimalConfig` accepts and stores each new parameter from a sample input dict. Run `black` + `mypy` + `flake8` on all three touched files before moving to Step 3.

---

## STEP 3 — Build BeefCowCalfRequirementsCalculator

**Files:** `beef_cow_calf_requirements_calculator.py` (new) | `nrc_requirements_calculator.py` | `nasem_requirements_calculator.py`

This is the most complex step, as it was for the feedlot module. Unlike feedlot (a single growth-and-finish calculation with no reproductive component), cow-calf requirements must branch on four distinct physiological states a beef cow moves through across the year: open and dry, pregnant and dry, pregnant and lactating (overlap period after rebreeding while still nursing), and lactating-only post-weaning-prep. Replacement heifers and calves need their own growth-only branch. This mirrors the structure already proven in `nasem_requirements_calculator.py` for dairy — gestation and lactation energy/protein/mineral requirements are summed, not mutually exclusive, exactly like the dairy calculator already does for pregnant lactating cows.

> **Trace-first note (Lesson 8):**
>
> Before writing any new equation, open `nasem_requirements_calculator.py` and read `_calculate_maintenance_energy_requirements`, `_calculate_growth_energy_requirements`, and `_calculate_metabolizable_protein_requirement` in full. These already implement gestation energy via gravid uterine weight, growth energy via frame gain, and protein requirements that sum gestation + growth + maintenance + lactation terms — the exact shape cow-calf needs. The cow-calf calculator should reuse the same gravid uterine weight equation structure (`calf_birth_weight`, `gravid_uterine_weight`, `uterine_weight`) since that NASEM 2021 equation is species-general, not dairy-breed-specific, only requiring `mature_body_weight` and `day_of_pregnancy` as inputs — both of which beef cows have. Where NRC 2016 (Beef) Chapter 13 gives a beef-specific coefficient that differs from the NASEM 2021 dairy coefficient, use the NRC 2016 beef coefficient and cite it; where the dairy equation's mathematical form is species-general, reuse the dairy calculator's private method directly via composition rather than re-deriving it.

### 3.1 File Structure

Create `RUFAS/biophysical/animal/nutrients/beef_cow_calf_requirements_calculator.py`. Follow the exact class structure of `beef_nrc_requirements_calculator.py` (PR #32): a stateless class with `@classmethod` methods, a single public `calculate_requirements()` entry point, and private `_calculate_*` methods for each nutrient component, each returning intermediate values needed by later methods (mirroring how `BeefNRCRequirementsCalculator` threads `SBW`, `EQSBW`, and `EBG` through its method chain).

### 3.2 Maintenance Energy (NEm) — Use the Verified Inventory Equation Directly

> **Source location:** `NRC2016_Beef_Requirements_Calculator_Inventory_Final.xlsx`, Sheet `"1_Maintenance_Energy"`
>
> This sheet already contains the exact, verbatim NRC 2016 equation (Ch.11/Ch.19 Eq.19-1 to 19-18) including the `L` (lactation) and `COMP` (body condition) terms cow-calf needs — these are NOT present in the feedlot version (PR #32 used `L=1`, `COMP=1` implicitly since feedlot animals are neither lactating nor body-condition-scored in that plan). Read this sheet directly before writing any code; do not approximate.

The full equation, exactly as verified in the inventory, is:

```
SBW  = BW × 0.96
a1   = 0.077
a2   = 0.0007 × (20 - Tp)    # Tp = previous temperature (°C); a2 must be ≥ 0
COMP = 0.8 + (BCS - 1) × 0.05   # BCS = body condition score, 1-9 scale
SEX  = 1.15 for bulls; 1.0 for all others

NEm  = SBW^0.75 × (a1 × BE × L × COMP × SEX + a2)
         # BE = breed factor, Table 19-1 (Sheet 5)
         # L  = lactation factor, Table 19-1 (Sheet 5) — 1.0 for feedlot, breed-specific (1.0-1.2) for cow-calf
```

Cold and heat stress are also fully specified in Sheet 1 (Section C) with a complete insulation model (external insulation EI from wind speed/hair depth/mud coverage, tissue insulation TI from BCS, lower critical temperature LCT, and a heat-stress THI-based term) — this is more complete than the simplified a2-only cold-stress term PR #32 used for feedlot. Cow-calf cattle on pasture are more weather-exposed than feedlot cattle at a bunk, so implementing the FULL Sheet 1 Section C model (EI/TI/LCT/MEcs/NEcs and NEhs), not just the simplified feedlot a2 term, is warranted for this module. Mud DMI adjustment (MUD1) from Sheet 1 also applies directly — reuse the `Pen.mud_condition` concept introduced in PR #32 (Step 7.3 of this plan repurposes/extends it for pasture).

> **Correction to an earlier draft of this plan:**
>
> An earlier draft of this section proposed inventing a new "grazing activity multiplier" constant. This is unnecessary and must NOT be implemented — the verified NRC 2016 equation in Sheet 1 has no separate grazing/activity term; the `L` and `COMP` factors already account for the physiological differences between feedlot and cow-calf cattle. Do not add an extra multiplier on top of the verified equation.

### 3.3 Lactation Energy and Protein (Suckling, Not Milking)

> **Source location:** `NRC2016_Beef_Requirements_Calculator_Inventory_Final.xlsx`, Sheet `"8_Pregnancy_Lactation"` Section B (Ch.19 Eq.19-19 to 19-36) and Sheet `"5_Table19-1_Breeds"` columns Peak Milk Yield, Milk Fat, Milk Protein, Milk SNF.
>
> This sheet is explicitly labeled "Phase 2 (Cow-Calf)" in the inventory and contains the verbatim NRC 2016 Wood lactation curve model with exact equations — no estimation method needs to be invented. Read this sheet and Sheet 5's breed columns directly before writing any code.

This is structurally the biggest departure from both dairy and feedlot. Dairy cows are milked and their lactation energy requirement is driven by measured milk yield (`MilkProductionOutputs`). Beef cows are not milked — NRC 2016 models beef cow milk production via a Wood lactation curve parameterized by breed peak yield and milk composition, both already tabulated per breed in Sheet 5 (e.g. Angus: peak yield 8 kg/d, milk fat 4%, protein 3.8%, SNF 8.3%; Braunvieh: peak yield 12 kg/d, lactation factor L=1.0 vs Angus L=1.2 — these per-breed differences are exactly why Step 1 kept `Breed` as a real enum dimension).

```python
# Wood lactation curve — NRC 2016 Ch.19 Eq.19-19 to 19-36, Sheet 8 Section B, verbatim:
n     = DIM / 7                               # week in lactation; DIM = days in milk (this plan's lactation_day)
k     = 1 / T                                 # T = week of peak yield, default 8
aPKYD = (0.125 × RMY + 0.375) × PKYD         # RMY = relative milk yield, 1.0 = average; PKYD = Table 19-1 peak yield
a     = 1 / (aPKYD × k × e^1)
Yn    = (n / (a × e^(k×n))) × AgeFactor      # AgeFactor: 0.85 for first-calf heifers, 1.0 for mature cows

# Energy content of milk — Sheet 8, verbatim:
E     = 0.092 × MkFat + 0.049 × MkSNF - 0.0569   # MkFat, MkSNF from Table 19-1 (Sheet 5), breed-specific

# Lactation energy requirement:
NEl   = Yn × E                                # Mcal/d

# MP for lactation — Sheet 8, verbatim:
YProtn = Yn × MkProt / 100                   # MkProt = milk protein %, Table 19-1 (Sheet 5)
MPl    = (YProtn / 0.65) × 1000              # g/d, 0.65 = lactation MP efficiency
```

Implement this as its own private method (`_calculate_beef_milk_yield_and_lactation_requirement`) taking `DIM`, `breed`, and `parity` (for `AgeFactor`) as inputs, returning `Yn`, `NEl`, and `MPl` together since all three are computed from the same curve evaluation. The `AgeFactor` distinction (0.85 first-calf heifer vs 1.0 mature) maps directly onto this plan's `times_calved` attribute from Step 4.1 — `times_calved == 1` uses 0.85, `times_calved >= 2` uses 1.0.

### 3.4 Gestation Energy and Protein

> **Source location:** `NRC2016_Beef_Requirements_Calculator_Inventory_Final.xlsx`, Sheet `"8_Pregnancy_Lactation"` Section A (Ch.19 Eq.19-37 to 19-42).
>
> Use these verified beef-specific equations directly rather than reusing the NASEM 2021 dairy gravid uterine weight equation by composition, as an earlier draft of this plan proposed. The inventory's beef-specific pregnancy equations are already verified against the Ch.19 source and use calf birth weight (CBW) from Table 19-1 by breed, which the dairy calculator does not have access to in the same form.

```python
# NRC 2016 Ch.19 Eq.19-37 to 19-42, Sheet 8 Section A, verbatim.
# CBW = calf birth weight (kg), Table 19-1 by breed (Sheet 5). DP = days pregnant (0-283).

NEy = CBW × (0.05855 - 0.0000996×DP) × exp(0.0323×DP - 0.0000275×DP²) / 1000    # Mcal/d
MEy = NEy / 0.13                                                                    # ME requirement for pregnancy
FFP = MEy / ME_diet                                                                 # feed DM for pregnancy

Ypn = CBW × (0.001669 - 0.00000211×DP) × exp(0.0278×DP - 0.0000176×DP²) × 6.25  # net protein, g/d
MPy = Ypn / 0.65                                                                    # MP requirement for pregnancy

CW  = CBW × 0.01828 × exp(0.02×DP - 0.0000143×DP²)                               # gravid uterus weight, kg
  # CW feeds back into EQSBW = (SBW - CW) × (SRW / MSBW), Sheet 1 Section A — confirm this exact EQSBW
  # formula (which subtracts conceptus weight, unlike the simpler SBW-only EQSBW PR #32 used for feedlot,
  # where CW is always 0) is used consistently everywhere EQSBW appears in this calculator.
```

CBW (calf birth weight) is breed-specific and already tabulated in Table 19-1 (Sheet 5) — do not use the flat `AnimalModuleConstants.BEEF_CALF_BIRTH_WEIGHT_KG = 35.0` constant from Step 2.1 as the actual input to these equations; that constant is a herd-level default/fallback only. The calculator's CBW input should come from Sheet 5's per-breed Calf Birth Weight column, exactly as `BE` (breed factor) and `L` (lactation factor) already do for the same animal.

### 3.5 Growth Energy (Replacement Heifers and Calves)

> **Source location:** `NRC2016_Beef_Requirements_Calculator_Inventory_Final.xlsx`, Sheet `"2_Growth_Energy"` (Ch.12 & Ch.19 Eq.19-43 to 19-52, including the Box 12-1 worked example) and Sheet `"2_Protein_Ch6_Exact"` (Ch.6 protein/amino acids, including the updated MCP equations from Galyean & Tedeschi 2014).
>
> These are the SAME sheets PR #32 already used and validated for feedlot growth (Box 12-1: MP = 691 g/d). `BEEF_HEIFER_REPLACEMENT` and `BEEF_CALF` need a growth-only energy and protein calculation with no lactation or gestation term (until the replacement heifer herself becomes pregnant and transitions to `BEEF_COW` per Step 4). Reuse `BeefNRCRequirementsCalculator`'s existing growth methods directly via composition — they already implement Sheet 2's equations correctly — rather than re-deriving them. Only the target ADG input differs: replacement heifers target `BEEF_HEIFER_TARGET_ADG_KG_D` (0.45-0.90 kg/d range, Step 2.1) rather than a feedlot finishing ADG.

### 3.6 Calcium and Phosphorus

> **Source location:** Sheet `"6_Minerals_Table19-3_19-4"` and Sheet `"13_Minerals_Ch7_Full"` (the latter explicitly includes "critical DDGS/S toxicity data and receiving mineral adjustments" and full Ch.7 Ca/P/S/Co/Cu data, a superset of what PR #32 used for feedlot's Table 19-3-only mineral calculation).
>
> Reuse `BeefNRCRequirementsCalculator._calculate_calcium` / `_calculate_phosphorus` directly via composition for the maintenance and growth terms (already validated in PR #32), then ADD the pregnancy and lactation mineral terms from Sheet 13's full Ch.7 data, since feedlot animals never gestate or lactate and so PR #32's implementation has no pregnancy/lactation mineral terms to reuse — these must be newly implemented from Sheet 13 directly, not assumed to already exist somewhere in the codebase.

### 3.7 Dry Matter Intake (DMI)

> **Source location:** `NRC2016_Beef_Requirements_Calculator_Inventory_Final.xlsx`, Sheet `"3_DMI_Ch10_Exact"` Section C ("BEEF COW DMI", Ch.10 Eq.10-5 + Table 10-1) and Section D ("FORA_DMI" grazing adjustment).
>
> This sheet contains a verified exact equation (Eq.10-5) plus an alternative simple guideline table (Table 10-1) and a forage-mass-based grazing adjustment (FORA_DMI), letting the implementation match whichever input data is available (precise diet energy concentration vs. simple forage-quality category vs. measured pasture biomass). This replaces the single flat 2.25%-of-BW approximation an earlier draft of this plan proposed.

```python
# PRIMARY METHOD — Eq.10-5, Sheet 3 Section C, verbatim. Use when diet NEm concentration is known:
NEm_intake = BW^0.75 × (0.04997×NEm_diet² + 0.04631)   # nonpregnant/pregnant cows
  # + 0.03840 × BW^0.75  added ONLY for nonpregnant cows (intercept adjustment)

DMI = NEm_intake / NEm_diet + 0.2 × Yn      # + 0.2×Yn ONLY for lactating cows; Yn from Section 3.3's Wood curve
  # IF NEm_diet ≤ 0.95: use divisor = 0.95 instead
  # NOTE: BW here is NON-PREGNANT body weight, used even for pregnant/lactating cows — this is an explicit
  # instruction in the inventory and is easy to get wrong if body_weight (which includes conceptus weight
  # for a pregnant cow) is passed directly without first subtracting CW from Section 3.4.

# FALLBACK METHOD — Table 10-1, Sheet 3 Section C, when diet NEm concentration is not modeled (e.g. simple
# pasture-quality-category config rather than full diet formulation):
#   Low quality forage (<52% TDN):   dry cow 1.8% BW | lactating 2.2% BW
#   Average quality (52-59% TDN):    dry cow 2.2% BW | lactating 2.5% BW
#   High quality forage (>59% TDN):  dry cow 2.5% BW | lactating 2.7% BW

# GRAZING ADJUSTMENT — Section D FORA_DMI, applied on top of either method above when forage mass is known:
# IF available forage mass FM ≥ 1150 kg/ha (or FORA ≥ 4× predicted DMI in g/kg BW): no adjustment.
# ELSE: RelDMI(%) = 0.17×FM - 0.000074×FM² + 2.4 ; DMI_adjusted = DMI_predicted × RelDMI/100
```

Implement both the Eq.10-5 precise method and the Table 10-1 guideline method, selected by which inputs `AnimalConfig` provides (a config flag, e.g. `beef_dmi_method: 'precise' | 'guideline'`, defaulting to `'guideline'` since most cow-calf operations do not formulate diets to the same NEm precision as feedlot). The FORA_DMI grazing adjustment is optional and only applies if pasture forage mass data is configured (ties into the `Pen.forage_quality_factor` concept from Step 7.3 — confirm during Step 7 whether forage mass should be a `Pen` attribute feeding into this adjustment, rather than inventing a separate input path).

Suckling calf DMI uses the existing Sheet 3 Section A calf equation pattern combined with the suckling milk-energy credit from Section 3.3 — read Sheet 3 Section A's calf NEm-intake equation directly rather than approximating a flat percent-of-body-weight figure, and confirm against the trace-first note below before writing a new intake-separation method.

> **Trace-first note: reuse `calf_ration_manager.py`'s separation pattern.**
>
> `calf_ration_manager.py` already separates `WHOLE_MILK_ID` / `MILK_REPLACER_ID` intake from `STARTER_ID` (solid feed) intake for dairy calves, and calculates requirements based on combined nutritional intake. A nursing beef calf is structurally identical — milk (from the dam, not metered/fed) plus pasture forage. Before writing a new intake-separation method, check whether `CalfRationManager.calc_requirements` can be extended with a suckling-milk-estimate parameter rather than building a fully separate path. If reuse is impractical because `CalfRationManager` assumes a managed (bucket-fed) milk source, document why in Step 9 and proceed with a new method, keeping the same method signature shape for consistency.

### 3.8 Validation Targets and Tolerances

> **Source location:** Sheet `"7_Validation_Examples"` ("Use these values as `pytest.approx()` targets for unit tests on `BeefNRCRequirementsCalculator`. Box 12-1 values are exact — use ±0% tolerance. NRC Ch.20 table values allow ±3% tolerance.") This sheet's stated tolerances are the AUTHORITATIVE source — the table below adapts them for the new cow-calf-specific components (gestation, lactation) that Sheet 7 does not cover, since Sheet 7 was built for feedlot validation in PR #32.

Also relevant: Sheet `"12_Receiving_Stress_Ch15"` (Table 15-1/15-2 exact values for stressed calves) applies directly to a freshly weaned `BEEF_CALF` transitioning through Step 8's hand-off, exactly the way it already applied to feedlot receiving cattle in PR #32 — reuse the existing receiving-stress DMI adjustment rather than treating weaning stress as a new, separate concept.

| Component | Inventory Sheet | Tolerance |
|-----------|-----------------|-----------|
| Maintenance NEm (incl. L, COMP, cold/heat stress) | `1_Maintenance_Energy` | ±3% (Sheet 7 standard) |
| Gestation energy/protein (NEy, MPy, CW) | `8_Pregnancy_Lactation` Section A | ±3% |
| Lactation (Wood curve Yn, NEl, MPl) | `8_Pregnancy_Lactation` Section B | ±5% (curve has more parameters than gestation — wider band) |
| Growth energy (replacement heifers) | `2_Growth_Energy` (reused from PR #32) | ±3% |
| Metabolizable Protein, all components summed | `2_Protein_Ch6_Exact` + `8_Pregnancy_Lactation` | ±5% |
| Calcium / Phosphorus (incl. pregnancy/lactation terms) | `6_Minerals_Table19-3_19-4`, `13_Minerals_Ch7_Full` | ±5% |
| DMI — precise method (Eq.10-5) | `3_DMI_Ch10_Exact` Section C | ±3% |
| DMI — guideline method (Table 10-1) | `3_DMI_Ch10_Exact` Section C | ±10% (guideline ranges are inherently wider than an exact equation) |

Where Sheet 7 does not already contain a worked numeric example for a given component (gestation and lactation are new to this module, unlike growth/maintenance which Sheet 7 already validates from PR #32), construct the test input from Sheet 8's equation parameters directly and verify the calculation by hand against the verbatim equation before treating it as a fixed expected value in a unit test — do not invent a target number without first computing it independently from the verified equation.

### 3.9 Dairy and Feedlot Guards

Following PR #32's pattern exactly: add guards to `NRCRequirementsCalculator.calculate_requirements()`, `NASEMRequirementsCalculator.calculate_requirements()`, and `BeefNRCRequirementsCalculator.calculate_requirements()` so each raises `NotImplementedError` if called with a cow-calf animal type. This was a one-line addition per calculator in PR #32 and should be just as small here.

### Step 3 Test Checkpoint

> **Required before proceeding to Step 4:**
>
> Write ALL validation tests from Section 3.8 FIRST, including the milk-yield curve unit tests from Section 3.3, before implementing any equation (TDD, no exceptions — Lesson from the testing skill's Golden Rule). Each private method gets its own unit test with a known reference input/output pair before integration into `calculate_requirements()`. Run `black` + `mypy` + `flake8` on the new file. Confirm the dairy and feedlot guards raise `NotImplementedError` with a passing test for each of the three existing calculators.

---

## STEP 4 — Extend the Animal Class — Cow-Calf Lifecycle

**Files:** `animal.py`

Unlike feedlot — which added a slim parallel daily-routine path because feedlot animals have no reproduction or lactation — cow-calf animals DO have reproduction and lactation, just beef-specific versions of both. This means Step 4 extends the EXISTING `daily_routines()` dispatch rather than bypassing it, reusing `daily_growth_update()` unchanged and branching `daily_reproduction_update()` and `daily_milking_update()` (renamed conceptually to suckling for beef) on `animal_type.is_beef_cow_calf`.

### 4.1 New Instance Attributes

Set in a new `_initialize_beef_cow_calf_animal()` method, called from `Animal.__init__` alongside the existing `_initialize_feedlot_animal()` call (both guarded by their respective `is_feedlot` / `is_beef_cow_calf` checks, so only one ever runs for a given animal).

| Attribute | Type | Description |
|-----------|------|-------------|
| `days_in_breeding_season` | `int \| None` | Days since breeding season opened for this cow; None if not yet bred this cycle |
| `calf_at_side` | `Animal \| None` | Reference to the nursing calf currently with this cow, None if weaned/dry |
| `dam` | `Animal \| None` | Reference to a BEEF_CALF's mother, used for suckling milk credit |
| `lactation_day` | `int` | Days in milk for a beef cow, drives the milk-yield curve (Section 3.3) |
| `weaning_day` | `int \| None` | Simulation day this calf was or will be weaned; set at birth from AnimalConfig |
| `body_condition_score` | `float` | 1-9 scale, NRC 2016 standard; influences rebreeding success probability |
| `times_calved` | `int` | Parity counter for a beef cow, drives heifer→cow transition and cull-by-age logic |
| `is_open` | `bool` | True if a cow failed to conceive during the most recent breeding season |

### 4.2 Extending daily_reproduction_update()

The existing dairy `daily_reproduction_update()` handles AI-based, protocol-driven dairy reproduction (`HeiferReproductionProtocol`, `CowReproductionProtocol` from `repro_protocol_enums.py`). Beef cow-calf reproduction is fundamentally seasonal and natural-service-based — a defined breeding season window, not a continuous AI calendar. Add a beef-specific branch at the top of the method, following Lesson 6's rule of copying the existing dairy logic into the else-branch byte-for-byte rather than rewriting it.

```python
def daily_reproduction_update(
    self, time: RufasTime
) -> tuple[NewBornCalfValuesTypedDict | None, HerdReproductionStatistics]:
    """
    ... (existing docstring, extend with beef branch note) ...
    """
    if self.animal_type.is_beef_cow_calf:
        return self._beef_daily_reproduction_update(time)
    # vvv EXISTING DAIRY LOGIC BELOW — COPIED VERBATIM, NOT RE-TYPED vvv
    ... (exact existing method body, unchanged) ...
```

New method `_beef_daily_reproduction_update(time)` implements:

1. If `animal_type` is `BEEF_BULL`: return immediately (bulls don't gestate or calve).
2. If the cow is within the configured breeding season window (`AnimalConfig.beef_breeding_season_start_day` to `start_day + beef_breeding_season_length`) and `is_open`: probabilistically determine conception using a natural-service success rate constant (cite NRC reference for typical 90%+ seasonal conception rates with adequate bull ratio).
3. If pregnant: increment `days_in_pregnancy` exactly as the existing dairy code does (reuse the same counter field and increment logic — do not introduce a parallel pregnancy counter).
4. If `days_in_pregnancy` reaches `BEEF_GESTATION_LENGTH_DAYS`: trigger calving — generate a `NewBornCalfValuesTypedDict`, apply `BEEF_STILLBIRTH_RATE` and `BEEF_PREWEANING_SURVIVAL_RATE` probabilistically (reuse the existing dairy `still_birth_rate` pattern from `AnimalConfig`/the dairy reproduction module rather than inventing a new random-draw mechanism), set `calf_at_side`, reset `lactation_day` to 0, increment `times_calved`.

> **Trace-first note before writing the conception-probability draw:**
>
> The existing dairy reproduction module already implements probabilistic conception draws for AI-based protocols (`heifer_estrus_detection_rate` and similar fields referenced in `animal_config.py`'s docstring). Find and reuse the underlying random-draw utility function rather than calling `random.random()` directly in `animal.py` — using the same utility keeps simulation seeding/reproducibility consistent across dairy and beef, which matters for RuFaS's deterministic-with-seed testing approach.

### 4.3 Suckling Instead of Milking

Rename conceptually (not necessarily literally — check existing call sites before renaming a public method, since other modules may call `daily_milking_update` by name) the dairy `daily_milking_update()` pattern into a parallel `daily_suckling_update()` for beef cows, and a corresponding method on the calf side that applies the suckling energy/protein credit calculated in Step 3.3.

```python
def daily_milking_update(self, time: RufasTime) -> None:
    if self.animal_type.is_beef_cow_calf:
        self._beef_daily_suckling_update(time)
        return
    if not self.animal_type.is_cow:   # EXISTING guard — already covers feedlot AND now beef (redundant but harmless)
        return
    # vvv EXISTING DAIRY LOGIC BELOW — COPIED VERBATIM vvv
```

`_beef_daily_suckling_update(time)` increments `lactation_day` for the cow if `calf_at_side` is not None, and applies the suckling credit to the calf's own nutrient requirement calculation (the calf's requirement calculator, Section 3.5/3.7, subtracts the milk-derived energy/protein from its own gross requirement before computing the forage DMI it must additionally consume — this mirrors how a dairy calf's starter DMI calculation already accounts for milk/replacer intake in `calf_ration_manager.py`).

### 4.4 Weaning and Life-Stage Update

Add a `_beef_cow_calf_life_stage_update` method and register it in the existing `ANIMAL_TYPE_TO_LIFE_STAGE_UPDATE_METHOD_MAP` dictionary, following the exact same registration pattern PR #32 used for `_feedlot_life_stage_update`.

```python
ANIMAL_TYPE_TO_LIFE_STAGE_UPDATE_METHOD_MAP = {
    AnimalType.CALF:                    self._calf_life_stage_update,
    AnimalType.HEIFER_I:                self._heiferI_life_stage_update,
    AnimalType.HEIFER_II:               self._heiferII_life_stage_update,
    AnimalType.HEIFER_III:              self._heiferIII_life_stage_update,
    AnimalType.LAC_COW:                 self._cow_life_stage_update,
    AnimalType.DRY_COW:                 self._cow_life_stage_update,
    AnimalType.FEEDLOT_STEER:           self._feedlot_life_stage_update,
    AnimalType.FEEDLOT_HEIFER:          self._feedlot_life_stage_update,
    # ADD:
    AnimalType.BEEF_CALF:               self._beef_calf_life_stage_update,
    AnimalType.BEEF_HEIFER_REPLACEMENT: self._beef_replacement_heifer_life_stage_update,
    AnimalType.BEEF_COW:                self._beef_cow_life_stage_update,
    AnimalType.BEEF_BULL:               self._beef_bull_life_stage_update,
}
```

Each of the four new methods handles a distinct transition, all returning the existing `AnimalStatus` enum:

| Method | Checks | On trigger |
|--------|--------|------------|
| `_beef_calf_life_stage_update` | `days_born >= beef_weaning_age_days` OR `body_weight >= beef_weaning_weight_kg` (whichever first, if both configured) | `CALF_WEANED` event, `beef_post_weaning_destination` dispatch, clear dam's `calf_at_side` |
| `_beef_replacement_heifer_life_stage_update` | `body_weight >= BEEF_HEIFER_TARGET_BREEDING_PCT_MATURE × mature_body_weight` AND within breeding season | Eligible for breeding via `daily_reproduction_update`, `REPLACEMENT_HEIFER_REACHED_BREEDING_WEIGHT`, `animal_type → BEEF_COW` after first calving |
| `_beef_cow_life_stage_update` | `is_open` after breeding season closes; OR `days_born > BEEF_COW_MAX_AGE_DAYS` | `COW_CULLED_OPEN` / `COW_CULLED_AGE` event, `AnimalStatus.CULLED` |
| `_beef_bull_life_stage_update` | Age/soundness checks (config-gated, optional for first implementation) | `AnimalStatus.REMAINING` by config rule |

> **Apply Lesson 1 here explicitly:**
>
> When HerdManager later reports per-class statistics (Step 7), `BEEF_CALF`, `BEEF_HEIFER_REPLACEMENT`, `BEEF_COW`, and `BEEF_BULL` must each resolve to their own filtered list, never a shared pooled list — this is the exact bug pattern CodeRabbit caught for `FEEDLOT_STEER`/`FEEDLOT_HEIFER` in PR #32 round 2, and there are now four sub-types instead of two, so the risk surface is larger.

### 4.5 Daily Routine Dispatch

Unlike feedlot's slim `_feedlot_daily_routines()` replacement, cow-calf reuses the existing `daily_routines()` method directly without a parallel slim path, because cow-calf animals legitimately need `_daily_nutrients_update()`, `_daily_digestive_system_update()`, `daily_milking_update()` (suckling), `daily_growth_update()`, and `daily_reproduction_update()` — exactly the same set of dairy steps, just with beef-specific branches inside several of them as detailed above. No new top-level daily routine method is needed; only the branches within the existing steps.

### Step 4 Test Checkpoint

> **Required before proceeding to Step 5:**
>
> Write `test_beef_cow_calf_lifecycle.py` FIRST. Cover, at minimum: a cow transitioning into the breeding season as `is_open`, a successful conception draw, full gestation to calving with `calf_at_side` set, a calf reaching weaning age and triggering `CALF_WEANED`, a replacement heifer reaching breeding weight and being promoted to `BEEF_COW`, and a cow exceeding `BEEF_COW_MAX_AGE_DAYS` being culled. Each test must assert the SPECIFIC method was routed to (`mocker.patch` + `assert_called`, per Lesson 4) not just the output `AnimalStatus`. Run the full existing `test_animal` suite as a regression check — a single dairy or feedlot test failure means a shared method (`daily_reproduction_update`, `daily_milking_update`, the life-stage dispatch map) was broken.

---

## STEP 5 — Extend Reproduction — Beef Breeding Season

**Files:** reproduction (existing module) | `repro_protocol_enums.py` | `animal_config.py`

Step 4 introduced the cow-calf-specific reproduction branch directly in `animal.py` for simplicity and speed of delivery. Step 5 hardens that into the existing reproduction module's protocol pattern, so beef breeding season logic is configurable and testable the same way `HeiferReproductionProtocol` and `CowReproductionProtocol` already are for dairy, rather than being hardcoded inline in `animal.py`.

### 5.1 repro_protocol_enums.py — Add Beef Protocol

```python
class BeefReproductionProtocol(Enum):
    """Reproduction protocols available for beef cow-calf herds."""
    NATURAL_SERVICE_SEASONAL  = 'natural_service_seasonal'   # bull-bred, defined breeding season
    AI_SEASONAL               = 'ai_seasonal'                # AI within a defined season, no natural service
    AI_CONTROLLED_BREEDING    = 'ai_controlled_breeding'     # CIDR/timed-AI programs, closer to dairy pattern
```

Starting scope for this plan (per the effort estimates in the summary table): implement `NATURAL_SERVICE_SEASONAL` only, since it is the dominant commercial practice (the NRC reference material notes natural service with a defined breeding season is standard for the great majority of US/Canadian cow-calf operations). Define the enum with all three values now so Step 5's class structure does not need revisiting later, but only implement the natural-service branch's logic — raise `NotImplementedError` for the other two with a clear TODO comment citing this as a documented future-PR scope decision (Lesson 7: name the gap explicitly).

### 5.2 AnimalConfig — Wire the Protocol Selection

Add `beef_reproduction_program: BeefReproductionProtocol` to `AnimalConfig`, following the exact pattern of the existing `heifer_reproduction_program: HeiferReproductionProtocol` field, including the `Attributes` docstring entry.

### 5.3 Conception Probability Model

Implement the natural-service conception draw as its own testable function (not inline in `animal.py` — Step 4's inline version should be refactored to call this once Step 5 is complete), parameterized by body condition score and bull ratio, since both materially affect real-world conception rates per the NRC reference material on reproductive efficiency.

```python
def calculate_seasonal_conception_probability(
    body_condition_score: float,
    bull_to_cow_ratio: int,
    days_since_calving: int,
) -> float:
    """
    NRC 2016 Ch.13-informed conception probability for natural-service seasonal breeding.
    Cows below body condition score 5 (1-9 scale) and cows bred too soon after calving
    (postpartum anestrus period, typically 45-60 days) have substantially reduced conception
    probability. This is a simplified single-draw-per-day model; a full estrus-cycle model
    is out of scope for this plan (documented limitation, Step 9).
    """
```

> **Explicitly scoped as a simplification — name it now, per Lesson 7:**
>
> A full 21-day estrus cycle model with multiple insemination windows per breeding season is NOT implemented in this plan. The simplified daily-probability draw approximates seasonal pregnancy rates in aggregate (matching the USDA 91.5% calved-per-cow-exposed statistic at the herd level over a full season) without modeling individual estrus cycles. State this explicitly in the calculator's docstring and in Step 9's documentation so it is a known, named scope boundary rather than a discovered gap during a later review.

### Step 5 Test Checkpoint

> **Required before proceeding to Step 6:**
>
> Write `test_beef_reproduction.py` FIRST. Validate that aggregate conception rate across a large simulated cohort (e.g. 1000 cows, fixed random seed) over a full breeding season lands within a reasonable band of the USDA 85.5% calf-crop-weaned reference (allowing for the separate preweaning survival/stillbirth draws that happen later in Step 4's calving logic — this test validates conception rate specifically, not final weaned calf crop). Confirm `NotImplementedError` is raised cleanly for the two unimplemented protocol values with a passing test for each.

---

## STEP 6 — Wire Ration Management — Seasonal Forage Diets

**Files:** `ration_manager.py` | `ration_optimizer.py`

Feedlot rations were a fixed three-phase step-up (starter/transition/finisher) over a few weeks. Cow-calf rations are seasonal and state-dependent across the whole year: a lactating cow-calf pair on summer pasture, a dry pregnant cow on winter hay/crop residue, and an optional creep-feed supplement for nursing calves. This step must extend `RationManager` with multiple named seasonal rations rather than a single step-up sequence.

> **Source location:** `NRC2016_BeefCattle_FeedLibrary_Complete.xlsx`, sheets `"🐮 Cow-Calf CC"` and `"🐮 Grazed Forages (Table 18-2)"`.
>
> The Cow-Calf CC tab already has 104 feeds with RUFAS IDs starting at 401 (e.g. 401 Alfalfa Cubes, 405 Alfalfa Hay, 410 Barley Grain), covering legumes, byproducts, energy grains, and more, all pre-tagged for the CC system. The Grazed Forages tab is genuine NRC 2016 Table 18-2 seasonal pasture composition data (TDN/NDF/CP by species, month, and region — e.g. Bermudagrass in North Carolina varies from 71.8% TDN in June vegetative growth to 65% TDN in July mature growth), explicitly noted in the sheet as "for seasonal lookup in cow-calf grazing simulations — NOT fixed composition constants." Use real feed IDs from these two tabs when building the seasonal ration configs below — do not invent placeholder feed IDs.

### 6.1 RationManager — Seasonal Ration Registration

```python
@classmethod
def set_ration_feeds(cls, ration_config: dict[str, Any]) -> None:
    # ... EXISTING dairy + feedlot staging logic, atomic-commit pattern (Lesson 3) ...

    # ADD — staged in LOCAL variables first, exactly like the feedlot fix that followed Lesson 3:
    beef_lactating_pasture_ration = {
        int(k): float(v) for k, v in ration_config.get("beef_lactating_pasture_ration", {}).items()
    }
    beef_dry_gestating_ration = {
        int(k): float(v) for k, v in ration_config.get("beef_dry_gestating_ration", {}).items()
    }
    beef_creep_feed_ration = {
        int(k): float(v) for k, v in ration_config.get("beef_creep_feed_ration", {}).items()
    }
    beef_replacement_heifer_ration = {
        int(k): float(v) for k, v in ration_config.get("beef_replacement_heifer_ration", {}).items()
    }

    # Validate ALL FOUR — non-negative AND sums to 100% — BEFORE committing to class state.
    # This is the exact validation block from the feedlot module's final, twice-corrected version:
    for name, ration in [
        ("beef_lactating_pasture",  beef_lactating_pasture_ration),
        ("beef_dry_gestating",      beef_dry_gestating_ration),
        ("beef_creep_feed",         beef_creep_feed_ration),
        ("beef_replacement_heifer", beef_replacement_heifer_ration),
    ]:
        if ration:
            if any(pct < 0.0 for pct in ration.values()):
                raise ValueError(f"Beef {name} ration percentages must be non-negative, got: "
                                 f"{[pct for pct in ration.values() if pct < 0.0]}")
            total_pct = sum(ration.values())
            if abs(total_pct - 100.0) > 1e-2:
                raise ValueError(f"Beef {name} ration percentages must sum to 100.0%, got {total_pct}%")

    # Only commit AFTER all validation passes (atomic — Lesson 3):
    cls.beef_lactating_pasture_ration  = beef_lactating_pasture_ration
    cls.beef_dry_gestating_ration      = beef_dry_gestating_ration
    cls.beef_creep_feed_ration         = beef_creep_feed_ration
    cls.beef_replacement_heifer_ration = beef_replacement_heifer_ration
```

> **Apply Lessons 2 and 3 from the FIRST draft, not as a follow-up fix:**
>
> PR #32 needed two separate review rounds to reach the validation block shown above — first the basic sum check, then the negative-percentage guard, then the atomic-commit refactor. Writing the complete, hardened version in the very first commit for cow-calf (using the version above as the template) should save at least one full review round compared to the feedlot module's history. Also `creep_feed_ration` is the only ration here with a config-driven on/off switch (`AnimalConfig.beef_creep_feeding_enabled`) — empty dict (no creep feeding configured) must be treated as valid and skip both checks, exactly as the `if ration:` guard above already does.

Scope decision on the Grazed Forages (Table 18-2) seasonal lookup data: this plan treats grazed-pasture composition as a STATIC per-ration input set by the user at config time (e.g. the `beef_lactating_pasture_ration` dict reflects whatever forage mix and quality the user configures for their region/season), not as a dynamic month-by-month lookup against the Grazed Forages tab's full species/region/season table. Implementing a true dynamic seasonal lookup (automatically swapping forage composition by simulation month and configured region) is a larger feature than this plan's effort estimate allows and is named here as an explicit future enhancement (Lesson 7), not a hidden gap. For this plan, the user selects representative feed IDs from the Cow-Calf CC and Grazed Forages tabs once per named ration (e.g. `beef_lactating_pasture_ration` uses a feed ID whose composition reflects "average summer Bermudagrass"), and the user is responsible for updating the ration config if they want to model a different season within the same simulation run.

### 6.2 RationManager — Seasonal Ration Selection Method

```python
@classmethod
def get_beef_seasonal_ration(
    cls, animal: "Animal", requirements: NutritionRequirements
) -> dict[RUFAS_ID, float]:
    """
    Selects the correct seasonal ration dict for a beef cow-calf animal based on its
    current reproductive/lactation state, mirroring get_feedlot_phase_ration's pattern
    of state-driven ration lookup.
    """
    if animal.animal_type == AnimalType.BEEF_HEIFER_REPLACEMENT:
        return cls.beef_replacement_heifer_ration
    if animal.animal_type == AnimalType.BEEF_COW and animal.calf_at_side is not None:
        return cls.beef_lactating_pasture_ration
    if animal.animal_type == AnimalType.BEEF_COW:
        return cls.beef_dry_gestating_ration
    if animal.animal_type == AnimalType.BEEF_BULL:
        return cls.beef_dry_gestating_ration   # bulls fed maintenance-level ration outside breeding season
    raise ValueError(f"No beef seasonal ration defined for animal_type {animal.animal_type}")
```

Creep feed is handled separately: it is a supplement ADDED to a nursing calf's diet alongside suckling and grazed forage, not a replacement ration selected by this method. Add a parallel, optional `get_beef_creep_feed_supplement(animal, requirements)` that returns an empty dict if `AnimalConfig.beef_creep_feeding_enabled` is `False` or the calf has not yet reached the configured creep-feeding start age.

### 6.3 RationOptimizer — Beef Constraint Set

Reuse the constraint-set dispatch pattern from PR #32's `_select_constraints`, with the type-consistency fix already applied there (all constraint attributes typed as the same `list[dict[str, Any]]` shape, per the fix that resolved @jrobichaud's typing comment).

```python
def _select_constraints(self, animal_combination: AnimalCombination) -> Sequence[dict[str, Any]]:
    # ... existing dairy and feedlot branches ...
    if animal_combination in (
        AnimalCombination.BEEF_COW_CALF_PAIR,
        AnimalCombination.BEEF_GESTATING,
    ):
        return self.beef_cow_constraints   # high forage-NDF MINIMUM, no upper finishing ceiling
    if animal_combination == AnimalCombination.BEEF_REPLACEMENT:
        return self.beef_replacement_constraints
    if animal_combination == AnimalCombination.BEEF_BULL_BATTERY:
        return self.beef_cow_constraints   # bulls share the dry-cow-style maintenance constraint set
    return self.heifer_constraints
```

> **Remember to update `handle_failed_constraints()` too — this exact omission was caught by CodeRabbit in PR #32:**
>
> The feedlot PR's first round added the `FEEDLOT_FINISHING` branch to `_select_constraints()` but forgot the matching branch in `handle_failed_constraints()`, causing failed-constraint summaries to silently use the wrong constraint set. Mirror the SAME branching logic in BOTH methods for all four new beef combinations in this same commit, not as a follow-up fix.

### Step 6 Test Checkpoint

> **Required before proceeding to Step 7:**
>
> Write `test_beef_ration.py` FIRST, including an autouse fixture that deep-copies and restores all `RationManager` beef ration class attributes around each test (Lesson 5, applied from the start). Include negative-percentage and bad-sum parametrized test cases using tuple-form `@pytest.mark.parametrize` args (PT006-compliant from the first draft). Test that `_select_constraints` and `handle_failed_constraints` agree for all four new combinations.

---

## STEP 7 — Extend Herd, Pen, and Reporter Infrastructure

**Files:** `herd_manager.py` | `herd_factory.py` | `pen.py` | `animal_module_reporter.py` | `nutrients.py` | `data_validator.py`

### 7.1 HerdManager — Per-Class Cohort Lists (Lesson 1, applied from the start)

```python
# In HerdManager.__init__ or equivalent setup — separate lists per AnimalType, never pooled:
self.beef_cows: list[Animal] = []
self.beef_replacement_heifers: list[Animal] = []
self.beef_calves: list[Animal] = []
self.beef_bulls: list[Animal] = []

# In the animals_by_type property/method — EACH AnimalType maps to ITS OWN filtered list:
return {
    # ... existing dairy and feedlot entries (feedlot entries already fixed per Lesson 1 in PR #32 round 2) ...
    AnimalType.BEEF_COW:                self.beef_cows,
    AnimalType.BEEF_HEIFER_REPLACEMENT: self.beef_replacement_heifers,
    AnimalType.BEEF_CALF:               self.beef_calves,
    AnimalType.BEEF_BULL:               self.beef_bulls,
}
```

Because beef cows transition between `BEEF_HEIFER_REPLACEMENT` → `BEEF_COW` (Step 4.4) and calves transition out via weaning (Step 8), HerdManager needs add/remove methods that keep these lists and each animal's individual `animal_type` attribute in sync — mirroring however the existing dairy `HEIFER_III` → `LAC_COW` transition already keeps HerdManager's internal lists consistent (trace this existing transition handling before writing new code, per Lesson 8).

### 7.2 HerdFactory — Cow-Calf Herd Initialization

```python
def initialize_herd(self, config):
    if config.animal_type.is_feedlot:
        return self._initialize_feedlot_herd(config)
    elif config.animal_type.is_beef_cow_calf:
        return self._initialize_beef_cow_calf_herd(config)
    else:
        # existing dairy path, unchanged
        ...

def _initialize_beef_cow_calf_herd(self, config) -> list[Animal]:
    try:
        cow_calf_cfg: dict[str, Any] = self.im.get_data("animal.herd_initialization.beef_cow_calf")
    except (KeyError, TypeError):
        return []

    # Lesson 2, applied from the first draft — not a follow-up fix:
    if not isinstance(cow_calf_cfg, dict) or not cow_calf_cfg:
        return []

    n_cows                         = int(cow_calf_cfg.get("num_cows", 0))
    n_replacement_heifers          = int(cow_calf_cfg.get("num_replacement_heifers", 0))
    n_bulls                        = int(cow_calf_cfg.get("num_bulls", 0))
    mature_cow_weight              = float(cow_calf_cfg.get(
        "mature_cow_weight", AnimalModuleConstants.BEEF_DEFAULT_MATURE_COW_WEIGHT_KG
    ))
    breed_str                      = str(cow_calf_cfg.get("breed", "XB"))
    initial_pregnancy_distribution = cow_calf_cfg.get("initial_pregnancy_distribution", [])
    # ... construct Animal() instances for cows (with staggered initial days_in_pregnancy per the
    #     distribution, so the herd doesn't unrealistically calve all on one day), replacement
    #     heifers, and bulls ...
```

> **Why `initial_pregnancy_distribution` matters and shouldn't be skipped:**
>
> A freshly initialized cow herd should reflect a realistic spread of days-in-pregnancy at simulation start (matching the spring/fall calving season distribution described in the NRC reference), not all cows at `days_in_pregnancy=0`. Without this, the herd will show an unrealistic synchronized calving spike in the first `BEEF_GESTATION_LENGTH_DAYS` of simulation rather than a steady-state distribution. This is analogous to how the feedlot config accepts a `days_already` (days already on feed) parameter for non-fresh-start initialization — reuse that same "allow non-zero starting state" config pattern here.

### 7.3 Pen.py — Pasture/Paddock Considerations

PR #32 added `mud_condition` to `Pen` for feedlot lot conditions. Cow-calf operations are typically pasture-based, so a parallel but distinct concept applies: `forage_availability_kg_per_ha` or simply a `forage_quality_factor` used in Step 3.7's DMI calculation. Keep this minimal for the first implementation — a single config-driven float, not a full pasture-growth-model — and document the simplification explicitly (Lesson 7) rather than letting scope creep into a full grazing/pasture-growth sub-system, which is out of scope for this plan.

### 7.4 nutrients.py — Routing for Cow-Calf

Apply the exact pattern used to fix the feedlot phosphorus routing gap (the integration-completeness fix added after PR #32's initial merge):

```python
def _calculate_phosphorus(self, animal):
    if animal.animal_type.is_feedlot:
        return animal.nutrition_requirements.phosphorus
    if animal.animal_type.is_beef_cow_calf:
        return animal.nutrition_requirements.phosphorus   # from BeefCowCalfRequirementsCalculator, Step 3.6
    else:
        # existing dairy path
        ...
```

Apply the SAME pattern for calcium and any other nutrient routed through `nutrients.py` for dairy/feedlot today. This is exactly the kind of "make it reachable from a real simulation, not just from a unit test fixture" wiring that Lesson 7 says must be a first-class step, not deferred.

### 7.5 data_validator.py — Cow-Calf Config Validation

```python
import math

def validate_beef_cow_calf_config(self, config):
    mature_cow_weight = float(config.get("mature_cow_weight", 0))
    if not math.isfinite(mature_cow_weight) or mature_cow_weight <= 0:
        raise ValueError(f"beef mature_cow_weight must be > 0, got {mature_cow_weight}")

    weaning_age = int(config.get("beef_weaning_age_days", 0))
    if weaning_age <= 0:
        raise ValueError(f"beef_weaning_age_days must be > 0, got {weaning_age}")

    breeding_season_length = int(config.get("beef_breeding_season_length", 0))
    if breeding_season_length <= 0:
        raise ValueError(f"beef_breeding_season_length must be > 0, got {breeding_season_length}")

    bull_ratio = int(config.get("beef_natural_service_bull_ratio", 0))
    if bull_ratio <= 0:
        raise ValueError(f"beef_natural_service_bull_ratio must be > 0, got {bull_ratio}")
    if bull_ratio > 50:   # NRC reference: typical range 20-30:1, 50:1 is an extreme outlier worth flagging
        raise ValueError(f"beef_natural_service_bull_ratio of {bull_ratio} exceeds the recommended maximum (50)")
```

Note that `math.isfinite()` guards and the `>0` checks are included from the FIRST draft here (Lesson 3), not added in a follow-up round as happened twice during the feedlot PR review.

### 7.6 AnimalModuleReporter — Cow-Calf Performance Reporting

```python
@classmethod
def report_cow_calf_performance(cls, animal: "Animal", simulation_day: int) -> None:
    """
    Reports cow-calf herd performance metrics to OutputManager: days_in_pregnancy,
    calf_weaning_weight (if applicable this day), calving_interval, body_condition_score.
    """
```

Mark this entry in `changelog.md` with `[OutputChange]` from the first draft — PR #32's round-2 review caught a mismatched `[NoOutputChange]` tag for the equivalent feedlot reporter method, and this method is unambiguously a new output, so there is no ambiguity to get wrong here.

### Step 7 Test Checkpoint

> **Required before proceeding to Step 8:**
>
> Write `test_beef_cow_calf_herd.py` FIRST, with an explicit test asserting that `BEEF_COW`, `BEEF_HEIFER_REPLACEMENT`, `BEEF_CALF`, and `BEEF_BULL` each resolve to a DISTINCT, non-shared list object in `animals_by_type` (Lesson 1 — write the regression test for the bug class itself, not just the happy path). Write a test passing a non-dict `cow_calf_cfg` and confirm `[]` is returned, not an `AttributeError` (Lesson 2). Write NaN/inf and zero/negative tests for every new `data_validator` rule (Lesson 3). Run `test_herd_manager`, `test_nutrients`, and `test_pen` as regression checks.

---

## STEP 8 — Wire Weaned Calf Hand-Off

**Files:** `herd_manager.py` | `animal.py` | `herd_factory.py`

This step did not exist in the feedlot plan because feedlot animals enter and exit the simulation as a single self-contained cohort. Cow-calf calves are born INSIDE the simulation and must hand off into either the existing dairy-style `CALF`→`HEIFER_I` pipeline (if `AnimalConfig.beef_post_weaning_destination` is `'replacement_heifer'`, though note this would actually become `BEEF_HEIFER_REPLACEMENT`, not the dairy `HEIFER_I`, per Step 1's reasoning for keeping beef and dairy types separate), the feedlot pipeline introduced in PR #32 (`'direct_to_feedlot'`), a generic stocker/backgrounding holding state (out of scope — see callout below), or simply exit the simulation as sold (`'sell'`).

### 8.1 Weaning Dispatch Logic

```python
def _beef_weaning_event(self, time: RufasTime) -> AnimalStatus:
    """
    Handles a BEEF_CALF reaching weaning age/weight. Dispatches the calf to its
    configured post-weaning destination per AnimalConfig.beef_post_weaning_destination.
    """
    self.events.append(animal_constants.CALF_WEANED)
    if self.dam is not None:
        self.dam.calf_at_side = None

    destination = AnimalConfig.beef_post_weaning_destination
    if destination == "replacement_heifer" and self.animal_type != AnimalType.BEEF_BULL:
        self.animal_type = AnimalType.BEEF_HEIFER_REPLACEMENT
        return AnimalStatus.LIFE_STAGE_CHANGED
    elif destination == "direct_to_feedlot":
        self.animal_type = AnimalType.FEEDLOT_STEER if self.sex == Sex.STEER else AnimalType.FEEDLOT_HEIFER
        self._initialize_feedlot_animal({
            "body_weight":        self.body_weight,
            "mature_body_weight": AnimalConfig.feedlot_entry_weight,   # or a dedicated mapping, see note
            "days_on_feed":       0,
        })
        return AnimalStatus.LIFE_STAGE_CHANGED
    elif destination == "sell":
        self.sold_at_day = time.simulation_day
        return AnimalStatus.SOLD
    else:
        raise ValueError(f"Unknown beef_post_weaning_destination: {destination}")
```

> **Scope boundary, named explicitly (Lesson 7): no generic stocker/backgrounding state in this plan.**
>
> The NRC reference material describes a distinct stocker/backgrounding segment between weaning and feedlot entry (forage-based growing phase, 0.35-1.15 kg/d gain, until 300-400 kg entry weight). This plan's `'direct_to_feedlot'` destination skips that intermediate phase and sends a freshly weaned calf straight into `FEEDLOT_STEER`/`FEEDLOT_HEIFER` at its current weaning weight, which is lighter than NRC 2016's expected feedlot entry weight (240 kg weaning vs. 300-400 kg typical feedlot entry). This is an explicitly accepted simplification for this plan, NOT a hidden gap — document it in Step 9 and flag it to Maxime/Rami as a candidate for a future 'stocker/backgrounding module' PR, distinct from both this plan and the original feedlot plan.

### 8.2 HerdManager List Membership on Hand-Off

When a calf's `animal_type` changes (weaning, replacement-heifer promotion, direct-to-feedlot), HerdManager's per-class lists (Section 7.1) must be updated to move the `Animal` reference from its old list to its new one in the same simulation day. Trace exactly how the existing `HEIFER_III` → `LAC_COW` dairy transition keeps HerdManager's lists in sync (Lesson 8) and reuse that same update-on-transition mechanism rather than inventing a parallel one.

### Step 8 Test Checkpoint

> **Required before proceeding to Step 9:**
>
> Write `test_beef_weaning_handoff.py` FIRST. Test all three implemented destinations (`replacement_heifer`/`direct_to_feedlot`/`sell`) individually, asserting both the `animal_type` change AND the HerdManager list membership change happen together, not just one or the other. Test that an unknown destination string raises `ValueError` with a clear message rather than silently doing nothing.

---

## STEP 9 — Documentation, Constants Audit, and Changelog

**Files:** `CLAUDE.md` | `docs/beef_module/` | `changelog.md`

Mirrors the documentation discipline already established in `docs/beef_module/README.md` for the feedlot module. Add a parallel section rather than overwriting the existing feedlot documentation.

- Create `docs/beef_module/cow_calf/` with a `README.md` describing the reference sources used (Beef NRC Management.docx, NRC 2016 Chapters 6/11/12/13/19/20), the same way the feedlot README documents the Requirements Calculator Inventory and Feed Library.
- List every explicitly named scope boundary from this plan in one place: the simplified single-draw conception model (Step 5.3), the missing stocker/backgrounding intermediate phase (Step 8.1), the grazing activity multiplier as a flat constant rather than per-pasture input (Step 3.2), and the milk-yield estimation method's wider validation tolerance (Step 3.8).
- Update the root `CLAUDE.md`'s existing `'Beef Module Reference Documents'` section (added for feedlot) to also point to `docs/beef_module/cow_calf/`.
- Add the `changelog.md` entry using `[OutputChange]` for `report_cow_calf_performance` and any other new reportable metric, applying the lesson from PR #32 round 2's changelog tag correction from the start.

### Step 9 Test Checkpoint

> **Required before proceeding to Step 10:**
>
> No code tests for this step, but run a documentation lint pass (the same MD022 blank-line-before-heading rule CodeRabbit flagged for `CLAUDE.md` in PR #32 round 2) on every new or edited markdown file.

---

## STEP 10 — Integration Test — Multi-Year Herd Simulation

**Files:** All files above

The feedlot integration test (Step 7 of that plan) ran a single 220-day pass because feedlot is a one-shot finishing process. Cow-calf is a perpetual cyclical system, so this integration test must run long enough to observe at least one full breeding-gestation-calving-weaning cycle, ideally two, to catch any state that silently degrades or drifts across cycle boundaries (a risk category that did not exist in the feedlot module).

### 10.1 Test Configuration

| Parameter | Value | Purpose |
|-----------|-------|---------|
| Number of cows | 80 | Mid-size US herd, matches USDA average + margin |
| Number of replacement heifers | 15 | ~18% replacement rate, matches USDA preconditioning stats |
| Number of bulls | 3 | ~27:1 cow:bull ratio, within NRC reference range |
| Breed | Angus (AN) | Known NEm multiplier 1.00, reused from feedlot validation |
| Mature cow weight | 520 kg | USDA average mature cow weight at weaning |
| Breeding season | 63 days, day 90 of simulation year | Spring calving pattern per NRC reference (60% of US calves) |
| Weaning age | 207 days | USDA average weaning age |
| Simulation length | 2 full years (730 days) | Captures two full breeding-gestation-calving-weaning cycles |
| Initial pregnancy distribution | staggered, matching spring calving season spread | Avoids unrealistic synchronized first calving |
| `beef_post_weaning_destination` | `'direct_to_feedlot'` for one sub-herd, `'replacement_heifer'` for another | Exercises both implemented hand-off paths in the same run |

### 10.2 Assertions to Verify

- Herd-level calf crop weaned per cow exposed lands within a reasonable band of the USDA 85.5% reference (allowing simulation variance, not requiring exact match).
- Mean calving interval across cows that calved twice is within ±10% of the 365-day target implied by a once-per-year calving pattern.
- No cow's `days_in_pregnancy` exceeds `BEEF_GESTATION_LENGTH_DAYS` without triggering calving (no stuck-pregnancy state).
- Every calf that reaches its configured weaning age/weight triggers exactly one `CALF_WEANED` event, and HerdManager list membership reflects the new `animal_type` within the same simulation day (Step 8 wiring check).
- Replacement heifers that reach `BEEF_HEIFER_TARGET_BREEDING_PCT_MATURE × mature_body_weight` within the breeding season are included in that season's conception draw; those below the threshold are correctly excluded.
- `animals_by_type` returns four distinct, non-overlapping list objects for the four beef `AnimalType` values at every simulation day checked (explicit Lesson 1 regression assertion, not just at day 0).
- No dairy-module attributes are accessed on beef cow-calf animals (no `AttributeError` on `milk_production`'s dairy-specific fields, no dairy reproduction protocol fields accessed).
- No feedlot-module attributes are accessed on beef cow-calf animals before an explicit `direct_to_feedlot` hand-off occurs.
- Ration optimizer succeeds for all 730 days across all four beef constraint sets (no fallback-to-previous-ration warnings).
- Pen forage availability/quality factor (Step 7.3) never drives DMI negative or above a sane physiological ceiling.

### Step 10 Test Checkpoint

> **Required before proceeding to Step 11:**
>
> Run the entire existing test suite as a full regression check: `pytest tests/ -k "not test_beef_cow_calf"`. A single dairy or feedlot test failure means a shared method (`daily_reproduction_update`, `daily_milking_update`, the life-stage dispatch map, `animals_by_type`) was broken by this integration. Set up E2E filter files following the same human-in-the-loop review discipline the testing skill requires for feedlot (never auto-accept E2E expected-result updates without manually reviewing and removing the warning line).

---

## STEP 11 — Validation Against NASEM/NRC Reference Benchmarks

**Files:** `BeefCowCalfRequirementsCalculator` unit tests

Mirrors Step 8 of the feedlot plan: validate the calculator's output against published reference values, using the tolerances defined in Section 3.8. Unlike feedlot's single Box 12-1 anchor value, cow-calf needs multiple anchor points because the calculator branches on physiological state (gestating vs. lactating vs. growing).

| Test ID | Animal/State | Reference Source | Primary check |
|---------|--------------|------------------|---------------|
| CC-MAINT-1 | 520 kg dry, non-pregnant cow, thermoneutral | NRC 2016 Ch.11 | NEm within ±3% |
| CC-GEST-1 | 520 kg cow, day 250 of pregnancy | NRC 2016 Ch.13 gravid uterine weight curve | Gestation energy within ±3% |
| CC-LACT-1 | 520 kg cow, peak lactation (day 60), 8 kg peak milk curve | NRC 2016 Ch.13 Fig 13-4 | Estimated milk yield within ±10% of curve reference point; lactation energy within ±5% |
| CC-GROW-1 | Replacement heifer, 60% of 520 kg mature weight, target ADG 0.675 kg/d | NRC 2016 Ch.12 (reused growth equation) | Growth energy within ±3% |
| CC-CALF-1 | BEEF_CALF, 35 kg birth weight, day 30, nursing + forage | NRC reference preweaning ADG ~1.0 kg/d | Combined suckling + forage requirement within ±5% |
| CC-DMI-1 | 520 kg cow, moderate condition, no pregnancy/lactation | NRC reference 2.25% BW guideline | DMI within ±5% of 11.7 kg/d |

Where multiple physiological states overlap (the realistic case of a cow that is both lactating AND newly rebred, i.e. pregnant again before this lactation's calf is weaned), add a combined-state test confirming the calculator correctly SUMS lactation and gestation requirement components rather than only applying one — this directly parallels how the existing dairy NASEM calculator already sums these terms for a pregnant lactating dairy cow, and is the single most important state-handling test in this entire plan, since getting it wrong would silently understate the requirement for the most nutritionally demanding state a beef cow experiences.

### Step 11 Test Checkpoint

> **Required before this work is considered complete:**
>
> Run `pytest tests/.../test_beef_cow_calf/ -m "validation" -v` and confirm all benchmark tests pass at their documented tolerance. Run code coverage specifically on `beef_cow_calf_requirements_calculator.py` and target 100% coverage on new code, per the testing skill's coverage expectation. Do NOT use BeefGEM outputs as a test oracle for any of these (NRC 2000 / monthly timestep mismatch, per the testing skill's explicit warning).

---

## Branching and PR Strategy — Applying Lesson 7 at the Process Level

The feedlot module's review history (two CodeRabbit rounds plus a separate follow-up PR for HerdFactory/phosphorus/data_validator wiring) suggests a slightly different PR segmentation for cow-calf, given it is a larger and more state-heavy addition.

| PR | Scope | Steps included | Rationale |
|----|-------|----------------|-----------|
| PR-A | Identity + constants + calculator | 1, 2, 3 | Self-contained, testable in isolation, no simulation wiring risk — mirrors how PR #32 isolated the calculator before lifecycle wiring |
| PR-B | Lifecycle + reproduction | 4, 5 | The highest-novelty, highest-risk steps (new state machine, new probabilistic model) reviewed on their own without ration/herd noise |
| PR-C | Ration + Herd/Pen/Reporter + weaning hand-off | 6, 7, 8 | The "make it reachable from a real simulation" integration wiring — explicitly scheduled as its own PR per Lesson 7, not deferred informally |
| PR-D | Docs + integration test + validation | 9, 10, 11 | Final correctness gate before merge to dev-msf, mirrors feedlot Steps 7-8 |

Each PR should still individually pass the full existing regression suite before merge, exactly as required for every feedlot PR. Each PR should also get a `/challenge plan` pass (per the OpenSpec workflow Maxime set up) before implementation begins, specifically to surface the kind of integration-completeness questions that were missed in the original feedlot plan and only caught in follow-up rounds — "how does HerdFactory actually wire this in", "what happens at the lactating-and-pregnant overlap state", "where does a weaned calf actually go".

---

## Addendum — Lessons from PR #32 Final Review (added post-merge)

## Lesson 9 — Respect the onion-layer architecture: never call upward-layer code from animal.py

Jules identified during PR #32 final review that animal.py sits at a lower
dependency layer than AnimalModuleReporter, HerdManager, and HerdFactory.
Calling any of these from inside animal.py creates circular imports. This
affects cow-calf Steps 4, 7, and 8 directly:

- `_beef_cow_calf_life_stage_update` must NOT call
  `AnimalModuleReporter.report_cow_calf_performance` — add a TODO comment
  naming where the call belongs instead (in the future `_beef_cow_calf_update`
  in herd_factory.py, same pattern as `_cow_update`)
- `_beef_weaning_event` must NOT call HerdManager methods directly — return
  the status and let the higher-layer caller handle list membership updates
- `BeefCowCalfRequirementsCalculator` import in animal.py IS safe at module
  level (confirmed via import test during feedlot work — no circular path)

The fix pattern established in PR #32: remove the call from animal.py,
add a TODO comment naming the exact architectural gap and where the call
belongs, and wire it properly in herd_factory.py's higher-layer update
method in Step 7.

## Lesson 10 — Wire the new animal type into _process_daily_herd_updates explicitly

`herd_manager._process_daily_herd_updates` iterates over calves, heiferIs,
heiferIIs, heiferIIIs, cows — new animal types are NOT automatically
included. Step 7 must:

1. Add a `_beef_cow_calf_update(animal)` method to herd_factory.py,
   mirroring `_cow_update` (~line 268)
2. Wire `beef_cows` + `beef_replacement_heifers` + `beef_calves` + `beef_bulls`
   into `_process_daily_herd_updates`

Without this, the daily routine never runs on cow-calf animals in a real
simulation — the exact gap that existed for feedlot animals at PR #32
merge and was identified as Known Limitation #1 in the implementation
report.

## Lesson 11 — Jules's import rule, verbatim

> "It is very rare we do import inside functions. It is done normally only
> to fix circular imports and a few more advanced imports. But if it is a
> circular import problem, this may need to be discussed."

Every import in every new cow-calf file must be at module level from the
first draft. Any that genuinely cannot be moved (real circular import)
must include a comment naming the exact import cycle (e.g. `a.py → b.py
→ c.py → a.py`) and must be mentioned explicitly in the PR description
so Jules can evaluate the architecture rather than just seeing a deferred
import and flagging it repeatedly.

---

## Appendix — Message to Feed Claude Code to Begin Step 1

Paste the block below into Claude Code to begin implementation. It intentionally starts with only Step 1, following the same one-step-at-a-time discipline used for the feedlot module, rather than handing over the entire plan at once.

```
I'm starting implementation of the cow-calf production system for RuFaS, a companion module to the
beef feedlot module (PR #32, already merged to dev-msf). Full plan reference: docs/beef_module/cow_calf/
(the document I'm about to share covers all 11 steps; we will work one step at a time).

Branch: feature/beef-cowcalf-step-1-enums (create from latest dev-msf)

Apply these lessons from the feedlot PR #32 review cycle to EVERY step, not just when reminded:
1. Never map two different AnimalType values to the same shared/pooled list in HerdManager.
2. Always isinstance(cfg, dict) guard before .get() on any config dict from InputManager.
3. Always math.isfinite() + sign + sum validation on numeric config inputs, staged in local
   variables and committed to class state only after ALL validation passes (atomic commit).
4. Every dispatch test must assert the target method was actually called (mocker.patch + assert_called),
   not just that the output type/shape looks right.
5. Any test touching RationManager or HerdManager class state needs an autouse fixture that
   deep-copies and restores that state around each test.
6. When adding a guard in front of existing dairy code, copy the original line verbatim into the
   else-branch — never re-type it.
7. Integration wiring (HerdFactory, data_validator, nutrients.py routing) is part of the plan's
   explicit steps, not implied follow-up work.
8. Before writing new code, trace whether the existing dairy code path already does it and can be
   reused via composition, rather than assuming new code is needed.

Starting with STEP 1 only: extend animal_types.py, animal_enums.py, animal_combination.py, and
animal_grouping_scenarios.py per the attached plan's Step 1 section. Write test_beef_cow_calf_enums.py
FIRST (TDD), confirm it fails, then implement, then confirm it passes. Run the full test_data_types/
regression suite afterward. Run black + mypy + flake8. Report back with test results before I review
and we proceed to Step 2.

After Step 1 is reviewed and committed, repeat this pattern for each subsequent step, always
referencing the specific step section of this document and always closing with the step's named Test
Checkpoint before moving on.
```
