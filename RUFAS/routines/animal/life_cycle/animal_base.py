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
	config = {}
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
		self.id = args['id']
		self.breed = args['breed']
		self.birth_date = args['birth_date']
		self.days_born = args['days_born']
		self.culled = False
		self.do_not_breed = False
		self.events = AnimalEvents()
		
		self.daily_growth = 0
		self.set_default_nutrient_rqmts()
		self.manure_excretion = {}
		self.ration_formulation = {'objective': 0.00}
		self.DMIest = 0
		self.DBW = 0

	def set_default_nutrient_rqmts(self):
		self.nutrient_rqmts = {}
		for key in self.nutrients:
			self.nutrient_rqmts[key] = {'op': '', 'val': 0}

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
		return self.culled