import datetime
from typing import Dict

from RUFAS.general_constants import GeneralConstants
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits

im = InputManager()
om = OutputManager()


class Time:
    def __init__(self):
        """
        This object is responsible for creating and tracking time in the simulation.
        """

        config_data: Dict[str, str | int | bool] = im.get_data("config")
        self.start_date: datetime = datetime.datetime.strptime(config_data["start_date"], '%Y:%j')
        self.end_date: datetime = datetime.datetime.strptime(config_data["end_date"], '%Y:%j')

        self.leap_year_length: int = GeneralConstants.LEAP_YEAR_LENGTH
        self.year_length: int = GeneralConstants.YEAR_LENGTH
        self.current_date: datetime = self.start_date
        self.simulation_length: int = (self.end_date - self.start_date).days
        self.simulation_day: int = 0

    def advance(self) -> None:
        """
        Advances the time in the simulation by 1 day and automatically detects end of years.
        """

        self.simulation_day += 1
        self.current_date += 1

    @property
    def current_julian_day(self) -> int:
        return int(self.current_date.strftime('%j'))

    @property
    def current_simulation_year(self) -> int:
        return self.current_date.year - self.start_date.year + 1

    def end_year(self) -> bool:
        """
        Determines if the current day is the last day of the year in the simulation.

        Returns
        -------
        bool
            True if the current day is the last day of the year, False otherwise.

        Notes
        -----
        This method compares the current day with the number of days in the current year.
        As soon as the current day is greater than the number of days in the year,
        the day is reset to 1 and the year is incremented by 1.
        """

        return self.current_date.month == 12 and self.current_date.day == 31

    def end_simulation(self) -> bool:
        """
        Description:
            Checks whether the simulation has ended
        Returns:
            bool: True if the simulation has ended, false otherwise
        """

        return self.current_date > self.end_date

    def record_time(self) -> None:
        """
        Records the current day, simulated year, and calendar year of the simulation in the OutputManager.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.record_time.__name__,
            "prefix": "Time",
        }
        om.add_variable("day", self.current_date.day,
                        dict(info_map, **{"units": MeasurementUnits.SIMULATION_DAY.value}))
        om.add_variable("year", self.current_simulation_year,
                        dict(info_map, **{"units": MeasurementUnits.SIMULATION_YEAR.value}))
        om.add_variable(
            "calendar_year", self.current_date.year, dict(info_map, **{"units": MeasurementUnits.CALENDAR_YEAR.value})
        )
        om.add_variable(
            "simulation_day", self.simulation_day, dict(info_map, **{"units": MeasurementUnits.SIMULATION_DAY.value})
        )

    @property
    def is_last_day_of_simulation(self) -> bool:
        """Checks whether the current day is the last day of the simulation.

        Returns:
            bool: True if the current day is the last day of the simulation, false otherwise

        """
        return self.current_date == self.end_date

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

    def __str__(self) -> str:
        return f"Year: {self.current_simulation_year}, Day: {self.current_julian_day}. " \
               f"Simulation Day: {self.simulation_day}"
