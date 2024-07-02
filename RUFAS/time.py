import datetime
from typing import Dict, List

from RUFAS.general_constants import GeneralConstants
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits
from RUFAS.util import Utility

om = OutputManager()


class Time:
    def __init__(self):
        """
        This object is responsible for creating and tracking time in the simulation.
        """
        self.im = InputManager()
        self.config_data: Dict[str, str | int | bool] = self.im.get_data("config")
        self.start_date: datetime = datetime.datetime.strptime(self.config_data["start_date"], "%Y:%j")
        self.end_date: datetime = datetime.datetime.strptime(self.config_data["end_date"], "%Y:%j")

        self.current_date: datetime = self.start_date
        self.simulation_length_days: int = (self.end_date - self.start_date).days
        self.simulation_length_years: int = self.end_date.year - self.start_date.year + 1

    def advance(self) -> None:
        """
        Advances the time in the simulation by 1 day.
        """
        self.current_date += datetime.timedelta(days=1)

    @property
    def years(self) -> List[List[int]]:
        """
        Returns a 2D array that consists all simulation days.

        Notes
        -----
        This method will be removed once the Weather class refactor is completed.
        """
        years: list[list[int]] = []

        for year in range(self.start_year_int, self.end_year_int + 1):
            year_length = (
                GeneralConstants.YEAR_LENGTH if not Utility.is_leap_year(year) else GeneralConstants.LEAP_YEAR_LENGTH
            )
            if year == self.start_year_int == self.end_year_int:
                days = [None for _ in range(1, self.start_day)]
                days += [_ for _ in range(self.start_day, self.end_day + 1)]
            elif year == self.start_year_int:
                days = [None for _ in range(1, self.start_day)]
                days += (_ for _ in range(self.start_day, year_length + 1))
            elif year == self.end_year_int:
                days = [_ for _ in range(1, self.end_day + 1)]
            else:
                days = [_ for _ in range(1, year_length + 1)]

            years.append(days)

        return years

    @property
    def start_year_int(self) -> int:
        """
        Returns the start calendar year in integer.

        Notes
        -----
        This method will be removed once the Weather class refactor is completed.
        """
        return self.start_date.year

    @property
    def start_day(self) -> int:
        """
        Returns the start Julian day in integer.

        Notes
        -----
        This method will be removed once the Weather class refactor is completed.
        """
        start_full_date: list[str] = self.config_data["start_date"].split(":")
        return int(start_full_date[1])

    @property
    def end_year_int(self) -> int:
        """
        Returns the end calendar year in integer.

        Notes
        -----
        This method will be removed once the Weather class refactor is completed.
        """
        end_full_date: list[str] = self.config_data["end_date"].split(":")
        return int(end_full_date[0])

    @property
    def end_day(self) -> int:
        """
        Returns the end Julian day in integer.

        Notes
        -----
        This method will be removed once the Weather class refactor is completed.
        """
        end_full_date: list[str] = self.config_data["end_date"].split(":")
        return int(end_full_date[1])

    @property
    def year_start_day(self) -> int:
        """
        Returns the first Julian day of the current year in integer.
        """
        return int(self.start_date.strftime("%j")) if self.current_date.year == self.start_date.year else 1

    @property
    def year_end_day(self) -> int:
        """
        Returns the last Julian day of the current year in integer.
        """
        days_in_year = (
            GeneralConstants.LEAP_YEAR_LENGTH
            if Utility.is_leap_year(self.current_date.year)
            else GeneralConstants.YEAR_LENGTH
        )
        return int(self.end_date.strftime("%j")) if self.current_date.year == self.end_date.year else days_in_year

    @property
    def current_julian_day(self) -> int:
        """
        Returns the current Julian day of the current year in integer.
        """
        return int(self.current_date.strftime("%j"))

    @property
    def current_month(self) -> int:
        """
        Returns the current month in integer.
        """
        return self.current_date.month

    @property
    def current_simulation_year(self) -> int:
        """
        Returns the current simulation year in integer.
        """
        return self.current_date.year - self.start_date.year + 1

    @property
    def current_calendar_year(self) -> int:
        """
        Returns the current calendar year in integer.
        """
        return self.current_date.year

    @property
    def simulation_day(self) -> int:
        """
        Returns the current simulation day in integer.
        """
        return (self.current_date - self.start_date).days

    def record_time(self) -> None:
        """
        Records the current day, simulated year, and calendar year of the simulation in the OutputManager.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.record_time.__name__,
            "prefix": "Time",
        }
        om.add_variable("day", self.current_julian_day, dict(info_map, **{"units": MeasurementUnits.SIMULATION_DAY}))
        om.add_variable(
            "year", self.current_simulation_year, dict(info_map, **{"units": MeasurementUnits.SIMULATION_YEAR})
        )
        om.add_variable(
            "calendar_year", self.current_calendar_year, dict(info_map, **{"units": MeasurementUnits.CALENDAR_YEAR})
        )
        om.add_variable(
            "simulation_day", self.simulation_day, dict(info_map, **{"units": MeasurementUnits.SIMULATION_DAY})
        )

    def convert_simulation_day_to_date(self, simulation_day: int) -> datetime.date:
        """
        Convert the simulation day to a date object that is relative to the start date of the simulation.

        Parameters
        ----------
        simulation_day : int
            The simulation day to convert to a date object.

        Returns
        -------
        datetime.date
            The date object that corresponds to the simulation day.
        """
        actual_date = self.start_date + datetime.timedelta(days=simulation_day - 1)
        return actual_date

    @staticmethod
    def convert_year_jday_date(year: int, day: int) -> datetime:
        """
        Converts the year and its day of the year to a datetime object

        Parameters
        ----------
        year: int
            Year of the date.
        day: int
            Number of days into the year.

        Returns
        -------
        datetime
            The date time object from the provided inputs

        """
        first_day_of_year = datetime.datetime(year, 1, 1)
        return first_day_of_year + datetime.timedelta(days=day - 1)

    def __str__(self) -> str:
        return (
            f"Year: {self.current_simulation_year}, Day: {self.current_julian_day}. "
            f"Simulation Day: {self.simulation_day}"
        )
