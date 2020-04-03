"""
RUFAS: Ruminant Farm Systems Model
File name: calf.py
Author(s): Manfei Li, mli497@wisc.edu
			Militsa Sotirova, militsasotirova@gmail.com
Description: This file updates the calf form birth to wean.
			Birth weight initialized with breed specific distributions,
			Gender determined with the semen type used,
			Sold or keep decision made by user input,
			Body weight gain with user input calf average daily gain.
"""
###############################################################################

import numpy as np
from random import random
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.ration.calf_ration import calculate_rqmts
from RUFAS.routines.animal.manure.calf_manure_excretion import\
	manure_calculations


class Calf(AnimalBase):
	# TODO: Body weight changed could be based on nutrition intake later from
	#  Ration Formulation

	def __init__(self, args):
		"""
		Initialize calf at the time it was born, determine stillbirth, gender,
		and birth weight.

		Args:
			args:
				args.breed: breed of the cow
				args.date: the date of the simulation when the calf was born
				args.daysBorn: age of the animal
		"""
		super().__init__(args)
		self.sold = False
		# gender determined with gender ratio relates to semen type
		if AnimalBase.config['semen_type'] == 'conventional':
			male_calf_rate = \
				AnimalBase.config['male_calf_rate_conventional_semen']
		else:
			male_calf_rate = AnimalBase.config['male_calf_rate_sexed_semen']
		if random() < male_calf_rate:
			self.gender = 'male'
		else:
			self.gender = 'female'

		# calf born, with stillbirth probability
		if random() < AnimalBase.config['still_birth_rate']:
			self.culled = True
			self.events.add_event(0, 'Still birth')
			return

		# sell the male calves and the unwanted female calves
		# (if AnimalBase.config['keep_female_calf_rate'] = 1,
		# keep all the female calves in farm.
		# if AnimalBase.config['keep_female_calf_rate = 0,
		# sell all female calves)
		if self.gender == 'male' or random() > \
			AnimalBase.config['keep_female_calf_rate']:
			self.sold = True
			return
		else:
			self.sold = False
		# birth weight determined by breed specific distribution
		if self.breed == 'HO':
			self.birth_weight = np.random.normal(
				AnimalBase.config['birth_weight_avg_ho'],
				AnimalBase.config['birth_weight_std_ho'])
		elif self.breed == 'JE':
			self.birth_weight = np.random.normal(
				AnimalBase.config['birth_weight_avg_je'],
				AnimalBase.config['birth_weight_std_je'])
		self.body_weight = self.birth_weight
		self.wean_weight = 0
		self.mature_body_weight = np.random.triangular(550, 700, 1000)

		self.p_animal = args['p_init']

	def init_from_calf(self, calf):
		"""
		Initialize calf value from class calf, for coding purposes

		Args:
			calf: initialized values from the first day
		"""
		super().init_from_animal(calf)
		self.culled = calf.culled
		self.sold = calf.sold
		self.gender = calf.gender
		self.sold = calf.sold
		self.birth_weight = calf.birth_weight
		self.body_weight = calf.body_weight
		self.wean_weight = calf.wean_weight
		self.mature_body_weight = calf.mature_body_weight

	def calc_nutrient_rqmts(self):
		"""
		Calculates this calf's nutrient requirements.
		"""
		self.nutrient_rqmts, self.DMIest, self.DBW = calculate_rqmts()

	def calc_base_manure(self):
		"""
		Calculates the values needed for animal class manure calculations.

		Returns:
			p_urine: amount of P required for urine production (g)
			p_feces_excrt: amount of P excreted by an animal (g)
		"""
		# amount of P required for urine production (g) (A.3.A.1)
		p_urine = 0.000002 * self.body_weight * 1000

		# excess P in the diet (g) (A.3.A.2)
		self.p_excess = self.p_intake - self.p_req

		# amount of P excreted by an animal (g) (A.3.A.3)
		if self.dP_reserves == 0 and self.p_intake >= self.p_req:
			p_feces_excrt = self.p_intake - self.p_req + self.p_maint_feces
		elif self.dP_reserves < 0 and self.p_intake >= self.p_req and \
				self.p_excess >= self.dP_reserves / 0.7:
			p_feces_excrt = self.p_intake - self.p_req + self.p_maint_feces - \
							self.dP_reserves
		else:
			p_feces_excrt = self.p_maint_feces

		return p_urine, p_feces_excrt

	def calc_manure_excretion(self, feed):
		"""
		Calculates and sets the manure excretion components.

		Args:
			feed: instance of the Feed class
		"""
		p_urine, p_feces_excrt = self.calc_base_manure()

		self.manure_excretion = manure_calculations(p_feces_excrt, p_urine)
		self.p_excrt = self.manure_excretion['p_excrt']

	def phosphorus_rqmts(self, DMI):
		"""
		Calculates and sets the animal's phosphorus requirement.

		Args:
			DMI: the Dry Matter Intake (kg)
		"""
		# amount of P required for endogenous losses (g) (A.1A-D.C.1)
		self.p_maint_feces = 0.0008 * DMI * 1000

		# amount pf P required for urine production (g) (A.1A-F.C.2)
		p_urine = 0.000002 * self.body_weight * 1000

		# absorbed P retained for growth (g) (A.1A-F.C.3)
		self.p_growth = \
			(0.0012 + 0.004635 * (self.mature_body_weight ** 0.22) *
				(self.body_weight ** (-0.22))) * \
			self.daily_growth / 0.96 * 1000

		# absorbed P required by the animal (g) (A.1A-F.C.6)
		p_absorb = p_urine + self.p_maint_feces + self.p_growth

		# requirement of P from the ration (g) (A.1A.C.7)
		self.p_req = p_absorb / 0.90

	def update(self):
		"""
		Controls calf's grow with average daily gain based on user's input until
		wean day. Calculate the wean weight at wean day. Here is the place to
		change growth rate with calf feeding methods later when we have calf
		nutrition from the ration formulation module.

		Returns: time when calf is weaned -- stop be fed with milk
		"""
		wean_day = False
		
		prev_weight = self.body_weight
		
		self.days_born += 1
		if self.days_born == AnimalBase.config['wean_day']:
			wean_day = True
			self.wean_weight = self.body_weight
			self.events.add_event(self.days_born, 'Wean Day')
			self.days_born -= 1  # will increment by 1 again in heifer update
		else:
			self.body_weight += np.random.normal(
				AnimalBase.config['avg_daily_gain_c'],
				AnimalBase.config['std_daily_gain_c'])
		
		self.daily_growth = self.body_weight - prev_weight
		
		return wean_day

	def __str__(self):
		if not self.culled:
			res_str = """
				==> Calf: \n
				ID: {} \n
				Birth Date: {}\n
				Days Born: {}\n
				Birth Weight: {}kg\n
				Body Weight: {}kg\n
				Wean Day: {}\n
				Life Events: \n
				{}
			""".format(
				self.id,
				self.birth_date,
				self.days_born,
				self.birth_weight,
				self.body_weight,
				AnimalBase.config['wean_day'],
				str(self.events))
		else:
			res_str = """
				==> Calf: \n
				Still Birth: True \n
				ID: {} \n
				Birth Date: {}\n
				Days Born: {}\n
				Life Events: \n
				{}
			""".format(
				self.id,
				self.birth_date,
				self.days_born,
				str(self.events))
		return res_str
