# Design — BeefGEM Management Enhancement Layer

## Architecture overview

BeefGEM sits on top of the three native segments. It does not
replace or modify the core NRC 2016 equations — it applies
multipliers and routes to alternative equations based on config flags.

## Phase A design

### FinishingSystem enum
Plain Enum (not str,Enum — house rule enforced by reviewer):
```python
class FinishingSystem(Enum):
    GRAIN_FED = "grain_fed"   # default — no behavior change
    GRASS_FED = "grass_fed"   # routes to Mits3 CH4
```

### CH4 routing
In AnimalModuleReporter.report_feedlot_performance():
```python
if AnimalConfig.finishing_system is FinishingSystem.GRASS_FED:
    ch4 = BeefNRCRequirementsCalculator.calculate_enteric_ch4_grass_fed(dmi)
else:
    ch4 = BeefNRCRequirementsCalculator.calculate_enteric_ch4_grain_fed(dmi)
```

## Phase B design

### Limit-feeding DMI cap
Applied inside BeefStockerRequirementsCalculator after base DMI:
```python
if inputs.diet_system is StockerDietSystem.LIMIT_FEED:
    dmi = dmi * (AnimalConfig.stocker_limit_feed_pct / 100.0)
```

### Stocker forage enteric CH4
```python
# Linear in DMI; no NRC 2016 equation number identified for the coefficients
ch4_g_d = BEEF_CH4_STOCKER_FORAGE_INTERCEPT + BEEF_CH4_STOCKER_FORAGE_SLOPE * dmi
# = 10.04 + 23.7 × dmi
```
The source document labels this "NASEM 2016, eq 6.8", but Ch.6 is protein and
amino acids and enteric methane is Ch.16. See the provenance note in the plan.
The intercept is non-zero, so callers representing a phase an animal never
entered must short-circuit rather than evaluate at zero intake.

## Phase C design

### BeefHerdScenario dataclass
Immutable configuration object. All fields validated at construction.
Passed to run_scenario() which applies fields to AnimalConfig before
running the simulation.

### compare_scenarios() return shape
One row per scenario name, 8 columns (herd summary metrics).
Requires pandas — already common in scientific Python stack.
If pandas is not acceptable, return List[dict] instead (config toggle).

### Herd summary metrics computation
Computed from live HerdManager state at end of simulation:
- calf_crop_pct: from cow event history (BEEF_CALVING events)
- mean_calving_interval_days: from consecutive BEEF_CALVING events
- replacement_rate_pct: len(beef_replacement_heifers) / len(beef_cows)
- mean_cow_bcs: mean of body_condition_score_9 across beef_cows
Four further metrics were specified and then cut, because nothing in current
state retains what they would summarise. They are absent from the returned
dict rather than zero, so a consumer cannot mistake an unwired metric for a
real measurement:

- mean_stocker_adg_kg_d: CUT — exit performance is written to the output
  manager and discarded; no herd-level accumulator exists
- mean_feedlot_adg_kg_d: CUT — same, and report_feedlot_performance is never
  called in production
- mean_feedlot_days_on_feed: CUT — same as above
- total_enteric_ch4_g_d: CUT — digestion supports dairy types only, so beef
  animals produce no daily methane to sum

## Phase D design

### THI calculation
```python
# NRC 2016 Ch.11
t_f = 1.8 * temperature_c + 32
thi = t_f - (0.55 - 0.0055 * relative_humidity_pct) * (1.8 * temperature_c - 26)
```

### Heat stress modifiers
Piecewise-linear interpolation between the four class values the BeefGEM
source reports as a step function. Applied after base DMI and NEm:
```python
dmi *= _interpolate_heat_stress(thi, BEEF_HEAT_STRESS_DMI_MULTIPLIERS)
ne_m *= _interpolate_heat_stress(thi, BEEF_HEAT_STRESS_NEm_MULTIPLIERS)
```
`BEEF_THI_BREAKPOINTS` is `(72.0, 80.0, 90.0)`; each multiplier tuple holds
three values pairing one-to-one with the anchors — DMI `(1.00, 0.88, 0.75)`,
NEm `(1.00, 1.12, 1.20)`. Below and at 72 the multiplier is 1.00; above 90 it
clamps to the last value. THI 72 is the onset of stress, so the response rises
continuously from 1.00 with no step at the threshold. The source's mild-class
values (0.95, 1.07) are not anchors; they fall out of the interpolation at
THI 75.33 and 76.67, inside the mild band. No zero floor is needed because
every multiplier is positive and the result is bounded by the tuple.

### Humidity source
`relative_humidity_pct` is a static `AnimalConfig` field validated to
0-100 and finite, not a daily weather input. `CurrentDayConditions` and the
weather input schema are unchanged; threading daily humidity through them is
a future-PR candidate.

### Compensatory gain decay
After restriction ends, CG advantage decays linearly:
```python
self.compensatory_gain_factor = max(
    1.0,
    self.compensatory_gain_factor - CG_DECAY_RATE_PER_DAY
)
```
Ceiling enforced at CG_MAX_ADG_MULTIPLIER = 1.25 at all times.

## Backward compatibility design
Every new field has a default that preserves current behavior:
| Field | Default | Behavior at default |
|-------|---------|---------------------|
| finishing_system | GRAIN_FED | Identical to pre-BeefGEM feedlot |
| stocker_diet_system | PASTURE | No DMI change |
| relative_humidity_pct | None | No THI calculated |
| enable_compensatory_gain | False | CG factor = 1.0 always |
