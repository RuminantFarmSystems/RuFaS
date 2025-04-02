[![Flake8](https://img.shields.io/badge/Flake8-passed-brightgreen)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/combined_format_lint_test_mypy.yml)
[![Pytest](https://img.shields.io/badge/Pytest-passed-brightgreen)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/combined_format_lint_test_mypy.yml)
[![Coverage](https://img.shields.io/badge/Coverage-89%25-yellowgreen)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/combined_format_lint_test_mypy.yml)
[![Mypy](https://img.shields.io/badge/Mypy-3315%20errors-red)](https://github.com/RuminantFarmSystems/MASM/actions/workflows/combined_format_lint_test_mypy.yml)

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

# 2025 Road Map
We adjusted our quarterly target schedule to align with the US federal fiscal year. Moooving forward, the quarters will be:
* Q1: October 1 to December 31st
* Q2: January 1 to March 31st
* Q3: April 1 to June 30th
* Q4: July 1 to September 30th

## Q1 Goals (October 1 - December 31)

### Overall Project Goals
* Biophysical module disentanglement
  
### Animal Module
* Complete lactation curve manuscript
* Update and cosolidate scientific documentation
* Implementation of genetics informed culling
* New herd initialization method to support footprinting
* Amino Acid Supply
* Finish refresh
  
### Manure Module
* Update manure temperature representation to include temperature limits
* Complete refresh design
  
### Soil and Crop Module
* Debug/improve accuracy of N2O emissions
* Complete first draft of documentation
  
### Feed Storage Module
* Implement dummy connection with animal module
* Implement dummy purchased feed logic
* Review and update Feed Module user inputs

### Energy, Economics, and Emissions (EEE) Module
* Design economics model
* Bring field energy use methods up to date
  
## Q2 Goals (January 1 to March 31)

### Overall Project Goals

* Scientific documentation - completion, review, and addition to GitHub
* Data collection app update
* Finish software orientation series (7 weeks)
* Website update

### Animal Module
* Complete SA and manuscript
* Complete Pilot testing manuscript
* Complete Sys engineering manuscript
* Amino Acid supplementation and impact on production
* Update ration formulation
* Implmement functional connection with feed inventory
  
### Manure Module
* Complete Scientific Documentation
* Improve representation of manure surface area and volume
* Representation of manure imports and exports
* Implement manure module refresh
  
### Soil and Crop Module

* Evaluation of model outputs with experimental datasets
* Pilot testing reports
* External review of first draft of documentation
* Review alignment of documentation with code
* Improve field management input methods
* Complete plan for refresh 

### Feed Storage Module
* Model evaluation
* Represent feed shrink
* Connect Feed module with updated Animal Module/Ration Formulation
* Consistent representation of crops → feeds
  
### Energy, Economics, and Emissions (EEE) Module
* Develop methodology for economics module
* Test/evaluate economics module
* Test field energy use methods
* Design and Implement animal energy use methods
* Develop methodology, design and implement feed storage energy use methods

## Q3 Goals (April 1 to June 30)
### Overall Project Goals
* Publish RuFaS Repository
  
### Animal Module
* Animal Health Submodule Design
  
### Manure Module
* Write and submit peer reviewed publication
* Represent water evaporation in liquid storage
* Sensitivity Analysis

### Soil and Crop Module
* Publication of initial model and evaluation
* Improve representation of irrigation
* Add methane emissions from soil
* Enable Complex combinations of harvesting
* Implement refresh - timeline TBD dependent on planning progress
* Consistent representation of crops → feeds
  
### Feed Storage Module
* Representation of multiple storage units for the same feed
  
### Energy, Economics, and Emissions (EEE) Module
* Design and implement manure energy use methods
  
## Q4 Goals (July 1 to September 30)
### Overall Project Goals
* Prepare for Annual Meeting
* Finish any tasks that were not finished in Q1-Q3

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

[Old Change Logs](https://docs.google.com/spreadsheets/d/1U-3igxdstHTFb6k5dVcE5-x9IL0r6q18eUiwwytKZyA/edit?usp=sharing).
