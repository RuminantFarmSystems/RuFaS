"""
RUFAS: Ruminant Farm Systems Model
File name: animal_base.py
Author(s): Manfei Li, mli497@wisc.edu
Description: This file initialize common parameters including ID, breed,
			birth date, and age for all animals to be identified.
"""
###############################################################################

from RUFAS.routines.animal.life_cycle.animal_events import AnimalEvents


class AnimalBase(object):
	global_id = 0
	config = []
	nutrients = None
	
	@staticmethod
	def set_nutrient_list(nutrients):
		AnimalBase.nutrients = nutrients

	@staticmethod
	def next_id():
		AnimalBase.global_id += 1
		return AnimalBase.global_id
	
	@staticmethod
	def set_config(config):
		AnimalBase.config = config

	def __init__(self, args):
		"""
		Initializes common parameters for all animals
		Args:
			args:
				args.breed: breed of the cow
				args.date: the date of the simulation when the calf was born
				args.daysBorn: age of the animal
		"""
		self._id = AnimalBase.next_id()
		self._breed = args['breed']
		self._birth_date = args['date']
		self._days_born = args['days_born']
		self._culled = False
		self._do_not_breed = False
		self._events = AnimalEvents()
		
		self._daily_growth = 0
		self._nutrient_rqmts = {}
		self.set_default_nutrient_rqmts()
		self._manure_excretion = {}
		self._ration_formulation = {'objective': 0.00}
		self._DMIest = 0
		self._DBW = 0
		self._p_animal = 0

	def init_from_animal(self, animal):
		self._id = animal._id
		self._breed = animal._breed
		self._birth_date = animal._birth_date
		self._days_born = animal._days_born
		self._culled = animal._culled
		self._do_not_breed = animal._do_not_breed
		self._events = animal._events
		
		self._daily_growth = 0
		self._nutrient_rqmts = {}
		self.set_default_nutrient_rqmts()
		self._manure_excretion = {}
		self._ration_formulation = {'objective': 0.00}
		self._DMIest = 0
		self._DBW = 0
		
	def set_default_nutrient_rqmts(self):
		"""
		Sets the default nutrient requirement values to be 0.
		"""
		for key in self.nutrients:
			self._nutrient_rqmts[key] = {'op': '', 'val': 0}

	def culled(self):
		"""
		Returns: True/False value indicating if culled
		"""
		return self._culled
