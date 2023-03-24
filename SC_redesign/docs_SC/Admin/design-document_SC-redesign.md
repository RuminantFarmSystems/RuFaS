# Design Document: Soil and Crop Module Redesign

Authors: Clay J. Morrow
Date created: 22 Mar 2023
Last updated: 22 Mar 2023
Reviewers: [TBD]

## Contents:
1. [Overview](#overview)
2. [Context](#context)
3. [Requirements](#requirements)
   a. [Fields](#fields)  
   b. [Crop Species](#crop-species)  
   c. [Crop Rotation](#crop-rotation)  
   d. [Coover Cropping](#cover-cropping)  
   e. [Soil Amendments](#soil-amendments)  
   f. [Tillage Practices](#tillage-practices)  
   g. [Outputs](#outputs)  
   h. [Beyond v1](#beyond-v1)  
4. [Progress](#progress)
   a. [Milestones](#milestones)  
   b. [GitHub Project](#sc-redesign-github-project)  
   c. [Timeline](#timeline)  
5. [Existing Solution](#existing-solution)
6. [Proposed Solution](#proposed-solution-design-details)
7. [Alternative Solutions](#alternative-solutions)
8. [Testability, etc.](#testability-monitoring-and-alerting)
9. [Cross-Team Impact](#cross-team-impact)
10. [Open Questions](#open-questions)
11. [Details](#detailed-scoping-and-timeline)

---

## Overview

This document will outline the new design for the Soil and Crop submodule of the RuFaS model. It will largely focus
on *redesigning* this module, since the original design had major problems. Here, I will outline the desired structure
of the module and its components, the requirements of the module, the steps taken to achieve those requirement goals 
along with estimated timelines, and the implications for RuFaS. 

Note: that details present in this document are revised version of the files 
[road-map_soil-and-crop.md](road-map_soil-and-crop.md) and 
[functionality-requirements.md](functionality-requirements.md).

---

## Context

As of the conception of this redesign (October 2022) and this writing (March 2023), the Soil and Crop module (SC), 
located primarily in `RUFAS/routines/field/`, is in a state of disarray and bugs are near-impossible to track down. 
Below is a list of the general problems that this redesign aims to address:

* The model returns entirely inaccurate results. For example, Crop yields are much lower than expected and are
inconsistent across years. 

* The components and sub-modules are not independent or isolated. For example Performing tests requires running the
**entire** model and looking through all the output.

* Formal unit tests are not implemented for any of the code, so every component's integrity is suspect.

* Format and structure is not consistent throughout the module

* Documentation, both for the module components and the overall model, is severely lacking and sometimes conflicts
with what the code does in actuality.

* Names of module entities are poorly selected and not intuitive.

For these reasons, RuFaS leadership (Kristan, Pooya, Joe, and I) decided that the est course of action was to rebuild
SC, essentially from the ground up, following improved standards and guidelines for a stable and reliable module.

---

## Requirements

Kristan laid out a series of requirements of the Soil and Crop module for version 1 (v1) and beyond. In general, this
document will focus on v1 requirements, but in planning for future features will also prevent difficult re-writes later
on, so we also describe known requirements for the future as well.

I've broken the requirements into sections based on the hierarchical organization structure present in the model's 
simulated farm systems (and in real systems). These requirements are formatted as checklists so that they can be 
ticked when as requirements are met.

### Fields

Farms should consist of collections of fields and their respective traits:

* [ ] each field has dimensions (i.e., the growing area) and geographic location (lat, long at midpoint)
* [x] each field has soil specifications (or general soil attributes for all fields in an area)
* [ ] multiple fields should grow crops simultaneously
* [x] fields/nutrient pools should be independent of each other (e.g., field $A$ grows crop $X$ with method $M$ 
while field $B$ grows crop $Y$ with method $L$, etc.)

### Crop Species

The module should be able to handle different crop types (species) interchangeably and execute routines based upon 
their attributes. At minimum, the following crops should be handled:

* [x] corn
* [x] alfalfa
* [x] grass - (tall fescue)
* [x] soybeans
* [x] winter wheat
* [x] winter rye
* [ ] triticale
 
All crops need to:

* [x] have species-specific default traits (attributes)
* [ ] be planted on specified days and/or according to a schedule
* [ ] be harvested on specified dates, according to a schedule, or according to a growth metric (i.e., "optimal" 
harvest)
* [ ] grow on a daily basis. During this process:
  - [ ] crop growth depends upon temperature, light, water, and nutrients
  - [ ] crops remove/exchange resources from soil
  - [ ] crops accumulate biomass
* [ ] remain unharvested, if specified
* [ ] leave biomass on field after cut, if specified (cover crop)
* [ ] fix nitrogen, if applicable

### Crop Rotation

Fields should be able to experience rotation schedules, if specified such that the following cases are handled:

* [ ] regular cycles/patterns repeated **across** years (e.g., crop $A$ in first year followed by 3 years of crop $B$)
* [ ] regular cycles/patterns repeated **within** years (e.g., cash crop in summer followed by cover crop in 
fall/winter)

### Cover Cropping

The model should also allow cover cropping, in which cover crop species are:

* [ ] planted on a specified date, typically after harvest of a cash crop
* [ ] grown daily, as in the [Crop Species](#crop-species) section. 
* [ ] optionally cut and left in the field to affect other processes such as:
  - [ ] slow/reduce runoff/erosion
  - [ ] increase/improve water infiltration 
  - [ ] return nutrients to soil (as residue)
  - [ ] improve nutrient retention of soil (trap crop)
  - [ ] reduce/mitigate soil compaction

### Soil Amendments

Nutrient additions to the soil should be handled:

* [x] no nutrient addition
* [x] manure application
* [x] commercial fertilizer application
* [x] both manure and fertilizer application

### Tillage Practices

The following soil tillage practice options should be implemented:

* [x] No-till (no soil tillage) should:
* [x] Standard Tillage (with rates specified; e.g., depth, percentages, etc.)
* [ ] Conservation Tillage

All methods should appropriately account for and/or alter:

* [ ] soil erosion
* [ ] water infiltration
* [ ] nutrient and water cycling/composition
* [ ] leeching
* [ ] soil compaction
* [ ] mixing (e.g., mixing fertilizer/manure into soil profile)

### Outputs

The model should return at least the following outputs **for each year**:

* [ ] emissions (i.e., $N_{2}O$, $NH_3$, $CO_2$)
* [ ] nutrient leaching and runoff (i.e., $N$ and $P$)
* [ ] water use
* [ ] energy usage (i.e., fossil fuels)
* [ ] soil nutrients ($C$, $N$, $P$)
* [ ] crop yields (mass)
* [ ] crop yields (mass)
* [ ] crop composition ($C$, $N$, $P$, $H_{2}O$, etc.)

### Integration

In addition to all these features, SC needs to be properly intergrated both amongst its own sub-modules and with other
RuFaS Modules:
* [ ] Field, Crop, and Soil, processes are connected and integrated (via the field manager). 
* [ ] SC takes, as input, results from the manure module. The manure generated by livestock is used to grow crops
* [ ] SC passes its output as input to the feed storage module
* [ ] SC needs to interact with the animal module once grazing is implemented (post v1)

### Beyond v1

#### Multi-Cropping

The model needs to be able to grow multiple crops at the same time in a single field. Multi-cropping should include:

* [ ] any number of crops grown together
* [ ] all crops drawing from (and limited by) the same resource pools
* [ ] nitrogen fixers and non-fixers grown together
* [ ] daily accumulation of biomass for each species
* [ ] overall biomass yield, in addition to species yields, after harvest

#### Customizable Species

With respect to crop species, users should be able to:

* [x] configure existing species, with alternative attribute values
* [x] create a custom species (e.g., beetroot) by defining all necessary attributes

#### Soil Amendment Options

Manure Application:

* [ ] differentiate between broadcasting (spread onto surface) and injection (knife, sweep, or disk variants)
* [x] nutrient composition of the manure should have sensible defaults **and also** be customizable

---

## Progress

### Milestones

**Other Note:** Re-review this section and update it according to Pooya's example

Below are measurable components that the module should have, which will be tracked as development
continues. 

* All the main process files (`.py`) need to be reformatted and reorganized to the new design, 
cross-checked with source documentation, tested, and documented (updated pseudocode). 
The original versions should remain in-tact and new versions placed in `SC_redesign/Crop_and_Soil/` until the redesign
is complete. In total, there are:
  - [x] 10 crop files, 2671 lines (`RUFAS/routines/field/crop/`): Done (Feb 2023)
  - [ ] 23 soil files, 2213 lines (`RUFAS/routines/field/soil/`): Approx. 52% finished (Mar 2023), expected April 2023 
  - [ ] 4 field management files, 295 lines (`RUFAS/routines/field/field_management`): 

* The main classes need to be rewritten with new formatting guidelines, and linked to the process classes.
  - [ ] `Soil`: mostly finished, dependent upon refactored soil files above: expected April 2023
  - [x] `Crop`: functionally finished (Mar 2023), minor tweaks likely as other files updated
  - [ ] `Field`: design finished, needs implementation (expected late April/early May 2023)

* [ ] The current `Crop.py` file (`RUFAS/routines/field/crop/`) needs to be re-written and organized 
into the new `FieldManager` class: expected May 2023 

* the new data manager and `SCInput` classes need to be created and utilized: expected May 2023

Here are a general list of things that the module code needs to do:

* [x] `Crop` should be able to initialize with different species-specific attributes and from input data: Feb 2023
* [x] `Crop` component methods should reflect daily crop processes (e.g., SWAT): Feb 2023
* [x] `Soil` should be able to initialize with soil profile attributes from input data: Mar 2023
* [ ] `Soil` component methods should reflect daily soil processes (e.g., SWAT): in progress, expected April 2023
* [x] `Field` should be able to initialize with different dimensions and geography, from input data: Feb 2023
  - should be able to initialize `Crop`(s) and `Soil`, passing them the data they need
  - needs to have one `Soil` and 0-n `Crop`
* [ ] `Field` methods should reflect field management processes (apply manure/fertilizer, plant/harvest crops, 
expected May 2023
  - methods should manage crops one by one 
  - and will often be wrappers that call `Soil` and `Crop` methods
* [ ] `FieldManager` should be able initialized based on input data: expected May 2023
  - should be able to initialize a number of `Fields`, passing them data they need
* [ ] `FieldManager` methods should reflect management of the system: expected May 2023
  - should track which `Field`/`Soil` processes need to run and execute them accordingly, such as: 
    + `Crop` planting/multi-cropping
    + following cropping patterns
    + `Crop` growing season/dormancy
    + `Crop` cutting/harvesting/killing/cover-cropping
    + fertilizer/manure addition to `Soil`
    + `Soil` tillage
  - should manage fields one by one
  - should pass relevant weather and time data to `Field`
  - should accept input from `SCInput` and pass output to output manager

### SC Redesign GitHub Project

In support of the milestones present in this document, the 
[Soil and Crop Redesign](https://github.com/orgs/RuminantFarmSystems/projects/1/views/2) GitHub Project contains all 
the itemized tasks for this particular project. These tasks are tracked and updated every time our developers work on
these tasks. While we will periodically update this file, the GitHub project is the best way to follow the progress
of this module. In particular, 
[this graphic](https://github.com/orgs/RuminantFarmSystems/projects/1/insights/2) shows the absolute and proportional 
subdivision of tasks between "Todo", "In Progres", and "Done". As seen from this figure, the number of tasks associated
with the project has been increasing (as we find new problems/issues) but the rate at which we complete tasks has grown
at a much greater rate.

### Timeline

This redesign project is somewhat unpredictable in terms of time. Because we are not the original authors of the code,
we do not fully understand its intricacies and nuances. This means that as we take on new files to refactor and learn
more about the design of the old code, we gain greater insight into what needs to be done and how. New tasks are
created as we learn more and even the code that we've already re-worked my need to be further tweaked once new
information from elsewhere in the model comes to light. With all that said, acknowledging that this is an iterative
process, I will attempt to give an estimate of when the project will be completed. These estimates are based on a few
important factors. 1) experience: based on how long it has taken us to get to where we currently are, we might expect that a similar level
of efficiency will continue for the remaining tasks (per person, per task); 2) resources: as of this writing, I (Clay)
am preparing to leave my position for a new job. That leaves 2 developers on the Crop and Soil team. Ed is working full
time and Matthew is working part-time between classes. 

Here are my estimates:
* Best case scenario: If everything goes right, the project might be finished in **early May**
* Most likely scenario: A more realistic estimate is **mid-late May**
* Worst case scenario: If things take longer than expected, I believe the project could be done **sometime in June**.

---

## Existing Solution

The existing Crop and Soil module exists in 
[RUFAS/routines/field/](https://github.com/RuminantFarmSystems/MASM/tree/SC_redesign/RUFAS/routines/field) but, as
discussed in the [Context](#context) section, this version of the model is poorly implemented.

---

## Proposed Solution (design details)

---

## Alternative Solutions

---

## Testability, Monitoring, and Alerting

---

## Cross-Team Impact

---

## Open Questions

---

## Detailed Scoping and Timeline