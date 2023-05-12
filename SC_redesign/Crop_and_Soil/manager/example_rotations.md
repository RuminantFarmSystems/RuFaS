# Introduction

This document is meant to outline how the `CropInput` system should work. 

The input data is parsed and used to create a `CropScheduleSpec`, which determines how a crop should be scheduled
in a field, and `CropRotation` which is a container for multiple `CropScheduleSpec`s. The `CropRotation` class should
be created when `Field`s are initialized and each field should have their own component `CropRotation`. 

## Scheduling an individual crop practice

The `CropScheduleSpec` class is a dataclass that contains the specifications of the timings of management practices
concerning the planting and harvesting of individual crops. The specification of this class should be flexible and 
allow for different types of patterns. 

Below are examples for how crop management might be specified.

#### Example 1: 
A user wants to plant an instance of "corn" every year for 4 years starting in 1990. The planting and harvest
events should always take place on the same of the year. The following call to `CropScheduleSpec` should work:

```python
from SC_redesign.Crop_and_Soil.manager.crop_rotation import CropScheduleSpec

all_corn = CropScheduleSpec(crop_reference="corn", planting_years=1990, planting_days=120,
                            harvest_years=1990, harvest_days=220, pattern_repeat=3)
print(all_corn.planting_years)  # (1990, 1991, 1992, 1993)
print(all_corn.harvest_years)  # (1990, 1991, 1992, 1993)
```

#### Example 2: 
This time, the user wants to plant an instance of "corn" every other year, for 6 years, starting in 1990

```python
from SC_redesign.Crop_and_Soil.manager.crop_rotation import CropScheduleSpec

skipped_corn = CropScheduleSpec(crop_reference="corn", planting_years=1990, planting_days=120,
                                harvest_years=1990, harvest_days=220, pattern_repeat=3,
                                pattern_skip=1)
print(skipped_corn.planting_years)  # (1990, 1992, 1994, 1996)
print(skipped_corn.harvest_years)  # (1990, 1992, 1994, 1996)
```

#### Example 3: 
A user may also want to use a more complex pattern. Here, they'll plant two years in a row, skip a year, 
plant 3 years in a row, and then skip 2 years before starting over. The calendar days for planting and harvesting are 
different for each step. This will repeat one time after the first cycle:

```python
from SC_redesign.Crop_and_Soil.manager.crop_rotation import CropScheduleSpec

odd_pattern = CropScheduleSpec(crop_reference="corn",
                               planting_years=(1990, 1991, 1993, 1994, 1995),
                               planting_days=(115, 120, 120, 108, 130),
                               harvest_years=(1990, 1991, 1993, 1994, 1995),
                               harvest_days=(220, 222, 220, 230, 220),
                               pattern_repeat=1, pattern_skip=2)
print(odd_pattern.planting_years)  # (1990, 1991, 1993, 1994, 1995, 1998, 1999, 2001, 2002, 2003)
print(odd_pattern.planting_days)  # (115, 120, 120, 108, 130, 115, 120, 120, 108, 130)
print(odd_pattern.harvest_years)  # (1990, 1991, 1993, 1994, 1995, 1998, 1999, 2001, 2002, 2003)
print(odd_pattern.harvest_days)  # (220, 222, 220, 230, 220, 220, 222, 220, 230, 220)
```

#### Example 4: 
Some crops may be harvested and allowed to regrow multiple times after a single planting. In this example, 
alfalfa is harvested for 3 years after it is planted and then a rest year is given. On the final harvest, the crop is 
killed.

```python
from SC_redesign.Crop_and_Soil.manager.crop_rotation import CropScheduleSpec

alf_spec = CropScheduleSpec(crop_reference="alfalfa",
                            planting_years=1990,
                            planting_days=120,
                            harvest_years=([1990, 1991, 1992]),
                            harvest_days=220,
                            harvest_operations=(["no_kill", "no_kill", "default"]),
                            pattern_skip=1, pattern_repeat=2)
# TODO: Note that this does not yet work with the current CropScheduleSpec. Below is the *desired* output
print(alf_spec.planting_years)  # (1990, 1994, 1998)
print(alf_spec.planting_days)  # (120, 120, 120)
print(alf_spec.harvest_years)  # ([1990, 1991, 1992], [1994, 1995, 1996], [1998, 1999, 2000])
print(alf_spec.harvest_days)  # ([220, 220, 220], [220, 220, 220], [220, 220, 220])
print(alf_spec.harvest_operations)  # (["no_kill", "no_kill", "default"], ["no_kill", "no_kill", "default"], ["no_kill", "no_kill", "default"])
```

#### Example 5: 
In addition to scheduled harvesting, users should also be able to specify that harvest day should be
determined within the model, based on optimal growth conditions. This specification is identical to the previous
alfalfa specification, except harvest days are not given. Instead, we tell the input manager to use heat unit
scheduling to determine the optimal harvest date(s) for any given event:

```python
from SC_redesign.Crop_and_Soil.manager.crop_rotation import CropScheduleSpec

optimal_alf = CropScheduleSpec(crop_reference="alfalfa",
                               planting_years=1990,
                               planting_days=120,
                               harvest_years=([1990, 1991, 1992]),
                               use_optimal_harvest=True,
                               harvest_operations=(["no_kill", "no_kill", "default"]),
                               pattern_skip=1, pattern_repeat=2)
```

#### Example 6: 
The current design of `CropScheduleSpec` uses tuples. But examples 4 and 5 may make that an unfeasible structure.
It seems that numpy arrays will be the best to use here. In this way, we can always ensure that the final 
`planting_years`, `planting_days`, `harvest_years`, `harvest_days`, and `harvest_operation` arrays 
(after `__post_init__`) are always the same length. The individual elements of the arrays may not be the same length.
For example, if we plant alfalfa once and harvest it 3 times, we only need 1 instance of `Alfalfa`. This means 
that our arrays should be length 1. However, our harvest arrays need to have 3 sub-elements. 

The example below shows a situation that uses variable harvest. Here we have two alfalfa instances. The first is 
planted in 1990 and is harvested 3 times (on the same day each harvest). The second alfalfa is planted in 1994 and is 
harvested only once (on a different day from the previous year). Note that the arrays should all be length 2, but 
the harvest sub-arrays for the first alfalfa instance are length 3 while the second sub-array is length 1.

```python
from SC_redesign.Crop_and_Soil.manager.crop_rotation import CropScheduleSpec

new_alf = CropScheduleSpec(crop_reference="alfalfa",
                           planting_years=(1990, 1994),
                           planting_days=120,
                           harvest_years=([1990, 1991, 1992], 1994),
                           harvest_days=(220, 199),
                           harvest_operations=(["no_kill", "no_kill", "default"], "default"))
# TODO: Note that this does not yet work with the current CropScheduleSpec. Below is the *desired* output
print(new_alf.planting_years)  # (1990, 1994)
print(new_alf.planting_days)  # (120, 120)
print(new_alf.harvest_years)  # ([1990, 1991, 1992], 1994)
print(new_alf.harvest_days)  # ([220, 220, 220], 199)
```

#### Example 7
Note that users can also just explicitly specify their dates without using any patterns. The following code should 
produce identical results to Example 3 above.

```python
from SC_redesign.Crop_and_Soil.manager.crop_rotation import CropScheduleSpec

odd_pattern = CropScheduleSpec(crop_reference="corn",
                               planting_years=(1990, 1991, 1993, 1994, 1995, 1998, 1999, 2001, 2002, 2003),
                               planting_days=(115, 120, 120, 108, 130, 115, 120, 120, 108, 130),
                               harvest_years=(1990, 1991, 1993, 1994, 1995, 1998, 1999, 2001, 2002, 2003),
                               harvest_days=(220, 222, 220, 230, 220, 220, 222, 220, 230, 220))
print(odd_pattern.planting_years)  # (1990, 1991, 1993, 1994, 1995, 1998, 1999, 2001, 2002, 2003)
print(odd_pattern.planting_days)  # (115, 120, 120, 108, 130, 115, 120, 120, 108, 130)
print(odd_pattern.harvest_years)  # (1990, 1991, 1993, 1994, 1995, 1998, 1999, 2001, 2002, 2003)
print(odd_pattern.harvest_days)  # (220, 222, 220, 230, 220, 220, 222, 220, 230, 220)
```

## Scheduling an entire rotation practice

The `CropRotation` class is a dataclass that contains the specifications of timing practices for multiple crops 
that will be cycled on the field (i.e., a rotation). As such, a `CropRotation` is comprised of various 
`CropScheduleSpec` objects.

#### Example 1:

A common rotation is one year of corn, followed by 3 years of alfalfa. Only one planting event is needed for the 
perennial alfalfa. An example of this rotation might be:

```python
from SC_redesign.Crop_and_Soil.manager.crop_rotation import CropScheduleSpec, CropRotation

corn_spec = CropScheduleSpec(crop_reference="corn", planting_years=1990, planting_days=120, harvest_years=1990,
                             harvest_days=240, harvest_operations="default",
                             pattern_skip=3, pattern_repeat=2)
alf_spec = CropScheduleSpec(crop_reference="alfalfa", planting_years=1991, planting_days=120,
                            harvest_years=([1991, 1992, 1993]), harvest_days=240,
                            harvest_operations=(["no_kill", "no_kill", "default"]),
                            pattern_skip=1, pattern_repeat=2)
rotation = CropRotation([corn_spec, alf_spec])
# TODO: Note that this is not yet implemented. Below is the *desired* output
print(rotation.planting_years)  # {"corn": (1990, 1994, 1998), "alfalfa: (1991, 1995, 1999)}
print(
    rotation.harvest_years)  # {"corn": (1990, 1994, 1998), "alfalfa": ([1991, 1992, 1993], [1995, 1996, 1997], [1999, 2000, 2001])}
```

#### Example 2

RuFaS has a set of supported crops, with default values, but users may also want to define their own custom crops. In
this example, we use the same rotation as above, except the first year uses a user-defined "field_corn" (not shown).
The details of how to create the user-defined crop should occur in a separate input field, but can be referenced here:

```python
from SC_redesign.Crop_and_Soil.manager.crop_rotation import CropScheduleSpec, CropRotation

fc_spec = CropScheduleSpec(crop_reference="field_corn", planting_years=1990, planting_days=120, harvest_years=1990,
                           harvest_days=240, harvest_operations="default",
                           pattern_repeat=0)
corn_spec = CropScheduleSpec(crop_reference="corn", planting_years=1994, planting_days=120, harvest_years=1990,
                             harvest_days=240, harvest_operations="default",
                             pattern_skip=3, pattern_repeat=1)
alf_spec = CropScheduleSpec(crop_reference="alfalfa", planting_years=1991, planting_days=120,
                            harvest_years=([1991, 1992, 1993]), harvest_days=240,
                            harvest_operations=(["no_kill", "no_kill", "default"]),
                            pattern_skip=1, pattern_repeat=2)
rotation = CropRotation([corn_spec, alf_spec])
# TODO: Note that this is not yet implemented. Below is the *desired* output
print(rotation.planting_years)  # {"field_corn": (1990), "corn": (1994, 1998), "alfalfa: (1991, 1995, 1999)}
print(
    rotation.harvest_years)  # {"field_corn": (1990), "corn": (1994, 1998), "alfalfa": ([1991, 1992, 1993], [1995, 1996, 1997], [1999, 2000, 2001])}
```

#### Common rotations
Some common rotations (`CommonRotations`), like the ones mentioned above could be further simplified by giving the 
name and some basic parameters of the common rotation.

For example, the following code could produce the rotation from example 2 above:

```python
from SC_redesign.Crop_and_Soil.manager.crop_rotation import CropRotation

CropRotation.make_common_rotation(rotation_name="corn_alfala_a", start_date=1990, repeat=2)
```

## User input

Here, I will lay out a few templates for how users could specify crop management input. For the sake of this document,
I will use dictionaries. 

#### Approach #1

```python
input_one = {
    "field_specifications": {"A": {"lat": 44.5, "long": -89.5, "area": 1000, "crop_rotation": "rot_a"},
                             "B": {"lat": 44.52, "long": -89.15, "area": 900, "crop_rotation": "rot_b"},
                             "field_3": {"lat": 44.65, "long": -89.51, "area": 700, "crop_rotation": "rot_a"}
                             },
    "crop_management_specifications": {
        "rotations": {
            "rot_a": ("corn_a", "alfalfa_a"),
            "rot_b": ("fc_a", "alfalfa_a", "corn_b")
        },
        "schedule_specs": {
            "corn_a": {"crop_reference": "corn", "planting_years": 1990, "planting_days": 118, "harvest_years": 1990,
                       "harvest_days": 240, "harvest_operations": "default", 
                       "pattern_skip": 3, "pattern_repeat": 2},
            "fc_a": {"crop_reference": "field_corn", "planting_years": 1990, "planting_days": 118, 
                     "harvest_years": 1990, "harvest_operations": "default", "pattern_repeat": 0},
            "corn_b": {"crop_reference": "corn", "planting_years": 1994, "planting_days": 118, "harvest_years": 1994,
                       "harvest_days": 220, "harvest_operations": "default", "pattern_repeat": 1}, 
            "alfalfa_a": {"crop_reference": "alfalfa", "planting_years": 1991, "planting_days": 120,
                          "harvest_years": ([1991, 1992, 1993]), "harvest_days": 220,
                          "harvest_operations": (["no_kill", "no_kill", "default"]),
                          "pattern_skip": 1, "pattern_repeat": 2}
        }
    },
    "crop_customization": {
        "field_corn": {"species": "corn", "minimum_temperature": 5.0, "light_use_efficiency": 43.0}}
}
```

This particular input indicates that there are 3 fields in this farm (named "A", "B", and "field_3") and the fields 
will use the user-defined crop rotations "rot_a", "rot_b", and "rot_a" respectively (note that "rot_a" is used for two 
of the fields). 

The first rotation (named "rot_a") starts in 1990 and begins with corn, which is planted on the 118th day of
the year and harvested later that year on day 240. The year after the corn is harvested, alfalfa is planted on the 
118th day. That alfalfa is harvested for three years on day 220. This cycle is then repeated two more times 
(i.e., corn, alfalfa, alfalfa, alfalfa, corn, alfalfa, alfalfa, alfalfa, corn, alfalfa, alfalfa, alfalfa). This 
rotation is used by field `"A"` and `"field_3"`, according to the `"field_specifications"` entry.

Field `"B"` uses the second rotation (named "rot_b") which is slightly different. Here, we have a custom crop called
`"field_corn"` planted in 1990, followed by the same 3 years of alfalfa as in "rot_a". Then, after the last year of
alfalfa is harvested, default corn is again planted and the cycle between default corn and alfalfa is repeated:
(i.e., field_corn, alfalfa, alfalfa, alfalfa, corn, alfalfa, alfalfa, alfalfa, corn, alfalfa, alfalfa, alfalfa).
Note that since `"field_corn"` is not one of the supported crops, the user configures it in the `"crop_customization"`
input section. The format of this input mirrors a call to `CropSpeciesDataFactory.create_species_data()`.
