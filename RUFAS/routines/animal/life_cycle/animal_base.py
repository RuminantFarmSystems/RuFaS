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
		self.id = AnimalBase.next_id()
		self.breed = args['breed']
		self.birth_date = args['date']
		self.days_born = args['days_born']
		self.culled = False
		self.do_not_breed = False
		self.events = AnimalEvents()
		
		self.daily_growth = 0
		self.nutrient_rqmts = {}
		self.set_default_nutrient_rqmts()
		self.dry_matter_intake = 0
		self.manure_excretion = {}
		self.ration_formulation = {'objective': 0.00}
		self.DMIest = 0
		self.DBW = 0
		self.p_animal = 0
		self.p_intake = 0
		self.p_conc = 0
		self.p_excrt = 0
		self.body_weight = 0
		self.mature_body_weight = 0

	def init_from_animal(self, animal):
		self.id = animal.id
		self.breed = animal.breed
		self.birth_date = animal.birth_date
		self.days_born = animal.days_born
		self.culled = animal.culled
		self.do_not_breed = animal.do_not_breed
		self.events = animal.events
		self.body_weight = animal.body_weight
		self.mature_body_weight = animal.mature_body_weight
		
		self.daily_growth = 0
		self.nutrient_rqmts = {}
		self.set_default_nutrient_rqmts()
		self.dry_matter_intake = 0
		self.manure_excretion = {}
		self.ration_formulation = {'objective': 0.00}
		self.DMIest = 0
		self.DBW = 0
		self.p_animal = 0
		self.p_intake = 0
		self.p_conc = 0
		self.p_excrt = 0

	def set_default_nutrient_rqmts(self):
		"""
		Sets the default nutrient requirement values to be 0.
		"""
		for key in self.nutrients:
			self.nutrient_rqmts[key] = {'op': '', 'val': 0}

	def set_ration(self, ration, DMI):
		"""
		Sets this animal's ration formulation.

		Args:
			ration: dictionary representing the calculated ration
			DMI: the dry matter intake from @ration
		"""
		self.ration_formulation = ration
		self.dry_matter_intake = DMI

	def set_p_intake(self, p_intake, p_conc):
		"""
		Sets this animal's phosphorus intake.

		Args:
			p_intake: the phosphorus intake
			p_conc: the concentration of P in the ration
		"""
		self.p_intake = p_intake
		self.p_conc = p_conc

	def daily_p_update(self):
		"""
		Calculates this animal's daily phosphorus update.
		"""
		# (A.#.D.2) from P tracking
		self.p_animal = self.p_animal + self.p_intake - \
			self.p_excrt

	def set_p_purchased(self):
		"""
		Sets this animal's phosphorus value as a purchased animal.
		"""
		# (A.#.D.1) from P tracking
		self.p_animal = 0.0072 * self.body_weight * 1000

	def culled(self):
		"""
		Returns: True/False value indicating if culled
		"""
		return self.culled
