from typing import Dict


def is_leap_year(year):
    """
    Description:
        Helper method determines if the given year is a leap year
    Args:
        year: an int of the year
    Returns:
        bool: True if the year is a leap year
    """
    if year % 400 == 0:
        return True
    elif year % 100 == 0:
        return False
    elif year % 4 == 0:
        return True
    else:
        return False


class Config:
    def __init__(self, data: Dict[str, int | bool | str]):
        """
        Description:
            Object containing configuration information of the simulation

        Args:
            data: dictionary containing information from the json file specified
                under "config"
        """

        # gets a start/end date in the format year:julian-day. That way the program
        # can start in the middle of the year
        self.start_full_date: list[str] = data["start_date"].split(":")
        self.end_full_date: list[str] = data["end_date"].split(":")
        self.start_year: int = int(self.start_full_date[0])
        self.end_year: int = int(self.end_full_date[0])
        self.start_day: int = int(self.start_full_date[1])
        self.end_day: int = int(self.end_full_date[1])

        # set seed attributes
        self.set_seed = data["set_seed"]
        self.seed = data["random_seed"]

        # TODO: remove conditional once all json files have simulate_animals field
        self.simulate_animals = (
            data["simulate_animals"] if "simulate_animals" in data else True
        )

        year_length = 365
        leap_year_length = 366

        self.w_start_year: int = self.start_year
        self.w_start_day: int = self.start_day
        self.w_end_year: int = self.end_year
        self.w_end_day: int = self.end_day

        self.years: list[list[int]] = []

        for year in range(self.start_year, self.end_year + 1):
            if year == self.start_year == self.end_year:
                days = [None for _ in range(1, self.start_day)]
                days += [_ for _ in range(self.start_day, self.end_day + 1)]
            elif year == self.start_year:
                days = [None for _ in range(1, self.start_day)]
                if is_leap_year(year):
                    days += (_ for _ in range(self.start_day, leap_year_length + 1))
                else:
                    days += (_ for _ in range(self.start_day, year_length + 1))
            elif year == self.end_year:
                days = [_ for _ in range(1, self.end_day + 1)]
            else:
                if is_leap_year(year):
                    days = [_ for _ in range(1, leap_year_length + 1)]
                else:
                    days = [_ for _ in range(1, year_length + 1)]

            self.years.append(days)

        self.leap_year_length = leap_year_length
        self.year_length = year_length

        self.sim_length = self.calc_sim_length()

    def calc_sim_length(self):
        """
        Description:
            Calculates and returns the length of the simulation in days.
        """
        sim_length = 0
        for i in range(len(self.years)):
            if i == 0:
                # check for leap year
                if is_leap_year(self.start_year):
                    sim_length += self.leap_year_length - self.start_day
                else:
                    sim_length += self.year_length - self.start_day
            else:
                sim_length += len(self.years[i])

        return sim_length + 1
