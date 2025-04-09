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

DEFAULT_DAYS_SINCE_LAST_TURNING: int = 1
"""Default days since the previous compost turning event (days). Default is set to 1."""

COMPOSTING_DECOMPOSITION_TEMPERATURE: float = 60.0
"""The temperature of the inner compost layer at which microbial growth and decomposition is maximized (C)."""

DEFAULT_MOLE_FRACTION_OF_OXYGEN: float = 0.15
"""The default mole fraction of oxygen in the air wihtin the compost layer."""

OXYGEN_HALF_SATURATION_CONSTANT: float = 0.02
"""The half saturation constant of Oxygen gas (O2)"""

AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN: float = 0.21
"""The mole fraction of oxygen in ambient air."""


class SolidsStorageCalculator:
    """
    This class contains methods to calculate the carbon decomposition, methane emission,
    nitrogen loss to leaching, and dry matter loss of the current day.
    The calculations are based on the composting type and the manure temperature.
    The methods are static and can be called without creating an instance of the class.
    """

    @staticmethod
    def calculate_nitrogen_loss_to_leaching(
        fraction_nitrogen_lost_to_leaching: float, received_manure_nitrogen: float
    ) -> float:
        """
        This function calculates the amount of nitrogen leached out of the manure-bedding
        pile of the current day.

        Parameters
        ----------
        fraction_nitrogen_lost_to_leaching : float
            The fraction of nitrogen lost to leaching, unitless.
        received_manure_nitrogen : float
            The nitrogen content of the received manure, kg.

        Returns
        -------
        float
            The total nitrogen loss to leaching of the current day, kg.
        """

        return fraction_nitrogen_lost_to_leaching * received_manure_nitrogen

    @staticmethod
    def calculate_dry_matter_loss(methane_emission: float, carbon_decomposition: float) -> float:
        """
        This function calculates the total dry matter loss of the current day.

        Parameters
        ----------
        methane_emission : float
            The methane emission of the current day, kg/day.
        carbon_decomposition : float
            The carbon decomposition of the current day, kg/day.

        Returns
        -------
        float
            The total dry matter loss of the current day, kg/day.
        """
        return 2 * carbon_decomposition + methane_emission

    @staticmethod
    def calculate_carbon_decomposition(
        manure_temperature: float, non_degradable_volatile_solids: float, degradable_volatile_solids: float
    ) -> float:
        """
        This function calculates the total carbon decomposition of the current day.

        Parameters
        ----------
        manure_temperature : float
            The manure temperature of the current day, Celsius.  In Composting, this value is equal to ambient
            temperature of the current day. In Open Lot and Compost Bedded Pack Barn, this value is
            set to a default/constant value (30 C).
        non_degradable_volatile_solids : float
            The non-degradable volatile solids of the current day, kg.
        degradable_volatile_solids : float
            The degradable volatile solids of the current day, kg.

        Returns
        -------
        float
            The total carbon decomposition of the current day, kg/day.
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
        This function calculates the carbon decomposition rate of the current day.

        Parameters
        ----------
        manure_temperature : float
            The manure temperature of the current day, Celsius.

        Returns
        -------
        float
            The carbon decomposition rate of the current day, per day.
        """
        max_microbial_decomposition_rate = SolidsStorageCalculator.calculate_max_microbial_decomposition_rate()
        slow_microbial_decomposition_rate = SolidsStorageCalculator.calculate_slow_fraction_decomposition_rate(
            manure_temperature
        )

        return float(
            (
                (max_microbial_decomposition_rate - slow_microbial_decomposition_rate)
                * (math.e ** (FIRST_ORDER_DECAYING_COEFFICIENT * (DEFAULT_DAYS_SINCE_LAST_TURNING - DEFAULT_LAG_TIME)))
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
            The max microbial decomposition rate of the current day, per day.
        """

        return float(
            EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE
            * (
                1.066 ** (COMPOSTING_DECOMPOSITION_TEMPERATURE - 10)
                - 1.21 ** (COMPOSTING_DECOMPOSITION_TEMPERATURE - 50)
            )
        )

    @staticmethod
    def calculate_slow_fraction_decomposition_rate(manure_temperature: float) -> float:
        """
        This function calculates the microbial decomposition rate of the slowly-degrading fraction
        in decomposing material on the current day.

        Parameters
        ----------
        manure_temperature : float
            The manure temperature of the current day, Celsius.

        Returns
        -------
        float
            The slow microbial decomposition rate of the current day, per day.
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
