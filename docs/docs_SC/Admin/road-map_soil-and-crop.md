## Introduction

The purpose of this document is to provide a road map for the RuFaS Soil and 
Crop (SC) Module. It will outline plans to guide the design and structure of the 
module. 

[Jump to Milestones](#milestones) to skip the details and look at the deliverables, 
broken down into manageable pieces. 

### Module status and problems (October 2022)

As of this writing, the Soil and Crop module (SC), located in `RUFAS/routines/field/`, is in a state of disarray and
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
  planting/harvesting crops, etc.) and often correspond to following a schedule (do x on date Y).
  - initialized at the start of a simulation and persists for the full duration,
  changing as time passes

* A `Soil` instance represents the soil profile of a single agricultural field.
  - built from `SoilData` whose attributes contain information about the soil such as water and 
  nutrient content. 
  - because a soil profile typically consists of multiple layers, `Soil` 
  attributes are often lists whose elements correspond to a soil layer 
  (e.g. `Soil.nitrates[1]` is the amount of nitrates present in the second soil 
  layer from the surface). 
  - component "process classes" contain methods that pertain to soil processes (e.g., nutrient cycling, erosion, etc.)
  - initialized with its containing `Field`, changing as time passes

* A `Crop` instance represents a single crop species within an agricultural field.
  - built from `CropData` whose attributes contain information about the crop such as species-specific
  data values, planting/harvest dates, biomass composition, etc.
  - component "process classes" contain methods pertaining to crop processes such as nutrient uptake, 
  increasing/decreasing biomass, etc.
  - depends upon and interacts with the `Soil` in its `Field` (e.g., exchanging resources)
  - initialized when planted, destroyed when killed (after collecting final 
  data), changes as time passes
  
In pursuit of modularity and isolation, these classes will follow the "composite" design pattern, wherein they are made
up of (contain) other classes. The primary component classes are process classes, which each house methods for a 
particular process (biological, management, etc). For example the `Crop` 
class is a composite of `NitrogenIncorporation`, `PhosphorusIncorporation`, `GrowthConstraints`, 
etc. The main classes `Field`, `Crop`, and `Soil` all utilize from such process classes. 
The benefit of these process superclasses is that they can be run/tested in isolation while coming 
together in the main class to work
together for high-level processes. It also allows each of the units or classes to be completely agnostic of
the other units. 

### Main (composite) classes

In general, the main composite classes should receive most of their methods and attributes
from their respective components (e.g., `Crop` has an attribute `nitrogen_incorporation` which is an instance
of `NitrogenIncorporation` and `nitrogen_incorporation.incorporate_nitrogen()` is called by the main method). However, 
some features may be implemented directly in the  composite class: 

* class and initialization methods can be kept in base classes, when possible. As an 
example, the class method `Crop.plant_species(species)` initializes a crop with preset data values according to the 
`species` given. 

* Other situations may arise where methods and attributes should be housed in
the base class. Use good judgement, refer to the design principles, and ask
for a second opinion.

### Data classes

Data class components control the configuration/setup of each composite class and track the relevant state 
variables/attributes. 
For example, the `Crop` class is initialized with a component attribute `data` which is an instance of `CropData`. This
instance contains all the crop's data values and is used and updated by the other components. The starting value of one 
such attribute `data.nitrogen` is used and updated by `nitrogen_incorporation.incorporate_nitrogen()` and the
updated value is used by `growth_constraints.constrain_growth()` to calculate the crop's growth for the day. This 
process is repeated every day that the crop grows and many of the crop variables are utilized in this way.

### Process classes

The process classes will be utilized by the composite classes. 
They should follow consistent format, structure, and organization:

* they should be kept in separate files, with names referencing the overarching process or system. For
example, `nitrogen_incorporation.py` contains the `NitrogenIncorporation` class and related functionality. 

* they should be responsible for methods related to a single kind of process. For 
example, `NitrogenIncorporation` contains methods and attributes related to a 
crop's demand for, uptake, fixation, and incorporation of nitrogen.

* they have/utilize data class components (e.g., `NitrogenIncorporation` is initialized with `data`, which is an 
instance of `CropData`. It is important that any variables used by multiple process classes are attributes of the data 
* class.

* see the section on [Design Principles](#design-principles) for more details

## Managing the system: FieldManager

An SC simulation contains many instances of fields and their crops and soil which need to change
independently through time. The `FieldManager` class will be the high-level container that 
initializes and stores all the fields according to user input (from `SCInput`), tracks them 
through time (i.e., checks if the current date/weather should trigger an event), directs 
them to perform their tasks, and pushes their output to the output handler.

### Input handling: SCInput

The model's configuration will be handled by the `SCInput` class (or similar), which that provides 
data and specifications to the model:

  * the attributes of `SCInput` contain **all** necessary input for the SC module to run and any
  optional input values.
  
  * needs to be agnostic to the structure of the data and should contain 
  `@classmethod` functions that take data of different formats and returns the
  class. As an example `SCInput.from_json()` would build the class from input
  given in a .json file and `SCinput.from_dict()` would build from a dictionary,
  etc.
  
  * This way, we can change input format without changing the model - this class
  will always give data to the module in the same format, regardless of
  input format. 

### Data collection: OutputCurator

The `FieldManager` would pass relevant output to another auxiliary class `OutputCurator` (or similar), which collect 
any data generated by the model that needs tracking (e.g., from `Crop`, `Soil`, and `Field`) for output to the user. 
This occurs at the end of each iteration/day of the simulaton. Like `SCInput` this class needs to be agnostic to the 
output structure and can have methods that reformat the data to the output desired depending upon interface/View. 

**Note:** this may be redundant with the new `OutputManager` class being developed by Pooya and Niko, so I'll simply 
refer to this as the "output manager" rather than by a class name.

### FieldManager details

Here are some specifics about how `FieldManager` should work:

* the main method `.manage_fields()` (or similar), which executes all field events for a day, is called by the
simulation engine every day.
  - checks the current date and time, evaluates if any events should be triggered (evaluated for each field) 
  - executes daily routines for each field one at a time (fully manage field `X` before moving on to field `Y`)
  - within a field, it tells the soil to complete all its daily and triggered routines
  - within a field, it tells each crop - one at a time - to complete their daily and triggered routines (remember,
  multiple crops in a field need to share soil resources)
* `FieldManager` handles dependence on temporal variables such as the current day, year, and 
weather and passes the values to entities that need them (e.g., `Crop.is_harvest_day(date)`).

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

`FieldManager.manage_fields()` is called every day and does the following:

**Example steps:**

* Year 0, days 0:
  - startup: initializes the first `field` and its `soil`, followed by the second `field` and
  `soil`, and then the third (from specifications contained in `SCInput`)
  - enters first `field`: does (**A**) = applies daily `soil` routines (nutrient cycling, erosion,
  etc.)
  - enters second `field`: does (**A**)
  - enters third `field`:  does (**A**)
  
* Year 0, days 1-7:
  - does (**A**) for all `field`s

* Year 0, day 8:
  - enters first `field`:
    + fertilization triggered: nutrients are added to the `soil`
  - does (**A**) for second `field`
  - enters third `field`:
    + planting triggered = "plants" alfalfa by initializing a new `crop` (i.e.,
    `Crop.plant_species("alfalfa")`)
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
    + does (**C**) = execute grazing routines (some % of `crop` biomass is removed each day)
    
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
    
**From here on out, only days when events occur will be shown:**
    
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

Note that, at the end of each day, `manage_fields()` would also be sending data to the 
output manager. At the end of each year (and the simulation), the output manager would
aggregate/summarize these data.

## General Design principles

**!Under Construction!**

* Single Responsibility Principle (SRP)

* Don't repeat yourself (DRY)

* Parsimony: simplify code and make it concise when possible

## Code guidelines

Below is a bullet list of format/organization guidelines that the Soil and Crop module will
follow:

* All names and attributes should be descriptive and long enough to be
intuitive. Generally:
  - functions should be 2-5 full words, all lowercase, separated with `_` ("snake case")
  - function names should start with a verb and method function verbs should 
  describe what it does *from the perspective of the composite class object* (e.g. a
  `Crop` can `.store_nitrogen()`, `.fix_nitrogen()`, 
  `.extract_nitrogen_from_soil()`, etc.)
  - attributes should be 1-3 full words, snake case
  - classes should be 1-2 full words, capitalized first letters of each word, no word separation (title case)
  - avoid abbreviations (some are acceptable if used repeatedly like `calc_` as
  a function prefix). 
  - readability is so important: more than short code. You'll thank me later.

* main class methods should generally be *void* functions (return nothing). 
  - Their primary job is to update the class attributes. For example, in the `NitrogenIncorporation` class,
  `Nfix_nitrogen()` updates the `data.fixed_nitrogen` 
  attribute with the amount of  nitrogen fixed during the day.
  - Most often they will take no arguments directly. When arguments are needed, 
  they should accept values (instead of class) whenever possible. For example 
  `stratify_nitrogen_uptake_requests(layer_nitrates)` requires a list of nitrates 
  available in each soil layer, and **not** a `Soil` object. Configuration classes are the notable exception.
  
* functions that do not directly update class attributes (helper functions) 
should:
  - be static functions (i.e., use the `@staticmethod` decorator) 
  - generally implement equations and perform calculations 
  - **always** accept values as argument input and not objects (lists of values
  may also be acceptable in some situations, i.e. 'vectorized' operations). 
  This is critical for modularity and flexibility, and it makes testing easier.
  - (almost) always return values
  - not require the containing class (or any) to fully work 
  (e.g., `NitrogenIncorporation._determine_nitrogen_shape_parameters()` can be called without an instance of 
  `NitrogenIncorporation`)
  - should be as general as possible (anticipate/facilitate usability and alternative 
  applications by users)
  - may often be "private" methods (prefixed with an `_`), since RUFAS won't (usually) use them outside the class. 
  This may be counterintuitive for a `@staticmethod` but private methods in python are convention-only and can still
  be used outside the class. This provides savvy users the flexibility to use the core functions for their own 
  purposes in their own ways. 

* data class attribute declarations should 
  - be separated by attributes needed by process classes for calculations (should have default values) and 
  those that are **only** set by the methods. These should be explicitly initialized as `None`
  - have type hints (see the `typing` module)
  - have documentation of what the attribute represents in the model, with a docstrings line below the attribute
  
* argument and function output types should be explicitly stated whenever possible via type hints (e.g., 
`def fun(x: float, y: int) -> float:` indicates that `x` is a float, `y` is an integer, and the
output is a `float`).
  
* in-line documentation (docstrings):
  - attributes should be documented below its declaration (short: around 1 line)
  - methods should have short but descriptive documentation (about 1 sentence/phrase)
  - static functions should have descriptive (but concise) docs: 1) overall description, 2) argument description, 3)
  output description, 4) source material reference, 5) details
  - all methods that require external arguments should also be documented
  - units need to be included when they matter, but some funcions are unit neutral (e.g., input kg, 
  get kg back, same with g and mg, etc.)
  - **units always matter for data attributes**  

* **ALL** classes should have tests for **all** methods and functions.

Here's an example of a component class that follows these guidelines:

```python
# crop_data.py

from typing import Optional, List
from dataclasses import dataclass

@dataclass
class CropData:
    root_depth: float = 1.0
    """current depth of the plant roots in the soil (mm)"""
    
    total_soil_layers: Optional[int] = None
    """total number of layers in the soil profile (unitless)"""
    accessible_soil_layers: Optional[int] = None
    """number of layers in the soil profile that the plant roots have access to (unitless)"""
    inaccessible_soil_layers: Optional[int] = None
    """number of layers in the soil profile that the plant roots do not have access to (unitless)"""
```  

```python
# nitrogen_incorporation.py

from typing import Optional, List
from bisect import bisect
from crop_data import CropData

class NitrogenIncorporation:
  def __init__(self, crop_data: Optional[CropData] = None):
    self.data = crop_data or CropData()
    
  def incorporate_nitrogen(self) -> None:
    """main nitrogen incorporation function, executes plant processes to add nitrogen to biomass"""
    # ... do some stuff ...
    self.find_deepest_accessible_soil_layer(...)
    # ... do some other stuff ...  
  
 
  def find_deepest_accessible_soil_layer(self, depths: List[float]) -> None:
      """evaluates the accessibility of layers in the soil profile by plant roots

      Args:
          depths: the maximum depth of each soil layer

      Details: gets the total number of soil layers, the deepest layer accessible to the roots,
      and the number of layers that remain inaccessible to the plant.
      """
      self.data.total_soil_layers = len(depths)
      self.data.accessible_soil_layers = self._determine_deepest_accessible_layer(self.data.root_depth, depths)
      self.data.inaccessible_soil_layers = max(len(depths) - self.data.accessible_soil_layers, 0)
      
  @staticmethod
  def _determine_deepest_accessible_layer(root_depth: float, layer_bounds: List[float]) -> int:
      """
      Description:
          Determines the deepest soil layer that is accessible to roots.

      Args:
          root_depth: the root depth of a plant
          layer_bounds: the depths of the lower boundaries of each soil layer

      Returns:
          an integer indicating the deepest soil layer that the roots can access

          example: return of 1 means only the first layer is accessible (i.e., accessible_depths[:1]) and a return of
          2 means the first and second layers are accessible (i.e., accessible_depths[:2])
      """
      if root_depth <= 0:  # handle no roots
          raise ValueError("root_depth cannot be less than zero")
      else:
          insert_position = bisect(layer_bounds, root_depth)
          deepest_layer = len(layer_bounds)
          return min(insert_position + 1, deepest_layer)
```

Note that `_determine_deepest_accessible_layer()` could be useful for other processes (e.g., phosphorus 
incorporation) and can be easily reused. This isn't a great example, since we can directly access the updated values 
of `data` directly, but other functions are useful across modules.

## Model Documentation 

**Under Construction**

## Code Review

A code review process will ensure that the module components meet the consistency and 
standardization laid out here. A new github branch called `SC_redesign` has been created, and will 
house the Soil and Crop redesign until it is ready to be merged with the `master` branch.
Development will occur on user-specific sub-branches that will be added to `SC_redesign` via 
pull request. 

In order to merge a development branch into `SC_redesign`, all tests in the `SC_redesign/Crop_and_Soil/tests_SC/` 
need to pass, 2 people need to review the code, and no conflicts with the base branch can exist.

## Milestones 

Below are measurable components that the module should have, which will be tracked as development
continues. 

* All the main process files (`.py`) need to be reformatted and reorganized to the new design, 
cross-checked with source documentation, tested, and documented (updated pseudocode). 
The original versions should remain in-tact and new versions placed in `SC_redesign/Crop_and_Soil/` until the redesign
is complete. In total, there are:
  - [ ] 10 crop files, 2671 lines (`RUFAS/routines/field/crop/`)
  - [ ] 23 soil files, 2213 lines (`RUFAS/routines/field/soil/`)
  - [ ] 4 field management files, 295 lines (`RUFAS/routines/field/field_management`)

* The main classes need to be rewritten with new formatting guidelines, and linked to the process classes.
  - [ ] `Soil`
  - [ ] `Crop`
  - [ ] `Field`

* The current `Crop.py` file (`RUFAS/routines/field/crop/`) needs to be re-written and organized 
into the new `FieldManager` class. 

* the new data manager and `SCInput` classes need to be created and utilized

Here are a list of things that the module code needs to do (see 
[SC_redesign/Crop_and_Soil/docs/Admin/Functionality-Requirements.md](./Functionality-Requirements.md) 
for more details about what SC should do):

* [ ] `Crop` should be able to initialize with different species-specific attributes and from input data
* [ ] `Crop` component methods should reflect daily crop processes (e.g., SWAT)
* [ ] `Soil` should be able to initialize with soil profile attributes from input data
* [ ] `Soil` component methods should reflect daily soil processes (e.g., SWAT)
* [ ] `Field` should be able to initialize with different dimensions and geography, from input data
  - should be able to initialize `Crop`(s) and `Soil`, passing them the data they need
  - needs to have one `Soil` and 0-n `Crop`
* [ ] `Field` methods should reflect field management processes (apply manure/fertilizer, plant/harvest crops,
  - methods should manage crops one by one 
  - and will often be wrappers that call `Soil` and `Crop` methods
* [ ] `FieldManager` should be able initialized based on input data
  - should be able to initialize a number of `Fields`, passing them data they need
* [ ] `FieldManager` methods should reflect management of the system
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
