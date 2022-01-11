"""
RUFAS: Ruminant Farm Systems Model
File name: calf.py
Author(s): Manfei Li, mli497@wisc.edu
Militsa Sotirova, militsasotirova@gmail.com
Description: This file updates the calf form birth to wean.
Birth weight initialized with breed specific distributions,
Gender determined with the semen type used,
Sold or keep decision made by user input,
Body weight gain with user input calf average daily gain.
"""

import numpy as np
from random import random
from scipy.stats import truncnorm
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.ration.calf_ration import calc_requirements
from RUFAS.routines.animal.manure.calf_manure_excretion import \
    manure_calculations
from RUFAS.routines.animal.life_cycle import animal_events_constants as c


class Calf(AnimalBase):
    def __init__(self, args):
        """
        Description:
            initialize calf at the time it was born
        Args:
            args.id: id of the animal
            args.breed: breed of the animal
            args.birth_date: the date of the simulation when the calf was born
            args.daysBorn: age of the animal
            (optional: include the following to assign animal information)
            args.birth_weight: the birth weight of the animal
            args.body_weight: current body weight of the animal
            args.wean_weight: the wean weight of the animal
            args.mature_body_weight: the mature body weight of the animal
            args.events: events of the animal
        """
        super().__init__(args)

        self.gender = ''
        self.sold = False
        self.wean_weight = 0
        self.birth_weight = 0
        self.animal_intake = 0
        self._DBW = 0

        if 'body_weight' in args:
            self.assign_calf_values(args)
        else:
            self.init_values(args)

        self.target_adg_calf = self.birth_weight / AnimalBase.config['wean_day']

    def init_values(self, args):
        """
        Determine stillbirth, gender, and birth weight
        """
        # gender determined with gender ratio relates to semen type
        if AnimalBase.config['semen_type'] == 'conventional':
            male_calf_rate = \
                AnimalBase.config['male_calf_rate_conventional_semen']
        else:
            male_calf_rate = AnimalBase.config['male_calf_rate_sexed_semen']
        if random() < male_calf_rate:
            self.gender = 'male'
        else:
            self.gender = 'female'

        # calf born, with stillbirth probability
        if random() < AnimalBase.config['still_birth_rate']:
            self.culled = True
            self.events.add_event(0, 0, c.STILL_BIRTH)

        # sell the male calves and the unwanted female calves
        # (if AnimalBase.config['keep_female_calf_rate'] = 1,
        # keep all the female calves in farm.
        # if AnimalBase.config['keep_female_calf_rate = 0,
        # sell all female calves)

        if self.gender == 'male' or random() > \
                AnimalBase.config['keep_female_calf_rate']:
            self.sold = True
        else:
            self.sold = False

        self.birth_weight = args['birth_weight']
        self.body_weight = args['birth_weight']
        self.mature_body_weight = truncnorm.rvs(-2*AnimalBase.config['mature_body_weight_std'], 2*AnimalBase.config['mature_body_weight_std'], \
                        AnimalBase.config['mature_body_weight_avg'], AnimalBase.config['mature_body_weight_std'])
        self.wean_weight = 0
        self.p_animal = args['p_init']

    def assign_calf_values(self, args):
        """
        Assign calf with given values
        """
        self.culled = False
        self.sold = False
        self.gender = 'female'
        self.birth_weight = args['birth_weight']
        self.body_weight = args['body_weight']
        self.wean_weight = args['wean_weight']
        self.mature_body_weight = args['mature_body_weight']
        self.events.init_from_string(args['events'])

    def get_calf_values(self):
        """
        Get current information from the calf
        """
        values = {
            'id': self.id,
            'breed': self.breed,
            'birth_date': self.birth_date,
            'days_born': self.days_born,
            'birth_weight': self.birth_weight,
            'body_weight': self.body_weight,
            'wean_weight': self.wean_weight,
            'mature_body_weight': self.mature_body_weight,
            'events': str(self.events)
        }
        return values

    def calc_nutrient_rqmts(self, feed, temp):
        """
        Calculates this calf's nutrient requirements.
        """
        # self.nutrient_rqmts, self.DMIest, self.DBW = calculate_rqmts()
        wean_day = AnimalBase.config['wean_day']
        wean_length = AnimalBase.config['wean_length']
        milk_type = AnimalBase.config['milk_type']
        self.animal_intake, self.nutrient_rqmts = calc_requirements(self, feed, temp, wean_day, wean_length, milk_type)
        self._DBW = self.nutrient_rqmts['live_weight_change']['val']

    def calc_manure_excretion(self, feed):
        """
        Calculates and sets the manure excretion components.

        Args:
            feed: instance of the Feed class
        """
        p_urine, p_feces_excrt = self.calc_base_manure()

        self.p_excrt, self.manure_excretion = \
            manure_calculations(self.body_weight, p_feces_excrt, p_urine)

    def phosphorus_rqmts(self, DMI):
        """
        Calculates and sets the animal's phosphorus requirement.

        Args:
            DMI: the Dry Matter Intake (kg)
        """
        # amount of P required for endogenous losses (g) (A.1A-D.E.1)
        self.p_maint_feces = 0.0008 * DMI * 1000

        # amount pf P required for urine production (g) (A.1A-F.E.2)
        p_urine = 0.000002 * self.body_weight * 1000

        # absorbed P retained for growth (g) (A.1A-F.E.3)
        self.p_growth = \
            (0.0012 + 0.004635 * (self.mature_body_weight ** 0.22) *
             (self.body_weight ** (-0.22))) * \
            self.daily_growth / 0.96 * 1000

        # absorbed P required by the animal (g) (A.1A-F.E.6)
        p_absorb = p_urine + self.p_maint_feces + self.p_growth

        # requirement of P from the ration (g) (A.1A.E.7)
        self.p_req = p_absorb / 0.90

    def update(self, sim_day):
        """
        Controls calf's grow with average daily gain based on user's input until
        wean day. Calculate the wean weight at wean day. Here is the place to
        change growth rate with calf feeding methods later when we have calf
        nutrition from the ration formulation module.

        Returns: time when calf is weaned -- stop be fed with milk
        """
        self.update_body_weight_history(sim_day)

        wean_day = False

        prev_weight = self.body_weight

        self.days_born += 1
        if self.days_born == AnimalBase.config['wean_day']:
            wean_day = True
            self.wean_weight = self.body_weight
            self.events.add_event(self.days_born, sim_day, c.WEAN_DAY)
            self.days_born -= 1  # will increment by 1 again in heifer update
        else:
            self.body_weight += self.target_adg_calf

        self.daily_growth = self.body_weight - prev_weight

        return wean_day
