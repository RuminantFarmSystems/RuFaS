import pytest
from pytest import approx
from pytest_mock import MockFixture

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.animal.manure.calf_manure_excretion import manure_calculations
from RUFAS.routines.animal.manure.general_manure import AnimalManureExcretions


@pytest.mark.parametrize("methane_model", [None, "dummy"])
def test_calf_manure_excretions(methane_model: str, mocker: MockFixture) -> None:
    """Unit test for the manure_calculations function in calf_manure_excretion.py."""
    # Arrange
    body_weight = 100.0
    fecal_phosphorus = 1.0
    urine_phosphorus_required = 2.0

    dry_matter_intake = 10.0
    mock_nutrient_amounts = {"dm": dry_matter_intake}
    CP_concentration = 11.0
    mock_nutrient_concentrations = {"CP": CP_concentration}

    total_manure_excreted = 3.45 * dry_matter_intake
    total_solids = 0.393 * dry_matter_intake
    total_volatile_solids = 0.0023 * body_weight
    degradable_volatile_solids = 0.9 * total_volatile_solids
    non_degradable_volatile_solids = total_volatile_solids - degradable_volatile_solids

    manure_nitrogen = (112.55 * dry_matter_intake * (CP_concentration / 100)) * GeneralConstants.GRAMS_TO_KG
    urine_nitrogen = 0.45 * manure_nitrogen

    methane_emission = 0.0
    if methane_model:
        methane_emission = (0.013 * (body_weight**0.75) * 4.184) / 0.05565

    total_phosphorus_excreted = 3.0
    inorganic_phosphorus_fraction = 0.4
    organic_phosphorus_fraction = 0.6
    manure_phosphorus_excreted = 1.2
    manure_phosphorus_fraction = 0.3
    patch_for_calculate_phosphorus_excretion_values = mocker.patch(
        "RUFAS.routines.animal.manure.calf_manure_excretion.calculate_phosphorus_excretion_values",
        return_value=(
            total_phosphorus_excreted,
            inorganic_phosphorus_fraction,
            organic_phosphorus_fraction,
            manure_phosphorus_excreted,
            manure_phosphorus_fraction,
        ),
    )

    urea = 9.52
    urine = 2
    total_ammoniacal_nitrogen_concentration = 0.14
    potassium = 0.0

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
    assert manure_excretion_values["urea"] == approx(urea)
    assert manure_excretion_values["urine"] == approx(urine)
    assert manure_excretion_values["total_ammoniacal_nitrogen_concentration"] == approx(
        total_ammoniacal_nitrogen_concentration
    )
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
