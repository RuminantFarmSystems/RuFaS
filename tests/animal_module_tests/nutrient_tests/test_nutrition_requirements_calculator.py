import pytest

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.nutrients.nutrition_requirements_calculator import NutritionRequirementsCalculator


@pytest.mark.parametrize(
    "type, fat, true_protein, lactose, milk, expected",
    [(AnimalType.LAC_COW, 1.1, 2.1, 1.3, 33.0, 9.142852), (AnimalType.HEIFER_III, 0.0, 0.0, 0.0, 0.0, 0.0)],
)
def test_calculate_lactation_energy_requirements(
    type: AnimalType, fat: float, true_protein: float, lactose: float, milk: float, expected: float
) -> None:
    """Test that the lactation energy requirement is calculated correctly."""
    actual = NutritionRequirementsCalculator._calculate_lactation_energy_requirements(
        type, fat, true_protein, lactose, milk
    )

    assert pytest.approx(actual) == expected
