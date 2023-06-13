"""
RUFAS: Ruminant Farm Systems Model
File name: ration_NLP.py
Description: Calculates the ration for animals using a Non-Linear
    programming method utilizing the scipy package. The NLP is formulated using
    constraint functions. Note NLP (Non-linear Program) will be used throughout
    descriptions for functions in this file.
Author(s):
    Chris VanKerkhove, cjv47@cornell.edu
"""
import numpy as np
import random
from scipy.optimize import minimize
from typing import Dict, List

from RUFAS.routines.animal.animal_module_constants import AnimalModuleConstants

from RUFAS.routines.animal.ration.user_defined_ration import UserDefinedRationManager as UserDefinedRationManager
udrv = UserDefinedRationManager()

def set_globals(price_, NEmaint_, NEa_, NEpreg_, NEl_, NEg_, MP_req_, C_req_, P_req_,
                 TDN_, DE_, EE_, is_fat_, BW_, calcium_, phosphorus_, NDF_, type_,
                 is_wetforage_, Kd_, N_A_, N_B_, CP_, dRUP_, limit_, cow_type_,
                 DMIest_= None):
    """
    Sets the global variables with the feed information to be used in the
    constraint functions below. If the input described below is a list, it is a
    list with a length of the decision vector.

    Args:
        price_: A list of the price of each feed
        NEmaint_: Net energy for maintenance requirement (Mcal)
        NEa_: Net energy for activity requirement (Mcal)
        NEpreg_: Net energy requirement for pregnancy (Mcal)
        NEl_: Net energy requirement for lactation (Mcal)
        NEg_: Net energy for growth requirement (Mcal)
        MP_req_: Metabolizable protein requirement for growth (g)
        C_req_: Calcium requirement (g)
        P_req_: Phosphorus requirement (g)
        DMIest_: dry matter intake estimation (kg)
        TDN_: A list of otal digestible nutrient in each feed (% of DM)
        DE_: A list of digestible energy in each feed (Mcal/kg)
        EE_: A list of ether extract, crude fat in each feed (% of DM)
        is_fat_: A list of booleans, if the feed is fat supplement or not
                (yes = 1; no = 0)
        BW_: the average body weight of the pen
        calcium_: A list of the calcium content of each feed (% of DM)
        phosphorus_: A list of phosphorus content of each feed (% of DM)
        NDF_: A list of neutral detergent fiber in each feed (% of DM)
        type_: A list of feed types (Forage, Concentrate, or Mineral)
        is_wetforage_: A list of booleans, if the feed is wet forage or not
                    (yes = 1; no = 0)
        Kd_: A list of the rumen protein degradation rate in each feed (%/h)
        N_A_: A list of fraction A of protein, degraded immediately in rumen for
            each feed (% of CP)
        N_B_: A list of fraction B of protein, potentially degradable protein,
            require time to generally degrade in rumen in each feed (% of CP)
        CP_: A list of crude protein in each feed (% of DM)
        dRUP_: A list of RUP degradability in each feed (% of RUP)
        limit_: A list of the limiting upper bounds for each feed (kg)
        cow_type_: A boolean which is True if cow is lactating, False else
    """
    global price, n, NEmaint, NEa, NEpreg, NEl, NEg, MP_req, C_req, P_req, \
        DMIest, TDN, DE, EE, is_fat, BW, calcium, phosphorus, NDF, type, \
        is_wetforage, Kd, N_A, N_B, CP, dRUP, limit, cow_type

    price = price_
    n = len(price)
    NEmaint = NEmaint_
    NEa = NEa_
    NEpreg = NEpreg_
    NEl = NEl_
    NEg = NEg_
    MP_req = MP_req_
    C_req = C_req_
    P_req = P_req_
    DMIest = DMIest_
    TDN = TDN_
    DE = DE_
    EE = EE_
    is_fat = is_fat_
    BW = BW_
    calcium = calcium_
    phosphorus = phosphorus_
    NDF = NDF_
    type = type_
    is_wetforage = is_wetforage_
    Kd = Kd_
    N_A = N_A_
    N_B = N_B_
    CP = CP_
    dRUP = dRUP_
    limit = limit_
    cow_type = cow_type_


def list_reconfig(list):
    """
    Helper function that takes an input of a list and returns that list with
    each value occuring a total of 3 times consecutively. This method is
    required for matching the decision variables to one of the three energy
    constraint.

    Args:
        list: A list of values
    """
    list_reconfig = []
    for i in list:
        list_reconfig.append(i)
        list_reconfig.append(i)
        list_reconfig.append(i)
    return list_reconfig


def objective(x):
    """
    Sets up the objective function in the optimize function for the non-linear
    program. Whenever the paramert x is used, it refers to the "decision vetor
    of the NLP" which means it is a list of solutions where each value in the
    list corresponds to the amount of a given feed (kg) in the formulated diet.
    The goal of this NLP is to minimize the cost of all feeds while satisfying
    all "constraints", which just means the diet fulfills the average nutrient
    requirements in the pen.

    Args:
        x: The decision vector of the NLP
    """
    return sum(np.multiply(x, price))


def NEmact_constraint(x):
    """
    Sets up the RHS multipliers for the maintenance and activity requirements
    satisfied by the feed. Each equation has a reference to the respective
    calculation in the pseudo code. The global variables defined in the begining
    of this function are used in future functions.

    Args:
        x: The decision vector of the NLP
    """
    global MEact
    global TDNact
    global DEact
    # DMI calculated by the NLP
    DMI = sum(x)
    # Dietary TDN content, kg
    TotalTDN = sum(np.multiply(x, TDN))
    TotalTDN = np.multiply(TotalTDN, 0.01)
    # [A.Cow.E.1]-[A.Heifer.E.1]
    # TDN concentration, %
    if DMI != 0:
        TDNconc = (TotalTDN / DMI) * 100
    else:
        TDNconc = 0
    SBW = BW * 0.96
    # [A.Cow.E.2]-[A.Heifer.E.2]
    # The amount of intake needed to meet the maintenance requirement, dimensionless
    if TotalTDN < (0.035 * BW ** 0.75):
        DMI_to_maint = 1
    else:
        DMI_to_maint = (TotalTDN / (0.035 * SBW ** 0.75))
    # [A.Cow.E.3]-[A.Heifer.E.3]
    # TDN discount, TDN digestibility decrease caused by DMI and TDNconc
    if TDNconc < 60:
        Discount = 1
    else:
        Discount = (TDNconc - ((0.18 * TDNconc - 10.3) * (DMI_to_maint - 1))) / TDNconc
    # [A.Cow.E.4]-[A.Heifer.E.4]
    # Actual TDN content of feed i, %
    TDNact = np.multiply(TDN, Discount)
    # [A.Cow.E.5]-[A.Heifer.E.5]
    # Actual digestible energy of feed i, Mcal/kg
    DEact = np.multiply(DE, Discount)
    # [A.Cow.E.6]-[A.Heifer.E.6]
    # Actual metabolizable energy of feed i, Mcal/kg
    MEact = []
    for i in range(len(DEact)):
        if type[i] == 'Mineral':
            MEact.append(0)
        elif is_fat[i] == 1:
            MEact.append(DE[i])
        elif EE[i] >= 3:
            MEact.append(1.01 * DEact[i] - 0.45 + 0.0046 * (EE[i] - 3))
        else:
            MEact.append(1.01 * DEact[i] - 0.45)
    # [A.Cow.E.8]-[A.Heifer.E.8]
    # Actual net energy for maintenance of feed i, Mcal/kg
    NEm_act = []
    for i in range(len(MEact)):
        if is_fat[i] == 1:
            NEm_act.append(0.8 * MEact[i])
        else:
            NEm_act.append(1.37 * MEact[i] - 0.138 * MEact[i] ** 2 + 0.0105 * MEact[i] ** 3 - 1.12)
    # Constraining to only allow each feed to only satisfy a single energy constraint
    multiplier = []
    for i in range(int(n / 3)):
        multiplier.append(1)
        multiplier.append(0)
        multiplier.append(0)
    # returning the NEm_act constraint in the NLP
    return (sum(np.multiply(x, np.multiply(multiplier, NEm_act))) - (NEmaint + NEa))


def NEl_constraint(x):
    """
    Sets up the RHS multipliers for the lactation and pregnancy requirements
    satisfied by each feed. Each calculation has a reference to the respective
    calculation in the pseudocode. Note to eliminate code repetition the global
    variable MEact is used (calculated in NEmact_constraint).

    Args:
        x: The decision vector of the NLP
"""
    # Actual net energy for lactation of feed i, Mcal/kg
    NElact = []
    # [A.Cow.E.7]-[A.Heifer.E.7]
    for i in range(len(MEact)):
        if type[i] == 'Mineral':
            NElact.append(0)
        elif is_fat[i] == 1:
            NElact.append(0.8 * DEact[i])
        elif EE[i] >= 3:
            NElact.append(0.703 * MEact[i] - 0.19 + ((0.097 * MEact[i] + 0.19) / 97) * (EE[i] - 3))
        else:
            NElact.append(0.703 * MEact[i] - 0.19)
    # Constraining to only allow each feed to only satisfy a single energy constraint
    multiplier = []
    for i in range(int(n / 3)):
        multiplier.append(0)
        multiplier.append(1)
        multiplier.append(0)
    # returning the NElact constraint in the NLP
    return sum(np.multiply(x, np.multiply(multiplier, NElact))) - (NEpreg + NEl)


def NEgact_constraint(x):
    """
    Sets up the RHS multipliers for the growth requirements satisfied by each
    feed. Each calculation has a reference to the respective calculation in the
    pseudocode. Note to eliminate code repetition the global variable MEact is
    used (calculated in NEmact_constraint).

    Args:
        x: The decision vector of the NLP
    """
    # Actual net energy for growth of feed i, Mcal/kg
    NEgact = []
    # [A.Cow.E.9]-[A.Heifer.E.9]
    for i in range(len(MEact)):
        if type[i] == 'Mineral':
            NEgact.append(0)
        elif is_fat[i] == 1:
            NEgact.append(0.55 * MEact[i])
        else:
            NEgact.append(1.42 * MEact[i] - 0.174 * MEact[i] ** 2 + 0.0122 * MEact[i] ** 3 - 1.65)
    # Constraining to only allow each feed to only satisfy a single energy constraint
    multiplier = []
    for i in range(int(n / 3)):
        multiplier.append(0)
        multiplier.append(0)
        multiplier.append(1)
    # returning the NEgact constraint in the NLP
    return sum(np.multiply(x, np.multiply(multiplier, NEgact))) - NEg


def calcium_constraint(x):
    """
    Sets up the RHS multipliers for the calcium requirements satisfied by each
    feed. Each calculation has a reference to the respective calculation in the
    pseudocode. Note the calculated calcium requirement 'C_req' is in grams and
    x is in kg thus the divide by 1000.

    Args:
        x: The decision vector of the NLP
    """
    # Ca digestibility of feed i (proportion of Ca)
    dCa = []
    for i in range(len(type)):
        if type[i] == 'Forage':
            dCa.append(.3)
        elif type[i] == 'Conc':
            dCa.append(.6)
        elif type[i] == 'Mineral':
            dCa.append(.95)
        else:
            dCa.append(0)
    # [A.Cow.E.16]-[A.Heifer.E.16]
    return (sum(np.multiply(x, np.multiply(np.multiply(calcium, 0.01), dCa))) - (C_req / 1000))


def phosphorus_constraint(x):
    """
    Sets up the RHS multipliers for the phosphorus requirements satisfied by each
    feed. Each calculation has a reference to the respective calculation in the
    pseudocode. Becasue the maintenance requirement contains non-linearity
    properties, that requirement will be calculated in this function. Note the
    calculated phosphorus requirement 'P_req' is in grams and x is in kg thus
    the divide by 1000.

    Args:
        x: The decision vector of the NLP
    """
    DMI = sum(x)
    # P digestibility of feed i (proportion of P)
    dP = []
    for i in range(len(type)):
        if type[i] == 'Forage':
            dP.append(.64)
        elif type[i] == 'Conc':
            dP.append(.70)
        elif type[i] == 'Mineral':
            dP.append(0.80)
        else:
            dP.append(0)
    # Phosphorus Requirements
    # ----------------------
    # [A.Cow.C.6]-[A.Heifer.C.5]
    # Phosphorus maintenance requirement (g)
    if cow_type:
        #lactating cows
        P_maint = 1 * DMI + 0.002 * BW
    else:
        #all other animals
        P_maint = 0.8 * DMI + 0.002 * BW
    # [A.Cow.E.16]-[A.Heifer.16]
    return sum(np.multiply(x, np.multiply(np.multiply(phosphorus, 0.01), dP))) - ((P_req + P_maint) / 1000)


def protein_constraint(x):
    """
    Sets up the protein requirement constraint in the NLP. Because part of the
    maintenance requirement for protein contains non-linearity properties, that
    requirement will be calculated in this function. Each calculation has a
    reference to the respective calculation in the pseudocode.

    Args:
        x: The decision vector of the NLP.
    """
    DMI = sum(x)
    # Boolean values to identify if feed is a concentrate
    is_conc = []
    for i in range(len(type)):
        if type[i] == 'Conc':
            is_conc.append(1)
        else:
            is_conc.append(0)
    # Dietary concentrate percentage (% of DM)
    if DMI != 0:
        PercentConc = (sum(np.multiply(x, is_conc)) / DMI) * 100
    else:
        PercentConc = 0
    # [A.Cow.E.10]-[A.Heifer.E.10]
    # Protein passage rate of feed i (%/h)
    Kp = []
    for i in range(len(type)):
        if type[i] == 'Conc':
            Kp.append(2.904 + 1.375 * (DMI / BW) * 100 - 0.02 * PercentConc)
        elif type[i] == 'Forage' and is_wetforage[i] == 0:
            Kp.append(3.362 + 0.479 * (DMI / BW) * 100 - 0.017 * NDF[i] - 0.007 * PercentConc)
        elif is_wetforage[i] == 1:
            Kp.append(3.054 + 0.614 * (DMI / BW) * 100)
        else:
            Kp.append(0)
    # [A.Cow.E.11]-[A.Heifer.E.11]
    # Rumen degradable protein of feed i (% of DM)
    RDP = []
    for i in range(len(Kd)):
        if Kp[i] > -Kd[i]:
            RDP.append((Kd[i] / (Kd[i] + Kp[i])) * (N_B[i] / 100) * CP[i] + (N_A[i] / 100) * CP[i])
        else:
            RDP.append(0)
    # [A.Cow.E.12]-[A.Cow.E.12]
    # Rumen undegradable protein of feed i (% of DM)
    RUP = []
    for i in range(len(CP)):
        RUP.append(CP[i] - RDP[i])
    # Dietary actual TDN (kg)
    TDNact_diet = sum(np.multiply(x, np.multiply(TDNact, 0.01)))
    # Dietary RDP (kg)
    RDP_diet = sum(np.multiply(x, np.multiply(RDP, 0.01)))
    # [A.Cow.E.13]-[A.Cow.E.13]
    # Metabolizable bacterial protein production (g)
    MPbact = 0.64 * min(1000 * .13 * TDNact_diet, 1000 * 0.85 * RDP_diet)
    # [A.Cow.E.14]-[A.Heifer.E.14]
    # Dietary RUP (kg)
    RUP_diet = sum(np.multiply(x, np.multiply(np.multiply(RUP, 0.01), np.multiply(dRUP, 0.01))))
    # [A.Cow.E.15]
    # Total metabolizable protein supply
    MP_supply = MPbact + RUP_diet + 0.4 * 11.8 * DMI

    # B: PROTEIN REQUIREMENTS:
    # Maintenance Requirement
    # ---------------------
    # [A.Cow.B.1]-[A.Heifer.B.1]
    # Metabolizable protein requirement for maintenance (g)
    MPm = (DMI * 1000 * 0.03 - 0.5 * ((MPbact / 0.8) - MPbact)) + 0.4 * 11.8 * (DMI / 0.67)
    return (MP_supply - ((MP_req + MPm) / 1000))


def NDF_constraint_1(x):
    """
    Sets up the RHS multipliers for each feed to instill an overall NDF percent
    constraint. This is a lower bound constraint on overall NDF percent.

    Args:
        x: The decision vector of the NLP
    """
    # From E/D: OTHER REQUIREMENTS
    DMI = sum(x)
    if DMI != 0:
        return (sum(np.multiply(x, NDF)) / DMI) - 25


def NDF_constraint_2(x):
    """
    Sets up the RHS multipliers for each feed to instill an overall NDF percent
    constraint. This is an upper bound constraint on overall NDF percent.

    Args:
        x: The decision vector of the NLP
    """
    # From E/D: OTHER REQUIREMENTS
    DMI = sum(x)
    if DMI != 0:
        return (-(sum(np.multiply(x, NDF)) / DMI) + 45)


def forage_NDF_constraint(x):
    """
    Sets up the RHS multipliers for only FORAGES to instill a NDF percent across
    forages constraint. This is a lower bound constraint on NDF percent across
    forages.

    Args:
        x: The decision vector of the NLP
    """
    # From E/D: OTHER REQUIREMENTS
    is_forage = []
    for i in range(len(type)):
        if type[i] == 'Forage':
            is_forage.append(1)
        else:
            is_forage.append(0)
    DMI = sum(x)
    if DMI != 0:
        return (sum(np.multiply(x, np.multiply(NDF, is_forage))) / DMI) - 19


def fat_constraint(x):
    """
    Sets up the RHS multipliers for each feed to instill an overall fat percent
    constraint. This is an upper bound constraint on over fat percent.

    Args:
        x: The decision vector of the NLP
    """
    # From E/D: OTHER REQUIREMENTS
    DMI = sum(x)
    if DMI != 0:
        return -(sum(np.multiply(x, EE)) / DMI) + 7


def DMI_constraint_lower(x):
    """
    Constraint in place to make sure the sum of all the feeds in the ration is
    greater than the DMI_est + 20% calculated in the requirements
    greater than the DMI_est + 20% calculated in the requirements

    Args:
        x: The decision vector of the NLP
    """
    return (sum(x)) - DMIest-DMIest*AnimalModuleConstants.DMI_CONSTRAINT_PERCENT


def DMI_constraint_upper(x):
    """
    Constraint in place to make sure the sum of all the feeds in the ration is
    less than the DMI_est + 20% calculated in the requirements.

    Args:
        x: The decision vector of the NLP
    """
    return -(sum(x)) + DMIest+DMIest*AnimalModuleConstants.DMI_CONSTRAINT_PERCENT


def energy_req_limit_constraint(x):
    """
    Constraint that limits each feed to only satisfying a single energy constraint
    (NEmact, NEgact, or NEl).

    Args:
        x: The decision vector of the NLP
    """
    n = len(price) /    3
    list = []
    for i in range(int(n)):
        a = i * 3
        list.append(x[a] * x[a + 1])
        list.append(x[a] * x[a + 2])
        list.append(x[a + 1] * x[a + 2])
    return -sum(list)

def get_ration_vals(x):
    """
    Function that calculates and retrieves ration values used throughout the
    ration.

    Args:
        x: the decision vector of the NLP (should be a completed ration)
    """
    #ration vals (subject to adding other ration vals)
    ME_tot = sum(np.multiply(x, MEact))
    ration_vals = {'ME_tot': ME_tot}
    return ration_vals


def make_user_bounds(ration_percents: Dict, DMIest: float) -> List:
    """
    Calculates user bounds for optimize function

    Uses udrv object to get tolerance, e.g. the +/- percentage allowed around those.
    Returns a list of each key/value pair three times, but divided by three
        This return in triplicate is necessary for the scipy.minimize function,
         which requires the decision vector in this shape
    
    Parameters
    ----------
    ration_percents: Dict
        keys are feed IDs, values are percent of DMI
    DMIest: float
        average estimated DMI for pen
    Returns
    -------
    List
        List of each bound, divided by three and reported in triplicate for scipy.minimize function
    """
    tribounds = []
    # udr = user defined ration
    udr_tolerance = udrv.tolerance
    for key in ration_percents.keys():
        target = ration_percents[key]/100*(DMIest+0.0001) # change from percent to decimal percent, adding a little bit in case of 0 return
        # target = ration_percents[key]
        targetbounds = ((target-target*udr_tolerance)/3,(target+target*udr_tolerance)/3)
        tribounds.append(targetbounds)
        tribounds.append(targetbounds)
        tribounds.append(targetbounds)
    return tribounds



# establishing the constraints of the NLP
constraint_functions = [
    NEmact_constraint,
    NEl_constraint,
    NEgact_constraint,
    calcium_constraint,
    phosphorus_constraint,
    protein_constraint,
    NDF_constraint_1,
    NDF_constraint_2,
    forage_NDF_constraint,
    fat_constraint,
    DMI_constraint_upper,
    DMI_constraint_lower
]

cow_cons = [{'type': 'ineq', 'fun': func} for func in constraint_functions]

heifer_cons = [cons for cons in cow_cons if cons['fun'] not in [NEl_constraint, DMI_constraint_lower]]

def optimize(animal_combination, available_feeds: Dict) -> None:

    """
    Calls the objective function and constraint functions and formulates
    the inputs for the minimization function. Returns the optimized solution
    as a dictionary with feed keys corresponding to their ration (kg).

    Parameters
    ----------
    animal_combination : Pen.AnimalCombination
        The animal combination to optimize the ration for.
    
    available_feeds: Dict 
        a DefaultDict of the AvailableFeeds class attributes defined in ration_driver.py
    
    Returns
    -------
    OptimizeResult object from scipy package

    """

    n = len(price)
    x0 = [1]
    for i in range(n-1):
        x0.append(random.random() * 10)
    # OPTIMIZE:
    # establishing the bounds of the NLP
    bnds = []
    # Dividing limit by 3 for tri-decision variables for farm grown feeds
    if udrv.udr_or_not:
        bnds = make_user_bounds(UserDefinedRationManager.ration_to_use(animal_combination, available_feeds), DMIest)
    else:    
        for i in range(len(limit)):
            bnds.append((0, (limit[i] / 3) + 0.0001))
        bnds = tuple(bnds)


    if udrv.udr_or_not:
        # accumulator = []
        if str(animal_combination) in ['AnimalCombination.LAC_COW']:
            usermod = minimize(objective, x0, method='SLSQP', bounds=bnds, constraints=cow_cons)
        else:
            usermod = minimize(objective, x0, method='SLSQP', bounds=bnds, constraints=heifer_cons)
        # Uncomment to use
        if usermod.success:
            # print(animal_type)
            print('No constraints violated')
        if not usermod.success:
            failed_constraints = find_failed_constraints(usermod.x, cow_cons)
            if not failed_constraints:
                print('No constraints violated')
        return usermod
    # TODO: Put AnimalCombination enum in a separate file and import it here to avoid circular import
    elif str(animal_combination) in ['AnimalCombination.LAC_COW']:
        return minimize(objective, x0, method='SLSQP', bounds=bnds, constraints=cow_cons)
    elif str(animal_combination) in ['AnimalCombination.GROWING', 'AnimalCombination.CLOSE_UP',
                                     'AnimalCombination.GROWING_AND_CLOSE_UP']:
        return minimize(objective, x0, method='SLSQP', bounds=bnds, constraints=heifer_cons)
    else:
        raise ValueError("Invalid animal combination: " + str(animal_combination))
