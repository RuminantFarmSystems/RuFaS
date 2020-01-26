"""
RUFAS: Ruminant Farm Systems Model
File name: heiferI.py
Author(s): Manfei Li, mli497@wisc.edu
			Militsa Sotirova, militsasotirova@gmail.com
Description: This file updates the heifer form wean to start breeding.
			Body weight gain with user input heifer average daily gain.

"""
###############################################################################

from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.ration.growing_heifer_ration import calculate_rqmts
from RUFAS.routines.animal.manure.growing_heifer_manure_excretion import \
	manure_calculations
import numpy as np


class HeiferI(Calf):
	# TODO: Body weight changed could be based on nutrition intake later from
	#  Ration Formulation

	def __init__(self, calf):
		"""
		Initialize the 1st heifer group from calf, pass calf information to
		heiferI.

		Args:
			calf: class calf with calf parameters
		"""
		super().init_from_calf(calf)

	def init_from_heiferI(self, heiferI):
		"""
		Initialize the 1st heifer group from animal base,
		pass animal information to heiferI

		Args:
			heiferI: animal to pass into the calf initialization

		Returns:

		"""
		super().init_from_calf(heiferI)

	def calc_nutrient_rqmts(self):
		"""
		Calculates this heiferI's nutrient requirements.
		"""
		self._nutrient_rqmts, self._DMIest, self._DBW = calculate_rqmts()

	def calc_manure_excretion(self, feed):
		"""
		Calculates and sets the manure excretion components.

		Args:
			feed: instance of the Feed class
		"""
		self._manure_excretion = manure_calculations()

	def update(self):
		"""
		Controls heifer's grow with average daily gain based on user's input
		until breeding start day. Here is the place to change growth rate with
		heifer feeding methods later when we have heifer nutrition from the
		ration furmulation module. Once reach the breeding start day,
		this heifer would be move to next stage, the heiferII stage

		Returns: the second stage of heifer -- breeding stage starts
		"""
		second_stage = False
		
		prev_weight = self._body_weight
		
		self._body_weight += np.random.normal(
			AnimalBase.config['avg_daily_gain_h'],
			AnimalBase.config['std_daily_gain_h'])
		
		self._daily_growth = self._body_weight - prev_weight
		
		self._days_born += 1
		if self._days_born == AnimalBase.config['breeding_start_day_h']:
			second_stage = True
			self._events.add_event(self._days_born, 'Breeding start')
			self._days_born -= 1  # will increment in next stage again

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
		""".format(
			self._id,
			self._birth_date,
			self._days_born,
			self._birth_weight,
			self._wean_weight,
			self._body_weight,
			AnimalBase.config['breeding_start_day_h'],
			str(self._events))

		return res_str
