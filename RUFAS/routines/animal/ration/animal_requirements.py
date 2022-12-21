"""
RUFAS: Ruminant Farm Systems Model
File name: animal_requirements.py
Description: Calculates the following energy, mineral, and dry matter intake
    estimation for a single animal using the function in this file.
Author(s): Chris VanKerkhove, cjv47@cornell.edu
"""

import math
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase

def calc_rqmts(BW, MW, DOP, animal_type, parity=None, CI=None , TP_Milk=None, Fat_Milk=None,
                Lactose_Milk=None, Milk=None, DIM=None, lactating=None,
                BCS5= None, PrevTemp = None,
                ADG_heifer = None, Age = None):
    """
    Calculates the dietary requirements of a single animal. These values are used
    on the RHS of the linear program and furthermore will be used in constraint
    generation functions. Each calculation has a reference to the
    respective calculation in the pseudocode (both Cow and Heifer).
    (Note that arguments that are only for a single animal class are instanciated
    at None however the respective parameters must be set when calling said
    animal class)

    Args:
        BW: Body weight (kg)
        MW: Mature body weight(kg)
        animal_type: the type of animal (string)
        DOP: Days of pregnancy (d) (except Heifer Is)
    (Args for just cow requirements):
        parity: Number of parity
        CI: Calving interval (d)
        TP_Milk: Milk true protein content  (% of milk)
        Fat_Milk: Milk fat content (% of milk)
        Lactose_Milk: Milk lactose content (% of milk)
        Milk: Milk production (kg)
        DIM: Days in milk (int)
        lactating: Boolean value which is true for lactating cows and false for dry cows
    (Args for just heifer requirements):
        BCS5: Body Condition Score (1-5 basis)
        PrevTemp: Average daily temperature of last month, °C
        ADG_heifer: Average daily gain of a heifer
        Age: Current age, month

    """
    # TODO: put the following original comments into a wiki or other resource
    # A: ENERGY REQUIREMENTS:
    # (divided into the following 5 components: maintenance,
    # activity, growth, pregnancy, and lactation requirements)
    # --------------------------------------------
    
    # --------------------------------------------
    if AnimalBase.config['NASEM_or_NRC_requirement_calculations'] == 'NASEM':
        NEmaint, CW, CBW = calculate_NASEM_energy_maintenance_requirements(BW, MW, DOP, BCS5, PrevTemp, animal_type)
        NEg, ADG, EQSBW = calculate_NASEM_energy_growth_requirements(BW, MW, CW, animal_type, parity, CI, ADG_heifer)
        NEpreg = calculate_NASEM_energy_pregnancy_requirements(DOP, CBW)
        NEl = calculate_NASEM_energy_lactation_requirements(animal_type, Fat_Milk, TP_Milk, Lactose_Milk, Milk)
        MP_req = calculate_NASEM_protein_requirements(BW,MW,CW,DOP,animal_type,Milk,TP_Milk, CBW, NEg,ADG,EQSBW)
        Ca_req = calculate_NASEM_calcium_requirements(BW, MW, DOP, animal_type, lactating, ADG, Milk)
        P_req = calculate_NASEM_P_requirements(BW, MW, DOP, Milk, animal_type, ADG)
        DMIest = calculate_DMI_NASEM(BW, MW, DIM, lactating, NEl, BCS5, parity)
    elif AnimalBase.config['NASEM_or_NRC_requirement_calculations'] == 'NRC':
        NEmaint, CW, CBW = calculate_NRC_energy_maintenance_requirements(BW, MW, DOP, BCS5, PrevTemp, animal_type)
        NEg, ADG, EQSBW = calculate_NRC_energy_growth_requirements(BW, MW, CW, animal_type, parity, CI, ADG_heifer)
        NEpreg = calculate_NRC_energy_pregnancy_requirements(DOP, CBW)
        NEl = calculate_NRC_energy_lactation_requirements(animal_type, Fat_Milk, TP_Milk, Lactose_Milk, Milk)
        MP_req = calculate_NRC_protein_requirements(BW,MW,CW,DOP,animal_type,Milk,TP_Milk, CBW, NEg,ADG,EQSBW)
        Ca_req = calculate_NRC_calcium_requirements(BW, MW, DOP, animal_type, lactating, ADG, Milk)
        P_req = calculate_NRC_P_requirements(BW, MW, DOP, Milk, animal_type, ADG)
        DMIest = calculate_DMI_NRC(animal_type, BW, DOP, DIM, lactating, Milk, Fat_Milk)
    else:
        DMIest=[]
        print(f"DMI estimation method \
            {AnimalBase.config['NASEM_or_NRC_requirement_calculations']}\
            not supported")
    # Requirements summary dictionary
    return {'NEmaint': NEmaint, 'NEg': NEg, 'NEpreg': NEpreg,
            'NEl': NEl, 'MP_req': MP_req, 'Ca_req': Ca_req, 'P_req': P_req,
            'DMIest': DMIest}


def calculate_NRC_energy_maintenance_requirements(BW, MW, DOP, BCS5, PrevTemp, animal_type):
    # Maintenance requirements
    # ---------------------
    # [A.Cow.A.1]-[A.Heifer.A.1]
    # Calf birth weight (kg)
    CBW = MW * 0.06275
    # [A.Cow.A.2]-[A.Heifer.A.2]
    # Conceptus weight (kg)
    if DOP == None:
        CW = 0
    elif DOP > 190:
        CW = (18 + (DOP - 190) * 0.665) * (CBW / 45)
    else:
        CW = 0
    # [A.Cow.A.3]
    # Net energy for maintenance requirement (Mcal)
    if animal_type == 'cow':
        NEmaint = (0.08 * (BW - CW) ** 0.75)

    # Heifer Energy Requirements
    # [A.Heifer.A.3]
    elif animal_type == 'heifer':
        # BCS9 = Body condition score, 1 - 9 basis
        BCDS9 = (BCS5 -1) * 2 + 1
        # [A.Heifer.A.4]
        # Net energy for maintenance requirement, Mcal
        NEmaint = (BW-CW)**(0.75) * (0.086*(0.8+ (BCDS9 - 1) * 0.5)) + 0.0007*(20-PrevTemp)
    return NEmaint, CW, CBW

def calculate_NASEM_energy_maintenance_requirements(BW, MW, DOP, DIM):
    NEmaint = []
    # Maintenance requirement is calculated based on:
    # metabolic body weight (MBW; body weight0.75), gain in pregnancy tissues, and activity (locomotion).
    #CBW = input variable; otherwise MW * 0.06275
    # where, CBW = Calf birth weight (kg); MW = Mature body weight (kg)
    CBW = MW * 0.06275

    # CBW = Calf birth weight (kg) can be estimated using the equation above,
    # otherwise there is an input variable depending on breed. Holstein = 42 kg; Jersey = 31 kg

    # MW = Mature body weight (kg)
    # Default values of MW according to NASEM (2021) = 700 kg for Holstein; 520 kg for Jersey

    # In NASEM (2021) instead of estimating calving weight, gain in pregnancy tissues are estimated.

    # GrUterW = (CBW * 1.825) *  〖exp〗 ** (-0.0243 - (0.0000245 * DayGest) * (280 - DayGest))
    # UterW = ((CBW * 0.2288) * 〖exp〗** (-0.2*DIM)) )+0.204)
    GrUterW = CBW * 1.825 *  math.exp(-0.0243 - (0.0000245 * DOP) * (280 - DOP))
    UterW = (CBW * 0.2288 * math.exp(-0.2*DIM)) + 0.204 # TODO ASK EDWARD IF THE PARENTHESES MATCH

    # where,
    # DGest = Day of gestation (this must be between 12 and 280 DGest)
    # DIM= Days in milk (lactation)
    # GrUterW = Gravid uterine weight
    # UterW = Uterine weight

    # NEmaint=〖0.10*(BW-GrUterW - UterW)〗**0.75
    NEmaint=(0.10*(BW-GrUterW - UterW))**0.75
    # This formula is for normal activity in confinement conditions,
    # otherwise adjustments for activity requirement under grazing conditions should be included (Celina module?)
    # NEmaint = Net energy for maintenance requirement, Mcal NEL/day
    return NEmaint

def calculate_NRC_energy_activity_requirements():
    pass

def calculate_NASEM_energy_activity_requirements(BW, housing, distance):
    #(NEa, Horiz_Locomotion, DistParlor*NtripsParlor, Positive_Vert_Locom,Graz_Act, km_Vert_Dist, nonpasturekgDMI):
    pass
    # Activity requirement (NEa) is proportional to body weight and daily walking distance.
    # The maintenance requirement is assumed to provide adequate energy for normal activity of cows in confinement.
    # Grazing system and hilly topography will cost additional energy.

    # Additional energy requirements are also estimated as follows:
    # Horiz_Locomotion= (DistParlor*NtripsParlor)*0.00035*BW
    # Positive_Vert_Locom= km_Vert_Dist*0.0067*BW
    # Graz_Act = 0.0075 * BW0.75 *((600-12*nonpasturekgDMI))/600

    # where,
    # Horiz_Locomotion= Cost of locomotion on a flat surface, Mcal NEL/day
    # Positive_Vert_Locom= energy requirement for daily total climb while grazing and during transit between
    # the milking parlor and the barn or paddock, Mcal NEL/day
    # Grazing_Act = Grazing activity, Mcal NEL/day
    # DistParlor = round trip distance from the barn or paddock to the parlor, meters
    # NtripsParlor = number of trips to the parlor
    # km_Vert_Dist = km of vertical distance
    # nonpasturekgDMI = consumption of concentrate supplement, kg/day (on a DM basis)

    # NEa =	Horiz_Locomotion + Positive_Vert_Locom + Grazing_Act
    if housing == 'Barn':
        NEa =  distance * 0.00035 * BW  # ?????? TODO ASK EDWARD
    else:
        nonpasturekgDMI = 9999 # TODO ASK EDWARD IF THIS IS SAME AS DMI FROM RATION, then import DMI amount
        NEa = distance * BW * 0.75 * ((600-12*nonpasturekgDMI))/600
    # NEa = Total net energy requirement for activity, Mcal NEL/day
    return NEa

def calculate_NRC_energy_growth_requirements(BW, MW, CW, animal_type, parity, CI, ADG_heifer):
    # Activity requirements
    # ---------------------
    # Activity requirements must be calculated after grouping and thus is in a
    # separate function
    # Growth requirements
    # ---------------------
    # [A.Cow.A.7]-[A.Heifer.A.8]
    # Mature shrunk body weight (kg)
    MSBW = 0.96 * MW
    # [A.Cow.A.8]-[A.Heifer.A.9]
    # Shrunk body weight (kg)
    SBW = 0.96 * BW
    # [A.Cow.A.9]-[A.Heifer.A.10]
    # Empty body weight (kg)
    # EBW = 0.891 * SBW
    # [A.Cow.A.10]-[A.Heifer.A.11]
    # Equivalent shrunk body weight (kg)
    EQSBW = (SBW - CW) * (478 / MSBW)
    # [A.Cow.A.11]
    # Average Daily Gain (kg)
    if animal_type == 'cow':
        if parity == 1 and CI != 0:
            ADG = ((0.92 - 0.82) * MSBW) / CI
        elif parity == 2 and CI != 0:
            ADG = ((1 - 0.92) * MSBW) / CI
        else:
            ADG = 0
    # [A.Heifer.A.12]
    # Average Daily Gain (kg)
    elif animal_type == 'heifer':
        ADG = max(ADG_heifer, 0)
    # [A.Cow.A.12]-[A.Heifer.A.13]
    # Equivalent empty weight gain (kg)
    EQEBG = 0.956 * ADG
    # [A.Cow.A.13]-[A.Heifer.A.14]
    # Equivalent shrunk body weight (kg)
    EQEBW = 0.891 * EQSBW
    # [A.Cow.A.14]-[A.Heifer.A.15]
    # Net energy for growth requirement (Mcal)
    NEg = 0.0635 * EQEBW ** 0.75 * EQEBG ** 1.097
    return NEg, ADG, EQSBW

def calculate_NASEM_energy_growth_requirements(BW, MW, ADG_heifer):
    # In NASEM (2021), body frame gain (fat + protein) corresponds to the true growth and it is part
    # of the calculation which is further partitioned to body reserves or condition gain (or loss),
    # and pregnancy-associated gain (considered a pregnancy requirement).

    # EBW =	0.85*BW
    # EBW = Empty body weight (without digesta contents), kg

    # EBG = 0.85*ADG
    EBG = 0.85*ADG_heifer
    # EBG = Empty body weight gain, kg/day

    # ADG = Average daily gain, kg/day
    # FatADG =(0.067 + 0.375*(BW/MW))*EBG/ADG
    # FatADG = Fat constituent of average daily gain, g/g
    FatADG = (0.067 + 0.375*(BW/MW))*EBG/ADG_heifer

    # ProtADG=(0.201 + 0.081*(BW/MW))*EBG/ADG
    # ProtADG = Protein constituent of average daily gain, g/g
    ProtADG=(0.201 + 0.081*(BW/MW))*EBG/ADG_heifer

    # REFADG = 9.4*FatADG+5.55*ProtADG
    # REFADG = Retained energy of frame ADG, Mcal/kg
    REFADG = 9.4*FatADG+5.55*ProtADG

    # MEFrameADG= REFADG/0.4
    # MEFrameADG = Metabolizable energy for frame ADG, Mcal/kg. The value 0.4
    # is assumed to be the efficiency of converting feed ME to NE for gain (NEg).
    MEFrameADG= REFADG/0.4

    # NElFrameADG= REFADG/0.61
    # NElFrameADG = Net energy for frame ADG, Mcal/kg.
    NElFrameADG= REFADG/0.61
    # The efficiency of converting NEl to NEg is based on the conversions of 0.40 for ME to NEg
    # and 0.66 for ME to NEl and is thus 0.40/0.66 = 0.61.
    return NEg # TODO ASK EDWARD HOW TO GET NEg

def calculate_NRC_energy_pregnancy_requirements(DOP, CBW):
    # Pregnancy requirement
    # ---------------------
    # [A.Cow.A.15]-[A.Heifer.A.16]
    # Metabolizable energy requirement for pregnancy (Mcal)
    if DOP == None:
        MEpreg = 0
    elif DOP > 190:
        MEpreg = (2 * 0.00159 * DOP - 0.0352) * (CBW / (45 * 0.14))
    else:
        MEpreg = 0
    # [A.Cow.A.16]-[A.Heifer.A.17]
    # Net energy requirement for pregnancy (Mcal)
    NEpreg = MEpreg * 0.64
    return NEpreg

def calculate_NASEM_energy_pregnancy_requirements(DOP, DIM, GrUterW, UterW):
    # (GrUterWGain1, DayGEst, GrUterW, GrUterWGain2, DIM, GrUterW, UterW, NElPreg)                                                  ):
    # Daily rates of wet tissue deposition(kg/day) are derived from equations previously described in the maintenance
    # requirements section.

    # GrUterWGain1 = (0.0243 – (0.0000245 * DayGest)) *GrUterW
    GrUterWGain1 = (0.0243 - (0.0000245 * DOP)) *GrUterW
    # GrUterWGain2 = –0.2 * DIM * (UterW – 0.204)
    GrUterWGain2 = -0.2 * DIM * (UterW - 0.204)
    # NElPreg  = GrUterWGain * (0.882 / 0.14) * 0.66
    # TODO IS THIS 1 + 2?
    NEpreg  = GrUterWGain * (0.882 / 0.14) * 0.66

    # where,
    # DGest = Day of gestation (this must be between 12 and 280 DGest)
    # DIM= Days in milk (lactation)
    # GrUterW = Gravid uterine weight
    # GrUterWGain1= Energy Req. during gestation, Mcal NEl/day
    # UterW = Uterine weight
    # GrUterWGain2 = Energy Req. during uterine involution
    # NElPreg = Net energy (lactation) requirement for pregnancy, Mcal NEL/d.
    # Assumptions: tissue contains 0.882 Mcal of energy / kg; an ME to gestation energy efficiency of 0.14;
    # and ME to NEl efficiency of 0.66.MEpreg = Metabolizable energy requirement for pregnancy, Mcal NEl/day
    return NEpreg

def calculate_NRC_energy_lactation_requirements(animal_type, Fat_Milk, TP_Milk, Lactose_Milk, Milk):
    # Lactation requirement
    # ---------------------
    if animal_type == 'cow':
        # [A.Cow.A.17]
        # Milk energy (Mcal/kg of milk production)
        Milken = 0.0929 * Fat_Milk + (0.0547 / 0.93) * TP_Milk + 0.0395 * Lactose_Milk
        # [A.Cow.A.18]
        # Net energy requirement for lactation (Mcal)
        NEl = Milken * Milk
    else:
        NEl = 0
    return NEl

def calculate_NASEM_energy_lactation_requirements(animal_type, Fat_Milk, TP_Milk, Lactose_Milk, Milk):
    # Lactation requirement
    # ---------------------
    if animal_type == 'cow':
        # [A.Cow.A.17]
        # Milk energy (Mcal/kg of milk production)
        Milken = 0.0929 * Fat_Milk + (0.0547 / 0.93) * TP_Milk + 0.0395 * Lactose_Milk
        # [A.Cow.A.18]
        # Net energy requirement for lactation (Mcal)
        NEl = Milken * Milk
    else:
        NEl = 0
    return NEl

def calculate_NRC_protein_requirements(BW,MW,CW,DOP,animal_type,Milk,TP_Milk, CBW, NEg,ADG,EQSBW):
    # B: PROTEIN REQUIREMENTS:
    # divided into 4 components: maintenance, growth, pregnancy, and lactation
    # --------------------------------------------
    # Maintenance Requirement
    # ---------------------
    # [A.Cow.B.1]-[A.Heifer.B.1]
    # Metabolizable protein requirement for maintenance (g)
    # (note this is not the full calculation, which will be completed within the
    # non-linear program)
    MPm = 0.3 * (BW - CW) ** 0.6 + 4.1 * (BW - CW) ** 0.5
    # Growth Requirement
    # ---------------------
    # [A.Cow.B.2]-[A.Heifer.B.2]
    # Net protein requirement for growth (g)
    if ADG == 0:
        NPg = 0
    else:
        NPg = ADG * (268 - 29.4 * (NEg / ADG))
    # [A.Cow.B.3]-[A.Heifer.B.3]
    # Efficiency of converting metabolizable protein to net protein
    if EQSBW <= 478:
        EffMP_NPg = (83.4 - 0.114 * EQSBW) / 100
    else:
        EffMP_NPg = 0.28908
    # [A.Cow.B.4]-[A.Heifer.B.4]
    # Metabolizable protein requirement for growth (g)
    MPg = NPg / EffMP_NPg
    # Pregnancy Requirement
    # ---------------------
    # [A.Cow.B.5]-[A.Heifer.B.5]
    # Metabolizable protein requirement for pregnancy (g)
    if DOP == None:
        MPpreg = 0
    elif DOP > 190:
        MPpreg = (0.69 * DOP - 69.2) * (CBW / (45 * 0.33))
    else:
        MPpreg = 0
    # Lactation Requirement
    # ---------------------
    if animal_type == 'cow':
        # [A.Cow.B.6]
        MPlact = Milk * (TP_Milk / 100) * (1000 / 0.67)
    # Total Protein Requirement  (g)
    # ---------------------
    if animal_type == 'cow':
        # [A.Cow.B.7]
        MP_req = MPm + MPg + MPpreg + MPlact
    elif animal_type == 'heifer':
        # [A.Heifer.B.6]
        MP_req = MPm + MPg + MPpreg
    return MP_req

def calculate_NASEM_protein_requirements():
    pass

def calculate_NRC_calcium_requirements(BW, MW, DOP, animal_type, lactating, ADG, Milk):
    # C: MINERAL REQUIREMENTS
    # Calcium and Phosphorus are the only requirements tracked currently
    # --------------------------------------------
    # Calcium Requirements
    # ----------------------
    if animal_type == 'cow':
        # [A.Cow.C.1]
        # Calcium maintenance requirement (g)
        if lactating:
            Ca_maint = 0.031 * BW + 0.08 * (BW / 100)
        else:
            Ca_maint = 0.0154 * BW + 0.08 * (BW / 100)
    elif animal_type == 'heifer':
        # [A.Heifer.C.1]
        # Calcium maintenance requirement (g)
        Ca_main = 0.0154*BW + 0.08*(BW/100)
    # [A.Cow.C.2]-[A.Heifer.C.2]
    # Calcium growth requirement (g)
    Ca_growth = 9.83 * MW ** 0.22 * BW ** (-0.22) * (ADG / 0.96)
    # [A.Cow.C.3]-[A.Heifer.C.3]
    # Calcium pregnancy requirement (g)
    if DOP == None:
        Ca_preg = 0
    elif DOP > 190:
        Ca_preg = 0.02456 * math.exp((0.05581 - 0.00007 * DOP) * DOP) - 0.02456 * \
                  math.exp((0.05581 - 0.00007 * (DOP - 1)) * (DOP - 1))
    else:
        Ca_preg = 0

    if animal_type == 'cow':
        # [A.Cow.C.4]
        # Calcium lactation requirement (g)
        Ca_lact = 1.22 * Milk
        # [A.Cow.C.5]
        # Total calcium requirement (g)
        Ca_req = Ca_maint + Ca_growth + Ca_preg + Ca_lact
    elif animal_type == 'heifer':
        # [A.Heifer.C.4]
        # Total calcium requirement (g)
        Ca_req = Ca_main + Ca_growth + Ca_preg
    return Ca_req

def calculate_NASEM_calcium_requirements():
    pass

# Mineral: Ca and P
def calculate_NRC_P_requirements(BW, MW, DOP, Milk, animal_type, ADG):
    # Phosphorus Requirements
    # ----------------------
    # [A.Cow.C.7]-[A.Heifer.C.6]
    # Phosphorus growth requirement (g)
    P_growth = (1.2 + 4.635 * MW ** 0.22 * BW ** (-0.22)) * (ADG / 0.96)
    # [A.Cow.C.8]-[A.Heifer.C.7]
    # Phosphorus pregnancy requirement (g)
    if DOP == None:
        P_preg = 0
    elif DOP > 190:
        P_preg = 0.02743 * math.exp((0.05527 - 0.000075 * DOP) * DOP) - 0.02743 * \
                 math.exp((0.05527 - 0.000075 * (DOP - 1)) * (DOP - 1))
    else:
        P_preg = 0

    if animal_type == 'cow':
        # [A.Cow.C.9]
        # Phosphorus lactation requirement (g)
        P_lact = 0.9 * Milk
    # Total phosphorus requirement (g)
    # (note this sum does not include the maintenance requirement which will
    # be calculated within the NLP and added to this sum)
    if animal_type == 'cow':
        # [A.Cow.C.10]
        P_req = P_growth + P_preg + P_lact
    elif animal_type == 'heifer':
        # [A.Heifer.C.8]
        P_req = P_growth + P_preg
    return P_req

def calculate_NASEM_P_requirements():
    pass

def calculate_DMI_NRC(animal_type: str, BW: float, DOP: int, DIM: int|None, 
                    lactating: bool|None, Milk:float, Fat_Milk:float):
    """
    Method to calculate dry matter intake in kg
        following NRC book 2001, Equations 1-2, pg.4, & Eq. on pg. 325
    # D: DMI ESTIMATION:
    # The sum of dry matter intake of each feed is assumed to be less than
    # dry matter intake estimation (Sum of Feed < DMIest).
    Args:
        BW: Body weight (kg)
        DIM: Days in milk
        DOP: Days of pregnancy (d) (except Heifer Is)
        lactating: Boolean value which is true for lactating cows
             and false for dry cows
        Milk: Milk production (kg)
        Fat_Milk: Milk fat content (% of milk)
    Return: 
        DMIest: estimate of dry matter intake
    """
    if animal_type=='cow':
        if lactating:
            FCM = (0.4 * Milk) + (15 * Fat_Milk * (Milk / 100))
            DMIest = (0.372 * FCM + 0.0968 * BW ** 0.75) \
                * (1 - math.exp(-0.192 * ((DIM / 7) + 3.67)))
        else:
            DMIest = ((1.97 - 0.75 * math.exp(0.16 * (DOP - 280))) / 100) * BW
    else:
        DMIest = 0 # TODO: Actual calculation for DMIest
                    # this comment is a holdover from the previous version
    return DMIest

def calculate_DMI_NASEM(BW: float, MW:float, DIM: int|None, 
                        lactating: bool | None, NEl: float,
                        BCS5: int|None, parity: int|None):
    """
    Method to calculate dry matter intake in kg
        following NASEM book 2021, Equation 2-1, pg.12 & Eq.2-3, pg.14
    # D: DMI ESTIMATION:
    # The sum of dry matter intake of each feed is assumed to be less than
    # dry matter intake estimation (Sum of Feed < DMIest).
    # Args:
        BW: Body weight (kg)
        MW: Mature body weight(kg)
        DIM: Days in milk
        lactating: Boolean value which is true for lactating cows and false for dry cows
        NEl: net energy requirement for lactation (Mcal)
        BCS5: Body Condition Score (1-5 basis)
        parity: Number of parity
    Return: 
        DMIest: estimate of dry matter intake
    """
    if BCS5==None:
        BCS5=3
        # print("Body condition score was 'None'")
    if lactating:
        DMIest = ((3.7 + parity*5.7)+0.305*NEl
            +0.022*BW+(-0.689-1.87*parity)*BCS5) \
                *(1-(0.212+parity*0.136)*math.exp(-0.053*DIM))
    else:
        DMIest = 0.022*MW*(1-math.exp(-1.54*(BW/MW)))
        """
        # TODO: implement this by getting NDF_concentration_percentage
            (neutral detergent fiber) from the feeds
        DMIest = (0.0226*MW*(1-math.exp(-1.47*(BW/MW))))\
            -(0.082*(NDF_concentration_percentage\
            -(23.1+56*(BW/MW)-30.6(BW/MW)^2)))
        """
    return DMIest

# TODO: change MW to mature_body_weight
# TODO: Change DOP to days_of_pregnancy
# TODO: Change BW to body_weight_kg
# TODO: Change FCM to fat_corrected_milk_kg
# TODO: Change DIM to days_in_milk
# TODO: Change BCS5 to body_condition_score_5
# TODO: Change Milk to milk_production_daily_kg
# TODO: Milken to milk_energy_Mcal_per_kg
# TODO: Change NEl to net_energy_for_lactation
# TODO: change other energy units - NEg, NEm, NEa
# TODO: change ADG, TP_Milk, CBW, EQSBW

def energy_activity_rqmts(BW, housing, distance):
    """
    Calculates the net energy for activity requirement portion of the energy
    requirements for animals. This is separate because it must be calculated after
    grouping due to pen input args and cannot be used individually on an animal.

    Arg(s):
        BW: BW: Body weight (kg)
        housing: Housing type (Barn or Grazing)
        distance: Daily walking distance (km)
    """
    # Activity requirements
    # ---------------------
    # [A.Cow.A.4]-[A.Heifer.A.5]
    # Net energy for activity requirement caused by grazing system (Mcal)
    if housing == 'Grazing':
        NEa1 = 0.0012 * BW
    else:
        NEa1 = 0
    # [A.Cow.A.6]-[A.Heifer.A.7]
    # Total net energy for activity requirement (Mcal)
    NEa = distance * 0.00045 * BW + NEa1
    return NEa
