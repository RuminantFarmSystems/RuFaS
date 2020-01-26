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

    def __init__(self, heiferII):
        """
        Args:
            heiferII: the heifer from the second stage that has grown into a
            heifer of the third stage
        """
        self._dry_matter_intake = 0
        super().init_from_heiferII(heiferII)

    def init_from_heiferIII(self, heiferIII):
        """
        Initialize the heifer in this stage from the second stage and initialize
        the repro program parameters for coding purposes

        Args:
            heiferIII: another heifer out of the herd
        """
        super().init_from_heiferII(heiferIII)

    def calc_nutrient_rqmts(self):
        """
        Calculates this heiferIII's nutrient requirements.
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
        until breeding start day here is the place to change growth rate with
        heifer feeding methods later when we have heifer nutrition from the
        ration formulation module next to it could build the function of
        ranking heifers.

        Returns: cow_stage - heifer close to calving, move to cow stage
        """
        cow_stage = False
        self._days_born += 1

        if self._preg:
            self._days_in_preg += 1

        prev_weight = self._body_weight

        if self._days_born < AnimalBase.config['grow_end_day']:
            # Heifer can only grow to a maximum weight of mature_body_weight
            if self._body_weight < AnimalBase.config['mature_body_weight']:
                self._body_weight += np.random.normal(
                    AnimalBase.config['avg_daily_gain_h'],
                    AnimalBase.config['std_daily_gain_h'])
            if self._body_weight > AnimalBase.config['mature_body_weight']:
                self._body_weight = AnimalBase.config['mature_body_weight']
                self._mature_body_weight = self._body_weight
                self._events.add_event(
                    self._days_born,
                    'Mature body weight prior to grow end day')

        self._daily_growth = self._body_weight - prev_weight

        if self._days_born == AnimalBase.config['grow_end_day']:
            self._mature_body_weight = self._body_weight
            self._events.add_event(self._days_born, 'Mature body weight')

        if self._days_in_preg == self._gestation_length:
            self._days_born -= 1  # will be incremented again in next stage
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
            format(self._id,
                   self._birth_date,
                   self._days_born,
                   self._body_weight,
                   AnimalBase.config['breeding_start_day_h'],
                   self._repro_program,
                   self._days_in_preg,
                   self._gestation_length,
                   str(self._events))

        return res_str
