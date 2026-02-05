from typing import Optional
import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.biophysical.animal.nutrients.nasem_requirements_calculator import (
    AMINO_ACID_CALCULATOR,
    NASEMRequirementsCalculator,
)
from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements


def test_calculate_requirements(mocker: MockerFixture) -> None:
    """Test that the energy and nutritional requirements of an animal are calculated correctly."""
    # Arrange
    body_weight: float = 650.0
    mature_body_weight: float = 750.0
    day_of_pregnancy: Optional[int] = 150
    body_condition_score_5: int = 3
    days_in_milk: Optional[int] = 100
    average_daily_gain_heifer: Optional[float] = 0.8
    animal_type: AnimalType = AnimalType.LAC_COW
    parity: int = 2
    calving_interval: Optional[int] = 365
    milk_fat: float = 4.2
    milk_true_protein: float = 3.2
    milk_lactose: float = 4.8
    milk_production: float = 30.0
    housing: str = "Barn"
    distance: float = 500.0
    lactating: bool = True
    ndf_percentage: float = 35.0
    process_based_phosphorus_requirement: float = 0.45

    mock_calculate_maintenance_energy_requirements = mocker.patch.object(
        NASEMRequirementsCalculator, "_calculate_maintenance_energy_requirements", return_value=(10.0, 5.0, 2.0)
    )
    mock_calculate_growth_energy_requirements = mocker.patch.object(
        NASEMRequirementsCalculator, "_calculate_growth_energy_requirements", return_value=(8.0, 0.7, 1.5)
    )
    mock_calculate_pregnancy_energy_requirements = mocker.patch.object(
        NASEMRequirementsCalculator, "_calculate_pregnancy_energy_requirements", return_value=(6.0, 1.2)
    )
    mock_calculate_lactation_energy_requirements = mocker.patch.object(
        NASEMRequirementsCalculator, "_calculate_lactation_energy_requirements", return_value=20.0
    )
    mock_calculate_dry_matter_intake = mocker.patch.object(
        NASEMRequirementsCalculator, "_calculate_dry_matter_intake", return_value=18.0
    )
    mock_calculate_protein_requirement = mocker.patch.object(
        NASEMRequirementsCalculator, "_calculate_protein_requirement", return_value=15.0
    )
    mock_calculate_calcium_requirement = mocker.patch.object(
        NASEMRequirementsCalculator, "_calculate_calcium_requirement", return_value=1.2
    )
    mock_calculate_phosphorus_requirement = mocker.patch.object(
        NASEMRequirementsCalculator, "_calculate_phosphorus_requirement", return_value=0.8
    )
    mock_calculate_activity_energy_requirements = mocker.patch.object(
        NASEMRequirementsCalculator, "_calculate_activity_energy_requirements", return_value=5.0
    )
    mock_calculate_essential_amino_acid_requirements = mocker.patch.object(
        AMINO_ACID_CALCULATOR,
        "calculate_essential_amino_acid_requirements",
        return_value=(
            mock_eaa_requirements := EssentialAminoAcidRequirements(
                histidine=2.0,
                isoleucine=2.0,
                leucine=2.0,
                lysine=2.0,
                methionine=2.0,
                phenylalanine=2.0,
                threonine=2.0,
                thryptophan=2.0,
                valine=2.0,
            )
        ),
    )

    # Act
    result: NutritionRequirements = NASEMRequirementsCalculator.calculate_requirements(
        body_weight,
        mature_body_weight,
        day_of_pregnancy,
        body_condition_score_5,
        days_in_milk,
        average_daily_gain_heifer,
        animal_type,
        parity,
        calving_interval,
        milk_fat,
        milk_true_protein,
        milk_lactose,
        milk_production,
        housing,
        distance,
        lactating,
        ndf_percentage,
        process_based_phosphorus_requirement,
    )

    # Assert
    mock_calculate_maintenance_energy_requirements.assert_called_once_with(
        body_weight, mature_body_weight, day_of_pregnancy, days_in_milk
    )
    mock_calculate_growth_energy_requirements.assert_called_once_with(
        body_weight, mature_body_weight, average_daily_gain_heifer, animal_type, parity, calving_interval
    )
    mock_calculate_pregnancy_energy_requirements.assert_called_once_with(
        lactating, day_of_pregnancy, days_in_milk, 5.0, 2.0
    )
    mock_calculate_lactation_energy_requirements.assert_called_once_with(
        animal_type, milk_fat, milk_true_protein, milk_lactose, milk_production
    )
    mock_calculate_dry_matter_intake.assert_called_once_with(
        body_weight, mature_body_weight, days_in_milk, lactating, 20.0, parity, body_condition_score_5, ndf_percentage
    )
    mock_calculate_protein_requirement.assert_called_once_with(
        lactating, body_weight, 1.5, 1.2, 18.0, milk_true_protein, milk_production, ndf_percentage
    )
    mock_calculate_calcium_requirement.assert_called_once_with(
        body_weight, mature_body_weight, day_of_pregnancy, 0.7, 18.0, milk_true_protein, milk_production, parity
    )
    mock_calculate_phosphorus_requirement.assert_called_once_with(
        body_weight,
        mature_body_weight,
        animal_type,
        day_of_pregnancy,
        0.7,
        18.0,
        milk_true_protein,
        milk_production,
        parity,
    )
    mock_calculate_activity_energy_requirements.assert_called_once_with(body_weight, housing, distance)
    mock_calculate_essential_amino_acid_requirements.assert_called_once_with(
        animal_type=animal_type,
        lactating=lactating,
        body_weight=body_weight,
        frame_weight_gain=1.5,
        gravid_uterine_weight_gain=1.2,
        dry_matter_intake_estimate=18.0,
        milk_true_protein=milk_true_protein,
        milk_production=milk_production,
        NDF_conc=ndf_percentage,
    )

    assert isinstance(result, NutritionRequirements)
    assert result.maintenance_energy == 10.0
    assert result.growth_energy == 8.0
    assert result.pregnancy_energy == 6.0
    assert result.lactation_energy == 20.0
    assert result.metabolizable_protein == 15.0
    assert result.calcium == 1.2
    assert result.phosphorus == 0.8
    assert result.process_based_phosphorus == process_based_phosphorus_requirement
    assert result.dry_matter == 18.0
    assert result.activity_energy == 5.0
    assert result.essential_amino_acids == mock_eaa_requirements


@pytest.mark.parametrize(
    "body_weight, mature_body_weight, day_of_pregnancy, days_in_milk, expected_energy, expected_gravid_uterine_weight,"
    "expected_uterine_weight",
    [
        # Test case 1: Non-pregnant, non-lactating animal
        (600.0, 650.0, None, None, 12.1231, 0.0, 0.0),
        # Test case 2: Pregnant animal (Day 200 of pregnancy), not lactating
        (600.0, 650.0, 200, None, 11.74071, 15.7676, 9.3322),
        # Test case 3: Pregnant and lactating animal (Day 200, 100 days in milk)
        (600.0, 650.0, 200, 100, 11.88025, 15.76758, 0.2040),
    ],
)
def test_calculate_maintenance_energy_requirements(
    body_weight: float,
    mature_body_weight: float,
    day_of_pregnancy: int | None,
    days_in_milk: int | None,
    expected_energy: float,
    expected_gravid_uterine_weight: float,
    expected_uterine_weight: float,
) -> None:
    assert NASEMRequirementsCalculator._calculate_maintenance_energy_requirements(
        body_weight, mature_body_weight, day_of_pregnancy, days_in_milk
    ) == pytest.approx((expected_energy, expected_gravid_uterine_weight, expected_uterine_weight), rel=1e-5)


@pytest.mark.parametrize(
    "body_weight, mature_body_weight, average_daily_gain_heifer, animal_type, parity, calving_interval, "
    "expected_energy, expected_avg_daily_gain, expected_frame_weight_gain",
    [
        # Test case 1: Lactating cow, first parity, calving interval 400 days
        (600.0, 650.0, None, AnimalType.LAC_COW, 1, 400, 0.9965, 0.156, 0.4585),
        # Test case 2: Heifer I with specified average daily gain
        (500.0, 700.0, 900.0, AnimalType.HEIFER_I, 0, None, 4943.7811, 900.0, 0.4063),
        # Test case 3: Heifer II with specified average daily gain
        (550.0, 680.0, 850.0, AnimalType.HEIFER_II, 0, None, 5013.4942, 850.0, 0.4299),
        # Test case 4: Lactating cow, second parity, valid calving interval (parity == 2 branch)
        (600.0, 650.0, None, AnimalType.LAC_COW, 2, 450, 0.7086, 0.1109, 0.4585),
        # Test case 5: Lactating cow, second parity, zero calving interval (parity == 2 but calving_interval == 0)
        (600.0, 650.0, None, AnimalType.LAC_COW, 2, 0, 0.0, 0.00001, 0.0),
        # Test case 6: Animal type not in specified categories, should result in avg_daily_gain = 0.0
        (600.0, 650.0, None, AnimalType.DRY_COW, 0, None, 0.0, 0.00001, 0.0),
        # Test case 6: Animal type not in specified categories, should result in avg_daily_gain = 0.0
        (600.0, 650.0, None, AnimalType.CALF, 0, None, 0.0, 0.00001, 0.0),
    ],
)
def test_calculate_growth_energy_requirements(
    body_weight: float,
    mature_body_weight: float,
    average_daily_gain_heifer: float | None,
    animal_type: AnimalType,
    parity: int,
    calving_interval: int | None,
    expected_energy: float,
    expected_avg_daily_gain: float,
    expected_frame_weight_gain: float,
) -> None:
    assert NASEMRequirementsCalculator._calculate_growth_energy_requirements(
        body_weight, mature_body_weight, average_daily_gain_heifer, animal_type, parity, calving_interval
    ) == pytest.approx((expected_energy, expected_avg_daily_gain, expected_frame_weight_gain), rel=1e-3)


@pytest.mark.parametrize(
    "lactating, day_of_pregnancy, days_in_milk, gravid_uterine_weight, uterine_weight, expected_energy,"
    "expected_weight_gain",
    [
        # Test case 1: Lactating animal with valid days in milk
        (True, None, 150, 30.0, 5.0, 0.0, 0.0),
        # Test case 2: Non-lactating animal, pregnant at day 200
        (False, 200, None, 30.0, 5.0, 2.419956, 0.582),
        # Test case 3: Non-lactating animal, not pregnant
        (False, None, None, 30.0, 5.0, 0.0, 0.0),
        # Test case 4: Lactating animal, no day_of_pregnancy, DIM < 100
        (True, None, 50, 30.0, 5.0, -302.148, -47.96),
    ],
)
def test_calculate_pregnancy_energy_requirements(
    lactating: bool,
    day_of_pregnancy: int | None,
    days_in_milk: int | None,
    gravid_uterine_weight: float,
    uterine_weight: float,
    expected_energy: float,
    expected_weight_gain: float,
) -> None:
    """Test that energy requirements for pregnancy are calculated correctly."""
    assert NASEMRequirementsCalculator._calculate_pregnancy_energy_requirements(
        lactating, day_of_pregnancy, days_in_milk, gravid_uterine_weight, uterine_weight
    ) == pytest.approx((expected_energy, expected_weight_gain), rel=1e-5)


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
