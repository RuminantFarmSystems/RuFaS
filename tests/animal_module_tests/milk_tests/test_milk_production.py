import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal_constants import DRY
from RUFAS.biophysical.animal.animal_properties.general_properties import GeneralProperties
from RUFAS.biophysical.animal.animal_properties.milk_production_properties import MilkProductionProperties
from RUFAS.biophysical.animal.data_types.milk_production_record import MilkProductionRecord
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.time import Time
from RUFAS.util import Utility
from tests.animal_module_tests.general_property_values import LAC_COW_PROPERTIES


@pytest.fixture
def milking_properties() -> MilkProductionProperties:
    return MilkProductionProperties(
        crude_protein_content=1.7,
        true_protein_content=1.5,
        fat_content=2.0,
        lactose_content=3.0,
        milk_production_reduction=0.3,
        current_lactation_305_day_milk_produced=0.0,
        crude_protein_percent=3.2,
        true_protein_percent=3.0,
        fat_percent=3.5,
        lactose_percent=4.8,
        wood_l=29.0,
        wood_m=0.25,
        wood_n=0.003,
        milk_production_history=[],
    )


@pytest.fixture
def general_properties() -> GeneralProperties:
    return GeneralProperties(
        **LAC_COW_PROPERTIES, nutrient_concentrations={"dm": 0.23}, metabolizable_energy_intake=2.4
    )


@pytest.fixture
def time(mocker: MockerFixture) -> Time:
    mocker.patch.object(Time, "__init__", return_value=None)
    return Time()


def test_set_milk_quality() -> None:
    """Tests that milk quality class attributes are set correctly."""
    MilkProduction.set_milk_quality(1.0, 2.0)

    assert MilkProduction.FAT_PERCENT == 1.0
    assert MilkProduction.TRUE_PROTEIN_PERCENT == 2.0


def test_perform_daily_milking_update_not_milking(
    mocker: MockerFixture,
    milking_properties: MilkProductionProperties,
    general_properties: GeneralProperties,
    time: Time,
) -> None:
    """Tests that daily milking update is performed correctly when cow is not milking."""
    general_properties.days_in_milk = 0
    general_properties.daily_milk_produced = 0.0
    mocker.patch.object(Time, "simulation_day", new_callable=mocker.PropertyMock, return_value=100)
    expected_record = MilkProductionRecord(
        simulation_day=100, days_in_milk=0, milk_production=0.0, days_born=LAC_COW_PROPERTIES["days_born"]
    )
    milking_properties.milk_production_history = []

    milking_properties, actual_general = MilkProduction.perform_daily_milking_update(
        milking_properties, general_properties, time
    )

    assert actual_general == general_properties
    assert milking_properties.milk_production_history[-1] == expected_record


def test_perform_daily_milking_update_dry_off(
    mocker: MockerFixture,
    milking_properties: MilkProductionProperties,
    general_properties: GeneralProperties,
    time: Time,
) -> None:
    """Tests that daily milking update is performed correctly when cow stops milking."""
    general_properties.days_in_preg = general_properties.dry_off_day_of_pregnancy
    add_event = mocker.patch.object(general_properties.events, "add_event")
    mocker.patch.object(Time, "simulation_day", new_callable=mocker.PropertyMock, return_value=100)
    expected_record = MilkProductionRecord(
        simulation_day=100,
        days_in_milk=0,
        milk_production=0.0,
        days_born=LAC_COW_PROPERTIES["days_born"],
    )

    milking_properties, general_properties = MilkProduction.perform_daily_milking_update(
        milking_properties, general_properties, time
    )

    add_event.assert_called_once_with(general_properties.days_born, 100, DRY)
    assert general_properties.days_in_milk == 0
    assert general_properties.daily_milk_produced == 0.0
    assert milking_properties.crude_protein_content == 0.0
    assert milking_properties.true_protein_content == 0.0
    assert milking_properties.fat_content == 0.0
    assert milking_properties.lactose_content == 0.0
    assert milking_properties.current_lactation_305_day_milk_produced == 0.0
    assert milking_properties.crude_protein_percent == 0.0
    assert milking_properties.true_protein_percent == 0.0
    assert milking_properties.fat_percent == 0.0
    assert milking_properties.lactose_percent == 0.0
    assert milking_properties.milk_production_history[-1] == expected_record


@pytest.mark.parametrize(
    "days_in_milk,expected_days_in_milk,expected_305_day_production", [(200, 201, 0.0), (304, 305, 344.0)]
)
def test_perform_daily_milking_update(
    mocker: MockerFixture,
    milking_properties: MilkProductionProperties,
    general_properties: GeneralProperties,
    time: Time,
    days_in_milk: int,
    expected_days_in_milk: int,
    expected_305_day_production: float,
) -> None:
    """Tests perform_daily_milking_update when a cow is milking."""
    general_properties.days_in_milk = days_in_milk
    milking_properties.milk_production_history = [
        MilkProductionRecord(simulation_day=1, days_in_milk=100, milk_production=1.0, days_born=500) for _ in range(305)
    ]
    milking_properties.milk_production_reduction = -6.0
    expected_milk_produced = 40.0
    mocker.patch.object(MilkProduction, "calculate_daily_milk_production", return_value=45.0)
    mocker.patch.object(Utility, "generate_random_number", return_value=1.0)
    mocker.patch.object(Time, "simulation_day", new_callable=mocker.PropertyMock, return_value=500)
    expected_record = MilkProductionRecord(
        simulation_day=500,
        days_in_milk=expected_days_in_milk,
        milk_production=40.0,
        days_born=LAC_COW_PROPERTIES["days_born"],
    )

    milking_properties, general_properties = MilkProduction.perform_daily_milking_update(
        milking_properties, general_properties, time
    )

    assert general_properties.days_in_milk == expected_days_in_milk
    assert general_properties.daily_milk_produced == expected_milk_produced
    assert milking_properties.true_protein_content == 1.2
    assert pytest.approx(milking_properties.fat_content) == 1.4
    assert milking_properties.milk_production_history[-1] == expected_record
    assert milking_properties.current_lactation_305_day_milk_produced == expected_305_day_production


@pytest.mark.parametrize(
    "day,l_param,m_param,n_param,expected",
    [
        (1, 17.8, 0.229, 0.00331, 17.7411794),
        (40, 17.8, 0.229, 0.00331, 36.2903495),
        (200, 17.8, 0.229, 0.00331, 30.8924906),
        (305, 17.8, 0.229, 0.00331, 24.0371332),
    ],
)
def test_get_milk_yield_values_wood_curve(
    day: int, l_param: float, m_param: float, n_param: float, expected: float
) -> None:
    """Test that milk yield on a given day is estimated correctly."""
    actual = MilkProduction.calculate_daily_milk_production(day, l_param, m_param, n_param)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "l_param,m_param,n_param,expected",
    [(17.8, 0.229, 0.00331, 9745.195761), (19.9, 0.231, 0.00299, 11523.229036), (22.1, 0.334, 0.00400, 17955.511169)],
)
def test_calc_305_day_milk_yield(l_param: float, m_param: float, n_param: float, expected: float) -> None:
    """Test that 305 day milk yields are estimated correctly."""
    actual = MilkProduction.calc_305_day_milk_yield(l_param, m_param, n_param)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize("milk,reduction,variance,expected", [(30.0, -4.0, 2.0, 28.0), (28.0, 0.0, -1.0, 27.0)])
def test_adjust_milk_production(
    mocker: MockerFixture,
    milking_properties: MilkProductionProperties,
    general_properties: GeneralProperties,
    milk: float,
    reduction: float,
    variance: float,
    expected: float,
) -> None:
    """Test that milk production is varied correctly."""
    milking_properties.milk_production_reduction = reduction
    general_properties.daily_milk_produced = milk
    mocker.patch.object(Utility, "generate_random_number", return_value=variance)

    actual = MilkProduction._adjust_milk_production(milking_properties, general_properties)

    assert actual.daily_milk_produced == expected


@pytest.mark.parametrize("milk,nutrient,expected", [(30.0, 5.0, 1.5), (25.0, 0.0, 0.0), (20.0, 100.0, 20.0)])
def test_calculate_nutrient_content(milk: float, nutrient: float, expected: float) -> None:
    """Test that nutrient content of milk is calculated correctly."""
    actual = MilkProduction._calculate_nutrient_content(milk, nutrient)

    assert actual == expected


@pytest.mark.parametrize(
    "sim_day,milk_days,milk_produced,age,expected",
    [
        (
            100,
            30,
            25.0,
            300,
            MilkProductionRecord(simulation_day=100, days_in_milk=30, milk_production=25.0, days_born=300),
        ),
        (
            1000,
            300,
            20.0,
            800,
            MilkProductionRecord(simulation_day=1000, days_in_milk=300, milk_production=20.0, days_born=800),
        ),
    ],
)
def test_update_milking_history(
    mocker: MockerFixture,
    milking_properties: MilkProductionProperties,
    general_properties: GeneralProperties,
    time: Time,
    sim_day: int,
    milk_days: int,
    milk_produced: float,
    age: int,
    expected: MilkProductionRecord,
) -> None:
    """Tests that the milking history of a cow is updated correctly."""
    milking_properties.milk_production_history = []
    general_properties.days_in_milk = milk_days
    general_properties.daily_milk_produced = milk_produced
    general_properties.days_born = age
    mocker.patch.object(Time, "simulation_day", new_callable=mocker.PropertyMock, return_value=sim_day)

    milking_properties = MilkProduction._update_milking_history(milking_properties, general_properties, time)

    assert milking_properties.milk_production_history[-1] == expected
