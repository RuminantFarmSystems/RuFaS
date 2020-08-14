################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: cow_requirements.py
Description: Calculates the following energy, mineral, and dry matter intake
    estimation for a single cow using the function in this file.
"""
################################################################################
import math
###TODO: Find out what units the percent values come in from the cow when linking###
###TODO: Edit function for dry cow requirement calculations as well
def calculate_requirements(BW, MW, DOP, housing, distance, parity, CI, TP_Milk,
                            Fat_Milk, Lactose_Milk, Milk, DIM, type
                            ):
    """
    Calculate the dietary requirements of a single cow. These values are used
    on the RHS of the linear program and furthermore will be used in constraint
    generation functions. This function calculates requirements for both
    lactating and dry cows. Each calculation has a reference to the
    respective calculation in the pseudocode.

    Args:
        BW: Body weight (kg)
        MW: Mature body weight(kg)
        DOP: Days of pregnancy (d)
        housing: Housing type (Barn or Grazing)
        distance: Daily walking distance (km)
        parity: Number of parity
        CI: Calving interval (d)
        TP_Milk: Milk true protein content  (% of milk)
        Fat_Milk: Milk fat content (% of milk)
        Lactose_Milk: Milk lactose content (% of milk)
        Milk: Milk production (kg)
        type: Boolean value which is true for lactating cowns and false for dry
        cows

    """

    # A: ENERGY REQUIREMENTS:
    # (divided into the following 5 components: maintenance,
    # activity, growth, pregnancy, and lactation requirements)
    #--------------------------------------------
    # Maintenance requirements
    # ---------------------
    # [A.Cow.A.1]
    # Calf birth weight (kg)
    CBW = MW * 0.06275
    # [A.Cow.A.2]
    # Conceptus weight (kg)
    if DOP > 190:
        CW = (18 + (DOP - 190) * 0.665) * (CBW/45)
    else:
        CW = 0
    # [A.Cow.A.3]
    # Net energy for maintenance requirement (Mcal)
    NEmaint = (0.08*(BW - CW)**0.75)
    # Activity requirements
    # ---------------------
    # [A.Cow.A.4]
    # Net energy for activity requirement caused by grazing system (Mcal)
    if housing == 'Grazing':
        NEa1 = 0.0012*BW
    else:
        NEa1 = 0
    # [A.Cow.A.6]
    # Total net energy for activity requirement (Mcal)
    NEa = distance * 0.00045 * BW + NEa1
    # Growth requirements
    # ---------------------
    # [A.Cow.A.7]
    # Mature shrunk body weight (kg)
    MSBW = 0.96 * MW
    # [A.Cow.A.8]
    # Shrunk body weight (kg)
    SBW = 0.96 * BW
    # [A.Cow.A.9]
    # Empty body weight (kg)
    EBW = 0.891 * SBW
    # [A.Cow.A.10]
    # Equivalent shrunk bodyweight (kg)
    EQSBW = (SBW - CW) * (478/MSBW)
    # [A.Cow.A.11]
    # Average Daily Gain (kg)
    if parity == 1 and CI != 0:
        ADG = ((0.92-0.82) * MSBW) / CI
    elif parity == 2 and CI!=0:
        ADG = ((1 - 0.92) * MSBW) / CI
    else:
        ADG = 0
    # [A.Cow.A.12]
    # Equivalent empty weight gain (kg)
    EQEBG = 0.956 * ADG
    # [A.Cow.A.13]
    # Equivalent shrunk body weight (kg)
    EQEBW = 0.891 * EQSBW
    # [A.Cow.A.14]
    # Net energy for growth requirement (Mcal)
    NEg = 0.0635 * EQEBW**0.75 * EQEBG**1.097
    # Pregnancy requirement
    # ---------------------
    # [A.Cow.A.15]
    # Metabolizable energy requirement for pregnancy (Mcal)
    if DOP > 190:
        MEpreg = (2*0.00159*DOP - 0.0352) * (CBW/(45*0.14))
    else:
        MEpreg = 0
    # [A.Cow.A.16]
    # Net energy requirement for pregnancy (Mcal)
    NEpreg = MEpreg * 0.64
    # Lactation requirement
    # ---------------------
    # [A.Cow.A.17]
    # Milk energy (Mcal/kg of milk production)
    Milken = 0.0929 * Fat_Milk + (0.0547/0.93) * TP_Milk + 0.0395 * Lactose_Milk
    # [A.Cow.A.18]
    # Net energy requirement for lactation (Mcal)
    NEl = Milken * Milk

    # B: PROTIEN REQUIREMENTS:
    # divided into 4 components: maintenance, growth, pregnancy, and lactation
    #--------------------------------------------
    # Maintenance Requirement
    # ---------------------
    # [A.Cow.B.1]
    # Metabolizable protein requirement for maintenance (g)
    # (note this is not the full calculation, which will be completed within the
    # non-linear program)
    MPm = 0.3 * (BW -CW)**0.6 + 4.1 * (BW-CW)**0.5
    # Growth Requirement
    # ---------------------
    # [A.Cow.B.2]
    # Net protein requirement for growth (g)
    if ADG == 0:
        NPg = 0
    else:
        NPg = ADG*(268 - 29.4* (NEg/ADG))
    # [A.Cow.B.3]
    # Efficiency of converting metabolizable protein to net protein
    if EQSBW <= 478:
        EffMP_NPg = (83.4-0.114*EQSBW) / 100
    else:
        EffMP_NPg = 0.28908
    # [A.Cow.B.4]
    # Metabolizable protein requirement for growth (g)
    MPg = NPg / EffMP_NPg
    # Pregnancy Requirement
    # ---------------------
    # [A.Cow.B.5]
    # Metabolizable protein requirement for pregnancy (g)
    if DOP > 190:
        MPpreg = (0.69*DOP-69.2) * (CBW/(45*0.33))
    else:
        MPpreg = 0
    # Lactation Requirement
    # ---------------------
    # [A.Cow.B.6]
    MPlact = Milk * (TP_Milk/100) * (1000/0.67)
    # Total Protien Requirement  (g)
    # ---------------------
    # [A.Cow.B.7]
    MP_req = MPm + MPg + MPpreg + MPlact

    # C: MINERAL REQUIREMENTS
    # Calcium and Phosphorus are the only requirements tracked currently
    #--------------------------------------------
    # Calcium Requirements
    #----------------------
    # [A.Cow.C.1]
    # Calcium maintenance requirement (g)
    if type:
        Ca_maint = 0.031 * BW + 0.08 * (BW/100)
    else:
        Ca_maint = 0.0154 * BW + 0.08 * (BW/100)
    # [A.Cow.C.2]
    # Calcium growth requirement (g)
    Ca_growth = 9.83 * MW**0.22 * BW**(-0.22) * (ADG/0.96)
    # [A.Cow.C.3]
    # Calcium pregnancy requirement (g)
    if DOP > 190:
        Ca_preg = 0.02456 * math.exp((0.05581-0.00007*DOP)*DOP) - 0.02456 * \
                                math.exp((0.05581-0.00007*(DOP-1)) * (DOP -1))
    else:
        Ca_preg = 0
    # [A.Cow.C.4]
    # Calcium lactation requirement (g)
    Ca_lact = 1.22 * Milk
    # [A.Cow.C.5]
    # Total calcium requirement (g)
    Ca_req = Ca_maint + Ca_growth + Ca_preg + Ca_lact
    # Phosphorus Requirements
    #----------------------
    # [A.Cow.C.7]
    # Phosphorus growth requirement (g)
    P_growth = (1.2+4.635 * MW**0.22 * BW**(-0.22)) * (ADG/0.96)
    # [A.Cow.C.8]
    # Phosphorus pregnancy requirement (g)
    if DOP > 190:
        P_preg = 0.02743 * math.exp((0.05527-0.000075*DOP)*DOP) - 0.02743 * \
                                math.exp((0.05527-0.000075*(DOP-1)) * (DOP -1))
    else:
        P_preg = 0
    # [A.Cow.C.9]
    # Phosphorus lactation requirement (g)
    P_lact = 0.9 * Milk
    # Total phosphorus requirement (g)
    # (note this sum does not include the maintenance requirement which will
    # be calculated within the NLP and added to this sum)
    # [A.Cow.C.10]
    P_req =  P_growth + P_preg + P_lact

    # D: DMI ESTIMATION:
    # The sum of dry matter intake of each feed is assumed to be less than
    # dry matter intake estimation (Sum of Feed < DMIest).
    #--------------------------------------------
    # [A.Cow.D.1]
    # Fat corrected milk (kg)
    FCM = (0.4 * Milk) + (15 * Fat_Milk * (Milk/100))
    # [A.Cow.D.2]
    # Dry matter intake estimation (kg)
    if type:
        DMIest = (0.372 * FCM + 0.0968 * BW**0.75) * (1- math.exp(-0.192 \
                                                            *((DIM/7) + 3.67)))
    else:
        DMIest = ( (1.97-0.75*math.exp(0.16 * (DOP-280))) / 100 ) * BW
    # Requirements summary dictionary
    return {'NEmaint' : NEmaint, 'NEa' : NEa, 'NEg' : NEg, 'NEpreg' : NEpreg,
            'NEl' : NEl, 'MP_req': MP_req, 'Ca_req' : Ca_req, 'P_req' : P_req,
            'DMIest' : DMIest}
