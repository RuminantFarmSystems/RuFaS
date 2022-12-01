import math

from RUFAS.routines.manure.constants.gas_emission_constants import GasEmissionConstants
from RUFAS.routines.manure.constants.general_constants import GeneralConstants
from RUFAS.routines.manure.constants.manure_constants import ManureConstants


class GasEmissions:
    @classmethod
    def calc_E_CH4_slurry_storage(cls,
                                  TS: float,
                                  enclosed=False,
                                  tempC=15.0,
                                  VS_frac=GasEmissionConstants.DEFAULT_VOLATILE_SOLIDS_FRACTION,
                                  n_eff=0.99,
                                  VS_loss_yesterday=0.0) -> float:
        """Calculates methane emissions from manure storage using total solids and manure kg.

        Args:
            TS: Total solids, kg.
            enclosed: True if manure storage is enclosed, and False if manure storage is open to air.
            tempC: temperature, C.
            VS_frac: Fraction (0-1) volatile solids.
            n_eff: efficiency of process              TODO: confirm n_eff meaning
            VS_loss_yesterday: VS loss from previous day.

        Returns:
            CH4 emissions from storage, kg CH4/day.

        """
        c = 0.024
        VS_tot = TS * VS_frac

        constants = GasEmissionConstants
        b1 = constants.b1
        b2 = constants.b2
        lnA = constants.lnA
        E = constants.E
        R = constants.R
        Bo = constants.Bo
        E_CH4_pot = constants.POTENTIAL_METHANE_YIELD_OF_MANURE

        tempK = cls._convert_tempC_to_tempK(tempC)
        ex = math.exp(lnA - (E / (R * tempK)))

        VSd = (Bo / E_CH4_pot)
        VSnd = 1 - VSd
        E_CH4_open_air = c * VS_tot * (VSd * b1 + VSnd * b2) * ex

        if not enclosed:
            return E_CH4_open_air
        else:
            return E_CH4_open_air * (1 - n_eff)

    @staticmethod
    def _calc_modified_hours(hours: float) -> float:
        """Calculate modified hours."""

        if hours > 14:
            modified_hours = - math.tanh(hours - 21.5) / 3.5
        elif hours > 4:
            modified_hours = math.tanh(hours - 9.5) / 2.5
        else:
            modified_hours = - math.tanh(hours + 3.5) / 3.5

        return modified_hours

    @classmethod
    def _calc_ambient_temp(cls, hours: float, t_min: float, t_max: float) -> float:
        """Calculates ambient temperature.

        Args:
            hours: hours of the day from 1 to 24.
            t_min: Minimum barn temperature, C.
            t_max: Maximum barn temperature, C.

        Returns:
            Ambient temperature, °C.

        """
        modified_hours = cls._calc_modified_hours(hours)
        t_ambient = modified_hours * (t_max - t_min) / 2 + (t_max + t_min) / 2
        return t_ambient

    @classmethod
    def calc_E_CH4_housing(cls, num_animals: int, barn_area: float, hours=24, t_min=20.0, t_max=25.0) -> float:
        """Calculates methane housing emissions.

        Args:
            num_animals: Number of animals in the pen.
            barn_area: Area of the barn based on housing type, m^2.
            hours: hours of the day from 1 to 24.
            t_min: Minimum barn temperature, C.
            t_max: Maximum barn temperature, C.

        Returns:
            Methane floor emissions, kg CH4/day.

        """
        t_ambient = cls._calc_ambient_temp(hours, t_min, t_max)
        t = max(-5.0, 0.63 * t_ambient + 6.0)
        return num_animals * max(0.0, 0.13 * t) * barn_area / 1000

    @classmethod
    def calc_E_C02_housing(cls, num_animals: int, barn_area: float, hours=24, t_min=20.0, t_max=25.0) -> float:
        """Calculates carbon dioxide housing emissions.

        Args:
            num_animals: Number of animals in the pen.
            barn_area: Area of the barn based on housing type, m^2.
            hours: hours of the day from 1 to 24.
            t_min: Minimum barn temperature, C.
            t_max: Maximum barn temperature, C.

        Returns:
            Carbon dioxide floor emissions, kg CO2/day.

        """
        t_ambient = cls._calc_ambient_temp(hours, t_min, t_max)
        t = max(-5.0, 0.63 * t_ambient + 6.0)
        return num_animals * max(0.0, 0.0065 + 0.0192 * t) * barn_area / 1000

    @classmethod
    def calc_E_NH3_emission(cls, num_animals: int,
                            barn_area: float,
                            urine_TAN: float,
                            urine: float,
                            tempC: float, hsc=GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT) -> float:
        """Calculates NH3 storage emissions.

        Args:
            num_animals: Number of animals in the pen.
            barn_area: surface area for treatment, m^2.
            urine_TAN: total ammoniacal nitrogen in manure urine, kg N.
            urine: total amount of manure urine in exposed surface area, kg.
            tempC: temperature, C.
            hsc: housing specific constant, s/m.

        Returns:
            NH3 storage emissions, kg N/day.

        """
        p = ManureConstants.MANURE_DENSITY  # kg/m^3
        pH = 7.5
        c = GeneralConstants.SECONDS_PER_DAY  # s/day
        tempK = cls._convert_tempC_to_tempK(tempC)  # K
        r = cls._calc_r_barn(tempC, hsc)
        M = urine / barn_area  # manure per area of exposed surface, kg/m^2
        Q = cls._calc_Q(tempK, pH)
        if r * M * Q > 0:
            return num_animals * barn_area * ((urine_TAN / barn_area) * c * p) / (r * M * Q)
        else:
            return 0

    @classmethod
    def _calc_r_barn(cls, tempC: float, hsc=GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT) -> float:
        """Calculates barn resistance.

        Args:
            tempC: temperature in Celsius, C.
            hsc: housing specific constant, s/m.

        Returns:
            Barn resistance, s/m.

        """
        return hsc * (1 - 0.027 * (20.0 - tempC))

    @classmethod
    def _calc_Kh(cls, tempK: float) -> float:
        """Calculates Henry's constant.

        Args:
            tempK: temperature in Kelvin, K.

        Returns:
            Henry's constant, M/atm.

        """

        return 10 ** (1478 / tempK - 1.69)

    @classmethod
    def _calc_Ka(cls, tempK: float, pH: float) -> float:
        """Calculates acid dissociation constant.

        Args:
            tempK: temperature in Kelvin, K.
            pH: manure acidity, dimensionless.

        Returns:
            Acid dissociation constant, dimensionless.

        """

        return 1 + 10 ** (0.09018 + 2729.9 / tempK - pH)

    @classmethod
    def _calc_Q(cls, tempK: float, pH: float) -> float:
        """Calculates Q, the equilibrium coefficient for the NH3 gas in the air.

        This is calculated based on a given concentration of TAN in the solution.

        Args:
            tempK: temperature in Kelvin, K.
            pH: manure acidity, dimensionless.

        Returns:
            Q, the equilibrium coefficient for the NH3 gas in the air, dimensionless.

        """
        Kh = cls._calc_Kh(tempK)
        Ka = cls._calc_Ka(tempK, pH)
        return Kh * Ka

    @staticmethod
    def _convert_tempC_to_tempK(tempC: float) -> float:
        """Converts a temperature from Celsius to Kelvin.

        Args:
            tempC: temperature in Celsius, C.

        Returns:
            Temperature in Kelvin, K.

        """
        return tempC + 273.15

    # TODO: Review the units
    @classmethod
    def calc_CH4_volume_using_Chen_equation(cls, VS_total: float,
                                            hydraulic_retention_time: int) -> float:
        """Calculates CH4 generation volume using the Chen-Hashimoto equation.

        Args:
            VS_total: total volatile solids, kg.
            hydraulic_retention_time: hydraulic retention time, days.

        Returns:
            CH4 generation volume, m^3.

        """
        return (GasEmissionConstants.METHANE_POTENTIAL_Go *
                (1 - GasEmissionConstants.CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH /
                 (hydraulic_retention_time * GasEmissionConstants.SPECIFIC_GROWTH_RATE +
                  GasEmissionConstants.CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH - 1)) *
                VS_total * GeneralConstants.GRAMS_TO_KG)

    @classmethod
    def calc_biogas_energy_content(cls, CH4_volume: float) -> float:
        """Calculates biogas energy content.

        Args:
            CH4_volume: CH4 generation volume, m^3.

        Returns:
            Biogas energy content, MJ.

        """
        return CH4_volume * GasEmissionConstants.METHANE_DENSITY * GasEmissionConstants.METHANE_ENERGY_DENSITY

    @classmethod
    def calc_E_CH4_anaerobic_lagoon(cls, VS: float) -> float:
        """Calculates methane emissions from anaerobic lagoon.

        Args:
            VS: volatile solids, kg.

        Returns:
            Methane emissions from anaerobic lagoon, kg CH4-N /day.

        """
        constants = GasEmissionConstants
        Bo = constants.Bo
        MCF = constants.MCF
        MS = constants.MS
        METHANE_FACTOR = constants.METHANE_FACTOR
        return VS * Bo * MCF * MS * METHANE_FACTOR

    @classmethod
    def calc_CO2_equivalent_of_CH4(cls, CH4: float) -> float:
        """Calculates the CO2 equivalent of CH4.

        Args:
            CH4: methane, kg/day.

        Returns:
            CO2 equivalent of CH4, kg/day.

        """

        return CH4 * 30

    @classmethod
    def calc_CO2_equivalent_of_N20(cls, N2O: float) -> float:
        """Calculates the CO2 equivalent of N2O.

        Args:
            N2O: nitrous oxide, kg/day.

        Returns:
            CO2 equivalent of N2O, kg/day.

        """
        return N2O * 310
