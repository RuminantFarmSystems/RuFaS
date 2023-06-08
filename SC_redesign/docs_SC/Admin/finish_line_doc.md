# Crop and Soil Finish Line document

Authors: Ed Hansen  
Date created: 22 May 2023  
Last updated: 22 May 2023  
Reviewers:  

## Contents:
1. [Overview](#overview)
2. [Context](#context)
3. [Requirements](#requirements)
4. [Open Questions](#open-questions)
5. [Details](#detailed-scoping-and-timeline)   
    a. [Timeline](#timeline)  

---

## Overview

This document contains an overview and timeline for the tasks remaining before the Crop and Soil overhaul is complete 
and can be integrated into the rest of RuFaS.

---

## Context

As of the writing of this (22 May) we are about two weeks out from an ideal finish date (Friday, 2 June). Before this
there are a number of functionalities that must be implemented. Due to Clay recently leaving for his new job, I (Ed) 
believe it is important to reestablish a clear plan/path for what needs to happen to make the Crop and Soil module ready
for delivery with the MVP for several reasons:   
    1) To help the people working on the Crop and Soil module full-time to keep a clear picture of what needs to be 
done.   
    2) To help the project manager (Jenn) track progress more accurately.  
    3) To help any developers/engineers/SMEs who have not been working on the Crop and Soil module but who may 
contribute get up to speed on the state of the module quickly.  

---

## Requirements

### Field Requirements
- [ ] Test that all the below processes have been correctly and cohesively integrated into the `Field` module.

#### Water
Biophysical processes that involve the movement of water are often complex and intertwined with Crop and Soil processes,
so there is a need to make sure all these processes are coordinated between Crop and Soil objects.
- [x] Create a method that can be run on a daily basis which handles all water operations at the field level.

#### Growth/Non-water Component Processes
- [x] Create a method that can be run on a daily basis that will run all daily crop growth and soil update operations.

#### Tillage
- [x] Refactor the old `tillage.py`.
  - The old module is relatively short and simple, so it will be refactored to meet the style standards of the new Crop
    and Soil module but will not be more complex or feature-rich than the old module.
- [ ] Integrate the refactored module into `Field`.

#### Fertilizer
Fertilizer application and update routines have already been implemented, but are contained in 
`soil/phosphorus_cycling`.
- [x] Write a fertilizer module at the level of `Field`.
    - This module will, for now, be a wrapper for the existing fertilizer routines in `soil/phosphorus_cycling`, with 
    the understanding that the functionality will eventually be moved to the level of `Field` after delivery of v1 Crop 
    and Soil module.
- [ ] Integrate the fertilizer module into `Field` so that it can be called when fertilizer is applied to the field.

#### Manure
The Manure application and update routines are in same state as their fertilizer counterparts, and the requirements are
nearly identical for both modules.
- [ ] Write a manure module at the level of `Field`.
  - This module will also have functionality moved here from the `soil/phosphorus_cycling` module at some point after 
    the delivery of the v1 Crop and Soil module.
- [ ] Integrate the manure module into `Field`.

#### Scheduling
Certain types of events, (Crop planting/harvesting, soil amendments) need to be scheduled by the user to occur over the
run of the simulation.
- Crop planting and harvesting.
  - [x] Finish implementing and testing Crop planting/harvesting scheduler. - 3 points
  - Integrate crop scheduler and execution of events into `Field` methods.
    - [ ] Implement and test `check_crop_planting_schedule()`, which iterates through list of `PlantingEvent`s, and for 
    all planting events that should happen call `plant_crop()` on them. - 1 point
    - [ ] Implement and test `plant_crop()` to take a crop specification, initialize a `Crop`, and add it to the `crops` 
    attribute of `Field`. - 2 points
    - Implement and test `check_crop_harvesting_schedule()`, which will
      - [ ] Iterate through list of `HarvestEvent`s and execute all operations that it finds on the current day. - 2 points
      - [ ] Iterate through the `crops` attribute to check if any are harvested using optimal (a.k.a. heat scheduled 
      harvesting) and if so, harvest them if they have met the optimal harvesting threshold. - 2 points
    - [ ] Add calls to `check_crop_planting_schedule()` and `check_crop_harvesting_schedule()` in `Field`s daily 
    routine. - 1 point
- Tillage
  - [ ] Implement and test tillage application scheduler. - 3 points
  - [ ] Implement and test `check_tillage_schedule()` which will iterate through a list of `TillageEvent`s and collect 
    and execute all the ones that happen on the current day. - 2 points
  - [ ] Add call to `check_tillage_schedule()` in `Field`s daily routine. - 1 point
- Fertilizer
  - [ ] Implement and test fertilizer application scheduler. - 3 points
  - [ ] Implement and test `check_fertilizer_schedule()` which will iterate through a list of `FertilizerEvent`s and 
  collect and execute all the ones that happen on the current day. - 2 points
  - [ ] Add call to `check_fertilizer_schedule()` in `Field`s daily routine. - 1 point
- Manure
  - [ ] Implement and test manure application scheduler. - 3 points
  - [ ] Implement and test `check_manure_schedule()` which will iterate through a list of `ManureEvent`s and collect and 
  execute all the ones that happen on the current day. - 2 points
  - [ ] Add call to `check_manure_schedule()` in `Field`s daily routine. - 1 point

### Field Manager
- Implement and test methods to translate user input into configuration dictionary.
  - [ ] Schedules for crop plantings and harvestings. - 3 points
  - [ ] Schedules for manure applications. - 2 points
  - [ ] Schedules for fertilizer applications. - 2 points
  - [ ] Schedules for tillage operations. - 2 points
  - [ ] Soil profile configurations. - 4 points
  - [ ] Custom crop types. - 2 points
- Implement methods that turn configurations dictionaries into object instances that will be used to run the simulation.
  - [ ] Create `Soil` instances. - 3 points
  - [ ] Create `FieldData` instances. - 2 point
  - Load lists of `Event` objects into `Field` instances.
    - [ ] Crop `PlantingEvent`s and `HarvestEvent`s. - 2 points
    - [ ] `TillageEvent`s. - 2 points
    - [ ] `FertilizerEvent`s. - 2 points
    - [ ] `ManureEvent`s. - 2 points
- Implement and test methods that mirror the public facing methods of the old `Field` module.
  - [ ] Daily update routine - 1 point
  - [ ] Pre-annual routine - 1 point
- Integrate `FieldManager` into `SimulationEngine` and `State`.
  - [ ] Replace calls to old daily fields routine with calls to new one in `SimulationEngine`. - 1 point
  - [ ] Replace calls to old annual fields routine with calls to new one in `SimulationEngine`. - 1 point
  - [ ] Replace initialization of `Fields` with initialization of `FieldManager` in `State`. - 3 points

#### OutputGatherer
- Implement an `OutputGatherer` module that will handle all output from the Crop and Soil modules
  - [ ] Implement a method that will collect and pass values to the Output Manager daily. - 2 points
  - [ ] Implement a method that will collect and pass values to the Output Manager annually. - 2 points
- [ ] Integrate the `OutputGatherer` into the `FieldManager` module. - 2 points

#### FieldInputManager
- Note: this `FieldInputManager` is dependent on being able to interface with the `InputManager`, so this task should 
only be started when `InputManager` is ready.
- Implement an `FieldInputManager` module that can initialize `Field` instances with the following information
  - [ ] Schedules for crop rotations, plantings, and harvestings.
  - [ ] Schedules for manure applications.
  - [ ] Schedules for fertilizer applications.
  - [ ] Schedules for tillage operations.
  - [ ] Custom soil profile configurations.
  - [ ] Custom crop types.

---

## Open Questions
- How and when the `FieldManureConnector` module will be integrated into `Field`?
- How and when (and will) the Feed and Field modules be connected?

---

## Detailed Scoping and Timeline

### Timeline
Ideally all tasks in this document will be finished by Friday, 2 June, though this is a very ambitious deadline and 
would almost certainly require a heavy prioritization of velocity at the expense of thoroughness. To meet this deadline,
the below timeline would have to be followed:
- Mon 22 May - Friday 26 May
  - Integrate and test water processes in `Field`.
  - Integrate and test crop growth / soil update processes in `Field`.
  - Implement and test `OutputGatherer`.
  - Refactor, test, and integrate `Tillage` into `Field`.
  - Refactor, test, and integrate `Fertilizer` into `Field`.
  - Refactor, test, and integrate `Manure` into `Field`.
- Mon 29 May - Friday 2 June
  - Implement and integrate scheduling mechanism for Crop planting/harvesting operations, and soil amendment operations.
  - Develop a `FieldManager` module.
  - Integrate `OutputGatherer` into `FieldManager`.
  - Implement and integrate `InputManager` into `FieldManager`.
  - Implement methods in `FieldManager` to make it usable to by the `SimulationEngine`
  - Replace the old Crop and Soil module with the new Crop and Soil module.
