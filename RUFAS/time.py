from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
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
        self.index = 0

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

        self.leap_year_length = 366
        self.year_length = 365

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
                days = [_ for _ in range(1, year_length)]

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
