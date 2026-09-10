# Silage Preseal + Infiltration Phases — Design Spec

Status: Draft, ready for whiteboard/SME + team review (rufas-design-doc gate) — updated 2026-09-08
Date: 2026-08-19
Scope: `RUFAS/biophysical/feed_storage/silage.py`, `storage.py`, `crop_soil_to_feed_storage_connection.py`, feed-storage input schema

## 1. Motivation

RuFaS's silage module currently implements 2 of IFSM's 5 documented ensiling phases (Effluent, Fermentation). Preseal, Infiltration, and Feed-out are entirely absent. This spec covers restoring **Preseal** and **Infiltration** only. Effluent and Fermentation are explicitly untouched — they're considered established and out of scope for this work, even though the prior audit (Section 6) found real bugs in them.

Sources used to derive this design:
- `docs/beef_module/` sibling reference pattern (N/A here — see below instead)
- IFSM Reference Manual: `c:\researchLife\05-dev\msf\fourrager\04_Resources\IFSM Reference Manual.md` (prose description, phase overview, some equations — several equations are only present as stripped images in this file and are **not** authoritative for exact math)
- **IFSM Fortran source (authoritative for equations)**: `c:\researchLife\05-dev\msf\fourrager\04_Resources\Silostg.for` — subroutines `SILO` (orchestrator, lines 210-631), `PRESEAL` (634-714), `FERMENT` (717-791, reference only, not being changed), `TOWER` (794-876, infiltration — radial), `BUNKER` (879-984, infiltration — vertical section), `EFFLU` (987-1026, reference only, not being changed), `FEEDOUT` (1029-1104, out of scope this round)

All equation references below cite `Silostg.for` line numbers as the source of truth. This spec does not re-derive or restate every line of Fortran arithmetic — it describes structure, data flow, and the decisions made translating an offline/batch model into RuFaS's incremental daily/interval simulation. Implementers should read the cited subroutine directly for exact constants.

## 2. Explain-it-to-future-me notes

These are plain-language explanations preserved verbatim for whoever (including future-you) needs to re-orient on this design without re-reading Fortran.

### 2.1 Why Preseal can't be computed the instant a crop is stored

When a truck dumps a load of chopped silage into a bunker, that pile sits exposed to open air until the next truckload gets dumped on top of it (burying it) or the crew finishes and covers the whole bunker with plastic. During that exposed window the crop is still breathing (aerobic respiration) and losing dry matter — the longer it sits uncovered, the more it loses. So the loss depends on **how long that specific load sat exposed before something covered it**.

IFSM doesn't have a problem with this because it isn't a day-by-day simulator for this part — it waits until the entire silo-filling process for the season is finished, so it already knows the full delivery schedule (load 1 at 9am, load 2 at 11am, etc.). Once the full list is known, "how long was load 1 exposed" is trivial: `(load 2's arrival time) − (load 1's arrival time)`.

RuFaS can't do that trick — it runs forward in time one interval at a time. When load 1 arrives *today*, RuFaS doesn't know whether load 2 is coming tomorrow, next week, or never. So at the moment load 1 arrives, we can't yet calculate its preseal loss, because the number we need depends on something that hasn't happened yet in the simulation.

**Fix:** don't compute load 1's preseal loss the instant it arrives. Compute it retroactively, at the first moment we do know the answer:
- If load 2 later arrives in the same storage → we now know load 1's exposure time (`load2.storage_time − load1.storage_time`, capped at 3 days per source), so we finalize load 1's preseal loss then.
- If nothing ever arrives on top of it → use the same fallback the source uses for "the newest load with nothing on top of it yet": a fixed 0.125 days (3 hours), applied when that load first needs its other losses processed.

It's a timing problem, not a math problem — we're moving *when* we compute this number to whenever we first have enough information to compute it correctly.

### 2.2 What "RS conservation" means here

As infiltration eats into the crop from the oxygen front inward, it's specifically consuming the *respirable* part of the dry matter — the sugars/starches aerobic microbes can actually burn. Fiber (NDF) and protein aren't respirable, so as more of the crop degrades, what's left is proportionally more fiber/protein and less respirable material — like squeezing a sponge, eventually there's nothing left to squeeze. The rule: **infiltration can never claim to have consumed more respirable substrate than the crop actually has left.** "How much respirable stuff is left" is computed fresh each time straight from the crop's current fiber/protein/ash percentages (fields that already exist) — nothing new to track. If the infiltration math ever tries to remove more than that, it's clipped at the ceiling instead of letting dry matter go negative.

In the source, this ceiling appears **only** in `TOWER`, `BUNKER`, and `FEEDOUT` — not in `FERMENT` or `EFFLU`. Those two phases are trusted to stay in-bounds by their own closed-form math over their validated ranges. This is why RS conservation is being introduced specifically as part of Infiltration, not retrofitted onto the existing Fermentation/Effluent code.

### 2.3 Bunker/Pile vs. Bag — two different infiltration shapes

**Bunker/Pile — front moves down from the open top**, like a bathtub slowly draining from the top: the exposed top layer is progressively more oxygen-damaged, and the damage front sinks deeper the longer it sits before feed-out starts consuming it from that same top surface.

**Bag — front moves inward from the wall**, radially: oxygen creeps in through the plastic tube wall toward the center, shrinking a cylindrical "safe zone."

These need genuinely different math (front sinking down a column vs. front shrinking inward radially) — `BUNKER` (source) for Bunker/Pile, `TOWER` (source) for Bag, matching the manual's explicit statement that bags/bales use the tower relationships.

## 3. Scope

**In scope:**
- Preseal phase for `Bunker`, `Pile`, `Bag` (all `Silage` subclasses)
- Infiltration phase for the same three classes, with RS conservation as its safety ceiling
- New per-crop state: temperature, initial pH estimate
- New per-storage config: geometry (width/height for Bunker/Pile, diameter for Bag) — optional, reference-table fallback
- Permeability: reference-table only, keyed by storage type, no per-farm override

**Out of scope (explicitly not touched):**
- Effluent (`silage.py`, existing) — established, not to be modified
- Fermentation (`storage.py`, existing, shared base class) — not to be modified
- Feed-out phase — separate future work
- Hay, Baleage, Grain storage types — Preseal/Infiltration are ensiling-specific
- Sourcing the actual reference-table values (geometry defaults, permeability defaults) — blocking prerequisite, tracked separately (Section 7)
- Fixing the bugs in Effluent/Fermentation identified in the prior audit (Section 6) — documented for awareness only

## 4. Architecture

```
receive_crop()  →  [Preseal loss finalized lazily — see 2.1]
                          ↓
process_degradations()  →  existing Effluent (unchanged) → existing Fermentation (unchanged)  →  Infiltration (new)
```

Preseal loss for crop N is finalized at the first of:
1. Crop N+1 being received into the same `Storage` (use `next.storage_time − crop.storage_time`, capped at 3 days), or
2. Crop N entering `process_degradations` for the first time with no successor yet received (use fixed 0.125 days), whichever happens first.

Once finalized, a crop's preseal loss is computed exactly once and never revisited (matches the source's one-shot-per-plot semantics — `Silostg.for:634-714`).

Infiltration runs inside `process_degradations`, after the existing Effluent → Fermentation sequence, using whichever of `BUNKER` or `TOWER` math applies to the crop's storage class (Section 5.2).

## 5. Component design

### 5.1 Preseal

Translates `PRESEAL` (`Silostg.for:634-714`). Key structural points for implementation (see source for exact constants):

- Respiration rate depends on crop type (haylage vs. corn silage — different `MUMAX` constant), current DM content, current temperature, and current pH.
- The subroutine internally steps through the exposure duration **one day at a time** (`Silostg.for:673-703`), because temperature rises each day from respiration heat, which feeds into the next day's respiration rate (positive feedback / self-heating). This internal day-stepping must be preserved — collapsing it into a single evaluation over the full exposure window would lose the self-heating effect.
- Mass-loss stoichiometry is **not** a simple 1:1 dry-matter removal: per `Silostg.for:697,708`, respiration converts dry matter to both CO₂ (leaves the system) and water (stays in the crop, raising moisture). The exact split (108g water retained / 72g gas lost per 180g dry matter respired, matching the manual's stated 108:180 ratio) must be preserved in the mass/DM-content update, not approximated as pure DM removal.
- Fiber (NDF) and protein (CP) concentrations increase via simple dilution as DM is lost (no chemical breakdown in this phase, unlike Fermentation's hemicellulose breakdown).
- Initial pH estimate (needed only for alfalfa's `FPH` respiration factor): defaults to the no-acid-treatment case, `FACID = 0`, which resolves to a fixed starting pH (`Silostg.for:271`, evaluated at `FACID=0`). RuFaS does not currently model silage additive treatments, so this is a hard default for v1, not a per-farm input.

### 5.2 Infiltration

Two implementations, dispatched by storage class:

| RuFaS class | Source subroutine | Front geometry | Permeability role (reference table only) |
|---|---|---|---|
| `Bunker` | `BUNKER` (`Silostg.for:879-984`) | Vertical section, front sinks from open top | Wall 4, cover 1 (cm/h) — `hf_silo_types.bunker_silo`, Buckmaster 1989. **Sourced.** |
| `Pile` | `BUNKER` (`Silostg.for:879-984`) | Vertical section, front sinks from open top | Wall 4, cover 4 (cm/h) — `hf_silo_types.pile_silo`, Buckmaster 1989. **Sourced.** |
| `Bag` | `TOWER` (`Silostg.for:794-876`), radial-diffusion portion only | Radial front shrinks inward from wall | 1.0 cm/h. **Sourced 2026-09-09** — IFSM Reference Manual (Rotz et al. 2023, v4.7), p.76-77: "Oxygen permeability is set to that for sealed plastic (1.0 cm/h) rather than that for a silo structure (4.0 cm/hr)" for bags/bales. Primary-source citation, supersedes the MSF table's blank `source` column. |

Reference table: `05-dev/msf/fourrager/02_Architecture/2026-08-26-hf-rt16-rt18-rt19-erd-proposal.md`
(`hf_silo_types`, RT-19), status "Draft — for supervisor validation before Jira/DDL" as of 2026-09-01.
RuFaS has no DB/CSV ingestion layer for this class of data (confirmed prior investigation) — these
values get mirrored as a hardcoded Python constant (e.g. `SILAGE_PERMEABILITY_CONSTANTS`, same pattern
as `ALFALFA_FERMENTATION_CONSTANTS` in `storage.py`), not queried live from the MSF DB.

**Unit question — RESOLVED 2026-09-09.** Checked directly against the primary source (Buckmaster,
Rotz & Muck 1989, *A Comprehensive Model of Forage Changes in the Silo*, Trans. ASAE 32(4):1143-1152
— `fourrager/04_Resources/1989 A Comprehensive Model of Forage Changes in the Silo.pdf`). The paper's
own Nomenclature (p. 1152) defines `U` plainly as "permeability, cm/h" — no `/atm` term anywhere in
the paper, including the equation that consumes it (`Q = 2100 U_eff A`, eq. [27]). The earlier "class
of value ~cm/atm-h" note in this spec was an unconfirmed assumption about general gas-permeability
convention, not something drawn from this source. **No unit conversion needed** — the MSF table's
plain cm/h matches the primary literature exactly.

Also worth noting for the reviewer: the paper's own baseline permeabilities used in its sensitivity
analysis (p. 1149) are "2, 4, and 6 cm/h for the wall of a bottom-unloaded tower silo, the wall of a
top-unloaded tower silo, and the cover of a bunker silo respectively" — a different split than the
MSF table's per-class wall/cover pairs (bunker wall 4/cover 1, pile wall 4/cover 4, bag wall 1/cover
1). Not a contradiction (different classification: unloading direction vs. storage shape), but the
MSF table's specific wall-vs-cover assignment per class isn't a direct one-to-one lift from this
paper's own stated baseline values — worth the reviewer knowing it's a synthesis, not a verbatim copy.

Note: `TOWER`'s additional "downward diffusion into the top plot" branch (`Silostg.for:836-863`, using a hardcoded top-cover constant distinct from the general wall permeability) applies only to a physically stacked tower silo with a distinguishable top plot being unloaded from above. A `Bag` doesn't have that structure — only the radial-diffusion portion of `TOWER` applies.

Both implementations:
1. Compute current respirable substrate fraction fresh each call: `RS = 1 − ndf_fraction − crude_protein_fraction − ash_fraction`, from the crop's current composition (no new state).
2. Compute the phase's candidate DM-loss fraction from the front-tracking math.
3. Clip the candidate loss at `RS` before applying it (`Silostg.for:826-829` for `TOWER`, `:951,:964` for `BUNKER`) — this is the RS conservation guarantee.
4. Update NDF/CP/DM-content by dilution, same pattern as Preseal and existing Fermentation.

`Bunker`/`Pile` additionally require compositing plot quality into vertical sections before infiltration, since a bunker isn't emptied one plot at a time (`Silostg.for:889-916`) — the existing `Storage.stored` list of individual crops needs a bunker-specific aggregation step before this phase runs, distinct from how `Bag`/tower-style storage tracks per-plot infiltration individually.

## 6. Known bugs from the prior audit (context, not fixed by this spec)

These were identified auditing the *existing* Effluent/Fermentation code. Per Section 3, none are fixed here — table kept for your own reference since Infiltration's RS ceiling addresses the same underlying failure mode (unbounded negative mass) for the *new* code only.

| # | Location | Issue | Severity | Fixed by this spec? |
|---|---|---|---|---|
| 1 | `storage.py:318-351` (`_calculate_mass_attributes_after_loss`) | No floor at zero on `dry_matter_mass`/`fresh_mass` after loss | High | No — Fermentation/Effluent untouched. New Preseal/Infiltration code will have its own floor + RS ceiling. |
| 2 | `storage.py:809` (`recalculate_nutrient_percentage`) | `0.0/0.0` → reachable `ZeroDivisionError` when a crop is fully depleted before purge | High | No |
| 3 | `silage.py:134` | `estimated_maximum_effluent` recomputed every effluent call, contradicting `HarvestedCrop`'s own "calculated once" docstring | High | No |
| 4 | `silage.py:181-182` (`calculate_days_of_effluent_loss_to_process`) | Effluent window not actually capped past day 10 when processing interval is coarse | Medium-high | No |
| 5 | `storage.py:580` (`calculate_dry_matter_loss_to_gas`) | Fermentation rate law goes negative in-range for non-alfalfa near 60% DM | High | No — confirmed (via Fortran) to be a RuFaS-introduced artifact of looping the equation daily; source evaluates it once. |
| 6 | `storage.py:574-584` | Extensive (mass) vs. intensive (concentration) basis mismatch within the daily fermentation loop | Medium | No |
| 7 | `storage.py:809-833` | `recalculate_nutrient_percentage` doesn't handle `dry_matter_loss_fraction` outside `[0,1)` | Low-medium | No |
| 8 | `storage.py:722-767` (`_calculate_moisture_loss`) | Unguarded division if `initial_dry_matter_percentage == 0` or `loss_period == 0` | Medium | No |
| 9 | `crop_soil_to_feed_storage_connection.py` (`_calculate_total_sensible_heat_generated`) | Fractional powers on `moisture_frac`/`bale_density` undefined if inputs go out of `[0,100]`-derived range | Low-medium | No (hay-only, not silage) |
| 10 | `storage.py:22-38` (fermentation constants) | 3 free parameters (`base_loss_fraction`, `loss_coefficient`, `lower_dry_matter_limit`), possibly 1 redundant degree of freedom if fit jointly | Identifiability | No |
| 11 | `crop_soil_to_feed_storage_connection.py:8` | Effluent DM threshold is `0.30`; source uses `0.29` | Low | No |
| 12 | `silage.py:15` (`EFFLUENT_CONSTRAINER = 10`) | Real `FOFT` curve (source) saturates around day ~79-80, not day 10 — effluent timescale understated ~8x | High (accuracy) | No |

## 7. Prerequisites / blocking work

**Updated 2026-09-08** — partial progress from the MSF `hf_silo_types` (RT-19) reference table
(`05-dev/msf/fourrager/02_Architecture/2026-08-26-hf-rt16-rt18-rt19-erd-proposal.md`):

- **Permeability, Bunker/Pile — RESOLVED.** Wall/cover values sourced to Buckmaster 1989 (see §5.2
  table). Units confirmed cm/h, no conversion needed (see §5.2). Safe to hardcode as a Python constant.
- **Permeability, Bag — RESOLVED 2026-09-09.** Sourced directly to the IFSM Reference Manual itself
  (see §5.2) — 1.0 cm/h for sealed plastic. Permeability is now sourced for all three in-scope
  storage types.

**Updated 2026-09-09** — checked Buckmaster, Rotz & Muck (1989) directly for geometry defaults
(`fourrager/04_Resources/1989 A Comprehensive Model of Forage Changes in the Silo.pdf`). Result is
partial, with real caveats:

- **Bunker — a usable citable example exists, but read the caveat.** p. 1149 (sensitivity analysis):
  for a 150 t DM capacity comparison, "the comparably sized bunker was 9.14 x 3.05 x 28.9 m." Axis
  labels aren't stated explicitly in the paper's text; by ordinary bunker convention this reads as
  width 9.14 m × height 3.05 m × length 28.9 m, but that assignment is my inference, not a paper
  quote — confirm before hardcoding. **Caveat:** this is one specific worked example used to compare
  silo types in the paper's own sensitivity figures (Fig. 5, 7), not a general survey of typical
  bunker dimensions across farms. Citable, but the reviewer should know it's "the example the authors
  happened to run," not "the industry-typical size."
- **Tower — same page, same caveat:** "6.1 m in dia. 21.3 m high," same 150 t DM comparison set.
- **Pile — NOT COVERED.** The paper's own scope (title, abstract) is tower and bunker silos only —
  no pile silo appears anywhere in it. Zero geometry data available from this source for `Pile`.
- **Bag — NOT SAFELY COVERED, despite `Bag` reusing `TOWER`'s radial math.** The tower dimensions
  above (6.1 m diameter) belong to an upright tower silo — a structure roughly the diameter of a
  small building. A plastic bag silo is a laid tube typically ~2.4-3.66 m in diameter (order-of-
  magnitude smaller). Reusing the tower's 6.1 m figure as a "Bag diameter default" would not be an
  unsourced placeholder, it would be an actively wrong number carrying a false citation. Do not
  borrow it. Bag's diameter remains fully unsourced.

**Updated 2026-09-09 — Pile checked against three more sources, decision now resolved (not just
narrowed).** Checked the IFSM Reference Manual directly (never mentions "pile" as a distinct
structure — only tower/bunker, extended to bag/bale via the tower equations), MSF's own live
Django DB schema, and a UW-Extension pile-density spreadsheet doc
(`CA-12_CA-14_Silage_Average_Density_Formula.md`):

- MSF's production DB already treats geometry as per-farm data for **every** storage type, not just
  Pile — `feed_inventory_bunkersilostorage.{full_length,wall_height,average_width}_meter`,
  `feed_inventory_bagsilostorage.{diameter,full_length}_meter`,
  `feed_inventory_pilesilostorage.{length_excluding_ramps,base_width}_meter` all exist as real
  per-farm input columns already in production. There is no reference-default geometry table
  anywhere in the live MSF system, for any storage type.
- This matches the IFSM manual's own explicit statement for bag/bale (§5.2 above): dimensions are
  "set to reflect those of a bag or bale" — i.e., real input, not a literature default.
- Separately, Pile's actual shape isn't width/height at all — the UW-Extension doc models it as a
  domed trapezoidal cross-section needing 5 inputs (bottom width, pile depth, dome height, top
  width, length), not the simple two-number shape this spec assumed for Bunker/Pile. Even a found
  "typical size" wouldn't have dropped cleanly into §3's width/height framing.

**Decision: geometry dimensions get no reference-table fallback, for any of Bunker/Pile/Bag.**
Two independent, authoritative sources (the primary IFSM manual and MSF's own production schema)
converge on the same answer — this isn't a compromise from failing to find data, it's the
architecturally correct choice. Drop the "optional, reference-table fallback" half of §3's scope;
geometry becomes a required field in each storage's own config JSON, same as MSF's DB already
requires. The Bunker/Tower worked-example numbers found above (Buckmaster 1989, p.1149) are kept in
this doc for context but are **not** to be wired in as a code fallback.

No placeholder numbers will be hardcoded into production code paths — the lookup mechanism will be
built, but calling it for Bag permeability or for any geometry dimension without a sourced/decided value
should fail loudly (explicit error), not silently return an invented number, until the open items above
are closed.

## 8. Testing strategy

- Unit tests per new function: normal case, zero-exposure edge case, RS-ceiling-triggered case.
- Component test: small synthetic silo (a few plots) through Preseal → existing Effluent/Fermentation (unmodified) → Infiltration, for one `Bunker` and one `Bag` case, asserting total DM loss stays under 100% and matches a hand-calculated expectation for at least one case.
- Follows existing repo convention: `unit`/`component` pytest markers (`tests/CLAUDE.md`).

## 9. Non-goals

- Feed-out phase (separate future work, shares Preseal's respiration submodel structurally but with different constants — not assumed reusable without its own design pass)
- Fixing Effluent/Fermentation bugs (Section 6)
- Corn silage kernel-processing density/NEL adjustments (`CSSILO`, `Silostg.for:1107+`) — not reviewed as part of this design
