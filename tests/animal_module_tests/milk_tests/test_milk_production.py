import pytest

from RUFAS.biophysical.animal.milk.milk_production import MilkProduction


@pytest.fixture
def milk_production() -> MilkProduction:
    return MilkProduction()


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
    milk_production: MilkProduction, day: int, l_param: float, m_param: float, n_param: float, expected: float
) -> None:
    """Test that milk yield on a given day is estimated correctly."""
    actual = milk_production.calculate_daily_milk_production(day, l_param, m_param, n_param)

    assert pytest.approx(actual) == expected
