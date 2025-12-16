import numpy as np
import pytest
from pytest_mock import MockerFixture
from scipy.integrate import quad

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_constants import DRY
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.milk_production import MilkProductionInputs, MilkProductionOutputs
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.general_constants import GeneralConstants
from RUFAS.rufas_time import RufasTime
from RUFAS.util import Utility


@pytest.fixture
def time(mocker: MockerFixture) -> RufasTime:
    mocker.patch.object(RufasTime, "__init__", return_value=None)
    return RufasTime()


def test_milk_production_initialization(mocker: MockerFixture) -> None:
    """Test the initialization of the MilkProduction class."""
    mock_generate_random_number = mocker.patch.object(Utility, "generate_random_number", return_value=1.5)

    milk_production = MilkProduction()

    assert isinstance(milk_production, MilkProduction)
    assert milk_production._daily_milk_produced == 0.0
    assert milk_production._milk_production_variance == 1.5
    assert milk_production.crude_protein_content == 0.0
    assert milk_production.true_protein_content == 0.0
    assert milk_production.fat_content == 0.0
    assert milk_production.lactose_content == 0.0
    assert milk_production.milk_production_reduction == 0.0
    assert milk_production.current_lactation_305_day_milk_produced == 0.0
    assert isinstance(milk_production.milk_production_history, list)
    assert len(milk_production.milk_production_history) == 0

    mock_generate_random_number.assert_called_once_with(
        AnimalModuleConstants.DAILY_MILK_VARIATION_MEAN,
        AnimalModuleConstants.DAILY_MILK_VARIATION_STD_DEV,
    )


@pytest.mark.parametrize(
    "initial_milk, variance, reduction, expected_output",
    [
        (10.0, 2.0, 1.0, 11.0),  # Normal case: initial + variance - reduction
        (5.0, -1.0, 0.5, 3.5),  # Negative variance decreases production
        (3.0, 2.0, 5.0, 0.0),  # Reduction larger than total production, should floor at 0
        (0.0, 2.0, 1.0, 0.0),  # Initial production is 0, so output must remain 0
        (10.0, -5.0, 5.0, 0.0),  # Net production drops to 0
    ],
)
def test_daily_milk_produced_property(
    initial_milk: float, variance: float, reduction: float, expected_output: float
) -> None:
    """Test the daily_milk_produced property of the MilkProduction class."""
    milk_production = MilkProduction()
    milk_production._daily_milk_produced = initial_milk
    milk_production._milk_production_variance = variance
    milk_production.milk_production_reduction = reduction

    assert milk_production.daily_milk_produced == expected_output


@pytest.mark.parametrize("new_value", [15.0, 0.0, 25.5])
def test_daily_milk_produced_setter(mocker: MockerFixture, new_value: float) -> None:
    """Test the setter for the daily_milk_produced property of the MilkProduction class."""
    milk_production = MilkProduction()

    mocker.patch.object(milk_production, "_milk_production_variance", 0.0)
    mocker.patch.object(milk_production, "milk_production_reduction", 0.0)

    milk_production.daily_milk_produced = new_value

    assert milk_production._daily_milk_produced == new_value

    expected_value = new_value if new_value > 0.0 else 0.0
    assert milk_production.daily_milk_produced == expected_value


@pytest.mark.parametrize(
    "fat_percent, true_protein_percent, lactose_percent",
    [
        (3.5, 3.2, 4.8),  # Standard milk composition
        (4.0, 3.5, 5.0),  # Higher fat and protein
        (2.5, 2.8, 4.5),  # Lower fat and protein
    ],
)
def test_set_milk_quality(fat_percent: float, true_protein_percent: float, lactose_percent: float) -> None:
    """Test the set_milk_quality method of the MilkProduction class."""
    MilkProduction.set_milk_quality(fat_percent, true_protein_percent, lactose_percent)

    assert MilkProduction.fat_percent == fat_percent
    assert MilkProduction.true_protein_percent == true_protein_percent
    assert MilkProduction.lactose_percent == lactose_percent


@pytest.mark.parametrize(
    "wood_l, wood_m, wood_n",
    [
        (0.1, 0.5, 0.2),  # Standard values
        (0.2, 0.7, 0.3),  # Slightly higher values
        (0.05, 0.3, 0.1),  # Lower values
    ],
)
def test_set_wood_parameters(wood_l: float, wood_m: float, wood_n: float) -> None:
    """Test the set_wood_parameters method of the MilkProduction class."""
    milk_production = MilkProduction()

    milk_production.set_wood_parameters(wood_l, wood_m, wood_n)

    assert milk_production.wood_l == wood_l
    assert milk_production.wood_m == wood_m
    assert milk_production.wood_n == wood_n


@pytest.mark.parametrize(
    "days_in_milk, days_in_pregnancy, is_milking, expected_milk, expected_days_in_milk, should_add_dry_event",
    [
        (150, 200, True, 20.0, 151, False),  # Normal milking progression
        (0, 0, False, 0.0, 0, False),  # Not milking from start
        (304, 200, True, 18.5, 305, False),  # 305-day calculation update
        (200, AnimalConfig.dry_off_day_of_pregnancy, True, 0.0, 0, True),  # Dry-off day reached
    ],
)
def test_perform_daily_milking_update(
    mocker: MockerFixture,
    days_in_milk: int,
    days_in_pregnancy: int,
    is_milking: bool,
    expected_milk: float,
    expected_days_in_milk: int,
    should_add_dry_event: bool,
) -> None:
    """Test the perform_daily_milking_update method of the MilkProduction class."""
    milk_production = MilkProduction()
    milk_production.set_wood_parameters(0.1, 0.2, 0.3)

    mock_milk_inputs = mocker.MagicMock(spec=MilkProductionInputs)
    mock_milk_inputs.days_in_milk = days_in_milk
    mock_milk_inputs.days_in_pregnancy = days_in_pregnancy
    mock_milk_inputs.is_milking = is_milking
    mock_milk_inputs.days_born = 500

    mock_time = mocker.MagicMock(spec=RufasTime)
    mock_time.simulation_day = 1000

    mock_add_event = mocker.patch.object(AnimalEvents, "add_event")
    mocker.patch.object(milk_production, "calculate_daily_milk_production", return_value=expected_milk)
    mocker.patch.object(milk_production, "_calculate_nutrient_content", return_value=0.0)
    mocker.patch.object(milk_production, "_update_milking_history")
    mocker.patch.object(Utility, "generate_random_number", return_value=0.0)

    output = milk_production.perform_daily_milking_update(mock_milk_inputs, mock_time)

    assert isinstance(output, MilkProductionOutputs)
    assert output.days_in_milk == expected_days_in_milk
    assert milk_production.daily_milk_produced == expected_milk

    if should_add_dry_event:
        mock_add_event.assert_called_once_with(mock_milk_inputs.days_born, mock_time.simulation_day, DRY)
    else:
        mock_add_event.assert_not_called()


@pytest.fixture
def milk_production() -> MilkProduction:
    """Create a MilkProduction instance with basic required attributes set."""
    mp = MilkProduction()
    mp.crude_protein_percent = 0.03
    mp.true_protein_percent = 0.03
    mp.fat_percent = 0.04
    mp.lactose_percent = 0.05
    mp.wood_l = 1.0
    mp.wood_m = 2.0
    mp.wood_n = 3.0
    return mp


def test_perform_daily_milking_update_without_history_not_milking(
    milk_production: MilkProduction,
) -> None:
    """
    If the animal is not milking (days_in_milk == 0), daily milk is set to 0 and
    days_in_milk in the output is unchanged.
    """
    milk_production._daily_milk_produced = 10.0

    inputs = MilkProductionInputs(
        days_in_milk=0,
        days_born=100,
        days_in_pregnancy=50,
    )

    outputs = milk_production.perform_daily_milking_update_without_history(inputs)

    assert outputs.days_in_milk == 0
    assert milk_production._daily_milk_produced == 0.0


def test_perform_daily_milking_update_without_history_dry_off_day(
    milk_production: MilkProduction,
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
) -> None:
    """
    If today is the dry-off day, all milk/nutrient contents are zeroed and no
    further calculations are performed.
    """
    dry_off_day = 200
    monkeypatch.setattr(AnimalConfig, "dry_off_day_of_pregnancy", dry_off_day)
    milk_production._daily_milk_produced = 25.0
    milk_production.crude_protein_content = 1.0
    milk_production.true_protein_content = 1.0
    milk_production.fat_content = 1.0
    milk_production.lactose_content = 1.0
    milk_production.current_lactation_305_day_milk_produced = 123.0

    calc_daily_milk = mocker.patch.object(milk_production, "calculate_daily_milk_production")
    calc_nutrient = mocker.patch.object(milk_production, "_calculate_nutrient_content")
    rand_gen = mocker.patch.object(Utility, "generate_random_number")

    inputs = MilkProductionInputs(
        days_in_milk=50,
        days_born=400,
        days_in_pregnancy=dry_off_day,
    )

    outputs = milk_production.perform_daily_milking_update_without_history(inputs)

    assert outputs.days_in_milk == 50

    assert milk_production._daily_milk_produced == 0.0
    assert milk_production.crude_protein_content == 0.0
    assert milk_production.true_protein_content == 0.0
    assert milk_production.fat_content == 0.0
    assert milk_production.lactose_content == 0.0
    assert milk_production.current_lactation_305_day_milk_produced == 0.0

    calc_daily_milk.assert_not_called()
    calc_nutrient.assert_not_called()
    rand_gen.assert_not_called()


def test_perform_daily_milking_update_without_history_normal_milking_day(
    milk_production: MilkProduction,
    mocker: MockerFixture,
) -> None:
    """
    On a normal milking day (milking and not dry-off day), days_in_milk increments,
    daily milk is calculated, and nutrient contents are updated via _calculate_nutrient_content.
    """
    if AnimalConfig.dry_off_day_of_pregnancy > 0:
        days_in_pregnancy = AnimalConfig.dry_off_day_of_pregnancy - 1
    else:
        days_in_pregnancy = AnimalConfig.dry_off_day_of_pregnancy + 1

    inputs = MilkProductionInputs(
        days_in_milk=30,
        days_born=400,
        days_in_pregnancy=days_in_pregnancy,
    )

    mocker.patch.object(Utility, "generate_random_number", return_value=0.123)

    mocked_daily_milk = 35.0
    mock_calc_daily_milk = mocker.patch.object(
        milk_production,
        "calculate_daily_milk_production",
        return_value=mocked_daily_milk,
    )

    previous_crude_protein_content = milk_production.crude_protein_content

    mock_calc_nutrient = mocker.patch.object(
        milk_production,
        "_calculate_nutrient_content",
        side_effect=[1.1, 2.2, 3.3, 4.4],
    )

    outputs = milk_production.perform_daily_milking_update_without_history(inputs)

    assert outputs.days_in_milk == 31

    assert milk_production._daily_milk_produced == mocked_daily_milk

    assert milk_production.crude_protein_content == 1.1
    assert milk_production.true_protein_content == 2.2
    assert milk_production.fat_content == 3.3
    assert milk_production.lactose_content == 4.4

    mock_calc_daily_milk.assert_called_once_with(
        inputs.days_in_milk,
        milk_production.wood_l,
        milk_production.wood_m,
        milk_production.wood_n,
    )
    assert mock_calc_nutrient.call_count == 4

    calls = mock_calc_nutrient.call_args_list

    expected_daily_for_nutrients = milk_production.daily_milk_produced

    assert calls[0].args[0] == pytest.approx(expected_daily_for_nutrients)
    assert calls[0].args[1] == previous_crude_protein_content

    assert calls[1].args[0] == pytest.approx(expected_daily_for_nutrients)
    assert calls[1].args[1] == milk_production.true_protein_percent

    assert calls[2].args[0] == pytest.approx(expected_daily_for_nutrients)
    assert calls[2].args[1] == milk_production.fat_percent

    assert calls[3].args[0] == pytest.approx(expected_daily_for_nutrients)
    assert calls[3].args[1] == milk_production.lactose_percent


@pytest.mark.parametrize(
    "days_in_milk, l_param, m_param, n_param, expected_output",
    [
        (1, 25.0, 0.1, 0.002, 24.95),  # Day 1, no decay
        (50, 30.0, 0.2, 0.003, 56.463927489817394),  # Mid-lactation
        (150, 20.0, 0.3, 0.004, 49.34926448831275),  # Later stage
        (300, 15.0, 0.4, 0.005, 32.77162963540164),  # End of lactation
    ],
)
def test_calculate_daily_milk_production(
    days_in_milk: int, l_param: float, m_param: float, n_param: float, expected_output: float
) -> None:
    """
    Test the calculate_daily_milk_production method of the MilkProduction class.

    Note
    ----
    The function tested here uses the @njit decorator which obscures unit test coverage.
    """
    func = MilkProduction.calculate_daily_milk_production
    try:
        calc_func = func.py_func
    except AttributeError:
        calc_func = func

    result_raw = calc_func(days_in_milk, l_param, m_param, n_param)
    result = float(result_raw)

    assert isinstance(result, float)
    assert np.isclose(result, expected_output, rtol=1e-3)


@pytest.mark.parametrize(
    "l_param, m_param, n_param, expected",
    [
        (0.1, 0.2, 0.3, quad(MilkProduction.calculate_daily_milk_production, 1, 305, args=(0.1, 0.2, 0.3))[0]),
        (0.2, 0.3, 0.4, quad(MilkProduction.calculate_daily_milk_production, 1, 305, args=(0.2, 0.3, 0.4))[0]),
        (0.3, 0.4, 0.5, quad(MilkProduction.calculate_daily_milk_production, 1, 305, args=(0.3, 0.4, 0.5))[0]),
    ],
)
def test_calc_305_day_milk_yield(l_param: float, m_param: float, n_param: float, expected: float) -> None:
    """Test the calc_305_day_milk_yield method of the MilkProduction class."""
    assert MilkProduction.calc_305_day_milk_yield(l_param, m_param, n_param) == pytest.approx(expected, rel=1e-6)


@pytest.mark.parametrize(
    "random_value, milk_reduction, expected",
    [
        (1.2, 0.5, 0.7),
        (-0.3, 0.2, -0.5),
        (0.0, 0.0, 0.0),
    ],
)
def test_get_milk_production_adjustment(
    mocker: MockerFixture, random_value: float, milk_reduction: float, expected: float
) -> None:
    """Test the _get_milk_production_adjustment method of the MilkProduction class."""
    mocker.patch.object(Utility, "generate_random_number", return_value=random_value)

    milk_production = MilkProduction()
    milk_production.milk_production_reduction = milk_reduction
    result = milk_production._get_milk_production_adjustment()

    assert result == pytest.approx(expected, rel=1e-6)


@pytest.mark.parametrize(
    "milk, nutrient_percentage, expected",
    [
        (10.0, 3.5, 10.0 * 3.5 * GeneralConstants.PERCENTAGE_TO_FRACTION),
        (20.0, 4.0, 20.0 * 4.0 * GeneralConstants.PERCENTAGE_TO_FRACTION),
        (0.0, 5.0, 0.0),
        (15.0, 0.0, 0.0),
    ],
)
def test_calculate_nutrient_content(milk: float, nutrient_percentage: float, expected: float) -> None:
    """Test the _calculate_nutrient_content method of the MilkProduction class."""
    milk_production = MilkProduction()
    result = milk_production._calculate_nutrient_content(milk, nutrient_percentage)

    assert result == pytest.approx(expected, rel=1e-6)


def test_update_milking_history(mocker: MockerFixture) -> None:
    """Test the _update_milking_history method of the MilkProduction class."""
    mock_time = mocker.Mock()
    mock_time.simulation_day = 100

    milk_production = MilkProduction()
    milk_production.milk_production_history = []

    days_in_milk = 150
    daily_milk_produced = 25.5
    days_born = 500

    milk_production._update_milking_history(days_in_milk, daily_milk_produced, days_born, mock_time)

    assert len(milk_production.milk_production_history) == 1
    record = milk_production.milk_production_history[0]

    assert isinstance(record, dict)
    assert record["simulation_day"] == 100
    assert record["days_in_milk"] == days_in_milk
    assert record["milk_production"] == daily_milk_produced
    assert record["days_born"] == days_born
