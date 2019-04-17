import math
import numpy as np
from heiferIII import HeiferIII
from random import random
from config import Config

config = Config()


class Cow(HeiferIII):
	def __init__(self, heiferIII, args):
		super().init_from_heiferIII(heiferIII)
		self._calves = 0
		self._milking = False
		self._days_in_milk = 0
		self._single_acc_milk_prod = 0
		self._future_cull_date = 0
		self._cull_reason = None
		self._repro_program = args['repro_program']

		# TAI params
		self._presynch_method = args['presynch_method']
		self._tai_method_c = args['tai_method_c']
		self._presynch_program_start_day = 0
		self._tai_program_start_day_c = 0
		self._resynch_method = args['resynch_method']

		# ecnomics counts
		self._ED_days = 0
		self._ED_econ_days = 0
		self._GnRH_injections = 0
		self._PGF_injections = 0
		self._semen_used = 0
		self._AI_times = 0
		self._preg_diagnoses = 0
		self._feed_cost = 0
		self._fixed_cost = 0
		self._milk_income = 0

	def init_from_cow(self, cow):
		super().init_from_heiferIII(Cow)
		self._calves = cow._calves
		self._milking = cow._milking
		self._days_in_milk = cow._days_in_milk
		self._single_acc_milk_prod = cow._single_acc_milk_prod
		self._future_cull_date = cow._future_cull_date
		self._cull_reason = cow._cull_reason
		self._repro_program = cow._repro_program

		# TAI params
		self._presynch_method = cow._presynch_method
		self._tai_method_c = cow._tai_method_c
		self._presynch_program_start_day = cow._presynch_program_start_day
		self._tai_program_start_day_c = cow._tai_program_start_day_c
		self._resynch_method = cow._resynch_method

		# ecnomics counts
		self._ED_days = cow._ED_days
		self._GnRH_injections = cow._GnRH_injections
		self._PGF_injections = cow._PGF_injections
		self._semen_used = cow._semen_used
		self._AI_times = cow._AI_times
		self._preg_diagnoses = cow._preg_diagnoses
		self._feed_cost = cow._feed_cost
		self._fixed_cost = cow._fixed_cost
		self._milk_income = cow._milk_income

	def _determine_param_value(self, mean, std):
		return np.random.normal(mean, std)

	# lactation curve
	def _milking_update(self):
		if self._days_in_preg == self._gestation_length - config.dry_period:
			self._milking = False
			self._events.add_event(self._days_born, 'dry')
			self._days_in_milk = 0
			return 0, 0, 0, 0

		self._days_in_milk += 1
		if self._breed == 'HO':
			breed_index = 0
			parity_index = 2 if self._calves - 1 > 2 else self._calves - 1
		elif self._breed == 'JE':
			breed_index = 1
			parity_index = 2 if self._calves - 1 > 2 else self._calves - 1
		if config.lactation_curve == 'wood':
			l = self._determine_param_value(config.l[breed_index][parity_index], config.l_std[breed_index][parity_index])
			m = self._determine_param_value(config.m[breed_index][parity_index], config.m_std[breed_index][parity_index])
			n = self._determine_param_value(config.n[breed_index][parity_index], config.n_std[breed_index][parity_index])

			daily_milk_produced = l * \
				math.pow(self._days_in_milk, m) * \
				math.exp((0 - n) * self._days_in_milk)
		elif config.lactation_curve == 'milkbot':
			daily_milk_produced = config.a * \
				(1 - math.exp((config.c-self._days_in_milk) / config.b) / 2) * \
				math.exp((0 - config.d) * self._days_in_milk)
		self._single_acc_milk_prod += daily_milk_produced

		# calculate fat percent in milk and fat corrected milk production
		fat_percent = 12.86 * self._days_in_milk ** (-1.081) * math.exp((0.0926) * (math.log(self._days_in_milk)) ** 2) * (math.log(self._days_in_milk) ** 1.107)
		daily_fat_correct_milk_production = 0.4 * daily_milk_produced + 0.15 * fat_percent * daily_milk_produced

		# calculate body weight when milking
		if self._calves == 1:
			self._body_weight = self._mature_body_weight * (1-(1-(self._birth_weight/self._mature_body_weight)**(1/3)) * math.exp(-0.0039 * self._days_born)) **3 - (20/65) * self._days_in_milk * math.exp(1-self._days_in_milk/65) + 0.0187**3 * (self._days_in_preg - 50) ** 3
		else:
			self._body_weight = self._mature_body_weight * (1-(1-(self._birth_weight/self._mature_body_weight)**(1/3)) * math.exp(-0.006 * self._days_born)) **3 - (40/75) * self._days_in_milk * math.exp(1-self._days_in_milk/75) + 0.0187**3 * (self._days_in_preg - 50) ** 3

		#caculate dry matter intake from fat corrected milk production
		if self._milking:
			dry_matter_intake = 0.372 * daily_fat_correct_milk_production + 0.0968 * self._body_weight**0.75 * (1-math.exp(-0.192 * (self._days_in_milk/7 +3.67)))
		else:
			dry_matter_intake = 12

		return daily_milk_produced, fat_percent, daily_fat_correct_milk_production, dry_matter_intake

	# cow update
	def update(self, record_econ_stats):
		if self._culled:
			return None

		daily_milk_produced = 0
		cull_stage = False
		new_born = False
		self._days_born += 1

		if self._preg and self._days_in_preg == self._gestation_length:
			self._calves += 1
			self._milking = True
			self._days_in_milk = 0
			self._preg = False
			self._days_in_preg = 0
			self._gestation_length = 0
			self._events.add_event(self._days_born, 'New birth, start milking')
			self._involuntary_cull_update()
			new_born = True

			# restarting estrus
			if self._repro_program in ['ED', 'ED-TAI']:
				self._restart_estrus()

		daily_milk_produced = 0
		fat_percent = 0
		daily_fat_correct_milk_production = 0
		dry_matter_intake = 0
		if self._milking:
			daily_milk_produced, fat_percent, daily_fat_correct_milk_production, dry_matter_intake = self._milking_update()
			if self._repro_program == 'ED':
					self._ed_update(record_econ_stats)
			elif self._repro_program == 'ED-TAI':
					self._ed_tai_update(record_econ_stats)
			elif self._repro_program == 'TAI':
				if self._days_in_milk >= config.vwp:
					self._tai_update(record_econ_stats)

		self._preg_update(record_econ_stats)
		cull_stage = self._cull_update(daily_milk_produced)

		self._economy_update(cull_stage, daily_milk_produced, dry_matter_intake, record_econ_stats)

		return daily_milk_produced, fat_percent, daily_fat_correct_milk_production, dry_matter_intake, cull_stage, new_born

	################ ED methods #################

	def _determine_estrus_day(self, start_date, estrus_note, avg, std):
		estrus_day = int(start_date + abs(np.random.normal(avg, std)))
		self._events.add_event(estrus_day, estrus_note)
		return estrus_day

	def _restart_estrus(self):
		self._estrus_day = self._determine_estrus_day(self._days_born, '1st estrus after calving', config.avg_estrus_cycle_r, config.std_estrus_cycle_r)

	def _later_estrus(self):
		self._estrus_day = self._determine_estrus_day(self._estrus_day, 'estrus occur before vwp', config.avg_estrus_cycle_c, config.std_estrus_cycle_c)

	def _return_estrus(self):
		self._estrus_day = self._determine_estrus_day(self._estrus_day, 'Estrus', config.avg_estrus_cycle_c, config.std_estrus_cycle_c)

	def _after_ai_estrus(self):
		self._estrus_day = self._determine_estrus_day(self._estrus_day, 'Estrus after AI', config.avg_estrus_cycle_c, config.std_estrus_cycle_c)

	def _after_abortion_estrus(self):
		self._estrus_day = self._determine_estrus_day(self._abortion_day, 'Estrus after abortion', config.avg_estrus_cycle_c, config.std_estrus_cycle_c)

	def _ed_update(self, record_econ_stats):
		# if on estrus day, start detecting estrus
		if self._days_born == self._estrus_day:
			self._estrus_count += 1

			if 1 <= self._days_in_milk and self._days_in_milk <= config.vwp:
				self._later_estrus()
			else:
				estrus_detection_rand = random()
				if estrus_detection_rand < config.estrus_detection_rate:
					# Estrus detected
					self._events.add_event(self._days_born, 'Estrus detected')
					estrus_service_rand = random()
					if estrus_service_rand < config.estrus_service_rate:
						# serviced
						self._ai_day = self._estrus_day + 1
						self._conception_rate = config.ed_conception_rate
					else:
						self._return_estrus()
				else:
					self._return_estrus()

		if self._milking:
			self._ED_days += 1
			if record_econ_stats:
				self._ED_econ_days += 1


	################ TAI methods #################

	def _determine_tai_program_day(self, date):
		self._tai_program_start_day_c = date

	def _tai_program_day_after_preg_check(self, record_econ_stats):
		if self._resynch_method == 'TAIafterPD':
			self._tai_program_start_day_c = self._abortion_day + 1
			self._conception_rate -= config.conception_rate_decrease
		elif self._resynch_method == 'TAIbeforePD':
			self._tai_program_start_day_c = self._abortion_day - 6
			self._conception_rate -= config.conception_rate_decrease
			if self._tai_method_c in ['OvSynch 56', 'OvSynch 48', 'CoSynch 72']:
				self._events.add_event(self._tai_program_start_day_c, 'Inject GnRH')
				self._GnRH_injections = self._GnRH_injections + 1 if record_econ_stats else self._GnRH_injections
		elif self._resynch_method == 'PGFatPD':
			self._events.add_event(self._days_born, 'Inject PGF')
			self._PGF_injections = self._PGF_injections + 1 if record_econ_stats else self._PGF_injections
			self._tai_program_start_day_c = self._abortion_day + 8
			self._conception_rate -= config.conception_rate_decrease

	def _OvSynch56_update(self, record_econ_stats):
		if self._days_born == self._tai_program_start_day_c:
			self._events.add_event(self._days_born, 'Inject GnRH')
			self._GnRH_injections = self._GnRH_injections + 1 if record_econ_stats else self._GnRH_injections
		elif self._days_born == self._tai_program_start_day_c + 7:
			self._events.add_event(self._days_born, 'Inject PGF')
			self._PGF_injections = self._PGF_injections + 1 if record_econ_stats else self._PGF_injections
		elif self._days_born == self._tai_program_start_day_c + 9:
			self._events.add_event(self._days_born, 'Inject GnRH')
			self._GnRH_injections = self._GnRH_injections + 1 if record_econ_stats else self._GnRH_injections
		elif self._days_born == self._tai_program_start_day_c + 10:
			self._ai_day = self._days_born
			self._conception_rate = config.ovsynch56_conception_rate

	def _OvSynch48_update(self, record_econ_stats):
		if self._days_born == self._tai_program_start_day_c:
			self._events.add_event(self._days_born, 'Inject GnRH')
			self._GnRH_injections = self._GnRH_injections + 1 if record_econ_stats else self._GnRH_injections
		elif self._days_born == self._tai_program_start_day_c + 7:
			self._events.add_event(self._days_born, 'Inject PGF')
			self._PGF_injections = self._PGF_injections + 1 if record_econ_stats else self._PGF_injections
		elif self._days_born == self._tai_program_start_day_c + 9:
			self._events.add_event(self._days_born, 'Inject GnRH')
			self._GnRH_injections = self._GnRH_injections + 1 if record_econ_stats else self._GnRH_injections
		elif self._days_born == self._tai_program_start_day_c + 10:
			self._ai_day = self._days_born
			self._conception_rate = config.ovsynch48_conception_rate

	def _CoSynch72_update(self, record_econ_stats):
		if self._days_born == self._tai_program_start_day_c:
			self._events.add_event(self._days_born, 'Inject GnRH')
			self._GnRH_injections = self._GnRH_injections + 1 if record_econ_stats else self._GnRH_injections
		elif self._days_born == self._tai_program_start_day_c + 7:
			self._events.add_event(self._days_born, 'Inject PGF')
			self._PGF_injections = self._PGF_injections + 1 if record_econ_stats else self._PGF_injections
		elif self._days_born == self._tai_program_start_day_c + 10:
			self._events.add_event(self._days_born, 'Inject GnRH')
			self._GnRH_injections = self._GnRH_injections + 1 if record_econ_stats else self._GnRH_injections
			self._ai_day = self._days_born
			self._conception_rate = config.cosynch72_conception_rate

	def _5dCoSynch_update(self, record_econ_stats):
		if self._days_born == self._tai_program_start_day_c:
			self._events.add_event(self._days_born, 'Inject GnRH')
			self._GnRH_injections = self._GnRH_injections + 1 if record_econ_stats else self._GnRH_injections
		elif self._days_born == self._tai_program_start_day_c + 5:
			self._events.add_event(self._days_born, 'Inject PGF')
			self._PGF_injections = self._PGF_injections + 1 if record_econ_stats else self._PGF_injections
		elif self._days_born == self._tai_program_start_day_c + 6:
			self._events.add_event(self._days_born, 'Inject PGF')
			self._PGF_injections = self._PGF_injections + 1 if record_econ_stats else self._PGF_injections
		elif self._days_born == self._tai_program_start_day_c + 8:
			self._events.add_event(self._days_born, 'Inject GnRH')
			self._GnRH_injections = self._GnRH_injections + 1 if record_econ_stats else self._GnRH_injections
			self._ai_day = self._days_born
			self._conception_rate = config._5dcosynch_conception_rate

	def _user_defined_update(self):
		if self._days_born == self._tai_program_start_day_c + config.tai_program_length:
			self._ai_day = self._days_born
			self._conception_rate = config.defined_conception_rate_c

	def _determine_presynch_program_day(self, date):
		self._presynch_program_start_day = date

	def _presynch_update(self, record_econ_stats):
		if self._days_born == self._presynch_program_start_day:
			self._events.add_event(self._days_born, 'Inject PGF')
			self._PGF_injections = self._PGF_injections + 1 if record_econ_stats else self._PGF_injections
		elif self._days_born == self._presynch_program_start_day + 14:
			self._events.add_event(self._days_born, 'Inject PGF')
			self._PGF_injections = self._PGF_injections + 1 if record_econ_stats else self._PGF_injections
		elif self._days_born == self._presynch_program_start_day + 26:
			self._tai_program_start_day_c = self._days_born
			self._events.add_event(self._days_born, 'PreSynch end')

	def _doubleovsynch_update(self, record_econ_stats):
		if self._days_born == self._presynch_program_start_day:
			self._events.add_event(self._days_born, 'Inject GnRH')
			self._GnRH_injections = self._GnRH_injections + 1 if record_econ_stats else self._GnRH_injections
		elif self._days_born == self._presynch_program_start_day + 7:
			self._events.add_event(self._days_born, 'Inject PGF')
			self._PGF_injections = self._PGF_injections + 1 if record_econ_stats else self._PGF_injections
		elif self._days_born == self._presynch_program_start_day + 10:
			self._events.add_event(self._days_born, 'Inject GnRH')
			self._GnRH_injections = self._GnRH_injections + 1 if record_econ_stats else self._GnRH_injections
		elif self._days_born == self._presynch_program_start_day + 17:
			self._tai_program_start_day_c = self._days_born
			self._events.add_event(self._days_born, 'Double OvSynch end')

	def _g6g_update(self, record_econ_stats):
		if self._days_born == self._presynch_program_start_day:
			self._events.add_event(self._days_born, 'Inject PGF')
			self._PGF_injections = self._PGF_injections + 1 if record_econ_stats else self._PGF_injections
		elif self._days_born == self._presynch_program_start_day + 2:
			self._events.add_event(self._days_born, 'Inject GnRH')
			self._GnRH_injections = self._GnRH_injections + 1 if record_econ_stats else self._GnRH_injections
		elif self._days_born == self._presynch_program_start_day + 9:
			self._tai_program_start_day_c = self._days_born
			self._events.add_event(self._days_born, 'G6G end')

	def _user_defined_presynch_update(self):
		if self._days_born == self._presynch_program_start_day:
			self._tai_program_start_day_c = self._days_born + config.presynch_program_length

	def _tai_update(self, record_econ_stats):
		if self._days_in_milk == config.vwp:
			if self._presynch_method:
				self._determine_presynch_program_day(self._days_born)
			else:
				self._determine_tai_program_day(self._days_born)

		if self._presynch_method:
			if self._presynch_method == 'PreSynch':
				self._presynch_update(record_econ_stats)
			elif self._presynch_method == 'Double OvSynch':
				self._doubleovsynch_update(record_econ_stats)
			elif self._presynch_method == 'G6G':
				self._g6g_update(record_econ_stats)
			elif self._presynch_method == 'user_defined':
				self._user_defined_presynch_update()

		if self._tai_method_c == 'OvSynch 56':
			self._OvSynch56_update(record_econ_stats)
		elif self._tai_method_c == 'OvSynch 48':
			self._OvSynch48_update(record_econ_stats)
		elif self._tai_method_c == 'CoSynch 72':
			self._CoSynch72_update(record_econ_stats)
		elif self._tai_method_c == '5d CoSynch':
			self._5dCoSynch_update(record_econ_stats)
		elif self._tai_method_c == 'user_defined':
			self._user_defined_update()

	################ ED-TAI methods #################
	def _ed_tai_update(self, record_econ_stats):
		# if on estrus day, start detecting estrus
		if self._days_born == self._estrus_day and self._days_in_milk < config.tai_program_start_day:
			self._estrus_count += 1

			if 1 <= self._days_in_milk and self._days_in_milk <= config.vwp:
				self._later_estrus()
			else:
				estrus_detection_rand = random()
				if estrus_detection_rand < config.estrus_detection_rate:
					# Estrus detected
					self._events.add_event(self._days_born, 'Estrus detected')
					estrus_service_rand = random()
					if estrus_service_rand < config.estrus_service_rate:
						# serviced
						self._ai_day = self._estrus_day + 1
						self._conception_rate = config.ed_conception_rate
					else:
						self._return_estrus()
				else:
					self._return_estrus()

		if self._milking:
			self._ED_days += 1

		if self._days_in_milk == config.tai_program_start_day and self._ai_day == 0:
			self._estrus_day = 0
			self._determine_tai_program_day(self._days_born)

		if self._days_in_milk == config.tai_program_start_day and self._ai_day == 0:
			if self._tai_method_c == 'OvSynch 56':
				self._OvSynch56_update(record_econ_stats)
			elif self._tai_method_c == 'OvSynch 48':
				self._OvSynch48_update(record_econ_stats)
			elif self._tai_method_c == 'CoSynch 72':
				self._CoSynch72_update(record_econ_stats)
			elif self._tai_method_c == '5d CoSynch':
				self._5dCoSynch_update(record_econ_stats)
			elif self._tai_method_c == 'user_defined':
				self._user_defined_update()

	def _resynch_ed_tai(self, record_econ_stats):
		if self._resynch_method == 'TAIafterPD':
			self._tai_program_start_day_c = self._abortion_day + 1
			self._conception_rate -= config.conception_rate_decrease
		elif self._resynch_method == 'TAIbeforePD':
			self._tai_program_start_day_c = self._abortion_day - 6
			self._conception_rate -= config.conception_rate_decrease
			if self._tai_method_c in ['OvSynch 56', 'OvSynch 48', 'CoSynch 72']:
				self._events.add_event(self._tai_program_start_day_c, 'Inject GnRH')
				self._GnRH_injections = self._GnRH_injections + 1 if record_econ_stats else self._GnRH_injections
		elif self._resynch_method == 'PGFatPD':
			self._events.add_event(self._days_born, 'Inject PGF')
			self._PGF_injections = self._PGF_injections + 1 if record_econ_stats else self._PGF_injections
			self._tai_program_start_day_c = self._abortion_day + 8
			self._conception_rate -= config.conception_rate_decrease
			self._estrus_day = self._determine_estrus_day(self._abortion_day, 'estrus after PGF', config.avg_estrus_cycle_p, config.std_estrus_cycle_p)

	################ Preg methods #################

	def _open(self, record_econ_stats):
		if self._repro_program == 'ED':
			self._after_abortion_estrus()
		elif self._repro_program == 'TAI':
			self._tai_program_day_after_preg_check(record_econ_stats)
		elif self._repro_program == 'ED-TAI':
			self._resynch_ed_tai(record_econ_stats)

	def _preg_update(self, record_econ_stats):
		if self._preg:
			self._days_in_preg += 1

		if self._days_born == self._ai_day:
			self._events.add_event(
				self._days_born, 'Inseminated with {}'.format(config.semen_type))
			if record_econ_stats:
				self._semen_used += 1
				self._AI_times += 1
			conception_rand = random()
			if conception_rand < self._conception_rate:
				self._days_in_preg = 1
				self._preg = True
				self._gestation_length = int(np.random.normal(
					config.avg_gestation_len, config.std_gestation_len))
				self._events.add_event(self._days_born, 'Cow pregnant')
			else:
				if self._repro_program in ['ED', 'ED-TAI']:
					self._ai_day = 0
					self._after_ai_estrus()
				self._events.add_event(self._days_born, 'Cow not pregnant')
		elif self._days_born == self._ai_day + config.preg_check_day_1:
			if record_econ_stats:
				self._preg_diagnoses += 1
			if self._preg:
				preg_loss_rand = random()
				if preg_loss_rand > config.preg_loss_rate_1:
					self._events.add_event(
						self._days_born, 'Preg check 1, confirmed')
				else:
					self._days_in_preg = 0
					self._preg = False
					self._abortion_day = self._days_born
					self._open(record_econ_stats)
					self._events.add_event(
						self._days_born, 'Preg loss happened before 1st preg check')
			else:
				self._abortion_day = self._days_born
				self._open(record_econ_stats)
				self._events.add_event(
					self._days_born, 'Preg check 1, not pregnant')
		elif self._days_born == self._ai_day + config.preg_check_day_2:
			if record_econ_stats:
				self._preg_diagnoses += 1
			preg_loss_rand = random()
			if preg_loss_rand > config.preg_loss_rate_2:
				self._events.add_event(
					self._days_born, 'Preg check 2, confirmed')
			else:
				self._days_in_preg = 0
				self._preg = False
				self._abortion_day = self._days_born
				self._open(record_econ_stats)
				self._events.add_event(
					self._days_born, 'Preg loss happened between 1st and 2nd preg check')
		elif self._days_born == self._ai_day + config.preg_check_day_3:
			if record_econ_stats:
				self._preg_diagnoses += 1
			preg_loss_rand = random()
			if preg_loss_rand > config.preg_loss_rate_3:
				self._events.add_event(
					self._days_born, 'Preg check 3, confirmed')
			else:
				self._days_in_preg = 0
				self._preg = False
				self._abortion_day = self._days_born
				self._open(record_econ_stats)
				self._events.add_event(
					self._days_born, 'Preg loss happened between 2nd and 3rd preg check')

	################ Cull methods #################
	def _cull_update(self, record_econ_stats):
		if not self._preg and self._days_in_milk > config.repro_cull_time:
			self._culled = True
			self._events.add_event(self._days_born, 'Cull for repro problem')
			self._cull_reason = "Reproduction failure"
			return True
		if self._days_in_milk > 80 and not self._preg and self._milk_income < self._feed_cost + self._fixed_cost: #daily_milk_produced < config.cull_milk_production:
			self._culled = True
			self._events.add_event(self._days_born, 'Cull for low production')
			self._cull_reason = "Low production"
			return True
		if self._days_born == self._future_cull_date:
			self._culled = True
			self._events.add_event(self._days_born, 'Cull for {}'.format(self._cull_reason))
			return True
		return False

	def _involuntary_cull_update(self):
		inv_cull_rate = 0
		if self._calves >= 4:
			inv_cull_rate = config.parity_cull_prob[3]
		else:
			inv_cull_rate = config.parity_cull_prob[self._calves-1]
		cull_rand = random()
		if (cull_rand <= inv_cull_rate):
			cull_reason_rand = random()
			cull_reason_cp = []
			if (cull_reason_rand <= 0.1633):
				cull_reason_cp = config.feet_leg_cp
				self._cull_reason = "Lameness"
			elif (cull_reason_rand <= 0.4516):
				cull_reason_cp = config.injury_cp
				self._cull_reason = "Injury"
			elif (cull_reason_rand <= 0.6955):
				cull_reason_cp = config.mastitis_cp
				self._cull_reason = "Mastitis"
			elif (cull_reason_rand <= 0.8346):
				cull_reason_cp = config.disease_cp
				self._cull_reason = "Disease"
			elif (cull_reason_rand <= 0.8991):
				cull_reason_cp = config.udder_cp
				self._cull_reason = "Udder"
			else:
				cull_reason_cp = config.unkown_cp
				self._cull_reason = "Unknown"

			c_upper = c_lower = x_upper = x_lower = 0
			for i in range(len(cull_reason_cp) - 1):
				if (cull_reason_cp[i] <= cull_reason_rand and cull_reason_rand < cull_reason_cp[i+1]):
					c_lower = cull_reason_cp[i]
					c_upper = cull_reason_cp[i+1]
					x_lower = config.cull_day_count[i]
					x_upper = config.cull_day_count[i+1]
			ai = (x_upper-x_lower) / (c_upper-c_lower)
			self._future_cull_date = round(x_lower + ai * (cull_reason_rand - c_lower) + self._days_born)

	def _economy_update(self, cull_stage, daily_milk_produced, dry_matter_intake, record_econ_stats):
		# cow ecnomics
		if record_econ_stats:
			if self._milking:
				self._feed_cost += dry_matter_intake * 0.25
			else:
				self._feed_cost += dry_matter_intake * 0.15

			if cull_stage == False:
				self._fixed_cost += 2.5

			self._milk_income += daily_milk_produced * 0.40

	def get_economy_stats(self):
		if self._repro_program == 'ED':
			self._repro_cost = self._ED_days * 0.15
		if self._repro_program == 'TAI':
			self._repro_cost = self._GnRH_injections * 2.4 + self._PGF_injections * 2.65 + (self._GnRH_injections + self._PGF_injections) * 0.25
		if self._repro_program == 'ED-TAI':
			self._repro_cost = self._ED_days * 0.15 + self._GnRH_injections * 2.4 + self._PGF_injections * 2.65 + (self._GnRH_injections + self._PGF_injections) * 0.25

		semen_cost = self._semen_used * 10
		AI_cost = self._AI_times *5
		preg_check_cost = self._preg_diagnoses * 3
		slaughter_value = self._body_weight * 0.65

		return self._repro_cost, semen_cost, AI_cost, preg_check_cost, self._feed_cost, self._fixed_cost, self._milk_income, slaughter_value

	def __str__(self):
		res_str = """
			==> Cow: \n
			ID: {} \n
			Birth Date: {}\n
			Days Born: {}\n
			Body Weight: {}kg\n
			Repro program: {}\n
			Parity: {}\n
			Days in milk: {}\n
			Days in preg: {}\n
			Gestation Length: {}\n
			Life Events: \n
			{}
		""".format(self._id,
				   self._birth_date,
				   self._days_born,
				   self._body_weight,
				   self._repro_program,
				   self._calves,
				   self._days_in_milk,
				   self._days_in_preg,
				   self._gestation_length,
				   str(self._events))

		return res_str