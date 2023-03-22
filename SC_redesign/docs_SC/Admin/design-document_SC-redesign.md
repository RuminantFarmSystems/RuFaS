# Design Document: Soil and Crop Module Redesign

Authors: Clay J. Morrow
Date created: 22 Mar 2023
Last updated: 22 Mar 2023
Reviewers: [TBD]

__Contents__:
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
4. [Milestones](#milestones)
5. [Existing Solution](#existing-solution)
6. [Proposed Solution](#proposed-solution)
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

## Milestones

**Note:** check [road-map_soil-and-crop.md](road-map_soil-and-crop.md)

---

## Existing Solution

---

## Proposed Solution

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