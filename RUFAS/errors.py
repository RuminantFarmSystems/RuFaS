################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: errors.py
Description: Defines custom errors for RUFAS
Author(s): Kass Chupongstimun, kass_c@hotmail.com
'''
################################################################################

#-------------------------------------------------------------------------------
# Error: UserInput
#-------------------------------------------------------------------------------
class UserInput(Exception):
	'''Raised when the user enters an invalid input at the prompt'''

	def __init__(self, msg):
		self.msg = "USER INPUT ERROR: " + msg

#-------------------------------------------------------------------------------
# Error: InvalidJSONfile
#-------------------------------------------------------------------------------
class InvalidJSONfile(Exception):
	'''Raised when the json file fed to the program has problems'''

	def __init__(self, fName):
		self.msg = "Skipping simulation for {}\n".format(fName)

#-------------------------------------------------------------------------------
# Error: JSONfileData
#-------------------------------------------------------------------------------
class JSONfileData(Exception):
	'''Raised when specific parts of the json file has problems'''

	def __init__(self, section, msg):
		self.section = section
		self.msg = msg

