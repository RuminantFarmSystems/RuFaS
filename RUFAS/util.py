"""
RUFAS: Ruminant Farm Systems Model
File name: util.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
"""
import json
import sys
from pathlib import Path
from typing import Callable, List, Tuple

from RUFAS import errors


class Utility:
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
        if getattr(sys, 'frozen', False):
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
            if file_path.suffix == '.json':
                if not file_path.is_file():
                    raise errors.UserInput((str(file_path), 'does not exist'))
            else:
                raise errors.UserInput((str(file_path), 'is not a JSON file'))

            with file_path.open('r') as f:
                data = json.load(f)

            return data

        except errors.UserInput as e:
            print(e.msg)

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

    @staticmethod
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
