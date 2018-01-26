################################################################################
#
# MASM: Modular Agricultural Systems Modeling Environment
#
# prompt_user.py - Contains user input prompt routines
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

import sys
from pathlib import Path
from MASM.errors import UserInputError

#-------------------------------------------------------------------------------
# Function: MASM_prompt_input
#           Prompts the user for an input file name that could either be a json
#           file for a single simulation mode or a directory containing json
#           files for a batch simulation
#           Loops back to the prompt until the user inputs a valid file name or
#           chooses to quit the program
#-------------------------------------------------------------------------------
def MASM_prompt_input():
    
    print("\nSingle Simulation:\n\t" +
          "Enter a json file name\n" +
          "Batch Simulation:\n\t" +
          "Enter a directory containing json files\n" +
          "Exit MASM:\n\t" +
          "Enter \'Q\' or \'q\'")

    while(True):
        try:
            userInput = input("\nEnter MASM Input: ")
            #userInput = "Sample.MASM"

            #
            # Handle user exiting program
            #
            if userInput.upper() == 'Q':
                print("Exiting MASM...")
                sys.exit()
                
            inputPath = Path(userInput).resolve()

            #
            # Handle json file input
            #
            if inputPath.suffix == '.json':
                if not inputPath.is_file():
                    raise UserInputError("Specified file does not exist")
                else:
                    print("json file Detected...\n")
                    return [inputPath]
            
            #
            # Handle directory of MASM files input
            #
            elif inputPath.is_dir():
                # Grab all json files in dir
                pathList = list(inputPath.glob('*.json'))
                # Handle no json files in dir
                if len(pathList) < 1:
                    raise UserInputError("Directory contains no json files")
                else:
                    print(str(len(pathList)) + " json files detected...\n")
                    return pathList

            #
            # Handle bad inputs
            #
            else:
                raise UserInputError("Invalid Input")
                
        except UserInputError as e:
                print(e.msg)
