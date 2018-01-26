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

from MASM.classes import State, Config, Time, Weather
from MASM.output import OutputHandler
from MASM.input import read_json_file
from MASM.errors import InvalidJSONfileError

# Import all 'main' simulation routines

#
# Define Module Global Variables
#
state = None
config = None
time = None
weather = None
output_handler = None

#-------------------------------------------------------------------------------
# Function: MASM_Simulate
#           Executes the simulation using the json file at the path specified
#           Deals with simulation iterations as specified
#           Skips over the simulation (immediately returns) when an error in
#           the input json file is detected
#
# Parameters: input_fPath - path to the input json file
#------------------------------------------------------------------------------- 
def MASM_Simulate(input_fPath:Path):
    
    #
    # Instantiates global variables for this simulation
    # New instances are created for every new simulation
    #
    initialize_globals()

    #
    # Reads the json input file
    #
    try:
        read_json_file(input_fPath, state, config, weather, output_handler)
    except InvalidJSONfileError as e:
        print(e.msg)
        return
    
    #
    # MAIN Simulation Loop
    #
    while not end_iterations():
        
        print("Simulating: {} Iteration: {}".format(config.fName, time.i))
        
        if config.iterate:
            output_handler.update_fNames(time.i)
            config.modify_parameters(time.i)

        while not end_simulation():
            annual_simulation()
        
        time.advance_iteration()
        
    print("Simulation Successful: {}\n".format(config.fName))

#------------------------------------------------------------------------------- 
# Function: daily_simulation
#           Executes the daily routines of the simulation
#------------------------------------------------------------------------------- 
def daily_simulation():
    
    #
    # Daily Routines
    # Pass only information needed
    #
    
    # This IF statement is in place because of the soil hydrology file Pete has
    # provided. His values are calculated starting from day 274 of year 1. 
    if time.MMDD_to_JulianDay(time.m, time.d) >= 274 or time.y > 1:
                
        # calculate daily runoff (soil)
        state.soil.dailyInfiltration(weather.rainfall[time.y-1]
                                  [time.MMDD_to_JulianDay(time.m, time.d)-1],
                                  weather.cumulative)
    
        # calculate daily transpiration (soil)
        state.soil.dailyEvapotranspiration(time.MMDD_to_JulianDay(time.m, time.d)
            , weather.tMax[time.y-1][time.MMDD_to_JulianDay(time.m, time.d)-1]
            , weather.tMin[time.y-1][time.MMDD_to_JulianDay(time.m, time.d)-1]
            , weather.tAvg[time.y-1][time.MMDD_to_JulianDay(time.m, time.d)-1]
            , weather.biomass[time.y-1][time.MMDD_to_JulianDay(time.m, time.d)-1]
            , state.location.latitude)
        
        state.soil.dailyPercolation()  
        
        state.soil.dailySoilErosion(weather.rainfall[time.y-1]
                                  [time.MMDD_to_JulianDay(time.m, time.d)-1], time.MMDD_to_JulianDay(time.m, time.d)) 
        
        state.soil.updateDailyOutput(output_handler.report_handlers.get
                    ("soil_Summary"), weather.rainfall[time.y-1]
                    [time.MMDD_to_JulianDay(time.m, time.d)-1], 
                    time.MMDD_to_JulianDay(time.m, time.d), time.y)
        
        if float(weather.tAvg[time.y-1][time.MMDD_to_JulianDay(time.m, time.d)-1]) > 0:
            weather.cumulative = max(-10, min(20, weather.cumulative + 1.0))
        else:
            weather.cumulative = max(-10, min(20, weather.cumulative - 1.0)) 
            
        state.soil.updateCurrentSoilWater(weather.rainfall[time.y-1]
            [time.MMDD_to_JulianDay(time.m, time.d)-1])       
    
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
    
