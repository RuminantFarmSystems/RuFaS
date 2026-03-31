from numpy import sqrt
from datetime import date

from RUFAS.biophysical.animal.data_types.animal_enums import Breed
from RUFAS.input_manager import InputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.output_manager import OutputManager
from RUFAS.util import Utility

"""
The base change time and value in the net merit value.

References
----------
CDCB website

"""
BASE_CHANGE_LOOKUP_TABLE = {
    date.fromisoformat("2020-04-01"): 231,
    date.fromisoformat("2014-12-01"): 184,
    date.fromisoformat("2010-01-01"): 132,
    date.fromisoformat("2005-01-01"): 0,
}


"""The only breed currently supported in this module is Holsteins."""
SUPPORTED_BREED: str = "HO"


class AnimalGenetics:
    """
    Attributes
    ----------
    net_merit : dict[str, dict[str, dict[str, float]]], default {}
        Lookup table of Net Merit averages and standard deviations (lifetime USD), separated by breed and time.
    top_semen : dict[str, dict[str, float]], default {}
        Lookup table of Top Listing Semen estimated Predicted Transmitting Ability, separated by breed.
    year_month_of_first_net_merit_value: str
        The earliest net merit value available in year and month (YYYY-MM) format.
    year_month_of_last_net_merit_value: str
        The latest net merit value available in year and month (YYYY-MM) format.
    year_month_of_first_top_semen_value: str
        The earliest top semen value available in year and month (YYYY-MM) format.
    year_month_of_last_top_semen_value: str
        The latest top semen value available in year and month (YYYY-MM) format.

    """

    net_merit: dict[str, dict[str, dict[str, float]]] = {}
    top_semen: dict[str, dict[str, float]] = {}
    year_month_of_first_net_merit_value: str
    year_month_of_last_net_merit_value: str
    year_month_of_first_top_semen_value: str
    year_month_of_last_top_semen_value: str

    @classmethod
    def initialize_class_variables(cls) -> None:
        """This method initializes the class variables for net_merit and top_semen."""
        im = InputManager()
        net_merit_HO: dict[str, list[str | float]] = im.get_data("animal_net_merit")
        top_listing_semen_HO: dict[str, list[str | float]] = im.get_data("animal_top_listing_semen")

        cls.net_merit = {
            SUPPORTED_BREED: {
                net_merit_HO["year_month"][i]: {"average": net_merit_HO["average"][i], "std": net_merit_HO["std"][i]}
                for i in range(len(net_merit_HO["year_month"]))
            }
        }
        cls.net_merit = cls.net_merit_base_change(cls.net_merit)
        cls.net_merit = cls.net_merit_fill_gap(cls.net_merit)

        cls.year_month_of_first_net_merit_value = min(cls.net_merit[SUPPORTED_BREED].keys())
        cls.year_month_of_last_net_merit_value = max(cls.net_merit[SUPPORTED_BREED].keys())

        cls.top_semen = {
            SUPPORTED_BREED: {
                top_listing_semen_HO["year_month"][i]: top_listing_semen_HO["estimated_PTA"][i]
                for i in range(len(top_listing_semen_HO["year_month"]))
            }
        }

        cls.year_month_of_first_top_semen_value = min(cls.top_semen[SUPPORTED_BREED].keys())
        cls.year_month_of_last_top_semen_value = max(cls.top_semen[SUPPORTED_BREED].keys())

    @staticmethod
    def net_merit_base_change(
        original_net_merit: dict[str, dict[str, dict[str, float]]],
    ) -> dict[str, dict[str, dict[str, float]]]:
        """
        This function performs the base change for the net merit data.

        Parameters
        ----------
        original_net_merit: dict[str, dict[str, dict[str, float]]]
            The original net merit data, $USD.

        Returns
        -------
        dict[str, dict[str, dict[str, float]]]
            The net merit data after base change, $USD.

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
        total_adjustment_value = sum([BASE_CHANGE_LOOKUP_TABLE[i] for i in BASE_CHANGE_LOOKUP_TABLE.keys()])
        for breed in original_net_merit.keys():
            adjusted_net_merit[breed] = {}
            for year_month in original_net_merit[breed].keys():
                adjusted_net_merit[breed][year_month] = {}
                datetime_year_month = date.fromisoformat(year_month + "-01")
                increase = sum(
                    [
                        BASE_CHANGE_LOOKUP_TABLE[base_change_time]
                        for base_change_time in BASE_CHANGE_LOOKUP_TABLE.keys()
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
        original_net_merit: dict[str, dict[str, dict[str, float]]],
    ) -> dict[str, dict[str, dict[str, float]]]:
        """
        The input net merit data only has three entries per year, this function fills in the gap in between entries by
        using linear approximation.

        Parameters
        ----------
        original_net_merit: dict[str, dict[str, dict[str, float]]]
            The original net merit data, $USD.

        Returns
        -------
        dict[str, dict[str, dict[str, float]]]
            The net merit data after filling the gap in between entries, $USD.
        """
        expanded_net_merit: dict[str, dict[str, dict[str, float]]] = {}
        monthly_increase_lookup = {2005: 132 / 60, 2010: 184 / 60, 2015: 231 / 60, 2020: (360.731239 - 36.931108) / 48}

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

    @staticmethod
    def assign_net_merit_value_to_animals_entering_herd(birth_date: str, breed: Breed) -> float:
        """
        This function calculates the net merit value for animals entering the herd, either during initialization or
        for animals bought during the simulation.

        Parameters
        ----------
        birth_date: str
            The birthdate of the animal in the format "YYYY-MM-DD".
        breed: str
            The breed of the animal.

        Returns
        -------
        float
            The net merit value of the animal, $USD.

        Notes
        -----
        With the birthdate and the breed of the animal, this function first looks up the mean and standard deviation
        of the net merit value, then generates a random value from the distribution as the net merit value.
        """
        birth_year_month = birth_date[:7]
        birth_year_month = AnimalGenetics._clamp_birth_year_month_in_data_range(birth_year_month, is_for_net_merit=True)
        average = AnimalGenetics.net_merit[breed.name][birth_year_month]["average"]
        std = AnimalGenetics.net_merit[breed.name][birth_year_month]["std"]
        return Utility.generate_random_number(average, std)

    @staticmethod
    def assign_net_merit_value_to_newborn_calf(time: RufasTime, breed: Breed, dam_net_merit_value: float) -> float:
        """
        This function calculates the net merit value for the newborn calves.

        Parameters
        ----------
        time: RufasTime
            The RufasTime instance that contains the birthdate of the newborn calf.
            This function will be called on the day of birth for the newborn calf; therefore, the current date will be
            the birthdate of the calf.
        breed: str
            The breed of the newborn calf.
        dam_net_merit_value: float
            The net merit value of the dam (mother cow).

        Returns
        -------
        float
            The net merit value of the newborn calf, $USD.

        Notes
        -----
        With the birthdate and the breed of the animal, this function first looks up the top listing semen value.
        The mean for the net merit value of the newborn can then be calculated as the sum of the top listing semen
        value and the net merit value of the dam.
        The standard deviation is the square root of the Mendelian sampling variance, which is simply half of the
        population variance.
        """
        birth_year_month = str(time.current_calendar_year) + "-" + str(time.current_month).zfill(2)
        net_merit_birth_year_month = AnimalGenetics._clamp_birth_year_month_in_data_range(
            birth_year_month, is_for_net_merit=True
        )
        top_semen_birth_year_month = AnimalGenetics._clamp_birth_year_month_in_data_range(
            birth_year_month, is_for_net_merit=False
        )
        semen_predicted_transmitting_ability: float = AnimalGenetics.top_semen[breed.name][top_semen_birth_year_month]
        average_net_merit = semen_predicted_transmitting_ability + dam_net_merit_value
        variance = ((AnimalGenetics.net_merit[breed.name][net_merit_birth_year_month]["std"]) ** 2) / 2
        return Utility.generate_random_number(average_net_merit, sqrt(variance))

    @staticmethod
    def _clamp_birth_year_month_in_data_range(birth_year_month: str, is_for_net_merit: bool) -> str:
        """
        Checks if the birth month of an animal is available in either the net merit or top semen data, and clamps the
        month to the earliest or latest date if the date is not available.

        Parameters
        ----------
        birth_year_month : str
            The year and month of an animal's birth, in the format "YYYY-MM".
        is_for_net_merit : bool
            True if the birth month is being checked against the net merit data, False if it is being checked against
            the top semen data.

        Returns
        -------
        str
            The birth month of the animal, clamped between the earliest and latest dates available.

        """
        if is_for_net_merit:
            earliest_date = AnimalGenetics.year_month_of_first_net_merit_value
            latest_date = AnimalGenetics.year_month_of_last_net_merit_value
            data_type = "net merit"
        else:
            earliest_date = AnimalGenetics.year_month_of_first_top_semen_value
            latest_date = AnimalGenetics.year_month_of_last_top_semen_value
            data_type = "top semen"
        is_birth_date_in_range = earliest_date <= birth_year_month <= latest_date
        if not is_birth_date_in_range:
            clamped_birth_year_month = min(max(earliest_date, birth_year_month), latest_date)
            om = OutputManager()
            info_map = {
                "class": AnimalGenetics.__class__.__name__,
                "function": AnimalGenetics._clamp_birth_year_month_in_data_range.__name__,
                "birth_year_month": birth_year_month,
                "date_of_earliest_data": earliest_date,
                "date_of_latest_data": latest_date,
                "type_of_genetic_data": data_type,
            }
            om.add_error(
                "Animal birthdate out of range for animal genetics data",
                f"No {data_type} data for {birth_year_month}, using data from closest available date: "
                f"{clamped_birth_year_month}",
                info_map,
            )
            birth_year_month = clamped_birth_year_month
        return birth_year_month
