# Changelog

## Readme

A **changelog** is a structured record of changes made to the codebase over time. It documents new features, bug fixes, and improvements, giving both developers and users a transparent view of how the project evolves across versions. A changelog ensures that the entire development process is **trackable**, improves **collaboration** by clearly communicating changes across team members, and offers **transparency** to users and stakeholders. Additionally, it helps with **debugging** by highlighting specific updates or changes that could potentially introduce new issues. 

### Each changelog entry must include
- PR #. Just the number, omit "PR" and "#". Include a link to the Pull Request using the format "\[<PR #>\]\(\<link to PR\>\)" (see the example below).
- Major or minor change. How big are the changes in the PR? Would you nominate it for a Major version upgrade? Choose either "Major change" or  "minor change" in square brackets.
- Impact area: What parts of the codebase, inputs, or outputs are affected by this PR? Some options are Animal Module, Manure Module, Output structure, whole code base, etc. Put this in square brackets. If more than one impact area is needed, use multiple square brackets.
- A brief and concise description of change. Keep it short, yet informative. A few sentences should be enough. Avoid using broad and general statements such as "update xyz", it should be "update xyz to abc".

### Example Entry
- [123](https://github.com/RuminantFarmSystems/MASM/pull/123) - [Major change/ minor change] [Impact Area] Short description of the change or feature.

---
## Changelog Entries

### Current version
v0.9.1

### Next Version Updates

- [1968](https://github.com/RuminantFarmSystems/MASM/pull/1968) - [minor change] [Changelog] Move the changelog from a Google sheet into a markdown document in the repository.
- [1948](https://github.com/RuminantFarmSystems/MASM/pull/1948) - [minor change] [Soil and Crop] Utilize a residue tracker property method in the layer data pool that sums structural and metabolic litter.
- [1944](https://github.com/RuminantFarmSystems/MASM/pull/1944) - [minor change] [Documentation] Updates the Sphinx GitHub Action so that it can be triggered manually on specific branches and modifies it to not remove any .rst files.