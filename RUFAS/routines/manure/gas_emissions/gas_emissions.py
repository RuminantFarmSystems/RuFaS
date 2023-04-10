import math

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.manure.constants.gas_emission_constants import GasEmissionConstants
from RUFAS.routines.manure.constants.manure_constants import ManureConstants


class GasEmissions:
    # TODO: review docstring
    @classmethod
    def calc_methane_emission_for_slurry_storage(cls,
                                                 total_volatile_solids: float,
                                                 temperature_celsius=GasEmissionConstants.DEFAULT_SLURRY_STORAGE_TEMPERATURE,
                                                 ) -> float:
        """Calculates methane emissions from manure storage using total solids.

        Args:
            total_volatile_solids: total volatile solids in manure, kg.
            temperature_celsius: temperature in Celsius, C.

        Returns:
            CH4 emissions from storage, kg CH4/day.

        """
        constants = GasEmissionConstants
        b1 = constants.b1
        b2 = constants.b2
        lnA = constants.lnA
        E = constants.E
        R = constants.R
        Bo = constants.Bo
        E_CH4_pot = constants.POTENTIAL_METHANE_YIELD_OF_MANURE

        tempK = cls._convert_temperature_celsius_to_kelvin(temperature_celsius)
        ex = math.exp(lnA - (E / (R * tempK)))

        Vsd = total_volatile_solids * (Bo / E_CH4_pot)  # g
        VSnd = total_volatile_solids - Vsd  # g

        VSd_term = 24 * Vsd * b1 * ex
        VSnd_term = 24 * VSnd * b2 * ex
        E_CH4_open_air = VSd_term + VSnd_term  # kg CH4/day

        return E_CH4_open_air

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
    def calc_housing_methane_emission(cls,
                                      num_animals: int,
                                      barn_area: float,
                                      current_barn_temp: float,
                                      ) -> float:
        """Calculates methane housing emission.

        Args:
            num_animals: Number of animals in the pen.
            barn_area: Area of the barn based on housing type, m^2.
            current_barn_temp: Current barn temperature, degree Celsius.

        Returns:
            Methane floor emission, kg CH4/day.

        """
        return num_animals * max(0.0, 0.13 * current_barn_temp) * barn_area / 1000

    @classmethod
    def calc_housing_carbon_dioxide_emission(cls,
                                             num_animals: int,
                                             barn_area: float,
                                             current_barn_temp: float
                                             ) -> float:
        return num_animals * max(0.0, 0.0065 + 0.0192 * current_barn_temp) * barn_area / 1000

    @classmethod
    def calc_housing_ammonia_emission(cls,
                                      num_animals: int,
                                      barn_area: float,
                                      urine_total_ammoniacal_nitrogen: float,
                                      urine: float,
                                      temperature_celsius: float,
                                      pH=GasEmissionConstants.DEFAULT_PH_FOR_HOUSING_AMMONIA,
                                      housing_specific_constant=GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT_FOR_HOUSING,
                                      ) -> float:
        """Calculates ammonia housing emissions for manure handlers.

        Parameters
        ----------
        num_animals : int
            Number of animals in the pen.
        barn_area : float
            Surface area per animal, m^2.
        urine_total_ammoniacal_nitrogen : float
            Total ammoniacal nitrogen in urine per animal, kg N.
        urine : float
            Total urine per animal, kg.
        temperature_celsius : float
            Current temperature, C.
        pH : float
            pH of the urine.
        housing_specific_constant : float, optional
            Housing specific constant, s/m.
            The default is GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT_FOR_HOUSING.

        """
        total_barn_area = num_animals * barn_area
        TAN = urine_total_ammoniacal_nitrogen / total_barn_area
        p = ManureConstants.MANURE_DENSITY  # kg/m^3
        c = GeneralConstants.SECONDS_PER_DAY  # s/day
        tempK = cls._convert_temperature_celsius_to_kelvin(temperature_celsius)  # K
        r = cls._calc_barn_resistance(temperature_celsius, housing_specific_constant)
        M = urine / total_barn_area  # manure per area of exposed surface, kg/m^2
        Q = cls._calc_Q(tempK, pH)
        loss = (TAN * c * p) / (r * M * Q)
        total_loss = loss * total_barn_area

        # Add this number to manure TAN, and then pass this new sum to storage ammonia as TAN
        remaining = (TAN - loss) * total_barn_area

        return max(0.0, total_loss)

    @classmethod
    def calc_storage_ammonia_emission(cls,
                                      manure_total_ammoniacal_nitrogen: float,
                                      manure_volume: float,
                                      total_solids: float,
                                      storage_area: float,  # use 1 m^2 for now
                                      temperature_celsius: float,
                                      pH: float,
                                      ) -> float:
        TAN = manure_total_ammoniacal_nitrogen
        p = ManureConstants.MANURE_DENSITY  # kg/m^3
        c = GeneralConstants.SECONDS_PER_DAY  # s/day
        tempK = cls._convert_temperature_celsius_to_kelvin(temperature_celsius)  # K

        manure_mass = manure_volume * ManureConstants.MANURE_DENSITY
        housing_specific_constant = cls._calc_housing_specific_constant(manure_mass, total_solids)
        r = cls._calc_barn_resistance(temperature_celsius, housing_specific_constant)

        M = manure_mass - total_solids
        Q = cls._calc_Q(tempK, pH)
        loss = (TAN * c * p) / (r * M * Q)
        total_loss = loss * storage_area

        return max(0.0, total_loss)

    @classmethod
    def _calc_housing_specific_constant(cls, manure_mass: float, total_solids: float) -> float:
        dry_matter = manure_mass / total_solids
        if dry_matter >= 13.0:  # solid manure
            housing_specific_constant = 10.0
        elif dry_matter >= 8.0:  # semi-solid manure
            housing_specific_constant = 10.0
        elif dry_matter >= 5.0:  # slurry manure
            housing_specific_constant = 19.0
        else:  # liquid manure
            housing_specific_constant = 4.1
        return housing_specific_constant

    # TODO: Be more descriptive
    @classmethod
    def _calc_barn_resistance(cls, temperature_celsius: float,
                              housing_specific_constant=GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT_FOR_HOUSING) -> \
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

        This is calculated based on a given concentration of total ammoniacal nitrogen in the solution.

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
    def _convert_temperature_celsius_to_kelvin(cls, temperature_celsius: float) -> float:
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
