import numpy as np

from RUFAS.input_manager import InputManager
from RUFAS.time import Time
from RUFAS.util import Utility

import datetime

base_change_lookup_table = {
    datetime.date.fromisoformat("2020-04-01"): 231,
    datetime.date.fromisoformat("2014-12-01"): 184,
    datetime.date.fromisoformat("2010-01-01"): 132,
    datetime.date.fromisoformat("2005-01-01"): 0,
}


class AnimalGenetics:
    def __init__(self) -> None:
        """Get the net merit and top listing semen data from InputManager, save them as class attributes, and perform
        base change and fill the gap for the net merit data."""
        im = InputManager()
        net_merit_HO: dict[str, list[str | float]] = im.get_data("animal_net_merit")
        top_listing_semen_HO: dict[str, list[str | float]] = im.get_data("animal_top_listing_semen")
        self.net_merit: dict[str, dict[str, dict[str, float]]] = {
            "HO": {
                net_merit_HO["year_month"][i]: {"average": net_merit_HO["average"][i], "std": net_merit_HO["std"][i]}
                for i in range(len(net_merit_HO["year_month"]))
            }
        }
        self.net_merit = self.net_merit_base_change(self.net_merit)
        self.net_merit = self.net_merit_fill_gap(self.net_merit)

        self.top_semen: dict[str, dict[str, float]] = {
            "HO": {
                top_listing_semen_HO["year_month"][i]: top_listing_semen_HO["estimated_PTA"][i]
                for i in range(len(top_listing_semen_HO["year_month"]))
            }
        }

    @staticmethod
    def net_merit_base_change(
        original_net_merit: dict[str, dict[str, dict[str, float]]]
    ) -> dict[str, dict[str, dict[str, float]]]:
        """
        This function performs the base change for the net merit data.

        Parameters
        ----------
        original_net_merit: dict[str, dict[str, dict[str, float]]]
            The original net merit data.

        Returns
        -------
        dict[str, dict[str, dict[str, float]]]
            The net merit data after base change.

        Notes
        -----
        The CDCB reevaluates and adjusts the net merit value to keep it within a reasonable range by changing the
        baseline every five years. Therefore, to realign the past data with the current values, we first change every
        value to match the oldest value, and shift all data back into the reasonable range.

        References
        ----------
        https://aipl.arsusda.gov/reference/base2010.htm

        https://aipl.arsusda.gov/reference/base2014.htm

        https://uscdcb.com/wp-content/uploads/2020/02/Norman-et-al-Genetic-Base-Change-April-2020-FINAL_new.pdf
        """
        adjusted_net_merit: dict[str, dict[str, dict[str, float]]] = {}
        total_adjustment_value = sum([base_change_lookup_table[i] for i in base_change_lookup_table.keys()])
        for breed in original_net_merit.keys():
            adjusted_net_merit[breed] = {}
            for year_month in original_net_merit[breed].keys():
                adjusted_net_merit[breed][year_month] = {}
                datetime_year_month = datetime.date.fromisoformat(year_month + "-01")
                increase = sum(
                    [
                        base_change_lookup_table[base_change_time]
                        for base_change_time in base_change_lookup_table.keys()
                        if datetime_year_month >= base_change_time
                    ]
                )
                original_value = original_net_merit[breed][year_month]["average"] + increase
                adjusted_value = original_value - total_adjustment_value
                adjusted_net_merit[breed][year_month]["average"] = adjusted_value
                adjusted_net_merit[breed][year_month]["std"] = original_net_merit[breed][year_month]["std"]
        return adjusted_net_merit

    @staticmethod
    def net_merit_fill_gap(
        original_net_merit: dict[str, dict[str, dict[str, float]]]
    ) -> dict[str, dict[str, dict[str, float]]]:
        """
        The input net merit data only has three entries per year, this function fills in the gap in between entries by
        using linear approximation.

        Parameters
        ----------
        original_net_merit: dict[str, dict[str, dict[str, float]]]
            The original net merit data.

        Returns
        -------
        dict[str, dict[str, dict[str, float]]]
            The net merit data after filling the gap in between entries.
        """
        expanded_net_merit: dict[str, dict[str, dict[str, float]]] = {}
        monthly_increase_lookup = {2005: 140 / 60, 2010: 253 / 60, 2015: 369 / 60, 2020: (538 - 396) / 24}

        for breed in original_net_merit.keys():
            expanded_net_merit[breed] = {}
            years = [int(year_month[:4]) for year_month in original_net_merit[breed].keys()]
            max_year = max(years)
            current_keys = list(original_net_merit[breed].keys())
            for year_month in current_keys:
                expanded_net_merit[breed][year_month] = {
                    "average": original_net_merit[breed][year_month]["average"],
                    "std": original_net_merit[breed][year_month]["std"],
                }
                year, month = int(year_month[:4]), int(year_month[5:])

                if month < 12:
                    month += 1
                else:
                    year += 1
                    month = 1
                next_year_month = str(year) + "-" + str(month).zfill(2)
                num_inc = 1
                while next_year_month not in current_keys:
                    average_monthly_increase_key = year - (year % 5)
                    average_monthly_increase = monthly_increase_lookup[average_monthly_increase_key]
                    expanded_net_merit[breed][next_year_month] = {
                        "average": original_net_merit[breed][year_month]["average"]
                        + num_inc * average_monthly_increase,
                        "std": original_net_merit[breed][year_month]["std"],
                    }
                    if month < 12:
                        month += 1
                    else:
                        year += 1
                        month = 1
                    next_year_month = str(year) + "-" + str(month).zfill(2)
                    num_inc += 1
                    if year > max_year:
                        break

            updated_keys = list(expanded_net_merit[breed].keys())
            updated_keys.sort()
            expanded_net_merit[breed] = {k: expanded_net_merit[breed][k] for k in updated_keys}
        return expanded_net_merit

    def assign_net_merit_value_to_animals_entering_herd(self, birth_date: str, breed: str) -> float:
        """
        This function calculates the net merit value for animals entering the herd, either during initialization or
        for animals bought during the simulation.

        Parameters
        ----------
        birth_date: str
            The birthdate of the animal in the format "%Y-%m-%d".
        breed: str
            The breed of the animal.

        Returns
        -------
        float
            The net merit value of the animal

        Notes
        -----
        With the birthdate and the breed of the animal, this function first looks up the mean and standard deviation
        of the net merit value, then generates a random value from the distribution as the net merit value.
        """
        birth_year_month = birth_date[:7]
        average = self.net_merit[breed][birth_year_month]["average"]
        std = self.net_merit[breed][birth_year_month]["std"]
        return Utility.generate_random_number(average, std)

    def assign_net_merit_value_to_newborn_calf(self, time: Time, breed: str, dam_net_merit_value: float) -> float:
        """
        This function calculates the net merit value for the newborn calves.

        Parameters
        ----------
        time: Time
            The Time instance that contains the birthdate of the newborn calf.
        breed: str
            The breed of the newborn calf.
        dam_net_merit_value: float
            The net merit value of the dam (mother cow).

        Returns
        -------
        float
            The net merit value of the newborn calf.

        Notes
        -----
        With the birthdate and the breed of the animal, this function first looks up the top listing semen value.
        The mean for the net merit value of the newborn can then be calculated as the sum of the top listing semen
        value and the net merit value of the dam.
        The standard deviation is the square root of the Mendelian sampling variance, which is simply half of the
        population variance.
        """
        birth_year_month = str(time.current_calendar_year) + "-" + str(time.current_month).zfill(2)
        semen_PTA: float = self.top_semen[breed][birth_year_month]
        average_net_merit = semen_PTA + dam_net_merit_value
        variance = ((self.net_merit[breed][birth_year_month]["std"]) ** 2) / 2
        return Utility.generate_random_number(average_net_merit, np.sqrt(variance))
