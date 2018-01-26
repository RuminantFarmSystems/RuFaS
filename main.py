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

from MASM.simulation_engine import MASM_Simulate
from MASM.input import MASM_prompt_input

#-------------------------------------------------------------------------------
# Function: main
#           Main function of MASM, the whole simulation is executed here
#-------------------------------------------------------------------------------
def main():
 
    print("MASM: Modular Agricultural Systems Modeling Environment")

    #
    # Prompt user for an input
    # Input could either be a MASM file when doing only 1 simulation
    # or a directory containing MASM files when doing a batch simulation
    #
    input_files_list = MASM_prompt_input()
    
    #
    # Begin the simulation
    # Runs the simulation for each input file in input_file_path
    # Runs only 1 simulation in the case of a single input file
    #
    for input_file_path in input_files_list:
        MASM_Simulate(input_file_path)

#-------------------------------------------------------------------------------
#
# PROGRAM ENTRY POINT
#
#------------------------------------------------------------------------------- 
if __name__ == '__main__': main()
        
    