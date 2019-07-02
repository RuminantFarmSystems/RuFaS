'''
RUFAS: Ruminant Farm Systems Model
File name: heiferI.py
Author(s): Manfei Li, mli497@wisc.edu
Description: This file updates the heifer form wean to start breeding.
			Body weight gain with user input heifer average daily gain.
			TODO: Body weight changed could be based on nutrition intake later fron Ration Formulation
'''
###############################################################################

from calf import Calf
from animal_base import AnimalBase
from config import Config
import numpy as np

config = Config()

class HeiferI(Calf):
	'''
		Description:
			initialize the 1st heifer group from calf, pass calf information to heiferI
		Input:
			calf: class calf with calf parameters
		Output:
	'''
	def __init__(self, calf):
		super().init_from_calf(calf)

	'''
		Description:
			initialize the 1st heifer group from animal base, pass animal information to heiferI
	'''
	def init_from_heiferI(self, heiferI):
		super().init_from_calf(heiferI)

	'''
		Description:
			controls heifer's grow with average daily gain based on user's input untill breeding start day
			here is the place to change growth rate with heifer feeding methods later when we have heifer nutrition from the ration furmulation module
			once reach the breeding start day, this heifer would be move to next stage, the heiferII stage
		Input:
		Output:
			second_stage: the second stage of heifer -- breeding stage starts
	'''
	def update(self):
		second_stage = False
		self._body_weight += np.random.normal(config.avg_daily_gain_h, config.std_daily_gain_h)
		self._days_born += 1
		if self._days_born == config.breeding_start_day_h:
			second_stage = True
			self._events.add_event(self._days_born, 'Breeding start')
			self._days_born -= 1 # will increment in next stage again

		return second_stage

	def __str__(self):
		res_str = """
			==> Heifer I: \n
			ID: {} \n
			Birth Date: {}\n
			Days Born: {}\n
			Birth Weight: {}kg\n
			Wean Weight: {}kg\n
			Body Weight: {}kg\n
			Breeding Start Day: {}\n
			Life Events: \n
			{}
		""".format(self._id,
				   self._birth_date,
				   self._days_born,
				   self._birth_weight,
				   self._wean_weight,
				   self._body_weight,
				   config.breeding_start_day_h,
				   str(self._events))

		return res_str