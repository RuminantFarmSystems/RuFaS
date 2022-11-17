---
title: "Soil and Crop Road Map"
author: "Clay J. Morrow (morrowcj@outlook.com)"
date: "09 November, 2022"
output: 
  html_document: 
    keep_md: yes
    toc: true
    toc_float: true
    toc_depth: 4
    highlight: "kate"
    pandoc_args: "--highlight-style=espresso"
---





## Introduction

The purpose of this document is to provide a road map for the RuFaS Soil and 
Crop Module. It will outline plans to guide the design and structure of the 
module. 

[Jump to Milestones](#milestones) to skip the details and look at the deliverables, 
broken down into manageable pieces. 

### Module status and problems (October 2022)

As of this writing, the Soil and Crop module (SC) is in a state of disarray and
bugs are near-impossible to track down. Below is a list of the general problems
that this document aims to address:

* The model returns entirely inaccurate results. For example, Crop
yields are much lower than expected and are inconsistent across 
years. 

* The components and sub-modules are not independent or isolated. For example
Performing tests requires running the **entire** model and looking through all
the output.

* Formal unit tests are not implemented for any of the code, so every 
component's integrity is suspect.

* Format and structure is not consistent throughout the module

* Documentation, both for the module components and the overall model, is 
severely lacking and sometimes conflicts with what the code does in actuality.

* Names of module entities are poorly selected and not intuitive. 

## Basic structure: Field, Soil, and Crop

The three main classes in this module are `Field`, `Soil`, and `Crop`. 

* A `Field` instance represents a single agricultural field on a farm. 
  - data attributes contain high-level information about the field such as 
  its dimensions and geographic location. 
  - contains a single `Soil` instance, and a variable number of
  `Crop` instances (in a list). 
  - methods pertain to management of the field (e.g., applying fertilizer, 
  planting/harvesting crops, etc.).
  - initialized at the start of a simulation and persists for the full duration,
  changing as time passes

* A `Soil` instance represents the soil profile of a single agricultural field.
  - data attributes contain information about the soil such as water and 
  nutrient content. 
  - because a soil profile typically consists of multiple layers, `Soil` 
  attributes are often lists whose elements correspond to a soil layer 
  (e.g. `Soil.nitrates[1]` is the amount of nitrates present in the second soil 
  layer from the surface). 
  - methods pertain to soil processes (e.g., nutrient cycling, erosion, etc.)
  - initialized with its containing `Field`, changing as time passes

* A `Crop` instance represents a single crop within an agricultural field.
  - data attributes contain information about the crop such as species-specific
  data, planting/harvest dates, biomass composition, etc.
  - methods pertain to crop processes such as nutrient uptake, 
  increasing/decreasing biomass, etc.
  - dependent upon the `Soil` in its `Field` (e.g., exchanging resources)
  - initialized when planted, destroyed when killed (after collecting final 
  data); changes as time passes
  
In pursuit of modularity and isolation, these classes inherit from a 
number of process classes, where methods are contained. For example the `Crop` 
class inherits from `NitrogenIncorporation`, `PhosphorusUptake`, `GrowthConstraints`, 
etc. The main classes `Field`, `Crop`, and `Soil` all inherit from such process 
superclasses. The benefit of these process superclasses is that they can 
be run/tested in isolation while coming together in the main class to work
together for high-level processes.

### Base classes

In general, the base classes should inherit most of their methods and attributes
from their respective superclasses (e.g., `Crop` inherits 
`.incorporate_nitrogen()` and `.nitrogen` from `NitrogenIncorporation`). However 
some things should be kept in the base class. In general, these should pertain 
to different initialization conditions or 'meta' attributes:

* setter/getter methods should be kept in base classes, when possible. As an 
example, `Crop._assign_species_attributes(species)` would set crop attributes 
according to its species (e.g., corn has different default attributes than 
alfalfa).

* similarly, `@classmethod` functions that initialize the class should be kept 
in the base classes

* meta-attributes that pertain to the entire crop might be stored in the base
class. As an example `Crop.species`, `Crop.crop_serial_ID`, and 
`Crop.simulation_counter` might be the species of the crop, the unique 
identifier of the crop in the simulation, and the current loop of the
simulation, respectively. These and similar attributes may be desired for 
reporting purposes and may fit best in the base class.

* Other situations may arise where methods and attributes should be housed in
the base class. Use good judgement, refer to the design principles, and ask
for a second opinion.

### Process superclasses

The process superclasses will be inherited by the base classes. 
They should follow consistent format, structure, and organization:

* they should be kept in separate files, with names referencing the superclass. For
example, `nitrogen_incorporation.py` contains the `NitrogenIncorporation` class
and related helper functions 

* they should be responsible for methods related to a single kind of process. For 
example, `NitrogenIncorporation` contains methods and attributes related to a 
crop's demand for, uptake, fixation, and incorporation of nitrogen.

* It is important that any variables used by multiple superclasses have the same name when 
declared in those classes!

* see the section on [Design Principles](#design-principles) for more details

## Input handling: SCInput

The model also needs a auxiliary class (`SCInput` or similar) that provides 
data to the model:

  * attributes contain **all** necessary input for the SC module to run and any
  optional input values
  
  * needs to be agnostic to the structure of the data and should contain 
  `@classmethod` functions that take data of different formats and returns the
  class. As an example `SCInput.from_json()` would build the class from input
  given in a .json file and `SCinput.from_dict()` would build from a dictionary,
  etc.
  
  * This way, we can change input format without changing the model - this class
  handles will always give data to the module in the same format, regardless of
  input format. 

## Data collection: OutputCurator

Another auxiliary class `OutputCurator` will collect any data generated by the model that needs 
tracking (e.g., from `Crop`, `Soil`, and `Field`) at the end of each iteration/day of the simulaton.
Like `SCInput` this class needs to be agnostic to the output structure and can have methods that
reformat the data to the output desired depending upon interface/View. 

## Managing the system: FieldManager

An SC simulation contains many instances of fields and thier crops that need to change
independently through time. The `FieldManager` class will be the high-level container that 
initializes and and stores all the fields according to user input (from `SCInput`), tracks them 
through time, directs them to perform their tasks, and pushes their output to `OutputCurator`

### FieldManager details

Here are some specifics about how `FieldManager` should work:

* the main method `.direct_fields()`, which executes all field events for a day, is called by the
simulation engine every day. 
  - it conducts all methods for each field one at a time (fully manage field `X` before moving on 
  to field `Y`)
  - within a field, it tells the soil to complete all its daily routines
  - within a field, it tells each crop - one at a time - to complete their daily routines (remember,
  multiple crops in a field need to share soil resources)
* `FieldManager` handles dependence on temporal variables such as the current day, year, and 
weather and passess the values to entities that need them.

### FieldManager simulation example

Below is a detailed example of a how `FieldManager` should behave for a system with 3 fields over a
two-year simulation. **Note:** This example is meant to display the flexibility of the model, not a 
realistic scenario.

**Example details:**

* in the first field: 
  - the soil is fertilized on day 8 of both years.
  - the soil is tilled on day 5 of the second year.
  - corn is planted on day 10 of the first and second year of the simulation
  - corn is cut on day 100 of both years but is only harvested (collected) during the first year. 
  In the second year, the biomass is left in the field.
* in the second field: 
  - no fertilization occurs
  - no crops are ever planted
* in the third field:
  - no fertilization occurs
  - alfalfa is planted on day 8 of the first year (perennials only planted once)
  - alfalfa is harvested on day 90 of both years
  - corn is planted on day 10 of the first year
  - corn is never cut
  - grass is planted on day 15 of the second year
  - grazing occurs both years, starting on day 50 and ending day 100. The grazers prefer grass

`FieldManager.direct_fields()` is called every day and does the following:

**Example steps:**

* Year 0, days 0:
  - startup: initializes the first `field` and its `soil`, followed by the second `field` and
  `soil`, and then the third
  - enters first `field`: does (**A**) = applies daily `soil` routines (nutrient cycling, erosion,
  etc.)
  - enters second `field`: does (**A**)
  - enters third `field`:  does (**A**)
  
* Year 0, days 1-7:
  - does (**A**) for all `field`s

* Year 0, day 8:
  - enters first `field`:
    + fertilization trigerred: nutrients are added to the `soil`
  - does (**A**) for second `field`
  - enters third `field`:
    + planting triggered = "plants" alfalfa by initializing a new `crop` (i.e.,
    `Crop(species="alfalfa")`)
    + does (**A**)
    + does (**B**) = applies daily `crop` routines for the alfalfa

* Year 0, day 10
  - enters first `field`:
    + planting triggered: initialize a new corn `crop`
    + does (**A**)
  - does (**A**) for second `field`
  - enters third `field`:
    + planting triggered: initialize a new corn `crop`
    + does (**A**)
    + does (**B**) for alfalfa, then corn

* Year 0, days 11-49:
  - does (**A**) for all `field`s and (**B**) for all `crop`s
  
* Year 0, day 50:
  - does (**A**) and (**B**) for all first and second `field`s 
  - enters third `field`:
    + grazing triggered: grazers are released
    + does (**A**)
    + does(**B**)
    + does (**C**) = execute grazing routines (some % of `crop` biomasses are removed each day)
    
* Year 0, days 51-89:
  - does (**A**) for all `field`s, (**B**) for all `crop`s, and (**C**) for the third `field`
  
* Year 0, day 90:
  - does (**A**) and (**B**) for first and second fields
  - enters third `field`:
    + harvest triggered: alfalfa `crop` is cut and biomass is collected, (alfalfa is not killed and 
    continues growing)
    + does (**A**)
    + does (**B**) for alfalfa and corn
    + does (**C**)
    
From here on out, only days where events occur will be shown:
    
* Year 0, day 100:
  - enters first field:
    + harvest triggered: corn is cut, collected, and killed (the `crop` is destroyed)
    + does (**A**)
  - does (**A**), (**B**), for second and `field`
  - enters third `field`:
    + end grazing triggered: stop grazing routines
    + does (**A**)
    + does (**B**)
  
* Year 1, day 5: tillage routines triggered in first `field`, ...

* Year 1, day 8: fertilization routines triggered in first `field`, ...

* Year 1, day 10: planting triggered - new corn `crop` initialized in first `field`, ...

* Year 1, day 15: planting triggered - new grass `crop` initialized in third `field`, ...

* Year 1, day 50: grazing triggered - grazing routines start again in third `field`, ...

* Year 1, day 90: harvest triggered - alfalfa collected, ...

* Year 1, day 100: 
  - harvest triggered - corn is cut, killed, and left in the first `field`, (**B**) 
  no longer occurs in first `field` since all crops are gone, 
  - end grazing triggered: strop grazing routines in third `field`, 
  - ...

Note that, at the end of each day, `.direct_fields()` would also be sending data to the 
`OutputCurator`. At the end of each year (and the simulation), the `OutputCurator` would
aggregate/summarize these data.

## General Design principles

**!Under Constructon!**

* Single Responsibility Principle (SRP)

* Don't repeat yourself (DRY)

## Code guidelines

Below is a bullet list of format/organization guidelines that the Soil and Crop module will
follow:

* All names and attributes should be descriptive and long enough to be
intuitive. Generally:
  - functions should be 2-5 full words, all lowercase, seperated with `_`
  - function names should start with a verb and class *member* function verbs should 
  describes what it does *from the perspective of the base class object* (e.g. a
  `Crop` can `.store_nitrogen()`, `.fix_nitrogen()`, 
  `.extract_nitrogen_from_soil()`, etc.)
  - attributes should be 1-3 full words, all lowercase, seperated with `_`
  - classes should be 1-2 full words, camel case, no word seperation
  - avoid abbreviations (some are acceptable if used repeatedly like `calc_` as
  a function prefix). 
  - readability is so important. You'll thank me later.

* class member functions should generally be *void* functions (return nothing). 
  - Their primary job is to update the class attributes. For example, 
  `NitrogenIncorporation.fix_nitrogen()` updates the `NitrogenIncorporation.fixed_nitrogen` 
  attribute with the amount of  nitrogen fixed during the day.
  - Most often they will take no arguments directly. When arguments are needed, 
  they should accept values (not objects) whenever possible. For example 
  `NitrogenIncorporation.stratify_nitrogen_uptake_requests(layer_nitrates)` requires a list of nitrates 
  available in each soil layer, and **not** a `Soil` object.
  - An exception to the above rule is when a direct interaction/exchange between
  classes is needed. For example, `NitrogenIncorporation.extract_nitrogen_from_soil(soil)` 
  requires a `Soil` instance because it transfers resources from the soil into the crop 
  (i.e., for `NitrogenIncorporation.nitrogen` to increase, `Soil.nitrogen` needs to 
  decrease simultaneously).
  
* functions that do not directly update class attributes (helper functions) 
should:
  - be external to the class, but usually in the same file (but may be reused in other files - 
  don't repeat yourself). 
  - generally, perform calculations and will often start with the `calc_` prefix 
  [**Note to self**: this is a hold-over from legacy code and I don't 
  particularly like it - perhaps I'll change this convention at some point, 
  but for now it's OK]
  - **always** accept values as argument input and not objects (lists of values
  may also be acceptable in some situations, i.e. 'vectorized' operations). 
  This is critical for modularity and flexibility and it makes testing easier.
  - almost always return values
  - not require the class (or any) to fully work
  - should be as general as possible (anticipate/facilitate reusability and alternative 
  applications by users)

* class attribute declarations should be seperated by 
  - those needed by member functions for for calculations. These should have default values
  - those that are **only** set by the methods. These should be explicitly initialized as `None`
  
* argument and function output types should be explicitly stated whenever possible.(e.g., 
`def fun(x: float, y: int) -> float:` indicates that `x` is a float, `y` is an integer, and the
output is a `float`.
  
* in-line documentation (docstrings):
  - attributes should be documented below its declaration (short: < 1 line)
  - member functions should have be short but descriptive documentation (about 1 sentence/phrase)
  - helper functons should have concise docs 1) overall description, 2) argument discription, 3)
  output description
  - member functions that require external arguments should also be documented within the class
  - units need to be included when they matter, but some funcions are unit neutral (e.g., input kg, 
  get kg back, same with g and mg, etc.)
  - units always matter **within** a class
  
Here's an example of a `Crop` process superclass that follows these guidelines:
  

```python
# nitrogen_incorporation.py

class NitrogenIncorporation:
  def __init__(self):
    self.optimal_nitrogen_fraction = 1/3
    """optimal proportion of crop biomass comprised of nitrogen"""
    self.biomass = 100
    """total crop biomass (kg)"""
    self.total_nitrogen_uptake = 25.3
    """total nitrogen to be taken up from soil in a day (kg)"""
    self.nitrogen = 0
    """total nitrogen stored in the crop (kg)"""
    self.optimal_nitrogen = None
    """optimal amount of nitrogen desired by the crop (kg)"""
    
  def determine_optimal_nitrogen(self) -> None:
    """determine the crop's optimal nitrogen for the day"""
    self.optimal_nitrogen = calc_mass_from_fraction(self.optimal_nitrogen_fraction, self.biomass)
    
  def extract_nitrogen_from_soil(soil: Soil) -> None:
    """extract nitrogen from the soil
    
    Args: 
      soil: an instance of Soil, from which nitrogen will transfered
    """
    soil.nitrogen -= self.total_nitrogen_uptake
    self.nitrogen += self.total_nitrogen_uptake 
    
    
def calc_mass_from_fraction(fraction: float, whole: float) -> float:
  """calculate mass of a constituent from the fractional mass of the whole
  
  Args:
    fraction: proportion of the whole comprised of the constituent
    whole: total mass of the whole
    
  Returns: mass of the constituent
  """
  return fraction * whole
```

Note that `calc_mass_from_fraction()` could be usefull for other processes (e.g., phosphorus 
incorporation) and can be easily reused:


```python
from nitrogen_incorporation import calc_mass_from_fraction

phosphorus_biomass = calc_mass_from_fraction(phosphorus_fraction, biomass)
```

## Model Documentation 

**Under Construction**

## Code Review

A code review process will facilitate that the module components meet the consistency and 
standardization laid out here. A new github branch called `SC_redesign` has been created, and will 
house the Soil and Crop redesign until it is ready to be merged with the `master` branch.
Development will occur on user-specific sub-branches that will be added to `SC_redesign` via 
pull request. 

## Milestones 

Below are measurable components that the module should have, which will be tracked as development
continues. 

* All the main process files (`.py`) need to be reformatted and reorganized to the new design, 
cross-checked with source documentation, tested, and documented (updated pseudocode). In total, 
there are:
  - 10 crop files (`RUFAS/routines/field/crop/`)
  - 23 soil files files (`RUFAS/routines/field/soil/`)
  - 4 field management files (`RUFAS/routines/field/field_management`)
  
* The main classes (`Soil,` `Crop`, and `Field`) need to be rewritten with new formatting 
guidelines, and linked to the process classes.

* The current `Crop.py` file (`RUFAS/routines/field/crop/`) need to be re-written and organized 
into the new `FieldManager` class. 

* the new `DataCurator` and `SCInput` classes need to be created

Here are a list of things that the code needs to do (see 
[`SC_redesign/Functionality-Requirements`](SC_redesign/Functionality-Requirements.html) for more 
details about what SC should do):

* `Crop` should be able to initialize with different species-specific attributes and from input data
* `Crop` methods should reflect daily crop processes (e.g., SWAT)
* `Soil` should be able to initialize with soil profile attributes from input data
* `Soil` methods should reflect daily soil processes (e.g., SWAT)
* `Field` should be able to initialize with different dimensions and geography, + input data
  - should be able to initialize `Crop` and `Soil`, passing them the data they need
  - needs to have one `Soil` and 0-n `Crop`
* `Field` methods should reflect field management processes (apply manure/fert, plant/harvest crops,
  - methods should manage crops one by one
etc.) and will often be wrappers that call `Soil` and `Crop` methods
* `FieldManager` should be able initialized based on input data
  - should be able to initialize a number of `Fields`, passing them data they need
* `FieldManager` methods should reflect management of the system
  - should track which `Field`/`Soil` processes need to run and execute them accordingly, such as: 
    + `Crop` planting/multi-cropping
    + following cropping patterns
    + `Crop` growing season/dormancy
    + `Crop` cutting/harvesting/killing/cover-cropping
    + fertilizer/manure addition to `Soil`
    + `Soil` tillage
  - should manage fields one by one
  - should pass relevant weather and time data to `Field`
  - should accept input from `SCInput` and pass output to `OutputCurator`

  
