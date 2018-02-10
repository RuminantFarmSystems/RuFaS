################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# main.py - Main program routine
#
# Authors: Kass Chupongstimun
#          Jit Patil JITs
#
################################################################################

#!/usr/bin/env python3

import RUFAS

#-------------------------------------------------------------------------------
# Function: main
#           Main function of RUFAS, the whole simulation is executed here
#-------------------------------------------------f------------------------------
def main():
 
    print("RUFAS: Ruminant Farm Systems Model")

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
#
# PROGRAM ENTRY POINT
#
#------------------------------------------------------------------------------- 
if __name__ == '__main__': main()
        
    