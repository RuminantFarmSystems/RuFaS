import math

DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSD: float = 0.5
"""Default carbon content (percent by mass) of manure degradable volatile solids (unitless, [0, 1])."""

DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSND: float = 0.35
"""Default carbon content (percent by mass) of manure non-degradable volatile solids (unitless, [0, 1])."""

DEFAULT_EFFECT_OF_MOISTURE_ON_MICROBIAL_DECOMPOSITION: float = 0.65
"""The default effect of moisture on microbial decomposition."""

EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE: float = 2.37e-3
"""The rate of effectiveness of microbial decomposition."""

FIRST_ORDER_DECAYING_COEFFICIENT: float = 0.1
"""The first order decaying coefficient."""

DEFAULT_LAG_TIME: int = 2
"""Default lag time used in the calculation of the carbon decomposition rate (days). Default is set to 2."""

DEFAULT_DAYS_SINCE_LAST_MIXING: int = 1
"""Default days since the previous mixing event (days). Default is set to 1. For Composting, this refers to compost
turning. For Open Lot, this refers to lot harrowing. For Compost Bedded Pack barn, this refers to pack tillage."""

DECOMPOSITION_TEMPERATURE: float = 60.0
"""The temperature of the inner decomposing material layer at which microbial growth and decomposition is
maximized (C)."""

DEFAULT_MOLE_FRACTION_OF_OXYGEN: float = 0.15
"""The default mole fraction of oxygen in the air within the decomposing material layer."""

OXYGEN_HALF_SATURATION_CONSTANT: float = 0.02
"""The half saturation constant of Oxygen gas (O2)"""

AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN: float = 0.21
"""The mole fraction of oxygen in ambient air."""

ACHIEVABLE_METHANE_EMISSION: float = 0.24
"""Achievable emission of methane (:math:`CH_4`) from dairy manure (:math:`m^3 CH_4`/kg VS)."""

METHANE_FACTOR: float = 0.67
"""Unit conversion factor for methane from :math:`m^3` to kg (unitless)."""

MCF_CONSTANT_A: float = 0.0625
"""
Parameter estimate (unitless) of a regression using IPCC data (2006) used in the
Methane Conversion Factor (MCF) calculation. The coefficient scales the ambient barn temperature.
"""

MCF_CONSTANT_B: float = 0.25
"""
Parameter estimate (unitless) of a regression using IPCC data (2006) used in the
Methane Conversion Factor (MCF) calculation. The coefficient is a constant offset.
"""


class SolidsStorageCalculator:
    """
    This class contains methods to calculate the carbon decomposition, methane emission,
    nitrogen loss to leaching, and dry matter loss on the current day.
    The methods are static and can be called without creating an instance of the class.
    """

    @staticmethod
    def calculate_nitrogen_loss_to_leaching(
        fraction_nitrogen_lost_to_leaching: float, received_manure_nitrogen: float
    ) -> float:
        """
        This function calculates the amount of nitrogen leached out of the manure-bedding
        mix on the current day.

        Parameters
        ----------
        fraction_nitrogen_lost_to_leaching : float
            The fraction of nitrogen lost to leaching, unitless.
        received_manure_nitrogen : float
            The nitrogen content of the received manure, kg.

        Returns
        -------
        float
            The total nitrogen loss to leaching on the current day, kg.
        """

        return fraction_nitrogen_lost_to_leaching * received_manure_nitrogen

    @staticmethod
    def calculate_dry_matter_loss(methane_emission: float, carbon_decomposition: float) -> float:
        """
        This function calculates the total dry matter loss on the current day.

        Parameters
        ----------
        methane_emission : float
            The methane emission on the current day, kg/day.
        carbon_decomposition : float
            The carbon decomposition on the current day, kg/day.

        Returns
        -------
        float
            The total dry matter loss on the current day, kg/day.
        """
        return 2 * carbon_decomposition + methane_emission

    @staticmethod
    def calculate_carbon_decomposition(
        manure_temperature: float, non_degradable_volatile_solids: float, degradable_volatile_solids: float
    ) -> float:
        """
        This function calculates the total carbon decomposition on the current day.

        Parameters
        ----------
        manure_temperature : float
            The manure temperature on the current day, Celsius.  In Composting, this value is equal to ambient
            temperature on the current day. In Open Lot and Compost Bedded Pack Barn, this value is
            set to a default/constant value (30 C).
        non_degradable_volatile_solids : float
            The non-degradable volatile solids on the current day, kg.
        degradable_volatile_solids : float
            The degradable volatile solids on the current day, kg.

        Returns
        -------
        float
            The total carbon decomposition on the current day, kg/day.
        """
        carbon_decomposition_rate = SolidsStorageCalculator.calculate_carbon_decomposition_rate(manure_temperature)
        anaerobic_coefficient = SolidsStorageCalculator.calculate_anaerobic_coefficient()

        return (
            (
                degradable_volatile_solids * DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSD
                + non_degradable_volatile_solids * DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSND
            )
            * carbon_decomposition_rate
            * DEFAULT_EFFECT_OF_MOISTURE_ON_MICROBIAL_DECOMPOSITION
            * anaerobic_coefficient
        )

    @staticmethod
    def calculate_carbon_decomposition_rate(manure_temperature: float) -> float:
        """
        This function calculates the carbon decomposition rate on the current day.

        Parameters
        ----------
        manure_temperature : float
            The manure temperature on the current day, Celsius. In Composting, this value is equal to ambient
            temperature on the current day. In Open Lot and Compost Bedded Pack Barn, this value is
            set to a default/constant value (30 C).

        Returns
        -------
        float
            The carbon decomposition rate on the current day, per day.
        """
        max_microbial_decomposition_rate = SolidsStorageCalculator.calculate_max_microbial_decomposition_rate()
        slow_microbial_decomposition_rate = SolidsStorageCalculator.calculate_slow_fraction_decomposition_rate(
            manure_temperature
        )

        return float(
            (
                (max_microbial_decomposition_rate - slow_microbial_decomposition_rate)
                * (math.e ** (FIRST_ORDER_DECAYING_COEFFICIENT * (DEFAULT_DAYS_SINCE_LAST_MIXING - DEFAULT_LAG_TIME)))
                + slow_microbial_decomposition_rate
            )
        )

    @staticmethod
    def calculate_max_microbial_decomposition_rate() -> float:
        """
        This function calculates the max microbial decomposition rate.
        This parameter is set to 0.04195 but the equation and set values are shown below for reference.

        Returns
        -------
        float
            The max microbial decomposition rate on the current day, per day.
        """

        return float(
            EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE
            * (1.066 ** (DECOMPOSITION_TEMPERATURE - 10) - 1.21 ** (DECOMPOSITION_TEMPERATURE - 50))
        )

    @staticmethod
    def calculate_slow_fraction_decomposition_rate(manure_temperature: float) -> float:
        """
        This function calculates the microbial decomposition rate of the slowly-degrading fraction
        in decomposing material on the current day.

        Parameters
        ----------
        manure_temperature : float
            The manure temperature on the current day, Celsius. In Composting, this value is equal to ambient
            temperature on the current day. In Open Lot and Compost Bedded Pack Barn, this value is
            set to a default/constant value (30 C).

        Returns
        -------
        float
            The microbial decomposition rate of the slowly-degrading fraction on the current day.
        """

        return float(
            EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE
            * (1.066 ** (manure_temperature - 10) - 1.21 ** (manure_temperature - 50))
        )

    @staticmethod
    def calculate_anaerobic_coefficient() -> float:
        """
        This function calculates the anaerobic coefficient. The value of this parameter is equal to 0.96639,
        but the equation and set values are included below for reference.

        Returns
        -------
        float
            The anaerobic coefficient, unitless.
        """
        return (
            DEFAULT_MOLE_FRACTION_OF_OXYGEN / (OXYGEN_HALF_SATURATION_CONSTANT + DEFAULT_MOLE_FRACTION_OF_OXYGEN)
        ) * (
            (OXYGEN_HALF_SATURATION_CONSTANT + AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN)
            / AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN
        )

    @staticmethod
    def calculate_ifsm_methane_emission(manure_volatile_solids: float, manure_temperature: float) -> float:
        """Calculates emission of methane on the current day using an adaptation of the tier 2 approach
        of the IPCC (2006), based on manure volatile solids addition to the open lot and a temperature-dependent
        methane conversion factor.

        Parameters
        ----------
        manure_volatile_solids : float
            The volatile solids (kg).

        manure_temperature : float
            The manure temperature (Celsius).

        Returns
        -------
        float
            The calculated methane emissions (in kg) for the given ambient barn temperature.

        """
        if manure_volatile_solids < 0:
            raise ValueError(f"Manure volatile solids mass must be positive. Received {manure_volatile_solids}.")
        Bo = ACHIEVABLE_METHANE_EMISSION
        methane_conversion_factor = SolidsStorageCalculator.calculate_methane_conversion_factor(manure_temperature)
        methane_emissions_in_kg = (manure_volatile_solids * Bo * METHANE_FACTOR * methane_conversion_factor) / 100
        return methane_emissions_in_kg

    @staticmethod
    def calculate_methane_conversion_factor(manure_temperature: float) -> float:
        """
        Calculate the Methane Conversion Factor (MCF) for the open lots treatment using the following function:

        Parameters
        ----------
        manure_temperature : float
            The ambient barn temperature (in Celsius).

        Returns
        -------
        float
            The calculated Methane Conversion Factor (MCF) for the given ambient barn temperature.

        """
        return max(0.0, MCF_CONSTANT_A * manure_temperature - MCF_CONSTANT_B)

    @staticmethod
    def calculate_degradable_volatile_solids_fraction(degradable_volatile_solids: float, total_solids: float) -> float:
        """
        Calculates the fraction of degradable volatile solids.

        Parameters
        ----------
        degradable_volatile_solids : float
            Mass of degradable volatile solids in the manure stream (kg).
        total_solids : float
            Mass of total solids in the manure stream (kg).

        Returns
        -------
        float
            The fraction of degradable volatile solids (unitless).

        """
        return degradable_volatile_solids / total_solids
