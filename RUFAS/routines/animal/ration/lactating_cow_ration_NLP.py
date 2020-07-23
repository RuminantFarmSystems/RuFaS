################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: lactating_cow_ration_NLP.py
Description: Calculates the ration for lactating cows using a Non-Linear
    programming method utilizing the scipy package. The NLP is formulated using
    constraint functions. Note NLP (Non-linear Program) will be used throughout
    descriptions for functions in this file.
Author(s):
    Chris VanKerkhove, cjv47@cornell.edu
"""
################################################################################
import numpy as np
import random
from scipy.optimize import minimize

def set_globals(price_, NEmaint_, NEa_, NEpreg_, NEl_, NEg_, MP_req_, C_req_, P_req_,
                DMIest_, TDN_, DE_, EE_, is_fat_, BW_, SBW_, Ca_, P_, NDF_, type_, is_wetforage_,
                Kd_, NA_, NB_, CP_, dRUP_):
    """
    Sets the global variables with the feed information to be used in the
    constraint functions below.
    """
    global price
    global n
    global NEmaint
    global NEa
    global NEpreg
    global NEl
    global NEg
    global MP_req
    global C_req
    global P_req
    global DMIest
    global TDN
    global DE
    global EE
    global is_fat
    global BW
    global SBW
    global Ca
    global P
    global NDF
    global type
    global is_wetforage
    global Kd
    global NA
    global NB
    global CP
    global dRUP

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
    SBW = SBW_
    Ca = Ca_
    P = P_
    NDF = NDF_
    type = type_
    is_wetforage = is_wetforage_
    Kd = Kd_
    NA = NA_
    NB = NB_
    CP = CP_
    dRUP = dRUP_

def list_reconfig(list):
    """
    Helper function that takes an input of a list and returns that list with
    each value occuring a total of 3 times. This method is required for matching
    the decision variables to each energy constraint.

    Args:
        list: A list of integers
    """
    list_reconfig = []
    for i in list:
        list_reconfig.append(i)
        list_reconfig.append(i)
        list_reconfig.append(i)
    return list_reconfig

def objective(x):
    """
    Sets up the objective function in the optimize function for the NLP.

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
    # DMI calculated by the NLP
    DMI = sum(x)
    # Dietary TDN content, kg
    TotalTDN = sum(np.multiply(x, TDN))
    TotalTDN = np.multiply(TotalTDN, 0.01)
    # [A.Cow.E.1]
    # TDN concentration, %
    if DMI != 0:
        TDNconc = (TotalTDN / DMI) * 100
    else:
        TDNconc = 0
    # [A.Cow.E.2]
    # The amount of intake needed to meet the maintenance requirement, dimensionless
    if TotalTDN < (0.035 * BW**0.75):
        DMI_to_maint = 1
    else:
        DMI_to_maint = (TotalTDN / (0.035 * SBW**0.75))
    # [A.Cow.E.3]
    # TDN discount, TDN digestibility decrease caused by DMI and TDNconc
    if TDNconc < 60:
        Discount = 1
    else:
        Discount = (TDNconc - ((0.18 * TDNconc - 10.3) * (DMI_to_maint - 1))) / TDNconc
    # [A.Cow.E.4]
    # Actual TDN content of feed i, %
    TDNact = np.multiply(TDN, Discount)
    # [A.Cow.E.5]
    # Actual digestible energy of feed i, Mcal/kg
    DEact = np.multiply(DE, Discount)
    # [A.Cow.E.5]
    # Actual metabolizable energy of feed i, Mcal/kg
    MEact = []
    for i in range(len(DEact)):
        if is_fat[i] == 1:
            MEact.append(DE[i])
        elif EE[i] >= 3:
            MEact.append(1.01 * DEact[i] - 0.45 + 0.0046 * (EE[i] - 3))
        else:
            MEact.append(1.01 * DEact[i] - 0.45)
    # [A.Cow.E.7]
    # Actual net energy for maintenance of feed i, Mcal/kg
    NEm_act = []
    for i in range(len(MEact)):
        if is_fat[i] == 1:
            NEm_act.append(0.8*MEact[i])
        else:
            NEm_act.append(1.37 * MEact[i] - 0.138 * MEact[i]**2 + 0.0105 * MEact[i]**3 - 1.12)
    # Constraining to only allow each feed to only satisfy a single energy constraint
    multiplier = []
    for i in range(int(n/3)):
        multiplier.append(1)
        multiplier.append(0)
        multiplier.append(0)
    # returning the NEm_act constraint in the NLP
    return (sum(np.multiply(x, np.multiply(multiplier,NEm_act))) - (NEmaint + NEa))

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
    # [A.Cow.E.6]
    for i in range(len(MEact)):
        if is_fat[i] == 1:
            NElact.append(0.8 * MEact[i])
        elif EE[i] >= 3:
            NElact.append(0.703 * MEact[i] - 0.19 + ((0.097 * MEact[i] + 0.19) / 97) * (EE[i] - 3))
        else:
            NElact.append(0.703 * MEact[i] - 0.19)
    #Constraining to only allow each feed to only satisfy a single energy constraint
    multiplier = []
    for i in range(int(n/3)):
        multiplier.append(0)
        multiplier.append(1)
        multiplier.append(0)
    #returning the NElact constraint in the NLP
    return (sum(np.multiply(x, np.multiply(multiplier, NElact))) - (NEpreg + NEl))

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
    # [A.Cow.E.8]
    for i in range(len(MEact)):
        if is_fat[i] == 1:
            NEgact.append(0.55 * MEact[i])
        else:
            NEgact.append(1.42 * MEact[i] - 0.174 * MEact[i]**2 + 0.0122 * MEact[i]**3 -1.65)
    #Constraining to only allow each feed to only satisfy a single energy constraint
    multiplier = []
    for i in range(int(n/3)):
        multiplier.append(0)
        multiplier.append(0)
        multiplier.append(1)
    #returning the NEgact constraint in the NLP
    return (sum(np.multiply(x, np.multiply(multiplier, NEgact))) - NEg)

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
    # [A.Cow.E.15]
    return (sum(np.multiply(x,np.multiply(np.multiply(Ca,0.01) ,dCa))) - (C_req/1000))

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
    #----------------------
    # [A.Cow.C.6]
    # Phosphorus maintenance requirement (g)
    P_maint = 1*DMI + 0.002*BW
    # [A.Cow.E.15]
    return (sum(np.multiply(x,np.multiply(np.multiply(P,0.01),dP))) - ((P_req+P_maint)/1000))

def protien_constraint(x):
    """
    Sets up the protien requirement constraint in the NLP. Because part of the
    maintenance requirement for protien contains non-linearity properties, that
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
    # [A.Cow.E.9]
    # Protein passage rate of feed i (%/h)
    Kp = []
    for i in range(len(type)):
        if type[i] == 'Conc':
            Kp.append(2.904 + 1.375*(DMI/BW)*100 - 0.02*PercentConc)
        elif type[i] == 'Forage' and is_wetforage[i] == 0:
            Kp.append(3.362 + 0.479 *(DMI/BW)*100 - 0.17*NDF[i] - 0.007*PercentConc)
        elif is_wetforage[i] == 1:
            Kp.append(3.054 + 0.614*(DMI/BW)*100)
        else:
            Kp.append(0)
    # [A.Cow.E.10]
    # Rumen degradable protein of feed i (% of DM)
    RDP = []
    for i in range(len(Kd)):
        if Kp[i] > -Kd[i]:
            RDP.append((Kd[i]/(Kd[i]+Kp[i])) * (NB[i]/100) * CP[i] + (NA[i]/100)*CP[i])
        else:
            RDP.append(0)
    # [A.Cow.E.11]
    # Rumen undegradable protein of feed i (% of DM)
    RUP = []
    for i in range(len(CP)):
        RUP.append(CP[i]-RDP[i])
    # Dietary actual TDN (kg)
    TDNact_diet = sum(np.multiply(x, np.multiply(TDNact,0.01)))
    # Dietary RDP (kg)
    RDP_diet = sum(np.multiply(x, np.multiply(RDP,0.01)))
    # [A.Cow.E.12]
    # Metabolizable bacterial protein production (g)
    MPbact = 0.64 * min(1000*.13*TDNact_diet, 1000*0.85*RDP_diet)
    # [A.Cow.E.13]
    # Dietary RUP (kg)
    RUP_diet = sum(np.multiply(x, np.multiply(np.multiply(RUP,0.01), np.multiply(dRUP,0.01))))
    # [A.Cow.E.14]
    # Total metabolizable protein supply
    MP_supply = MPbact + RUP_diet + 0.4*11.8*DMI

    # B: PROTIEN REQUIREMENTS:
    # Maintenance Requirement
    # ---------------------
    # [A.Cow.B.1]
    # Metabolizable protein requirement for maintenance (g)
    MPm = (DMI*1000*0.03 - 0.5*((MPbact/0.8) - MPbact)) + 0.4*11.8*(DMI/0.67)
    return (MP_supply - ((MP_req + MPm)/1000))

def NDF_constraint_1(x):
    """
    Sets up the RHS multipliers for each feed to instill an overall NDF percent
    constraint. This is a lower bound constraint on overall NDF percent.

    Args:
        x: The decision vector of the NLP
    """
    #From E: OTHER REQUIREMENTS
    DMI = sum(x)
    if DMI != 0:
        return ((sum(np.multiply(x, NDF)) / DMI) - 25)

def NDF_constraint_2(x):
    """
    Sets up the RHS multipliers for each feed to instill an overall NDF percent
    constraint. This is an upper bound constraint on overall NDF percent.

    Args:
        x: The decision vector of the NLP
    """
    #From E: OTHER REQUIREMENTS
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
    #From E: OTHER REQUIREMENTS
    is_forage = []
    for i in range(len(type)):
        if type[i] == 'Forage':
            is_forage.append(1)
        else:
            is_forage.append(0)
    DMI = sum(x)
    if DMI != 0:
        return ((sum(np.multiply(x, np.multiply(NDF, is_forage))) / DMI) - 19)

def fat_constraint(x):
    """
    Sets up the RHS multipliers for each feed to instill an overall fat percent
    constraint. This is an upper bound constraint on over fat percent.

    Args:
        x: The decision vector of the NLP
    """
    #From E: OTHER REQUIREMENTS
    DMI = sum(x)
    if DMI != 0:
        return (-(sum(np.multiply(x, EE)) / DMI) + 7)

def DMI_constraint(x):
    """
    Constraint in place to make sure the sum of all the feeds in the ration is
    less than the DMI_est calculated in the requirements.

    Args:
        x: The decision vector of the NLP
    """
    return (-(sum(x)) + DMIest)

def energy_req_limit_constraint(x):
    """
    Constraint that limits each feed to only satisfying a single energy constraint
    (NEmact, NEgact, or NEl).

    Args:
        x: The decision vector of the NLP
    """
    n = len(price) / 3
    list = []
    for i in range(int(n)):
        a = i*3
        list.append(x[a]*x[a+1])
        list.append(x[a]*x[a+2])
        list.append(x[a+1]*x[a+2])
    return -sum(list)

def optimize():
    """
    Calls the objective function and constraint functions and formulates
    the inputs for the minimization function. Returns the optimized solution
    as a dictionary with feed keys corresponding to their ration (kg).

    Args:
        *This function requires no inputs, but utilizes the functions created
        above in this file*

    """

    n = len(price)
    x0 = []
    for i in range(n):
        x0.append(random.random()*10)
    '''
    for i in range(n):
        x0[i] = x1[i] +.1
    '''
    ## OPTIMIZE:
    #establishing the bounds of the NLP
    b= (0, 100)
    bnds = []
    for i in range(len(price)):
        bnds.append(b)
    bnds = tuple(bnds)

    #establishing the constraints of the NLP
    con1 = {'type': 'ineq', 'fun': NEmact_constraint}
    con2 = {'type': 'ineq', 'fun': NEl_constraint}
    con3 = {'type': 'ineq', 'fun': NEgact_constraint}
    con4 = {'type': 'ineq', 'fun': calcium_constraint}
    con5 = {'type': 'ineq', 'fun': phosphorus_constraint}
    con6 = {'type': 'ineq', 'fun': protien_constraint}
    con7 = {'type': 'ineq', 'fun': NDF_constraint_1}
    con8 = {'type': 'ineq', 'fun': NDF_constraint_2}
    con9 = {'type': 'ineq', 'fun': forage_NDF_constraint}
    con10 = {'type': 'ineq', 'fun': fat_constraint}
    con11 = {'type': 'ineq', 'fun': DMI_constraint}
    con12 = {'type': 'eq', 'fun': energy_req_limit_constraint}
    cons = ([con1,con2,con3,con4, con5,con6,con7,con8,con9,con10,con12])

    solution = minimize(objective, x0, method='SLSQP', bounds=bnds, constraints=cons)

    return(solution)


'''
solution = optimize()
print(objective(solution.x))
print(solution.success)
rounded = [round(num, 2) for num in solution.x]
print(rounded)
print('Con_1')
print(NEmact_constraint(solution.x))
print('Con_2')
print(NEl_constraint(solution.x))
print('Con_3')
print(NEgact_constraint(solution.x))
print('Con_4')
print(calcium_constraint(solution.x))
print('Con_5')
print(phosphorus_constraint(solution.x))
print('Con_6')
print(protien_constraint(solution.x))
print('Con_7')
print(NDF_constraint_1(solution.x))
print('Con_8')
print(NDF_constraint_2(solution.x))
print('Con_9')
print(forage_NDF_constraint(solution.x))
print('Con_10')
print(fat_constraint(solution.x))
print('Con_11')
print(DMI_constraint(solution.x))
print('Con_12')
print(NEmact_limit_constraint(solution.x))
'''
