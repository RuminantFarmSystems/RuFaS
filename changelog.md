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

- [2011](https://github.com/RuminantFarmSystems/MASM/pull/2011) - [minor change] [Animal] Implements the Animal Growth submodule logic and tests.
- [2021](https://github.com/RuminantFarmSystems/MASM/pull/2021) - [minor change] [Animal] **Adds dependency**. Creates a new `MilkProduction` submodule and several support submodules to calculate milk production.
- [2022](https://github.com/RuminantFarmSystems/MASM/pull/2022) - [minor change] [Manure] Removes DefaultEnum class and all references to it in the Manure module.
- [2006](https://github.com/RuminantFarmSystems/MASM/pull/2006) - [minor change] [Manure] Adds a method to determine storage manure temperature based on outdoor air temperature for use in calculations of emissions associated with Manure Storages.
- [2023](https://github.com/RuminantFarmSystems/MASM/pull/2023) - [minor change] [Manure] Fixes calculation of organic bedding dry solids added to manure in manure handler.
- [2025](https://github.com/RuminantFarmSystems/MASM/pull/2025) - [minor change] [Formatting] Sorts import statements in codebase.
- [2004](https://github.com/RuminantFarmSystems/MASM/pull/2004) - [minor change] [Animal] Implement the animal digestive system in the biophysical folder.
- [2017](https://github.com/RuminantFarmSystems/MASM/pull/2017) - [minor change] [Animal] Deduplicates references to lactation parameters in the `LactationCurve` submodule and reorganizes structure to be consistent with other animal submodules.
- [1985](https://github.com/RuminantFarmSystems/MASM/pull/1985) - [minor change] [TaskManager] extracts all the input data values (for all input variables from JSON input files) for each task and combines them into a single CSV file for side-by-side comparison.
- [2031](https://github.com/RuminantFarmSystems/MASM/pull/2031) - [minor change] [Formatting] Changes all relative import statements that import from higher-level modules to be absolute import statements.
- [2032](https://github.com/RuminantFarmSystems/MASM/pull/2032) - [minor change] [Soil] Change the daily routine sequence to prevent unrealistic decomposition.
- [2029](https://github.com/RuminantFarmSystems/MASM/pull/2029) - [minor change] [EEE] Adding tests for emission.py (2/2)
- [2033](https://github.com/RuminantFarmSystems/MASM/pull/2033) - [minor change] [InputManager] Consolidate methods for adding data to the Input Manager at runtime.
- [2039](https://github.com/RuminantFarmSystems/MASM/pull/2039) - [minor change] [Animal][Testing] Renames AnimalNutrients to Nutrients and adds full unit testing coverage for this class.
- [2014](https://github.com/RuminantFarmSystems/MASM/pull/2014) - [minor change] [Feed Storage] Fixes the Feed Storage mass degradation routines to properly account for mass and moisture loss, and updates E2E test suite to test these changes.
- [2054](https://github.com/RuminantFarmSystems/MASM/pull/2054) - [minor change] [e2e Testing] Adding end-to-end testing coverage for the Crop and Soil module.
- [1575](https://github.com/RuminantFarmSystems/MASM/pull/1575) - [minor change] [OutputManager] Adds options to periodically dump variables pool to a JSON file to help manage the size of the pool during a simulation.
- [2047](https://github.com/RuminantFarmSystems/MASM/pull/2047) - [minor change] [Soil and Crop] Break down methods in the fields_data_reporter into smaller and more specific methods.
- [1945](https://github.com/RuminantFarmSystems/MASM/pull/1945) - [minor change] [Animal] Implements Animal Genetics submodule.
- [2048](https://github.com/RuminantFarmSystems/MASM/pull/2048) - [minor change] [Animal][Testing] Adds end to end testing for Animal domain.
- [1809](https://github.com/RuminantFarmSystems/MASM/pull/1809) - [minor change] [InputManager] Extract the validation methods from InputManager.
- [2045](https://github.com/RuminantFarmSystems/MASM/pull/2045) - [minor change] [Documentation] Regenerates the Sphinx HTML documentation.
- [2050](https://github.com/RuminantFarmSystems/MASM/pull/2050) - [minor change] [Crop & Soil][Feed Storage] Disentangle the Crop & Soil and Feed Storage modules.
- [2061](https://github.com/RuminantFarmSystems/MASM/pull/2061) - [minor change] [DataValidator] Removed the usage of OutputManager in DataValidator.
- [2057](https://github.com/RuminantFarmSystems/MASM/pull/2057) - [minor change] [Crop & Soil][Manure] Disentangle the Crop & Soil and Manure modules.
- [2059](https://github.com/RuminantFarmSystems/MASM/pull/2059) - [minor change] [Crop & Soil][GeneralConstants] Update references to constants in Crop and Soil module to use GeneralConstants.
- [1866](https://github.com/RuminantFarmSystems/MASM/pull/1866) - [minor change] [Metadata] Adds minimums for some Animal module inputs in metadata.
- [2066](https://github.com/RuminantFarmSystems/MASM/pull/2066) - [minor change] [OutputManager] Handles data origins info and enables user control over reporting detail levels.
- [2069](https://github.com/RuminantFarmSystems/MASM/pull/2069) - [minor change] [Crop & Soil] Flatten the units in SC module.
- [2076](https://github.com/RuminantFarmSystems/MASM/pull/2076) - [minor change] [Crop & Soil] Removes TODOs from the Crop & Soil module.
- [1785](https://github.com/RuminantFarmSystems/MASM/pull/1785) - [minor change] [TaskManager] Adds sobol and morris samplers, updates argument names.
- [2093](https://github.com/RuminantFarmSystems/MASM/pull/2093) - [minor change] [Testing] Increases tolerance level for comparing values changed in E2E testing results comparisons.
- [2086](https://github.com/RuminantFarmSystems/MASM/pull/2086) - [minor change] [Animal] Updates default parity fraction.
- [2090](https://github.com/RuminantFarmSystems/MASM/pull/2090) - [minor change] [Crop & Soil] Restructures CropData class.
- [1836](https://github.com/RuminantFarmSystems/MASM/pull/1836) - [minor change] [Feed] Updates default prices in default_feed.json using average prices sourced by Kristan (detailed in sheet in PR).
- [2119](https://github.com/RuminantFarmSystems/MASM/pull/2119) - [minor change] [OutputManager] Make the log routing usable by other modules.
- [2046](https://github.com/RuminantFarmSystems/MASM/pull/2046) - [major change] [Data Collection App] Integrates the Data Collection App into the RuFaS repository and adds a RuFaS task type to update it.

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
