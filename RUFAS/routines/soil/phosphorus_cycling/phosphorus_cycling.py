################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# phosphorus_cycling.py
#
# Authors: DR. Peter A. Vadas
#          USDA-ARS Dairy Forage Research Center
#          1925 Linden Dr. West
#          Madison, WI 53706
#          PHONE NO. (608) 890-0069
#          E-mail: peter.vadas@ars.usda.gov
#
# Coders:  Jacob Johnson
#          William Donovan
#
################################################################################

from . import fert_leach, fertilizer, manure, manure_leach, p_mineralization,\
    tillage, soluble_P, erosion


def update_all(soil, field_management, weather, time):

    fert_management = field_management.managed_applications['fertilizer']
    if (time.year, time.day) in fert_management.applications:
        if fert_management.check_conditions(soil, weather, time):
            fertilizer.update_all(soil, fert_management.applications[(time.year, time.day)].data)

    manure_management = field_management.managed_applications['manure']
    if (time.year, time.day) in manure_management.applicaitons:
        if manure_management.check_conditions(soil, weather, time):
            manure.update_all(soil, manure_management.applications[(time.year, time.day)].data)

    till_management = field_management.managed_applications['tillage']
    if (time.year, time.day) in till_management.applications:
        if till_management.check_conditions(soil, weather, time):
            tillage.update_all(soil, till_management.applications[(time.year, time.day)].data)

    soluble_P.update_all(soil)

    fert_leach.update_all(soil, weather, time)

    manure_leach.update_all(soil, weather, time)

    p_mineralization.update_all(soil, time)

    erosion.update_all(soil)
