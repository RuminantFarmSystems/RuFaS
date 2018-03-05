################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# SimulationEngine.py - Contains the functions that manage the control flow of 
#                       the simulation
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

import json
from pathlib import Path

from RUFAS import routines, errors
from RUFAS.classes import Config, State, Weather, Time
from RUFAS.output import OutputHandler

#
# Define Simulation Global Variables
#
config = None
state = None
output = None
weather = None
time = None

#-------------------------------------------------------------------------------
# Function: simulate
#           Executes the simulation using the json file at the path specified
#           Skips over the simulation (immediately returns) when an error in
#           the input json file is detected
#
# Parameters: input_fPath - path to the input json file
#------------------------------------------------------------------------------- 
def simulate(input_fPath:Path):

    #
    # Reads the json input file and uses the information to instantiate the
    # simulation global variables
    #
    try:
        read_json_file(input_fPath)
    except errors.InvalidJSONfile as e:
        print(e.msg)
        return
    
    #
    # Creates a new directory for the output files (if doesn't already exist)
    # Deletes existing output files of the same name from previous simulation
    # Transfer needed (initial) data from state to report handlers
    #
    output.initialize_output_dir(config.output_dir)
    output.initialize_reports(state)
    
    #
    # MAIN Simulation Loop
    #
    print("\nSimulating: {}".format(input_fPath.name))

    while not end_simulation():
        annual_simulation()
        
    print("Simulation Successful: {}\n".format(input_fPath.name))

#------------------------------------------------------------------------------- 
# Function: daily_simulation
#           Executes the daily routines of the simulation
#------------------------------------------------------------------------------- 
def daily_simulation():
    
    #
    # This IF statement is in place because of the soil hydrology file Pete has
    # provided. His values are calculated starting from day 274 of year 1.
    # We should avoid doing this if possible
    #
    if time.julian_day() >= 274 or time.y > 1:
        
        #
        # Daily Routines
        # Pass only information needed
        #
        routines.daily_soil_routine(state.soil, weather, time)
    
        #
        # Daily Output Updates
        #
        output.reports['soil_summary'].daily_update(state.soil, weather, time)
    
        #
        # Daily Attribute Updates
        # Update attributes in preparation of following day
        #
        routines.daily_soil_update(state.soil, weather, time)
    
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
#           Writes the annual report to the output files
#           Flushes the data in the output object
#           Resets the state for the following year
#------------------------------------------------------------------------------- 
def annual_simulation():
   
    while not time.end_year():
        monthly_simulation()

    #
    # Annual Routines
    #
    output.write_annual_reports()
    output.annual_flush()
    #state.annual_reset()
    time.advance()
    
#------------------------------------------------------------------------------- 
# Function: end_simulation
# Returns: True if the simulation cycle is done
#          False otherwise
#------------------------------------------------------------------------------- 
def end_simulation():
    return time.y > config.duration
    
#-------------------------------------------------------------------------------
# Function: read_json_file
#           Reads and interprets the json file
#           Sets up the parameters of the simulation
#
# Parameters: fPath - Path to the json input file for the simulation
#
# Raises: InvalidJSONfileError - when there is a problem with the json file
#-------------------------------------------------------------------------------
def read_json_file(fPath:Path):

    # Specify that we are using global variables
    global config, state, output, weather, time
    
    with fPath.open('r') as f:
        data = json.load(f)
        
        # Instantiate objects using dictionary data from .json file
        try:
            config = Config(data['config'])
            state = State(data['farm'])
            output = OutputHandler(data['output'])
            weather = Weather(data['weather'], config.duration)
            time = Time()
            
        except errors.JSONfileData as e:
            print("JSON FILE ERROR: " + 
                  "{} \n\t{} Section\n{}\n".format(fPath.name, e.section, e.msg))
            raise errors.InvalidJSONfile(fPath.name)
    