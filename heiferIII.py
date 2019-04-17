import numpy as np
from heiferII import HeiferII
from random import random
from config import Config

config = Config()

class HeiferIII(HeiferII):
    def __init__(self, heiferII):
        super().init_from_heiferII(heiferII)

    def init_from_heiferIII(self, heiferIII):
        super().init_from_heiferII(heiferIII)

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