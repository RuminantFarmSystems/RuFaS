import math
from typing import Tuple, Dict

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.animal.manure.general_manure import AnimalManureExcretions
from RUFAS.routines.animal.manure.general_manure import (
    calculate_phosphorus_excretion_values,
)
from RUFAS.routines.animal.animal_module_constants import AnimalModuleConstants


def manure_calculations(
    body_weight: float,
    daily_milk_production: float,
    fecal_phosphorus: float,
    urine_phosphorus_required: float,
    methane_model: str,
    metabolizable_energy_intake: float,
    nutrient_amount: Dict[str, float],
    nutrient_conc: Dict[str, float],
) -> Tuple[float, AnimalManureExcretions]:
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
    methane_model : str
        Methane model used for methane emission calculations, including Mills, IPCC.
    metabolizable_energy_intake : float
        Metabolizable energy intake, Mcal/kg dry matter.
    nutrient_amount : Dict[str, float]
        Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.
    nutrient_conc : Dict[str, float]
        Concentrations of nutrients in pen ration, calculated per animal, percentages.

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
    # TODO: Add TypedDicts for ration_formulation and available feeds - GitHub Issue #1218
    # TODO: Pass in available feeds directly instead of a Feed object - GitHub Issue #1218
    # TODO: Rename abbreviated key names to full names - GitHub Issue #1218
    nutrient_amounts = nutrient_amount
    nutrient_concentrations = nutrient_conc
    dry_matter_intake = nutrient_amounts["dm"]
    # ash_diet_content = nutrient_amounts['ash']
    CP_concentration = nutrient_concentrations["CP"]
    potassium_concentration = nutrient_concentrations["potassium"]
    ASH_concentration = nutrient_concentrations["ash"]
    NDF_concentration = nutrient_concentrations["NDF"]
    EE_concentration = nutrient_concentrations["EE"]
    ADF_concentration = nutrient_concentrations["ADF"]
    starch_concentration = nutrient_concentrations["starch"]
    # Soluble residue
    # Dietary percentage of soluble residues, % DM, in the note of [A.3B.C.2]
    soluble_residue = (
        (GeneralConstants.FRACTION_TO_PERCENTAGE - ASH_concentration)
        - NDF_concentration
        - CP_concentration
        - EE_concentration
    )
    # TODO: Further calculations to account for entire diet:- GitHub Issue #1218
    # DMI: dry matter intake, kg
    # DM: dietary dry matter, % of diet
    # CP: dietary crude protein, % of DM

    # Total urine, kg [A.3F.A.1]
    urine = 15.4

    # Manure excretion
    # Amount of feces and urine excreted daily by the dry cow, kg [A.3F.A.2]
    total_manure_excreted = 0.00711 * body_weight + 0.324 * CP_concentration + 0.259 * NDF_concentration + 8.05

    # Total solids excretion
    # Amount of dry material excreted by the dry cow, kg [A.3F.A.3]
    total_solids = 0.178 * dry_matter_intake + 2.733

    # Organic matter intake, kg [A.2.A.3]
    dry_matter_intake = max(dry_matter_intake, AnimalModuleConstants.MINIMUM_DMI_DRY)
    organic_matter_intake = (
        dry_matter_intake
        * (GeneralConstants.FRACTION_TO_PERCENTAGE - ASH_concentration)
        / GeneralConstants.FRACTION_TO_PERCENTAGE
    )

    # Total volatile solids, kg [A.3E.A.6]
    total_volatile_solids = (
        -1.201 + 0.402 * organic_matter_intake + 0.036 * NDF_concentration - 0.024 * CP_concentration
    )

    # Degradable volatile solids, kg [A.3E.A.5]
    degradable_volatile_solids = (
        -1.017 + 0.364 * organic_matter_intake + 0.029 * NDF_concentration - 0.023 * CP_concentration
    )

    # Non-degradable volatile solids, kg [A.3A.A.6]
    non_degradable_volatile_solids = total_volatile_solids - degradable_volatile_solids

    # Nitrogen in liquid and solid manure, kg [A.3B.B.1]
    manure_nitrogen = (
        15.1
        + 0.83
        * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS)
        * (CP_concentration * GeneralConstants.PROTEIN_TO_NITROGEN)
        / GeneralConstants.FRACTION_TO_PERCENTAGE
    ) * GeneralConstants.GRAMS_TO_KG

    # Nitrogen excretion in feces, kg [A.3B.B.2]
    fecal_nitrogen = (
        0.345
        + 0.317
        * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS)
        * (CP_concentration * GeneralConstants.PROTEIN_TO_NITROGEN)
        / GeneralConstants.FRACTION_TO_PERCENTAGE
    ) * GeneralConstants.GRAMS_TO_KG

    # Nitrogen excretion in urine, kg [A.3B.B.3]
    urine_nitrogen = manure_nitrogen - fecal_nitrogen

    # Urinary N concentration, g N/kg [A.3G.B.1]
    urinary_nitrogen_concentration = (urine_nitrogen * GeneralConstants.KG_TO_GRAMS) / urine
    # Nitrogen concentration in urinary urea, g urea-N/L [A.3G.B.2]
    urine_urea_nitrogen_concentration = -1.16 + 0.86 * urinary_nitrogen_concentration

    # Clamp the urine urea nitrogen concentration to be between 2 and 12 g urea-N/L
    urine_urea_nitrogen_concentration_lower_bound = AnimalModuleConstants.URINE_UREA_NITROGEN_CONCENTRATION_LOWER_BOUND
    urine_urea_nitrogen_concentration_upper_bound = AnimalModuleConstants.URINE_UREA_NITROGEN_CONCENTRATION_UPPER_BOUND
    urine_urea_nitrogen_concentration = max(
        urine_urea_nitrogen_concentration_lower_bound,
        min(
            urine_urea_nitrogen_concentration,
            urine_urea_nitrogen_concentration_upper_bound,
        ),
    )

     # Total ammoniacal nitrogen in the manure slurry, kg
    manure_total_ammoniacal_nitrogen = urine_nitrogen

    # Amount of potassium excreted, g [A.3B.B.4]
    potassium = (
        dry_matter_intake
        * (potassium_concentration / GeneralConstants.FRACTION_TO_PERCENTAGE)
        * GeneralConstants.KG_TO_GRAMS
    )

    # Methane emissions, g/day
    methane_emission = 0.0
    if methane_model == "Mills":
        # Methane model = 'Mills' [A.3E.C.2]
        methane_emission = (
            45.98
            - 45.98
            * math.exp(
                -((-0.0011 * starch_concentration / ADF_concentration) + 0.0045) * metabolizable_energy_intake * 4.184
            )
        ) / 0.05565
    else:
        # Default: IPCC Tier 2
        gross_energy_concentration = (
            0.263 * CP_concentration + 0.522 * EE_concentration + 0.198 * NDF_concentration + 0.160 * soluble_residue
        )  # [A.3B.C.2]
        methane_emission = (0.065 * gross_energy_concentration * dry_matter_intake) / 0.05565  # [A.3B.C.3]

    phosphorus_excretion_values = calculate_phosphorus_excretion_values(
        daily_milk_production=daily_milk_production,
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
        urea=urine_urea_nitrogen_concentration,
        urine=urine,
        manure_total_ammoniacal_nitrogen = manure_total_ammoniacal_nitrogen,
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
        potassium=potassium,
        enteric_methane_g=methane_emission,
    )

    return total_phosphorus_excreted, manure_excretion_values
