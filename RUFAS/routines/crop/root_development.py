"""
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
"""
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
# "pseudocode_crop" C.3.A.1
#
def calc_daily_root_biomass(crop_type, time):
    in_growing_period = crop_type.start_date <= time.day <= crop_type.harvest_date and not crop_type.is_dormant

    if in_growing_period:
        crop_type.fr_root = 0.4 - 0.2 * crop_type.fr_PHU
    else:
        crop_type.fr_root = 0


#
# Calculates depth of root development in the soil on a given
# day (AKA z_root).
# "pseudocode_crop" C.3.A.2/3
#
def calc_z_root(crop_type, time):
    # Save the previous day's value
    crop_type.prev_z_root = crop_type.z_root

    after_harvest = time.day > crop_type.harvest_date

    # C.3.A.2
    if crop_type.crop_type == "perennial" and crop_type.planted:
        crop_type.z_root = crop_type.z_root_max

    elif after_harvest:
        crop_type.z_root = 0

    # C.3.A.3
    elif crop_type.crop_type == "annual" and crop_type.fr_PHU > 0.4:
        crop_type.z_root = crop_type.z_root_max

    else:  # crop_type == "annual" and self.fr_PHU <= 0.4
        crop_type.z_root = 2.5 * crop_type.fr_PHU * crop_type.z_root_max
