################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: t_ration.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
'''
################################################################################

from RUFAS.routines.animal import Animal

#-------------------------------------------------------------------------------
# Function: test_ration
#-------------------------------------------------------------------------------
def test_ration():

    animal = Animal({'housing': "barn", 'ration': {'user_input': False}})

    #
    # HARD-CODED USER INPUTS!!!!!
    #
    animal.parity = 1      # number of lactations
    animal.WIM = 20        # week in milk, week
    animal.AMF = 3.5       # average milk fat for the breed, %
    animal.BWR = 1         # ratio of calving body weight to holstein calving weight
    animal.base_NED = 1     # Baseline net energy density of the diet

    purchased_feed = {
                "CG":
                {
                "price": 0.132,
                "units": "w",
                "limit": 20,
                "nutrition":
                {
                    "FI": 0.056,
                    "RV": -0.154,
                    "NE": 1.97,
                    "CP": 0.1,
                    "ICP": 0.41,
                    "RDP": 0.12,
                    "conc": "conc"
                }
                },
                "PROT":
                {
                    "price": 0.462,
                    "units": "x",
                    "limit": 2,
                    "nutrition":
                    {
                        "FI": 0.048,
                        "RV": -0.162,
                        "NE": 1.85,
                        "CP": 0.49,
                        "ICP": 0.33,
                        "RDP": 0.32,
                        "conc": "conc"
                    }
                },
                "UPROT":
                {
                    "price": 0.76,
                    "units": "y",
                    "limit": 2,
                    "nutrition":
                    {
                        "FI": 0.048,
                        "RV": -0.162,
                        "NE": 5.67,
                        "CP": 0.62,
                        "ICP": 0.2,
                        "RDP": 0.4,
                        "conc": "conc"
                    }
                },
                "FAT":
                {
                    "price": 1.06,
                    "units": "z",
                    "limit": 100,
                    "nutrition":
                    {
                        "FI": 0.0,
                        "RV": 0.0,
                        "NE": 10.92,
                        "CP": 0.0,
                        "ICP": 0.0,
                        "RDP": 0.0,
                        "conc": "conc"
                    }
                }
            }

    farm_feed = {
                "FRGE":
                {
                    "price": 0.0,
                    "units": "x",
                    "limit": 9999999,
                    "nutrition":
                    {
                        "FI": 0.52,
                        "RV": 0.204,
                        "NE": 1.41,
                        "CP": 0.164,
                        "ICP": 0.036,
                        "RDP": 0.121,
                        "conc": "rough"
                    }
                },
                "HMC":
                {
                    "price": 0.0,
                    "units": "x",
                    "limit": 0,
                    "nutrition":
                    {
                        "FI": 0.04,
                        "RV": -0.17,
                        "NE": 2.25,
                        "CP": 0.09,
                        "ICP": 0.07,
                        "RDP": 0.034,
                        "conc": "conc"
                    }
                }
            }
    animal.formulate_optimized_ration(farm_feed, purchased_feed)
    print(animal.ration)
