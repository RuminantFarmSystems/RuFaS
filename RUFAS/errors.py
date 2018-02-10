################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# errors.py - Contains custom errors
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

#-------------------------------------------------------------------------------
# Class: UserInputError
#
#-------------------------------------------------------------------------------     
class UserInputError(Exception):
    
    def __init__(self, msg):
        self.msg = "USER INPUT ERROR: " + msg

#-------------------------------------------------------------------------------
# Class: SectionError
#
#-------------------------------------------------------------------------------     
class InvalidJSONfileError(Exception):
    
    def __init__(self, fName):
        self.msg = "Skipping simulation for {}\n".format(fName)
        
#-------------------------------------------------------------------------------
# Class: LengthMismatchError
#
#-------------------------------------------------------------------------------     
class JSONfileDataError(Exception):
    
    def __init__(self, section, msg):
        self.section = section
        self.msg = msg
        
        