"""
RUFAS: Ruminant Farm Systems Model
File name: calf_manure_excretion.py
Description: Determines manure excretion with information from the ration
    formulation, outputs used by the manure module.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
           Joseph Merhi, jm2257@cornell.edu
"""
from typing import Tuple

from RUFAS.routines.animal.manure.general_manure import AnimalManureExcretions
from RUFAS.routines.animal.manure.general_manure import calculate_phosphorus_excretion_values
from RUFAS.routines.animal.ration.ration_driver import ration_report


def manure_calculations(ration_formulation,
                        feed,
                        body_weight: float,
                        fecal_phosphorus: float,
                        urine_phosphorus_required: float) \
        -> Tuple[float, AnimalManureExcretions]:
    """Calculates the manure excretion values for a calf with information from the ration formulation.

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
    # Manure excretion
    # Amount of feces and urine excreted daily by the calf, kg [A.3A.A.1]
    total_manure_excreted = 0.0567 * body_weight

    # Total solids excretion
    # Amount of dry material excreted by the calf, kg [A.3A.A.2]
    total_solids = 0.0093 * body_weight

    # Total volatile solids, kg/day [A.3A.A.3]
    total_volatile_solids = 0.0023 * body_weight

    # Degradable volatile solids, kg/day [A.3C.A.5]
    degradable_volatile_solids = 0.9 * total_volatile_solids

    # Non-degradable volatile solids, kg/day
    non_degradable_volatile_solids = total_volatile_solids - degradable_volatile_solids

    # Nitrogen excretion
    # Amount of nitrogen excreted by the calf, kg [A.3A.B.1]
    # TODO: Review this part. It was added to get the dry matter intake and CP concentration.
    nutrient_amounts, nutrient_concentrations = ration_report(ration_formulation, feed.available_feeds)
    dry_matter_intake = nutrient_amounts['dm']
    CP_concentration = nutrient_concentrations['CP']
    manure_nitrogen = 112.55 * dry_matter_intake * (CP_concentration / 100)
    urine_nitrogen = 0.45 * manure_nitrogen

    # Methane emissions, g/day [A.3A.C.1]
    methane_emission = (0.013 * (body_weight ** 0.75) * 4.184) / 0.05565

    phosphorus_excretion_values = calculate_phosphorus_excretion_values(
            daily_milk_production=0,
            total_manure_excreted=total_manure_excreted,
            fecal_phosphorus=fecal_phosphorus,
            urine_phosphorus_required=urine_phosphorus_required
    )

    (total_phosphorus_excreted, inorganic_phosphorus_fraction, organic_phosphorus_fraction,
     manure_phosphorus_excreted, manure_phosphorus_fraction) = phosphorus_excretion_values

    manure_excretion_values = AnimalManureExcretions(
            urea=0.340,  # TODO: Implement with correct equation
            urine=2,
            total_ammoniacal_nitrogen_concentration=0.14,  # TODO: Implement with correct equation
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
            potassium=0,
            methane=methane_emission
    )

    return total_phosphorus_excreted, manure_excretion_values
