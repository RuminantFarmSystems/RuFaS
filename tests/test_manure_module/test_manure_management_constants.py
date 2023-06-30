from pytest import approx

from RUFAS.routines.manure.constants.gas_emission_constants import GasEmissionConstants
from RUFAS.routines.manure.constants.manure_constants import ManureConstants


def test_manure_constants() -> None:
    """Tests the manure constants in file manure_constants.py."""
    constants = ManureConstants
    assert constants.MANURE_DENSITY == approx(990.0)
    assert constants.UREA_MOLAR_MASS == approx(60.06)
    assert constants.UREA_DENSITY == approx(1.32)
    assert constants.TAN_MOLAR_MASS == approx(17.0306)
    assert constants.URINE_TAN_FACTOR == approx(0.45)
    assert constants.MANURE_SOLIDS_BEDDING_DENSITY == approx(400.0)


def test_gas_emission_constants() -> None:
    """Unit test for the gas emission constants in file gas_emission_constants.py."""

    assert GasEmissionConstants.METHANE_EMISSION_COEFFICIENT == approx(24)
    assert GasEmissionConstants.DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR == approx(1.0)
    assert GasEmissionConstants.NON_DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR == approx(0.01)
    assert GasEmissionConstants.NATURAL_LOG_ARRHENIUS_CONSTANT == approx(43.33)
    assert GasEmissionConstants.ACTIVATION_ENERGY == approx(112700)
    assert GasEmissionConstants.GAS_CONSTANT == approx(8.314)

    assert GasEmissionConstants.ACHIEVABLE_METHANE_EMISSION == approx(0.24)
    assert GasEmissionConstants.METHANE_CONVERSION_FACTOR == approx(0.79)
    assert GasEmissionConstants.FRACTION_OF_HANDLED_MANURE == approx(0.9)
    assert GasEmissionConstants.METHANE_FACTOR == approx(0.67)

    assert GasEmissionConstants.METHANE_ENERGY_DENSITY == approx(55)
    assert GasEmissionConstants.METHANE_DENSITY == approx(0.657)
    assert GasEmissionConstants.METHANE_POTENTIAL_Go == approx(240.0)
    assert GasEmissionConstants.POTENTIAL_METHANE_YIELD_OF_MANURE == approx(0.48)

    assert GasEmissionConstants.DEFAULT_VOLATILE_SOLIDS_FRACTION == approx(0.68)
    assert GasEmissionConstants.CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH == approx(3.1)
    assert GasEmissionConstants.SPECIFIC_GROWTH_RATE == approx(0.637)

    assert GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT == approx(260.0)
    assert GasEmissionConstants.DEFAULT_PH_FOR_HOUSING_AMMONIA == approx(7.7)
    assert GasEmissionConstants.DEFAULT_PH_FOR_STORAGE_AMMONIA == approx(7.5)
    assert GasEmissionConstants.GENERAL_LOWER_BOUND_TEMPERATURE == approx(-40.0)
    assert GasEmissionConstants.GENERAL_UPPER_BOUND_TEMPERATURE == approx(60.0)
