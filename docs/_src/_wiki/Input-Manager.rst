Input Manager
=============

Overview
--------

The Input Manager (IM) serves as an upgrade and update to the previous
method of input data management in the RuFaS model.

Previously RuFaS would take its input from a series of json files, csv
files, and SQLite DBs. This posed a number of challenges for running the
model under different scenarios and starting conditions. Additionally,
it suffered from scalability and validation issues.

The IM addresses these issues with these functionalities and features:

1.  Differentiation of critical inputs from non-critical inputs.
    Critical inputs are inputs without which the simulation cannot run
    whereas non-critical inputs are inputs which can be fixed on the fly
    should they not exist or are not in the correct form or expected
    conditions.
2.  Input data validation to ensure that the structure of the data is
    usable and the values are within predefined ranges and/or follow
    specified patterns.
3.  Fixing non-critical data inputs which make validations fail.
4.  Terminating a simulation when critical inputs make data validations
    fail.
5.  Reporting its activities’ logs to Output Manager’s logs pool.
6.  Being the Single Source of Truth (SSOT) for all inputs that RuFaS
    needs. In other words, IM is the entry point to the system and is
    upstream to all other parts of the system (biophysical modules, EEE
    module, Output Manager, etc…).
7.  Being vertically scalable.
8.  Allowing modification to input data without needing to change the
    code.
9.  Allowing integration with different parts of the system (Animal
    Module, Crop and Soil Module, Manure Module, etc...).
10. Allowing sequential runs.

.. figure:: /_static/IM_diagram.png
   :alt: RuFaS Overview - IM
   :align: center
   :name: rufas overview

   A high-level flow of IM within RuFaS.

How does IM work?
-----------------

1. Loads and parses the metadata file(s) specified by Task Manager.
2. Loads and parses input data as instructed by metadata.
3. Performs validation on data as instructed by metadata.
4. For non-critical inputs that have failed the validation step, "fixes"
   these inputs by loading their default values.
5. After validation and fixing, returns a boolean value to indicate
   whether or not the input data was valid.

.. figure:: /_static/how_does_IM_work.png
   :alt: RuFaS Overview - IM
   :align: center
   :name: rufas overview

Input validation process in IM:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: /_static/IM_validation_process.png
   :alt: RuFaS Overview - IM
   :align: center
   :name: rufas overview

Click
`here <https://whimsical.com/input-manager-data-validation-overview-T6TuSktxPUYe3BRUURhaDm>`__
to see enlarged version of this diagram.

Notes:
~~~~~~

- Like Output Manager, Input Manager is a singleton, i.e., only one
  instance of it can exist. After the first instance is created, future
  calls to the constructor method return the first instance. Also, the
  initializer method only works once.
- During a normal simulation, IM will terminate the data validation
  process as soon as it encounters a critical input that is unfixable
  (i.e. it does not have a default value provided by the metadata). This
  is set by the flag, ``eager_termination``, which ensures that users
  are not running simulations with bad data.
- However, IM's data validation functionality can be used separate from
  running a simulation. This functionality allows the user to validate
  their input data in toto because ``eager_termination`` is turned off.
  With ``eager_termination`` off, the unfixable-critical data is
  catalogued by Output Manager and the user can see a full report of
  their entire set of input data and see which inputs have been fixed
  and for what reason along with which critical inputs are invalid. To
  use this functionality, add the ``-ov`` (for only validation) flag to
  the command to run the model: ``python main.py -ov`` For more details
  on this and other gnu arguments that can be used, try
  ``python main.py -h`` for help or read through the details in the
  forthcoming gnu args section of the RuFaS wiki.

Getting Data from Input Manager's Data Pool
-------------------------------------------

Input Manager has a single data pool to which all data from all input
files is loaded. To retrieve the data needed from the Input Manager's
data pool:

1. Import the InputManager class into the Python file in which you are
   working. ``from RUFAS.input_manager import InputManager``
2. Instantiate InputManager (``input_manager = InputManager()``) in the
   constructor if possible, or within the static method. **Do not
   initialize InputManager as a global variable, as this can lead to
   unexpected initialization during imports.** Since InputManager is a
   singleton, multiple initializations do not significantly affect
   complexity.
3. Set up a variable to hold the value you want to get from the pool and
   call Input Manager's ``get_data()`` method.
   ``cow_data = InputManager.get_data('cow_data')``
4. The user can request as broad or narrow a selection of the data as
   they want. More details on this process can be found in the
   docstrings of the IM's ``get_data()`` method:
   https://github.com/RuminantFarmSystems/RuFaS/blob/main/RUFAS/input_manager.py#L534

Adding New Input Data to be Validated by Input Manager
------------------------------------------------------

If there is new data that is needed to run a simulation, the data must
be added to appropriate input file AND all metadata files must be
updated accordingly to know to expect and how to validate this new input
data. This means adding the appropriate guidelines for the data (e.g.
minimum/maximum value, string RegEx pattern, etc.) as well as a default
value that can be substituted should the provided input value be invalid
according to the provided validation guidelines. The structure of the
input data should always match the appropriate metadata properties
section.

In the pipeline for IM development:

1. IM should provide data sanity check (i.e. corpus validation)
   functionality to ensure that input data collectively makes sense.
2. IM should allow integration with various input streams (files, DBs,
   API calls, etc...).

Metadata
--------

Introduction
------------

Metadata is defined as the information that describes and explains data.
It provides context with details such as the source, type, owner,
relationships to other data sets. It can also provide guidelines for the
validity of the data's values. So, metadata can help to understand the
relevance of a particular data set and guide people and systems like
RuFaS on how to use it.

Both of RUFAS's IO Managers rely on metadata to function properly. The
metadata for OutputManager describes what and how output streams should
be populated.

For InputManager, the metadata:

1. Distinguishes critical inputs from non-critical inputs.
2. Describes the data validation rules.
3. Supplies default values for critical inputs.

RuFaS relies on metadata for handling inputs to be able to successfully
run simulations.

The majority of the rest of this Wiki page will be dedicated to
explaining the InputManager's metadata.

The Metadata File(s)
--------------------

The InputManager's metadata is stored in JSON format. The JSON format
provides needed flexibility and compatibility with Python dictionaries
and API payloads. The metadata also contains pointers to the input data
needed to run the RuFaS simulation. These data will be validated by the
rules and guidelines set in that very same metadata.

| The metadata files are stored within the main input folder within the
  metadata subfolder (RuFaS > input > metadata). Within that subfolder
  there is also a ``properties`` directory that contains one or more
  metadata properties files.
| The input files to which the metadata points are currently stored
  within the same input folder but within the data subfolder (RuFaS >
  input > data). These subfolders are further subdivided into folders
  that closely mimic the structure of the codebase (animal, field, soil,
  manure storage and handling, etc). It is important to note: this
  file-directory structure is only how things are set up right now. The
  metadata is ambivalent to the sources and locations of the input data
  so long as the paths pointing to the data are up to date. The metadata
  is also capable of pointing to input sources that are not file-based
  such as API-payloads.

Metadata Blobs
--------------

The metadata structure consists of 3 main blobs - "files", "properties",
and "cross-validation".

The "files" blob
~~~~~~~~~~~~~~~~

This blob is broken into sub-blobs closely mimicking the structure of
the codebase.

Each "files" sub-blob contains:

- The path to the required input source needed to run the simulation as
  described by that metadata.
- The format for that input source.
- The title and description of the sub-blob.
- The name of the properties sub-blob within the metadata which contains
  the validation information for the input source of this "files"
  sub-blob.

Template "files"-blob structure:

::

   "data_entry": {
     "title": "<title-optional>",
     "description": "<description-optional>",
     "path": "<path to the corresponding file>",
     "type": "<either csv or json>",
     "properties": {}
   }

Examples in action:

::

   "files": {
       "config": {
         "title": "Config Data",
         "description": "Configuration Information",
         "path": "input/data/config/multi_crop_config.json",
         "type": "json",
         "properties": "config_properties"
       },
       "animal": {
         "title": "Animal data",
         "description": "Animal module specification.",
         "path": "input/data/animal/no_animal.json",
         "type": "json",
         "properties": "animal_properties"
       },
   ...

Loading multiple properties files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``files`` blob includes a special ``properties`` entry that points
to JSON files containing validation rules for every other file entry.
This entry can reference a single file via ``path`` or multiple files via
``paths``. When multiple properties documents are supplied, Input Manager
loads them in order and merges the resulting dictionaries; if the same
property key appears in more than one file, the definition in the later
file overrides the earlier one. The Data Validator checks that the
``path``/``paths`` attribute is a non-empty string or list of strings
before loading begins and raises errors when a referenced file is missing
or malformed.

The default layout keeps these files beside the metadata file under
``input/metadata/properties``. A typical configuration combines base
rules with domain-specific extensions:

::

   "properties": {
     "title": "Metadata Properties",
     "description": "The properties of input data.",
     "paths": [
       "input/metadata/properties/default.json",
       "input/metadata/properties/commodity_properties.json"
     ],
     "type": "json",
     "properties": "NA"
   },

The "properties" blob
~~~~~~~~~~~~~~~~~~~~~

This second blob is also broken into sub-blobs. Each sub-blob contains
the validation guidelines for any input sources that use these set of
properties. Every input has to correspond to one properties sub-blob.
This enables the input's data to be validated and added to the
InputManager's data pool. As noted above, input sources can be files
(JSON or CSV) or API-payloads.

Within the "properties" blob sub-blobs, the following information is
available for each piece of data from the corresponding input:

- Data type (broken into 5 main types: number, string, array, boolean,
  object).
- Description of the field (currently optional but we want this field
  filled out whenever possible).
- Validation guidelines including maximum, minimum, pattern, default,
  maximum length, minimum length.

The template structure for a CSV formatted input source properties blob:

::

   "properties": {
     "column1-title": {
       "description": "<optional description for this column>",
       <data description template>
     }
   }

The template structure for a JSON formatted input source properties
blob:

::

   "properties": {
      "<var name>": {
       "type": "<an item from list:[number, array, bool, string, –what else?-]>" 
       "description": "<optional description for this variable>",
       <data description template>
      }
   }

Additionally the metadata supports the Object datatype. There is no
validation of the object type in and of itself. Each nested piece of
data within an object is expected to have its own validation guidelines
assuming it is not another object type.

The structure template for an object type in a JSON input source:

::

   "properties": {
      "<var name>": {
       "type": "object" 
       "description": "<optional description for this variable>",
        "<nested var name>": {
        "type": "<an item from list:[number, array, bool, string, –what else?-]>" 
        "description": "<optional description for this variable>",
        <data description template>
        }
      }
   }

Validation guidelines are present within each field within the
"properties" blob sub-blob. These guidelines inform InputManager how to
validate the data and whether the data being validated is critical or
non-critical.

Critical data are data without which the simulation cannot be
successfully run.

Critical data are distinguished by having a "default" field present in
the "properties" blob sub-blob. The "default" value is the value which
InputManager will replace the value given from the input source if that
value is determined to be invalid. Non-critical data will not have a
"default" field.

InputManager uses the other validation guidelines based on what type of
data it is. The metadata has been written such that the guidelines set
what ranges and patterns of values are known to be able to be handleable
by the RuFaS model. So a value from an input source that fails the
metadata validation guidelines will be flagged by InputManager.

+-----------+------------+------------+------------+------------+------------+
| data type | minimum    | maximum    | minimum    | maximum    | pattern    |
|           |            |            | length     | length     |            |
+===========+============+============+============+============+============+
| number    | applicable | applicable | N/A        | N/A        | N/A        |
+-----------+------------+------------+------------+------------+------------+
| string    | N/A        | N/A        | applicable | applicable | applicable |
+-----------+------------+------------+------------+------------+------------+
| array     | applicable | applicable | applicable | applicable | applicable |
|           | if element | if element | if element | if element | if element |
|           | is         | is         | is         | is         | is         |
|           | number\*   | number\*   | string\*   | string\*   | string\*   |
+-----------+------------+------------+------------+------------+------------+
| bool      | N/A        | N/A        | N/A        | N/A        | N/A        |
+-----------+------------+------------+------------+------------+------------+

\*We validate every single item within the array. Each item will be
routed to the corresponding data type validation of each element.
I.e.,if the element is a number, we check min and max.

Modifiability
^^^^^^^^^^^^^

The ``modifiability`` property indicates whether a variable is required
at initialization and whether it can be modified during runtime. The
``modifiability`` property is a string with three possible options
(enum):

- ``"required_and_locked"``: The variable must be included in the input
  file at initialization and cannot be modified during runtime.
- ``"required_and_unlocked"``: The variable must be included in the
  input file at initialization and can be modified during runtime.
- ``"not_required_and_unlocked"``: It is optional to include the
  variable in the input file at initialization, and it can be modified
  during runtime.

  - Note: If a variable with ``modifiability`` of
    ``"not_required_and_unlocked"`` is also included in the input, it
    will still be validated against the metadata (and fixed if needed
    and possible). If the ``modifiability`` of a variable is not
    specified, it will default to ``"not_required_and_unlocked"``.

Data Validation during Initialization
'''''''''''''''''''''''''''''''''''''

When validating the input data, the InputManager iterates all the
variables in the metadata. If a variable's value is not specified in the
input data, the InputManager will check its modifiability in the
metadata.

- If the variable is required upon initialization (modifiability set to
  ``"required_and_locked"`` or ``"required_and_unlocked"``), the
  InputManager will log an error to the OutputManager and raise a
  KeyError to terminate the simulation.
- If the variable is not required upon initialization (modifiability set
  to ``"not_required_and_unlocked"`` or no modifiability specified), the
  InputManager will log a warning to the OutputManager and continue the
  data validation process. The InputManager will attempt to fix the
  missing data later on in the process.

Adding data to pool during Runtime
''''''''''''''''''''''''''''''''''

When adding data to the InputManager variable pool during runtime, the
InputManager checks whether the variable is modifiable before taking any
action. If the variable is not modifiable during runtime (modifiability
set to ``"required_and_locked"``), the InputManager will refer to the
``eager_termination`` flag for further action:

- If the ``eager_termination`` flag is set to ``False``, the
  InputManager will log a warning to the OutputManager and continue the
  simulation without interruption.
- If the ``eager_termination`` flag is set to ``True``, the InputManager
  will log an error to the OutputManager and raise a PermissionError to
  terminate the simulation.

Examples of properties blobs in action:

::

   "manure_management_properties": {
         "manure_management_scenarios": {
           "type": "array",
           "description": "Manure Management Scenarios -- Add as many different manure scenarios as needed",
           "properties": {
             "type": "object",
             "scenario_id": {
               "type": "number",
               "description": "Scenario ID -- An identification number for livestock enclosures.",
               "modifiability": "required_and_locked",
               "minimum": 0
             },
             "bedding_type": {
               "type": "string",
               "description": "Bedding Type -- The material used for bedding pack.",
               "modifiability": "required_and_unlocked",
               "pattern": "^(Sand|Straw|Sawdust|Manure_solids|Other)$"
             },
             "manure_handler": {
               "type": "string",
               "description": "Manure Handling Method -- Method for cleaning barn alleyways.",
               "pattern": "^(flush system|alley scraper|manual scraping|tillage|manual skid steer scraping|harrowing)$"
             },
             "manure_separator": {
               "type": "string",
               "description": "Manure Separator Type -- The type of solid-liquid separator equipment to separate coarse fibrous solids/sand",
               "modifiability": "unrequired_and_unlocked",
               "pattern": "^(screw press|sand lane|rotary screen|none|other)$"
             },
             "manure_treatment_methods": {
               "type": "string",
               "description": "Manure Treatment Methods -- Select the Manure Treatment Methods.",
               "pattern": "^(slurry storage underfloor|slurry storage outdoor|open lots|compost bedded pack barn|anaerobic lagoon|anaerobic digestion|other)$"
             }
           }
         },

The "cross-validation" blob
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cross-validation enforces coherence across fields and files — ensuring that independently valid inputs also make sense when considered together. While individual-field validation in the properties blob can confirm that values are well-formed and within acceptable ranges, it cannot capture relationships between different parts of the input structure.

Cross-validation fills this gap by validating cross-field dependencies and system-level constraints. For example, verifying that the total number of stalls across all calf pens is at least as large as the number of calves divided by the maximum stocking density requires values from multiple parts of the input tree. These checks ensure that the overall configuration is not just syntactically valid, but operationally realistic and internally consistent, helping prevent subtle configuration errors that could lead to invalid or misleading simulation results.

The cross-validation configuration is stored in one or more standalone
JSON files (separate from the main metadata file). Each file contains a
top-level ``"cross_validation"`` key whose value is an array of
*validation blocks*.

Cross-validation file paths are registered in the metadata under a
dedicated ``cross_validation_file_paths`` entry. Input Manager loads
every file in that list and runs all blocks from all files in order.

Structure of a validation block
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each block has four top-level keys:

- ``description`` — human-readable label reported in error logs when
  the block fails.
- ``aliases`` — maps short local names (used inside this block) to
  actual data addresses or literal constant values.
- ``apply_when`` *(optional)* — an array of condition clauses that
  act as a guard: if any clause is not satisfied the entire block is
  skipped and counted as passing.
- ``rules`` — an array of condition clauses that must all be satisfied
  for the block to pass.

Template:

::

   {
     "description": "<human-readable label>",
     "aliases": {
       "variables": {
         "<alias>": "<dot-separated address in IM pool>"
       },
       "constants": {
         "<alias>": <literal value>
       }
     },
     "apply_when": [ <condition clause>, ... ],
     "rules":      [ <condition clause>, ... ]
   }


Aliases
'''''''

The ``aliases`` block populates a local *alias pool* used only while
evaluating cross validation rules. It has two optional sub-keys:

- ``variables`` — a mapping of alias name → dot-separated address.
  Input Manager resolves each address against the IM data pool (the
  same pool used by ``get_data()``) and stores the result under the
  alias name.
- ``constants`` — a mapping of alias name → literal value (number,
  string, boolean). No pool lookup is performed; the literal is stored
  as-is.

Only the keys ``variables`` and ``constants`` are accepted; any other
key in ``aliases`` is treated as an error.


Condition clauses
'''''''''''''''''

Both ``apply_when`` entries and ``rules`` entries are *condition
clauses*. A condition clause compares a left-hand expression to a
right-hand expression using a relationship operator:

::

   {
     "left_hand":  <expression block>,
     "right_hand": <expression block>,
     "relationship": "<operator>"
   }

Supported relationship operators:

+-------------------------+-----------------------------------------------+
| Operator                | Meaning                                       |
+=========================+===============================================+
| ``equal``               | LHS == RHS (pairwise when both are lists)     |
+-------------------------+-----------------------------------------------+
| ``not_equal``           | LHS != RHS                                    |
+-------------------------+-----------------------------------------------+
| ``greater``             | LHS > RHS (pairwise when both are lists)      |
+-------------------------+-----------------------------------------------+
| ``greater_or_equal_to`` | LHS >= RHS (pairwise when both are lists)     |
+-------------------------+-----------------------------------------------+
| ``is_of_type``          | All LHS values match the type string in RHS   |
|                         | (``"string"``, ``"integer"``, ``"float"``,    |
|                         | ``"boolean"``, ``"number"``)                  |
+-------------------------+-----------------------------------------------+
| ``is_null``             | All LHS values are ``None``                   |
+-------------------------+-----------------------------------------------+
| ``regex``               | LHS value fully matches the RHS regex pattern |
+-------------------------+-----------------------------------------------+
| ``is_equal_length``     | LHS and RHS are lists of the same length      |
+-------------------------+-----------------------------------------------+

When both sides resolve to lists of equal length, comparison operators
(``equal``, ``not_equal``, ``greater``, ``greater_or_equal_to``) are
applied pairwise and every pair must pass.

Expression blocks
'''''''''''''''''

Each of ``left_hand`` and ``right_hand`` is an *expression block*.
Exactly one of the following sub-block types must be present:

**aggregation** — resolves one or more aliases from the pool and
applies an operation.

::

   {
     "aggregation": {
       "operation": "<op>",
       "operands":  ["<alias>", ...],
       "mode":      "<element_wise | aggregate>"
     },
     "save_as": "<alias>"
   }

- ``operands`` — non-empty list of alias names to resolve.
- ``operation`` — aggregation function to apply. Supported operations:
  ``"no_op"`` (pass through), ``"sum"``, ``"division"``. When
  ``operands`` contains more than one entry, ``operation`` must be
  provided and cannot be ``"no_op"``.
- ``mode`` — required when any resolved operand is a list or dict:

  - ``"element_wise"`` — return the resolved values as-is, one per
    element.
  - ``"aggregate"`` — apply the operation across all elements and
    return a single result.

**for_each** — iterates over a list of dicts in the alias pool and
either filters entries or enforces a condition on every entry.

::

   {
     "for_each": {
       "in":               "<alias for list[dict]>",
       "field":            "<key within each dict to evaluate>",
       "value_to_compare": "<alias for scalar comparand>",
       "field_to_compare": "<key within each dict used as comparand>",
       "relationship":     "<operator>",
       "mode":             "<filter | enforce>"
     },
     "save_as": "<alias>"
   }

- ``in`` — alias that resolves to a ``list`` of ``dict`` objects.
- ``field`` — the dict key whose value is the left-hand comparand for
  each entry.
- Exactly one of ``value_to_compare`` or ``field_to_compare`` must be
  provided:

  - ``value_to_compare`` — alias resolved once from the pool; the same
    value is used as the right-hand comparand for every entry.
  - ``field_to_compare`` — key read from each entry at comparison time.

- ``relationship`` — one of the supported operators listed above.
- ``mode``:

  - ``"filter"`` — returns the subset of entries that satisfy the
    condition.
  - ``"enforce"`` — returns ``[True]`` when all entries satisfy the
    condition, otherwise ``[False]``.

**save_as** (optional, applies to both block types)

If ``"save_as"`` is present on an expression block, the result of that
expression is written back into the local alias pool under the given
name. This allows a computed intermediate value to be referenced by
subsequent expressions within the same block.

::

   "right_hand": {
     "aggregation": {
       "operation": "division",
       "operands": ["number_of_calves", "pen_stocking_density"]
     },
     "save_as": "min_num_stalls"
   }

The ``apply_when`` guard
''''''''''''''''''''''''

When ``apply_when`` is present, Input Manager evaluates every clause in
the array before running the ``rules``. If any ``apply_when`` clause is
*not* satisfied, the entire block is skipped and treated as passing.
This is useful for blocks whose rules only make sense under specific
conditions — for example, a rule that applies only when a pen's animal
type is ``"CALF"``.

::

   "apply_when": [
     {
       "left_hand": {
         "aggregation": { "operation": "no_op", "mode": "aggregate",
                          "operands": ["pen_animal_type"] }
       },
       "right_hand": {
         "aggregation": { "operation": "no_op", "mode": "element_wise",
                          "operands": ["calf_pen_type"] }
       },
       "relationship": "equal"
     }
   ]

Error behaviour and ``eager_termination``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When a block's rules fail, Input Manager records the block's
``description`` in a list of failures. Two termination modes control
what happens next:

- **Eager termination on** (normal simulation): the first failing rule
  inside a block stops evaluation of that block immediately. The first
  failing block stops evaluation of the entire ruleset.
- **Eager termination off** (``-ov`` mode): all rules in all blocks are
  evaluated. At the end, if any block failed, Input Manager logs all
  failing block descriptions and returns ``False``.

In both modes, ``apply_when`` failures are silent — they mean "this
block does not apply" and are always counted as passing.

Full example
^^^^^^^^^^^^

The following example checks that the total number of stalls in all
calf pens is sufficient to hold every calf at the configured maximum
stocking density. The ``apply_when`` guard ensures the rule is skipped
if the first pen is not a calf pen:

::

   {
     "description": "Number of stalls in calf pen",
     "aliases": {
       "variables": {
         "number_of_calves":    "animal.herd_information.calf_num",
         "pen_animal_type":     "animal.pen_information.0.animal_combination",
         "pen_stall_num":       "animal.pen_information.0.number_of_stalls",
         "pen_stocking_density":"animal.pen_information.0.max_stocking_density"
       },
       "constants": {
         "calf_pen_type": "CALF"
       }
     },
     "apply_when": [
       {
         "left_hand":  { "aggregation": { "operation": "no_op",
                          "mode": "aggregate", "operands": ["pen_animal_type"] } },
         "right_hand": { "aggregation": { "operation": "no_op",
                          "mode": "element_wise", "operands": ["calf_pen_type"] } },
         "relationship": "equal"
       }
     ],
     "rules": [
       {
         "left_hand":  { "aggregation": { "operation": "sum",
                          "mode": "aggregate", "operands": ["pen_stall_num"] } },
         "right_hand": { "aggregation": { "operation": "division",
                          "mode": "element_wise",
                          "operands": ["number_of_calves", "pen_stocking_density"] },
                         "save_as": "min_num_stalls" },
         "relationship": "greater_or_equal_to"
       }
     ]
   }

Decision-tree flow diagram
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. mermaid:: /_static/cross_validation_flow.mmd
   :zoom:



.. |RuFaS Overview - IM| image:: https://github.com/RuminantFarmSystems/RuFaS/assets/70217952/33d2952d-a49e-4cbd-b2d8-798a0ea69dcc
.. |Input Manager Data Validation Overview| image:: https://github.com/RuminantFarmSystems/RuFaS/assets/70217952/064328ad-eeda-4936-91a7-a026ace4fbf3
