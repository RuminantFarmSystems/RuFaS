"""
RUFAS: Ruminant Farm Systems Model
File name: animal_base.py
Author(s): Manfei Li, mli497@wisc.edu
           Militsa Sotirova, militsasotrirova@gmail.com
	   Tayler Hansen, tlhansen@cornell.edu
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
		self.p_req = 0
		self.dP_reserves = 0
		self.p_excess = 0
		self.p_gest = 0
		self.p_growth = 0
		self.p_maint_feces = 0

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
		
		self.daily_growth = animal.daily_growth
		self.nutrient_rqmts = animal.nutrient_rqmts
		self.set_default_nutrient_rqmts()
		self.dry_matter_intake = animal.dry_matter_intake
		self.manure_excretion = animal.manure_excretion
		self.ration_formulation = animal.ration_formulation
		self.DMIest = animal.DMIest
		self.DBW = animal.DBW
		self.p_animal = animal.p_animal
		self.p_intake = animal.p_intake
		self.p_conc = animal.p_conc
		self.p_excrt = animal.p_excrt
		self.p_req = animal.p_req
		self.dP_reserves = animal.dP_reserves
		self.p_excess = animal.p_excess
		self.p_gest = animal.p_gest
		self.p_growth = animal.p_growth
		self.p_maint_feces = animal.p_maint_feces

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
		# Amount of P in diet greater than animal requirements (A.1G.A.1)
		self.p_excess = max(self.p_intake - self.p_req, 0)

		# change in body P reserves (g), must be <= 0 (A.1G.A.2)
		prev_dP_reserves = self.dP_reserves

		if self.p_intake < self.p_req:
			self.dP_reserves = self.p_intake - self.p_req + self.dP_reserves
		elif self.p_intake >= self.p_req and self.dP_reserves < 0:
			self.dP_reserves = 0.7 * self.p_excess + self.dP_reserves
		else:
			self.dP_reserves = 0

		# amount of P in the animal (A.1G.A.3)
		if self.id == 7417:
			print(self.days_born, self.p_animal, self.p_intake, self.p_req, self.p_excess, self.dP_reserves)
		self.p_animal = self.p_animal + self.p_gest + self.p_growth + (self.dP_reserves - prev_dP_reserves)
		# if self.p_animal < 0:
		# 	print(self.id)

	def calc_base_manure(self):
		"""
		Calculates the values needed for animal class manure calculations.

		Returns:
			p_urine: amount of P required for urine production (g)
			p_feces_excrt: amount of P excreted by an animal (g)
		"""
		# amount of P required for urine production (g) (A.1G.B.1)
		p_urine = 0.000002 * self.body_weight * 1000

		# excess P in the diet (g) (A.1G.A.1)
		self.p_excess = max(self.p_intake - self.p_req, 0)

		# amount of P excreted by an animal (g) (A.1G.B.2)
		if self.dP_reserves == 0 and self.p_intake >= self.p_req:
			p_feces_excrt = self.p_intake - self.p_req + self.p_maint_feces
		elif self.dP_reserves < 0 and self.p_intake >= self.p_req and \
				self.p_excess >= (-1) * self.dP_reserves / 0.7:
			p_feces_excrt = self.p_intake - self.p_req + self.p_maint_feces + \
							self.dP_reserves / 0.7
		else:
			p_feces_excrt = self.p_maint_feces

		return p_urine, p_feces_excrt

	def set_p_purchased(self):
		"""
		Sets this animal's phosphorus value as a purchased animal.
		"""
		# (A.1G.C.1) from P tracking
		self.p_animal = 0.0072 * self.body_weight * 1000

	def culled(self):
		"""
		Returns: True/False value indicating if culled
		"""
		return self.culled
