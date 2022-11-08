"""
RUFAS: Ruminant Farm Systems Model
File name: user_prompt.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
"""

import sys
from pathlib import Path
from RUFAS import util, errors
import fileReader
import config.global_variables


def obtain_file_list(path=None, verbose: bool = True) -> list[Path]:
    """
    Description: obtains a json file list, usable by RuFaS, from the user. The location of the files is given
    directly as a path string, or as a response to an input prompt.

    Args:
         path: a path (absolute or relative) to the file or directory to be used.
         verbose: should messages containing details be printed?

    Returns:
          a list of file Paths

    Details: If path=None, the user will be prompted to provide a path with user_prompt()
    """
    if path is None:
        path_list = user_prompt()
    else:
        path_list = convert_path_string_to_list(path, verbose)
    return path_list


def user_prompt() -> list[Path]:
    """
    Description: prompts the user for an input path to RuFaS data.

    Details: User input is passed to convert_path_string_to_list

    Returns: A list of paths to json input files
    """
    user_input = prompt_user_for_input()
    formatted_input = convert_path_string_to_list(path=user_input)
    return formatted_input


def convert_path_string_to_list(path: str, verbose: bool = True):
    """
    Description: converts a file path string into list of file paths

    Args:
        path: The path (relative or absolute) to an input json file or a directory containing .json files
        verbose: should progress messages be printed?

    Returns: a list of OS-specific files

    Details: If a path to a json file is given, it is converted to a Path list with convert_json_path_to_list(). If a
    path to a directory is given, a Path list pointing to json files within the directory is retrieved with
    get_json_list_from_dir().
    """
    input_path = Path(str(path).strip())

    if input_path.suffix == '.txt':  # TODO: Deprecated - GitHub Issue #210
        Warning("ability to use .txt files is deprecated. Please use .json input files in the future")
        if not input_path.is_file():
            raise errors.UserInput("Specified file does not exist")
        if verbose: print("commented json file detected, stripping comments...\n")
        json_filename = fileReader.convert_to_json(str(input_path))
        json_path = Path(json_filename.strip())
        return [json_path]


    if input_path.suffix == '.json':
        return convert_json_path_to_list(input_path, verbose)

    elif input_path.is_dir():
        return get_json_list_from_dir(input_path, verbose)

    else:
        raise ValueError("Invalid input path")


def get_json_list_from_dir(dir_path: Path, verbose: bool) -> list[Path]:
    """gets a list of all json files contained in a directory.

    Details: throws an error if the directory does not exist or if not json files are found.

    Args:
         dir_path: path to search for json files
         verbose: should status messages be printed?

    Returns: a list of json files (as libpath.Path objects)
    """
    if not dir_path.is_dir():
        raise IsADirectoryError("specified path is not a directory")

    json_paths = list(dir_path.glob("*.json"))
    if len(json_paths) < 1:
        raise FileExistsError("Directory contains no json files")
    else:
        if verbose:
            print(str(len(json_paths)) + "json files detected...\n")
        return json_paths


def convert_json_path_to_list(json_path: Path, verbose: bool) -> list[Path]:
    """converts a path to a json file into a list of libpath.Path objects

    Details: throws an error if the file is not found.
    """
    if not json_path.is_file():
        raise errors.UserInput("Specified file does not exist")

    if verbose: print("json file detected... \n")

    return [json_path]


def prompt_user_for_input() -> str:
    """prompts a user for RuFaS input

    Details: the user is prompted with a message giving them options for input. Input can be a path string,
    the letter 'Q' to quit by calling sys.exit(), or 'dir' to print the directory with util.get_base_dir()

    Returns: the user input, as a string"""
    print("\nSingle Simulation:\n\t" +
          "Enter a json file name\n" +
          "Batch Simulation:\n\t" +
          "Enter a directory containing json files\n" +
          "Print Base Directory:\n\t" +  # TODO: neither "dir" nor "Q/q" work at all - GitHub Issue #208
          "Enter \'dir\'\n" +
          "Exit RUFAS:\n\t" +
          "Enter \'Q\' or \'q\'")

    while True:

        try:
            user_input = 'input/' + input("\nEnter RUFAS Input: ")

            if user_input.upper() == 'Q':
                print("Exiting RUFAS...")
                sys.exit()

            elif user_input.lower() == 'dir':
                print(str(util.get_base_dir()))  # TODO: No such function, likely cause of GitHub Issue #208
                continue

            return user_input
        except errors.UserInput as e:
            print(e.msg)

# TODO make tests. The following should work (from RUFAS/ dir) - GitHub Issue #209
# convert_path_string_to_list("../input/ARL.json")
# convert_path_string_to_list("../input/ARL.json", verbose=False)
# convert_path_string_to_list("../input/")
# convert_path_string_to_list(path=prompt_user_for_input())
# input_prompt()