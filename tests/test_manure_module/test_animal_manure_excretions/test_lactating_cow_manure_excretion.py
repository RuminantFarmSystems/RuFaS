import math

import pytest
from pytest import approx
from pytest_mock import MockerFixture

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.animal.manure.general_manure import AnimalManureExcretions
from RUFAS.routines.animal.manure.lactating_cow_manure_excretion import (
    manure_calculations,
)
from RUFAS.routines.animal.manure.lactating_cow_manure_excretion import (
    methane_mitigation,
)
from RUFAS.routines.animal.animal_module_constants import AnimalModuleConstants


@pytest.mark.parametrize(
    "NDF_concentration, EE_concentration, starch_concentration, methane_mitigation_method,\
          methane_mitigation_additive_amount, expected_reduction",
    [
        (35.0, 5.0, 20.0, "3-NOP", 70.0, -25.3169),
        (40.0, 4.0, 25.0, "Monensin", 20.0, -3.73),
        (45.0, 3.0, 30.0, "Essential Oils", 80.0, 0.0),
        (50.0, 2.0, 35.0, "Seaweed", 90.0, 0.0),
        (55.0, 1.0, 40.0, "None", 70.0, 0.0),
    ],
)
def test_methane_mitigation(
    NDF_concentration,
    EE_concentration,
    starch_concentration,
    methane_mitigation_method,
    methane_mitigation_additive_amount,
    expected_reduction,
):
    # Act
    actual_reduction = methane_mitigation(
        NDF_concentration,
        EE_concentration,
        starch_concentration,
        methane_mitigation_method,
        methane_mitigation_additive_amount,
    )

    # Assert
    assert actual_reduction == pytest.approx(expected_reduction, abs=1e-2)


@pytest.mark.parametrize(
    "methane_model, methane_mitigation_method",
    [
        ("Mutian", "3-NOP"),
        ("Mills", "Monensin"),
        ("IPCC", "Essential Oils"),
        ("IPCC", "Seaweed"),
        ("Mutian", "None"),
    ],
)
def test_lactating_cow_manure_calculations(  # noqa
    methane_model: str, methane_mitigation_method: str, mocker: MockerFixture
) -> None:
    """Unit test for the manure_calculations function in lactating_cow_manure_excretion.py."""
    # Arrange
    body_weight = 600.0
    days_in_milk = 150
    milk_protein = 3.5
    daily_milk_production = 25.0
    fecal_phosphorus = 1.0
    urine_phosphorus_required = 2.0
    milk_fat = 3.8
    metabolizable_energy_intake = 12.5
    dry_matter_intake = 30.0
    ASH_diet_content = 1.8
    ASH_concentration = 6.0
    dry_matter_concentration = 55.0
    ADF_concentration = 15.0
    CP_concentration = 16.0
    lignin_concentration = 4.0
    NDF_concentration = 36.0
    potassium_concentration = 1.0
    EE_concentration = 4.0
    starch_concentration = 19.0

    fecal_water = (
        1.987 * dry_matter_intake
        + 0.348 * ADF_concentration
        - 0.412 * CP_concentration
        - 0.074 * dry_matter_concentration
        - 0.0057 * days_in_milk
    )
    fecal_solids = -0.576 + 0.370 * dry_matter_intake - 0.075 * CP_concentration + 0.059 * ADF_concentration
    urine = -7.742 + 0.388 * dry_matter_intake + 0.726 * CP_concentration + 2.066 * milk_protein
    total_manure_excreted = fecal_water + fecal_solids + urine

    manure_nitrogen = (
        20.3
        + 0.654
        * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS)
        * (CP_concentration * GeneralConstants.PROTEIN_TO_NITROGEN)
        / GeneralConstants.FRACTION_TO_PERCENTAGE
    ) * GeneralConstants.GRAMS_TO_KG
    dry_matter_intake = max(dry_matter_intake, AnimalModuleConstants.MINIMUM_DMI_LACT)
    fecal_nitrogen = (-18.5 + 10.1 * dry_matter_intake) * GeneralConstants.GRAMS_TO_KG
    urine_nitrogen = manure_nitrogen - fecal_nitrogen

    organic_matter_intake = dry_matter_intake - ASH_diet_content
    degradable_volatile_solids = (
        -1.017 + 0.364 * organic_matter_intake + 0.029 * NDF_concentration - 0.023 * CP_concentration
    )
    total_volatile_solids = (
        -1.201 + 0.402 * organic_matter_intake + 0.036 * NDF_concentration - 0.024 * CP_concentration
    )
    non_degradable_volatile_solids = total_volatile_solids - degradable_volatile_solids

    urinary_nitrogen_concentration = (urine_nitrogen * GeneralConstants.KG_TO_GRAMS) / urine
    urine_urea_nitrogen_concentration = -1.16 + 0.86 * urinary_nitrogen_concentration
    urine_urea_nitrogen_concentration_lower_bound = 2
    urine_urea_nitrogen_concentration_upper_bound = 12
    if urine_urea_nitrogen_concentration < urine_urea_nitrogen_concentration_lower_bound:
        urine_urea_nitrogen_concentration = urine_urea_nitrogen_concentration_lower_bound
    elif urine_urea_nitrogen_concentration > urine_urea_nitrogen_concentration_upper_bound:
        urine_urea_nitrogen_concentration = urine_urea_nitrogen_concentration_upper_bound
    else:
        urine_urea_nitrogen_concentration = urine_urea_nitrogen_concentration
    tan_percent_of_urea = 48.2 - 2.9 * urine_urea_nitrogen_concentration
    total_ammoniacal_nitrogen_concentration = (
        tan_percent_of_urea / GeneralConstants.FRACTION_TO_PERCENTAGE
    ) * urine_urea_nitrogen_concentration

    potassium = (
        7.21 * dry_matter_intake + 15944 * potassium_concentration / GeneralConstants.FRACTION_TO_PERCENTAGE - 164.5
    )

    total_phosphorus_excreted = 4.0
    inorganic_phosphorus_fraction = 0.4
    organic_phosphorus_fraction = 0.6
    manure_phosphorus_excreted = 1.6
    manure_phosphorus_fraction = 0.3

    methane_mitigation_additive_amount = 0.0
    if methane_mitigation_method == "3-NOP":
        methane_mitigation_additive_amount = 70.0
    elif methane_mitigation_method == "Monensin":
        methane_mitigation_additive_amount = 24.0
    elif methane_mitigation_method == "Essential Oils":
        methane_mitigation_additive_amount = 0.0
    elif methane_mitigation_method == "Seaweed":
        methane_mitigation_additive_amount = 0.0
    methane_emission_original = 0.0
    if methane_model == "Mutian":
        methane_emission_original = (
            -126 + 11.3 * dry_matter_intake + 2.30 * NDF_concentration + 28.8 * milk_fat + 0.148 * body_weight
        )
    elif methane_model == "Mills":
        starch_to_ADF_concentration_ratio = -0.0011 * starch_concentration / ADF_concentration
        temp = -(starch_to_ADF_concentration_ratio + 0.0045) * metabolizable_energy_intake * 4.184
        methane_emission_original = 45.98 * (1 - math.exp(temp)) / 0.05565
    elif methane_model == "IPCC":
        soluble_residue = (
            GeneralConstants.FRACTION_TO_PERCENTAGE
            - ASH_concentration
            - NDF_concentration
            - CP_concentration
            - EE_concentration
        )
        gross_energy_concentration = (
            0.263 * CP_concentration + 0.522 * EE_concentration + 0.198 * NDF_concentration + 0.160 * soluble_residue
        )
        methane_emission_original = 0.065 * gross_energy_concentration * dry_matter_intake / 0.05565

    methane_yield_original = 0.0
    methane_yield_reduction = 0.0
    if dry_matter_intake != 0:
        methane_yield_original = methane_emission_original / dry_matter_intake
        methane_yield_reduction = methane_mitigation(
            NDF_concentration,
            EE_concentration,
            starch_concentration,
            methane_mitigation_method,
            methane_mitigation_additive_amount,
        )

    methane_emission = (
        methane_yield_original
        * (1 + methane_yield_reduction / GeneralConstants.FRACTION_TO_PERCENTAGE)
        * dry_matter_intake
    )

    # Patching
    mock_nutrient_amounts = {"dm": dry_matter_intake, "ash": ASH_diet_content}
    mock_nutrient_concentrations = {
        "ash": ASH_concentration,
        "dm": dry_matter_concentration,
        "ADF": ADF_concentration,
        "CP": CP_concentration,
        "lignin": lignin_concentration,
        "NDF": NDF_concentration,
        "potassium": potassium_concentration,
        "EE": EE_concentration,
        "starch": starch_concentration,
    }

    patch_for_calculate_phosphorus_excretion_values = mocker.patch(
        "RUFAS.routines.animal.manure.lactating_cow_manure_excretion.calculate_phosphorus_excretion_values"
    )
    patch_for_calculate_phosphorus_excretion_values.return_value = (
        total_phosphorus_excreted,
        inorganic_phosphorus_fraction,
        organic_phosphorus_fraction,
        manure_phosphorus_excreted,
        manure_phosphorus_fraction,
    )

    # Act
    actual_total_phosphorus_excreted: float
    manure_excretion_values: AnimalManureExcretions
    actual_total_phosphorus_excreted, manure_excretion_values = manure_calculations(
        body_weight=body_weight,
        days_in_milk=days_in_milk,
        milk_protein=milk_protein,
        daily_milk_production=daily_milk_production,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required,
        methane_model=methane_model,
        methane_mitigation_method=methane_mitigation_method,
        methane_mitigation_additive_amount=methane_mitigation_additive_amount,
        milk_fat=milk_fat,
        metabolizable_energy_intake=metabolizable_energy_intake,
        nutrient_amount=mock_nutrient_amounts,
        nutrient_conc=mock_nutrient_concentrations,
    )

    # Assert
    patch_for_calculate_phosphorus_excretion_values.assert_called_once_with(
        daily_milk_production=daily_milk_production,
        total_manure_excreted=total_manure_excreted,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required,
    )
    assert actual_total_phosphorus_excreted == approx(total_phosphorus_excreted)
    assert manure_excretion_values["urea"] == approx(urine_urea_nitrogen_concentration)
    assert manure_excretion_values["urine"] == approx(urine)
    assert manure_excretion_values["total_ammoniacal_nitrogen_concentration"] == approx(
        total_ammoniacal_nitrogen_concentration
    )
    assert manure_excretion_values["urine_nitrogen"] == approx(urine_nitrogen)
    assert manure_excretion_values["manure_nitrogen"] == approx(manure_nitrogen)
    assert manure_excretion_values["manure_mass"] == approx(total_manure_excreted)
    assert manure_excretion_values["total_solids"] == approx(fecal_solids)
    assert manure_excretion_values["degradable_volatile_solids"] == approx(degradable_volatile_solids)
    assert manure_excretion_values["non_degradable_volatile_solids"] == approx(non_degradable_volatile_solids)
    assert manure_excretion_values["inorganic_phosphorus_fraction"] == approx(inorganic_phosphorus_fraction)
    assert manure_excretion_values["organic_phosphorus_fraction"] == approx(organic_phosphorus_fraction)
    assert manure_excretion_values["phosphorus"] == approx(manure_phosphorus_excreted)
    assert manure_excretion_values["phosphorus_fraction"] == approx(manure_phosphorus_fraction)
    assert manure_excretion_values["potassium"] == approx(potassium)
    assert manure_excretion_values["enteric_methane_g"] == approx(methane_emission)
