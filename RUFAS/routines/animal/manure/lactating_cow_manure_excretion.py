################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: lactating_cow_manure_excretion.py
Description: Determines manure excretion with information from the ration formulation,
                outputs used by the manure module.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
"""
################################################################################
from RUFAS.routines.feed.feed import FeedNames, Nutrients

def manure_calculations(ration_formulation, feed, BW, DIM, mPrt):
    '''
    Calculates input for manure module with information from the ration formulation.
    Equations referenced are from pseudocode.
    
    Args:
        ration_formulation: dictionary which stores the calculated ration
            For n available feeds, the output_handler of the linear programming for the ration formulation
            is a dictionary that looks like:
            {    
                'feed1': amount of feed 1 in kg,
                'feed2': amount of feed 2 in kg,
                ...
                'feedn': amount of feed n in kg,
                'status': 'Optimal',
                'objective': price
            }
        feed: instance of the Feed class
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
    Further calculations to account for entire diet:
    DMI: dry matter intake, kg
    DM: dietary dry matter, % of diet  
    ADF: dietary ADF, % of DM 
    CP: dietary crude protein, % of DM 
    LIG: dietary lignin, % of DM 
    Ash: dietary Ash, % of DM 
    NDF: dietary NDF, % of DM
    -----------------------------------------------------
    Li's example to highlight difference between DM and DMI, as well as respective calculations:
    Suppose we have a diet with only feeds A and B and the result from the linear programming is 
    A = 10 kg
    B = 15 kg
    Then, since all the variables in the solution are in DM basis, the DMI = 10 + 15 = 25 kg.
    Let the DM content of A be 80%, of B be 40%. 
    Farmers need to feed 10 / 0.8 = 12.5 kg of A and 15 / 0.4 = 37.5 kg of B (as fed basis).
    Then, the DM content of the diet is (10 + 15) / (12.5 + 37.5) = 50%.
    
    For the nutrient compositions:
    Let the CP content of A be 80%, of B be 40%.
    Then the CP content of the diet is (10 * 0.8 + 15 * 0.4) / (10 + 15) = 56% in DM basis.
    Similarly for ADF, LIG, Ash, and NDF.   
    '''
    DMI = 0
    total_diet = 0  # in kg
    ADF_diet_content = 0 
    CP_diet_content = 0
    LIG_diet_content = 0
    Ash_diet_content = 0
    NDF_diet_content = 0
    for key in ration_formulation:
        # not every key in the ration_formulation dictionary refers to a feed
        if key in feed.managed_feed_names:
            # percentages of the DM of each nutrient
            managed_feed = FeedNames[key]
            nutrients: dict[str, float] = feed.values(managed_feed)
            DM_feed_content = 0.01 * nutrients[Nutrients.DM.name]
            ADF_feed_content = 0.01 * nutrients[Nutrients.ADF_DM.name]
            CP_feed_content = 0.01 * nutrients[Nutrients.CP_DM.name]
            LIG_feed_content = 0.01 * nutrients[Nutrients.LIG_DM.name]
            Ash_feed_content = 0.01 * nutrients[Nutrients.Ash_DM.name]
            NDF_feed_content = 0.01 * nutrients[Nutrients.NDF_DM.name]

            # kg of each nutrient
            DM_feed_amount = ration_formulation[key]
            ADF_feed_amount = ADF_feed_content * DM_feed_amount
            CP_feed_amount = CP_feed_content * DM_feed_amount
            LIG_feed_amount = LIG_feed_content * DM_feed_amount
            Ash_feed_amount = Ash_feed_content * DM_feed_amount
            NDF_feed_amount = NDF_feed_content * DM_feed_amount
            
            # add to running sums
            as_fed_feed_amount = DM_feed_amount / DM_feed_content
            total_diet += as_fed_feed_amount
            DMI += DM_feed_amount
            ADF_diet_content += ADF_feed_amount
            CP_diet_content += CP_feed_amount
            LIG_diet_content += LIG_feed_amount
            Ash_diet_content += Ash_feed_amount
            NDF_diet_content += NDF_feed_amount
    
    # to find total percentages
    DM = DMI / total_diet * 100
    ADF = ADF_diet_content / DMI * 100
    CP = CP_diet_content / DMI * 100
    LIG = LIG_diet_content / DMI * 100
    Ash = Ash_diet_content / DMI * 100
    NDF = NDF_diet_content / DMI * 100
                
    # Faecal water, kg (Eq 1.2)
    F_water = 1.987 * DMI + 0.348 * ADF - 0.412 * CP - 0.074 * DM - 0.0057 * DIM
    # Faecal dry matter, kg (Eq 1.3)
    F_DM = -0.576 + 0.370 * DMI - 0.075 * CP + 0.059 * ADF
    # Total urine, kg (Eq 1.4)
    U_E = -7.742 + 0.388 * DMI + 0.726 * CP + 2.066 * mPrt
    # Amount of manure, kg (Eq 1.1)
    Mkg = F_water + F_DM + U_E
    
    # Faecal nitrogen, g (Eq 2.2)
    F_N = (-0.0368 + 0.0096 * DMI + 0.0022 * CP + 0.0034 * LIG - 0.000043 * BW) * 1000
    # Urine nitrogen, g (Eq 2.3)
    U_N = (-0.2837 + 0.0068 * DMI + 0.0155 * CP + 0.00013 * DIM + 0.000092 * BW) * 1000
    # Nitrogen in liquid and solid manure, g (Eq 2.1)
    MN = F_N + U_N
    
    #Organic matter intake, kg
    OMI = DMI - Ash_diet_content
    # Degradable volatile solids, g (Eq 3.1)
    VSd = (-1.017 + 0.364 * OMI + 0.029 * NDF - 0.023 * CP) * 1000
    
    # Nondegradable volatile solids, g (Eq 4.1)
    VSnd = (-0.184 + 0.038 * OMI + 0.007 * NDF - 0.001 * CP) * 1000
    
    # Urea concentration, mol/L (Eq 5.1)
    U = (-1.16 + 0.86 * (U_N / U_E)) / 28
    
    # Total ammoniacal nitrogen concentration in the manure slurry, mol/L (Eq 6.1)
    TAN_s = (-162.4 * U * U + 96.4 * U) / 100 
    
    return {"U": U, 
            "TAN_s": TAN_s, 
            "MN": MN, 
            "Mkg": Mkg, 
            "VSd": VSd, 
            "VSnd": VSnd}