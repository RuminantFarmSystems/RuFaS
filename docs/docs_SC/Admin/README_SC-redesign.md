## Contents
1. [Introduction](#introduction)
2. [Directory Structure](#directory-structure)

---

## Introduction 

The [SC_redesign](.) **folder** (of the `SC_redesign` **branch**) is a temporary directory that houses the redesigned 
and restructured Crop and Soil module (SC). This folder exists so that the SC can be fully rewritten in a way 
that better aligns with the goals and standards of the RuFaS team. The folder allows the rewrite to take place
independently of the rest of the RuFaS codebase so as not to affect the model until the new SC is completed.

---

## Directory Structure

The [SC_redesign](.) folder contains:
* This README file
* An [__init__.py](./__init__.py) file, which tells python to treat this folder as a module where code is stored.
* The code directory, [Crop_and_Soil](./Crop_and_Soil), which contains all the updated code for the SC module, 
organized into sub-folders corresponding to the SC submodules. 
* The documentation directory, [docs_SC](./docs_SC), which contains text-based documentation about the module, 
including model-level documentation as well as goals and plans.

Once the new SC is finished, the full [Crop_and_Soil](./Crop_and_Soil) folder can be moved back into
[RUFAS/routines/](../RUFAS/routines) to replace the current module (i.e., the [field](../RUFAS/routines/field) folder).

### Code directory

[Crop_and_Soil](./Crop_and_Soil) is a python module directory for the SC of the RuFaS model. In addition to the 
requisite [__init__.py](./Crop_and_Soil/__init__.py) file, it is organized into 5 sub-folders:

1. [crop](./Crop_and_Soil/crop): contains code pertaining to crops grown in fields. The main classes are
`Crop` ([crop.py](./Crop_and_Soil/crop/crop.py)) and `CropData` ([crop_data.py](./Crop_and_Soil/crop/crop_data.py)).
Together, these classes represent a crop growing in a field. The other python files contain supporting classes 
representing growth processes or model configuration.
2. [soil](./Crop_and_Soil/soil): contains code pertaining to the soil that resides in the fields. The main classes 
**will be** `Soil` ([soil.py](./Crop_and_Soil/soil/soil.py)) and `SoilData` 
([soil_data.py](./Crop_and_Soil/soil/soil_data.py)). Together, these classes represent a soil profile of 
a single agricultural field. Other files contain supporting classes. <!-- TODO: Update when soil complete -->
3. [field](./Crop_and_Soil/field): contains code pertaining to the individual fields that make up an agricultural farm.
The main classes will be `Field` ([field.py](./Crop_and_Soil/field/field.py)) and `FieldData` 
([field_data.py](./Crop_and_Soil/field/field_data.py)). Together, these classes represent a single field that will 
contain soil and crops. Other files contain supporting classes. <!-- TODO: Update when field complete --> 
4. [manager](./Crop_and_Soil/manager): contains code pertaining to the management of agricultural farms and fields. The
main class will be `FieldManager` ([field_manger.py](./Crop_and_Soil/manager/field_manager.py)) and a configuration
class. Other files will contain support classes. <!-- TODO: Update when manager complete -->
5. [tests_SC](./Crop_and_Soil/tests_SC): contains all tests (using the `pytest` framework) of the SC module. Each file
in this test directory corresponds to a code file. Every file should have a corresponding test and every component
of the file (classes, functions, etc.) should have tests associated with them.

For more details about the SC module design, see [road-map_soil-and-crop.md](./docs_SC/admin/road-map_soil-and-crop.md) 
and [functionality-requirements.md](./docs_SC/admin/functionality-requirements.md).

### Documentation directory

[docs_SC](./docs_SC) is not a python module, but is simply a folder that contains the documentation for the SC module.
This directory is divided into two main sub-folders:

1. [model_docs](./docs_SC/model_docs): contains the high-level descriptions of the SC model components. The files 
contained within this directory are destined to become the wiki files for the SC module. The main document,
containing the overall summary is [Crop_and_Soil.md](./docs_SC/model_docs/Crop_and_Soil.md).
2. [admin](./docs_SC/admin): contains documents pertaining to the design and structure of the SC module. Examples of
the types of files to be included here are: documents that describe the goals or plans for the module, design principles,
tasks and checklists, required and desired functionality of the module, etc. The primary document of interest (at the
time of this writing) is the [road-map_soil-and-crop.md](./docs_SC/admin/road-map_soil-and-crop.md) file.

---