"""
This file serves as a way to compare metadata properties files used in RuFaS.

To run this file, you will need 2 args:
1. The file path to a metadata properties file (file_path_1).
2. The file path to the separate metadata properties file you to which want to compare the first file (file_path_2).

Then, in the terminal:
python compare_metadata_properties.py file_path_1 file_path_2

This will produce a list of the differences in a .txt file saved in the output directory titled:
"diff_results_file_name_1_vs_file_name_2.txt"

"""

from deepdiff import DeepDiff
from pprint import pformat

import argparse
import json
import os


def load_json(file_path: str):
    """
    Loads a json file.
    """
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist or cannot be accessed.")
    except PermissionError:
        print(f"Error: Permission denied when trying to read from {file_path}.")
    except OSError as e:
        print(f"An unexpected OS error occurred: {e}")


def compare_metadata_properties() -> None:
    """
    Compares two json files using the DeepDiff package and saves the results in a txt file.
    """
    parser = argparse.ArgumentParser(description="Compare two JSON files for differences.")
    parser.add_argument("file1", type=str, help="Path to the first JSON file")
    parser.add_argument("file2", type=str, help="Path to the second JSON file")
    args = parser.parse_args()

    data1 = load_json(args.file1)
    data2 = load_json(args.file2)

    diff = DeepDiff(data1, data2, ignore_order=True, verbose_level=2)

    formatted_diff = pformat(diff, indent=2)

    file_name = "diff_results_" + os.path.basename(str(args.file1)) + "_vs_" + os.path.basename(str(args.file2))
    try:
        with open(f"output/{file_name}.txt", "w") as file:
            file.write(f"Comparing: '{str(args.file1)}' to '{str(args.file2)}'\n")
            file.write(formatted_diff)
    except FileNotFoundError:
        print(f"Error: The directory 'output' does not exist or {file_name}.txt cannot be accessed.")
    except PermissionError:
        print(f"Error: Permission denied when trying to write to {file_name}.txt.")
    except OSError as e:
        print(f"An unexpected OS error occurred: {e}")


if __name__ == "__main__":
    compare_metadata_properties()
