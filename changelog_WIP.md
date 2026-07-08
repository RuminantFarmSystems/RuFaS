# WIP (Work In Progress) Changelog

## Readme

A **changelog** is a structured record of changes made to the codebase over time. It documents new features, bug fixes, and improvements, giving both developers and users a transparent view of how the project evolves across versions. A changelog ensures that the entire development process is **trackable**, improves **collaboration** by clearly communicating changes across team members, and offers **transparency** to users and stakeholders. Additionally, it helps with **debugging** by highlighting specific updates or changes that could potentially introduce new issues.

This **WIP Changelog** records development changes in progress and not yet included in a version release.

### Each changelog entry must include

- PR #. Just the number, omit "PR" and "#". Include a link to the Pull Request using the format "\[<PR #>\]\(\<link to PR\>\)" (see the example below).
- Major or minor change. How big are the changes in the PR? Would you nominate it for a Major version upgrade? Choose either "Major change" or "minor change" in square brackets.
- Impact area: What parts of the codebase, inputs, or outputs are affected by this PR? Some options are Animal Module, Manure Module, Output structure, whole code base, etc. Put this in square brackets. If more than one impact area is needed, use multiple square brackets.
- A brief and concise description of change. Keep it short, yet informative. A few sentences should be enough. Avoid using broad and general statements such as "update xyz", it should be "update xyz to abc".

### Example Entry

- [123](https://github.com/RuminantFarmSystems/RuFaS/pull/123) - [Major change/ minor change] [Impact Area] Short description of the change or feature.

---

## Changelog Entries


### Next Version Updates

- [2994](https://github.com/RuminantFarmSystems/RuFaS/pull/2994) - [minor change] [NoInputChange] [OutputChange] Adds minimums to urine nitrogen equation.
- [2997](https://github.com/RuminantFarmSystems/RuFaS/pull/2997) - [minor change] [NoInputChange] [OutputChange] Updates throughput in tractor dataset for combine headers.
- [2998](https://github.com/RuminantFarmSystems/RuFaS/pull/2998) - [minor change] [NoInputChange] [OutputChange] Moved changelog entries to reflect what was in v1.0. Brought changes in 2994 and 2997 into one branch.
- [3091](https://github.com/RuminantFarmSystems/RuFaS/pull/3091) - [minor change] [InputChange] [OutputChange] Fixes large seedbed conditioner entry in `tractor_dataset.csv` input.
- [2793](https://github.com/RuminantFarmSystems/RuFaS/pull/2793) - [minor change] [Animal] [OutputManager] [NoInputChange] [OutputChange] Track and summarize when effective DMI falls below the empirical domain of manure equations for lactating and dry cows at end of simulation.
- [2743](https://github.com/RuminantFarmSystems/RuFaS/pull/2743) - [minor change] [NoInputChange] [NoOutputChange] Fix broken IM unit test.
- [2772](https://github.com/RuminantFarmSystems/RuFaS/pull/2772) - [minor change] [SimulationEngine] [NoInputChange] [NoOutputChange] Refactors `SimulationEngine`.`_daily_simulation()` to accommodate isolating modules.
- [2813](https://github.com/RuminantFarmSystems/RuFaS/pull/2813) - [minor change] [Docs] [NoInputChange] [NoOutputChange] Updates branching and versioning policy docs.
- [2867](https://github.com/RuminantFarmSystems/RuFaS/pull/2867) - [minor change] [NoInputChange] [NoOutputChange] Updates expand_data_temporally() util function to offer options of full simulation expansion and front-padding data.
- [2902](https://github.com/RuminantFarmSystems/RuFaS/pull/2902) - [minor change] [NoInputChange] [NoOutputChange] Add v1.0.0 release notes.
- [2909](https://github.com/RuminantFarmSystems/RuFaS/pull/2909) - [minor change] [pyproject.toml][NoInputChange] [NoOutputChange] Separate dependencies by category in `pyproject.toml` file and create a RuFaS v1.0.0 pinned `constraints-release.txt` file.
- [2740](https://github.com/RuminantFarmSystems/RuFaS/pull/2740) - [minor change] [NoInputChange] [NoOutputChange] Added warnings for feed purchases exceeding advance purchase allowance/
- [2740](https://github.com/RuminantFarmSystems/RuFaS/pull/2740) - [minor change] [NoInputChange] [NoOutputChange] Added warnings for feed purchases exceeding advance purchase allowance.
- [2921](https://github.com/RuminantFarmSystems/RuFaS/pull/2921) - [minor change] [OutputManager][NoInputChange] [NoOutputChange] Override incorrect fill type for complex data structure data padding.
- [2924](https://github.com/RuminantFarmSystems/RuFaS/pull/2924) - [minor change] [NoInputChange] [NoOutputChange] Updated advance purchase allowance to prevent excessive warnings for example run.
- [2929](https://github.com/RuminantFarmSystems/RuFaS/pull/2929) - [minor change] [GraphGenerator] [NoInputChange] [NoOutputChange] Sanitizes non-numerical data sent to graph generator to allow graphing to occur despite.
- [2932](https://github.com/RuminantFarmSystems/RuFaS/pull/2932) - [minor change] [SimulationEngine] [NoInputChange] [NoOutputChange] Enabled Field only simulation.
- [2916](https://github.com/RuminantFarmSystems/RuFaS/pull/2916) - [minor change] [Cross Validation] [NoInputChange] [NoOutputChange] Added cross validation rules for the Crop and Soil module.
- [2925](https://github.com/RuminantFarmSystems/RuFaS/pull/2925) - [minor change] [NoInputChange] [NoOutputChange] Fix the `graph_and_report` option in report_generation.py.
- [2907](https://github.com/RuminantFarmSystems/RuFaS/pull/2907) - [minor change] [NoInputChange] [OutputChange] Fix the FarmGrownFeed Emissions unit issue. The mirror issue of [Fix FarmGrownFeed Emissions Unit on test #2908](https://github.com/RuminantFarmSystems/RuFaS/pull/2908) to update `dev`.
- [2934](https://github.com/RuminantFarmSystems/RuFaS/pull/2934) - [minor change] [NoInputChange] [NoOutputChange] [Animal][Reproduction] Refactor `Reproduction.execute_cow_ed_protocol()`.
- [2949](https://github.com/RuminantFarmSystems/RuFaS/pull/2949) - [minor change] [NoInputChange] [NoOutputChange] [Verbosity] Updates CLI verbosity arg to override verbosity of full run including task manager verbosity.
- [2947](https://github.com/RuminantFarmSystems/RuFaS/pull/2947) - [minor change] [NoInputChange] [NoOutputChange] [Animal][Reproduction] Created weather data cross validation rules.
- [2948](https://github.com/RuminantFarmSystems/RuFaS/pull/2948) - [minor change] [Feeds][NoInputChange] [NoOutputChange] Removes feed id maximums in metadata properties.
- [2960](https://github.com/RuminantFarmSystems/RuFaS/pull/2960) - [minor change] [Docs][NoInputChange] [NoOutputChange] Adds SME evaluation report for v1.0.
- [2734](https://github.com/RuminantFarmSystems/RuFaS/pull/2734) - [minor change] [InputChange][OutputChange][Animal] Implements the Genetics submodule.
- [2939](https://github.com/RuminantFarmSystems/RuFaS/pull/2939) - [minor change] [InputChange][OutputChange][SimulationEngine] Disentangles data sharing between biophysical modules in SimulationEngine.
- [2971](https://github.com/RuminantFarmSystems/RuFaS/pull/2971) - [minor change] [InputChange][OutputChange][Feed] Reorganizes feed input structure and adapts feed input handling to accommodate new structure.
- [2968](https://github.com/RuminantFarmSystems/RuFaS/pull/2968) - [minor change] [InputChange][OutputChange][Animal] Refactored HerdManager's daily_routine.
- [2809](https://github.com/RuminantFarmSystems/RuFaS/pull/2809) - [minor change] [Animal] [NoInputChange] [NoOutputChange] Reorders grouping of attributes in some HerdStatistics methods, updates docstrings.
- [2983](https://github.com/RuminantFarmSystems/RuFaS/pull/2983) - [minor change] [Animal] [NoInputChange] [NoOutputChange] Deleted data padder function in AnimalModuleReporter.
- [2984](https://github.com/RuminantFarmSystems/RuFaS/pull/2984) - [minor change] [Manure] [NoInputChange] [NoOutputChange] Adds manure stream compatibility check to Separators to enforce that Separators cannot be first processors in a chain.
- [2931](https://github.com/RuminantFarmSystems/RuFaS/pull/2931) - [minor change] [NoInputChange] [OutputChange] automatically add "simulation_day" to info_maps when variables are added to OutputManager, improves data padding usability.
- [2991](https://github.com/RuminantFarmSystems/RuFaS/pull/2991) - [minor change] [NoInputChange] [NoOutputChange] Updated the docstrings in the Crop and Soil module.
- [3002](https://github.com/RuminantFarmSystems/RuFaS/pull/3002) - [minor change] [InputChange] [NoOutputChange] Adds animals-only simulation type.
- [3004](https://github.com/RuminantFarmSystems/RuFaS/pull/3004) - [minor change] [NoInputChange] [NoOutputChange] Removes public `available_feeds` property from FeedManager.
- [3000](https://github.com/RuminantFarmSystems/RuFaS/pull/3000) - [minor change] [NoInputChange] [NoOutputChange] Updated the error messages for all biophysical modules.
- [2715](https://github.com/RuminantFarmSystems/RuFaS/pull/2715) - [minor change] [Animal] [NoInputChange] [OutputChange] Renames the 305-day milk yield output from `milk_production_305days_herd_mean` to `milk_305_day_yield_herd_mean`, splits the calculation into a pure Wood's-curve integral and a per-cow simulation estimate, and adds L1/L2/L3+ herd-level reporting.
- [3022](https://github.com/RuminantFarmSystems/RuFaS/pull/3022) - [minor change] [Tests] [NoInputChange] [NoOutputChange] Adds missing changelog entry for #2715 and fixes the one mypy error it introduced by typing the `history` parameter of `_make_milk_production` in `test_milk_production.py`.
- [2623](https://github.com/RuminantFarmSystems/RuFaS/pull/2623) - [minor change] [Manure] [Crop and Soil] [InputChange] [OutputChange] Adds a `daily_spread` block to per-field manure schedules that applies DailySpread manure to the field daily, either capped by N/P targets or by emptying all available DailySpread manure.
- [3003](https://github.com/RuminantFarmSystems/RuFaS/pull/3003) - [minor change] [Animal] [InputChange] [OutputChange] Added `calf_mortality_rate` and `heifer_mortality_rate` user inputs to model pre-wean and post-wean youngstock mortality.
- [3032](https://github.com/RuminantFarmSystems/RuFaS/pull/3032) - [minor change] [Animal] [NoInputChange] [NoOutputChange] Updates and fixes docstrings to be more consistently formatted.
- [3027](https://github.com/RuminantFarmSystems/RuFaS/pull/3027) - [minor change] [SimulationEngine] [NoInputChange] [NoOutputChange] Moves daily animal update earlier in day to align feed reporting across `HerdManager` and `FeedManager` modules.
- [3026](https://github.com/RuminantFarmSystems/RuFaS/pull/3026) - [minor change] [E2ETesting] [NoInputChange] [NoOutputChange] Fixes E2E test results comparison tolerence.
- [2999](https://github.com/RuminantFarmSystems/RuFaS/pull/2999) - [minor change] [Cross Validation] [Feed Storage] [NoInputChange] [NoOutputChange] Added cross validation rules for feed storage inputs.
- [3024](https://github.com/RuminantFarmSystems/RuFaS/pull/3024) - [minor change] [DataValidator] [NoInputChange] [NoOutputChange] Adds path to input to error/warning messages in `DataValidator` for easier invalid input fixing.
- [3033](https://github.com/RuminantFarmSystems/RuFaS/pull/3033) - [minor change] [Tests] [pyproject.toml] [NoInputChange] [NoOutputChange] Bumps `pytest` from `==7.4.4` to `>=9.0.3`, swaps the unmaintained `pytest-lazy-fixture` for the maintained `pytest-lazy-fixtures` fork.
- [3046](https://github.com/RuminantFarmSystems/RuFaS/pull/3046) - [minor change] [Feed Storage] [NoInputChange] [NoOutputChange] Updates and fixes docstrings to be more consistently formatted.
- [3048](https://github.com/RuminantFarmSystems/RuFaS/pull/3048) - [minor change] [EEE] [NoInputChange] [NoOutputChange] Updates and fixes the EEE module docstrings to be more consistently formatted.
- [3052](https://github.com/RuminantFarmSystems/RuFaS/pull/3052) - [minor change] [e2e-testing] [NoInputChange] [NoOutputChange] Updates and e2e-testing filters.
- [3041](https://github.com/RuminantFarmSystems/RuFaS/pull/3041) - [minor change] [NoInputChange] [NoOutputChange] [OutputManager] [GraphGenerator] [ReportGenerator] Updates docstrings in post-processing modules to follow NumPy-style format.
- [3071](https://github.com/RuminantFarmSystems/RuFaS/pull/3071) - [minor change] [NoInputChange] [NoOutputChange] [Manure] Updates `Manure` module docstrings.
- [3050](https://github.com/RuminantFarmSystems/RuFaS/pull/3050) - [minor change] [FieldManager] [SimulationEngine] [NoInputChange] [NoOutputChange] Moves the field config data gathering out of `FieldManager.__init__()` into `SimulationEngine`, passing field data as a parameter instead.
- [3074](https://github.com/RuminantFarmSystems/RuFaS/pull/3074) - [minor change] [CropSchedule][NoInputChange] [NoOutputChange] Adds check for incompatibility between planting and harvesting schedules for crops.
- [3072](https://github.com/RuminantFarmSystems/RuFaS/pull/3072) - [minor change] [main.py] [NoInputChange] [NoOutputChange] Moves `main.py` into `RUFAS/` for better packaging while maintaining legacy `main.py` script access.
- [3054](https://github.com/RuminantFarmSystems/RuFaS/pull/3054) - [minor change] [Animal] [Reproduction] [NoInputChange] [NoOutputChange] Adds early-exit guard in presynch and OvSynch hormone schedule setup to skip already-pregnant cows.
- [3084](https://github.com/RuminantFarmSystems/RuFaS/pull/3084) - [minor change] [Feeds] [NoInputChange] [NoOutputChange] Adds feed config validation in-simulation.
- [3077](https://github.com/RuminantFarmSystems/RuFaS/pull/3077) - [minor change] [Animal] [NoInputChange] [OutputChange] Fix `herd_reproduction_statistics` being reset every simulation day, so the end-of-simulation breeding and conception outputs tally over the whole simulation.
- [3094](https://github.com/RuminantFarmSystems/RuFaS/pull/3094) - [minor change] [NoInputChange] [NoOutputChange] Updates and aligns formatting and content of docstrings in InputManager and DataValidator classes.
- [3047](https://github.com/RuminantFarmSystems/RuFaS/pull/3047) - [minor change] [Animal] [NoInputChange] [OutputChange] Adds heifer average daily gain (ADG) reporting by pen and by heifer animal type (Heifer I, II, III) to `HerdStatistics` and `AnimalModuleReporter`.
- [3070](https://github.com/RuminantFarmSystems/RuFaS/pull/3070) - [minor change] [Config] [InputChange] [NoOutputChange] Removes the `random_seed` field from all 6 config input files and from 3 config input files in helpful_scripts.
- [3087](https://github.com/RuminantFarmSystems/RuFaS/pull/3087) - [minor change] [SimulationEngine] [NoInputChange] [NoOutputChange] Extracts post-loop logic from `SimulationEngine.simulate()` into `_post_loop_processing()`, `_post_loop_reporting()`, and `_post_loop_logging()`.
- [3098](https://github.com/RuminantFarmSystems/RuFaS/pull/3098) - [minor change] [InputManager] [InputChange] [NoOutputChange] Adds actually nulled input blobs and logic to not silently load defaults into pool.
- [3049](https://github.com/RuminantFarmSystems/RuFaS/pull/3049) - [minor change] [Utility] [NoInputChange] [NoOutputChange] Updates docstrings across 9 utility files to NumPy-style format.
- [3100](https://github.com/RuminantFarmSystems/RuFaS/pull/3100) - [minor change] [Maintenance] [NoInputChange] [NoOutputChange] Aligns formatting on docstrings for `tuple` returns.
- [3043](https://github.com/RuminantFarmSystems/RuFaS/pull/3043) - [minor change] [Animal] [Ration] [NoInputChange] [NoOutputChange] Refactor `Pen.formulate_optimized_ration` to remove the `# noqa: C901`; behavior unchanged.
- [3104](https://github.com/RuminantFarmSystems/RuFaS/pull/3104) - [minor change] [Testing] [NoInputChange] [NoOutputChange] Updates unit testing coverage for add_error calls added in PR 3000.
- [3115](https://github.com/RuminantFarmSystems/RuFaS/pull/3115) - [minor change] [Animal] [NoInputChange] [NoOutputChange] Adds separate tracking for unmitigated vs. mitigated enteric methane for cows.
