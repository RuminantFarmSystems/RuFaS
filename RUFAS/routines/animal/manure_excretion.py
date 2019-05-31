################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: manure_excretion.py
Description: Determines manure excretion with information from the ration formulation, 
                outputs used by the manure module.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
'''
################################################################################


def manure_calculations(ration_formulation, BW, DIM, mPrt):
    '''
    Calculates inputs for manure module with information from the ration formulation. Equations referenced are from pseudocode.
    
    Args:
        DMI: dry matter intake, kg (from feed formulation)
        ADF: dietary ADF, % of DM (from feed formulation)
        CP: dietary crude protein, % of DM (from feed formulation)
        DM: dietary dry matter, % of diet (from feed formulation)
        LIG: dietary lignin, % of DM (from feed formulation)
        ash: dietary ash, % of DM (from feed formulation)
        BW: body weight, kg (from animal input)
        DIM: days in milk, d (from animal input)
        mPrt: milk protein, % of milk (from animal input)
    
    Returns:
        U: urea concentration, mol/L
        TAN_s: total ammoniacal nitrogen concentration in the manure slurry, mol/L
        MN: nitrogen in liquid and solid manure, g
        Mkg: amount of manure, kg
        VSd: degradable volatile solids, g
        VSnd: nondegradable volatile solids, g
    '''
    # Faecal water, kg (Eq 1.2)
    F_water = 1.987 * DMI + 0.348 * ADF - 0.412 * CP - 0.074 * DM - 0.0057 * DIM
    # Faecal dry matter, kg (Eq 1.3)
    F_DM = -0.576 + 0.370 * DMI - 0.075 * CP + 0.059 * ADF
    # Total urine, kg (Eq 1.4)
    U_E = -7.742 + 0.388 * DMI + 0.726 * CP + 2.066 * mPrt
    # Amount of manure, kg (Eq 1.1)
    Mkg = F_water + F_DM + U_E
    
    # Faecal nitrogen, g (Eq 2.2)
    F_N = -0.0368 + 0.0096 * DMI + 0.0022 * CP + 0.0034 * LIG - 0.000043 * BW
    # Urine nitrogen, g (Eq 2.3)
    U_N = -0.2837 + 0.0068 * DMI + 0.0155 * CP + 0.00013 * DIM + 0.000092 * BW
    # Nitrogen in liquid and solid manure, g (Eq 2.1)
    MN = F_N + U_N
    
    # Organic matter intake, kg
    OMI = DMI * (1 - ash)
    # Degradable volatile solids, g (Eq 3.1)
    VSd = -1.017 + 0.364 * OMI + 0.029 * NDF - 0.023 * CP
    
    # Nondegradable volatile solids, g (Eq 4.1)
    VSnd = -0.184 + 0.038 * OMI + 0.007 * NDF - 0.001 * CP
    
    # Urea concentration, mol/L (Eq 5.1)
    U = (-1.16 + 0.86 * (U_N / U_E)) / 28
    
    # Total ammoniacal nitrogen concentration in the manure slurry, mol/L (Eq 6.1)
    TAN_s = -5.8 * U + 3.4
    
    return U, TAN_s, MN, Mkg, VSd, VSnd

def calc_weighted_sum(nutrient):
    '''
    Calculates the weighted sum of the specified nutrient in each ingredient in the calculated ration.
    
    Args:
        nutrient: the specified nutrient for which to calculate the weighted sum
        ration_formulation: 
    
    Returns: the weighted sum of the @nutrient in each ingredient in the calculated ration.
    '''
    pass

