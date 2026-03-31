import datetime
import math

import numpy as np

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits


class Weather:
    """
    The `Weather` class manages all weather data used to run a single simulation.

    Parameters
    ----------
    weather_file : dict[str, List[Any]]
        The weather dictionary read from the provided weather input source.

    Attributes
    ----------
    weather_data : dict[datetime, CurrentDayCondition]
        A dictionary that maps a date to the corresponding CurrentDayCondition.
    mean_annual_temperature : int
        Mean of mean daily temperatures over all the weather data used by the simulation (°C).

    """

    def __init__(self, weather_file: dict, time: RufasTime):
        """
        Initializes the `Weather` instance using user-supplied whether data and overall simulation parameters.

        Parameters
        ----------
        weather_file : dict
            All the weather data available to be used by the simulation.
        time : RufasTime
            The RufasTime instance containing time configuration information of the simulation.

        Notes
        -----
        Contains daily weather information stored in 2D lists. Data lists are in the format Data[year][julian_day].
        Allows daily information to be accessed by indexing to [time.year - 1][time.day - 1] (list indexing starts at 0,
        time starts at 1).

        """
        self.om = OutputManager()
        self.weather_data = {}

        self.check_adequate_weather_data(weather_file, time)

        start_time = time.start_date
        end_time = time.end_date

        self.cos: list[float] = []
        self.sin: list[float] = []
        self.means: list[float] = []
        self.phase_shift: float = 0.0
        self.intercept_mean_temp: float = 0.0
        self.amplitude: float = 0.0

        for i in range(len(weather_file["year"])):
            year = weather_file["year"][i]
            jday = weather_file["jday"][i]
            date_key = RufasTime.convert_year_jday_to_date(year, jday)

            # Only include dates within the simulation period to save on space
            if start_time <= date_key <= end_time:
                self.cos.append(math.cos(2 * math.pi / 365 * jday))
                self.sin.append(math.sin(2 * math.pi / 365 * jday))
                self.means.append(weather_file["avg"][i])
                conditions = CurrentDayConditions(
                    incoming_light=weather_file["Hday"][i],
                    min_air_temperature=weather_file["low"][i],
                    mean_air_temperature=weather_file["avg"][i],
                    max_air_temperature=weather_file["high"][i],
                    precipitation=weather_file["precip"][i],
                    irrigation=weather_file["irrigation"][i],
                )
                if date_key in self.weather_data.keys():
                    info_map = {
                        "class": self.__class__.__name__,
                        "function": "__init__",
                        "prefix": "Weather",
                    }
                    self.om.add_warning(
                        "Duplicate weather", f"duplicate weather data found for the date {date_key}", info_map
                    )
                self.weather_data[date_key] = conditions

        self.mean_annual_temperature = self._calculate_average_annual_temperature(weather_file["avg"])

        self.set_linest_temperature_factors()

        info_map = {
            "class": self.__class__.__name__,
            "function": "__init__",
            "prefix": "Weather",
        }
        self.om.add_variable(
            "average_annual_temperature",
            self.mean_annual_temperature,
            dict(info_map, **{"units": MeasurementUnits.DEGREES_CELSIUS}),
        )

    def set_linest_temperature_factors(self) -> None:
        """
        This function performs least-squares regression using cosine and sine components to model seasonal air
        temperature. This enables determination of the amplitude and phase shift (peak) of the sinusoidal curve of
        seasonal air temperature. First, sin and cos coefficients are generated for each Julian day of the simulation.
        The function then fits the model:

        T(d) = A*cos(d) + B*sin(d) + C

        where:
            - T(d) is the mean air temperature for day d in the simulation
            - A and B are coefficients
            - C is the intercept (mean)

        From the fitted model, the method calculates and stores the fitted intercept term representing average air
        temperature, amplitude of the modeled cos/sin function, and phase shift (peak temperature). These parameters are
        simulation-wide, i.e., only weather data utilized in the simulation is used.

        """
        mean_temperatures = np.array(self.means, dtype=float)
        cosine_components = np.array(self.cos, dtype=float)
        sine_components = np.array(self.sin, dtype=float)

        design_matrix = np.column_stack((cosine_components, sine_components, np.ones_like(mean_temperatures)))

        regression_coefficients, *_ = np.linalg.lstsq(design_matrix, mean_temperatures, rcond=None)

        cosine_coefficient, sine_coefficient, intercept_mean_temperature = regression_coefficients

        self.intercept_mean_temp = intercept_mean_temperature

        self.amplitude = math.sqrt(cosine_coefficient**2 + sine_coefficient**2)

        phase_angle_radians = math.atan2(sine_coefficient, cosine_coefficient)
        phase_shift_days = (phase_angle_radians / (2 * math.pi) * 365) + 365
        if phase_shift_days > 365:
            self.phase_shift = (phase_angle_radians / (2 * math.pi) * 365) - 365
        else:
            self.phase_shift = phase_shift_days

    def get_current_day_conditions(self, time: RufasTime, latitude: float | None = None) -> CurrentDayConditions:
        """
        Creates a CurrentDayConditions object containing all the weather conditions on the current day.

        Parameters
        ----------
        time: RufasTime
            RufasTime object containing the current time of the simulation.
        latitude : float | None, default None
            Latitude of the location which weather data is being collected for (degrees). If no latitude is provided,
            then the daylength will not be provided in the returned CurrentDayConditions instance.

        Returns
        -------
        CurrentDayConditions
            CurrentDayConditions instance including all the weather conditions of the specified date.

        Raises
        ------
        KeyError
            While attempting to collect weather conditions that are not contained in the Weather object.

        """
        if latitude:
            daylength = CurrentDayConditions.determine_daylength(
                time.current_julian_day, latitude, time.current_calendar_year
            )
        else:
            daylength = None
        try:
            self.weather_data[time.current_date].daylength = daylength
            self.weather_data[time.current_date].annual_mean_air_temperature = self.mean_annual_temperature
        except KeyError:
            raise KeyError(
                f"Attempted to get weather conditions for day: {time.current_julian_day},"
                f" year: {time.current_calendar_year}."
            )

        return self.weather_data[time.current_date]

    def get_conditions_series(
        self, time: RufasTime, starting_offset: int, ending_offset: int, latitude: float | None = None
    ) -> list[CurrentDayConditions]:
        """
        Generates a series of CurrentDayConditions.

        Parameters
        ----------
        time : RufasTime
            A RufasTime instance containing the current time information of the simulation.
        starting_offset : int
            Number of days before or after the given date to start the weather conditions series.
        ending_offset : int
            Number of days before or after the given date to end the weather conditions series.
        latitude : float | None, default None
            The latitude of the location that weather conditions are being collected for (degrees). If no latitude is
            provided, then no daylengths will be included in weather conditions returned.

        Returns
        -------
        list[CurrentDayConditions]
            Series of current day conditions in chronological order.

        """
        conditions_list = []

        for i in range(starting_offset, ending_offset + 1):
            date = time.current_date + datetime.timedelta(days=i)
            if latitude:
                daylength = CurrentDayConditions.determine_daylength(int(date.strftime("%j")), latitude, date.year)
            else:
                daylength = None
            self.weather_data[date].daylength = daylength
            self.weather_data[date].annual_mean_air_temperature = self.mean_annual_temperature
            conditions_list.append(self.weather_data[date])

        return conditions_list

    def record_weather(self, time: RufasTime) -> None:
        """
        Records the current weather conditions in the OutputManager.

        Parameters
        ----------
        time: RufasTime
            RufasTime object containing the current time of the simulation.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.record_weather.__name__,
            "prefix": "Weather",
        }
        current_weather = self.get_current_day_conditions(time)
        self.om.add_variable(
            "precipitation",
            current_weather.precipitation,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable(
            "rainfall", current_weather.rainfall, dict(info_map, **{"units": MeasurementUnits.MILLIMETERS})
        )
        self.om.add_variable(
            "snowfall", current_weather.snowfall, dict(info_map, **{"units": MeasurementUnits.MILLIMETERS})
        )
        self.om.add_variable(
            "maximum_temperature",
            current_weather.max_air_temperature,
            dict(info_map, **{"units": MeasurementUnits.DEGREES_CELSIUS}),
        )
        self.om.add_variable(
            "minimum_temperature",
            current_weather.min_air_temperature,
            dict(info_map, **{"units": MeasurementUnits.DEGREES_CELSIUS}),
        )
        self.om.add_variable(
            "average_temperature",
            current_weather.mean_air_temperature,
            dict(info_map, **{"units": MeasurementUnits.DEGREES_CELSIUS}),
        )
        self.om.add_variable(
            "radiation",
            current_weather.incoming_light,
            dict(info_map, **{"units": MeasurementUnits.MEGAJOULES_PER_SQUARE_METER}),
        )
        self.om.add_variable(
            "irrigation", current_weather.irrigation, dict(info_map, **{"units": MeasurementUnits.MILLIMETERS})
        )

    @staticmethod
    def _calculate_average_annual_temperature(
        daily_average_temperatures: list[float],
    ) -> float:
        """
        Calculates the average annual air temperature based on the daily average air temperatures.

        Parameters
        ----------
        daily_average_temperatures : list(float)
            List of daily average air temperatures in the passed to be run by the simulation (degrees C).

        Returns
        -------
        float
            The average annual air temperature (degrees C).

        Notes
        -----
        This method calculates the average annual air temperature by taking the average of all daily average air
        temperatures provided in the weather input file. Previous implementations calculated the average annual
        temperature for individual years, which led to the value fluctuating more than desired.

        This method is intended to approximate SWAT's method for calculating the average annual temperature. SWAT
        calculates average high and low temperatures for each month over every simulated year, then averages those
        values to get a single annual average air temperature for the entire simulation. The exact implementation for
        this can be found at in the SWAT source code file `readwgn.f
        <https://bitbucket.org/blacklandgrasslandmodels/swat_development/src/master/readwgn.f>`_

        """
        return np.mean(np.array(daily_average_temperatures))

    @staticmethod
    def check_adequate_weather_data(weather_file: dict, time: RufasTime) -> None:
        """
        Checks that there is enough weather data to cover the whole simulation time.

        Parameters
        ----------
        weather_file: dict
            File containing weather data.
        time: RufasTime
            The RufasTime instance containing time configuration information of the simulation.

        Returns
        -------
        None

        """
        om = OutputManager()
        years_list = weather_file["year"]
        days_list = weather_file["jday"]
        date_range = (time.end_date - time.start_date).days + 1

        for i in range(date_range):
            current_date = time.start_date + datetime.timedelta(days=i)
            current_date_year = current_date.year
            current_date_jday = current_date.timetuple().tm_yday

            if (current_date_jday in days_list) and (current_date_year in years_list):
                continue
            else:
                info_map = {
                    "class": "Weather",
                    "function": Weather.check_adequate_weather_data.__name__,
                }
                om.add_error(
                    "Inadequate weather data.",
                    "Not enough weather data provided to support the duration of simulation period",
                    info_map,
                )
                raise ValueError("Not enough weather data provided to support the duration of simulation period")
