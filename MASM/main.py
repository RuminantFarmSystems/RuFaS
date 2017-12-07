################################################################################
#
# MASM: Modular Agricultural Systems Modeling Environment
#
# main.py - Main program routine
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

#!/usr/bin/env python

from MASM.simulation_engine import MASM_Simulate
from MASM.inputs import MASM_prompt_input

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
    MASM_file_paths = MASM_prompt_input()
    
    #
    # Begin the simulation
    # Runs the simulation for each MASM file in MASM_FileList
    # Runs only 1 simulation in the case of a single MASM file input
    #
    for MASM_file in MASM_file_paths:
        MASM_Simulate(MASM_file)

#-------------------------------------------------------------------------------
#
# PROGRAM ENTRY POINT
#
#------------------------------------------------------------------------------- 
if __name__ == '__main__':
    main()
    
    