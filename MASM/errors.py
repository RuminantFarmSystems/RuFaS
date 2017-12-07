################################################################################
#
# MASM: Modular Agricultural Systems Modeling Environment
#
# errors.py - Contains custom errors
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

#-------------------------------------------------------------------------------
# Class: InputError
#
#-------------------------------------------------------------------------------     
class UserInputError(Exception):
    
    def __init__(self, msg):
        self.msg = "USER INPUT ERROR: " + msg
        
#-------------------------------------------------------------------------------
# Class: InputError
#
#-------------------------------------------------------------------------------     
class MASMfileError(Exception):
    
    def __init__(self, section, line, msg):
        self.msg = "MASM FILE ERROR: " + msg
        
#-------------------------------------------------------------------------------
# Class: InputError
#
#-------------------------------------------------------------------------------     
class InputParsingError(Exception):
    pass