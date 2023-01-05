class HeatUnits:
    def __init__(self, use_heat_unit_temperature: bool = False):
        self.minimum_temperature = 20
        self.maximum_temperature = 38
        self.potential_heat_units = 800
        self.accumulated_heat_units = 0  # accumulator
        self.is_growing = True  # TODO: not currently using; SWAT 5:2.1.4
        self.use_heat_unit_temperature: bool = use_heat_unit_temperature
        """determines if heat unit temperature will be used for heat unit accumulation."""
        # self.heat_unit_scheduling = True

        self.new_heat_units = None
        self.heat_fraction = None
        self.minimum_heat_unit_temperature = None
        self.maximum_heat_unit_temperature = None
        self.heat_unit_temperature = None
        self.previous_heat_fraction = None

    def absorb_heat_units(self, mean_air_temperature: float = None,
                          min_air_temperature: float = None, max_air_temperature: float = None) -> None:
        """main function for absorbing heat units during a day and accumulating them

        Args:
            mean_air_temperature: average air temperature for the day (C)
            min_air_temperature: minimum air temperature for the day (C)
            max_air_temperature: maximum air temperature for the day (C)

        Details: if the attribute use_heat_unit_temperature is false, both min_air_temperature and max_air_temperature
        are optional. Otherwise, they are used to determine heat unit accumulation rather than average air temperature.
        """
        self._check_absorb_heat_for_input_errors(mean_air_temperature, min_air_temperature, max_air_temperature)

        if self.use_heat_unit_temperature:
            self.maximum_heat_unit_temperature = \
                HeatUnits.determine_maximum_heat_unit_temperature(max_air_temperature, self.maximum_temperature)
            self.minimum_heat_unit_temperature = \
                HeatUnits.determine_minimum_heat_unit_temperature(min_air_temperature, self.minimum_temperature)
            self.heat_unit_temperature = \
                (self.minimum_heat_unit_temperature + self.maximum_heat_unit_temperature) / 2

        if self.use_heat_unit_temperature or mean_air_temperature is None:
            use_temp = self.heat_unit_temperature
        else:
            use_temp = mean_air_temperature
        self.is_growing = self.minimum_temperature <= use_temp <= self.maximum_temperature
        self.accumulate_heat_units(mean_air_temperature)
        self.previous_heat_fraction = self.heat_fraction
        self.heat_fraction = self.accumulated_heat_units / self.potential_heat_units

    # TODO: add these warnings to output manager at a later date.
    def _check_absorb_heat_for_input_errors(self, mean_air_temperature: float = None,
                                            min_air_temperature: float = None,
                                            max_air_temperature: float = None):
        """raises errors if inputs given for absorb_heat_units don't make sense with the value of the
        use_heat_unit_temperature attribute"""
        if self.use_heat_unit_temperature and (min_air_temperature is None or max_air_temperature is None):
            raise ValueError("min_air_temperature and max_air_temperature must be provided" +
                             " when use_heat_unit_temperature is True")
        if not self.use_heat_unit_temperature and mean_air_temperature is None:
            raise ValueError("mean_air_temperature must be provided when use_heat_temperature is False")

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
        if self.use_heat_unit_temperature or (air_temperature is None):  # alternative method
            self.new_heat_units = self.determine_new_heat_units(self.heat_unit_temperature, self.minimum_temperature)
        else:  # main method
            self.new_heat_units = self.determine_new_heat_units(air_temperature, self.minimum_temperature)

    def add_heat_units(self) -> None:
        """add newly acquired heat units to accumulated heat units"""
        self.accumulated_heat_units += self.new_heat_units

    @staticmethod
    def determine_new_heat_units(temperature: float, min_temperature: float) -> float:
        """calculates the heat units that will be accumulated during a day

        Args:
            temperature: the temperature to be compared to min_temp for accumulating heat units (C)
            min_temperature: the minimum temperature below which a crop cannot grow (C)
        """
        return max(temperature - min_temperature, 0)  # from SWAT:

    @staticmethod
    def determine_minimum_heat_unit_temperature(min_air_temp: float, min_growth_temp: float) -> float:
        """ calculates minimum heat unit temperature on current day.

        Args:
            min_air_temp: minimum temperature on the current day
            min_growth_temp: minimum temperature at which a crop can grow_crop

        Returns:
            float: minimum heat unit temperature
        """
        return max(min_air_temp, min_growth_temp)

    @staticmethod
    def determine_maximum_heat_unit_temperature(max_air_temp: float, max_growth_temp: float) -> float:
        """calculates maximum heat unit temperature on current day.
            "pseudocode_crop" C.2.A.4

        Args:
            max_air_temp: maximum temperature on the current day
            max_growth_temp: maximum temperature at which a crop can grow_crop

        Returns:
            maximum heat unit temperature
        """
        return min(max_air_temp, max_growth_temp)
