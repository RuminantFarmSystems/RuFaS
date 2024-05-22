import datetime

from RUFAS.general_constants import GeneralConstants
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits
from RUFAS.util import Utility

im = InputManager()
om = OutputManager()


class Time:
    def __init__(self):
        """
        This object is responsible for creating and tracking time in the simulation.
        """

        self._init_time_config()
        self.calendar_year: int = self.start_year_int
        self.year: int = 1  # current year
        self.simulation_length = self._calc_sim_length()

        # finds the first non-null day of the first year
        for i in range(0, len(self.years[0])):
            if self.years[0][i] is None:
                continue
            else:
                self.day = self.years[0][i]
                break

        self.simulation_day = 0

    def _init_time_config(self) -> None:
        """
        Initializes the time configuration for the instance by parsing the config data from InputManager pool.
        """
        config_data = im.get_data("config")
        self.start_full_date: list[str] = config_data["start_date"].split(":")
        self.end_full_date: list[str] = config_data["end_date"].split(":")
        self.start_year_int: int = int(self.start_full_date[0])
        self.end_year_int: int = int(self.end_full_date[0])
        self.start_day: int = int(self.start_full_date[1])
        self.end_day: int = int(self.end_full_date[1])

        self.leap_year_length = GeneralConstants.LEAP_YEAR_LENGTH
        self.year_length = GeneralConstants.YEAR_LENGTH

        self.years: list[list[int]] = []

        for year in range(self.start_year_int, self.end_year_int + 1):
            year_length = self.year_length if not Utility.is_leap_year(year) else self.leap_year_length
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

            self.years.append(days)

    def _calc_sim_length(self) -> int:
        """
        Calculates and returns the length of the simulation in days.

        Returns
        -------
        int
            The length of the simulation in days.
        """
        sim_length = 0
        for i in range(len(self.years)):
            if i == 0:
                if Utility.is_leap_year(self.start_year_int):
                    sim_length += self.leap_year_length - self.start_day
                else:
                    sim_length += self.year_length - self.start_day
            else:
                sim_length += len(self.years[i])

        return sim_length + 1

    def advance(self) -> None:
        """
        Advances the time in the simulation by 1 day and automatically detects end of years.
        """

        self.simulation_day += 1

        if self.end_year():
            self.day = 1
            self.year += 1
            self.calendar_year += 1
        else:
            self.day += 1

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

        return self.day > len(self.years[self.year - 1])

    def end_simulation(self):
        """
        Description:
            Checks whether the simulation has ended
        Returns:
            bool: True if the simulation has ended, false otherwise
        """
        # midyear end date adjusted
        if self.year > len(self.years):
            return True
        elif self.year == len(self.years):
            return self.day > len(self.years[self.year - 1])

        return False

    def record_time(self) -> None:
        """
        Records the current day, simulated year, and calendar year of the simulation in the OutputManager.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.record_time.__name__,
            "prefix": "Time",
        }
        om.add_variable("day", self.day, dict(info_map, **{"units": MeasurementUnits.SIMULATION_DAY}))
        om.add_variable("year", self.year, dict(info_map, **{"units": MeasurementUnits.SIMULATION_YEAR}))
        om.add_variable(
            "calendar_year", self.calendar_year, dict(info_map, **{"units": MeasurementUnits.CALENDAR_YEAR})
        )
        om.add_variable(
            "simulation_day", self.simulation_day, dict(info_map, **{"units": MeasurementUnits.SIMULATION_DAY})
        )

    @property
    def is_last_day_of_simulation(self):
        """Checks whether the current day is the last day of the simulation.

        Returns:
            bool: True if the current day is the last day of the simulation, false otherwise

        """
        if self.year == len(self.years):
            return self.day == len(self.years[self.year - 1])

        return False

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

        start_year = int(self.start_full_date[0])
        start_day_of_year = int(self.start_full_date[1])
        start_date = datetime.date(start_year, 1, 1) + datetime.timedelta(days=start_day_of_year - 1)
        actual_date = start_date + datetime.timedelta(days=simulation_day - 1)
        return actual_date

    def __str__(self) -> str:
        return f"Year: {self.year}, Day: {self.day}. Simulation Day: {self.simulation_day}"
