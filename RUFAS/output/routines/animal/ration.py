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
    for nutrient_type in feed.nutrient_rqmts:
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
    upper_bounds = [feed.available_feeds[feed_name]['Limit']
                    for feed_name in feed.available_feed_names]

    # util.LP_print(LHS, RHS, objective, var_names, operators,
    #			  "minimize", "RATION", lower_bounds, upper_bounds)

    return util.LP_solve(LHS, RHS, objective, var_names, operators,
                         "minimize", "RATION", lower_bounds, upper_bounds)


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
