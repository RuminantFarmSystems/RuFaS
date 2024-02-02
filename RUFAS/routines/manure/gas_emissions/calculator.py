import math

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.manure.constants_and_units.gas_emission_constants import (
    GasEmissionConstants,
)
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants


class GasEmissionsCalculator:
    @classmethod
    def methane_emission_from_slurry_storage(
            cls,
            total_volatile_solids: float,
            temp=GasEmissionConstants.DEFAULT_SLURRY_STORAGE_TEMPERATURE,
    ) -> float:
        """
        Calculate the methane emission from manure storage using total volatile solids.

        Notes
        -----
        The equation used to calculate the methane emission from manure storage is as follows:

        .. math::

            E_{CH_4} = 24 \\cdot VS_{d} \\cdot b_{1} \\cdot e^{lnA - \\frac{E}{RT}}
            + 24 \\cdot VS_{nd} \\cdot b_{2} \\cdot e^{lnA - \\frac{E}{RT}}

        where:

            :math:`E_{CH_4}` is the methane emission from manure storage (kg :math:`CH_4`/day),

            :math:`VS_{d}` is the degradable volatile solids in manure (kg),

            :math:`b_{1}` is the degradable volatile solids rate correcting factor (1.0, unitless),

            :math:`VS_{nd}` is the non-degradable volatile solids in manure (kg),

            :math:`b_{2}` is the non-degradable volatile solids rate correcting factor (0.01, unitless),

            :math:`lnA` is the natural log of the Arrhenius constant (43.33, unitless),

            :math:`E` is the activation energy (112700.0 J/mol),

            :math:`R` is the ideal gas constant (8.314 J/mol :math:`\\cdot` K),

            :math:`T` is the temperature in Kelvin (:math:`K`).

        The degradable and non-degradable volatile solids are calculated using the following equations:

        .. math::

            VS_d = \\frac{VS \\cdot B_o}{E_{CH_4,pot}}

            VS_{nd} = VS - VS_d

        where:

            :math:`VS` is the total volatile solids in manure (kg),

            :math:`VS_d` is the degradable volatile solids in manure (kg),

            :math:`VS_{nd}` is the non-degradable volatile solids in manure (kg),

            :math:`B_o` is the achievable methane emission (0.24 kg :math:`CH_4`/kg VS),

            :math:`E_{CH_4,pot}` is the potential methane production (0.48 kg :math:`CH_4`/kg VS).

        Parameters
        ----------
        total_volatile_solids : float
            Total volatile solids in manure (kg).
        temp : float
            Temperature in Celsius (:math:`^\\circ C`). Default is set to 20 degrees Celsius. This value is
            listed as :attr:`DEFAULT_SLURRY_STORAGE_TEMPERATURE` in :class:`GasEmissionConstants`.

        Returns
        -------
        float
            Methane emission from manure storage (kg :math:`CH_4`/day).

        """
        if total_volatile_solids < 0:
            raise ValueError(
                f"Total volatile solids must be greater than 0. Total volatile solids provided: {total_volatile_solids}"
            )

        arrhenius_exponent = cls._arrhenius_exponent(temp)

        (
            degradable_volatile_solids,
            non_degradable_volatile_solids,
        ) = cls._volatile_solid_components(total_volatile_solids)

        methane_emission_from_degradable_volatile_solids = (
                GasEmissionConstants.METHANE_EMISSION_COEFFICIENT
                * degradable_volatile_solids
                * GasEmissionConstants.DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR
                * arrhenius_exponent
        )
        methane_emission_from_non_degradable_volatile_solids = (
                GasEmissionConstants.METHANE_EMISSION_COEFFICIENT
                * non_degradable_volatile_solids
                * GasEmissionConstants.NON_DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR
                * arrhenius_exponent
        )

        methane_emission = (
                methane_emission_from_degradable_volatile_solids
                + methane_emission_from_non_degradable_volatile_solids
        )

        return methane_emission

    @classmethod
    def _arrhenius_exponent(cls, temp: float) -> float:
        """
        Calculate the Arrhenius exponent.

        Notes
        -----
        The Arrhenius exponent is calculated as follows:

        .. math::

            e^{lnA - \\frac{E}{RT}}

        where:

            :math:`lnA` is the natural log of the Arrhenius constant (unitless),

            :math:`E` is the activation energy (joules per mol, J/mol),

            :math:`R` is the universal gas constant (joules per mol Kelvin, J/mol :math:`\\cdot` K),

            :math:`T` is the temperature in Kelvin (K).

        Parameters
        ----------
        temp : float
            Temperature in Celsius (:math:`^\\circ C`).

        Returns
        -------
        float
            Arrhenius exponent (unitless).

        Raises
        ------
        ValueError
            If the temperature is not between -40 and 50 degrees Celsius.

        """
        if not (GasEmissionConstants.GENERAL_LOWER_BOUND_TEMPERATURE <= temp
                <= GasEmissionConstants.GENERAL_UPPER_BOUND_TEMPERATURE):
            raise ValueError(
                f"Temperature must be between -40 and 60 degrees Celsius. Temperature provided: {temp}"
            )

        temp_kelvin = cls._convert_temperature_celsius_to_kelvin(temp)
        return math.exp(
            GasEmissionConstants.NATURAL_LOG_ARRHENIUS_CONSTANT
            - (
                    GasEmissionConstants.ACTIVATION_ENERGY
                    / (GasEmissionConstants.GAS_CONSTANT * temp_kelvin)
            )
        )

    @classmethod
    def _volatile_solid_components(
            cls, total_volatile_solids: float
    ) -> tuple[float, float]:
        """
        Calculate the degradable and non-degradable volatile solids.

        Notes
        -----
        The degradable and non-degradable volatile solids are calculated as follows:

        .. math::

            VS_d = \\frac{VS \\cdot B_o}{E_{CH_4,pot}}

            VS_{nd} = VS - VS_d

        where:

            :math:`VS_d` is the degradable volatile solids (kg),

            :math:`VS_{nd}` is the non-degradable volatile solids (kg),

            :math:`VS` is the total volatile solids (kg),

            :math:`B_o` is the achievable methane emission (kg :math:`CH_4`/kg VS),

            :math:`E_{CH_4,pot}` is the potential methane yield of manure (kg :math:`CH_4`/kg VS).

        Parameters
        ----------
        total_volatile_solids : float
            Total volatile solids in manure (kg).

        Returns
        -------
        tuple[float, float]
            Degradable volatile solids (kg) and non-degradable volatile solids (kg).

        Raises
        ------
        ValueError
            If the total volatile solids is negative.

        """
        if total_volatile_solids < 0:
            raise ValueError(
                f"Total volatile solids must be non-negative. Total volatile solids provided: {total_volatile_solids}"
            )

        degradable_volatile_solids = (
                total_volatile_solids
                * GasEmissionConstants.ACHIEVABLE_METHANE_EMISSION
                / GasEmissionConstants.POTENTIAL_METHANE_YIELD_OF_MANURE
        )
        non_degradable_volatile_solids = (
                total_volatile_solids - degradable_volatile_solids
        )
        return degradable_volatile_solids, non_degradable_volatile_solids

    # TODO: to be removed in the next PR while refactoring slurry storage treatments - Issue #1066
    @classmethod
    def methane_emission_for_slurry_storage(
            cls,
            manure_total_solids: float,
            is_enclosed=False,
            temperature_celsius=GasEmissionConstants.DEFAULT_SLURRY_STORAGE_TEMPERATURE,
            manure_volatile_solids_fraction=(
                    GasEmissionConstants.DEFAULT_VOLATILE_SOLIDS_FRACTION
            ),
            efficiency_fraction=0.99,
    ) -> float:
        """Calculates methane emissions from manure storage using total solids.

        Args:
            manure_total_solids: Total solids, kg.
            is_enclosed: True if manure storage is enclosed, and False if manure storage is open to air.
            temperature_celsius: temperature in Celsius, C.
            manure_volatile_solids_fraction: Fraction (0-1) volatile solids. # TODO: review this - Issue #1066
            efficiency_fraction: efficiency of process, unitless. # TODO: review this - Issue #1066

        Returns:
            CH4 emissions from storage, kg CH4/day.

        """
        c = 0.024
        VS_tot = manure_total_solids * manure_volatile_solids_fraction

        constants = GasEmissionConstants
        b1 = constants.DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR
        b2 = constants.NON_DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR
        lnA = constants.NATURAL_LOG_ARRHENIUS_CONSTANT
        E = constants.ACTIVATION_ENERGY
        R = constants.GAS_CONSTANT
        Bo = constants.ACHIEVABLE_METHANE_EMISSION
        E_CH4_pot = constants.POTENTIAL_METHANE_YIELD_OF_MANURE

        tempK = cls._convert_temperature_celsius_to_kelvin(temperature_celsius)
        ex = math.exp(lnA - (E / (R * tempK)))

        VSd = Bo / E_CH4_pot
        VSnd = 1 - VSd
        E_CH4_open_air = c * VS_tot * (VSd * b1 + VSnd * b2) * ex

        if not is_enclosed:
            return E_CH4_open_air
        else:
            return E_CH4_open_air * (1 - efficiency_fraction)

    @classmethod
    def _modified_hours(cls, hours: float) -> float:
        """
        Calculate modified hours based on the specific conditions.

        Notes
        -----
        The modified hours is calculated using a piecewise-defined hyperbolic tangent function as follows:

        .. math::

            \\begin{cases}
                \\frac{-\\tanh(hours - 21.5)}{3.5} & \\text{if } hours > 14 \\\\
                \\frac{\\tanh(hours - 9.5)}{2.5} & \\text{if } 4 < hours \\leq 14 \\\\
                \\frac{-\\tanh(hours + 3.5)}{3.5} & \\text{if } hours \\leq 4
            \\end{cases}

        where:

            :math:`hours` is the input hour(s) of the day.

        Parameters
        ----------
        hours : float
            The input hour(s) of the day, must be in the range of [0, 24].

        Returns
        -------
        float
            The modified hours as calculated using the piecewise-defined hyperbolic tangent function.

        Raises
        ------
        ValueError
            If the input `hours` is not in the range [0, 24].

        """
        if not 0 <= hours <= 24:
            raise ValueError(
                f"Hours must be in the range of [0, 24]. Hours provided: {hours}"
            )

        if hours > 14:
            return -math.tanh(hours - 21.5) / 3.5
        elif hours > 4:
            return math.tanh(hours - 9.5) / 2.5
        else:
            return -math.tanh(hours + 3.5) / 3.5

    @classmethod
    def _ambient_temperature(
            cls, hours: float, min_temp: float, max_temp: float
    ) -> float:
        """
        Calculate the ambient temperature based on the time of the day and the minimum and maximum barn temperatures.

        Notes
        -----
        The ambient temperature is calculated as follows:

        .. math::

            T_{ambient} = modified\\_hours \\cdot \\frac{T_{max} - T_{min}}{2} + \\frac{T_{max} + T_{min}}{2}

        where:

            :math:`T_{ambient}` is the ambient temperature,

            :math:`T_{min}` and :math:`T_{max}` are the minimum and maximum barn temperatures, respectively,

            :math:`modified_{hours}` is the result of the :func:`_modified_hours` function.

        Parameters
        ----------
        hours : float
            The hour(s) of the day, must be in the range of [0, 24].
        min_temp : float
            The minimum barn temperature (:math:`^{\\circ}C`).
        max_temp : float
            The maximum barn temperature (:math:`^{\\circ}C`). Must be greater than or equal to `min_temp`.

        Returns
        -------
        float
            The ambient temperature (:math:`^{\\circ}C`).

        Raises
        ------
        ValueError
            If the input `hours` is not in the range [0, 24],
            If `min_temp` is greater than `max_temp`.

        """
        if not 0 <= hours <= 24:
            raise ValueError(
                f"Hours should be between 0 and 24. Hours provided: {hours}"
            )
        if min_temp > max_temp:
            raise ValueError(
                f"Minimum temperature cannot be greater than maximum temperature: {min_temp=}, {max_temp=}"
            )

        modified_hours = cls._modified_hours(hours)
        return modified_hours * (max_temp - min_temp) / 2 + (max_temp + min_temp) / 2

    @classmethod
    def housing_methane_emission(
            cls, num_animals: int, barn_area: float, barn_temp: float
    ) -> float:
        """
        Calculate housing methane emissions from manure handlers.

        Notes
        -----
        The equation used to calculate housing methane emissions is:

        .. math::

            E_{CH_4} = num\\_animals \\times max(0, 0.13 * T_{barn}) \\times barn\\_area / 1000

        where:

            :math:`E_{CH_4}` is the methane housing emission in kg :math:`CH_4/day`,

            :math:`T_{barn}` is the barn temperature in :math:`^{\\circ}C`,

            :math:`barn\\_area` is the barn area per animal based on housing type in :math:`m^2`, and

            :math:`num\\_animals` is the number of animals in the pen.

        Parameters
        ----------
        num_animals : int
            Number of animals in the pen (unitless).
        barn_area : float
            Barn area per animal based on housing type (:math:`m^2`).
        barn_temp : float
            Current barn temperature (:math:`^{\\circ}C`).

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
            raise ValueError("Number of animals must be greater than or equal to 0.")

        if barn_area < 0:
            raise ValueError("Barn area must be greater than or equal to 0.")

        return num_animals * max(0.0, 0.13 * barn_temp) * barn_area / 1000

    @classmethod
    def housing_carbon_dioxide_emission(
            cls, num_animals: int, barn_area: float, barn_temp: float
    ) -> float:
        """
        Calculate carbon dioxide housing emission.

        Notes
        -----
        The equation used to calculate housing carbon dioxide emissions is:

        .. math::

            E_{CO_2} = num\\_animals \\times max(0, 0.0065 + 0.0192 * T_{barn}) \\times barn\\_area / 1000

        where:

            :math:`E_{CO_2}` is the carbon dioxide housing emission in kg :math:`CO_2/day`,

            :math:`T_{barn}` is the barn temperature in :math:`^{\\circ}C`,

            :math:`barn\\_area` is the barn area per animal based on housing type in :math:`m^2`, and

            :math:`num\\_animals` is the number of animals in the pen.

        Parameters
        ----------
        num_animals : int
            Number of animals in the pen (unitless).
        barn_area : float
            Barn area per animal based on housing type (:math:`m^2`).
        barn_temp : float
            Current barn temperature (:math:`^{\\circ}C`).

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
            raise ValueError("Number of animals must be greater than or equal to 0.")

        if barn_area < 0:
            raise ValueError("Barn area must be greater than or equal to 0.")

        return num_animals * max(0.0, 0.0065 + 0.0192 * barn_temp) * barn_area / 1000

    @classmethod
    def housing_ammonia_emission(
            cls,
            num_animals: int,
            barn_area_per_animal: float,
            urine_total_ammoniacal_nitrogen: float,
            urine: float,
            temp: float,
            pH=GasEmissionConstants.DEFAULT_PH_FOR_HOUSING_AMMONIA,
            hsc=GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT,
    ) -> float:
        """
        Calculate housing ammonia emission.

        Notes
        -----
        The equation used to calculate housing ammonia emission is:

        .. math::

            E_{NH_3} = total\\_barn\\_area \\times \\frac{TAN \\times c \\times \\gamma}{r \\times M \\times Q}

        where:

            :math:`E_{NH_3}` is the housing ammonia emission in kg :math:`NH_3`/day,

            :math:`total\\_barn\\_area` is the total barn area in :math:`m^2`, calculated as
            :math:`num\\_animals \\times barn\\_area\\_per\\_animal`,

            :math:`TAN` is the total ammoniacal nitrogen in urine in kg, calculated as
            :math:`urine\\_total\\_ammoniacal\\_nitrogen  / total\\_barn\\_area`,

            :math:`c` is the number of seconds in a day (86400 s),

            :math:`\\gamma` is the manure density in kg/:math:`m^3`,

            :math:`r` is the resistance of :math:`NH_3` transport to the atmosphere in s/m,

            :math:`M` is the manure urine per area of exposed surface in kg/:math:`m^2`, calculated as
            :math:`urine / total\\_barn\\_area`,

            :math:`Q` is the equilibrium coefficient for the :math:`NH_3` gas in the air (unitless).

        The value of :math:`r` is calculated as:

        .. math::

            r_{barn} = HSC \\times [1 - 0.027 \\times (20 - T)]

        where:

            :math:`r_{barn}` is the resistance of :math:`NH_3` transport to the atmosphere (s/m),

            :math:`HSC` is the housing-specific constant (s/m, default is 260 s/m),

            :math:`T` is the barn temperature (:math:`^{\\circ}C`).

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

            :math:`T` is the barn temperature (:math:`^{\\circ}C`).

        The value of :math:`K_a` is calculated as:

        .. math::

            K_a = 1 + 10^{0.09018 + 2729.9 / T - pH}

        where:

            :math:`K_a` is the dissociation coefficient of ammonium ion (unitless),

            :math:`T` is the barn temperature (:math:`^{\\circ}C`),

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
            Current barn temperature (:math:`^{\\circ}C`).
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
            raise ValueError("Number of animals must be greater than or equal to 0.")

        if barn_area_per_animal < 0:
            raise ValueError("Barn area must be greater than or equal to 0.")

        if urine_total_ammoniacal_nitrogen < 0:
            raise ValueError(
                "Urine total ammoniacal nitrogen must be greater than or equal to 0."
            )

        if urine < 0:
            raise ValueError("Urine must be greater than or equal to 0.")

        # If any of the aforementioned values is 0, then the result will be 0.
        if (
                num_animals == 0
                or barn_area_per_animal == 0
                or urine_total_ammoniacal_nitrogen == 0
                or urine == 0
        ):
            return 0.0

        total_barn_area = num_animals * barn_area_per_animal
        total_ammoniacal_nitrogen = urine_total_ammoniacal_nitrogen / total_barn_area
        manure_density = ManureConstants.MANURE_DENSITY  # kg/m^3
        seconds_per_day = GeneralConstants.SECONDS_PER_DAY
        temperature_kelvin = cls._convert_temperature_celsius_to_kelvin(temp)
        ammonia_barn_resistance = cls._ammonia_barn_resistance(temp, hsc)
        manure_urine_per_area = urine / total_barn_area  # kg/m^2
        equilibrium_coefficient = cls._equilibrium_coefficient(temperature_kelvin, pH)
        ammonia_loss = (
                               total_ammoniacal_nitrogen * seconds_per_day * manure_density
                       ) / (ammonia_barn_resistance * manure_urine_per_area * equilibrium_coefficient)
        total_ammonia_loss = ammonia_loss * total_barn_area
        return max(0.0, total_ammonia_loss)

    @classmethod
    def storage_ammonia_emission(
            cls,
            num_animals: int,
            manure_total_ammoniacal_nitrogen: float,
            manure_volume: float,
            manure_density: float,
            total_solids: float,
            temp: float,
            storage_area_per_animal=GasEmissionConstants.DEFAULT_STORAGE_AREA_PER_ANIMAL,
            pH=GasEmissionConstants.DEFAULT_PH_FOR_STORAGE_AMMONIA,
    ) -> float:
        """
        Calculate storage ammonia emissions for manure treatments.

        Notes
        -----
        The equation used to calculate storage ammonia emission is:

        .. math::

            E_{NH_3} = total\\_storage\\_area \\cdot \\frac{TAN \\cdot c \\cdot \\gamma}{r \\cdot M \\cdot Q}

        where:

            :math:`E_{NH_3}` is the storage ammonia emission in kg :math:`NH_3`/day,

            :math:`total\\_storage\\_area` is the total storage area in :math:`m^2`, calculated as
            :math:`num\\_animals \\times storage\\_area\\_per\\_animal`,

            :math:`TAN` is the total ammoniacal nitrogen in manure in kg,

            :math:`c` is the number of seconds in a day (86400 s),

            :math:`\\gamma` is the manure density in kg/:math:`m^3`,

            :math:`r` is the resistance of :math:`NH_3` transport to the atmosphere in s/m,

            :math:`M` is the manure mass excluding solids per area of exposed surface in kg/:math:`m^2`,
            calculated as :math:`(total\\_manure\\_mass - total\\_solids) / total\\_storage\\_area`,

            :math:`Q` is the equilibrium coefficient for the :math:`NH_3` gas in the air (unitless).

        The value of :math:`r` is calculated as:

        .. math::

            r_{storage} = HSC \\cdot [1 - 0.027 \\cdot (20 - T)]

        where:

            :math:`r_{storage}` is the resistance of :math:`NH_3` transport to the atmosphere (s/m),

            :math:`HSC` is the housing-specific constant (s/m, default is 260 s/m),

            :math:`T` is the storage area temperature (:math:`^{\\circ}C`).

        The value of :math:`Q` is calculated as:

        .. math::

            Q = K_h \\cdot K_a

        where:

            :math:`Q` is the equilibrium coefficient for the :math:`NH_3` gas in the air (unitless),

            :math:`K_h` is the Henry's law coefficient of :math:`NH_3` (unitless),

            :math:`K_a` is the dissociation coefficient of ammonium ion (unitless).

        The value of :math:`K_h` is calculated as:

        .. math::

            K_h = 10^{1478 / T - 1.69}

        where:

            :math:`K_h` is the Henry's law coefficient of :math:`NH_3` (unitless),

            :math:`T` is the storage area temperature in Kelvin.

        The value of :math:`K_a` is calculated as:

        .. math::

            K_a = 1 + 10^{0.09018 + 2729.9 / T - pH}

        where:

            :math:`K_a` is the dissociation coefficient of ammonium ion (unitless),

            :math:`T` is the storage area temperature in Kelvin,

            :math:`pH` is the manure solution acidity (unitless).

        Parameters
        ----------
        num_animals : int
            Number of animals in the storage area (unitless).
        manure_total_ammoniacal_nitrogen : float
            Total ammoniacal nitrogen in manure (kg).
        manure_volume : float
            Total volume of the manure produced by the animals in the storage area (:math:`m^3`).
        manure_density : float
            Density of the manure (kg/:math:`m^3`).
        total_solids : float
            Total solids present in the manure (kg).
        temp : float
            Current storage area temperature (:math:`^{\\circ}C`).
        storage_area_per_animal : float, optional
            Storage area per animal based on manure treatment type (:math:`m^2`).
            Default is set to a value listed as :attr:`DEFAULT_STORAGE_AREA_PER_ANIMAL
            in :class:`GasEmissionConstants`.
        pH : float, optional
            pH value for storage ammonia emission (unitless). Default is set to a value listed as
            :attr:`DEFAULT_PH_FOR_STORAGE_AMMONIA` in :class:`GasEmissionConstants`.

        Returns
        -------
        float
            Storage ammonia emission (kg :math:`NH_3`/day).

        Raises
        ------
        ValueError
            If the number of animals, storage area, manure total ammoniacal nitrogen, manure volume, manure density or
            total solids in manure are less than 0.

        """
        if num_animals < 0:
            raise ValueError("Number of animals must be greater than or equal to 0.")
        if storage_area_per_animal < 0:
            raise ValueError(
                "Storage area per animal must be greater than or equal to 0."
            )
        if manure_total_ammoniacal_nitrogen < 0:
            raise ValueError(
                "Manure total ammoniacal nitrogen must be greater than or equal to 0."
            )
        if manure_volume < 0:
            raise ValueError("Manure volume must be greater than or equal to 0.")
        if manure_density < 0:
            raise ValueError("Manure density must be greater than or equal to 0.")
        if total_solids < 0:
            raise ValueError("Total solids must be greater than or equal to 0.")

        # If any of the input parameters is 0, then the result will be 0.
        if any(
                param == 0
                for param in [
                    num_animals,
                    storage_area_per_animal,
                    manure_total_ammoniacal_nitrogen,
                    manure_volume,
                    manure_density,
                    total_solids,
                ]
        ):
            return 0.0

        total_storage_area = num_animals * storage_area_per_animal
        temp_kelvin = cls._convert_temperature_celsius_to_kelvin(temp)
        total_manure_mass = manure_volume * manure_density
        housing_specific_constant = cls._housing_specific_constant(
            total_manure_mass, total_solids
        )
        storage_area_resistance = cls._ammonia_barn_resistance(
            temp, housing_specific_constant
        )
        manure_mass_excluding_solids = total_manure_mass - total_solids
        equilibrium_coefficient = cls._equilibrium_coefficient(temp_kelvin, pH)
        ammonia_loss = (
                               manure_total_ammoniacal_nitrogen
                               * GeneralConstants.SECONDS_PER_DAY
                               * manure_density
                       ) / (
                               storage_area_resistance
                               * manure_mass_excluding_solids
                               * equilibrium_coefficient
                       )
        total_ammonia_loss = ammonia_loss * total_storage_area
        return max(0.0, total_ammonia_loss)

    @classmethod
    def _housing_specific_constant(
            cls, manure_mass: float, total_solids: float
    ) -> float:
        """
        Calculate housing specific constant.

        The housing-specific constant represents the resistance of ammonia transport to the atmosphere,
        and its value depends on the type of manure being considered. The different types of manure
        include solid and semi-solid manure, slurry manure, and liquid manure.

        Parameters
        ----------
        manure_mass : float
            Total manure mass (kg). Must be greater than or equal to 0.
        total_solids : float
            Total solids in manure (kg). Must be greater than or equal to 0.

        Returns
        -------
        float
            Housing specific constant, s/m.

        Raises
        ------
        ValueError
            If manure_mass or total_solids are less than 0.

        """
        if manure_mass < 0.0:
            raise ValueError("Manure mass must be greater than or equal to 0.")
        elif total_solids < 0.0:
            raise ValueError("Total solids must be greater than or equal to 0.")
        elif manure_mass == 0.0 or total_solids == 0.0:
            return GasEmissionConstants.SOLID_AND_SEMI_SOLID_MANURE_HSC

        dry_matter = manure_mass / total_solids

        if dry_matter >= GasEmissionConstants.SOLID_MANURE_THRESHOLD:
            return GasEmissionConstants.SOLID_AND_SEMI_SOLID_MANURE_HSC
        elif dry_matter >= GasEmissionConstants.SLURRY_MANURE_THRESHOLD:
            return GasEmissionConstants.SLURRY_MANURE_HSC
        else:
            return GasEmissionConstants.LIQUID_MANURE_HSC

    @classmethod
    def ammonia_emission(
            cls,
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
        r = cls._ammonia_barn_resistance(temperature_celsius, housing_specific_constant)
        M = mass / barn_area  # manure per area of exposed surface, kg/m^2
        Q = cls._equilibrium_coefficient(tempK, pH)
        if r * M * Q > 0:
            return (
                    num_animals
                    * barn_area
                    * ((total_ammoniacal_nitrogen / barn_area) * c * p)
                    / (r * M * Q)
            )
        else:
            return 0.0

    @classmethod
    def ammonia_storage_emission(
            cls,
            num_animals: int,
            barn_area: float,
            manure_total_ammoniacal_nitrogen: float,
            manure_mass: float,  # TODO: Decide to use volume or mass - Issue #1117
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
        return cls.ammonia_emission(
            num_animals=num_animals,
            barn_area=barn_area,
            total_ammoniacal_nitrogen=manure_total_ammoniacal_nitrogen,
            mass=manure_mass,
            temperature_celsius=temperature_celsius,
            housing_specific_constant=housing_specific_constant,
        )

    @classmethod
    def _ammonia_barn_resistance(
            cls, temp: float, hsc=GasEmissionConstants.DEFAULT_HOUSING_SPECIFIC_CONSTANT
    ) -> float:
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

            :math:`T` is barn temperature (:math:`^{\\circ}C`).

        Parameters
        ----------
        temp : float
            Temperature in Celsius (:math:`^{\\circ}C`).
        hsc : float, optional
            Housing specific constant, s/m. Default is set to 260 s/m. This value is listed as
                :attr:`DEFAULT_HOUSING_SPECIFIC_CONSTANT` in :class:`GasEmissionConstants`.

        Returns
        -------
        float
            Resistance of :math:`NH_3` transport to the atmosphere in a barn, s/m.

        """
        return hsc * (1 - 0.027 * (20.0 - max(temp, -15.0)))

    @classmethod
    def _henry_law_coefficient_of_ammonia(cls, temp: float) -> float:
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
    def _dissociation_coefficient_of_ammonium(cls, temp: float, pH: float) -> float:
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
    def _equilibrium_coefficient(cls, temp: float, pH: float) -> float:
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
        Kh = cls._henry_law_coefficient_of_ammonia(temp)
        Ka = cls._dissociation_coefficient_of_ammonium(temp, pH)
        return Kh * Ka

    @classmethod
    def _convert_temperature_celsius_to_kelvin(
            cls, temperature_celsius: float
    ) -> float:
        """Converts a temperature from Celsius to Kelvin.

        Args:
            temperature_celsius: temperature in Celsius, C.

        Returns:
            Temperature in Kelvin, K.

        """
        return temperature_celsius + 273.15

    @classmethod
    def methane_volume_via_Chen_equation(
            cls, manure_total_volatile_solids: float, hydraulic_retention_time: int
    ) -> float:
        """Calculates CH4 generation volume using the Chen-Hashimoto equation.

        Args:
            manure_total_volatile_solids: total volatile solids, kg.
            hydraulic_retention_time: hydraulic retention time, days.

        Returns:
            CH4 generation volume, m^3.

        """
        return (
                GasEmissionConstants.METHANE_POTENTIAL_Go
                * (
                        1
                        - GasEmissionConstants.CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH
                        / (
                                hydraulic_retention_time * GasEmissionConstants.SPECIFIC_GROWTH_RATE
                                + GasEmissionConstants.CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH
                                - 1
                        )
                )
                * manure_total_volatile_solids
                * GeneralConstants.GRAMS_TO_KG
        )

    @classmethod
    def biogas_energy_content(cls, methane_volume: float) -> float:
        """Calculates biogas energy content.

        Args:
            methane_volume: Methane generation volume, m^3.

        Returns:
            Biogas energy content, MJ.

        """
        return (
                methane_volume
                * GasEmissionConstants.METHANE_DENSITY
                * GasEmissionConstants.METHANE_ENERGY_DENSITY
        )

    @classmethod
    def methane_emission_from_anaerobic_lagoon(
            cls, manure_volatile_solids: float
    ) -> float:
        """
        Calculate methane emission from anaerobic lagoon.

        Notes
        -----
        The equation used to calculate methane emission from anaerobic lagoon is:

        .. math::

            E_{CH_4} = Bo \\cdot MCF \\cdot MS \\cdot MF \\cdot VS

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
        Bo = GasEmissionConstants.ACHIEVABLE_METHANE_EMISSION
        MCF = GasEmissionConstants.METHANE_CONVERSION_FACTOR
        MS = GasEmissionConstants.FRACTION_OF_HANDLED_MANURE
        MF = GasEmissionConstants.METHANE_FACTOR
        return Bo * MCF * MS * MF * manure_volatile_solids

    @classmethod
    def _methane_conversion_factor(cls, ambient_barn_temp: float) -> float:
        """
        Calculate the Methane Conversion Factor (MCF) using the exponential function:

        MCF(T) = 7.11 * e^(0.0884 * t)

        Parameters
        ----------
        ambient_barn_temp : float
            The ambient barn temperature (in Celsius).

        Returns
        -------
        float
            The calculated Methane Conversion Factor (MCF) for the given ambient barn temperature.

        """
        return GasEmissionConstants.MCF_CONSTANT_A * math.exp(
            GasEmissionConstants.MCF_CONSTANT_B * ambient_barn_temp
        )

    @classmethod
    def ifsm_methane_emission(cls, manure_volatile_solids: float, ambient_barn_temp: float) -> float:
        """Calculates emission of methane for a day using an adaptation of the tier 2 approach
        of the IPCC(2006), given ambient barn temperature and a methane conversion factor for the manure
        management.

        CH4 emission = (VS * Bo * 0.67 * MCF) / 100

        Parameters
        ----------
        manure_volatile_solids : float
            The volatile solids (in kg)

        ambient_barn_temp : float
            The ambient barn temperature (in Celsius)

        Returns
        -------
        float
            The calculated methane emissions (in kg) for the given ambient barn temperature.

        """
        if manure_volatile_solids < 0:
            raise ValueError(f"{manure_volatile_solids=} mass must be positive.")
        Bo = GasEmissionConstants.ACHIEVABLE_METHANE_EMISSION
        methane_conversion_factor = GasEmissionsCalculator._methane_conversion_factor(ambient_barn_temp)
        methane_emissions_in_kg = (manure_volatile_solids
                                   * Bo
                                   * GasEmissionConstants.METHANE_FACTOR
                                   * methane_conversion_factor
                                   ) / 100
        return methane_emissions_in_kg

    @classmethod
    def _microbial_decomp_rate(cls, temperature: float) -> float:
        """
        Calculates the microbial decomposition (unitless) rate per day:

        max decomp rate = eff. decomp rate * (1.066^(temp - 10) - 1.21^(temp - 50))

        Parameters
        ----------
        temperature : float
            The temperature of the medium (in Celsius)

        Returns
        -------
        float
            The microbial decomposition rate per day (unitless)

        """
        return ManureConstants.EFFECTIVE_MICROBIAL_DECOMP_RATE * (
                math.pow(1.066, (temperature - 10)) - math.pow(1.21, (temperature - 50))
        )

    @classmethod
    def _carbon_decomposition_rate(
            cls, days_since_last_tillage: int = 1, lag: int = 2
    ) -> float:
        """
        Calculates the carbon decomposition taking place in the composting process of
        the manure-bedding mix due to microbial activity.

        Rate C Decomp = (max decomp rate - slow decomp rate) *
        e^(decay * (days_since_last_tillage - lag)) * slow decomp rate

        Parameters
        ----------
        days_since_last_tillage : int
            The number of days since manure was last tilled

        lag : int
            Lag time in days.

        Returns
        -------
        float
            The carbon decomposition rate per day (unitless)

        """
        decomposition_temp = 60
        compost_bed_pack_temp = 30
        decay = 0.1

        max_microbial_decom_rate = cls._microbial_decomp_rate(decomposition_temp)
        slow_decomp_rate = cls._microbial_decomp_rate(compost_bed_pack_temp)
        exponent_coeff = decay * (days_since_last_tillage - lag)

        c_decomp_rate = (
                (max_microbial_decom_rate - slow_decomp_rate)
                * math.exp(exponent_coeff)
                * slow_decomp_rate
        )
        return c_decomp_rate

    @classmethod
    def _anaerobic_effect(
            cls,
            oxygen_mole_fraction: float = 0.15,
            oxygen_half_saturation_constant: float = GasEmissionConstants.OXYGEN_HALF_SATURATION_CONSTANT,
            oxygen_ambient_air_mole_fraction: float = 0.21,
    ) -> float:
        """
        Calculates the anaerobic effect.

        Anaerobic effect = (O2 / (O2,hsat + O2)) * ((O2,hsat + O2,amb) / O2,amb)


        Parameters
        ----------
        oxygen_mole_fraction : float
            Mole fraction of oxygen in the air within the windrow

        oxygen_half_saturation_constant : float
            half saturation constant for oxygen gas

        oxygen_ambient_air_mole_fraction : fot
            mole fraction of oxygen gas in ambient air

        Returns
        -------
        float
            The anaerobic effect (unitless)

        Raises
        ------
        ValueError
            If oxytem_mole_fraction or oxygen_ambient_air_mole_fraction are not between [0, 1]

        """
        if not (0.0 < oxygen_mole_fraction < 1.0):
            raise ValueError(f"{oxygen_mole_fraction=} must be in the range [0, 1]")
        if not (0.0 < oxygen_ambient_air_mole_fraction < 1.0):
            raise ValueError(
                f"{oxygen_ambient_air_mole_fraction=} must be in the range [0, 1]"
            )
        anaerobic_effect = (
                                   oxygen_mole_fraction
                                   / (oxygen_half_saturation_constant + oxygen_mole_fraction)
                           ) * (
                                   (oxygen_half_saturation_constant + oxygen_ambient_air_mole_fraction)
                                   / oxygen_ambient_air_mole_fraction
                           )
        return anaerobic_effect

    @classmethod
    def total_carbon_decomposition(
            cls,
            manure_total_solids: float,
            bedding_total_mass: float,
            days_since_last_tillage: int,
            lag: int,
            moisture_effect: float = ManureConstants.DEFAULT_MOISTURE_EFFECT_MICROBIAL_DECOMP,
            carbon_available_in_manure: float = ManureConstants.DEFAULT_CARBON_FRACTION_AVAILABLE_IN_MANURE,
            carbon_available_in_bedding: float = GasEmissionConstants.DEFAULT_CARBON_AVAILABLE_IN_BEDDING
    ) -> float:
        """Calculates the carbon decomposition from the composting process of the manure-bed mixture
        due to microbial activity (decomposition, consumption, respiration).

        Parameters
        ----------
        manure_total_solids : float
            The total solids from the manure (in kg)

        bedding_total_mass : float
            The total mass of the bedding material (in kg)

        days_since_last_tillage : int
            The number of days since the last tillage event

        lag : int
            The lag time

        moisture_effect : float
            The effect of moisture on microbial decomposition

        carbon_available_in_manure : float
            the proportion of carbon available in manure (unitless)

        carbon_available_in_bedding : float
            the carbon available in the bedding (unitless)

        Returns
        -------
        float
            The total carbon decomposition (in kg).

        """
        carbon_from_manure = manure_total_solids * carbon_available_in_manure
        carbon_from_bedding = bedding_total_mass * carbon_available_in_bedding
        total_carbon = carbon_from_manure + carbon_from_bedding

        microbial_decomp_rate = cls._carbon_decomposition_rate(
            days_since_last_tillage, lag
        )
        microbial_decomp_anaerobic_conditions_effect = cls._anaerobic_effect()
        total_carbon_decomposition = (
                total_carbon
                * microbial_decomp_rate
                * moisture_effect
                * microbial_decomp_anaerobic_conditions_effect
        )
        return total_carbon_decomposition

    @staticmethod
    def nitrogen_loss_in_compost_bedded_pack_barn_from_ammonia_emission(
            daily_nitrogen_input: float, is_bedding_tilled: bool
    ) -> float:
        """
        Calculate the nitrogen loss from ammonia emission in the compost bedded pack barn.

        Parameters
        ----------
        daily_nitrogen_input : float
            The mass of nitrogen present in the manure excreted by animals (kg).
        is_bedding_tilled : bool
            Indicator for if the bedding is tilled for the current simulation day.

        Returns
        -------
        float
            The nitrogen lost to ammonia emission in the compost bedded pack barn (kg).

        Raises
        ------
        ValueError
            If the daily nitrogen input is negative.
        """

        if daily_nitrogen_input < 0.0:
            raise ValueError(
                f"Daily nitrogen input mass must be non-negative: {daily_nitrogen_input}"
            )

        coefficient_tilled = (
            GasEmissionConstants.AMMONIA_EMISSION_COEFFICIENT_WITH_TILLED_BEDDING
        )
        coefficient_untilled = (
            GasEmissionConstants.AMMONIA_EMISSION_COEFFICIENT_WITH_UNTILLED_BEDDING
        )

        nitrogen_loss_tilled = (
                coefficient_tilled * daily_nitrogen_input * is_bedding_tilled
        )

        nitrogen_loss_untilled = (
                coefficient_untilled * daily_nitrogen_input * (not is_bedding_tilled)
        )

        return nitrogen_loss_tilled + nitrogen_loss_untilled

    @staticmethod
    def _nitrogen_loss_from_leaching(
            daily_nitrogen_input: float,
    ) -> float:
        """
        Calculate the mass of nitrogen that leaches out of the manure-bedding mixture.

        Parameters
        ----------
        daily_nitrogen_input : float
            The mass of nitrogen present in the manure excreted by animals (kg).

        Returns
        -------
        float
            The amount of nitrogen that leaches out of the bedding mixture (kg).

        Raises
        ------
        ValueError
            If the daily nitrogen input is negative.
        """

        if daily_nitrogen_input < 0.0:
            raise ValueError(
                f"Daily nitrogen input mass must be non-negative: {daily_nitrogen_input}"
            )

        return GasEmissionConstants.LEACHING_COEFFICIENT * daily_nitrogen_input

    @staticmethod
    def nitrogen_loss_in_compost_bedded_pack_barn_from_nitrous_oxide_emission(
            daily_nitrogen_input: float, is_bedding_tilled: bool
    ) -> float:
        """
        Calculate the nitrogen loss from nitrous oxide emission in a compost bedded pack barn.

        Parameters
        ----------
        daily_nitrogen_input : float
            The mass of nitrogen present in the manure excreted by animals (kg).
        is_bedding_tilled : bool
            Indicator for if the bedding is tilled for the current simulation day.

        Returns
        -------
        float
            The nitrogen lost to nitrous oxide emissions in the compost bedded pack barn (kg).

        Raises
        ------
        ValueError
            If the daily nitrogen input is negative.
        """

        if daily_nitrogen_input < 0.0:
            raise ValueError(
                f"Daily nitrogen input mass must be non-negative: {daily_nitrogen_input}"
            )

        coefficient_tilled = (
            GasEmissionConstants.NITROUS_OXIDE_COEFFICIENT_WITH_TILLED_BEDDING
        )
        coefficient_untilled = (
            GasEmissionConstants.NITROUS_OXIDE_COEFFICIENT_WITH_UNTILLED_BEDDING
        )

        nitrogen_loss_tilled = (
                coefficient_tilled * daily_nitrogen_input * is_bedding_tilled
        )
        nitrogen_loss_untilled = (
                coefficient_untilled * daily_nitrogen_input * (not is_bedding_tilled)
        )

        return nitrogen_loss_tilled + nitrogen_loss_untilled

    @staticmethod
    def total_nitrogen_loss_from_compost_bedded_pack_barn(
            daily_nitrogen_input: float, is_bedding_tilled: bool
    ) -> float:
        """
        Calculate the total nitrogen loss from a compost bedded pack barn.

        Parameters
        ----------
        daily_nitrogen_input : float
            The mass of nitrogen present in the manure excreted by animals (kg).
        is_bedding_tilled : bool
            Indicator for if the bedding is tilled for the current simulation day.

        Returns
        -------
        float
            The total nitrogen loss from the compost bedded pack barn (kg).

        Raises
        ------
        ValueError
            If the daily nitrogen input is negative.
        """

        if daily_nitrogen_input < 0.0:
            raise ValueError(
                f"Daily nitrogen input mass must be non-negative: {daily_nitrogen_input}"
            )

        ammonia_loss = GasEmissionsCalculator.nitrogen_loss_in_compost_bedded_pack_barn_from_ammonia_emission(
            daily_nitrogen_input, is_bedding_tilled
        )

        nitrous_oxide_loss = \
            GasEmissionsCalculator.nitrogen_loss_in_compost_bedded_pack_barn_from_nitrous_oxide_emission(
                daily_nitrogen_input, is_bedding_tilled
            )

        leaching_loss = GasEmissionsCalculator._nitrogen_loss_from_leaching(
            daily_nitrogen_input
        )

        total_nitrogen_loss = ammonia_loss + nitrous_oxide_loss + leaching_loss

        return total_nitrogen_loss

    @staticmethod
    def nitrogen_loss_in_open_lots_from_ammonia_emission(daily_nitrogen_input: float) -> float:
        """
        Calculate the nitrogen loss from ammonia emission in the open lots manure treatment.

        Parameters
        ----------
        daily_nitrogen_input : float
            The amount of nitrogen present in the manure excreted by animals (kg).

        Returns
        -------
        float
            The amount of nitrogen lost to ammonia emission (kg).

        Raises
        ------
        ValueError
            If the daily nitrogen input is negative.
        """

        if daily_nitrogen_input < 0.0:
            raise ValueError(
                f"Daily nitrogen input mass must be non-negative: {daily_nitrogen_input}"
            )

        return GasEmissionConstants.AMMONIA_EMISSION_COEFFICIENT_IN_OPEN_LOTS * daily_nitrogen_input

    @staticmethod
    def nitrogen_loss_in_open_lots_from_nitrous_oxide_emission(daily_nitrogen_input: float) -> float:
        """
        Calculate the nitrogen loss from nitrous oxide emission in the open lots manure treatment.

        Parameters
        ----------
        daily_nitrogen_input : float
            The amount of nitrogen present in the manure excreted by animals (kg).

        Returns
        -------
        float
            The nitrogen lost to nitrous oxide emission (kg).

        Raises
        ------
        ValueError
            If the daily nitrogen input is negative.
        """

        if daily_nitrogen_input < 0.0:
            raise ValueError(
                f"Daily nitrogen input mass must be non-negative: {daily_nitrogen_input}"
            )

        return GasEmissionConstants.NITROUS_OXIDE_COEFFICIENT_IN_OPEN_LOTS * daily_nitrogen_input

    @staticmethod
    def total_nitrogen_loss_from_open_lots(daily_nitrogen_input: float) -> float:
        """
        Calculate the total nitrogen loss from the open lots manure treatment.

        Parameters
        ----------
        daily_nitrogen_input : float
            The amount of nitrogen present in the manure excreted by animals (kg).

        Returns
        -------
        float
            The total nitrogen loss from the open lots manure treatment (kg).

        """
        return (
                GasEmissionsCalculator.nitrogen_loss_in_open_lots_from_ammonia_emission(daily_nitrogen_input)
                + GasEmissionsCalculator._nitrogen_loss_from_leaching(daily_nitrogen_input)
                + GasEmissionsCalculator.nitrogen_loss_in_open_lots_from_nitrous_oxide_emission(daily_nitrogen_input)
        )

    @staticmethod
    def empirical_nitrogen_loss_from_nitrous_oxide_emission(
            emission_factor__kg_nitrous_oxide_N_per_kg_manure_N: float,
            manure_nitrogen__kg_N_per_day: float
    ) -> float:
        """
        Calculate the daily empirical nitrogen loss from nitrous oxide emission from a manure treatment
        and storage system (kg :math:`N_2O`-N/day).

        Parameters
        ----------
        emission_factor__kg_nitrous_oxide_N_per_kg_manure_N : float
            The emission factor for nitrous oxide based on the type of manure treatment and storage system
            and whether the manure is covered or not (kg :math:`N_2O`-N/kg manure N).
        manure_nitrogen__kg_N_per_day: float
            The amount of manure nitrogen that enters the manure treatment system each day (kg N/day).

        Returns
        -------
        float
            The empirical nitrogen loss from nitrous oxide emission (kg :math:`N_2O`-N/day).
        """

        return emission_factor__kg_nitrous_oxide_N_per_kg_manure_N * manure_nitrogen__kg_N_per_day
