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


def manure_calculations(body_weight: float, fecal_phosphorus: float, urine_phosphorus_required: float) \
        -> Tuple[float, AnimalManureExcretions]:
    """Calculates the manure excretion values for a calf with information from the ration formulation.

    Parameters
    ----------
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
    # Amount of manure, kg [A.3A.A.1]
    total_manure_excreted = 0.0567 * body_weight

    # Total solids, kg/day [A.3A.A.2]
    total_solids = 0.0093 * body_weight

    # Methane Emissions [A.3A.C.1]
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
            total_ammoniacal_nitrogen=0.14,  # TODO: Implement with correct equation
            nitrogen=532.407,  # TODO: Implement with correct equation
            manure_mass=total_manure_excreted,
            total_solids=total_solids,
            degradable_volatile_solids=7087.413,  # TODO: Implement with correct equation
            non_degradable_volatile_solids=859.390,  # TODO: Implement with correct equation
            inorganic_phosphorus_fraction=inorganic_phosphorus_fraction,
            organic_phosphorus_fraction=organic_phosphorus_fraction,
            phosphorus=manure_phosphorus_excreted,
            phosphorus_fraction=manure_phosphorus_fraction,
            potassium=0,
            methane=methane_emission
    )

    return total_phosphorus_excreted, manure_excretion_values
