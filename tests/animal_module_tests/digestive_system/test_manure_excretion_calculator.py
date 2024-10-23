import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.digestive_system.manure_excretion_calculator import ManureExcretionCalculator
from RUFAS.biophysical.animal.data_types.animal_manure_excretions import AnimalManureExcretions
from RUFAS.general_constants import GeneralConstants


@pytest.mark.parametrize(
    "body_weight,fecal_phosphorus,urine_phosphorus_required,nutrient_amounts,nutrient_concentrations,"
    "inorganic_phosphorus_fraction,total_phosphorus_excreted,organic_phosphorus_fraction,manure_phosphorus_excreted,"
    "manure_phosphorus_fraction",
    [(500000, 36.5, 22.8, {"dm": 24.3}, {"CP": 92.4}, 26.3, 56.2, 58.3, 77.7, 0.35)],
)
def test_calf_manure(
    body_weight: float,
    fecal_phosphorus: float,
    urine_phosphorus_required: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
    inorganic_phosphorus_fraction: float,
    total_phosphorus_excreted: float,
    organic_phosphorus_fraction: float,
    manure_phosphorus_excreted: float,
    manure_phosphorus_fraction: float,
    mocker: MockerFixture,
) -> None:
    """Tests that calf manure excretion is correctly calculated."""
    mock_phosphorus_excretion = mocker.patch.object(
        ManureExcretionCalculator,
        "_calculate_phosphorus_excretion_values",
        return_value=(
            total_phosphorus_excreted,
            inorganic_phosphorus_fraction,
            organic_phosphorus_fraction,
            manure_phosphorus_excreted,
            manure_phosphorus_fraction,
        ),
    )
    total_manure_excreted = 3.45 * nutrient_amounts["dm"]
    total_solids = 0.393 * nutrient_amounts["dm"]
    degradable_volatile_solids = 0.9 * 0.0023 * body_weight
    non_degradable_volatile_solids = 0.0023 * body_weight - 0.9 * 0.0023 * body_weight
    manure_nitrogen = (
        112.55 * nutrient_amounts["dm"] * (nutrient_concentrations["CP"] / 100)
    ) * GeneralConstants.GRAMS_TO_KG
    urine_nitrogen = 0.45 * (
        (112.55 * nutrient_amounts["dm"] * (nutrient_concentrations["CP"] / 100)) * GeneralConstants.GRAMS_TO_KG
    )

    expected = (
        total_phosphorus_excreted,
        AnimalManureExcretions(
            urea=9.52,
            urine=2.0,
            manure_total_ammoniacal_nitrogen=urine_nitrogen,
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
        ),
    )

    actual = ManureExcretionCalculator.calculate_calf_manure(
        body_weight, fecal_phosphorus, urine_phosphorus_required, nutrient_amounts, nutrient_concentrations
    )

    mock_phosphorus_excretion.assert_called_once_with(
        daily_milk_production=0,
        total_manure_excreted=total_manure_excreted,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required,
    )

    assert actual == expected


@pytest.mark.parametrize(
    "body_weight,fecal_phosphorus,urine_phosphorus_required,nutrient_amounts,nutrient_concentrations,"
    "inorganic_phosphorus_fraction,total_phosphorus_excreted,organic_phosphorus_fraction,manure_phosphorus_excreted,"
    "manure_phosphorus_fraction",
    [(500000, 36.5, 22.8, {"dm": 24.3}, {"CP": 92.4, "potassium": 23.6}, 26.3, 56.2, 58.3, 77.7, 0.35)],
)
def test_heifer_manure(
    body_weight: float,
    fecal_phosphorus: float,
    urine_phosphorus_required: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
    inorganic_phosphorus_fraction: float,
    total_phosphorus_excreted: float,
    organic_phosphorus_fraction: float,
    manure_phosphorus_excreted: float,
    manure_phosphorus_fraction: float,
    mocker: MockerFixture,
) -> None:
    """Tests manure excretion values for a growing heifer is calculated correctly."""
    total_manure_excreted = 4.158 * nutrient_amounts["dm"] - 0.0246 * body_weight
    total_solids = 0.178 * nutrient_amounts["dm"] + 2.733
    degradable_volatile_solids = 0.9 * 0.0073 * body_weight
    non_degradable_volatile_solids = 0.0073 * body_weight - 0.9 * 0.0073 * body_weight
    manure_nitrogen = (
        15.1
        + 0.83
        * (nutrient_amounts["dm"] * GeneralConstants.KG_TO_GRAMS)
        * (nutrient_concentrations["CP"] * GeneralConstants.PROTEIN_TO_NITROGEN)
        / GeneralConstants.FRACTION_TO_PERCENTAGE
    ) * GeneralConstants.GRAMS_TO_KG
    fecal_nitrogen = (
        0.345
        + 0.317
        * (nutrient_amounts["dm"] * GeneralConstants.KG_TO_GRAMS)
        * (nutrient_concentrations["CP"] * GeneralConstants.PROTEIN_TO_NITROGEN)
        / GeneralConstants.FRACTION_TO_PERCENTAGE
    ) * GeneralConstants.GRAMS_TO_KG
    urine_nitrogen = manure_nitrogen - fecal_nitrogen
    urinary_nitrogen_concentration = (urine_nitrogen * GeneralConstants.KG_TO_GRAMS) / 9.0
    urine_urea_nitrogen_concentration = -1.16 + 0.86 * urinary_nitrogen_concentration
    potassium = (
        nutrient_amounts["dm"]
        * (nutrient_concentrations["potassium"] / GeneralConstants.FRACTION_TO_PERCENTAGE)
        * GeneralConstants.KG_TO_GRAMS
    )
    mock_phosphorus_excretion = mocker.patch.object(
        ManureExcretionCalculator,
        "_calculate_phosphorus_excretion_values",
        return_value=(
            total_phosphorus_excreted,
            inorganic_phosphorus_fraction,
            organic_phosphorus_fraction,
            manure_phosphorus_excreted,
            manure_phosphorus_fraction,
        ),
    )
    expected = (
        total_phosphorus_excreted,
        AnimalManureExcretions(
            urea=urine_urea_nitrogen_concentration,
            urine=9.0,
            manure_total_ammoniacal_nitrogen=urine_nitrogen,
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
        ),
    )
    actual = ManureExcretionCalculator.calculate_heifer_manure(
        body_weight, fecal_phosphorus, urine_phosphorus_required, nutrient_amounts, nutrient_concentrations
    )

    mock_phosphorus_excretion.assert_called_once_with(
        daily_milk_production=0,
        total_manure_excreted=total_manure_excreted,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required,
    )

    assert actual == expected


@pytest.mark.parametrize(
    "days_in_milk,milk_protein,daily_milk_production,fecal_phosphorus,urine_phosphorus_required,"
    "nutrient_amounts,nutrient_concentrations,inorganic_phosphorus_fraction,total_phosphorus_excreted,"
    "organic_phosphorus_fraction,manure_phosphorus_excreted,manure_phosphorus_fraction",
    [
        (
            707,
            36.5,
            22.8,
            32.5,
            22.9,
            {"dm": 24.3, "ash": 69.4},
            {"CP": 92.4, "potassium": 23.6, "dm": 77.7, "NDF": 84.1, "ADF": 4.2},
            26.3,
            56.2,
            58.3,
            77.7,
            0.35,
        )
    ],
)
def test_lactating_cow_manure(
    days_in_milk: int,
    milk_protein: float,
    daily_milk_production: float,
    fecal_phosphorus: float,
    urine_phosphorus_required: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
    inorganic_phosphorus_fraction: float,
    total_phosphorus_excreted: float,
    organic_phosphorus_fraction: float,
    manure_phosphorus_excreted: float,
    manure_phosphorus_fraction: float,
    mocker: MockerFixture,
) -> None:
    """Test the manure excretion values for a lactating cow with information from the ration formulation."""
    dry_matter_intake = nutrient_amounts["dm"]
    ASH_diet_content = nutrient_amounts["ash"]
    dry_matter_concentration = nutrient_concentrations["dm"]
    ADF_concentration = nutrient_concentrations["ADF"]
    CP_concentration = nutrient_concentrations["CP"]
    NDF_concentration = nutrient_concentrations["NDF"]
    potassium_concentration = nutrient_concentrations["potassium"]
    fecal_solids = -0.576 + 0.370 * dry_matter_intake - 0.075 * CP_concentration + 0.059 * ADF_concentration
    urine = -7.742 + 0.388 * dry_matter_intake + 0.726 * CP_concentration + 2.066 * milk_protein
    total_manure_excreted = (
        (
            1.987 * dry_matter_intake
            + 0.348 * ADF_concentration
            - 0.412 * CP_concentration
            - 0.074 * dry_matter_concentration
            - 0.0057 * days_in_milk
        )
        + fecal_solids
        + urine
    )
    manure_nitrogen = (20.3 + 0.654 * (dry_matter_intake * 1000) * (CP_concentration * 0.16) / 100) * 0.001
    dry_matter_intake = max(dry_matter_intake, 2.0)
    fecal_nitrogen = (-18.5 + 10.1 * dry_matter_intake) * 0.001
    urine_nitrogen = manure_nitrogen - fecal_nitrogen
    organic_matter_intake = dry_matter_intake - ASH_diet_content
    degradable_volatile_solids = (
        -1.017 + 0.364 * organic_matter_intake + 0.029 * NDF_concentration - 0.023 * CP_concentration
    )
    total_volatile_solids = (
        -1.201 + 0.402 * organic_matter_intake + 0.036 * NDF_concentration - 0.024 * CP_concentration
    )
    non_degradable_volatile_solids = total_volatile_solids - degradable_volatile_solids
    urinary_nitrogen_concentration = (urine_nitrogen * 1000) / urine
    urine_urea_nitrogen_concentration = -1.16 + 0.86 * urinary_nitrogen_concentration
    potassium = (
        7.21 * dry_matter_intake + 15944 * potassium_concentration / 100 - 164.5
    )
    mock_phosphorus_excretion = mocker.patch.object(
        ManureExcretionCalculator,
        "_calculate_phosphorus_excretion_values",
        return_value=(
            total_phosphorus_excreted,
            inorganic_phosphorus_fraction,
            organic_phosphorus_fraction,
            manure_phosphorus_excreted,
            manure_phosphorus_fraction,
        ),
    )
    expected = (
        total_phosphorus_excreted,
        AnimalManureExcretions(
            urea=urine_urea_nitrogen_concentration,
            urine=urine,
            manure_total_ammoniacal_nitrogen=urine_nitrogen,
            urine_nitrogen=urine_nitrogen,
            manure_nitrogen=manure_nitrogen,
            manure_mass=total_manure_excreted,
            total_solids=fecal_solids,
            degradable_volatile_solids=degradable_volatile_solids,
            non_degradable_volatile_solids=non_degradable_volatile_solids,
            inorganic_phosphorus_fraction=inorganic_phosphorus_fraction,
            organic_phosphorus_fraction=organic_phosphorus_fraction,
            non_water_inorganic_phosphorus_fraction=0.0,
            non_water_organic_phosphorus_fraction=0.0,
            phosphorus=manure_phosphorus_excreted,
            phosphorus_fraction=manure_phosphorus_fraction,
            potassium=potassium,
        ),
    )

    actual = ManureExcretionCalculator._calculate_lactating_cow_manure(
        days_in_milk,
        milk_protein,
        daily_milk_production,
        fecal_phosphorus,
        urine_phosphorus_required,
        nutrient_amounts,
        nutrient_concentrations,
    )

    assert expected == actual
    mock_phosphorus_excretion.assert_called_once_with(
        daily_milk_production=daily_milk_production,
        total_manure_excreted=total_manure_excreted,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required,
    )


@pytest.mark.parametrize(
    "body_weight,days_in_milk,milk_protein,daily_milk_production,fecal_phosphorus,"
    "urine_phosphorus_required,nutrient_amounts,nutrient_concentrations",
    [(43.2, 6, 225.3, 21.4, 14.3, 92.4, {"a": 56.2}, {"b": 58.3})],
)
def test_cow_manure_lactating(
    body_weight: float,
    days_in_milk: int,
    milk_protein: float,
    daily_milk_production: float,
    fecal_phosphorus: float,
    urine_phosphorus_required: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
    mocker: MockerFixture,
) -> None:
    mock_lactating_cow_manure = mocker.patch.object(ManureExcretionCalculator, "_calculate_lactating_cow_manure")
    ManureExcretionCalculator.calculate_cow_manure(
        True,
        body_weight,
        days_in_milk,
        milk_protein,
        daily_milk_production,
        fecal_phosphorus,
        urine_phosphorus_required,
        nutrient_amounts,
        nutrient_concentrations,
    )
    mock_lactating_cow_manure.assert_called_once_with(
        days_in_milk,
        milk_protein,
        daily_milk_production,
        fecal_phosphorus,
        urine_phosphorus_required,
        nutrient_amounts,
        nutrient_concentrations,
    )


@pytest.mark.parametrize(
    "body_weight,days_in_milk,milk_protein,daily_milk_production,fecal_phosphorus,"
    "urine_phosphorus_required,nutrient_amounts,nutrient_concentrations",
    [(43.2, 6, 225.3, 21.4, 14.3, 92.4, {"a": 56.2}, {"b": 58.3})],
)
def test_cow_manure_dry(
    body_weight: float,
    days_in_milk: int,
    milk_protein: float,
    daily_milk_production: float,
    fecal_phosphorus: float,
    urine_phosphorus_required: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
    mocker: MockerFixture,
) -> None:
    mock_dry_cow_manure = mocker.patch.object(ManureExcretionCalculator, "_calculate_dry_cow_manure")
    ManureExcretionCalculator.calculate_cow_manure(
        False,
        body_weight,
        days_in_milk,
        milk_protein,
        daily_milk_production,
        fecal_phosphorus,
        urine_phosphorus_required,
        nutrient_amounts,
        nutrient_concentrations,
    )
    mock_dry_cow_manure.assert_called_once_with(
        body_weight,
        daily_milk_production,
        fecal_phosphorus,
        urine_phosphorus_required,
        nutrient_amounts,
        nutrient_concentrations,
    )
