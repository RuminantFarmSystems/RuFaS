'''
RUFAS: Ruminant Farm Systems Model
File name: heiferI.py
Author(s): Manfei Li, mli497@wisc.edu
Description: This file updates the heifer form wean to start breeding.
			Body weight gain with user input heifer average daily gain.
			TODO: Body weight changed could be based on nutrition intake later fron Ration Formulation
'''
###############################################################################

from RUFAS.routines.animal.calf import Calf
from RUFAS.routines.animal.animal_base import AnimalBase
import numpy as np

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
       	Calculates this heiferI's nutrient requirements.
    '''
	def calc_nutrient_rqmts(self):
		# self.nutrient_rqmts = ration.calculate_rqmts(BW, BCS, CBW, CI, concentrate, CP_Milk, DOP, DHD, DVD, DIM, fat_milk, lactose_milk, milk, parity, type, nutrients_list)
		self._nutrient_rqmts = {'FU': {'op': '<=', 'val': 7.566673489860807}, 'RU': {'op': '>=', 'val': 0}, 'ME_DM': {'op': '>=', 'val': 57.238188330372566}, 'RDP_DM': {'op': '>=', 'val': 2.0347001114951313}, 'RUP_DM': {'op': '>=', 'val': 1.2716733909335047}}

	'''
		Calculates and sets the manure excretion components.
	'''  
	def calc_manure_excretion(self, feed):
		
		# self.manure_excretion = manure_excretion.manure_calculations(this.ration_formulation, feed, BW, DIM, mPrt)
		self._manure_excretion = {"U": 0.340, 
			"TAN_s": 0.14, 
			"MN": 532.407, 
			"Mkg": 70.792, 
			"VSd": 7087.413, 
			"VSnd": 859.390}  

	'''
		Sets this animal's ration formulation.
		Args:
			ration_formulation: dictionary representing the calculated ration
	'''
	def set_ration(self, ration_formulation):
		self._ration_formulation = ration_formulation        

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
		
		prev_weight = self._body_weight
		
		self._body_weight += np.random.normal(AnimalBase.config['avg_daily_gain_h'], AnimalBase.config['std_daily_gain_h'])
		
		self._daily_growth = self._body_weight - prev_weight
		
		self._days_born += 1
		if self._days_born == AnimalBase.config['breeding_start_day_h']:
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
				   AnimalBase.config['breeding_start_day_h'],
				   str(self._events))

		return res_str