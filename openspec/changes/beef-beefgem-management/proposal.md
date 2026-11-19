# Proposal — BeefGEM Management Enhancement Layer

## Summary
Add management-level enhancements to the RuFaS beef cattle module
on top of the three native production segments (feedlot, cow-calf,
stocker). BeefGEM introduces configuration flags, modifiers, and
scenario comparison tools that are off by default and backward
compatible with all existing simulations.

## Problem statement
The three native beef segments (PR #32 feedlot, PR #33-36 cow-calf,
PR #47 stocker) implement NRC 2016 biophysical equations correctly
but lack:
- A finishing system flag to distinguish grain-fed vs grass-fed
  enteric CH4 pathways
- Stocker limit-feeding as a management lever
- NASEM 2016 enteric CH4 equations for stocker and grass-fed
  finishing
- Herd population summary metrics for scenario comparison
- A scenario runner to compare named management strategies
- Heat stress (THI-based) DMI and NEm modifiers
- Compensatory gain modelling after nutritional restriction

Without these, the beef module cannot support the management
decision-support use cases that are the primary value of whole-farm
simulation.

## Scope
**In scope:**
- FinishingSystem enum (GRAIN_FED / GRASS_FED)
- Limit-feeding diet system for stocker (LIMIT_FEED)
- NASEM 2016 Eq.6.8 enteric CH4 for stocker on forage
- Mits3 enteric CH4 for grass-fed feedlot
- Herd population summary reporter (4 metrics)
- beef_scenario_runner.py with compare_scenarios() → pd.DataFrame
- 8 pre-built named scenarios
- THI-based heat stress DMI/NEm modifiers (opt-in)
- Compensatory gain multiplier after restriction (opt-in)

**Out of scope:**
- Pasture growth model
- Genetic improvement simulation
- Economic output
- Sexed-pen management

## Prerequisite
All three native segments must be merged to dev-msf before
BeefGEM begins:
- PR #32 (feedlot) ✅ merged
- PR #33-#36 (cow-calf) ✅ merged
- PR #47 (stocker) — pending review

## Implementation strategy
Single PR: feature/beef-beefgem-management
Phases implemented in strict dependency order: A → B → C → D
Estimated effort: 8.5 developer-days

## Backward compatibility
Every feature is opt-in via a default value that preserves current
behavior. No existing simulation will change output without explicit
configuration.

## Rollback plan
Since all new features are gated by default-off config flags, a
rollback simply means not enabling the flags. No data migration
required. If the PR is reverted entirely, all three native segments
continue to work unchanged.
