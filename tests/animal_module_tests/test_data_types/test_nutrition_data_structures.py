import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionEvaluationResults, NutritionRequirements, NutritionSupply


@pytest.fixture
def requirements(mocker: MockerFixture) -> NutritionRequirements:
    """Nutrition requirements fixture."""
    mocker.patch.object(NutritionRequirements, "__init__", return_value=None)
    return NutritionRequirements()


@pytest.fixture
def supply(mocker: MockerFixture) -> NutritionSupply:
    """Nutrition supply fixture."""
    mocker.patch.object(NutritionSupply, "__init__", return_value=None)
    return NutritionSupply()


@pytest.fixture
def evaluation(mocker: MockerFixture) -> NutritionEvaluationResults:
    """Nutrition evaluation results fixture."""
    mocker.patch.object(NutritionEvaluationResults, "__init__", return_value=None)
    return NutritionEvaluationResults()


@pytest.mark.parametrize(
    "maintenance,growth,pregnancy,lactation,activity,expected",
    [(0.0, 0.0, 0.0, 0.0, 0.0, 0.0), (10.0, 20.0, 30.0, 40.0, 50.0, 150.0)]
)
def test_total_energy_requirement(requirements: NutritionRequirements, maintenance: float, growth: float, pregnancy: float, lactation: float, activity: float, expected: float) -> None:
    """Test that total energy requirement is calculated correctly."""
    requirements.maintenance = maintenance
    requirements.growth = growth
    requirements.pregnancy = pregnancy
    requirements.lactation = lactation
    requirements.activity = activity

    actual = requirements.total_energy_requirement

    assert actual == expected
