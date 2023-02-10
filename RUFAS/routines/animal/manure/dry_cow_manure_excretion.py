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
    # TODO: Rename abbreviated variable names
    nutrient_amounts, nutrient_concentrations = ration_report(ration_formulation, feed.available_feeds)
    dry_matter_intake = nutrient_amounts['dm']
    CP_concentration = nutrient_concentrations['CP']
    potassium_concentration = nutrient_concentrations['potassium']
    ASH_concentration = nutrient_concentrations["ash"]  # TODO: Unused
    NDF_concentration = nutrient_concentrations['NDF']  # TODO: Unused
    EE_concentration = nutrient_concentrations["EE"]  # TODO: Unused
    ADF_concentration = nutrient_concentrations['ADF']
    starch_concentration = nutrient_concentrations['starch']

    # Amount of manure, kg [A.3D.A.1]
    total_manure_excreted = 0.022 * body_weight + 21.844

    # Total solids, kg/d [A.3D.A.2]
    total_solids = 0.178 * dry_matter_intake + 2.733

    # Nitrogen in liquid and solid manure , g [A.3D.B.1]
    nitrogen = 12.747 * dry_matter_intake + 1606.290 * CP_concentration / 100 - 117.5  # TODO: Divide by 1000?

    # Amount of potassium excreted, g/day [A.3D.B.3]
    potassium = 1000 * dry_matter_intake * potassium_concentration / 100

    # Methane Emissions [A.3F.C.1]
    methane_emission = (45.98 - 45.98 * math.exp(- ((- 0.0011 * starch_concentration / ADF_concentration) + 0.0045)
                                                 * metabolizable_energy_intake * 4.184)) / 0.05565

    phosphorus_excretion_values = calculate_phosphorus_excretion_values(
            daily_milk_production=daily_milk_production,
            total_manure_excreted=total_manure_excreted,
            fecal_phosphorus=fecal_phosphorus,
            urine_phosphorus_required=urine_phosphorus_required
    )

    (total_phosphorus_excreted, inorganic_phosphorus_fraction, organic_phosphorus_fraction,
     manure_phosphorus_excreted, manure_phosphorus_fraction) = phosphorus_excretion_values

    manure_excretion_values = AnimalManureExcretions(
            urea=0.340,  # TODO: Implement with correct equation
            urine=8,
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
