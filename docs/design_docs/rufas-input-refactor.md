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

## Proposed Solution

## Alternative Solutions

## Testability, Monitoring and Alerting

## Cross-Team Impact

## Open Questions

## Detailed Scoping and Timeline
