from typing import Optional
from RUFAS.routines.field.crop.crop_data import CropData


class HeatUnits:
    """
    A class that manages heat units for crop growth.

    Parameters
    ----------
    crop_data : Optional[CropData], optional
        An instance of `CropData` containing crop specifications and attributes. If not provided, a default
        `CropData` instance is initialized with default values.

    Attributes
    ----------
    data : CropData
        A reference to the `crop_data` object, used for accessing and updating crop-related data like
        temperature thresholds, accumulated heat units, and growth stages.

    Notes
    -----
    This module primarily follows the Heat Units section of the SWAT model (5:3.1)

    """

    def __init__(self, crop_data: Optional[CropData] = None):
        self.data = crop_data or CropData()  # initialize with defaults, if not given

    def absorb_heat_units(self, mean_air_temperature: float = None,
                          min_air_temperature: float = None, max_air_temperature: float = None) -> None:
        """
        Main function for absorbing heat units during a day and accumulating them.

        Parameters
        ----------
        mean_air_temperature : Optional[float]
            Average air temperature for the day (°C).
        min_air_temperature : Optional[float]
            Minimum air temperature for the day (°C).
        max_air_temperature : Optional[float]
            Maximum air temperature for the day (°C).

        Notes
        -----
        If the attribute `use_heat_unit_temperature` in CropData is False, both `min_air_temperature` and
        `max_air_temperature` are optional. Otherwise, they are used to determine heat unit accumulation rather than
        average air temperature.

        References
        ----------
        SWAT 5:1.1, 5:2.1.2

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
        """
        Accumulates heat units during a day based on the air temperature.

        Parameters
        ----------
        air_temperature : float
            The average air temperature during the day (°C).

        Notes
        -----
        The method of accumulation depends on the attribute `use_heat_unit_temperature`:
        - If `use_heat_unit_temperature` is False (default), the method accumulates every degree Celsius above the
        crop's minimum temperature for growth as heat units, following the SWAT manual.
        - If `use_heat_unit_temperature` is True, or `air_temperature` is None, an alternative method is used. In this
        method, the `heat_unit_temperature` attribute is used in place of the average air temperature. The accumulation
        varies depending on the relationship between the air temperature range and the crop's growth temperature range:
            1. If both min and max air temperatures are higher than the crop's min and max growth temperatures,
               accumulation is greater than the main method.
            2. If both min and max air temperatures are lower than the crop's min and max temperatures,
               accumulation is greater than the main method.
            3. If the air temperature range is entirely within the crop's temperature range, accumulation equals
               the middle of the crop temperature window.
            4. If the crop's temperature range is entirely within the air temperature range, accumulation equals
               the middle of the air temperature range.

        """
        self.assign_new_heat_units(air_temperature)
        self.add_heat_units()

    def assign_new_heat_units(self, air_temperature: float = None) -> None:
        """
        Assign new heat units based on whether the alternative accumulation method is to be used.

        Parameters
        ----------
        air_temperature : Optional[float], optional
            The average air temperature during the day (°C).

        """
        if self.data.use_heat_unit_temperature or (air_temperature is None):  # alternative method
            self.data.new_heat_units = self._determine_new_heat_units(self.data.heat_unit_temperature,
                                                                      self.data.minimum_temperature)
        else:  # main method
            self.data.new_heat_units = self._determine_new_heat_units(air_temperature, self.data.minimum_temperature)

    def add_heat_units(self) -> None:
        """
        Add newly acquired heat units to accumulated heat units.
        """
        self.data.accumulated_heat_units += self.data.new_heat_units

    # TODO: add these warnings to output manager at a later date.
    def _check_absorb_heat_for_input_errors(self, mean_air_temperature: float = None,
                                            min_air_temperature: float = None,
                                            max_air_temperature: float = None) -> None:
        """
        Raises errors if inputs given for absorb_heat_units don't make sense with the value of the
        use_heat_unit_temperature attribute.

        Parameters
        ----------
        mean_air_temperature : Optional[float], optional
            Average air temperature for the day (°C).
        min_air_temperature : Optional[float], optional
            Minimum air temperature for the day (°C).
        max_air_temperature : Optional[float], optional
            Maximum air temperature for the day (°C).

        Raises
        ------
        ValueError
            If `use_heat_unit_temperature` is True and both `min_air_temperature` and `max_air_temperature` are not
            provided.
            If `use_heat_unit_temperature` is False and `mean_air_temperature` is not provided.

        """
        if self.data.use_heat_unit_temperature and (min_air_temperature is None or max_air_temperature is None):
            raise ValueError("min_air_temperature and max_air_temperature must be provided" +
                             " when use_heat_unit_temperature is True")
        if not self.data.use_heat_unit_temperature and mean_air_temperature is None:
            raise ValueError("mean_air_temperature must be provided when use_heat_temperature is False")

    @staticmethod
    def _determine_new_heat_units(temperature: float, min_temperature: float) -> float:
        """
        Calculates the heat units that will be accumulated during a day.

        Parameters
        ----------
        temperature : float
            The temperature to be compared to min_temperature for accumulating heat units (°C).
        min_temperature : float
            The minimum temperature below which a crop cannot grow (°C).

        Returns
        -------
        float
            The calculated heat units to be accumulated based on the given temperature and minimum temperature (C).

        References
        ----------
        SWAT Reference 5:1.1

        """
        return max(temperature - min_temperature, 0)  # from SWAT:

    @staticmethod
    def _determine_minimum_heat_unit_temperature(min_air_temp: float, min_growth_temp: float) -> float:
        """
        Calculates the minimum heat unit temperature on the current day.

        Parameters
        ----------
        min_air_temp : float
            Minimum air temperature on the current day (°C).
        min_growth_temp : float
            Minimum temperature at which a crop can grow (°C).

        Returns
        -------
        float
            The calculated minimum heat unit temperature for the day (°C).

        """
        return max(min_air_temp, min_growth_temp)

    @staticmethod
    def _determine_maximum_heat_unit_temperature(max_air_temp: float, max_growth_temp: float) -> float:
        """
        Calculates the maximum heat unit temperature on the current day.

        Parameters
        ----------
        max_air_temp : float
            Maximum air temperature on the current day (°C).
        max_growth_temp : float
            Maximum temperature at which a crop can grow (°C).

        Returns
        -------
        float
            The maximum heat unit temperature for the day.

        References
        ----------
        "pseudocode_crop" C.2.A.4

        """
        return min(max_air_temp, max_growth_temp)

    # TODO: Heat scheduling? SWAT 5:1.1.1 - GitHub Issue #368
