################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# animal.py - 
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

import math
from RUFAS.routines.animal.ration import Ration

#------------------------------------------------------------------------------
# Function: daily_animal_routine
# 
#------------------------------------------------------------------------------
def daily_animal_routine(animal, weather, time):
	pass

#------------------------------------------------------------------------------
# Function: daily_animal_routine
# 
#------------------------------------------------------------------------------
def daily_animal_update(animal, weather, time):
	pass

#------------------------------------------------------------------------------
# Class: animal
# 
#------------------------------------------------------------------------------
class Animal():

	def __init__(self, data):
		pass

	def annual_reset():
		pass

#------------------------------------------------------------------------------
# Class: Ration
# 		 Instantiated daily, for each day of ration calculation
#------------------------------------------------------------------------------
class Ration():

	def __init__(self, parity, WIM, AMF, BWR, base_NED, housing):
		
		self.parity = parity		# number of lactations
		self.WIM = WIM				# week in milk, week
		self.AMF = AMF				# average milk fat for the breed, %
		self.BWR = BWR				# ratio of calving body weight to holstein calving weight
		self.base_NED = base_NED	# Baseline net energy density of the diet
		self.housing = housing		# Animal housing info

	def optimize_feed_ration(self):
		
		self.estimate_requirements()
		self.estimate_protein_rqmts()
		self.setup_LP_LHS()
		self.setup_LP_RHS()

		#
		# RUN LINEAR PROGRAM
		#
	
	def estimate_requirements(self):

		# Calculate Fiber Intake Capacity (FIC)
		if self.parity > 1:
			self.FIC = ( (0.564 * (self.WIM + 0.857)**(0.360)) *
						 math.exp(-0.0186 * (self.WIM + 0.857)) )
		else:
			self.FIC = ( (0.388 * (self.WIM + 3) ** (0.588)) *
						 math.exp(-0.0277 * (self.WIM + 3)) )

		# Estimate Base milk production
		# BaseMY is the milk base milk yield estimated from breed specific lactation curve
		if parity > 1:
			self.base_my = ( 33.95 * (self.WIM ** 0.2208) *
							 math.exp(-0.03395 * self.WIM) )
		else:
			self.base_my = ( 24.12 * (self.WIM ** 0.1782) *
				 			 math.exp(-0.02095 * self.WIM) )

		# Estimate Base milk fat
		# BaseMF is the base milk fat estimated from breed specific 
		# average milk fat and component lactation curve
		base_MF = ( 1.4286 * self.AMF * (self.WIM ** -0.24) *
					math.exp(0.016 * self.WIM) )

		if parity > 1:
			self.BW = (self.BWR * 690 * ((self.WIM + 1.57) ** -0.0803) *
					   math.exp(0.00720 * (self.WIM + 1.57)))

	def estimate_energy_rqmts(self):
		
		# set number of hours, position changes and distances traveled
		# if housed in a barn, drylot or grazing
		if self.housing == "barn":
			self.hours = 12
			self.posHG = 9
			self.flat_dist = 0.5
			self.slope_dist = 0.001
		elif self.housing == "drylot":
			self.hours = 15
			self.posHG = 9
			self.flat_dist = 1.5
			self.slope_dist = 0.001
		else:
			self.hours = 16
			self.posHG = 6
			self.flat_dist = 1.0
			self.slope_dist = 0.0


	def estimate_energy_rqmts(self):
		pass

	def setup_LP_LHS():
		pass

	def setup_LP_RHS():
		pass

