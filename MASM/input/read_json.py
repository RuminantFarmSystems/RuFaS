################################################################################
#
# MASM: Modular Agricultural Systems Modeling Environment
#
# read_json.py - Contains routines to read and interpret json files
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

import json
import csv
from pathlib import Path

from MASM.errors import LengthMismatchError, JSONfileError, InvalidJSONfileError
from MASM.classes import State, Config, Weather, Location
from MASM.output import OutputHandler

#-------------------------------------------------------------------------------
# Function: read_json_file
#           Sets up the parameters of the simulation
#           Reads and interprets the json file
#
# Parameters: fPath - Path to the MASM file for the simulation
#             c - Config object to be written to
#             w - Weather object to be written to
#             o - Output object to be written to
#
# Raises: InvalidJSONfileError - when there is a problem with the json file
#-------------------------------------------------------------------------------
def read_json_file(fPath:Path):
    
    with fPath.open('r') as f:
        data = json.load(f)
        
        try:
            config = Config(data['config'], fPath.name)
            state = State(data['farm'])
            output = OutputHandler(data['output'])
            weather = Weather(data['weather'], config.duration)
            
        except (JSONfileError, LengthMismatchError) as e:
            print(e.msg)
            raise InvalidJSONfileError(fPath.name)
        
        return {
                'config': config,
                'state': state,
                'output': output,
                'weather': weather
                }
    
"""
#-------------------------------------------------------------------------------
# Function: read_crops
# 
#-------------------------------------------------------------------------------
def read_crops(f, cp, c:Config):
    pass

#-------------------------------------------------------------------------------
# Function: read_feed
# 
#-------------------------------------------------------------------------------
def read_feed(f, fd, c:Config):
    pass

#-------------------------------------------------------------------------------
# Function: read_fieldOps
# 
#-------------------------------------------------------------------------------
def read_fieldOps(f, fo, c:Config):
    pass

#-------------------------------------------------------------------------------
# Function: read_herd
# 
#-------------------------------------------------------------------------------
def read_herd(f, hd, c:Config):
    pass

#-------------------------------------------------------------------------------
# Function: read_housing
# 
#-------------------------------------------------------------------------------
def read_housing(f, hs, c:Config):
    pass

#-------------------------------------------------------------------------------
# Function: read_manure
# 
#-------------------------------------------------------------------------------
def read_manure(f, mn, c:Config):
    pass
"""