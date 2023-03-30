"""
RUFAS: Ruminant Farm Systems Model
File name: growing_heifer_manure_excretion.py
Description: Determines manure excretion with information from the
    ration formulation, outputs used by the manure module.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
           Joseph Merhi, jm2257@cornell.edu
"""
from typing import Tuple

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.animal.manure.general_manure import AnimalManureExcretions
from RUFAS.routines.animal.manure.general_manure import calculate_phosphorus_excretion_values
from RUFAS.routines.animal.ration.ration_driver import ration_report


def manure_calculations(ration_formulation,
                        feed,
                        body_weight: float,
                        fecal_phosphorus: float,
                        urine_phosphorus_required: float) \
        -> Tuple[float, AnimalManureExcretions]:
    """Calculates the manure excretion values for a growing heifer with information from the ration formulation.

    Parameters
    ----------
    ration_formulation : Dict[str, float]
        Dictionary that stores the calculated ration.
    feed : Dict[str, float]
        A Feed object that contains information about the available feeds.
    body_weight : float
        Body weight of the current animal, kg.
    fecal_phosphorus : float
        Amount of fecal phosphorus excreted by the current animal, g.
    urine_phosphorus_required : float
        Amount of phosphorus required for urine production, g.

    Returns
    -------
    float
        Total amount of phosphorus excreted by the given animal, g.
    AnimalManureExcretions
        A dictionary that contains the manure excretion values as specified
            in the AnimalManureExcretions class definition.

    """
    # TODO: Same TODOs as in dry_cow_manure_excretion.py
    nutrient_amounts, nutrient_concentrations = ration_report(
        ration_formulation, feed.available_feeds)
    dry_matter_intake = nutrient_amounts['dm']
    CP_concentration = nutrient_concentrations['CP']
    potassium_concentration = nutrient_concentrations['potassium']
    ASH_concentration = nutrient_concentrations["ash"]
    NDF_concentration = nutrient_concentrations['NDF']
    EE_concentration = nutrient_concentrations["EE"]

    # Total urine, kg [A.3B.A.1]
    urine = 9.0

    # Manure excretion
    # Amount of feces and urine excreted daily by the growing heifer, kg [A.3B.A.2]
    total_manure_excreted = 4.158 * dry_matter_intake - 0.0246 * body_weight

    # Total solids excretion
    # Amount of dry material excreted by the growing heifer, kg [A.3F.A.3]
    total_solids = 0.178 * dry_matter_intake + 2.733

    # Total volatile solids, kg [A.3B.A.3]
    total_volatile_solids = 0.0073 * body_weight

    # Degradable volatile solids, kg [A.3A.A.5]
    degradable_volatile_solids = 0.9 * total_volatile_solids

    # Non-degradable volatile solids, kg [A.3A.A.6]
    non_degradable_volatile_solids = total_volatile_solids - degradable_volatile_solids

    # Nitrogen in liquid and solid manure, kg [A.3B.B.1]
    manure_nitrogen = (15.1
                       + 0.83 * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS) *
                       (CP_concentration * GeneralConstants.PROTEIN_TO_NITROGEN) / 100
                       ) * GeneralConstants.GRAMS_TO_KG

    # Nitrogen excretion in urine, kg [A.3B.B.2]
    urine_nitrogen = (14.3
                      + 0.510 * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS) *
                      (CP_concentration * GeneralConstants.PROTEIN_TO_NITROGEN) / 100
                      ) * GeneralConstants.GRAMS_TO_KG

    # Nitrogen excretion in feces, kg [A.3B.B.3]
    fecal_nitrogen = manure_nitrogen - urine_nitrogen  # TODO: Unused

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

    # Amount of potassium excreted, g [A.3B.B.4]
    potassium = dry_matter_intake * \
        (potassium_concentration / 100) * GeneralConstants.KG_TO_GRAMS

    # Methane emissions, g/day [A.3B.C.1]
    # Methane model = Boadi
    methane_emission = (38.62 + 26.44 * dry_matter_intake) * 0.554
    # TODO: Implement the other methane model - IPCC Tier 2

    phosphorus_excretion_values = calculate_phosphorus_excretion_values(
        daily_milk_production=0,
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
        total_solids=total_solids,
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
