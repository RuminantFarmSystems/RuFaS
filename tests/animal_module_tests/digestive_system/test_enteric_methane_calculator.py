import math

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.digestive_system.enteric_methane_calculator import EntericMethaneCalculator
from RUFAS.biophysical.animal.digestive_system.methane_mitigation_calculator import MethaneMitigationCalculator


def test_calf_methane_no_model() -> None:
    """Test the calf methane result without model provided."""
    observed = EntericMethaneCalculator.calf_methane(None, 30)
    assert observed == 0


@pytest.mark.parametrize("body_weight,expected", [(30, 12.52883), (195.45, 51.09126)])
def test_calf_methane_with_model(body_weight: float, expected: float) -> None:
    """Test the calf methane result without model provided."""
    observed = EntericMethaneCalculator.calf_methane("model", body_weight)
    assert pytest.approx(observed) == expected


def test_heifer_methane_no_model() -> None:
    """Test the heifer methane result without model provided."""
    observed = EntericMethaneCalculator.heifer_methane(None, 30, {})
    assert observed == 0


@pytest.mark.parametrize(
    "dry_matter_intake,nutrient_concentrations", [(59.67, {"CP": 3.69, "EE": 57.4, "NDF": 39.14, "ash": 56.27})]
)
def test_heifer_methane_with_model(dry_matter_intake: float, nutrient_concentrations: dict[str, float]) -> None:
    """Test the calf methane result without model provided."""
    CP_concentration = nutrient_concentrations["CP"]
    EE_concentration = nutrient_concentrations["EE"]
    NDF_concentration = nutrient_concentrations["NDF"]
    ASH_concentration = nutrient_concentrations["ash"]

    expected_gross_energy_concentration = (
        0.263 * CP_concentration
        + 0.522 * EE_concentration
        + 0.198 * NDF_concentration
        + 0.160 * ((100 - ASH_concentration) - NDF_concentration - CP_concentration - EE_concentration)
    )
    expected = (0.065 * expected_gross_energy_concentration * dry_matter_intake) / 0.05565
    observed = EntericMethaneCalculator.heifer_methane("model", dry_matter_intake, nutrient_concentrations)
    assert pytest.approx(observed) == expected


@pytest.mark.parametrize(
    "body_weight,milk_fat,metabolizable_energy_intake,nutrient_amounts,nutrient_concentrations,"
    "methane_mitigation_method,methane_mitigation_additive_amount",
    [(59.67, 33.7, 77.7, {"dm": 3.69}, {"EE": 57.4, "NDF": 39.14, "starch": 56.27}, "test_method", 92.4)],
)
def test_cow_methane_is_lactating_with_mitigation(
    body_weight: float,
    milk_fat: float,
    metabolizable_energy_intake: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
    methane_mitigation_method: str,
    methane_mitigation_additive_amount: float,
    mocker: MockerFixture,
) -> None:
    """Test the daily enteric emissions for lactating cows with mitigation."""
    dry_matter_intake = nutrient_amounts["dm"]
    NDF_concentration = nutrient_concentrations["NDF"]
    EE_concentration = nutrient_concentrations["EE"]
    starch_concentration = nutrient_concentrations["starch"]

    mock_lactating_cow_manure = mocker.patch.object(EntericMethaneCalculator, "_lactating_cow_manure", return_value=25)

    methane_yield = 25 / dry_matter_intake
    mock_methane_mitigation = mocker.patch.object(MethaneMitigationCalculator, "methane_mitigation", return_value=23.5)
    expected = methane_yield * (1 + 23.5 / 100) * dry_matter_intake
    observed = EntericMethaneCalculator.cow_methane(
        True,
        body_weight,
        milk_fat,
        metabolizable_energy_intake,
        nutrient_amounts,
        nutrient_concentrations,
        methane_mitigation_method,
        methane_mitigation_additive_amount,
        "model",
    )
    assert observed == expected

    mock_lactating_cow_manure.assert_called_once_with(
        body_weight,
        milk_fat,
        metabolizable_energy_intake,
        nutrient_amounts,
        nutrient_concentrations,
        "model",
    )
    mock_methane_mitigation.assert_called_once_with(
        NDF_concentration,
        EE_concentration,
        starch_concentration,
        methane_mitigation_method,
        methane_mitigation_additive_amount,
    )


@pytest.mark.parametrize(
    "body_weight,milk_fat,metabolizable_energy_intake,nutrient_amounts,nutrient_concentrations,"
    "methane_mitigation_method,methane_mitigation_additive_amount",
    [(59.67, 33.7, 77.7, {"dm": 3.69}, {"EE": 57.4, "NDF": 39.14, "starch": 56.27}, "test_method", 92.4)],
)
def test_cow_manure_dry_with_mitigation(
    body_weight: float,
    milk_fat: float,
    metabolizable_energy_intake: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
    methane_mitigation_method: str,
    methane_mitigation_additive_amount: float,
    mocker: MockerFixture,
) -> None:
    """Test the daily enteric emissions for dry cows with mitigation."""
    dry_matter_intake = nutrient_amounts["dm"]
    NDF_concentration = nutrient_concentrations["NDF"]
    EE_concentration = nutrient_concentrations["EE"]
    starch_concentration = nutrient_concentrations["starch"]

    mock_dry_cow_manure = mocker.patch.object(EntericMethaneCalculator, "_dry_cow_manure", return_value=25)

    methane_yield = 25 / dry_matter_intake
    mock_methane_mitigation = mocker.patch.object(MethaneMitigationCalculator, "methane_mitigation", return_value=23.5)
    expected = methane_yield * (1 + 23.5 / 100) * dry_matter_intake
    observed = EntericMethaneCalculator.cow_methane(
        False,
        body_weight,
        milk_fat,
        metabolizable_energy_intake,
        nutrient_amounts,
        nutrient_concentrations,
        methane_mitigation_method,
        methane_mitigation_additive_amount,
        "model",
    )
    assert observed == expected

    mock_dry_cow_manure.assert_called_once_with(
        "model", metabolizable_energy_intake, nutrient_amounts, nutrient_concentrations
    )
    mock_methane_mitigation.assert_called_once_with(
        NDF_concentration,
        EE_concentration,
        starch_concentration,
        methane_mitigation_method,
        methane_mitigation_additive_amount,
    )


@pytest.mark.parametrize(
    "body_weight,milk_fat,metabolizable_energy_intake,nutrient_amounts,nutrient_concentrations",
    [
        (
            59.67,
            6.31,
            5.25,
            {"dm": 42.32},
            {"ash": 39.14, "ADF": 39.54, "CP": 26.14, "NDF": 48.14, "EE": 35.4, "starch": 54.2},
        )
    ],
)
def test_lactating_cow_manure_mutian(
    body_weight: float,
    milk_fat: float,
    metabolizable_energy_intake: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
) -> None:
    """Test the daily enteric emissions for lactating cows with Mutian method."""
    dry_matter_intake = nutrient_amounts["dm"]
    NDF_concentration = nutrient_concentrations["NDF"]
    expected = -126 + 11.3 * dry_matter_intake + 2.30 * NDF_concentration + 28.8 * milk_fat + 0.148 * body_weight
    observed = EntericMethaneCalculator._lactating_cow_manure(
        body_weight, milk_fat, metabolizable_energy_intake, nutrient_amounts, nutrient_concentrations, "Mutian"
    )
    assert expected == observed


@pytest.mark.parametrize(
    "body_weight,milk_fat,metabolizable_energy_intake,nutrient_amounts,nutrient_concentrations",
    [
        (
            59.67,
            6.31,
            5.25,
            {"dm": 42.32},
            {"ash": 39.14, "ADF": 39.54, "CP": 26.14, "NDF": 48.14, "EE": 35.4, "starch": 54.2},
        )
    ],
)
def test_lactating_cow_manure_mills(
    body_weight: float,
    milk_fat: float,
    metabolizable_energy_intake: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
) -> None:
    """Test the daily enteric emissions for lactating cows with Mills method."""
    ADF_concentration = nutrient_concentrations["ADF"]
    starch_concentration = nutrient_concentrations["starch"]
    expected = (
        45.98
        * (
            1
            - math.exp(
                -(-0.0011 * starch_concentration / ADF_concentration + 0.0045) * metabolizable_energy_intake * 4.184
            )
        )
        / 0.05565
    )
    observed = EntericMethaneCalculator._lactating_cow_manure(
        body_weight, milk_fat, metabolizable_energy_intake, nutrient_amounts, nutrient_concentrations, "Mills"
    )
    assert expected == observed


@pytest.mark.parametrize(
    "body_weight,milk_fat,metabolizable_energy_intake,nutrient_amounts,nutrient_concentrations",
    [
        (
            59.67,
            6.31,
            5.25,
            {"dm": 42.32},
            {"ash": 39.14, "ADF": 39.54, "CP": 26.14, "NDF": 48.14, "EE": 35.4, "starch": 54.2},
        )
    ],
)
def test_lactating_cow_manure_IPCC(
    body_weight: float,
    milk_fat: float,
    metabolizable_energy_intake: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
) -> None:
    """Test the daily enteric emissions for lactating cows with IPCC method."""
    dry_matter_intake = nutrient_amounts["dm"]
    ASH_concentration = nutrient_concentrations["ash"]
    CP_concentration = nutrient_concentrations["CP"]
    NDF_concentration = nutrient_concentrations["NDF"]
    EE_concentration = nutrient_concentrations["EE"]
    soluble_residue = 100 - ASH_concentration - NDF_concentration - CP_concentration - EE_concentration
    gross_energy_concentration = (
        0.263 * CP_concentration + 0.522 * EE_concentration + 0.198 * NDF_concentration + 0.160 * soluble_residue
    )
    expected = 0.065 * gross_energy_concentration * dry_matter_intake / 0.05565
    observed = EntericMethaneCalculator._lactating_cow_manure(
        body_weight, milk_fat, metabolizable_energy_intake, nutrient_amounts, nutrient_concentrations, "IPCC"
    )
    assert expected == observed


def test_lactating_cow_manure_other() -> None:
    """Test the daily enteric emissions for lactating cows with no specific method."""
    observed = EntericMethaneCalculator._lactating_cow_manure(
        59.67,
        6.31,
        5.25,
        {"dm": 42.32},
        {"ash": 39.14, "ADF": 39.54, "CP": 26.14, "NDF": 48.14, "EE": 35.4, "starch": 54.2},
        "test",
    )
    assert observed == 0


@pytest.mark.parametrize(
    "metabolizable_energy_intake,nutrient_amounts,nutrient_concentrations",
    [(5.25, {"dm": 42.32}, {"ash": 39.14, "ADF": 39.54, "CP": 26.14, "NDF": 48.14, "EE": 35.4, "starch": 54.2})],
)
def test_dry_cow_manure_mills(
    metabolizable_energy_intake: float, nutrient_amounts: dict[str, float], nutrient_concentrations: dict[str, float]
) -> None:
    """Test the daily enteric emissions for dry cows with Mills method."""
    ADF_concentration = nutrient_concentrations["ADF"]
    starch_concentration = nutrient_concentrations["starch"]
    expected = (
        45.98
        - 45.98
        * math.exp(
            -((-0.0011 * starch_concentration / ADF_concentration) + 0.0045) * metabolizable_energy_intake * 4.184
        )
    ) / 0.05565
    observed = EntericMethaneCalculator._dry_cow_manure(
        "Mills", metabolizable_energy_intake, nutrient_amounts, nutrient_concentrations
    )
    assert expected == observed


@pytest.mark.parametrize(
    "metabolizable_energy_intake,nutrient_amounts,nutrient_concentrations",
    [(5.25, {"dm": 42.32}, {"ash": 39.14, "ADF": 39.54, "CP": 26.14, "NDF": 48.14, "EE": 35.4, "starch": 54.2})],
)
def test_dry_cow_manure_others(
    metabolizable_energy_intake: float, nutrient_amounts: dict[str, float], nutrient_concentrations: dict[str, float]
) -> None:
    """Test the daily enteric emissions for dry cows with other method."""
    dry_matter_intake = nutrient_amounts["dm"]
    ASH_concentration = nutrient_concentrations["ash"]
    CP_concentration = nutrient_concentrations["CP"]
    NDF_concentration = nutrient_concentrations["NDF"]
    EE_concentration = nutrient_concentrations["EE"]
    soluble_residue = (100 - ASH_concentration) - NDF_concentration - CP_concentration - EE_concentration
    expected = (
        0.065
        * (0.263 * CP_concentration + 0.522 * EE_concentration + 0.198 * NDF_concentration + 0.160 * soluble_residue)
        * dry_matter_intake
    ) / 0.05565
    observed = EntericMethaneCalculator._dry_cow_manure(
        "other", metabolizable_energy_intake, nutrient_amounts, nutrient_concentrations
    )
    assert expected == observed
