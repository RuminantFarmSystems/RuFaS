# RuFaS Input Redesign
Authors: Clay J. Morrow
Created: 11, April 2023
Last Edited: 11, April 2023
Reviewed by: [TBA]
Status: Draft

## Contents
1. [Overview](#overview)
2. [Context](#context)  
3. [Requirements](#requirements)
4. [Milestones](#milestones)
5. [Existing Solutions](#existing-solution)
6. [Proposed Solution](#proposed-solution)
7. [Alternative Solutions](#alternative-solutions)
8. [Testability, Monitoring and Alerting](#testability-monitoring-and-alerting)
9. [Cross-Team Impact](#cross-team-impact)
10. [Open Questions](#open-questions)
11. [Detailed Scoping and Timeline](#detailed-scoping-and-timeline)

---

## Overview

The way that RuFaS handles user input, at the time of this document's creation, is not ideal for many applications of 
the model. This document discusses how to update that functionality to allow RuFaS to be more modular and versatile. 

---

## Context

Currently, RuFaS takes its input from a series of json files. This poses a number of challenges for running the model
under different scenarios or starting conditions. To do so, users must either 1) overwrite the input files or 2) 
write multiple input files (RuFaS does handle running multiple input files sequentially). This is further complicated by
the fact that the primary input file contains path references to *other* input files of the various sub-categories of
input, which are handled separately and inconsistently by the submodules. This design is especially problematic when 
trying to run many instances of RuFaS in parallel; creating thousands of input files that differ by only a few values 
value is inefficient and altering a single file on multiple threads is not safe. For further details about the current 
structure, see the [Existing Solution](#existing-solution) section.

Because of these challenges, a redesign and refactor of the input manager is warranted. 

---

## Requirements

RuFaS should handle input such that:
* JSON files containing user-specified input can be used to setup the simulation (current functionality)
* alternative input methods can also be handled (e.g., dictionaries or other user-initialized data objects)
* external methods (e.g., sensitivity analysis, validation, and mathematical optimization) can execute RuFaS by altering
the input values automatically
* parallel or distributed evaluation of multiple RuFaS instances can be done in a thread safe way, with many alternative
starting conditions.
* the actual model and submodules are agnostic to the structure of the input that the user specified.

---

## Milestones

**TBD**

---

## Existing Solution

The main method of the model `run_rufas()` accepts a path to a JSON file or a directory of JSON files, via the 
`input_path` argument. The file path(s) are passed to `execute_simulations_from_files()` (and `SimulationEngine`) 
which runs RuFaS model using input specified in the files. The input files are located in the [input/](../../input) 
directory by default and have two main components: 
* overall configuration data (the "config" field) such as the time periods to be simulated, the random seed, the 
location to which output files should be saved, etc.
* and references to *other* input files to use. 

Take, for example, the following input file `ARL.json`:

```json
{
    "config":
    {
        "start_date" : "1990:1",
        "end_date" : "2019:365",
        "csv_dir": "output/CSVs/",
        "graphic_dir": "output/graphics/",
        "set_seed": false,
        "seed": 0,
        "simulate_animals": false
    },
    "weather": "ARL_weather.csv",
    "output": "field_report.json",
    "farm":
    {
        "fields": {
            "field_1": {
                "soil": "ARL_soil.json",
                "crop": "ARL_rotation.json",
                "field_management": "ARL_no_fert_field_management.json"
            }
        },
        "animal": "barnyard_animal.json",
        "feed": "purchased_feed.json",
        "manure": "manure_management.json"
    }
}
```

The "config" field specifies the configuration information and the remaining fields are paths to other files. The 
"weather" field points to a csv file containing weather data and the others point to additional json files. 
Importantly, these referenced files are required to be in specific sub-directories of [input/](../../input): the 
soil file [ARL_soil.json](../../input/soil/ARL_soil.json) is located at [input/soil/](../../input/soil), and must be 
for the model to work properly. The Soil and Crop module locates and parses this file to get the data it needs, once 
the program enters this module. 

### Set-up Details

The `SimulationEngine` class handles the set-up of the objects needed for the simulation (and submodules) through the
`_initialize_simulation()` method:
* the main input file is converted to a dictionary called `data`,    
* the `Config` class is initialized with `Config(data['config'], data['weather'])`, which creates the `self.config`
attribute and uses the contained path to the weather file 
(by prepending "~/input/weather" to the string) to parse the file **for dates ranges only**.
* the `Weather` class is initialized with `Weather(data['weather'], self.config)`, which *again* reads the
weather file (using similar code to `Config`).
* the `Time` class is initialized with `Time(self.config)`
* the `State` class is initialized with `State(data['farm'], self.config, self.weather, self.time)`, 
which initializes the required objects for each of the modules (simplified below):
    - Crop and Soil: `Fields(data['fields'], time)`
    - Feed: `Feed(feed_path)` - where `feed_path` is an expanded path to the `data['feed']` json file
    - Animal: `AnimalManagement(animal_config, config, self.feed, weather, time)` - where `animal_config` is a modified
      version of the dictionary created from the `data['animal']` json file, with the addition of a sub-dictionary 
      created from the 'data['manure']` json file
    - Manure: `ManureStorage(self.animal_management)` and `ManureManagement` - where `self.animal_management` is the 
      instance of `AnimalManagement` referenced previously and `manure_management_config` is the dictionary created from
      `data['manure']`

## Proposed Solution

## Alternative Solutions

## Testability, Monitoring and Alerting

## Cross-Team Impact

## Open Questions

## Detailed Scoping and Timeline
