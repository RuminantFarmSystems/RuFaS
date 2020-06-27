'''
RUFAS: Ruminant Farm Systems Model
File name: calf.py
Author(s): Manfei Li, mli497@wisc.edu
		   Militsa Sotirova, militsasotirova@gmail.com
Description: This file updates the calf form birth to wean.
			Birth weight initialized with breed specific distributions,
			Gender determined with the semen type used,
			Sold or keep decision made by user input,
			Body weight gain with user input calf average daily gain.
			TODO: Body weight changed could be based on nutrition intake later from Ration Formulation
'''
###############################################################################

import numpy as np
from random import random
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.ration.calf_ration import calculate_rqmts
from RUFAS.routines.animal.manure.calf_manure_excretion import manure_calculations

class Calf(AnimalBase):
	'''
		Description:
			initialize calf at the time it was born
		Input:
			args.id: id of the cow
			args.breed: breed of the cow
			args.birth_date: the date of the simulation when the calf was born
			args.daysBorn: age of the animal
			(optional: include the following to assign cow information) 
			args.birth_weight: the birth weight of the cow
			args.body_weight: current body weight of the cow
			args.wean_weight: the wean weight of the cow
			args.events: events of the cow
		Output:
	'''
	def __init__(self, args):
		super().__init__(args)
		
		if 'birth_weight' in args:
			self.assign_calf_values(args)
		else:
			self.init_values()

	'''
		determine stillbirth, gender, and birth weight
	'''
	def init_values(self):
		# gender determined with gender ratio relates to semen type
		if AnimalBase.config['semen_type'] == 'conventional':
			male_calf_rate = AnimalBase.config['male_calf_rate_conventional_semen']
		else:
			male_calf_rate = AnimalBase.config['male_calf_rate_sexed_semen']
		if random() < male_calf_rate:
			self.gender = 'male'
		else:
			self.gender = 'female'

		# calf born, with stillbirth porbabality
		if random() < AnimalBase.config['still_birth_rate']:
			self.culled = True
			self.events.add_event(0, 'Still birth')

		# sell the male calves and the unwanted female calves (if AnimalBase.config['keep_female_calf_rate'] = 1, 
		# keep all the female calves in farm. if AnimalBase.config['keep_female_calf_rate = 0, sell all female calves)
		if self.gender == 'male' or random() > AnimalBase.config['keep_female_calf_rate']:
			self.sold = True
		else:
			self.sold = False

		# birthweight determined by breed specific distribution
		if self.breed == 'HO':
			self.birth_weight = np.random.normal(AnimalBase.config['birth_weight_avg_ho'], AnimalBase.config['birth_weight_std_ho'])
			while self.birth_weight < AnimalBase.config['birth_weight_avg_ho'] - 2 * AnimalBase.config['birth_weight_std_ho'] \
				or self.birth_weight > AnimalBase.config['birth_weight_avg_ho'] + 2 * AnimalBase.config['birth_weight_std_ho']:
				self.birth_weight = np.random.normal(AnimalBase.config['birth_weight_avg_ho'], AnimalBase.config['birth_weight_std_ho'])
		elif self.breed == 'JE':
			self.birth_weight = np.random.normal(AnimalBase.config['birth_weight_avg_je'], AnimalBase.config['birth_weight_std_je'])
			while self.birth_weight < AnimalBase.config['birth_weight_avg_je'] - 2 * AnimalBase.config['birth_weight_std_je'] \
				or self.birth_weight > AnimalBase.config['birth_weight_avg_je'] + 2 * AnimalBase.config['birth_weight_std_je']:
				self.birth_weight = np.random.normal(AnimalBase.config['birth_weight_avg_je'], AnimalBase.config['birth_weight_std_je'])
		self.body_weight = self.birth_weight
		self.wean_weight = 0
	
	'''
		assign calf with given values
	'''
	def assign_calf_values(self, args):
		self.culled = False
		self.sold = False
		self.gender = 'female'
		self.birth_weight = args['birth_weight']
		self.body_weight = args['body_weight']
		self.wean_weight = args['wean_weight']
		self.events.init_from_string(args['events'])

	'''
		get current information from the calf
	'''
	def get_calf_values(self):
		values = {
            'id' : self.id,
            'breed' : self.breed,
            'birth_date' : self.birth_date,
            'days_born' : self.days_born,
            'birth_weight' : self.birth_weight,
            'body_weight' : self.body_weight,
            'wean_weight' : self.wean_weight,
            'events' : str(self.events)
		}
		return values
	
	'''
       	Calculates this calf's nutrient requirements.
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
			controls calf's grow with average daily gain based on user's input until wean day
			calculate the wean weight at wean day
			here is the place to change growth rate with calf feeding methods later when we have calf nutrition from the ration furmulation module
		Input:
		Output:
			wean_day: time when calf is weaned -- stop be fed with milk
	'''
	def update(self):
		wean_day = False
		
		prev_weight = self.body_weight
		
		self.days_born += 1
		if self.days_born == AnimalBase.config['wean_day']:
			wean_day = True
			self.wean_weight = self.body_weight
			self.events.add_event(self.days_born, 'Wean Day')
			self.days_born -= 1 # will increment by 1 again in heifer update
		else:
			gained_weight = np.random.normal(AnimalBase.config['avg_daily_gain_c'], AnimalBase.config['std_daily_gain_c'])
			while gained_weight < AnimalBase.config['avg_daily_gain_c'] - 2 * AnimalBase.config['std_daily_gain_c'] \
				or gained_weight > AnimalBase.config['avg_daily_gain_c'] + 2 * AnimalBase.config['std_daily_gain_c']:
				gained_weight = np.random.normal(AnimalBase.config['avg_daily_gain_c'], AnimalBase.config['std_daily_gain_c'])
			self.body_weight += gained_weight
		
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
			""".format(self.id,
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
			""".format(self.id,
					self.birth_date,
					self.days_born,
					str(self.events))
		return res_str
