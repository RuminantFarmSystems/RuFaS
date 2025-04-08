import math

from RUFAS.biophysical.manure.manure_constants import ManureConstants

OXYGEN_HALF_SATURATION_CONSTANT: float = 0.02
"""The half saturation constant of Oxygen gas (O2)"""

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

DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSD = 0.5
"""Default carbon content (percent by mass) of manure degradable volatile solids (unitless, [0, 1])."""

DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSND = 0.35
"""Default carbon content (percent by mass) of manure non-degradable volatile solids (unitless, [0, 1])."""

LEACHING_COEFFICIENT: float = 0.035
"""Leaching coefficient used in the calculation of nitrogen loss in a compost bedded pack barn (unitless)."""

class OpenLotCbpbCalculator:

    @staticmethod
    def calculate_ifsm_methane_emission(manure_volatile_solids: float, ambient_barn_temp: float) -> float:
        """Calculates emission of methane for a day using an adaptation of the tier 2 approach
        of the IPCC(2006), given ambient barn temperature and a methane conversion factor for the manure
        management.

        Parameters
        ----------
        manure_volatile_solids : float
            The volatile solids (kg).

        ambient_barn_temp : float
            The ambient barn temperature (Celsius).

        Returns
        -------
        float
            The calculated methane emissions (in kg) for the given ambient barn temperature.

        Notes
        -----
        CH4 emission = (VS * Bo * 0.67 * MCF) / 100

        """
        if manure_volatile_solids < 0:
            raise ValueError(f"{manure_volatile_solids=} mass must be positive.")
        Bo = ACHIEVABLE_METHANE_EMISSION
        methane_conversion_factor = OpenLotCbpbCalculator.calculate_methane_conversion_factor(ambient_barn_temp)
        methane_emissions_in_kg = (manure_volatile_solids * Bo * METHANE_FACTOR * methane_conversion_factor) / 100
        return methane_emissions_in_kg

    @staticmethod
    def calculate_methane_conversion_factor(ambient_barn_temp: float) -> float:
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
        return max(0.0, MCF_CONSTANT_A * ambient_barn_temp - MCF_CONSTANT_B)

    @staticmethod
    def calculate_total_carbon_decomposition(
        degradable_volatile_solids: float,
        non_degradable_volatile_solids: float,
        days_since_last_tillage: int,
        lag: int,
        moisture_effect: float = ManureConstants.DEFAULT_MOISTURE_EFFECT_MICROBIAL_DECOMP,
    ) -> float:
        """Calculates the carbon decomposition from the composting process of the manure-bed mixture
        due to microbial activity (decomposition, consumption, respiration).

        Parameters
        ----------
        non_degradable_volatile_solids : float
            Mass of non-degradable volatile solids in the manure stream (kg).
        degradable_volatile_solids : float
            Mass of degradable volatile solids in the manure stream (kg).
        days_since_last_tillage : int
            The number of days since the last tillage event.
        lag : int
            The lag time.
        moisture_effect : float
            The effect of moisture on microbial decomposition.

        Returns
        -------
        float
            The total carbon decomposition (kg).

        """
        carbon_from_VSd = degradable_volatile_solids * DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSD
        carbon_from_VSnd = non_degradable_volatile_solids * DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSND
        total_carbon = carbon_from_VSd + carbon_from_VSnd

        microbial_decomp_rate = OpenLotCbpbCalculator.calculate_carbon_decomposition_rate(days_since_last_tillage, lag)
        microbial_decomp_anaerobic_conditions_effect = OpenLotCbpbCalculator.calculate_anaerobic_effect()
        total_carbon_decomposition = (
            total_carbon * microbial_decomp_rate * moisture_effect * microbial_decomp_anaerobic_conditions_effect
        )
        return total_carbon_decomposition

    @staticmethod
    def calculate_carbon_decomposition_rate(days_since_last_tillage: int = 1, lag: int = 2) -> float:
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

        max_microbial_decom_rate = OpenLotCbpbCalculator.calculate_microbial_decomp_rate(decomposition_temp)
        slow_decomp_rate = OpenLotCbpbCalculator.calculate_microbial_decomp_rate(compost_bed_pack_temp)
        exponent_coeff = decay * (days_since_last_tillage - lag)

        c_decomp_rate = (max_microbial_decom_rate - slow_decomp_rate) * math.exp(exponent_coeff) * slow_decomp_rate
        return c_decomp_rate

    @staticmethod
    def calculate_anaerobic_effect(
        oxygen_mole_fraction: float = 0.15,
        oxygen_half_saturation_constant: float = OXYGEN_HALF_SATURATION_CONSTANT,
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

    @staticmethod
    def calculate_microbial_decomp_rate(temperature: float) -> float:
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

    @staticmethod
    def calculate_nitrogen_loss_from_leaching(received_nitrogen: float) -> float:
        """
        Calculate the mass of nitrogen that leaches out of the manure-bedding mixture.

        Parameters
        ----------
        received_nitrogen : float
            The mass of nitrogen present in the manure excreted by animals (kg).

        Returns
        -------
        float
            The amount of nitrogen that leaches out of the mixture (kg).

        Raises
        ------
        ValueError
            If the daily nitrogen input is negative.

        """

        if received_nitrogen < 0.0:
            raise ValueError(f"Daily nitrogen input mass must be non-negative: {received_nitrogen}")

        return LEACHING_COEFFICIENT * received_nitrogen


    @staticmethod
    def calculate_total_nitrogen_loss(
        storage_ammonia: float, storage_nitrogen_leached: float, storage_nitrous_oxide: float
    ) -> float:
        """
        Calculate the total nitrogen loss from the manure treatment.

        Parameters
        ----------
        storage_ammonia : float
            The amount of nitrogen lost to ammonia emission (kg).
        storage_nitrogen_leached : float
            The amount of nitrogen that leaches out of the bedding mixture (kg).
        storage_nitrous_oxide : float
            Nitrous oxide nitrogen emissions (kg).

        Returns
        -------
        float
            The total nitrogen loss from the open lots manure treatment (kg).

        """
        return storage_ammonia + storage_nitrogen_leached + storage_nitrous_oxide