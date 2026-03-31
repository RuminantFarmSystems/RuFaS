import pytest
from typing import Generator

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.digestive_system import DigestiveSystemInputs
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionSupply


@pytest.fixture
def sample_nutrition_supply() -> Generator[NutritionSupply, None, None]:
    """Fixture to provide a sample NutritionSupply object."""
    yield NutritionSupply(
        metabolizable_energy=50.0,
        maintenance_energy=10.0,
        lactation_energy=15.0,
        growth_energy=20.0,
        metabolizable_protein=5.0,
        calcium=0.5,
        phosphorus=0.3,
        dry_matter=50.0,
        wet_matter=50.0,
        ndf_supply=40.0,
        forage_ndf_supply=30.0,
        fat_supply=5.0,
        crude_protein=10.0,
        adf_supply=20.0,
        digestible_energy_supply=45.0,
        tdn_supply=60.0,
        lignin_supply=5.0,
        ash_supply=5.0,
        potassium_supply=0.5,
        starch_supply=5.0,
        byproduct_supply=5.0,
    )


@pytest.fixture
def sample_digestive_input(sample_nutrition_supply: NutritionSupply) -> Generator[DigestiveSystemInputs, None, None]:
    """Fixture to provide a sample DigestiveSystemInputs instance."""
    yield DigestiveSystemInputs(
        animal_type=AnimalType.LAC_COW,
        body_weight=650.0,
        nutrients=sample_nutrition_supply,
        days_in_milk=100,
        metabolizable_energy_intake=40.0,
        phosphorus_intake=0.4,
        phosphorus_requirement=0.3,
        phosphorus_reserves=0.2,
        phosphorus_endogenous_loss=0.1,
        daily_milk_produced=35.0,
        fat_content=3.8,
        protein_content=3.2,
    )


def test_digestive_system_inputs_initialization(sample_digestive_input: DigestiveSystemInputs) -> None:
    """Test that DigestiveSystemInputs correctly stores attribute values."""
    assert sample_digestive_input.animal_type == AnimalType.LAC_COW
    assert sample_digestive_input.body_weight == 650.0
    assert sample_digestive_input.nutrients.dry_matter == 50.0
    assert sample_digestive_input.days_in_milk == 100
    assert sample_digestive_input.metabolizable_energy_intake == 40.0
    assert sample_digestive_input.phosphorus_intake == 0.4
    assert sample_digestive_input.phosphorus_requirement == 0.3
    assert sample_digestive_input.phosphorus_reserves == 0.2
    assert sample_digestive_input.phosphorus_endogenous_loss == 0.1
    assert sample_digestive_input.daily_milk_produced == 35.0
    assert sample_digestive_input.fat_content == 3.8
    assert sample_digestive_input.protein_content == 3.2


@pytest.mark.parametrize(
    "days_in_milk, expected_is_milking",
    [
        (100, True),
        (1, True),
        (0, False),
        (-1, False),
    ],
)
def test_is_milking_property(
    days_in_milk: int, expected_is_milking: bool, sample_nutrition_supply: NutritionSupply
) -> None:
    """Test the is_milking property for various days_in_milk values."""
    digestive_input = DigestiveSystemInputs(
        animal_type=AnimalType.LAC_COW,
        body_weight=650.0,
        nutrients=sample_nutrition_supply,
        days_in_milk=days_in_milk,
        metabolizable_energy_intake=40.0,
        phosphorus_intake=0.4,
        phosphorus_requirement=0.3,
        phosphorus_reserves=0.2,
        phosphorus_endogenous_loss=0.1,
        daily_milk_produced=35.0,
        fat_content=3.8,
        protein_content=3.2,
    )

    assert digestive_input.is_milking == expected_is_milking
