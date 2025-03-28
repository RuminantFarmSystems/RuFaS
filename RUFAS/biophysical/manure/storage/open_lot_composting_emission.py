import math

from RUFAS.biophysical.manure.manure_constants import ManureConstants

OXYGEN_HALF_SATURATION_CONSTANT: float = 0.02
"""The half saturation constant of Oxygen gas (O2)"""


class OpenLotCompostingEmission:

    @staticmethod
    def total_carbon_decomposition(
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
        carbon_from_VSd = degradable_volatile_solids * ManureConstants.DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSD
        carbon_from_VSnd = non_degradable_volatile_solids * ManureConstants.DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSND
        total_carbon = carbon_from_VSd + carbon_from_VSnd

        microbial_decomp_rate = OpenLotCompostingEmission.carbon_decomposition_rate(days_since_last_tillage, lag)
        microbial_decomp_anaerobic_conditions_effect = OpenLotCompostingEmission.anaerobic_effect()
        total_carbon_decomposition = (
            total_carbon * microbial_decomp_rate * moisture_effect * microbial_decomp_anaerobic_conditions_effect
        )
        return total_carbon_decomposition

    @staticmethod
    def carbon_decomposition_rate(days_since_last_tillage: int = 1, lag: int = 2) -> float:
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

        max_microbial_decom_rate = OpenLotCompostingEmission.microbial_decomp_rate(decomposition_temp)
        slow_decomp_rate = OpenLotCompostingEmission.microbial_decomp_rate(compost_bed_pack_temp)
        exponent_coeff = decay * (days_since_last_tillage - lag)

        c_decomp_rate = (max_microbial_decom_rate - slow_decomp_rate) * math.exp(exponent_coeff) * slow_decomp_rate
        return c_decomp_rate

    @staticmethod
    def anaerobic_effect(
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
    def microbial_decomp_rate(temperature: float) -> float:
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
