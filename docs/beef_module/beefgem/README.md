# docs/beef_module/beefgem/

BeefGEM management enhancement layer — reference documents.

## Files

### `RuFaS_BeefGEM_Implementation_Plan.md` — implement from this

The execution plan for the `feature/beef-beefgem-management` PR.
Written in RuFaS style (plain Enum, mypy strict, scoped Black, TDD).
Covers Phases A–D in strict dependency order.

### `RuFaS_BeefGEM_Source_Reference.md` — source provenance, read this one

The readable conversion of the June 2026 source document (BeefGEM 4.0 /
USDA-ARS Rotz et al.). Greppable, diffable, and renders on GitHub, so it is
the primary reference for anything in the source material.

Contains BeefGEM rule IDs (R-CH4-ENT-003, D-STOCKER-TO-FINISH-001, …),
`simulate.py` / `herd_dynamics.py` / `physiology.py` source mappings,
the `COW_CALF_STOCKER_FEEDLOT` grouping scenario definition, test-marker
taxonomy, and five named future-PR gaps (Section 10).

**Its stocker section is superseded.** The native stocker module it
describes is already implemented in the animal subsystem. Implement from
the execution plan above, not from this file.

**Its `calving_rate` field is not a conception rate.** The source
document's `BeefHerdScenario.calving_rate` and its `high_conception_rate`
/ `low_conception_rate` scenarios conflate calf crop weaned with
conception. 0.855 is calf crop weaned — downstream of conception,
gestation loss and pre-weaning mortality — and is carried in this
codebase as `BEEF_CALF_CROP_WEANED_RATE`. The conception-equivalent of
the same USDA figure is 91.5%. The scenario runner therefore exposes
`conception_rate_multiplier`, a dimensionless scale factor on the
calibrated base daily conception probability, not a rate. Those lines
are left as converted, to keep the conversion faithful to its source.

Code blocks were flattened by the pandoc conversion and re-fenced
heuristically — treat them as indicative, not copy-paste ready.

### `RuFaS_BeefGEM_Management_Implementation_Plan.docx` — archival original

The original Word document the Markdown above was converted from. Kept for
provenance. Prefer the Markdown for reading, searching, and review; consult
the DOCX only to check the conversion or recover formatting it dropped.

Tracked via a scoped exception in `.gitignore` — the repo-wide `*.docx`
rule would otherwise exclude it.

## Scope boundaries

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

**`finishing_system` has no effect on a run yet.** It only selects the
methane equation inside `report_feedlot_performance`, which is never
called (above), so `feedlot_mean_daily_enteric_ch4_g_d` is never written
either.

**Compensatory gain never applies in a run.** The factor is set only when
a stocker hands off to the feedlot, and feedlot animals are not iterated
in the herd daily loop, so neither the uplift nor its decay executes.
`enable_compensatory_gain` therefore changes no output today.

**Beef cattle produce no enteric methane in the herd totals.**
Digestion supports dairy animal types only, so beef animals never
contribute to the herd methane total. The beef methane equations live
in `EntericMethaneCalculator` beside the dairy ones, but the reporter
evaluates them at exit as mean-daily values and writes them directly
to output, not accumulated. A herd-level methane
total requires per-day beef methane, which is a modelling gap rather
than a plumbing one.

**The combined grouping scenario cannot be selected for a run.** The
cow-calf, stocker and feedlot grouping scenario is defined and its
mapping is correct, but it is rejected at selection. A replacement heifer
promoting to cow on first calving reaches pen assignment, which cannot
resolve a beef cow to a pen combination without dispatching on her live
reproduction state. That dispatch does not exist. Rejecting at selection
beats failing part-way through a multi-year run. The same unresolved
state exists in the cow-calf-only scenario and predates this work.

**Backgrounding duration is not a scenario variable.** The stocker phase
ends on target weight or on a maximum-days ceiling, not a configured
duration, so a scenario cannot vary it. The extended-backgrounding
scenario was removed rather than shipped with no effect.

**The scenario runner does not drive simulations.** Running a herd
requires a populated input manager, the weather and feed subsystems,
and the ration formulation cycle. The runner therefore takes the herd
drive as an injectable callable and composes scenarios, replicates
and comparison around it. The default raises rather than returning,
so a caller cannot obtain plausible-looking numbers from a herd that
was never driven. Nothing in a simulation run calls the runner or
`AnimalModuleReporter.get_beef_herd_summary`; both are library entry
points awaiting a caller, and the only end-to-end test is skipped for
that reason.

**Calf crop counts survivors.** The herd summary divides lifetime calvings
by the cows currently in the herd, not by the cows exposed during the
breeding season. Cows culled, sold or died mid-season have already left the
cohort, so the figure is biased upward. An unbiased denominator is not
recoverable from current state.

## Coefficient provenance

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

## OpenSpec

The four OpenSpec artifacts at `openspec/changes/beef-beefgem-management/`
(`proposal.md`, `design.md`, `specs.md`, `tasks.md`) were derived from the
`.md` execution plan and are the authoritative task checklist for
`/apply-plan`.
