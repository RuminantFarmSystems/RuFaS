################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: classes.py
Description: Contains top level class definitions for RUFAS
Author(s): Kass Chupongstimun, kass_c@hotmail.com
		   Jit Patil, spatil5@wisc.edu
'''
################################################################################

import csv
import math

from RUFAS import util
from RUFAS import errors
from RUFAS.routines import Soil, Animal, Feed, Crop

#-------------------------------------------------------------------------------
# Class: State
#-------------------------------------------------------------------------------
class State():
	'''Contains information about the current state of the farm.

	The state object represents the state of the farm at a certain instant in
	time. It contains information arranged in different objects by what routine
	they (mostly) relate to. The state object (or some of its sub-objects) will
	be passed to routines during the simulation, which may access the
	information in the different sub-objects in the state to use in its
	calculations.
	The state object should ONLY store persistent data that WILL be used in
	future calculations and/or reports.
	DO NOT store immediate operands or values that do not NEED to be accessed in
	the future or in an output report in the state object.
	'''

	def __init__(self, data):
		'''
		TODO: Add DocString
		'''

		self.soil = Soil(data['soil'])
		self.animal = Animal(data['animal'])
		self.feed = Feed(data['feed'])
		self.crop = Crop(data['crop'])

		#self.fieldOps = FieldOps()
		#self.herd = Herd()
		#self.housing = Housing()
		#self.manure = Manure()

	#---------------------------------------------------------------------------
	# Method: annual_reset
	#---------------------------------------------------------------------------
	def annual_reset(self):
		'''Annual Reset'''

		self.soil.annual_reset()
		self.animal.annual_reset()
		self.crop.annual_reset()
		self.feed.annual_reset()

		#self.fieldOps.annual_reset()
		#self.herd.annual_reset()
		#self.housing.annual_reset()
		#self.manure.annual_reset()

#-------------------------------------------------------------------------------
# Class: Config
#-------------------------------------------------------------------------------
class Config():
	'''Contains configuration information of the simulation'''

	def __init__(self, data):
		'''
		TODO: Add DocString
		'''

		if data['duration'] <= 0:
			raise errors.JSONfileData("CONFIG",
								"\tSimulation Duration must be at least 1 year")

		self.duration = data['duration']
		self.output_dir = data['output_dir']

#-------------------------------------------------------------------------------
# Class: Weather
#-------------------------------------------------------------------------------
class Weather():
	'''Contains daily weather information stored in 2D lists

	Data lists are in the format Data[year][julian_day].
	'''

	def __init__(self, weather_path_str, duration):

		#
		# Weather Data in 2D lists -> [year][julianDay]
		#
		self.rainfall = [[0 for _ in range(365)]for _ in range(duration)]
		self.tMax = [[0 for _ in range(365)]for _ in range(duration)]
		self.tMin = [[0 for _ in range(365)]for _ in range(duration)]
		self.tAvg = [[0 for _ in range(365)]for _ in range(duration)]
		self.biomass = [[0 for _ in range(365)]for _ in range(duration)]
		self.radiation = [[0 for _ in range(365)]for _ in range(duration)]
		self.addedN = [[0 for _ in range(365)]for _ in range(duration)]

		rainfallData = []
		tMaxData = []
		tMinData = []
		tAvgData = []
		bioMassData = []
		radiationData = []
		addedNData = []

		weather_full_path = util.get_base_dir() / weather_path_str

		if not weather_full_path.is_file():
			raise errors.JSONfileData("WEATHER",
									  "\tWeather file specified does not exist")

		#
		# Read data from CSV file
		# Data read is in the format data[day]
		# 1D list of length total number of days in the whole weather file
		#
		with weather_full_path.open('r') as f:
			readCSV = csv.reader(f, delimiter=',')

			currentRow = 0
			for row in readCSV:
				if currentRow != 0: # Skip the first row because first row contains column headers
					# 1) Read rainfall data
					rainfallData.append(float(row[1]))

					# 2) Read max temperature data
					tMaxData.append(float(row[2]))

					# 3) Read min temperature data
					tMinData.append(float(row[3]))

					# 4) Read avg temperature data
					tAvgData.append(float(row[4]))

					# 5) Read biomass data
					bioMassData.append(float(row[5]))

					# 6) Read radiation data
					radiationData.append(float(row[6]))

					# 7) Added N Data
					addedNData.append(float(row[7]))

				currentRow += 1

		# Make sure weather data length matchs simulation duration
		weather_file_years = math.floor(currentRow / 365)
		if weather_file_years < duration:
			raise errors.JSONfileData("WEATHER",
									  "\tWeather file contains " +
									  str(weather_file_years) +
									  "\n\tSimulation specifies " + str(duration) +
									  " years")
		#
		# TODO: check for weather file length match with simulation duration
		#
		# Print out number of rows(days) read from CSV file
		#print(str(currentRow - 1))

		#
		# Put weather data into the format:
		#    data[year][julian_day]
		#

		# 1) Update Rainfall in weather
		for i in range(0, duration):
			for j in range(0, 365):
				if (i*365+j) >= len(rainfallData):
					break
				else:
					self.rainfall[i][j] = rainfallData[i*365 + j]

		# 2) Update Max Temperature in weather
		for i in range(0, duration):
			for j in range(0, 365):
				if (i*365+j) >= len(tMaxData):
					break
				else:
					self.tMax[i][j] = tMaxData[i*365 + j]

		# 3) Update Min Temperature in weather
		for i in range(0, duration):
			for j in range(0, 365):
				if (i*365+j) >= len(tMinData):
					break
				else:
					self.tMin[i][j] = tMinData[i*365 + j]

		# 4) Update Avg Temperature in weather
		for i in range(0, duration):
			for j in range(0, 365):
				if (i*365+j) >= len(tAvgData):
					break
				else:
					self.tAvg[i][j] = tAvgData[i*365 + j]

		# 5) Update biomass in weather
		for i in range(0, duration):
			for j in range(0, 365):
				if (i*365+j) >= len(bioMassData):
					break
				else:
					self.biomass[i][j] = bioMassData[i*365 + j]

		# 6) Update radiation in weather
		for i in range(0, duration):
			for j in range(0, 365):
				if (i*365+j) >= len(radiationData):
					break
				else:
					self.radiation[i][j] = radiationData[i*365 + j]

		# 7) Update addedN in weather
		for i in range(0, duration):
			for j in range(0, 365):
				if (i*365+j) >= len(addedNData):
					break
				else:
					self.addedN[i][j] = addedNData[i*365 + j]


#-------------------------------------------------------------------------------
# Class: Time
#-------------------------------------------------------------------------------
class Time():
	'''Contains information about the current time in the simulation

	This object is responsible for tracking time in the simulation
	'''

	def __init__(self, duration):

		#self.day_in_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

		self.duration = duration # Simulation duration in years
		self.day = 1  # Current Julian Day
		self.year = 1  # Current Year

	#---------------------------------------------------------------------------
	# Method: to_str
	#---------------------------------------------------------------------------
	def to_str(self):
		'''Returns a string representation of the current time.

		Returns:
			str: a String representation of the current time in the simulation
				in the format "Year: <year> Day: <day>"
		'''

		return "Year: {} Day: {}".format(self.year, self.day)



	#---------------------------------------------------------------------------
	# Method: advance
	#---------------------------------------------------------------------------
	def advance(self):
		'''Advances the time in the simulation by 1 day

		Automatically detects end of months and years
		'''

		if self.end_year():
			self.day = 1
			self.year += 1
		else:
			self.day += 1

	#---------------------------------------------------------------------------
	# Method: end_year
	#---------------------------------------------------------------------------
	def end_year(self):
		'''Returns a bool signifying the end of a year.

		Returns:
			bool: True if it is the end of a year, False otherwise
		'''

		return self.day > 365

	#-------------------------------------------------------------------------------
	# Function: end_simulation
	#-------------------------------------------------------------------------------
	def end_simulation(self):
	    '''Checks whether the simulation has ended

	    Returns:
	        bool: True if the simulation has ended, false otherwise
	    '''

	    return self.year > self.duration

	"""
	#----------------------------------------------------------------------------
	# Method: julian_day
	#----------------------------------------------------------------------------
	def julian_day(self):
		'''Returns the julian day of the year.

		Returns:
			int: The julian day of the year.
		'''

		julian_day = 0
		for i in range(0, self.m - 1):
			julian_day += self.day_in_months[i]
		julian_day += self.d

		return julian_day

	#---------------------------------------------------------------------------
	# Method: end_month
	#---------------------------------------------------------------------------
	def end_month(self):
		'''Returns a bool signifying the end of a month.

		Returns:
			bool: True if it is the end of a year, False otherwise
		'''

		if (self.d > 30) and (self.m == 4 or self.m == 6 or
							  self.m == 9 or self.m == 11):
			return True
		elif (self.d > 31) and (self.m == 1 or self.m == 3 or self.m == 5 or
								self.m == 7 or self.m == 8 or self.m == 10 or
								self.m == 12):
			return True
		elif self.d > 28 and self.m == 2:
			return True
		else:
			return False
	"""
