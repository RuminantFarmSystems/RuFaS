from typing import Optional
from RUFAS.routines.field.crop.crop_data import CropData

"""
This module primarily follows the Heat Units section of the SWAT model (5:3.1)
"""


class HeatUnits:
    def __init__(self, crop_data: Optional[CropData] = None):
        self.data = crop_data or CropData()  # initialize with defaults, if not given

    def absorb_heat_units(self, mean_air_temperature: float = None,
                          min_air_temperature: float = None, max_air_temperature: float = None) -> None:
        """main function for absorbing heat units during a day and accumulating them

        Args:
            mean_air_temperature: average air temperature for the day (C)
            min_air_temperature: minimum air temperature for the day (C)
            max_air_temperature: maximum air temperature for the day (C)

        SWAT References: 5:1.1, 5:2.1.2,

        Details: if the attribute use_heat_unit_temperature is false, both min_air_temperature and max_air_temperature
        are optional. Otherwise, they are used to determine heat unit accumulation rather than average air temperature.
        """
        self._check_absorb_heat_for_input_errors(mean_air_temperature, min_air_temperature, max_air_temperature)

        if self.data.use_heat_unit_temperature:
            self.data.maximum_heat_unit_temperature = \
                HeatUnits._determine_maximum_heat_unit_temperature(max_air_temperature, self.data.maximum_temperature)
            self.data.minimum_heat_unit_temperature = \
                HeatUnits._determine_minimum_heat_unit_temperature(min_air_temperature, self.data.minimum_temperature)
            self.data.heat_unit_temperature = \
                (self.data.minimum_heat_unit_temperature + self.data.maximum_heat_unit_temperature) / 2

        if self.data.use_heat_unit_temperature or mean_air_temperature is None:
            use_temp = self.data.heat_unit_temperature
        else:
            use_temp = mean_air_temperature
        self.data.is_growing = self.data.minimum_temperature <= use_temp <= self.data.maximum_temperature
        self.accumulate_heat_units(mean_air_temperature)

    def accumulate_heat_units(self, air_temperature: float = None) -> None:
        """accumulates heat units during a day

        Args:
            air_temperature: the average air temperature during the day (C)

        Details:
            If the attribute use_heat_unit_temperature is False, then the main
            accumulation method occurs (as in SWAT manual). This method accumulates every degree C above the crop's
            minimum temperature for growth as heat units.

            If use_heat_unit_temperature is True (or air_temperature=None), then the alternative method is used. in this
            method, the heat_unit_temperature attribute is used in place of average air temperature.

            Whereas heat units accumulated by the main method are always equal to the average air temperature (when
            above the minimum threshold), the alternative method is context dependent:
                1. if the minimum and maximum air temperature are both **higher** than the crop's minimum and maximum
                growth temperatures, then accumulation will be greater than with the main method
                2. if the minimum and maximum air temperatures are both **lower** than the crop's minimum and maximum
                temperatures, then accumulation will be greater than with the main method
                3. if the air temperature window is entirely contained within the crop temperature window
                (i.e., crop mint < air mint < air maxt < crop maxt), then accumulation will be equal to the middle of
                the crop temperature window
                4. if the crop temperature window is entirely contained withing the air temperature window, then
                accumulation will equal the middle of the temperature window
        """
        self.assign_new_heat_units(air_temperature)
        self.add_heat_units()

    def assign_new_heat_units(self, air_temperature: float = None) -> None:
        """assign new heat units based on if the alternative accumulation method is to be used"""
        if self.data.use_heat_unit_temperature or (air_temperature is None):  # alternative method
            self.data.new_heat_units = self._determine_new_heat_units(self.data.heat_unit_temperature,
                                                                      self.data.minimum_temperature)
        else:  # main method
            self.data.new_heat_units = self._determine_new_heat_units(air_temperature, self.data.minimum_temperature)

    def add_heat_units(self) -> None:
        """add newly acquired heat units to accumulated heat units"""
        self.data.accumulated_heat_units += self.data.new_heat_units

    # TODO: add these warnings to output manager at a later date.
    def _check_absorb_heat_for_input_errors(self, mean_air_temperature: float = None,
                                            min_air_temperature: float = None,
                                            max_air_temperature: float = None):
        """raises errors if inputs given for absorb_heat_units don't make sense with the value of the
        use_heat_unit_temperature attribute"""
        if self.data.use_heat_unit_temperature and (min_air_temperature is None or max_air_temperature is None):
            raise ValueError("min_air_temperature and max_air_temperature must be provided" +
                             " when use_heat_unit_temperature is True")
        if not self.data.use_heat_unit_temperature and mean_air_temperature is None:
            raise ValueError("mean_air_temperature must be provided when use_heat_temperature is False")

    @staticmethod
    def _determine_new_heat_units(temperature: float, min_temperature: float) -> float:
        """calculates the heat units that will be accumulated during a day

        Args:
            temperature: the temperature to be compared to min_temp for accumulating heat units (C)
            min_temperature: the minimum temperature below which a crop cannot grow (C)

        SWAT Reference: 5:1.1
        """
        return max(temperature - min_temperature, 0)  # from SWAT:

    @staticmethod
    def _determine_minimum_heat_unit_temperature(min_air_temp: float, min_growth_temp: float) -> float:
        """ calculates minimum heat unit temperature on current day.

        Args:
            min_air_temp: minimum temperature on the current day
            min_growth_temp: minimum temperature at which a crop can grow_crop

        Returns:
            float: minimum heat unit temperature
        """
        return max(min_air_temp, min_growth_temp)

    @staticmethod
    def _determine_maximum_heat_unit_temperature(max_air_temp: float, max_growth_temp: float) -> float:
        """calculates maximum heat unit temperature on current day.
            "pseudocode_crop" C.2.A.4

        Args:
            max_air_temp: maximum temperature on the current day
            max_growth_temp: maximum temperature at which a crop can grow_crop

        Returns:
            maximum heat unit temperature
        """
        return min(max_air_temp, max_growth_temp)

    # TODO: Heat scheduling? SWAT 5:1.1.1 - GitHub Issue #368
