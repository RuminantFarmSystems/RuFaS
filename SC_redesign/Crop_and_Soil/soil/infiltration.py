from math import exp, log
from typing import Optional

from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

"""
This module is based on the 'Runoff Volume: SCS Curve Number Procedure' (2:1.1) section of the SWAT model documentation
"""


class Infiltration:
    def __init__(self, soil_data: Optional[SoilData] = None):
        self.data = soil_data or SoilData()

    def infiltrate(self, second_moisture_condition_parameter: float, rainfall: float, is_top_layer_frozen: bool,
                   weighting_coefficient: float) -> None:
        """main routine for determining runoff and infiltration of soil for a given day"""
        third_moisture_condition_parameter = self._determine_third_moisture_condition_parameter(
                                                                                    second_moisture_condition_parameter)

        # --- adjust moisture condition parameters for slope of soil, if necessary -------------------------------------
        if abs(self.data.average_slope_fraction - 0.05) != 0:
            adjusted_second_moisture_condition_parameter = self._determine_second_moisture_condition_adjusted(
                                                                                    self.data.average_slope_fraction,
                                                                                    second_moisture_condition_parameter,
                                                                                    third_moisture_condition_parameter)
            adjusted_third_moisture_condition_parameter = self._determine_third_moisture_condition_parameter(
                                                                        adjusted_second_moisture_condition_parameter)
        else:
            adjusted_second_moisture_condition_parameter = second_moisture_condition_parameter
            adjusted_third_moisture_condition_parameter = third_moisture_condition_parameter
        # --------------------------------------------------------------------------------------------------------------
        adjusted_first_moisture_condition_parameter = self._determine_first_moisture_condition_parameter(
                                                                        adjusted_second_moisture_condition_parameter)

        first_moisture_condition_retention_parameter = self._determine_retention_parameter_for_moisture_condition(
                                                                            adjusted_first_moisture_condition_parameter)
        third_moisture_condition_retention_parameter = self._determine_retention_parameter_for_moisture_condition(
                                                                            adjusted_third_moisture_condition_parameter)

        profile_saturation = self.data.profile_saturation
        profile_field_capacity = self.data.profile_field_capacity

        second_shape_coefficient = self._determine_second_shape_coefficient(profile_field_capacity, profile_saturation,
                                                                            first_moisture_condition_retention_parameter,
                                                                            third_moisture_condition_retention_parameter)
        first_shape_coefficient = self._determine_first_shape_coefficient(profile_field_capacity,
                                                                          first_moisture_condition_retention_parameter,
                                                                          third_moisture_condition_retention_parameter,
                                                                          second_shape_coefficient)
        profile_water_content = self.data.profile_soil_water_content
        retention_parameter = self._determine_retention_parameter(profile_water_content,
                                                                  first_moisture_condition_retention_parameter,
                                                                  first_shape_coefficient,
                                                                  second_shape_coefficient)

        # --- Adjust retention parameter only if top layer of soil is frozen -------------------------------------------
        if is_top_layer_frozen:
            retention_parameter = self._determine_frozen_retention_parameter(
                                                                        first_moisture_condition_retention_parameter,
                                                                        retention_parameter)
        # --------------------------------------------------------------------------------------------------------------

        runoff = self._determine_accumulated_runoff(rainfall, retention_parameter)

        # --- Update previous retention parameter ----------------------------------------------------------------------
        if self.data.previous_retention_parameter is None:
            self.data.previous_retention_parameter = 0.9 * first_moisture_condition_retention_parameter
        else:
            self.data.previous_retention_parameter = self._determine_updated_retention_parameter(
                                                                        self.data.previous_retention_parameter,
                                                                        self.data.potential_evapotranspiration,
                                                                        first_moisture_condition_retention_parameter,
                                                                        rainfall,
                                                                        runoff,
                                                                        weighting_coefficient)
        # --------------------------------------------------------------------------------------------------------------

        self.data.moisture_condition_parameter = self._determine_moisture_condition_parameter(retention_parameter)

    # --- static methods ---
    @staticmethod
    def _determine_first_moisture_condition_parameter(second_moisture_condition: float):
        """determine curve number for dry (wilting point) conditions

        Args:
            second_moisture_condition: curve number for average moisture conditions

        Returns:
            curve number 1 (dry/wilting point conditions), unitless

        SWAT Reference: 2:1.1.4
        """
        top = 20 * (100 - second_moisture_condition)
        bottom = (100 - second_moisture_condition + exp(2.533 - 0.0636 * (100 - second_moisture_condition)))
        return second_moisture_condition - (top / bottom)

    @staticmethod
    def _determine_third_moisture_condition_parameter(second_moisture_condition: float):
        """determine curve number for wet (field capacity) conditions

        Args:
            second_moisture_condition: curve number for average moisture conditions

        Returns:
            curve number 3 (wet/field capacity conditions), unitless

        SWAT Reference: 2:1.1.5
        """
        return second_moisture_condition * exp(0.00673 * (100 - second_moisture_condition))

    @staticmethod
    def _determine_retention_parameter_for_moisture_condition(moisture_condition_parameter: float) -> float:
        """calculates the retention parameter used to determine runoff

        Args:
            moisture_condition_parameter: curve number for the day (from SCS runoff equations (SWAT 2:1.1))

        Returns:
            retention parameter in mm

        SWAT Reference: 2:1.1.2
        """
        return 25.4 * ((1000 / moisture_condition_parameter) - 10)

    @staticmethod
    def _determine_second_shape_coefficient(field_capacity: float,
                                            saturation: float,
                                            max_retention_parameter: float,
                                            third_moisture_condition_retention_parameter: float) -> float:
        """determines the second shape coefficient for use in calculating the first shape coefficient and retention
        parameter for a given day

        Args:
            field_capacity: amount of water in soil profile at field capacity in mm
            saturation: amount of water in soil profile when saturated in mm
            max_retention_parameter: retention parameter calculated from curve number 1 (driest conditions)
            third_moisture_condition_retention_parameter: retention parameter calculated from curve number 3 (the
                wettest conditions)

        Returns:
            the second shape coefficient (unitless)

        SWAT Reference: 2:1.1.8
        """
        first_top_term = log((field_capacity / (1 - (third_moisture_condition_retention_parameter /
                                                     max_retention_parameter))) -
                             field_capacity)
        second_top_term = log((saturation / (1 - (2.54 / max_retention_parameter))) - saturation)
        return (first_top_term - second_top_term) / (saturation - field_capacity)

    @staticmethod
    def _determine_first_shape_coefficient(field_capacity: float,
                                           max_retention_parameter: float,
                                           third_moisture_condition_retention_parameter: float,
                                           second_shape_coefficient: float) -> float:
        """calculates the first shape coefficient for use in calculating the retention parameter

        Args:
            field_capacity: amount of water in soil profile at field capacity in mm
            max_retention_parameter: retention parameter calculated from curve number 1 (driest conditions)
            third_moisture_condition_retention_parameter: retention parameter calculated from curve number 3 (the
                wettest conditions)
            second_shape_coefficient: the second shape coefficient (unitless)

        Returns:
            the first shape coefficient unitless

        SWAT Reference: 2:1.1.7
        """
        first_term = log((field_capacity / (1 - (third_moisture_condition_retention_parameter /
                                                 max_retention_parameter))) - field_capacity)
        second_term = second_shape_coefficient * field_capacity
        return first_term + second_term

    @staticmethod
    def _determine_retention_parameter(soil_water_content: float,
                                       max_retention_parameter: float,
                                       first_shape_coefficient: float,
                                       second_shape_coefficient: float) -> float:
        """returns the retention parameter for a given day

        Args:
            soil_water_content: amount of water held in the soil profile excluding amount of water held in profile at
                the wilting point in mm
            max_retention_parameter: maximum retention parameter, calculated from curve number 1 (driest conditions) in
                mm
            first_shape_coefficient: first shape coefficient, unitless
            second_shape_coefficient: second shape coefficient, unitless

        Returns:
            retention parameter for a given day in mm

        SWAT Reference: 2:1.1.6
        """
        return max_retention_parameter * (1 - (soil_water_content / (soil_water_content + exp(first_shape_coefficient -
                                                                                              (second_shape_coefficient
                                                                                               * soil_water_content)))))

    @staticmethod
    def _determine_frozen_retention_parameter(max_retention_parameter: float, retention_parameter: float) -> float:
        """determines the adjusted retention parameter if the top layer of soil is frozen

        Args:
            max_retention_parameter: maximum retention parameter, calculated from curve number 1 (driest conditions) in
                mm
            retention_parameter: retention parameter for a given day in mm

        Returns:
            retention parameter for a given day adjusted for frozen soil in mm

        SWAT Reference: 2:1.1.10
        """
        return max_retention_parameter * (1 - exp(-0.000862 * retention_parameter))

    @staticmethod
    def _determine_second_moisture_condition_adjusted(average_fraction_slope: float,
                                                      second_moisture_condition: float,
                                                      third_moisture_condition: float) -> float:
        """determines curve for moisture condition 2 (average moisture conditions) adjusted for slope

        Args:
            average_fraction_slope: average slope fraction of subbasin
            second_moisture_condition: moisture condition 2 curve for (default) 5% slope
            third_moisture_condition: moisture condition 3 curve for (default) 5% slope

        Returns:
            moisture condition 2 curve adjusted for actual slop of the soil

        SWAT Reference: 2:1.1.12
        """
        first_factor = (third_moisture_condition - second_moisture_condition) / 3
        second_factor = 1 - (2 * exp(-13.86 * average_fraction_slope))
        return (first_factor * second_factor) + second_moisture_condition

    @staticmethod
    def _determine_accumulated_runoff(rainfall: float, retention_parameter: float) -> float:
        """calculates accumulated runoff or rainfall excess

        Args:
            rainfall: rainfall depth of given day in mm
            retention_parameter: retention parameter based on curve number in mm

        Returns:
            accumulated runoff or rainfall excess in mm

        Details:
            Runoff only occurs when rainfall is greater than initial abstractions (about surface storage, interception,
            etc.) which are approximated as 0.2 * retention parameter in SWAT 2:1.1 and here

        SWAT Reference: 2:1.1.1, 3
        """
        if rainfall > (0.2 * retention_parameter):
            return ((rainfall - (0.2 * retention_parameter)) ** 2) / (rainfall + (0.8 * retention_parameter))
        else:
            return 0

    @staticmethod
    def _determine_updated_retention_parameter(previous_retention_parameter: float,
                                               potential_evapotranspiration: float,
                                               max_retention_parameter: float,
                                               rainfall: float,
                                               runoff: float,
                                               weighting_coefficient: float) -> float:
        """updates the retention parameter based on the previous day's retention parameter and the current day's
            conditions

        Args:
            previous_retention_parameter: retention parameter from previous day in mm
            potential_evapotranspiration: potential evapotranspiration for current day in mm per day
            max_retention_parameter: maximum retention parameter for the current day in mm
            rainfall: rainfall depth of current day in mm
            runoff: surface runoff of current day in mm
            weighting_coefficient: weighting coefficient used to calculate retention coefficient for daily curve number
                calculations dependent on plant evapotranspiration

        Returns:
            retention parameter for the current day in mm

        SWAT Reference: 2:1.1.9
        """
        retention_parameter = previous_retention_parameter - rainfall + runoff
        retention_parameter += potential_evapotranspiration * exp((((-1) * weighting_coefficient) *
                                                                   previous_retention_parameter)
                                                                  / max_retention_parameter)
        return retention_parameter

    @staticmethod
    def _determine_moisture_condition_parameter(retention_parameter: float) -> float:
        return 25400 / (retention_parameter + 254)
