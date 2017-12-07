################################################################################
#
# MASM: Modular Agricultural Systems Modeling Environment
#
# Util.py
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

from pathlib import Path
from MASM.errors import InputParsingError
        
#-------------------------------------------------------------------------------
# Function: toPath
#           Converts a given file name string to the appropriate path object
#-------------------------------------------------------------------------------
def to_path(fName):
    return Path("../Inputs/" + fName)

#-------------------------------------------------------------------------------
# Function: get_fName
#           Converts a given file name string to the appropriate path object
#-------------------------------------------------------------------------------
def get_fName(fPath: Path):
    return str(fPath)[str(fPath).rfind('/') + 1::]

#-------------------------------------------------------------------------------
# Function: to_ints
#           Parses all elements of a list of strings to integers
#-------------------------------------------------------------------------------
def to_ints(l:list):
    return [int(_) for _ in l]

#-------------------------------------------------------------------------------
# Function: to_floats
#           Parses all elements of a list of strings to floating points
#-------------------------------------------------------------------------------
def to_floats(l:list):
    return [float(_) for _ in l]

#-------------------------------------------------------------------------------
# Function: to_bools
#           Parses all elements of a list of strings to booleans
#-------------------------------------------------------------------------------
def to_bools(l:list):
    for i in l:
        if not (int(i) != 0 or int(i) != 1):
            raise InputParsingError()
        
    return [int(_) == 1 for _ in l]

#-------------------------------------------------------------------------------
# Function: toString2Dlist
#           
#-------------------------------------------------------------------------------
def to_str_2Dlist(l:list):
    s = ""
    for row in l:
        for e in row:
            s += e + '\t'
        s = s.rstrip() + '\n'
    return s.rstrip()
        
