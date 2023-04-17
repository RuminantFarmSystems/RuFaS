"""
RUFAS: Ruminant Farm Systems Model
File name: lactating_cow_manure_excretion.py
Description: Determines manure excretion with information from the ration
    formulation, outputs used by the manure module.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
           Joseph Merhi, jm2257@cornell.edu
"""
import math
from typing import Tuple

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.animal.manure.general_manure import AnimalManureExcretions
from RUFAS.routines.animal.manure.general_manure import calculate_phosphorus_excretion_values
from RUFAS.routines.animal.ration.ration_driver import ration_report


def manure_calculations(ration_formulation,
                        feed,
                        body_weight: float,
                        days_in_milk: int,
                        milk_protein: float,
                        daily_milk_production: float,
                        fecal_phosphorus: float,
                        urine_phosphorus_required: float,
                        methane_model: str,
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
        Methane model used for methane emission calculations, including Mutian, Mills, IPCC.
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
    nutrient_amounts, nutrient_concentrations = ration_report(
        ration_formulation, feed.available_feeds)
    dry_matter_intake = nutrient_amounts['dm']
    ASH_diet_content = nutrient_amounts['ash']
    ASH_concentration = nutrient_concentrations["ash"]
    dry_matter_concentration = nutrient_concentrations['dm']
    ADF_concentration = nutrient_concentrations['ADF']
    CP_concentration = nutrient_concentrations['CP']
    lignin_concentration = nutrient_concentrations['lignin']
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
    fecal_nitrogen = manure_nitrogen - urine_nitrogen

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
    urine_urea_nitrogen_concentration_lower_bound = 2
    urine_urea_nitrogen_concentration_upper_bound = 12
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
        methane_emission = (- 12
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
        phosphorus=manure_phosphorus_excreted,
        phosphorus_fraction=manure_phosphorus_fraction,
        potassium=potassium,
        methane=methane_emission
    )

    return total_phosphorus_excreted, manure_excretion_values
