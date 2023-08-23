[![Testing](https://github.com/RuminantFarmSystems/MASM/actions/workflows/testing_pytest.yml/badge.svg)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/testing_pytest.yml)
[![Linting](https://github.com/RuminantFarmSystems/MASM/actions/workflows/lint_flake8.yml/badge.svg)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/lint_flake8.yml)
[![Coverage](https://img.shields.io/badge/coverage-85%25-yellowgreen)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/coverage_pytest-cov.yml)
# Vision
To support research and sustainable decision-making in ruminant animal production through a state-of-art, open-source modeling environment that is continuously adapting as technology and scientific knowledge advance.

# Mission
To build an integrated, whole-farm model that simulates milk, meat, and crop production, greenhouse gas emissions, water quality impacts, soil health, and other sustainability outcomes of ruminant farms. We strive to achieve the highest standards for prediction accuracy, code structure and clarity, documentation, and accessibility. Through continuous learning and improvement of our methods and algorithms, we are creating an open and inclusive platform for scientific collaboration. 

# Priorities
When decision-making is difficult and doubtful, we use these as our North Star to navigate the uncertain and unknown world.
## Current
* Deliver Minimum Viable Product (MVP)
* Payoff the tech debt
* Establish a positive and inclusive team culture

## Past
N/A

# 2023 H2 Roadmap
## Milestone 1: Aug 11th
[GitHub Milestone](https://github.com/RuminantFarmSystems/MASM/milestone/2)

Dev Team:
|Title|Owner|Status|Priority|Remarks|
|--|--|--|--|--|
Finish Input Manager Development|Niko, Allister, Pooya|Complete|P0
Finish Input Manager MetaData|Allister, Niko|Complete|P0
Confirm the validity of inputs||Consolidated||Will be done in MS 2
Design and implement EEE |Pooya,Ed|In Progress||Moved to MS 2
Finish CBPB and Compost for Manure Module |Michael, Loi|Partially Completed||Compost  Not Complete, moved to MS 2

SMEs:
|Title|Owner|Status|Priority|Remarks|
|--|--|--|--|--|
Develop plan and begin model accuracy evaluation execution
Develop plan and begin sensitivity analysis execution
Complete Manure Module Documentation and Design Docs for remaining functionality
Review, modify, and approve EEE design doc. Evaluate its implementation.

## Milestone 2: Sep 30th
[GitHub Milestone](https://github.com/RuminantFarmSystems/MASM/milestone/4)

Dev Team:
|Title|Owner|Status|Priority|Remarks|
|--|--|--|--|--|
Design and implement EEE (Review progress on this)
Finish Compost for Manure Module 
Redesign and implement Feed storage module ||||Moved to MS 2.5
Revisit the Animal Module design – Refactoring -- Animal Manager
Revisit the Animal Module design – Refactoring -- Animal Ration formulation
Revisit the Animal Module design – Refactoring -- Animal Life Cycle|||| Moved to MS 2.5
Deprecate the output handler, add missing functionalities, and reports to OM
Go through the entire codebase and ensure IM is the only way we are receiving input data||||[IM Integration tracking](https://docs.google.com/spreadsheets/d/1k8J6MelPrsrz6Tv4fQNAG-kLSN7oQTQOCEy3I6F0IqU/edit?usp=sharing)


SMEs:
|Title|Owner|Status|Priority|Remarks|
|--|--|--|--|--|
Complete model evaluation
Complete Sensitivity Analysis
Complete External/Scientific Documentation for Animal, Manure, & EEE modules and put on GitHub
Complete Cohort 1 Pilot testing

## Milestone 2.5: Oct 31th
[GitHub Milestone](https://github.com/RuminantFarmSystems/MASM/milestone/5)

Dev Team:
|Title|Owner|Status|Priority|Remarks|
|--|--|--|--|--|
Redesign and implement the Feed storage module
Refactor Animal Module -- Animal Life Cycle

SMEs:
|Title|Owner|Status|Priority|Remarks|
|--|--|--|--|--|

## Milestone 3: Dec 31th
[GitHub Milestone](https://github.com/RuminantFarmSystems/MASM/milestone/6)

Dev Team:
|Title|Owner|Status|Priority|Remarks|
|--|--|--|--|--|
Revisit classes.py
Deprecate DB(s)
Deprecate output handler ||||moved to MS 2
Develop post-processing and report generation
Develop end-to-end testing
Publish V1 Repo

SMEs:
|Title|Owner|Status|Priority|Remarks|
|--|--|--|--|--|
Complete External/Scientific Documentation for the Crop and Soil module
Complete Cohort 2 Pilot testing
Develop standard reports recipe (at least one industry-facing and one scientist-facing)
Develop a set of standard scenarios for end-to-end testing


# Resources

[RuFaS Version 1 High Level Functional Requirements](https://docs.google.com/document/d/1fJ3lIOtUJjHKWdaDx2M0c2ZVwCTE-Qy4mK2Vvjt012g/edit?usp=sharing)

[Onboarding Document](https://docs.google.com/document/d/1zN92KK2OkTDkutVmT96u7eEu3B2UDWgP/edit?usp=sharing&ouid=111321898904316595397&rtpof=true&sd=true)

[Uncle Bob Clean Code Lessons](https://youtube.com/playlist?list=PLs4sTjbm8kLhbJy-rT4DILg-kKw3ZCwDx)

[Unit Testing Reference](https://realpython.com/python-testing/)

[Doc String Reference](https://numpydoc.readthedocs.io/en/latest/format.html)

[Doc String Guide](https://realpython.com/documenting-python-code/)

[Pseudocode Guidelines](https://docs.google.com/document/d/1e5gM7fuT06iQYDKvwUAB-jVaLjw3iZizXAdSnOEDco0/edit?usp=sharing)

[2023 Fixathon End tasks](https://docs.google.com/spreadsheets/d/1PcxDMAKYupDahtYiIpTKMMTjL4rbGa5ntiKf5ZuHHvU/edit?usp=sharing)

[2023 Fixathon tasks alive](https://docs.google.com/spreadsheets/d/13_DoP4uFIsXjFKOcJhG25ys3dOL4wPp1rT-0Xu_fUyA/edit?usp=sharing)

[2022 Fixathon tasks](https://docs.google.com/spreadsheets/d/1SnY3c4vBXrD9ybHoswJW28FrkG4DWx4fyvotIXA85BM/edit?usp=sharing)
