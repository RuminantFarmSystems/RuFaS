'''
RUFAS: Ruminant Farm Systems Model
File name: calf.py
Author(s): Manfei Li, mli497@wisc.edu
Description: This file updates the calf form birth to wean.
			Birth weight initialized with breed specific distributions,
			Gender determined with the semen type used,
			Sold or keep decision made by user input,
			Body weight gain with user input calf average daily gain.
			TODO: Body weight changed could be based on nutrition intake later fron Ration Formulation
'''
###############################################################################

import numpy as np
from random import random
from animal_base import AnimalBase
from config import Config

config = Config()

class Calf(AnimalBase):
	'''
		Description:
			initialize calf at the time it was born, determine stillbirth, gender, and birth weight
		Input:
			args.breed: breed of the cow
			args.date: the date of the simulation when the calf was born
			args.daysBorn: age of the animal
		Output:
	'''
	def __init__(self, args):
		super().__init__(args)
		self._sold = False

		# gender determined with gender ratio relates to semen type
		if config.semen_type == 'conventional':
			male_calf_rate = config.male_calf_rate_conventional_semen
		else:
			male_calf_rate = config.male_calf_rate_sexed_semen
		if random() < male_calf_rate:
			self._gender = 'male'
		else:
			self._gender = 'female'

		# calf born, with stillbirth porbabality
		if random() < config.still_birth_rate:
			self._culled = True
			self._events.add_event(0, 'Still birth')
			return

		# sell the male calves and the unwanted female calves (if config.keep_female_calf_rate = 1, keep all the female calves in farm. if config.keep_female_calf_rate = 0, sell all female calves)
		if self._gender == 'male' or random() > config.keep_female_calf_rate:
			self._sold = True
			return
		else:
			self._sold = False

		# birthweight determined by breed specific distribution
		if self._breed == 'HO':
			self._birth_weight = np.random.normal(config.birth_weight_avg_ho, config.birth_weight_std_ho)
		elif self._breed == 'JE':
			self._birth_weight = np.random.normal(config.birth_weight_avg_je, config.birth_weight_std_je)
		self._body_weight = self._birth_weight
		self._wean_weight = 0

	'''
		Description:
			initialize calf value from class calf, for coding purpose
		Input:
			calf: initialed values from the first day
		Output:
	'''
	def init_from_calf(self, calf):
		super().init_from_animal(calf)
		self._culled = calf._culled
		self._sold = calf._sold
		self._gender = calf._gender
		self._sold = calf._sold
		self._birth_weight = calf._birth_weight
		self._body_weight = calf._body_weight
		self._wean_weight = calf._wean_weight

	'''
		Description:
			controls calf's grow with average daily gain based on user's input untill wean day
			caculate the wean weight at wean day
			here is the place to change growth rate with calf feeding methods later when we have calf nutrition from the ration furmulation module
		Input:
		Output:
			wean_day: time when calf is weaned -- stop be fed with milk
	'''
	def update(self):
		wean_day = False

		self._days_born += 1
		if self._days_born == config.wean_day:
			wean_day = True
			self._wean_weight = self._body_weight
			self._events.add_event(self._days_born, 'Wean Day')
			self._days_born -= 1 # will increment by 1 again in heifer update
		else:
			self._body_weight += np.random.normal(config.avg_daily_gain_c, config.std_daily_gain_c)

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
			""".format(self._id,
					self._birth_date,
					self._days_born,
					self._birth_weight,
					self._body_weight,
					config.wean_day,
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
			""".format(self._id,
					self._birth_date,
					self._days_born,
					str(self._events))
		return res_str
