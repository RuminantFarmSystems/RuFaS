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
from glob import glob

import MASM.util as util
from MASM.errors import UserInputError

#-------------------------------------------------------------------------------
# Function: MASM_prompt_input
#           Prompts the user for an input file name that could either be a MASM
#           file for a single simulation mode or a MASMBATCH file for a batch
#           simulation mode
#           Loops back to the prompt until the user inputs a valid file name or
#           chooses to quit the program
#-------------------------------------------------------------------------------
def MASM_prompt_input():
    
    print("")
    print("Single Simulation:\n\tEnter a MASM file name")
    print("Batch Simulation:\n\tEnter a directory containing MASM files")
    print("Exit MASM:\n\tEnter \'Q\' or \'q\'")

    while(True):
        try:            
            #userInput = input("\nEnter MASM Input: ")
            userInput = "Sample.MASM"
            
            #
            # Handle MASM file input
            #
            if userInput.endswith(".MASM"):
                fPath = util.to_path(userInput)
                if not fPath.is_file():
                    raise UserInputError("Specified MASM file does not exist")
                else:
                    print("MASM file Detected...")
                    return [fPath]
            
            #
            # Handle directory of MASM files input
            #
            elif util.to_path(userInput).is_dir():
                # Grab all MASM files in dir
                fPathList = glob(str(util.to_path(userInput)) + "/*.MASM")
                # Handle no MASM files in dir
                if len(fPathList) < 1:
                    raise UserInputError("Directory contains no MASM files")
                else:
                    print(str(len(fPathList)) + " MASM files detected...")
                    return [Path(_) for _ in fPathList]

            #
            # Handle user exiting program
            #
            elif userInput.upper() == 'Q':
                print("Exiting MASM...")
                sys.exit()
            
            #
            # Handle bad inputs
            #
            else:
                raise UserInputError("Invalid Input")
                
        except UserInputError as e:
                print(e.msg)
