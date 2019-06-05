################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: errors.py
Description: Defines custom errors for RUFAS
Author(s): Kass Chupongstimun, kass_c@hotmail.com
'''
################################################################################


# -------------------------------------------------------------------------------
# Error: UserInput
# -------------------------------------------------------------------------------
class UserInput(Exception):
	'''Raised when the user enters an invalid input at the prompt'''

	def __init__(self, msg):
		self.msg = "USER INPUT ERROR: " + msg


# -------------------------------------------------------------------------------
# Error: InvalidJSONfile
# -------------------------------------------------------------------------------
class InvalidJSONfile(Exception):
	'''Raised when the json file fed to the program has problems'''

	def __init__(self, fName):
		self.msg = "Skipping simulation for {}\n".format(fName)


# -------------------------------------------------------------------------------
# Error: JSONfileData
# -------------------------------------------------------------------------------
class JSONfileData(Exception):
	'''Raised when specific parts of the json file has problems'''

	def __init__(self, section, msg):
		self.section = section
		self.msg = msg


# -------------------------------------------------------------------------------
# Error: InvalidWeatherCSV
# -------------------------------------------------------------------------------
class InvalidWeatherCSV(Exception):
	'''Raised when the weather file fed to the program has problems'''

	def __init__(self, weather_full_path, msg):
		self.weather_full_path = weather_full_path
		self.msg = msg


# -------------------------------------------------------------------------------
# Error: InvalidWeatherfile
# -------------------------------------------------------------------------------
class InvalidWeatherfile(Exception):
	'''Raised when the weather file fed to the program has problems'''

	def __init__(self, wName):
		self.msg = "Skipping simulation for {}\n".format(wName)
