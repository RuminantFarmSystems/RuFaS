"""
RUFAS: Ruminant Farm Systems Model
File name: heifer_requirements.py
Description: Calculates the following energy, mineral, and dry matter intake
    estimation for a single heifer using the function in this file.
Author(s): Chris VanKerkhove, cjv47@cornell.edu
"""
import math

def calc_rqmts(BW, MW, DOP, BCS5, PrevTemp, bred):
        """
        Calculates the dietary requirements of a single cow. These values are used
        on the RHS of the linear program and furthermore will be used in constraint
        generation functions. This function calculates requirements for both
        lactating and dry cows. Each calculation has a reference to the
        respective calculation in the pseudocode.

        Args:
            BW: Body weight (kg)
            MW: Mature body weight(kg)
            DOP: Days of pregnancy (d)
            BCS5: Body Condition Score (1-5 basis)
            PrevTemp: Average daily temperature of last month, °C
            bred: A boolean if the animal has been bred or not
            Age1stBred: 1st breeding age, month
            Age1st: First calving age, month
            Age: Current age, month
        """
    # A: ENERGY REQUIREMENTS:
    # (divided into the following 4 components: maintenance,
    # activity, growth, and pregnancy requirements)
    # --------------------------------------------
    # Maintenance requirements
    # ---------------------
    # [A.Heifer.A.1]
    # Calf birth weight (kg)
    CBW = MW * 0.06275
    # [A.Heifer.A.2]
    # Conceptus weight (kg)
    if DOP > 190:
        CW = (18 + (DOP - 190) * 0.665) * (CBW / 45)
    else:
        CW = 0
    # [A.Heifer.A.3]
    # BCS9 = Body condition score, 1 - 9 basis
    BCS9 = (BCS5 -1) * 2 + 1
    # [A.Heifer.A.4]
    # Net energy for maintenance requirement, Mcal
    NEmaint = (BW-CW)**(0.75) * (0.086*(0.8+ (BCDS9 - 1) * 0.5)) + 0.0007*(20-PrevTemp)
    # --------------------------------------------
    # Activity Requirement
    # ---------------------
    # calculated in a seperate function
    # --------------------------------------------
    # Growth Requirement
    # ---------------------
    # [A.Heifer.A.8]
    # Mature shrunk body weight (kg)
    MSBW = 0.96 * MW
    # [A.Heifer.A.9]
    # Shrunk body weight (kg)
    SBW = 0.96 * BW
    # [A.Heifer.A.10]
    # Empty body weight (kg)
    # EBW = 0.891 * SBW
    # [A.Heifer.A.11]
    # Equivalent shrunk body weight (kg)
    EQSBW = (SBW - CW) * (478 / MSBW)
    # [A.Heifer.A.12]
    # Average Daily Gain (kg)
    if not bred:
        ADG = (0.55*MSBW - SBW) / (Age1stBred-Age)*30.4
    else:
        (0.82*MSBW-SBW) / (Age1st - Age)
    # [A.Heifer.A.13]
    # Equivalent empty weight gain (kg)
    EQEBG = 0.956 * ADG
    # [A.Heifer.A.14]
    # Equivalent shrunk body weight (kg)
    EQEBW = 0.891 * EQSBW
    # [A.Heifer.A.15]
    # Net energy for growth requirement (Mcal)
    NEg = (0.0635 * EQEBW)** 0.75 * EQEBG**1.097
    # Pregnancy requirement
    # ---------------------
    # [A.Heifer.A.16]
    # Metabolizable energy requirement for pregnancy (Mcal)
    if DOP > 190:
        MEpreg = (2 * 0.00159 * DOP - 0.0352) * (CBW / (45 * 0.14))
    else:
        MEpreg = 0
    # [A.Heifer.A.17]
    # Net energy requirement for pregnancy (Mcal)
    NEpreg = MEpreg * 0.64

    # B: PROTEIN REQUIREMENTS:
    # divided into 4 components: maintenance, growth, pregnancy
    # --------------------------------------------
    # Maintenance Requirement
    # ---------------------
    # [A.Heifer.B.1]
    # Metabolizable protein requirement for maintenance (g)
    # (note this is not the full calculation, which will be completed within the
    # non-linear program)
    MPm = 0.3 * (BW - CW) ** 0.6 + 4.1 * (BW - CW) ** 0.5
    # Growth Requirement
    # ---------------------
    # [A.Heifer.B.2]
    # Net protein requirement for growth (g)
    if ADG == 0:
        NPg = 0
    else:
        NPg = ADG * (268 - 29.4 * (NEg / ADG))
    # [A.Heifer.B.3]
    # Efficiency of converting metabolizable protein to net protein
    if EQSBW <= 478:
        EffMP_NPg = (83.4 - 0.114 * EQSBW) / 100
    else:
        EffMP_NPg = 0.28908
    # [A.Heifer.B.4]
    # Metabolizable protein requirement for growth (g)
    MPg = NPg / EffMP_NPg
    # Pregnancy Requirement
    # ---------------------
    # [A.Heifer.B.5]
    # Metabolizable protein requirement for pregnancy (g)
    if DOP > 190:
        MPpreg = (0.69 * DOP - 69.2) * (CBW / (45 * 0.33))
    else:
        MPpreg = 0
    # Total Protein Requirement  (g)
    # ---------------------
    # [A.Heifer.B.6]
    MP_req = MPm + MPg + MPpreg

    # C: MINERAL REQUIREMENTS
    # Calcium and Phosphorus are the only requirements tracked currently
    # --------------------------------------------
    # Calcium Requirements
    # ----------------------
    # [A.Heifer.C.1]
    # Calcium maintenance requirement (g)
    Ca_main = 0.0154*BW + 0.08*(BW/100)
    # [A.Heifer.C.2]
    # Calcium growth requirement (g)
    Ca_growth = 9.83 * (MW ** 0.22) * (BW ** (-0.22)) * (ADG / 0.96)
    # [A.Heifer.C.3]
    # Calcium pregnancy requirement (g)
    if DOP > 190:
        Ca_preg = 0.02456 * math.exp((0.05581 - 0.00007 * DOP) * DOP) - 0.02456 * \
                  math.exp((0.05581 - 0.00007 * (DOP - 1)) * (DOP - 1))
    else:
        Ca_preg = 0
    # [A.Heifer.C.4]
    # Total calcium requirement (g)
    Ca_req = Ca_maint + Ca_growth + Ca_preg
    # Phosphorus Requirements
    # ----------------------
    # [A.Heifer.C.5]
    # Phosphorus growth requirement (g)
    P_growth = (1.2 + 4.635 * MW ** 0.22 * BW ** (-0.22)) * (ADG / 0.96)
    # [A.Heifer.C.6]
    # Phosphorus pregnancy requirement (g)
    if DOP > 190:
        P_preg = 0.02743 * math.exp((0.05527 - 0.000075 * DOP) * DOP) - 0.02743 * \
                 math.exp((0.05527 - 0.000075 * (DOP - 1)) * (DOP - 1))
    else:
        P_preg = 0
    # Total phosphorus requirement (g)
    # (note this sum does not include the maintenance requirement which will
    # be calculated within the NLP and added to this sum)
    # [A.Heifer.C.8]
    P_req = P_growth + P_preg
    
