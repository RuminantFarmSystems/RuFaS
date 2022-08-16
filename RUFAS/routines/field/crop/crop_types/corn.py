from RUFAS.routines.field.crop.crop_types.base_crop import BaseCrop

# Define global variables containing corn parameters
# Keeping them separate from the Class definitions allows for them to be changed before running
# RUFAS. This is important for the validation module.

# ToDo:
#   Check that the only manually initiated attributes in Corn are "internally calculated" and "output" variables
#   Also, check that only values that actually make sense to change be included in this dictionary
#   All data values need to be documented in CornConfigData AND the attributes in Corn class.
CornConfigData = {"T_base_min": 10, # Heat Unit Data ----v
                  "T_base_max": 30,
                  "PHU": 1200,
                  "fr_PHU_1": 0.15,  # LAI data ----v
                  "fr_PHU_2": 0.50,
                  "fr_LAI_1": 0.05,
                  "fr_LAI_2": 0.95,
                  "fr_PHU_sen": 0.90,
                  "fr_PHU_harvest": 1.2,
                  "fr_PHU_harvest_min": 0.7,
                  "LAI_max": 3,
                  "LAI_min": 0,
                  "z_root_max": 2000,  # root depth data ----v
                  "kl": 0.65,  # biomass data ----v
                  "RUE": 39,
                  "T_opt": 25,
                  "beta_w": 10,  # water use data ----v
                  "epco": 0.5,
                  "N_fix": 0.0,  # nitrogen uptake data ----v
                  "beta_n": 10,
                  "fr_n1": 0.047,
                  "fr_n2": 0.0177,
                  "fr_n3": 0.0138,
                  "fr_n3ish": 0.01381,
                  "beta_p": 10,  # phosphorus uptake data ----v
                  "fr_PHU_50": 0.5,
                  "fr_PHU_100": 1.0,
                  "fr_p1": 0.0048,
                  "fr_p2": 0.0018,
                  "fr_p3": 0.0014,
                  "fr_p3ish": 0.00141,
                  "HI_max": 0,  # yields data ----v
                  "HI_min": 0.3,
                  "HI_actual": 0,
                  "HI_opt": 0.6,
                  "harvest_eff": 0.9,
                  "DM_harvest_percent": 0.35,  # TODO: Hard coded dry matter percent at harvest - GitHub Issue #155
                  "gamma_wu": 0,
                  "biomass_dry_down_percent": 0.0,
                  "NDF_harvest_percent": 0.0}


class Corn(BaseCrop):
    """Corn class"""
    def __init__(self, crop_name, data):
        """create an instance of Corn
                    
           Args: 
            crop_name (str): the name of the crop
            data (dict): data used to construct the class
        """
        super().__init__(crop_name=crop_name, data=data, species="corn")

    # species-specific methods ...
