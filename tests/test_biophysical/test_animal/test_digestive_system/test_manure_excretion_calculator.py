import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionSupply
from RUFAS.biophysical.animal.digestive_system.manure_excretion_calculator import ManureExcretionCalculator
from RUFAS.biophysical.animal.data_types.animal_manure_excretions import AnimalManureExcretions
from RUFAS.general_constants import GeneralConstants
from RUFAS.user_constants import UserConstants


def test_calculate_calf_manure(mocker: MockerFixture) -> None:
    """
    Test calculate_calf_manure to ensure phosphorus excretion and manure excretion values are correctly calculated.
    """

    mock_nutrition = mocker.MagicMock(spec=NutritionSupply)
    mock_nutrition.dry_matter = 10.0
    mock_nutrition.crude_protein_percentage = 15.0

    mock_phosphorus_values = (5.0, 0.2, 0.3, 4.5, 0.5)

    mock_phosphorus_excretion = mocker.patch.object(
        ManureExcretionCalculator, "_calculate_phosphorus_excretion_values", return_value=mock_phosphorus_values
    )

    mocker.patch.object(GeneralConstants, "PERCENTAGE_TO_FRACTION", 0.01)
    mocker.patch.object(GeneralConstants, "GRAMS_TO_KG", 0.001)

    phosphorus_excreted, manure_excretion = ManureExcretionCalculator.calculate_calf_manure(
        body_weight=100.0,
        fecal_phosphorus=1.5,
        urine_phosphorus_required=2.0,
        nutrient_amounts=mock_nutrition,
    )

    assert isinstance(phosphorus_excreted, float)
    assert phosphorus_excreted == 5.0
    assert isinstance(manure_excretion, AnimalManureExcretions)
    assert manure_excretion.urine == 2.0
    assert manure_excretion.manure_nitrogen > 0

    mock_phosphorus_excretion.assert_called_once()


@pytest.mark.parametrize(
    "body_weight, fecal_phosphorus, urine_phosphorus_required, dry_matter, crude_protein, potassium,"
    "expected_phosphorus",
    [
        (300.0, 2.0, 3.0, 12.0, 16.0, 1.2, 5.5),
        (400.0, 2.5, 3.5, 14.0, 18.0, 1.5, 6.0),
    ],
)
def test_calculate_heifer_manure(
    mocker: MockerFixture,
    body_weight: float,
    fecal_phosphorus: float,
    urine_phosphorus_required: float,
    dry_matter: float,
    crude_protein: float,
    potassium: float,
    expected_phosphorus: float,
) -> None:
    mock_nutrition = mocker.MagicMock(spec=NutritionSupply)
    mock_nutrition.dry_matter = dry_matter
    mock_nutrition.crude_protein_percentage = crude_protein
    mock_nutrition.potassium_percentage = potassium

    mock_phosphorus_values = (expected_phosphorus, 0.2, 0.3, 4.5, 0.5)

    mock_phosphorus_excretion = mocker.patch.object(
        ManureExcretionCalculator, "_calculate_phosphorus_excretion_values", return_value=mock_phosphorus_values
    )

    mocker.patch.object(GeneralConstants, "KG_TO_GRAMS", 1000.0)
    mocker.patch.object(GeneralConstants, "GRAMS_TO_KG", 0.001)
    mocker.patch.object(GeneralConstants, "PERCENTAGE_TO_FRACTION", 0.01)
    mocker.patch.object(UserConstants, "PROTEIN_TO_NITROGEN", 0.16)

    phosphorus_excreted, manure_excretion = ManureExcretionCalculator.calculate_heifer_manure(
        body_weight=body_weight,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required,
        nutrient_amount=mock_nutrition,
    )

    assert isinstance(phosphorus_excreted, float)
    assert phosphorus_excreted == expected_phosphorus

    assert isinstance(manure_excretion, AnimalManureExcretions)
    assert manure_excretion.urine > 0
    assert manure_excretion.manure_nitrogen > 0
    assert manure_excretion.potassium > 0

    mock_phosphorus_excretion.assert_called_once()


@pytest.mark.parametrize(
    "is_lactating, body_weight, days_in_milk, milk_protein, daily_milk_production, fecal_phosphorus,"
    "urine_phosphorus_required, expected_phosphorus",
    [
        (True, 650.0, 150, 3.2, 30.0, 2.5, 3.0, 6.5),
        (False, 700.0, 0, 0.0, 0.0, 2.0, 2.5, 5.0),
    ],
)
def test_calculate_cow_manure(
    mocker: MockerFixture,
    is_lactating: bool,
    body_weight: float,
    days_in_milk: int,
    milk_protein: float,
    daily_milk_production: float,
    fecal_phosphorus: float,
    urine_phosphorus_required: float,
    expected_phosphorus: float,
) -> None:
    mock_nutrition = mocker.MagicMock(spec=NutritionSupply)

    mock_lactating_manure = (expected_phosphorus, mocker.MagicMock(spec=AnimalManureExcretions))
    mock_dry_manure = (expected_phosphorus, mocker.MagicMock(spec=AnimalManureExcretions))

    mock_lactating_calc = mocker.patch.object(
        ManureExcretionCalculator, "_calculate_lactating_cow_manure", return_value=mock_lactating_manure
    )

    mock_dry_calc = mocker.patch.object(
        ManureExcretionCalculator, "_calculate_dry_cow_manure", return_value=mock_dry_manure
    )

    phosphorus_excreted, manure_excretion = ManureExcretionCalculator.calculate_cow_manure(
        is_lactating=is_lactating,
        body_weight=body_weight,
        days_in_milk=days_in_milk,
        milk_protein=milk_protein,
        daily_milk_production=daily_milk_production,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required,
        nutrient_amounts=mock_nutrition,
    )

    assert isinstance(phosphorus_excreted, float)
    assert phosphorus_excreted == expected_phosphorus

    assert isinstance(manure_excretion, AnimalManureExcretions)

    if is_lactating:
        mock_lactating_calc.assert_called_once()
        mock_dry_calc.assert_not_called()
    else:
        mock_dry_calc.assert_called_once()
        mock_lactating_calc.assert_not_called()


@pytest.mark.parametrize(
    "days_in_milk, milk_protein, daily_milk_production, fecal_phosphorus, urine_phosphorus_required, "
    "dry_matter, crude_protein, potassium, ash_supply, expected_phosphorus",
    [
        (150, 3.2, 30.0, 2.5, 3.0, 20.0, 16.0, 1.2, 2.0, 6.5),
        (200, 3.5, 35.0, 2.0, 2.5, 22.0, 18.0, 1.5, 2.5, 7.0),
    ],
)
def test_calculate_lactating_cow_manure(
    mocker: MockerFixture,
    days_in_milk: int,
    milk_protein: float,
    daily_milk_production: float,
    fecal_phosphorus: float,
    urine_phosphorus_required: float,
    dry_matter: float,
    crude_protein: float,
    potassium: float,
    ash_supply: float,
    expected_phosphorus: float,
) -> None:
    mock_nutrition = mocker.MagicMock(spec=NutritionSupply)
    mock_nutrition.dry_matter = dry_matter
    mock_nutrition.crude_protein_percentage = crude_protein
    mock_nutrition.potassium_percentage = potassium
    mock_nutrition.ash_supply = ash_supply

    mock_phosphorus_values = (expected_phosphorus, 0.2, 0.3, 4.5, 0.5)

    mock_phosphorus_excretion = mocker.patch.object(
        ManureExcretionCalculator, "_calculate_phosphorus_excretion_values", return_value=mock_phosphorus_values
    )

    mocker.patch.object(GeneralConstants, "KG_TO_GRAMS", 1000.0)
    mocker.patch.object(GeneralConstants, "GRAMS_TO_KG", 0.001)
    mocker.patch.object(GeneralConstants, "PERCENTAGE_TO_FRACTION", 0.01)
    mocker.patch.object(UserConstants, "PROTEIN_TO_NITROGEN", 0.16)
    mocker.patch.object(AnimalModuleConstants, "MINIMUM_DMI_LACT", 5.0)

    phosphorus_excreted, manure_excretion = ManureExcretionCalculator._calculate_lactating_cow_manure(
        days_in_milk=days_in_milk,
        milk_protein=milk_protein,
        daily_milk_production=daily_milk_production,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required,
        nutrient_amounts=mock_nutrition,
    )

    assert isinstance(phosphorus_excreted, float)
    assert phosphorus_excreted == expected_phosphorus

    assert isinstance(manure_excretion, AnimalManureExcretions)
    assert manure_excretion.urine > 0
    assert manure_excretion.manure_nitrogen > 0
    assert manure_excretion.potassium > 0

    mock_phosphorus_excretion.assert_called_once()


@pytest.mark.parametrize(
    "body_weight, daily_milk_production, fecal_phosphorus, urine_phosphorus_required, "
    "dry_matter, crude_protein, potassium, ash_percentage, expected_phosphorus",
    [
        (650.0, 0.0, 2.5, 3.0, 18.0, 14.0, 1.0, 5.0, 6.2),
        (700.0, 0.0, 2.0, 2.5, 20.0, 16.0, 1.2, 4.5, 5.8),
    ],
)
def test_calculate_dry_cow_manure(
    mocker: MockerFixture,
    body_weight: float,
    daily_milk_production: float,
    fecal_phosphorus: float,
    urine_phosphorus_required: float,
    dry_matter: float,
    crude_protein: float,
    potassium: float,
    ash_percentage: float,
    expected_phosphorus: float,
) -> None:
    mock_nutrition = mocker.MagicMock(spec=NutritionSupply)
    mock_nutrition.dry_matter = dry_matter
    mock_nutrition.crude_protein_percentage = crude_protein
    mock_nutrition.potassium_percentage = potassium
    mock_nutrition.ash_percentage = ash_percentage
    mock_nutrition.ndf_percentage = 1.0

    mock_phosphorus_values = (expected_phosphorus, 0.2, 0.3, 4.5, 0.5)

    mock_phosphorus_excretion = mocker.patch.object(
        ManureExcretionCalculator, "_calculate_phosphorus_excretion_values", return_value=mock_phosphorus_values
    )

    mocker.patch.object(GeneralConstants, "KG_TO_GRAMS", 1000.0)
    mocker.patch.object(GeneralConstants, "GRAMS_TO_KG", 0.001)
    mocker.patch.object(GeneralConstants, "PERCENTAGE_TO_FRACTION", 0.01)
    mocker.patch.object(UserConstants, "PROTEIN_TO_NITROGEN", 0.16)
    mocker.patch.object(GeneralConstants, "FRACTION_TO_PERCENTAGE", 100.0)
    mocker.patch.object(AnimalModuleConstants, "MINIMUM_DMI_DRY", 5.0)

    phosphorus_excreted, manure_excretion = ManureExcretionCalculator._calculate_dry_cow_manure(
        body_weight=body_weight,
        daily_milk_production=daily_milk_production,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required,
        nutrient_amounts=mock_nutrition,
    )

    assert isinstance(phosphorus_excreted, float)
    assert phosphorus_excreted == expected_phosphorus

    assert isinstance(manure_excretion, AnimalManureExcretions)
    assert manure_excretion.urine > 0
    assert manure_excretion.manure_nitrogen > 0
    assert manure_excretion.potassium > 0

    mock_phosphorus_excretion.assert_called_once()


@pytest.mark.parametrize(
    "daily_milk_production, total_manure_excreted, fecal_phosphorus, urine_phosphorus_required, expected_values",
    [
        (
            30.0,
            20.0,
            2.5,
            3.0,
            (
                32.5,
                pytest.approx(0.0001375, abs=1.4e-07),
                pytest.approx(1.37500000000e-05, abs=1.4e-08),
                5.5,
                pytest.approx(0.000275, abs=2.8e-07),
            ),
        ),
        (0.0, 15.0, 2.0, 2.5, (4.5, 0.00015, 0.000015, 4.5, pytest.approx(0.0003, abs=3.0e-07))),
        (25.0, 0.0, 2.0, 3.0, (pytest.approx(27.5, abs=2.8e-02), 0.0, 0.0, 5.0, 0.0)),
    ],
)
def test_calculate_phosphorus_excretion_values(
    mocker: MockerFixture,
    daily_milk_production: float,
    total_manure_excreted: float,
    fecal_phosphorus: float,
    urine_phosphorus_required: float,
    expected_values: tuple[float, float, float, float, float],
) -> None:
    mocker.patch.object(GeneralConstants, "KG_TO_GRAMS", 1000.0)

    result = ManureExcretionCalculator._calculate_phosphorus_excretion_values(
        daily_milk_production=daily_milk_production,
        total_manure_excreted=total_manure_excreted,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required,
    )

    assert isinstance(result, tuple)
    assert len(result) == 5

    for res, expected in zip(result, expected_values):
        assert pytest.approx(res, rel=1e-3) == expected
