import datetime
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple, Optional

from RUFAS import errors
from RUFAS.config import is_leap_year


class Utility:
    @staticmethod
    def convert_list_of_dicts_to_dict_of_lists(
        list_of_dicts: List[Dict[str, Any]]
    ) -> Dict[str, List[Any]]:
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
        result = {}

        for item in list_of_dicts:
            for key, value in item.items():
                if key not in result:
                    result[key] = []
                result[key].append(value)

        return result

    @staticmethod
    def get_base_dir():
        """
        Gets the base directory as reference for all relative paths.

        Unfrozen application - gets the project directory
        Frozen application - gets the executable directory

        Returns
        -------
        Path: The reference directory for all paths in the program.

        """

        # Frozen
        if getattr(sys, "frozen", False):
            #
            # Get the executable file path
            # Resolve to absolute path
            # Take the parent base_dir/RUFAS_exe
            #                 parent = base_dir/

            return Path(sys.executable).resolve().parent

        # Unfrozen
        else:
            #
            # Get path of current file (util.py)
            # Resolve to absolute path
            # Get the 2nd parent  base_dir/RUFAS/util.py
            #                     parent[0] = base_dir/RUFAS
            #                     parent[1] = base_dir/
            return Path(__file__).resolve().parents[1]

    @staticmethod
    def read_json_file(file_path: Path):
        """
        Description:
            Reads and interprets the JSON file at the given path. Compiles the
            information into dictionaries used to instantiate simulation objects.

        Parameters
        ----------
        file_path (Path): Path to the input json file

        Raises
        ------
        InvalidJSONFileError: If the json file at the given path does not
                conform with the format required

        Returns
        -------
        data: the data read from the json file

        """

        try:
            if file_path.suffix == ".json":
                if not file_path.is_file():
                    raise errors.UserInput((str(file_path), "does not exist"))
            else:
                raise errors.UserInput((str(file_path), "is not a JSON file"))

            with file_path.open("r") as f:
                data = json.load(f)

            return data

        except errors.UserInput as e:
            print(e.msg)

    @staticmethod
    def calc_average(
        num_values: int, cur_avg: float, new_value: float
    ) -> Tuple[int, float]:
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
    def remove_items_from_list_by_indices(arr: List, removed_idx: List[int]) -> None:
        """
        Remove items from a list given a list of indices.
        The operation is done in-place.

        Parameters
        ----------
        arr: a list of items
        removed_idx: a list that contains indices of the items to be removed

        Returns
        -------
        None

        """

        # Safer to remove elements from the back
        for idx in sorted(removed_idx, reverse=True):
            del arr[idx]

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
    def make_serializable(cls, obj, max_depth=3):
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
            return tuple(
                [cls._make_serializable(elem, depth + 1, max_depth) for elem in obj]
            )

        # If the object is a set, serialize each element recursively
        # Note: sets are not serializable by default, so we convert them to lists
        if isinstance(obj, set):
            return [cls._make_serializable(elem, depth + 1, max_depth) for elem in obj]

        # If the object is a dictionary, serialize each key-value pair recursively
        # Note: dictionary keys must be strings
        if isinstance(obj, dict):
            return {
                str(
                    cls._make_serializable(key, depth, max_depth)
                ): cls._make_serializable(value, depth, max_depth)
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
    def day_to_month_conversion(day: int, calendar_year: int) -> int:
        """
        Converts the julian day into the corresponding month of the current calendar year.

        Parameters
        ----------
        day : int
            Current julian day of the simulation.
        calendar_year : int
            Current calendar year of the simulation.

        Returns
        -------
        int
            The corresponding month of the year (1 for January, 2 for February, etc.).

        Notes
        -----
        The calendar year is specified so it can be determined if it is a leap year.

        """
        non_leap_cumulative_days_in_months = [31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
        leap_cumulative_days_in_months = [31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]

        cumulative_days_in_months = \
            leap_cumulative_days_in_months if is_leap_year(calendar_year) else non_leap_cumulative_days_in_months

        for month, day_count in enumerate(cumulative_days_in_months):
            if day <= day_count:
                return month + 1

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
        timestamp_format_string: str = (
            f"{base_timestamp_str}.%f" if include_millis else base_timestamp_str
        )
        return datetime.datetime.now().strftime(timestamp_format_string)
