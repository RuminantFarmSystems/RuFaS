from typing import Optional

from RUFAS.biophysical.field.crop.crop_data import CropData


class HeatUnits:
    """
    A class that manages heat units for crop growth.

    Parameters
    ----------
    crop_data : Optional[CropData], optional
        An instance of `CropData` containing crop specifications and attributes. If not provided, a default
        `CropData` instance is initialized with default values.
    maximum_temperature : float, default 38
        Maximum temperature for plant growth (Celsius).
    use_heat_unit_temperature : bool, default False
        If alternative heat unit method is used.
    new_heat_units : Optional[float], default None
        Heat units accumulated on the current day (Celsius).
    minimum_heat_unit_temperature : Optional[float], default None
        Minimum temperature for heat unit calculations (Celsius).
    maximum_heat_unit_temperature : Optional[float], default None
        Maximum temperature for heat unit calculations (Celsius).
    heat_unit_temperature : Optional[float], default None
        Heat unit temperature for alternative method (Celsius).

    Attributes
    ----------
    data : CropData
        A reference to the `crop_data` object, used for accessing and updating crop-related data like
        temperature thresholds, accumulated heat units, and growth stages.
    maximum_temperature : float
        Maximum temperature for plant growth (Celsius).
    use_heat_unit_temperature : bool
        If alternative heat unit method is used.
    new_heat_units : Optional[float]
        Heat units accumulated on the current day (Celsius*).
    minimum_heat_unit_temperature : Optional[float]
        Minimum temperature for heat unit calculations (Celsius).
    maximum_heat_unit_temperature : Optional[float]
        Maximum temperature for heat unit calculations (Celsius).
    heat_unit_temperature : Optional[float]
        Heat unit temperature for alternative method (Celsius).

    Notes
    -----
    This module primarily follows the Heat Units section of the SWAT model (5:3.1)

    """

    def __init__(
        self,
        crop_data: Optional[CropData] = None,
        maximum_temperature: float = 38.0,
        use_heat_unit_temperature: bool = False,
        new_heat_units: Optional[float] = None,
        minimum_heat_unit_temperature: Optional[float] = None,
        maximum_heat_unit_temperature: Optional[float] = None,
        heat_unit_temperature: Optional[float] = None,
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

    def accumulate_heat_units(self, air_temperature: Optional[float] = None) -> None:
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

    def assign_new_heat_units(self, air_temperature: Optional[float] = None) -> None:
        """
        Assign new heat units based on whether the alternative accumulation method is to be used.

        Parameters
        ----------
        air_temperature : Optional[float], optional
            The average air temperature during the day (°C).

        """
        if self.use_heat_unit_temperature or (air_temperature is None):  # alternative method
            self.new_heat_units = self._determine_new_heat_units(
                self.heat_unit_temperature, self.data.minimum_temperature
            )
        else:  # main method
            self.new_heat_units = self._determine_new_heat_units(air_temperature, self.data.minimum_temperature)

    def add_heat_units(self) -> None:
        """
        Add newly acquired heat units to accumulated heat units.
        """
        self.data.accumulated_heat_units += self.new_heat_units

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
        return max(temperature - min_temperature, 0)

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
