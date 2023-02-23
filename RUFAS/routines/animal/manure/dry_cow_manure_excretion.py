"""
RUFAS: Ruminant Farm Systems Model
File name: dry_cow_manure_excretion.py
Description: Determines manure excretion with information from the ration
    formulation, outputs used by the manure module.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
           Joseph Merhi, jm2257@cornell.edu
"""
from typing import Tuple

import math

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.animal.manure.general_manure import AnimalManureExcretions
from RUFAS.routines.animal.manure.general_manure import calculate_phosphorus_excretion_values
from RUFAS.routines.animal.ration.ration_driver import ration_report


def manure_calculations(ration_formulation,
                        feed,
                        body_weight: float,
                        daily_milk_production: float,
                        fecal_phosphorus: float,
                        urine_phosphorus_required: float,
                        metabolizable_energy_intake: float) \
        -> Tuple[float, AnimalManureExcretions]:
    """Calculates the manure excretion values for a non-lactating cow with information from the ration formulation.

    Parameters
    ----------
    ration_formulation : Dict[str, float]
        Dictionary that stores the calculated ration.
    feed : Dict[str, float]
        A Feed object that contains information about the available feeds.
    body_weight : float
        Body weight of the current animal, kg.
    daily_milk_production : float
        Daily milk production of the current animal, kg.
    fecal_phosphorus : float
        Amount of fecal phosphorus excreted by the current animal, g.
    urine_phosphorus_required : float
        Amount of phosphorus required for urine production, g.
    metabolizable_energy_intake : float
        Metabolizable energy intake, Mcal/kg dry matter.

    Returns
    -------
    float
        Total amount of phosphorus excreted by the given animal, g.
    AnimalManureExcretions
        A dictionary that contains the manure excretion values as specified
            in the AnimalManureExcretions class definition.

    # TODO: Further calculations to account for entire diet:
    DMI: dry matter intake, kg
    DM: dietary dry matter, % of diet
    CP: dietary crude protein, % of DM

    """
    # TODO: Add TypedDicts for ration_formulation and available feeds
    # TODO: Pass in available feeds directly instead of a Feed object
    # TODO: Rename abbreviated key names to full names
    nutrient_amounts, nutrient_concentrations = ration_report(ration_formulation, feed.available_feeds)
    dry_matter_intake = nutrient_amounts['dm']
    ash_diet_content = nutrient_amounts['ash']
    CP_concentration = nutrient_concentrations['CP']
    potassium_concentration = nutrient_concentrations['potassium']
    ASH_concentration = nutrient_concentrations["ash"]  # TODO: Unused
    NDF_concentration = nutrient_concentrations['NDF']
    EE_concentration = nutrient_concentrations["EE"]  # TODO: Unused
    ADF_concentration = nutrient_concentrations['ADF']
    starch_concentration = nutrient_concentrations['starch']

    # Total urine, kg [A.3F.A.1]
    urine = 15.4

    # Manure excretion
    # Amount of feces and urine excreted daily by the dry cow, kg [A.3F.A.2]
    total_manure_excreted = 0.022 * body_weight + 21.844

    # Total solids excretion
    # Amount of dry material excreted by the dry cow, kg [A.3F.A.3]
    total_solids = 0.178 * dry_matter_intake + 2.733

    # Organic matter intake, kg.
    organic_matter_intake = dry_matter_intake - ash_diet_content

    # Total volatile solids, kg [A.3F.A.4]
    total_volatile_solids = (-1.201
                             + 0.402 * organic_matter_intake
                             + 0.036 * NDF_concentration
                             - 0.024 * CP_concentration)

    # Degradable volatile solids, kg [A.3F.A.5]
    degradable_volatile_solids = (-1.017
                                  + 0.364 * organic_matter_intake
                                  + 0.029 * NDF_concentration
                                  - 0.023 * CP_concentration)

    # Non-degradable volatile solids, kg
    non_degradable_volatile_solids = total_volatile_solids - degradable_volatile_solids

    # Nitrogen in liquid and solid manure, kg [A.3F.B.1]
    manure_nitrogen = (12.747 * dry_matter_intake
                       + 1606.290 * (CP_concentration / 100)
                       - 117.5)

    # Nitrogen excretion in urine, kg [A.3F.B.2]
    urine_nitrogen = (14.3 + 0.510 * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS) * (CP_concentration / 100)
                      ) * GeneralConstants.GRAMS_TO_KG

    # Nitrogen excretion in feces, kg [A.3F.B.3]
    fecal_nitrogen = manure_nitrogen - urine_nitrogen  # TODO: Unused

    # Nitrogen concentration in urinary urea, g urea-N/L [A.3G.B.1]
    urinary_nitrogen_concentration = (urine_nitrogen * 100) / urine
    urine_urea_nitrogen_concentration = -1.16 + 0.86 * urinary_nitrogen_concentration

    # Total ammoniacal nitrogen concentration in the manure slurry,
    # g ammoniacal nitrogen/L manure slurry [A.3G.B.3]
    tan_percent_of_urea = 48.2 - 2.9 * urine_urea_nitrogen_concentration
    total_ammoniacal_nitrogen_concentration = (tan_percent_of_urea / 100) * urine_urea_nitrogen_concentration

    # Amount of potassium excreted, g [A.3D.B.3]
    potassium = dry_matter_intake * (potassium_concentration / 100) * GeneralConstants.KG_TO_GRAMS

    # Methane emissions, g/day [A.3F.C.1]
    # Methane model = 'Mills'
    methane_emission = (45.98 - 45.98 * math.exp(-((-0.0011 * starch_concentration / ADF_concentration) + 0.0045)
                                                 * metabolizable_energy_intake * 4.184)) / 0.05565
    # TODO: Implement the other methane model - IPCC Tier 2. But need to pass in a methane_model parameter first.

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
