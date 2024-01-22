from pytest import approx

from RUFAS.routines.manure.constants_and_units.gas_emission_constants import GasEmissionConstants
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants


def test_manure_constants() -> None:
    """
    Unit test for the manure constants in file manure_constants.py.

    This function checks the accuracy of the constants based on predefined expected values.
    Assertions are arranged in the order the constants appear in the class definition.
    """

    # Assert
    assert ManureConstants.MANURE_DENSITY == approx(990.0)
    assert ManureConstants.UREA_MOLAR_MASS == approx(60.06)
    assert ManureConstants.UREA_DENSITY == approx(1.32)
    assert ManureConstants.TAN_MOLAR_MASS == approx(17.0306)
    assert ManureConstants.URINE_TAN_FACTOR == approx(0.45)
    assert ManureConstants.MANURE_SOLIDS_BEDDING_DENSITY == approx(400.0)
    assert ManureConstants.LIQUID_MANURE_DENSITY == approx(1000)
    assert ManureConstants.SLURRY_MANURE_DENSITY == approx(990)
    assert ManureConstants.SOLID_MANURE_DENSITY == approx(700)
    assert ManureConstants.DEFAULT_CARBON_FRACTION_AVAILABLE_IN_MANURE == approx(0.5)
    assert ManureConstants.EFFECTIVE_MICROBIAL_DECOMP_RATE == approx(2.37e-3)
    assert ManureConstants.DEFAULT_MOISTURE_EFFECT_MICROBIAL_DECOMP == approx(0.65)
    assert ManureConstants.DEFAULT_DAYS_SINCE_LAST_TILLAGE == approx(1)
    assert ManureConstants.DEFAULT_LAG_TIME == approx(2)
    assert ManureConstants.COMPOST_BEDDING_ORGANIC_NITROGEN_FRACTION == approx(0.952)
    assert ManureConstants.COMPOST_BEDDING_INORGANIC_NITROGEN_AMMONIUM_FRACTION == approx(0.5)


def test_gas_emission_constants() -> None:
    """
    Unit test for the gas emission constants in file gas_emission_constants.py.

    This function checks the accuracy of the constants based on predefined expected values.
    Assertions are arranged in the order the constants appear in the class definition.
    """

    # Assert
    assert GasEmissionConstants.METHANE_EMISSION_COEFFICIENT == approx(24)
    assert GasEmissionConstants.DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR == approx(1.0)
    assert GasEmissionConstants.NON_DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR == approx(0.01)
    assert GasEmissionConstants.NATURAL_LOG_ARRHENIUS_CONSTANT == approx(43.33)
    assert GasEmissionConstants.ACTIVATION_ENERGY == approx(112700.0)
    assert GasEmissionConstants.GAS_CONSTANT == approx(8.314)
    assert GasEmissionConstants.ACHIEVABLE_METHANE_EMISSION == approx(0.24)
    assert GasEmissionConstants.METHANE_CONVERSION_FACTOR == approx(0.79)
    assert GasEmissionConstants.FRACTION_OF_HANDLED_MANURE == approx(0.9)
    assert GasEmissionConstants.METHANE_FACTOR == approx(0.67)
    assert GasEmissionConstants.METHANE_ENERGY_DENSITY == approx(55.0)
    assert GasEmissionConstants.METHANE_DENSITY == approx(0.657)
    assert GasEmissionConstants.METHANE_POTENTIAL_Go == approx(240.0)
    assert GasEmissionConstants.MCF_CONSTANT_A == approx(7.11)
    assert GasEmissionConstants.MCF_CONSTANT_B == approx(0.0884)
    assert GasEmissionConstants.POTENTIAL_METHANE_YIELD_OF_MANURE == approx(0.48)
    assert GasEmissionConstants.DEFAULT_SLURRY_STORAGE_TEMPERATURE == approx(15.0)
    assert GasEmissionConstants.DEFAULT_VOLATILE_SOLIDS_FRACTION == approx(0.68)
    assert GasEmissionConstants.CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH == approx(3.1)
    assert GasEmissionConstants.SPECIFIC_GROWTH_RATE == approx(0.637)
    assert GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT == approx(260.0)
    assert GasEmissionConstants.DEFAULT_PH_FOR_HOUSING_AMMONIA == approx(7.7)
    assert GasEmissionConstants.DEFAULT_PH_FOR_STORAGE_AMMONIA == approx(7.5)
    assert GasEmissionConstants.OXYGEN_HALF_SATURATION_CONSTANT == approx(0.02)
    assert GasEmissionConstants.DEFAULT_CARBON_AVAILABLE_IN_BEDDING == approx(0.35)
    assert GasEmissionConstants.GENERAL_LOWER_BOUND_TEMPERATURE == approx(-40.0)
    assert GasEmissionConstants.GENERAL_UPPER_BOUND_TEMPERATURE == approx(60.0)
    assert GasEmissionConstants.SOLID_AND_SEMI_SOLID_MANURE_HSC == approx(10.0)
    assert GasEmissionConstants.SLURRY_MANURE_HSC == approx(19.0)
    assert GasEmissionConstants.LIQUID_MANURE_HSC == approx(4.1)
    assert GasEmissionConstants.SOLID_MANURE_THRESHOLD == approx(0.08)
    assert GasEmissionConstants.SLURRY_MANURE_THRESHOLD == approx(0.05)
    assert GasEmissionConstants.DEFAULT_STORAGE_AREA_PER_ANIMAL == approx(1.0)
    assert GasEmissionConstants.AMMONIA_EMISSION_COEFFICIENT_WITH_TILLED_BEDDING == approx(0.5)
    assert GasEmissionConstants.AMMONIA_EMISSION_COEFFICIENT_WITH_UNTILLED_BEDDING == approx(0.25)
    assert GasEmissionConstants.LEACHING_COEFFICIENT == approx(0.035)
    assert GasEmissionConstants.NITROUS_OXIDE_COEFFICIENT_WITH_TILLED_BEDDING == approx(0.07)
    assert GasEmissionConstants.NITROUS_OXIDE_COEFFICIENT_WITH_UNTILLED_BEDDING == approx(0.01)
    assert GasEmissionConstants.DEFAULT_CARBON_FRACTION_AVAILABLE_IN_BEDDING == approx(0.35)
