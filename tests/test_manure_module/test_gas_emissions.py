from __future__ import annotations

import math

import pytest
from pytest import approx
from pytest_mock import MockerFixture

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.manure.constants.gas_emission_constants import GasEmissionConstants
from RUFAS.routines.manure.constants.manure_constants import ManureConstants
from RUFAS.routines.manure.gas_emissions.gas_emissions import GasEmissions


@pytest.mark.parametrize('is_enclosed', [True, False])
def test_calc_E_CH4_slurry_storage(is_enclosed: bool, mocker: MockerFixture) -> None:
    """Tests calc_methane_emission_for_slurry_storage() in gas_emissions.py."""

    # Arrange
    manure_total_solids = 1000.0
    tempC = 15.0
    tempK = 288.15
    patch_for_convert_tempC_to_tempK = mocker.patch(
        'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._convert_temperature_celsius_to_kelvin',
        return_value=tempK,
    )
    manure_volatile_solids_fraction = 0.5
    efficiency_fraction = 0.99
    degradable_volatile_solids = GasEmissionConstants.ACHIEVABLE_METHANE_EMISSION / GasEmissionConstants.POTENTIAL_METHANE_YIELD_OF_MANURE
    non_degradable_volatile_solids = 1 - degradable_volatile_solids
    b1 = GasEmissionConstants.DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR
    b2 = GasEmissionConstants.NON_DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR
    ex = math.exp(GasEmissionConstants.NATURAL_LOG_ARRHENIUS_CONSTANT - (
            GasEmissionConstants.ACTIVATION_ENERGY / (GasEmissionConstants.GAS_CONSTANT * tempK)))
    expected_E_CH4_open_air = (0.024 * manure_total_solids * manure_volatile_solids_fraction *
                               (degradable_volatile_solids * b1 + non_degradable_volatile_solids * b2) * ex)
    expected_E_CH4_enclosed = expected_E_CH4_open_air * (1 - efficiency_fraction)

    # Act
    actual = GasEmissions.calc_methane_emission_for_slurry_storage(manure_total_solids, is_enclosed,
                                                                   tempC, manure_volatile_solids_fraction,
                                                                   efficiency_fraction)

    # Assert
    patch_for_convert_tempC_to_tempK.assert_called_once_with(tempC)
    if is_enclosed:
        assert actual == expected_E_CH4_enclosed
    else:
        assert actual == expected_E_CH4_open_air


@pytest.mark.parametrize('hours', [hour for hour in range(0, 24)])
def test_calc_modified_hours(hours: float) -> None:
    """Tests _calc_modified_hours() in gas_emissions.py."""

    # Arrange
    if hours > 14:
        expected = - math.tanh(hours - 21.5) / 3.5
    elif hours > 4:
        expected = math.tanh(hours - 9.5) / 2.5
    else:
        expected = - math.tanh(hours + 3.5) / 3.5

    # Act
    actual = GasEmissions._calc_modified_hours(hours)

    # Assert
    assert actual == expected


def test_calc_ambient_temp(mocker: MockerFixture) -> None:
    """Tests _calc_ambient_temp() in gas_emissions.py."""

    # Arrange
    hours = 10.0
    modified_hours = 8.0
    patch_for_calc_modified_hours = mocker.patch(
        'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._calc_modified_hours',
        return_value=modified_hours,
    )
    t_min = 20.0
    t_max = 30.0
    expected = modified_hours * (t_max - t_min) / 2 + (t_max + t_min) / 2

    # Act
    actual = GasEmissions._calc_ambient_temperature(hours, t_min, t_max)

    # Assert
    patch_for_calc_modified_hours.assert_called_once_with(hours)
    assert actual == expected


@pytest.mark.parametrize(
    'num_animals, barn_area, barn_temp, expected, error_message',
    [
        (10, 100.0, 25.0, 10 * (0.0065 + 0.0192 * 25.0) * 100.0 / 1000, None),  # Standard case
        (0, 100.0, 25.0, 0, None),  # Edge case: no animals
        (10, 0.0, 25.0, 0, None),  # Edge case: no area
        (10, 100.0, -20.0, 0, None),  # Edge case: negative barn_temp
        (-1, 100.0, 25.0, ValueError, 'Number of animals must be greater than or equal to 0.'),
        # Exception case: negative number of animals
        (10, -100.0, 25.0, ValueError, 'Barn area must be greater than or equal to 0.'),
        # Exception case: negative barn area
    ]
)
def test_calc_housing_carbon_dioxide_emission(num_animals: int, barn_area: float, barn_temp: float,
                                              expected: float | Exception, error_message: str | None) -> None:
    """
    Unit test for calc_housing_carbon_dioxide_emission() method in gas_emissions.py.

    This test verifies that the method correctly calculates the carbon dioxide housing emissions
    given the number of animals, the barn area, and the current barn temperature.

    """
    # Act and assert
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected, match=error_message):  # type: ignore
            GasEmissions.calc_housing_carbon_dioxide_emission(num_animals, barn_area, barn_temp)
    else:
        actual = GasEmissions.calc_housing_carbon_dioxide_emission(num_animals, barn_area, barn_temp)
        assert actual == pytest.approx(expected)


@pytest.mark.parametrize('sign_of_RMQ', [-1, 1])
def test_calc_ammonia_emission(sign_of_RMQ: int, mocker: MockerFixture) -> None:
    """Tests calc_ammonia_emission() in gas_emissions.py."""

    # Arrange
    num_animals = 100
    barn_area = 50.0
    manure_urine_total_ammoniacal_nitrogen = 5.0
    manure_urine = 25.0
    c = GeneralConstants.SECONDS_PER_DAY
    tempC = 20.0
    tempK = 293.15
    patch_for_convert_tempC_to_tempK = mocker.patch(
        'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._convert_temperature_celsius_to_kelvin',
        return_value=tempK,
    )
    hsc = 200.0
    r = sign_of_RMQ * 42.0
    patch_for_calc_r_barn = mocker.patch(
        'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._calc_ammonia_barn_resistance',
        return_value=r,
    )
    p = ManureConstants.MANURE_DENSITY
    pH = 7.5
    Q = 2.0
    patch_for_calc_Q = mocker.patch(
        'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._calc_equilibrium_coefficient',
        return_value=Q,
    )
    M = manure_urine / barn_area
    expected = num_animals * barn_area * ((manure_urine_total_ammoniacal_nitrogen / barn_area) * c * p) / (r * M * Q)

    # Act
    actual = GasEmissions.calc_ammonia_emission(num_animals, barn_area, manure_urine_total_ammoniacal_nitrogen,
                                                manure_urine, tempC, hsc)

    # Assert
    patch_for_convert_tempC_to_tempK.assert_called_once_with(tempC)
    patch_for_calc_r_barn.assert_called_once_with(tempC, hsc)
    patch_for_calc_Q.assert_called_once_with(tempK, pH)
    if r * M * Q > 0:
        assert actual == expected
    else:
        assert actual == 0.0


def test_calc_barn_resistance() -> None:
    """Tests _calc_barn_resistance() in gas_emissions.py."""

    # Arrange
    tempC = 15.0
    hsc = GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT
    expected = hsc * (1 - 0.027 * (20.0 - tempC))

    # Act
    actual = GasEmissions._calc_ammonia_barn_resistance(tempC)

    # Assert
    assert actual == expected


def test_calc_Kh() -> None:
    """Tests _calc_Kh() in gas_emissions.py."""

    # Arrange
    tempK = 293.15
    expected = 10 ** (1478 / tempK - 1.69)

    # Act
    actual = GasEmissions._calc_henry_law_coefficient_of_ammonia(tempK)

    # Assert
    assert actual == expected


def test_calc_Ka() -> None:
    """Tests _calc_Ka() in gas_emissions.py."""

    # Arrange
    tempK = 293.15
    pH = 9.0
    expected = 1 + 10 ** (0.09018 + 2729.9 / tempK - pH)

    # Act
    actual = GasEmissions._calc_dissociation_coefficient_of_ammonium(tempK, pH)

    # Assert
    assert actual == expected


def test_calc_Q(mocker: MockerFixture) -> None:
    """Tests _calc_Q() in gas_emissions.py."""

    # Arrange
    tempK = 293.15
    pH = 9.0
    Kh = 10.0
    patch_for_calc_Kh = mocker.patch(
        'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._calc_henry_law_coefficient_of_ammonia',
        return_value=Kh,
    )
    Ka = 20.0
    patch_for_calc_Ka = mocker.patch(
        'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._calc_dissociation_coefficient_of_ammonium',
        return_value=Ka,
    )
    expected = Kh * Ka

    # Act
    actual = GasEmissions._calc_equilibrium_coefficient(tempK, pH)

    # Assert
    assert actual == expected
    patch_for_calc_Kh.assert_called_once_with(tempK)
    patch_for_calc_Ka.assert_called_once_with(tempK, pH)


def test_convert_tempC_to_tempK() -> None:
    """Tests _convert_temperature_celsius_to_kelvin() in gas_emissions.py."""

    # Arrange
    tempC = 15.0
    expected = tempC + 273.15

    # Act
    actual = GasEmissions._convert_temperature_celsius_to_kelvin(tempC)

    # Assert
    assert actual == expected


def test_calc_methane_volume_via_Chen_equation() -> None:
    """Tests _calc_methane_volume_via_Chen_equation() in gas_emissions.py."""

    # Arrange
    VS_total = 10.0
    hydraulic_retention_time = 20
    expected = (GasEmissionConstants.METHANE_POTENTIAL_Go *
                (1 - GasEmissionConstants.CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH /
                 (hydraulic_retention_time * GasEmissionConstants.SPECIFIC_GROWTH_RATE +
                  GasEmissionConstants.CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH - 1)) *
                VS_total * GeneralConstants.GRAMS_TO_KG)

    # Act
    actual = GasEmissions.calc_methane_volume_via_Chen_equation(VS_total, hydraulic_retention_time)

    # Assert
    assert actual == expected


def test_calc_biogas_energy_content() -> None:
    """Tests calc_biogas_energy_content() in gas_emissions.py."""

    # Arrange
    CH4_volume = 10.0
    expected = (CH4_volume * GasEmissionConstants.METHANE_DENSITY *
                GasEmissionConstants.METHANE_ENERGY_DENSITY)

    # Act
    actual = GasEmissions.calc_biogas_energy_content(CH4_volume)

    # Assert
    assert actual == expected


def test_calc_methane_emission_for_anaerobic_lagoon() -> None:
    """Tests calc_methane_emission_for_anaerobic_lagoon() in gas_emissions.py."""

    # Arrange
    manure_volatile_solids = 10.0
    expected = (manure_volatile_solids
                * GasEmissionConstants.ACHIEVABLE_METHANE_EMISSION
                * GasEmissionConstants.METHANE_CONVERSION_FACTOR
                * GasEmissionConstants.FRACTION_OF_HANDLED_MANURE
                * GasEmissionConstants.METHANE_FACTOR)

    # Act
    actual = GasEmissions.calc_methane_emission_from_anaerobic_lagoon(manure_volatile_solids)

    # Assert
    assert actual == approx(expected)


@pytest.mark.parametrize(
    "num_animals, barn_area, barn_temp, expected, error_message",
    [
        (10, 100.0, 30.0, 10 * max(0.0, 0.13 * 30.0) * 100.0 / 1000, None),  # Standard case
        (0, 100.0, 30.0, 0, None),  # Edge case: no animals
        (10, 0.0, 30.0, 0, None),  # Edge case: no area
        (10, 100.0, -20.0, 0, None),  # Edge case: negative barn_temp
        # Exception case: negative number of animals
        (-1, 100.0, 30.0, ValueError, 'Number of animals must be greater than or equal to 0.'),
        # Exception case: negative barn area
        (10, -100.0, 30.0, ValueError, 'Barn area must be greater than or equal to 0.'),
    ]
)
def test_calc_housing_methane_emission(num_animals: int, barn_area: float, barn_temp: float,
                                       expected: float | Exception, error_message: str | None) -> None:
    """
    Unit test for calc_housing_methane_emission() method in gas_emissions.py.

    This test verifies that the method correctly calculates the methane housing emissions
    given the number of animals, the barn area, and the current barn temperature.

    """
    # Act and assert
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected, match=error_message):  # type: ignore
            GasEmissions.calc_housing_methane_emission(num_animals, barn_area, barn_temp)
    else:
        actual = GasEmissions.calc_housing_methane_emission(num_animals, barn_area, barn_temp)
        assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    'num_animals, barn_area, urine_tan, urine, temp, pH, hsc, expected, error_message',
    [
        # Standard case
        (10, 100.0, 25.0, 30.0, 20.0, 7.7, 260.0, 2372.453635832584, None),
        # Edge cases: Zero input values for num_animals, barn_area, urine_tan, urine
        (0, 100.0, 25.0, 30.0, 20.0, 7.7, 260.0, 0.0, None),
        (10, 0.0, 25.0, 30.0, 20.0, 7.7, 260.0, 0.0, None),
        (10, 100.0, 0.0, 30.0, 20.0, 7.7, 260.0, 0.0, None),
        (10, 100.0, 25.0, 0.0, 20.0, 7.7, 260.0, 0.0, None),
        # Exception cases: Negative input values for num_animals, barn_area, urine_tan, urine
        (-1, 100.0, 25.0, 30.0, 20.0, 7.7, 260.0, ValueError,
         'Number of animals must be greater than or equal to 0.'),
        (10, -100.0, 25.0, 30.0, 20.0, 7.7, 260.0, ValueError,
         'Barn area must be greater than or equal to 0.'),
        (10, 100.0, -25.0, 30.0, 20.0, 7.7, 260.0, ValueError,
         'Urine total ammoniacal nitrogen must be greater than or equal to 0.'),
        (10, 100.0, 25.0, -30.0, 20.0, 7.7, 260.0, ValueError,
         'Urine must be greater than or equal to 0.'),
    ]
)
def test_calc_housing_ammonia_emission(num_animals: int, barn_area: float, urine_tan: float, urine: float, temp: float,
                                       pH: float, hsc: float, expected: float | Exception,
                                       error_message: str | None) -> None:
    """
    Unit test for calc_housing_ammonia_emission() method in gas_emissions.py.

    This test verifies that the method correctly calculates the ammonia housing emissions
    given the number of animals, the barn area, urine total ammoniacal nitrogen, urine, temperature,
    pH and housing-specific constant.

    """
    # Act and assert
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected, match=error_message):  # type: ignore
            GasEmissions.calc_housing_ammonia_emission(num_animals, barn_area, urine_tan, urine, temp, pH, hsc)
    else:
        actual = GasEmissions.calc_housing_ammonia_emission(num_animals, barn_area, urine_tan, urine, temp, pH, hsc)
        assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    'temp, expected, error_message',
    [
        # Standard case
        (20.0, 0.05443994340019855, None),
        # Edge cases: Lower and upper bound temperatures
        (-40.0, 3.6974151606958807e-07, None),
        (60.0, 14.031085750034068, None),
        # Exception case: Temperature outside the defined range
        (-41.0, ValueError, 'Temperature must be between -40 and 60 degrees Celsius. Temperature provided: -41.0'),
        (61.0, ValueError, 'Temperature must be between -40 and 60 degrees Celsius. Temperature provided: 61.0'),
    ]
)
def test_calc_arrhenius_exponent(mocker: MockerFixture, temp: float, expected: float | Exception,
                                 error_message: str | None) -> None:
    """
    Unit test for _calc_arrhenius_exponent() method in gas_emissions.py.

    This test verifies that the method correctly calculates the Arrhenius exponent
    given the temperature. It also checks that the method raises an exception for temperatures
    outside the range of -40.0 to 60.0 degrees Celsius.

    """
    # Arrange
    temp_kelvin = temp + 273.15
    patch_for_convert_temp = mocker.patch(
        'RUFAS.routines.manure.gas_emissions.gas_emissions.'
        'GasEmissions._convert_temperature_celsius_to_kelvin',
        return_value=temp_kelvin)

    # Act and Assert
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected, match=error_message):  # type: ignore
            GasEmissions._calc_arrhenius_exponent(temp)
        if GasEmissionConstants.GENERAL_LOWER_BOUND_TEMPERATURE <= temp <= GasEmissionConstants.GENERAL_UPPER_BOUND_TEMPERATURE:
            patch_for_convert_temp.assert_called_once_with(temp)
    else:
        actual = GasEmissions._calc_arrhenius_exponent(temp)
        assert actual == approx(expected, rel=1e-6)
        patch_for_convert_temp.assert_called_once_with(temp)


@pytest.mark.parametrize(
    'total_volatile_solids, expected, error_message',
    [
        # Standard case
        (1.0, (0.5, 0.5), None),
        (45.0, (22.5, 22.5), None),
        # Edge cases: Zero and very large volatile solids
        (0.0, (0.0, 0.0), None),
        (1e6, (5e5, 5e5), None),
        # Exception case: Negative volatile solids
        (-1.0, ValueError, 'Total volatile solids must be non-negative. Total volatile solids provided: -1.0'),
    ]
)
def test_calc_volatile_solid_components(total_volatile_solids: float,
                                        expected: tuple[float, float] | Exception,
                                        error_message: str | None) -> None:
    """
    Unit test for _calc_volatile_solid_components() method in gas_emissions.py.

    This test verifies that the method correctly calculates the degradable and non-degradable
    volatile solids given the total volatile solids. It also checks that the method raises an
    exception for total volatile solids that are negative.

    """
    # Act and assert
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected, match=error_message):
            GasEmissions._calc_volatile_solid_components(total_volatile_solids)
    else:
        actual = GasEmissions._calc_volatile_solid_components(total_volatile_solids)
        assert actual == approx(expected, rel=1e-6)


@pytest.mark.parametrize(
    'total_volatile_solids, temp, expected, error_message',
    [
        # Standard case
        (1.0, 20.0, 4.848, None),
        (10.0, 20.0, 4.848, None),
        # Edge case: Zero total volatile solids
        (0.0, 20.0, 0.0, None),
        # Case when temperature is not provided, default should be used
        (1.0, None, 4.848, None),
        # Exception case: Negative total volatile solids
        (-1.0, 20.0, ValueError, 'Total volatile solids must be greater than 0. Total volatile solids provided: -1.0'),
    ]
)
def test_calc_methane_emission_from_slurry_storage(mocker: MockerFixture, total_volatile_solids: float,
                                                   temp: float | None,
                                                   expected: float | Exception, error_message: str | None) -> None:
    """
    Unit test for calc_methane_emission_from_slurry_storage() method in gas_emissions.py.

    This test verifies that the method correctly calculates the methane emission from manure storage
    given the total volatile solids and temperature. It also checks that the method raises an exception for
    total volatile solids that are negative.

    """
    # Arrange
    patch_for_arrhenius_exponent = mocker.patch(
        'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._calc_arrhenius_exponent',
        return_value=0.2  # Dummy return value
    )
    patch_for_volatile_solid_components = mocker.patch(
        'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._calc_volatile_solid_components',
        return_value=(1.0, 1.0) if total_volatile_solids != 0.0 else (0.0, 0.0)  # Dummy return value
    )

    # Act and assert
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected, match=error_message):
            GasEmissions.calc_methane_emission_from_slurry_storage(total_volatile_solids, temp)
    else:
        if temp is None:
            actual = GasEmissions.calc_methane_emission_from_slurry_storage(total_volatile_solids)
        else:
            actual = GasEmissions.calc_methane_emission_from_slurry_storage(total_volatile_solids, temp)
        assert actual == approx(expected, rel=1e-6)

        patch_for_arrhenius_exponent.assert_called_once_with(
            temp if temp is not None else GasEmissionConstants.DEFAULT_SLURRY_STORAGE_TEMPERATURE)
        patch_for_volatile_solid_components.assert_called_once_with(total_volatile_solids)
