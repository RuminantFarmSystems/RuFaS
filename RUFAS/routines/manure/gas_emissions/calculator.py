import math
from typing import Tuple

import numpy as np

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.manure.constants_and_units.gas_emission_constants import GasEmissionConstants
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants


class GasEmissionsCalculator:
    @classmethod
    def calculate_liquid_storage_methane(
        cls,
        accumulated_liquid_manure_total_degradable_volatile_solids: float,
        accumulated_liquid_manure_total_non_degradable_volatile_solids: float,
        stored_manure_temperature: float,
    ) -> Tuple[float, float]:
        """
        Calculate the methane emission from manure storage using total volatile solids.

        Notes
        -----
        The equation used to calculate the methane emission from manure storage is as follows:

        .. math::

            E_{CH_4} = 24 \\cdot e^{lnA - \\frac{E}{RT}} \\cdot VS_{d} \\cdot b_{1} \\cdot \frac{1}{1000}
            + 24 \\cdot e^{lnA - \\frac{E}{RT}} \\cdot VS_{nd} \\cdot b_{2} \\cdot \frac{1}{1000}

        where:

            :math:`E_{CH_4}` is the methane emission from manure storage (kg :math:`CH_4`/day),

            :math:`VS_{d}` is the degradable volatile solids in manure (kg),

            :math:`b_{1}` is the degradable volatile solids rate correcting factor (1.0, unitless),

            :math:`VS_{nd}` is the non-degradable volatile solids in manure (kg),

            :math:`b_{2}` is the non-degradable volatile solids rate correcting factor (0.01, unitless),

            :math:`lnA` is the natural log of the Arrhenius constant (31.2, $\frac{\text{kg VS}}{\text{h}}^{-1}$),

            :math:`E` is the activation energy (81,000.0 J/mol),

            :math:`R` is the ideal gas constant (8.314 J/mol :math:`\\cdot` K),

            :math:`T` is the temperature in Kelvin (:math:`K`).

        Parameters
        ----------
        accumulated_liquid_manure_total_degradable_volatile_solids: float
            Total degradable volatile solids in manure (kg).
        accumulated_liquid_manure_total_non_degradable_volatile_solids: float,
            Total non-degradable volatile solids in manure (kg).
        stored_manure_temperature : float
            Temperature of the manure in storage in Celsius (:math:`^\\circ C`).

        Returns
        -------
        float
            Methane emission from manure volatile solids (kg :math:`CH_4`/day).
        float
            Methane emission from degradable volatile solids (kg :math:`CH_4`/day).

        Raises
        ------
        ValueError
            If the total volatile solids is not positive.
        """
        if accumulated_liquid_manure_total_degradable_volatile_solids <= 0:
            raise ValueError(
                "Total degradable volatile solids must be positive. Total degradable volatile solids provided: "
                f"{accumulated_liquid_manure_total_degradable_volatile_solids}"
            )

        arrhenius_exponent = cls._arrhenius_exponent(stored_manure_temperature)

        methane_emission_from_degradable_volatile_solids = (
            GasEmissionConstants.HOUR_TO_DAY_CONVERSION_FACTOR
            * (
                arrhenius_exponent
                * accumulated_liquid_manure_total_degradable_volatile_solids
                * GasEmissionConstants.DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR
            )
            * GeneralConstants.GRAMS_TO_KG
        )
        methane_emission_from_non_degradable_volatile_solids = (
            GasEmissionConstants.HOUR_TO_DAY_CONVERSION_FACTOR
            * (
                arrhenius_exponent
                * accumulated_liquid_manure_total_non_degradable_volatile_solids
                * GasEmissionConstants.NON_DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR
            )
            * GeneralConstants.GRAMS_TO_KG
        )

        methane_emission = (
            methane_emission_from_degradable_volatile_solids + methane_emission_from_non_degradable_volatile_solids
        )

        return methane_emission, methane_emission_from_degradable_volatile_solids

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
        if not (
            GasEmissionConstants.GENERAL_LOWER_BOUND_TEMPERATURE
            <= temp
            <= GasEmissionConstants.GENERAL_UPPER_BOUND_TEMPERATURE
        ):
            raise ValueError(f"Temperature must be between -40 and 60 degrees Celsius. Temperature provided: {temp}")

        temp_kelvin = cls._convert_temperature_celsius_to_kelvin(temp)
        return math.exp(
            GasEmissionConstants.NATURAL_LOG_ARRHENIUS_CONSTANT
            - (GasEmissionConstants.ACTIVATION_ENERGY / (GasEmissionConstants.GAS_CONSTANT * temp_kelvin))
        )

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
            raise ValueError(f"Hours must be in the range of [0, 24]. Hours provided: {hours}")

        if hours > 14:
            return -math.tanh(hours - 21.5) / 3.5
        elif hours > 4:
            return math.tanh(hours - 9.5) / 2.5
        else:
            return -math.tanh(hours + 3.5) / 3.5

    @classmethod
    def calculate_housing_methane_emission(cls, barn_area: float, barn_temperature: float) -> float:
        """
        Calculate housing methane emissions from manure handlers.

        Notes
        -----
        The equation used to calculate housing methane emissions is:

        .. math::

            E_{CH_4} = max(0, 0.13 * T_{barn}) \\times barn\\_area / 1000

        where:

            :math:`E_{CH_4}` is the methane housing emission in kg :math:`CH_4/day`,

            :math:`T_{barn}` is the barn temperature in :math:`^{\\circ}C`, and

            :math:`barn\\_area` is the total barn area based on the pen type and number of stalls in :math:`m^2`.

        Parameters
        ----------
        barn_area : float
            Barn area per animal based on housing type (:math:`m^2`).
        barn_temperature : float
            Current barn temperature (:math:`^{\\circ}C`).

        Returns
        -------
        float
            Housing methane emissions (kg :math:`CH_4/day`).

        Raises
        ------
        ValueError
            If the barn area is less than 0.

        """
        if barn_area < 0:
            raise ValueError("Barn area must be greater than or equal to 0.")

        return max(0.0, 0.13 * barn_temperature) * barn_area / 1000

    @classmethod
    def calculate_housing_carbon_dioxide_emission(cls, barn_area: float, barn_temperature: float) -> float:
        """
        Calculate carbon dioxide housing emission.

        Notes
        -----
        The equation used to calculate housing carbon dioxide emissions is:

        .. math::

            E_{CO_2} = max(0, 0.0065 + 0.0192 * T_{barn}) \\times barn\\_area / 1000

        where:

            :math:`E_{CO_2}` is the carbon dioxide housing emission in kg :math:`CO_2/day`,

            :math:`T_{barn}` is the barn temperature in :math:`^{\\circ}C`, and

            :math:`barn\\_area` is the total barn area based on the pen type and number of stalls in :math:`m^2`.

        Parameters
        ----------
        barn_area : float
            Barn area per animal based on housing type (:math:`m^2`).
        barn_temperature : float
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
        if barn_area < 0:
            raise ValueError("Barn area must be greater than or equal to 0.")

        return max(0.0, 0.0065 + 0.0192 * barn_temperature) * barn_area / 1000

    @classmethod
    def calculate_housing_ammonia_emission(
        cls,
        num_animals: int,
        barn_area: float,
        urine_total_ammoniacal_nitrogen: float,
        urine: float,
        barn_temperature: float,
        pH: float = GasEmissionConstants.DEFAULT_PH_FOR_HOUSING_AMMONIA,
        housing_specific_constant: float = GasEmissionConstants.HOUSING_HSC,
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

            :math:`M` is the urine per area of exposed surface in kg/:math:`m^2`, calculated as
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
        barn_area : float
            Barn area based on housing type and number of stalls(:math:`m^2`).
        urine_total_ammoniacal_nitrogen : float
            Total ammoniacal nitrogen in manure (kg).
        urine : float
            Amount of manure produced by animals in the barn (kg).
        barn_temperature : float
            Current barn temperature (:math:`^{\\circ}C`).
        pH : float, optional
            pH value for housing ammonia emission (unitless). Default is set to 7.7. This value is listed as
                :attr:`DEFAULT_PH_FOR_HOUSING_AMMONIA` in :class:`GasEmissionConstants`.
        housing_specific_constant : float, optional
            Housing-specific constant (unitless). Default is set to 260 s/m. This value is listed as
                :attr:`HOUSING_HSC` in :class:`GasEmissionConstants`.

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

        if barn_area < 0:
            raise ValueError("Barn area must be greater than or equal to 0.")

        if urine_total_ammoniacal_nitrogen < 0:
            raise ValueError("Manure total ammoniacal nitrogen must be greater than or equal to 0.")

        if urine < 0:
            raise ValueError("Manure must be greater than or equal to 0.")

        # If any of the aforementioned values is 0, then the result will be 0.
        if num_animals == 0 or barn_area == 0 or urine_total_ammoniacal_nitrogen == 0 or urine == 0:
            return 0.0

        total_barn_area = barn_area
        total_ammoniacal_nitrogen = urine_total_ammoniacal_nitrogen / total_barn_area
        manure_density = ManureConstants.SLURRY_MANURE_DENSITY  # kg/m^3
        seconds_per_day = GeneralConstants.SECONDS_PER_DAY
        temperature_kelvin = cls._convert_temperature_celsius_to_kelvin(barn_temperature)
        ammonia_resistance = cls._ammonia_resistance(barn_temperature, housing_specific_constant)
        manure_per_area = urine / total_barn_area  # kg/m^2
        equilibrium_coefficient = cls._equilibrium_coefficient(temperature_kelvin, pH)
        ammonia_loss = (total_ammoniacal_nitrogen * seconds_per_day * manure_density) / (
            ammonia_resistance * manure_per_area * equilibrium_coefficient
        )
        total_ammonia_loss = ammonia_loss * total_barn_area
        return max(0.0, total_ammonia_loss)

    @classmethod
    def calculate_liquid_storage_ammonia_emission(
        cls,
        num_animals: int,
        manure_total_ammoniacal_nitrogen: float,
        manure_volume: float,
        manure_density: float,
        storage_temperature: float,
        storage_area_per_animal: float = GasEmissionConstants.DEFAULT_STORAGE_AREA_PER_ANIMAL,
        pH: float = GasEmissionConstants.DEFAULT_PH_FOR_STORAGE_AMMONIA,
    ) -> float:
        """
        Calculate storage ammonia emissions for liquidmanure treatments.

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
        storage_temperature : float
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
            If the num_animals is < 0.
            If storage_area < 0.
            If manure_total_ammoniacal_nitrogen < 0.
            If manure_volume < 0.
            If manure_density < 0.
            If total_solids in manure < 0.

        """
        if num_animals < 0:
            raise ValueError("Number of animals must be greater than or equal to 0.")
        if storage_area_per_animal < 0:
            raise ValueError("Storage area per animal must be greater than or equal to 0.")
        if manure_total_ammoniacal_nitrogen < 0:
            raise ValueError("Manure total ammoniacal nitrogen must be greater than or equal to 0.")
        if manure_volume < 0:
            raise ValueError("Manure volume must be greater than or equal to 0.")
        if manure_density < 0:
            raise ValueError("Manure density must be greater than or equal to 0.")

        # If any of the input parameters is 0, then the result will be 0.
        if any(
            param == 0
            for param in [
                num_animals,
                storage_area_per_animal,
                manure_total_ammoniacal_nitrogen,
                manure_volume,
                manure_density,
            ]
        ):
            return 0.0

        total_storage_area = num_animals * storage_area_per_animal
        temp_kelvin = cls._convert_temperature_celsius_to_kelvin(storage_temperature)
        total_manure_mass = (manure_volume * manure_density) / total_storage_area
        manure_total_ammoniacal_nitrogen_per_area = manure_total_ammoniacal_nitrogen / total_storage_area
        storage_area_resistance = GasEmissionConstants.STORAGE_HSC
        equilibrium_coefficient = cls._equilibrium_coefficient(temp_kelvin, pH)
        ammonia_loss = (
            manure_total_ammoniacal_nitrogen_per_area * GeneralConstants.SECONDS_PER_DAY * manure_density
        ) / (storage_area_resistance * total_manure_mass * equilibrium_coefficient)
        total_ammonia_loss = min(ammonia_loss * total_storage_area, manure_total_ammoniacal_nitrogen)
        return max(0.0, total_ammonia_loss)

    @classmethod
    def _ammonia_resistance(
        cls,
        temp: float,
        hsc: float,
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
                :attr:`HOUSING_HSC` in :class:`GasEmissionConstants`.

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
    def _convert_temperature_celsius_to_kelvin(cls, temperature_celsius: float) -> float:
        """Converts a temperature from Celsius to Kelvin.

        Args:
            temperature_celsius: temperature in Celsius, C.

        Returns:
            Temperature in Kelvin, K.

        """
        return temperature_celsius + 273.15

    @classmethod
    def calculate_CSTR_methane_volume(cls, manure_total_volatile_solids: float) -> float:
        """
        Calculates CH4 generation volume of anaerobic digestion in a continuously-stirred tank reactor.

        Parameters
        ----------
        manure_total_volatile_solids : float
            Total volatile solids, kg.

        Returns
        -------
        float
            CH4 generation volume, m^3.

        Notes
        -----
        This function originates from personal communications with subject matter experts Wei Liao (liaow@msu.edu) and
        April Leytem (april.leytem@usda.gov). The equation is a simplification of the IPCC Tier II estimate of CH4
        emissions from anaerobic digesters, where CH4 generated in the digester is assumed to be equivalent to the
        amount of manure volatile solids loaded per day, multiplied by the generally-accepted methane potential value
        for dairy manure (240 L CH4 per kg of manure volatile solids).

        """
        return GasEmissionConstants.ACHIEVABLE_METHANE_EMISSION * manure_total_volatile_solids

    @classmethod
    def calculate_digester_methane_leakage(
        cls, generated_methane_mass: float, digester_methane_leakage_fraction: float
    ) -> float:
        """
        Calculates the mass of methane lost from a digester.

        Parameters
        ----------
        generated_methane_mass : float
            Amount of methane generated within the digester, kg.
        digester_methane_leakage_fraction : float
            Fraction of generated methane that escapes as leakage (unitless).

        Returns
        -------
        float
            Mass of methane lost as leakage, kg.

        """
        return generated_methane_mass * digester_methane_leakage_fraction

    @classmethod
    def calculate_methane_energy_content(cls, methane_mass: float) -> float:
        """
        Calculates energy content of methane generated in a digester.

        Parameters
        ----------
        methane_mass : float
            Methane generation mass, kg.

        Returns
        -------
        float
            Methane energy content, MJ.

        """
        return methane_mass * GasEmissionConstants.METHANE_ENERGY_DENSITY

    @classmethod
    def methane_emission_from_anaerobic_lagoon(cls, manure_volatile_solids: float) -> float:
        """
        Calculate methane emission from anaerobic lagoon.

        Notes
        -----
        The equation used to calculate methane emission from anaerobic lagoon is:

        .. math::

            E_{CH_4} = Bo \\cdot MCF \\cdot MS \\cdot MF \\cdot VS

        where:

            :math:`E_{CH_4}` is methane emissions from anaerobic lagoon (kg :math:`CH_4`-N/day),

            :math:`Bo` is the achievable emission of methane during anaerobic digestion (:math:`m^3 CH_4`/kg VS),

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
        Calculate the Methane Conversion Factor (MCF) for the open lots treatment using the following function:

        MCF(T) = 0.0625 * T - 0.25

        Parameters
        ----------
        ambient_barn_temp : float
            The ambient barn temperature (in Celsius).

        Returns
        -------
        float
            The calculated Methane Conversion Factor (MCF) for the given ambient barn temperature.

        References
        ----------
        .. [1] Open Lots Design Document, V1 eqn. M.1.A.1
        """
        return GasEmissionConstants.MCF_CONSTANT_A * ambient_barn_temp - GasEmissionConstants.MCF_CONSTANT_B

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
        methane_emissions_in_kg = (
            manure_volatile_solids * Bo * GasEmissionConstants.METHANE_FACTOR * methane_conversion_factor
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
    def _carbon_decomposition_rate(cls, days_since_last_tillage: int = 1, lag: int = 2) -> float:
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

        c_decomp_rate = (max_microbial_decom_rate - slow_decomp_rate) * math.exp(exponent_coeff) * slow_decomp_rate
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
            If oxytem_mole_fraction or oxygen_ambient_air_mole_fraction are not between [0, 1].

        """
        if not (0.0 < oxygen_mole_fraction < 1.0):
            raise ValueError(f"{oxygen_mole_fraction=} must be in the range [0, 1]")
        if not (0.0 < oxygen_ambient_air_mole_fraction < 1.0):
            raise ValueError(f"{oxygen_ambient_air_mole_fraction=} must be in the range [0, 1]")
        anaerobic_effect = (oxygen_mole_fraction / (oxygen_half_saturation_constant + oxygen_mole_fraction)) * (
            (oxygen_half_saturation_constant + oxygen_ambient_air_mole_fraction) / oxygen_ambient_air_mole_fraction
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
        carbon_available_in_bedding: float = GasEmissionConstants.DEFAULT_CARBON_AVAILABLE_IN_BEDDING,
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

        microbial_decomp_rate = cls._carbon_decomposition_rate(days_since_last_tillage, lag)
        microbial_decomp_anaerobic_conditions_effect = cls._anaerobic_effect()
        total_carbon_decomposition = (
            total_carbon * microbial_decomp_rate * moisture_effect * microbial_decomp_anaerobic_conditions_effect
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
            raise ValueError(f"Daily nitrogen input mass must be non-negative: {daily_nitrogen_input}")

        coefficient_tilled = GasEmissionConstants.AMMONIA_EMISSION_COEFFICIENT_WITH_TILLED_BEDDING
        coefficient_untilled = GasEmissionConstants.AMMONIA_EMISSION_COEFFICIENT_WITH_UNTILLED_BEDDING

        nitrogen_loss_tilled = coefficient_tilled * daily_nitrogen_input * is_bedding_tilled

        nitrogen_loss_untilled = coefficient_untilled * daily_nitrogen_input * (not is_bedding_tilled)

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
            raise ValueError(f"Daily nitrogen input mass must be non-negative: {daily_nitrogen_input}")

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
            raise ValueError(f"Daily nitrogen input mass must be non-negative: {daily_nitrogen_input}")

        coefficient_tilled = GasEmissionConstants.NITROUS_OXIDE_COEFFICIENT_WITH_TILLED_BEDDING
        coefficient_untilled = GasEmissionConstants.NITROUS_OXIDE_COEFFICIENT_WITH_UNTILLED_BEDDING

        nitrogen_loss_tilled = coefficient_tilled * daily_nitrogen_input * is_bedding_tilled
        nitrogen_loss_untilled = coefficient_untilled * daily_nitrogen_input * (not is_bedding_tilled)

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
            raise ValueError(f"Daily nitrogen input mass must be non-negative: {daily_nitrogen_input}")

        ammonia_loss = GasEmissionsCalculator.nitrogen_loss_in_compost_bedded_pack_barn_from_ammonia_emission(
            daily_nitrogen_input, is_bedding_tilled
        )
        # fmt: off
        nitrous_oxide_loss = (
            GasEmissionsCalculator.nitrogen_loss_in_compost_bedded_pack_barn_from_nitrous_oxide_emission(
                daily_nitrogen_input, is_bedding_tilled
            )
        )
        # fmt: on
        leaching_loss = GasEmissionsCalculator._nitrogen_loss_from_leaching(daily_nitrogen_input)

        total_nitrogen_loss = ammonia_loss + nitrous_oxide_loss + leaching_loss

        return total_nitrogen_loss

    @staticmethod
    def nitrogen_loss_in_open_lots_from_ammonia_emission(
        daily_nitrogen_input: float,
    ) -> float:
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
            raise ValueError(f"Daily nitrogen input mass must be non-negative: {daily_nitrogen_input}")

        return GasEmissionConstants.AMMONIA_EMISSION_COEFFICIENT_IN_OPEN_LOTS * daily_nitrogen_input

    @staticmethod
    def nitrogen_loss_in_open_lots_from_nitrous_oxide_emission(
        daily_nitrogen_input: float,
    ) -> float:
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
            raise ValueError(f"Daily nitrogen input mass must be non-negative: {daily_nitrogen_input}")

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
    def calculate_empirical_nitrogen_loss_from_nitrous_oxide_emission(
        emission_factor_kg_nitrous_oxide_N_per_kg_manure_N: float,
        manure_nitrogen_kg_N_per_day: float,
    ) -> float:
        """
        Calculate the daily empirical nitrogen loss from nitrous oxide emission from a manure treatment
        and storage system (kg :math:`N_2O`-N/day).

        Parameters
        ----------
        emission_factor_kg_nitrous_oxide_N_per_kg_manure_N : float
            The emission factor for nitrous oxide based on the type of manure treatment and storage system
            and whether the manure is covered or not (kg :math:`N_2O`-N/kg manure N).
        manure_nitrogen_kg_N_per_day: float
            The amount of manure nitrogen that enters the manure treatment system each day (kg N/day).

        Returns
        -------
        float
            The empirical nitrogen loss from nitrous oxide emission (kg :math:`N_2O`-N/day).
        """

        return emission_factor_kg_nitrous_oxide_N_per_kg_manure_N * manure_nitrogen_kg_N_per_day

    @staticmethod
    def determine_barn_air_temperature(air_temperature: float) -> float:
        """Determines the ambient inside barn temperature based on the outdoor air temperature.

        Parameters
        ----------
        air_temperature : float
            The air temperature (°C).

        Returns
        -------
        float
            The barn temperature (°C).

        References
        ----------
        Between 5 and 30 C, barn temperature is assumed to be equal to outdoor air temperature.
        This function assumes that barn temperature does not drop below 5 C or increase above 30 C.
        These bounds were suggested by manure SMEs and are supported by barn temperature ranges
        reported in Bucklin et al. (FL, upper limit; https://doi.org/10.13031/2013.28851).
        The lower bound (5 C) suggested by SMEs was based on general industry standards/conditions.
        """
        return float(np.clip(air_temperature, 5.0, 30.0))
