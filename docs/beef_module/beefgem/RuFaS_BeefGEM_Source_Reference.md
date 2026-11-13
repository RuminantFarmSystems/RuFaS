<!--
CONVERTED SOURCE DOCUMENT — reference only, do not implement from this file.

Origin : RuFaS_BeefGEM_Management_Implementation_Plan.docx (June 2026)
Status : Phase B (Steps B-1, B-2) is SUPERSEDED — the native stocker module
         it describes was delivered by PR #47 and merged to dev-msf.

Implement from : docs/beef_module/beefgem/RuFaS_BeefGEM_Implementation_Plan.md

Value retained here:
  - BeefGEM 4.0 source mapping (simulate.py, herd_dynamics.py, physiology.py)
  - Rule identifiers (R-CH4-ENT-003, D-STOCKER-TO-FINISH-001, ...)
  - COW_CALF_STOCKER_FEEDLOT grouping scenario definition (Step B-1)
  - Test-marker taxonomy (unit / component / integration / regression)
  - Five named future-PR gaps (Section 10)

Note: code blocks were flattened by the DOCX conversion and have been
re-fenced heuristically. Treat the code as indicative, not copy-paste ready —
the .md execution plan carries the authoritative versions.
-->

**RuFaS Beef Cattle Module**

**BeefGEM Management Features — Post Full-Module Integration Plan**

*McGill University \| Animal Science & Aquatic Sciences \| June 2026*

|     |
|-----|
|     |

# 1. Purpose and Scope

This document is a forward implementation plan for enriching the RuFaS beef cattle module with management features present in BeefGEM 4.0 (USDA/ARS) but not yet in RuFaS. It is intentionally written as a post-full-module plan — to be executed only after all three RuFaS beef module segments (feedlot ✓ done, cow-calf — in progress, stocker — next pending) are implemented, integrated, and all tests are passing.

The plan is grounded in direct code review of the beefgem-rules-main repository (Python re-extraction of BeefGEM 4.0, 166 rules, 366 tests passing) and the NRC 2016 Beef Cattle reference. It covers six management feature areas across four implementation phases, each with file-level instructions, BeefGEM source mapping, and test checkpoints.

Features are grouped into four implementation phases:

- Phase A — Production system flag and finishing type (1 step, low effort)

- Phase B — Backgrounding / stocker module (2 steps, medium effort)

- Phase C — Herd population dynamics with scenario levers (3 steps, high effort)

- Phase D — Environmental stress and performance modifiers (2 steps, medium effort)

# 2. What This Plan Does NOT Cover

The following are explicitly out of scope for this plan:

- GHG emission equation upgrades (separate GHG implementation plan)

- Manure module changes (manure module scope)

- NRC 2016 nutrition equation improvements (already in BeefNRCRequirementsCalculator)

- Crop / pasture module integration

- Economic / cost-of-production modelling

# 3. Prerequisites: All Three Beef Module Segments Must Be Complete

This plan must NOT be started until all three beef module segments below are merged, integrated, and fully passing their test suites. Attempting any phase of this plan before the stocker module (Segment 3) is complete will produce merge conflicts and require rework.

| **\#** | **Segment**                   | **Status**     | **What this plan depends on from it**                                                                                                                                                                                                           |
|--------|-------------------------------|----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1      | Feedlot module                | DONE (PR \#32) | FEEDLOT_STEER/HEIFER types, BeefNRCRequirementsCalculator, AnimalConfig feedlot params, feedlot daily routines — Phase A finishing_system flag extends these                                                                                    |
| 2      | Cow-Calf module               | IN PROGRESS    | BEEF_COW/CALF/HEIFER_REPLACEMENT/BULL types, BeefCowCalfRequirementsCalculator, \_beef_weaning_event(), calving/culling lifecycle, AnimalConfig beef params — Phases B, C, D all extend these                                                   |
| 3      | Stocker module (native RuFaS) | NEXT PENDING   | BEEF_STOCKER_STEER/HEIFER types, BeefStockerRequirementsCalculator, stocker-to-feedlot transfer, stocker daily routines — Phase B BeefGEM enhancement extends these; Phase C scenario runner depends on all three segments being wired together |

Only start this BeefGEM management implementation plan once all three rows above are complete. The implementation sequence within this plan also has an internal order dependency: Phase A can be done independently (it only touches the feedlot module), but Phases B, C, and D must be done in order after the native stocker module (Segment 3) is merged.

# 4. Phase A — Production System Flag

## Overview

BeefGEM uses a single binary flag (HERD row0 col10 in the .frm input file) to switch between grain-confined feedlot and grass-finished production systems. This flag is decoded as finishing_confined (bool) in simulate.py and routes the animal group to a completely different enteric CH₄ equation. RuFaS currently has no such flag — all feedlot animals follow the same code path regardless of finishing system. This step adds it.

## Step A-1 — Add finishing_system to AnimalConfig and AnimalType

**Files to modify**

- animal_config.py

- animal_types.py

- animal_module_constants.py

**BeefGEM source**

simulate.py → finishing_confined: bool parameter; \_herd_enteric_ch4_by_group() routing logic

**Code change — animal_config.py**

Add to the feedlot section of AnimalConfig (alongside feedlot_entry_weight, etc.):

```python
finishing_system: str = "grain_fed" # "grain_fed" | "grass_fed"
```

The default is "grain_fed" (existing feedlot behaviour is unchanged). When set to "grass_fed", the animal group uses the Mits3 enteric CH₄ model instead of the finishing equation.

**Code change — animal_types.py**

Add a boolean property to AnimalType:

```python
@property
def is_grass_finished(self) -> bool:
return (self.is_feedlot and AnimalConfig.finishing_system == "grass_fed")
```

**Code change — animal_module_constants.py**

Add valid system values:

```python
FINISHING_SYSTEM_GRAIN = "grain_fed"
FINISHING_SYSTEM_GRASS = "grass_fed"
```

**Test checkpoint A-1**

- Write test_finishing_system_flag.py FIRST

- Test that finishing_system="grain_fed" keeps existing code path (regression)

- Test that is_grass_finished returns True when finishing_system="grass_fed" for FEEDLOT_STEER

- Test that is_grass_finished returns False for BEEF_COW and dairy types

# 5. Phase B — Backgrounding / Stocker Module

## Overview

The stocker/backgrounding phase is the bridge between the cow-calf segment and the feedlot. BeefGEM models it as a 6-month forage-based growing phase (stocker_mo=6 in ReproStrategy, herd_dynamics.py). In RuFaS, building the native stocker module is Segment 3 of your roadmap (next pending). This Phase B does NOT duplicate that work — it instead describes the BeefGEM-specific enhancements to apply ON TOP of the native stocker module once it is complete: specifically the backgrounding enteric CH4 equation (R-CH4-ENT-003), the limit-feeding configuration lever, and the compensatory gain trigger.

IMPORTANT: Steps B-1 and B-2 in this phase assume BEEF_STOCKER_STEER/HEIFER types, BeefStockerRequirementsCalculator, and the stocker-to-feedlot transfer logic already exist from Segment 3. If those do not exist yet, skip this phase and return to it after the native stocker module PR is merged.

## Step B-1 — Add STOCKER Animal Type and Enums

**Files to modify**

- animal_types.py

- animal_combination.py

- animal_grouping_scenarios.py

- animal_constants.py

**BeefGEM source**

herd_dynamics.py → LIVE = ('cows','calves','young_heifers','yearling_heifers','stockers','finishing')

herd_dynamics.py → stockers_to_finishing() → D-STOCKER-TO-FINISH-001

**Code change — animal_types.py**

Add after BEEF_BULL:

```python
BEEF_STOCKER_STEER = 'BeefStockerSteer'
BEEF_STOCKER_HEIFER = 'BeefStockerHeifer'
@property
def is_beef_stocker(self) -> bool:
return self in (AnimalType.BEEF_STOCKER_STEER, AnimalType.BEEF_STOCKER_HEIFER)
```

**Code change — animal_combination.py**

Add:

```python
BEEF_STOCKER = "beef_stocker"
```

**Code change — animal_constants.py**

Add event string constants:

```python
STOCKER_ENTRY = "stocker entry"
STOCKER_TO_FEEDLOT = "stocker to feedlot transfer"
STOCKER_MAX_DAYS = "stocker max days reached"
```

**Code change — animal_grouping_scenarios.py**

Add a COW_CALF_STOCKER_FEEDLOT scenario that includes all three stages in one simulation:

```python
COW_CALF_STOCKER_FEEDLOT: { AnimalCombination.BEEF_COW_CALF: [BEEF_COW, BEEF_CALF, BEEF_HEIFER_REPLACEMENT, BEEF_BULL], AnimalCombination.BEEF_STOCKER: [BEEF_STOCKER_STEER, BEEF_STOCKER_HEIFER], AnimalCombination.FEEDLOT_FINISHING: [FEEDLOT_STEER, FEEDLOT_HEIFER], }
```

**Test checkpoint B-1**

- Write test_stocker_enums.py FIRST — confirm BEEF_STOCKER_STEER/HEIFER appear in is_beef_stocker, are absent from is_feedlot, is_beef_cow_calf, and is_grass_finished

- Confirm BEEF_STOCKER maps to a distinct, non-shared list in animals_by_type (Lesson 1 regression test)

## Step B-2 — Build BeefStockerRequirementsCalculator

**Files to create/modify**

- beef_stocker_requirements_calculator.py (new file)

- nrc_requirements_calculator.py (dispatch hook)

- animal.py (\_initialize_stocker_animal, stocker daily routines)

- animal_module_constants.py (stocker constants)

- animal_config.py (stocker config parameters)

- herd_manager.py (beef_stocker_animals property)

- ration_manager.py (stocker forage-based ration)

- animal_module_reporter.py (report_stocker_performance)

**BeefGEM source**

methane.py → enteric_ch4_backgrounding() — R-CH4-ENT-003 (NASEM 2016, eq 6.8)

physiology.py → group_physiology('stockers', csbw_kg) — DMI as fraction of BW (2.6%)

herd_dynamics.py → stockers_to_finishing() — D-STOCKER-TO-FINISH-001 (monthly fraction transfer)

**Key constants to add to animal_module_constants.py**

| **Constant**                  | **Value** | **Source / Note**                                      |
|-------------------------------|-----------|--------------------------------------------------------|
| STOCKER_DMI_RATIO             | 0.026     | 2.6% BW/day — BeefGEM physiology.py 'stockers'         |
| STOCKER_MIN_ENTRY_WEIGHT_KG   | 180.0     | Minimum weaning weight for stocker placement           |
| STOCKER_TARGET_EXIT_WEIGHT_KG | 350.0     | NRC 2016: 300–400 kg feedlot entry weight              |
| STOCKER_TARGET_ADG_KG         | 0.8       | NRC 2016: mid-range of 0.35–1.15 kg/d on forage        |
| STOCKER_MAX_DAYS              | 210       | 7 months maximum backgrounding (BeefGEM: stocker_mo=6) |
| STOCKER_BRODY_K               | 0.00175   | BeefGEM physiology.py Brody curve k for stockers       |

**Key config parameters to add to AnimalConfig (stocker section)**

| **Parameter**          | **Default** | **Description**                                      |
|------------------------|-------------|------------------------------------------------------|
| stocker_entry_weight   | 240.0 kg    | Entry weight at weaning / stocker placement          |
| stocker_exit_weight    | 350.0 kg    | Weight threshold to transfer to feedlot              |
| stocker_max_days       | 210         | Maximum days in backgrounding before forced transfer |
| stocker_target_adg     | 0.8 kg/d    | Target ADG on forage diet                            |
| stocker_diet_system    | "pasture"   | "pasture" \| "drylot_forage" \| "limit_feed"         |
| stocker_limit_feed_pct | 85.0        | % of ad libitum DMI when limit_feed is used          |

**Backgrounding enteric CH₄ equation (from BeefGEM R-CH4-ENT-003)**

The NASEM 2016 backgrounding equation replaces the feedlot finishing equation for stocker animals:

\# R-CH4-ENT-003 (NASEM 2016, eq 6.8) — Backgrounding cattle \# Units: kg CH4/head/day (divide g result by 1000) def enteric_ch4_backgrounding(bw_kg, dmi_kg_day, fat_frac): g_per_day = 71.5 + 0.12\*bw_kg + 0.01\*(dmi_kg_day\*\*3) - 244.8\*fat_frac return max(0.0, g_per_day) / 1000.0

This must be wired into the nutrition supply calculator for BEEF_STOCKER_STEER and BEEF_STOCKER_HEIFER, replacing the feedlot finishing equation used by FEEDLOT_STEER/HEIFER.

**Weaning dispatch extension (\_beef_weaning_event in animal.py)**

Extend the existing dispatch logic from the cow-calf integration plan to add a stocker destination:

elif destination == "stocker": self.animal_type = (AnimalType.BEEF_STOCKER_STEER if self.sex == Sex.STEER else AnimalType.BEEF_STOCKER_HEIFER) self.\_initialize_stocker_animal({ "body_weight": self.body_weight, "target_exit_weight": AnimalConfig.stocker_exit_weight, "days_in_stocker": 0, }) return AnimalStatus.LIFE_STAGE_CHANGED

**Stocker-to-feedlot transfer (\_stocker_life_stage_update in animal.py)**

Daily check mirrors the feedlot slaughter-weight check but transfers the animal instead of selling:

```python
def _stocker_life_stage_update(self, time: RufasTime) -> AnimalStatus:
self.days_in_stocker += 1
if (self.body_weight >= AnimalConfig.stocker_exit_weight or
self.days_in_stocker >= AnimalConfig.stocker_max_days):
self.events.append(animal_constants.STOCKER_TO_FEEDLOT)
self.animal_type = (AnimalType.FEEDLOT_STEER
if
self.sex == Sex.STEER else AnimalType.FEEDLOT_HEIFER)
self._initialize_feedlot_animal({ "body_weight":
self.body_weight, "mature_body_weight": AnimalConfig.feedlot_slaughter_weight, "days_on_feed": 0, })
return AnimalStatus.LIFE_STAGE_CHANGED
return AnimalStatus.ALIVE
```

**Test checkpoint B-2**

- Write test_stocker_requirements_calculator.py FIRST — validate energy requirements for a 240 kg Angus stocker at 0.8 kg/d ADG against NRC 2016 Chapter 12

- Write test_stocker_lifecycle.py — test that a stocker animal at stocker_exit_weight triggers STOCKER_TO_FEEDLOT event and becomes FEEDLOT_STEER in the same day

- Write test_stocker_to_feedlot_handoff.py — test HerdManager list membership changes from beef_stocker_animals to feedlot_animals in same simulation day

- Write test_weaning_to_stocker.py — test that a BEEF_CALF with destination="stocker" becomes BEEF_STOCKER_STEER/HEIFER at weaning

# 6. Phase C — Herd Population Dynamics and Scenario Levers

## Overview

BeefGEM's herd_dynamics.py models the whole beef herd as a population with conservation-enforced transitions: calving → mortality → weaning → heifer development → cull+refill → stocker → finishing → sold. This is driven by a ReproStrategy dataclass with six management levers that your supervisor wants to vary as scenarios.

RuFaS's cow-calf integration plan handles the calving/weaning/culling logic for individual animals with daily resolution. This Phase adds a herd-level population summary layer on top of the existing daily individual-animal logic — enabling the scenario comparisons your supervisor wants without replacing the individual-animal simulation.

## BeefGEM ReproStrategy Parameters — the Scenario Levers

| **Parameter**  | **BeefGEM Default** | **Range** | **Effect on Production**                                                            |
|----------------|---------------------|-----------|-------------------------------------------------------------------------------------|
| calving_month  | 4 (April)           | 1–12      | Shifts calving season; drives seasonal feed demand, calf age at feedlot entry       |
| weaning_age_mo | 7 months            | 5–8 mo    | Earlier weaning → lighter calves, reduced cow energy demand; later → heavier calves |
| cull_rate      | 0.15 (15%/yr)       | 0.10–0.25 | Higher cull rate → more replacement heifers needed → more stocker animals           |
| calf_mortality | 0.15 (15%)          | 0.05–0.25 | Affects calf crop weaned per cow exposed; directly impacts herd productivity        |
| stocker_mo     | 6 months            | 4–9 mo    | Longer backgrounding → heavier feedlot entry weight, different energy profile       |
| calving_rate   | 1.0                 | 0.80–0.98 | Conception success; 0.85 = USDA 2007 national average (85.5% calf crop weaned)      |

## Step C-1 — Add BeefHerdScenario Config and ReproStrategy Equivalent

**Files to modify**

- animal_config.py (add beef_herd_scenario section)

- animal_module_constants.py (scenario defaults)

- animal_typed_dicts.py (BeefHerdScenarioDict type)

**Code change — animal_config.py**

Add a new BeefHerdScenario config class (separate from AnimalConfig feedlot params):

\# Mirrors BeefGEM ReproStrategy dataclass (herd_dynamics.py) @dataclass class BeefHerdScenario: calving_month: int = 4 \# 1-12 (April spring calving default) weaning_age_mo: int = 7 \# months (5-8 range) cull_rate: float = 0.15 \# fraction/yr (15% default) calf_mortality: float = 0.15 \# fraction over nursing period stocker_mo: int = 6 \# months in backgrounding calving_rate: float = 0.915 \# USDA 2007 average (91.5%) post_weaning_dest: str = "stocker" \# "stocker"\|"direct_to_feedlot"\|"sell" def \_\_post_init\_\_(self): assert 1 \<= self.calving_month \<= 12 assert 5 \<= self.weaning_age_mo \<= 12 assert 0.0 \<= self.cull_rate \<= 0.5 assert 0.0 \<= self.calf_mortality \<= 0.5 assert 0.0 \< self.calving_rate \<= 1.0

**Test checkpoint C-1**

- Write test_beef_herd_scenario.py — validate all field range assertions trigger correctly on out-of-bound inputs

- Test that calving_month=4, weaning_age_mo=7 produces wean_month=11 (November) as expected

## Step C-2 — Herd Population Summary Reporter

**Files to modify**

- animal_module_reporter.py (report_beef_herd_population_summary)

- herd_manager.py (beef population properties)

**What to report (mirrors BeefGEM HerdState fields)**

Each simulation year, add a herd population summary output. This is the aggregate view your supervisor wants for scenario comparison:

| **Output Field**             | **BeefGEM Source**             | **Calculation in RuFaS**                            |
|------------------------------|--------------------------------|-----------------------------------------------------|
| calf_crop_weaned_pct         | D-WEAN-001 survivors/cows      | weaned_calves_this_year / cows_exposed × 100        |
| calving_interval_days        | calving_month cycle            | mean(days between successive calvings per cow)      |
| herd_cull_count              | D-CULL-REFILL-001 culled       | sum of BEEF_COW animals with CULLED event this year |
| replacement_heifers_entering | yearlings entering cow herd    | BEEF_HEIFER_REPLACEMENT → BEEF_COW transitions      |
| stocker_to_feedlot_count     | D-STOCKER-TO-FINISH-001        | STOCKER_TO_FEEDLOT events this year                 |
| feedlot_finished_count       | D-FINISH-SELL-001 sold         | SLAUGHTER_WEIGHT_REACHED events this year           |
| mean_stocker_entry_weight_kg | group_body_weight('stockers')  | mean BW of all stocker-entry events this year       |
| mean_feedlot_entry_weight_kg | group_body_weight('finishing') | mean BW of all feedlot-entry events this year       |

**Test checkpoint C-2**

- Write test_beef_herd_reporter.py FIRST — run a 2-year simulation with 80 cows and assert calf_crop_weaned_pct is within 70–100% range (not a specific number — simulation variance is expected)

- Assert calving_interval_days is within ±10% of 365 days for once-per-year calving (mirrors Step 10.2 assertion from the cow-calf integration plan)

- Mark with @pytest.mark.integration — requires HerdManager, Animal, and ReporterOutputManager

## Step C-3 — Scenario Runner and Comparison Output

**Files to create**

- beef_scenario_runner.py (new utility module)

**Purpose**

This is the feature your supervisor wants most: the ability to vary a scenario lever (e.g., calving month, weaning age, cull rate) and compare outcomes across runs. BeefGEM does this by instantiating different ReproStrategy objects and calling simulate() for each. RuFaS should replicate this pattern using BeefHerdScenario.

**Key scenarios to enable (matching your supervisor's interest)**

| **Scenario Name**       | **Parameter Changed**                 | **Expected Effect**                                                                              |
|-------------------------|---------------------------------------|--------------------------------------------------------------------------------------------------|
| spring_calving_baseline | calving_month=4, weaning_age_mo=7     | Reference: April calving, November weaning, standard Canadian spring pattern                     |
| fall_calving            | calving_month=10, weaning_age_mo=7    | October calving; calves weaned in spring; different seasonal feed demand pattern                 |
| early_weaning           | weaning_age_mo=5                      | Reduces cow energy demand post-calving; lighter calves entering stocker phase                    |
| extended_backgrounding  | stocker_mo=9                          | Heavier feedlot entry weight (~400 kg); more forage consumed; fewer finishing days               |
| high_conception_rate    | calving_rate=0.95                     | More calves per cow exposed; surplus heifers available for sale not replacement                  |
| low_conception_rate     | calving_rate=0.80                     | 80% calving rate; replacement heifers may be insufficient to maintain herd size                  |
| aggressive_culling      | cull_rate=0.22                        | 22% annual cull — more replacement pressure; affects stocker/feedlot throughput                  |
| direct_to_feedlot       | post_weaning_dest='direct_to_feedlot' | Skip backgrounding; lighter calves go straight to feedlot; tests early-weaning feedlot economics |

**Scenario runner code structure**

\# beef_scenario_runner.py def run_scenario(scenario: BeefHerdScenario, years: int = 3) -\> dict: """Run a single scenario and return a summary dict for comparison.""" AnimalConfig.set_beef_herd_scenario(scenario) herd = HerdFactory.create_beef_herd(...) sim = Simulation(herd, years=years) sim.run() return AnimalModuleReporter.get_beef_herd_summary(sim) def compare_scenarios(scenarios: dict\[str, BeefHerdScenario\], years: int = 3) -\> pd.DataFrame: """Run multiple named scenarios and return a comparison DataFrame.""" results = {name: run_scenario(s, years) for name, s in scenarios.items()} return pd.DataFrame(results).T

**Test checkpoint C-3**

- Write test_scenario_runner.py — run spring_calving_baseline and fall_calving scenarios back-to-back

- Assert that calving season shifts the month of peak calf counts in the herd reporter output

- Assert compare_scenarios returns a DataFrame with one row per scenario name and columns for all reporter fields

# 7. Phase D — Environmental Stress and Performance Modifiers

## Overview

BeefGEM includes two management modifiers that affect animal performance but are absent from the current RuFaS beef module: heat stress (THI-based DMI and ADG reduction) and compensatory gain (enhanced ADG after a period of nutritional restriction). The feedlot module currently handles cold stress and mud condition — this phase adds the heat stress counterpart and compensatory gain.

## Step D-1 — Heat Stress (THI-Based DMI and NEm Modifier)

**Files to modify**

- beef_nrc_requirements_calculator.py (\_calculate_dmi, \_calculate_maintenance_energy)

- animal_module_constants.py (THI thresholds)

- animal_config.py (heat_stress_thi_threshold)

**BeefGEM source**

simulate.py → io_wth.py → monthly_mean_temps() used for storage temperature (weather file integration)

NRC 2016 Chapter 15 provides the beef-specific THI equations for DMI and performance reduction

**THI calculation and thresholds**

\# THI = Temperature-Humidity Index \# NRC 2016 Ch. 15 / USDA heat stress thresholds def calculate_thi(temp_c: float, rh_pct: float) -\> float: temp_f = temp_c \* 9/5 + 32 return (0.8 \* temp_f) + (rh_pct/100) \* (temp_f - 14.4) + 46.4 \# Thresholds (add to animal_module_constants.py) THI_MILD_STRESS_THRESHOLD = 72.0 \# onset of mild heat stress THI_MODERATE_STRESS_THRESHOLD = 80.0 \# moderate stress THI_SEVERE_STRESS_THRESHOLD = 90.0 \# severe stress \# DMI reduction fractions by THI class (NRC 2016 Table 15-1) THI_DMI_MULTIPLIER = { "none": 1.00, "mild": 0.95, \# 5% DMI reduction "moderate": 0.88, \# 12% DMI reduction "severe": 0.75, \# 25% DMI reduction } \# NEm multiplier for thermoregulation in heat (NRC 2016 Ch. 15) THI_NEm_MULTIPLIER = { "none": 1.00, "mild": 1.07, \# panting increases maintenance "moderate": 1.12, "severe": 1.20, }

**Code change — beef_nrc_requirements_calculator.py**

Extend \_calculate_dmi() and \_calculate_maintenance_energy() to accept thi_class: str = 'none' alongside the existing temperature_c parameter:

\# In \_calculate_dmi(): dmi \*= AnimalModuleConstants.THI_DMI_MULTIPLIER.get(thi_class, 1.0) \# In \_calculate_maintenance_energy(): ne_m \*= AnimalModuleConstants.THI_NEm_MULTIPLIER.get(thi_class, 1.0)

**Test checkpoint D-1**

- Write test_heat_stress.py — test that DMI at THI_class='severe' is 25% lower than at THI_class='none' for the same animal

- Test that THI_class='none' produces identical output to current (no-heat-stress) implementation (regression guard)

- Test calculate_thi(35.0, 80.0) gives expected value within ±0.1 of manual calculation

## Step D-2 — Compensatory Gain

**Files to modify**

- animal.py (compensatory_gain_factor attribute)

- beef_nrc_requirements_calculator.py (\_calculate_growth_energy)

- animal_config.py (enable_compensatory_gain: bool)

- animal_module_constants.py (CG constants)

**BeefGEM source**

BeefGEM documents compensatory gain as an ADG multiplier applied to animals coming off restricted diets. The CHM attributes enhanced feed efficiency after restriction to mobilization of muscle protein during the restriction period. BeefGEM applies it as a flat factor during the first post-restriction phase.

**Implementation approach (NRC 2016 Ch. 12)**

\# animal.py — add to Animal.\_\_init\_\_: self.days_restricted: int = 0 \# days on restricted intake self.compensatory_gain_factor: float = 1.0 \# 1.0 = no CG; \>1.0 = enhanced gain \# animal_module_constants.py: CG_RESTRICTION_THRESHOLD_DAYS = 21 \# minimum restriction period to trigger CG CG_MIN_INTAKE_FRACTION = 0.70 \# below this fraction of ad lib = restricted CG_MAX_ADG_MULTIPLIER = 1.25 \# cap to prevent biological implausibility CG_DECAY_RATE_PER_DAY = 0.02 \# CG advantage declines 2%/day after restriction ends \# In \_calculate_growth_energy(): effective_adg = target_adg \* implant_adg_factor \* compensatory_gain_factor effective_adg = min(effective_adg, target_adg \* AnimalModuleConstants.CG_MAX_ADG_MULTIPLIER)

**When compensatory gain is triggered**

- A stocker animal on a limit-feed program (stocker_diet_system='limit_feed', stocker_limit_feed_pct \< 80%) accumulates days_restricted

- On transfer to the feedlot (\_stocker_life_stage_update), compensatory_gain_factor is set from days_restricted via a lookup table

- The factor decays by CG_DECAY_RATE_PER_DAY until it reaches 1.0

- If enable_compensatory_gain=False in AnimalConfig, compensatory_gain_factor is always 1.0 (default off — maintains backward compatibility)

**Test checkpoint D-2**

- Write test_compensatory_gain.py — test that 30 days of restricted intake (65% ad lib) produces compensatory_gain_factor \> 1.0 on feedlot entry

- Test that CG decays correctly: after CG_DECAY_RATE_PER_DAY × days, factor should approach 1.0

- Test that enable_compensatory_gain=False always returns factor=1.0 regardless of restriction history (regression guard for default config)

# 8. Step Summary Table

| **Phase** | **Step** | **Title**                                             | **Files Touched**                                                                                      | **Effort** | **Priority** |
|-----------|----------|-------------------------------------------------------|--------------------------------------------------------------------------------------------------------|------------|--------------|
| A         | A-1      | Production system flag (grain vs. grass-finished)     | animal_config.py, animal_types.py, animal_module_constants.py                                          | 0.5 day    | High         |
| B         | B-1      | BEEF_STOCKER enums and combinations                   | animal_types.py, animal_combination.py, animal_grouping_scenarios.py, animal_constants.py              | 0.5 day    | High         |
| B         | B-2      | BeefStockerRequirementsCalculator + stocker lifecycle | beef_stocker_requirements_calculator.py (new), animal.py, herd_manager.py, ration_manager.py, reporter | 3–4 days   | High         |
| C         | C-1      | BeefHerdScenario config and ReproStrategy equivalent  | animal_config.py, animal_module_constants.py, animal_typed_dicts.py                                    | 1 day      | High         |
| C         | C-2      | Herd population summary reporter                      | animal_module_reporter.py, herd_manager.py                                                             | 1.5 days   | High         |
| C         | C-3      | Scenario runner and comparison output                 | beef_scenario_runner.py (new)                                                                          | 1 day      | High         |
| D         | D-1      | Heat stress — THI-based DMI and NEm modifier          | beef_nrc_requirements_calculator.py, animal_module_constants.py, animal_config.py                      | 1 day      | Medium       |
| D         | D-2      | Compensatory gain after restriction                   | animal.py, beef_nrc_requirements_calculator.py, animal_config.py, animal_module_constants.py           | 1.5 days   | Medium       |

**Total estimated effort: 10–11 developer-days across 8 steps, 4 phases.**

# 9. Test-Driven Development Requirements

This plan follows the same TDD discipline as the feedlot and cow-calf integration plans. The mandatory sequence for every step:

- Write the failing test FIRST (red)

- Implement the minimum code to pass (green)

- Refactor without breaking the test

- 100% branch coverage expected on all new code

Test markers to use (from the RuFaS beef module testing skill):

- @pytest.mark.unit — for equation-level tests (THI calculation, CG factor, stocker requirements)

- @pytest.mark.component — for lifecycle event tests (stocker-to-feedlot transfer)

- @pytest.mark.integration — for multi-module herd simulation tests (Steps C-2, C-3)

- @pytest.mark.regression — for backward-compatibility guards (finishing_system='grain_fed' default unchanged)

# 10. Explicit Scope Boundaries

The following are named gaps in this plan — documented here so they can be tracked as future PRs and not accidentally missed:

| **Named Gap**                                                                              | **Future PR Candidate**                                                                                                                |
|--------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| Brody growth curve for stocker body weight (BeefGEM physiology.py CSBW model)              | Beef growth curve enhancement PR — currently using daily NRC 2016 equations which are superior but have different structure            |
| Pasture DMI supply-driven grazing fraction (BeefGEM grazing_capacity_fraction)             | Pasture module integration — requires pasture DM availability input from the crop module                                               |
| Ionophore (monensin) DMI reduction (3–5% reduction, BeefGEM documented but not quantified) | Additive effects PR — add monensin_dmi_reduction_pct to AnimalConfig alongside enable_compensatory_gain                                |
| Implant ADG factor quantification (BeefGEM documents but does not quantify the multiplier) | Implant product database — map implant product names to ADG multipliers from product labels or USDA data                               |
| Body condition scoring (BCS) effect on reproduction                                        | BCS module — BeefGEM's calving_rate lever implicitly captures BCS effects; explicit BCS tracking is needed for the reproduction module |

*Sources: BeefGEM beefgem-rules-main (USDA/ARS, Rotz et al.); NRC (2016) Nutrient Requirements of Beef Cattle, 8th Revised Edition; RuFaS Feedlot Implementation Plan (PR \#32); RuFaS CowCalf Integration Plan. Prepared June 2026, McGill University.*

