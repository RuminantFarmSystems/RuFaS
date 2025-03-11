import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.digestive_system.enteric_methane_calculator import EntericMethaneCalculator
from RUFAS.biophysical.animal.digestive_system.methane_mitigation_calculator import MethaneMitigationCalculator


def test_calf_methane_no_model() -> None:
    """Test the calf methane result without model provided."""
    actual = EntericMethaneCalculator.calculate_calf_methane(None, 30)
    assert actual == 0


@pytest.mark.parametrize("body_weight,expected", [(30, 12.52883), (195.45, 51.09126)])
def test_calf_methane_with_model(body_weight: float, expected: float) -> None:
    """Test the calf methane result without model provided."""
    actual = EntericMethaneCalculator.calculate_calf_methane("model", body_weight)
    assert pytest.approx(actual) == expected


def test_heifer_methane_no_model() -> None:
    """Test the heifer methane result without model provided."""
    actual = EntericMethaneCalculator.calculate_heifer_methane(None, 30, {})
    assert actual == 0


@pytest.mark.parametrize(
    "dry_matter_intake,nutrient_concentrations,expected",
    [(59.67, {"CP": 3.69, "EE": 57.4, "NDF": 39.14, "ash": 56.27}, 2065.9805725876017)],
)
def test_heifer_methane_with_model(
    dry_matter_intake: float, nutrient_concentrations: dict[str, float], expected: float
) -> None:
    """Test the calf methane result without model provided."""
    actual = EntericMethaneCalculator.calculate_heifer_methane("model", dry_matter_intake, nutrient_concentrations)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "body_weight,milk_fat,metabolizable_energy_intake,nutrient_amounts,nutrient_concentrations,"
    "methane_mitigation_method,methane_mitigation_additive_amount,expected",
    [
        (
            59.67,
            33.7,
            77.7,
            {"dm": 3.69},
            {"EE": 57.4, "NDF": 39.14, "starch": 56.27},
            "test_method",
            92.4,
            30.874999999999996,
        )
    ],
)
def test_cow_methane_is_lactating_with_mitigation(
    body_weight: float,
    milk_fat: float,
    metabolizable_energy_intake: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
    methane_mitigation_method: str,
    methane_mitigation_additive_amount: float,
    expected: float,
    mocker: MockerFixture,
) -> None:
    """Test the daily enteric emissions for lactating cows with mitigation."""
    NDF_concentration = nutrient_concentrations["NDF"]
    EE_concentration = nutrient_concentrations["EE"]
    starch_concentration = nutrient_concentrations["starch"]

    mock_lactating_cow_manure = mocker.patch.object(
        EntericMethaneCalculator, "_calculate_lactating_cow_manure", return_value=25
    )

    mock_methane_mitigation = mocker.patch.object(MethaneMitigationCalculator, "mitigate_methane", return_value=23.5)

    actual = EntericMethaneCalculator.calculate_cow_methane(
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

    assert pytest.approx(actual) == expected

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
    "methane_mitigation_method,methane_mitigation_additive_amount,expected",
    [
        (
            59.67,
            33.7,
            77.7,
            {"dm": 3.69},
            {"EE": 57.4, "NDF": 39.14, "starch": 56.27},
            "test_method",
            92.4,
            30.874999999999996,
        )
    ],
)
def test_cow_manure_dry_with_mitigation(
    body_weight: float,
    milk_fat: float,
    metabolizable_energy_intake: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
    methane_mitigation_method: str,
    methane_mitigation_additive_amount: float,
    expected: float,
    mocker: MockerFixture,
) -> None:
    """Test the daily enteric emissions for dry cows with mitigation."""
    NDF_concentration = nutrient_concentrations["NDF"]
    EE_concentration = nutrient_concentrations["EE"]
    starch_concentration = nutrient_concentrations["starch"]

    mock_dry_cow_manure = mocker.patch.object(EntericMethaneCalculator, "_calculate_dry_cow_manure", return_value=25)

    mock_methane_mitigation = mocker.patch.object(MethaneMitigationCalculator, "mitigate_methane", return_value=23.5)

    actual = EntericMethaneCalculator.calculate_cow_methane(
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

    assert pytest.approx(actual) == expected

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
    "body_weight,milk_fat,metabolizable_energy_intake,nutrient_amounts,nutrient_concentrations,expected",
    [
        (
            59.67,
            6.31,
            5.25,
            {"dm": 42.32},
            {"ash": 39.14, "ADF": 39.54, "CP": 26.14, "NDF": 48.14, "EE": 35.4, "starch": 54.2},
            653.4971599999999,
        )
    ],
)
def test_lactating_cow_manure_mutian(
    body_weight: float,
    milk_fat: float,
    metabolizable_energy_intake: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
    expected: float,
) -> None:
    """Test the daily enteric emissions for lactating cows with Mutian method."""
    actual = EntericMethaneCalculator._calculate_lactating_cow_manure(
        body_weight, milk_fat, metabolizable_energy_intake, nutrient_amounts, nutrient_concentrations, "Mutian"
    )
    assert expected == actual


@pytest.mark.parametrize(
    "body_weight,milk_fat,metabolizable_energy_intake,nutrient_amounts,nutrient_concentrations,expected",
    [
        (
            59.67,
            6.31,
            5.25,
            {"dm": 42.32},
            {"ash": 39.14, "ADF": 39.54, "CP": 26.14, "NDF": 48.14, "EE": 35.4, "starch": 54.2},
            52.55881469520194,
        )
    ],
)
def test_lactating_cow_manure_mills(
    body_weight: float,
    milk_fat: float,
    metabolizable_energy_intake: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
    expected: float,
) -> None:
    """Test the daily enteric emissions for lactating cows with Mills method."""
    actual = EntericMethaneCalculator._calculate_lactating_cow_manure(
        body_weight, milk_fat, metabolizable_energy_intake, nutrient_amounts, nutrient_concentrations, "Mills"
    )
    assert expected == actual


@pytest.mark.parametrize(
    "body_weight,milk_fat,metabolizable_energy_intake,nutrient_amounts,nutrient_concentrations,expected",
    [
        (
            59.67,
            6.31,
            5.25,
            {"dm": 42.32},
            {"ash": 39.14, "ADF": 39.54, "CP": 26.14, "NDF": 48.14, "EE": 35.4, "starch": 54.2},
            1338.2847136028754,
        )
    ],
)
def test_lactating_cow_manure_IPCC(
    body_weight: float,
    milk_fat: float,
    metabolizable_energy_intake: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
    expected: float,
) -> None:
    """Test the daily enteric emissions for lactating cows with IPCC method."""
    actual = EntericMethaneCalculator._calculate_lactating_cow_manure(
        body_weight, milk_fat, metabolizable_energy_intake, nutrient_amounts, nutrient_concentrations, "IPCC"
    )
    assert expected == actual


def test_lactating_cow_manure_other() -> None:
    """Test the daily enteric emissions for lactating cows with no specific method."""
    actual = EntericMethaneCalculator._calculate_lactating_cow_manure(
        59.67,
        6.31,
        5.25,
        {"dm": 42.32},
        {"ash": 39.14, "ADF": 39.54, "CP": 26.14, "NDF": 48.14, "EE": 35.4, "starch": 54.2},
        "test",
    )
    assert actual == 0


@pytest.mark.parametrize(
    "metabolizable_energy_intake,nutrient_amounts,nutrient_concentrations,expected",
    [
        (
            5.25,
            {"dm": 42.32},
            {"ash": 39.14, "ADF": 39.54, "CP": 26.14, "NDF": 48.14, "EE": 35.4, "starch": 54.2},
            52.55881469520198,
        )
    ],
)
def test_dry_cow_manure_mills(
    metabolizable_energy_intake: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
    expected: float,
) -> None:
    """Test the daily enteric emissions for dry cows with Mills method."""
    actual = EntericMethaneCalculator._calculate_dry_cow_manure(
        "Mills", metabolizable_energy_intake, nutrient_amounts, nutrient_concentrations
    )
    assert expected == actual


@pytest.mark.parametrize(
    "metabolizable_energy_intake,nutrient_amounts,nutrient_concentrations,expected",
    [
        (
            5.25,
            {"dm": 42.32},
            {"ash": 39.14, "ADF": 39.54, "CP": 26.14, "NDF": 48.14, "EE": 35.4, "starch": 54.2},
            1338.2847136028754,
        )
    ],
)
def test_dry_cow_manure_others(
    metabolizable_energy_intake: float,
    nutrient_amounts: dict[str, float],
    nutrient_concentrations: dict[str, float],
    expected: float,
) -> None:
    """Test the daily enteric emissions for dry cows with other method."""
    actual = EntericMethaneCalculator._calculate_dry_cow_manure(
        "other", metabolizable_energy_intake, nutrient_amounts, nutrient_concentrations
    )
    assert expected == actual
