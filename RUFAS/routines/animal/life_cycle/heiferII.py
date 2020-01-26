"""
RUFAS: Ruminant Farm Systems Model
File name: heiferII.py
Author(s): Manfei Li, mli497@wisc.edu
			Militsa Sotirova, militsasotirova@gmail.com
Description: This file updates the heifer form breeding to close to calving.
			Body weight gain with user input average daily gain,
			once mature body weight or grow end day reached, grow stop.
			Reproduction program could be chosen from the ED, TAI,
			Synch-ED projects, reference:
			http://www.dcrcouncil.org/wp-content/uploads/2018/12/Dairy-Heifer-Protocol-Sheet-Updated-2018.pdf
			Preg check follows AI for three times.
"""
###############################################################################
import numpy as np
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.ration.growing_heifer_ration import calculate_rqmts
from RUFAS.routines.animal.manure.growing_heifer_manure_excretion import \
	manure_calculations
from random import random
import math


class HeiferII(HeiferI):
	# TODO: Body weight changed could be based on nutrition intake later from
	#  Ration Formulation.

	def __init__(self, heiferI, args):
		"""
		Initialize the heifer in this stage from the first stage and initialize
		the repro program parameters.

		Args:
			heiferI: first stage of heifer, pass heifer information from heiferI
			args:
				args.repro_program: reproduction program used in heifer,
					three of them: ED, TAI, and synch-ED programs
				args.tai_method_h: timed-AI protocols used for reproduction
					programs, three of them: 5dCG2P, 5dCGP, and user-defined
				args.synch_ed_method_h: synch ed protocols used for reproduction
					programs, two of them: 2P and CP
		"""
		super().init_from_heiferI(heiferI)
		self.repro_program = args['repro_program']
		self.mature_body_weight = 0

		# Estrus variables
		self.estrus_count = 0
		self.estrus_day = 0

		# TAI variables
		self.tai_method_h = args['tai_method_h']
		self.tai_program_start_day_h = 0

		# synch_ED variables
		self.synch_ed_method_h = args['synch_ed_method_h']
		self.synch_ed_program_start_day_h = 0
		self.synch_ed_estrus_day = 0
		self.stop_day = 0

		self.conception_rate = 0
		self.ai_day = 0
		self.abortion_day = 0
		self.days_in_preg = 0
		self.preg = False
		self.gestation_length = 0

	def init_from_heiferII(self, heiferII):
		"""
		Initialize the heifer in this stage from the first stage and initialize
		the repro program parameters for coding purposes.

		Args:
			heiferII: another heifer out of the herd
		"""
		super().init_from_heiferI(heiferII)
		self.repro_program = heiferII.repro_program
		self.mature_body_weight = heiferII.mature_body_weight

		# ED variables
		self.estrus_count = heiferII.estrus_count
		self.estrus_day = heiferII.estrus_day

		# TAI variables
		self.tai_method_h = heiferII.tai_method_h
		self.tai_program_start_day_h = heiferII.tai_program_start_day_h

		# synch_ED variables
		self.synch_ed_method_h = heiferII.synch_ed_method_h
		self.synch_ed_program_start_day_h = \
			heiferII.synch_ed_program_start_day_h
		self.synch_ed_estrus_day = heiferII.synch_ed_estrus_day
		self.stop_day = heiferII.stop_day

		self.conception_rate = heiferII.conception_rate
		self.ai_day = heiferII.ai_day
		self.abortion_day = heiferII.abortion_day
		self.days_in_preg = heiferII.days_in_preg
		self.preg = heiferII.preg
		self.gestation_length = heiferII.gestation_length

	def calc_nutrient_rqmts(self):
		"""
		Calculates this heiferII's nutrient requirements.
		"""
		self.nutrient_rqmts, self.DMIest, self.DBW = calculate_rqmts()

	def calc_manure_excretion(self, feed):
		"""
		Calculates and sets the manure excretion components.

		Args:
			feed: instance of the Feed class
		"""
		self.manure_excretion = manure_calculations()

	def phosphorus_retained(self, DMI):
		"""
		Calculates the phosphorus retained by the animal.

		Args:
			DMI: the Dry Matter Intake (kg)

		Returns: the amount of phosphorus retained by the animal
			in grams per day
		"""
		# amount of P required for maintenance (g/d) (A.#.B.1)
		p_maint = 0.0008 * DMI + 0.000002 * self.body_weight * 1000

		# amount of P required for growth of a fetus (A.#.B.2)
		if self.days_in_preg >= 190 :
			exp_1 = (0.05527 - 0.000075 * self.days_in_preg) * self.days_in_preg
			exp_2 = (0.05527 - 0.000075 * (self.days_in_preg - 1)) * \
				(self.days_in_preg - 1)
			p_gest = (
					0.00002743 * math.exp(exp_1) -
					0.00002743 * math.exp(exp_2)) * 1000
		else:
			p_gest = 0

		# amount of P required for growth (g/d) (A.#.B.3)
		p_growth = (0.0012 + 0.004635 * (self.mature_body_weight ** 0.22) * (
				self.body_weight ** (-0.22))) * \
			self.daily_growth / 0.96 * 1000

		# amount of P retained (g/d) (A.#.B.4)
		p_retained = p_maint + p_gest + p_growth

		return p_retained

	def update(self):
		"""
		Controls heifer's grow with average daily gain based on user's input
		until breeding start day. Here is the place to change growth rate with
		heifer feeding methods later when we have heifer nutrition from the
		ration formulation module. Breeding starts with assigned
		reproduction program. Time to move to the 3rd stage --
		replacement stage determined based on gestion length and user input of
		replacement time. Culling for reproduction problem occur when heifer
		doesn't get pregnant for a long time.

		Returns:
			cull_stage: culling for reproduction failure
			third_stage: move to next stage -- heiferIII stage when time comes
		"""
		cull_stage = False
		third_stage = False

		prev_weight = self.body_weight
		self.days_born += 1

		if self.days_born < AnimalBase.config['grow_end_day']:
			# Heifer can only grow to a maximum weight of mature_body_weight
			if self.body_weight < AnimalBase.config['mature_body_weight']:
				self.body_weight += np.random.normal(
					AnimalBase.config['avg_daily_gain_h'],
					AnimalBase.config['std_daily_gain_h'])
			if self.body_weight > AnimalBase.config['mature_body_weight']:
				self.body_weight = AnimalBase.config['mature_body_weight']
				self.mature_body_weight = self.body_weight
				self.events.add_event(
					self.days_born,
					'Mature body weight prior to grow end day')

		self.daily_growth = self.body_weight - prev_weight

		# Mature body weight
		if self.days_born == AnimalBase.config['grow_end_day']:
			self.mature_body_weight = self.body_weight
			self.events.add_event(self.days_born, 'Mature body weight')

		# breeding method assign to heifer
		if self.days_born >= AnimalBase.config['breeding_start_day_h']:
			if self.repro_program == 'ED':
				self._ed_update()
			elif self.repro_program == 'TAI':
				self._tai_update()
			elif self.repro_program == 'synch-ED':
				self._synch_ed_update()
			self._preg_update()
			# piror to calving, heifer move to replacement group
			if self.days_in_preg == self.gestation_length - \
				AnimalBase.config['replacement_day']:
				self.days_born -= 1  # will be increment again in next stage
				third_stage = True
				self.events.add_event(self.days_born, 'moving to heiferIII')
		# cull heifer for reproduction reason
		if not self.preg and \
			self.days_born > AnimalBase.config['heifer_repro_cull_time']:
			self.events.add_event(
				self.days_born, 'Cull for heifer repro problem')
			cull_stage = True

		return cull_stage, third_stage

	# ED methods

	def _determine_estrus_day(self, start_date, estrus_note):
		"""
		In estrus detection program, determine estrus day and estrus note

		Args:
			start_date: start day of a estrus cycle, 1st day when breeding start
				or last estrus happened or return estrus from preg loss
			estrus_note: note of this estrus

		Returns: the day when this estrus should occur

		"""
		estrus_day = int(start_date + np.random.normal(
			AnimalBase.config['avg_estrus_cycle_h'],
			AnimalBase.config['std_estrus_cycle_h']))
		self.events.add_event(estrus_day, estrus_note)
		return estrus_day

	def _return_estrus(self):
		"""
		Return estrus after estrus not detected or not serviced
		"""
		self.estrus_day = self._determine_estrus_day(
			self.estrus_day, 'Estrus')

	def _after_ai_estrus(self):
		"""
		Return estrus after AI
		"""
		self.estrus_day = self._determine_estrus_day(
			self.estrus_day, 'Estrus after AI')

	def _after_abortion_estrus(self):
		"""
		Return estrus after abortion at preg check
		"""
		self.estrus_day = self._determine_estrus_day(
			self.abortion_day, 'Estrus after abortion')

	def _ed_update(self):
		"""
		Estrus occur at estrus day,
		estrus detected with detection rate,
		service preformed with service rate,
		conception successed with conception rate
		"""
		if self.days_born == AnimalBase.config['breeding_start_day_h']:
			self.estrus_day = self._determine_estrus_day(
				AnimalBase.config['breeding_start_day_h'], 'First estrus')

		# if on estrus day, start detecting estrus
		if self.days_born == self.estrus_day:
			self.estrus_count += 1

			estrus_detection_rand = random()
			if estrus_detection_rand < \
				AnimalBase.config['estrus_detection_rate']:
				# Estrus detected
				self.events.add_event(self.days_born, 'Estrus detected')
				ed_service_rand = random()
				if ed_service_rand < AnimalBase.config['estrus_service_rate']:
					# serviced
					self.ai_day = self.estrus_day + 1
					self.conception_rate = \
						AnimalBase.config['estrus_conception_rate']
				else:
					self._return_estrus()
			else:
				self._return_estrus()

	# TAI methods

	def _determine_tai_program_day(self, date):
		"""
		Determine the program start time when reach breeding start time

		Args:
			date: the time breeding program start
		"""
		self.tai_program_start_day_h = date

	def _tai_program_day_after_abortion(self):
		"""
		Determine the TAI restart date after abortion preg checks
		"""
		self.tai_program_start_day_h = self.abortion_day + 1

	def _5dCG2P_update(self):
		"""
		5dCG2P protocol for tai method
		"""
		if self.days_born == self.tai_program_start_day_h:
			self.events.add_event(self.days_born, 'Inject GnRH')
		elif self.days_born == self.tai_program_start_day_h + 5:
			self.events.add_event(self.days_born, 'Inject PGF')
		elif self.days_born == self.tai_program_start_day_h + 6:
			self.events.add_event(self.days_born, 'Inject PGF')
		elif self.days_born == self.tai_program_start_day_h + 8:
			self.ai_day = self.days_born
			self.conception_rate = AnimalBase.config['m5dCG2P_conception_rate']
			self.events.add_event(self.days_born, 'Inject GnRH')

	def _5dCGP_update(self):
		"""
		5dCGP protocol for tai method
		"""
		if self.days_born == self.tai_program_start_day_h:
			self.events.add_event(self.days_born, 'Inject GnRH')
		elif self.days_born == self.tai_program_start_day_h + 5:
			self.events.add_event(self.days_born, 'Inject PGF')
		elif self.days_born == self.tai_program_start_day_h + 8:
			self.ai_day = self.days_born
			self.conception_rate = AnimalBase.config['m5dCGP_conception_rate']
			self.events.add_event(self.days_born, 'Inject GnRH')

	def _user_defined_update(self):
		"""
		User defined protocol for tai method
		"""
		if self.days_born == self.tai_program_start_day_h + \
			AnimalBase.config['tai_program_length']:
			self.ai_day = self.days_born
			self.conception_rate = AnimalBase.config['defined_conception_rate']

	def _tai_update(self):
		"""
		Tai method update, assign tai method
		"""
		if self.days_born == AnimalBase.config['breeding_start_day_h']:
			self._determine_tai_program_day(
				AnimalBase.config['breeding_start_day_h'])

		if self.tai_method_h == '5dCG2P':
			self._5dCG2P_update()
		elif self.tai_method_h == '5dCGP':
			self._5dCGP_update()
		elif self.tai_method_h == 'user_defined':
			self._user_defined_update()

	# synch-ED methods

	def _determine_synch_ed_program_day(self, date):
		"""
		Determine the program start time when reach breeding start time

		Args:
			date: the time breeding program start
		"""
		self.synch_ed_program_start_day_h = date

	def _determine_synch_ed_estrus_day(self, date, avg, std, max_val):
		"""
		Determine synch ed leading estrus start day, with normal distribution

		Args:
			date: start of the synch ed day
			avg: average of estrus occur after synch ed
			std: standard deviation of synch ed
			max_val: max value can go for the normal distribution,
				avoiding negative value
		"""
		norm = abs(np.random.normal(avg, std))
		if norm >= max_val:
			norm = max_val - 1
		self.synch_ed_estrus_day = int(date + norm)

	def _synch_ed_program_day_after_abortion(self):
		"""
		Return to synch ed after abortion when spot at the preg check
		"""
		self.synch_ed_program_start_day_h = self.abortion_day

	def _2P_update(self):
		"""
		2P protocol for synch ed method
		estrus detection happens when estrus occur
		"""
		if self.days_born == self.synch_ed_program_start_day_h:
			self.events.add_event(self.days_born, 'Inject PGF')
			self._determine_synch_ed_estrus_day(self.days_born, 5, 3, 14)

		if self.days_born == self.synch_ed_estrus_day:
			self.events.add_event(self.days_born, 'Estrus occurs')
			estrus_detection_rand = random()
			if estrus_detection_rand < \
				AnimalBase.config['estrus_detection_rate']:
				self.events.add_event(self.days_born, 'Estrus detected')
				ed_service_rand = random()
				if ed_service_rand < AnimalBase.config['estrus_service_rate']:
					self.ai_day = self.synch_ed_estrus_day + 1
					self.conception_rate = \
						AnimalBase.config['ed_conception_rate']
				else:
					if self.days_born - \
							self.synch_ed_program_start_day_h < 14:
						# second round of injection
						self.events.add_event(
							self.synch_ed_program_start_day_h +
							14, 'Inject PGF')
						self._determine_synch_ed_estrus_day(
							self.synch_ed_program_start_day_h + 14, 3, 2, 7)
					else:
						# second round of injection also failed,
						# roll back to return_synch
						self.stop_day = self.synch_ed_program_start_day_h + 21
						self._determine_synch_ed_program_day(self.stop_day)
			else:
				self.stop_day = self.synch_ed_program_start_day_h + 21
				self._determine_synch_ed_program_day(self.stop_day)

	def _CP_update(self):
		"""
		CP protocol for synch ed method
		estrus detection happens when estrus occur
		"""
		if self.days_born == self.synch_ed_program_start_day_h:
			self.events.add_event(self.days_born, 'Inject CIDR')
		elif self.days_born == self.synch_ed_program_start_day_h + 7:
			self.events.add_event(self.days_born, 'Inject PGF')
			self._determine_synch_ed_estrus_day(self.days_born, 3, 2, 7)

		if self.days_born == self.synch_ed_estrus_day:
			self.events.add_event(self.days_born, 'Estrus occurs')
			estrus_detection_rand = random()
			if estrus_detection_rand < \
				AnimalBase.config['estrus_detection_rate']:
				self.events.add_event(self.days_born, 'Estrus detected')
				ed_service_rand = random()
				if ed_service_rand < AnimalBase.config['ed_service_rate']:
					self.ai_day = self.synch_ed_estrus_day + 1
					self.conception_rate = \
						AnimalBase.config['ed_conception_rate']
				else:
					self.stop_day = self.synch_ed_program_start_day_h + 14
					self._determine_synch_ed_program_day(self.stop_day)
			else:
				self.stop_day = self.synch_ed_program_start_day_h + 14
				self._determine_synch_ed_program_day(self.stop_day)

	def _synch_ed_update(self):
		"""
		Synch ed method update, assign with protocols: 2P or CP
		"""
		if self.days_born == AnimalBase.config['breeding_start_day_h']:
			self._determine_synch_ed_program_day(
				AnimalBase.config['breeding_start_day_h'])

		if self.synch_ed_method_h == '2P':
			self._2P_update()
		elif self.synch_ed_method_h == 'CP':
			self._CP_update()

	# Preg stage

	# after preg loss between 1 and 3 preg checks, return to
	# corresponding protocols
	def _open(self):
		"""
		Assign breeding method for open heifers after spot open at preg check
		three methods can be assigned: ED, TAI, synch-ED
		"""
		if self.repro_program == 'ED':
			self._after_abortion_estrus()
		elif self.repro_program == 'TAI':
			self._tai_program_day_after_abortion()
		elif self.repro_program == 'synch-ED':
			self._synch_ed_program_day_after_abortion()

	# artificial inseminated and go through 3 preg checks
	def _preg_update(self):
		"""
		update AI for heifers reach ai day, inseminate the heifer with specific
			semen type
		by comparing with conception rate, if conception success, gestation
			length determined
		for preg check 1, confirm the conception
		for preg check 2 and 3, confirm pregnancy, there are chances of preg
			loss in each period of time between preg checks
		"""
		if self.preg:
			self.days_in_preg += 1

		# AI
		if self.days_born == self.ai_day:
			self.events.add_event(
				self.days_born,
				'Inseminated with {}'.format(AnimalBase.config['semen_type']))
			# conception
			conception_rand = random()
			if conception_rand < self.conception_rate:
				self.days_in_preg = 1
				self.preg = True
				self.gestation_length = int(
					np.random.normal(
						AnimalBase.config['avg_gestation_len'],
						AnimalBase.config['std_gestation_len']))
				self.events.add_event(self.days_born, 'Heifer pregnant')
			else:
				self.events.add_event(self.days_born, 'Heifer not pregnant')
		# preg check 1
		elif self.days_born == self.ai_day + \
			AnimalBase.config['preg_check_day_1']:
			if self.preg:
				preg_loss_rand = random()
				if preg_loss_rand > AnimalBase.config['preg_loss_rate_1']:
					self.events.add_event(
						self.days_born,
						'Preg check 1, confirmed')
				else:
					self.days_in_preg = 0
					self.preg = False
					self.abortion_day = self.days_born
					self._open()
					self.events.add_event(
						self.days_born,
						'Preg loss happened before 1st preg check')
			else:
				self.abortion_day = self.days_born
				self._open()
				self.events.add_event(
					self.days_born,
					'Preg check 1, not pregnant')
		# preg check 2
		elif self.days_born == self.ai_day + \
			AnimalBase.config['preg_check_day_2']:
			preg_loss_rand = random()
			if preg_loss_rand > \
				AnimalBase.config['preg_loss_rate_2']:
				self.events.add_event(
					self.days_born,
					'Preg check 2, confirmed')
			else:
				self.days_in_preg = 0
				self.preg = False
				self.abortion_day = self.days_born
				self._open()
				self.events.add_event(
					self.days_born,
					'Preg loss happened between 1st and 2nd preg check')
		# preg check 3
		elif self.days_born == self.ai_day + \
			AnimalBase.config['preg_check_day_3']:
			preg_loss_rand = random()
			if preg_loss_rand > AnimalBase.config['preg_loss_rate_3']:
				self.events.add_event(
					self.days_born, 'Preg check 3, confirmed')
			else:
				self.days_in_preg = 0
				self.preg = False
				self.abortion_day = self.days_born
				self._open()
				self.events.add_event(
					self.days_born,
					'Preg loss happened between 2nd and 3rd preg check')

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
		""".format(
			self.id,
			self.birth_date,
			self.days_born,
			self.body_weight,
			AnimalBase.config['breeding_start_day_h'],
			self.repro_program,
			self.days_in_preg,
			self.gestation_length,
			str(self.events))

		return res_str
