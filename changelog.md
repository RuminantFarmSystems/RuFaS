# Changelog

## Readme

A **changelog** is a structured record of changes made to the codebase over time. It documents new features, bug fixes, and improvements, giving both developers and users a transparent view of how the project evolves across versions. A changelog ensures that the entire development process is **trackable**, improves **collaboration** by clearly communicating changes across team members, and offers **transparency** to users and stakeholders. Additionally, it helps with **debugging** by highlighting specific updates or changes that could potentially introduce new issues.

### Each changelog entry must include

- PR #. Just the number, omit "PR" and "#". Include a link to the Pull Request using the format "\[<PR #>\]\(\<link to PR\>\)" (see the example below).
- Major or minor change. How big are the changes in the PR? Would you nominate it for a Major version upgrade? Choose either "Major change" or "minor change" in square brackets.
- Impact area: What parts of the codebase, inputs, or outputs are affected by this PR? Some options are Animal Module, Manure Module, Output structure, whole code base, etc. Put this in square brackets. If more than one impact area is needed, use multiple square brackets.
- A brief and concise description of change. Keep it short, yet informative. A few sentences should be enough. Avoid using broad and general statements such as "update xyz", it should be "update xyz to abc".

### Example Entry

- [123](https://github.com/RuminantFarmSystems/MASM/pull/123) - [Major change/ minor change] [Impact Area] Short description of the change or feature.

---

## Changelog Entries

### Current version

v0.9.2

### Next Version Updates

- [2021](https://github.com/RuminantFarmSystems/MASM/pull/2021) - [minor change] [Animal] **Adds dependency**. Creates a new `MilkProduction` submodule and several support submodules to calculate milk production.
- [2022](https://github.com/RuminantFarmSystems/MASM/pull/2022) - [minor change] [Manure] Removes DefaultEnum class and all references to it in the Manure module.
- [2023](https://github.com/RuminantFarmSystems/MASM/pull/2023) - [minor change] [Manure] Fixes calculation of organic bedding dry solids added to manure in manure handler.
- [2025](https://github.com/RuminantFarmSystems/MASM/pull/2025) - [minor change] [Formatting] Sorts import statements in codebase.
- [2017](https://github.com/RuminantFarmSystems/MASM/pull/2017) - [minor change] [Animal] Deduplicates references to lactation parameters in the `LactationCurve` submodule and reorganizes structure to be consistent with other animal submodules.
- [1985](https://github.com/RuminantFarmSystems/MASM/pull/1985) - [minor change] [TaskManager] extracts all the input data values (for all input variables from JSON input files) for each task and combines them into a single CSV file for side-by-side comparison.

### v0.9.2

- [1968](https://github.com/RuminantFarmSystems/MASM/pull/1968) - [minor change] [Changelog] Move the changelog from a Google sheet into a markdown document in the repository.
- [1976](https://github.com/RuminantFarmSystems/MASM/pull/1976) - [minor change] [EEE] Add unit tests for the Emission module.
- [1977](https://github.com/RuminantFarmSystems/MASM/pull/1977) - [minor change] [EEE] Improve emission.py codebase and clarity.
- [1948](https://github.com/RuminantFarmSystems/MASM/pull/1948) - [minor change] [Soil and Crop] Utilize a residue tracker property method in the layer data pool that sums structural and metabolic litter.
- [1980](https://github.com/RuminantFarmSystems/MASM/pull/1980) - [minor change] [Soil and Crop] Set return value and add warning when silt and clay are zero.
- [1973](https://github.com/RuminantFarmSystems/MASM/pull/1973) - [minor change] [OutputManager] Avoid global variable usage of output manager [2/2].
- [1870](https://github.com/RuminantFarmSystems/MASM/pull/1870) - [minor change] [Soil and Crop] Partition denitrified nitrates between nitrous oxide emissions and dinitrogen emissions,
- [1974](https://github.com/RuminantFarmSystems/MASM/pull/1974) - [minor change] [Animal] Establishes the AnimalPhosphorusStatus calculator class and the AnimalPhosphorus class to perform the daily phosphorus update for each animal for eventual incorporation into the newly refreshed Animal module.
- [1944](https://github.com/RuminantFarmSystems/MASM/pull/1944) - [minor change] [GitHub Actions] Updates the Sphinx GitHub Action so that it can be triggered manually on specific branches and modifies it to not remove any .rst files.
- [1986](https://github.com/RuminantFarmSystems/MASM/pull/1986) - [minor change] [Animal] Creates the biophysical folder, and necessary files with empty class and folders for the redesigned animal module.
- [1979](https://github.com/RuminantFarmSystems/MASM/pull/1979) - [minor change] [EEE] Updates synthetic fertilizer emissions to be partitioned by crop schedule instead of by dry yield.
- [1784](https://github.com/RuminantFarmSystems/MASM/pull/1784) - [minor change] [Task Manager][Feed Storage] Adds end-to-end testing routine for the Feed Storage module which can be extended to test other parts of RuFaS.
- [1998](https://github.com/RuminantFarmSystems/MASM/pull/1998) - [minor change] [GitHub Actions] Adds if statement to make sure there is a PR to comment on before attempting to post a comment.
- [2000](https://github.com/RuminantFarmSystems/MASM/pull/2000) - [minor change] [CurrentWeatherConditions] Removed optional type hints.
- [1989](https://github.com/RuminantFarmSystems/MASM/pull/1989) - [minor change] [Animal] Method formulate_ration now correctly returns pen.ration_per_animal instead of pen.ration.
- [2001](https://github.com/RuminantFarmSystems/MASM/pull/2001) - [minor change] [E2E Testing] Changes E2ETestResultsComparer so that it constructs file paths properly on Windows machines.
- [2010](https://github.com/RuminantFarmSystems/MASM/pull/2010) - [minor change] Updates liquid manure nitrogen input source used to calculate N2O emissions for manure storages.
- [2002](https://github.com/RuminantFarmSystems/MASM/pull/2002) - [minor change] [Manure] Adds a method to determine the ambient inside barn temperature based on the outdoor air temperature for use in calculations of emissions associated with Manure Handlers.
- [2009](https://github.com/RuminantFarmSystems/MASM/pull/2009) - [minor change] [Time][Feed Storage] Modifies the init of Time so that a time object can be created without needing config from IM. This in turn allows us to avoid deep copies used for time management.
