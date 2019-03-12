'''
RUFAS: Ruminant Farm Systems Model

File name: root_development.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the root development in the soil. The update_all()
             function is the only function intended to be used outside of this
             module.

CropType attribute definitions:

    fr_PHU = Fraction of potential heat units accumulated for the plant on a
             given day in the growing season.

    fr_root = Fraction of total biomass partitioned to roots on a given day in
              the growing season.

    z_root_max = Maximum depth of root development

    z_root = Depth of root development in the soil on a given day


CropType values updated by calling update_all():

    fr_root
    z_root
'''
###############################################################################

#
# This function calls the functions in this module necessary to update the
# root development of the given crop.
#
def update_all(crop_type, time):
    calc_daily_root_biomass(crop_type, time)
    calc_z_root(crop_type, time)


#
# Calculates the fraction of total biomass partitioned to roots
# on a given day in the growing season (AKA fr_root).
# "Pseudo code_SC_Water Uptake_1.0.docx" section 2.A.1
#
def calc_daily_root_biomass(crop_type, time):
    inGrowingPeriod = crop_type.planting_date <= time.day <= crop_type.harvest_date

    if inGrowingPeriod:
        crop_type.fr_root = 0.4 - 0.2 * crop_type.fr_PHU
    else:
        crop_type.fr_root = 0


#
# Calculates depth of root development in the soil on a given
# day (AKA z_root).
# "Pseudo code_SC_Water Uptake_1.0.docx" section 2.A.2
#
def calc_z_root(crop_type, time):
    # Save the previous day's value
    crop_type.prev_z_root = crop_type.z_root

    afterHarvest = time.day > crop_type.harvest_date

    if crop_type.crop_type == "perennial":
        crop_type.z_root = crop_type.z_root_max

    elif afterHarvest:
        crop_type.z_root = 0

    elif crop_type.crop_type == "annual" and crop_type.fr_PHU > 0.4:
        crop_type.z_root = crop_type.z_root_max

    else: # crop_type == "annual" and self.fr_PHU <= 0.4
        crop_type.z_root = 2.5 * crop_type.fr_PHU * crop_type.z_root_max
