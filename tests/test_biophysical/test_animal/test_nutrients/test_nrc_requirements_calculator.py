import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.biophysical.animal.nutrients.nrc_requirements_calculator import NRCRequirementsCalculator
from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements


def test_calculate_requirements(mocker: MockerFixture) -> None:
    """Test that the energy and nutritional requirements of an animal are calculated correctly using NRC methodology."""
    # Arrange
    body_weight: float = 650.0
    mature_body_weight: float = 750.0
    day_of_pregnancy: int | None = 150
    body_condition_score_5: int = 3
    days_in_milk: int | None = 100
    average_daily_gain_heifer: float | None = 0.8
    animal_type: AnimalType = AnimalType.LAC_COW
    parity: int = 2
    calving_interval: int | None = 365
    milk_fat: float = 4.2
    milk_true_protein: float = 3.2
    milk_lactose: float = 4.8
    milk_production: float = 30.0
    housing: str = "Barn"
    distance: float = 500.0
    previous_temperature: float | None = 22.0
    net_energy_diet_concentration: float = 2.1
    days_born: float = 900
    TDN_percentage: float = 65.0
    process_based_phosphorus_requirement: float = 0.45

    mock_calculate_maintenance_energy_requirements = mocker.patch.object(
        NRCRequirementsCalculator, "_calculate_maintenance_energy_requirements", return_value=(10.0, 5.0, 2.0)
    )
    mock_calculate_growth_energy_requirements = mocker.patch.object(
        NRCRequirementsCalculator, "_calculate_growth_energy_requirements", return_value=(8.0, 0.7, 1.5)
    )
    mock_calculate_pregnancy_energy_requirements = mocker.patch.object(
        NRCRequirementsCalculator, "_calculate_pregnancy_energy_requirements", return_value=6.0
    )
    mock_calculate_lactation_energy_requirements = mocker.patch.object(
        NRCRequirementsCalculator, "_calculate_lactation_energy_requirements", return_value=20.0
    )
    mock_calculate_dry_matter_intake = mocker.patch.object(
        NRCRequirementsCalculator, "_calculate_dry_matter_intake", return_value=18.0
    )
    mock_calculate_protein_requirement = mocker.patch.object(
        NRCRequirementsCalculator, "_calculate_protein_requirement", return_value=15.0
    )
    mock_calculate_calcium_requirement = mocker.patch.object(
        NRCRequirementsCalculator, "_calculate_calcium_requirement", return_value=1.2
    )
    mock_calculate_phosphorus_requirement = mocker.patch.object(
        NRCRequirementsCalculator, "_calculate_phosphorus_requirement", return_value=0.8
    )
    mock_calculate_activity_energy_requirements = mocker.patch.object(
        NRCRequirementsCalculator, "_calculate_activity_energy_requirements", return_value=5.0
    )

    # Act
    result: NutritionRequirements = NRCRequirementsCalculator.calculate_requirements(
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
        previous_temperature,
        net_energy_diet_concentration,
        days_born,
        TDN_percentage,
        process_based_phosphorus_requirement,
    )

    # Assert
    mock_calculate_maintenance_energy_requirements.assert_called_once_with(
        body_weight, mature_body_weight, day_of_pregnancy, body_condition_score_5, previous_temperature, animal_type
    )
    mock_calculate_growth_energy_requirements.assert_called_once_with(
        body_weight, mature_body_weight, 5.0, animal_type, parity, calving_interval, average_daily_gain_heifer
    )
    mock_calculate_pregnancy_energy_requirements.assert_called_once_with(day_of_pregnancy, 2.0)
    mock_calculate_lactation_energy_requirements.assert_called_once_with(
        animal_type, milk_fat, milk_true_protein, milk_lactose, milk_production
    )
    mock_calculate_dry_matter_intake.assert_called_once_with(
        animal_type,
        body_weight,
        day_of_pregnancy,
        days_in_milk,
        milk_production,
        milk_fat,
        net_energy_diet_concentration,
        days_born,
    )
    mock_calculate_protein_requirement.assert_called_once_with(
        body_weight,
        5.0,
        day_of_pregnancy,
        animal_type,
        milk_production,
        milk_true_protein,
        2.0,
        8.0,
        0.7,
        1.5,
        18.0,
        TDN_percentage,
    )
    mock_calculate_calcium_requirement.assert_called_once_with(
        body_weight, mature_body_weight, day_of_pregnancy, animal_type, 0.7, milk_production
    )
    mock_calculate_phosphorus_requirement.assert_called_once_with(
        body_weight, mature_body_weight, day_of_pregnancy, milk_production, animal_type, 0.7, 18.0
    )
    mock_calculate_activity_energy_requirements.assert_called_once_with(body_weight, housing, distance)

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
    assert result.essential_amino_acids == EssentialAminoAcidRequirements(
        histidine=0.0,
        isoleucine=0.0,
        leucine=0.0,
        lysine=0.0,
        methionine=0.0,
        phenylalanine=0.0,
        threonine=0.0,
        thryptophan=0.0,
        valine=0.0,
    )


@pytest.mark.parametrize(
    "body_weight, mature_body_weight, day_of_pregnancy, body_condition_score_5, previous_temperature, animal_type, "
    "expected_energy, expected_conceptus_weight, expected_calf_birth_weight",
    [
        # Test case 1: Non-pregnant animal
        (600.0, 650.0, None, 3, None, AnimalType.LAC_COW, 9.6984, 0.0, 0.0),
        # Test case 2: Pregnant animal (Day 200 of pregnancy)
        (600.0, 650.0, 200, 3, 15.0, AnimalType.LAC_COW, 9.42633, 22.3424, 40.7875),
        # Test case 3: Pregnant heifer (Day 200, different body condition score)
        (500.0, 600.0, 200, 4, 10.0, AnimalType.HEIFER_II, 9.6986, 20.6238, 37.65),
    ],
)
def test_calculate_maintenance_energy_requirements(
    body_weight: float,
    mature_body_weight: float,
    day_of_pregnancy: int | None,
    body_condition_score_5: int,
    previous_temperature: float | None,
    animal_type: AnimalType,
    expected_energy: float,
    expected_conceptus_weight: float,
    expected_calf_birth_weight: float,
) -> None:
    """Test that maintenance energy requirements are calculated correctly."""
    assert NRCRequirementsCalculator._calculate_maintenance_energy_requirements(
        body_weight, mature_body_weight, day_of_pregnancy, body_condition_score_5, previous_temperature, animal_type
    ) == pytest.approx((expected_energy, expected_conceptus_weight, expected_calf_birth_weight), rel=1e-5)


@pytest.mark.parametrize(
    "body_weight, mature_body_weight, conceptus_weight, animal_type, parity, calving_interval, "
    "average_daily_gain_heifer, expected_energy, expected_avg_daily_gain, expected_shrunk_body_weight",
    [
        # Test case 1: Lactating cow, first parity, calving interval 400 days
        (600.0, 650.0, 0.0, AnimalType.LAC_COW, 1, 400, None, 0.695, 0.156, 393.1),
        # Test case 2: Heifer I with specified average daily gain
        (500.0, 700.0, 0.0, AnimalType.HEIFER_I, 0, None, 900.0, 7665.2, 900.0, 304.2),
        # Test case 3: Heifer II with specified average daily gain
        (550.0, 680.0, 0.0, AnimalType.HEIFER_II, 0, None, 850.0, 7902.7, 850.0, 344.5),
        # Test case 4: Lactating cow, second parity, valid calving interval (parity == 2 branch)
        (600.0, 650.0, 0.0, AnimalType.LAC_COW, 2, 450, None, 0.478, 0.1109, 393.1),
        # Test case 5: Lactating cow, second parity, zero calving interval (parity == 2 but calving_interval == 0)
        (600.0, 650.0, 0.0, AnimalType.LAC_COW, 2, 0, None, 0.0, 0.0, 393.1),
        # Test case 6: Dry cow, should result in avg_daily_gain = 0.0
        (600.0, 650.0, 0.0, AnimalType.DRY_COW, 0, None, None, 0.0, 0.0, 393.1),
    ],
)
def test_calculate_growth_energy_requirements(
    body_weight: float,
    mature_body_weight: float,
    conceptus_weight: float,
    animal_type: AnimalType,
    parity: int,
    calving_interval: int | None,
    average_daily_gain_heifer: float | None,
    expected_energy: float,
    expected_avg_daily_gain: float,
    expected_shrunk_body_weight: float,
) -> None:
    """Test that growth energy requirements are calculated correctly."""
    assert NRCRequirementsCalculator._calculate_growth_energy_requirements(
        body_weight,
        mature_body_weight,
        conceptus_weight,
        animal_type,
        parity,
        calving_interval,
        average_daily_gain_heifer,
    ) == pytest.approx((expected_energy, expected_avg_daily_gain, expected_shrunk_body_weight), rel=1e-3)


@pytest.mark.parametrize(
    "day_of_pregnancy, calf_birth_weight, expected_energy",
    [
        # Test case 1: No pregnancy (None value for day_of_pregnancy)
        (None, 40.0, 0.0),
        # Test case 2: Early pregnancy (before 190 days)
        (150, 40.0, 0.0),
        # Test case 3: Pregnancy at 200 days
        (200, 40.0, 2.4413),
        # Test case 4: Pregnancy at 250 days
        (250, 45.0, 3.4733),
        # Test case 5: Pregnancy at 280 days (near full term)
        (280, 50.0, 4.3438),
    ],
)
def test_calculate_pregnancy_energy_requirements(
    day_of_pregnancy: int | None, calf_birth_weight: float, expected_energy: float
) -> None:
    """Test that pregnancy energy requirements are calculated correctly."""
    result = NRCRequirementsCalculator._calculate_pregnancy_energy_requirements(day_of_pregnancy, calf_birth_weight)

    assert result == pytest.approx(expected_energy, rel=1e-3)


@pytest.mark.parametrize(
    "body_weight, conceptus_weight, day_of_pregnancy, animal_type, milk_production, milk_true_protein, "
    "calf_birth_weight, net_energy_growth, average_daily_gain, equivalent_shrunk_body_weight, "
    "dry_matter_intake_estimate, TDN_conc, expected_protein",
    [
        # Test case 1: Non-lactating, non-pregnant animal (dry cow)
        (600.0, 0.0, None, AnimalType.DRY_COW, 0.0, 0.0, 0.0, 0.0, 0.0, 400.0, 20.0, 0.7, 627.7565),
        # Test case 2: Lactating cow, not pregnant
        (600.0, 0.0, None, AnimalType.LAC_COW, 30.0, 3.2, 0.0, 5.0, 0.5, 450.0, 22.0, 0.7, 2071.4334),
        # Test case 3: Pregnant cow at 200 days, lactating
        (650.0, 10.0, 200, AnimalType.LAC_COW, 25.0, 3.5, 45.0, 6.0, 0.8, 460.0, 25.0, 0.7, 2397.1431),
        # Test case 4: Heifer at 250 days of pregnancy, not lactating
        (500.0, 8.0, 250, AnimalType.HEIFER_II, 0.0, 0.0, 42.0, 4.0, 0.6, 380.0, 18.0, 0.7, 965.3124),
        # Test case 5: Near-term pregnancy at 280 days, lactating cow
        (700.0, 12.0, 280, AnimalType.LAC_COW, 28.0, 3.8, 50.0, 7.0, 0.9, 470.0, 26.0, 0.7, 2914.3608),
        # Test case 6: Near-term pregnancy, non-lactating dry cow
        (650.0, 10.0, 280, AnimalType.DRY_COW, 0.0, 0.0, 48.0, 5.5, 0.7, 390.0, 21.0, 0.7, 1124.5907),
        # Test case 7: lactating cow
        (700.0, 12.0, 180, AnimalType.LAC_COW, 28.0, 3.8, 50.0, 7.0, 0.9, 479.0, 26.0, 0.7, 2500.5975),
    ],
)
def test_calculate_protein_requirement(
    body_weight: float,
    conceptus_weight: float,
    day_of_pregnancy: int | None,
    animal_type: AnimalType,
    milk_production: float,
    milk_true_protein: float,
    calf_birth_weight: float,
    net_energy_growth: float,
    average_daily_gain: float,
    equivalent_shrunk_body_weight: float,
    dry_matter_intake_estimate: float,
    TDN_conc: float | None,
    expected_protein: float,
) -> None:
    """Test that metabolizable protein requirements are correctly calculated."""

    result = NRCRequirementsCalculator._calculate_protein_requirement(
        body_weight,
        conceptus_weight,
        day_of_pregnancy,
        animal_type,
        milk_production,
        milk_true_protein,
        calf_birth_weight,
        net_energy_growth,
        average_daily_gain,
        equivalent_shrunk_body_weight,
        dry_matter_intake_estimate,
        TDN_conc,
    )

    assert result == pytest.approx(expected_protein, rel=1e-3)


@pytest.mark.parametrize(
    "body_weight, mature_body_weight, day_of_pregnancy, animal_type, average_daily_gain, milk_production,"
    "expected_calcium",
    [
        # Test case 1: Lactating cow, not pregnant
        (600.0, 650.0, None, AnimalType.LAC_COW, 0.8, 30.0, 64.0171),
        # Test case 2: Lactating cow, pregnant at 200 days
        (650.0, 700.0, 200, AnimalType.LAC_COW, 1.0, 28.0, 68.1289),
        # Test case 3: Dry cow, not pregnant
        (550.0, 600.0, None, AnimalType.DRY_COW, 0.6, 0.0, 15.1724),
        # Test case 4: Dry cow, pregnant at 250 days
        (580.0, 620.0, 250, AnimalType.DRY_COW, 0.5, 0.0, 21.9178),
        # Test case 5: Heifer, not pregnant
        (400.0, 500.0, None, AnimalType.HEIFER_II, 1.2, 0.0, 19.3857),
        # Test case 6: Heifer, pregnant at 280 days
        (420.0, 510.0, 280, AnimalType.HEIFER_III, 1.0, 0.0, 27.7713),
        # Test case 7: Lac cow, pregnant at 150 days
        (420.0, 510.0, 150, AnimalType.LAC_COW, 1.0, 0.0, 24.0424),
    ],
)
def test_calculate_calcium_requirement(
    body_weight: float,
    mature_body_weight: float,
    day_of_pregnancy: int | None,
    animal_type: AnimalType,
    average_daily_gain: float,
    milk_production: float,
    expected_calcium: float,
) -> None:
    """Test that calcium requirements are correctly calculated."""

    result = NRCRequirementsCalculator._calculate_calcium_requirement(
        body_weight, mature_body_weight, day_of_pregnancy, animal_type, average_daily_gain, milk_production
    )

    assert result == pytest.approx(expected_calcium, rel=1e-3)


@pytest.mark.parametrize(
    "body_weight, mature_body_weight, day_of_pregnancy, milk_production, animal_type, average_daily_gain, "
    "dry_matter_intake_estimate, expected_phosphorus",
    [
        # Test case 1: Lactating cow, not pregnant
        (600.0, 650.0, None, 30.0, AnimalType.LAC_COW, 0.8, 22.0, 55.1311),
        # Test case 2: Lactating cow, pregnant at 200 days
        (650.0, 700.0, 200, 28.0, AnimalType.LAC_COW, 1.0, 24.0, 58.8173),
        # Test case 3: Dry cow, not pregnant
        (550.0, 600.0, None, 0.0, AnimalType.DRY_COW, 0.6, 20.0, 20.8028),
        # Test case 4: Dry cow, pregnant at 250 days
        (580.0, 620.0, 250, 0.0, AnimalType.DRY_COW, 0.5, 21.0, 25.5116),
        # Test case 5: Heifer, not pregnant
        (400.0, 500.0, None, 0.0, AnimalType.HEIFER_II, 1.2, 18.0, 22.7852),
        # Test case 6: Heifer, pregnant at 280 days
        (420.0, 510.0, 280, 0.0, AnimalType.HEIFER_III, 1.0, 19.0, 27.6740),
        # Test case 7: Lactating cow, pregnant at 150 days
        (650.0, 700.0, 150, 28.0, AnimalType.LAC_COW, 1.0, 24.0, 56.6574),
    ],
)
def test_calculate_phosphorus_requirement(
    body_weight: float,
    mature_body_weight: float,
    day_of_pregnancy: int | None,
    milk_production: float,
    animal_type: AnimalType,
    average_daily_gain: float,
    dry_matter_intake_estimate: float,
    expected_phosphorus: float,
) -> None:
    """Test that phosphorus requirements are correctly calculated."""

    result = NRCRequirementsCalculator._calculate_phosphorus_requirement(
        body_weight,
        mature_body_weight,
        day_of_pregnancy,
        milk_production,
        animal_type,
        average_daily_gain,
        dry_matter_intake_estimate,
    )

    assert result == pytest.approx(expected_phosphorus, rel=1e-3)


@pytest.mark.parametrize(
    "animal_type, body_weight, day_of_pregnancy, days_in_milk, milk_production, milk_fat, "
    "net_energy_diet_concentration, days_born, expected_dmi",
    [
        # Test case 1: Lactating cow, mid-lactation
        (AnimalType.LAC_COW, 600.0, 150, 100, 30.0, 3.5, 1.2, None, 21.35),
        # Test case 2: Lactating cow, early lactation
        (AnimalType.LAC_COW, 650.0, 120, 30, 28.0, 4.0, 1.3, None, 17.9110),
        # Test case 3: Dry cow, not pregnant
        (AnimalType.DRY_COW, 550.0, 150, None, 0.0, 0.0, 1.1, None, 10.8349),
        # Test case 4: Dry cow, late pregnancy
        (AnimalType.DRY_COW, 580.0, 250, None, 0.0, 0.0, 1.0, None, 11.3902),
        # Test case 5: Heifer over 1 year old
        (AnimalType.HEIFER_II, 400.0, None, None, 0.0, 0.0, 1.2, 500, 8.3700),
        # Test case 6: Heifer under 1 year old
        (AnimalType.HEIFER_I, 300.0, None, None, 0.0, 0.0, 0.9, 300, 7.7675),
        # Test case 7: Heifer in late pregnancy
        (AnimalType.HEIFER_III, 420.0, 280, None, 0.0, 0.0, 1.1, 450, 7.4965),
    ],
)
def test_calculate_dry_matter_intake(
    animal_type: AnimalType,
    body_weight: float,
    day_of_pregnancy: int,
    days_in_milk: int | None,
    milk_production: float,
    milk_fat: float,
    net_energy_diet_concentration: float,
    days_born: float,
    expected_dmi: float,
) -> None:
    """Test that dry matter intake is correctly calculated."""

    result = NRCRequirementsCalculator._calculate_dry_matter_intake(
        animal_type,
        body_weight,
        day_of_pregnancy,
        days_in_milk,
        milk_production,
        milk_fat,
        net_energy_diet_concentration,
        days_born,
    )

    assert result == pytest.approx(expected_dmi, rel=1e-3)


@pytest.mark.parametrize(
    "body_weight, housing, distance, expected_energy",
    [
        # Test case 1: Barn-housed animal, minimal walking
        (600.0, "Barn", 100, 0.027),
        # Test case 2: Barn-housed animal, moderate walking
        (650.0, "Barn", 500, 0.14625),
        # Test case 3: Barn-housed animal, extensive walking
        (700.0, "Barn", 1000, 0.315),
        # Test case 4: Grazing animal, minimal walking
        (600.0, "Grazing", 100, 0.747),
        # Test case 5: Grazing animal, moderate walking
        (650.0, "Grazing", 500, 0.9262),
        # Test case 6: Grazing animal, extensive walking
        (700.0, "Grazing", 1000, 1.155),
    ],
)
def test_calculate_activity_energy_requirements(
    body_weight: float, housing: str, distance: float, expected_energy: float
) -> None:
    """Test that activity energy requirements are correctly calculated."""

    result = NRCRequirementsCalculator._calculate_activity_energy_requirements(body_weight, housing, distance)

    assert result == pytest.approx(expected_energy, rel=1e-3)
