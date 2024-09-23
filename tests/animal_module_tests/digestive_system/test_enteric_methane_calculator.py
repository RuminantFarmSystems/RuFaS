import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.digestive_system.enteric_methane_calculator import EntericMethaneCalculator
from RUFAS.biophysical.animal.digestive_system.methane_mitigation_calculator import MethaneMitigationCalculator
from RUFAS.general_constants import GeneralConstants


def test_calf_methane_no_model() -> None:
    """Test the calf methane result without model provided."""
    observed = EntericMethaneCalculator.calf_methane(None, 30)
    assert observed == 0


@pytest.mark.parametrize(
    "body_weight,expected",
    [
        (30, 12.52883),
        (195.45, 51.09126)
    ]
)
def test_calf_methane_with_model(body_weight: float, expected: float) -> None:
    """Test the calf methane result without model provided."""
    observed = EntericMethaneCalculator.calf_methane("model", body_weight)
    assert pytest.approx(observed) == expected


def test_heifer_methane_no_model() -> None:
    """Test the heifer methane result without model provided."""
    observed = EntericMethaneCalculator.heifer_methane(None, 30, {})
    assert observed == 0


@pytest.mark.parametrize(
    "dry_matter_intake,nutrient_concentrations",
    [
        (59.67, {"CP": 3.69, "EE": 57.4, "NDF": 39.14, "ash": 56.27})
    ]
)
def test_heifer_methane_with_model(dry_matter_intake: float,
                                   nutrient_concentrations: dict[str, float]) -> None:
    """Test the calf methane result without model provided."""
    CP_concentration = nutrient_concentrations["CP"]
    EE_concentration = nutrient_concentrations["EE"]
    NDF_concentration = nutrient_concentrations["NDF"]
    ASH_concentration = nutrient_concentrations["ash"]

    expected_gross_energy_concentration = (
        0.263 * CP_concentration
        + 0.522 * EE_concentration
        + 0.198 * NDF_concentration
        + 0.160 * (
            (100 - ASH_concentration)
            - NDF_concentration
            - CP_concentration
            - EE_concentration
        )
    )
    expected = (0.065 * expected_gross_energy_concentration * dry_matter_intake) / 0.05565
    observed = EntericMethaneCalculator.heifer_methane("model", dry_matter_intake, nutrient_concentrations)
    assert pytest.approx(observed) == expected


@pytest.mark.parametrize(
    "body_weight,milk_fat,metabolizable_energy_intake,nutrient_amounts,nutrient_concentrations,"
    "methane_mitigation_method,methane_mitigation_additive_amount",
    [
        (59.67, 33.7, 77.7, {"dm": 3.69}, {"EE": 57.4, "NDF": 39.14, "starch": 56.27},
         "test_method", 92.4)
    ]
)
def test_cow_methane_is_lactating_with_mitigation(body_weight: float,
                                                  milk_fat: float,
                                                  metabolizable_energy_intake: float,
                                                  nutrient_amounts: dict[str, float],
                                                  nutrient_concentrations: dict[str, float],
                                                  methane_mitigation_method: str,
                                                  methane_mitigation_additive_amount: float,
                                                  mocker: MockerFixture) -> None:
    """Test the daily enteric emissions for lactating cows with mitigation."""
    dry_matter_intake = nutrient_amounts["dm"]
    NDF_concentration = nutrient_concentrations["NDF"]
    EE_concentration = nutrient_concentrations["EE"]
    starch_concentration = nutrient_concentrations["starch"]

    mock_lactating_cow_manure = mocker.patch.object(EntericMethaneCalculator, "_lactating_cow_manure",
                                                    return_value=25)

    methane_yield = 25 / dry_matter_intake
    mock_methane_mitigation = mocker.patch.object(MethaneMitigationCalculator,
                                                  "methane_mitigation",
                                                  return_value=23.5)
    expected = (
        methane_yield
        * (1 + 23.5 / 100)
        * dry_matter_intake
    )
    observed = EntericMethaneCalculator.cow_methane(True,
                                                    body_weight,
                                                    milk_fat,
                                                    metabolizable_energy_intake,
                                                    nutrient_amounts,
                                                    nutrient_concentrations,
                                                    methane_mitigation_method,
                                                    methane_mitigation_additive_amount,
                                                    "model")
    assert observed == expected

    mock_lactating_cow_manure.assert_called_once_with(
        body_weight,
        milk_fat,
        metabolizable_energy_intake,
        nutrient_amounts,
        nutrient_concentrations,
        "model",
    )
    mock_methane_mitigation.assert_called_once_with(NDF_concentration,
                                                    EE_concentration,
                                                    starch_concentration,
                                                    methane_mitigation_method,
                                                    methane_mitigation_additive_amount)


@pytest.mark.parametrize(
    "body_weight,milk_fat,metabolizable_energy_intake,nutrient_amounts,nutrient_concentrations,"
    "methane_mitigation_method,methane_mitigation_additive_amount",
    [
        (59.67, 33.7, 77.7, {"dm": 3.69}, {"EE": 57.4, "NDF": 39.14, "starch": 56.27},
         "test_method", 92.4)
    ]
)
def test_cow_manure_dry_with_mitigation(body_weight: float,
                                        milk_fat: float,
                                        metabolizable_energy_intake: float,
                                        nutrient_amounts: dict[str, float],
                                        nutrient_concentrations: dict[str, float],
                                        methane_mitigation_method: str,
                                        methane_mitigation_additive_amount: float,
                                        mocker: MockerFixture) -> None:
    """Test the daily enteric emissions for dry cows with mitigation."""
    dry_matter_intake = nutrient_amounts["dm"]
    NDF_concentration = nutrient_concentrations["NDF"]
    EE_concentration = nutrient_concentrations["EE"]
    starch_concentration = nutrient_concentrations["starch"]

    mock_dry_cow_manure = mocker.patch.object(EntericMethaneCalculator, "_dry_cow_manure",
                                                    return_value=25)

    methane_yield = 25 / dry_matter_intake
    mock_methane_mitigation = mocker.patch.object(MethaneMitigationCalculator,
                                                  "methane_mitigation",
                                                  return_value=23.5)
    expected = (
        methane_yield
        * (1 + 23.5 / 100)
        * dry_matter_intake
    )
    observed = EntericMethaneCalculator.cow_methane(False,
                                                    body_weight,
                                                    milk_fat,
                                                    metabolizable_energy_intake,
                                                    nutrient_amounts,
                                                    nutrient_concentrations,
                                                    methane_mitigation_method,
                                                    methane_mitigation_additive_amount,
                                                    "model")
    assert observed == expected

    mock_dry_cow_manure.assert_called_once_with(
        "model",
        metabolizable_energy_intake,
        nutrient_amounts,
        nutrient_concentrations
    )
    mock_methane_mitigation.assert_called_once_with(NDF_concentration,
                                                    EE_concentration,
                                                    starch_concentration,
                                                    methane_mitigation_method,
                                                    methane_mitigation_additive_amount)
