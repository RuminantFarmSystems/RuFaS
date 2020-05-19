"""
RUFAS: Ruminant Farm Systems Model

phosphorus_cycling.py

Author(s):  Jacob Johnson jacob8399@gmail.com
            William Donovan wmdonovan@wisc.edu
"""

from . import fert_leach, fertilizer, manure, manure_leach, p_mineralization, \
    tillage, soluble_P, erosion


def update_all(soil, application_management, weather, time):
    """
    Description:
        Runs the phosphorus cycling sub-module.
        Currently largely based on Peter Vadas' SurPhos
    Args:
        soil: instance of the Soil class specified in soil.py
        application_management: instance of the ApplicationManagement class
            specified in application_management.py
        weather: instance of the Weather class specified in classes.py
        time: instance of the Time class specified in classes.py
    """

    if (time.year, time.day) in application_management.managed_applications['fertilizer'].applications:
        if application_management.managed_applications['fertilizer'].check_conditions(soil, weather, time):
            fertilizer.update_all(soil,
                                  application_management.managed_applications['fertilizer'].applications[
                                      (time.year, time.day)])

    if (time.year, time.day) in application_management.managed_applications['manure'].applications:
        if application_management.managed_applications['manure'].check_conditions(soil, weather, time):
            manure.update_all(soil,
                              application_management.managed_applications['manure'].applications[(time.year, time.day)])

    if (time.year, time.day) in application_management.managed_applications['tillage'].applications:
        if application_management.managed_applications['tillage'].check_conditions(soil, weather, time):
            tillage.update_all(soil, application_management.managed_applications['tillage'].applications[
                (time.year, time.day)])

    soluble_P.update_all(soil)

    fert_leach.update_all(soil, weather, time)

    manure_leach.update_all(soil, weather, time)

    p_mineralization.update_all(soil, time)

    erosion.update_all(soil)
