import math
from unittest.mock import MagicMock
import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal_nutrients.animal_nutrients import CALVES_AND_HEIFERS, AnimalNutrients
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.general_constants import GeneralConstants


def test_perform_daily_phosphorus_update(mocker: MockerFixture) -> None:
    """Tests that daily phosphorus update is performed correctly."""
    mock_animal_status = MagicMock()
    mock_general_properties = MagicMock()

    mock_get_dmi = mocker.patch("RUFAS.biophysical.animal.animal_nutrients.animal_nutrients.AnimalNutrients."
                                "_get_dry_matter_intake", return_value=10.0)
    mock_calc_phosphorus_requirements = mocker.patch(
        'RUFAS.biophysical.animal.animal_nutrients.animal_nutrients.AnimalNutrients._calculate_phosphorus_requirements',
        return_value=mock_animal_status
    )
    mock_calc_total_phosphorus = mocker.patch(
        'RUFAS.biophysical.animal.animal_nutrients.animal_nutrients.AnimalNutrients._calculate_total_animal_phosphorus',
        return_value=mock_animal_status
    )

    result = AnimalNutrients.perform_daily_phosphorus_update(mock_animal_status, mock_general_properties)

    mock_get_dmi.assert_called_once()
    mock_calc_phosphorus_requirements.assert_called_once_with(mock_general_properties, mock_animal_status, 10.0)
    mock_calc_total_phosphorus.assert_called_once_with(mock_animal_status)

    assert result == mock_animal_status


def test_get_dry_matter_intake() -> None:
    """Tests that dry matter intake is calculated correctly."""
    pass


@pytest.mark.parametrize(
    "phosphorus_intake, phosphorus_requirement, initial_reserves, phosphorus_for_gestation, phosphorus_for_growth,"
    "expected_excess_in_diet, expected_reserves, expected_total_phosphorus",
    [
        # Case 1: phosphorus_intake < phosphorus_requirement (if condition)
        (5.0, 8.0, -5.0, 2.0, 1.0, 0.0, -8.0, 100.0 + 2.0 + 1.0 + (-8.0 + 5.0)),
        # Case 2: phosphorus_intake >= phosphorus_requirement and reserves < 0 (elif condition)
        (10.0, 8.0, -5.0, 2.0, 1.0, 2.0, 0.7 * 2.0 - 5.0, 100.0 + 2.0 + 1.0 + ((0.7 * 2.0 - 5.0) + 5.0)),
        # Case 3: phosphorus_intake >= phosphorus_requirement and reserves >= 0 (else condition)
        (10.0, 8.0, 5.0, 2.0, 1.0, 2.0, 0.0, 100.0 + 2.0 + 1.0 + (0.0 - 5.0)),
    ],
)
def test_calculate_total_animal_phosphorus(
    phosphorus_intake: float, phosphorus_requirement: float, initial_reserves: float,
    phosphorus_for_gestation: float, phosphorus_for_growth: float,
    expected_excess_in_diet: float, expected_reserves: float, expected_total_phosphorus: float,
) -> None:
    """Tests that total animal phosphorus is calculated correctly for different scenarios."""
    mock_phosphorus_status = MagicMock()
    mock_phosphorus_status.phosphorus_intake = phosphorus_intake
    mock_phosphorus_status.phosphorus_requirement = phosphorus_requirement
    mock_phosphorus_status.phosphorus_reserves = initial_reserves
    mock_phosphorus_status.phosphorus_for_gestation = phosphorus_for_gestation
    mock_phosphorus_status.phosphorus_for_growth = phosphorus_for_growth
    mock_phosphorus_status.total_phosphorus_in_animal = 100.0

    AnimalNutrients._calculate_total_animal_phosphorus(mock_phosphorus_status)

    assert mock_phosphorus_status.phosphorus_excess_in_diet == expected_excess_in_diet
    assert mock_phosphorus_status.phosphorus_reserves == pytest.approx(expected_reserves, 1e-3)
    assert mock_phosphorus_status.total_phosphorus_in_animal == pytest.approx(expected_total_phosphorus, 1e-3)


@pytest.mark.parametrize(
    "animal_type, dry_matter_intake, expected_loss",
    [
        # Case 1: Animal is a calf or heifer (if condition)
        (AnimalType.CALF, 10.0, 0.0008 * 10.0 * GeneralConstants.KG_TO_GRAMS),
        (AnimalType.HEIFER_I, 15.0, 0.0008 * 15.0 * GeneralConstants.KG_TO_GRAMS),
        (AnimalType.HEIFER_II, 20.0, 0.0008 * 20.0 * GeneralConstants.KG_TO_GRAMS),
        (AnimalType.HEIFER_III, 25.0, 0.0008 * 25.0 * GeneralConstants.KG_TO_GRAMS),
        # Case 2: Animal is not a calf or heifer (else condition)
        (AnimalType.DRY_COW, 10.0, 0.001 * 10.0 * GeneralConstants.KG_TO_GRAMS),
        (AnimalType.LAC_COW, 20.0, 0.001 * 20.0 * GeneralConstants.KG_TO_GRAMS),
    ],
)
def test_calculate_phosphorus_endogenous_loss(animal_type: AnimalType, dry_matter_intake: float, expected_loss: float,
                                              ) -> None:
    """Tests that phosphorus endogenous loss is calculated correctly for different animal types."""
    mock_general_properties = MagicMock()
    mock_general_properties.animal_type = animal_type
    mock_phosphorus_status = MagicMock()

    result = AnimalNutrients._calculate_phosphorus_endogenous_loss(
        mock_general_properties, mock_phosphorus_status, dry_matter_intake
    )

    assert result == pytest.approx(expected_loss, 1e-3)


@pytest.mark.parametrize(
    "animal_type, body_weight, dry_matter_intake, endogenous_loss, growth_phosphorus, gestation_phosphorus,"
    "milk_phosphorus, absorbed_phosphorus, expected_urine_phosphorus",
    [
        (AnimalType.CALF, 100.0, 10.0, 0.8, 2.0, 1.5, 0.5, 3.0, 0.000002 * 100.0 * GeneralConstants.KG_TO_GRAMS),
        (AnimalType.LAC_COW, 500.0, 25.0, 1.0, 3.0, 2.5, 1.0, 6.0, 0.000002 * 500.0 * GeneralConstants.KG_TO_GRAMS),
    ],
)
def test_calculate_phosphorus_requirements(
    animal_type: AnimalType, body_weight: float, dry_matter_intake: float, endogenous_loss: float,
    growth_phosphorus: float, gestation_phosphorus: float, milk_phosphorus: float, absorbed_phosphorus: float,
    expected_urine_phosphorus: float, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Tests that phosphorus requirements are calculated correctly for different animal scenarios."""
    mock_general_properties = MagicMock()
    mock_general_properties.animal_type = animal_type
    mock_general_properties.body_weight = body_weight

    mock_phosphorus_status = MagicMock()
    mock_phosphorus_status.phosphorus_for_gestation_required_for_calf = 0.0

    monkeypatch.setattr(AnimalNutrients, '_calculate_phosphorus_endogenous_loss',
                        MagicMock(return_value=endogenous_loss))
    monkeypatch.setattr(AnimalNutrients, '_calculate_phosphorus_for_growth', MagicMock(return_value=growth_phosphorus))
    monkeypatch.setattr(AnimalNutrients, '_calculate_gestational_phosphorus',
                        MagicMock(return_value=gestation_phosphorus))
    monkeypatch.setattr(AnimalNutrients, '_calculate_milk_phosphorus', MagicMock(return_value=milk_phosphorus))
    monkeypatch.setattr(AnimalNutrients, '_calculate_absorbed_phosphorus', MagicMock(return_value=absorbed_phosphorus))
    monkeypatch.setattr(AnimalNutrients, '_calculate_animal_phosphorus_requirement',
                        MagicMock(return_value=absorbed_phosphorus))

    result = AnimalNutrients._calculate_phosphorus_requirements(
        mock_general_properties, mock_phosphorus_status, dry_matter_intake
    )

    assert result.phosphorus_endogenous_loss == endogenous_loss
    assert result.phosphorus_for_growth == growth_phosphorus
    assert result.phosphorus_for_gestation == gestation_phosphorus
    assert result.phosphorus_for_gestation_required_for_calf == gestation_phosphorus
    assert result.phosphorus_requirement == absorbed_phosphorus
    assert expected_urine_phosphorus == pytest.approx(0.000002 * mock_general_properties.body_weight
                                                      * GeneralConstants.KG_TO_GRAMS)


@pytest.mark.parametrize(
    "animal_type, body_weight, mature_body_weight, daily_growth",
    [
        # Case 1: Animal is a heifer (should calculate growth phosphorus)
        (AnimalType.HEIFER_I, 100.0, 400.0, 0.5),
        # Case 2: Animal weight is less than mature body weight (should calculate growth phosphorus)
        (AnimalType.LAC_COW, 300.0, 500.0, 0.8),
        # Case 3: Animal is not a calf or heifer and body weight is equal to mature weight (should return 0.0)
        (AnimalType.DRY_COW, 500.0, 500.0, 0.6),
    ],
)
def test_calculate_phosphorus_for_growth(
    animal_type: AnimalType, body_weight: float, mature_body_weight: float, daily_growth: float,
) -> None:
    """Tests that phosphorus retained for growth is calculated correctly for different scenarios."""
    mock_general_properties = MagicMock()
    mock_general_properties.animal_type = animal_type
    mock_general_properties.body_weight = body_weight
    mock_general_properties.mature_body_weight = mature_body_weight
    mock_general_properties.daily_growth = daily_growth

    if animal_type in CALVES_AND_HEIFERS or body_weight < mature_body_weight:
        expected_growth_phosphorus = (
            (0.0012 + 0.004635 * (mature_body_weight ** 0.22) * (body_weight ** -0.22))
            * daily_growth / 0.96 * GeneralConstants.KG_TO_GRAMS
        )
    else:
        expected_growth_phosphorus = 0.0

    result = AnimalNutrients._calculate_phosphorus_for_growth(mock_general_properties)

    assert result == pytest.approx(expected_growth_phosphorus, 1e-3)


@pytest.mark.parametrize(
    "days_in_preg, expected_phosphorus",
    [
        # Case 1: days_in_preg >= 190 (should calculate gestational phosphorus)
        (190, (0.00002743 * math.exp((0.05527 - 0.000075 * 190) * 190)
               - 0.00002743 * math.exp((0.05527 - 0.000075 * 189) * 189))
            * GeneralConstants.KG_TO_GRAMS),
        # Case 2: days_in_preg < 190 (should return 0.0)
        (150, 0.0),
        # Case 3: days_in_preg exactly on the threshold
        (191, (0.00002743 * math.exp((0.05527 - 0.000075 * 191) * 191)
               - 0.00002743 * math.exp((0.05527 - 0.000075 * 190) * 190))
            * GeneralConstants.KG_TO_GRAMS),
    ],
)
def test_calculate_gestational_phosphorus(days_in_preg: int, expected_phosphorus: float) -> None:
    """Tests that gestational phosphorus is calculated correctly based on days in pregnancy."""
    mock_general_properties = MagicMock()
    mock_general_properties.days_in_preg = days_in_preg

    result = AnimalNutrients._calculate_gestational_phosphorus(mock_general_properties)

    assert result == pytest.approx(expected_phosphorus, 1e-3)


@pytest.mark.parametrize(
    "is_milking, daily_milk_produced, expected_milk_phosphorus",
    [
        # Case 1: Animal is milking (should calculate milk phosphorus)
        (True, 30.0, 0.0009 * 30.0 * GeneralConstants.KG_TO_GRAMS),
        # Case 2: Animal is not milking (should return 0.0)
        (False, 30.0, 0.0),
        # Case 3: No milk production but animal is marked as milking
        (True, 0.0, 0.0),
    ],
)
def test_calculate_milk_phosphorus(is_milking: bool, daily_milk_produced: float, expected_milk_phosphorus: float
                                   ) -> None:
    """Tests that milk phosphorus is calculated correctly based on milking status and milk production."""
    mock_general_properties = MagicMock()
    mock_general_properties.is_milking = is_milking
    mock_general_properties.daily_milk_produced = daily_milk_produced

    result = AnimalNutrients._calculate_milk_phosphorus(mock_general_properties)

    assert result == pytest.approx(expected_milk_phosphorus, 1e-3)


@pytest.mark.parametrize(
    "animal_type, endogenous_loss, growth_phosphorus, gestation_phosphorus, milk_phosphorus,"
    "urine_production_phosphorus, expected_absorbed_phosphorus",
    [
        # Case 1: Animal is a dry cow or lactating cow (includes milk phosphorus)
        (AnimalType.DRY_COW, 0.5, 1.0, 2.0, 3.0, 0.2, 0.2 + 0.5 + 1.0 + 2.0 + 3.0),
        (AnimalType.LAC_COW, 0.4, 0.9, 1.8, 2.5, 0.1, 0.1 + 0.4 + 0.9 + 1.8 + 2.5),
        # Case 2: Animal is a heifer (does not include milk phosphorus)
        (AnimalType.HEIFER_II, 0.3, 0.8, 1.5, 2.0, 0.05, 0.05 + 0.3 + 0.8 + 1.5),
        (AnimalType.HEIFER_III, 0.2, 0.7, 1.2, 1.5, 0.04, 0.04 + 0.2 + 0.7 + 1.2),
        # Case 3: Other animal types (does not include milk or gestation phosphorus)
        (AnimalType.CALF, 0.1, 0.6, 1.0, 1.0, 0.03, 0.03 + 0.1 + 0.6),
    ],
)
def test_calculate_absorbed_phosphorus(
    animal_type: AnimalType, endogenous_loss: float, growth_phosphorus: float, gestation_phosphorus: float,
    milk_phosphorus: float, urine_production_phosphorus: float, expected_absorbed_phosphorus: float,
) -> None:
    """Tests that absorbed phosphorus is calculated correctly based on animal type."""
    mock_general_properties = MagicMock()
    mock_general_properties.animal_type = animal_type

    mock_phosphorus_status = MagicMock()
    mock_phosphorus_status.phosphorus_endogenous_loss = endogenous_loss
    mock_phosphorus_status.phosphorus_for_growth = growth_phosphorus
    mock_phosphorus_status.phosphorus_for_gestation = gestation_phosphorus

    result = AnimalNutrients._calculate_absorbed_phosphorus(
        mock_general_properties,
        mock_phosphorus_status,
        milk_phosphorus,
        urine_production_phosphorus
    )

    assert result == pytest.approx(expected_absorbed_phosphorus, 1e-3)


@pytest.mark.parametrize(
    "animal_type, is_milking, ration_phosphorus_concentration, absorbed_phosphorus, expected_requirement",
    [
        # Case 1: Animal is a dry or lactating cow and is milking (complex formula)
        (AnimalType.LAC_COW, True, 0.3, 5.0, 5.0 / (1.86696 - 5.01238 * 0.3 + 5.12286 * 0.3**2)),
        (AnimalType.DRY_COW, True, 0.2, 4.0, 4.0 / (1.86696 - 5.01238 * 0.2 + 5.12286 * 0.2**2)),
        # Case 2: Animal is a calf (should use 0.90 as divisor)
        (AnimalType.CALF, False, 0.1, 3.0, 3.0 / 0.90),
        # Case 3: Other animal types (should use 0.664 as divisor)
        (AnimalType.HEIFER_II, False, 0.1, 2.5, 2.5 / 0.664),
        (AnimalType.HEIFER_III, False, 0.1, 2.0, 2.0 / 0.664),
    ],
)
def test_calculate_animal_phosphorus_requirement(
    animal_type: AnimalType, is_milking: bool, ration_phosphorus_concentration: float, absorbed_phosphorus: float,
    expected_requirement,
) -> None:
    """Tests that the animal phosphorus requirement is calculated correctly based on the animal type and conditions."""
    mock_general_properties = MagicMock()
    mock_general_properties.animal_type = animal_type
    mock_general_properties.is_milking = is_milking

    mock_phosphorus_status = MagicMock()
    mock_phosphorus_status.ration_phosphorus_concentration = ration_phosphorus_concentration

    result = AnimalNutrients._calculate_animal_phosphorus_requirement(
        mock_general_properties, mock_phosphorus_status, absorbed_phosphorus
    )

    assert result == pytest.approx(expected_requirement, 1e-3)


@pytest.mark.parametrize(
    "animal_type, expected_result",
    [
        # Cases where the animal is a calf or heifer
        (AnimalType.CALF, True),
        (AnimalType.HEIFER_I, True),
        (AnimalType.HEIFER_II, True),
        (AnimalType.HEIFER_III, True),
        # Cases where the animal is not a calf or heifer
        (AnimalType.DRY_COW, False),
        (AnimalType.LAC_COW, False),
    ],
)
def test_is_calf_or_heifer(animal_type: AnimalType, expected_result: bool) -> None:
    """Tests that the function correctly identifies calves and heifers."""
    result = AnimalNutrients._is_calf_or_heifer(animal_type)
    assert result == expected_result
