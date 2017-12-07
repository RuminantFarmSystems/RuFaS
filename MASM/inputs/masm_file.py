################################################################################
#
# MASM: Modular Agricultural Systems Modeling Environment
#
# masm_file.py - Contains all MASM file reading routines
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

import sys
from pathlib import Path

from MASM import util
from MASM.errors import InputParsingError, MASMfileError
from MASM.data import *
from MASM.outputs import OutputHandler

#-------------------------------------------------------------------------------
# Function: read_MASM_file
#           Sets up the parameters of the simulation
#           Reads and interprets the MASM file contents into fContents
#           Extracts data from fContents to the specified objects
#           Handles all MASM file errors
#
# Parameters: fPath - Path to the MASM file for the simulation
#             c - Config object to be written to
#             w - Weather object to be written to
#             o - Output object to be written to
#-------------------------------------------------------------------------------
def read_MASM_file(fPath:Path, s:State, c:Config, w:Weather, o:OutputHandler):
    
    c.MASM_fName = util.get_fName(fPath)
    
    try:
        fContents = interpret_MASM_file(fPath)
        
        read_config(fContents, c)
        read_farm(fContents, s, c)
        #read_weather(fContents, c, w)
        read_output_options(fContents, o, c)
        
    except MASMfileError as e:
        print(e.msg)
        sys.exit()

#-------------------------------------------------------------------------------
# Function: interpret_MASM_file
#           Opens the file specified and inteprets the contents. The contents of
#           the file are separated into sections, and sections in to lines.
#           Sections are marked by the '@' at the beginning of the line.
#           All lines beginning with # or containing only whitespace are ignored
#           All leading and trailing whitespace is stripped from every line.
#
# Parameters: fPath - the path of the file to be intepreted
#
# Returns: A 2D list with sections as its elements. Each section is also a list 
#          with elements corresponding to each line in the section as a string
#          with all leading and trailing whitespace stripped.
#-------------------------------------------------------------------------------
def interpret_MASM_file(fPath:Path):
    
    with fPath.open('r') as f:
        fContents = []
        section = []
        
        for line in f:
            if not (line.startswith('#') or line.isspace()):
                # Start of new Section
                if line.startswith('@'):
                    # Avoid appending empty sections
                    if len(section) > 0:
                        fContents.append(section)
                        section = []
                    section.append(line.replace('@','').rstrip())
                else:
                    section.append(line.rstrip())
                         
        fContents.append(section)
    
    return fContents

#-------------------------------------------------------------------------------
# Function: get_section_data
#           Searches through the sections in fContents and retrieves the data of
#           the specified section. Also checks that data exists in that section.
#
# Parameters: sectionName - name of the section to be retrieved as a string
#             fContents - list containing sections through which to search
#             c:Config - used to get MASM file name to print error message
#
# Raises: MASMfileError when the section has no data in it
#
# Returns: A 2D list corresponding to the section retrieved, with each element
#          corresponding to the lines in the section. Each line, initially a
#          string, is split according to whitespace in to a list of strings.
#          Returned list omits the first element of the section, which denotes
#          the section name.
#-------------------------------------------------------------------------------
def get_section_data(sectionName, fContents, c:Config):
    
    for section in fContents:
        if section[0] == sectionName:
            # At least 2 elements, section label and 1 data line
            if len(section) < 2:
                raise MASMfileError("MASM FILE ERROR: " + sectionName + 
                                 " section in " + c.fName + " contains no data")
            else:
                return [line.rsplit() for line in section[1::]]

#-------------------------------------------------------------------------------
# Function: read_config
# 
#-------------------------------------------------------------------------------
def read_config(fContents, c:Config):
    lines = get_section_data("CONFIG", fContents, c)
        
    data = util.to_ints(lines[0])
    c.iterations = data[0]
    c.iterate = data[0] > 1
    c.years = data[1]

#-------------------------------------------------------------------------------
# Function: read_output_options
# 
#-------------------------------------------------------------------------------
def read_output_options(fContents, o:OutputHandler, c:Config):
    lines = get_section_data("OUTPUT", fContents, c)
    
    numOutputFiles = len(o.outputList)
    
    #
    # Specify active output reports
    #
    try:
        data = util.to_bools(lines[0])
    except InputParsingError:
        raise MASMfileError("MASM FILE ERROR: Cannot parse input at line 1 of "
                         + "@OUTPUT section")
    if len(data) != numOutputFiles:
        raise MASMfileError("MASM FILE ERROR: Line 1 of @OUTPUT section must "
                         + "contain " + str(numOutputFiles) + " values")
    for i in range(numOutputFiles):
        o.outputList[i].active = data[i]
    
    #
    # Set custom output file names
    #
    data = lines[1]
    if len(data) != numOutputFiles:
        raise MASMfileError("MASM FILE ERROR: Line 2 of @OUTPUT section must "
                         + "contain " + str(numOutputFiles) + " values")
    for i in range(numOutputFiles):
        if data[i] != '0':
            o.outputList[i].set_fName(data[i])
    
#-------------------------------------------------------------------------------
# Function: read_weather
# 
#-------------------------------------------------------------------------------
def read_weather(fContents, c:Config, w:Weather):
    lines = get_section_data("WEATHER", fContents, c)
    
    wPath = util.to_path(lines[0])
    
    with wPath.open('r') as f:
        pass
        
        #
        # Interpret weather file here
        #

#-------------------------------------------------------------------------------
# Function: read_farm
# 
#-------------------------------------------------------------------------------
def read_farm(fContents, s:State, c:Config):
    
    read_crops(fContents, s.crops, c)
    read_feed(fContents, s.feed, c)
    read_fieldOps(fContents, s.fieldOps, c)
    read_herd(fContents, s.herd, c)
    read_housing(fContents, s.housing, c)
    read_manure(fContents, s.manure, c)
    read_soil(fContents, s.soil, c)
    
#-------------------------------------------------------------------------------
# Function: read_crops
# 
#-------------------------------------------------------------------------------
def read_crops(f, cp:Crops, c:Config):
    pass

#-------------------------------------------------------------------------------
# Function: read_feed
# 
#-------------------------------------------------------------------------------
def read_feed(f, fd:Feed, c:Config):
    pass

#-------------------------------------------------------------------------------
# Function: read_fieldOps
# 
#-------------------------------------------------------------------------------
def read_fieldOps(f, fo:FieldOps, c:Config):
    pass

#-------------------------------------------------------------------------------
# Function: read_herd
# 
#-------------------------------------------------------------------------------
def read_herd(f, hd:Herd, c:Config):
    pass

#-------------------------------------------------------------------------------
# Function: read_housing
# 
#-------------------------------------------------------------------------------
def read_housing(f, hs:Housing, c:Config):
    pass

#-------------------------------------------------------------------------------
# Function: read_manure
# 
#-------------------------------------------------------------------------------
def read_manure(f, mn:Manure, c:Config):
    pass

#-------------------------------------------------------------------------------
# Function: read_soil
# 
#-------------------------------------------------------------------------------
def read_soil(f, so:Soil, c:Config):
    pass

    