from typing import Tuple, Dict

from RUFAS.general_constants import GeneralConstants
from ....shared_structures.animal_manure_excretions import AnimalManureExcretions
from RUFAS.routines.animal.manure.general_manure import (
    calculate_phosphorus_excretion_values,
)


def manure_calculations(
    body_weight: float,
    fecal_phosphorus: float,
    urine_phosphorus_required: float,
    methane_model: str,
    nutrient_amount: Dict[str, float],
    nutrient_conc: Dict[str, float],
) -> Tuple[float, AnimalManureExcretions]:
    """Calculates the manure excretion values for a calf with information from the ration formulation.

    Parameters
    ----------
    body_weight : float
        Body weight of the current animal, kg.
    fecal_phosphorus : float
        Amount of fecal phosphorus excreted by the current animal, g.
    urine_phosphorus_required : float
        Amount of phosphorus required for urine production, g.
    methane_model : str
        Methane model used for methane emission calculations, including Mutian, Mills, IPCC.
    nutrient_amount : Dict[str, float]
        Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.
    nutrient_conc : Dict[str, float]
        Concentration of nutrients in pen ration, calculated per animal, percentages.

    Returns
    -------
    float
        Total amount of phosphorus excreted by the given animal, g.
    AnimalManureExcretions
        A dictionary that contains the manure excretion values as specified
            in the AnimalManureExcretions class definition.

    Notes
    -----
    nutrient_amount_units = {
        "dm": "kg/animal",
        "CP": "percent of DM",
        "ADF": "percent of DM",
        "NDF": "percent of DM",
        "lignin": "percent of DM",
        "ash": "percent of DM",
        "phosphorus": "percent of DM",
        "potassium": "percent of DM",
        "N": "percent of DM",
    }
    """
    nutrient_amounts = nutrient_amount
    nutrient_concentrations = nutrient_conc
    dry_matter_intake = nutrient_amounts["dm"]
    CP_concentration = nutrient_concentrations["CP"]

    # Manure excretion
    # Amount of feces and urine excreted daily by the calf, kg [A.3A.A.1]
    total_manure_excreted = 3.45 * dry_matter_intake

    # Total urine, kg [A.3A.A.2]
    urine = 2.0

    # Total solids excretion
    # Amount of dry material excreted by the calf, kg [A.3A.A.3]
    total_solids = 0.393 * dry_matter_intake

    # Total volatile solids, kg/day [A.3A.A.4]
    total_volatile_solids = 0.0023 * body_weight

    # Degradable volatile solids, kg/day [A.3A.A.5]
    degradable_volatile_solids = 0.9 * total_volatile_solids

    # Non-degradable volatile solids, kg/day [A.3A.A.6]
    non_degradable_volatile_solids = total_volatile_solids - degradable_volatile_solids

    # Nitrogen excretion
    # Amount of nitrogen excreted by the calf, kg [A.3A.B.1]
    manure_nitrogen = (112.55 * dry_matter_intake * (CP_concentration / 100)) * GeneralConstants.GRAMS_TO_KG

    # Amount of urine nitrogen excreted by a calf, kg [A.3A.B.2]
    urine_nitrogen = 0.45 * manure_nitrogen

    # Methane emissions, g/day [A.3A.C.1]
    methane_emission = 0.0
    if methane_model:
        methane_emission = (0.013 * (body_weight**0.75) * 4.184) / 0.05565

    phosphorus_excretion_values = calculate_phosphorus_excretion_values(
        daily_milk_production=0,
        total_manure_excreted=total_manure_excreted,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required,
    )

    (
        total_phosphorus_excreted,
        inorganic_phosphorus_fraction,
        organic_phosphorus_fraction,
        manure_phosphorus_excreted,
        manure_phosphorus_fraction,
    ) = phosphorus_excretion_values

    manure_excretion_values = AnimalManureExcretions(
        urea=9.52,  # 0.340 mol/L TODO: Implement with correct equation GitHub Issue # 1216
        urine=urine,
        # TODO: Implement with correct equation GitHub Issue # 1216
        total_ammoniacal_nitrogen_concentration=0.14,
        urine_nitrogen=urine_nitrogen,
        manure_nitrogen=manure_nitrogen,
        manure_mass=total_manure_excreted,
        total_solids=total_solids,
        degradable_volatile_solids=degradable_volatile_solids,
        non_degradable_volatile_solids=non_degradable_volatile_solids,
        inorganic_phosphorus_fraction=inorganic_phosphorus_fraction,
        organic_phosphorus_fraction=organic_phosphorus_fraction,
        non_water_inorganic_phosphorus_fraction=0.0,
        non_water_organic_phosphorus_fraction=0.0,
        phosphorus=manure_phosphorus_excreted,
        phosphorus_fraction=manure_phosphorus_fraction,
        potassium=0,
        enteric_methane_g=methane_emission,
    )

    return total_phosphorus_excreted, manure_excretion_values
