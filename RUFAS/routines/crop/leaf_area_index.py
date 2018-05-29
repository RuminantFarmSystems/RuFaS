'''
This module contains the necessary functions for calculating and updating the 
Leaf Area Index of the current day. The only function that is meant to be called 
outside of this file is calculate_LAI_actual().

CropType values updated by calling calculate_LAI_actual():
    prev_fr_LAI_max
    fr_LAI_max
    LAI_actual
    prev_LAI_actual
'''
from math import exp, log, floor, sqrt

def calculate_LAI_actual(crop):
    l1, l2 = calculate_shape_coefficients(crop)
    
    crop.prev_fr_LAI_max = crop.fr_LAI_max
    crop.fr_LAI_max = crop.fr_PHU / (crop.fr_PHU + exp(l1 - l2*crop.fr_PHU))
    
    exp_part = exp(5 * (crop.prev_LAI_actual - crop.LAI_max))
    dLAI_max = (crop.fr_LAI_max - crop.prev_fr_LAI_max) * crop.LAI_max * (1-exp_part)
    
    dLAI_actual = dLAI_max * sqrt(crop.gamma_reg)
    
    temp_for_LAI = crop.LAI_actual
    if crop.fr_PHU < crop.fr_PHU_sen:
        crop.LAI_actual = crop.prev_LAI_actual + dLAI_actual
    else:
        crop.LAI_actual = crop.LAI_max * (1-crop.fr_PHU) / (1-crop.fr_PHU_sen)
    crop.prev_LAI_actual = temp_for_LAI
    

def calculate_shape_coefficients(crop):
    l2_part1_floor = floor((crop.fr_PHU_1 / crop.fr_LAI_1) - crop.fr_PHU_1)
    l2_part2_floor = floor((crop.fr_PHU_2 / crop.fr_LAI_2) - crop.fr_PHU_2)
    
    l2 = ( (log(l2_part1_floor) - log(l2_part2_floor)) 
           / (crop.fr_PHU_2 - crop.fr_PHU_1) )
 
    
    l1_floor = floor((crop.fr_PHU_1 / crop.fr_LAI_1) - crop.fr_PHU_1)
    
    l1 = log(l1_floor) + l2 * crop.fr_PHU_1
    
    return l1, l2
    