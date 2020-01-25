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
		self._sold = False
		# gender determined with gender ratio relates to semen type
		if AnimalBase.config['semen_type'] == 'conventional':
			male_calf_rate = \
				AnimalBase.config['male_calf_rate_conventional_semen']
		else:
			male_calf_rate = AnimalBase.config['male_calf_rate_sexed_semen']
		if random() < male_calf_rate:
			self._gender = 'male'
		else:
			self._gender = 'female'

		# calf born, with stillbirth porbabality
		if random() < AnimalBase.config['still_birth_rate']:
			self._culled = True
			self._events.add_event(0, 'Still birth')
			return

		# sell the male calves and the unwanted female calves
		# (if AnimalBase.config['keep_female_calf_rate'] = 1,
		# keep all the female calves in farm.
		# if AnimalBase.config['keep_female_calf_rate = 0,
		# sell all female calves)
		if self._gender == 'male' or random() > \
			AnimalBase.config['keep_female_calf_rate']:
			self._sold = True
			return
		else:
			self._sold = False

		# birth weight determined by breed specific distribution
		if self._breed == 'HO':
			self._birth_weight = np.random.normal(
				AnimalBase.config['birth_weight_avg_ho'],
				AnimalBase.config['birth_weight_std_ho'])
		elif self._breed == 'JE':
			self._birth_weight = np.random.normal(
				AnimalBase.config['birth_weight_avg_je'],
				AnimalBase.config['birth_weight_std_je'])
		self._body_weight = self._birth_weight
		self._wean_weight = 0

	def init_from_calf(self, calf):
		"""
		Initialize calf value from class calf, for coding purposes

		Args:
			calf: initialized values from the first day
		"""
		super().init_from_animal(calf)
		self._culled = calf._culled
		self._sold = calf._sold
		self._gender = calf._gender
		self._sold = calf._sold
		self._birth_weight = calf._birth_weight
		self._body_weight = calf._body_weight
		self._wean_weight = calf._wean_weight

	def calc_nutrient_rqmts(self):
		"""
		Calculates this calf's nutrient requirements.
		"""
		self._nutrient_rqmts, self._DMIest, self._DBW = calculate_rqmts()

	def calc_manure_excretion(self, feed):
		"""
		Calculates and sets the manure excretion components.

		Args:
			feed: instance of the Feed class
		"""
		self._manure_excretion = manure_calculations()

	def set_ration(self, ration_formulation, feed):
		"""
		Sets this animal's ration formulation.

		Args:
			ration_formulation: dictionary representing the calculated ration
			feed: instance of the Feed class
		"""
		self._ration_formulation = ration_formulation  
		self._dry_matter_intake = 0
		for key in ration_formulation:
			if key in feed.managed_feed_names:
				DM_feed_amount = ration_formulation[key]
				self._dry_matter_intake += DM_feed_amount

	def update(self):
		"""
		Controls calf's grow with average daily gain based on user's input until
		wean day. Calculate the wean weight at wean day. Here is the place to
		change growth rate with calf feeding methods later when we have calf
		nutrition from the ration formulation module.

		Returns: time when calf is weaned -- stop be fed with milk
		"""
		wean_day = False
		
		prev_weight = self._body_weight
		
		self._days_born += 1
		if self._days_born == AnimalBase.config['wean_day']:
			wean_day = True
			self._wean_weight = self._body_weight
			self._events.add_event(self._days_born, 'Wean Day')
			self._days_born -= 1  # will increment by 1 again in heifer update
		else:
			self._body_weight += np.random.normal(
				AnimalBase.config['avg_daily_gain_c'],
				AnimalBase.config['std_daily_gain_c'])
		
		self._daily_growth = self._body_weight - prev_weight
		
		return wean_day

	def __str__(self):
		if not self._culled:
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
				self._id,
				self._birth_date,
				self._days_born,
				self._birth_weight,
				self._body_weight,
				AnimalBase.config['wean_day'],
				str(self._events))
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
				self._id,
				self._birth_date,
				self._days_born,
				str(self._events))
		return res_str
