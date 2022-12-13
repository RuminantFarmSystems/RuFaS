import math
import pytest
from pytest_mock import MockerFixture

from RUFAS.routines.manure.constants.gas_emission_constants import GasEmissionConstants
from RUFAS.routines.manure.constants.general_constants import GeneralConstants
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
            'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._convert_tempC_to_tempK',
            return_value=tempK,
    )
    manure_volatile_solids_fraction = 0.5
    efficiency_fraction = 0.99
    degradable_volatile_solids = GasEmissionConstants.Bo / GasEmissionConstants.POTENTIAL_METHANE_YIELD_OF_MANURE
    non_degradable_volatile_solids = 1 - degradable_volatile_solids
    b1 = GasEmissionConstants.b1
    b2 = GasEmissionConstants.b2
    ex = math.exp(GasEmissionConstants.lnA - (GasEmissionConstants.E / (GasEmissionConstants.R * tempK)))
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
    actual = GasEmissions._calc_ambient_temp(hours, t_min, t_max)

    # Assert
    patch_for_calc_modified_hours.assert_called_once_with(hours)
    assert actual == expected


@pytest.mark.parametrize('ambient_temp', [temp for temp in range(-40, 40, 10)])
def test_calc_methane_housing_emission(ambient_temp: float, mocker: MockerFixture) -> None:
    """Tests calc_methane_housing_emission() in gas_emissions.py."""

    # Arrange
    num_animals = 100
    barn_area = 50.0
    hours = 10
    t_min = 20.0
    t_max = 30.0
    patch_for_calc_ambient_temp = mocker.patch(
            'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._calc_ambient_temp',
            return_value=ambient_temp,
    )
    expected = num_animals * max(0.0, 0.13 * max(-5.0, 0.63 * ambient_temp + 6.0)) * barn_area / 1000

    # Act
    actual = GasEmissions.calc_methane_housing_emission(num_animals, barn_area, hours, t_min, t_max)

    # Assert
    patch_for_calc_ambient_temp.assert_called_once_with(hours, t_min, t_max)
    assert actual == expected


@pytest.mark.parametrize('ambient_temp', [temp for temp in range(-40, 40, 10)])
def test_calc_carbon_dioxide_housing_emission(ambient_temp: float, mocker: MockerFixture) -> None:
    """Tests calc_carbon_dioxide_housing_emission() in gas_emissions.py."""

    # Arrange
    num_animals = 100
    barn_area = 50.0
    hours = 10
    t_min = 20.0
    t_max = 30.0
    patch_for_calc_ambient_temp = mocker.patch(
            'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._calc_ambient_temp',
            return_value=ambient_temp,
    )
    expected = num_animals * max(0.0, 0.0065 + 0.0192 * max(-5.0, 0.63 * ambient_temp + 6.0)) * barn_area / 1000

    # Act
    actual = GasEmissions.calc_carbon_dioxide_housing_emission(num_animals, barn_area, hours, t_min, t_max)

    # Assert
    patch_for_calc_ambient_temp.assert_called_once_with(hours, t_min, t_max)
    assert actual == expected


@pytest.mark.parametrize('sign_of_RMQ', [-1, 1])
def test_calc_ammonia_housing_emission(sign_of_RMQ: int, mocker: MockerFixture) -> None:
    """Tests calc_ammonia_housing_emission() in gas_emissions.py."""

    # Arrange
    num_animals = 100
    barn_area = 50.0
    manure_urine_total_ammoniacal_nitrogen = 5.0
    manure_urine = 25.0
    c = GeneralConstants.SECONDS_PER_DAY
    tempC = 20.0
    tempK = 293.15
    patch_for_convert_tempC_to_tempK = mocker.patch(
            'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._convert_tempC_to_tempK',
            return_value=tempK,
    )
    hsc = 200.0
    r = sign_of_RMQ * 42.0
    patch_for_calc_r_barn = mocker.patch(
            'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._calc_barn_resistance',
            return_value=r,
    )
    p = ManureConstants.MANURE_DENSITY
    pH = 7.5
    Q = 2.0
    patch_for_calc_Q = mocker.patch(
            'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._calc_Q',
            return_value=Q,
    )
    M = manure_urine / barn_area
    expected = num_animals * barn_area * ((manure_urine_total_ammoniacal_nitrogen / barn_area) * c * p) / (r * M * Q)

    # Act
    actual = GasEmissions.calc_ammonia_housing_emission(num_animals, barn_area, manure_urine_total_ammoniacal_nitrogen, manure_urine, tempC, hsc)

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
    actual = GasEmissions._calc_barn_resistance(tempC)

    # Assert
    assert actual == expected


def test_calc_Kh() -> None:
    """Tests _calc_Kh() in gas_emissions.py."""

    # Arrange
    tempK = 293.15
    expected = 10 ** (1478 / tempK - 1.69)

    # Act
    actual = GasEmissions._calc_Kh(tempK)

    # Assert
    assert actual == expected


def test_calc_Ka() -> None:
    """Tests _calc_Ka() in gas_emissions.py."""

    # Arrange
    tempK = 293.15
    pH = 9.0
    expected = 1 + 10 ** (0.09018 + 2729.9 / tempK - pH)

    # Act
    actual = GasEmissions._calc_Ka(tempK, pH)

    # Assert
    assert actual == expected


def test_calc_Q(mocker: MockerFixture) -> None:
    """Tests _calc_Q() in gas_emissions.py."""

    # Arrange
    tempK = 293.15
    pH = 9.0
    Kh = 10.0
    patch_for_calc_Kh = mocker.patch(
            'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._calc_Kh',
            return_value=Kh,
    )
    Ka = 20.0
    patch_for_calc_Ka = mocker.patch(
            'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._calc_Ka',
            return_value=Ka,
    )
    expected = Kh * Ka

    # Act
    actual = GasEmissions._calc_Q(tempK, pH)

    # Assert
    assert actual == expected
    patch_for_calc_Kh.assert_called_once_with(tempK)
    patch_for_calc_Ka.assert_called_once_with(tempK, pH)


def test_convert_tempC_to_tempK() -> None:
    """Tests _convert_tempC_to_tempK() in gas_emissions.py."""

    # Arrange
    tempC = 15.0
    expected = tempC + 273.15

    # Act
    actual = GasEmissions._convert_tempC_to_tempK(tempC)

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
    expected = (manure_volatile_solids * GasEmissionConstants.Bo *
                GasEmissionConstants.MCF * GasEmissionConstants.MS * GasEmissionConstants.METHANE_FACTOR)

    # Act
    actual = GasEmissions.calc_methane_emission_for_anaerobic_lagoon(manure_volatile_solids)

    # Assert
    assert actual == expected
