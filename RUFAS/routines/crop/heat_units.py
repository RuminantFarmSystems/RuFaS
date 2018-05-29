'''
This module contains the necessary functions for calculating and updating a 
CropType's fr_PHU (fraction of PHU accumulated by current day).

CropType values updated by calling calculate_frPHU():
    prev_accumulated_HU
    accumulated_HU
    prev_fr_PHU
    fr_PHU
'''

def calculate_frPHU(crop, T_min, T_max):
    # Part 1B of Crop Biomass pseudocode
    if T_min < crop.T_base_min:
        T_HU_min = crop.T_base_min
    else:
        T_HU_min = T_min

    if T_max > crop.T_base_max:
        T_HU_max = crop.T_base_max
    else:
        T_HU_max = T_max

    T_HU = (T_HU_min + T_HU_max) / 2.0

    if T_HU < crop.T_base_min:
        HU = 0.0
    else:
        HU = T_HU - crop.T_base_min


    # Part 1C of Crop Biomass pseudocode
    
    # This one saves accumulated_HU leading up to today
    crop.prev_accumulated_HU = crop.accumulated_HU
    
    # This one saves accumulated_HU leading up to and including today
    crop.accumulated_HU += HU


    #
    # 2) Calculate accumulated fraction of potential Heat Units
    #
    crop.prev_fr_PHU = crop.fr_PHU
    crop.fr_PHU = crop.accumulated_HU / crop.PHU
