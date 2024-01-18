from typing import List
from RUFAS.output_manager import OutputManager
from RUFAS.config import Config

om = OutputManager()


class Time:
    def __init__(self, config: Config):
        """
        Description:
            This object is responsible for creating and tracking time in the simulation.
        Args:
            config: instance of the Config class containing information necessary
                to initialize time
        """

        calendar_year: int = config.start_year
        # number of years
        years: List[List[int]] = config.years

        self.start_year: int = calendar_year
        self.calendar_year: int = calendar_year
        self.years: List[List[int]] = config.years
        self.year: int = 1  # current year
        self.leap_year_length: int = config.leap_year_length
        self.year_length: int = config.year_length

        # finds the first non-null day of the first year
        for i in range(0, len(self.years[0])):
            if self.years[0][i] is None:
                continue
            else:
                self.day = self.years[0][i]
                break
        self.index = 0

    def to_str(self):
        """
        Description:
            Returns a string representation of the current time.
        Returns:
            str: a String representation of the current time in the simulation
                in the format "Year: <year> Day: <day>"
        """

        return "Year: {} Day: {}".format(self.year, self.day)

    def advance(self):
        """
        Description:
            Advances the time in the simulation by 1 day
            Automatically detects end of months and years
        """
        self.index += 1

        if self.end_year():
            self.day = 1
            self.year += 1
            self.calendar_year += 1
        else:
            self.day += 1

    def end_year(self):
        """
        Description:
            Returns a bool signifying the end of a year.
        Returns:
            bool: True if it is the end of a year, False otherwise
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
        om.add_variable("day", self.day, info_map)
        om.add_variable("year", self.year, info_map)
        om.add_variable("calendar_year", self.calendar_year, info_map)

    @property
    def is_last_day_of_simulation(self):
        """Checks whether the current day is the last day of the simulation.

        Returns:
            bool: True if the current day is the last day of the simulation, false otherwise

        """
        if self.year == len(self.years):
            return self.day == len(self.years[self.year - 1])

        return False
