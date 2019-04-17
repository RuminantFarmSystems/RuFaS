import numpy as np
from heiferI import HeiferI
from random import random
from config import Config

config = Config()

class HeiferII(HeiferI):
	def __init__(self, heiferI, args):
		super().init_from_heiferI(heiferI)
		self._repro_program = args['repro_program']
		self._mature_body_weight = 0

		# Estrus variables
		self._estrus_count = 0
		self._estrus_day = 0

		# TAI variables
		self._tai_method_h = args['tai_method_h']
		self._tai_program_start_day_h = 0

		# synch_ED variables
		self._synch_ed_method_h = args['synch_ed_method_h']
		self._synch_ed_program_start_day_h = 0
		self._synch_ed_estrus_day = 0
		self._stop_day = 0

		self._conception_rate = 0
		self._ai_day = 0
		self._abortion_day = 0
		self._days_in_preg = 0
		self._preg = False
		self._gestation_length = 0

	def init_from_heiferII(self, heiferII):
		super().init_from_heiferI(heiferII)
		self._repro_program = heiferII._repro_program
		self._mature_body_weight = heiferII._mature_body_weight

		# ED variables
		self._estrus_count = heiferII._estrus_count
		self._estrus_day = heiferII._estrus_day

		# TAI variables
		self._tai_method_h = heiferII._tai_method_h
		self._tai_program_start_day_h = heiferII._tai_program_start_day_h

		# synch_ED variables
		self._synch_ed_method_h = heiferII._synch_ed_method_h
		self._synch_ed_program_start_day_h = heiferII._synch_ed_program_start_day_h
		self._synch_ed_estrus_day = heiferII._synch_ed_estrus_day
		self._stop_day = heiferII._stop_day

		self._conception_rate = heiferII._conception_rate
		self._ai_day = heiferII._ai_day
		self._abortion_day = heiferII._abortion_day
		self._days_in_preg = heiferII._days_in_preg
		self._preg = heiferII._preg
		self._gestation_length = heiferII._gestation_length

	def update(self):
		cull_stage = False
		third_stage = False
		self._days_born += 1

		if self._days_born < config.grow_end_day:
			# Heifer can only grow to a maximum weight of mature_body_weight
			if self._body_weight < config.mature_body_weight:
				self._body_weight += np.random.normal(config.avg_daily_gain_h, config.std_daily_gain_h)
			if self._body_weight > config.mature_body_weight:
				self._body_weight = config.mature_body_weight
				self._mature_body_weight = self._body_weight
				self._events.add_event(self._days_born, 'Mature body weight prior to grow end day')

		# Mature body weight
		if self._days_born == config.grow_end_day:
			self._mature_body_weight = self._body_weight
			self._events.add_event(self._days_born, 'Mature body weight')

		# breeding method assign to heifer
		if self._days_born >= config.breeding_start_day_h:
			if self._repro_program == 'ED':
				self._ed_update()
			elif self._repro_program == 'TAI':
				self._tai_update()
			elif self._repro_program == 'synch-ED':
				self._synch_ed_update()
			self._preg_update()
			# piror to calving, heifer move to replacement group
			if self._days_in_preg == self._gestation_length - config.replacement_day:
				self._days_born -= 1	# will be increment again in next stage
				third_stage = True
				self._events.add_event(self._days_born, 'moving to heiferIII')
		# cull heifer for reproduction reason
		if not self._preg and self._days_born > config.heifer_repro_cull_time:
			self._events.add_event(self._days_born, 'Cull for heifer repro problem')
			cull_stage = True

		return cull_stage, third_stage

	################ ED methods #################

	def _determine_estrus_day(self, start_date, estrus_note):
		estrus_day =  int(start_date + np.random.normal(config.avg_estrus_cycle_h, config.std_estrus_cycle_h))
		self._events.add_event(estrus_day, estrus_note)
		return estrus_day

	def _return_estrus(self):
		self._estrus_day = self._determine_estrus_day(self._estrus_day, 'Estrus')

	def _after_ai_estrus(self):
		self._estrus_day = self._determine_estrus_day(self._estrus_day, 'Estrus after AI')

	def _after_abortion_estrus(self):
		self._estrus_day = self._determine_estrus_day(self._abortion_day, 'Estrus after abortion')

	def _ed_update(self):
		if self._days_born == config.breeding_start_day_h:
			self._estrus_day = self._determine_estrus_day(config.breeding_start_day_h, 'First estrus')

		# if on estrus day, start detecting estrus
		if self._days_born == self._estrus_day:
			self._estrus_count += 1

			estrus_detection_rand = random()
			if estrus_detection_rand < config.estrus_detection_rate:
				# Estrus detected
				self._events.add_event(self._days_born, 'Estrus detected')
				ed_service_rand = random()
				if ed_service_rand < config.estrus_service_rate:
					# serviced
					self._ai_day = self._estrus_day + 1
					self._conception_rate = config.estrus_service_rate
				else:
					self._return_estrus()
			else:
				self._return_estrus()

	################ TAI methods #################

	# Tai when reach breeding start time
	def _determine_tai_program_day(self, date):
		self._tai_program_start_day_h = date

	# Tai after preg checks
	def _tai_program_day_after_abortion(self):
		self._tai_program_start_day_h = self._abortion_day + 1

	# Tai method 5dCG2P
	def _5dCG2P_update(self):
		if self._days_born == self._tai_program_start_day_h:
			self._events.add_event(self._days_born, 'Inject GnRH')
		elif self._days_born == self._tai_program_start_day_h + 5:
			self._events.add_event(self._days_born, 'Inject PGF')
		elif self._days_born == self._tai_program_start_day_h + 6:
			self._events.add_event(self._days_born, 'Inject PGF')
		elif self._days_born == self._tai_program_start_day_h + 8:
			self._ai_day = self._days_born
			self._conception_rate = config.m5dCG2P_conception_rate
			self._events.add_event(self._days_born, 'Inject GnRH')

	# Tai method 5dCGP
	def _5dCGP_update(self):
		if self._days_born == self._tai_program_start_day_h:
			self._events.add_event(self._days_born, 'Inject GnRH')
		elif self._days_born == self._tai_program_start_day_h + 5:
			self._events.add_event(self._days_born, 'Inject PGF')
		elif self._days_born == self._tai_program_start_day_h + 8:
			self._ai_day = self._days_born
			self._conception_rate = config.m5dCGP_conception_rate
			self._events.add_event(self._days_born, 'Inject GnRH')

	# Tai method user_define
	def _user_defined_update(self):
		if self._days_born == self._tai_program_start_day_h + config.tai_program_length:
			self._ai_day = self._days_born
			self._conception_rate = config.defined_conception_rate

	# Tai method assigned
	def _tai_update(self):
		if self._days_born == config.breeding_start_day_h:
			self._determine_tai_program_day(config.breeding_start_day_h)

		if self._tai_method_h == '5dCG2P':
			self._5dCG2P_update()
		elif self._tai_method_h == '5dCGP':
			self._5dCGP_update()
		elif self._tai_method_h == 'user_defined':
			self._user_defined_update()

	################ synch-ED methods #################


	def _determine_synch_ed_program_day(self, date):
		self._synch_ed_program_start_day_h = date

	def _determine_synch_ed_estrus_day(self, date, avg, std, max):
		norm = abs(np.random.normal(avg, std))
		if norm >= max:
			norm = max - 1
		self._synch_ed_estrus_day = int(date + norm)

	def _synch_ed_program_day_after_abortion(self):
		self._synch_ed_program_start_day_h = self._abortion_day

	def _2P_update(self):
		if self._days_born == self._synch_ed_program_start_day_h:
			self._events.add_event(self._days_born, 'Inject PGF')
			self._determine_synch_ed_estrus_day(self._days_born, 5, 3, 14)

		if self._days_born == self._synch_ed_estrus_day:
			self._events.add_event(self._days_born, 'Estrus occurs')
			estrus_detection_rand = random()
			if estrus_detection_rand < config.estrus_detection_rate:
				self._events.add_event(self._days_born, 'Estrus detected')
				ed_service_rand = random()
				if ed_service_rand < config.estrus_service_rate:
					self._ai_day = self._synch_ed_estrus_day + 1
					self._conception_rate = config.ed_conception_rate
				else:
					if self._days_born - self._synch_ed_program_start_day_h < 14:
						# second round of injection
						self._events.add_event(self._synch_ed_program_start_day_h + 14, 'Inject PGF')
						self._determine_synch_ed_estrus_day(self._synch_ed_program_start_day_h + 14, 3, 2, 7)
					else:
						# second round of injection also failed, roll back to return_synch
						self._stop_day = self._synch_ed_program_start_day_h + 21
						self._determine_synch_ed_program_day(self._stop_day)
			else:
				self._stop_day = self._synch_ed_program_start_day_h + 21
				self._determine_synch_ed_program_day(self._stop_day)

	def _CP_update(self):
		if (self._days_born == self._synch_ed_program_start_day_h):
			self._events.add_event(self._days_born, 'Inject CIDR')
		elif (self._days_born == self._synch_ed_program_start_day_h + 7):
			self._events.add_event(self._days_born, 'Inject PGF')
			self._determine_synch_ed_estrus_day(self._days_born, 3, 2, 7)

		if self._days_born == self._synch_ed_estrus_day:
			self._events.add_event(self._days_born, 'Estrus occurs')
			estrus_detection_rand = random()
			if estrus_detection_rand < config.estrus_detection_rate:
				self._events.add_event(self._days_born, 'Estrus detected')
				ed_service_rand = random()
				if ed_service_rand < config.ed_service_rate:
					self._ai_day = self._synch_ed_estrus_day + 1
					self._conception_rate = config.ed_conception_rate
				else:
					self._stop_day = self._synch_ed_program_start_day_h + 14
					self._determine_synch_ed_program_day(self._stop_day)
			else:
				self._stop_day = self._synch_ed_program_start_day_h + 14
				self._determine_synch_ed_program_day(self._stop_day)

	def _synch_ed_update(self):
		if self._days_born == config.breeding_start_day_h:
			self._determine_synch_ed_program_day(config.breeding_start_day_h)

		if self._synch_ed_method_h == '2P':
			self._2P_update()
		elif self._synch_ed_method_h == 'CP':
			self._CP_update()

	################ Preg stage #################

	# after preg loss between 1 and 3 preg checks, return to coresponding protocols
	def _open(self):
		if self._repro_program == 'ED':
			self._after_abortion_estrus()
		elif self._repro_program == 'TAI':
			self._tai_program_day_after_abortion()
		elif self._repro_program == 'synch-ED':
			self._synch_ed_program_day_after_abortion()

	# artificial inseminated and go through 3 preg checks
	def _preg_update(self):
		if self._preg:
			self._days_in_preg += 1

		# AI
		if self._days_born == self._ai_day:
			self._events.add_event(self._days_born, 'Inseminated with {}'.format(config.semen_type))
			# conception
			conception_rand = random()
			if conception_rand < self._conception_rate:
				self._days_in_preg = 1
				self._preg = True
				self._gestation_length = int(np.random.normal(config.avg_gestation_len, config.std_gestation_len))
				self._events.add_event(self._days_born, 'Heifer pregnant')
			else:
				self._events.add_event(self._days_born, 'Heifer not pregnant')
		# preg check 1
		elif self._days_born == self._ai_day + config.preg_check_day_1:
			if self._preg:
				preg_loss_rand = random()
				if preg_loss_rand > config.preg_loss_rate_1:
					self._events.add_event(self._days_born, 'Preg check 1, confirmed')
				else:
					self._days_in_preg = 0
					self._preg = False
					self._abortion_day = self._days_born
					self._open()
					self._events.add_event(self._days_born, 'Preg loss happened before 1st preg check')
			else:
				self._abortion_day = self._days_born
				self._open()
				self._events.add_event(self._days_born, 'Preg check 1, not pregnant')
		# preg check 2
		elif self._days_born == self._ai_day + config.preg_check_day_2:
			preg_loss_rand = random()
			if preg_loss_rand > config.preg_loss_rate_2:
				self._events.add_event(self._days_born, 'Preg check 2, confirmed')
			else:
				self._days_in_preg = 0
				self._preg = False
				self._abortion_day = self._days_born
				self._open()
				self._events.add_event(self._days_born, 'Preg loss happened between 1st and 2nd preg check')
		# preg check 3
		elif self._days_born == self._ai_day + config.preg_check_day_3:
			preg_loss_rand = random()
			if preg_loss_rand > config.preg_loss_rate_3:
				self._events.add_event(self._days_born, 'Preg check 3, confirmed')
			else:
				self._days_in_preg = 0
				self._preg = False
				self._abortion_day = self._days_born
				self._open()
				self._events.add_event(self._days_born, 'Preg loss happened between 2nd and 3rd preg check')

	def __str__(self):
		res_str = """
			==> Heifer II: \n
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