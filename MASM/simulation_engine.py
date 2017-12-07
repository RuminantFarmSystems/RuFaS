################################################################################
#
# MASM: Modular Agricultural Systems Modeling Environment
#
# SimulationEngine.py - Contains the functions that manage the control flow of 
#                       the simulation
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

from pathlib import Path

from MASM.data import State, Config, Time, Weather
from MASM.outputs import OutputHandler
from MASM.inputs import read_MASM_file

# Import all 'main' simulation routines

#
# Define Global Variables
#
state = None
config = None
time = None
weather = None
output_handler = None

#-------------------------------------------------------------------------------
# Function: MASM_Simulate
#           Executes the simulation using the MASM file specified
#           Deals with simulation iterations as specified
#
# Parameters: MASMfile - the MASM file to be used as the simulation input
#------------------------------------------------------------------------------- 
def MASM_Simulate(MASMfile: Path):
    
    #
    # Instantiates global variables for this simulation
    # New instances are created for every new simulation
    #
    initialize_globals()
    
    #
    # Reads the specified MASM file
    #
    read_MASM_file(MASMfile, state, config, weather, output_handler)
    
    #
    # Single cycle Simulation, no repetitions
    #
    if not config.iterate:        
        while not end_simulation():
            annual_simulation()
 
    #
    # Multiple repetitions of the simulation specified
    #               
    else:
        while not end_iterations():
            output_handler.update_fNames(time.i)
            
            while not end_simulation():
                annual_simulation()
            
            #
            # Repetition Routines
            #
            config.modify_parameters(time.i)
            time.advance_iteration()

#------------------------------------------------------------------------------- 
# Function: daily_simulation
#           Executes the daily routines of the simulation
#------------------------------------------------------------------------------- 
def daily_simulation():
    
    #
    # Daily Routines
    # Pass only information needed
    #
    time.advance()

#------------------------------------------------------------------------------- 
# Function: monthly_simulation
#           Executes the monthly routines of the simulation
#------------------------------------------------------------------------------- 
def monthly_simulation():
    
    while not time.end_month():
        daily_simulation()
        
    #
    # Monthly Routines
    #
    time.advance()

#------------------------------------------------------------------------------- 
# Function: annual_simulation
#           Executes the annual routines of the simulation
#           Writes the annual report to the output text file
#           Flushes the data in the output object
#           Resets the state for the following year
#------------------------------------------------------------------------------- 
def annual_simulation():
   
    while not time.end_year():
        monthly_simulation()
            
    #
    # Annual Routines
    #
    print("Simulating: " + config.MASM_fName
          + " Year: " + str(time.y) + " Iteration: " + str(time.i))
    
    output_handler.write_annual_reports(time)
    output_handler.annual_flush()
    state.annual_reset()
    time.advance()
    
#------------------------------------------------------------------------------- 
# Function: end_simulation
# Returns: True if the simulation cycle is done
#          False otherwise
#------------------------------------------------------------------------------- 
def end_simulation():
    return time.y > config.years

#------------------------------------------------------------------------------- 
# Function: end_iterations
# Returns: True if all specified iterations of the simulation is complete
#          False otherwise
#------------------------------------------------------------------------------- 
def end_iterations():
    return time.i > config.iterations


#------------------------------------------------------------------------------- 
# Function: initialize_globals
#           Initializes all simulation global objects
#           Creates a new instance for each object
#------------------------------------------------------------------------------- 
def initialize_globals():
    
    global state, config, time, weather, output_handler
    state = State()
    config = Config()
    weather = Weather()
    time = Time()
    output_handler = OutputHandler()


    
