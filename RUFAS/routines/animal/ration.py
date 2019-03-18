################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: ration.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
'''
################################################################################

from numpy import exp
from RUFAS import util

# -------------------------------------------------------------------------------
# Function: optimize
# -------------------------------------------------------------------------------
def new_optimize(feed, rqmts):
    '''
    Sets up the arguments for the linear programming optimization.

	Args:
        feed : instance of the Feed class
        rqmts : dict which represents the dietary requirements of the cows

    Returns:
        dict: the dictionary that is returned by the call to util.LP_solve()
	'''

    # LHS is of the following form. LHS stands for Left Hand Side.
    # [
    #     [##,##, ..., ##],  // Each column has the coefficients for one specific feed type
    #     [##,##, ..., ##],  // Each row has the coefficients for one specific nutrient type
    #     [##,##, ..., ##],  // Each row represents the LHS of a constraint equation
    #     [##,##, ..., ##],
    #     [##,##, ..., ##]
    # ]
    LHS = []
    constraint = [feed.available_feeds[feed_name]['FU']
                  for feed_name in feed.available_feed_names]
    LHS.append(constraint)

    constraint = [(feed.available_feeds[feed_name]['RU'] - 0.21)
                  for feed_name in feed.available_feed_names]
    LHS.append(constraint)
    #for now, set as dummy variables:
    DMIest = 0
    BW = 0
    DBW = 0
    ME_DM_arr, RDP_DM_arr, RUP_DM_arr = calculate_ME_RDP_RUP(feed, DMIest, BW, DBW)
    LHS.append(ME_DM_arr)
    LHS.append(RDP_DM_arr)
    LHS.append(RUP_DM_arr)

    # RHS is of the following form. Each value represents the required RHS value
    # for the corresponding LHS constraint found in LHS.
    # [
    #     ##,
    #     ##,
    #     ##,
    #     ##,
    #     ##
    # ]
    RHS = [rqmts[nutrient]['val'] for nutrient in feed.nutrients_in_LP]

    # objective is of the form [##,##, ..., ##] with the values being the price
    # for each food type. This makes the objective function represent the total
    # cost of a ration formulation.
    objective = [feed.available_feeds[feed_name]['Price']
                 for feed_name in feed.available_feed_names]

    # Each variable represents the quantity of a feed type. The variables are
    # named after their corresponding food type.
    var_names = feed.available_feed_names

    # operators is of the form [##, ##, ..., ##] with each value being one of
    # '<=', '>=', or '=='. These are the operators between the corresponding
    # LHS constraint and RHS required value.
    operators = [rqmts[nutrient]['op'] for nutrient in feed.nutrients_in_LP]

    # The lower bounds for quantity of a food type are zero since a negative
    # quantity of food in this context does not make sense.
    lower_bounds = [0] * len(feed.available_feed_names)

    # The upper bounds are the 'Limit' specified in the csv library for each
    # food type.
    upper_bounds = [feed.available_feeds[feed_name]['Limit']
                    for feed_name in feed.available_feed_names]

    # util.LP_print(LHS, RHS, objective, var_names, operators,
    #			  "minimize", "RATION", lower_bounds, upper_bounds)

    return util.LP_solve(LHS, RHS, objective, var_names, operators,
                         "minimize", "RATION", lower_bounds, upper_bounds)


# -------------------------------------------------------------------------------
# Function: optimize
# -------------------------------------------------------------------------------
def optimize(feed, rqmts):
    '''
    Sets up the arguments for the linear programming optimization.

	Args:
        feed : instance of the Feed class
        rqmts : dict which represents the dietary requirements of the cows

    Returns:
        dict: the dictionary that is returned by the call to util.LP_solve()
	'''

    # LHS is of the following form. LHS stands for Left Hand Side.
    # [
    #     [##,##, ..., ##],  // Each column has the coefficients for one specific feed type
    #     [##,##, ..., ##],  // Each row has the coefficients for one specific nutrient type
    #     [##,##, ..., ##],  // Each row represents the LHS of a constraint equation
    #     [##,##, ..., ##],
    #     [##,##, ..., ##]
    # ]
    LHS = []
    for nutrient_type in feed.nutrients_in_LP:
        constraint = [feed.available_feeds[feed_name][nutrient_type]
                      for feed_name in feed.available_feed_names]

        LHS.append(constraint)
    # RHS is of the following form. Each value represents the required RHS value
    # for the corresponding LHS constraint found in LHS.
    # [
    #     ##,
    #     ##,
    #     ##,
    #     ##,
    #     ##
    # ]
    RHS = [rqmts[nutrient]['val'] for nutrient in feed.nutrients_in_LP]

    # objective is of the form [##,##, ..., ##] with the values being the price
    # for each food type. This makes the objective function represent the total
    # cost of a ration formulation.
    objective = [feed.available_feeds[feed_name]['Price']
                 for feed_name in feed.available_feed_names]

    # Each variable represents the quantity of a feed type. The variables are
    # named after their corresponding food type.
    var_names = feed.available_feed_names

    # operators is of the form [##, ##, ..., ##] with each value being one of
    # '<=', '>=', or '=='. These are the operators between the corresponding
    # LHS constraint and RHS required value.
    operators = [rqmts[nutrient]['op'] for nutrient in feed.nutrients_in_LP]

    # The lower bounds for quantity of a food type are zero since a negative
    # quantity of food in this context does not make sense.
    lower_bounds = [0] * len(feed.available_feed_names)

    # The upper bounds are the 'Limit' specified in the csv library for each
    # food type.
    upper_bounds = [feed.available_feeds[feed_name]['Limit']
                    for feed_name in feed.available_feed_names]

    # util.LP_print(LHS, RHS, objective, var_names, operators,
    #			  "minimize", "RATION", lower_bounds, upper_bounds)

    return util.LP_solve(LHS, RHS, objective, var_names, operators,
                         "minimize", "RATION", lower_bounds, upper_bounds)


def new_calculate_rqmts(BW, BCS, CBW, CI, concentrate, CP_Milk, DOP, DHD, DVD,
                        DIM, fat_milk, lactose_milk, milk, parity, type):
    '''
    Calculate the dietary requirements of the cows. These values are used
    on the RHS of the linear program. Each calculation has a reference to the
    respective calculation in the pseudocode.

	Args:
        BW: body weight, kg
        BCS: body condition score, 1 to 5
        CBW: calf birth weight, kg
        CI: calving inerval, days
        concentrate: concentrate supplementation when farming type is "Pasture", kg
        CP_Milk: milk crude protein content
        DOP: days of pregnancy, days
        DHD: daily horizontal distance, km
        DVD: daily vertical distance, km
        DIM: days in milk, days
        fat_milk: milk fat content
        lactose_milk: milk lactose content
        milk: milk production, kg
        parity: number of times birth was given
        type: farming type, "Barn" or "Pasture"

    Returns:
        dict : a dictionary that represents the dietary requirements of the cows,
            used as the RHS of the LP
    '''

    #ENERGY REQUIREMENTS (divided into the following 5 components: maintenance,
    #lactation, activity, pregnancy, and body weight change requirements):

    #Maintenance requirements
    #------------------------
    #Ideal Body Weight, kg (A.ER.1.2)
    IBW = BW / (0.65 + 0.1 * BCS)
    #Net Energy maintenance, Mcal (A.ER.1.1)
    NEm = 0.10 * IBW ** 0.75

    #Lactation requirements
    #----------------------
    #Net Energy lactation, Mcal (A.ER.2.1)
    NEl = 9.29 * milk * fat_milk + 5.5 * milk * CP_Milk + 3.95 * milk * lactose_milk

    #Activity requirements
    #---------------------
    #Net Energy activity, Mcal (A.ER.3.1)
    if type == "Barn":
        Neact = (DHD * 0.35 * BW + DVD * 5 * BW) / 1000
    elif type == "Pasture":
        Neact = (DHD * 0.35 * BW + DVD * 5 * BW + 10 * BW ** 0.75 * ((600 - 12 * concentrate) / 600)) / 1000

    #Pregnancy energy requirements
    #-----------------------------
    #Net Energy pregnancy, Mcal (A.ER.4.1)
    if DOP < 190:
        NEpreg = 0
    elif DOP >= 190 and DOP <= 279:
        NEpreg = ((0.00318 * DOP - 0.0352) * (CBW / 45)) / 0.218
    else:
        NEpreg = ((0.00318 * 279 - 0.0352) * (CBW / 45)) / 0.218

    #Body Weight change requirements
    #-------------------------------
    #Target Calving Weight, kg (A.ER.5.1)
    if parity == 1:
        TCW = 700 * 0.85
    elif parity == 2:
        TCW = 700 * 0.92
    elif parity == 3:
        TCW = 700 * 0.96
    elif parity > 3:
        TCW = 700 * 1
    #Body weight change (delta body weight = DBW), kg (A.ER.5.4)
    DBW = (TCW - 0.94 * BW) / (280 - CI + DOP)
    #Net Energy body weight, Mcal (A.ER.5.5)
    if DBW > 0:
        NEbw = DBW * 6.7 * 0.88
    else:
        NEbw = DBW * 6.7 * 0.85

    #Total energy requirements, mCal (A.ER.6.1)
    TNEL = NEm + Nel + NEact + NEpreg + NEbw

    #FEED INTAKE
    #Dry Matter Intake estimation, kg (A.FI.1.1)
    if DIM > 100:
        DMIest = 2.58 + 0.30 * NEl + 0.027 * BW + 0.05 * DBW - 1.15 * BCS
    else:
        DMIest = (2.58 + 0.30 * NEl + 0.027 * BW) * (1 - exp(-0.192 * ((DIM + 3.5)/ 7 + 3.67)))

    #Fiber Intake Capacity, Fiber Units/day (A.FI.2.2)
    if parity == 1:
        FIC = 0.338 * (WIM + 3) ** 0.588 * exp(-0.0277 * (WIM + 3))
    else:
        FIC = 0.564 * (WIM + 0.857) ** 0.36 * exp(-0.0186 * (WIM + 0.857))
    #Maximum Fiber Intake (A.FI.2.3)
    FIMax = 0.01025 * BW * FIC

    #PROTEIN REQUIREMENTS - temporarily based on IFSM, will be replaced with NRC
    #Metabolize protein required for maintenance per day, g (A.PR.1.1)
    MPM = 3.8 * (0.96 * BW) ** 0.75
    #Metabolize protein required for lactation per day, g (A.PR.2.1)
    MPMLK = 10 * CP_Milk * milk / 0.65
    #Microbial crude protein, kg (A.PR.3.1)
    MCP = 0.13 * 0.51 * DMIest
    #Rumen degradable (RDPreq, kg) and undegradable protein (RUPreq, kg) requirements
    RDPreq = MCP / 0.9 #(A.PR.3.2)
    MPreq = MPM + MPMLK #(A.PR.3.3)
    RUPreq = MPreq / 1000 - 0.8 * 0.8 * MCP #(A.PR.3.4)

    RU_min = 0

    nutrient_rqmts = [
        {'op': '<=', 'val': FIMax}, #(A.LP.2.1)
        {'op': '>=', 'val': RU_min}, #(A.LP.2.2)
        {'op': '>=', 'val': TNEL / 0.68}, #(A.LP.2.3)
        {'op': '>=', 'val': RDPreq}, #(A.LP.2.4)
        {'op': '>=', 'val': RUPreq} #(A.LP.2.5)
    ]

    return dict(zip(nutrients_list, nutrient_rqmts))


# -------------------------------------------------------------------------------
# Function: Calculate the dietary requirements of the cows. These values are used
#           on the RHS of the linear program.
# -------------------------------------------------------------------------------
def calculate_rqmts(parity, WIM, AMF, BWR, base_NED, housing,
                    nutrients_list, milk_production_multiplier):
    '''
    Calculate the dietary requirements of the cows. These values are used
    on the RHS of the linear program.

	Args:
        parity : number
        WIM : number of weeks since parturition
        AMF : number for the average milk fat
        BWR : number for the mature body weight of the animal in kg
        base_NED : number for the baseline net energy content of the diet
        housing : string which can be either "barn", "drylot", or "pasture"
        nutrients_list : list that is the LHS of the returned dictionary
        milk_production_multiplier : number

    Returns:
        dict : a dictionary that represents the dietary requirements of the cows,
            where the left hand side is nutrients_list and the right hand side is
            calculated in this method
	'''

    #
    # FIC: Fiber intake capacity
    #
    if parity > 1:
        FIC = (0.564 * (WIM + 0.857) ** 0.360 *
               exp(-0.0186 * (WIM + 0.857)))
    else:
        FIC = (0.388 * (WIM + 3) ** 0.588 *
               exp(-0.0277 * (WIM + 3)))

    #
    # Estimate Base milk production (base milk yield)
    # BaseMY is the milk base milk yield estimated from breed specific lactation curve
    #
    if parity > 1:
        base_MY = (33.95 * WIM ** 0.2208 *
                   exp(-0.03395 * WIM))
    else:
        base_MY = (24.12 * WIM ** 0.1782 *
                   exp(-0.02095 * WIM))

    base_MY *= milk_production_multiplier

    #
    # Estimate Base milk fat
    # BaseMF is the base milk fat estimated from breed specific
    # average milk fat and compoMEInt lactation curve
    #
    base_MF = (1.4286 * AMF * WIM ** -0.24 *
               exp(0.016 * WIM))

    #
    # Estimate Body Weight
    # The body weight is estimated as a function of DIM and
    # the ratio of the calving weight of the breed to that of holsteins
    #
    if parity > 1:
        BW = (BWR * 690 * ((WIM + 1.57) ** -0.0803) *
              exp(0.00720 * (WIM + 1.57)))
    else:
        BW = (BWR * 567 * ((WIM + 1.71) ** -0.0730) *
              exp(0.00869 * (WIM + 1.71)))

    #
    # Estimate Change in Body weight
    #
    if WIM < 56:
        if parity > 1:
            DBW = (BWR * 690 * ((WIM + 0.57) ** (-0.0803)) *
                   exp(0.00720 * (WIM + 0.57)))
        else:
            DBW = (BWR * 567 * ((WIM + 0.71) ** (-0.730)) *
                   exp(0.00869 * (WIM + 0.71)))

        # change in body weight (kg/d)
        CBW = (BW - DBW) / 7

    #
    # Estimate eMEIrgy equivalent of Change in Bodyweight
    #
    if WIM < 11:
        CS = 3.4
    else:
        CS = 5  # change eMEIrgy value depending on stage in lactation
    MEIKG = 0.5381 * CS + 3.2855  # MEIt eMEIrgy in deposited or mobilized body (Mcal/kg bw) tissue

    if CBW < 0:
        MECBW = MEIKG * CBW / 0.785 / 100
    else:
        MECBW = MEIKG * CBW / 0.75 / 100

    #
    # Estimate Maintenance EMEIrgy Req
    # MEIeds: BW
    #
    SBW = 0.96 * BW
    MEIM = 0.073 * (SBW ** 0.75)

    #
    # Estimate Activity EMEIrgy Rew
    # set number of hours, position changes and distances traveled
    # if housed in a barn, drylot or grazing
    #
    if housing == "barn":
        hours = 12
        posHG = 9
        flat_dist = 0.5
        slope_dist = 0.001
    elif housing == "drylot":
        hours = 15
        posHG = 9
        flat_dist = 1.5
        slope_dist = 0.001
    else:
        hours = 16
        posHG = 6
        flat_dist = 1.0
        slope_dist = 0.0

    stand = 0.1 * hours * SBW / 0.96
    chang = 0.062 * posHG * SBW / 0.96
    dist_F = 0.621 * flat_dist * SBW / 0.96
    dist_S = 6.69 * slope_dist * SBW / 0.96
    MEIACT = (stand + chang + dist_F + dist_S) / 1000

    #
    # Estimate Maintenance Protein Req
    #
    MPM = 3.8 * SBW ** 0.75  # g metabolizable protein for maintenance

    #
    # Estimate lacatation eMEIrgy and protein Req
    # MEIeds: base_MY, base_MF
    #
    ME_mlk = base_MY * (0.3523 + 0.0962 * base_MF) / 0.644  # Mcal ME required for milk
    PROT_mlk = 1.9 + 0.4 * base_MF  # milk protein %
    MP_mlk = 10 * PROT_mlk * base_MY / 0.65  # g metabolizable protein for milk

    #
    # Sum total requirements
    # MEIeds: MEIM, MEIACT, ME_mlk, MECBW, MPM
    #
    ME_req = MEIM / 0.667 + MEIACT / 0.667 + ME_mlk + MECBW  # total ME req (Mcal)
    MP_req = MPM + MP_mlk  # total MP rew (g)

    #
    # Estimate Rumen degradable and undegradable protein
    # MEIeds: base_NED, ME_req
    #
    base_MED = 1.095 * base_NED + 0.751  # BaseMED is the baseliMEI Metabolizable eMEIrgy of the diet
    DMI_est = ME_req / base_MED
    TDN = 0.31 * base_NED + 0.2  # Total digestible Nutrients (TDN) is a measure of diet quality/content used the the NRC
    MCP = 0.13 * TDN * DMI_est  # MCP is microbial crude protein

    # Set Constraints limits based on requirements and intake capacity
    # (RHS of constraints matrix)
    # MEIeds: BW, FIC, base_NED, DMI_est, MP_req, MCP

    FI_max = 0.01025 * BW * FIC
    RV_min = 0
    NE_min = base_NED * DMI_est * (1 - 0.0206) - 0.7 * MP_req / 1000
    RDP_min = MCP / 0.9
    RUP_min = MP_req / 1000 - 0.8 * 0.8 * MCP

    # The order of this list needs to correspond with the order of the nutrients
    # in feed.nutrient_types. If not, the LHS constraints will not pair up
    # with the correct RHS values.
    nutrient_rqmts = [
        {'op': '<=', 'val': FI_max},
        {'op': '>=', 'val': NE_min},
        {'op': '>=', 'val': RDP_min},
        {'op': '>=', 'val': RUP_min},
        {'op': '>=', 'val': RV_min}
    ]

    return dict(zip(nutrients_list, nutrient_rqmts))

def calculate_ME_RDP_RUP(feed, DMIest, BW, DBW):
    '''
    Calculates some of the Feed Composition values, which are the LHS multipliers
    in the LP

	Args:
        feed: an instance of the feed class
        DMIest: dry matter intake estimation
        BW: body Weight
        DBW: change in body weight

    Returns:
        three lists, where each element in each list is the respective value for
            ME_DM, RDP_DM, and RUP_DM for each feed
    '''
    ME_DM_arr = []
    RDP_DM_arr = []
    RUP_DM_arr = []
    DMI_BW = DMIest / BW
    for feed_name in feed.available_feed_names:
        #Obtains the necessary values from the particular feed for the calculations
        Ash_DM = feed.available_feeds[feed_name]['Ash_DM']
        CP_DM = feed.available_feeds[feed_name]['CP_DM']
        dFA_FA_base = feed.available_feeds[feed_name]['dFA_FA_base']
        dRUP_RUP = feed.available_feeds[feed_name]['dRUP_RUP']
        dStarch_Starch_base = feed.available_feeds[feed_name]['dStarch_Starch_base']
        FA_DM = feed.available_feeds[feed_name]['FA_DM']
        FU = feed.available_feeds[feed_name]['FU']
        IVNDFD_NDF = feed.available_feeds[feed_name]['IVNDFD_NDF']
        NDF_DM = feed.available_feeds[feed_name]['NDF_DM']
        NDIP_DM = feed.available_feeds[feed_name]['NDIP_DM']
        RU = feed.available_feeds[feed_name]['RU']
        RUP_CP = feed.available_feeds[feed_name]['RUP_CP']
        Starch_DM = feed.available_feeds[feed_name]['Starch_DM']
        sNPNCPE_DM = feed.available_feeds[feed_name]['sNPNCPE_DM']

        #Neutral detergent fiber (NDF) (A.FE.1.1)
        dNDF_NDF_base = 0.12 + 0.61 * IVNDFD_NDF
        #Digested NDF, proportion of NDF (A.FE.1.2)
        dNDF_NDF = dNDF_NDF_base - 0.43 * (Starch_DM - 0.26) - 0.3 * (DMI_BW - 0.035)

        #Digested Starch (A.FE.2.1)
        dStarch_Starch = dStarch_Starch_base - 1.0 * (DMI_BW - 0.035)

        #Digested rumen undegradable protien (A.FE.3.1)
        dRUP_DM = CP_DM * RUP_CP * dRUP_RUP
        #Digested CP (A.FE.3.2)
        RDP_DM = CP_DM * (1 - RUP_CP)
        dCP_CP = (RDP_DM + dRUP_DM) / CP_DM

        #Residual Organic Matter (ROM) (A.FE.4.1)
        if feed_name == 'Fatty acid' or feed_name == 'FA Soap':
            FatFactor = 1
        else:
            FatFactor = 1.06
        ROM_DM = 1 - Ash_DM - NDF_DM - Starch_DM - FA_DM / FatFactor - (CP_DM - 0.64 * sNPNCPE_DM)
        #Digested ROM (A.FE.4.2)
        dROM_ROM = 0.96

        #Digested failatty acids (A.FE.5.1)
        dFA_FA = dFA_FA_base - 0.8 * (DMI_BW - 0.035)

        #Endogenous fecal materials (A.FE.6.1)
        NDF_DMI = NDF_DM / DMIest
        efCP_DM = 0.0116 + 0.0134 * NDF_DMI
        efROM_DM = 0.0343

        #Digested energy per unit DM (A.FE.7.1)
        DE_DM = 4.2 * NDF_DM * dNDF_NDF \
            + 4.23 * Starch_DM * dStarch_Starch \
            + 9.40 * FA_DM * dFA_FA \
            + 5.65 * (RDP_DM - sNPNCPE_DM + dRUP_DM) \
            + 0.89 * sNPNCPE_DM \
            + 4.00 * ROM_DM * dROM_ROM \
            - 5.65 * efCP_DM \
            - 4.00 * efROM_DM

        #Gas energy loss, mCal/kg of DM (A.FE.8.2)
        GasE_DM = 0.294 - 3.5 * FA_DM + 4.1 * (NDF_DM - NDIP_DM) * IVNDFD_NDF
        #Urine energy loss per day, mCal (A.FE.8.3)
        DE = DE_DM * DMIest
        UE = 0.00275 * (BW ** 0.75) + 0.0177 * DE + 0.00813 * UN
        #Appararently digested CP (A.FE.8.4)
        adCP_CP = dCP_CP - (efCP_DM / CP_DM)
        #Urine energy loss, mCal/kg (A.FE.8.5)
        Body_gain_CP = DBW * 0.072
        UN = (DMIest * CP_DM * adCP_CP - Milk * CP_MIlk - Body_gain_CP) * 1000 / 6.25
        UE_DM = UE / DMIest #(A.FE.8.6)
        #Metabolized energy per unit DM (A.FE.8.1)
        ME_DM = DE_DM - GasE_DM - UE_DM

        #Conversion between ME and NE (A.FE.9.1)
        NEL_DM = 0.68 * ME_DM

        ME_DM_arr.append(ME_DM)
        RDP_DM_arr.append(RDP_DM)
        RUP_DM_arr.append(RUP_CP * CP_DM)

    return ME_DM_arr, RDP_DM_arr, RUP_DM_arr
