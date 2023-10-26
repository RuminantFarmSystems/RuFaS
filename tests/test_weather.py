import pytest

from RUFAS.weather import Weather


@pytest.mark.parametrize("avg_daily_temperatures,expected", [
    ([12.3, 20.4, 15.6, 20.5, 17.8], 17.32),
    ([-4.55, -3.22, -1.05, -0.3, 1.44, 3.99, 8.6], 0.7014285714285712)
])
def test_calculate_average_annual_temperature(avg_daily_temperatures: list[float], expected: float) -> None:
    """Tests that the annual average air temperature is correctly calculated based on average daily temperatures."""
    actual = Weather._calculate_average_annual_temperature(avg_daily_temperatures)
    assert actual == expected
