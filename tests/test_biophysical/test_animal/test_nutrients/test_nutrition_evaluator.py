from dataclasses import asdict
import pytest
from pytest_lazyfixture import lazy_fixture
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements, NutritionSupply
from RUFAS.biophysical.animal.nutrients.nutrition_evaluator import NutritionEvaluator
from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements


@pytest.fixture
def nutrition_requirements_base() -> NutritionRequirements:
    """Base nutrition requirements fixture."""
    return NutritionRequirements(
        maintenance_energy=10.0,
        growth_energy=5.0,
        pregnancy_energy=0.0,
        lactation_energy=8.0,
        metabolizable_protein=600.0,
        calcium=100.0,
        phosphorus=50.0,
        process_based_phosphorus=50.0,
        dry_matter=10.0,
        activity_energy=2.0,
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
def nutrition_supply_base() -> NutritionSupply:
    """Base nutrition supply fixture (adequate supply)."""
    return NutritionSupply(
        metabolizable_energy=30.0,
        maintenance_energy=12.0,
        lactation_energy=9.0,
        growth_energy=6.0,
        metabolizable_protein=700.0,
        calcium=120.0,
        phosphorus=55.0,
        dry_matter=12.0,
        wet_matter=15.0,
        ndf_supply=3.0,
        forage_ndf_supply=1.5,
        fat_supply=2.0,
        crude_protein=3.0,
        adf_supply=1.0,
        digestible_energy_supply=28.0,
        tdn_supply=6.0,
        lignin_supply=0.5,
        ash_supply=0.3,
        potassium_supply=0.2,
        starch_supply=2.0,
        byproduct_supply=1.0,
    )


@pytest.fixture
def nutrition_supply_insufficient_energy() -> NutritionSupply:
    """Fixture for insufficient energy supply."""
    return NutritionSupply(
        metabolizable_energy=15.0,
        maintenance_energy=5.0,
        lactation_energy=3.0,
        growth_energy=2.0,
        metabolizable_protein=500.0,
        calcium=90.0,
        phosphorus=45.0,
        dry_matter=8.0,
        wet_matter=10.0,
        ndf_supply=2.0,
        forage_ndf_supply=1.0,
        fat_supply=1.8,
        crude_protein=2.5,
        adf_supply=0.8,
        digestible_energy_supply=14.0,
        tdn_supply=4.0,
        lignin_supply=0.3,
        ash_supply=0.2,
        potassium_supply=0.1,
        starch_supply=1.5,
        byproduct_supply=0.5,
    )


@pytest.fixture
def nutrition_supply_insufficient_protein() -> NutritionSupply:
    """Fixture for insufficient protein supply."""
    return NutritionSupply(
        metabolizable_energy=30.0,
        maintenance_energy=12.0,
        lactation_energy=9.0,
        growth_energy=6.0,
        metabolizable_protein=300.0,
        calcium=120.0,
        phosphorus=55.0,
        dry_matter=12.0,
        wet_matter=15.0,
        ndf_supply=3.0,
        forage_ndf_supply=1.5,
        fat_supply=2.0,
        crude_protein=1.5,
        adf_supply=1.0,
        digestible_energy_supply=28.0,
        tdn_supply=6.0,
        lignin_supply=0.5,
        ash_supply=0.3,
        potassium_supply=0.2,
        starch_supply=2.0,
        byproduct_supply=1.0,
    )


@pytest.fixture
def nutrition_supply_excess_protein() -> NutritionSupply:
    """Fixture for excess protein supply."""
    return NutritionSupply(
        metabolizable_energy=30.0,
        maintenance_energy=12.0,
        lactation_energy=9.0,
        growth_energy=6.0,
        metabolizable_protein=1500.0,
        calcium=120.0,
        phosphorus=55.0,
        dry_matter=12.0,
        wet_matter=15.0,
        ndf_supply=3.0,
        forage_ndf_supply=1.5,
        fat_supply=2.0,
        crude_protein=3.0,
        adf_supply=1.0,
        digestible_energy_supply=28.0,
        tdn_supply=6.0,
        lignin_supply=0.5,
        ash_supply=0.3,
        potassium_supply=0.2,
        starch_supply=2.0,
        byproduct_supply=1.0,
    )


@pytest.mark.parametrize(
    "supply, is_cow, expected_valid",
    [
        (lazy_fixture("nutrition_supply_base"), True, False),
        (lazy_fixture("nutrition_supply_insufficient_energy"), True, False),
        (lazy_fixture("nutrition_supply_insufficient_protein"), True, False),
    ],
)
def test_evaluate_nutrition_supply(
    nutrition_requirements_base: NutritionRequirements, supply: NutritionSupply, is_cow: bool, expected_valid: bool
) -> None:
    is_valid, evaluation = NutritionEvaluator.evaluate_nutrition_supply(nutrition_requirements_base, supply, is_cow)

    assert is_valid == expected_valid

    evaluation_dict = asdict(evaluation)
    for key in [
        "total_energy",
        "maintenance_energy",
        "lactation_energy",
        "growth_energy",
        "metabolizable_protein",
        "calcium",
        "phosphorus",
        "dry_matter",
        "ndf_percent",
        "forage_ndf_percent",
        "fat_percent",
    ]:
        assert key in evaluation_dict


@pytest.mark.parametrize(
    "supply, expected_difference",
    [
        (lazy_fixture("nutrition_supply_base"), -13.0),
        (lazy_fixture("nutrition_supply_insufficient_energy"), -20.0),
    ],
)
def test_calculate_total_energy_supplied(
    nutrition_requirements_base: NutritionRequirements, supply: NutritionSupply, expected_difference: float
) -> None:
    energy_difference = NutritionEvaluator._calculate_total_energy_supplied(nutrition_requirements_base, supply)
    assert energy_difference == pytest.approx(expected_difference, rel=1e-5)


@pytest.mark.parametrize(
    "supply, expected_difference",
    [
        (lazy_fixture("nutrition_supply_base"), 0.0),
        (lazy_fixture("nutrition_supply_insufficient_energy"), -7.0),
    ],
)
def test_calculate_activity_maintenance_energy_supplied(
    nutrition_requirements_base: NutritionRequirements, supply: NutritionSupply, expected_difference: float
) -> None:
    energy_difference = NutritionEvaluator._calculate_activity_maintenance_energy_supplied(
        nutrition_requirements_base, supply
    )
    assert energy_difference == pytest.approx(expected_difference, rel=1e-5)


@pytest.mark.parametrize(
    "supply, expected_difference",
    [
        # Case 1: Lactation energy supplied meets the exact requirement
        (lazy_fixture("nutrition_supply_base"), 1.0),
        # Case 2: Lactation energy supplied is less than required
        (lazy_fixture("nutrition_supply_insufficient_energy"), -5.0),
        # Case 3: No lactation energy required (heifer case)
        (
            lazy_fixture("nutrition_supply_base"),
            1.0,
        ),
    ],
)
def test_calculate_lactation_energy_supplied(
    nutrition_requirements_base: NutritionRequirements, supply: NutritionSupply, expected_difference: float
) -> None:
    energy_difference = NutritionEvaluator._calculate_lactation_energy_supplied(nutrition_requirements_base, supply)
    assert energy_difference == pytest.approx(expected_difference, rel=1e-5)


@pytest.mark.parametrize(
    "supply, expected_difference",
    [
        (lazy_fixture("nutrition_supply_base"), 1.0),
        (lazy_fixture("nutrition_supply_insufficient_energy"), -3.0),
    ],
)
def test_calculate_growth_energy_supplied(
    nutrition_requirements_base: NutritionRequirements, supply: NutritionSupply, expected_difference: float
) -> None:
    energy_difference = NutritionEvaluator._calculate_growth_energy_supplied(nutrition_requirements_base, supply)
    assert energy_difference == pytest.approx(expected_difference, rel=1e-5)


@pytest.mark.parametrize(
    "supply, expected_difference",
    [
        (lazy_fixture("nutrition_supply_base"), 20.0),
        (lazy_fixture("nutrition_supply_insufficient_energy"), -10.0),
    ],
)
def test_calculate_calcium_supplied(
    nutrition_requirements_base: NutritionRequirements, supply: NutritionSupply, expected_difference: float
) -> None:
    calcium_difference = NutritionEvaluator._calculate_calcium_supplied(nutrition_requirements_base, supply)
    assert calcium_difference == pytest.approx(expected_difference, rel=1e-5)


@pytest.mark.parametrize(
    "supply, expected_difference",
    [
        (lazy_fixture("nutrition_supply_base"), 5.0),
        (lazy_fixture("nutrition_supply_insufficient_energy"), -5.0),
    ],
)
def test_calculate_phosphorus_supplied(
    nutrition_requirements_base: NutritionRequirements, supply: NutritionSupply, expected_difference: float
) -> None:
    phosphorus_difference = NutritionEvaluator._calculate_phosphorus_supplied(nutrition_requirements_base, supply)
    assert phosphorus_difference == pytest.approx(expected_difference, rel=1e-5)


@pytest.mark.parametrize(
    "supply, expected_difference",
    [
        (lazy_fixture("nutrition_supply_base"), 0.0),
        (lazy_fixture("nutrition_supply_insufficient_protein"), -300.0),
        (lazy_fixture("nutrition_supply_excess_protein"), 600.0),
    ],
)
def test_calculate_protein_supplied(
    nutrition_requirements_base: NutritionRequirements, supply: NutritionSupply, expected_difference: float
) -> None:
    protein_difference = NutritionEvaluator._calculate_protein_supplied(nutrition_requirements_base, supply)
    assert protein_difference == pytest.approx(expected_difference, rel=1e-5)


@pytest.mark.parametrize(
    "supply, expected_difference",
    [
        (lazy_fixture("nutrition_supply_base"), 0.0),
        # Low NDF case (triggers the first if condition)
        (
            NutritionSupply(
                metabolizable_energy=30.0,
                maintenance_energy=12.0,
                lactation_energy=9.0,
                growth_energy=6.0,
                metabolizable_protein=700.0,
                calcium=120.0,
                phosphorus=55.0,
                dry_matter=12.0,
                wet_matter=15.0,
                ndf_supply=1.0,
                forage_ndf_supply=1.5,
                fat_supply=2.0,
                crude_protein=3.0,
                adf_supply=1.0,
                digestible_energy_supply=28.0,
                tdn_supply=6.0,
                lignin_supply=0.5,
                ash_supply=0.3,
                potassium_supply=0.2,
                starch_supply=2.0,
                byproduct_supply=1.0,
            ),
            -16.6667,
        ),
        # High NDF case (triggers the elif condition)
        (
            NutritionSupply(
                metabolizable_energy=30.0,
                maintenance_energy=12.0,
                lactation_energy=9.0,
                growth_energy=6.0,
                metabolizable_protein=700.0,
                calcium=120.0,
                phosphorus=55.0,
                dry_matter=12.0,
                wet_matter=15.0,
                ndf_supply=8.0,
                forage_ndf_supply=1.5,
                fat_supply=2.0,
                crude_protein=3.0,
                adf_supply=1.0,
                digestible_energy_supply=28.0,
                tdn_supply=6.0,
                lignin_supply=0.5,
                ash_supply=0.3,
                potassium_supply=0.2,
                starch_supply=2.0,
                byproduct_supply=1.0,
            ),
            21.6667,
        ),
        # 0.0 DM case (returns 0.0)
        (
            NutritionSupply(
                metabolizable_energy=30.0,
                maintenance_energy=12.0,
                lactation_energy=9.0,
                growth_energy=6.0,
                metabolizable_protein=700.0,
                calcium=120.0,
                phosphorus=55.0,
                dry_matter=0.0,
                wet_matter=15.0,
                ndf_supply=8.0,
                forage_ndf_supply=1.5,
                fat_supply=2.0,
                crude_protein=3.0,
                adf_supply=1.0,
                digestible_energy_supply=28.0,
                tdn_supply=6.0,
                lignin_supply=0.5,
                ash_supply=0.3,
                potassium_supply=0.2,
                starch_supply=2.0,
                byproduct_supply=1.0,
            ),
            0.0,
        ),
    ],
)
def test_calculate_neutral_detergent_fiber_supplied(
    supply: NutritionSupply,
    expected_difference: float,
    nutrition_requirements_base: NutritionRequirements,
) -> None:
    ndf_difference = NutritionEvaluator._calculate_neutral_detergent_fiber_supplied(nutrition_requirements_base, supply)
    assert ndf_difference == pytest.approx(expected_difference, rel=1e-5)


@pytest.mark.parametrize(
    "supply, expected_difference",
    [
        (lazy_fixture("nutrition_supply_base"), -2.5),
        # Low forage NDF case (forage NDF undershoots the required amount)
        (
            NutritionSupply(
                metabolizable_energy=30.0,
                maintenance_energy=12.0,
                lactation_energy=9.0,
                growth_energy=6.0,
                metabolizable_protein=700.0,
                calcium=120.0,
                phosphorus=55.0,
                dry_matter=12.0,
                wet_matter=15.0,
                ndf_supply=3.0,
                forage_ndf_supply=0.5,
                fat_supply=2.0,
                crude_protein=3.0,
                adf_supply=1.0,
                digestible_energy_supply=28.0,
                tdn_supply=6.0,
                lignin_supply=0.5,
                ash_supply=0.3,
                potassium_supply=0.2,
                starch_supply=2.0,
                byproduct_supply=1.0,
            ),
            -10.8333,
        ),
        # Sufficient forage NDF case (meets the minimum requirement)
        (
            NutritionSupply(
                metabolizable_energy=30.0,
                maintenance_energy=12.0,
                lactation_energy=9.0,
                growth_energy=6.0,
                metabolizable_protein=700.0,
                calcium=120.0,
                phosphorus=55.0,
                dry_matter=12.0,
                wet_matter=15.0,
                ndf_supply=3.0,
                forage_ndf_supply=3.0,
                fat_supply=2.0,
                crude_protein=3.0,
                adf_supply=1.0,
                digestible_energy_supply=28.0,
                tdn_supply=6.0,
                lignin_supply=0.5,
                ash_supply=0.3,
                potassium_supply=0.2,
                starch_supply=2.0,
                byproduct_supply=1.0,
            ),
            10.0,
        ),
        # 0.0 DM (returns 0.0)
        (
            NutritionSupply(
                metabolizable_energy=30.0,
                maintenance_energy=12.0,
                lactation_energy=9.0,
                growth_energy=6.0,
                metabolizable_protein=700.0,
                calcium=120.0,
                phosphorus=55.0,
                dry_matter=0.0,
                wet_matter=15.0,
                ndf_supply=3.0,
                forage_ndf_supply=3.0,
                fat_supply=2.0,
                crude_protein=3.0,
                adf_supply=1.0,
                digestible_energy_supply=28.0,
                tdn_supply=6.0,
                lignin_supply=0.5,
                ash_supply=0.3,
                potassium_supply=0.2,
                starch_supply=2.0,
                byproduct_supply=1.0,
            ),
            0.0,
        ),
    ],
)
def test_calculate_forage_neutral_detergent_fiber_supplied(
    supply: NutritionSupply,
    expected_difference: float,
    nutrition_requirements_base: NutritionRequirements,
) -> None:
    forage_ndf_difference = NutritionEvaluator._calculate_forage_neutral_detergent_fiber_supplied(
        nutrition_requirements_base, supply
    )
    assert forage_ndf_difference == pytest.approx(expected_difference, rel=1e-5)


@pytest.mark.parametrize(
    "supply, expected_difference",
    [
        (lazy_fixture("nutrition_supply_base"), -9.6667),
        # Low fat case (fat supply is below the required amount)
        (
            NutritionSupply(
                metabolizable_energy=30.0,
                maintenance_energy=12.0,
                lactation_energy=9.0,
                growth_energy=6.0,
                metabolizable_protein=700.0,
                calcium=120.0,
                phosphorus=55.0,
                dry_matter=12.0,
                wet_matter=15.0,
                ndf_supply=3.0,
                forage_ndf_supply=1.5,
                fat_supply=0.5,
                crude_protein=3.0,
                adf_supply=1.0,
                digestible_energy_supply=28.0,
                tdn_supply=6.0,
                lignin_supply=0.5,
                ash_supply=0.3,
                potassium_supply=0.2,
                starch_supply=2.0,
                byproduct_supply=1.0,
            ),
            2.83333,
        ),
        # Sufficient fat case (meets the minimum requirement)
        (
            NutritionSupply(
                metabolizable_energy=30.0,
                maintenance_energy=12.0,
                lactation_energy=9.0,
                growth_energy=6.0,
                metabolizable_protein=700.0,
                calcium=120.0,
                phosphorus=55.0,
                dry_matter=12.0,
                wet_matter=15.0,
                ndf_supply=3.0,
                forage_ndf_supply=1.5,
                fat_supply=2.0,
                crude_protein=3.0,
                adf_supply=1.0,
                digestible_energy_supply=28.0,
                tdn_supply=6.0,
                lignin_supply=0.5,
                ash_supply=0.3,
                potassium_supply=0.2,
                starch_supply=2.0,
                byproduct_supply=1.0,
            ),
            -9.6667,
        ),
        # 0.0 DM (0.0 returned)
        (
            NutritionSupply(
                metabolizable_energy=30.0,
                maintenance_energy=12.0,
                lactation_energy=9.0,
                growth_energy=6.0,
                metabolizable_protein=700.0,
                calcium=120.0,
                phosphorus=55.0,
                dry_matter=0.0,
                wet_matter=15.0,
                ndf_supply=3.0,
                forage_ndf_supply=1.5,
                fat_supply=2.0,
                crude_protein=3.0,
                adf_supply=1.0,
                digestible_energy_supply=28.0,
                tdn_supply=6.0,
                lignin_supply=0.5,
                ash_supply=0.3,
                potassium_supply=0.2,
                starch_supply=2.0,
                byproduct_supply=1.0,
            ),
            0.0,
        ),
    ],
)
def test_calculate_fat_supplied(
    supply: NutritionSupply,
    expected_difference: float,
    nutrition_requirements_base: NutritionRequirements,
) -> None:
    fat_difference = NutritionEvaluator._calculate_fat_supplied(nutrition_requirements_base, supply)
    assert fat_difference == pytest.approx(expected_difference, rel=1e-5)


@pytest.mark.parametrize(
    "supply, expected_difference",
    [
        (lazy_fixture("nutrition_supply_base"), 0.0),
        # Low dry matter case (dry matter intake is below the lower limit)
        (
            NutritionSupply(
                metabolizable_energy=30.0,
                maintenance_energy=12.0,
                lactation_energy=9.0,
                growth_energy=6.0,
                metabolizable_protein=700.0,
                calcium=120.0,
                phosphorus=55.0,
                dry_matter=6.0,
                wet_matter=15.0,
                ndf_supply=3.0,
                forage_ndf_supply=1.5,
                fat_supply=2.0,
                crude_protein=3.0,
                adf_supply=1.0,
                digestible_energy_supply=28.0,
                tdn_supply=6.0,
                lignin_supply=0.5,
                ash_supply=0.3,
                potassium_supply=0.2,
                starch_supply=2.0,
                byproduct_supply=1.0,
            ),
            -1.0,
        ),
        # High dry matter case (dry matter intake exceeds the upper limit)
        (
            NutritionSupply(
                metabolizable_energy=30.0,
                maintenance_energy=12.0,
                lactation_energy=9.0,
                growth_energy=6.0,
                metabolizable_protein=700.0,
                calcium=120.0,
                phosphorus=55.0,
                dry_matter=14.0,
                wet_matter=15.0,
                ndf_supply=3.0,
                forage_ndf_supply=1.5,
                fat_supply=2.0,
                crude_protein=3.0,
                adf_supply=1.0,
                digestible_energy_supply=28.0,
                tdn_supply=6.0,
                lignin_supply=0.5,
                ash_supply=0.3,
                potassium_supply=0.2,
                starch_supply=2.0,
                byproduct_supply=1.0,
            ),
            1.0,
        ),
    ],
)
def test_calculate_dry_matter_intake(
    nutrition_requirements_base: NutritionRequirements, supply: NutritionSupply, expected_difference: float
) -> None:
    dry_matter_difference = NutritionEvaluator._calculate_dry_matter_intake(nutrition_requirements_base, supply)
    assert dry_matter_difference == pytest.approx(expected_difference, rel=1e-5)
