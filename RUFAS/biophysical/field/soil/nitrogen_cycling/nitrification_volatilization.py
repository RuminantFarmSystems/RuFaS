from math import exp
from typing import Optional

from RUFAS.biophysical.field.soil.soil_data import SoilData


class NitrificationVolatilization:
    """
    Manages the nitrification and volatilization operations for the ammonium pool, in accordance with SWAT section
    3:1.3.

    Parameters
    ----------
    soil_data : SoilData, optional
        The SoilData object used by this module for tracking the nitrification and volatilization of ammonium in the
        soil. If not provided, a new SoilData object will be instantiated.
    field_size : float, optional
        The size of the field in hectares (ha), used to initialize a SoilData object if one is not directly provided.

    Attributes
    ----------
    data : SoilData
        Holds the SoilData object for tracking nitrification and volatilization processes.

    Notes
    -----
    The provision of a field size is crucial when a pre-configured SoilData object is not available, as it enables the
    initialization of a SoilData object. This allows for the simulation of nitrification and volatilization processes
    specific to the given field size.

    """

    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None):
        self.data = soil_data or SoilData(field_size=field_size)

    def do_daily_nitrification_and_volatilization(self) -> None:
        """
        Conducts the nitrification and volatilization of ammonium within the soil profile on a daily basis.

        Notes
        -----
        This method uses the `nutrient_cycling_water_factor` calculated by :class:`LayerData`, instead of the water
        factor that SWAT specifies for use in calculating denitrification/volatilization (see SWAT Theoretical
        documentation eqn. 3:1.3.2, 3).

        References
        ----------
        SWAT Theoretical documentation section 3:1.3

        """
        self.data.set_vectorized_layer_attribute("ammonia_emissions", [0.0] * len(self.data.soil_layers))
        for layer in self.data.soil_layers:
            if layer.temperature <= 5:
                continue

            temp_factor = self._calculate_nitrification_volatilization_temp_factor(layer.temperature)
            water_factor = layer.nutrient_cycling_water_factor

            depth_factor = self._calculate_volatilization_depth_factor(layer.depth_of_layer_center)

            nitrification_regulator = self._calculate_nitrification_regulator(temp_factor, water_factor)
            volatilization_regulator = self._calculate_volatilization_regulator(
                temp_factor,
                depth_factor,
                layer.ammonium_volatilization_cation_exchange_factor,
            )

            nitrification_loss_fraction = self._calculate_ammonium_loss_fraction(nitrification_regulator)
            volatilization_loss_fraction = self._calculate_ammonium_loss_fraction(volatilization_regulator)

            total_ammonium_lost = self._calculate_total_ammonium_lost(
                layer.ammonium_content,
                nitrification_regulator,
                volatilization_regulator,
            )

            nitrified_ammonium = self._calculate_ammonium_lost_to_process(
                total_ammonium_lost,
                nitrification_loss_fraction,
                volatilization_loss_fraction,
            )
            volatilized_ammonium = self._calculate_ammonium_lost_to_process(
                total_ammonium_lost,
                volatilization_loss_fraction,
                nitrification_loss_fraction,
            )

            layer.ammonium_content -= total_ammonium_lost
            layer.nitrate_content += nitrified_ammonium
            layer.ammonia_emissions = volatilized_ammonium
            layer.annual_ammonia_emissions_total += volatilized_ammonium

    # --- Static methods ---
    @staticmethod
    def _calculate_nitrification_volatilization_temp_factor(
        temperature: float,
    ) -> float:
        """
        Calculates the nitrification/volatilization temperature factor.

        Parameters
        ----------
        temperature : float
            Current temperature of the soil layer (degrees C).

        Returns
        -------
        float
            The nitrification/volatilization temperature factor of the current layer of soil (unitless).

        Notes
        -----
        SWAT does not explicitly say that this temperature factor should be upper-bounded at 1.0, but after discussion
        with Pete Vadas it came to light that this factor needs to have an upper bound.

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.3.1

        """
        return min(1.0, 0.41 * ((temperature - 5) / 10))

    @staticmethod
    def _calculate_nitrification_soil_water_factor(
        water_content: float, wilting_point: float, field_capacity: float
    ) -> float:
        """
        Calculates the soil water factor for nitrification.

        Parameters
        ----------
        water_content : float
            Water present in this soil layer (mm).
        wilting_point : float
            Amount of water in this soil layer when at wilting point (mm).
        field_capacity : float
            Amount of water in this soil layer when at field capacity (mm).

        Returns
        -------
        float
            The nitrification soil water factor (unitless).

        Notes
        -----
        The SWAT documentation for this equation appears to be misaligned with its implementation, see the file nitvol.f
        (https://bitbucket.org/blacklandgrasslandmodels/swat_development/src/master/nitvol.f).

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.3.2, 3

        """
        if water_content >= 0.25 * field_capacity - 0.75 * wilting_point:
            return 1.0
        upper_term = water_content - wilting_point
        bottom_term = 0.25 * (field_capacity - wilting_point)
        return upper_term / bottom_term

    @staticmethod
    def _calculate_volatilization_depth_factor(depth: float) -> float:
        """
        Calculates the depth factor for use in determining volatilization.

        Parameters
        ----------
        depth : float
            The depth of the center of this soil layer (mm).

        Returns
        -------
        float
            The volatilization depth factor (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.3.4

        """
        exponential_term = exp(4.706 - 0.0305 * depth)
        return 1 - (depth / (depth + exponential_term))

    @staticmethod
    def _calculate_nitrification_regulator(temp_factor: float, water_factor: float) -> float:
        """
        Calculates the nitrification regulator for this layer of soil.

        Parameters
        ----------
        temp_factor : float
            The nitrification/volatilization temperature factor of the current layer of soil (unitless).
        water_factor : float
            The nitrification soil water factor of the current soil layer (unitless).

        Returns
        -------
        float
            The nitrification regulator for this layer of soil (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.3.6

        """
        return temp_factor * water_factor

    @staticmethod
    def _calculate_volatilization_regulator(
        temp_factor: float, depth_factor: float, cation_exchange_factor: float
    ) -> float:
        """
        Calculates the volatilization regulator for this layer of soil.

        Parameters
        ----------
        temp_factor : float
            The nitrification/volatilization temperature factor of the current layer of soil (unitless).
        depth_factor : float
            The volatilization depth factor (unitless).
        cation_exchange_factor : float
            The volatilization cation exchange factor (unitless).

        Returns
        -------
        float
            The volatilization regulator for this layer of soil (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.3.7

        """
        return temp_factor * depth_factor * cation_exchange_factor

    @staticmethod
    def _calculate_total_ammonium_lost(
        ammonium_content: float,
        nitrification_regulator: float,
        volatilization_regulator: float,
    ) -> float:
        """
        Calculates the amount of ammonium lost to nitrification and volatilization.

        Parameters
        ----------
        ammonium_content : float
            The ammonium content of this soil layer (kg / ha).
        nitrification_regulator : float
            The nitrification regulator for this layer of soil (unitless).
        volatilization_regulator : float
            The volatilization regulator for this layer of soil (unitless).

        Returns
        -------
        float
            The amount of ammonium lost to nitrification and volatilization (kg / ha).

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.3.8

        """
        exponential_term = exp(-1 * nitrification_regulator - volatilization_regulator)
        return ammonium_content * (1 - exponential_term)

    @staticmethod
    def _calculate_ammonium_loss_fraction(regulator: float) -> float:
        """
        Calculates the fraction of lost ammonium that is lost to the specified process.

        Parameters
        ----------
        regulator : float
            The regulator for the process that ammonium is being lost to (unitless).

        Returns
        -------
        float
            Fraction of lost ammonium that is lost due to the given process (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.3.9, 10

        Notes
        -----
        This method is used to calculate the fraction of ammonium lost to both nitrification and volatilization.

        """
        return 1 - exp(-1 * regulator)

    @staticmethod
    def _calculate_ammonium_lost_to_process(
        total_lost_ammonium: float,
        actual_loss_fraction: float,
        other_loss_fraction: float,
    ) -> float:
        """
        Calculates the amount of ammonium lost to the specified process.

        Parameters
        ----------
        total_lost_ammonium : float
            The total ammonium content lost to nitrification and volatilization (kg / ha).
        actual_loss_fraction : float
            The loss fraction for the specified process that ammonium is being lost to (unitless).
        other_loss_fraction : float
            The loss fraction for the other process that ammonium is lost to (unitless).

        Returns
        -------
        float
            The amount of ammonium that is lost to the specified process (kg / ha).

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.3.11, 12

        Notes
        -----
        This method is intended to be used to calculate both the amount of ammonium lost to nitrification and to
        volatilization. To calculate the amount lost to nitrification, pass the nitrification loss fraction as the
        `actual_loss_fraction` and the volatilization loss fraction as the `other_loss_fraction`, and vice versa for
        calculating the amount lost to volatilization.

        """
        return (actual_loss_fraction / (actual_loss_fraction + other_loss_fraction)) * total_lost_ammonium
