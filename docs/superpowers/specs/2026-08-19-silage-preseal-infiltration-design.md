# Silage Preseal + Infiltration + Feed-out Phases — Design Spec

Status: Draft, ready for whiteboard/SME + team review (rufas-design-doc gate) — updated 2026-09-14
Date: 2026-08-19
Scope: `RUFAS/biophysical/feed_storage/silage.py`, `storage.py`, `crop_soil_to_feed_storage_connection.py`, feed-storage input schema

**2026-09-11 — Infiltration split out to a follow-up PR.** This document originally scoped Preseal and
Infiltration together. The implementation delivers **Preseal only**; Infiltration is future work,
tracked in its own plan (`PLAN_silage-infiltration-phase.md`, dependent on this Preseal work merging
first). Section 5.2, the Infiltration rows of Sections 3/4/8, and the design decisions specific to it
are retained below for context/reuse by that follow-up, but describe work **not** implemented by this
PR — see Section 9 for the authoritative current scope boundary.

**2026-09-11 (later same day) — Infiltration implemented and merged into this branch's history
(`PLAN_silage-infiltration-phase.md`, 6 commits `28ed6c973`..`3cb1bbf2f`, plus a phase-ordering
correction `4e52e3ecd` — Infiltration must run *after* Fermentation, not before; see Section 4). This
document is now extended to also design **Feed-out**, IFSM's 5th and final ensiling phase (Section
5.3) — the last of the three phases named in this doc's title. Feed-out is architecturally larger than
Preseal or Infiltration individually because it requires vertical-section compositing (deferred by
Infiltration's own Open Decision 3) as a genuine prerequisite — but per a primary-source re-check
(`Silostg.for` + IFSM Reference Manual, see Section 5.3.3), it does **not** need any new integration
with `FeedManager`: IFSM's own feed-out rate is a static per-storage constant (total stored DM ÷ 365
days), computed entirely within the storage, the same way Preseal/Infiltration already work. Per
`rufas-design-doc`'s ~1-engineer-month threshold, Feed-out still gets the full design-doc process (this
section), driven by the vertical-section-compositing prerequisite, not by any `FeedManager` integration.

**2026-09-14 — Section 5.3 rewritten to match a literal re-read of `FEEDOUT`/`SILO`/`BUNKER` and the
Reference Manual's Silo Storage/Feed-Out prose (directive: "just follow IFSM").** Three changes: (1)
dropped the `FeedManager` rate-integration proposal (5.3.3) — IFSM's `FDRTE` is a static per-storage
average, so no new cross-module data path is needed; (2) replaced the "single largest unknown"
framing of vertical-section compositing (5.3.2) with IFSM's actual formula (`NVS =
floor(total_DM/(10·FDRTE))`, equal-mass split, uniform averaged quality) — a direct translation, not a
sub-design; (3) **corrected a factual error** in 5.3.4 — `SILTYP.EQ.2` is bottom-unloaded tower, not
Bag (the glossary at `Silostg.for:83` was previously misread); Bunker and Bag both use `PSIA = 0.21`.
`CSAF`/`PSIA` sourcing in Section 7 are resolved as a result (derived from existing geometry, not
looked up). Only the `ISILO` 4/5 (`TSTR`) gap remains genuinely unresolved.

## 1. Motivation

RuFaS's silage module currently implements 2 of IFSM's 5 documented ensiling phases (Effluent, Fermentation). Preseal, Infiltration, and Feed-out are entirely absent. This spec covers restoring **Preseal** now, with **Infiltration** designed here but implemented in a follow-up PR (see banner above), and now **Feed-out** (Section 5.3) as the third and final phase this document plans. Effluent and Fermentation are explicitly untouched — they're considered established and out of scope for this work, even though the prior audit (Section 6) found real bugs in them.

Feed-out is different in degree, not kind, from Preseal/Infiltration: like them, it's a `process_degradations` phase (Section 5.3.3) — IFSM's own feed-out rate is a static per-storage average, not a live removal signal, so this phase does not hook into `FeedManager`'s removal path at all. What Feed-out does need, uniquely among the three phases, is vertical sections (deferred by Infiltration's Open Decision 3) to have a well-defined "face" being fed out at all — that's its real architectural cost.

Sources used to derive this design:
- `docs/beef_module/` sibling reference pattern (N/A here — see below instead)
- IFSM Reference Manual: `c:\researchLife\05-dev\msf\fourrager\04_Resources\IFSM Reference Manual.md` (prose description, phase overview, some equations — several equations are only present as stripped images in this file and are **not** authoritative for exact math)
- **IFSM Fortran source (authoritative for equations)**: `c:\researchLife\05-dev\msf\fourrager\04_Resources\Silostg.for` — subroutines `SILO` (orchestrator, lines 210-631), `PRESEAL` (634-714), `FERMENT` (717-791, reference only, not being changed), `TOWER` (794-876, infiltration — radial), `BUNKER` (879-984, infiltration — vertical section), `EFFLU` (987-1026, reference only, not being changed), `FEEDOUT` (1029-1104, designed in Section 5.3, implementation TBD)
- `Silostg.for:1-95`'s own glossary block (`C PARTIAL GLOSSARY FOR STORAGE MODEL`) — authoritative for `PLOT(I,J)` column meanings, `SILTYP`, `CSAF` vs. `CSA`, `FDRTE`, `NVS`, cited throughout Section 5.3
- Pitt & Muck (1993), *A Diffusion Model of Aerobic Deterioration at the Exposed Face of Bunker Silos* (`03-literature/pitt-1993-a-diffusion-model-of-aerobic-deteriorati.md`) — the primary mechanistic O₂/heat/yeast diffusion source `FEEDOUT`'s `DML4A` structurally mirrors; Wilkinson (2012) (`00-inbox/silage_pdfs/#Wilkinson2012...pdf`) — review synthesis, empirical benchmarks only (Section 5.3.5)
- `05-dev/msf/expert-system/scientific review/` (`RuFaS_to_MSF_Silage_Parameter_Mapping.md`, `Silage_Model_Needs_Specification.md`, `Mechanistic_Silage_Model_Architecture.md`, `CA-12_CA-14_Silage_Average_Density_Formula.md`) — a parallel MSF Expert System design track that independently scoped Feed-out (Gaps G-21/G-22/G-23, `fo_plan_feedout`); see Section 5.3's approach-decision note for how this spec's scope relates to that track

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

**In scope (this PR):**
- Preseal phase for `Bunker`, `Pile`, `Bag` (all `Silage` subclasses)
- New per-crop state: temperature
- `PRESEAL_INITIAL_PH`: a fixed Preseal calculation constant (not per-crop state — see §5.1's detail below)
- New per-storage config: geometry (width/height for Bunker/Pile, diameter for Bag) — optional, reference-table fallback

**Designed here, implemented in a follow-up PR (`PLAN_silage-infiltration-phase.md`) — delivered
2026-09-11 (6 commits `28ed6c973`..`3cb1bbf2f`, phase-order fix `4e52e3ecd`):**
- Infiltration phase for `Bunker`, `Pile`, `Bag`, with RS conservation as its safety ceiling
- Permeability: reference-table only, keyed by storage type, no per-farm override

**Designed here (Section 5.3), implementation TBD in its own follow-up (design-doc process, not a
direct `PLAN_*.md`, per Section 0's banner):**
- Feed-out phase for `Bunker`, `Pile`, `Bag`, reusing the same RS-conservation ceiling
- Vertical-section compositing for `Bunker`/`Pile` (a genuine prerequisite, not previously built —
  Infiltration's Open Decision 3 deferred exactly this)
- A static per-storage feed-out rate (total stored DM ÷ 365 days), matching IFSM's own `FDRTE` —
  computed within `Storage` itself, no `FeedManager` integration required (see Section 5.3.3)

**Out of scope (explicitly not touched):**
- Effluent (`silage.py`, existing) — established, not to be modified
- Fermentation (`storage.py`, existing, shared base class) — not to be modified
- Hay, Baleage, Grain storage types — Preseal/Infiltration/Feed-out are ensiling-specific
- Sourcing the actual reference-table values (geometry defaults, permeability defaults, feedout-face
  area) — blocking prerequisite, tracked separately (Section 7)
- Fixing the bugs in Effluent/Fermentation identified in the prior audit (Section 6) — documented for awareness only
- LOADER (unloading-equipment type), `ISILO`/`TSTR` per-silo state-machine tracking, and the
  large-particle NDF split (`PLOT(I,12)`/`PLOT(I,13)`) — real dimensions of the source's `FEEDOUT`
  math with no RuFaS analogue yet; see Section 5.3's Open Questions for the proposed simplifications

## 4. Architecture

This PR delivers:

```
receive_crop()  →  [Preseal loss finalized lazily — see 2.1]
                          ↓
process_degradations()  →  existing Effluent (unchanged) → existing Fermentation (unchanged)
```

Preseal loss for crop N is finalized at the first of:
1. Crop N+1 being received into the same `Storage` (use `next.storage_time − crop.storage_time`, capped at 3 days), or
2. Crop N entering `process_degradations` for the first time with no successor yet received (use fixed 0.125 days), whichever happens first.

Once finalized, a crop's preseal loss is computed exactly once and never revisited (matches the source's one-shot-per-plot semantics — `Silostg.for:634-714`).

**Follow-up PR** (`PLAN_silage-infiltration-phase.md`, delivered 2026-09-11) added Infiltration to the
chain, using whichever of `BUNKER` or `TOWER` math applies to the crop's storage class (Section 5.2):

```
process_degradations()  →  existing Effluent → existing Fermentation → Infiltration (new)
```

The plan's first delivered version placed Infiltration *before* Fermentation (Open Decision 6 argued
this was the least-invasive wiring). An SME review after merge (2026-09-11) confirmed this was wrong
relative to IFSM's actual phase order and it was corrected (`4e52e3ecd`) to run after Fermentation, as
shown above — this is the order Feed-out (Section 5.3) now builds on.

**Feed-out** (Section 5.3, design only — implementation TBD) slots into the same `process_degradations`
chain as Infiltration — no `FeedManager` hook needed, per a primary-source re-check (Section 5.3.3):

```
process_degradations()  →  Effluent → Fermentation → Infiltration → Feed-out (new, last)
```

Feed-out's rate input is a static per-storage constant IFSM itself computes from total stored DM
(`FDRTE = total_stored_DM / 365`, `Silostg.for:233,242`) — this design follows that literally rather
than introducing a new `FeedManager` integration point (see Section 5.3.3 for the reasoning and the
recomputation-cadence question that remains genuinely open).

## 5. Component design

### 5.1 Preseal

Translates `PRESEAL` (`Silostg.for:634-714`). Key structural points for implementation (see source for exact constants):

- Respiration rate depends on crop type (haylage vs. corn silage — different `MUMAX` constant), current DM content, current temperature, and current pH.
- The subroutine internally steps through the exposure duration **one day at a time** (`Silostg.for:673-703`), because temperature rises each day from respiration heat, which feeds into the next day's respiration rate (positive feedback / self-heating). This internal day-stepping must be preserved — collapsing it into a single evaluation over the full exposure window would lose the self-heating effect.
- Mass-loss stoichiometry is **not** a simple 1:1 dry-matter removal: per `Silostg.for:697,708`, respiration converts dry matter to both CO₂ (leaves the system) and water (stays in the crop, raising moisture). The exact split (108g water retained / 72g gas lost per 180g dry matter respired, matching the manual's stated 108:180 ratio) must be preserved in the mass/DM-content update, not approximated as pure DM removal.
- Fiber (NDF) and protein (CP) concentrations increase via simple dilution as DM is lost (no chemical breakdown in this phase, unlike Fermentation's hemicellulose breakdown).
- Initial pH estimate (needed only for alfalfa's `FPH` respiration factor): defaults to the no-acid-treatment case, `FACID = 0`, which resolves to a fixed starting pH (`Silostg.for:271`, evaluated at `FACID=0`). RuFaS does not currently model silage additive treatments, so this is a hard default for v1, not a per-farm input.

### 5.2 Infiltration (follow-up PR — not implemented here)

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

**2026-09-11 status: Infiltration's own vertical-section compositing was deferred (Open Decision 3 of
`PLAN_silage-infiltration-phase.md`) — it shipped treating each stored crop as its own infiltration
column, explicitly *not* building sections "given Feed-out isn't scoped." Section 5.3 below is that
scoping, and now builds sections for real.**

### 5.3 Feed-out

Translates `FEEDOUT` (`Silostg.for:1029-1104`). This is IFSM's 5th and final ensiling phase, and the
last one RuFaS is missing. Unlike Preseal/Infiltration, it does not slot cleanly into
`process_degradations` alone — see the architecture diagram in Section 4.

**Approach decision (SME-confirmed 2026-09-11): use the full IFSM `FEEDOUT` backbone as v1, keep the
objective simple.** A separate, more mature design track — the MSF Expert System's own scientific
review (`05-dev/msf/expert-system/scientific review/`) — has already scoped Feed-out formally as Gaps
G-21/G-22/G-23 in `RuFaS_to_MSF_Silage_Parameter_Mapping.md`, with a farmer-facing MCP tool
(`fo_plan_feedout`) and two new reference tables (RT-23 aerobic stability, RT-24 feed-out DM-loss
factors). That track's own design principle (`Silage_Model_Needs_Specification.md`, "the fit-for-
purpose test") argues explicitly *against* full mechanistic simulation for the farmer-facing question
`fo_plan_feedout` answers — "Pitt & Muck (1993) already reports ~3% DM loss at the recommended
15 cm/day face-removal rate, rising to ~9% at one-third that rate... Simulation adds cost, not
information" — favoring a literature-calibrated lookup (RT-24) instead. **This spec deliberately
diverges from that recommendation for RuFaS itself**: RuFaS's own purpose here isn't answering one
farmer-facing advisory question, it's giving the whole-farm simulation accurate day-by-day mass/
composition state, the same way the other four phases do — a lookup table would satisfy
`fo_plan_feedout`'s narrower question but wouldn't give RuFaS the same kind of tracked state Preseal/
Effluent/Fermentation/Infiltration already produce. Translating the actual `FEEDOUT` equations (same
precedent as those four phases) is the more consistent choice for RuFaS specifically. "Keep the
objective simple" carries into Section 5.3.4's Open Questions: each proposes the simplest viable
default (hard-coded `LOADER`, deferred `TSTR` investigation, aggregate-`ndf` dilution over the large-
particle split) rather than fully resolving every dimension of the source model — same scope discipline
Preseal/Infiltration already used (flat density, no packing-factor submodel, reference-table-only
permeability).

**Cross-project synergy, not duplication.** Shipping this closes Gap G-21 in
`RuFaS_to_MSF_Silage_Parameter_Mapping.md` (currently "not in RuFaS") and gives `fo_plan_feedout`/
`fo_calculate_inventory` a real RuFaS-provided feed-out signal to consume, rather than requiring RT-24
to stand entirely alone. `Mechanistic_Silage_Model_Architecture.md` independently reached the same
"vertical sections" conclusion as Section 5.3.2 below (a layer at the bunker base can still be
fermenting while the top layer near the face is aerobically spoiling — "the same spatial layers at
different times, not sequential stages of one pipeline") — worth reading before finalizing 5.3.2's
shape, since that document already worked through why a simple pipeline structure breaks down here.

#### 5.3.1 What `FEEDOUT` actually computes

Surface-spoilage dry-matter loss (`DML4` in the source) during active removal, split into two additive
terms, both floored/ceilinged the same way as Infiltration:

- **`DML4A`** — diffusion-driven loss through the exposed feedout face, structurally parallel to
  Infiltration's front-tracking math (`GAMMA`/`C`/`MUBAR` terms mirror `TOWER`/`BUNKER`'s own
  diffusion-front derivation), but driven by `DF = 100*(FDRTE/DM)/(DENS*CSAF)` — a **feed-out rate**
  term Infiltration never needed. `CSAF` ("cross-sectional area of feedout **surface**",
  `Silostg.for:34`) is a *different* area than Infiltration's `top_area_m2`/`front_radius_m` geometry —
  it's the exposed face being actively unloaded, not the storage's static top or radial front.
  `MUTAU`/`FD`/`FT` mirror Preseal's own respiration-rate structure (piecewise water-activity and
  temperature factors), matching this spec's Section 5.1 more than Section 5.2's math — worth noting
  since it means Feed-out reuses Preseal's respiration submodel *shape*, but with different constants
  (per Section 9's non-goal note: "not assumed reusable without its own design pass" — that pass is
  this section).
- **`DML4B`** — a fixed "0.125 days bunk time" loss (`0.0299*MUTAU*0.125/DM`), applied regardless of
  `FDRTE`/`CSAF` — models spoilage in the feed bunk after removal, not in the silo. Structurally the
  simplest term to translate (no geometry dependency at all).
- **`DML4 = min(DML4A + DML4B, RS)`** — same respirable-substrate ceiling pattern as Preseal/Infiltration
  (`Silostg.for:1097`, `RS = 1 - PLOT(NN,4) - PLOT(NN,5) - ASH`, identical form to
  `calculate_respirable_substrate_fraction` — **reuse it directly, do not re-derive**).
- Applies to `PLOT(NN,11)` (stored DM mass — matches `crop.dry_matter_mass`), `PLOT(NN,4)`/`PLOT(NN,5)`
  (NDF/CP — matches `crop.ndf`/`crop.crude_protein_percent`, diluted the same way as every other phase),
  and `PLOT(NN,12)` (NDF content **of large particles specifically** — no RuFaS analogue; see Open
  Questions below).

`PLOT(NN,1)` gating (`Silostg.for:1084,1097`) is **not** a section-count or plot-index threshold — per
the glossary (`Silostg.for:54-56`), `PLOT(I,1)` is the **crop type code** (1=corn, 2=small grain,
4=alfalfa, 5=grass). The `.GE.4` branch is "if this plot's crop is alfalfa or grass" (haylage), not a
section/geometry condition — a crop-type-dependent loss coefficient, same pattern as Preseal's
alfalfa-vs-corn `MUMAX` split (Section 5.1).

#### 5.3.2 Vertical-section compositing

Per Section 5.2's status note above, this is being built now, not deferred again. `Bunker`/`Pile`
storage in the source is a stack of `PLOT` rows composited into `NVS` vertical sections
(`Silostg.for:889-916`, called from `BUNKER`); Feed-out consumes those sections from the open top down,
one at a time, as `FDRTE` empties them (`Silostg.for:1029` is called per-section, `NN` indexing into
the section, not the raw per-fill `PLOT` row).

**IFSM's actual method is a literal, fully-specified formula, not an open architectural question:**
`NVS = floor(total_stored_DM / (10 * FDRTE))`, floored at a minimum of 1 section (`Silostg.for:920-921`)
— i.e., "how many 10-day chunks will it take to feed out everything currently in the silo." Each
section then gets **exactly** `total_stored_DM / NVS` (`:930`) and the **mass-weighted average quality
of every currently-stored plot** (`:922-933`, `CNDF`/`CCP`/`CNPN`/`AVGT`/`AVGPH` computed once across
all of `self.stored`, then copied identically onto every section) — there is no depth-quality gradient
between sections, only a difference in *when* each section gets fed out. This drops the earlier framing
of this as "the single largest unknown": it's a direct translation, not a sub-design.

Proposed RuFaS shape: a storage-level `_sections: list[...]` attribute on `Bunker`/`Pile` only (not
`Bag`, which stays per-crop like Infiltration's radial front — a bag has no vertical stack), built by
(1) computing `NVS` from current `total_dry_matter_mass` and the storage's Feed-out rate (Section 5.3.3),
(2) computing the mass-weighted average of `ndf`/`crude_protein_percent`/`npn`/`temperature`/`ph` across
`self.stored`, and (3) splitting `total_dry_matter_mass` into `NVS` equal shares carrying that averaged
composition. Real open question, scoped down from the prior framing: exactly when to recompute the
section list as `self.stored` changes (IFSM recomputes once per silo-emptying cycle in a batch model;
RuFaS's day-by-day loop needs an explicit recomputation trigger) — flagged in Section 5.3.4.

#### 5.3.3 Feed-out rate — a static per-storage constant, matching IFSM literally

`FDRTE` in the source is a crude annualized average (`Silostg.for:233`,
`FDRTE = 1000.*(TMSTO(1)+TMSTO(2))/365.` — total stored mass for the year, divided by 365), computed
once per silo-emptying cycle from the *entire* stored mass, then deflated at the end of that cycle by
the cycle's total loss fraction (`FDRTE = FDRTE*(1.-SDML)`, `:624`). It is not derived from any daily
withdrawal amount — the Fortran model runs as an offline batch simulation with no concept of "today's
actual request," and nothing in `FEEDOUT`, `BUNKER`, or the `SILO` orchestrator ever reads a per-day
removal quantity from anywhere else.

**Revised direction (supersedes the 2026-09-11 `FeedManager`-integration proposal): follow IFSM
literally — use the same static per-storage rate, computed entirely within `Storage`/`Silage`, not from
`FeedManager`.** A primary-source re-check found no live "today's request" signal anywhere in IFSM's own
feed-out math to justify deviating from it; `FeedManager.manage_daily_feed_request` →
`_deduct_from_storage` remains completely untouched by this design. Concretely:
`feed_out_rate_kg_dm_per_day = total_dry_matter_mass / 365`, computed from `self.stored` the same way
`NVS` is (Section 5.3.2) — no new cross-module data path, no new integration point between
`FeedManager` and `Storage.process_degradations`.

**Remaining open question (scoped down from "needs SME sign-off on a new integration," to just a
recomputation-cadence choice):** IFSM computes this rate once per silo-emptying cycle in a batch model;
RuFaS's day-by-day loop needs an explicit trigger for when to recompute it as `self.stored` grows or
shrinks (e.g., once when Feed-out first activates for a storage vs. recomputed every
`process_degradations` call). Candidate default: compute once, on first Feed-out activation for a given
storage, and hold it fixed thereafter — closest behavioral match to IFSM's own once-per-cycle
semantics — but this is a genuinely small decision now, not the structural integration question the
prior draft posed.

#### 5.3.4 Open Questions (for team review, not resolved by this section)

- **LOADER — RESOLVED, confirmed by source, not just a proposed simplification.** `Silostg.for:1039`,
  `DATA LOADER/0/` — the source itself hardcodes skid-steer (`LOADER=0`) with no branch anywhere in
  `FEEDOUT` that ever sets it otherwise. RuFaS's `LOADER=0` default is a literal translation of IFSM's
  own behavior, not a RuFaS-side simplification away from it.
- **`TSTR`/`ISILO` — partially resolved.** `TSTR = ISILO(NSILO)` is not a per-silo lifecycle/state
  machine; it's the same static silo-type configuration code used throughout `SILO` (`ISILO(NSILO)`:
  1 = top-unloaded tower, 2 = bottom-unloaded tower, 3 = bunker, per the glossary at `Silostg.for:83`),
  assigned once and constant for the run — maps directly onto RuFaS's `StorageType`. **Still genuinely
  open:** `TSTR.EQ.5` zeroes `DML4A` entirely, but `ISILO` values 4/5 are never defined in this file, its
  glossary, or the IFSM Reference Manual excerpt available in this repo (the `.BLK` include files that
  might define them aren't present). Since RuFaS's `StorageType` enum has no 4th/5th-type analogue,
  proposed resolution: treat `TSTR=5` as never-applicable to RuFaS's storage types rather than chasing
  the undefined code further.
- **Large-particle NDF split** — unchanged from the prior draft; no primary source resolves this
  further. `PLOT(I,12)`/`PLOT(I,13)` ("NDF content of large particles" / "portion of large particles")
  have no RuFaS analogue. Proposed: apply Feed-out's NDF dilution to the aggregate `crop.ndf` directly
  (same as every other phase) — needs SME sign-off, since it means Feed-out's fiber-concentration
  accuracy is intentionally coarser than the source for this one term.
- **Bag/`PSIA` — CORRECTION to the prior draft, now resolved, no sourcing pass needed.** The prior
  version of this bullet misread the source: `SILTYP.EQ.2` (`Silostg.for:1072`) is **bottom-unloaded
  tower** per the glossary (`:83`), not Bag. Bunker (`SILTYP=3`) falls into the `ELSE` branch → `PSIA
  = 0.21`. The Reference Manual states bags/bales are "simulated using the tower silo relationships"
  generally, which — combined with Bag having a single opened end rather than a bottom-unload
  mechanism — means Bag is best coded as the top-unload-tower branch (`SILTYP=1`), also giving
  `PSIA = 0.21`. **Resolved reading: Bunker and Bag both use `PSIA = 0.21`; only bottom-unloaded tower
  (a type RuFaS doesn't have) uses `0.105`.** No literature-sourcing pass is needed — this falls out of
  the existing branch logic, not a table lookup.

#### 5.3.5 Empirical plausibility benchmarks (literature + the MSF Expert System's own reference work)

Wilkinson, M. (2012), *The aerobic stability of silage: key findings and recent developments*, Grass
and Forage Science 68:1-19 (`00-inbox/silage_pdfs/#Wilkinson2012...pdf`) — a review paper, not a
primary equation source (it does not give `FEEDOUT`-equivalent constants for `LOADER`/`TSTR`/`PSIA`
above), but it does give real farm-scale numbers useful as **plausibility checks** on whatever
Section 5.3.3's annualized-average rate produces, and as component-test sanity targets. Pitt & Muck
(1993) — cited directly by name in `05-dev/msf/expert-system/scientific review/Silage_Model_Needs_
Specification.md` as the numeric backbone for `fo_plan_feedout` itself — is the actual mechanistic
diffusion-model source `FEEDOUT`'s `DML4A` structurally resembles (O₂/heat/yeast diffusion at the
exposed face; `00-inbox`/`03-literature` note: `pitt-1993-a-diffusion-model-of-aerobic-deteriorati.md`).

- **Feed-out face-removal rate, recommended vs. real-world vs. dose-response.** Wilkinson (2005)'s own
  recommended target is 1-2 m of exposed face consumed per week (0.15-0.3 m/24h in winter, double that
  in summer) — at 1 m/week, silage is never exposed more than 168 h before removal. Real farm data (54
  commercial farms, Italy — Borreani & Tabacco 2010) ranged 0.07-0.25 m/24h in winter and 0.08-0.33 m/
  24h in summer — real farms often move *slower* than the recommended target. **Pitt & Muck (1993)
  gives the actual dose-response this drives**: only ~3% DM loss at the recommended 15 cm/day removal
  rate, rising to ~9% at one-third that rate (5 cm/day) — this is the same 15 cm/day figure the MSF
  Expert System's own `Silage_Model_Needs_Specification.md` already treats as sufficient evidence for
  its `fo_plan_feedout` advisory tool, so it's a doubly-anchored number. **For Bag specifically**, MSF's
  own `CA-12_CA-14_Silage_Average_Density_Formula.md` gives a distinct real-world threshold: "< 18
  inches/day (≈0.46 m/day) → consider increasing feedout rate." **Use all of this as a sanity check**:
  convert the annualized kg-DM/day rate (Section 5.3.3) into an equivalent face-advance rate
  (via `dry_matter_density_kg_per_m3` × the storage's cross-sectional area) and confirm both that it
  falls in a plausible real-world band and that the resulting `DML4` lands near the 3%/9% dose-response
  anchor for at least one component-test scenario — a rate or loss wildly outside these ranges would
  indicate a unit-conversion bug rather than a genuinely fast/slow farm.
- **Density effect on loss, from the same primary source**: raising silage density from 480 to
  960 kg/m³ shrinks the 24-h heated zone from 0.35 to 0.15 m and cuts 24-h losses from 0.93 to
  0.85 kg DM per m² of *face area* — note this is normalized per unit face area (matching `CSAF`
  directly), not per whole-silo mass, making it a more direct calibration target for `DML4A` than a
  whole-silo percentage would be.
- **Air penetration depth into the feed-out face**: 1-2 m (Honig 1991; Weinberg & Ashbell 1994) —
  plausibility bound for how deep Feed-out's diffusion front should reach; a design analogous to
  Infiltration's `front_radius_m`/`front_depth_cm` should stay within this order of magnitude for
  typical storage geometries.
- **A concrete DM-loss anchor**: silage 0.2-0.5 m behind the face that feels warm to the touch has "most
  likely been exposed to air for more than 48 h and has probably lost about 5% of its total DM." Useful
  as a rough component-test expectation (e.g., "≈5% DM loss after 2 days' exposure at a typical
  removal rate" is plausible; "50% after 2 days" would not be).
- **Recommended silage density at feed-out**: 170-180 kg DM/m³ for lower-DM crops (250 g DM/kg FW) up
  to 240-250 kg DM/m³ for higher-DM crops (450 g DM/kg FW) (Spiekers et al. 2009); 240 kg DM/m³ with
  max porosity 0.4 proposed for maize/whole-crop wheat (Holmes & Muck 2007). Corroborates (does not
  replace) the existing `dry_matter_density_kg_per_m3` config field already shipped with
  Preseal/Infiltration — a secondary literature source for realistic test-fixture values.
- **Not directly reusable for Feed-out, but worth banking for Infiltration's own future validation
  effort**: cover-film oxygen permeability measured directly against DM loss — 10% loss in the upper
  40 cm layer under a low-permeability co-extruded film vs. 37% under conventional polyethylene film,
  same maize crop, same conditions (Borreani et al. 2007). A real external data point if/when
  Infiltration's shipped output ever needs a literature sanity check.

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
architecturally correct choice. No placeholder numbers are hardcoded into production code paths, and
no literature default is ever substituted for a real dimension: a missing value is never turned into
an invented number. The Bunker/Tower worked-example numbers found above (Buckmaster 1989, p.1149) are
kept in this doc for context but are **not** wired in as a code fallback.

**Revised during implementation: geometry is optional, and a missing value skips Preseal rather than
failing loudly.** The original plan above called for geometry to be a *required* config field, with
construction failing loudly (an explicit error) if it was absent — enforcing "no invented number" by
refusing to run at all without real data. That would have broken every existing Bunker/Pile/Bag
config anywhere the moment this feature shipped, since none of them predate these fields. The revised
behavior: `width_m`/`height_m`/`diameter_m`/`dry_matter_density_kg_per_m3` are optional on
`Bunker`/`Pile`/`Bag`; a storage missing any of the fields it needs simply skips Preseal for its
crops (no exception, no substituted number — the rest of the model, Effluent/Fermentation/mass
tracking, is unaffected). A *present but invalid* value (non-numeric, zero, negative) still raises
`ValueError` — the "no silent fallback for a real farm's storage" principle is preserved for anyone
who does configure Preseal; it's absence, not garbage, that's now tolerated. This is strictly
opt-in: no existing farm config is required to change.

**2026-09-11 — prerequisites for Feed-out (Section 5.3), updated after a primary-source re-check:**
- **`CSAF`/feedout-face area — geometry-only, `PACK` deliberately not modeled (`/challenge-plan`
  round-1 correction, 2026-09-14).** IFSM's own formula (Tower: `π·(width/2)²`; Bunker/Pile: `width ×
  settled_height`, where `settled_height = (0.70 + 0.25·PACK) × configured_height`,
  `Silostg.for:567-571`) depends on a packing factor RuFaS has never modeled anywhere (no `PACK`
  config on any storage, no packing-time/tractor-mass inputs). An earlier version of this section
  marked the settled-height formula "RESOLVED, derived not sourced" — that was premature: the shipped
  implementation uses the flat, unscaled `width × height` for Bunker/Pile (and the unchanged
  `π·(width/2)²` for Tower/`Bag`), matching Infiltration's own already-established "no packing-factor
  submodel" precedent for the identical geometry problem. This is a **known, cited bias**: using the
  unscaled area overstates Bunker/Pile face-diffusion loss by roughly 5–43% depending on the
  (unmodeled) `PACK` value that would have shrunk it. Flagged for SME awareness, not silently
  corrected — implementing the settled-height scaling would require a new `pack_factor` config field,
  a real scope increase deferred to a future PR if the bias proves material.
- **`PSIA` constant for Feed-out — RESOLVED, see Section 5.3.4's corrected Bag/`PSIA` bullet.**
  Bunker and Bag both use `0.21`; only bottom-unloaded tower (no RuFaS analogue) uses `0.105`. No
  literature-sourcing pass needed.
- **Vertical-section compositing** (Section 5.3.2) remains a genuine prerequisite for Feed-out's
  `Bunker`/`Pile` math — Feed-out cannot ship before sections exist, unlike Infiltration, which shipped
  without them via a documented scope reduction — but per Section 5.3.2's update, the compositing
  formula itself is now a direct translation, not an open architectural question. The real remaining
  work is implementation (building `_sections` and wiring `receive_crop`/`remove_empty_crops`), not
  further design.

## 8. Testing strategy

**This PR (Preseal):**
- Unit tests per new function: normal case, zero-exposure edge case, empty-crop edge case.
- Component test: small synthetic silo (a few plots) through Preseal → existing Effluent/Fermentation (unmodified), asserting total DM loss stays under 100% and matches a hand-calculated expectation for at least one case.
- Follows existing repo convention: `unit`/`component` pytest markers (`tests/CLAUDE.md`).

**Delivered 2026-09-11 (Infiltration, `PLAN_silage-infiltration-phase.md`):**
- Unit tests per new function: normal case, zero-exposure edge case, RS-ceiling-triggered case.
- Component test: small synthetic silo (a few plots) through Preseal → Effluent → Fermentation →
  Infiltration, for one `Bunker` and one `Bag` case, asserting total DM loss stays under 100%.
- A dedicated call-order regression test (`test_process_degradations_runs_fermentation_before_infiltration`)
  was added *after* the phase-ordering bug (Section 4) — asserting actual call order, not just that both
  phases eventually ran, since a presence-only test would not have caught that bug.

**Follow-up (Feed-out, Section 5.3 — design only, implementation TBD):**
- Unit tests per new function, same normal/zero/RS-ceiling-edge pattern as Infiltration.
- A call-order regression test analogous to the one above is non-negotiable here too — Feed-out is the
  4th phase-ordering integration point in a row (after Preseal, Infiltration, and Infiltration's own
  order-fix), and this design's Section 4 architecture diagram makes the intended order explicit
  (`Effluent → Fermentation → Infiltration → Feed-out`) precisely so a test can assert it directly.
- Component test: small synthetic silo through Preseal → Effluent → Fermentation → Infiltration →
  Feed-out via `process_degradations` alone (matching Section 4's revised diagram) — `FeedManager` is
  untouched by this design, so no test needs to drive `manage_daily_feed_request` for Feed-out coverage.
- Vertical-section compositing (Section 5.3.2) needs its own unit tests independent of Feed-out's loss
  math — section-count formula (`NVS`), mass-weighted compositing, and interaction with `receive_crop`/
  `remove_empty_crops` are all independently testable before any `FEEDOUT` math is wired to them.

## 9. Non-goals

**Not delivered by this PR (tracked separately):**
- Infiltration phase (Section 5.2) — designed here, implemented 2026-09-11 (`PLAN_silage-infiltration-phase.md`, phase-order corrected in `4e52e3ecd`)
- Feed-out phase (Section 5.3) — designed here 2026-09-11, implementation not yet started; needs
  vertical-section compositing as a prerequisite and its own `PLAN_*.md`/team-review cycle once this
  section is written up and signed off

**Non-goals of this whole design line (Preseal + Infiltration + Feed-out):**
- Fixing Effluent/Fermentation bugs (Section 6)
- Corn silage kernel-processing density/NEL adjustments (`CSSILO`, `Silostg.for:1107+`) — not reviewed as part of this design
- Equipment-type modeling (`LOADER`), per-silo lifecycle state tracking (`TSTR`/`ISILO`), and
  large/small-particle NDF fractionation (`PLOT(I,12)`/`PLOT(I,13)`) — flagged as open questions in
  Section 5.3.4, proposed as hard-coded simplifications rather than modeled, pending SME sign-off
