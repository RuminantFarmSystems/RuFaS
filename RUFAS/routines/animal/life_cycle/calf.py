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

	def calc_manure_excretion(self, feed):
		"""
		Calculates and sets the manure excretion components.

		Args:
			feed: instance of the Feed class
		"""
		self.manure_excretion = manure_calculations()

	def phosphorus_retained(self, DMI):
		"""
		Calculates the phosphorus retained by the animal. Note that equation
		(A.#.B.2) (which deals with the P retained for fetal growth)
		is omitted because that is a calculation for HeiferII, HeiferIII, and
		Cows.

		Args:
			DMI: the Dry Matter Intake (kg)

		Returns: the amount of phosphorus retained by the animal
			in grams per day
		"""
		# amount of P required for maintenance (g/d) (A.#.B.1)
		p_maint = 0.0008 * DMI + 0.000002 * self.body_weight * 1000

		# OMITTED: calculation for p_gest (A.#.B.2)

		# amount of P required for growth (g/d) (A.#.B.3)
		p_growth = (0.0012 + 0.004635 * (self.mature_body_weight ** 0.22) * (
					self.body_weight ** (-0.22))) * \
			self.daily_growth / 0.96 * 1000

		# amount of P retained (g/d) (A.#.B.4)
		p_retained = p_maint + p_growth

		return p_retained

	def phosphorus_excreted(self, p_intake, total_manure):
		"""
		Calculates the phosphorus excreted by the animal. Note that equation
		(A.#.C.1) (which deals with the P in milk produced) is omitted because
		that is a calculation for Cows.

		Args:
			p_intake: amount of P in formulated ration (g)
			total_manure: amount of manure excreted by animal (kg)

		Returns:
			P excreted by animal
			WIP (water extractable inorganic P) fraction
			WOP (water extractable organic P) fraction
		"""
		# OMITTED: calculation for p_milk (A.#.C.1)

		# P in urine (g) (A.#.C.2)
		p_urine = 0.000002 * self.body_weight * 1000

		# P in feces (g) (A.#.C.3)
		p_feces = -2.3 + 0.63 * p_intake

		# P in manure (g) (A.#.C.4)
		p_manure = p_urine + p_feces

		# Water extractable Inorganic P (WIP) fraction - fraction of manure
		# compromised of inorganic water extractable P (A.#.C.5)
		WIP_frac = 0.50 * ((p_feces + p_urine) / (total_manure * 1000))

		# Water extractable Organic P (WOP) fraction - fraction of maure
		# compromised of organic water extractable P (A.#.C.6)
		WOP_frac = 0.05 * ((p_feces + p_urine) / (total_manure * 1000))

		# P excreted (g)
		p_excrt = p_manure

		return p_excrt, WIP_frac, WOP_frac

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
