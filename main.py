################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: main.py
Description: Main entry point of RUFAS
Author(s): Kass Chupongstimun, kass_c@hotmail.com
'''
################################################################################

#!/usr/bin/env python3

import RUFAS

def main():
    '''
    Main function of RUFAS, executes simulations for all files specified.

    Prompts the user to enter an input path to a json file or a directory of
    json files. The path(s) are returned in a list, which the program loops
    through and executes the simulation for each of the files in the list.
    '''

    print("\nRUFAS: Ruminant Farm Systems Model 2018")

    #
    # Prompt user for an input
    # Input could either be a json file when doing only 1 simulation
    # or a directory containing json files when doing a batch simulation
    #
    input_file_list = RUFAS.input_prompt()

    #
    # Begin the simulation
    # Runs the simulation for each input file in input_file_path
    # Runs only 1 simulation in the case of a single input file
    #
    for input_file_path in input_file_list:
        RUFAS.simulate(input_file_path)

#-------------------------------------------------------------------------------
# PROGRAM ENTRY POINT
#-------------------------------------------------------------------------------
if __name__ == '__main__': main()

