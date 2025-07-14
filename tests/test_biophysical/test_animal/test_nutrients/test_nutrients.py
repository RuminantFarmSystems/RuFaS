from unittest.mock import MagicMock
import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.nutrients.nutrients import Nutrients
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.general_constants import GeneralConstants


def test_perform_daily_phosphorus_update(mocker: MockerFixture) -> None:
    """Tests that daily phosphorus update is performed correctly."""

    # Arrange
    mock_nutrient_inputs = MagicMock()
    nutrients = Nutrients()

    mock_calc_phosphorus_requirements = mocker.patch.object(
        nutrients, "_calculate_phosphorus_requirements", return_value=None
    )
    mock_calc_total_phosphorus = mocker.patch.object(nutrients, "_calculate_total_animal_phosphorus", return_value=None)

    # Act
    nutrients.perform_daily_phosphorus_update(mock_nutrient_inputs)

    # Assert
    mock_calc_phosphorus_requirements.assert_called_once_with(mock_nutrient_inputs)
    mock_calc_total_phosphorus.assert_called_once()


def test_set_dry_matter_intake() -> None:
    """Tests that dry matter intake is set correctly."""
    expected = 10.0
    nutrients = Nutrients()
    nutrients.set_dry_matter_intake(10.0)
    assert nutrients._dry_matter_intake == expected


def test_set_phosphorus_intake() -> None:
    """Tests that dry matter intake is set correctly."""
    expected = 10.0
    nutrients = Nutrients()
    nutrients.set_phosphorus_intake(10.0)
    assert nutrients.phosphorus_intake == expected


@pytest.mark.parametrize(
    "phosphorus_intake, phosphorus_requirement, phosphorus_reserves, phosphorus_for_gestation, phosphorus_for_growth, "
    "expected_excess, expected_reserves, expected_total_phosphorus",
    [
        # Test case 1: Intake equals requirement, reserves start at 0
        (50.0, 50.0, 0.0, 2.0, 3.0, 0.0, 0.0, 5.0),
        # Test case 2: Intake greater than requirement, reserves >= 0
        (60.0, 50.0, 5.0, 2.0, 3.0, 10.0, 0.0, 0.0),
        # Test case 3: Intake greater than requirement, reserves < 0
        (60.0, 50.0, -5.0, 2.0, 3.0, 10.0, 2.0, 12.0),
        # Test case 4: Intake less than requirement, reserves start at 10
        (40.0, 50.0, 10.0, 2.0, 3.0, 0.0, 0.0, -5.0),
        # Test case 5: Intake less than requirement, reserves start at -10
        (40.0, 50.0, -10.0, 2.0, 3.0, 0.0, -20.0, -5.0),
        # Test case 6: Intake equals requirement, reserves < 0
        (50.0, 50.0, -5.0, 2.0, 3.0, 0.0, -5.0, 5.0),
    ],
)
def test_calculate_total_animal_phosphorus(
    phosphorus_intake: float,
    phosphorus_requirement: float,
    phosphorus_reserves: float,
    phosphorus_for_gestation: float,
    phosphorus_for_growth: float,
    expected_excess: float,
    expected_reserves: float,
    expected_total_phosphorus: float,
) -> None:
    """Test that total phosphorus in the animal is calculated correctly."""

    # Arrange
    nutrients = Nutrients()
    nutrients.phosphorus_intake = phosphorus_intake
    nutrients.phosphorus_requirement = phosphorus_requirement
    nutrients.phosphorus_reserves = phosphorus_reserves
    nutrients.phosphorus_for_gestation = phosphorus_for_gestation
    nutrients.phosphorus_for_growth = phosphorus_for_growth
    nutrients.total_phosphorus_in_animal = 0.0

    # Act
    nutrients._calculate_total_animal_phosphorus()

    # Assert
    assert nutrients.phosphorus_excess_in_diet == expected_excess
    assert nutrients.phosphorus_reserves == expected_reserves
    assert nutrients.total_phosphorus_in_animal == pytest.approx(expected_total_phosphorus, rel=1e-3)


@pytest.mark.parametrize(
    "is_cow, dry_matter_intake, expected_loss",
    [
        # Test case 1: Animal is a cow
        (True, 20.0, 20.0),
        # Test case 2: Animal is not a cow
        (False, 20.0, 16.0),
        # Test case 3: Zero dry matter intake for cow
        (True, 0.0, 0.0),
        # Test case 4: Zero dry matter intake for non-cow
        (False, 0.0, 0.0),
        # Test case 5: High dry matter intake for cow
        (True, 50.0, 50.0),
        # Test case 6: High dry matter intake for non-cow
        (False, 50.0, 40.0),
    ],
)
def test_calculate_phosphorus_endogenous_loss(is_cow: bool, dry_matter_intake: float, expected_loss: float) -> None:
    """Test that phosphorus required for endogenous loss is correctly calculated."""

    # Arrange
    nutrients = Nutrients()
    mock_nutrient_inputs = MagicMock()
    mock_nutrient_inputs.animal_type.is_cow = is_cow
    nutrients._dry_matter_intake = dry_matter_intake

    # Act
    result = nutrients._calculate_phosphorus_endogenous_loss(mock_nutrient_inputs)

    # Assert
    assert result == pytest.approx(expected_loss, rel=1e-3)


@pytest.mark.parametrize(
    "body_weight, endogenous_loss, growth_phosphorus, gestational_phosphorus, milk_phosphorus, absorbed_phosphorus,"
    "expected_requirement",
    [
        # Test case 1: Standard phosphorus requirements
        (600.0, 15.0, 10.0, 5.0, 8.0, 20.0, 25.0),
        # Test case 2: Higher body weight, increased phosphorus needs
        (750.0, 18.0, 12.0, 6.5, 9.5, 22.5, 28.0),
        # Test case 3: Low body weight, lower phosphorus needs
        (450.0, 12.0, 7.5, 3.0, 5.0, 15.0, 18.0),
        # Test case 4: No phosphorus for growth, lactation, or gestation
        (500.0, 14.0, 0.0, 0.0, 0.0, 10.0, 10.0),
        # Test case 5: High phosphorus for gestation and growth
        (650.0, 16.0, 15.0, 8.0, 12.0, 30.0, 35.0),
    ],
)
def test_calculate_phosphorus_requirements(
    body_weight: float,
    endogenous_loss: float,
    growth_phosphorus: float,
    gestational_phosphorus: float,
    milk_phosphorus: float,
    absorbed_phosphorus: float,
    expected_requirement: float,
    mocker: MockerFixture,
) -> None:
    """Test that phosphorus requirements are correctly calculated."""

    # Arrange
    nutrients = Nutrients()
    nutrients._dry_matter_intake = 10.0
    mock_nutrient_inputs = MagicMock()
    mock_nutrient_inputs.body_weight = body_weight

    # Patch methods

    mock_endogenous_loss = mocker.patch.object(
        nutrients, "_calculate_phosphorus_endogenous_loss", return_value=endogenous_loss
    )
    mock_growth_phosphorus = mocker.patch.object(
        nutrients, "_calculate_phosphorus_for_growth", return_value=growth_phosphorus
    )
    mock_gestational_phosphorus = mocker.patch.object(
        nutrients, "_calculate_gestational_phosphorus", return_value=gestational_phosphorus
    )
    mock_milk_phosphorus = mocker.patch.object(nutrients, "_calculate_milk_phosphorus", return_value=milk_phosphorus)
    mock_absorbed_phosphorus = mocker.patch.object(
        nutrients, "_calculate_absorbed_phosphorus", return_value=absorbed_phosphorus
    )
    mock_animal_phosphorus_requirement = mocker.patch.object(
        nutrients, "_calculate_animal_phosphorus_requirement", return_value=expected_requirement
    )

    # Act
    nutrients._calculate_phosphorus_requirements(mock_nutrient_inputs)

    # Assert
    mock_endogenous_loss.assert_called_once_with(mock_nutrient_inputs)
    assert nutrients.phosphorus_endogenous_loss == endogenous_loss

    mock_growth_phosphorus.assert_called_once_with(mock_nutrient_inputs)
    assert nutrients.phosphorus_for_growth == growth_phosphorus

    mock_gestational_phosphorus.assert_called_once_with(mock_nutrient_inputs)
    assert nutrients.phosphorus_for_gestation == gestational_phosphorus
    assert nutrients.phosphorus_for_gestation_required_for_calf == gestational_phosphorus

    mock_milk_phosphorus.assert_called_once_with(mock_nutrient_inputs)

    mock_absorbed_phosphorus.assert_called_once_with(
        mock_nutrient_inputs, milk_phosphorus, 0.000002 * body_weight * GeneralConstants.KG_TO_GRAMS
    )

    mock_animal_phosphorus_requirement.assert_called_once_with(mock_nutrient_inputs, absorbed_phosphorus)
    assert nutrients.phosphorus_requirement == expected_requirement


@pytest.mark.parametrize(
    "is_cow, body_weight, mature_body_weight, daily_growth, expected_growth_phosphorus",
    [
        # Test case 1: Heifer with growth (not a cow)
        (False, 400.0, 600.0, 0.8, 5.2228),
        # Test case 2: Growing heifer (below mature body weight)
        (True, 500.0, 700.0, 1.0, 6.449),
        # Test case 3: Cow at mature weight (should return 0)
        (True, 600.0, 600.0, 1.2, 0.0),
        # Test case 4: Cow above mature weight (should return 0)
        (True, 650.0, 600.0, 0.5, 0.0),
        # Test case 5: Calf growing rapidly (not a cow)
        (False, 250.0, 500.0, 1.5, 10.3102),
        # Test case 6: Non-growing heifer (daily growth = 0)
        (False, 400.0, 600.0, 0.0, 0.0),
    ],
)
def test_calculate_phosphorus_for_growth(
    is_cow: bool, body_weight: float, mature_body_weight: float, daily_growth: float, expected_growth_phosphorus: float
) -> None:
    """Test that phosphorus retained for growth is correctly calculated."""

    # Arrange
    nutrients = Nutrients()
    mock_nutrient_inputs = MagicMock()
    mock_nutrient_inputs.animal_type.is_cow = is_cow
    mock_nutrient_inputs.body_weight = body_weight
    mock_nutrient_inputs.mature_body_weight = mature_body_weight
    mock_nutrient_inputs.daily_growth = daily_growth

    # Act
    result = nutrients._calculate_phosphorus_for_growth(mock_nutrient_inputs)

    # Assert
    assert result == pytest.approx(expected_growth_phosphorus, rel=1e-3)


@pytest.mark.parametrize(
    "days_in_pregnancy, expected_gestational_phosphorus",
    [
        # Test case 1: Early pregnancy (should return 0)
        (100, 0.0),
        # Test case 2: Just before threshold (should still return 0)
        (189, 0.0),
        # Test case 3: At the threshold (190 days)
        (190, 1.7622),
        # Test case 4: Mid-late pregnancy
        (220, 3.0678),
        # Test case 5: Late pregnancy
        (260, 4.8651),
        # Test case 6: Very late pregnancy
        (280, 5.3452),
    ],
)
def test_calculate_gestational_phosphorus(days_in_pregnancy: int, expected_gestational_phosphorus: float) -> None:
    """Test that gestational phosphorus is correctly calculated."""

    # Arrange
    nutrients = Nutrients()
    mock_nutrient_inputs = MagicMock()
    mock_nutrient_inputs.days_in_pregnancy = days_in_pregnancy

    # Act
    result = nutrients._calculate_gestational_phosphorus(mock_nutrient_inputs)

    # Assert
    assert result == pytest.approx(expected_gestational_phosphorus, rel=1e-3)


@pytest.mark.parametrize(
    "is_milking, daily_milk_produced, expected_milk_phosphorus",
    [
        # Test case 1: Milking cow producing moderate milk
        (True, 30.0, 27.0),
        # Test case 2: High milk production
        (True, 50.0, 45.0),
        # Test case 3: Low milk production
        (True, 10.0, 9.0),
        # Test case 4: Not milking (should return 0)
        (False, 20.0, 0.0),
        # Test case 5: Edge case - no milk production while milking (should return 0)
        (True, 0.0, 0.0),
    ],
)
def test_calculate_milk_phosphorus(
    is_milking: bool, daily_milk_produced: float, expected_milk_phosphorus: float
) -> None:
    """Test that milk phosphorus is correctly calculated."""

    # Arrange
    nutrients = Nutrients()
    mock_nutrient_inputs = MagicMock()
    mock_nutrient_inputs.is_milking = is_milking
    mock_nutrient_inputs.daily_milk_produced = daily_milk_produced

    # Act
    result = nutrients._calculate_milk_phosphorus(mock_nutrient_inputs)

    # Assert
    assert result == pytest.approx(expected_milk_phosphorus, rel=1e-3)


@pytest.mark.parametrize(
    "animal_type, phosphorus_endogenous_loss, phosphorus_for_growth, phosphorus_for_gestation, milk_phosphorus,"
    "urine_production_phosphorus, expected_absorbed_phosphorus",
    [
        # Test case 1: Lactating cow (includes milk phosphorus)
        (AnimalType.LAC_COW, 5.0, 3.0, 2.0, 10.0, 1.5, 21.5),
        # Test case 2: Dry cow (no milk phosphorus)
        (AnimalType.DRY_COW, 4.5, 2.5, 3.5, 0.0, 1.0, 11.5),
        # Test case 3: Heifer II (no milk phosphorus)
        (AnimalType.HEIFER_II, 3.5, 2.0, 1.5, 0.0, 0.5, 7.5),
        # Test case 4: Heifer III (no milk phosphorus)
        (AnimalType.HEIFER_III, 3.0, 1.5, 2.0, 0.0, 0.8, 7.3),
        # Test case 5: Heifer I (no milk or gestational phosphorus)
        (AnimalType.HEIFER_I, 2.5, 1.0, 0.0, 0.0, 0.3, 3.8),
        # Test case 6: Calf (no milk or gestational phosphorus)
        (AnimalType.CALF, 1.8, 0.8, 0.0, 0.0, 0.2, 2.8),
    ],
)
def test_calculate_absorbed_phosphorus(
    animal_type: str,
    phosphorus_endogenous_loss: float,
    phosphorus_for_growth: float,
    phosphorus_for_gestation: float,
    milk_phosphorus: float,
    urine_production_phosphorus: float,
    expected_absorbed_phosphorus: float,
) -> None:
    """Test that absorbed phosphorus is correctly calculated based on animal type."""

    # Arrange
    nutrients = Nutrients()
    mock_nutrient_inputs = MagicMock()
    mock_nutrient_inputs.animal_type.is_cow = animal_type in ["LAC_COW", "DRY_COW"]
    mock_nutrient_inputs.animal_type = animal_type

    nutrients.phosphorus_endogenous_loss = phosphorus_endogenous_loss
    nutrients.phosphorus_for_growth = phosphorus_for_growth
    nutrients.phosphorus_for_gestation = phosphorus_for_gestation

    # Act
    result = nutrients._calculate_absorbed_phosphorus(
        mock_nutrient_inputs, milk_phosphorus, urine_production_phosphorus
    )

    # Assert
    assert result == pytest.approx(expected_absorbed_phosphorus, rel=1e-3)


@pytest.mark.parametrize(
    "animal_type, is_cow, is_milking, ration_phosphorus_concentration, absorbed_phosphorus, expected_requirement",
    [
        # Test case 1: Lactating cow with ration phosphorus concentration 0.3
        (AnimalType.LAC_COW, True, True, 0.3, 15.0, 18.1971),
        # Test case 2: Lactating cow with ration phosphorus concentration 0.4
        (AnimalType.LAC_COW, True, True, 0.4, 18.0, 26.4059),
        # Test case 3: Dry cow (not milking)
        (AnimalType.DRY_COW, True, False, 0.25, 12.0, 18.0723),
        # Test case 4: Heifer II
        (AnimalType.HEIFER_II, False, False, 0.28, 14.0, 21.0843),
        # Test case 5: Heifer III
        (AnimalType.HEIFER_III, False, False, 0.26, 10.0, 15.0602),
        # Test case 6: Calf
        (AnimalType.CALF, False, False, 0.2, 8.0, 8.8889),
    ],
)
def test_calculate_animal_phosphorus_requirement(
    animal_type: AnimalType,
    is_cow: bool,
    is_milking: bool,
    ration_phosphorus_concentration: float,
    absorbed_phosphorus: float,
    expected_requirement: float,
) -> None:
    """Test that phosphorus requirement is correctly calculated based on animal type."""

    # Arrange
    nutrients = Nutrients()
    mock_nutrient_inputs = MagicMock()
    mock_nutrient_inputs.animal_type = animal_type
    mock_nutrient_inputs.is_milking = is_milking

    # Set ration phosphorus concentration
    nutrients.ration_phosphorus_concentration = ration_phosphorus_concentration

    # Act
    result = nutrients._calculate_animal_phosphorus_requirement(mock_nutrient_inputs, absorbed_phosphorus)

    # Assert
    assert result == pytest.approx(expected_requirement, rel=1e-3)
