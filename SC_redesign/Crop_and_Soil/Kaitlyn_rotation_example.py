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
