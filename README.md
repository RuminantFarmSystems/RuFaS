[![Testing](https://github.com/RuminantFarmSystems/MASM/actions/workflows/testing_pytest.yml/badge.svg)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/testing_pytest.yml)
[![Linting](https://github.com/RuminantFarmSystems/MASM/actions/workflows/lint_flake8.yml/badge.svg)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/lint_flake8.yml)
[![Coverage](https://img.shields.io/badge/coverage-93%25-green)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/coverage_pytest-cov.yml)
[![Test and Coverage](https://github.com/RuminantFarmSystems/MASM/actions/workflows/coverage_pytest-cov.yml/badge.svg)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/coverage_pytest-cov.yml)

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

# Definitions for Priority Levels
- **P0 (Priority 0):** These are the 🔥 "fire-breathing dragon" tasks! They are critical and need immediate attention. Team members should don their hero capes 🦸‍♂️🦸‍♀️ and charge into action on P0 tasks. However, if someone finds themselves in a knightly standstill while battling these dragons 🐉, they can embark on a noble quest to tackle lower-priority tasks while working to rescue the damsel in distress (unblocking the higher priority task).

- **P1 (Priority 1):** Think of these as the trusty steed tasks 🐎. They're important and require attention once the dragons (P0) are vanquished. Knights of the project realm should prioritize P0 tasks but, if they encounter a moat or a drawbridge on their way, they can hop on their trusty steed 🏇 and joust with P1 tasks, all while working on strategies to lower the drawbridge (resolve blockers).

- **P2 (Priority 2):** These are the friendly village tasks 🏘️. They're less urgent but still vital to the kingdom. Team members can take a leisurely stroll through the village (work on P2 tasks) when the dragons and drawbridges are at bay. If they happen upon a blocked path, they can enjoy a cup of tea with the villagers ☕ (work on P2 tasks), all while devising clever plans to remove any obstacles in their way.

Remember, in the grand adventure of project work, flexibility and creativity are your allies! 🚀

# 2023 Dev team sprint and on-call schedule
| Start Date | End Date   | Sprint | On-Call |
|------------|------------|--------|---------|
| 11/8/2023  | 11/14/2023 | 1      | Niko       |
| 11/15/2023 | 11/21/2023 | 1      | Allister       |
| 11/22/2023 | 11/28/2023 | 2      | Ed       |
| 11/29/2023 | 12/5/2023  | 2      | Loi       |
| 12/6/2023  | 12/12/2023 | 3      | Pooya       |
| 12/13/2023 | 12/19/2023 | 3      | Niko       |
| 12/20/2023 | 12/26/2023 | 4      | Allister       |
| 12/27/2023 | 1/2/2024   | 4      | Ed       |

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
Design and implement EEE (Review progress on this)|Pooya, Roohi, Kristan, Jenn||P1
Finish Compost for Manure Module |Varma, Loi||P0
Redesign and implement Feed storage module |Kevin, Pooya, Kristan|||Moved to MS 2.5
Revisit the Animal Module design – Refactoring -- Animal Manager||Design Phase|P2| Moved to MS 2.5
Revisit the Animal Module design – Refactoring -- Animal Ration formulation|Joe|In Review|P0
Revisit the Animal Module design – Refactoring -- Animal Life Cycle|Yijing, Simon, Anchey|Design phase|P0
Deprecate the output handler, add missing functionalities, and reports to OM|Niko, Allister||P0
Go through the entire codebase and ensure IM is the only way we are receiving input data|Allister, Niko||P0|[IM Integration tracking](https://docs.google.com/spreadsheets/d/1k8J6MelPrsrz6Tv4fQNAG-kLSN7oQTQOCEy3I6F0IqU/edit?usp=sharing)
Revert soil profile properties and rewrite soil profile inputs|Ed|Completed|P1|[#773](https://github.com/RuminantFarmSystems/MASM/issues/773)

SMEs:
|Title|Owner|Status|Priority|Remarks|
|--|--|--|--|--|
Complete model evaluation||||Moved to Milestone 3
Complete Sensitivity Analysis||||Moved to Milestone 3
Complete External/Scientific Documentation for Animal, Manure, & EEE modules and put on GitHub|Varma, Joe, Haowen, Kristan, Jenn, Emmanuel||P1
Complete Cohort 1 Pilot testing|Kristan, Haowen, Kat||P0
Complete evaluation of soil temperature|Ed, Jenn, Matthew|Completed|P0|[#764](https://github.com/RuminantFarmSystems/MASM/issues/764)

## Milestone 2.5: Oct 31th
[GitHub Milestone](https://github.com/RuminantFarmSystems/MASM/milestone/5)

Dev Team:
|Title|Owner|Status|Priority|Remarks|
|--|--|--|--|--|
Redesign and implement the Feed storage module|Pooya, Kevin, Kristan||P1
Refactor Animal Module -- Animal Manager|Joe||P0
Rewrite and clean field input files in the `input/` directory|Ed, Matthew|Completed|P1|[#769](https://github.com/RuminantFarmSystems/MASM/issues/769) 

SMEs:
|Title|Owner|Status|Priority|Remarks|
|--|--|--|--|--|
Complete Cohort 1 Pilot testing|Kristan, Haowen, Kat||P0
Complete evaluation of soil hydrology|Ed, Jenn, Matthew|Completed|P0|[#766](https://github.com/RuminantFarmSystems/MASM/issues/766)

## Milestone 3: Dec 31th
[GitHub Milestone](https://github.com/RuminantFarmSystems/MASM/milestone/6)

Dev Team:
|Title|Owner|Status|Priority|Remarks|
|--|--|--|--|--|
Refactor manure excretion and methane emission in the animal module|Dev team, Joe, Haowen||P2
Revisit classes.py|Allister
Deprecate DB(s)|Allister
Deprecate output handler ||moved to MS 2||
Develop post-processing and report generation|||P1
Develop end-to-end testing|||P1
Publish V1 Repo|||P2

SMEs:
|Title|Owner|Status|Priority|Remarks|
|--|--|--|--|--|
Complete External/Scientific Documentation for the Crop and Soil module|||P0
Complete model evaluation using existing experimental data|||P2
Complete Sensitivity Analysis of Animal Module|||P1
Complete Sensitivity Analysis of Crop and Soil Module|||P1|Should be moved to milestone after this.
Complete full evaluation of Crop and Soil Module|Ed, Jenn, Matthew||P0|[#762](https://github.com/RuminantFarmSystems/MASM/issues/762)
Initiate Sensitivity Analysis of Manure Module|||P1
Complete Cohort 2 Pilot testing|||P0
Develop standard reports recipe (at least one industry-facing and one scientist-facing)|||P1
Develop a set of standard scenarios for end-to-end testing|||P1


# Resources

[RuFaS Version 1 High Level Functional Requirements](https://docs.google.com/document/d/1fJ3lIOtUJjHKWdaDx2M0c2ZVwCTE-Qy4mK2Vvjt012g/edit?usp=sharing)

[Onboarding Wiki](https://github.com/RuminantFarmSystems/MASM/wiki/Onboarding-New-Team-Members)

[Uncle Bob Clean Code Lessons](https://youtube.com/playlist?list=PLs4sTjbm8kLhbJy-rT4DILg-kKw3ZCwDx)

[Unit Testing Reference](https://realpython.com/python-testing/)

[Doc String Reference](https://numpydoc.readthedocs.io/en/latest/format.html)

[Doc String Guide](https://realpython.com/documenting-python-code/)

[Pseudocode Guidelines](https://docs.google.com/document/d/1e5gM7fuT06iQYDKvwUAB-jVaLjw3iZizXAdSnOEDco0/edit?usp=sharing)

[2023 Fixathon End tasks](https://docs.google.com/spreadsheets/d/1PcxDMAKYupDahtYiIpTKMMTjL4rbGa5ntiKf5ZuHHvU/edit?usp=sharing)

[2023 Fixathon tasks alive](https://docs.google.com/spreadsheets/d/13_DoP4uFIsXjFKOcJhG25ys3dOL4wPp1rT-0Xu_fUyA/edit?usp=sharing)

[2022 Fixathon tasks](https://docs.google.com/spreadsheets/d/1SnY3c4vBXrD9ybHoswJW28FrkG4DWx4fyvotIXA85BM/edit?usp=sharing)
