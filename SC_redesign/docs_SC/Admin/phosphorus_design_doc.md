# Design Document: Phosphorus Cycling Module Redesign

Authors: Ed Hansen  
Date Created: 27 Mar 2023  
Last Updated: 27 Mar 2023  
Reviewers: Clay Morrow

## Contents:
1. [Overview](#overview)
2. [Context](#context)
3. [Requirements](#requirements)  
   a. [Phosphorus Cycling](#phosphorus-cycling)  
   b. [Fertilizer](#fertilizer)  
   c. [Manure Application](#manure-application)  
   d. [Manure](#manure)  
   f. [Mineralization](#mineralization)  
   g. [Soluble Phosphorus](#soluble-phosphorus)  
   i. [Other Requirements](#other-requirement-details)
4. [Open Questions](#open-questions)
5. [Beyond Version 1](#beyond-version-1)

--- 

## Overview
This document will detail how the redesigned Phosphorus Cycling (PC) submodule operates/will operate within the Soil 
module of RuFaS. The redesign that is described in this document is a part of the larger Soil and Crop redesign project,
on which details can be found here: [design-document_SC-redesign.md](design-document_SC-redesign.md).

---

## Context
The Phosphorus Cycling submodule is based largely on the SurPhos model for predicting the portions of phosphorus that 
are lost from the soil surface in runoff. It was designed specifically to improve on the shortcomings of the SWAT model 
in this aspect. Currently (March 2023), the state of the Phosphorus Cycling submodule 
(`RUFAS/routines/field/soil/phosphorus_cycling/`)is in the same state of disarray as the rest of the Soil and Crop 
module, described in the above document describing the Soil and Crop redesign.

---

## Requirements
This section will list the requirements of PC in order to be integrated with and used by other modules. 
* Provide a composite class that can be used by higher level modules to efficiently and effectively manage phosphorus on
and in the soil, including
  * Phosphorus content on the soil surface.
  * Phosphorus content in each layer of the soil profile.
  * Amount of phosphorus that have been lost from the field due to runoff.
* Provide ability to add phosphorus via fertilizer to a field.
* Provide ability to add phosphorus via manure to a field, with options for
  * Manure applied with a machine.
  * Manure applied with by animals grazing in said field.

### Other Requirement Details
* This section does not flush out the requirements that may be addressed in future versions of this module. See 
[Beyond Version 1](#beyond-version-1)

---

## Existing Solution
In the previous implementation of the Phosphorus Cycling module, the model simply maintained a soil profile that was 
based on the user-defined input.

---

## Proposed Solution
Automatically divide the user-defined top layer of soil into two layers: a top layer that is 20 mm thick, so that the 
simulation can follow critical parts of the SurPhos model, and then a second layer. This second layer is the same as the
user-defined top layer of soil except for the fact that it's top depth is 20 mm below where the user specified it was.  

Most of the Soil and Crop modules outside of PC will not have their operations disrupted by this new top layer, however
in a few specific cases processes that work with the whole soil profile are dependent on the top layer of soil. In these
cases the model will treat the soil profile as if it had the original top layer of soil, as defined by the user.

---

## Alternative Solution
Some solutions considered when this design was being flushed out:
* Maintain a special set of pools in the soil profile that are used to track what is in the top 20 mm of the soil 
    profile.
  * Pros:
    * Enables most accurate picture of soil profile to be maintained.
    * Does not mutate the soil profile specified by the user.
  * Cons:
    * Would likely result in an extremely complex implementation that touches many modules outside of Phosphorus 
    Cycling.
* Do not simulate the top 20 mm of soil in the profile (this one is kind of a non-starter, but listed to fully flush 
out options).
  * Pros:
    * Does not require any additional implementation at all.
    * Does not change user-input attributes at all.
  * Cons:
    * Severely hinders the accuracy of the SurPhos model that this module is based on.

---

## Beyond Version 1
There are some requirements that will not be implemented for version 1 but should be considered for future enhancements,
including:
* Tilling. Currently, the phosphorus pools both in the soil profile and on the soil surface are not affected by tillage.
* Nitrogen and organic matter. Pete Vadas (one of the SurPhos creators) has noted that methods and practices from 
SurPhos can be applied to nitrogen and organic matter, which would result in a more accurate picture of the soil profile
overall.
Note that both the above enhancements will almost certainly require conversations with Pete to make sure they are 
implemented correctly, and possibly the development of some novel features in SurPhos.

---
## Scoping
This section describes about the design and implementation of PC.

### Phosphorus Cycling
This submodule will serve as the composite class for PC. It will include
- a main routine that can be called by higher-level modules and will execute all daily updates on phosphorus already in
the field.
- methods used by multiple PC sub-modules

It will be structured similar to other 
[Soil and Crop classes](design-document_SC-redesign.md#module-design-and-structure), with one notable difference: all 
states related to phosphorus will be maintained in `SoilData` and `LayerData` instances, not in a `@dataclass` specific
to PC.

### Fertilizer
`Fertilizer` serves as the handler of all additions and daily management of phosphorus that comes from fertilizer on the
soil surface. There are two methods that can be called by higher-level modules:
1. add_fertilizer_phosphorus(), which adds phosphorus to fertilizer phosphorus surface pools
2. do_fertilizer_phosphorus_operations(), which conducts daily leaching and runoff activities based on only 3 
parameters:
   * the amount of rainfall on the current day
   * the amount of runoff on the current day
   * the size of the field on which these operations are occurring

The `Fertilizer` submodule is designed with the assumption that there will not be frequent applications of phosphorus 
via fertilizer (~1 time per year). This reflects the most common real-world agricultural practices.

### Manure Application
This submodule handles **applying** phosphorus from manure to a field (which is, arguably, a crappier way to apply 
phosphorus than applying via fertilizer). When implementing this submodule, the original intent was to have everything 
in the `Manure` module but the application operations became too complex, and necessitated separate modules. 
There are two methods to be used by higher level modules. One is for manure applied by animals grazing in a field 
[grazing not yet implemented in RuFaS], and the other is for manure applied by machine. Each type of manure has its own 
set of pools and factors that includes
* Pools of Phosphorus
  * Water-extractable inorganic pool
  * Water-extractable organic pool
  * Stable inorganic pool
  * Stable organic pool
* Factors that determine phosphorus absorption, runoff, etc.
  * % of field covered by manure
  * how wet the manure on the field is (the moisture factor)
  * the dry-weight equivalent of the amount of manure on the field

Unlike the `Fertilizer` submodule, `ManureApplication` is designed to handle more frequent applications of manure 
phosphorus. It does this by resetting the various factors it maintains to an average weighted by masses of the new 
phosphorus application and the phosphorus already on the field.

### Manure
The `Manure` submodule handles all daily operations on the phosphorus from manure that is currently on the field, and 
will only have one method that gets called by higher-level modules. These operations consist of
* Transferring phosphorus from the surface pools to soil phosphorus pools
* Transferring phosphorus between different surface pools to reflect the chemical composition of the manure changing
* Removing phosphorus from the surface pools as runoff occurs.

### Mineralization
This submodule will model the chemical transformations of phosphorus in the soil profile as it is mineralized and 
immobilized (i.e. is transferred between different pools within the soil profile).


### Soluble Phosphorus
This submodule will be responsible for maintaining an accurate state of the soil profile in regard to its phosphorus 
content. There are two main processes it will need to simulate in order to accomplish this
* Erosion from the top layer of soil
* Phosphorus movement between different layers in the soil profile

### Other Details
* The SurPhos model specifically tracks the amount of phosphorus in the top 20 mm of the soil profile, as this 
phosphorus was determined to be critical to accurately tracking how much phosphorus was removed from the field in 
runoff. To see how we integrate this into PC, see the [solution](#proposed-solution) that we have elected to implement.