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

            E_{CH_4} = num\\_animals \\times max(0, 0.13 * T_{barn}) \\times barn\\_area / 1000

        where:

            :math:`E_{CH_4}` is the methane housing emission in kg :math:`CH_4/day`,

            :math:`T_{barn}` is the barn temperature in :math:`^{\circ}C`,

            :math:`barn\\_area` is the barn area per animal based on housing type in :math:`m^2`, and

            :math:`num\\_animals` is the number of animals in the pen.

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

            E_{CO_2} = num\\_animals \\times max(0, 0.0065 + 0.0192 * T_{barn}) \\times barn\\_area / 1000

        where:

            :math:`E_{CO_2}` is the carbon dioxide housing emission in kg :math:`CO_2/day`,

            :math:`T_{barn}` is the barn temperature in :math:`^{\circ}C`,

            :math:`barn\\_area` is the barn area per animal based on housing type in :math:`m^2`, and

            :math:`num\\_animals` is the number of animals in the pen.

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
    def calc_housing_ammonia_emission(cls, num_animals: int, barn_area_per_animal: float,
                                      urine_total_ammoniacal_nitrogen: float,
                                      urine: float, temp: float,
                                      pH=GasEmissionConstants.DEFAULT_PH_FOR_HOUSING_AMMONIA,
                                      hsc=GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT) -> float:
        """
        Calculate housing ammonia emission.

        Notes
        -----
        The equation used to calculate housing ammonia emission is:

        .. math::

            E_{NH_3} = total\\_barn\\_area \\times \\frac{TAN \\times c \\times \gamma}{r \\times M \\times Q}

        where:

            :math:`E_{NH_3}` is the housing ammonia emission in kg :math:`NH_3`/day,

            :math:`total\\_barn\\_area` is the total barn area in :math:`m^2`, calculated as :math:`num\\_animals \\times barn\\_area\\_per\\_animal`,

            :math:`TAN` is the total ammoniacal nitrogen in urine in kg, calculated as :math:`urine\\_total\\_ammoniacal\\_nitrogen  / total\\_barn\\_area`,

            :math:`c` is the number of seconds in a day (86400 s),

            :math:`\gamma` is the manure density in kg/:math:`m^3`,

            :math:`r` is the resistance of :math:`NH_3` transport to the atmosphere in s/m,

            :math:`M` is the manure urine per area of exposed surface in kg/:math:`m^2`, calculated as :math:`urine / total\\_barn\\_area`,

            :math:`Q` is the equilibrium coefficient for the :math:`NH_3` gas in the air (unitless).

        The value of :math:`r` is calculated as:

        .. math::

            r_{barn} = HSC \\times [1 - 0.027 \\times (20 - T)]

        where:

            :math:`r_{barn}` is the resistance of :math:`NH_3` transport to the atmosphere (s/m),

            :math:`HSC` is the housing-specific constant (s/m, default is 260 s/m),

            :math:`T` is the barn temperature (:math:`^{\circ}C`).

        The value of :math:`Q` is calculated as:

        .. math::

            Q = K_h \\times K_a

        where:

            :math:`Q` is the equilibrium coefficient for the :math:`NH_3` gas in the air (unitless),

            :math:`K_h` is the Henry's law coefficient of :math:`NH_3` (unitless),

            :math:`K_a` is the dissociation coefficient of ammonium ion (unitless).

        The value of :math:`K_h` is calculated as:

        .. math::

            K_h = 10^{1478 / T - 1.69}

        where:

            :math:`K_h` is the Henry's law coefficient of :math:`NH_3` (unitless),

            :math:`T` is the barn temperature (:math:`^{\circ}C`).

        The value of :math:`K_a` is calculated as:

        .. math::

            K_a = 1 + 10^{0.09018 + 2729.9 / T - pH}

        where:

            :math:`K_a` is the dissociation coefficient of ammonium ion (unitless),

            :math:`T` is the barn temperature (:math:`^{\circ}C`),

            :math:`pH` is the manure solution acidity (unitless).

        Parameters
        ----------
        num_animals : int
            Number of animals in the barn (unitless).
        barn_area_per_animal : float
            Barn area per animal based on housing type (:math:`m^2`).
        urine_total_ammoniacal_nitrogen : float
            Total ammoniacal nitrogen in urine (kg).
        urine : float
            Amount of urine produced by animals in the barn (kg).
        temp : float
            Current barn temperature (:math:`^{\circ}C`).
        pH : float, optional
            pH value for housing ammonia emission (unitless). Default is set to 7.7. This value is listed as
                :attr:`DEFAULT_PH_FOR_HOUSING_AMMONIA` in :class:`GasEmissionConstants`.
        hsc : float, optional
            Housing-specific constant (unitless). Default is set to 260 s/m. This value is listed as
                :attr:`DEFAULT_HOUSING_SPECIFIC_CONSTANT` in :class:`GasEmissionConstants`.

        Returns
        -------
        float
            Housing ammonia emission (kg :math:`NH_3`/day).

        Raises
        ------
        ValueError
            If the number of animals, barn area, urine total ammoniacal nitrogen, or urine is less than 0.

        """
        if num_animals < 0:
            raise ValueError('Number of animals must be greater than or equal to 0.')

        if barn_area_per_animal < 0:
            raise ValueError('Barn area must be greater than or equal to 0.')

        if urine_total_ammoniacal_nitrogen < 0:
            raise ValueError('Urine total ammoniacal nitrogen must be greater than or equal to 0.')

        if urine < 0:
            raise ValueError('Urine must be greater than or equal to 0.')

        # If any of the aforementioned values is 0, then the result will be 0.
        if num_animals == 0 or barn_area_per_animal == 0 or urine_total_ammoniacal_nitrogen == 0 or urine == 0:
            return 0.0

        total_barn_area = num_animals * barn_area_per_animal
        total_ammoniacal_nitrogen = urine_total_ammoniacal_nitrogen / total_barn_area
        manure_density = ManureConstants.MANURE_DENSITY  # kg/m^3
        seconds_per_day = GeneralConstants.SECONDS_PER_DAY
        temperature_kelvin = cls._convert_temperature_celsius_to_kelvin(temp)
        ammonia_barn_resistance = cls._calc_ammonia_barn_resistance(temp, hsc)
        manure_urine_per_area = urine / total_barn_area  # kg/m^2
        equilibrium_coefficient = cls._calc_equilibrium_coefficient(temperature_kelvin, pH)
        ammonia_loss = (total_ammoniacal_nitrogen * seconds_per_day * manure_density) / \
                       (ammonia_barn_resistance * manure_urine_per_area * equilibrium_coefficient)
        total_ammonia_loss = ammonia_loss * total_barn_area
        return max(0.0, total_ammonia_loss)

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
        r = cls._calc_ammonia_barn_resistance(temperature_celsius, housing_specific_constant)
        M = mass / barn_area  # manure per area of exposed surface, kg/m^2
        Q = cls._calc_equilibrium_coefficient(tempK, pH)
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

    @classmethod
    def _calc_ammonia_barn_resistance(cls, temp: float, hsc=GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT) -> float:
        """
        Calculate resistance of :math:`NH_3` transport to the atmosphere in a barn.

        Notes
        -----
        The equation used to calculate resistance of :math:`NH_3` transport to the atmosphere in a barn is:

        .. math::

            r_{barn} = HSC \\times [1 - 0.027 \\times (20 - T)]

        where:

            :math:`r_{barn}` is resistance of :math:`NH_3` transport to the atmosphere in a barn (s/m),

            :math:`HSC` is housing specific constant (s/m, default is 260 s/m),

            :math:`T` is barn temperature (:math:`^{\circ}C`).

        Parameters
        ----------
        temp : float
            Temperature in Celsius (:math:`^{\circ}C`).
        hsc : float, optional
            Housing specific constant, s/m. Default is set to 260 s/m. This value is listed as
                :attr:`DEFAULT_HOUSING_SPECIFIC_CONSTANT` in :class:`GasEmissionConstants`.

        Returns
        -------
        float
            Resistance of :math:`NH_3` transport to the atmosphere in a barn, s/m.

        """
        return hsc * (1 - 0.027 * (20.0 - temp))

    @classmethod
    def _calc_henry_law_coefficient_of_ammonia(cls, temp: float) -> float:
        """
        Calculate Henry's law coefficient of ammonia.

        Notes
        -----
        The equation used to calculate Henry's law coefficient of ammonia is:

        .. math::

            K_h = 10^{1478/T - 1.69}

        where:

            :math:`K_h` is Henry's law coefficient (unitless),

            :math:`T` is temperature (K).

        Parameters
        ----------
        temp : float
            Temperature in Kelvin (K).

        Returns
        -------
        float
            Henry's law coefficient of ammonia (unitless).

        """
        return 10 ** (1478 / temp - 1.69)

    @classmethod
    def _calc_dissociation_coefficient_of_ammonium(cls, temp: float, pH: float) -> float:
        """
        Calculate dissociation coefficient of ammonium.

        Notes
        -----
        The equation used to calculate the dissociation coefficient of ammonium is:

        .. math::

            K_a = 1 + 10^{0.09018 + 2729.9/T - pH}

        where:

            :math:`K_a` is the dissociation coefficient of ammonium (unitless),

            :math:`T` is temperature (K),

            :math:`pH` is the manure solution acidity (unitless).

        Parameters
        ----------
        temp : float
            Temperature in Kelvin (K).
        pH : float
            Manure solution acidity (unitless).

        Returns
        -------
        float
            Dissociation coefficient of ammonium (unitless).

        """
        return 1 + 10 ** (0.09018 + 2729.9 / temp - pH)

    @classmethod
    def _calc_equilibrium_coefficient(cls, temp: float, pH: float) -> float:
        """
        Calculate Q, the equilibrium coefficient for the :math:`NH_3` gas in the air for a given
        concentration of total ammoniacal nitrogen in the solution.

        Notes
        -----
        The equation used to calculate Q is:

        .. math::

            Q = K_h * K_a

        where:

            :math:`Q` is the equilibrium coefficient for the :math:`NH_3` gas in the air (unitless),

            :math:`K_h` is Henry's law coefficient of ammonia (unitless), and

            :math:`K_a` is the dissociation coefficient of ammonium (unitless).

        Parameters
        ----------
        temp : float
            Manure solution temperature in Kelvin (K).
        pH : float
            Manure solution acidity (unitless).

        Returns
        -------
        float
            Equilibrium coefficient for the :math:`NH_3` gas in the air (unitless).

        """
        Kh = cls._calc_henry_law_coefficient_of_ammonia(temp)
        Ka = cls._calc_dissociation_coefficient_of_ammonium(temp, pH)
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
    def calc_methane_emission_from_anaerobic_lagoon(cls, manure_volatile_solids: float) -> float:
        """
        Calculate methane emission from anaerobic lagoon.

        Notes
        -----
        The equation used to calculate methane emission from anaerobic lagoon is:

        .. math::

            E_{CH_4} = Bo \cdot MCF \cdot MS \cdot MF \cdot VS

        where:

            :math:`E_{CH_4}` is methane emissions from anaerobic lagoon (kg :math:`CH_4`-N/day),

            :math:`Bo` is the achievable emission of methane during anaerobic digestion (kg :math:`CH_4`/kg VS),

            :math:`MCF` is the methane conversion factor (unitless),

            :math:`MS` is the fraction of manure handled by the anaerobic lagoon (unitless),

            :math:`MF` is the unit conversion factor for methane from :math:`m^3` to kg (unitless),

            :math:`VS` is the amount of volatile solids in manure (kg).

        Parameters
        ----------
        manure_volatile_solids : float
            Amount of volatile solids in manure (kg).

        Returns
        -------
        float
            Methane emission from anaerobic lagoon (kg :math:`CH_4`-N/day).

        """
        Bo = GasEmissionConstants.Bo
        MCF = GasEmissionConstants.METHANE_CONVERSION_FACTOR
        MS = GasEmissionConstants.FRACTION_OF_HANDLED_MANURE
        MF = GasEmissionConstants.METHANE_FACTOR
        return Bo * MCF * MS * MF * manure_volatile_solids
