import pytest

from RUFAS.biophysical.animal.nutrients.nasem_requirements_calculator import NASEMRequirementsCalculator


@pytest.mark.parametrize(
    "weight, mature_weight, days_milk, lact, lact_energy, parity, body_score, ndf, expected",
    [
        (400.0, 450.0, None, False, 0.0, 0, 3, 30.0, 8.950167),
        (400.0, 450.0, 100, True, 1000.0, 1, 3, 45.0, 315.099203),
    ]
)
def test_calculate_dry_matter_intake(weight: float, mature_weight: float, days_milk: int | None, lact: bool, lact_energy: float, parity: int, body_score: int, ndf: float, expected: float) -> None:
    """Test that dry matter intake is estimated correctly."""
    actual = NASEMRequirementsCalculator._calculate_dry_matter_intake(weight, mature_weight, days_milk, lact, lact_energy, parity, body_score, ndf)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "weight, housing, distance, expected",
    [
        (450.0, "Barn", 100.0, 0.01575), (475.0, "Grazing", 120.0, 41.895), (500.0, "Other", 50.0, 0.0)
    ]
)
def test_calculate_activity_energy_requirements(weight: float, housing: float, distance: float, expected: float) -> None:
    """Test that net energy requirement for activity is calculated correctly."""
    actual = NASEMRequirementsCalculator._calculate_activity_energy_requirements(weight, housing, distance)

    assert actual == expected
