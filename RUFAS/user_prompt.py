################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# user_prompt.py - Contains user input prompt routine
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

import sys
from pathlib import Path

from RUFAS import util
from RUFAS import errors

#-------------------------------------------------------------------------------
# Function: input_prompt
#           Prompts the user for an input file name that could either be a json
#           file for a single simulation mode or a directory containing json
#           files for a batch simulation
#           The user could also choose to see the current base directory
#           and to quit the program
#           Loops back to the prompt until the user inputs a valid file name or
#           chooses to quit the program
#
# Returns: A list of Path objects containing the Paths to the json files from
#          which the program will draw data for the simulation
#          The list could contain only 1 or multiple paths
#-------------------------------------------------------------------------------
def input_prompt():
    
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
                
        except errors.UserInput as e:
                print(e.msg)
