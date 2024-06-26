import datetime
import re
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple, Optional
import numpy as np

from .general_constants import GeneralConstants


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
    def pad_temporal_data(
        data_to_pad: dict[str, dict[str, list[Any]]],
        fill_value: Any = np.nan,
        fill_gap_values: bool = False,
        fill_end_values: bool = False,
    ) -> dict[str, dict[str, list[Any]]]:
        """
        Pads data based on the simulation day(s) it was recorded on, relative to when other data was recorded, so that
        values are present for all days in a certain range.

        Parameters
        ----------
        data_to_pad : dict[str, dict[str, list[Any]]]
            The data to be padded. The top level key is a variable name, and points to a dictionary that contains the
            keys "values" and optionally "info_maps".
        fill_value : Any, default numpy.nan
            Value that is used to pad the front of the data values, and optionally the values in between original values
            and after the last original value.
        fill_gap_values : bool, default False
            If true, values between known data points are padded with the last known value from the data set. If false,
            values between known data points are filled with `fill_value`.
        fill_end_values : bool, default False
            If true, values after last known data point are padded with the last known value from the data set. If
            false, values after the last known data point are filled with `fill_value`.

        Returns
        -------
        dict[str, dict[str, list[Any]]]
            The padded data, so that gaps in the data are filled in with the last known value or `fill_value`.

        Raises
        ------
        TypeError
            If a variable has no info maps.
        ValueError
            If the number of info maps does not match the number of values for a variable.
            If a value for "simulation_day" is not present in every info map.

        Notes
        -----
        This method assumes there will never be multiple values recorded for a single variable on a single simulation
        day.

        """
        all_simulation_days = []
        for key, value in data_to_pad.items():
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

        padded_data: dict[str, dict[str, list[Any]]] = {}
        for key, data in data_to_pad.items():
            padded_variable_data: dict[str, list[Any]] = {"values": [], "info_maps": []}
            original_units = data["info_maps"][0]["units"]
            zipped_data = zip(data["values"], data["info_maps"])
            indexed_data = {data[1]["simulation_day"]: data for data in zipped_data}
            last_day_of_original_data = max(indexed_data.keys())
            last_value = fill_value
            for day in range(first_day, last_day_of_original_data + 1):
                if day in indexed_data.keys():
                    last_value = indexed_data[day] if fill_gap_values else fill_value
                    padded_variable_data["values"].append(indexed_data[day][0])
                    padded_variable_data["info_maps"].append(indexed_data[day][1])
                    padded_variable_data["info_maps"][-1]["simulation_day"] = day
                elif last_value is fill_value:
                    padded_variable_data["values"].append(last_value)
                    padded_variable_data["info_maps"].append({"simulation_day": day, "units": original_units})
                else:
                    padded_variable_data["values"].append(last_value[0])
                    padded_variable_data["info_maps"].append(last_value[1].copy())
                    padded_variable_data["info_maps"][-1]["simulation_day"] = day

            tail_fill_value = indexed_data[last_day_of_original_data][0] if fill_end_values else fill_value
            for day in range(last_day_of_original_data + 1, last_day + 1):
                padded_variable_data["values"].append(tail_fill_value)
                padded_variable_data["info_maps"].append({"simulation_day": day, "units": original_units})

            padded_data[key] = padded_variable_data

        return padded_data

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
    def remove_special_chars(input_string: str | list[str] | None) -> str:
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
    def convert_ordinal_date_to_month_date(year: int, day: int) -> datetime.date:
        """Generates a datetime.date based on a year and ordinal day."""
        maximum_day = (
            GeneralConstants.YEAR_LENGTH if not Utility.is_leap_year(year) else GeneralConstants.LEAP_YEAR_LENGTH
        )
        if not 1 <= day <= maximum_day:
            raise ValueError(f"Invalid day: {day} of year {year} must be between 1 and {maximum_day}.")
        return datetime.date(year, 1, 1) + datetime.timedelta(days=day - 1)
