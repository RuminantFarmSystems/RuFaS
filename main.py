################################################################################
#
# MASM: Modular Agricultural Systems Modeling Environment
#
# main.py - Main program routine
#
# Authors: Kass Chupongstimun
#          Jit Patil JITs
#
################################################################################

#!/usr/bin/env python3

import MASM

#-------------------------------------------------------------------------------
# Function: main
#           Main function of MASM, the whole simulation is executed here
#-------------------------------------------------------------------------------
def main():
 
    print("MASM: Modular Agricultural Systems Modeling Environment")
    
    #
    # Prompt user for an input
    # Input could either be a json file when doing only 1 simulation
    # or a directory containing json files when doing a batch simulation
    #
    input_file_list = MASM.input_prompt()
    
    #
    # Begin the simulation
    # Runs the simulation for each input file in input_file_path
    # Runs only 1 simulation in the case of a single input file
    #
    for input_file_path in input_file_list:
        MASM.simulate(input_file_path)

#-------------------------------------------------------------------------------
#
# PROGRAM ENTRY POINT
#
#------------------------------------------------------------------------------- 
if __name__ == '__main__': main()
        
    