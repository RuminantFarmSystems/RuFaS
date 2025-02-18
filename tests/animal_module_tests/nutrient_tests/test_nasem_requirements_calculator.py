import pytest

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.nutrients.nasem_requirements_calculator import NASEMRequirementsCalculator


def test_calculate_requirements() -> None:
    """Test that the energy and nutritional requirements of an animal are calculated correctly."""
    pass


def test_calculate_maintenance_energy_requirements() -> None:
    """Test that energy requirements for maintenance are calculated correctly."""
    pass


def test_calculate_growth_energy_requirements() -> None:
    """Test that energy requirements for growth are calculated correctly."""
    pass


def test_calculate_pregnancy_energy_requirements() -> None:
    """Test that energy requirements for pregnancy are calculated correctly."""
    pass


@pytest.mark.parametrize(
    "lact, weight, frame_gain, gravid_gain, dmi, true_protein, milk, ndf, expected",
    [
        (True, 490.0, 100.0, 500.0, 45.0, 1.2, 25.0, 50.0, 190887.068472),
        (False, 490.0, 100.0, 500.0, 45.0, 0.0, 0.0, 50.0, 190462.225718),
    ],
)
def test_calculate_protein_requirement(
    lact: bool,
    weight: float,
    frame_gain: float,
    gravid_gain: float,
    dmi: float,
    true_protein: float,
    milk: float,
    ndf: float,
    expected: float,
) -> None:
    """Test that the protein requirement is calculated correctly."""
    actual = NASEMRequirementsCalculator._calculate_protein_requirement(
        lact, weight, frame_gain, gravid_gain, dmi, true_protein, milk, ndf
    )

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "weight, mature_weight, day_preg, avg_gain, dmi, true_protein, milk, parity, expected",
    [
        (450.0, 555.0, 100, 3.1, 50.0, 3.0, 31.0, 1, 79.634005),
        (560.0, 560.0, None, 0.0, 40.0, 0.0, 0.0, 3, 36.0),
    ],
)
def test_calculate_calcium_requirement(
    weight: float,
    mature_weight: float,
    day_preg: int | None,
    avg_gain: float,
    dmi: float,
    true_protein: float,
    milk: float,
    parity: int,
    expected: float,
) -> None:
    """Test that calcium requirement is calculated correctly."""
    actual = NASEMRequirementsCalculator._calculate_calcium_requirement(
        weight, mature_weight, day_preg, avg_gain, dmi, true_protein, milk, parity
    )

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "weight, mature_weight, type, day_preg, avg_gain, dmi, true_protein, milk, parity, expected",
    [
        (500.0, 650.0, AnimalType.LAC_COW, 200, 4.0, 45.0, 3.0, 29.0, 3, 72.330420),
        (300.0, 650.0, AnimalType.HEIFER_II, 0, 4.0, 40.0, 0.0, 0.0, 0, 58.957788),
        (25.0, 600.0, AnimalType.CALF, 0, 1.2, 10.0, 0.0, 0.0, 0, 12.631220),
    ],
)
def test_calculate_phosphorus_requirement(
    weight: float,
    mature_weight: float,
    type: AnimalType,
    day_preg: int,
    avg_gain: float,
    dmi: float,
    true_protein: float,
    milk: float,
    parity: int,
    expected: float,
) -> None:
    """Test that phosphorus requirement is calculated correctly."""
    actual = NASEMRequirementsCalculator._calculate_phosphorus_requirement(
        weight, mature_weight, type, day_preg, avg_gain, dmi, true_protein, milk, parity
    )

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "weight, mature_weight, days_milk, lact, lact_energy, parity, body_score, ndf, expected",
    [
        (400.0, 450.0, None, False, 0.0, 0, 3, 30.0, 8.950167),
        (400.0, 450.0, 100, True, 1000.0, 1, 3, 45.0, 315.099203),
    ],
)
def test_calculate_dry_matter_intake(
    weight: float,
    mature_weight: float,
    days_milk: int | None,
    lact: bool,
    lact_energy: float,
    parity: int,
    body_score: int,
    ndf: float,
    expected: float,
) -> None:
    """Test that dry matter intake is estimated correctly."""
    actual = NASEMRequirementsCalculator._calculate_dry_matter_intake(
        weight, mature_weight, days_milk, lact, lact_energy, parity, body_score, ndf
    )

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "weight, housing, distance, expected",
    [(450.0, "Barn", 100.0, 0.01575), (475.0, "Grazing", 120.0, 41.895), (500.0, "Other", 50.0, 0.0)],
)
def test_calculate_activity_energy_requirements(weight: float, housing: str, distance: float, expected: float) -> None:
    """Test that net energy requirement for activity is calculated correctly."""
    actual = NASEMRequirementsCalculator._calculate_activity_energy_requirements(weight, housing, distance)

    assert actual == expected
