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
# Error: UserInput
#        Raised when the user enters an invalid input at the prompt
#-------------------------------------------------------------------------------     
class UserInput(Exception):
    
    def __init__(self, msg):
        self.msg = "USER INPUT ERROR: " + msg

#-------------------------------------------------------------------------------
# Error: InvalidJSONfile
#        Raised when the json file fed to the program has problems
#-------------------------------------------------------------------------------     
class InvalidJSONfile(Exception):
    
    def __init__(self, fName):
        self.msg = "Skipping simulation for {}\n".format(fName)
        
#-------------------------------------------------------------------------------
# Error: JSONfileData
#        Raised when speficif parts of the json file has problems
#-------------------------------------------------------------------------------     
class JSONfileData(Exception):
    
    def __init__(self, section, msg):
        self.section = section
        self.msg = msg
        
        