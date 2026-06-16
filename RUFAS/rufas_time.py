from datetime import datetime, timedelta
from typing import Dict

from RUFAS.general_constants import GeneralConstants
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits
from RUFAS.util import Utility


class RufasTime:
    """
    This object is responsible for creating and tracking time in the simulation.

    Parameters
    ----------
    start_date : datetime
        The start date of the simulation.
    end_date : datetime
        The end date of the simulation.
    current_date : datetime
        The current date in the simulation.

    Attributes
    ----------
    om : OutputManager
        The ``OutputManager`` instance.
    im : InputManager
        The ``InputManager`` instance.
    start_date : datetime
        The start date of the simulation.
    end_date : datetime
        The end date of the simulation.
    current_date : datetime
        The current date in the simulation.
    simulation_length_days : int
        The number of days in the simulation.
    simulation_length_years : int
        The number of years in the simulation.
    """

    def __init__(self, start_date: datetime = None, end_date: datetime = None, current_date: datetime = None) -> None:
        """Initializes the ``RufasTime`` object."""
        self.om = OutputManager()
        self.im = InputManager()

        config_data: Dict[str, str | int | bool] = {}
        if not start_date or not end_date:
            config_data = self.im.get_data("config")

        self.start_date: datetime = start_date or datetime.strptime(str(config_data["start_date"]), "%Y:%j")
        self.end_date: datetime = end_date or datetime.strptime(str(config_data["end_date"]), "%Y:%j")

        self.current_date: datetime = current_date or self.start_date
        self.simulation_length_days: int = (self.end_date - self.start_date).days + 1
        self.simulation_length_years: int = self.end_date.year - self.start_date.year + 1

    def advance(self) -> None:
        """Advances the time in the simulation by 1 day."""
        self.current_date += timedelta(days=1)

    @property
    def year_start_day(self) -> int:
        """
        Returns the first Julian day of the current year.

        Returns
        -------
        int
            The first Julian day of the current year.
        """
        return int(self.start_date.strftime("%j")) if self.current_date.year == self.start_date.year else 1

    @property
    def year_end_day(self) -> int:
        """
        Returns the last Julian day of the current year.

        Returns
        -------
        int
            The last Julian day of the current year.
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
        Returns the current Julian day of the current year.

        Returns
        -------
            The current Julian day of the current year.
        """
        return int(self.current_date.strftime("%j"))

    @property
    def current_month(self) -> int:
        """
        Returns the current month.

        Returns
        -------
        int
            The current month.
        """
        return self.current_date.month

    @property
    def current_simulation_year(self) -> int:
        """
        Returns the current simulation year.

        Returns
        -------
            The current simulation year.
        """
        return self.current_date.year - self.start_date.year + 1

    @property
    def current_calendar_year(self) -> int:
        """
        Returns the current calendar year.

        Returns
        -------
        int
            The current calendar year.
        """
        return self.current_date.year

    @property
    def simulation_day(self) -> int:
        """
        Returns the current simulation day.

        Returns
        -------
        int
            The current simulation day.
        """
        return (self.current_date - self.start_date).days

    def record_time(self) -> None:
        """Records the current day, simulated year, and calendar year of the simulation in the ``OutputManager``."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self.record_time.__name__,
            "prefix": "RufasTime",
        }
        self.om.add_variable("day", self.current_julian_day, dict(info_map, **{"units": MeasurementUnits.JULIAN_DAY}))
        self.om.add_variable(
            "year", self.current_simulation_year, dict(info_map, **{"units": MeasurementUnits.SIMULATION_YEAR})
        )
        self.om.add_variable(
            "calendar_year", self.current_calendar_year, dict(info_map, **{"units": MeasurementUnits.CALENDAR_YEAR})
        )
        self.om.add_variable(
            "simulation_day", self.simulation_day, dict(info_map, **{"units": MeasurementUnits.SIMULATION_DAY})
        )

    def convert_simulation_day_to_date(self, simulation_day: int) -> datetime:
        """
        Convert the simulation day to a ``datetime`` object that is relative to the start date of the simulation.

        Parameters
        ----------
        simulation_day : int
            The simulation day to convert to a ``datetime`` object.

        Returns
        -------
        datetime
            The ``datetime`` object that corresponds to the simulation day.
        """
        actual_date = self.start_date + timedelta(days=simulation_day - 1)
        return actual_date

    @staticmethod
    def convert_year_jday_to_date(year: int, day: int) -> datetime:
        """
        Converts the year and its day of the year to a ``datetime`` object.

        Parameters
        ----------
        year: int
            Year of the date.
        day: int
            Number of days into the year.

        Returns
        -------
        datetime
            The ``datetime`` object from the provided inputs.

        """
        first_day_of_year = datetime(year, 1, 1)
        return first_day_of_year + timedelta(days=day - 1)

    def convert_slice_to_simulation_day(self, slice_day: int) -> int:
        """
        Converts the slice day to a simulation day.

        Parameters
        ----------
        slice_day: int
            The slice day to convert to a simulation day.

        Returns
        -------
        int
            The simulation day that corresponds to the slice day.
        """
        if slice_day == 0:
            return 1
        if slice_day < 0:
            return self.simulation_length_days + slice_day
        return slice_day

    def __str__(self) -> str:
        return (
            f"Year: {self.current_simulation_year}, Day: {self.current_julian_day}. "
            f"Simulation Day: {self.simulation_day}"
        )
