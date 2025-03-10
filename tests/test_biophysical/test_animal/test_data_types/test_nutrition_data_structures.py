import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.data_types.nutrition_data_structures import (
    NutritionEvaluationResults,
    NutritionRequirements,
)


@pytest.fixture
def requirements(mocker: MockerFixture) -> NutritionRequirements:
    """Nutrition requirements fixture."""
    mocker.patch.object(NutritionRequirements, "__init__", return_value=None)
    return NutritionRequirements()


@pytest.fixture
def evaluation(mocker: MockerFixture) -> NutritionEvaluationResults:
    """Nutrition evaluation results fixture."""
    mocker.patch.object(NutritionEvaluationResults, "__init__", return_value=None)
    return NutritionEvaluationResults()


@pytest.mark.parametrize(
    "maintenance,growth,pregnancy,lactation,activity,expected",
    [(0.0, 0.0, 0.0, 0.0, 0.0, 0.0), (10.0, 20.0, 30.0, 40.0, 50.0, 150.0)],
)
def test_total_energy_requirement(
    requirements: NutritionRequirements,
    maintenance: float,
    growth: float,
    pregnancy: float,
    lactation: float,
    activity: float,
    expected: float,
) -> None:
    """Test that total energy requirement is calculated correctly."""
    requirements.maintenance_energy = maintenance
    requirements.growth_energy = growth
    requirements.pregnancy_energy = pregnancy
    requirements.lactation_energy = lactation
    requirements.activity_energy = activity

    actual = requirements.total_energy_requirement

    assert actual == expected


@pytest.mark.parametrize(
    "protein,ndf,fat,dry_matter,expected",
    ([0.0, 0.0, 0.0, 0.0, True], [1.0, 0.0, 0.0, 0.0, False], [0.0, 0.0, -3.0, 0.0, False]),
)
def test_are_clamped_values_acceptable(
    evaluation: NutritionEvaluationResults, protein: float, ndf: float, fat: float, dry_matter: float, expected: bool
) -> None:
    """Test that clamped values are checked correctly."""
    evaluation.metabolizable_protein = protein
    evaluation.ndf_percent = ndf
    evaluation.fat_percent = fat
    evaluation.dry_matter = dry_matter

    actual = evaluation._are_clamped_values_acceptable

    assert actual == expected


@pytest.mark.parametrize(
    "maint,growth,calcium,phos,forage_ndf,expected",
    [(20.0, 0.0, 1.0, 2.0, 0.0, True), (0.0, 0.0, 0.0, 0.0, 0.0, True), (-10.0, 30.0, 2.0, 1.0, 1.0, False)],
)
def test_is_valid_heifer_ration(
    evaluation: NutritionEvaluationResults,
    maint: float,
    growth: float,
    calcium: float,
    phos: float,
    forage_ndf: float,
    expected: float,
) -> None:
    """Test that results correctly indicate whether heifer ration is valid."""
    evaluation.metabolizable_protein, evaluation.ndf_percent, evaluation.fat_percent, evaluation.dry_matter = (
        0.0,
        0.0,
        0.0,
        0.0,
    )
    evaluation.total_energy, evaluation.lactation_energy = None, None
    evaluation.maintenance_energy = maint
    evaluation.growth_energy = growth
    evaluation.calcium = calcium
    evaluation.phosphorus = phos
    evaluation.forage_ndf_percent = forage_ndf

    actual = evaluation.is_valid_heifer_ration

    assert actual == expected


@pytest.mark.parametrize(
    "total,maint,lactation,growth,calcium,phos,expected",
    [
        (30.0, 20.0, 0.0, 0.0, 1.0, 2.0, True),
        (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, True),
        (30.0, -10.0, 20.0, 30.0, 2.0, 1.0, False),
        (None, 10.0, 13.0, 10.0, 20.0, 15.0, False),
    ],
)
def test_is_valid_cow_ration(
    evaluation: NutritionEvaluationResults,
    total: float | None,
    maint: float,
    lactation: float,
    growth: float,
    calcium: float,
    phos: float,
    expected: float,
) -> None:
    """Test that results correctly indicate whether cow ration is valid."""
    (
        evaluation.metabolizable_protein,
        evaluation.ndf_percent,
        evaluation.fat_percent,
        evaluation.dry_matter,
        evaluation.forage_ndf_percent,
    ) = (
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    )
    evaluation.total_energy = total
    evaluation.maintenance_energy = maint
    evaluation.lactation_energy = lactation
    evaluation.growth_energy = growth
    evaluation.calcium = calcium
    evaluation.phosphorus = phos

    actual = evaluation.is_valid_cow_ration

    assert actual == expected
