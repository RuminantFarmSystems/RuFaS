

"""
This module is based upon the "Root Development" section of the SWAT model
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
        crop_type: an instance of a crop
    """

    fr_root=0.4 - 0.2 * crop_type.fr_PHU
    if fr_root < 0:
        crop_type.fr_root = 0
    else: 
        crop_type.fr_root = fr_root




def calc_z_root(crop_type):
    """
    Description:
        Calculates depth of root development in the soil on a given
        day (AKA z_root).
        "pseudocode_crop" C.3.A.2/3

    Args:
        crop_type: an instance of a crop
    """

    if not crop_type.z_root == crop_type.z_root_max:

        # C.3.A.3
        if crop_type.fr_PHU > 0.4:
            crop_type.z_root = crop_type.z_root_max

        else:  # self.fr_PHU <= 0.4
            crop_type.z_root = 2.5 * crop_type.fr_PHU * crop_type.z_root_max
