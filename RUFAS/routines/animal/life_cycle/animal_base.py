'''
RUFAS: Ruminant Farm Systems Model
File name: animal_base.py
Author(s): Manfei Li, mli497@wisc.edu
Description: This file initialize common parameters
			include ID, breed, birth date, and age for all animals to be indentified
'''
###############################################################################


from RUFAS.routines.animal.life_cycle.animal_events import AnimalEvents
import random
import numpy as np

# initial a cow with ID
class AnimalBase(object):
	config = []
	nutrients = None
	
	@staticmethod
	def set_nutrient_list(nutrients):
		AnimalBase.nutrients = nutrients

	@staticmethod
	def set_config(config):
		AnimalBase.config = config

	# Method: __init__
	'''
		Description:
			initialize common parameters for all animals
		Input:
			args.breed: breed of the cow
			args.date: the date of the simulation when the calf was born
			args.daysBorn: age of the animal
		Output:
	'''
	def __init__(self, args):
		self._id = args['id']
		self._breed = args['breed']
		self._birth_date = args['birth_date']
		self._days_born = args['days_born']
		self._culled = False
		self._do_not_breed = False
		self._events = AnimalEvents()
		
		self._daily_growth = 0
		self.set_default_nutrient_rqmts()
		self._manure_excretion = {}
		self._ration_formulation = {'objective': 0.00}
		self._DMIest = 0
		self._DBW = 0

	def set_default_nutrient_rqmts(self):
		self._nutrient_rqmts = {}
		for key in self.nutrients:
			self._nutrient_rqmts[key] = {'op': '', 'val': 0}

	# Method: is_culled
	'''
		Description:
			Check if the the cow is culled
		Input:
			From repro, production, and health culling section
		Output:
			True/False value inidicating if culled
	'''
	def culled(self):
		return self._culled