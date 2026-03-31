import datetime
import enum
import os
import re
import shutil
from copy import deepcopy
from pathlib import Path
from random import random
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter

from RUFAS.general_constants import GeneralConstants


class Utility:
    @staticmethod
    def convert_list_of_dicts_to_dict_of_lists(list_of_dicts: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
        """
        Convert a list of dictionaries into a dictionary of lists.

        Parameters
        ----------
        list_of_dicts : List[Dict[str, Any]]
            A list of dictionaries with string keys and integer values.

        Returns
        -------
        Dict[str, List[Any]]
            A dictionary where keys are unique keys from input dictionaries,
            and values are lists of corresponding values from input dictionaries.
        """
        result: Dict[str, List[Any]] = {}

        for item in list_of_dicts:
            for key, value in item.items():
                if key not in result:
                    result[key] = []
                result[key].append(value)

        return result

    @staticmethod
    def convert_dict_of_lists_to_list_of_dicts(dict_of_lists: dict[str, list[Any]]) -> list[dict[str, Any]]:
        """
        Convert a dictionary of lists into a list of dictionaries.

        Parameters
        ----------
        dict_of_lists : dict[str, list[Any]]
            A dictionary where keys are unique keys and values are lists of corresponding values.

        Returns
        -------
        list[dict[str, Any]]
            A list of dictionaries with string keys and integer values.

        """
        return [dict(zip(dict_of_lists.keys(), values)) for values in zip(*dict_of_lists.values())]

    @staticmethod
    def flatten_keys_to_nested_structure(input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a dictionary with flat, dot-separated keys into a nested structure composed of
        dictionaries and lists based on the keys. Numeric segments in the keys indicate list indices,
        while non-numeric segments indicate dictionary keys.

        Parameters
        ----------
        input_dict : Dict[str, Any]
            A dictionary where the keys are strings that may include dots to signify hierarchical
            levels in the resulting nested structure. Numeric key segments result in list creations,
            and non-numeric segments result in dictionary creations.

        Returns
        -------
        Dict[str, Union[Dict, list]]
            A nested structure of dictionaries and lists derived by interpreting the flat dictionary keys.

        """
        nested_structure: Dict[str, Any] = {}
        for flat_key, value in input_dict.items():
            keys = flat_key.split(".")
            current: Dict[str, Any] | List[Any] = nested_structure
            for i, key in enumerate(keys[:-1]):
                next_key_is_digit = keys[i + 1].isdigit() if i + 1 < len(keys) else False

                if key.isdigit():
                    key = int(key)
                    while len(current) <= key:
                        current.append([] if next_key_is_digit else {})
                    current = current[key]
                else:
                    if isinstance(current, list):
                        current = current[-1]
                    if key not in current:
                        current[key] = [] if next_key_is_digit else {}
                    current = current[key]

            last_key = keys[-1]
            if last_key.isdigit():
                last_key = int(last_key)
                while len(current) <= last_key:
                    current.append(None)
                current[last_key] = value
            else:
                current[last_key] = value

        return nested_structure

    @staticmethod
    def find_max_index_from_keys(data: dict[str, Any]) -> int | None:
        """
        Extracts and returns the maximum index (n) from the keys of the given dictionary.
        Assumes keys follow the format `<prefix>_<number>.<suffix>` and number >= 0.

        Parameters
        ----------
        data: Dict[str, Any]
            The dictionary whose keys will be analyzed.

        Returns
        -------
        int | None
            The maximum index found among the keys, or None if no numeric index is found.
        """
        pattern = re.compile(r"_([0-9]+)\.")
        max_number = -1

        for key in data.keys():
            match = pattern.search(key)
            if match:
                number = int(match.group(1))
                if number > max_number:
                    max_number = number

        return max_number if max_number != -1 else None

    @staticmethod
    def expand_data_temporally(
        data_to_expand: dict[str, dict[str, list[Any]]],
        fill_value: Any = np.nan,
        use_fill_value_in_gaps: bool = True,
        use_fill_value_at_end: bool = True,
    ) -> dict[str, dict[str, list[Any]]]:
        """
        Pads and expands data based on the simulation day(s) it was recorded on, relative to when other data was
        recorded, so that values are present for all days in a certain range.

        Parameters
        ----------
        data_to_expand : dict[str, dict[str, list[Any]]]
            The data to be padded and expanded. The top level key is a variable name, and points to a dictionary that
            contains the keys "values" and optionally "info_maps".
        fill_value : Any, default numpy.nan
            Value that is used to pad the front of the data values, and optionally the values in between original values
            and after the last original value.
        use_fill_value_in_gaps : bool, default True
            If false, values between known data points are expanded with the last known value from the data set. If
            true, values between known data points are filled with `fill_value`.
        use_fill_value_at_end : bool, default True
            If false, values after last known data point are padded with the last known value from the data set. If
            true, values after the last known data point are filled with `fill_value`.

        Returns
        -------
        dict[str, dict[str, list[Any]]]
            The filled data, so that gaps in the data are filled in with the last known value or `fill_value`.

        Raises
        ------
        TypeError
            If a variable has no info maps.
        ValueError
            If there is no data to be filled.
            If the number of info maps does not match the number of values for a variable.
            If a value for "simulation_day" is not present in every info map.

        Notes
        -----
        This method assumes there will never be multiple values recorded for a single variable on a single simulation
        day.

        """
        if not data_to_expand:
            raise ValueError("Cannot fill empty dataset.")

        all_simulation_days = []
        for key, value in data_to_expand.items():
            info_maps = value.get("info_maps")
            if info_maps is None:
                raise TypeError(f"Variable '{key}' has no info maps.")
            if len(info_maps) != len(value["values"]):
                raise ValueError(f"Variable '{key}' does not have matching number of values and info maps.")
            if not all("simulation_day" in info_map.keys() for info_map in info_maps):
                raise ValueError(f"Variable '{key}' does not have simulation day value in every info map.")
            all_simulation_days += [info_map["simulation_day"] for info_map in info_maps]

        filtered_simulation_days = sorted(set(all_simulation_days))
        first_day = filtered_simulation_days[0]
        last_day = filtered_simulation_days[-1]

        expanded_data: dict[str, dict[str, list[Any]]] = {}
        for key, data in data_to_expand.items():
            expanded_variable_data: dict[str, list[Any]] = {"values": [], "info_maps": []}
            original_units = data["info_maps"][0]["units"]
            zipped_data = zip(data["values"], data["info_maps"])
            indexed_data = {data[1]["simulation_day"]: data for data in zipped_data}
            last_day_of_original_data = max(indexed_data.keys())
            last_value = (fill_value, {"simulation_day": 0, "units": original_units})
            for day in range(first_day, last_day_of_original_data + 1):
                if day in indexed_data.keys():
                    last_value = indexed_data[day] if not use_fill_value_in_gaps else (fill_value, indexed_data[day][1])
                    expanded_variable_data["values"].append(indexed_data[day][0])
                    expanded_variable_data["info_maps"].append(indexed_data[day][1])
                    expanded_variable_data["info_maps"][-1]["simulation_day"] = day
                else:
                    expanded_variable_data["values"].append(last_value[0])
                    expanded_variable_data["info_maps"].append(last_value[1].copy())
                    expanded_variable_data["info_maps"][-1]["simulation_day"] = day

            tail_fill_value = indexed_data[last_day_of_original_data][0] if not use_fill_value_at_end else fill_value
            for day in range(last_day_of_original_data + 1, last_day + 1):
                expanded_variable_data["values"].append(tail_fill_value)
                expanded_variable_data["info_maps"].append({"simulation_day": day, "units": original_units})

            expanded_data[key] = expanded_variable_data

        return expanded_data

    @staticmethod
    def deep_merge(target: Dict[Any, Any], updates: Dict[Any, Any]) -> None:
        """
        Recursively merges 'updates' into 'target'. Supports deep merging for dictionaries and lists, including lists
        that contain dictionaries and dictionaries that contain lists.

        Parameters
        ----------
        target : Dict[Any, Any]
            The primary dictionary to be updated.
        updates : Dict[Any, Any]
            The dictionary containing updates to be merged into target.
        """
        for key, value in updates.items():
            if key in target:
                if isinstance(value, dict) and isinstance(target[key], dict):
                    Utility.deep_merge(target[key], value)
                elif isinstance(value, list) and isinstance(target[key], list):
                    if len(target[key]) < len(value):
                        target[key].extend([None] * (len(value) - len(target[key])))

                    for i, item in enumerate(value):
                        if i < len(target[key]):
                            if isinstance(item, dict) and isinstance(target[key][i], dict):
                                Utility.deep_merge(target[key][i], item)
                            else:
                                target[key][i] = item
                        else:
                            target[key].append(item)
                else:
                    target[key] = value
            else:
                target[key] = value

    @staticmethod
    def calc_average(num_values: int, cur_avg: float, new_value: float) -> Tuple[int, float]:
        """
        Calculate the new average given the number of values,
        the current average, and the new value.

        Parameters
        ----------
        num_values: number of values for the current average
        cur_avg: the current average value
        new_value: the new value to be averaged

        Returns
        -------
        new_num_values: the new number of values for the new average
        new_avg: the new average value calculated

        """
        new_num_values = num_values + 1
        new_avg = (cur_avg * num_values + new_value) / new_num_values

        return new_num_values, new_avg

    @staticmethod
    def remove_items_from_list_by_indices(data: List[Any], indices_to_remove: List[int]) -> None:
        """
        Remove items from a list given a list of indices.
        The operation is done in-place.

        Parameters
        ----------
        data: List[Any] a list of items
            The list to remove items from
        indices_to_remove : List[Any]
            The list that contains indices of the items to be removed

        Returns
        -------
        None

        """

        # Sort and reverse the index list before removing items to make sure items are removed from the end of the list
        # to prevent the shifting of indices from affecting later removals.
        for idx in sorted(indices_to_remove, reverse=True):
            del data[idx]

    @staticmethod
    def percent_calculator(denominator: float) -> Callable[[float], float]:
        """
        Return a percent calculator closure that already stores the value of the given denominator.

        Parameters
        ----------
        denominator: the denominator to

        Returns
        -------
        A closure function that already stores the denominator internally
        so the user only needs to pass in the numerator.

        """

        def calc(numerator: float) -> float:
            return numerator * 100 / denominator

        return calc

    @classmethod
    def make_serializable(cls, obj: object, max_depth: int = 3) -> object:
        """Converts the given object into a serializable object.

        Parameters
        ----------
        obj
            The object to be serialized.
        max_depth : int, optional
            The maximum depth of recursion.

        Returns
        -------
        A serializable object.

        """
        return cls._make_serializable(obj, depth=0, max_depth=max_depth)

    @classmethod
    def _make_serializable(cls, obj: object, depth: int, max_depth: int) -> object:
        """Makes the given object serializable.

        The object can be a primitive type, a list, a tuple, a set, a dictionary,
        or an instance of a custom class.

        A recursive algorithm is used to traverse the object and convert it into
        a serializable object. The maximum depth of recursion is specified by the
        parameter max_depth.

        Parameters
        ----------
        obj : object
            The object to be serialized.
        depth : int
            The current depth of recursion.
        max_depth : int
            The maximum depth of recursion.

        Returns
        -------
        object
            A serializable object.

        """
        # If the object is a primitive type, return it directly
        if isinstance(obj, (int, float, str, bool, type(None))):
            return obj

        if isinstance(obj, enum.Enum):
            return obj.value

        if depth == max_depth:
            return cls._get_str(obj)

        # If the object is a list, serialize each element recursively
        if isinstance(obj, list):
            return [cls._make_serializable(elem, depth + 1, max_depth) for elem in obj]

        # If the object is a tuple, serialize each element recursively
        if isinstance(obj, tuple):
            return tuple([cls._make_serializable(elem, depth + 1, max_depth) for elem in obj])

        # If the object is a set, serialize each element recursively
        # Note: sets are not serializable by default, so we convert them to lists
        if isinstance(obj, set):
            return [cls._make_serializable(elem, depth + 1, max_depth) for elem in obj]

        # If the object is a dictionary, serialize each key-value pair recursively
        # Note: dictionary keys must be strings
        if isinstance(obj, dict):
            return {
                str(cls._make_serializable(key, depth, max_depth)): cls._make_serializable(value, depth, max_depth)
                for key, value in obj.items()
            }

        # If the object is a custom class, serialize its __dict__ attribute
        if hasattr(obj, "__dict__"):
            return cls._make_serializable(obj.__dict__, depth, max_depth)

        # When none of the above conditions are met, return a string representation of the object.
        return cls._get_str(obj)

    @classmethod
    def _get_str(cls, obj: object) -> str:
        """Returns a string representation of the given object.

        Parameters
        ----------
        obj : object
            The object to be converted to a string.

        Returns
        -------
        str
            A string representation of the given object.

        Notes
        -----
        If the object has a custom __str__ method, then that method will be used.
        Otherwise, a variant of the default __str__ method will be used.

        Normally, the default __str__ method returns a string of the format:
        `<module>.<class> object at <memory address>`.
        Here, we want to simplify that string to the format:
        `<class> object at <memory address>`.

        This turns out to be saving quite a bit of space when serializing objects.

        """
        if obj.__class__.__str__ != object.__str__:
            return str(obj)

        class_name = obj.__class__.__name__
        memory_address = hex(id(obj))
        return f"{class_name} object at {memory_address}"

    @classmethod
    def empty_dir(cls, dir_path: Path, keep: Optional[List[str]] = None) -> None:
        """Empties the given directory, except for the files or subdirectories in the keep list.

        Parameters
        ----------
        dir_path : Path
            The path to the directory to be emptied.
        keep : List, optional
            A list of file or subdirectory names to be kept.

        Returns
        -------
        None

        """
        if keep is None:
            keep = []

        for file in dir_path.iterdir():
            if file.name not in keep:
                if file.is_file():
                    file.unlink()
                elif file.is_dir():
                    shutil.rmtree(file)

    @staticmethod
    def get_timestamp(include_millis: bool = False) -> str:
        """
        Produces the current system time as a timestamp string.

        Parameters
        ----------
        include_millis : bool
            If True, adds milliseconds to the timestamp.

        Returns
        -------
        str
            The current time's timestamp string.

        Example
        --------
        >>> Utility.get_timestamp(include_millis=True)
        28-Jun-2023_Wed_15-48-21.406585
        >>> Utility.get_timestamp(include_millis=False)
        28-Jun-2023_Wed_15-48-21
        """

        base_timestamp_str: str = "%d-%b-%Y_%a_%H-%M-%S"
        timestamp_format_string: str = f"{base_timestamp_str}.%f" if include_millis else base_timestamp_str
        return datetime.datetime.now().strftime(timestamp_format_string)

    @staticmethod
    def filter_dictionary(
        dict_to_filter: Dict[str, Any], filter_patterns: List[str], filter_by_exclusion: bool
    ) -> Dict[Any, Any]:
        """
        Returns a filtered dictionary based on either inclusion or exclusion.

        Parameters
        ----------
        dict_to_filter : Dict[str, Any]
            The dictionary to be filtered.
        filter_patterns : List[str]
            A list of patterns by which to filter the dictionary.
        filter_by_exclusion : bool
            A flag indicating whether the dictionary should be filtered by exclusion
            or inclusion.

        Returns
        -------
        Dict[str, Any]
            The filtered dictionary.
        """
        if filter_by_exclusion:
            return {
                key: dict_to_filter[key]
                for key in dict_to_filter.keys()
                if not any(re.search(pattern, key) for pattern in filter_patterns)
            }
        return {
            key: dict_to_filter[key]
            for key in dict_to_filter.keys()
            if any(re.search(pattern, key) for pattern in filter_patterns)
        }

    @staticmethod
    def remove_special_chars(input_string: str | list[str]) -> str:
        """Function to remove special characters from a string.

        Parameters
        ----------
        input_string : str
            The string from which the special characters should be removed.

        Returns
        -------
        str
            The input string with the special characters filtered out.
        """
        chars_to_remove = ["<", ">", ":", "/", '"', "|", "\\", "?", "*", "."]

        filtered_string = "".join(char for char in input_string if char not in chars_to_remove)

        return filtered_string

    @staticmethod
    def is_leap_year(year: int) -> bool:
        """
        Helper method determines if the given year is a leap year

        Parameters
        ----------
        year: int
            The year.

        Returns
        -------
        bool
            True if the year is a leap year, otherwise False.
        """
        if year % 400 == 0:
            return True
        elif year % 100 == 0:
            return False
        elif year % 4 == 0:
            return True
        else:
            return False

    @staticmethod
    def generate_time_series(date: datetime.date, starting_offset: int, ending_offset: int) -> list[datetime.date]:
        """
        Generates a list of dates based on a given date and when the dates should start and end relative to the given
        date.

        Parameters
        ----------
        date : datetime.date
            Date around which the time series will be generated.
        starting_offset : int
            Number of days before or after the given date to start the time series.
        ending_offset : int
            Number of days before or after the given date to end the time series.

        Raises
        ------
        ValueError
            If the starting_offset is greater than the ending_offset.

        Examples
        --------
        >>> Utility.generate_time_series(datetime.date(2024, 6, 1), 0, 0)
        [datetime.date(2024, 6, 1)]
        >>> Utility.generate_time_series(datetime.date(2024, 6, 1), -2, 0)
        [datetime.date(2024, 5, 30), datetime.date(2024, 5, 31), datetime.date(2024, 6, 1)]
        >>> Utility.generate_time_series(datetime.date(2024, 6, 1), -2, -2)
        [datetime.date(2024, 5, 30)]
        >>> Utility.generate_time_series(datetime.date(2024, 6, 1), 0, 2)
        [datetime.date(2024, 6, 1), datetime.date(2024, 6, 2), datetime.date(2024, 6, 3)]
        >>> Utility.generate_time_series(datetime.date(2024, 6, 1), -1, 1)
        [datetime.date(2024, 5, 31), datetime.date(2024, 6, 1), datetime.date(2024, 6, 2)]
        >>> Utility.generate_time_series(datetime.date(2024, 6, 1), 3, 5)
        [datetime.date(2024, 6, 4), datetime.date(2024, 6, 5), datetime.date(2024, 6, 6)]

        """
        if starting_offset > ending_offset:
            raise ValueError(f"Starting offset ({starting_offset=}) is greater than ending offset ({ending_offset=}).")

        time_series = [date + datetime.timedelta(day) for day in range(starting_offset, ending_offset + 1)]

        return time_series

    @staticmethod
    def convert_celsius_to_kelvin(temperature: float) -> float:
        """Converts a temperature in degrees Celsius to degrees Kelvin."""
        return temperature + GeneralConstants.CELSIUS_TO_KELVIN

    @staticmethod
    def convert_ordinal_date_to_month_date(year: int, day: int) -> datetime.date:
        """Generates a datetime.date based on a year and ordinal day."""
        maximum_day = (
            GeneralConstants.YEAR_LENGTH if not Utility.is_leap_year(year) else GeneralConstants.LEAP_YEAR_LENGTH
        )
        if not 1 <= day <= maximum_day:
            raise ValueError(f"Invalid day: {day} of year {year} must be between 1 and {maximum_day}.")
        return datetime.date(year, 1, 1) + datetime.timedelta(days=day - 1)

    @staticmethod
    def generate_random_number(mean: float, std_dev: float) -> float:
        """Generates a normally distributed random number using the provided mean and standard deviation."""
        return np.random.normal(mean, std_dev)

    @staticmethod
    def flatten_dictionary(
        input_dictionary: dict[str, Any], parent_key: str = "", separator: str = "."
    ) -> dict[str, Any]:
        """
        Flatten a nested dictionary to a single level of depth by joining the keys with "."
        """
        items: list[tuple[str, Any]] = []
        for key, value in input_dictionary.items():
            new_key = parent_key + separator + key if parent_key else key
            if isinstance(value, dict) and value:
                items.extend(Utility.flatten_dictionary(value, new_key, separator=separator).items())
            elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                for i in range(len(value)):
                    items.extend(Utility.flatten_dictionary(value[i], new_key + f"_{i}", separator=separator).items())
            else:
                items.append((new_key, value))
        return dict(items)

    @staticmethod
    def combine_saved_input_csv(
        saved_csv_working_folder: Path, output_csv_path: Path, import_csv_path: Path | None
    ) -> None:
        """
        Merge multiple saved input data CSVs files into one single CSV file for a direct side-by-side comparison.
        """
        result_df = pd.DataFrame(columns=["property_group", "variable_name"])

        if import_csv_path and not import_csv_path == Path(""):
            current_df = pd.read_csv(import_csv_path, index_col=False)
            result_df = current_df.merge(result_df, how="outer", on=["property_group", "variable_name"])

        saved_csv_list = [file for file in os.listdir(saved_csv_working_folder) if file.endswith(".csv")]
        for csv_file in saved_csv_list:
            csv_file_path = saved_csv_working_folder / csv_file
            current_df = pd.read_csv(csv_file_path, index_col=False)

            data_prefix = [col for col in list(current_df.columns) if col not in ["property_group", "variable_name"]][0]

            if data_prefix in list(result_df.columns) or any(
                data_prefix in prefix for prefix in list(result_df.columns)
            ):
                same_prefix_columns: list[str] = [prefix for prefix in list(result_df.columns) if data_prefix in prefix]
                if len(same_prefix_columns) == 1:
                    result_df.rename(columns={same_prefix_columns[0]: same_prefix_columns[0] + "_1"}, inplace=True)
                    current_df.rename(columns={data_prefix: data_prefix + "_2"}, inplace=True)
                else:
                    suffix_numbers = [column_name.split(f"{data_prefix}_")[1] for column_name in same_prefix_columns]
                    current_df.rename(
                        columns={data_prefix: f"{data_prefix}_{int(max(suffix_numbers)) + 1}"}, inplace=True
                    )
            result_df = current_df.merge(result_df, how="outer", on=["property_group", "variable_name"])
        output_csv_path = output_csv_path / "saved_input_data.csv"
        result_df.to_csv(output_csv_path, index=False)

        shutil.rmtree(saved_csv_working_folder)

    @staticmethod
    def convert_list_to_dict_by_key(list_of_dicts: List[Dict[str, Any]], id_key: str) -> Dict[Any, Dict[str, Any]]:
        """
        Convert a list of dictionaries into a dictionary keyed by a specified identifier,
        where each value is the original dictionary minus the identifier key.

        Parameters
        ----------
        list_of_dicts : List[Dict[str, Any]]
            A list of dictionaries, each containing a unique identifier and other data.
        id_key : str
            The key in each dictionary to use as the unique identifier.

        Returns
        -------
        Dict[Any, Dict[str, Any]]
            A dictionary where each key is the unique identifier from the list and each
            value is the corresponding dictionary minus the identifier key.

        Notes
        -----
        The use of dict_.pop('ID') mutates the original dictionaries in list_of_dicts by removing their 'ID' keys.
        If you need to keep the original list and dictionaries intact, make a copy before calling this function.

        Example
        -------
        Given a list of dictionaries like this:
        [
            {"ID": 1, "value": 2, "other_keys": "other values"},
            {"ID": 3, "value": 4, "other_keys": "other values"}
        ]
        And using 'ID' as the id_key:

        convert_list_to_dict_by_key(list_of_dicts, 'ID')

        Would return:
        {
            1: {"value": 2, "other_keys": "other values"},
            3: {"value": 4, "other_keys": "other values"}
        }
        """
        result = {}
        for dict_ in deepcopy(list_of_dicts):
            if id_key in dict_:
                id_value = dict_.pop(id_key)
                result[id_value] = dict_
            else:
                raise KeyError(f"Key '{id_key}' not found in dictionary.")

        return result

    @staticmethod
    def elongate_list(list_to_elongate: list[Any], reference_list_length: int) -> list[Any]:
        """
        Takes a list and lengthens it to match the length of the reference list, if the original length was 1.

        Parameters
        ----------
        list_to_elongate : list[Any]
            List to be extended if its length is 1.
        reference_list_length : int
            Length of that the list should be extended to, if it its original length is 1.

        Returns
        -------
        list[Any]
            The elongated list.

        Notes
        -----
        In the context of Schedule-descendant classes, the reference list length will always be the length of the years
        list.

        """
        if len(list_to_elongate) != 1:
            return list_to_elongate
        elongated_list = list_to_elongate * reference_list_length
        return elongated_list

    @staticmethod
    def determine_if_all_non_negative_values(values: list[int | float]) -> bool:
        """
        Checks that all values in a list are >= 0.

        Parameters
        ----------
        values : List[Any]
            List of values to be checked.

        Returns
        -------
        bool
            True if all values are >= 0, False otherwise.

        """
        return all(value >= 0 for value in values)

    @staticmethod
    def validate_fractions(fractions: List[float]) -> bool:
        """
        Checks that all fractions passed are valid.

        Parameters
        ----------
        fractions : List[float]
            List of fractions to be valid

        Returns
        -------
        bool
            True if all fractions passed are valid, False otherwise.

        Notes
        -----
        A fraction is valid if it is in the range[0.0, 1.0]

        """
        return all(0.0 <= fraction <= 1.0 for fraction in fractions)

    @staticmethod
    def round_numeric_values_in_dict(data: dict[str, any], significant_digits: int) -> dict[str, Any]:
        """
        Rounds all numeric values in a dictionary to the specified number of significant digits.

        Parameters
        ----------
        data : dict[str, any]
            The dictionary containing numeric values to be rounded.
        significant_digits : int
            The number of significant digits to round the numeric values to.

        Returns
        -------
        dict[str, any]
            The dictionary with numeric values rounded to the specified number of significant digits.

        Notes
        -----
        Some specific behavior of the round() function used by this method:

        If significant_digits is None or 0, floats are converted to ints.
        round(12.7) -> 13 (int)
        round(12.3) -> 12 (int)
        round(-12.7) -> -13 (int)
        round(12.5) -> 12 (int) - If rounded number is 5, Python rounds to the nearest even number.
        round(11.5) -> 12 (int) - Because of this rule, both 11.5 and 12.5 round to 12.

        If significant_digits is less than 0, it rounds to the nearest multiple of 10, 100, 1000, etc.
        round(1234, -2) -> 1200 (rounds to the nearest multiple of 100)
        round(1234, -3) -> 1000 (rounds to the nearest multiple of 1000)
        round(-1234, -1) -> -1230 (rounds to the nearest multiple of 10)

        If significant_digits is 0, it rounds to the nearest integer and converts it to a float.
        round(12.7, 0) -> 13.0 (float)
        round(-12.3, 0) -> -12.0 (float)
        """
        return {
            key: (
                [round(x, significant_digits) for x in value]
                if isinstance(value, list) and all(isinstance(x, (float, int)) for x in value)
                else value
            )
            for key, value in data.items()
        }

    @staticmethod
    def compare_randomized_rate_less_than(reference_rate: float) -> bool:
        """
        Compare a random rate to a reference rate to determine if an event occurs.

        Parameters
        ----------
        reference_rate : float
            Reference rate for comparison.

        Returns
        -------
        bool
            True if the randomized rate is less than the reference rate, False otherwise.
        """

        return random() < reference_rate

    @staticmethod
    def validate_date_format(date_format: str) -> bool:
        """
        Checks if date_format is a valid Python datetime format for both strftime() and strptime().

        Parameters
        ----------
        date_format : str
            The date format to be validated.

        Returns
        -------
        bool

        """
        test_date = datetime.datetime(2020, 12, 31, 00, 00, 00, 00)
        try:
            test_str = test_date.strftime(date_format)
            _ = datetime.datetime.strptime(test_str, date_format)
            return False if test_str == date_format else True
        except Exception:
            return False

    @staticmethod
    def get_date_formatter(date_format: str | None) -> DateFormatter:
        """
        Get a `matplotlib.dates.DateFormatter` instance for the requested date format.

        Parameters
        ----------
        date_format : str
            The format requested by the user. Common date formats are:
            - "%j/%Y": Formats dates as "day_of_year/year" (e.g., "123/2024").
            - "%d/%m/%Y": Formats dates as "day/month/year" (e.g., "23/12/2024").
            - "%m/%d/%Y": Formats dates as "month/day/year" (e.g., "12/23/2024").
            - "%b/%d/%Y": Formats dates as "month_abbreviation/day/year" (e.g., "Dec/23/2024").
            - "%B/%d/%Y": Formats dates as "month_string/day/year" (e.g., "December/23/2024").
            - "%m/%d/%y": Formats dates as "month/day/year_without_century" (e.g., "12/23/24").
            - "%m %d %Y": Formats dates as "month day year" (e.g., "12 23 2024").
            - "%m-%d-%Y": Formats dates as "month-day-year" (e.g., "12-23-2024").

        Returns
        -------
        matplotlib.dates.DateFormatter
            A `DateFormatter` instance for the specified format.

        Notes
        -----
        If the date_format is None or invalid, the default format "%d/%m/%Y" will be used instead.

        """

        if date_format is None or not Utility.validate_date_format(date_format):
            return DateFormatter("%d/%m/%Y")

        return DateFormatter(date_format)


class Aggregator:
    @staticmethod
    def average(data: list[float]) -> float:
        """
        Calculates the average of a list of numbers.

        Parameters
        ----------
        data : list[float]
            A list of numbers whose average is to be calculated.

        Returns
        -------
        float
            The average of the input numbers.
        """
        return sum(data) / len(data) if data else 0

    @staticmethod
    def division(data: list[float]) -> float | None:
        """
        Divides the first number in the list by each of the subsequent numbers.

        Parameters
        ----------
        data : list[float]
            A list of numbers for the division operation.

        Returns
        -------
        float
            The result of dividing the first number by each subsequent number.
            Returns None if the list is empty or has only one element.
        """
        if len(data) < 2:
            return None
        result = data[0]
        for num in data[1:]:
            if num == 0:  # Avoid division by zero
                return None
            result /= num
        return result

    @staticmethod
    def product(data: list[float]) -> float:
        """
        Returns the product of a list of numbers.

        Parameters
        ----------
        data : list[float]
            A list of numbers whose product is to be calculated.

        Returns
        -------
        float
            The product of the input numbers. Returns 1 for an empty list.
        """
        product = 1.0
        for num in data:
            product *= num
        return product

    @staticmethod
    def standard_deviation(data: list[float]) -> float:
        """
        Calculates the standard deviation of a list of numbers.

        Parameters
        ----------
        data : list[float]
            A list of numbers whose standard deviation is to be calculated.

        Returns
        -------
        float
            The standard deviation of the input numbers.
        """
        mean = Aggregator.average(data)
        return (sum((x - mean) ** 2 for x in data) / len(data)) ** 0.5 if data else 0.0

    @staticmethod
    def sum(data: list[float]) -> float:
        """
        Returns the sum of a list of numbers.

        Parameters
        ----------
        data : list[float]
            A list of numbers whose sum is to be calculated.

        Returns
        -------
        float
            The sum of the input numbers.
        """
        return sum(data)

    @staticmethod
    def subtraction(data: list[float]) -> float | None:
        """
        Subtracts each subsequent number in the list from the first number.

        Parameters
        ----------
        data : list[float]
            A list of numbers for the subtraction operation.

        Returns
        -------
        float
            The result of subtracting each subsequent number from the first number.
            Returns None if the list is empty or has only one element.
        """
        if len(data) < 2:
            return None
        result = data[0]
        for num in data[1:]:
            result -= num
        return result

    @staticmethod
    def no_op(data: list[Any]) -> Any | None:
        return data if data else None
