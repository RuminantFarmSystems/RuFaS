Authors: Clay Morrow, Ed Hansen  
Date last edited: 5/31/2023

# Introduction

This document is meant to outline how the `FieldManager` will handle the scheduling of crop plantings and harvestings. 

The input data is parsed and used to create a `CropSchedule`, which determines how a crop should be scheduled
in a field. From that `CropSchedule` two lists of `Event`s will be created, a list of `PlantingEvent`s and a list of 
`HarvestEvent`s. 

## Scheduling an individual crop practice

The `CropSchedule` class is a dataclass that contains the specifications of the timings of management practices
concerning the planting and harvesting of individual crops. The specification of this class should be flexible and 
allow for different types of patterns. 

Below are examples for how crop management might be specified.

#### Example 1: 
A user wants to plant an instance of "corn" every year for 4 years starting in 1990. The planting and harvest
events should always take place on the same of the year. The following call to `CropSchedule` should work:

```python
from SC_redesign.Crop_and_Soil.manager.crop_schedule import CropSchedule

all_corn = CropSchedule(crop_reference="corn", planting_years=1990, planting_days=120,
                            harvest_years=1990, harvest_days=220, pattern_repeat=3)
print(all_corn.planting_years)  # (1990, 1991, 1992, 1993)
print(all_corn.harvest_years)  # (1990, 1991, 1992, 1993)
```

#### Example 2: 
This time, the user wants to plant an instance of "corn" every other year, for 6 years, starting in 1990

```python
from SC_redesign.Crop_and_Soil.manager.crop_schedule import CropSchedule

skipped_corn = CropSchedule(crop_reference="corn", planting_years=1990, planting_days=120,
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
from SC_redesign.Crop_and_Soil.manager.crop_schedule import CropSchedule

odd_pattern = CropSchedule(crop_reference="corn",
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
from SC_redesign.Crop_and_Soil.manager.crop_schedule import CropSchedule

alf_spec = CropSchedule(crop_reference="alfalfa",
                            planting_years=1990,
                            planting_days=120,
                            harvest_years=([1990, 1991, 1992]),
                            harvest_days=220,
                            harvest_operations=(["no_kill", "no_kill", "default"]),
                            pattern_skip=1, pattern_repeat=2)
# TODO: Note that this does not yet work with the current CropSchedule. Below is the *desired* output
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
from SC_redesign.Crop_and_Soil.manager.crop_schedule import CropSchedule

optimal_alf = CropSchedule(crop_reference="alfalfa",
                               planting_years=1990,
                               planting_days=120,
                               harvest_years=([1990, 1991, 1992]),
                               use_heat_scheduling=True,
                               harvest_operations=(["no_kill", "no_kill", "default"]),
                               pattern_skip=1, pattern_repeat=2)
```

#### Example 6
Note that users can also just explicitly specify their dates without using any patterns. The following code should 
produce identical results to Example 3 above.

```python
from SC_redesign.Crop_and_Soil.manager.crop_schedule import CropSchedule

odd_pattern = CropSchedule(crop_reference="corn",
                               planting_years=(1990, 1991, 1993, 1994, 1995, 1998, 1999, 2001, 2002, 2003),
                               planting_days=(115, 120, 120, 108, 130, 115, 120, 120, 108, 130),
                               harvest_years=(1990, 1991, 1993, 1994, 1995, 1998, 1999, 2001, 2002, 2003),
                               harvest_days=(220, 222, 220, 230, 220, 220, 222, 220, 230, 220))
print(odd_pattern.planting_years)  # (1990, 1991, 1993, 1994, 1995, 1998, 1999, 2001, 2002, 2003)
print(odd_pattern.planting_days)  # (115, 120, 120, 108, 130, 115, 120, 120, 108, 130)
print(odd_pattern.harvest_years)  # (1990, 1991, 1993, 1994, 1995, 1998, 1999, 2001, 2002, 2003)
print(odd_pattern.harvest_days)  # (220, 222, 220, 230, 220, 220, 222, 220, 230, 220)
```

## User input

Here, a few templates for how users could specify crop management input are laid out. For the sake of this document, 
dictionaries are used. 

#### Approach #1

```python
input_one = {
    "field_specifications": {"A": {"lat": 44.5, "long": -89.5, "area": 1000, "crop_schedules": ("corn_a", "alfalfa_a")},
                             "B": {"lat": 44.52, "long": -89.15, "area": 900, "crop_schedules": ("fc_a", "alfalfa_a", "corn_b")},
                             "field_3": {"lat": 44.65, "long": -89.51, "area": 700, "crop_schedules": ("corn_a", "alfalfa_a")}
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
    },
    "crop_customization": {
        "field_corn": {"species": "corn", "minimum_temperature": 5.0, "light_use_efficiency": 43.0}}
}
```

This particular input indicates that there are 3 fields in this farm (named "A", "B", and "field_3") and the fields 
will use some combination of the user-defined crop schedules. 

For field `"A"`, the combination of the `"corn_a"` and `"alfalfa_a"` schedules means that planting in the field starts 
in 1990 and begins with corn, which is planted on the 118th day of the year and harvested later that year on day 240. 
The year after the corn is harvested, alfalfa is planted on the 118th day. That alfalfa is harvested for three years on
day 220. This cycle is then repeated two more times (i.e., corn, alfalfa, alfalfa, alfalfa, corn, alfalfa, alfalfa, 
alfalfa, corn, alfalfa, alfalfa, alfalfa).

For field `"B"`, the combination of `"fc_a"`, `"alfalfa_a"`, and `"corn_b"`. Here, we have a custom crop called
`"field_corn"` planted in 1990, followed by the same 3 years of alfalfa. Then, after the last year of
alfalfa is harvested, default corn is again planted and the cycle between default corn and alfalfa is repeated:
(i.e., field_corn, alfalfa, alfalfa, alfalfa, corn, alfalfa, alfalfa, alfalfa, corn, alfalfa, alfalfa, alfalfa).
Note that since `"field_corn"` is not one of the supported crops, the user configures it in the `"crop_customization"`
input section. The format of this input mirrors a call to `CropSpeciesDataFactory.create_species_data()`.

Also note field specifications are not fully filled in. 
