"""
RUFAS: Ruminant Farm Systems Model
File name: animal_requirements.py
Description: This file contains constants used in calculations of animal requirements
    May also serve as repository for values associated with ration formulation in the future
Author(s): Joe Waddell jw2574@cornell.edu
"""

# animal_requirements.py minimum values for returns
# TODO: move these to the animal_module_constants.py once PR 366 is merged in
minimum_DMI = 1.0 # kg/day minimum instituted for all animals
minimum_DMI_percentage = 0.01 # as a percentage of body_weight in kg
minimum_phosophorus = 0.0
minimum_calcium = 0.0
