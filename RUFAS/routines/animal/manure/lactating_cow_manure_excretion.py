import math
from typing import Tuple

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.animal.manure.general_manure import AnimalManureExcretions
from RUFAS.routines.animal.manure.general_manure import calculate_phosphorus_excretion_values
from RUFAS.routines.animal.ration.ration_driver import RationReporter
from RUFAS.routines.animal.animal_module_constants import AnimalModuleConstants


def methane_mitigation(NDF_concentration: float,
                       EE_concentration: float,
                       starch_concentration: float,
                       CP_concentration: float,
                       methane_mitigation_method: str,
                       methane_mitigation_additive_amount: float) -> float:
    """Calculates reduction in methane yield (%) due to addition of certain methane mitigation feed additive.

    Parameters
    ----------
    NDF_concentration : float
        Concentration of neutral detergent fiber (NDF) in the ration.
    EE_concentration : float
        Concentration of ether extract (EE) in the ration.
    starch_concentration : float
        Concentration of starch in the ration.
    CP_concentration : float
        Concentration of crude protein (CP) in the ration.
    methane_mitigation_method: str
        Methane mitigation method used to reduce enteric methane emissions, including "3-NOP", "Monensin",
        "EssentialOils", and "Seaweed".
    methane_mitigation_additive_amount: float
        The amount of methane mitigation feed additive that is added, mg/kg dry matter intake (DMI).
        The recommended dose for 3-NOP is
        between 40 and 100 mg/kg DMI, while that for monensin is between 16 and 36 mg/kg DMI.

    Returns
    -------
    float
        Reduction in methane yield (methane production/DMI), %.
    """

    methane_yield_reduction = 0.0
    Monensin_CP_lower_bound = AnimalModuleConstants.MONENSIN_CP_LOWER_BOUND
    Monensin_CP_upper_bound = AnimalModuleConstants.MONENSIN_CP_UPPER_BOUND

    if methane_mitigation_method == "3-NOP":
        methane_yield_reduction = -30.8 - 0.226 * (methane_mitigation_additive_amount - 70.5) + 0.906 * (
            NDF_concentration - 32.9) + 3.871 * (EE_concentration - 4.2) - 0.337 * (starch_concentration - 21.1)
    elif methane_mitigation_method == "Monensin":
        if Monensin_CP_lower_bound <= CP_concentration <= Monensin_CP_upper_bound:
            methane_yield_reduction = (0.30054 - 0.00377 *
                                       methane_mitigation_additive_amount - 1.57832 * CP_concentration/100) * 100
        else:
            methane_yield_reduction = (
                0.03223 - 0.00410 * methane_mitigation_additive_amount) * 100
    elif methane_mitigation_method == "Essential Oils":
        methane_yield_reduction = 0.0
    elif methane_mitigation_method == "Seaweed":
        methane_yield_reduction = 0.0
    return methane_yield_reduction


def manure_calculations(ration_formulation,
                        feed,
                        body_weight: float,
                        days_in_milk: int,
                        milk_protein: float,
                        daily_milk_production: float,
                        fecal_phosphorus: float,
                        urine_phosphorus_required: float,
                        methane_model: str,
                        methane_mitigation_method: str,
                        methane_mitigation_additive_amount: float,
                        milk_fat: float,
                        metabolizable_energy_intake: float) \
        -> Tuple[float, AnimalManureExcretions]:
    """Calculates the manure excretion values for a cow with information from the ration formulation.

    Parameters
    ----------
    ration_formulation : Dict[str, float]
        Dictionary that stores the calculated ration.
    feed : Dict[str, float]
        A Feed object that contains information about the available feeds.
    body_weight : float
        Body weight of the current cow, kg.
    days_in_milk : int
        Days in milk, days.
    milk_protein : float
        Milk protein (from animal input), % of milk.
    daily_milk_production : float
        Daily milk production of the current cow, kg.
    fecal_phosphorus : float
        Amount of fecal phosphorus excreted by the current cow, g.
    urine_phosphorus_required : float
        Amount of phosphorus required for urine production, g.
    methane_model : str
        Methane model used for methane emission calculations, including "Mutian", "Mills", "IPCC".
    milk_fat : float
        Milk fat (from animal input), % of milk.
    metabolizable_energy_intake : float
        Metabolizable energy intake, Mcal/kg dry matter.

    Returns
    -------
    float
        Total amount of phosphorus excreted by the given animal, g.
    AnimalManureExcretions
        A dictionary that contains the manure excretion values as specified
            in the AnimalManureExcretions class definition.

    """
    nutrient_amounts, nutrient_concentrations = RationReporter.report_ration(
        ration_formulation, feed.available_feeds)
    dry_matter_intake = nutrient_amounts['dm']
    ASH_diet_content = nutrient_amounts['ash']
    ASH_concentration = nutrient_concentrations["ash"]
    dry_matter_concentration = nutrient_concentrations['dm']
    ADF_concentration = nutrient_concentrations['ADF']
    CP_concentration = nutrient_concentrations['CP']
    # lignin_concentration = nutrient_concentrations['lignin']
    NDF_concentration = nutrient_concentrations['NDF']
    potassium_concentration = nutrient_concentrations['potassium']
    EE_concentration = nutrient_concentrations["EE"]
    starch_concentration = nutrient_concentrations['starch']

    # Fecal water, kg [A.3E.A.1]
    fecal_water = (1.987 * dry_matter_intake
                   + 0.348 * ADF_concentration
                   - 0.412 * CP_concentration
                   - 0.074 * dry_matter_concentration
                   - 0.0057 * days_in_milk)
    # Total Solids, kg [A.3E.A.2]
    # The amount of fecal solids is assumed to be equivalent to the amount of total solids
    fecal_solids = (-0.576
                    + 0.370 * dry_matter_intake
                    - 0.075 * CP_concentration
                    + 0.059 * ADF_concentration)
    # Total urine, kg [A.3E.A.3]
    urine = (-7.742
             + 0.388 * dry_matter_intake
             + 0.726 * CP_concentration
             + 2.066 * milk_protein)

    # Manure excretion
    # Amount of feces and urine excreted daily by the growing heifer, kg [A.3E.A.4]
    total_manure_excreted = fecal_water + fecal_solids + urine

    # Total manure nitrogen, kg [A.3E.B.1]
    manure_nitrogen = (20.3
                       + 0.654 * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS) *
                       (CP_concentration * GeneralConstants.PROTEIN_TO_NITROGEN) / 100
                       ) * GeneralConstants.GRAMS_TO_KG

    # Urine nitrogen, kg [A.3E.B.2]
    urine_nitrogen = (12.0
                      + 0.333 * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS) *
                      (CP_concentration * GeneralConstants.PROTEIN_TO_NITROGEN) / 100
                      ) * GeneralConstants.GRAMS_TO_KG

    # Fecal nitrogen, kg [A.3B.B.3]
    # fecal_nitrogen = manure_nitrogen - urine_nitrogen

    # Organic matter intake, kg [A.2.A.3]
    organic_matter_intake = dry_matter_intake - ASH_diet_content

    # Degradable volatile solids, kg [A.3E.A.5]
    degradable_volatile_solids = (-1.017
                                  + 0.364 * organic_matter_intake
                                  + 0.029 * NDF_concentration
                                  - 0.023 * CP_concentration
                                  )

    # Total volatile solids, kg [A.3E.A.6]
    total_volatile_solids = (-1.201
                             + 0.402 * organic_matter_intake
                             + 0.036 * NDF_concentration
                             - 0.024 * CP_concentration
                             )

    # Non-degradable volatile solids, kg [A.3A.A.6]
    non_degradable_volatile_solids = total_volatile_solids - degradable_volatile_solids

    # Urinary N concentration, g N/kg [A.3G.B.1]
    urinary_nitrogen_concentration = (
        urine_nitrogen * GeneralConstants.KG_TO_GRAMS) / urine
    # Nitrogen concentration in urinary urea, g urea-N/L [A.3G.B.2]
    urine_urea_nitrogen_concentration = -1.16 + \
        0.86 * urinary_nitrogen_concentration

    # Clamp the urine urea nitrogen concentration to be between 2 and 12 g urea-N/L
    urine_urea_nitrogen_concentration_lower_bound = AnimalModuleConstants.URINE_UREA_NITROGEN_CONCENTRATION_LOWER_BOUND
    urine_urea_nitrogen_concentration_upper_bound = AnimalModuleConstants.URINE_UREA_NITROGEN_CONCENTRATION_UPPER_BOUND
    urine_urea_nitrogen_concentration = max(urine_urea_nitrogen_concentration_lower_bound, min(
        urine_urea_nitrogen_concentration, urine_urea_nitrogen_concentration_upper_bound))

    # Total ammoniacal nitrogen in the slurry top layer as a percentage of UUC, %, [A.3G.B.3]
    tan_percent_of_urea = 48.2 - 2.9 * urine_urea_nitrogen_concentration
    # Total ammoniacal nitrogen concentration in the manure slurry,
    # g ammoniacal nitrogen/L manure slurry [A.3G.B.4]
    total_ammoniacal_nitrogen_concentration = (
        tan_percent_of_urea / 100) * urine_urea_nitrogen_concentration

    # Amount of potassium excreted, g [A.3E.B.3]
    potassium = 7.21 * dry_matter_intake + 15944 * \
        potassium_concentration / 100 - 164.5

    # Methane Emissions
    methane_emission = 0.0
    if methane_model == "Mutian":  # [A.3E.C.1]
        methane_emission = (- 126
                            + 11.3 * dry_matter_intake
                            + 2.30 * NDF_concentration
                            + 28.8 * milk_fat
                            + 0.148 * body_weight)

    elif methane_model == "Mills":  # [A.3E.C.2]
        starch_to_ADF_concentration_ratio = -0.0011 * \
            starch_concentration / ADF_concentration
        temp = -(starch_to_ADF_concentration_ratio + 0.0045) * \
            metabolizable_energy_intake * 4.184
        methane_emission = 45.98 * (1 - math.exp(temp)) / 0.05565

    elif methane_model == "IPCC":  # IPCC
        # Calculating gross energy concentration (Moraes et al. 2014)
        soluble_residue = 100 - ASH_concentration - \
            NDF_concentration - CP_concentration - EE_concentration
        gross_energy_concentration = (0.263 * CP_concentration
                                      + 0.522 * EE_concentration
                                      + 0.198 * NDF_concentration
                                      + 0.160 * soluble_residue)  # [A.3B.C.2]
        methane_emission = 0.065 * gross_energy_concentration * \
            dry_matter_intake / 0.05565  # [A.3B.C.3]

    # Methane Mitigation
    methane_yield = 0.0
    methane_yield_reduction = 0.0
    if dry_matter_intake != 0:
        methane_yield = methane_emission/dry_matter_intake
        methane_yield_reduction = methane_mitigation(
            NDF_concentration, EE_concentration, starch_concentration, CP_concentration, methane_mitigation_method,
            methane_mitigation_additive_amount)

    methane_emission = methane_yield * \
        (1 + methane_yield_reduction/100) * dry_matter_intake

    phosphorus_excretion_values = calculate_phosphorus_excretion_values(
        daily_milk_production=daily_milk_production,
        total_manure_excreted=total_manure_excreted,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required
    )

    (total_phosphorus_excreted, inorganic_phosphorus_fraction, organic_phosphorus_fraction,
     manure_phosphorus_excreted, manure_phosphorus_fraction) = phosphorus_excretion_values

    manure_excretion_values = AnimalManureExcretions(
        urea=urine_urea_nitrogen_concentration,
        urine=urine,
        total_ammoniacal_nitrogen_concentration=total_ammoniacal_nitrogen_concentration,
        urine_nitrogen=urine_nitrogen,
        manure_nitrogen=manure_nitrogen,
        manure_mass=total_manure_excreted,
        total_solids=fecal_solids,
        degradable_volatile_solids=degradable_volatile_solids,
        non_degradable_volatile_solids=non_degradable_volatile_solids,
        inorganic_phosphorus_fraction=inorganic_phosphorus_fraction,
        organic_phosphorus_fraction=organic_phosphorus_fraction,
        non_water_inorganic_phosphorus_fraction=0.0,
        non_water_organic_phosphorus_fraction=0.0,
        phosphorus=manure_phosphorus_excreted,
        phosphorus_fraction=manure_phosphorus_fraction,
        potassium=potassium,
        enteric_methane_g=methane_emission
    )

    return total_phosphorus_excreted, manure_excretion_values
