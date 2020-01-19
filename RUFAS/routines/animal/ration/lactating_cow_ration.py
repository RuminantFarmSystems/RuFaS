################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: lactating_cow_ration.py
Description: Calculates the ration for lactating cows.
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Militsa Sotirova, militsasotirova@gmail.com
"""
################################################################################

from numpy import exp
from RUFAS import util
import math
from RUFAS.routines.feed.feed import NutrientValues, Nutrients, Feeds
from typing import List, Dict

# These values are needed and calculated in calculate_rqmts() but they are also
# needed in optimize(), so when they are calculated in calculate_rqmts(),
# these global variables keep track of their values in order to minimize code
# repetition. They are initialized to -1 for debugging purposes.

global_BW = -1
global_DMIest = -1
global_DBW = -1
global_milk = -1
global_CP_Milk = -1


def set_globals(DMIest, BW, DBW, milk, CP_milk):
    """
    Sets the global variables with averages from pen.
    Args:
        DMIest: dry matter intake estimation, kg
        BW: body weight, kg
        DBW: Body weight change (delta body weight = DBW), kg
        milk: milk production, kg
        CP_Milk: milk crude protein content
    """
    global global_BW
    global global_DMIest
    global global_DBW
    global global_milk
    global global_CP_Milk

    global_DMIest = DMIest
    global_BW = BW
    global_DBW = DBW
    global_milk = milk
    global_CP_Milk = CP_milk


def optimize(feed, rqmts):
    """
    Sets up the arguments for the linear programming optimization.

    Args:
<<<<<<< HEAD:RUFAS/routines/animal/ration/lactating_cow_ration.py
        feed : instance of the Feed class
        rqmts : dict which represents the dietary requirements of the cows
=======
	    feed : instance of the Feed class
	    rqmts : dict which represents the dietary requirements of the cows
>>>>>>> 9eaa8c2b3a37d66bc578382a7a7abfe0994a8877:RUFAS/routines/animal/ration.py

    Returns:
        dict: the dictionary that is returned by the call to util.LP_solve()
    """

    # LHS is of the following form. LHS stands for Left Hand Side.
    # [
    #     [##,##, ..., ##],  // Each column has the coefficients for one specific feed type
    #     [##,##, ..., ##],  // Each row has the coefficients for one specific nutrient type
    #     [##,##, ..., ##],  // Each row represents the LHS of a constraint equation
    #     [##,##, ..., ##],
    #     [##,##, ..., ##]
    # ]

    LHS = []
    constraint = [percentage(feed.available_feeds[feed_name]['FU'])
                  for feed_name in feed.available_feed_names]
    LHS.append(constraint)

    constraint = [(percentage(feed.available_feeds[feed_name]['RU']) - 0.21)
                  for feed_name in feed.available_feed_names]
    LHS.append(constraint)

    ME_DM_arr, RDP_DM_arr, RUP_DM_arr = calculate_ME_RDP_RUP(feed, global_DMIest, global_BW, global_DBW, global_milk,
                                                             global_CP_Milk)
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
    RHS = [rqmts[nutrient]['val'] for nutrient in feed.nutrient_rqmts]

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
    operators = [rqmts[nutrient]['op'] for nutrient in feed.nutrient_rqmts]

    # The lower bounds for quantity of a food type are zero since a negative
    # quantity of food in this context does not make sense.
    lower_bounds = [0] * len(feed.available_feed_names)

    # The upper bounds are the 'Limit' specified in the csv library for each
    # food type.
    upper_bounds = [feed.available_feeds[feed_name]['Limits']
                    for feed_name in feed.available_feed_names]

    # util.LP_print(LHS, RHS, objective, var_names, operators, "minimize", "RATION", lower_bounds, upper_bounds)

    return util.LP_solve(LHS, RHS, objective, var_names, operators, "minimize", "RATION", lower_bounds, upper_bounds)

def calculate_rqmts(BW, BCS, CBW, CI, pasture_concentrate, CP_Milk, DOP, DHD, DVD,
                    DIM, fat_milk, lactose_milk, milk, parity, type, nutrients_list):
    """
    Calculate the dietary requirements of the cows. These values are used
    on the RHS of the linear program. Each calculation has a reference to the
    respective calculation in the pseudocode.

    Args:
        BW: body weight, kg
        BCS: body condition score, 1 to 5
        CBW: calf birth weight, kg
        CI: calving interval, days
        pasture_concentrate: concentrate supplementation when farming type is "pasture", kg
        CP_Milk: milk crude protein content
        DOP: days of pregnancy, days
        DHD: daily horizontal distance, km
        DVD: daily vertical distance, km
        DIM: days in milk, days
        fat_milk: milk fat content
        lactose_milk: milk lactose content
        milk: milk production, kg
        parity: number of times birth was given
        type: farming type, "barn" or "pasture"
        nutrients_list: a list of the nutrients for which requirements are calculated

    Returns:
        dict : a dictionary that represents the dietary requirements of the cows,
            where the left hand side is nutrients_list and the right hand side is
            calculated in this method
        DMIest: dry matter intake estimation, kg
        DBW: Body weight change (delta body weight = DBW), kg
    """

    # Sets these variables as global. See comment at the beginning of this file for further details.
    global global_BW
    global global_DMIest
    global global_DBW
    global global_milk
    global global_CP_Milk

    global_BW = BW
    global_milk = milk
    global_CP_Milk = CP_Milk
    # ENERGY REQUIREMENTS (divided into the following 5 components: maintenance,
    # lactation, activity, pregnancy, and body weight change requirements):

    # Maintenance requirements
    # ------------------------
    # Ideal Body Weight, kg (A.ER.1.2)
    IBW = BW / (0.65 + 0.1 * BCS)
    # Net Energy maintenance, Mcal (A.ER.1.1)
    NEm = 0.10 * (IBW ** 0.75)

    # Lactation requirements
    # ----------------------
    # Net Energy lactation, Mcal (A.ER.2.1)
    NEl = (9.29 * milk * fat_milk + 5.5 * milk * CP_Milk + 3.95 * milk * lactose_milk) / 100

    # Activity requirements
    # ---------------------
    # Net Energy activity, Mcal (A.ER.3.1)
    if type == "barn":
        NEact = (DHD * 0.35 * BW + DVD * 5 * BW) / 1000
    elif type == "pasture":
        NEact = (DHD * 0.35 * BW + DVD * 5 * BW + 10 * (BW ** 0.75) * ((600 - 12 * pasture_concentrate) / 600)) / 1000

    # Pregnancy energy requirements
    # -----------------------------
    # Net Energy pregnancy, Mcal (A.ER.4.1)
    if DOP < 190:
        NEpreg = 0
    elif DOP >= 190 and DOP <= 279:
        NEpreg = ((0.00318 * DOP - 0.0352) * (CBW / 45)) / 0.218
    else:
        NEpreg = ((0.00318 * 279 - 0.0352) * (CBW / 45)) / 0.218

    # Body Weight change requirements
    # -------------------------------
    # Target Calving Weight, kg (A.ER.5.1)
    if parity == 1:
        TCW = 700 * 0.85
    elif parity == 2:
        TCW = 700 * 0.92
    elif parity == 3:
        TCW = 700 * 0.96
    elif parity > 3:
        TCW = 700 * 1
    # Body weight change (delta body weight = DBW), kg (A.ER.5.4)
    DBW = 0  # (TCW - 0.94 * BW) / (280 - CI + DOP)
    global_DBW = DBW
    # Net Energy body weight, Mcal (A.ER.5.5)
    if DBW > 0:
        NEbw = DBW * 6.7 * 0.88
    else:
        NEbw = DBW * 6.7 * 0.85

    # Total energy requirements, mCal (A.ER.6.1)
    TNEL = NEm + NEl + NEact + NEpreg + NEbw

    # FEED INTAKE
    # Dry Matter Intake estimation, kg (A.FI.1.1)
    if DIM > 100:
        DMIest = 2.58 + 0.30 * NEl + 0.027 * BW + 0.05 * DBW - 1.15 * BCS
    else:
        DMIest = (2.58 + 0.30 * NEl + 0.027 * BW) * (1 - exp(-0.192 * ((DIM + 3.5) / 7 + 3.67)))
    global_DMIest = DMIest
    # Fiber Intake Capacity, Fiber Units/day (A.FI.2.2)
    # Weeks in milk
    WIM = math.ceil(DIM / 7)
    if parity == 1:
        FIC = 0.338 * ((WIM + 3) ** 0.588) * exp(-0.0277 * (WIM + 3))
    elif parity > 1:
        FIC = 0.564 * ((WIM + 0.857) ** 0.36) * exp(-0.0186 * (WIM + 0.857))
    # Maximum Fiber Intake (A.FI.2.3)
    FIMax = 0.01025 * BW * FIC

    # PROTEIN REQUIREMENTS - temporarily based on IFSM, will be replaced with NRC
    # Metabolize protein required for maintenance per day, g (A.PR.1.1)
    MPM = 3.8 * ((0.96 * BW) ** 0.75)
    # Metabolize protein required for lactation per day, g (A.PR.2.1)
    MPMLK = 10 * CP_Milk * milk / 0.65
    # Microbial crude protein, kg (A.PR.3.1)
    MCP = 0.13 * 0.51 * DMIest
    # Rumen degradable (RDPreq, kg) and undegradable protein (RUPreq, kg) requirements
    RDPreq = MCP / 0.9  # (A.PR.3.2)
    MPreq = MPM + MPMLK  # (A.PR.3.3)
    RUPreq = MPreq / 1000 - 0.8 * 0.8 * MCP  # (A.PR.3.4)

    RU_min = 0

    nutrient_rqmts = [
        {'op': '<=', 'val': FIMax},  # (A.LP.2.1)
        {'op': '>=', 'val': RU_min},  # (A.LP.2.2)
        {'op': '>=', 'val': TNEL / 0.68},  # (A.LP.2.3)
        {'op': '>=', 'val': RDPreq},  # (A.LP.2.4)
        {'op': '>=', 'val': RUPreq}  # (A.LP.2.5)
    ]

    return dict(zip(nutrients_list, nutrient_rqmts)), DMIest, DBW


def calculate_ME_RDP_RUP(feed, DMIest, BW, DBW, milk, CP_Milk):
    """
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
    """
    ME_DM_arr = []
    RDP_DM_arr = []
    RUP_DM_arr = []
    DMI_BW = DMIest / BW
    #
    for managed_feed in feed.managed_feeds:
        nutrients: Dict[str, float] = feed.values(managed_feed, False)
        Ash_DM = nutrients[Nutrients.Ash_DM.name]
        print('ash: ', Ash_DM)
        CP_DM = nutrients[Nutrients.CP_DM.name]
        print('cp: ', CP_DM)
    #
    for feed_name in feed.available_feed_names:
        # Obtains the necessary values from the particular feed for the calculations
        Ash_DM = feed.available_feeds[feed_name]['Ash_DM']
        CP_DM = feed.available_feeds[feed_name]['CP_DM']
        dFA_FA_base = feed.available_feeds[feed_name]['dFA_FA_base']
        dRUP_RUP = feed.available_feeds[feed_name]['dRUP_RUP']
        dStarch_Starch_base = feed.available_feeds[feed_name]['dStarch_Starch_base']  # basic starch digestibility
        FA_DM = feed.available_feeds[feed_name]['FA_DM']
        FU = feed.available_feeds[feed_name]['FU']
        IVNDFD_NDF = feed.available_feeds[feed_name]['IVNDFD_NDF']
        NDF_DM = feed.available_feeds[feed_name]['NDF_DM']
        NDIP_DM = feed.available_feeds[feed_name]['NDIP_DM']
        RU = feed.available_feeds[feed_name]['RU']
        RUP_CP = feed.available_feeds[feed_name]['RUP_CP']
        Starch_DM = feed.available_feeds[feed_name]['Starch_DM']
        sNPNCPE_DM = feed.available_feeds[feed_name]['sNPNCPE_DM']

        # Neutral detergent fiber (NDF) (A.FE.1.1)
        dNDF_NDF_base = 0.12 + 0.61 * percentage(IVNDFD_NDF)
        # Digested NDF, proportion of NDF (A.FE.1.2)
        dNDF_NDF = dNDF_NDF_base - 0.43 * (percentage(Starch_DM) - 0.26) - 3.0 * (DMI_BW - 0.035)

        # Digested Starch (A.FE.2.1)
        dStarch_Starch = dStarch_Starch_base - 1.0 * (DMI_BW - 0.035)

        # Digested rumen undegradable protein (A.FE.3.1)
        dRUP_DM = CP_DM * percentage(RUP_CP) * dRUP_RUP
        # Digested CP (A.FE.3.2)
        RDP_DM = CP_DM * (1 - percentage(RUP_CP))
        dCP_CP = (RDP_DM + dRUP_DM) / CP_DM

        # Residual Organic Matter (ROM) (A.FE.4.1)
        if feed_name == 'Fatty acid' or feed_name == 'FA Soap':
            FatFactor = 1
        else:
            FatFactor = 1.06
        ROM_DM = 100 - Ash_DM - NDF_DM - Starch_DM - FA_DM / FatFactor - (CP_DM - 0.64 * sNPNCPE_DM)
        # Digested ROM (A.FE.4.2)
        dROM_ROM = 0.96

        # Digested fatty acids (A.FE.5.1)
        dFA_FA = dFA_FA_base - 0.8 * (DMI_BW - 0.035)

        # Endogenous fecal materials (A.FE.6.1)
        NDF_DMI = NDF_DM / DMIest
        efCP_DM = 0.0116 + 0.0134 * percentage(NDF_DMI)
        # Endogenous fecal ROM (A.FE.6.2)
        efROM_DM = 0.0343

        # Digested energy per unit DM (A.FE.7.1)
        DE_DM = 4.2 * NDF_DM * percentage(dNDF_NDF) + 4.23 * Starch_DM * percentage(
            dStarch_Starch) + 9.40 * FA_DM * percentage(dFA_FA) + 5.65 * CP_DM * percentage(dCP_CP) + 0.89 * percentage(
            sNPNCPE_DM) + 4.00 * ROM_DM * percentage(dROM_ROM) - 5.65 * efCP_DM - 4.00 * efROM_DM

        # Gas energy loss, mCal/kg of DM (A.FE.8.2)
        GasE_DM = (0.294 * DMIest - 0.35 * FA_DM + 0.041 * NDF_DM * dNDF_NDF) / DMIest
        # Apparently digested CP (A.FE.8.4)
        adCP_CP = dCP_CP - (efCP_DM * 100 / CP_DM)
        Body_gain_CP = DBW * 0.072
        # (A.FE.8.6)
        UE_DM = 0.00275 * (BW ** 0.75) / DMIest + 0.0177 * DE_DM + 0.00813 * percentage(
            CP_DM) * adCP_CP * 1000 / 6.25 - (
                        0.00813 * (milk * percentage(CP_Milk) + Body_gain_CP) * 1000 / 6.25) / DMIest
        # Apparently digested CP (A.FE.8.4)
        adCP_CP = dCP_CP - (efCP_DM / CP_DM)
        # Metabolized energy per unit DM (A.FE.8.1)
        ME_DM = DE_DM - GasE_DM - UE_DM

        # Conversion between ME and NE (A.FE.9.1)
        NEL_DM = 0.68 * ME_DM

        ME_DM_arr.append(ME_DM)
        RDP_DM_arr.append(percentage(RDP_DM))
        RUP_DM_arr.append(percentage(RUP_CP) * percentage(CP_DM))

    return ME_DM_arr, RDP_DM_arr, RUP_DM_arr


def percentage(val):
    """
    Calculates the true value of a percentage.

    Args:
        val: a number

    Returns:
        0.01 multiplied by val
    """
    return 0.01 * val
