import pytest

from RUFAS.biophysical.animal.data_types.nutrition_data_structures import (
    NutritionEvaluationResults,
    NutritionRequirements,
    NutritionSupply,
)
from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements
from RUFAS.user_constants import UserConstants


@pytest.fixture
def requirements() -> NutritionRequirements:
    """Nutrition requirements fixture."""
    return NutritionRequirements(
        maintenance_energy=10.0,
        growth_energy=20.0,
        pregnancy_energy=30.0,
        lactation_energy=40.0,
        metabolizable_protein=50.0,
        calcium=60.0,
        phosphorus=70.0,
        process_based_phosphorus=80.0,
        dry_matter=90.0,
        activity_energy=100.0,
        essential_amino_acids=EssentialAminoAcidRequirements(
            histidine=0.0,
            isoleucine=0.0,
            leucine=0.0,
            lysine=0.0,
            methionine=0.0,
            phenylalanine=0.0,
            threonine=0.0,
            thryptophan=0.0,
            valine=0.0,
        ),
    )


@pytest.fixture
def supply() -> NutritionSupply:
    """Nutrition supply fixture."""
    return NutritionSupply(
        metabolizable_energy=10.0,
        maintenance_energy=20.0,
        lactation_energy=30.0,
        growth_energy=40.0,
        metabolizable_protein=50.0,
        calcium=60.0,
        phosphorus=70.0,
        dry_matter=80.0,
        wet_matter=100.0,
        ndf_supply=10.0,
        forage_ndf_supply=20.0,
        fat_supply=5.0,
        crude_protein=25.0,
        adf_supply=15.0,
        digestible_energy_supply=35.0,
        tdn_supply=45.0,
        lignin_supply=5.0,
        ash_supply=7.0,
        potassium_supply=8.0,
        starch_supply=9.0,
        byproduct_supply=10.0,
    )


@pytest.fixture
def evaluation() -> NutritionEvaluationResults:
    """Nutrition evaluation results fixture."""
    return NutritionEvaluationResults(
        total_energy=50.0,
        maintenance_energy=20.0,
        lactation_energy=30.0,
        growth_energy=40.0,
        metabolizable_protein=10.0,
        calcium=5.0,
        phosphorus=4.0,
        dry_matter=3.0,
        ndf_percent=2.0,
        forage_ndf_percent=1.0,
        fat_percent=0.5,
    )


@pytest.fixture
def valid_heifer_cow_ration() -> NutritionEvaluationResults:
    """Nutrition evaluation results fixture."""
    return NutritionEvaluationResults(
        total_energy=50.0,
        maintenance_energy=20.0,
        lactation_energy=30.0,
        growth_energy=40.0,
        metabolizable_protein=0.0,
        calcium=5.0,
        phosphorus=4.0,
        dry_matter=0.0,
        ndf_percent=0.0,
        forage_ndf_percent=0.0,
        fat_percent=0.0,
    )


def test_total_energy_requirement(requirements: NutritionRequirements) -> None:
    """Test total energy requirement calculation."""
    assert requirements.total_energy_requirement == 200.0


def test_requirements_addition(requirements: NutritionRequirements) -> None:
    """Test adding two NutritionRequirements instances."""
    new_req = requirements + requirements
    assert new_req.maintenance_energy == 20.0
    assert new_req.growth_energy == 40.0


def test_requirements_division(requirements: NutritionRequirements) -> None:
    """Test dividing NutritionRequirements by a scalar."""
    new_req = requirements / 2
    assert new_req.maintenance_energy == 5.0


def test_requirements_zero_division(requirements: NutritionRequirements) -> None:
    """Test dividing NutritionRequirements by zero."""
    with pytest.raises(ZeroDivisionError):
        _ = requirements / 0.0


def test_make_empty_nutrition_requirements() -> None:
    """Test creation of empty NutritionRequirements instance."""
    empty_req = NutritionRequirements.make_empty_nutrition_requirements()
    assert empty_req.maintenance_energy == 0.0


def test_supply_post_init(supply: NutritionSupply) -> None:
    """Test that nitrogen supply is correctly calculated."""
    assert supply.nitrogen_supply == supply.crude_protein * UserConstants.PROTEIN_TO_NITROGEN


def test_supply_addition(supply: NutritionSupply) -> None:
    """Test adding two NutritionSupply instances."""
    new_supply = supply + supply
    assert new_supply.metabolizable_energy == 20.0


def test_supply_division(supply: NutritionSupply) -> None:
    """Test dividing NutritionSupply by a scalar."""
    new_supply = supply / 2
    assert new_supply.metabolizable_energy == 5.0


def test_supply_zero_division(supply: NutritionSupply) -> None:
    """Test dividing NutritionSupply by zero."""
    with pytest.raises(ZeroDivisionError):
        _ = supply / 0.0


def test_make_empty_nutrition_supply() -> None:
    """Test creation of empty NutritionSupply instance."""
    empty_supply = NutritionSupply.make_empty_nutrition_supply()
    assert empty_supply.metabolizable_energy == 0.0


def test_adf_percentage(supply: NutritionSupply) -> None:
    """Test that ADF percentage is correctly calculated."""
    assert supply.adf_percentage == 18.75


def test_ash_percentage(supply: NutritionSupply) -> None:
    """Test that ash percentage is correctly calculated."""
    assert supply.ash_percentage == 8.75


def test_crude_protein_percentage(supply: NutritionSupply) -> None:
    """Test that crude protein percentage is correctly calculated."""
    assert supply.crude_protein_percentage == 31.25


def test_dry_matter_percentage(supply: NutritionSupply) -> None:
    """Test that dry matter percentage is correctly calculated."""
    assert supply.dry_matter_percentage == 80.0


def test_fat_percentage(supply: NutritionSupply) -> None:
    """Test that fat percentage is correctly calculated."""
    assert supply.fat_percentage == 6.25


def test_ndf_percentage(supply: NutritionSupply) -> None:
    """Test that NDF percentage is correctly calculated."""
    assert supply.ndf_percentage == 12.5


def test_forage_ndf_percentage(supply: NutritionSupply) -> None:
    """Test that forage NDF percentage is correctly calculated."""
    assert supply.forage_ndf_percentage == 25.0


def test_potassium_percentage(supply: NutritionSupply) -> None:
    """Test that potassium percentage is correctly calculated."""
    assert supply.potassium_percentage == 10.0


def test_starch_percentage(supply: NutritionSupply) -> None:
    """Test that starch percentage is correctly calculated."""
    assert supply.starch_percentage == 11.25


def test_are_clamped_values_acceptable(evaluation: NutritionEvaluationResults) -> None:
    """Test that clamped values are checked correctly."""
    assert evaluation._are_clamped_values_acceptable is False


def test_is_valid_heifer_ration(valid_heifer_cow_ration: NutritionEvaluationResults) -> None:
    """Test that results correctly indicate whether heifer ration is valid."""
    assert valid_heifer_cow_ration.is_valid_heifer_ration is True


def test_is_valid_cow_ration(valid_heifer_cow_ration: NutritionEvaluationResults) -> None:
    """Test that results correctly indicate whether cow ration is valid."""
    assert valid_heifer_cow_ration.is_valid_cow_ration is True
    valid_heifer_cow_ration.total_energy = None
    assert valid_heifer_cow_ration.is_valid_cow_ration is False


def test_evaluation_report(valid_heifer_cow_ration: NutritionEvaluationResults) -> None:
    """Test that report property generates correct dictionary."""
    report = valid_heifer_cow_ration.report
    assert report["is_valid_heifer_ration"] is True
    assert report["is_valid_cow_ration"] is True


def test_evaluation_addition(evaluation: NutritionEvaluationResults) -> None:
    """Test adding two NutritionEvaluationResults instances."""
    new_eval = evaluation + evaluation
    assert new_eval.total_energy == 100.0


def test_evaluation_division(evaluation: NutritionEvaluationResults) -> None:
    """Test dividing NutritionEvaluationResults by a scalar."""
    new_eval = evaluation / 2
    assert new_eval.total_energy == 25.0


def test_evaluation_zero_division(evaluation: NutritionEvaluationResults) -> None:
    """Test dividing NutritionEvaluationResults by zero."""
    with pytest.raises(ZeroDivisionError):
        _ = evaluation / 0.0


def test_make_empty_evaluation_results() -> None:
    """Test creation of empty NutritionEvaluationResults instance."""
    empty_eval = NutritionEvaluationResults.make_empty_evaluation_results()
    assert empty_eval.total_energy == 0.0
