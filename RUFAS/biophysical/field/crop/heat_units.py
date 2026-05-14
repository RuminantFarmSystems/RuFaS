from RUFAS.biophysical.field.crop.crop_data import CropData


class HeatUnits:
    """
    A class that manages heat units for crop growth.

    Parameters
    ----------
    crop_data : CropData, optional
        An instance of ``CropData`` containing crop specifications and attributes. If not provided, a default
        ``CropData`` instance is initialized with default values.
    maximum_temperature : float, default 38
        Maximum temperature for plant growth (Celsius).
    use_heat_unit_temperature : bool, default False
        If alternative heat unit method is used.
    new_heat_units : float, optional
        Heat units accumulated on the current day (Celsius).
    minimum_heat_unit_temperature : float, optional
        Minimum temperature for heat unit calculations (Celsius).
    maximum_heat_unit_temperature : float, optional
        Maximum temperature for heat unit calculations (Celsius).
    heat_unit_temperature : float, optional
        Heat unit temperature for alternative method (Celsius).

    Attributes
    ----------
    data : CropData
        A reference to the ``crop_data`` object, used for accessing and updating crop-related data like
        temperature thresholds, accumulated heat units, and growth stages.
    maximum_temperature : float
        Maximum temperature for plant growth (Celsius).
    use_heat_unit_temperature : bool
        If alternative heat unit method is used.
    new_heat_units : float | None
        Heat units accumulated on the current day (Celsius*).
    minimum_heat_unit_temperature : float | None
        Minimum temperature for heat unit calculations (Celsius).
    maximum_heat_unit_temperature : float | None
        Maximum temperature for heat unit calculations (Celsius).
    heat_unit_temperature : float | None
        Heat unit temperature for alternative method (Celsius).

    Notes
    -----
    This module primarily follows the Heat Units section of the SWAT model (5:3.1)

    """

    def __init__(
        self,
        crop_data: CropData | None = None,
        maximum_temperature: float = 38.0,
        use_heat_unit_temperature: bool = False,
        new_heat_units: float | None = None,
        minimum_heat_unit_temperature: float | None = None,
        maximum_heat_unit_temperature: float | None = None,
        heat_unit_temperature: float | None = None,
    ) -> None:
        self.data = crop_data or CropData()
        self.maximum_temperature = maximum_temperature
        self.use_heat_unit_temperature = use_heat_unit_temperature
        self.new_heat_units = new_heat_units
        self.minimum_heat_unit_temperature = minimum_heat_unit_temperature
        self.maximum_heat_unit_temperature = maximum_heat_unit_temperature
        self.heat_unit_temperature = heat_unit_temperature

    def absorb_heat_units(
        self,
        mean_air_temperature: float | None = None,
        min_air_temperature: float | None = None,
        max_air_temperature: float | None = None,
    ) -> None:
        """
        Main function for absorbing heat units during a day and accumulating them.

        Parameters
        ----------
        mean_air_temperature : float, optional
            Average air temperature for the day (°C).
        min_air_temperature : float, optional
            Minimum air temperature for the day (°C).
        max_air_temperature : float, optional
            Maximum air temperature for the day (°C).

        Notes
        -----
        If the attribute ``use_heat_unit_temperature`` in CropData is False, both ``min_air_temperature`` and
        ``max_air_temperature`` are optional. Otherwise, they are used to determine heat unit accumulation rather than
        average air temperature.

        References
        ----------
        SWAT 5:1.1, 5:2.1.2

        """
        if self.use_heat_unit_temperature:
            self.maximum_heat_unit_temperature = HeatUnits._determine_maximum_heat_unit_temperature(
                max_air_temperature, self.maximum_temperature
            )
            self.minimum_heat_unit_temperature = HeatUnits._determine_minimum_heat_unit_temperature(
                min_air_temperature, self.data.minimum_temperature
            )
            self.heat_unit_temperature = (self.minimum_heat_unit_temperature + self.maximum_heat_unit_temperature) / 2

        if self.use_heat_unit_temperature or mean_air_temperature is None:
            use_temp = self.heat_unit_temperature
        else:
            use_temp = mean_air_temperature
        self.data.is_growing = self.data.minimum_temperature <= use_temp <= self.maximum_temperature
        self.accumulate_heat_units(mean_air_temperature)

    def accumulate_heat_units(self, air_temperature: float | None = None) -> None:
        """
        Add the day's heat unit value to the cumulative sum of heat unit values from previous days.

        Parameters
        ----------
        air_temperature : float
            The average air temperature for the day (Celsius).

        Notes
        -----
        The method for calculating the heat units depends on ``self.use_heat_unit_temperature`` and possibly
        ``self.heat_unit_temperature``. See documentation of ``self.assign_new_heat_units`` for details.

        """
        self.assign_current_heat_units(air_temperature)
        self.add_heat_units()

    def assign_current_heat_units(self, air_temperature: float | None = None) -> None:
        """
        Determine and save the day's "heat units".

        Parameters
        ----------
        air_temperature : float, optional
            The average air temperature during the day (°C) used to determine the heat units via
            ``self._determine_heat_unit_value``. If None or if ``self.use_heat_unit_temperature=True``, then
            ``self.heat_unit_temperature`` is used instead.

        """
        if self.use_heat_unit_temperature or (air_temperature is None):  # alternative method
            self.new_heat_units = self._determine_heat_unit_value(
                self.heat_unit_temperature, self.data.minimum_temperature
            )
        else:  # main method
            self.new_heat_units = self._determine_heat_unit_value(air_temperature, self.data.minimum_temperature)

    def add_heat_units(self) -> None:
        """
        Add newly acquired heat units to accumulated heat units.
        """
        self.data.accumulated_heat_units += self.new_heat_units

    @staticmethod
    def _determine_heat_unit_value(air_temperature: float, min_growing_temperature: float) -> float:
        """
        Calculates heat units as the zero-bounded difference between an air temperature and a crop's minimum
        growing temperature.

        Parameters
        ----------
        air_temperature : float
            The air temperature to be compared with min_temperature (Celsius).
        min_growing_temperature : float
            The minimum temperature below which a crop cannot grow (Celsius).

        Returns
        -------
        float
            The heat units for the day in degrees C, calculated by subtracting min_growing_temperature from
            ``air_temperature``.
            If the temperature difference is negative, 0 the result is 0.

        References
        ----------
        SWAT Reference 5:1.1
        """
        return max(air_temperature - min_growing_temperature, 0)

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
