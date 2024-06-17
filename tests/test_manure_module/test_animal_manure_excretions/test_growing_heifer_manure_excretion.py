import pytest
from pytest import approx
from pytest_mock import MockerFixture

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.animal.manure.general_manure import AnimalManureExcretions
from RUFAS.routines.animal.manure.growing_heifer_manure_excretion import (
    manure_calculations,
)


@pytest.mark.parametrize(
    "methane_model",
    [
        "Boadi",
        "IPCC",
    ],
)
def test_growing_heifer_manure_calculations(methane_model: str, mocker: MockerFixture) -> None:
    """Unit test for the manure_calculations function in growing_heifer_manure_excretion.py."""
    # Arrange
    body_weight = 100.0
    fecal_phosphorus = 1.0
    urine_phosphorus_required = 2.0

    dry_matter_intake = 10.0
    mock_nutrient_amounts = {"dm": dry_matter_intake}
    CP_concentration = 11.0
    potassium_concentration = 12.0
    ASH_concentration = 13.0
    NDF_concentration = 14.0
    EE_concentration = 15.0
    mock_nutrient_concentrations = {
        "CP": CP_concentration,
        "potassium": potassium_concentration,
        "ash": ASH_concentration,
        "NDF": NDF_concentration,
        "EE": EE_concentration,
    }

    total_manure_excreted = 4.158 * dry_matter_intake - 0.0246 * body_weight
    total_solids = 0.178 * dry_matter_intake + 2.733
    total_volatile_solids = 0.0073 * body_weight
    degradable_volatile_solids = 0.9 * total_volatile_solids
    non_degradable_volatile_solids = total_volatile_solids - degradable_volatile_solids
    urine = 9.0
    manure_nitrogen = (
        15.1
        + 0.83
        * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS)
        * (CP_concentration * GeneralConstants.PROTEIN_TO_NITROGEN / GeneralConstants.FRACTION_TO_PERCENTAGE)
    ) * GeneralConstants.GRAMS_TO_KG
    fecal_nitrogen = (
        0.345
        + 0.317
        * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS)
        * (CP_concentration * GeneralConstants.PROTEIN_TO_NITROGEN)
        / GeneralConstants.FRACTION_TO_PERCENTAGE
    ) * GeneralConstants.GRAMS_TO_KG
    urine_nitrogen = manure_nitrogen - fecal_nitrogen
    urinary_nitrogen_concentration = (urine_nitrogen * GeneralConstants.KG_TO_GRAMS) / urine
    urine_urea_nitrogen_concentration = -1.16 + 0.86 * urinary_nitrogen_concentration

    manure_total_ammoniacal_nitrogen = urine_nitrogen
    potassium = (
        dry_matter_intake
        * (potassium_concentration / GeneralConstants.FRACTION_TO_PERCENTAGE)
        * GeneralConstants.KG_TO_GRAMS
    )
    methane_emission = 0.0
    if methane_model:
        soluble_residue = (
            (GeneralConstants.FRACTION_TO_PERCENTAGE - ASH_concentration)
            - NDF_concentration
            - CP_concentration
            - EE_concentration
        )
        gross_energy_concentration = (
            0.263 * CP_concentration + 0.522 * EE_concentration + 0.198 * NDF_concentration + 0.160 * soluble_residue
        )
        methane_emission = (0.065 * gross_energy_concentration * dry_matter_intake) / 0.05565

    total_phosphorus_excreted = 4.0
    inorganic_phosphorus_fraction = 0.4
    organic_phosphorus_fraction = 0.6
    manure_phosphorus_excreted = 1.6
    manure_phosphorus_fraction = 0.3
    patch_for_calculate_phosphorus_excretion_values = mocker.patch(
        "RUFAS.routines.animal.manure.growing_heifer_manure_excretion.calculate_phosphorus_excretion_values",
        return_value=(
            total_phosphorus_excreted,
            inorganic_phosphorus_fraction,
            organic_phosphorus_fraction,
            manure_phosphorus_excreted,
            manure_phosphorus_fraction,
        ),
    )

    # Act
    actual_total_phosphorus_excreted: float
    manure_excretion_values: AnimalManureExcretions
    actual_total_phosphorus_excreted, manure_excretion_values = manure_calculations(
        body_weight=body_weight,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required,
        methane_model=methane_model,
        nutrient_amount=mock_nutrient_amounts,
        nutrient_conc=mock_nutrient_concentrations,
    )

    # Assert
    patch_for_calculate_phosphorus_excretion_values.assert_called_once_with(
        daily_milk_production=0,
        total_manure_excreted=total_manure_excreted,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required,
    )
    assert actual_total_phosphorus_excreted == approx(total_phosphorus_excreted)
    assert manure_excretion_values["urea"] == approx(urine_urea_nitrogen_concentration)
    assert manure_excretion_values["urine"] == approx(urine)
    assert manure_excretion_values["manure_total_ammoniacal_nitrogen"] == approx(manure_total_ammoniacal_nitrogen)
    assert manure_excretion_values["urine_nitrogen"] == approx(urine_nitrogen)
    assert manure_excretion_values["manure_nitrogen"] == approx(manure_nitrogen)
    assert manure_excretion_values["manure_mass"] == approx(total_manure_excreted)
    assert manure_excretion_values["total_solids"] == approx(total_solids)
    assert manure_excretion_values["degradable_volatile_solids"] == approx(degradable_volatile_solids)
    assert manure_excretion_values["non_degradable_volatile_solids"] == approx(non_degradable_volatile_solids)
    assert manure_excretion_values["inorganic_phosphorus_fraction"] == approx(inorganic_phosphorus_fraction)
    assert manure_excretion_values["organic_phosphorus_fraction"] == approx(organic_phosphorus_fraction)
    assert manure_excretion_values["phosphorus"] == approx(manure_phosphorus_excreted)
    assert manure_excretion_values["phosphorus_fraction"] == approx(manure_phosphorus_fraction)
    assert manure_excretion_values["potassium"] == approx(potassium)
    assert manure_excretion_values["enteric_methane_g"] == approx(methane_emission)
