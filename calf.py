import numpy as np
from random import random
from animal_base import AnimalBase
from config import Config

config = Config()

# calf born, with stillbirth porbabality, semen type related gender ratio and birthweight
class Calf(AnimalBase):
	def __init__(self, args):
		super().__init__(args)
		self._sold = False
		if random() < config.still_birth_rate:
			self._culled = True
			self._events.add_event(0, 'Still birth')
			return

		if config.semen_type == 'conventional':
			male_calf_rate = config.male_calf_rate_conventional_semen
		else:
			male_calf_rate = config.male_calf_rate_sexed_semen
		if random() < male_calf_rate:
			self._gender = 'male'
		else:
			self._gender = 'female'

		if self._gender == 'male' or random() > config.keep_female_calf_rate:
			self._sold = True
			return
		else:
			self._sold = False

		if self._breed == 'HO':
			self._birth_weight = np.random.normal(config.birth_weight_avg_ho, config.birth_weight_std_ho)
		elif self._breed == 'JE':
			self._birth_weight = np.random.normal(config.birth_weight_avg_je, config.birth_weight_std_je)
		self._body_weight = self._birth_weight
		self._wean_weight = 0

	def init_from_calf(self, calf):
		super().init_from_animal(calf)
		self._culled = calf._culled
		self._sold = calf._sold
		self._gender = calf._gender
		self._sold = calf._sold
		self._birth_weight = calf._birth_weight
		self._body_weight = calf._body_weight
		self._wean_weight = calf._wean_weight

	# update controls calf's grow
	def update(self):
		wean_day = False

		self._days_born += 1
		if self._days_born == config.wean_day:
			wean_day = True
			self._wean_weight = self._body_weight
			self._events.add_event(self._days_born, 'Wean Day')
			self._days_born -= 1 # will increment by 1 again in heifer update
		else:
			self._body_weight += np.random.normal(config.avg_daily_gain_c, config.std_daily_gain_c)

		return wean_day

	def __str__(self):
		if not self._culled:
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
			""".format(self._id,
					self._birth_date,
					self._days_born,
					self._birth_weight,
					self._body_weight,
					config.wean_day,
					str(self._events))
		else:
			res_str = """
				==> Calf: \n
				Still Birth: True \n
				ID: {} \n
				Birth Date: {}\n
				Days Born: {}\n
				Life Events: \n
				{}
			""".format(self._id,
					self._birth_date,
					self._days_born,
					str(self._events))
		return res_str