import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionSupply
from RUFAS.biophysical.animal.digestive_system.enteric_methane_calculator import EntericMethaneCalculator
from RUFAS.biophysical.animal.digestive_system.methane_mitigation_calculator import MethaneMitigationCalculator
from RUFAS.general_constants import GeneralConstants


def test_calf_methane_no_model() -> None:
    """Test the calf methane result without model provided."""
    actual = EntericMethaneCalculator.calculate_calf_methane({"Pattanaik": False}, 30)
    assert actual == {"Pattanaik": 0}


@pytest.mark.parametrize("body_weight,expected", [(30, {"Pattanaik": 12.52883}), (195.45, {"Pattanaik": 51.09126})])
def test_calf_methane_with_model(body_weight: float, expected: dict[str, float]) -> None:
    """Test the calf methane result without model provided."""
    actual = EntericMethaneCalculator.calculate_calf_methane({"Pattanaik": True}, body_weight)
    assert pytest.approx(actual) == expected


def test_heifer_methane_no_model() -> None:
    """Test the heifer methane result without model provided."""
    actual = EntericMethaneCalculator.calculate_heifer_methane(
        {"IPCC": False},
        NutritionSupply(
            metabolizable_energy=50.0,
            maintenance_energy=10.0,
            lactation_energy=15.0,
            growth_energy=20.0,
            metabolizable_protein=5.0,
            calcium=0.5,
            phosphorus=0.3,
            dry_matter=50.0,
            wet_matter=50.0,
            ndf_supply=40.0,
            forage_ndf_supply=30.0,
            fat_supply=5.0,
            crude_protein=10.0,
            adf_supply=20.0,
            digestible_energy_supply=45.0,
            tdn_supply=60.0,
            lignin_supply=5.0,
            ash_supply=5.0,
            potassium_supply=0.5,
            starch_supply=5.0,
            byproduct_supply=5.0,
        ),
    )
    assert actual == {"IPCC": 0}


@pytest.mark.parametrize(
    "nutrient_concentrations,expected",
    [
        (
            NutritionSupply(
                metabolizable_energy=50.0,
                maintenance_energy=10.0,
                lactation_energy=15.0,
                growth_energy=20.0,
                metabolizable_protein=5.0,
                calcium=0.5,
                phosphorus=0.3,
                dry_matter=50.0,
                wet_matter=50.0,
                ndf_supply=40.0,
                forage_ndf_supply=30.0,
                fat_supply=5.0,
                crude_protein=10.0,
                adf_supply=20.0,
                digestible_energy_supply=45.0,
                tdn_supply=60.0,
                lignin_supply=5.0,
                ash_supply=5.0,
                potassium_supply=0.5,
                starch_supply=5.0,
                byproduct_supply=5.0,
            ),
            {"IPCC": 0},
        )
    ],
)
def test_heifer_methane_with_model(nutrient_concentrations: NutritionSupply, expected: float) -> None:
    """Test the calf methane result without model provided."""
    actual = EntericMethaneCalculator.calculate_heifer_methane({"IPCC": False}, nutrient_concentrations)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "is_lactating, methane_mitigation_method, methane_mitigation_additive_amount, "
    "expected_methane, expected_mitigation_called",
    [
        (True, "3-NOP", 500.0, {"Mutian": 0, "Mills": 0, "IPCC": 299.7}, True),
        (True, "", 0.0, {"Mutian": 0, "Mills": 0, "IPCC": 300.0}, False),
        (False, "", 0.0, {"IPCC": 180.0, "Mills": 0}, False),
    ],
)
def test_calculate_cow_methane(
    mocker: MockerFixture,
    is_lactating: bool,
    methane_mitigation_method: str,
    methane_mitigation_additive_amount: float,
    expected_methane: float,
    expected_mitigation_called: bool,
) -> None:
    """
    Test for calculate_cow_methane with different cases.
    """
    mock_nutrition = mocker.MagicMock(spec=NutritionSupply)
    mock_nutrition.dry_matter = 20.0
    mock_nutrition.ndf_percentage = 40.0
    mock_nutrition.fat_percentage = 5.0
    mock_nutrition.starch_percentage = 15.0

    mock_lactating_methane = {"Mutian": 0, "Mills": 0, "IPCC": 300.0}
    mock_dry_methane = {"IPCC": 180.0, "Mills": 0}
    mock_methane_yield_reduction = -0.1
    mock_lactating_methane_calc = mocker.patch.object(
        EntericMethaneCalculator, "_calculate_lactating_cow_enteric_methane", return_value=mock_lactating_methane
    )
    mock_dry_methane_calc = mocker.patch.object(
        EntericMethaneCalculator, "_calculate_dry_cow_enteric_methane", return_value=mock_dry_methane
    )
    mock_mitigation = mocker.patch.object(
        MethaneMitigationCalculator, "mitigate_methane", return_value=mock_methane_yield_reduction
    )

    result = EntericMethaneCalculator.calculate_cow_methane(
        is_lactating=is_lactating,
        body_weight=650.0,
        milk_fat=3.5,
        metabolizable_energy_intake=28.0,
        nutrient_amounts=mock_nutrition,
        methane_mitigation_method=methane_mitigation_method,
        methane_mitigation_additive_amount=methane_mitigation_additive_amount,
        methane_models={
            "cows": {
                "lactating cows": {"Mutian": False, "Mills": False, "IPCC": True},
                "dry cows": {"Mills": False, "IPCC": True},
            }
        },
    )

    if is_lactating:
        mock_lactating_methane_calc.assert_called_once()
    else:
        mock_dry_methane_calc.assert_called_once()

    if expected_mitigation_called:
        mock_mitigation.assert_called()
    else:
        mock_mitigation.assert_not_called()

    assert isinstance(result, dict)
    assert result == expected_methane


@pytest.mark.parametrize(
    "methane_model, expected_methane",
    [
        (
            {"Mutian": True, "Mills": False, "IPCC": False},
            {"Mutian": 393.2, "Mills": 0, "IPCC": 0},
        ),  # Mutian model only example output
        (
            {"Mutian": False, "Mills": True, "IPCC": False},
            {"Mutian": 0, "Mills": 413.11769991015274, "IPCC": 0},
        ),  # Mills only model example output
        (
            {"Mutian": False, "Mills": False, "IPCC": True},
            {"Mutian": 0, "Mills": 0, "IPCC": 525.2840970350404},
        ),  # IPCC only model example output
        (
            {"Mutian": False, "Mills": True, "IPCC": True},
            {"Mutian": 0, "Mills": 413.11769991015274, "IPCC": 525.2840970350404},
        ),  # multi model usage tests
        (
            {"Mutian": True, "Mills": True, "IPCC": True},
            {"Mutian": 393.2, "Mills": 413.11769991015274, "IPCC": 525.2840970350404},
        ),  # all model usage test
    ],
)
def test_calculate_lactating_cow_enteric_methane(
    mocker: MockerFixture,
    methane_model: dict[str, bool],
    expected_methane: dict[str, float],
) -> None:
    """
    Parametrized test for _calculate_lactating_cow_enteric_methane with different methane models.
    """

    mock_nutrition = mocker.MagicMock(spec=NutritionSupply)
    mock_nutrition.dry_matter = 22.0
    mock_nutrition.ash_percentage = 5.0
    mock_nutrition.adf_percentage = 25.0
    mock_nutrition.crude_protein_percentage = 18.0
    mock_nutrition.ndf_percentage = 32.0
    mock_nutrition.fat_percentage = 6.0
    mock_nutrition.starch_percentage = 21.0

    mocker.patch.object(GeneralConstants, "FRACTION_TO_PERCENTAGE", 100.0)
    mock_exp = mocker.patch(
        "RUFAS.biophysical.animal.digestive_system.enteric_methane_calculator.exp", return_value=0.5
    )

    result = EntericMethaneCalculator._calculate_lactating_cow_enteric_methane(
        body_weight=650.0,
        milk_fat=3.5,
        metabolizable_energy_intake=28.0,
        nutrient_amounts=mock_nutrition,
        methane_models=methane_model,
    )

    assert isinstance(result, dict)
    assert result == expected_methane

    if methane_model["Mills"]:
        mock_exp.assert_called_once()


@pytest.mark.parametrize(
    "methane_model, expected_methane",
    [
        ({"Mills": True, "IPCC": False}, {"Mills": 413.11769991015274, "IPCC": 0}),
        ({"Mills": False, "IPCC": True}, {"IPCC": 525.2840970350404, "Mills": 0}),
        ({"Mills": True, "IPCC": True}, {"IPCC": 525.2840970350404, "Mills": 413.11769991015274}),
        ({"Mills": False, "IPCC": False}, {"IPCC": 0, "Mills": 0}),
    ],
)
def test_calculate_dry_cow_enteric_methane(
    mocker: MockerFixture, methane_model: dict[str, bool], expected_methane: dict[str, float]
) -> None:
    """
    Parametrized test for _calculate_dry_cow_enteric_methane with different methane models.
    """

    mock_nutrition = mocker.MagicMock(spec=NutritionSupply)
    mock_nutrition.dry_matter = 22.0
    mock_nutrition.ash_percentage = 5.0
    mock_nutrition.adf_percentage = 25.0
    mock_nutrition.crude_protein_percentage = 18.0
    mock_nutrition.ndf_percentage = 32.0
    mock_nutrition.fat_percentage = 6.0
    mock_nutrition.starch_percentage = 21.0

    mocker.patch.object(GeneralConstants, "FRACTION_TO_PERCENTAGE", 100.0)

    mock_exp = mocker.patch(
        "RUFAS.biophysical.animal.digestive_system.enteric_methane_calculator.exp", return_value=0.5
    )

    result = EntericMethaneCalculator._calculate_dry_cow_enteric_methane(
        methane_models=methane_model,
        metabolizable_energy_intake=28.0,
        nutrient_amounts=mock_nutrition,
    )

    assert isinstance(result, dict)
    assert result == expected_methane

    if methane_model["Mills"]:
        mock_exp.assert_called_once()
