import math

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.manure.constants.gas_emission_constants import GasEmissionConstants
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

        tempK = cls._convert_temperature_celsius_to_kelvin(temperature_celsius)
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

    @classmethod
    def calc_housing_methane_emission(cls, num_animals: int, barn_area: float, barn_temp: float) -> float:
        """
        Calculate housing methane emissions from manure handlers.

        Notes
        -----
        The equation used to calculate housing methane emissions is:

        .. math::

            E_{CH_4} = num\_animals \\times max(0, 0.13 * T_{barn}) \\times barn\_area / 1000

        where:

            :math:`E_{CH_4}` is the methane housing emission in kg :math:`CH_4/day`,

            :math:`T_{barn}` is the barn temperature in :math:`^{\circ}C`,

            :math:`barn\_area` is the barn area per animal based on housing type in :math:`m^2`, and

            :math:`num\_animals` is the number of animals in the pen.

        Parameters
        ----------
        num_animals : int
            Number of animals in the pen (unitless).
        barn_area : float
            Barn area per animal based on housing type (:math:`m^2`).
        barn_temp : float
            Current barn temperature (:math:`^{\circ}C`).

        Returns
        -------
        float
            Housing methane emissions (kg :math:`CH_4/day`).

        Raises
        ------
        ValueError
            If the number of animals or barn area is less than 0.

        """
        if num_animals < 0:
            raise ValueError('Number of animals must be greater than or equal to 0.')

        if barn_area < 0:
            raise ValueError('Barn area must be greater than or equal to 0.')

        return num_animals * max(0.0, 0.13 * barn_temp) * barn_area / 1000

    @classmethod
    def calc_housing_carbon_dioxide_emission(cls, num_animals: int, barn_area: float, barn_temp: float) -> float:
        """
        Calculate carbon dioxide housing emission.

        Notes
        -----
        The equation used to calculate housing carbon dioxide emissions is:

        .. math::

            E_{CO_2} = num\_animals \\times max(0, 0.0065 + 0.0192 * T_{barn}) \\times barn\_area / 1000

        where:

            :math:`E_{CO_2}` is the carbon dioxide housing emission in kg :math:`CO_2/day`,

            :math:`T_{barn}` is the barn temperature in :math:`^{\circ}C`,

            :math:`barn\_area` is the barn area per animal based on housing type in :math:`m^2`, and

            :math:`num\_animals` is the number of animals in the pen.

        Parameters
        ----------
        num_animals : int
            Number of animals in the pen (unitless).
        barn_area : float
            Barn area per animal based on housing type (:math:`m^2`).
        barn_temp : float
            Current barn temperature (:math:`^{\circ}C`).

        Returns
        -------
        float
            Carbon dioxide housing emission (kg :math:`CO_2`/day).

        Raises
        ------
        ValueError
            If the number of animals or barn area is less than 0.

        """
        if num_animals < 0:
            raise ValueError('Number of animals must be greater than or equal to 0.')

        if barn_area < 0:
            raise ValueError('Barn area must be greater than or equal to 0.')

        return num_animals * max(0.0, 0.0065 + 0.0192 * barn_temp) * barn_area / 1000

    @classmethod
    def calc_housing_ammonia_emission(cls, num_animals: int, barn_area: float,
                                      urine_total_ammoniacal_nitrogen: float,
                                      urine: float, temp: float,
                                      pH=GasEmissionConstants.DEFAULT_PH_FOR_HOUSING_AMMONIA,
                                      hsc=GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT) -> float:
        """
        Calculate housing ammonia emission.

        Notes
        -----
        The calculation is based on several factors, including the number of animals,
        the barn area, the total ammoniacal nitrogen in urine, the amount of urine,
        temperature, and the pH and housing-specific constant values.

        Parameters
        ----------
        num_animals : int
            Number of animals in the barn (unitless).
        barn_area : float
            Barn area per animal based on housing type (:math:`m^2`).
        urine_total_ammoniacal_nitrogen : float
            Total ammoniacal nitrogen in urine (kg).
        urine : float
            Amount of urine produced by animals in the barn (kg).
        temp : float
            Current barn temperature (:math:`^{\circ}C`).
        pH : float, optional
            pH value for housing ammonia emission (unitless). Default is set to
                :attr:`DEFAULT_PH_FOR_HOUSING_AMMONIA` in :class:`GasEmissionConstants`.
        hsc : float, optional
            Housing-specific constant (unitless). Default is set to :attr:`DEFAULT_HOUSING_SPECIFIC_CONSTANT` in
                :class:`GasEmissionConstants`.

        Returns
        -------
        float
            Housing ammonia emission (kg :math:`NH_3/day`).

        Raises
        ------
        ValueError
            If the number of animals, barn area, urine total ammoniacal nitrogen, or urine is less than 0.

        """
        if num_animals < 0:
            raise ValueError('Number of animals must be greater than or equal to 0.')

        if barn_area < 0:
            raise ValueError('Barn area must be greater than or equal to 0.')

        if urine_total_ammoniacal_nitrogen < 0:
            raise ValueError('Urine total ammoniacal nitrogen must be greater than or equal to 0.')

        if urine < 0:
            raise ValueError('Urine must be greater than or equal to 0.')

        # If any of the aforementioned values are 0, then the result is 0
        if num_animals == 0 or barn_area == 0 or urine_total_ammoniacal_nitrogen == 0 or urine == 0:
            return 0.0

        total_barn_area = num_animals * barn_area
        TAN = urine_total_ammoniacal_nitrogen / total_barn_area
        p = ManureConstants.MANURE_DENSITY  # kg/m^3
        c = GeneralConstants.SECONDS_PER_DAY  # s/day
        tempK = cls._convert_temperature_celsius_to_kelvin(temp)  # K
        r = cls._calc_barn_resistance(temp, hsc)
        M = urine / total_barn_area  # manure per area of exposed surface, kg/m^2
        Q = cls._calc_Q(tempK, pH)
        loss = (TAN * c * p) / (r * M * Q)
        total_loss = loss * total_barn_area
        return max(0.0, total_loss)

    @classmethod
    def calc_ammonia_emission(cls,
                              num_animals: int,
                              barn_area: float,
                              total_ammoniacal_nitrogen: float,
                              mass: float,
                              temperature_celsius: float,
                              housing_specific_constant=GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT,
                              ) -> float:
        """Calculates NH3 storage emissions.

        Args:
            num_animals: Number of animals in the pen.
            barn_area: Surface area for treatment, m^2.
            total_ammoniacal_nitrogen: total ammoniacal nitrogen in urine or manure, kg N.
            mass: total amount of urine or manure in exposed surface area, kg.
            temperature_celsius: temperature, C.
            housing_specific_constant: housing specific constant, s/m.

        Returns:
            NH3 storage emissions, kg N/day.

        """
        p = ManureConstants.MANURE_DENSITY  # kg/m^3
        pH = 7.5
        c = GeneralConstants.SECONDS_PER_DAY  # s/day
        tempK = cls._convert_temperature_celsius_to_kelvin(temperature_celsius)  # K
        r = cls._calc_barn_resistance(temperature_celsius, housing_specific_constant)
        M = mass / barn_area  # manure per area of exposed surface, kg/m^2
        Q = cls._calc_Q(tempK, pH)
        if r * M * Q > 0:
            return num_animals * barn_area * ((total_ammoniacal_nitrogen / barn_area) * c * p) / (
                    r * M * Q)
        else:
            return 0.0

    @classmethod
    def calc_ammonia_storage_emission(cls,
                                      num_animals: int,
                                      barn_area: float,
                                      manure_total_ammoniacal_nitrogen: float,
                                      manure_mass: float,  # TODO: Decide to use volume or mass
                                      temperature_celsius: float,
                                      housing_specific_constant=GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT,
                                      ) -> float:
        """Calculates ammonia storage emissions for manure treatments.

        Parameters
        ----------
        num_animals : int
            Number of animals in the pen.
        barn_area : float
            Surface area per animal, m^2.
        manure_total_ammoniacal_nitrogen : float
            Total ammoniacal nitrogen in manure per animal, kg N.
        manure_mass : float
            Manure mass per animal, kg.
        temperature_celsius : float
            Current temperature, C.
        housing_specific_constant : float, optional
            Housing specific constant, s/m.
            The default is GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT.

        """
        return cls.calc_ammonia_emission(
            num_animals=num_animals,
            barn_area=barn_area,
            total_ammoniacal_nitrogen=manure_total_ammoniacal_nitrogen,
            mass=manure_mass,
            temperature_celsius=temperature_celsius,
            housing_specific_constant=housing_specific_constant
        )

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
