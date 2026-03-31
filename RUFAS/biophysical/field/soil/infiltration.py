from math import exp, log
from typing import Optional

from RUFAS.biophysical.field.soil.soil_data import SoilData


class Infiltration:
    """
    Simulates the infiltration of water into the soil profile using the 'Runoff Volume: SCS Curve Number Procedure'
    as described in section 2:1.1 of the SWAT (Soil and Water Assessment Tool) model documentation.

    Parameters
    ----------
    soil_data : SoilData, optional
        An instance of SoilData for tracking the water infiltration in the soil profile. If not provided, a new
        instance will be created with the specified field size.
    field_size : float, optional
        The size of the field (ha).

    Attributes
    ----------
    data : SoilData
        The SoilData object that stores and manages the water infiltration data within the soil profile.

    """

    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        self.data = soil_data or SoilData(field_size=field_size)

    def infiltrate(self, rainfall: float) -> None:
        """
        Main routine for determining runoff and infiltration of soil for a given day.

        Parameters
        ----------
        rainfall : float
            Rainfall depth of current day (mm).

        Notes
        -----
        The amount of water that is allowed to infiltrate the soil profile on any given day is limited by the available
        capacity of the total soil profile. This means that on some days more water will infiltrate the surface soil
        layer than there is capacity in said layer. This works fine as long as water is allowed to percolate out of the
        surface layer after this.

        The methodology in SWAT automatically adjusts the Second Moisture Condition Parameter. This behavior was removed
        from RuFaS after consulting with SMEs who determined it was inappropriate to change user input in this way. See
        PR #772 for more discussion.

        """
        third_moisture_condition_parameter = self._determine_third_moisture_condition_parameter(
            self.data.second_moisture_condition_parameter
        )

        first_moisture_condition_parameter = self._determine_first_moisture_condition_parameter(
            self.data.second_moisture_condition_parameter
        )

        first_moisture_condition_retention_parameter = self._determine_retention_parameter_for_moisture_condition(
            first_moisture_condition_parameter
        )
        third_moisture_condition_retention_parameter = self._determine_retention_parameter_for_moisture_condition(
            third_moisture_condition_parameter
        )

        profile_saturation = self.data.profile_saturation
        profile_field_capacity = self.data.profile_field_capacity

        second_shape_coefficient = self._determine_second_shape_coefficient(
            profile_field_capacity,
            profile_saturation,
            first_moisture_condition_retention_parameter,
            third_moisture_condition_retention_parameter,
        )
        first_shape_coefficient = self._determine_first_shape_coefficient(
            profile_field_capacity,
            first_moisture_condition_retention_parameter,
            third_moisture_condition_retention_parameter,
            second_shape_coefficient,
        )
        profile_water_content = self.data.profile_soil_water_content
        retention_parameter = self._determine_retention_parameter(
            profile_water_content,
            first_moisture_condition_retention_parameter,
            first_shape_coefficient,
            second_shape_coefficient,
        )

        # --- Adjust retention parameter only if top layer of soil is frozen -------------------------------------------
        if self.data.soil_layers[0].temperature <= 0:
            retention_parameter = self._determine_frozen_retention_parameter(
                first_moisture_condition_retention_parameter, retention_parameter
            )
        # --------------------------------------------------------------------------------------------------------------
        self.data.accumulated_runoff = min(rainfall, self._determine_accumulated_runoff(rainfall, retention_parameter))
        infiltrated_water = max(0.0, rainfall - self.data.accumulated_runoff)
        self.data.infiltrated_water = infiltrated_water

        # Update annual totals
        self.data.annual_runoff_total += self.data.accumulated_runoff

    # --- static methods ---
    @staticmethod
    def _determine_first_moisture_condition_parameter(second_moisture_condition: float):
        """
        Determine the curve number for dry (wilting point) conditions.

        Parameters
        ----------
        second_moisture_condition : float
            Curve number for average moisture conditions (unitless).

        Returns
        -------
        float
            Curve number 1 (dry/wilting point conditions) (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 2:1.1.4

        """
        top = 20 * (100 - second_moisture_condition)
        bottom = 100 - second_moisture_condition + exp(2.533 - 0.0636 * (100 - second_moisture_condition))
        return second_moisture_condition - (top / bottom)

    @staticmethod
    def _determine_third_moisture_condition_parameter(second_moisture_condition: float):
        """
        Determine the curve number for wet (field capacity) conditions.

        Parameters
        ----------
        second_moisture_condition : float
            Curve number for average moisture conditions (unitless).

        Returns
        -------
        float
            Curve number 3 (wet/field capacity conditions) (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 2:1.1.5

        """
        return second_moisture_condition * exp(0.00673 * (100 - second_moisture_condition))

    @staticmethod
    def _determine_retention_parameter_for_moisture_condition(
        moisture_condition_parameter: float,
    ) -> float:
        """
        Calculate the retention parameter used to determine runoff.

        Parameters
        ----------
        moisture_condition_parameter : float
            Curve number for the day (from SCS runoff equations (SWAT 2:1.1)) (unitless).

        Returns
        -------
        float
            Retention parameter (mm).

        References
        ----------
        SWAT Theoretical documentation eqn. 2:1.1.2

        """
        return 25.4 * ((1000 / moisture_condition_parameter) - 10)

    @staticmethod
    def _determine_second_shape_coefficient(
        field_capacity: float,
        saturation: float,
        max_retention_parameter: float,
        third_moisture_condition_retention_parameter: float,
    ) -> float:
        """
        Determine the second shape coefficient for use in calculating the first shape coefficient and retention
        parameter for a given day.

        Parameters
        ----------
        field_capacity : float
            Amount of water in soil profile at field capacity (mm).
        saturation : float
            Amount of water in soil profile when saturated (mm).
        max_retention_parameter : float
            Retention parameter calculated from curve number 1 (the driest conditions) (unitless).
        third_moisture_condition_retention_parameter : float
            Retention parameter calculated from curve number 3 (the wettest conditions) (unitless).

        Returns
        -------
        float
            The second shape coefficient (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 2:1.1.8

        """
        first_top_term = log(
            (field_capacity / (1 - (third_moisture_condition_retention_parameter / max_retention_parameter)))
            - field_capacity
        )
        second_top_term = log((saturation / (1 - (2.54 / max_retention_parameter))) - saturation)
        return (first_top_term - second_top_term) / (saturation - field_capacity)

    @staticmethod
    def _determine_first_shape_coefficient(
        field_capacity: float,
        max_retention_parameter: float,
        third_moisture_condition_retention_parameter: float,
        second_shape_coefficient: float,
    ) -> float:
        """
        Calculate the first shape coefficient for use in calculating the retention parameter.

        Parameters
        ----------
        field_capacity : float
            Amount of water in soil profile at field capacity (mm).
        max_retention_parameter : float
            Retention parameter calculated from curve number 1 (the driest conditions) (unitless).
        third_moisture_condition_retention_parameter : float
            Retention parameter calculated from curve number 3 (the wettest conditions) (unitless).
        second_shape_coefficient : float
            The second shape coefficient (unitless).

        Returns
        -------
        float
            The first shape coefficient (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 2:1.1.7

        """
        first_term = log(
            (field_capacity / (1 - (third_moisture_condition_retention_parameter / max_retention_parameter)))
            - field_capacity
        )
        second_term = second_shape_coefficient * field_capacity
        return first_term + second_term

    @staticmethod
    def _determine_retention_parameter(
        soil_water_content: float,
        max_retention_parameter: float,
        first_shape_coefficient: float,
        second_shape_coefficient: float,
    ) -> float:
        """
        Return the retention parameter for a given day.

        Parameters
        ----------
        soil_water_content : float
            Amount of water held in the soil profile excluding the amount of water held in
            the profile at the wilting point (mm).
        max_retention_parameter : float
            Maximum retention parameter, calculated from curve number 1
            (the driest conditions) (mm).
        first_shape_coefficient : float
            First shape coefficient (unitless).
        second_shape_coefficient : float
            Second shape coefficient (unitless).

        Returns
        -------
        float
            Retention parameter for a given day (mm).

        References
        ----------
        SWAT Theoretical documentation eqn. 2:1.1.6

        """
        return max_retention_parameter * (
            1
            - (
                soil_water_content
                / (soil_water_content + exp(first_shape_coefficient - (second_shape_coefficient * soil_water_content)))
            )
        )

    @staticmethod
    def _determine_frozen_retention_parameter(max_retention_parameter: float, retention_parameter: float) -> float:
        """
        Determine the adjusted retention parameter if the top layer of soil is frozen.

        Parameters
        ----------
        max_retention_parameter : float
            Maximum retention parameter, calculated from curve number 1.
            (the driest conditions) (mm).
        retention_parameter : float
            Retention parameter for a given day (mm).

        Returns
        -------
        float
            Retention parameter for a given day adjusted for frozen soil (mm).

        References
        ----------
        SWAT Theoretical documentation eqn. 2:1.1.10

        """
        return max_retention_parameter * (1 - exp(-0.000862 * retention_parameter))

    @staticmethod
    def _determine_accumulated_runoff(rainfall: float, retention_parameter: float) -> float:
        """
        Calculate accumulated runoff or rainfall excess.

        Parameters
        ----------
        rainfall : float
            Rainfall depth of the given day (mm).
        retention_parameter : float
            Retention parameter based on curve number (mm).

        Returns
        -------
        float
            Accumulated runoff or rainfall excess (mm).

        Notes
        -----
        Runoff only occurs when rainfall is greater than initial abstractions (about surface storage, interception,
        etc.) which are approximated as 0.2 times the retention parameter in SWAT 2:1.1 and here.

        References
        ----------
        SWAT Theoretical documentation eqn. 2:1.1.1, 3

        """
        if rainfall > (0.2 * retention_parameter):
            return ((rainfall - (0.2 * retention_parameter)) ** 2) / (rainfall + (0.8 * retention_parameter))
        else:
            return 0
