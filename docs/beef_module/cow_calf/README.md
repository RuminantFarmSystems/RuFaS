# Beef Cow-Calf Module — Scope Boundaries and Known Simplifications

Implementation across PR-A (#33), PR-B (#34), PR-C (#35), PR-D (this PR).

## Named Scope Boundaries (explicitly not implemented)

The following were explicitly named and deferred in the integration plan (Lesson 7):

1. **Simplified conception model** (Step 5.3): a single daily-probability draw rather than a
   full 21-day estrus cycle model. Aggregate herd pregnancy rate matches the USDA 85.5%
   calf-crop-weaned reference at a seasonal level; individual estrus timing is not modeled.

2. **Static seasonal ration** (Step 6.1): grazed-pasture composition is a static user config
   input per ration, not a dynamic month-by-month lookup from NRC 2016 Table 18-2 (Grazed
   Forages tab). Future PR: implement seasonal forage composition lookup by species/region/month.

3. **No stocker/backgrounding intermediate phase** (Step 8.1): `direct_to_feedlot` destination
   sends a freshly weaned calf (typically 240 kg) directly to FEEDLOT_STEER/HEIFER at weaning
   weight, skipping the stocker/backgrounding growing phase (NRC 2016: 300–400 kg typical feedlot
   entry weight). Future PR: stocker/backgrounding module.

4. **Flat forage_quality_factor** (Step 7.3): pasture intake adjustment is a single config-driven
   float rather than a full pasture-growth model or per-paddock forage mass. Future PR: integrate
   pasture biomass from the field subsystem into DMI adjustment.

5. **Grazing activity energy cost** not modeled separately: NRC 2016 does not include a separate
   grazing-activity multiplier beyond the L and COMP terms already in the NEm equation (Step 3.2).
   No extra multiplier was added. Confirmed against the verified inventory equations.

## Integration Test Scope (Option B)

The 730-day integration test (`test_beef_integration.py`) covers one complete calving-weaning cycle
plus a second breeding season confirmed active. A second calving (day ~738) falls outside the 730-day
window because `_initialize_beef_cow_calf_herd` creates all cows with `days_in_pregnancy=0`.
Implementing `initial_pregnancy_distribution` to enable two full calving cycles within 730 days
is deferred to a future PR.

## Reference Sources

- NRC 2016 Beef Cattle Nutrient Requirements (9th rev.) — Chapters 6, 11, 12, 13, 19
- USDA NAHMS Beef 2007–2017 survey data (calf crop weaned, weaning age/weight, mature cow weight)
- `NRC2016_Beef_Requirements_Calculator_Inventory_Final.xlsx` — verified equation inventory
- `NRC2016_BeefCattle_FeedLibrary_Complete.xlsx` — feed IDs 401+ (Cow-Calf CC tab)
