import numpy as np
import pandas as pd

from RUFAS.input_manager import InputManager
from RUFAS.time import Time
from RUFAS.util import Utility

import matplotlib.pyplot as plt
import datetime

base_change_lookup_table = {
    datetime.date.fromisoformat('2020-04-01'): 369,
    datetime.date.fromisoformat('2014-12-01'): 253,
    datetime.date.fromisoformat('2010-01-01'): 140,
    datetime.date.fromisoformat('2005-04-01'): 107,
    datetime.date.fromisoformat('2000-04-01'): 0
}


class AnimalGenetics:
    def __init__(self) -> None:
        im = InputManager()
        net_merit_HO: dict[str, list[float]] = im.get_data('animal_net_merit')
        top_listing_semen_HO: dict[str, list[str | float]] = im.get_data('animal_top_listing_semen')
        self.net_merit: dict[str, dict[str, dict[str, float]]] = {
            "HO": {
                net_merit_HO["year_month"][i]: {
                    "average": net_merit_HO["average"][i],
                    "std": net_merit_HO["std"][i]} for i in range(len(net_merit_HO["year_month"]))
            }
        }

        self.net_merit_base_change()
        self.net_merit_fill_gap()

        self.top_semen: dict[str, dict[str, str | float]] = {
            "HO": {
                top_listing_semen_HO["year_month"][i]: top_listing_semen_HO["estimated_PTA"][i]
                for i in range(len(top_listing_semen_HO["year_month"]))
            }
        }

        year_months = list(self.net_merit["HO"].keys())
        df_net_merit = pd.DataFrame(columns=["year_month", "average", "std"])
        for i in range(len(year_months)):
            year_month = year_months[i]
            df_net_merit.loc[i] = [year_month,
                                   self.net_merit["HO"][year_month]["average"],
                                   self.net_merit["HO"][year_month]["std"]]
        df_net_merit.to_csv("updated_net_merit_HO.csv", index=False)

    def net_merit_base_change(self) -> None:
        total_adjustment_value = sum([base_change_lookup_table[i] for i in base_change_lookup_table.keys()])
        for year_month in self.net_merit["HO"].keys():
            datetime_year_month = datetime.date.fromisoformat(year_month + '-01')
            increase = sum([base_change_lookup_table[base_change_time]
                            for base_change_time in base_change_lookup_table.keys()
                            if datetime_year_month >= base_change_time])
            original_value = self.net_merit["HO"][year_month]["average"] + increase
            adjusted_value = original_value - total_adjustment_value
            self.net_merit["HO"][year_month]["average"] = adjusted_value

    def net_merit_fill_gap(self) -> None:
        monthly_increase_lookup = {
            2005: 140 / 60,
            2010: 253 / 60,
            2015: 369 / 60,
            2020: (538 - 396) / 24
        }
        years = [int(year_month[:4]) for year_month in self.net_merit["HO"].keys()]
        min_year, max_year = min(years), max(years)
        current_keys = list(self.net_merit["HO"].keys())
        for year_month in current_keys:
            year = int(year_month[:4])
            month = int(year_month[5:])
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
                self.net_merit["HO"][next_year_month] = {
                    "average": self.net_merit["HO"][year_month]["average"] + num_inc * average_monthly_increase,
                    "std": self.net_merit["HO"][year_month]["std"]
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

        updated_keys = list(self.net_merit["HO"].keys())
        updated_keys.sort()
        self.net_merit["HO"] = {
            k: self.net_merit["HO"][k] for k in updated_keys
        }

    def plot_net_merit(self, filename: str, width: float, title: str) -> None:
        year_months = list(self.net_merit["HO"].keys())
        means = [self.net_merit["HO"][year_month]["average"] for year_month in self.net_merit["HO"].keys()]
        stds = [self.net_merit["HO"][year_month]["std"] for year_month in self.net_merit["HO"].keys()]

        plt.title(title)
        plt.figure(figsize=(width, 7))
        plt.errorbar(year_months, means, fmt='.', yerr=stds)
        plt.xticks(rotation=90)
        plt.savefig(filename)
        plt.close()

    def assign_net_merit_value_to_animals_entering_herd(self, birth_date: str, breed: str) -> float:
        birth_year_month = birth_date[:7]
        average = self.net_merit[breed][birth_year_month]["average"]
        std = self.net_merit[breed][birth_year_month]["std"]
        return Utility.generate_random_number(average, std)

    def assign_net_merit_value_to_newborn_calf(self, time: Time, breed: str, dam_net_merit_value: float) -> float:
        birth_year_month = str(time.current_calendar_year) + "-" + str(time.current_month).zfill(2)
        semen_PTA: float = self.top_semen[breed][birth_year_month]
        semen_net_merit = semen_PTA * 2
        average_net_merit = (semen_net_merit + dam_net_merit_value) / 2
        variance = ((self.net_merit[breed][birth_year_month]["std"]) ** 2) / 2
        return Utility.generate_random_number(average_net_merit, np.sqrt(variance))
