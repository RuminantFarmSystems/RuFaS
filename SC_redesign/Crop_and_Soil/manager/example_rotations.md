# Introduction

This document is meant to outline how the CropInput system should work. 

## Scheduling an individual crop practice

The `CropScheduleSpec` class is a dataclass that contains the specifications of the timings of management practices
concerning the planting and harvesting of individual crops. The specification of this class should be flexible and allow
for different types of patterns. 

#### Example 1: A user wants to plant an instance of "corn" every year for 4 years starting in 1990. The planting and harvest
events should always take place on the same of the year. The following call to `CropScheduleSpec` should work:

```python
from SC_redesign.Crop_and_Soil.manager.crop_input import CropScheduleSpec
all_corn = CropScheduleSpec(crop_reference="corn", planting_years=1990, planting_days=120, 
                            harvest_years=1990, harvest_days=220, pattern_repeat=3)
print(all_corn.planting_years)  # (1990, 1991, 1992, 1993)
print(all_corn.harvest_years)  # (1990, 1991, 1992, 1993)
```

#### Example 2: This time, the user wants to plant an instance of "corn" every other year, for 6 years, starting in 1990

```python
from SC_redesign.Crop_and_Soil.manager.crop_input import CropScheduleSpec
skipped_corn = CropScheduleSpec(crop_reference="corn", planting_years=1990, planting_days=120, 
                                harvest_years=1990, harvest_days=220, pattern_repeat=3,
                                pattern_skip=1)
print(skipped_corn.planting_years)  # (1990, 1992, 1994, 1996)
print(skipped_corn.harvest_years)  # (1990, 1992, 1994, 1996)
```

#### Example 3: A user may also want to use a more complex pattern. Here, they'll plant two years in a row, skip a year, 
plant 3 years in a row, and then skip 2 years before starting over. The calendar days for planting and harvesting are 
different for each step. This will repeat one time after the first cycle:

```python
from SC_redesign.Crop_and_Soil.manager.crop_input import CropScheduleSpec
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

#### Example 4: Some crops may be harvested and allowed to regrow multiple times after a single planting. In this example, 
alfalfa is harvested for 3 years after it is planted and then a rest year is given. On the final harvest, the crop is killed.

```python
from SC_redesign.Crop_and_Soil.manager.crop_input import CropScheduleSpec
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

#### Example 5: In addition to scheduled harvesting, users should also be able to specify that harvest day should be
determined within the model, based on optimal growth conditions. This specification is identical to the previous
alfalfa specification, except harvest days are not given. Instead, we tell the input manager to use heat unit
scheduling to determine the optimal harvest date(s) for any given event:

```python
from SC_redesign.Crop_and_Soil.manager.crop_input import CropScheduleSpec
optimal_alf = CropScheduleSpec(crop_reference="alfalfa", 
                               planting_years=1990, 
                               planting_days=120,
                               harvest_years=([1990, 1991, 1992]),                            
                               use_optimal_harvest = True, 
                               harvest_operations=(["no_kill", "no_kill", "default"]),
                               pattern_skip=1, pattern_repeat=2)
```

#### Example 6: The current design of `CropScheduleSpec` uses tuples. But examples 4 and 5 may make that an unfeasible structure.
It seems that numpy arrays will be the best to use here. In this way, we can always ensure that the final 
`planting_years`, `planting_days`, `harvest_years`, `harvest_days`, and `harvest_operation` arrays 
(after `__post_init__`) are always the same length. The individual elements of the arrays may not be the same length.
For example, if we plant alfalfa once and harvest it 3 times, we only need 1 instance of `Alfalfa`. This means 
that our arrays should be length 1. However, our harvest arrays need to have 3 sub-elements. 

The example below shows a situation that uses variable harvest. Here we have two alfalfa instances. The first is planted
in 1990 and is harvested 3 times (on the same day each harvest). The second alfalfa is planted in 1994 and is 
harvested only once (on a different day from the previous year). Note that the arrays should all be length 2, but 
the harvest sub-arrays for the first alfalfa instance are length 3 while the second sub-array is length 1.

```python
from SC_redesign.Crop_and_Soil.manager.crop_input import CropScheduleSpec
new_alf = CropScheduleSpec(crop_reference="alfalfa", 
                               planting_years=(1990, 1994),
                               planting_days=120,
                               harvest_years=([1990, 1991, 1992], 1994),                            
                               harvest_days = (220, 199),
                               harvest_operations=(["no_kill", "no_kill", "default"], "default"))
# TODO: Note that this does not yet work with the current CropScheduleSpec. Below is the *desired* output
print(new_alf.planting_years)  # (1990, 1994)
print(new_alf.planting_days)  # (120, 120)
print(new_alf.harvest_years)  # ([1990, 1991, 1992], 1994)
print(new_alf.harvest_days)  # ([220, 220, 220], 199)
```

## Scheduling an entire rotation practice

The `CropRotation` class is a dataclass that contains the specifications of timing practices for multiple crops 
that will be cycled on the field (i.e., a rotation)
