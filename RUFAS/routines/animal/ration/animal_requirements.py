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
from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.output_manager import OutputManager
om = OutputManager()
from typing import Optional
from typing import Dict
from RUFAS.routines.animal.ration import ration_constants

def calc_rqmts(body_weight: float, mature_body_weight: float, day_of_pregnancy: int, animal_type: str, parity: Optional[int] = 0,
               calving_interval: Optional[int] = None, milk_true_protein: Optional[float] = 0.0,
               milk_fat: Optional[float] = 0.0, milk_lactose: Optional[float] = 0.0,
               milk_production: Optional[float] = 0.0, days_in_milk: Optional[int] = None,
               lactating: Optional[bool] = False, body_condition_score_5: Optional[int] = 3,
               previous_temperature: Optional[float] = None, average_daily_gain_heifer: Optional[float] = None)\
                -> Dict[str, float]:
    """
    Calculates the dietary requirements of a single animal.

    The energy requirements calculated according to NRC (2001) or NASEM (2021) are values that are used
    to generate the constraints or RHS of the nonlinear program for diet optimization.
    Each calculation has a reference to the respective calculation in the pseudocode (both Cow and Heifer).
    (Note that arguments that are only for a single animal class are instantiated
    at None however the respective parameters must be set when calling said
    animal class)
    Parameters
    ----------
    body_weight: float
        Body weight (kg)
    mature_body_weight: float
        Mature body weight(kg)
    animal_type: str
        the type of animal
    day_of_pregnancy: str, optional
        Day of pregnancy (d) (except Heifer Is)
    # parameters for just cow requirements)
    parity: int, optional
        Number of parity
    calving_interval: int, optional
        Calving interval (d)
    milk_true_protein: float, optional
        Milk true protein content  (% of milk)
    milk_fat: float, optional
        Milk fat content (% of milk)
    milk_lactose: float, optional
        Milk lactose content (% of milk)
    milk_production: float, optional
        Milk production (kg)
    days_in_milk: int, optional
        Days in milk
    lactating: bool, optional
        Boolean value which is true for lactating cows and false for dry cows
    # parameters for just heifer requirements
    body_condition_score_5: int, optional
        Body Condition Score (1-5 basis)
    previous_temperature: float, optional
        Average daily temperature of last month, °C
    average_daily_gain_heifer: float, optional
        Average daily gain of a heifer
    Returns
    -------
    Dict[str, float]
        dictionary of requirement values, see individual functions for each key value pair
    """
    if AnimalBase.config['energy_and_nutrient_calculation_method'] == 'NRC':
        net_energy_maintenance, conceptus_weight, calf_birth_weight = calculate_NRC_energy_maintenance_requirements(
            body_weight, mature_body_weight, day_of_pregnancy, body_condition_score_5, previous_temperature,
            animal_type)
        net_energy_growth, average_daily_gain, equivalent_shrunk_body_weight = calculate_NRC_energy_growth_requirements(
            body_weight, mature_body_weight, conceptus_weight, animal_type, parity, calving_interval,
            average_daily_gain_heifer)
        net_energy_pregnancy = calculate_NRC_energy_pregnancy_requirements(
            day_of_pregnancy, calf_birth_weight)
        net_energy_lactation = calculate_NRC_energy_lactation_requirements(
            animal_type, milk_fat, milk_true_protein, milk_lactose, milk_production)
        metabolizable_protein_requirement = calculate_NRC_protein_requirements(
            body_weight, conceptus_weight, day_of_pregnancy, animal_type, milk_production, milk_true_protein,
            calf_birth_weight, net_energy_growth, average_daily_gain, equivalent_shrunk_body_weight)
        calcium_requirement = calculate_NRC_calcium_requirements(
            body_weight, mature_body_weight, day_of_pregnancy, animal_type, lactating, average_daily_gain,
            milk_production)
        phosphorus_requirement = calculate_NRC_phosphorus_requirements(
            body_weight, mature_body_weight, day_of_pregnancy, milk_production, animal_type, average_daily_gain)
        dry_matter_intake_estimate = calculate_NRC_DMI(
            animal_type, body_weight, day_of_pregnancy, days_in_milk, lactating, milk_production, milk_fat)

    elif AnimalBase.config['energy_and_nutrient_calculation_method'] == 'NASEM':
        net_energy_lactation = calculate_NASEM_energy_lactation_requirements(
            animal_type, milk_fat, milk_true_protein, milk_lactose, milk_production)
        dry_matter_intake_estimate = calculate_NASEM_DMI(
            body_weight, mature_body_weight, days_in_milk, lactating, net_energy_lactation, parity,
            body_condition_score_5)
        net_energy_maintenance, gravid_uterine_weight, uterine_weight = \
            calculate_NASEM_energy_maintenance_requirements(body_weight, mature_body_weight, day_of_pregnancy,
                                                            days_in_milk)
        net_energy_growth, average_daily_gain, frame_weight_gain = calculate_NASEM_energy_growth_requirements(
            body_weight, mature_body_weight, average_daily_gain_heifer, animal_type, parity, calving_interval)
        net_energy_pregnancy, gravid_uterine_weight_gain = calculate_NASEM_energy_pregnancy_requirements(
            lactating, day_of_pregnancy, days_in_milk, gravid_uterine_weight, uterine_weight)
        metabolizable_protein_requirement = calculate_NASEM_protein_requirements(
            lactating, body_weight, frame_weight_gain, gravid_uterine_weight_gain, dry_matter_intake_estimate,
            milk_true_protein, milk_production)
        calcium_requirement = calculate_NASEM_calcium_requirements(
            body_weight, mature_body_weight, day_of_pregnancy, average_daily_gain, dry_matter_intake_estimate,
            milk_true_protein, milk_production, parity)
        phosphorus_requirement = calculate_NASEM_phosphorus_requirements(
            body_weight, mature_body_weight, animal_type, day_of_pregnancy, average_daily_gain,
            dry_matter_intake_estimate, milk_true_protein, milk_production, parity)
    else:
        energy_and_nutrient_calculation_method_error = f"energy and nutrient calculation method \
            {AnimalBase.config['energy_and_nutrient_calculation_method']}\
            not supported"
        info_map = {"function": calc_rqmts}
        om.add_error("energy_and_nutrient_calculation_method_error",
                     energy_and_nutrient_calculation_method_error, info_map)
    # Requirements summary dictionary
    return {'NEmaint': net_energy_maintenance, 'NEg': net_energy_growth, 'NEpreg': net_energy_pregnancy,
            'NEl': net_energy_lactation, 'MP_req': metabolizable_protein_requirement, 'Ca_req': calcium_requirement,
            'P_req': phosphorus_requirement,'DMIest': dry_matter_intake_estimate}


def calculate_NRC_energy_maintenance_requirements(body_weight: float, mature_body_weight: float,
                                                  day_of_pregnancy: Optional[int], body_condition_score_5: int,
                                                  previous_temperature: Optional[float],
                                                  animal_type: str) -> tuple[float, float, float]:
    """ Calculates energy requirement for maintenance, conceptus weight, and calf birth weight 

    Calculates the estimated energy requirements requirements for maintenance in megacalories per day,
    as well as conceptus weight (kg) and calf birth weight (kg), according to NRC (2001).

    Parameters
    ----------
    body_weight : float
        Body weight (kg)
    mature_body_weight : float
        Mature body weight (kg)
    day_of_pregnancy : int
        Day of pregnancy (days)
    body_condition_score_5 : int
        Body condition score (score from 1 to 5)
    previous_temperature : float
        Adjustment for previous temperature
    animal_type : strF
        Animal type according to set categories in RuFaS model, 
        currently only expecting either 'heifer' or 'cow' 

    Returns
    -------
    net_energy_maintenance : float
        Net energy requirement for maintenance (mcal/day)
    conceptus_weight : float
        Conceptus weight (kg)
    calf_birth_weight : float
        Calf birth weight (kg)

    Notes
    -----
    Energy requirements for activity are not included within calculations for maintenance.

    References
    ----------
    .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
    Chapter 2 "Energy",pp. 18-25, 2001.

    """
    calf_birth_weight = mature_body_weight * 0.06275 if day_of_pregnancy else 0.0
    conceptus_weight = 0.0
    if day_of_pregnancy and day_of_pregnancy > 190:
        conceptus_weight = (18 + (day_of_pregnancy - 190)
                            * 0.665) * (calf_birth_weight / 45)
    if animal_type == 'cow':
        net_energy_maintenance = (
            0.08 * (body_weight - conceptus_weight) ** 0.75)
    elif animal_type == 'heifer':
        body_condition_score_9 = (body_condition_score_5 - 1) * 2 + 1
        net_energy_maintenance = (body_weight-conceptus_weight)**(0.75) * \
            (0.086*(0.8 + (body_condition_score_9 - 1) * 0.5)) + \
            0.0007*(20-previous_temperature)
    return net_energy_maintenance, conceptus_weight, calf_birth_weight


def calculate_NASEM_energy_maintenance_requirements(body_weight: float, mature_body_weight: float,
                                                    day_of_pregnancy: Optional[int], days_in_milk: Optional[int]) -> \
        tuple[float, float, float]:
    """ Calculates energy requirement for maintenance and two measures of uterine weight

    The estimated energy requirements requirements for maintenance are calculated in megacalories per day,
    as well as gravid uterine weight and uterine weight in kg, according to NASEM (2021).

    Parameters
    ----------
    body_weight : float
        Body weight (kg)
    mature_body_weight : float
        Mature body weight (kg)
    day_of_pregnancy : int
        Day of pregnancy (days)
    days_in_milk : int
        Days in milk (lactation)

    Returns
    -------
    net_energy_maintenance : float
        Net energy requirement for maintenance (mcal/day)
    gravid_uterine_weight : float
        Gravid uterine weight (kg))
    uterine_weight : float
        Uterine weight (kg))

    Notes
    -----
    # NASEM (2021) does not adjust energy requirements for environmental temperature as it assumes
    # that confinement conditions already provide comfort temperature to the animals.
    # This is something to consider and update for the grazing module
    # Instead of calculating calf_birth_weight, NASEM (2021) also contains standards calf_birth_weight and
    # mature_body_weight (tabulated values) for selected breeds (eg., Holstein)
    # Instead of estimating conceptus_weight, gain in pregnancy tissues is estimated:
    # (gravid_uterine_weight and uterine_weight).
    # day_of_pregnancy (Day of pregnancy) was kept instead of DGest (Day ofgestation) as it is in NASEM (2021) book.

    References
    ----------
    .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle, 8th edition."
        National Academic Press, Chapter 3 "Energy", pp. 29, 2021.
    """
    if day_of_pregnancy is None:
        net_energy_maintenance = 0.10*body_weight**0.75
        gravid_uterine_weight = 0.0
        uterine_weight = 0.0
    else:
        calf_birth_weight = mature_body_weight * 0.06275
        gravid_uterine_weight = (calf_birth_weight * 1.825) * \
                                 math.exp(-0.0243 -(0.0000245 * day_of_pregnancy) * (280 - day_of_pregnancy))
        if days_in_milk == None:
            days_in_milk = 0
        uterine_weight = ((calf_birth_weight * 0.2288) *
                           math.exp(-0.2*days_in_milk)) + 0.204
        net_energy_maintenance = 0.10 * \
            (body_weight-gravid_uterine_weight - uterine_weight)**0.75
    return net_energy_maintenance, gravid_uterine_weight, uterine_weight


def calculate_NRC_energy_growth_requirements(body_weight: float, mature_body_weight: float, conceptus_weight: float,
                                             animal_type: float, parity: int, calving_interval: Optional[int],
                                             average_daily_gain_heifer: Optional[float]) -> tuple[float, float, float]:
    """ Calculates energy requirement for growth and associated weight gain parameters.

    The estimated energy requirements requirements for growth in megacalories per day,
    and average daily gain and estimate of shrunk body weight, in kilograms are calculated according to NRC (2001).

    Parameters
    ----------
    body_weight : float
        Body weight (kg)
    mature_body_weight : float
        Mature body weight (kg)
    conceptus_weight : float
        Conceptus weight (kg)
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    parity : int
        Parity number (lactation 1, 2.. n)
    calving_interval : int
        Calving interval (days)
    average_daily_gain_heifer : float
        Average daily gain (grams per day)

    Returns
    -------
    net_energy_growth : float
        Net energy requirement for growth (Mcal/d)
    average_daily_gain : float
        Average daily gain (grams per day)
    equivalent_shrunk_body_weight : float
        Equivalent shrunk body weight (kilograms)

    References
    ----------
    .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
    Chapter 11 "Growth", pp. 234-243, 2001.
    """
    # Activity requirements
    # ---------------------
    # Activity requirements must be calculated after grouping and thus is in a
    # separate function
    # Growth requirements
    # ---------------------
    # [A.Cow.A.7]-[A.Heifer.A.8]
    # Mature shrunk body weight (kg)
    MSBW = 0.96 * mature_body_weight
    # [A.Cow.A.8]-[A.Heifer.A.9]
    # Shrunk body weight (kg)
    SBW = 0.96 * body_weight
    # [A.Cow.A.9]-[A.Heifer.A.10]
    # Empty body weight (kg)
    # EBW = 0.891 * SBW
    # [A.Cow.A.10]-[A.Heifer.A.11]
    # Equivalent shrunk body weight (kg)
    equivalent_shrunk_body_weight = (SBW - conceptus_weight) * (478 / MSBW)
    # [A.Cow.A.11]
    # Average Daily Gain (kg)
    if animal_type == 'cow':
        if parity == 1 and calving_interval != 0:
            average_daily_gain = ((0.92 - 0.82) * MSBW) / calving_interval
        elif parity == 2 and calving_interval != 0:
            average_daily_gain = ((1 - 0.92) * MSBW) / calving_interval
        else:
            average_daily_gain = 0.0
    # [A.Heifer.A.12]
    # Average Daily Gain (kg)
    elif animal_type == 'heifer':
        average_daily_gain = max(average_daily_gain_heifer, 0.0)
    # [A.Cow.A.12]-[A.Heifer.A.13]
    # Equivalent empty weight gain (kg)
    EQEBG = 0.956 * average_daily_gain
    # [A.Cow.A.13]-[A.Heifer.A.14]
    # Equivalent shrunk body weight (kg)
    EQEBW = 0.891 * equivalent_shrunk_body_weight
    # [A.Cow.A.14]-[A.Heifer.A.15]
    # Net energy for growth requirement (Mcal)
    net_energy_growth = 0.0635 * EQEBW ** 0.75 * EQEBG ** 1.097
    return net_energy_growth, average_daily_gain, equivalent_shrunk_body_weight


def calculate_NASEM_energy_growth_requirements(
    body_weight: float, mature_body_weight: float, average_daily_gain_heifer: Optional[float], animal_type: str,
    parity: int, calving_interval: Optional[int]) -> tuple[float, float, float]:
    """ Calculates energy requirement for growth, and also growth metrics

    Calculates the estimated energy requirements requirements for growth in megacalories per day,
    and associated growth metrics, according to NASEM (2021).

    Parameters
    ----------
    body_weight : float
        Body weight (kilograms)
    mature_body_weight : float
        Mature body weight (kilograms)
    average_daily_gain_heifer : float
        Average daily gain (grams per day)
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    parity : int
        Parity number (lactation 1, 2.. n)
    calving_interval : int
        Calving interval (days)

    Returns
    -------
    net_energy_growth : float
        Net energy requirement for frame growth (Mcal/d)
    average_daily_gain : float
        Average daily gain (grams per day)
    frame_weight_gain : float
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
    MSBW = 0.96 * mature_body_weight
    if animal_type == 'cow':
        if parity == 1 and calving_interval != 0:
            average_daily_gain = ((0.92 - 0.82) * MSBW) / calving_interval
        elif parity == 2 and calving_interval != 0:
            average_daily_gain = ((1 - 0.92) * MSBW) / calving_interval
        else:
            average_daily_gain = 0.0
    elif animal_type == 'heifer':
        average_daily_gain = max(average_daily_gain_heifer, 0.0)
    else:
        average_daily_gain = 0.0
    EBG = 0.85*average_daily_gain
    if average_daily_gain == 0:
        average_daily_gain = 0.00001  # fix to avoid divide by 0 error
    FatADG = (0.067 + 0.375*(body_weight/mature_body_weight)) * \
        EBG/average_daily_gain
    ProtADG = (0.201 - 0.081*(body_weight/mature_body_weight)) * \
        EBG/average_daily_gain
    frame_weight_gain = FatADG + ProtADG
    REFADG = (9.4*FatADG + 5.55*ProtADG)*average_daily_gain
    MEFrameADG = REFADG/0.4  # Possible future use for this calc, see docstring notes
    net_energy_growth = REFADG/0.61
    return net_energy_growth, average_daily_gain, frame_weight_gain


def calculate_NRC_energy_pregnancy_requirements(day_of_pregnancy: Optional[int], calf_birth_weight: float) -> float:
    """ Calculates energy requirement for pregnancy according to NRC (2001).

    Calculates the estimated energy requirements requirements for pregnancy in megacalories per day

    Parameters
    ----------
    day_of_pregnancy : int
        Day of pregnancy (days)
    calf_birth_weight : float
        Calf birth weight (kilograms)

    Returns
    -------
    net_energy_pregnancy : float
        Net energy requirement for pregnancy (Mcal/d)

    Notes
    -----
    # day_of_pregnancy are counted from 190 day_of_pregnancy once pregnancy is confirmed. Otherwise, this nutritional requirement is assumed to be zero.

    References
    ----------
    .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press, Chapter 2 "Energy", pp. 21-22, 2001.

    """
    # Pregnancy requirement
    # ---------------------
    # [A.Cow.A.15]-[A.Heifer.A.16]
    # Metabolizable energy requirement for pregnancy (Mcal)
    if day_of_pregnancy == None:
        MEpreg = 0.0
    elif day_of_pregnancy > 190:
        MEpreg = (2 * 0.00159 * day_of_pregnancy - 0.0352) * \
            (calf_birth_weight / (45 * 0.14))
    else:
        MEpreg = 0.0
    # [A.Cow.A.16]-[A.Heifer.A.17]
    # Net energy requirement for pregnancy (Mcal)
    net_energy_pregnancy = MEpreg * 0.64
    return net_energy_pregnancy


def calculate_NASEM_energy_pregnancy_requirements(lactating: bool, day_of_pregnancy: Optional[int],
                                                  days_in_milk: Optional[int], gravid_uterine_weight: float,
                                                  uterine_weight: float) -> tuple[float, float]:
    """ Calculates energy requirement for pregnancy and gravid uterine weight gain

    Calculates the estimated energy requirements requirements for pregnancy in megacalories per day,
    according to NASEM (2021).

    Parameters
    ----------
    lactating : bool
        Physiological condition
    day_of_pregnancy : int
        Day of pregnancy
    days_in_milk : int
        Days in milk (lactation, days)
    gravid_uterine_weight : float
        Gravid uterine weight (kilograms)
    uterine_weight : float
        Uterine weight (kilograms)

    Returns
    -------
    net_energy_pregnancy : float
        Net energy requirement for pregnancy (Mcal/d)
    gravid_uterine_weight_gain : float
        Daiy energy Requirement associated to increased gain of reproductive tissues as pregnancy advances (Mcal/d)

    Notes
    -----
    # Assumptions: tissue contains 0.882 Mcal of energy / kg; an ME to gestation energy efficiency of 0.14;
    # and ME to net_energy_lactation efficiency of 0.66.MEpreg = Metabolizable energy requirement for pregnancy, Mcal net_energy_lactation/day
    # day_of_pregnancy are counted from day 12 of pregnancy once it was confirmed and goes until day 280 day_of_pregnancy.

    References
    ----------
    .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle, 8th edition."
        National Academic Press, Chapter 3 "Energy", pp. 31-32, 2021.

    """

    if lactating:
        gravid_uterine_weight_gain = -0.2 * \
            days_in_milk * (uterine_weight - 0.204)
    elif day_of_pregnancy == None:
        gravid_uterine_weight_gain = 0.0
    else:
        gravid_uterine_weight_gain = (
            0.0243 - (0.0000245 * day_of_pregnancy)) * gravid_uterine_weight
    net_energy_pregnancy = gravid_uterine_weight_gain * (0.882 / 0.14) * 0.66
    return net_energy_pregnancy, gravid_uterine_weight_gain


def calculate_NRC_energy_lactation_requirements(animal_type: str, milk_fat: float, milk_true_protein: float,
                                                milk_lactose: float, milk_production: float) -> float:
    """ Calculates energy requirement for lactation according to NRC (2001).

    Calculates the estimated energy requirements requirements for lactation in megacalories per day

    Parameters
    ----------
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    milk_fat : float
        Fat contents in milk (%)
    milk_true_protein : float
        True protein contents in milk (%)
    milk_lactose : float
        Lactose contents in milk (%)
    milk_production: float
        Milk production (kg/d)

    Returns
    -------
    net_energy_lactation : float
        Net energy requirement for lactation (Mcal/d)

    References
    ----------
    .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press, Chapter 2 "Energy", pp. 19, 2001.

    """

    # Lactation requirement
    # ---------------------
    if animal_type == 'cow':
        # [A.Cow.A.17]
        # Milk energy (Mcal/kg of milk production)
        milk_energy_Mcal_per_kg = 0.0929 * milk_fat + \
            (0.0547 / 0.93) * milk_true_protein + 0.0395 * milk_lactose
        # [A.Cow.A.18]
        # Net energy requirement for lactation (Mcal)
        net_energy_lactation = milk_energy_Mcal_per_kg * milk_production
    else:
        net_energy_lactation = 0.0
    return net_energy_lactation


def calculate_NASEM_energy_lactation_requirements(animal_type: str, milk_fat: float, milk_true_protein: float,
                                                  milk_lactose: float, milk_production: float) -> float:
    """ Calculates energy requirement for lactation according to NASEM (2021).

    Calculates the estimated energy requirements requirements for lactation in megacalories per day

    Parameters
    ----------
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    milk_fat : float
        Fat contents in milk (%)
    milk_true_protein : float
        True protein contents in milk (%)
    milk_lactose : float
        Lactose contents in milk (%)
    milk_production: float
        Milk yield (kg/d)

    Returns
    -------
    net_energy_lactation : float
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
        milk_energy_Mcal_per_kg = 0.0929 * milk_fat + \
            (0.0547 / 0.93) * milk_true_protein + 0.0395 * milk_lactose
        net_energy_lactation = milk_energy_Mcal_per_kg * milk_production
    else:
        net_energy_lactation = 0.0
    return net_energy_lactation


def calculate_NRC_protein_requirements(body_weight: float, conceptus_weight: float, day_of_pregnancy: Optional[int],
                                       animal_type: str, milk_production: float, milk_true_protein: float,
                                       calf_birth_weight: float, net_energy_growth: float, average_daily_gain: float,
                                       equivalent_shrunk_body_weight: float, dry_matter_intake_estimate: float) -> float:
    """ Protein requirement for maintenance according to NRC (2001).

    Calculates the estimated total metabolizable protein requirement (MP) in kilograms per day

    Parameters
    ----------
    body_weight : float
        Body weight (kilograms)
    mature_body_weight : float
        Mature body weight (kilograms)
    conceptus_weight : float
        Conceptus weight (kilograms)
    day_of_pregnancy : int
        Day of pregnancy (days)
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    milk_production: float
        Milk yield (kg/d)
    milk_true_protein : float
        True protein contents in milk (%)
    calf_birth_weight : float
        Calf birth weight
    net_energy_growth : float
        Net energy requirement for growth (Mcal/d)
    average_daily_gain : float
        Average daily gain (grams per day)
    equivalent_shrunk_body_weight : float
        Equivalent shrunk body weight (kilograms)

    Returns
    -------
    metabolizable_protein_requirement : float
        Metabolizable protein requirement (grams per day)

    Notes
    -----
    MP_bactria: Bacteria metabolizable protein production, g  
    TDN: Total digestible nutrients 
    MPm: Metabolizable protein requirement for maintenance, g
    NPg: Net protein requirement for growth, g
    EffMP_NPg: Efficiency of converting metabolizable protein to net protein
    MPg: Metabolizable protein requirement for growth, g
    MPpreg: Metabolizable protein requirement for pregnancy, g
    MPlact: Metabolizable protein requirement for lactation, g 

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

    TDN_estimate = 0.7  
    # communication with Dr. Edward Garcia
    # TODO: Calculate TDN from the previous rations, when formulated. Using this constant as a placeholder value for the first formulation.
    MP_bactria_estimate = dry_matter_intake_estimate * \
        GeneralConstants.KG_TO_GRAMS * TDN_estimate * 0.13
    # communication with Dr. Edward Garcia, to calculate a placeholder MP bacteria value for the first formulation.

    MPm = 0.3 * (body_weight - conceptus_weight) ** 0.6 + \
        4.1 * (body_weight - conceptus_weight) ** 0.5 + \
        (dry_matter_intake_estimate * GeneralConstants.KG_TO_GRAMS * 0.03 - 0.5 * (MP_bactria_estimate / 0.68 - MP_bactria_estimate)) + \
        0.4 * 11.8 * dry_matter_intake_estimate / 0.67
    # Growth Requirement
    # ---------------------
    # [A.Cow.B.2]-[A.Heifer.B.2]
    # Net protein requirement for growth (g)
    if average_daily_gain == 0:
        NPg = 0.0
    else:
        NPg = average_daily_gain * \
            (268 - 29.4 * (net_energy_growth / average_daily_gain))
    # [A.Cow.B.3]-[A.Heifer.B.3]
    # Efficiency of converting metabolizable protein to net protein
    if equivalent_shrunk_body_weight <= 478:
        EffMP_NPg = (83.4 - 0.114 * equivalent_shrunk_body_weight) / 100
    else:
        EffMP_NPg = 0.28908
    # [A.Cow.B.4]-[A.Heifer.B.4]
    # Metabolizable protein requirement for growth (g)
    MPg = NPg / EffMP_NPg
    # Pregnancy Requirement
    # ---------------------
    # [A.Cow.B.5]-[A.Heifer.B.5]
    # Metabolizable protein requirement for pregnancy (g)
    if day_of_pregnancy == None:
        MPpreg = 0.0
    elif day_of_pregnancy > 190:
        MPpreg = (0.69 * day_of_pregnancy - 69.2) * \
            (calf_birth_weight / (45 * 0.33))
    else:
        MPpreg = 0.0
    # Lactation Requirement
    # ---------------------
    if animal_type == 'cow':
        # [A.Cow.B.6]
        MPlact = milk_production * \
            (milk_true_protein / 100) * (GeneralConstants.KG_TO_GRAMS / 0.67)
    # Total Protein Requirement  (g)
    # ---------------------
    if animal_type == 'cow':
        # [A.Cow.B.7]
        metabolizable_protein_requirement = MPm + MPg + MPpreg + MPlact
    elif animal_type == 'heifer':
        # [A.Heifer.B.6]
        metabolizable_protein_requirement = MPm + MPg + MPpreg
    return metabolizable_protein_requirement


def calculate_NASEM_protein_requirements(lactating: bool, body_weight: float, frame_weight_gain: float, 
                                        gravid_uterine_weight_gain: float, dry_matter_intake_estimate: float,
                                        milk_true_protein: float, milk_production: float) -> float:
    """ Calculates Protein requirement for maintenance according to NASEM (2021).

    Calculates the estimated total metabolizable protein requirement (MP) in kilograms per day

    Parameters
    ----------
    lactating : bool
        Physiological condition
    body_weight : float
        Body weight (kilograms)
    frame_weight_gain : float
        Frame weight gain refers to the accretion of both fat and protein in carcass (grams per day)
    gravid_uterine_weight_gain : float
        Daiy energy Requirement associated to increased gain of reproductive tissues as pregnancy advances (Mcal/d)
    dry_matter_intake_estimate : float
        Estimated dry matter intake according to empirical prediction equation within NASEM (2021) (kg/d)
    milk_true_protein : float
        True protein contents in milk (%)
    milk_production: float
        Milk yield (kg/d)

    Returns
    -------
    metabolizable_protein_requirement : float
        Total metabolizable protein requirement (grams per day)

    Notes
    -----
    As in the NRC (2021), the protein requirement is also divided into four components: maintenance, growth, pregnancy,
    and lactation (all of them on a metabolizable protein basis (MP, g/d).
    The MP is defined as the sum of rumen undegraded protein (RUP + microbial protein (MCP).
    MP requirements for maintenance includes: scurf + endogenous urinary loss + metabolic fecal protein.
    Current versions of RuFaS code for both NRC and NASEM do not split MP into physiological functions.

    NPscurf: Net protein requirement for scurf, g 
    NPEndUrin: Net protein requirement for endogenous urinary excretion, g 
    CPMFP: Crude protein in metabolic fecal protein, g 
    NPMFP: Net protein requirement for metabolic fecal protein, g  
    NPGrowth: Net protein requirement for body frame weight gain, g 
    NPGest: Net protein requirement for pregnancy, g 
    NPMilk: Net protein in milk, or milk true protein yield, g 
    TargetEffMP: Proposed target efficiencies of converting metabolizable protein to export proteins and body gain.

    # TODO Consider inclusion of equations for estimating requirement for Non-Essential Aminoacids (NEAA)

    References
    ----------
    .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle, 8th edition." 
        National Academic Press, Chapter 6 "Protein", pp. 69-104, 2021.
    """
    NPscurf = 0.20 * body_weight**(0.60) * 0.85
    NPEndUrin = 53 * GeneralConstants.NITROGEN_TO_PROTEIN * body_weight * 0.001
    NDF_conc = 0.3
    # TODO get the current NDF_conc
    # hardcoded '0.3' is a general value that works for initial simulation purposes
    # In pen.py, cow.py, heiferI, II, III, ration_driver. add the variable to the calc_rqmts call each time
    # something like:
    # NDF_conc = conc['NDF']
    # amount, conc = ration_report(self.ration, feed.available_feeds)
    CPMFP = (11.62 + 0.134 * NDF_conc) * dry_matter_intake_estimate
    NPMFP = CPMFP * 0.73
    NPGrowth = frame_weight_gain * 0.11 * 0.86
    NPGest = gravid_uterine_weight_gain * 125
    NPMilk = (milk_true_protein / 100) * milk_production * GeneralConstants.KG_TO_GRAMS
    TargetEffMP = 0.69
    if lactating:
        metabolizable_protein_requirement = ((NPscurf + NPMFP + NPMilk + NPGrowth) /
                                              TargetEffMP) + (NPGest/0.33) + NPEndUrin
    else:
        metabolizable_protein_requirement = (NPscurf + NPMFP) / TargetEffMP + \
            (NPGest/0.33) + (NPGrowth/0.40) + NPEndUrin
    return metabolizable_protein_requirement


def calculate_NRC_calcium_requirements(body_weight: float, mature_body_weight: float, day_of_pregnancy: Optional[int],
                                       animal_type: str, lactating: bool, average_daily_gain: float, milk_production)\
                                        -> float:
    """ Calculates total Calcium requirement according to NRC (2001).

    Calculates the estimated the total calcium requirement (Ca) in grams per day

    Parameters
    ----------
    body_weight : float
        Body weight (kilograms)
    mature_body_weight : float
        Mature body weight (kilograms)
    day_of_pregnancy : int
        Day of pregnancy (days)
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    lactating : bool
        To emphasyze this physiological condition?
    average_daily_gain : float
        Average daily gain (grams per day)
    milk_production: float
        Milk yield (kg/d)

    Returns
    -------
    calcium_requirement : float
        Calcium requirement (grams per day)

    References
    ----------
    .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
        Chapter 6 "Minerals",pp. 106-109. 2001.

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
            Ca_maint = 0.031 * body_weight + 0.08 * (body_weight / 100)
        else:
            Ca_maint = 0.0154 * body_weight + 0.08 * (body_weight / 100)
    elif animal_type == 'heifer':
        # [A.Heifer.C.1]
        # Calcium maintenance requirement (g)
        Ca_main = 0.0154*body_weight + 0.08*(body_weight/100)
    # [A.Cow.C.2]-[A.Heifer.C.2]
    # Calcium growth requirement (g)
    Ca_growth = 9.83 * mature_body_weight ** 0.22 * \
        body_weight ** (-0.22) * (average_daily_gain / 0.96)
    # [A.Cow.C.3]-[A.Heifer.C.3]
    # Calcium pregnancy requirement (g)
    if day_of_pregnancy == None:
        Ca_preg = 0.0
    elif day_of_pregnancy > 190:
        Ca_preg = 0.02456 * math.exp((0.05581 - 0.00007 * day_of_pregnancy) * day_of_pregnancy) - 0.02456 * \
            math.exp((0.05581 - 0.00007 * (day_of_pregnancy - 1))
                     * (day_of_pregnancy - 1))
    else:
        Ca_preg = 0.0
    if animal_type == 'cow':
        # [A.Cow.C.4]
        # Calcium lactation requirement (g)
        Ca_lact = 1.22 * milk_production
        # [A.Cow.C.5]
        # Total calcium requirement (g)
        calcium_requirement = Ca_maint + Ca_growth + Ca_preg + Ca_lact
    elif animal_type == 'heifer':
        # [A.Heifer.C.4]
        # Total calcium requirement (g)
        calcium_requirement = Ca_main + Ca_growth + Ca_preg
    return calcium_requirement


def calculate_NASEM_calcium_requirements(body_weight: float, mature_body_weight: float,
                                        day_of_pregnancy: Optional[int],average_daily_gain: float,
                                        dry_matter_intake_estimate: float, milk_true_protein: float,
                                        milk_production: float, parity: int) -> float:
    """ Calculates total Calcium requirement according to NASEM (2021).

    Calculates the estimated the total calcium requirement (Ca) in grams per day.

    Parameters
    ----------
    body_weight : float
        Body weight (kilograms)
    mature_body_weight : float
        Mature body weight (kilograms)
    day_of_pregnancy : int
        Day of pregnancy (days)
    average_daily_gain : float
        Average daily gain (grams per day)
    dry_matter_intake_estimate : float
        Estimated dry matter intake (kg/d)
    milk_true_protein : float
        True protein contents in milk (%)
    milk_production : float
        Milk yield (kg/d)

    Returns
    -------
    calcium_requirement : float
        Calcium requirement (grams per day)

    Notes
    -----
    NASEM (2021) calculation for both Ca and P requirements consider milk production variables.

    References
    ----------
    .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle, 8th edition."
        National Academic Press, Chapter 7 "Minerals" pp. 106-110, 2021.
    """
    Ca_Maint = 0.90*dry_matter_intake_estimate
    if parity <= 2:
        Ca_Growth = ((9.83 * mature_body_weight**-0.22) *
                 body_weight**-0.22)*average_daily_gain
    else:
        Ca_Growth = 0.0
    if day_of_pregnancy == None:
        Ca_Preg = 0.0
    else:
        Ca_Preg = 0.02456 * math.exp((0.05581-0.00007*day_of_pregnancy)*day_of_pregnancy) - 0.02456 * \
            math.exp((0.05581-0.00007*(day_of_pregnancy-1)) *
                     (day_of_pregnancy - 1)) * (body_weight/715)
    Ca_Lact = (0.295 + 0.239 * milk_true_protein) * milk_production
    calcium_requirement = Ca_Maint + Ca_Growth + Ca_Preg + Ca_Lact
    return max(calcium_requirement, ration_constants.minimum_calcium)


def calculate_NRC_phosphorus_requirements(body_weight: float, mature_body_weight: float, 
                                          day_of_pregnancy: Optional[int], milk_production: float, animal_type: str,
                                          average_daily_gain: float) -> float:
    """ Calculates total Phosphorus requirement according to NRC (2001).

    Calculates the estimated the total phosphorus requirement (P) in grams per day

    Parameters
    ----------
    body_weight : float
        Body weight (kilograms)
    mature_body_weight : float
        Mature body weight (kilograms)
    day_of_pregnancy : int
        Day of pregnancy (days)
    milk_production: float
        Milk yield (kg/d)
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    average_daily_gain : float
        Average daily gain (grams per day)

    Returns
    -------
    phosphorus_requirement : float
        Phosphorus requirement (grams per day)

    Notes
    -----
    This total phosphorus requirement (g) sum does not include the maintenance requirement which will
    be calculated within the NLP and added to this sum

    References
    ----------
    .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
        Chapter 6 "Minerals",pp. 109-118. 2001.
    """
    P_growth = (1.2 + 4.635 * mature_body_weight ** 0.22 *
                body_weight ** (-0.22)) * (average_daily_gain / 0.96)
    if day_of_pregnancy == None:
        P_preg = 0.0
    elif day_of_pregnancy > 190:
        P_preg = 0.02743 * math.exp((0.05527 - 0.000075 * day_of_pregnancy) * day_of_pregnancy) - 0.02743 * \
            math.exp((0.05527 - 0.000075 * (day_of_pregnancy - 1))
                     * (day_of_pregnancy - 1))
    else:
        P_preg = 0.0
    if animal_type == 'cow':
        P_lact = 0.9 * milk_production
    if animal_type == 'cow':
        phosphorus_requirement = P_growth + P_preg + P_lact
    elif animal_type == 'heifer':
        phosphorus_requirement = P_growth + P_preg
    return phosphorus_requirement


def calculate_NASEM_phosphorus_requirements(body_weight: float, mature_body_weight: float, animal_type: str, 
                                            day_of_pregnancy: Optional[int], average_daily_gain: float, 
                                            dry_matter_intake_estimate: float, milk_true_protein: float,
                                            milk_production: float, parity: int) -> float:
    """ Calculates total Phosphorus requirement according to NASEM (2021).

    Calculates the estimated the total phosphorus requirement (P) in grams per day

    Parameters
    ----------
    body_weight : float
        Body weight (kilograms)
    mature_body_weight : float
        Mature body weight (kilograms)
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    day_of_pregnancy : int
        Day of pregnancy (days)
    average_daily_gain : float
        Average daily gain (grams per day)
    dry_matter_intake_estimate : float
        Estimated dry matter intake (kg/d)
    milk_true_protein : float
        True protein contents in milk (%)
    milk_production: float
        Milk yield (kg/d)

    Returns
    -------
    phosphorus_requirement : float
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
        P_Maint = 1.0 * dry_matter_intake_estimate + 0.0006 * body_weight
    elif animal_type == "heifer":
        P_Maint = 0.8 * dry_matter_intake_estimate + 0.0006 * body_weight
    else:
        P_Maint = 0.0
    if parity <= 2:
        P_Growth = (1.2+4.635*mature_body_weight**0.22 *
                body_weight ** -0.22) * average_daily_gain
    else:
        P_Growth = 0.0
    if day_of_pregnancy == None:
        P_Preg = 0.0
    else:
        P_Preg = 0.02743 * math.exp(0.05527-0.000075*day_of_pregnancy)*day_of_pregnancy - 0.02743 * \
            math.exp((0.05527-0.000075*(day_of_pregnancy-1)) *
                     (day_of_pregnancy-1)*(body_weight / 715))
    if milk_true_protein == None or milk_production == None:
        P_Lact = 0.0
    else:
        P_Lact = milk_production * (0.49 + 0.13*milk_true_protein)
    phosphorus_requirement = P_Maint + P_Growth + P_Preg + P_Lact
    return max(phosphorus_requirement, ration_constants.minimum_phosophorus)


def calculate_NRC_DMI(animal_type: str, body_weight: float, day_of_pregnancy: int, days_in_milk: Optional[int],
                      lactating: bool, milk_production: float, milk_fat: float) -> float:
    """ Calculates dry matter intake according to NRC (2001).

    Calculates the estimated total dry matter intake in kilograms per day

    Parameters
    ----------
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    body_weight : float
        Body weight (kilograms)
    day_of_pregnancy : int
        Day of pregnancy (days)
    days_in_milk : int
        Days in milk (days)
    lactating : bool
        Physiological condition (conditional)
    milk_production : float
        Milk yield (kg/d)
    milk_fat : float
        Fat contents in milk (%)

    Returns
    -------
    dry_matter_intake_estimate : float
        Dry matter intake (kilograms per day)

    Notes
    -----
    The sum of dry matter intake of each feed is assumed to be less than
    dry matter intake estimation (Sum of Feed < dry_matter_intake_estimate).

    References
    ----------
    .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press, Chapter 1 "Dry Matter Intake",
        pp. 4; and pp. 325, 2001 (Equations 1 and 2).

    """
    if animal_type == 'cow':
        if lactating:
            fat_corrected_milk_kg = (
                0.4 * milk_production) + (15 * milk_fat * (milk_production / 100))
            dry_matter_intake_estimate = (0.372 * fat_corrected_milk_kg + 0.0968 * body_weight ** 0.75) \
                * (1 - math.exp(-0.192 * ((days_in_milk / 7) + 3.67)))
        else:
            dry_matter_intake_estimate = (
                (1.97 - 0.75 * math.exp(0.16 * (day_of_pregnancy - 280))) / 100) * body_weight
    else:
        net_energy_maintenance_diet = 1 # TODO update this method to retrieve values from nutrient composition of 
                                        # ration from previous formulation.
                                        # Currently using magic value set by Edward and Haowen
        dry_matter_intake_estimate = body_weight**0.75 * (0.2435*net_energy_maintenance_diet 
                                                          - 0.0466*net_energy_maintenance_diet**2 
                                                          - 0.1128) / net_energy_maintenance_diet
        if day_of_pregnancy and day_of_pregnancy >= 210:
            adjustment_factor = 1+((210-day_of_pregnancy) * 0.0025)
            dry_matter_intake_estimate -= adjustment_factor
        # this comment is a holdover from the previous version
    # TODO: below (and in the NASEM calculation) we use a flat minimum DMI value, but...
    #   should we also consider a % value as a proportion of their current body weight?
    dry_matter_intake_estimate_minimum_flat = ration_constants.minimum_DMI
    dry_matter_intake_estimate_minimum_percentage = ration_constants.minimum_DMI_percentage * body_weight
    return max(dry_matter_intake_estimate, dry_matter_intake_estimate_minimum_percentage, 
               dry_matter_intake_estimate_minimum_flat)


def calculate_NASEM_DMI(body_weight: float, mature_body_weight: float, days_in_milk: Optional[int],
                        lactating: bool, net_energy_lactation: float,
                        parity: int, body_condition_score_5: int) -> float:
    """ Calculates dry matter intake according to NASEM (2021).

    Calculates the estimated total dry matter intake in kilograms per day

    Parameters
    ----------
    animal_type : str
        Animal type according to set categories at RuFaS model: 'Calf', 'Heifer I II III, 'Cow'
    body_weight : float
        Body weight (kilograms)
    mature_body_weight : float
        Mature body weight (kilograms)
    days_in_milk : int
        Days in milk (days)
    lactating : bool
        Physiological condition (conditional)
    net_energy_lactation : float
        Net energy for lactation
    parity : int
        Parity number
    body_condition_score_5 : int
        Body condition score (score; scale from 1 to 5)

    Returns
    -------
    dry_matter_intake_estimate: float
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
        parity_adjustment_factor = 0
        if parity > 1:
            parity_adjustment_factor = 1 
        dry_matter_intake_estimate = ((3.7 + parity_adjustment_factor*5.7)+0.305*net_energy_lactation
                                      + 0.022*body_weight+(-0.689-1.87*parity_adjustment_factor)*body_condition_score_5) \
            * (1-(0.212+parity_adjustment_factor*0.136)*math.exp(-0.053*days_in_milk))
    else:
        dry_matter_intake_estimate = 0.022*mature_body_weight * \
            (1-math.exp(-1.54*(body_weight/mature_body_weight)))
        """
        # TODO: implement this by getting NDF_concentration_percentage
            (neutral detergent fiber) from the feeds
        dry_matter_intake_estimate = (0.0226*mature_body_weight*(1-math.exp(-1.47*(body_weight/mature_body_weight))))\
            -(0.082*(NDF_concentration_percentage\
            -(23.1+56*(body_weight/mature_body_weight)-30.6(body_weight/mature_body_weight)^2)))
        """
    dry_matter_intake_estimate_minimum_flat = ration_constants.minimum_DMI
    dry_matter_intake_estimate_minimum_percentage = ration_constants.minimum_DMI_percentage * body_weight
    return max(dry_matter_intake_estimate, dry_matter_intake_estimate_minimum_percentage, 
               dry_matter_intake_estimate_minimum_flat)


def energy_activity_rqmts(body_weight: float, housing: str, distance: Optional[float]) -> float:
    """
    Calculates the net energy for activity requirement portion of the energy
    requirements for animals. This is separate because it must be calculated after
    grouping due to pen input args and cannot be used individually on an animal. The estimated energy requirements requirements for activity in megacalories per day are calculated following either NRC or NASEM guidelines
    
    Parameters
    ----------
    body_weight : float
        Body weight (kg)
    housing : str
        Housing type (Barn or Grazing)
    distance : float
        NASEM: Estimated distance travels by the animal daily (km)
        NRC: Daily walking distance (km)
    
    Returns
    -------
    net_energy_activity : float
        Net energy requirement for activity (mcal/day)

    Notes
    -----
    # Activity requirement (net_energy_activity) is proportional to body weight and daily walking distance.
    # Grazing system and hilly topography will cost additional energy. 
    # This is not implemented yet in the current version of code.
    # The latter requires implementation with the grazing module.

    References
    ----------
    .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle, 8th edition."
        National Academic Press, Chapter 3 "Energy", pp. 30-31, 2021.
        
    """
    if AnimalBase.config['energy_and_nutrient_calculation_method'] == 'NRC':
        # Activity requirements
        # ---------------------
        # [A.Cow.A.4]-[A.Heifer.A.5]
        # Net energy for activity requirement caused by grazing system (Mcal)
        if housing == 'Grazing':
            net_energy_activity1 = 0.0012 * body_weight
        else:
            net_energy_activity1 = 0.0
        # [A.Cow.A.6]-[A.Heifer.A.7]
        # Total net energy for activity requirement (Mcal)
        net_energy_activity = distance * 0.00045 * body_weight + net_energy_activity1
        return net_energy_activity
    elif AnimalBase.config['energy_and_nutrient_calculation_method'] == 'NASEM':
        if housing == 'Barn':
            net_energy_activity = distance * 0.00035 * \
                body_weight
        elif housing == 'Grazing':
            # TODO This will be the DMI supplemented after grazing - requires grazing module implementation
            nonpasturekgDMI = 1
            net_energy_activity = distance * body_weight * \
                0.75 * ((600-12*nonpasturekgDMI))/600
        else:
            net_energy_activity = 0.0
        return net_energy_activity
