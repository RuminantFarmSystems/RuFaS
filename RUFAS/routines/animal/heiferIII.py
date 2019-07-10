'''
RUFAS: Ruminant Farm Systems Model
File name: heiferIII.py
Author(s): Manfei Li, mli497@wisc.edu
Description: This file updates the heifer form close to calving to calving,
            replacement from other farms are enter the herd in this stage, and heifers can be sold in this stage.
			Body weight gain with user input average daily gain,
			once mature body weight or grow end day reached, grow stop.
			TODO: Body weight changed could be based on nutrition intake later fron Ration Formulation.
			TODO: Rank heifers to enter the herd or sold
'''
###############################################################################

import numpy as np
from RUFAS.routines.animal.heiferII import HeiferII
from RUFAS.routines.animal.animal_base import AnimalBase
from random import random

class HeiferIII(HeiferII):
    '''
		Description:
			initialize the heifer in this stage from the second stage
        Input:
			heiferI: first stage of heifer, pass heifer information from heiferI
        Output:
	'''
    def __init__(self, heiferII):
        super().init_from_heiferII(heiferII)

    '''
		Description:
            initialize the heifer in this stage from the second stage and initialize the repro program parameters for coding purpose
		Input:
			heiferII: another heifer out of the herd
		Output:
	'''
    def init_from_heiferIII(self, heiferIII):
        super().init_from_heiferII(heiferIII)

    '''
           Calculates this heiferIII's nutrient requirements.
    '''
    def calc_nutrient_rqmts(self):
        # self.nutrient_rqmts = ration.calculate_rqmts(BW, BCS, CBW, CI, concentrate, CP_Milk, DOP, DHD, DVD, DIM, fat_milk, lactose_milk, milk, parity, type, nutrients_list)
        self._nutrient_rqmts = {'FU': {'op': '<=', 'val': 7.566673489860807}, 'RU': {'op': '>=', 'val': 0}, 'ME_DM': {'op': '>=', 'val': 57.238188330372566}, 'RDP_DM': {'op': '>=', 'val': 2.0347001114951313}, 'RUP_DM': {'op': '>=', 'val': 1.2716733909335047}}       
        self._DMIest = 27.620363504458798 
        self._DBW = -0.4125
        
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
            next to it could build the fuction of ranking heifers
		Input:
		Output:
            cow_stage: heifer close to calving, move to cow stage
	'''
    def update(self):
        cow_stage = False
        self._days_born += 1

        if self._preg:
            self._days_in_preg += 1
            
        prev_weight = self._body_weight

        if self._days_born < AnimalBase.config['grow_end_day']:
            # Heifer can only grow to a maximum weight of mature_body_weight
            if self._body_weight < AnimalBase.config['mature_body_weight']:
                self._body_weight += np.random.normal(AnimalBase.config['avg_daily_gain_h'], AnimalBase.config['std_daily_gain_h'])
            if self._body_weight > AnimalBase.config['mature_body_weight']:
                self._body_weight = AnimalBase.config['mature_body_weight']
                self._mature_body_weight = self._body_weight
                self._events.add_event(self._days_born, 'Mature body weight prior to grow end day')
        
        self._daily_growth = self._body_weight - prev_weight
        
        if self._days_born == AnimalBase.config['grow_end_day']:
            self._mature_body_weight = self._body_weight
            self._events.add_event(self._days_born, 'Mature body weight')


        if self._days_in_preg == self._gestation_length:
            self._days_born -= 1 # will be incremented again in next stage
            cow_stage = True
        return cow_stage

    def __str__(self):
        return 'heiferIII'
        '''
        res_str = """
			==> Heifer III: \n
			ID: {} \n
			Birth Date: {}\n
			Days Born: {}\n
			Body Weight: {}kg\n
			Breed Start Day: {}\n
			Repro Method: {}\n
			Days in pregnancy: {}\n
            Gestation Length: {}\n
			Life Events: \n
			{}
		""".format(self._id,
				   self._birth_date,
				   self._days_born,
				   self._body_weight,
				   AnimalBase.config['breeding_start_day_h'],
				   self._repro_program,
				   self._days_in_preg,
                   self._gestation_length,
				   str(self._events))

        return res_str
        '''