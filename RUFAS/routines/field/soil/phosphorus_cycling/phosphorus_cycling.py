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


def update_all(soil, application, weather, time):

    fertilizer.update_all(soil, application, weather, time)

    manure.update_all(soil, application, weather, time)

    tillage.update_all(soil, application, weather, time)

    soluble_P.update_all(soil)

    fert_leach.update_all(soil, weather, time)

    manure_leach.update_all(soil, weather, time)

    p_mineralization.update_all(soil, time)

    erosion.update_all(soil)
