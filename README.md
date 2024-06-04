[![Flake8](https://img.shields.io/badge/Flake8-passed-brightgreen)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/combined_format_lint_test_mypy.yml)
[![Pytest](https://img.shields.io/badge/Pytest-failed-red)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/combined_format_lint_test_mypy.yml)
[![Coverage](https://img.shields.io/badge/Coverage-%25-red)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/combined_format_lint_test_mypy.yml)
[![Mypy](https://img.shields.io/badge/Mypy-3600%20errors-red)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/combined_format_lint_test_mypy.yml)


# Vision
To support research and sustainable decision-making in ruminant animal production through a state-of-the-art, open-source modeling environment that is continuously adapting as technology and scientific knowledge advance.

# Mission
To build an integrated, whole-farm model that simulates milk, meat, and crop production, greenhouse gas emissions, water quality impacts, soil health, and other sustainability outcomes of ruminant farms. We strive to achieve the highest standards for prediction accuracy, code structure and clarity, documentation, and accessibility. Through continuous learning and improvement of our methods and algorithms, we are creating an open and inclusive platform for scientific collaboration. 

# Priorities
When decision-making is difficult and doubtful, we use these as our North Star to navigate the uncertain and unknown world.
## Current
* Deliver Minimum Viable Product (MVP)
* Payoff the tech debt
* Establish a positive and inclusive team culture.

## Past
N/A

# Changelog
Find the changelog Google Sheet [here](https://docs.google.com/spreadsheets/d/1U-3igxdstHTFb6k5dVcE5-x9IL0r6q18eUiwwytKZyA/edit?usp=sharing).

# Priority Definitions for Project Tasks

## Individual Task Priorities

1. **Wish:** These are the 🌟 "star-gazing" tasks. They are desirable but not essential. Team members can engage in these tasks as a creative respite or when other higher-priority tasks are not pressing. Imagine these tasks like enjoying a calm night under the stars, dreaming about possibilities.

2. **Low:** Consider these tasks as the 🍃 "gentle breeze" in the project. They are tasks that need to be done but are not pressing. They can be approached in a relaxed manner, akin to enjoying a leisurely walk in a serene garden.

3. **Medium:** These tasks are the 🛤️ "steady path" of the project. They are important and should be completed in due course. Team members should keep a steady pace on these tasks, ensuring progress is consistent. If not done in a timely manner, these tasks will be escalated to "High."

4. **High:** Think of these tasks as the ⚓ "anchor" of the project. They are very important and should not be delayed. Team members should give these tasks focused attention, understanding their significant impact on the project.

5. **Urgent:** These are the 🚨 "flashing sirens" of the project. They demand immediate attention and swift action. Just like responding to an emergency, these tasks should be addressed with utmost urgency.

## Relative Task Priorities (For Milestones and Larger Work Chunks)

1. **P0 (Priority 0):** The 🔥 "fire-breathing dragon" tasks! Critical and needing immediate attention. Don your hero capes 🦸‍♂️🦸‍♀️ and charge into action. If you're in a knightly standstill, it's noble to embark on a quest to tackle lower-priority tasks while rescuing the damsel in distress (unblocking the higher-priority task).

2. **P1 (Priority 1):** The trusty steed tasks 🐎. Important to address once the dragons (P0) are vanquished. Prioritize P0, but if you encounter a moat or a drawbridge, hop on your steed 🏇 and joust with P1 tasks, strategizing to lower the drawbridge (resolve blockers).

3. **P2 (Priority 2):** The friendly village tasks 🏘️. Less urgent but vital. Take a leisurely stroll (work on P2 tasks) when dragons and drawbridges are at bay. Enjoy a cup of tea with the villagers ☕ (work on P2 tasks), while devising plans to remove obstacles.

Remember, flexibility and creativity are your allies in the grand adventure of project work! 🚀 Each task, whether a solo journey or part of a larger quest, plays a vital role in the epic saga of our project. Approach each with the dedication and spirit they deserve, and together, we will triumph!

# 2024 Road Map
## Q1 Goals
### SWE Goals
* Finish Feed Storage Module (P1)
  - Fix the issues in the Feed library _Issues_ [1245](https://github.com/RuminantFarmSystems/MASM/issues/1245)
  - Feed Degradation _Issues_ [1375](https://github.com/RuminantFarmSystems/MASM/issues/1375) [1376](https://github.com/RuminantFarmSystems/MASM/issues/1376) [1377](https://github.com/RuminantFarmSystems/MASM/issues/1377) [1378](https://github.com/RuminantFarmSystems/MASM/issues/1378) 
  - Purchase Feed logic
* Finish Energy and Emission from EEE Module for FARM ES (Purchased feed emissions and field management fuel) (P0)
* Implement Scenario Manager (P0)
* Implement end to end testing (P1)
* Analyze Animal Module and Plan on action items (P0) _Issues_ [1229](https://github.com/RuminantFarmSystems/MASM/issues/1229) [1232](https://github.com/RuminantFarmSystems/MASM/issues/1232) [1235](https://github.com/RuminantFarmSystems/MASM/issues/1235) 
* Analyze S&C Module and Plan action items (P0) _Issues_ [1230](https://github.com/RuminantFarmSystems/MASM/issues/1230) [1233](https://github.com/RuminantFarmSystems/MASM/issues/1233) [1236](https://github.com/RuminantFarmSystems/MASM/issues/1236)
* Analyze Manure Module and Plan action items (P0) _Issues_ [1231](https://github.com/RuminantFarmSystems/MASM/issues/1231) [1234](https://github.com/RuminantFarmSystems/MASM/issues/1234) [1237](https://github.com/RuminantFarmSystems/MASM/issues/1237)
* Un-entangle bio physical modules [document here](https://docs.google.com/document/d/17BVgTnsqwVEZbdNoztIfBQILYJ94inlyXgwCvq9iQQw/edit?usp=sharing)  _Issues_ [1411](https://github.com/RuminantFarmSystems/MASM/issues/1411)
* Implement IM cross validation (P1)
* Draft Developer’s Rights and Responsibilities (P2)
* Fix units across the codebase (P1) _Issues_ [1253](https://github.com/RuminantFarmSystems/MASM/issues/1253) [1254](https://github.com/RuminantFarmSystems/MASM/issues/1254) 
* Revisit website backend (P2)
### SME Goals
* Pilot testing reports (P0)
* Comparison/benchmarking with other estimates of GHG emissions (P0)
* Develop a set of standard scenarios for end-to-end testing (P0)
* SA of Animal & C&S module (P1)
* Evaluation of Manure Module (P1)
* SA of Manure Module (P1)
* SA of Feed module (P2)
* Energy methodology publication (P2)
* Website (P1)
* Complete feed module documentation (P1)
* Develop design doc for automated lactation curve parameter selection implementation in RuFaS (P2)
* Refine use of equipment (P2)
  
## Q2 Goals
### SWE Goals
* Finish Economics from EEE Module
* Finish Energy and Emission from EEE Module (Electricity and Manure Management Fuel)
* Take actions on the action items from Q1 Animal Module
* Take actions on the action items from Q1 S&C Module
* Take actions on the action items from Q1 Manure Module
* Revisit Time class
* Un-entangle bio physical modules- (implementation)
* Finalize Developer’s Rights and Responsibilities

### SME Goals
* Publish SA and evaluation of Animal Module
* Publish SA and evaluation of Crop and Soil Module
* Evaluate Manure Module and publish introduction manuscript
* Animal Health Design Doc development
* Grazing Design doc development
* Document Stakeholder Requirements

# Resources

[RuFaS Version 1 High Level Functional Requirements](https://docs.google.com/document/d/1fJ3lIOtUJjHKWdaDx2M0c2ZVwCTE-Qy4mK2Vvjt012g/edit?usp=sharing)

[Onboarding Wiki](https://github.com/RuminantFarmSystems/MASM/wiki/Onboarding-New-Team-Members)

[Uncle Bob Clean Code Lessons](https://youtube.com/playlist?list=PLs4sTjbm8kLhbJy-rT4DILg-kKw3ZCwDx)

[Unit Testing Reference](https://realpython.com/python-testing/)

[Doc String Reference](https://numpydoc.readthedocs.io/en/latest/format.html)

[Doc String Guide](https://realpython.com/documenting-python-code/)

[Pseudocode Guidelines](https://docs.google.com/document/d/1e5gM7fuT06iQYDKvwUAB-jVaLjw3iZizXAdSnOEDco0/edit?usp=sharing)

[2024 Fixathon tasks alive](https://docs.google.com/spreadsheets/d/1rtbnWAw9wA1GoD7VHE0VNrXzasaj2-2dquInr0ZjAeY/edit?usp=sharing)

[2023 Fixathon End tasks](https://docs.google.com/spreadsheets/d/1PcxDMAKYupDahtYiIpTKMMTjL4rbGa5ntiKf5ZuHHvU/edit?usp=sharing)

[2022 Fixathon End tasks](https://docs.google.com/spreadsheets/d/1SnY3c4vBXrD9ybHoswJW28FrkG4DWx4fyvotIXA85BM/edit?usp=sharing)
