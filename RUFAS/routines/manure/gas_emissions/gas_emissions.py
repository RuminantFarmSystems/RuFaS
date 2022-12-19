import math

from RUFAS.routines.manure.constants.gas_emission_constants import GasEmissionConstants
from RUFAS.routines.manure.constants.general_constants import GeneralConstants
from RUFAS.routines.manure.constants.manure_constants import ManureConstants


class GasEmissions:
    # TODO: review docstring
    @classmethod
    def calc_methane_emission_for_slurry_storage(cls,
                                                 manure_total_solids: float,
                                                 is_enclosed=False,
                                                 temperature_celsius=GasEmissionConstants.DEFAULT_SLURRY_STORAGE_TEMPERATURE,
                                                 manure_volatile_solids_fraction=(
                                                         GasEmissionConstants.DEFAULT_VOLATILE_SOLIDS_FRACTION),
                                                 efficiency_fraction=0.99) -> float:
        """Calculates methane emissions from manure storage using total solids.

        Args:
            manure_total_solids: Total solids, kg.
            is_enclosed: True if manure storage is enclosed, and False if manure storage is open to air.
            temperature_celsius: temperature in Celsius, C.
            manure_volatile_solids_fraction: Fraction (0-1) volatile solids. # TODO: review this
            efficiency_fraction: efficiency of process, unitless. # TODO: review this

        Returns:
            CH4 emissions from storage, kg CH4/day.

        """
        c = 0.024
        VS_tot = manure_total_solids * manure_volatile_solids_fraction

        constants = GasEmissionConstants
        b1 = constants.b1
        b2 = constants.b2
        lnA = constants.lnA
        E = constants.E
        R = constants.R
        Bo = constants.Bo
        E_CH4_pot = constants.POTENTIAL_METHANE_YIELD_OF_MANURE

        tempK = cls._convert_tempC_to_tempK(temperature_celsius)
        ex = math.exp(lnA - (E / (R * tempK)))

        VSd = (Bo / E_CH4_pot)
        VSnd = 1 - VSd
        E_CH4_open_air = c * VS_tot * (VSd * b1 + VSnd * b2) * ex

        if not is_enclosed:
            return E_CH4_open_air
        else:
            return E_CH4_open_air * (1 - efficiency_fraction)

    # TODO: Be more descriptive
    @classmethod
    def _calc_modified_hours(cls, hours: float) -> float:
        """Calculates modified hours.

        Args:
            hours: number of hours.

        Returns:
            modified hours.

        """

        if hours > 14:
            modified_hours = - math.tanh(hours - 21.5) / 3.5
        elif hours > 4:
            modified_hours = math.tanh(hours - 9.5) / 2.5
        else:
            modified_hours = - math.tanh(hours + 3.5) / 3.5

        return modified_hours

    # TODO: Be more descriptive
    @classmethod
    def _calc_ambient_temp(cls, hours: float, temperature_min: float, temperature_max: float) -> float:
        """Calculates ambient temperature.

        Args:
            hours: hours of the day from 1 to 24.
            temperature_min: Minimum barn temperature, C.
            temperature_max: Maximum barn temperature, C.

        Returns:
            Ambient temperature, °C.

        """
        modified_hours = cls._calc_modified_hours(hours)
        t_ambient = modified_hours * (temperature_max - temperature_min) / 2 + (temperature_max + temperature_min) / 2
        return t_ambient

    # TODO: Be more descriptive
    @classmethod
    def calc_methane_housing_emission(cls, num_animals: int, barn_area: float, hours=24, temperature_min=20.0,
                                      temperature_max=25.0) -> float:
        """Calculates methane housing emission.

        Args:
            num_animals: Number of animals in the pen.
            barn_area: Area of the barn based on housing type, m^2.
            hours: hours of the day from 1 to 24.
            temperature_min: Minimum barn temperature, C.
            temperature_max: Maximum barn temperature, C.

        Returns:
            Methane floor emissions, kg CH4/day.

        """
        t_ambient = cls._calc_ambient_temp(hours, temperature_min, temperature_max)
        t = max(-5.0, 0.63 * t_ambient + 6.0)
        return num_animals * max(0.0, 0.13 * t) * barn_area / 1000

    @classmethod
    def calc_carbon_dioxide_housing_emission(cls,
                                             num_animals: int,
                                             barn_area: float,
                                             hours=24,
                                             temperature_min=20.0,
                                             temperature_max=25.0) -> float:
        """Calculates carbon dioxide housing emissions.

        Args:
            num_animals: Number of animals in the pen.
            barn_area: Area of the barn based on housing type, m^2.
            hours: hours of the day from 1 to 24.
            temperature_min: Minimum barn temperature, C.
            temperature_max: Maximum barn temperature, C.

        Returns:
            Carbon dioxide floor emissions, kg CO2/day.

        """
        t_ambient = cls._calc_ambient_temp(hours, temperature_min, temperature_max)
        t = max(-5.0, 0.63 * t_ambient + 6.0)
        return num_animals * max(0.0, 0.0065 + 0.0192 * t) * barn_area / 1000

    @classmethod
    def calc_ammonia_housing_emission(cls, num_animals: int,
                                      barn_area: float,
                                      manure_urine_total_ammoniacal_nitrogen: float,
                                      manure_urine: float,
                                      temperature_celsius: float,
                                      housing_specific_constant=(
                                              GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT),
                                      ) -> float:
        """Calculates NH3 storage emissions.

        Args:
            num_animals: Number of animals in the pen.
            barn_area: surface area for treatment, m^2.
            manure_urine_total_ammoniacal_nitrogen: total ammoniacal nitrogen in manure urine, kg N.
            manure_urine: total amount of manure urine in exposed surface area, kg.
            temperature_celsius: temperature, C.
            housing_specific_constant: housing specific constant, s/m.

        Returns:
            NH3 storage emissions, kg N/day.

        """
        p = ManureConstants.MANURE_DENSITY  # kg/m^3
        pH = 7.5
        c = GeneralConstants.SECONDS_PER_DAY  # s/day
        tempK = cls._convert_tempC_to_tempK(temperature_celsius)  # K
        r = cls._calc_barn_resistance(temperature_celsius, housing_specific_constant)
        M = manure_urine / barn_area  # manure per area of exposed surface, kg/m^2
        Q = cls._calc_Q(tempK, pH)
        if r * M * Q > 0:
            return num_animals * barn_area * ((manure_urine_total_ammoniacal_nitrogen / barn_area) * c * p) / (
                    r * M * Q)
        else:
            return 0.0

    # TODO: Be more descriptive
    @classmethod
    def _calc_barn_resistance(cls, temperature_celsius: float,
                              housing_specific_constant=GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT) -> \
            float:
        """Calculates barn resistance.

        Args:
            temperature_celsius: temperature in Celsius, C.
            housing_specific_constant: housing specific constant, s/m.

        Returns:
            Barn resistance, s/m.

        """
        return housing_specific_constant * (1 - 0.027 * (20.0 - temperature_celsius))

    @classmethod
    def _calc_Kh(cls, temperature_kelvin: float) -> float:
        """Calculates Henry's constant.

        Args:
            temperature_kelvin: temperature in Kelvin, K.

        Returns:
            Henry's constant, M/atm.

        """

        return 10 ** (1478 / temperature_kelvin - 1.69)

    @classmethod
    def _calc_Ka(cls, temperature_kelvin: float, pH: float) -> float:
        """Calculates acid dissociation constant.

        Args:
            temperature_kelvin: temperature in Kelvin, K.
            pH: manure acidity, dimensionless.

        Returns:
            Acid dissociation constant, dimensionless.

        """

        return 1 + 10 ** (0.09018 + 2729.9 / temperature_kelvin - pH)

    @classmethod
    def _calc_Q(cls, temperature_kelvin: float, pH: float) -> float:
        """Calculates Q, the equilibrium coefficient for the NH3 gas in the air.

        This is calculated based on a given concentration of total_ammoniacal_nitrogen in the solution.

        Args:
            temperature_kelvin: temperature in Kelvin, K.
            pH: manure acidity, dimensionless.

        Returns:
            Q, the equilibrium coefficient for the NH3 gas in the air, dimensionless.

        """
        Kh = cls._calc_Kh(temperature_kelvin)
        Ka = cls._calc_Ka(temperature_kelvin, pH)
        return Kh * Ka

    @classmethod
    def _convert_tempC_to_tempK(cls, temperature_celsius: float) -> float:
        """Converts a temperature from Celsius to Kelvin.

        Args:
            temperature_celsius: temperature in Celsius, C.

        Returns:
            Temperature in Kelvin, K.

        """
        return temperature_celsius + 273.15

    @classmethod
    def calc_methane_volume_via_Chen_equation(cls, manure_total_volatile_solids: float,
                                              hydraulic_retention_time: int) -> float:
        """Calculates CH4 generation volume using the Chen-Hashimoto equation.

        Args:
            manure_total_volatile_solids: total volatile solids, kg.
            hydraulic_retention_time: hydraulic retention time, days.

        Returns:
            CH4 generation volume, m^3.

        """
        return (GasEmissionConstants.METHANE_POTENTIAL_Go *
                (1 - GasEmissionConstants.CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH /
                 (hydraulic_retention_time * GasEmissionConstants.SPECIFIC_GROWTH_RATE +
                  GasEmissionConstants.CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH - 1)) *
                manure_total_volatile_solids * GeneralConstants.GRAMS_TO_KG)

    @classmethod
    def calc_biogas_energy_content(cls, methane_volume: float) -> float:
        """Calculates biogas energy content.

        Args:
            methane_volume: Methane generation volume, m^3.

        Returns:
            Biogas energy content, MJ.

        """
        return methane_volume * GasEmissionConstants.METHANE_DENSITY * GasEmissionConstants.METHANE_ENERGY_DENSITY

    @classmethod
    def calc_methane_emission_for_anaerobic_lagoon(cls, manure_volatile_solids: float) -> float:
        """Calculates methane emissions from anaerobic lagoon.

        Args:
            manure_volatile_solids: volatile solids, kg.

        Returns:
            Methane emissions from anaerobic lagoon, kg CH4-N /day.

        """
        constants = GasEmissionConstants
        Bo = constants.Bo
        MCF = constants.MCF
        MS = constants.MS
        METHANE_FACTOR = constants.METHANE_FACTOR
        return manure_volatile_solids * Bo * MCF * MS * METHANE_FACTOR
