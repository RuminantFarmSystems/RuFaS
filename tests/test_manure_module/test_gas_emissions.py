import math
import pytest
from pytest_mock import MockerFixture

from RUFAS.routines.manure.constants.gas_emission_constants import GasEmissionConstants
from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.manure.constants.manure_constants import ManureConstants
from RUFAS.routines.manure.gas_emissions.gas_emissions import GasEmissions


def test_calc_methane_emission_for_slurry_storage(mocker: MockerFixture) -> None:
    """
    Unit test for calc_methane_emission_for_slurry_storage() in gas_emissions.py.

    """
    # Arrange
    total_volatile_solids = 10.0
    temperature_celsius = 20.0
    temperature_kelvin = temperature_celsius + 273.15

    constants = GasEmissionConstants
    patch_for_convert_tempC_to_tempK = mocker.patch(
        'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._convert_temp_celsius_to_kelvin',
        return_value=temperature_kelvin)
    arrhenius_exponent = math.exp(constants.lnA - (constants.E / (constants.R * temperature_kelvin)))

    volatile_solids_degradable = total_volatile_solids * (constants.Bo / constants.POTENTIAL_METHANE_YIELD_OF_MANURE)
    volatile_solids_non_degradable = total_volatile_solids - volatile_solids_degradable

    methane_emission_degradable = 24 * volatile_solids_degradable * constants.b1 * arrhenius_exponent
    methane_emission_non_degradable = 24 * volatile_solids_non_degradable * constants.b2 * arrhenius_exponent
    expected = methane_emission_degradable + methane_emission_non_degradable

    # Act
    actual = GasEmissions.calc_methane_emission_for_slurry_storage(total_volatile_solids, temperature_celsius)

    # Assert
    assert actual == expected
    patch_for_convert_tempC_to_tempK.assert_called_once_with(temperature_celsius)


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


def test_calc_housing_methane_emission() -> None:
    """
    Unit test for the calc_housing_methane_emission() method in the GasEmissions class.

    This test verifies that the method correctly calculates the methane housing emissions
    given the number of animals, the barn area, and the current barn temperature.

    """
    # Arrange
    num_animals = 10
    barn_area = 100.0
    current_barn_temp = 30.0

    expected = num_animals * max(0.0, 0.13 * current_barn_temp) * barn_area / 1000

    # Act
    actual = GasEmissions.calc_housing_methane_emission(num_animals, barn_area, current_barn_temp)

    # Assert
    assert actual == expected


def test_calc_housing_carbon_dioxide_emission() -> None:
    """
    Unit test for calc_housing_carbon_dioxide_emission() method in gas_emissions.py.

    This test verifies that the method correctly calculates the carbon dioxide housing emissions
    given the number of animals, the barn area, and the current barn temperature.

    """
    # Arrange
    num_animals = 10
    barn_area = 100.0
    barn_temp = 25.0

    expected = num_animals * max(0.0, 0.0065 + 0.0192 * barn_temp) * barn_area / 1000

    # Act
    actual = GasEmissions.calc_housing_carbon_dioxide_emission(num_animals, barn_area, barn_temp)

    # Assert
    assert actual == expected


def test_calc_housing_ammonia_emission(mocker: MockerFixture) -> None:
    """
    Unit test for calc_housing_ammonia_emission() method in GasEmissions class.

    This test verifies that the method correctly calculates the ammonia housing emissions
    given the input parameters.

    """
    # Arrange
    num_animals = 10
    barn_area = 100.0
    urine_total_ammoniacal_nitrogen = 5.0
    urine = 200.0
    temp = 25.0
    pH = 7.0
    housing_specific_constant = 260.0

    total_barn_area = num_animals * barn_area
    TAN = urine_total_ammoniacal_nitrogen / total_barn_area
    p = ManureConstants.MANURE_DENSITY  # kg/m^3
    c = GeneralConstants.SECONDS_PER_DAY  # s/day

    tempK = 298.15
    barn_resistance = 100.0
    Q = 10.0

    patch_for_convert_temp_celsius_to_kelvin = mocker.patch(
        'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._convert_temp_celsius_to_kelvin',
        return_value=tempK)

    patch_for_calc_barn_resistance = mocker.patch(
        'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._calc_barn_resistance',
        return_value=barn_resistance)

    patch_for_calc_Q = mocker.patch(
        'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._calc_Q',
        return_value=Q)

    M = urine / total_barn_area  # manure per area of exposed surface, kg/m^2
    loss = (TAN * c * p) / (barn_resistance * M * Q)
    expected = max(0.0, loss * total_barn_area)

    # Act
    actual = GasEmissions.calc_housing_ammonia_emission(num_animals, barn_area,
                                                        urine_total_ammoniacal_nitrogen, urine,
                                                        temp, pH, housing_specific_constant)

    # Assert
    assert actual == expected
    patch_for_convert_temp_celsius_to_kelvin.assert_called_once_with(temp)
    patch_for_calc_barn_resistance.assert_called_once_with(temp, housing_specific_constant)
    patch_for_calc_Q.assert_called_once_with(tempK, pH)


def test_calc_storage_ammonia_emission(mocker: MockerFixture) -> None:
    """
    Unit test for calc_storage_ammonia_emission() method in GasEmissions class.

    This test verifies that the method correctly calculates the storage ammonia emissions
    given the input parameters.

    """
    # Arrange
    num_animals = 10
    manure_total_ammoniacal_nitrogen = 5.0
    manure_volume = 1.0
    total_solids = 0.2
    storage_area = 1.0
    temp = 25.0
    pH = 7.0

    p = ManureConstants.MANURE_DENSITY  # kg/m^3
    c = GeneralConstants.SECONDS_PER_DAY  # s/day

    tempK = 298.15
    housing_specific_constant = 100.0
    barn_resistance = 100.0
    Q = 10.0

    patch_for_convert_temp_celsius_to_kelvin = mocker.patch(
        'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._convert_temp_celsius_to_kelvin',
        return_value=tempK)

    patch_for_calc_housing_specific_constant = mocker.patch(
        'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._calc_housing_specific_constant',
        return_value=housing_specific_constant)

    patch_for_calc_barn_resistance = mocker.patch(
        'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._calc_barn_resistance',
        return_value=barn_resistance)

    patch_for_calc_Q = mocker.patch(
        'RUFAS.routines.manure.gas_emissions.gas_emissions.GasEmissions._calc_Q',
        return_value=Q)

    manure_mass = manure_volume * ManureConstants.MANURE_DENSITY
    M = manure_mass - total_solids
    loss = (manure_total_ammoniacal_nitrogen * c * p) / (barn_resistance * M * Q)
    expected = max(0.0, loss * storage_area * num_animals)

    # Act
    actual = GasEmissions.calc_storage_ammonia_emission(num_animals, manure_total_ammoniacal_nitrogen,
                                                        manure_volume, total_solids, storage_area, temp, pH)

    # Assert
    assert actual == expected
    patch_for_convert_temp_celsius_to_kelvin.assert_called_once_with(temp)
    patch_for_calc_housing_specific_constant.assert_called_once_with(manure_mass, total_solids)
    patch_for_calc_barn_resistance.assert_called_once_with(temp, housing_specific_constant)
    patch_for_calc_Q.assert_called_once_with(tempK, pH)


def test_calc_housing_specific_constant() -> None:
    """
    Unit test for _calc_housing_specific_constant() method in GasEmissions class.

    This test verifies that the method correctly calculates the housing specific constant
    given different dry matter contents of manure.

    """
    # Arrange
    total_solids_zero = 0.0
    manure_mass_solid = 13.0
    manure_mass_semi_solid = 8.0
    manure_mass_slurry = 5.0
    manure_mass_liquid = 4.0
    total_solids_non_zero = 1.0

    # Act
    hsc_zero = GasEmissions._calc_housing_specific_constant(total_solids_zero, total_solids_zero)
    hsc_solid = GasEmissions._calc_housing_specific_constant(manure_mass_solid, total_solids_non_zero)
    hsc_semi_solid = GasEmissions._calc_housing_specific_constant(manure_mass_semi_solid, total_solids_non_zero)
    hsc_slurry = GasEmissions._calc_housing_specific_constant(manure_mass_slurry, total_solids_non_zero)
    hsc_liquid = GasEmissions._calc_housing_specific_constant(manure_mass_liquid, total_solids_non_zero)

    # Assert
    assert hsc_zero == 10.0
    assert hsc_solid == 10.0
    assert hsc_semi_solid == 10.0
    assert hsc_slurry == 19.0
    assert hsc_liquid == 4.1


def test_calc_barn_resistance() -> None:
    """Tests _calc_barn_resistance() in gas_emissions.py."""

    # Arrange
    tempC = 15.0
    hsc = GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT_FOR_HOUSING
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
    """Tests _convert_temp_celsius_to_kelvin() in gas_emissions.py."""

    # Arrange
    tempC = 15.0
    expected = tempC + 273.15

    # Act
    actual = GasEmissions._convert_temp_celsius_to_kelvin(tempC)

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
