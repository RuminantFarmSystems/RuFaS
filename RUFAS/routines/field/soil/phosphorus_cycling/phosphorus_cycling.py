"""
RUFAS: Ruminant Farm Systems Model

phosphorus_cycling.py

Author(s):  Jacob Johnson jacob8399@gmail.com
            William Donovan wmdonovan@wisc.edu
"""

from . import fert_leach, fertilizer, manure, manure_leach, P_mineralization, \
    tillage, soluble_P, erosion


def update_all(soil, field_management, weather, time):
    """
    Description:
        Runs the phosphorus cycling sub-module.
        Currently largely based on Peter Vadas' SurPhos
    Args:
        soil: instance of the Soil class specified in soil.py
        field_management: instance of the FieldManagement class
            specified in field_management.py
        weather: instance of the Weather class specified in classes.py
        time: instance of the Time class specified in classes.py
    """

    # check for scheduled fertilizer application and conducive conditions
    fert_management = field_management.managed_applications['fertilizer']
    if (time.year, time.day) in fert_management.applications:
        if fert_management.check_conditions(soil, weather, time):
            # apply fertilizer
            fertilizer.update_all(soil, fert_management.applications[(time.year, time.day)])

    # check for scheduled manure application and conducive conditions
    manure_management = field_management.managed_applications['manure']
    if (time.year, time.day) in manure_management.applications:
        if manure_management.check_conditions(soil, weather, time):
            # apply manure
            manure.update_all(soil, manure_management.applications[(time.year, time.day)])

    # check for scheduled tillage operations and conducive conditions
    till_management = field_management.managed_applications['tillage']
    if (time.year, time.day) in till_management.applications:
        if till_management.check_conditions(soil, weather, time):
            # till the soil
            tillage.update_all(soil, till_management.applications[(time.year, time.day)])

    # calculate soluble Phosphorus
    soluble_P.update_all(soil)

    # calculate leached fertilizer Phosphorus
    fert_leach.update_all(soil, weather, time)

    # calculate leached manure Phosphorus
    manure_leach.update_all(soil, weather, time)

    # calculate mineralized Phosphorus
    P_mineralization.update_all(soil, time)

    # calculate eroded Phosphorus
    erosion.update_all(soil)
