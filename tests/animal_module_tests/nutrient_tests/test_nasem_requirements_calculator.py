import pytest

from RUFAS.biophysical.animal.nutrients.nasem_requirements_calculator import NASEMRequirementsCalculator


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
