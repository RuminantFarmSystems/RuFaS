from unittest.mock import PropertyMock
import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.body_weight_history import BodyWeightHistory
from RUFAS.biophysical.animal.data_types.growth import GrowthInputs, GrowthOutputs
from RUFAS.biophysical.animal.growth.growth import Growth
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime


@pytest.mark.parametrize(
    "daily_growth, tissue_changed, body_weight_history, expected_daily_growth, expected_tissue_changed,"
    "expected_history",
    [
        (
            1.5,
            0.3,
            [{"simulation_day": 10, "days_born": 100, "body_weight": 200.0}],
            1.5,
            0.3,
            [{"simulation_day": 10, "days_born": 100, "body_weight": 200.0}],
        ),
        (0.0, 0.0, None, 0.0, 0.0, []),
        (None, None, None, 0.0, 0.0, []),
        (
            2.0,
            -0.5,
            [
                {"simulation_day": 20, "days_born": 150, "body_weight": 250.0},
                {"simulation_day": 25, "days_born": 155, "body_weight": 260.0},
            ],
            2.0,
            -0.5,
            [
                {"simulation_day": 20, "days_born": 150, "body_weight": 250.0},
                {"simulation_day": 25, "days_born": 155, "body_weight": 260.0},
            ],
        ),
    ],
)
def test_growth_init(
    daily_growth: float,
    tissue_changed: float,
    body_weight_history: list[BodyWeightHistory],
    expected_daily_growth: float,
    expected_tissue_changed: float,
    expected_history: list[BodyWeightHistory],
) -> None:
    """Test the initialization of the Growth class."""
    growth = Growth(daily_growth, tissue_changed, body_weight_history)

    assert growth.daily_growth == expected_daily_growth
    assert growth.tissue_changed == expected_tissue_changed
    assert isinstance(growth.body_weight_history, list)
    assert growth.body_weight_history == expected_history


@pytest.mark.parametrize(
    "animal_type, is_pregnant, body_weight, conceptus_weight, mature_body_weight, days_born, expected_body_weight,"
    "expected_conceptus_weight, should_add_event, should_raise_value_error, should_raise_runtime_error",
    [
        # Calf growth
        (AnimalType.CALF, False, 50.0, 0.0, 600.0, 30, 55.0, 0.0, False, False, False),
        # Non-pregnant heifer
        (AnimalType.HEIFER_II, False, 300.0, 0.0, 600.0, 400, 305.0, 0.0, False, False, False),
        # Heifer reaches mature bw
        (AnimalType.HEIFER_II, True, 500.0, 0.0, 400.0, 400, 400.0, 0.0, True, False, False),
        # Pregnant heifer
        (AnimalType.HEIFER_II, True, 500.0, 10.0, 600.0, 500, 505.0, 2.0, False, False, False),
        # Cow growth
        (AnimalType.LAC_COW, False, 650.0, 20.0, 600.0, 700, 655.0, 2.0, False, False, False),
        # ValueError: Unsupported type
        ("UNKNOWN_TYPE", False, 500.0, 0.0, 600.0, 500, 500.0, 0.0, False, True, False),
        # RuntimeError expectation for DRY_COW
        (AnimalType.DRY_COW, False, 500.0, 0.0, 600.0, 500, 505.0, 2.0, False, False, True),
    ],
)
def test_evaluate_body_weight_change(
    mocker: MockerFixture,
    animal_type: AnimalType,
    is_pregnant: bool,
    body_weight: float,
    conceptus_weight: float,
    mature_body_weight: float,
    days_born: int,
    expected_body_weight: float,
    expected_conceptus_weight: float,
    should_add_event: bool,
    should_raise_value_error: bool,
    should_raise_runtime_error: bool,
) -> None:
    """Test the evaluate_body_weight_change method of the Growth class."""
    growth = Growth()

    mock_growth_inputs = mocker.MagicMock(spec=GrowthInputs)
    mock_growth_inputs.animal_type = animal_type
    mock_growth_inputs.is_pregnant = is_pregnant
    mock_growth_inputs.body_weight = body_weight
    mock_growth_inputs.conceptus_weight = conceptus_weight
    mock_growth_inputs.mature_body_weight = mature_body_weight
    mock_growth_inputs.days_born = days_born

    mock_time = mocker.MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_add_error = mocker.patch.object(OutputManager, "add_error")

    mock_add_event = mocker.patch.object(AnimalEvents, "add_event")

    mocker.patch.object(growth, "calculate_calf_body_weight_change", return_value=5.0)
    mocker.patch.object(growth, "calculate_non_pregnant_heifer_body_weight_change", return_value=5.0)
    mocker.patch.object(growth, "calculate_pregnant_heifer_body_weight_change", return_value=(5.0, 2.0))
    mocker.patch.object(growth, "calculate_cow_body_weight_change", return_value=(5.0, 2.0, 1.0))

    if should_raise_value_error:
        with pytest.raises(ValueError, match=f"{animal_type} is not a valid animal type."):
            growth.evaluate_body_weight_change(mock_growth_inputs, mock_time)
        mock_add_error.assert_called_once()
        return

    if should_raise_runtime_error:
        mocker.patch.object(
            type(mock_growth_inputs.animal_type), "is_cow", new_callable=PropertyMock, return_value=False
        )
        with pytest.raises(
            RuntimeError, match=f"Unexpected execution path in process_digestion. Animal type: {animal_type}"
        ):
            growth.evaluate_body_weight_change(mock_growth_inputs, mock_time)
        mock_add_error.assert_called_once()
        return

    output = growth.evaluate_body_weight_change(mock_growth_inputs, mock_time)

    assert isinstance(output, GrowthOutputs)
    assert output.body_weight == expected_body_weight
    assert output.conceptus_weight == expected_conceptus_weight

    assert isinstance(growth.body_weight_history, list)
    assert growth.body_weight_history[-1] == {
        "simulation_day": mock_time.simulation_day,
        "days_born": days_born,
        "body_weight": expected_body_weight,
    }

    if should_add_event:
        mock_add_event.assert_called_once_with(
            days_born, mock_time.simulation_day, animal_constants.MATURE_BODY_WEIGHT_REGULAR
        )
    else:
        mock_add_event.assert_not_called()


@pytest.mark.parametrize(
    "birth_weight, expected_growth",
    [
        (40.0, 40.0 / AnimalConfig.wean_day),  # Standard calf birth weight
        (50.0, 50.0 / AnimalConfig.wean_day),  # Higher birth weight calf
        (30.0, 30.0 / AnimalConfig.wean_day),  # Lower birth weight calf
        (0.0, 0.0),  # Edge case: birth weight of 0 should return 0 growth
    ],
)
def test_calculate_calf_body_weight_change(
    mocker: MockerFixture,
    birth_weight: float,
    expected_growth: float,
) -> None:
    """Test the calculate_calf_body_weight_change method of the Growth class."""
    growth = Growth()

    mock_growth_inputs = mocker.MagicMock(spec=GrowthInputs)
    mock_growth_inputs.birth_weight = birth_weight

    result = growth.calculate_calf_body_weight_change(mock_growth_inputs)

    assert isinstance(result, float)
    assert result == expected_growth


@pytest.mark.parametrize(
    "body_weight, mature_body_weight, days_born, expected_growth",
    [
        # Standard heifer growth case
        (200.0, 500.0, 300, 0.72727272),
        # Near maturity, should return minimum growth rate
        (495.0, 500.0, 398, AnimalModuleConstants.MINIMUM_HEIFER_DAILY_GROWTH_RATE),
        # Edge case: divisor would be 0
        (250.0, 500.0, AnimalConfig.target_heifer_pregnant_day, 24.0),
        # Very young heifer, should still grow at normal rate
        (100.0, 600.0, 100, 0.7384615384615385),
    ],
)
def test_calculate_non_pregnant_heifer_body_weight_change(
    mocker: MockerFixture,
    body_weight: float,
    mature_body_weight: float,
    days_born: int,
    expected_growth: float,
) -> None:
    """Test the calculate_non_pregnant_heifer_body_weight_change method of the Growth class."""
    growth = Growth()

    mock_growth_inputs = mocker.MagicMock(spec=GrowthInputs)
    mock_growth_inputs.body_weight = body_weight
    mock_growth_inputs.mature_body_weight = mature_body_weight
    mock_growth_inputs.days_born = days_born

    result = growth.calculate_non_pregnant_heifer_body_weight_change(mock_growth_inputs)

    assert isinstance(result, float)
    assert result == pytest.approx(expected_growth, rel=1e-6)


@pytest.mark.parametrize(
    "target_growth, conceptus_growth, updated_conceptus_weight, expected_body_growth, expected_conceptus_weight",
    [
        # Standard pregnant heifer growth
        (0.85, 0.15, 5.0, 1.00, 5.0),
        # Higher target growth with moderate conceptus growth
        (1.20, 0.20, 6.5, 1.40, 6.5),
        # Minimal growth, small conceptus growth
        (0.50, 0.05, 2.0, 0.55, 2.0),
        # Edge case: zero target growth, only conceptus growth
        (0.00, 0.10, 3.0, 0.10, 3.0),
    ],
)
def test_calculate_pregnant_heifer_body_weight_change(
    mocker: MockerFixture,
    target_growth: float,
    conceptus_growth: float,
    updated_conceptus_weight: float,
    expected_body_growth: float,
    expected_conceptus_weight: float,
) -> None:
    growth = Growth()

    mock_growth_inputs = mocker.MagicMock(spec=GrowthInputs)

    mocker.patch.object(growth, "_calculate_pregnant_heifer_target_daily_growth", return_value=target_growth)
    mocker.patch.object(
        growth, "_calculate_pregnant_heifer_conceptus_growth", return_value=(conceptus_growth, updated_conceptus_weight)
    )

    result_body_growth, result_conceptus_weight = growth.calculate_pregnant_heifer_body_weight_change(
        mock_growth_inputs
    )

    assert isinstance(result_body_growth, float)
    assert isinstance(result_conceptus_weight, float)
    assert result_body_growth == expected_body_growth
    assert result_conceptus_weight == expected_conceptus_weight


@pytest.mark.parametrize(
    "conceptus_growth, updated_conceptus_weight, tissue_changed, target_adg_cow, body_weight_tissue,"
    "expected_body_growth, expected_conceptus_weight, expected_tissue_changed",
    [
        # Standard cow growth scenario
        (0.20, 8.0, 0.5, 1.00, 0.30, 1.50, 8.0, 0.5),
        # Higher growth and tissue mobilization
        (0.30, 10.0, 0.7, 1.20, 0.50, 2.00, 10.0, 0.7),
        # Low growth, minimal tissue mobilization
        (0.10, 5.0, 0.3, 0.50, 0.20, 0.80, 5.0, 0.3),
        # Edge case: No maternal gain, only conceptus & tissue effects
        (0.00, 6.0, 0.2, 0.00, 0.00, 0.00, 6.0, 0.2),
    ],
)
def test_calculate_cow_body_weight_change(
    mocker: MockerFixture,
    conceptus_growth: float,
    updated_conceptus_weight: float,
    tissue_changed: float,
    target_adg_cow: float,
    body_weight_tissue: float,
    expected_body_growth: float,
    expected_conceptus_weight: float,
    expected_tissue_changed: float,
) -> None:
    growth = Growth()

    mock_growth_inputs = mocker.MagicMock(spec=GrowthInputs)

    mocker.patch.object(
        growth,
        "_calculate_cow_conceptus_growth",
        return_value=(conceptus_growth, updated_conceptus_weight, tissue_changed),
    )
    mocker.patch.object(growth, "_calculate_cow_target_daily_growth", return_value=target_adg_cow)
    mocker.patch.object(
        growth, "_calculate_cow_body_weight_tissue_change", return_value=(body_weight_tissue, tissue_changed)
    )

    result_body_growth, result_conceptus_weight, result_tissue_changed = growth.calculate_cow_body_weight_change(
        mock_growth_inputs
    )

    assert isinstance(result_body_growth, float)
    assert isinstance(result_conceptus_weight, float)
    assert isinstance(result_tissue_changed, float)
    assert result_body_growth == expected_body_growth
    assert result_conceptus_weight == expected_conceptus_weight
    assert result_tissue_changed == expected_tissue_changed


@pytest.mark.parametrize(
    "days_in_pregnancy, gestation_length, conceptus_weight, calf_birth_weight, expected_conceptus_growth,"
    "expected_updated_conceptus_weight",
    [
        # End of pregnancy - conceptus weight should be reset to 0
        (276, 276, 12.0, 40.0, -12.0, 0.0),
        # Mid-pregnancy growth (days_in_pregnancy > 50)
        (150, 276, 5.0, 40.0, 0.1743159768160859, 5.174315976816086),
        # Early pregnancy (no growth expected)
        (30, 276, 4.0, 40.0, 0.0, 4.0),
    ],
)
def test_calculate_pregnant_heifer_conceptus_growth(
    mocker: MockerFixture,
    days_in_pregnancy: int,
    gestation_length: int,
    conceptus_weight: float,
    calf_birth_weight: float,
    expected_conceptus_growth: float,
    expected_updated_conceptus_weight: float,
) -> None:
    growth = Growth()

    mock_growth_inputs = mocker.MagicMock(spec=GrowthInputs)
    mock_growth_inputs.days_in_pregnancy = days_in_pregnancy
    mock_growth_inputs.gestation_length = gestation_length
    mock_growth_inputs.conceptus_weight = conceptus_weight
    mock_growth_inputs.calf_birth_weight = calf_birth_weight

    result_conceptus_growth, result_updated_conceptus_weight = growth._calculate_pregnant_heifer_conceptus_growth(
        mock_growth_inputs
    )

    assert result_conceptus_growth == expected_conceptus_growth
    assert result_updated_conceptus_weight == expected_updated_conceptus_weight


@pytest.mark.parametrize(
    "days_in_pregnancy, gestation_length, conceptus_weight, tissue_changed, expected_conceptus_growth,"
    "expected_updated_conceptus_weight, expected_updated_tissue_change",
    [
        # End of pregnancy - conceptus weight should reset, tissue change set to 0
        (276, 276, 12.0, 5.0, -12.0, 0.0, 0.0),
        # Mid-pregnancy growth (days_in_pregnancy > 50) with tissue change retained
        (150, 276, 5.0, 3.0, 1.80, 6.80, 3.0),
        # Early pregnancy (no growth expected, tissue change retained)
        (30, 276, 4.0, 2.0, 0.0, 4.0, 2.0),
    ],
)
def test_calculate_cow_conceptus_growth(
    mocker: MockerFixture,
    days_in_pregnancy: int,
    gestation_length: int,
    conceptus_weight: float,
    tissue_changed: float,
    expected_conceptus_growth: float,
    expected_updated_conceptus_weight: float,
    expected_updated_tissue_change: float,
) -> None:
    growth = Growth()
    growth.tissue_changed = tissue_changed

    mock_growth_inputs = mocker.MagicMock(spec=GrowthInputs)
    mock_growth_inputs.days_in_pregnancy = days_in_pregnancy
    mock_growth_inputs.gestation_length = gestation_length
    mock_growth_inputs.conceptus_weight = conceptus_weight

    mocker.patch.object(
        growth,
        "_calculate_pregnant_heifer_conceptus_growth",
        return_value=(expected_conceptus_growth, expected_updated_conceptus_weight),
    )

    result_conceptus_growth, result_updated_conceptus_weight, result_updated_tissue_change = (
        growth._calculate_cow_conceptus_growth(mock_growth_inputs)
    )

    assert isinstance(result_conceptus_growth, float)
    assert isinstance(result_updated_conceptus_weight, float)
    assert isinstance(result_updated_tissue_change, float)

    assert result_conceptus_growth == expected_conceptus_growth
    assert result_updated_conceptus_weight == expected_updated_conceptus_weight
    assert result_updated_tissue_change == expected_updated_tissue_change


@pytest.mark.parametrize(
    "gestation_length, days_in_pregnancy, mature_body_weight, body_weight, expected_growth",
    [
        # Early pregnancy: gradual weight increase
        (276, 30, 600.0, 250.0, 0.9443902439024388),
        # Mid-pregnancy: higher weight, lower gain
        (276, 150, 600.0, 450.0, 0.3199999999999995),
        # Near term: lowest growth (approaching maturity)
        (276, 270, 600.0, 590.0, -15.680000000000007),
        # Edge case: divisor set to 1 when `days_in_pregnancy == gestation_length`
        (276, 276, 600.0, 600.0, -103.68000000000006),
    ],
)
def test_calculate_pregnant_heifer_target_daily_growth(
    mocker: MockerFixture,
    gestation_length: int,
    days_in_pregnancy: int,
    mature_body_weight: float,
    body_weight: float,
    expected_growth: float,
) -> None:
    growth = Growth()

    mock_growth_inputs = mocker.MagicMock(spec=GrowthInputs)
    mock_growth_inputs.gestation_length = gestation_length
    mock_growth_inputs.days_in_pregnancy = days_in_pregnancy
    mock_growth_inputs.mature_body_weight = mature_body_weight
    mock_growth_inputs.body_weight = body_weight

    result = growth._calculate_pregnant_heifer_target_daily_growth(mock_growth_inputs)

    assert isinstance(result, float)
    assert result == expected_growth


@pytest.mark.parametrize(
    "calves, days_in_pregnancy, mature_body_weight, body_weight, gestation_length, calving_interval, expected_growth",
    [
        # Single calf, before pregnancy
        (1, 0, 700.0, 650.0, 280, 400, 0.16800000000000015),
        # Single calf, early pregnancy
        (1, 30, 700.0, 650.0, 280, 400, -0.02390438247011952),
        # Single calf, mid-pregnancy
        (1, 150, 700.0, 680.0, 280, 400, -0.2748091603053435),
        # Single calf, near term
        (1, 270, 700.0, 695.0, 280, 400, -4.636363636363637),
        # Twin calves, before pregnancy
        (2, 0, 700.0, 650.0, 280, 400, 0.13439999999999994),
        # Twin calves, early pregnancy
        (2, 30, 700.0, 650.0, 280, 400, 0.199203187250996),
        # Twin calves, mid-pregnancy
        (2, 150, 700.0, 680.0, 280, 400, 0.15267175572519084),
        # Twin calves, near term
        (2, 270, 700.0, 695.0, 280, 400, 0.45454545454545453),
        # No calves
        (0, 30, 700.0, 650.0, 280, 400, 0.00),
    ],
)
def test_calculate_cow_target_daily_growth(
    mocker: MockerFixture,
    calves: int,
    days_in_pregnancy: int,
    mature_body_weight: float,
    body_weight: float,
    gestation_length: int,
    calving_interval: int,
    expected_growth: float,
) -> None:
    growth = Growth()

    mock_growth_inputs = mocker.MagicMock(spec=GrowthInputs)
    mock_growth_inputs.calves = calves
    mock_growth_inputs.days_in_pregnancy = days_in_pregnancy
    mock_growth_inputs.mature_body_weight = mature_body_weight
    mock_growth_inputs.body_weight = body_weight
    mock_growth_inputs.gestation_length = gestation_length
    mock_growth_inputs.calving_interval = calving_interval

    result = growth._calculate_cow_target_daily_growth(mock_growth_inputs)

    assert result == expected_growth


@pytest.mark.parametrize(
    "is_milking, calves, days_in_milk, days_in_pregnancy, gestation_length, tissue_changed,"
    "expected_body_weight_tissue, expected_updated_tissue_changed",
    [
        # Single calf, early lactation
        (True, 1, 10, 100, 280, 0.0, pytest.approx(-0.606800483411535, abs=6.1e-03), 0.0),
        # Single calf, mid-lactation
        (True, 1, 40, 100, 280, 0.0, pytest.approx(-0.17385197560343396, abs=1.7e-03), 0.0),
        # Single calf, late lactation
        (
            True,
            1,
            60,
            217,
            280,
            0.0,
            pytest.approx(-0.02556115974977957, abs=2.6e-04),
            pytest.approx(19.93770460482806, abs=2.0e-01),
        ),
        # Twin calves, early lactation
        (True, 2, 10, 100, 280, 0.0, pytest.approx(-1.1541641350450582, abs=1.2e-02), 0.0),
        # Twin calves, mid-lactation
        (True, 2, 40, 100, 280, 0.0, pytest.approx(-0.3759337981849493, abs=3.8e-03), 0.0),
        # Twin calves, late lactation
        (
            True,
            2,
            60,
            217,
            280,
            0.0,
            pytest.approx(-0.09416857101184539, abs=9.4e-04),
            pytest.approx(39.55079982497513, abs=4.0e-01),
        ),
        # Dry cow (not milking)
        (False, 1, 0, 100, 280, 5.0, pytest.approx(0.08064516129032258, abs=8.1e-04), 5.0),
    ],
)
def test_calculate_cow_body_weight_tissue_change(
    mocker: MockerFixture,
    is_milking: bool,
    calves: int,
    days_in_milk: int,
    days_in_pregnancy: int,
    gestation_length: int,
    tissue_changed: float,
    expected_body_weight_tissue: float,
    expected_updated_tissue_changed: float,
) -> None:
    growth = Growth()
    growth.tissue_changed = tissue_changed

    mock_growth_inputs = mocker.MagicMock(spec=GrowthInputs)
    mock_growth_inputs.is_milking = is_milking
    mock_growth_inputs.calves = calves
    mock_growth_inputs.days_in_milk = days_in_milk
    mock_growth_inputs.days_in_pregnancy = days_in_pregnancy
    mock_growth_inputs.gestation_length = gestation_length

    result_body_weight_tissue, result_updated_tissue_changed = growth._calculate_cow_body_weight_tissue_change(
        mock_growth_inputs
    )

    assert isinstance(result_body_weight_tissue, float)
    assert isinstance(result_updated_tissue_changed, float)
    assert pytest.approx(result_body_weight_tissue, rel=1e-2) == expected_body_weight_tissue
    assert pytest.approx(result_updated_tissue_changed, rel=1e-2) == expected_updated_tissue_changed
