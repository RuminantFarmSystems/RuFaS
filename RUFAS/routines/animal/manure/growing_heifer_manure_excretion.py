"""
RUFAS: Ruminant Farm Systems Model
File name: growing_heifer_manure_excretion.py
Description: Determines manure excretion with information from the
    ration formulation, outputs used by the manure module.
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
    nutrient_amounts, nutrient_concentrations = ration_report(ration_formulation, feed.available_feeds)
    dry_matter_intake = nutrient_amounts['dm']
    CP_concentration = nutrient_concentrations['CP']
    potassium_concentration = nutrient_concentrations['potassium']
    ASH_concentration = nutrient_concentrations["ash"]
    NDF_concentration = nutrient_concentrations['NDF']
    EE_concentration = nutrient_concentrations["EE"]

    # Amount of manure, kg [A.3B.A.1]
    total_manure_excreted = 3.886 * dry_matter_intake - 0.029 * body_weight + 5.641

    # Total solids, kg/day [A.3B.A.2]
    total_solids = 0.0084 * body_weight

    # Nitrogen in liquid and solid manure, g/day [A.3D.B.1]
    nitrogen = 78.390 * dry_matter_intake * CP_concentration / 100 + 51.35  # TODO: Divide by 1000?

    # Amount of potassium excreted, g/day [A.3D.B.3]
    potassium = 1000 * dry_matter_intake * potassium_concentration / 100

    # Methane Emissions [A.3B.C.1]
    methane_emission = (38.62 + 26.44 * dry_matter_intake) * 0.554

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
            urine=7,
            total_ammoniacal_nitrogen=0.14,  # TODO: Implement with correct equation
            nitrogen=nitrogen,
            manure_mass=total_manure_excreted,
            total_solids=total_solids,
            degradable_volatile_solids=7087.413,  # TODO: Implement with correct equation
            non_degradable_volatile_solids=859.390,  # TODO: Implement with correct equation
            inorganic_phosphorus_fraction=inorganic_phosphorus_fraction,
            organic_phosphorus_fraction=organic_phosphorus_fraction,
            phosphorus=manure_phosphorus_excreted,
            phosphorus_fraction=manure_phosphorus_fraction,
            potassium=potassium,
            methane=methane_emission
    )

    return total_phosphorus_excreted, manure_excretion_values
