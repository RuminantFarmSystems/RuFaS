'''
RUFAS: Ruminant Farm Systems Model
File name: animal_base.py
Author(s): Manfei Li, mli497@wisc.edu
Description: This file initialize common parameters
			include ID, breed, birth date, and age for all animals to be indentified
'''
###############################################################################


from animal_events import AnimalEvents
import random
import numpy as np

# initial a cow with ID
class AnimalBase(object):
	global_id = 0

	@staticmethod
	def next_id():
		AnimalBase.global_id += 1
		return AnimalBase.global_id

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
		self._id = AnimalBase.next_id()
		self._breed = args['breed']
		self._birth_date = args['date']
		self._days_born = args['days_born']
		self._culled = False
		self._do_not_breed = False
		self._events = AnimalEvents()

	def init_from_animal(self, animal):
		self._id = animal._id
		self._breed = animal._breed
		self._birth_date = animal._birth_date
		self._days_born = animal._days_born
		self._culled = animal._culled
		self._do_not_breed = animal._do_not_breed
		self._events = animal._events

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