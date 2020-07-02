"""
RUFAS: Ruminant Farm Systems Model
File name: heiferIII.py
Author(s): Manfei Li, mli497@wisc.edu
           Militsa Sotirova, militsasotirova@gmail.com
Description: This file updates the heifer form close to calving to calving,
            replacement from other farms are enter the herd in this stage, and
            heifers can be sold in this stage. Body weight gain with user input
            average daily gain, once mature body weight or grow end day reached,
            grow stop.
"""
###############################################################################

import numpy as np
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.ration.growing_heifer_ration import calculate_rqmts
from RUFAS.routines.animal.manure.growing_heifer_manure_excretion import \
    manure_calculations


class HeiferIII(HeiferII):
    # TODO: Body weight changed could be based on nutrition intake later from
    #  Ration Formulation.
    # TODO: Rank heifers to enter the herd or sold
    
    def __init__(self, args):
        """
        Description:
			initialize the heifer in this stage from the second stage
        Input:
			args: same as heiferII
        """
        super().__init__(args)

    def get_heiferIII_values(self):
        """
        Get current information from the heiferIII
        """
        return self.get_heiferII_values()

    def calc_nutrient_rqmts(self):
        """
        Calculates this heiferIII's nutrient requirements.
        """
        self.nutrient_rqmts, self.DMIest, self.DBW = calculate_rqmts()

    def calc_manure_excretion(self, feed):
        """
        Calculates and sets the manure excretion components.

        Args:
            feed: instance of the Feed class
        """
        p_urine, p_feces_excrt = self.calc_base_manure()

        self.p_excrt, self.manure_excretion = \
            manure_calculations(p_feces_excrt, p_urine)

    def update(self):
        """
        Controls heifer's grow with average daily gain based on user's input
        until breeding start day here is the place to change growth rate with
        heifer feeding methods later when we have heifer nutrition from the
        ration formulation module next to it could build the function of
        ranking heifers.

        Returns: cow_stage - heifer close to calving, move to cow stage
        """
        self.body_weight_lst.append(self.body_weight)
        cow_stage = False
        self.days_born += 1

        if self.preg:
            self.days_in_preg += 1

        prev_weight = self.body_weight

        if self.days_born < AnimalBase.config['grow_end_day']:
            # Heifer can only grow to a maximum weight of mature_body_weight
            if self.body_weight < AnimalBase.config['mature_body_weight']:
                gained_weight = np.random.normal(
                    AnimalBase.config['avg_daily_gain_h'], 
                    AnimalBase.config['std_daily_gain_h'])
                while gained_weight < AnimalBase.config['avg_daily_gain_h'] \
                    - 2 * AnimalBase.config['std_daily_gain_h'] \
                    or gained_weight > AnimalBase.config['avg_daily_gain_h'] \
                        + 2 * AnimalBase.config['std_daily_gain_h']:
                    gained_weight = np.random.normal(
                        AnimalBase.config['avg_daily_gain_h'], 
                        AnimalBase.config['std_daily_gain_h'])
                self.body_weight += gained_weight
            if self.body_weight > AnimalBase.config['mature_body_weight']:
                self.body_weight = AnimalBase.config['mature_body_weight']
                self.mature_body_weight = self.body_weight
                self.events.add_event(self.days_born, 
                'Mature body weight prior to grow end day')
        
        self.daily_growth = self.body_weight - prev_weight
        
        if self.days_born == AnimalBase.config['grow_end_day']:
            self.mature_body_weight = self.body_weight
            self.events.add_event(self.days_born, 'Mature body weight')

        if self.days_in_preg == self.gestation_length:
            self.days_born -= 1  # will be incremented again in next stage
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
        """.\
            format(self.id,
                   self.birth_date,
                   self.days_born,
                   self.body_weight,
                   AnimalBase.config['breeding_start_day_h'],
                   self.repro_program,
                   self.days_in_preg,
                   self.gestation_length,
                   str(self.events))

        return res_str
