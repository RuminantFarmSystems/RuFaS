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


def update_all(crop_type):
    """
    Description:
        This function calls the functions in this module necessary to update the
        root development of the given crop.

    Args:
        crop_type: an instance of a crop
    """

    calc_daily_root_biomass(crop_type)
    calc_z_root(crop_type)


def calc_daily_root_biomass(crop_type):
    """
    Description:
        Calculates the fraction of total biomass partitioned to roots
        on a given day in the growing season (AKA fr_root).
        "pseudocode_crop" C.3.A.1

    Args:
        crop_type
    """

    crop_type.fr_root = 0.4 - 0.2 * crop_type.fr_PHU


def calc_z_root(crop_type):
    """
    Description:
        Calculates depth of root development in the soil on a given
        day (AKA z_root).
        "pseudocode_crop" C.3.A.2/3

    Args:
        crop_type
    """

    if not crop_type.z_root == crop_type.z_root_max:

        # C.3.A.3
        if crop_type.fr_PHU > 0.4:
            crop_type.z_root = crop_type.z_root_max

        else:  # self.fr_PHU <= 0.4
            crop_type.z_root = 2.5 * crop_type.fr_PHU * crop_type.z_root_max
