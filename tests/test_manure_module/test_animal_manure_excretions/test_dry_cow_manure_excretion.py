import math

import pytest
from pytest import approx
from pytest_mock import MockerFixture

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.animal.manure.dry_cow_manure_excretion import manure_calculations
from RUFAS.routines.animal.manure.general_manure import AnimalManureExcretions

@pytest.mark.parametrize(
    'methane_model',
    [
        'Mills',
        'IPCC',
    ]
)
def test_dry_cow_manure_calculations(methane_model: str,
                                     mocker: MockerFixture) -> None:
    """Unit test for the manure_calculations function in dry_cow_manure_excretion.py."""
    # Arrange
    mock_ration_formulation = mocker.MagicMock()
    mock_feed = mocker.MagicMock()
    body_weight = 100.0
    daily_milk_production = 10.0
    fecal_phosphorus = 1.0
    urine_phosphorus_required = 2.0
    metabolizable_energy_intake = 3.0

    dry_matter_intake = 10.0
    ash_diet_content = 0.1
    mock_nutrient_amounts = {
        'dm': dry_matter_intake,
        'ash': ash_diet_content
    }
    CP_concentration = 11.0
    potassium_concentration = 12.0
    ASH_concentration = 13.0
    NDF_concentration = 14.0
    EE_concentration = 15.0
    ADF_concentration = 16.0
    starch_concentration = 17.0
    mock_nutrient_concentrations = {
        'CP': CP_concentration,
        'potassium': potassium_concentration,
        'ash': ASH_concentration,
        'NDF': NDF_concentration,
        'EE': EE_concentration,
        'ADF': ADF_concentration,
        'starch': starch_concentration
    }
    patch_for_ration_report = mocker.patch(
        'RUFAS.routines.animal.manure.dry_cow_manure_excretion.ration_report',
        return_value=(mock_nutrient_amounts, mock_nutrient_concentrations)
    )

    urine = 15.4
    total_manure_excreted = total_manure_excreted = (0.00711 * body_weight 
                            + 0.324 * CP_concentration
                            + 0.259 * NDF_concentration
                            + 8.05) 
    total_solids = 0.178 * dry_matter_intake + 2.733
    organic_matter_intake = dry_matter_intake - ash_diet_content
    total_volatile_solids = (-1.201
                             + 0.402 * organic_matter_intake
                             + 0.036 * NDF_concentration
                             - 0.024 * CP_concentration)
    degradable_volatile_solids = (-1.017
                                  + 0.364 * organic_matter_intake
                                  + 0.029 * NDF_concentration
                                  - 0.023 * CP_concentration)
    non_degradable_volatile_solids = total_volatile_solids - degradable_volatile_solids
    manure_nitrogen = (15.1 + 0.83 * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS) * (CP_concentration * GeneralConstants.PROTEIN_TO_NITROGEN) / 100
                       ) * GeneralConstants.GRAMS_TO_KG
    urine_nitrogen = (14.3 + 0.510 * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS) * (CP_concentration * GeneralConstants.PROTEIN_TO_NITROGEN) / 100
                      ) * GeneralConstants.GRAMS_TO_KG
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
    total_ammoniacal_nitrogen_concentration = (tan_percent_of_urea / 100) * urine_urea_nitrogen_concentration
    potassium = dry_matter_intake * (potassium_concentration / 100) * GeneralConstants.KG_TO_GRAMS
    
    methane_emission = 0.0
    if methane_model == "Mills": 
        methane_emission = (45.98 - 45.98 * math.exp(-((-0.0011 * starch_concentration / ADF_concentration) + 0.0045)
                                                 * metabolizable_energy_intake * 4.184)) / 0.05565
    else:
        soluble_residue = (100 - ASH_concentration) - NDF_concentration - CP_concentration - EE_concentration
        gross_energy_concentration = (0.263 * CP_concentration + 0.522 * EE_concentration 
                                    + 0.198 * NDF_concentration + 0.160 * soluble_residue) 
        methane_emission = (0.065 * gross_energy_concentration * dry_matter_intake) / 0.05565 
    
    total_phosphorus_excreted = 5.0
    inorganic_phosphorus_fraction = 0.4
    organic_phosphorus_fraction = 0.6
    manure_phosphorus_excreted = 1.8
    manure_phosphorus_fraction = 0.3
    patch_for_calculate_phosphorus_excretion_values = mocker.patch(
        'RUFAS.routines.animal.manure.dry_cow_manure_excretion.calculate_phosphorus_excretion_values',
        return_value=(
            total_phosphorus_excreted,
            inorganic_phosphorus_fraction,
            organic_phosphorus_fraction,
            manure_phosphorus_excreted,
            manure_phosphorus_fraction
        )
    )

    # Act
    actual_total_phosphorus_excreted: float
    manure_excretion_values: AnimalManureExcretions
    actual_total_phosphorus_excreted, manure_excretion_values = manure_calculations(
        ration_formulation=mock_ration_formulation,
        feed=mock_feed,
        body_weight=body_weight,
        daily_milk_production=daily_milk_production,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required,
        methane_model=methane_model,
        metabolizable_energy_intake=metabolizable_energy_intake
    )

    # Assert
    patch_for_ration_report.assert_called_once_with(mock_ration_formulation, mock_feed.available_feeds)
    patch_for_calculate_phosphorus_excretion_values.assert_called_once_with(
        daily_milk_production=daily_milk_production,
        total_manure_excreted=total_manure_excreted,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required
    )
    assert actual_total_phosphorus_excreted == approx(total_phosphorus_excreted)
    assert manure_excretion_values['urea'] == approx(urine_urea_nitrogen_concentration)
    assert manure_excretion_values['urine'] == approx(urine)
    assert manure_excretion_values['total_ammoniacal_nitrogen_concentration'] == \
           approx(total_ammoniacal_nitrogen_concentration)
    assert manure_excretion_values['urine_nitrogen'] == approx(urine_nitrogen)
    assert manure_excretion_values['manure_nitrogen'] == approx(manure_nitrogen)
    assert manure_excretion_values['manure_mass'] == approx(total_manure_excreted)
    assert manure_excretion_values['total_solids'] == approx(total_solids)
    assert manure_excretion_values['degradable_volatile_solids'] == approx(degradable_volatile_solids)
    assert manure_excretion_values['non_degradable_volatile_solids'] == approx(non_degradable_volatile_solids)
    assert manure_excretion_values['inorganic_phosphorus_fraction'] == approx(inorganic_phosphorus_fraction)
    assert manure_excretion_values['organic_phosphorus_fraction'] == approx(organic_phosphorus_fraction)
    assert manure_excretion_values['phosphorus'] == approx(manure_phosphorus_excreted)
    assert manure_excretion_values['phosphorus_fraction'] == approx(manure_phosphorus_fraction)
    assert manure_excretion_values['potassium'] == approx(potassium)
    assert manure_excretion_values['methane'] == approx(methane_emission)
