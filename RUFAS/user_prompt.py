################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: user_prompt.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
"""
################################################################################

import sys
from pathlib import Path

from RUFAS import util
from RUFAS import errors
import fileReader

# -------------------------------------------------------------------------------
# Function: input_prompt
# -------------------------------------------------------------------------------
def input_prompt():
    """Prompts the user for an input to RUFAS.

    Prompts the user for an input path that could either be a path to a json
    file (for a single simulation mode) or a path to a directory containing one
    or more json files (for a batch simulation).
    Loops back to the prompt until the user either chooses to quit or enters a
    valid input.
    Valid inputs are:
        Valid path to a json file: single simulation mode
        Valid path to directory of json files: batch simulation mode
        'Q' or 'q': quit the program
        'dir': prints the program's current working directory

    Returns:
        list[Path]: A list of Path objects containing the Paths to the json
            files from which the program will draw data for the simulation.
            The list could contain only 1 or multiple paths.
    """

    print("\nSingle Simulation:\n\t" +
                "Enter a json file name\n" +
          "Batch Simulation:\n\t" +
                "Enter a directory containing json files\n" +
          "Print Base Directory:\n\t" +
                "Enter \'dir\'\n" +
          "Exit RUFAS:\n\t" +
                "Enter \'Q\' or \'q\'")

    while(True):

        try:
            user_input = input("\nEnter RUFAS Input: ")
            # user_input = 'Inputs/barnyard.json'
            #
            # Handle user exiting program
            #
            if user_input.upper() == 'Q':
                print("Exiting RUFAS...")
                sys.exit()

            #
            # Handle print base directory
            #
            elif user_input.lower() == 'dir':
                print(str(util.get_base_dir()))
                continue

            input_path = Path(user_input.strip())

            #
            # Handle commented json text file input
            #
            if input_path.suffix == '.txt':
                if not input_path.is_file():
                    raise errors.UserInput("Specified file does not exist")
                else:
                    print("commented json file detected, stripping comments...\n")
                json_filename = fileReader.convert_to_json(str(input_path))
                json_path = Path(json_filename.strip())
                return [json_path]

            #
            # Handle single json file input
            #
            if input_path.suffix == '.json':
                if not input_path.is_file():
                    raise errors.UserInput("Specified file does not exist")
                else:
                    print("json file Detected...\n")
                return [input_path]

            #
            # Handle directory of json files input
            #
            elif input_path.is_dir():
                # Grab all json files in dir
                path_list = list(input_path.glob('*.json'))
                # Handle no json files in dir
                if len(path_list) < 1:
                    raise errors.UserInput("Directory contains no json files")
                else:
                    print(str(len(path_list)) + " json files detected...\n")
                    return path_list

            #
            # Handle bad inputs
            #
            else:
                raise errors.UserInput("Invalid Input")

        #
        # Handles bad user inputs, prints out error messages
        #
        except errors.UserInput as e:
                print(e.msg)
