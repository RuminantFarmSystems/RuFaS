from calf import Calf
from animal_base import AnimalBase
from config import Config
import numpy as np

config = Config()

class HeiferI(Calf):
	def __init__(self, calf):
		super().init_from_calf(calf)

	def init_from_heiferI(self, heiferI):
		super().init_from_calf(heiferI)

	def update(self):
		second_stage = False
		self._body_weight += np.random.normal(config.avg_daily_gain_h, config.std_daily_gain_h)
		self._days_born += 1
		if self._days_born == config.breeding_start_day_h:
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
			Wean Day: {}\n
			Breeding Start Day: {}\n
			Life Events: \n
			{}
		""".format(self._id,
				   self._birth_date,
				   self._days_born,
				   self._birth_weight,
				   self._wean_weight,
				   self._body_weight,
				   config.wean_day,
				   config.breeding_start_day_h,
				   str(self._events))

		return res_str