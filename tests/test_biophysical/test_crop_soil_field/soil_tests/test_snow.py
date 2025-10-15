import math
from unittest.mock import MagicMock, patch

import pytest

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.field.soil.snow import Snow
from RUFAS.biophysical.field.soil.soil_data import SoilData


@pytest.fixture
def mock_om() -> OutputManager:
    return OutputManager()


@pytest.mark.parametrize(
    "soil_data, current_day_conditions",
    [
        (
            SoilData(previous_day_snow_temperature=-3.5, snow_lag_factor=1.0, field_size=10),
            CurrentDayConditions(
                incoming_light=11.3, min_air_temperature=-9, mean_air_temperature=-3, max_air_temperature=6
            ),
        ),
        (
            SoilData(previous_day_snow_temperature=-5, snow_lag_factor=1.0, field_size=10),
            CurrentDayConditions(
                incoming_light=11.3, min_air_temperature=-9, mean_air_temperature=-10, max_air_temperature=6
            ),
        ),
    ],
)
def test_calc_snow_temp(soil_data: SoilData, current_day_conditions: CurrentDayConditions):
    snow = Snow(soil_data=soil_data)

    if soil_data.previous_day_snow_temperature is None:
        expected_result = current_day_conditions.mean_air_temperature
    else:
        expected_result = (soil_data.previous_day_snow_temperature * (1 - soil_data.snow_lag_factor)) + (
            current_day_conditions.mean_air_temperature * soil_data.snow_lag_factor
        )

    actual_result = snow._calc_snow_temp(soil_data=soil_data, current_day_conditions=current_day_conditions)

    assert actual_result == expected_result


@pytest.mark.parametrize(
    "soil_data, current_day_conditions, day",
    [
        (
            SoilData(
                snow_content=20,
                current_day_snow_temperature=-3,
                snow_coverage_fraction=1.0,
                snow_melt_base_temperature=1.0,
                field_size=10,
            ),
            CurrentDayConditions(
                incoming_light=11.3, min_air_temperature=-3, mean_air_temperature=-3, max_air_temperature=-1
            ),
            15,
        ),
        (
            SoilData(
                snow_content=20,
                current_day_snow_temperature=3,
                snow_coverage_fraction=1.0,
                snow_melt_base_temperature=1.0,
                field_size=10,
            ),
            CurrentDayConditions(
                incoming_light=11.3, min_air_temperature=3, mean_air_temperature=3, max_air_temperature=5
            ),
            25,
        ),
        (
            SoilData(
                snow_content=0,
                current_day_snow_temperature=3,
                snow_coverage_fraction=1.0,
                snow_melt_base_temperature=1.0,
                field_size=10,
            ),
            CurrentDayConditions(
                incoming_light=11.3, min_air_temperature=3, mean_air_temperature=3, max_air_temperature=5
            ),
            25,
        ),
    ],
)
def test_melt_snow(
    soil_data: SoilData,
    current_day_conditions: CurrentDayConditions,
    day: int,
    mock_om: OutputManager,
):
    snow = Snow(soil_data=soil_data)

    melt_factor = 4.5
    snow_coverage_fraction = soil_data.snow_coverage_fraction
    expected_result = max(
        melt_factor
        * snow_coverage_fraction
        * (
            (soil_data.current_day_snow_temperature + current_day_conditions.max_air_temperature) / 2
            - soil_data.snow_melt_base_temperature
        ),
        0.0,
    )

    with patch.object(Snow, "_melt_factor", return_value=melt_factor) as mock_melt_factor:
        actual_result = snow._melt_snow(soil_data=soil_data, current_day_conditions=current_day_conditions, day=day)

    mock_melt_factor.assert_called_once_with(soil_data=soil_data, day=day)
    if expected_result > soil_data.snow_content:
        expected_result = soil_data.snow_content
    assert actual_result == expected_result


@pytest.mark.parametrize(
    "soil_data, day",
    [
        (
            SoilData(
                snow_melt_factor_maximum=4.5,
                snow_melt_factor_minimum=4.5,
                field_size=10,
            ),
            15,
        ),
        (
            SoilData(
                snow_melt_factor_maximum=4.5,
                snow_melt_factor_minimum=4.5,
                field_size=10,
            ),
            25,
        ),
    ],
)
def test_melt_factor(soil_data: SoilData, day: int):
    snow = Snow(soil_data=soil_data)

    expected_result = (soil_data.snow_melt_factor_maximum + soil_data.snow_melt_factor_minimum) / 2 + (
        (soil_data.snow_melt_factor_maximum - soil_data.snow_melt_factor_minimum)
        / 2
        * math.sin(2 * math.pi / 365)
        * (day - 81)
    )

    actual_result = snow._melt_factor(soil_data=soil_data, day=day)

    assert actual_result == expected_result


@pytest.mark.parametrize(
    "soil_data, current_day_conditions, day",
    [
        (
            SoilData(
                snow_content=-1,
                previous_day_snow_temperature=None,
                current_day_snow_temperature=-5,
                snow_lag_factor=1.0,
                snow_melt_base_temperature=1.0,
                snow_melt_factor_maximum=4.5,
                snow_melt_factor_minimum=4.5,
                snow_coverage_fraction=1.0,
                field_size=10,
            ),
            CurrentDayConditions(
                incoming_light=11.3,
                min_air_temperature=3,
                mean_air_temperature=-5,
                max_air_temperature=-1,
                snowfall=0.0,
            ),
            15,
        ),
        (
            SoilData(
                snow_content=-1,
                previous_day_snow_temperature=None,
                current_day_snow_temperature=None,
                snow_lag_factor=1.0,
                snow_melt_base_temperature=1.0,
                snow_melt_factor_maximum=4.5,
                snow_melt_factor_minimum=4.5,
                snow_coverage_fraction=1.0,
                field_size=10,
            ),
            CurrentDayConditions(
                incoming_light=11.3,
                min_air_temperature=3,
                mean_air_temperature=-5,
                max_air_temperature=-1,
                snowfall=1.0,
            ),
            25,
        ),
        (
            SoilData(
                snow_content=0.0,
                previous_day_snow_temperature=None,
                current_day_snow_temperature=-5,
                snow_lag_factor=1.0,
                snow_melt_base_temperature=1.0,
                snow_melt_factor_maximum=4.5,
                snow_melt_factor_minimum=4.5,
                snow_coverage_fraction=1.0,
                field_size=10,
            ),
            CurrentDayConditions(
                incoming_light=11.3,
                min_air_temperature=3,
                mean_air_temperature=-5,
                max_air_temperature=-1,
                snowfall=0.0,
            ),
            15,
        ),
        (
            SoilData(
                snow_content=0.0,
                previous_day_snow_temperature=None,
                current_day_snow_temperature=None,
                snow_lag_factor=1.0,
                snow_melt_base_temperature=1.0,
                snow_melt_factor_maximum=4.5,
                snow_melt_factor_minimum=4.5,
                snow_coverage_fraction=1.0,
                field_size=10,
            ),
            CurrentDayConditions(
                incoming_light=11.3,
                min_air_temperature=3,
                mean_air_temperature=-5,
                max_air_temperature=-1,
                snowfall=0.0,
            ),
            15,
        ),
        (
            SoilData(
                snow_content=0.0,
                previous_day_snow_temperature=None,
                current_day_snow_temperature=-5,
                snow_lag_factor=1.0,
                snow_melt_base_temperature=1.0,
                snow_melt_factor_maximum=4.5,
                snow_melt_factor_minimum=4.5,
                snow_coverage_fraction=1.0,
                field_size=10,
            ),
            CurrentDayConditions(
                incoming_light=11.3,
                min_air_temperature=3,
                mean_air_temperature=-5,
                max_air_temperature=-1,
                snowfall=1.0,
            ),
            15,
        ),
        (
            SoilData(
                snow_content=0.0,
                previous_day_snow_temperature=None,
                current_day_snow_temperature=None,
                snow_lag_factor=1.0,
                snow_melt_base_temperature=1.0,
                snow_melt_factor_maximum=4.5,
                snow_melt_factor_minimum=4.5,
                snow_coverage_fraction=1.0,
                field_size=10,
            ),
            CurrentDayConditions(
                incoming_light=11.3,
                min_air_temperature=3,
                mean_air_temperature=-5,
                max_air_temperature=-1,
                snowfall=1.0,
            ),
            15,
        ),
        (
            SoilData(
                snow_content=1.0,
                previous_day_snow_temperature=None,
                current_day_snow_temperature=-5,
                snow_lag_factor=1.0,
                snow_melt_base_temperature=1.0,
                snow_melt_factor_maximum=4.5,
                snow_melt_factor_minimum=4.5,
                snow_coverage_fraction=1.0,
                field_size=10,
            ),
            CurrentDayConditions(
                incoming_light=11.3,
                min_air_temperature=3,
                mean_air_temperature=-5,
                max_air_temperature=-1,
                snowfall=0.0,
            ),
            15,
        ),
        (
            SoilData(
                snow_content=1.0,
                previous_day_snow_temperature=None,
                current_day_snow_temperature=None,
                snow_lag_factor=1.0,
                snow_melt_base_temperature=1.0,
                snow_melt_factor_maximum=4.5,
                snow_melt_factor_minimum=4.5,
                snow_coverage_fraction=1.0,
                field_size=10,
            ),
            CurrentDayConditions(
                incoming_light=11.3,
                min_air_temperature=3,
                mean_air_temperature=-5,
                max_air_temperature=-1,
                snowfall=1.0,
            ),
            15,
        ),
    ],
)
def test_update_snow(soil_data: SoilData, current_day_conditions: CurrentDayConditions, day: int):
    snow = Snow(soil_data=soil_data)

    if soil_data.snow_content < 0.0:
        with pytest.raises(ValueError) as value_error:
            snow.update_snow(current_day_conditions=current_day_conditions, day=day)
        assert str(value_error.value) == "Snow Content should not be a negative number."

    elif soil_data.snow_content + current_day_conditions.snowfall == 0.0:
        snow.update_snow(current_day_conditions=current_day_conditions, day=day)
        assert soil_data.previous_day_snow_temperature is None
        assert soil_data.current_day_snow_temperature is None
        assert soil_data.snow_content == 0.0
        assert soil_data.snow_melt_amount == 0.0

    else:
        snow_content_before = soil_data.snow_content
        current_day_snow_temperature_before = soil_data.current_day_snow_temperature

        dummy_snow_temperature = current_day_conditions.mean_air_temperature
        dummy_melt_factor = 4.5
        snow_melt_amount = (
            dummy_melt_factor
            * soil_data.snow_coverage_fraction
            * (
                (dummy_snow_temperature + current_day_conditions.max_air_temperature) / 2
                - soil_data.snow_melt_base_temperature
            )
        )

        with patch.object(Snow, "_calc_snow_temp", return_value=dummy_snow_temperature) as mock_calc_snow_temp:
            with patch.object(Snow, "_melt_snow", return_value=snow_melt_amount) as mock_melt_snow:
                snow.update_snow(current_day_conditions=current_day_conditions, day=day)

        expected_previous_day_snow_temperature = (
            current_day_snow_temperature_before
            if current_day_snow_temperature_before is not None
            else current_day_conditions.mean_air_temperature
        )

        assert soil_data.previous_day_snow_temperature == expected_previous_day_snow_temperature
        mock_calc_snow_temp.assert_called_once_with(soil_data, current_day_conditions)
        assert soil_data.current_day_snow_temperature == dummy_snow_temperature
        mock_melt_snow.assert_called_once_with(soil_data, current_day_conditions, day)
        assert soil_data.snow_melt_amount == snow_melt_amount
        assert soil_data.snow_content == snow_content_before + current_day_conditions.snowfall - snow_melt_amount


@pytest.mark.parametrize(
    "max_sublimation,snow_content,expected_sublimation,expected_snow_content",
    [
        (10.0, 10.0, 10.0, 0.0),
        (14.0, 8.0, 8.0, 0.0),
        (5.0, 9.0, 5.0, 4.0),
        (11.0, 0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0, 0.0),
    ],
)
def test_sublimate(
    max_sublimation: float,
    snow_content: float,
    expected_sublimation: float,
    expected_snow_content,
) -> None:
    """Tests that water is correctly sublimated from the snow pack of a field."""
    mock_soil_data = MagicMock(SoilData)
    mock_soil_data.water_sublimated = 42.0
    mock_soil_data.snow_content = snow_content
    snow = Snow(mock_soil_data)

    snow.sublimate(max_sublimation)

    assert mock_soil_data.water_sublimated == expected_sublimation
    assert mock_soil_data.snow_content == expected_snow_content
