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
		
		self.ration = Ration(data['ration'])

	def annual_reset():
		pass
