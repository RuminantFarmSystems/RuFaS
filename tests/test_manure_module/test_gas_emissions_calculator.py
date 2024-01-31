from __future__ import annotations

import math

import pytest
from pytest import approx
from pytest_mock import MockerFixture

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.manure.constants_and_units.gas_emission_constants import (
    GasEmissionConstants,
)
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.gas_emissions.calculator import GasEmissionsCalculator


def test_mcf() -> None:
    """Tests _methane_conversion_factor() in calculator.py."""
    assert GasEmissionsCalculator._methane_conversion_factor(1.0) == pytest.approx(
        (
                GasEmissionConstants.MCF_CONSTANT_A
                * math.exp(GasEmissionConstants.MCF_CONSTANT_B)
        )
    )


def test_ifsm_methane_emission(mocker: MockerFixture) -> None:
    """Tests _ifsm_methane_emission() in calculator.py."""

    # Arrange
    ambient_barn_temp = 1.0
    mcf = 1.0
    patch_for_ifsm_methane_emission = mocker.patch(
        "RUFAS.routines.manure.gas_emissions.calculator.GasEmissionsCalculator._methane_conversion_factor",
        return_value=mcf,
    )
    manure_volatile_solids = 1000.0
    expected = (manure_volatile_solids * 0.24 * 0.67 * 1.0) / 100

    # Actual
    actual = GasEmissionsCalculator.ifsm_methane_emission(
        manure_volatile_solids, ambient_barn_temp
    )

    # Assert
    patch_for_ifsm_methane_emission.assert_called_once_with(mcf)
    assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "daily_nitrogen_input, is_bedding_tilled, expected, expected_error",
    [
        # Standard cases
        (1.5, False, 0.375, None),
        (1.5, True, 0.75, None),
        # When daily_nitrogen_input is zero
        (0.0, False, 0.0, None),
        (0.0, True, 0.0, None),
        # When daily_nitrogen_input is negative
        (-1.5, False, None, ValueError),
        (-1.5, True, None, ValueError),
    ],
)
def test_nitrogen_loss_in_compost_bedded_pack_barn_due_to_ammonia_emission(
        daily_nitrogen_input: float,
        is_bedding_tilled: bool,
        expected: float,
        expected_error: type[Exception],
) -> None:
    """
    Unit test for nitrogen_loss_in_compost_bedded_pack_barn_from_ammonia_emission() method in calculator.py.

    This test verifies that the method correctly calculates the nitrogen loss from ammonia emission in a
    compost bedded pack barn given the daily nitrogen input and whether the bedding is tilled or not.
    """

    # Act and Assert
    if expected_error:
        with pytest.raises(expected_error):
            GasEmissionsCalculator.nitrogen_loss_in_compost_bedded_pack_barn_from_ammonia_emission(
                daily_nitrogen_input, is_bedding_tilled
            )
    else:
        actual = GasEmissionsCalculator.nitrogen_loss_in_compost_bedded_pack_barn_from_ammonia_emission(
            daily_nitrogen_input, is_bedding_tilled
        )
        assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "daily_nitrogen_input, expected, expected_error",
    [
        # Standard cases
        (1.5, 0.0525, None),
        # When daily_nitrogen_input is zero
        (0.0, 0.0, None),
        # When daily_nitrogen_input is negative
        (-1.5, None, ValueError),
    ],
)
def test_nitrogen_loss_in_compost_bedded_pack_barn_due_to_leaching(
        daily_nitrogen_input: float, expected: float, expected_error: type[Exception]
) -> None:
    """
    Unit test for _nitrogen_loss_from_leaching() method in calculator.py.

    This test verifies that the method correctly calculates the nitrogen loss due to leaching in a
    compost bedded pack barn given the daily nitrogen input.
    """

    # Act and Assert
    if expected_error:
        with pytest.raises(expected_error):
            GasEmissionsCalculator._nitrogen_loss_from_leaching(
                daily_nitrogen_input
            )
    else:
        actual = GasEmissionsCalculator._nitrogen_loss_from_leaching(
            daily_nitrogen_input
        )
        assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "daily_nitrogen_input, is_bedding_tilled, expected, expected_error",
    [
        # Standard cases with tilled and untilled bedding
        (1.5, True, 0.105, None),
        (1.5, False, 0.015, None),
        # When daily_nitrogen_input is zero
        (0.0, True, 0.0, None),
        (0.0, False, 0.0, None),
        # When daily_nitrogen_input is negative
        (-1.5, True, None, ValueError),
        (-1.5, False, None, ValueError),
    ],
)
def test_nitrogen_loss_in_compost_bedded_pack_barn_due_to_nitrous_oxide_emission(
        daily_nitrogen_input: float,
        is_bedding_tilled: bool,
        expected: float,
        expected_error: type[Exception],
) -> None:
    """
    Unit test for nitrogen_loss_in_compost_bedded_pack_barn_from_nitrous_oxide_emission() method in calculator.py.

    This test verifies that the method correctly calculates the nitrogen loss due to nitrous oxide emission in a
    compost bedded pack barn given the daily nitrogen input and whether the bedding is tilled or not.
    """

    # Act and Assert
    if expected_error:
        with pytest.raises(expected_error):
            GasEmissionsCalculator.nitrogen_loss_in_compost_bedded_pack_barn_from_nitrous_oxide_emission(
                daily_nitrogen_input, is_bedding_tilled
            )
    else:
        actual = GasEmissionsCalculator.nitrogen_loss_in_compost_bedded_pack_barn_from_nitrous_oxide_emission(
            daily_nitrogen_input, is_bedding_tilled
        )
        assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "daily_nitrogen_input, is_bedding_tilled, expected_ammonia,"
    "expected_nitrous_oxide, expected_leaching, expected_error",
    [
        # Standard cases
        (1.5, True, 0.75, 0.105, 0.0525, None),
        (1.5, False, 0.375, 0.015, 0.0525, None),
        # When daily_nitrogen_input is zero
        (0.0, True, 0.0, 0.0, 0.0, None),
        (0.0, False, 0.0, 0.0, 0.0, None),
        # When daily_nitrogen_input is negative
        (-1.5, True, None, None, None, ValueError),
        (-1.5, False, None, None, None, ValueError),
    ],
)
def test_total_nitrogen_loss_from_compost_bedded_pack_barn(
        daily_nitrogen_input: float,
        is_bedding_tilled: bool,
        expected_ammonia: float,
        expected_nitrous_oxide: float,
        expected_leaching: float,
        expected_error: type[Exception],
        mocker: MockerFixture,
) -> None:
    """
    Unit test for the `total_nitrogen_loss_from_compost_bedded_pack_barn` method in calculator.py.

    This test verifies that the method correctly calculates the total nitrogen loss from a compost
    bedded pack barn, given the daily nitrogen input and whether the bedding is tilled or not.
    It checks for both valid inputs and invalid (negative) nitrogen input scenarios.
    """

    # Arrange
    mocker.patch(
        "RUFAS.routines.manure.gas_emissions.calculator.GasEmissionsCalculator"
        ".nitrogen_loss_in_compost_bedded_pack_barn_from_ammonia_emission",
        return_value=expected_ammonia,
    )
    mocker.patch(
        "RUFAS.routines.manure.gas_emissions.calculator.GasEmissionsCalculator"
        "._nitrogen_loss_from_leaching",
        return_value=expected_leaching,
    )
    mocker.patch(
        "RUFAS.routines.manure.gas_emissions.calculator.GasEmissionsCalculator."
        "nitrogen_loss_in_compost_bedded_pack_barn_from_nitrous_oxide_emission",
        return_value=expected_nitrous_oxide,
    )

    # Act & Assert
    if expected_error:
        with pytest.raises(expected_error):
            GasEmissionsCalculator.total_nitrogen_loss_from_compost_bedded_pack_barn(
                daily_nitrogen_input, is_bedding_tilled
            )
    else:
        total_nitrogen_loss = (
            GasEmissionsCalculator.total_nitrogen_loss_from_compost_bedded_pack_barn(
                daily_nitrogen_input, is_bedding_tilled
            )
        )
        expected = expected_ammonia + expected_leaching + expected_nitrous_oxide
        assert total_nitrogen_loss == pytest.approx(expected)


@pytest.mark.parametrize("temperature", [-10.0, 0.0, 10.0])
def test_microbial_decomp_rate(temperature: float) -> None:
    """Tests _microbial_decomp_rate() in calculator.py."""
    assert GasEmissionsCalculator._microbial_decomp_rate(temperature) == pytest.approx(
        2.37e-3
        * (math.pow(1.066, (temperature - 10)) - math.pow(1.21, (temperature - 50)))
    )


@pytest.mark.parametrize("days_since_last_tillage, lag", [(1, 1), (10, 2), (1, 3)])
def test_carbon_decomposition_rate(
        mocker: MockerFixture, days_since_last_tillage: int, lag: int
) -> None:
    """Tests _carbon_decomposition_rate() in calculator.py."""

    # Arrange
    max_decomp_rate = 2.0
    min_decomp_rate = 1.0
    mocker.patch(
        "RUFAS.routines.manure.gas_emissions.calculator.GasEmissionsCalculator._microbial_decomp_rate",
        side_effect=[max_decomp_rate, min_decomp_rate],
    )
    expected = math.exp(0.1 * (days_since_last_tillage - lag))

    assert GasEmissionsCalculator._carbon_decomposition_rate(
        days_since_last_tillage, lag
    ) == pytest.approx(expected)


@pytest.mark.parametrize(
    "oxygen_mole_fraction, oxygen_ambient_air_mole_fraction, should_throw",
    [
        (-1.0, 0.21, True),
        (2.0, 0.21, True),
        (0.15, -1.0, True),
        (0.15, 2.0, True),
        (0.15, 0.21, False),
    ],
)
def test_aneerobic_coefficient(
        oxygen_mole_fraction: float,
        oxygen_ambient_air_mole_fraction: float,
        should_throw: bool,
) -> None:
    """Tests _aneerobic_coefficient() in calculator.py."""
    if should_throw:
        with pytest.raises(ValueError):
            GasEmissionsCalculator._anaerobic_effect(
                oxygen_mole_fraction=oxygen_mole_fraction,
                oxygen_ambient_air_mole_fraction=oxygen_ambient_air_mole_fraction,
            )
    else:
        expected = (oxygen_mole_fraction / (0.02 + oxygen_mole_fraction)) * (
                (0.02 + oxygen_ambient_air_mole_fraction) / oxygen_ambient_air_mole_fraction
        )
        assert GasEmissionsCalculator._anaerobic_effect(
            oxygen_mole_fraction=oxygen_mole_fraction,
            oxygen_ambient_air_mole_fraction=oxygen_ambient_air_mole_fraction,
        ) == pytest.approx(expected)


def test_total_carbon_decomposition(mocker: MockerFixture) -> None:
    """Tests total_carbon_decomposition() in calculator.py."""
    total_solids = 10.0
    bedding_mass = 100.0
    days_since_last_tillage = 1
    lag = 1
    c_decomp_rate = 1.0
    anaerobic_effect = 1.0
    mocker.patch(
        "RUFAS.routines.manure.gas_emissions.calculator.GasEmissionsCalculator._carbon_decomposition_rate",
        return_value=c_decomp_rate,
    )
    mocker.patch(
        "RUFAS.routines.manure.gas_emissions.calculator.GasEmissionsCalculator._anaerobic_effect",
        return_value=anaerobic_effect,
    )
    expected = (
            (total_solids * 0.5 + bedding_mass * 0.35)
            * c_decomp_rate
            * 0.65
            * anaerobic_effect
    )

    assert GasEmissionsCalculator.total_carbon_decomposition(
        total_solids, bedding_mass, days_since_last_tillage, lag
    ) == pytest.approx(expected)


@pytest.mark.parametrize("hours", [hour for hour in range(0, 24)])
def test_modified_hours(hours: float) -> None:
    """Tests _modified_hours() in calculator.py."""

    # Arrange
    if hours > 14:
        expected = -math.tanh(hours - 21.5) / 3.5
    elif hours > 4:
        expected = math.tanh(hours - 9.5) / 2.5
    else:
        expected = -math.tanh(hours + 3.5) / 3.5

    # Act
    actual = GasEmissionsCalculator._modified_hours(hours)

    # Assert
    assert actual == expected


def test_ambient_temp(mocker: MockerFixture) -> None:
    """Tests _ambient_temp() in calculator.py."""

    # Arrange
    hours = 10.0
    modified_hours = 8.0
    patch_for_modified_hours = mocker.patch(
        "RUFAS.routines.manure.gas_emissions.calculator.GasEmissionsCalculator._modified_hours",
        return_value=modified_hours,
    )
    t_min = 20.0
    t_max = 30.0
    expected = modified_hours * (t_max - t_min) / 2 + (t_max + t_min) / 2

    # Act
    actual = GasEmissionsCalculator._ambient_temperature(hours, t_min, t_max)

    # Assert
    patch_for_modified_hours.assert_called_once_with(hours)
    assert actual == expected


@pytest.mark.parametrize(
    "num_animals, barn_area, barn_temp, expected, error_message",
    [
        (
                10,
                100.0,
                25.0,
                10 * (0.0065 + 0.0192 * 25.0) * 100.0 / 1000,
                None,
        ),  # Standard case
        (0, 100.0, 25.0, 0, None),  # Edge case: no animals
        (10, 0.0, 25.0, 0, None),  # Edge case: no area
        (10, 100.0, -20.0, 0, None),  # Edge case: negative barn_temp
        (
                -1,
                100.0,
                25.0,
                ValueError,
                "Number of animals must be greater than or equal to 0.",
        ),
        # Exception case: negative number of animals
        (10, -100.0, 25.0, ValueError, "Barn area must be greater than or equal to 0."),
        # Exception case: negative barn area
    ],
)
def test_housing_carbon_dioxide_emission(
        num_animals: int,
        barn_area: float,
        barn_temp: float,
        expected: float | Exception,
        error_message: str | None,
) -> None:
    """
    Unit test for housing_carbon_dioxide_emission() method in calculator.py.

    This test verifies that the method correctly calculates the carbon dioxide housing emissions
    given the number of animals, the barn area, and the current barn temperature.

    """
    # Act and assert
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected, match=error_message):  # type: ignore
            GasEmissionsCalculator.housing_carbon_dioxide_emission(
                num_animals, barn_area, barn_temp
            )
    else:
        actual = GasEmissionsCalculator.housing_carbon_dioxide_emission(
            num_animals, barn_area, barn_temp
        )
        assert actual == pytest.approx(expected)


def test_ammonia_resistance() -> None:
    """Tests _ammonia_resistance() in calculator.py."""

    # Arrange
    tempC = 15.0
    hsc = GasEmissionConstants.HOUSING_HSC
    expected = hsc * (1 - 0.027 * (20.0 - tempC))

    # Act
    actual = GasEmissionsCalculator._ammonia_resistance(tempC, hsc)

    # Assert
    assert actual == expected


def test_Kh() -> None:
    """Tests _Kh() in calculator.py."""

    # Arrange
    tempK = 293.15
    expected = 10 ** (1478 / tempK - 1.69)

    # Act
    actual = GasEmissionsCalculator._henry_law_coefficient_of_ammonia(tempK)

    # Assert
    assert actual == expected


def test_Ka() -> None:
    """Tests _Ka() in calculator.py."""

    # Arrange
    tempK = 293.15
    pH = 9.0
    expected = 1 + 10 ** (0.09018 + 2729.9 / tempK - pH)

    # Act
    actual = GasEmissionsCalculator._dissociation_coefficient_of_ammonium(tempK, pH)

    # Assert
    assert actual == expected


def test_Q(mocker: MockerFixture) -> None:
    """Tests _Q() in calculator.py."""

    # Arrange
    tempK = 293.15
    pH = 9.0
    Kh = 10.0
    patch_for_Kh = mocker.patch(
        "RUFAS.routines.manure.gas_emissions.calculator.GasEmissionsCalculator._henry_law_coefficient_of_ammonia",
        return_value=Kh,
    )
    Ka = 20.0
    patch_for_Ka = mocker.patch(
        "RUFAS.routines.manure.gas_emissions.calculator.GasEmissionsCalculator._dissociation_coefficient_of_ammonium",
        return_value=Ka,
    )
    expected = Kh * Ka

    # Act
    actual = GasEmissionsCalculator._equilibrium_coefficient(tempK, pH)

    # Assert
    assert actual == expected
    patch_for_Kh.assert_called_once_with(tempK)
    patch_for_Ka.assert_called_once_with(tempK, pH)


def test_convert_tempC_to_tempK() -> None:
    """Tests _convert_temperature_celsius_to_kelvin() in calculator.py."""

    # Arrange
    tempC = 15.0
    expected = tempC + 273.15

    # Act
    actual = GasEmissionsCalculator._convert_temperature_celsius_to_kelvin(tempC)

    # Assert
    assert actual == expected


def test_methane_volume_via_Chen_equation() -> None:
    """Tests _methane_volume_via_Chen_equation() in calculator.py."""

    # Arrange
    VS_total = 10.0
    hydraulic_retention_time = 20
    expected = (
            GasEmissionConstants.METHANE_POTENTIAL_Go
            * (
                    1
                    - GasEmissionConstants.CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH
                    / (
                            hydraulic_retention_time * GasEmissionConstants.SPECIFIC_GROWTH_RATE
                            + GasEmissionConstants.CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH
                            - 1
                    )
            )
            * VS_total
            * GeneralConstants.GRAMS_TO_KG
    )

    # Act
    actual = GasEmissionsCalculator.methane_volume_via_Chen_equation(
        VS_total, hydraulic_retention_time
    )

    # Assert
    assert actual == expected


def test_biogas_energy_content() -> None:
    """Tests biogas_energy_content() in calculator.py."""

    # Arrange
    CH4_volume = 10.0
    expected = (
            CH4_volume
            * GasEmissionConstants.METHANE_DENSITY
            * GasEmissionConstants.METHANE_ENERGY_DENSITY
    )

    # Act
    actual = GasEmissionsCalculator.biogas_energy_content(CH4_volume)

    # Assert
    assert actual == expected


def test_methane_emission_for_anaerobic_lagoon() -> None:
    """Tests methane_emission_for_anaerobic_lagoon() in calculator.py."""

    # Arrange
    manure_volatile_solids = 10.0
    expected = (
            manure_volatile_solids
            * GasEmissionConstants.ACHIEVABLE_METHANE_EMISSION
            * GasEmissionConstants.METHANE_CONVERSION_FACTOR
            * GasEmissionConstants.FRACTION_OF_HANDLED_MANURE
            * GasEmissionConstants.METHANE_FACTOR
    )

    # Act
    actual = GasEmissionsCalculator.methane_emission_from_anaerobic_lagoon(
        manure_volatile_solids
    )

    # Assert
    assert actual == approx(expected)


@pytest.mark.parametrize(
    "num_animals, barn_area, barn_temp, expected, error_message",
    [
        (
                10,
                100.0,
                30.0,
                10 * max(0.0, 0.13 * 30.0) * 100.0 / 1000,
                None,
        ),  # Standard case
        (0, 100.0, 30.0, 0, None),  # Edge case: no animals
        (10, 0.0, 30.0, 0, None),  # Edge case: no area
        (10, 100.0, -20.0, 0, None),  # Edge case: negative barn_temp
        # Exception case: negative number of animals
        (
                -1,
                100.0,
                30.0,
                ValueError,
                "Number of animals must be greater than or equal to 0.",
        ),
        # Exception case: negative barn area
        (10, -100.0, 30.0, ValueError, "Barn area must be greater than or equal to 0."),
    ],
)
def test_housing_methane_emission(
        num_animals: int,
        barn_area: float,
        barn_temp: float,
        expected: float | Exception,
        error_message: str | None,
) -> None:
    """
    Unit test for housing_methane_emission() method in calculator.py.

    This test verifies that the method correctly calculates the methane housing emissions
    given the number of animals, the barn area, and the current barn temperature.

    """
    # Act and assert
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected, match=error_message):  # type: ignore
            GasEmissionsCalculator.housing_methane_emission(
                num_animals, barn_area, barn_temp
            )
    else:
        actual = GasEmissionsCalculator.housing_methane_emission(
            num_animals, barn_area, barn_temp
        )
        assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "num_animals, barn_area, urine_tan, urine, temp, pH, hsc, expected, error_message",
    [
        # Standard case
        (10, 100.0, 25.0, 30.0, 20.0, 7.7, 260.0, 2372.453635832584, None),
        # Edge cases: Zero input values for num_animals, barn_area, urine_tan, urine
        (0, 100.0, 25.0, 30.0, 20.0, 7.7, 260.0, 0.0, None),
        (10, 0.0, 25.0, 30.0, 20.0, 7.7, 260.0, 0.0, None),
        (10, 100.0, 0.0, 30.0, 20.0, 7.7, 260.0, 0.0, None),
        (10, 100.0, 25.0, 0.0, 20.0, 7.7, 260.0, 0.0, None),
        # Exception cases: Negative input values for num_animals, barn_area, urine_tan, urine
        (
                -1,
                100.0,
                25.0,
                30.0,
                20.0,
                7.7,
                260.0,
                ValueError,
                "Number of animals must be greater than or equal to 0.",
        ),
        (
                10,
                -100.0,
                25.0,
                30.0,
                20.0,
                7.7,
                260.0,
                ValueError,
                "Barn area must be greater than or equal to 0.",
        ),
        (
                10,
                100.0,
                -25.0,
                30.0,
                20.0,
                7.7,
                260.0,
                ValueError,
                "Manure total ammoniacal nitrogen must be greater than or equal to 0.",
        ),
        (
                10,
                100.0,
                25.0,
                -30.0,
                20.0,
                7.7,
                260.0,
                ValueError,
                "Manure must be greater than or equal to 0.",
        ),
    ],
)
def test_housing_ammonia_emission(
        num_animals: int,
        barn_area: float,
        urine_tan: float,
        urine: float,
        temp: float,
        pH: float,
        hsc: float,
        expected: float | Exception,
        error_message: str | None,
) -> None:
    """
    Unit test for housing_ammonia_emission() method in calculator.py.

    This test verifies that the method correctly calculates the ammonia housing emissions
    given the number of animals, the barn area, urine total ammoniacal nitrogen, urine, temperature,
    pH and housing-specific constant.

    """
    # Act and assert
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected, match=error_message):  # type: ignore
            GasEmissionsCalculator.housing_ammonia_emission(
                num_animals, barn_area, urine_tan, urine, temp, pH, hsc
            )
    else:
        actual = GasEmissionsCalculator.housing_ammonia_emission(
            num_animals, barn_area, urine_tan, urine, temp, pH, hsc
        )
        assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "temp, expected, error_message",
    [
        # Standard case
        (20.0, 0.05443994340019855, None),
        # Edge cases: Lower and upper bound temperatures
        (-40.0, 3.6974151606958807e-07, None),
        (60.0, 14.031085750034068, None),
        # Exception case: Temperature outside the defined range
        (
                -41.0,
                ValueError,
                "Temperature must be between -40 and 60 degrees Celsius. Temperature provided: -41.0",
        ),
        (
                61.0,
                ValueError,
                "Temperature must be between -40 and 60 degrees Celsius. Temperature provided: 61.0",
        ),
    ],
)
def test_arrhenius_exponent(
        mocker: MockerFixture,
        temp: float,
        expected: float | Exception,
        error_message: str | None,
) -> None:
    """
    Unit test for _arrhenius_exponent() method in calculator.py.

    This test verifies that the method correctly calculates the Arrhenius exponent
    given the temperature. It also checks that the method raises an exception for temperatures
    outside the range of -40.0 to 60.0 degrees Celsius.

    """
    # Arrange
    temp_kelvin = temp + 273.15
    patch_for_convert_temp = mocker.patch(
        "RUFAS.routines.manure.gas_emissions.calculator"
        ".GasEmissionsCalculator._convert_temperature_celsius_to_kelvin",
        return_value=temp_kelvin,
    )

    # Act and Assert
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected, match=error_message):  # type: ignore
            GasEmissionsCalculator._arrhenius_exponent(temp)
        if (
                GasEmissionConstants.GENERAL_LOWER_BOUND_TEMPERATURE
                <= temp
                <= GasEmissionConstants.GENERAL_UPPER_BOUND_TEMPERATURE
        ):
            patch_for_convert_temp.assert_called_once_with(temp)
    else:
        actual = GasEmissionsCalculator._arrhenius_exponent(temp)
        assert actual == approx(expected, rel=1e-6)
        patch_for_convert_temp.assert_called_once_with(temp)


@pytest.mark.parametrize(
    "total_volatile_solids, expected, error_message",
    [
        # Standard case
        (1.0, (0.5, 0.5), None),
        (45.0, (22.5, 22.5), None),
        # Edge cases: Zero and very large volatile solids
        (0.0, (0.0, 0.0), None),
        (1e6, (5e5, 5e5), None),
        # Exception case: Negative volatile solids
        (
                -1.0,
                ValueError,
                "Total volatile solids must be non-negative. Total volatile solids provided: -1.0",
        ),
    ],
)
def test_volatile_solid_components(
        total_volatile_solids: float,
        expected: tuple[float, float] | Exception,
        error_message: str | None,
) -> None:
    """
    Unit test for _volatile_solid_components() method in calculator.py.

    This test verifies that the method correctly calculates the degradable and non-degradable
    volatile solids given the total volatile solids. It also checks that the method raises an
    exception for total volatile solids that are negative.

    """
    # Act and assert
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected, match=error_message):
            GasEmissionsCalculator._volatile_solid_components(total_volatile_solids)
    else:
        actual = GasEmissionsCalculator._volatile_solid_components(
            total_volatile_solids
        )
        assert actual == approx(expected, rel=1e-6)


@pytest.mark.parametrize(
    "total_volatile_solids, temp, expected, error_message",
    [
        # Standard case
        (1.0, 20.0, 4.848, None),
        (10.0, 20.0, 4.848, None),
        # Edge case: Zero total volatile solids
        (0.0, 20.0, 0.0, None),
        # Case when temperature is not provided, default should be used
        (1.0, None, 4.848, None),
        # Exception case: Negative total volatile solids
        (
                -1.0,
                20.0,
                ValueError,
                "Total volatile solids must be greater than 0. Total volatile solids provided: -1.0",
        ),
    ],
)
def test_methane_emission_from_slurry_storage(
        mocker: MockerFixture,
        total_volatile_solids: float,
        temp: float | None,
        expected: float | Exception,
        error_message: str | None,
) -> None:
    """
    Unit test for methane_emission_from_slurry_storage() method in calculator.py.

    This test verifies that the method correctly calculates the methane emission from manure storage
    given the total volatile solids and temperature. It also checks that the method raises an exception for
    total volatile solids that are negative.

    """
    # Arrange
    patch_for_arrhenius_exponent = mocker.patch(
        "RUFAS.routines.manure.gas_emissions.calculator.GasEmissionsCalculator._arrhenius_exponent",
        return_value=0.2,  # Dummy return value
    )
    patch_for_volatile_solid_components = mocker.patch(
        "RUFAS.routines.manure.gas_emissions.calculator.GasEmissionsCalculator._volatile_solid_components",
        return_value=(1.0, 1.0)
        if total_volatile_solids != 0.0
        else (0.0, 0.0),  # Dummy return value
    )

    # Act and assert
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected, match=error_message):
            GasEmissionsCalculator.methane_emission_from_slurry_storage(
                total_volatile_solids, temp
            )
    else:
        if temp is None:
            actual = GasEmissionsCalculator.methane_emission_from_slurry_storage(
                total_volatile_solids
            )
        else:
            actual = GasEmissionsCalculator.methane_emission_from_slurry_storage(
                total_volatile_solids, temp
            )
        assert actual == approx(expected, rel=1e-6)

        patch_for_arrhenius_exponent.assert_called_once_with(
            temp
            if temp is not None
            else GasEmissionConstants.DEFAULT_SLURRY_STORAGE_TEMPERATURE
        )
        patch_for_volatile_solid_components.assert_called_once_with(
            total_volatile_solids
        )


@pytest.mark.parametrize(
    "num_animals, storage_area, manure_tan, manure_volume, manure_density,"
    "total_solids, temp, pH, expected, error_message",
    [
        # Standard case
        (10, 100.0, 25.0, 30.0, 1000.0, 5.0, 20.0, 7.7, 151.99329115002092, None),
        # Edge cases: Zero input values for num_animals, storage_area,
        # manure_tan, manure_volume, manure_density, total_solids
        (0, 100.0, 25.0, 30.0, 1000.0, 5.0, 20.0, 7.7, 0.0, None),
        (10, 0.0, 25.0, 30.0, 1000.0, 5.0, 20.0, 7.7, 0.0, None),
        (10, 100.0, 0.0, 30.0, 1000.0, 5.0, 20.0, 7.7, 0.0, None),
        (10, 100.0, 25.0, 0.0, 1000.0, 5.0, 20.0, 7.7, 0.0, None),
        (10, 100.0, 25.0, 30.0, 0.0, 5.0, 20.0, 7.7, 0.0, None),
        (10, 100.0, 25.0, 30.0, 1000.0, 0.0, 20.0, 7.7, 0.0, None),
        # Exception cases: Negative input values for num_animals, storage_area,
        # manure_tan, manure_volume, manure_density, total_solids
        (
                -1,
                100.0,
                25.0,
                30.0,
                1000.0,
                5.0,
                20.0,
                7.7,
                ValueError,
                "Number of animals must be greater than or equal to 0.",
        ),
        (
                10,
                -100.0,
                25.0,
                30.0,
                1000.0,
                5.0,
                20.0,
                7.7,
                ValueError,
                "Storage area per animal must be greater than or equal to 0.",
        ),
        (
                10,
                100.0,
                -25.0,
                30.0,
                1000.0,
                5.0,
                20.0,
                7.7,
                ValueError,
                "Manure total ammoniacal nitrogen must be greater than or equal to 0.",
        ),
        (
                10,
                100.0,
                25.0,
                -30.0,
                1000.0,
                5.0,
                20.0,
                7.7,
                ValueError,
                "Manure volume must be greater than or equal to 0.",
        ),
        (
                10,
                100.0,
                25.0,
                30.0,
                -1000.0,
                5.0,
                20.0,
                7.7,
                ValueError,
                "Manure density must be greater than or equal to 0.",
        ),
        (
                10,
                100.0,
                25.0,
                30.0,
                1000.0,
                -5.0,
                20.0,
                7.7,
                ValueError,
                "Total solids must be greater than or equal to 0.",
        ),
    ],
)
def test_storage_ammonia_emission(
        num_animals: int,
        storage_area: float,
        manure_tan: float,
        manure_volume: float,
        manure_density: float,
        total_solids: float,
        temp: float,
        pH: float,
        expected: float | Exception,
        error_message: str | None,
) -> None:
    """
    Unit test for storage_ammonia_emission() method in calculator.py.

    This test verifies that the method correctly calculates the ammonia storage emissions
    given the number of animals, the storage area, manure total ammoniacal nitrogen, manure volume,
    manure density, total solids, temperature, and pH.

    """
    # Act and assert
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected, match=error_message):  # type: ignore
            GasEmissionsCalculator.storage_ammonia_emission(
                num_animals,
                manure_tan,
                manure_volume,
                manure_density,
                total_solids,
                temp,
                storage_area,
                pH,
            )
    else:
        actual = GasEmissionsCalculator.storage_ammonia_emission(
            num_animals,
            manure_tan,
            manure_volume,
            manure_density,
            total_solids,
            temp,
            storage_area,
            pH,
        )
        assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "daily_nitrogen_input, expected_output, expect_exception",
    [
        (0, 0, False),
        (10, GasEmissionConstants.NITROUS_OXIDE_COEFFICIENT_IN_OPEN_LOTS * 10, False),
        (1000, GasEmissionConstants.NITROUS_OXIDE_COEFFICIENT_IN_OPEN_LOTS * 1000, False),
        (-1, None, True),
        (-10, None, True),
    ]
)
def test_nitrogen_loss_in_open_lots_from_nitrous_oxide_emission(daily_nitrogen_input: float,
                                                                expected_output: float,
                                                                expect_exception: bool) -> None:
    """
    Unit test for nitrogen_loss_in_open_lots_from_nitrous_oxide_emission() method in calculator.py.
    """

    if expect_exception:
        with pytest.raises(ValueError):
            GasEmissionsCalculator.nitrogen_loss_in_open_lots_from_nitrous_oxide_emission(daily_nitrogen_input)
    else:
        assert GasEmissionsCalculator.nitrogen_loss_in_open_lots_from_nitrous_oxide_emission(
            daily_nitrogen_input) == expected_output


@pytest.mark.parametrize(
    "daily_nitrogen_input, expected_output, expect_exception",
    [
        (0, 0, False),
        (10, GasEmissionConstants.AMMONIA_EMISSION_COEFFICIENT_IN_OPEN_LOTS * 10, False),
        (1000, GasEmissionConstants.AMMONIA_EMISSION_COEFFICIENT_IN_OPEN_LOTS * 1000, False),
        (-1, None, True),
        (-10, None, True),
    ]
)
def test_nitrogen_loss_in_open_lots_from_ammonia_emission(daily_nitrogen_input: float,
                                                          expected_output: float,
                                                          expect_exception: bool) -> None:
    """
    Unit test for nitrogen_loss_in_open_lots_from_ammonia_emission() method in calculator.py.
    """

    if expect_exception:
        with pytest.raises(ValueError):
            GasEmissionsCalculator.nitrogen_loss_in_open_lots_from_ammonia_emission(daily_nitrogen_input)
    else:
        assert GasEmissionsCalculator.nitrogen_loss_in_open_lots_from_ammonia_emission(
            daily_nitrogen_input) == expected_output
