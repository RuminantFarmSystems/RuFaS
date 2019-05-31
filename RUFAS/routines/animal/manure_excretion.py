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
    Calculates inputs for manure module with information from the ration formulation. 
    Equations referenced are from pseudocode.
    
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
    
    '''
    For n available feeds, the output of the linear programming for the ration formulation 
    is a dictionary that looks something like:
    {    
        'feed1': amount,
        'feed2': amount,
        ...
        'feedn': amount,
        'status': 'Optimal'
        'objective': price
    }
    Thus, to find the weighted sums of the nutrients in each ingredient, we have to check if the 
    key is an available feed or not.
    '''
    ADF_sum = 0
    CP_sum = 0
    DM_sum = 0
    LIG_sum = 0
    ash_sum = 0
    for key in ration_formulation:
        if key in feed.available_feed_names:
            # to each sum, add the amount of the nutrient which is in the key
            ADF_sum += feed.available_feeds[key]['ADF_DM']
            CP_sum += feed.available_feeds[key]['CP_DM']
            DM_sum += feed.available_feeds[key]['DM']
            LIG_sum += feed.available_feeds[key]['LIG_DM']  # doesn't currently exist
            ash_sum += feed.available_feeds[key]['Ash_DM']
            
    # TODO: what to do about NDF in 3.1 and 4.1?
    
    # Faecal water, kg (Eq 1.2)
    F_water = 1.987 * DMI + 0.348 * ADF_sum - 0.412 * CP_sum - 0.074 * DM_sum - 0.0057 * DIM
    # Faecal dry matter, kg (Eq 1.3)
    F_DM = -0.576 + 0.370 * DMI - 0.075 * CP_sum + 0.059 * ADF_sum
    # Total urine, kg (Eq 1.4)
    U_E = -7.742 + 0.388 * DMI + 0.726 * CP_sum + 2.066 * mPrt
    # Amount of manure, kg (Eq 1.1)
    Mkg = F_water + F_DM + U_E
    
    # Faecal nitrogen, g (Eq 2.2)
    F_N = -0.0368 + 0.0096 * DMI + 0.0022 * CP_sum + 0.0034 * LIG_sum - 0.000043 * BW
    # Urine nitrogen, g (Eq 2.3)
    U_N = -0.2837 + 0.0068 * DMI + 0.0155 * CP_sum + 0.00013 * DIM + 0.000092 * BW
    # Nitrogen in liquid and solid manure, g (Eq 2.1)
    MN = F_N + U_N
    
    # Organic matter intake, kg
    OMI = DMI * (1 - ash_sum)
    # Degradable volatile solids, g (Eq 3.1)
    VSd = -1.017 + 0.364 * OMI + 0.029 * NDF - 0.023 * CP
    
    # Nondegradable volatile solids, g (Eq 4.1)
    VSnd = -0.184 + 0.038 * OMI + 0.007 * NDF - 0.001 * CP
    
    # Urea concentration, mol/L (Eq 5.1)
    U = (-1.16 + 0.86 * (U_N / U_E)) / 28
    
    # Total ammoniacal nitrogen concentration in the manure slurry, mol/L (Eq 6.1)
    TAN_s = -5.8 * U + 3.4
    
    return U, TAN_s, MN, Mkg, VSd, VSnd

