################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# phosphorus_cycling.py -
#
# Authors: DR. Peter A. Vadas
#          USDA-ARS Dairy Forage Research Center
#          1925 Linden Dr. West
#          Madison, WI 53706
#          PHONE NO. (608) 890-0069
#          E-mail: peter.vadas@ars.usda.gov
#
# Coders:  Kass Chupongstimun
#          Jit Patil
#
################################################################################

from . import fert_leach, fertilizer, manure, manure_leach, p_mineralization,\
    plow, sol_P
import math


def update_all(soil, weather, time):
    fertilizer.update_all(soil, time)

    manure.update_all(soil, time)

    plow.update_all(soil, time)

    sol_P.update_all(soil, weather, time)

    fert_leach.update_all(soil, weather, time)

    manure_leach.update_all(soil, weather, time)

    p_mineralization.update_all(soil, time)

