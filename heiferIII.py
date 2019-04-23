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
from heiferII import HeiferII
from random import random
from config import Config

config = Config()

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

        if self._days_born < config.grow_end_day:
            # Heifer can only grow to a maximum weight of mature_body_weight
            if self._body_weight < config.mature_body_weight:
                self._body_weight += np.random.normal(config.avg_daily_gain_h, config.std_daily_gain_h)
            if self._body_weight > config.mature_body_weight:
                self._body_weight = config.mature_body_weight
                self._mature_body_weight = self._body_weight
                self._events.add_event(self._days_born, 'Mature body weight prior to grow end day')

        if self._days_born == config.grow_end_day:
            self._mature_body_weight = self._body_weight
            self._events.add_event(self._days_born, 'Mature body weight')


        if self._days_in_preg == self._gestation_length:
            self._days_born -= 1 # will be incremented again in next stage
            cow_stage = True

        return cow_stage

    def __str__(self):
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
				   config.breeding_start_day_h,
				   self._repro_program,
				   self._days_in_preg,
                   self._gestation_length,
				   str(self._events))

        return res_str