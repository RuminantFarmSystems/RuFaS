import math

from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.general_constants import GeneralConstants
from RUFAS.user_constants import UserConstants


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
            temperature on the current day. In Open Lot and Bedded Pack, this value is
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
                degradable_volatile_solids * ManureConstants.DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSD
                + non_degradable_volatile_solids * ManureConstants.DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSND
            )
            * carbon_decomposition_rate
            * ManureConstants.DEFAULT_EFFECT_OF_MOISTURE_ON_MICROBIAL_DECOMPOSITION
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
            temperature on the current day. In Open Lot and Bedded Pack, this value is
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
                * (
                    math.e
                    ** (
                        ManureConstants.FIRST_ORDER_DECAYING_COEFFICIENT
                        * (ManureConstants.DEFAULT_DAYS_SINCE_LAST_MIXING - ManureConstants.DEFAULT_LAG_TIME)
                    )
                )
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
            ManureConstants.EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE
            * (
                1.066 ** (ManureConstants.DECOMPOSITION_TEMPERATURE - 10)
                - 1.21 ** (ManureConstants.DECOMPOSITION_TEMPERATURE - 50)
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
            The manure temperature on the current day, Celsius. In Composting, this value is equal to ambient
            temperature on the current day. In Open Lot and Bedded Pack, this value is
            set to a default/constant value (30 C).

        Returns
        -------
        float
            The microbial decomposition rate of the slowly-degrading fraction on the current day.
        """

        return float(
            ManureConstants.EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE
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
            ManureConstants.DEFAULT_MOLE_FRACTION_OF_OXYGEN
            / (ManureConstants.OXYGEN_HALF_SATURATION_CONSTANT + ManureConstants.DEFAULT_MOLE_FRACTION_OF_OXYGEN)
        ) * (
            (ManureConstants.OXYGEN_HALF_SATURATION_CONSTANT + GeneralConstants.AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN)
            / GeneralConstants.AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN
        )

    @staticmethod
    def calculate_ifsm_methane_emission(
        manure_volatile_solids: float, manure_temperature: float, methane_production_potential: float
    ) -> float:
        """Calculates emission of methane on the current day using an adaptation of the tier 2 approach
        of the IPCC (2006), based on manure volatile solids addition to the open lot and a temperature-dependent
        methane conversion factor.

        Parameters
        ----------
        manure_volatile_solids : float
            The volatile solids (kg).
        manure_temperature : float
            The manure temperature (Celsius).
        methane_production_potential : float
            Achievable emission of methane from dairy manure (m^3 methane / kg volatile solids).

        Returns
        -------
        float
            The calculated methane emissions (in kg) for the given ambient barn temperature.

        """
        if manure_volatile_solids < 0:
            raise ValueError(f"Manure volatile solids mass must be positive. Received {manure_volatile_solids}.")
        Bo = methane_production_potential
        methane_conversion_factor = SolidsStorageCalculator.calculate_methane_conversion_factor(manure_temperature)
        methane_emissions_in_kg = (
            manure_volatile_solids * Bo * UserConstants.METHANE_FACTOR * methane_conversion_factor
        ) / 100
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
        return max(0.0, ManureConstants.MCF_CONSTANT_A * manure_temperature - ManureConstants.MCF_CONSTANT_B)

    @staticmethod
    def calculate_degradable_volatile_solids_fraction(
        degradable_volatile_solids: float, total_volatile_solids: float
    ) -> float:
        """
        Calculates the fraction of degradable volatile solids.

        Parameters
        ----------
        degradable_volatile_solids : float
            Mass of degradable volatile solids in the manure stream (kg).
        total_volatile_solids : float
            Mass of total volatile solids in the manure stream (kg).

        Returns
        -------
        float
            The fraction of degradable volatile solids (unitless).

        """
        if total_volatile_solids == 0:
            return 0
        else:
            return degradable_volatile_solids / total_volatile_solids
