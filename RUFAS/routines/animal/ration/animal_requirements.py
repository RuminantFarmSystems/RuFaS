"""
RUFAS: Ruminant Farm Systems Model
File name: animal_requirements.py
Description: Calculates the following energy, mineral, and dry matter intake
    estimation for a single animal using the function in this file.
Author(s): Chris VanKerkhove, cjv47@cornell.edu, 
            Joe Waddell jw2574@cornell.edu, 
            Edward Cabezas Garcia ec867@cornell.edu
"""

import math
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase


# TODO: change MW to mature_body_weight
# TODO: Change DOP to days_of_pregnancy
# TODO: Change BW to body_weight_kg
# TODO: Change FCM to fat_corrected_milk_kg
# TODO: Change DIM to days_in_milk
# TODO: Change BCS5 to body_condition_score_5
# TODO: Change Milk to milk_production_daily_kg
# TODO: Change Milken to milk_energy_Mcal_per_kg
# TODO: Change NEl to net_energy_for_lactation
# TODO: Change all other energy units: NEg, NEm, NEa,
# TODO: ADG, TP_Milk, CBW, EQSBW


def calc_rqmts(BW, MW, DOP, animal_type, parity=None, CI=None, TP_Milk=None, Fat_Milk=None,
               Lactose_Milk=None, Milk=None, DIM=None, lactating=None,
               BCS5=None, PrevTemp=None,
               ADG_heifer=None, Age=None, distance=None):
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
    if AnimalBase.config['energy_and_nutrient_calculation_method'] == 'NRC':
        NEmaint, CW, CBW = calculate_NRC_energy_maintenance_requirements(
            BW, MW, DOP, BCS5, PrevTemp, animal_type)
        NEg, ADG, EQSBW = calculate_NRC_energy_growth_requirements(
            BW, MW, CW, animal_type, parity, CI, ADG_heifer)
        NEpreg = calculate_NRC_energy_pregnancy_requirements(DOP, CBW)
        NEl = calculate_NRC_energy_lactation_requirements(
            animal_type, Fat_Milk, TP_Milk, Lactose_Milk, Milk)
        MP_req = calculate_NRC_protein_requirements(
            BW, CW, DOP, animal_type, Milk, TP_Milk, CBW, NEg, ADG, EQSBW)
        Ca_req = calculate_NRC_calcium_requirements(
            BW, MW, DOP, animal_type, lactating, ADG, Milk)
        P_req = calculate_NRC_P_requirements(
            BW, MW, DOP, Milk, animal_type, ADG)
        DMIest = calculate_NRC_DMI(
            animal_type, BW, DOP, DIM, lactating, Milk, Fat_Milk)
    elif AnimalBase.config['energy_and_nutrient_calculation_method'] == 'NASEM':
        NEl = calculate_NASEM_energy_lactation_requirements(
            animal_type, Fat_Milk, TP_Milk, Lactose_Milk, Milk)
        DMIest = calculate_NASEM_DMI(BW, MW, DIM, lactating, NEl, parity, BCS5)
        NEmaint, GrUterW, UterW = calculate_NASEM_energy_maintenance_requirements(
            BW, MW, DOP, DIM)
        NEg, ADG, Frame_Weight_Gain_g = calculate_NASEM_energy_growth_requirements(
            BW, MW, ADG_heifer, animal_type, parity, CI)
        NEpreg, GrUterWGain = calculate_NASEM_energy_pregnancy_requirements(
            lactating, DOP, DIM, GrUterW, UterW)
        MP_req = calculate_NASEM_protein_requirements(
            lactating, BW, Frame_Weight_Gain_g, GrUterWGain, DMIest, TP_Milk, Milk)
        Ca_req = calculate_NASEM_calcium_requirements(
            BW, MW, DOP, ADG, DMIest, TP_Milk, Milk)
        P_req = calculate_NASEM_P_requirements(
            BW, MW, animal_type, DOP, ADG, DMIest, TP_Milk, Milk)
    else:
        DMIest = []
        print(f"DMI estimation method \
            {AnimalBase.config['NASEM_or_NRC_requirement_calculations']}\
            not supported")
    # Requirements summary dictionary
    return {'NEmaint': NEmaint, 'NEg': NEg, 'NEpreg': NEpreg,
            'NEl': NEl, 'MP_req': MP_req, 'Ca_req': Ca_req, 'P_req': P_req,
            'DMIest': DMIest}


def calculate_NRC_energy_maintenance_requirements(BW: float, MW: float, DOP: int | None, BCS5: int | None, PrevTemp: float | None,
                                                  animal_type: str) -> tuple[float, float, float]:
    """ Calculates energy requirement for maintenance, conceptus weight, and calf birth weight 

    Calculates the estimated energy requirements requirements for maintenance in megacalories per day,
    as well as conceptus weight (kg) and calf birth weight (kg), according to NRC (2001).

    Parameters
    ----------
    BW : float
        Body weight (kilograms)
    MW : float
        Mature body weight (kilograms)
    DOP : int
        Days of pregnancy (days)
    BCS5 : int
        Body condition score (score from 1 to 5)
    PrevTemp : float
        Adjustment for previous temperature
    animal_type : strF
        Animal type according to set categories in RuFaS model, 
        currently only expecting either 'heifer' or 'cow' 

    Returns
    -------
    NEmaint : float
        Net energy requirement for maintenance (mcal/day)
    CW : float
        Conceptus weight (kilograms)
    CBW : float
        Calf birth weight (kilograms)

    Notes
    -----
    Energy requirements for activity are not included within calculations for maintenance.

    References
    ----------
    .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press, Chapter 2 "Energy",pp. 18-25, 2001.

    """
    CBW = MW * 0.06275
    if DOP == None:
        CW = 0
        CBW = 0
    elif DOP > 190:
        CW = (18 + (DOP - 190) * 0.665) * (CBW / 45)
    else:
        CW = 0
    if animal_type == 'cow':
        NEmaint = (0.08 * (BW - CW) ** 0.75)
    elif animal_type == 'heifer':
        BCDS9 = (BCS5 - 1) * 2 + 1
        NEmaint = (BW-CW)**(0.75) * \
            (0.086*(0.8 + (BCDS9 - 1) * 0.5)) + 0.0007*(20-PrevTemp)
    return NEmaint, CW, CBW


def calculate_NASEM_energy_maintenance_requirements(BW: float, MW: float, DOP: int | None, DIM: int | None) -> tuple[float, float, float]:
    """ Calculates energy requirement for maintenance and two measures of uterine weight

    Calculates the estimated energy requirements requirements for maintenance in megacalories per day,
    as well as gravid uterine weight and uterine weight in kg, according to NASEM (2021).

    Parameters
    ----------
    BW : float
        Body weight (kilograms)
    MW : float
        Mature body weight (kilograms)
    DOP : int
        Days of pregnancy (days)
    DIM : int
        Days in milk (lactation)

    Returns
    -------
    NEmaint : float
        Net energy requirement for maintenance in megacalories per day
    GrUterW : float
        Gravid uterine weight in kilograms
    UterW : float
        Uterine weight in kilograms

    Notes
    -----
    # NASEM (2021) does not adjust energy requirements for environmental temperature as it assumes
    # that confinement conditions already provide comfort temperature to the animals. Something to think for the grazing module?
    # Instead of calculating CBW, NASEM (2021) also contains standards CBW and MW (tabulated values) for selected breeds (eg., Holstein)
    # Instead of estimating CW, gain in pregnancy tissues is estimated (GrUterW and UterW).
    # DOP (days of pregnancy) was kept instead of DGest (days of gestation) as it is in NASEM (2021) book.

    References
    ----------
    .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle, 8th edition."
        National Academic Press, Chapter 3 "Energy", pp. 29, 2021.
    """
    if DOP == None:
        NEmaint = 0.10*(BW)**0.75
        GrUterW = 0
        UterW = 0
    else:
        CBW = MW * 0.06275
        GrUterW = (CBW * 1.825) * math.exp(-0.0243 -
                                           (0.0000245 * DOP) * (280 - DOP))
        if DIM == None:
            DIM = 0
        UterW = ((CBW * 0.2288) * math.exp(-0.2*DIM)) + 0.204
        NEmaint = 0.10*(BW-GrUterW - UterW)**0.75
    return NEmaint, GrUterW, UterW


def calculate_NRC_energy_activity_requirements():
    """ TODO refactor existing energy activity requirements function here
    #   Same as NRC (2021) included: NEa = distance * 0.00035 * BW
    """
    pass


def calculate_NASEM_energy_activity_requirements(BW: float, housing: str, distance: float | None) -> float:
    """ Calculates energy requirement for activity according to NASEM (2001).

    Calculates the estimated energy requirements requirements for maintenance in megacalories per day

    Parameters
    ----------
    BW : float
        Body weight (kilograms)
    housing : str
        Production system
    distance : float
        Estimated distance traveles by the animal daily (meters)

    Returns
    -------
    NEa : float
        Net energy requirement for activity in megacalories per day

    Notes
    -----
    # Activity requirement (NEa) is proportional to body weight and daily walking distance.
    # Grazing system and hilly topography will cost additional energy. This is not implemented yet in the current version of code.
    # The latter requires implementation with the grazing module.

    References
    ----------
    .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle, 8th edition."
        National Academic Press, Chapter 3 "Energy", pp. 30-31, 2021.
    """
    if housing == 'Barn':
        NEa = distance * 0.00035 * BW  # TODO This logic is the same as NRC \
        # following instructions by Edward C.G., but can or should be updated according to Kristan R.
    elif housing == 'Grazing':
        # TODO This will be the DMI supplemented after grazing - requires implementation with grazing module
        nonpasturekgDMI = 1
        NEa = distance * BW * 0.75 * ((600-12*nonpasturekgDMI))/600
    else:
        NEa = 0
    return NEa


def calculate_NRC_energy_growth_requirements(BW: float, MW: float, CW: float, animal_type: float, parity: int | None, 
    CI: int | None, ADG_heifer: float | None) -> tuple[float, float, float]:
    """ Calculates energy requirement for growth and associated weight gain parameters.

    Calculates the estimated energy requirements requirements for growth in megacalories per day, 
    and average daily gain and estimate of shrunk body weight, according to NRC (2001).

    Parameters
    ----------
    BW : float
        Body weight (kilograms)
    MW : float
        Mature body weight (kilograms)
    CW : float
        Conceptus weight (kilograms)
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    parity : int
        Parity number (lactation 1, 2.. n)
    CI : int
        Calving interval (days)
    ADG_heifer : float
        Average daily gain (grams per day)

    Returns
    -------
    NEg : float
        Net energy requirement for growth (Mcal/d)
    ADG : float
        Average daily gain (grams per day)
    EQSBW : float
        Equivalent shrunk body weight (kilograms)

    References
    ----------
    .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press, Chapter xx, pp. xx-xx, 2001.
    """
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


def calculate_NASEM_energy_growth_requirements(BW: float, MW: float, ADG_heifer: float | None, animal_type: str,
                                               parity: int | None, CI: int | None) -> tuple[float, float, float]:
    """ Calculates energy requirement for growth, and also growth metrics

    Calculates the estimated energy requirements requirements for growth in megacalories per day,
    and associated growth metrics, according to NASEM (2021).

    Parameters
    ----------
    BW : float
        Body weight (kilograms)
    MW : float
        Mature body weight (kilograms)
    ADG_heifer : float
        Average daily gain (grams per day)
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    parity : int
        Parity number (lactation 1, 2.. n)
    CI : int
        Calving interval (days)

    Returns
    -------
    NEg : float
        Net energy requirement for frame growth (Mcal/d)
    ADG : float
        Average daily gain (grams per day)
    Frame_Weight_Gain_g : float
        Frame weight gain refers to the accretion of both fat and protein in carcass (grams per day)

    Notes
    -----
    # In NASEM (2021), body frame gain (fat + protein) corresponds to the true growth and it is part
    # of the calculation which is further partitioned to body reserves or condition gain (or loss),
    # and pregnancy-associated gain (considered a pregnancy requirement).

    References
    ----------
    .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle, 8th edition."
        National Academic Press, Chapter 3 "Energy", pp. 32-35, 2021.

    """
    MSBW = 0.96 * MW
    # TODO Edward: check this logic. We hashed it out early on,
    #  but I want to be sure that it's correct for parity =0 or >2
    if animal_type == 'cow':
        if parity == 1 and CI != 0:
            ADG = ((0.92 - 0.82) * MSBW) / CI
        elif parity == 2 and CI != 0:
            ADG = ((1 - 0.92) * MSBW) / CI
        else:
            ADG = 0
    elif animal_type == 'heifer':
        ADG = max(ADG_heifer, 0)
    else:
        ADG = 0
    EBG = 0.85*ADG
    if ADG == 0:
        ADG = 0.0001  # TODO fix to avoid divide by 0 error
    FatADG = (0.067 + 0.375*(BW/MW))*EBG/ADG
    ProtADG = (0.201 - 0.081*(BW/MW))*EBG/ADG
    Frame_Weight_Gain_g = FatADG + ProtADG
    REFADG = (9.4*FatADG + 5.55*ProtADG)*ADG
    MEFrameADG = REFADG/0.4  # Possible future use for this calc, see docstring notes
    NEg = REFADG/0.61
    return NEg, ADG, Frame_Weight_Gain_g


def calculate_NRC_energy_pregnancy_requirements(DOP: int | None, CBW: float | None) -> float:
    """ Calculates energy requirement for pregnancy according to NRC (2001).

    Calculates the estimated energy requirements requirements for pregnancy in megacalories per day

    Parameters
    ----------
    DOP : int
        Days of pregnancy (days)
    CBW : float
        Calf birth weight (kilograms)

    Returns
    -------
    NEpreg : float
        Net energy requirement for pregnancy (Mcal/d)

    Notes
    -----
    # DOP are counted from 190 DOP once pregnancy is confirmed. Otherwise, this nutritional requirement is assumed to be zero.

    References
    ----------
    .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press, Chapter xx, pp. xx-xx, 2001.

    """
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


def calculate_NASEM_energy_pregnancy_requirements(lactating: bool | None, DOP: int | None, DIM: int | None, GrUterW: float,
                                                  UterW: float) -> tuple[float, float]:
    """ Calculates energy requirement for pregnancy and gravid uterine weight gain

    Calculates the estimated energy requirements requirements for pregnancy in megacalories per day,
    according to NASEM (2021).

    Parameters
    ----------
    lactating : bool
        Physiological condition
    DOP : int
        Days of pregnancy
    DIM : int
        Days in milk (lactation, days)
    GrUterW : float
        Gravid uterine weight (kilograms)
    UterW : float
        Uterine weight (kilograms)

    Returns
    -------
    NEpreg : float
        Net energy requirement for pregnancy (Mcal/d)
    GrUterWGain : float
        Daiy energy Requirement associated to increased gain of reproductive tissues as pregnancy advances (Mcal/d)

    Notes
    -----
    # Assumptions: tissue contains 0.882 Mcal of energy / kg; an ME to gestation energy efficiency of 0.14;
    # and ME to NEl efficiency of 0.66.MEpreg = Metabolizable energy requirement for pregnancy, Mcal NEl/day
    # DOP are counted from day 12 of pregnancy once it was confirmed and goes until day 280 DOP.

    References
    ----------
    .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle, 8th edition."
        National Academic Press, Chapter 3 "Energy", pp. 31-32, 2021.

    """

    if lactating:  # and after the first month?
        GrUterWGain = -0.2 * DIM * (UterW - 0.204)
    elif DOP == None:
        GrUterWGain = 0
    else:
        GrUterWGain = (0.0243 - (0.0000245 * DOP)) * GrUterW
    NEpreg = GrUterWGain * (0.882 / 0.14) * 0.66
    return NEpreg, GrUterWGain


def calculate_NRC_energy_lactation_requirements(animal_type: str, Fat_Milk: float | None, TP_Milk: float | None,
                                                Lactose_Milk: float | None, Milk: float | None) -> float:
    """ Calculates energy requirement for lactation according to NRC (2001).

    Calculates the estimated energy requirements requirements for lactation in megacalories per day

    Parameters
    ----------
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    Fat_Milk : float
        Fat contents in milk (%)
    TP_Milk : float
        True protein contents in milk (%)
    Lactose_Milk : float
        Lactose contents in milk (%)
    Milk: float
        Milk yield (kg/d)

    Returns
    -------
    NEl : float
        Net energy requirement for lactation (Mcal/d)

    References
    ----------
    .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press, Chapter xx, pp. xx-xx, 2001.

    """

    # Lactation requirement
    # ---------------------
    if animal_type == 'cow':
        # [A.Cow.A.17]
        # Milk energy (Mcal/kg of milk production)
        Milken = 0.0929 * Fat_Milk + \
            (0.0547 / 0.93) * TP_Milk + 0.0395 * Lactose_Milk
        # [A.Cow.A.18]
        # Net energy requirement for lactation (Mcal)
        NEl = Milken * Milk
    else:
        NEl = 0
    return NEl


def calculate_NASEM_energy_lactation_requirements(animal_type: str, Fat_Milk: float | None, TP_Milk: float | None,
                                                  Lactose_Milk: float | None, Milk: float | None) -> float:
    """ Calculates energy requirement for lactation according to NASEM (2021).

    Calculates the estimated energy requirements requirements for lactation in megacalories per day

    Parameters
    ----------
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    Fat_Milk : float
        Fat contents in milk (%)
    TP_Milk : float
        True protein contents in milk (%)
    Lactose_Milk : float
        Lactose contents in milk (%)
    Milk: float
        Milk yield (kg/d)

    Returns
    -------
    NEl : float
        Net energy requirement for lactation (Mcal/d)

    Notes
    -----
    Same calculations as done in the NRC (2001). Requiremets are based on milk yield and composition.

    References
    ----------
    .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle, 8th edition."
        National Academic Press, Chapter 3 "Energy", pp. 30, 2021.

    """
    if animal_type == 'cow':
        Milken = 0.0929 * Fat_Milk + \
            (0.0547 / 0.93) * TP_Milk + 0.0395 * Lactose_Milk
        NEl = Milken * Milk
    else:
        NEl = 0
    return NEl


def calculate_NRC_protein_requirements(BW: float, CW: float, DOP: int | None, animal_type: str, Milk: float | None,
                                       TP_Milk: float | None, CBW: float, NEg: float, ADG: float, EQSBW: float) -> float:
    """ Protein requirement for maintenance according to NRC (2001).

    Calculates the estimated total metabolizable protein requirement (MP) in kilograms per day

    Parameters
    ----------
    BW : float
        Body weight (kilograms)
    MW : float
        Mature body weight (kilograms)
    CW : float
        Conceptus weight (kilograms)
    DOP : int
        Days of pregnancy (days)
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    Milk: float
        Milk yield (kg/d)
    TP_Milk : float
        True protein contents in milk (%)
    CBW : float
        Calf birth weight
    NEg : float
        Net energy requirement for growth (Mcal/d)
    ADG : float
        Average daily gain (grams per day)
    EQSBW : float
        Equivalent shrunk body weight (kilograms)

    Returns
    -------
    MP_req : float
        Metabolizable protein requirement (grams per day)

    References
    ----------
    .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition."
        National Academic Press, Chapter 5 "Protein and Amino acids",pp. 67-69. 2001;

    """

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


def calculate_NASEM_protein_requirements(lactating: bool | None, BW: float, Frame_Weight_Gain_g: float, GrUterWGain: float,
                                         DMIest: float, TP_Milk: float | None, Milk: float | None) -> float:
    """ Calculates Protein requirement for maintenance according to NASEM (2021).

    Calculates the estimated total metabolizable protein requirement (MP) in kilograms per day

    Parameters
    ----------
    lactating : bool
        Physiological condition
    BW : float
        Body weight (kilograms)
    Frame_Weight_Gain_g : float
        Frame weight gain refers to the accretion of both fat and protein in carcass (grams per day)
    GrUterWGain : float
        Daiy energy Requirement associated to increased gain of reproductive tissues as pregnancy advances (Mcal/d)
    DMIest : float
        Estimated dry matter intake according to empirical prediction equation within NASEM (2021) (kg/d)
    TP_Milk : float
        True protein contents in milk (%)
    Milk: float
        Milk yield (kg/d)

    Returns
    -------
    MP_req : float
        Total metabolizable protein requirement (grams per day)

    Notes
    -----
    As in the NRC (2021), the protein requirement is also divided into four components: maintenance, growth, pregnancy,
    and lactation (all of them on a metabolizable protein basis (MP, g/d).
    The MP is defined as the sum of rumen undegraded protein (RUP + microbial protein (MCP).
    MP requirements for maintenance includes: scurf + endogenous urinary loss + metabolic fecal protein.
    Current versions of RuFaS code for both NRC and NASEM do not split MP into physiological functions.

    # TODO Consider inclusion of equations for estimating requirement for Non-Essential Aminoacids (NEAA)

    References
    ----------
    .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle, 8th edition." 
        National Academic Press, Chapter 6 "Protein", pp. 69-104, 2021.
    """
    NPscurf = 0.20*BW**(0.60)*0.85
    NPEndUrin = 53*6.25 * BW * 0.001
    NDF_conc = 0.3
    # TODO get the correct NDF_conc
    # In pen.py, cow.py, heiferI, II, III, ration_driver. add the variable to the calc_rqmts call each time
    # something like:
    # NDF_conc = conc['NDF']
    # amount, conc = ration_report(self.ration, feed.available_feeds)
    CPMFP = (11.62+0.134*NDF_conc)*DMIest
    NPMFP = CPMFP*0.73
    NPGrowth = Frame_Weight_Gain_g*0.11*0.86
    NPGest = GrUterWGain * 125
    if TP_Milk is None:
        TP_Milk = 0
    if Milk is None:
        Milk = 0
    # TODO CHECK THAT TP_MILK is in % or 0.1 decimal percent etc.
    NPMilk = TP_Milk*Milk*1000
    TargetEffMP = 0.69
    if lactating:  # TODO better mimic logic from NRC if computationally superior
        MP_req = ((NPscurf + NPMFP + NPMilk + NPGrowth) /
                  TargetEffMP) + (NPGest/0.33) + NPEndUrin
    else:
        MP_req = (NPscurf + NPMFP) / TargetEffMP + \
            (NPGest/0.33) + (NPGrowth/0.40) + NPEndUrin
    MP_req = MP_req/100  # correcting the units g/kg
    return MP_req


def calculate_NRC_calcium_requirements(BW: float, MW: float, DOP: int | None, animal_type: str, lactating: bool | None,
                                       ADG: float, Milk) -> float:
    """ Calculates total Calcium requirement according to NRC (2001).

    Calculates the estimated the total calcium requirement (Ca) in grams per day

    Parameters
    ----------
    BW : float
        Body weight (kilograms)
    MW : float
        Mature body weight (kilograms)
    DOP : int
        Days of pregnancy (days)
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    lactating : bool
        To emphasyze this physiological condition?
    ADG : float
        Average daily gain (grams per day)
    Milk: float
        Milk yield (kg/d)

    Returns
    -------
    Ca_req : float
        Calcium requirement (grams per day)

    References
    ----------
    .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press, Chapter xx "xxxxxx",pp. xx-xx;
        Chapter 6 "Minerals",pp. 106-109. 2001

    """

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


def calculate_NASEM_calcium_requirements(BW: float, MW: float, DOP: int | None, ADG: float, DMIest: float, TP_Milk: float | None,
                                         Milk: float | None) -> float:
    """ Calculates total Calcium requirement according to NASEM (2021).

    Calculates the estimated the total calcium requirement (Ca) in grams per day.

    Parameters
    ----------
    BW : float
        Body weight (kilograms)
    MW : float
        Mature body weight (kilograms)
    DOP : int
        Days of pregnancy (days)
    ADG : float
        Average daily gain (grams per day)
    DMIest : float
        Estimated dry matter intake (kg/d)
    TP_Milk : float
        True protein contents in milk (%)
    Milk : float
        Milk yield (kg/d)

    Returns
    -------
    Ca_req : float
        Calcium requirement (grams per day)

    Notes
    -----
    NASEM (2021) calculation for both Ca and P requirements consider milk production variables.

    References
    ----------
    .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle, 8th edition."
        National Academic Press, Chapter 7 "Minerals" pp. 106-110, 2021.
    """
    Ca_Maint = 0.90*DMIest
    Ca_Growth = ((9.83 * MW**-0.22) * BW**-0.22)*ADG
    if DOP == None:
        Ca_Preg = 0
    else:
        Ca_Preg = 0.02456 * math.exp((0.05581-0.00007*DOP)*DOP) - 0.02456 * \
            math.exp((0.05581-0.00007*(DOP-1)) * (DOP - 1)) * (BW/715)
    if TP_Milk == None:
        TP_Milk = 0
    if Milk == None:
        Milk = 0
    Ca_Lact = (0.295 + 0.239 * TP_Milk) * Milk
    Ca_Req = Ca_Maint + Ca_Growth + Ca_Preg + Ca_Lact
    return Ca_Req


def calculate_NRC_P_requirements(BW: float, MW: float, DOP: int | None, Milk: float | None, animal_type: str,
                                 ADG: float) -> float:
    """ Calculates total Phosphorus requirement according to NRC (2001).

    Calculates the estimated the total phosphorus requirement (P) in grams per day

    Parameters
    ----------
    BW : float
        Body weight (kilograms)
    MW : float
        Mature body weight (kilograms)
    DOP : int
        Days of pregnancy (days)
    Milk: float
        Milk yield (kg/d)
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    ADG : float
        Average daily gain (grams per day)

    Returns
    -------
    P_req : float
        Phosphorus requirement (grams per day)

    Notes
    -----
    This total phosphorus requirement (g) sum does not include the maintenance requirement which will
    be calculated within the NLP and added to this sum

    References
    ----------
    .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press, Chapter xx "xxxxxx",pp. xx-xx;
        Chapter 6 "Minerals",pp. 109-118. 2001
    """
    P_growth = (1.2 + 4.635 * MW ** 0.22 * BW ** (-0.22)) * (ADG / 0.96)
    if DOP == None:
        P_preg = 0
    elif DOP > 190:
        P_preg = 0.02743 * math.exp((0.05527 - 0.000075 * DOP) * DOP) - 0.02743 * \
            math.exp((0.05527 - 0.000075 * (DOP - 1)) * (DOP - 1))
    else:
        P_preg = 0
    if animal_type == 'cow':
        P_lact = 0.9 * Milk
    if animal_type == 'cow':
        P_req = P_growth + P_preg + P_lact
    elif animal_type == 'heifer':
        P_req = P_growth + P_preg
    return P_req


def calculate_NASEM_P_requirements(BW: float, MW: float, animal_type: str, DOP: int | None, ADG: float, DMIest: float,
                                   TP_Milk: float | None, Milk: float | None) -> float:
    """ Calculates total Phosphorus requirement according to NASEM (2021).

    Calculates the estimated the total phosphorus requirement (P) in grams per day

    Parameters
    ----------
    BW : float
        Body weight (kilograms)
    MW : float
        Mature body weight (kilograms)
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    DOP : int
        Days of pregnancy (days)
    ADG : float
        Average daily gain (grams per day)
    DMIest : float
        Estimated dry matter intake (kg/d)
    TP_Milk : float
        True protein contents in milk (%)
    Milk: float
        Milk yield (kg/d)

    Returns
    -------
    P_req : float
        Phosphorus requirement (grams per day)

    Notes
    -----
    NASEM (2021) calculation for both Ca and P requirements consider milk production variables.

    References
    ----------
    .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle, 8th edition."
        National Academic Press, Chapter 7 "Minerals" pp. 112, 2021.

    """
    if animal_type == "cow":
        P_Maint = 1.0 * DMIest + 0.0006 * BW
    elif animal_type == "heifer":
        P_Maint = 0.8 * DMIest + 0.0006 * BW
    else:
        P_Maint = 0
    P_Growth = (1.2+4.635*MW**0.22 * BW ** -0.22) * ADG
    if DOP == None:
        P_Preg = 0
    else:
        P_Preg = 0.02743 * math.exp(0.05527-0.000075)*DOP - 0.02743 * \
            math.exp((0.05527-0.000075*(DOP-1))*(DOP-1)*(BW / 715))
    if TP_Milk == None or Milk == None:
        P_Lact = 0
    else:
        P_Lact = Milk * (0.49 + 0.13*TP_Milk)
    P_Req = P_Maint + P_Growth + P_Preg + P_Lact
    return P_Req


def calculate_NRC_DMI(animal_type: str, BW: float, DOP: int, DIM: int | None,
                      lactating: bool | None, Milk: float | None, Fat_Milk: float | None) -> float:
    """ Calculates dry matter intake according to NRC (2001).

    Calculates the estimated total dry matter intake in kilograms per day

    Parameters
    ----------
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    BW : float
        Body weight (kilograms)
    DOP : int
        Days of pregnancy (days)
    DIM : int
        Days in milk (days)
    lactating : bool
        Physiological condition (conditional)
    Milk : float
        Milk yield (kg/d)
    Fat_Milk : float
        Fat contents in milk (%)

    Returns
    -------
    DMIest : float
        Dry matter intake (kilograms per day)

    Notes
    -----
    The sum of dry matter intake of each feed is assumed to be less than
    dry matter intake estimation (Sum of Feed < DMIest).

    References
    ----------
    .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press, Chapter 1 "Dry Matter Intake",
        pp. 4; and pp. 325, 2001 (Equations 1 and 2).

    """
    if animal_type == 'cow':
        if lactating:
            FCM = (0.4 * Milk) + (15 * Fat_Milk * (Milk / 100))
            DMIest = (0.372 * FCM + 0.0968 * BW ** 0.75) \
                * (1 - math.exp(-0.192 * ((DIM / 7) + 3.67)))
        else:
            DMIest = ((1.97 - 0.75 * math.exp(0.16 * (DOP - 280))) / 100) * BW
    else:
        DMIest = 0  # TODO: Actual calculation for DMIest
        # this comment is a holdover from the previous version
    return DMIest


def calculate_NASEM_DMI(BW: float, MW: float, DIM: int | None,
                        lactating: bool | None, NEl: float,
                        parity: int | None, BCS5: int = 3) -> float:
    """ Calculates dry matter intake according to NASEM (2021).

    Calculates the estimated total dry matter intake in kilograms per day

    Parameters
    ----------
    # TODO Please check NEl (meaning = net energy for lactation; this is the units for energy)
    # Not sure if that has to be in the code?. I guess you meant milken (milk energy)?
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    BW : float
        Body weight (kilograms)
    MW : float
        Mature body weight (kilograms)
    DIM : int
        Days in milk (days)
    lactating : bool
        Physiological condition (conditional)
    NEl : float
        Net energy for lactation
    parity : int
        Parity number
    BCS5 : int
        Body condition score (score; scale from 1 to 5)

    Returns
    -------
    DMIest: float
        Dry matter intake (kilograms per day)

    Notes
    -----
    The sum of dry matter intake of each feed is assumed to be less than
    dry matter intake estimation (Sum of Feed < DMIest).
    There are additional equation in NASEM (2021) book including neutral detergent concentrations in the diet
    for both lactating (page 12) and growing animals (page 14). [1]

    References
    ----------
    .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle, 8th edition."
        National Academic Press, Chapter 2 "Dry matter intake" pp. 7-20, 2021.
    """
    if lactating:
        DMIest = ((3.7 + parity*5.7)+0.305*NEl
                  + 0.022*BW+(-0.689-1.87*parity)*BCS5) \
            * (1-(0.212+parity*0.136)*math.exp(-0.053*DIM))
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
