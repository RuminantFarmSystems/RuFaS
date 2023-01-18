---
title: Crop and Soil Functionality Requirements
author: Clay Morrow
date: 10 Oct, 2022
output: 
  html_document
---

# Crop and Soil Requirements

This document outlines expected functionality of the RuFaS Soil and Crop Module.

## Version 1.0.0 (Jan 2023)

### Fields

Farms should consist of collections of fields and their respective traits:

* [ ] each field has dimensions (i.e., the growing area) and geographic location (lat, long at midpoint)
* [ ] each field has soil specifications (or general soil attributes for all fields in an area)
* [ ] multiple fields should grow crops simultaneously
* [ ] fields/nutrient pools should be independent of each other (e.g., field $A$ grows crop $X$ with method $M$ while field 
$B$ grows crop $Y$ with method $L$, etc.)

### Crop Species

The module should be able to handle different crop types (species) interchangeably and execute routines based upon their
attributes. At minimum, the following crops should be handled:

* [ ] corn
* [ ] alfalfa
* [ ] grass - (tall fescue)
* [ ] soybeans
* [ ] winter wheat
* [ ] winter rye
* [ ] triticale
 
All crops need to:

* [ ] have species-specific default traits (attributes)
* [ ] be planted on specified days and/or according to a schedule
* [ ] be harvested on specified dates, according to a schedule, or according to a growth metric (i.e., "optimal" 
harvest)
* [ ] grow on a daily basis, including
  - [ ] depend upon temperature, light, water, and nutrients
  - [ ] remove/exchange resources from soil
  - [ ] accumulate biomass
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

* [ ] no nutrient addition
* [ ] manure application
* [ ] commercial fertilizer application
* [ ] both manure and fertilizer application

### Tillage Practices

The following soil tillage practice options should be implemented:

* [ ] No-till (no soil tillage) should:
* [ ] Standard Tillage (with rates specified; e.g., depth, percentages, etc.)
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

## Version 1.x.y (after v.1.0.0)

### Multi-Cropping

The model needs to be able to grow multiple crops at the same time in a single field. Multi-cropping should include:

* [ ] any number of crops grown together
* [ ] all crops drawing from (and limited by) the same resource pools
* [ ] nitrogen fixers and non-fixers grown together
* [ ] daily accumulation of biomass for each species
* [ ] overall biomass yield, in addition to species yields, after harvest

### Customizable Species

With respect to crop species, users should be able to:

* [ ] configure existing species, with alternative attribute values
* [ ] create a custom species (e.g., beetroot) by defining all necessary attributes

### Soil Amendment Options

Manure Application:

* [ ] differentiate between broadcasting (spread onto surface) and injection (knife, sweep, or disk variants)
* [ ] nutrient composition of the manure should have sensible defaults **and also** be customizable


# The Path Forward

Below is a record of the correspondence between Kristan and I that initiated the redesign of the Crop and Soil (SC) 
module.

#### Message From Kristen

Hi Clay and Reid, so I have been thinking about what to do with the sequential cropping pull request given this new 
realization that the functionality is not where we thought it was. I think there is still a path to pull this in, but 
I would like to request some more information about the plans to get to a working crop module. Specifically:

1) If we pull in this large, buggy less than ideal but still an improvement pull request, will the future updates still 
be able to be made in small pull requests?

2) I would like to see some sort of plan for what the refactoring would look like this would include:

   - some assessment of a timeline (maybe the next two months?) and description of the changes that need to be made
   - some assessment of how much of the current pull request will be changed in the near future. There are many files 
   changed (lots of them are jsons and crop config etc. files). Will all of them be overhauled when crop is refactored?
   
The goal of #1 is something like a back-up plan for the worst case scenario where you both are kidnapped by aliens. 
Is there some sort of design plan that we can put on paper so when you two are off partying with aliens that we aren't 
left with this non-functional code and having to start from scratch?

The goal of #2 is a gut check to ask if it is better to wait and do a large pull request in the future when crop has 
been refactored? I don't think either scenario is ideal so just sort through which is more efficient for everyone and 
the best path forward for the project overall.

I really appreciate both of your work and want your input on what you think is the best path forward as well.

#### My Response

1. **Current Pull Request**: If a full overhaul is needed, as I suspect is the case, then merging in the current PR will 
likely not help anyone in the future.
   - I spoke with both Reid and Hector yesterday, and they both agree that a full overhaul would be best in the long run 
   - Since the overhaul will probably include large reorganization and restructuring of the code, it seems unlikely that 
   subsequent PRs will be small. 
   - I think, since a large PR is necessary in either case (now or later), it makes most sense to hold off until after 
   we're confident in the code. 
   - When we finally do make the large PR, we will also be able to provide manual test scripts that demonstrate the 
   functionality of each feature. This way the reviewer doesn't need to dig through the code to determine what/how to
   test the code.
   - Each function and feature will also have automated tests so that we are confident that the code does what
   we think it does, allowing the reviewer to simply look over our test suite to see that the code works.

2. **Organization**: I have an idea for how I'd like to reorganize things but would probably want further input from 
Pooya about the engineering and design.
   - I will be sure to thoroughly document my plans and share them with you before we begin.
   - I'll also make sure that documentation of the model is kept up-to-date as we go through the process so that the 
   thinking is clear and the work is understandable and reproducible.
   - I will do everything in my power to make sure that a clear road map is in place so that things can be continued
   after I leave (aliens, emergency, or otherwise). I'm a firm believer in note-taking because the best advice I ever
   got was, "your closest collaborator is you from 4 years ago, and he doesn't answer emails."

3. **Time**: It has taken me about a month to validate, test, and reorganize 4 routines files (`biomass.py`, 
`growth_constraints.py`, `nitrogen_uptake.py`, and `nitrogen_fixation.py`). Assuming that rate of 1 file per 
person week is representative, and given that there are 8 crop files, 4 field management, and 23 soil files left to 
look at, that's a total of 35 person weeks. If brandon and I work at the same rate, we could get it done in 4.4 months
(35 person weeks / 4 weeks per month / 2 people). With a clear vision in place we could probably cut that by %30
(25 person weeks) and adding the two new programmers will also be helpful, but I have no idea when they will get
officially hired and trained. Here are my more concrete estimates:
   - Best case scenario: end of December 
   - Worst case scenario: early March
   - most likely scenario: Late January to early February 

How does all this sound? Should we setup a meeting with the 3 of us and Pooya to discuss further?
