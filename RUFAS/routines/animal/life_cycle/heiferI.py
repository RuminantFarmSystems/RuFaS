'''
RUFAS: Ruminant Farm Systems Model
File name: heiferI.py
Author(s): Manfei Li, mli497@wisc.edu
	       Militsa Sotirova, militsasotirova@gmail.com
Description: This file updates the heifer form wean to start breeding.
			Body weight gain with user input heifer average daily gain.
			TODO: Body weight changed could be based on nutrition intake later fron Ration Formulation
'''
###############################################################################

from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.ration.growing_heifer_ration import calculate_rqmts
from RUFAS.routines.animal.manure.growing_heifer_manure_excretion import manure_calculations
import numpy as np

class HeiferI(Calf):
	'''
		Description:
			initialize the 1st heifer group from calf information
		Input:
			args: same as calf
		Output:
	'''
	def __init__(self, args):
		super().__init__(args)

	'''
		get current information from the heiferI
	'''
	def get_heiferI_values(self):
		return self.get_calf_values()
		
	'''
       	Calculates this heiferI's nutrient requirements.
    '''
	def calc_nutrient_rqmts(self):
		self.nutrient_rqmts, self.DMIest, self.DBW = calculate_rqmts()
		
	'''
		Calculates and sets the manure excretion components.
	'''  
	def calc_manure_excretion(self, feed):
		self.manure_excretion = manure_calculations()

	'''
		Sets this animal's ration formulation.
		Args:
			ration_formulation: dictionary representing the calculated ration
	'''
	def set_ration(self, ration_formulation, feed):
		self.ration_formulation = ration_formulation  
		self.dry_matter_intake = 0
		for key in ration_formulation:
			if key in feed.managed_feed_names:
				DM_feed_amount = ration_formulation[key]
				self.dry_matter_intake += DM_feed_amount   

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
		
		prev_weight = self.body_weight

		gained_weight = np.random.normal(AnimalBase.config['avg_daily_gain_h'], AnimalBase.config['std_daily_gain_h'])
		while gained_weight < AnimalBase.config['avg_daily_gain_h'] - 2 * AnimalBase.config['std_daily_gain_h'] \
			or gained_weight > AnimalBase.config['avg_daily_gain_h'] + 2 * AnimalBase.config['std_daily_gain_h']:
			gained_weight = np.random.normal(AnimalBase.config['avg_daily_gain_h'], AnimalBase.config['std_daily_gain_h'])
		
		self.body_weight += gained_weight
		
		self.daily_growth = self.body_weight - prev_weight
		
		self.days_born += 1
		if self.days_born == AnimalBase.config['breeding_start_day_h']:
			second_stage = True
			self.events.add_event(self.days_born, 'Breeding start')
			self.days_born -= 1 # will increment in next stage again

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
		""".format(self.id,
				   self.birth_date,
				   self.days_born,
				   self.birth_weight,
				   self.wean_weight,
				   self.body_weight,
				   AnimalBase.config['breeding_start_day_h'],
				   str(self.events))

		return res_str