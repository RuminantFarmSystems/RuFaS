from dataclasses import dataclass
from typing import Optional
from collections.abc import Sequence

from SC_redesign.Crop_and_Soil.field.harvest_operations import HarvestOperation


@dataclass(kw_only=True)
class CropScheduleSpec:
    crop: float = "corn"
    """The crop to be planted. Either the name of one of supported `CropSpecies` or a reference to the name of a 
    custom, user-specified crop"""
    planting_years: int | Sequence[int] = (1, 2, 3)
    """the years during which the crop should be planted. For each value, a new crop will be initialized"""
    planting_days: int | Sequence[int] = 120
    """the (Julian) day on which the crop should be planted. If a single value is given, it will be repeated for 
    all years. Otherwise, there should be one value for each value in `planting_years`."""
    harvest_years: int | Sequence[int] = (1, 2, 3)
    """the years during which the crop should undergo a harvest operation"""
    harvest_days: int | Sequence[int] | Sequence[Sequence[int]] = 220
    """the (Julian) day on which the crop should be harvested. If a single value/element is given, it will be repeated 
    for all harvest years. Otherwise, there must be one element for each present in `harvest_years`. If multiple
    harvests can occur for the same crop instance, the corresponding element should be a list whose elements correspond.
    to separate harvest events"""
    harvest_operations: HarvestOperation | Sequence[HarvestOperation] = HarvestOperation.HARVEST
    """the harvest operation that should occur. If a single value is given, it will be repeated for all harvests. 
    Otherwise, the structure/dimensions should correspond to those of `harvest_days`."""
    pattern_skip: Optional[int] = None
    """the number of years to wait before repeating the pattern"""
    pattern_repeat: Optional[int] = None
    """the number of times the specified crop management pattern should be repeated"""

    def __post_init__(self):
        # convert attributes to tuples, no matter the length of the input
        self.planting_years = tuple([self.planting_years])
        self.planting_days = tuple([self.planting_days])
        self.harvest_years = tuple([self.harvest_years])
        self.harvest_days = tuple([self.harvest_days])
        self.harvest_operations = tuple([self.harvest_operations])

        # setup the pattern
        if self.pattern_repeat is None or self.pattern_repeat <= 0:
            return

        self.pattern_skip = self.pattern_skip or 0  # set to 0 if None
        for i in range(self.pattern_repeat - 1):
            pass








    def make_from_dict(self):
        pass

    def make_from_json(self):
        pass

    def make_from_tabular(self):
        pass


def repeat_pattern(pattern: Sequence[int] = [1, 2, 5], skip: int = 2, repeat: int = 2):
    """helper that repeats a pattern

    Parameters
    ----------

    """
    out = pattern
    span = max(pattern) - min(pattern)
    for i in range(repeat):
        new = [x + ((i+1)*span) + (1+i)*(skip+1) for x in pattern]
        out = out + new
    return out

#-- Planting Cases --
# One planting.
tmp = CropScheduleSpec(planting_years=1, planting_days=120)
# Three plantings, on the same date each year
tmp = CropScheduleSpec(planting_years=(1, 2, 3), planting_days=120)
# Three plantings with different dates each year
tmp = CropScheduleSpec(planting_years=(1, 2, 3), planting_days=(120, 111, 130))
# 4 plantings, two during the same year
tmp = CropScheduleSpec(planting_years=(1, 2, 2, 3), planting_days=(120, 120, 300, 120))



#--------------------
#<editor-fold desc="Example-Input">
#--------------------

# ---- Corn-Alfalfa Rotation ----
# User input
Rotation_1 = {"Crops": {"Crop 1": {"species": "corn",
                                   "planting years": [0, 1, 2],  # plant 3 years in a row
                                   "planting day": 121,  # Spring
                                   "harvest years": [0, 1, 2],  # harvest each plant year
                                   "harvest day": 220,  # Fall
                                   "skip": 3,  # wait 3 years before repeating the pattern
                                   "cycles": 2  # repeat the pattern twice
                                   },
                        "Crop 2": {"species": "alfalfa",
                                   "planting years": [3],  # plant in first gap year
                                   "planting day": 190,  # Summer
                                   "harvest years": [5],  # harvest 3rd year after planting
                                   "harvest day": 250,  # Fall
                                   "skip": 3,  # wait 3 years before repeating the pattern
                                   "cycles": 2  # repeat the pattern twice
                                   }
                        }
              }
# Resulting patterns in the field (by year)
years = [0, 1, 2, 3, 4, 5,
         6, 7, 8, 9, 10, 11]
species_in_field = ["corn", "corn", "corn", "alfalfa", "alfalfa", "alfalfa",
                    "corn", "corn", "corn", "alfalfa", "alfalfa", "alfalfa"]
planting_events = ["corn", "corn", "corn", "alfalfa", None, None,
                   "corn", "corn", "corn", "alfalfa", None, None]
harvest_events = ["corn", "corn", "corn", None, None, "alfalfa",
                  "corn", "corn", "corn", None, None, "alfalfa"]

# ---- Corn-Triticale Rotation ----
# User input
Rotation_2 = {"Crops": {"Crop 1": {"species": "corn",
                                   "planting years": [0],  # plant in first year
                                   "planting day": 121,  # Spring
                                   "harvest years": [0],  # harvest in planting year
                                   "harvest day": 220,  # Fall
                                   "skip": 0,  # don't wait before repeating the pattern
                                   "cycles": 4  # repeat the pattern 4 times
                                   },
                        "Crop 2": {"species": "triticale",
                                   "planting years": [0],  # plant in first year
                                   "planting day": 220,  # Fall (corn harvest day)
                                   "harvest years": [1],  # harvest the following year
                                   "harvest day": 121,  # Spring (corn panting day)
                                   "skip": 0,  # don't wait before repeating the pattern
                                   "cycles": 4  # repeat the pattern 4 times
                                   }
                        }
              }
# Resulting patterns in the field (by year)
years = [0, 1, 2, 3,
         4]  # dangling triticale harvest year

species_in_field = ["corn&triticale",
                    "corn&triticale",
                    "corn&triticale",
                    "corn&triticale",
                    "triticale"]

planting_events = ["corn&triticale",
                   "corn&triticale",
                   "corn&triticale",
                   "corn&triticale",
                   None]

harvest_events = ["corn",
                  "triticale&corn",
                  "triticale&corn",
                  "triticale&corn",
                  "triticale"]

# ---- Combined Rotation ----
# User input - This does repeats 3 years corn, 3 years alfalfa, 3 years corn & triticale
Rotation_3 = {"Crops": {"Crop 1": {"species": "corn",
                                   "planting years": [0, 1, 2, 6, 7, 8],  # plant 3 years in a row
                                   "planting day": 121,  # Spring
                                   "harvest years": [0, 1, 2],  # harvest each plant year
                                   "harvest day": 220,  # Fall
                                   "skip": 0,  # don't wait before repeating the pattern
                                   "cycles": 2  # repeat the pattern twice
                                   },
                        "Crop 2": {"species": "alfalfa",
                                   "planting years": [3],  # plant in first gap year of corn
                                   "planting day": 190,  # Summer
                                   "harvest years": [5],  # harvest 3rd year after planting
                                   "harvest day": 250,  # Fall
                                   "skip": 6,  # wait 6 years before repeating the pattern
                                   "cycles": 2  # repeat the pattern twice
                                   },
                        "Crop 3": {"species": "triticale",
                                   "planting years": [6, 7, 8],  # plant 3 years in a row (after 6 years)
                                   "planting day": 220,  # Fall (corn harvest day)
                                   "harvest years": [1],  # harvest the following year
                                   "harvest day": 121,  # Spring (corn panting day)
                                   "skip": 3,  # wait 6 years before repeating
                                   "cycles": 2  # repeat the pattern 4 times
                                   }
                        }
              }
# Resulting patterns in the field (by year)
years = [0, 1, 2,  # corn
         3, 4, 5,  # alfalfa
         6, 7, 8,  # corn & triticale
         9, 10, 11, # corn
         12, 13, 14, # alfalfa
         15, 16, 17, # corn & triticale
         18, ]  # dangling triticale harvest year

species_in_field = ["corn", "corn", "corn",
                    "alfalfa", "alfalfa", "alfalfa",
                    "corn&triticale", "corn&triticale", "corn&triticale",
                    "corn&triticale", "corn", "corn",
                    "alfalfa", "alfalfa", "alfalfa",
                    "corn&triticale", "corn&triticale", "corn&triticale",
                    "triticale"]

planting_events = ["corn", "corn", "corn",
                   "alfalfa", None, None,
                   "corn&triticale", "corn&triticale", "corn&triticale",
                   "corn", "corn", "corn",
                   "alfalfa", None, None,
                   "corn&triticale", "corn&triticale", "corn&triticale",
                   None]

harvest_events = ["corn", "corn", "corn",
                  None, None, "alfalfa",
                  "corn", "triticale&corn", "triticale&corn",
                  "triticale&corn", "corn", "corn",
                  None, None, "alfalfa"
                  "corn", "triticale&corn", "triticale&corn",
                  "triticale"]
#</editor-fold>

#--------------------
#<editor-fold desc="Input-App-format">
#--------------------

#</editor-fold>
