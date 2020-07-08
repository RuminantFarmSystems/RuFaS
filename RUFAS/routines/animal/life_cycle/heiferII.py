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
	
	def __init__(self, args):
		"""
		Description:
			initialize the heifer in this stage from the first stage and initialize or assigns the repro program parameters
		Input:
			(In addition to heiferI information)
			args.repro_program: reproduction program used in heifer, three of them: ED, TAI, and synch-ED programs
			args.tai_method_h: timed-AI protocols used for reproduction programs, three of them: 5dCG2P, 5dCGP, and user-defined
			args.synch_ed_method_h: synch ed protocols used for reproduction programs, two of them: 2P and CP
			(optional: include the following to assign repro program parameters)
			args.estrus_count
			args.estrus_day
			args.tai_program_start_day_h
			args.synch_ed_program_start_day_h
			args.synch_ed_estrus_day
			args.synch_ed_stop_day
			args.conception_rate
			args.ai_day
			args.abortion_day
			args.days_in_preg
			args.gestation_length
		"""
		super().__init__(args)

		if 'estrus_count' in args:
			self.assign_heiferII_values(args)
		else:
			self.init_values(args)

		self.target_adg_heifer_preg = 0

	def set_adg_preg(self):
		"""
		Sets the target average daily gain for an animal that is pregnant.
		If the gestation_length of the animal is equal to its days_in_preg,
		the difference is set to 1 (otherwise results in a division by 0 error).
		"""
		divisor = (self.gestation_length - self.days_in_preg)
		if divisor == 0:
			divisor = 1
		self.target_adg_heifer_preg = \
			(0.82 * 0.96 * self.mature_body_weight - 0.96 * self.body_weight) \
			/ divisor
		
	def init_values(self, args):
		"""
		Initialize repro program values
		"""
		self.repro_program = args['repro_program']

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
		self.synch_ed_stop_day = 0

		self.conception_rate = 0
		self.ai_day = 0
		self.abortion_day = 0
		self.days_in_preg = 0
		self.preg = False
		self.gestation_length = 0
		self.p_gest_for_calf = 0

	def assign_heiferII_values(self, args):
		"""
			Assign the repro program with given vales
		"""
		self.repro_program = args['repro_program']

		# Estrus variables
		self.estrus_count = args['estrus_count']
		self.estrus_day = args['estrus_day']

		# TAI variables
		self.tai_method_h = args['tai_method_h']
		self.tai_program_start_day_h = args['tai_program_start_day_h']

		# synch_ED variables
		self.synch_ed_method_h = args['synch_ed_method_h']
		self.synch_ed_program_start_day_h = args['synch_ed_program_start_day_h']
		self.synch_ed_estrus_day = args['synch_ed_estrus_day']
		self.synch_ed_stop_day = args['synch_ed_stop_day']

		self.conception_rate = args['conception_rate']
		self.ai_day = args['ai_day']
		self.abortion_day = args['abortion_day']
		self.days_in_preg = args['days_in_preg']
		self.preg = self.days_in_preg != 0
		self.gestation_length = args['gestation_length']
		self.p_gest_for_calf = args['p_gest_for_calf']

	def get_heiferII_values(self):
		"""
		Get current information from the heiferII
		"""
		values = {
            'id' : self.id,
            'breed' : self.breed,
            'birth_date' : self.birth_date,
            'days_born' : self.days_born,
            'birth_weight' : self.birth_weight,
            'body_weight' : self.body_weight,
            'wean_weight' : self.wean_weight,
            'events' : str(self.events),
            'repro_program': self.repro_program,
            'tai_method_h': self.tai_method_h,
            'synch_ed_method_h': self.synch_ed_method_h,
            'mature_body_weight': self.mature_body_weight,
            'estrus_count': self.estrus_count,
            'estrus_day': self.estrus_day,
            'tai_program_start_day_h': self.tai_program_start_day_h,
            'synch_ed_program_start_day_h': self.synch_ed_program_start_day_h,
            'synch_ed_estrus_day': self.synch_ed_estrus_day,
            'synch_ed_stop_day': self.synch_ed_stop_day,
            'conception_rate': self.conception_rate,
            'ai_day': self.ai_day,
            'abortion_day': self.abortion_day,
            'days_in_preg': self.days_in_preg,
            'gestation_length': self.gestation_length,
			'p_gest_for_calf': self.p_gest_for_calf
        }
		return values

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
		p_urine, p_feces_excrt = self.calc_base_manure()

		self.p_excrt, self.manure_excretion = \
			manure_calculations(p_feces_excrt, p_urine)

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

		# absorbed P retained for fetal growth (g) (A.1C-F.E.4)
		if self.days_in_preg >= 190:
			exp_1 = (0.05527 - 0.000075 * self.days_in_preg) * self.days_in_preg
			exp_2 = (0.05527 - 0.000075 * (self.days_in_preg - 1)) * \
				(self.days_in_preg - 1)
			self.p_gest = (
					0.00002743 * math.exp(exp_1) -
					0.00002743 * math.exp(exp_2)) * 1000
			self.p_gest_for_calf += self.p_gest
		else:
			self.p_gest = 0

		# absorbed P required by the animal (g) (A.1A-F.E.6)
		p_absorb = p_urine + self.p_maint_feces + self.p_growth + self.p_gest

		# requirement of P from the ration (g) (A.1B-D.E.7)
		self.p_req = p_absorb / 0.664

	def update(self, sim_day):
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
		self.update_body_weight_history(sim_day)
		cull_stage = False
		third_stage = False
		
		prev_weight = self.body_weight
		self.days_born += 1

		if self.days_born < AnimalBase.config['grow_end_day']:
			# Heifer can only grow to a maximum weight of mature_body_weight
			if self.preg:
				self.set_adg_preg()
				self.body_weight += self.target_adg_heifer_preg
			else:
				self.set_agd_non_preg()
				self.body_weight += self.target_adg_heifer_non_preg

			if self.body_weight > self.mature_body_weight:
				self.body_weight = self.mature_body_weight
				self.events.add_event(self.days_born, sim_day,
				'Mature body weight prior to grow end day')
		
		self.daily_growth = self.body_weight - prev_weight
		
		# Mature body weight
		if self.days_born == AnimalBase.config['grow_end_day']:
			self.mature_body_weight = self.body_weight
			self.events.add_event(self.days_born, sim_day, 'Mature body weight')

		# breeding method assign to heifer
		if self.days_born >= AnimalBase.config['breeding_start_day_h']:
			if self.repro_program == 'ED':
				self._ed_update(sim_day)
			elif self.repro_program == 'TAI':
				self._tai_update(sim_day)
			elif self.repro_program == 'synch-ED':
				self._synch_ed_update(sim_day)
			self._preg_update(sim_day)
			# prior to calving, heifer move to replacement group
			if self.days_in_preg == self.gestation_length - \
				AnimalBase.config['prefresh_day']:
				self.days_born -= 1  # will be increment again in next stage
				third_stage = True
				self.events.add_event(self.days_born, sim_day, 'moving to heiferIII')
		# cull heifer for reproduction reason
		if not self.preg and \
			self.days_born > AnimalBase.config['heifer_repro_cull_time']:
			self.events.add_event(
				self.days_born, sim_day, 'Cull for heifer repro problem')
			cull_stage = True

		return cull_stage, third_stage

	# ED methods

	def _determine_estrus_day(self, start_date, estrus_note, sim_day):
		"""
		In estrus detection program, determine estrus day and estrus note

		Args:
			start_date: start day of a estrus cycle, 1st day when breeding start
				or last estrus happened or return estrus from preg loss
			estrus_note: note of this estrus

		Returns: the day when this estrus should occur

		"""
		estrus_cycle = np.random.normal(
			AnimalBase.config['avg_estrus_cycle_heifer'],
			AnimalBase.config['std_estrus_cycle_heifer'])
		while estrus_cycle < AnimalBase.config['avg_estrus_cycle_heifer'] \
			- 2 * AnimalBase.config['std_estrus_cycle_heifer'] \
			or estrus_cycle > AnimalBase.config['avg_estrus_cycle_heifer'] \
				+ 2 * AnimalBase.config['std_estrus_cycle_heifer']:
			estrus_cycle = np.random.normal(
				AnimalBase.config['avg_estrus_cycle_heifer'],
				AnimalBase.config['std_estrus_cycle_heifer'])
		estrus_day =  int(start_date + estrus_cycle)
		self.events.add_event(estrus_day, sim_day, estrus_note)
		return estrus_day

	def _return_estrus(self, sim_day):
		"""
		Return estrus after estrus not detected or not serviced
		"""
		self.estrus_day = self._determine_estrus_day(
			self.estrus_day, 'Estrus', sim_day)

	def _after_ai_estrus(self, sim_day):
		"""
		Return estrus after AI
		"""
		self.estrus_day = self._determine_estrus_day(
			self.estrus_day, 'Estrus after AI', sim_day)

	def _after_abortion_estrus(self, sim_day):
		"""
		Return estrus after abortion at preg check
		"""
		self.estrus_day = self._determine_estrus_day(
			self.abortion_day, 'Estrus after abortion', sim_day)

	def _ed_update(self, sim_day):
		"""
		Estrus occur at estrus day,
		estrus detected with detection rate,
		service preformed with service rate,
		conception successed with conception rate
		"""
		if self.days_born == AnimalBase.config['breeding_start_day_h']:
			self.estrus_day = self._determine_estrus_day(
				AnimalBase.config['breeding_start_day_h'], 'First estrus',
				sim_day)

		# if on estrus day, start detecting estrus
		if self.days_born == self.estrus_day:
			self.estrus_count += 1

			estrus_detection_rand = random()
			if estrus_detection_rand < \
				AnimalBase.config['estrus_detection_rate']:
				# Estrus detected
				self.events.add_event(self.days_born, sim_day, 'Estrus detected')
				ed_service_rand = random()
				if ed_service_rand < AnimalBase.config['estrus_service_rate']:
					# serviced
					self.ai_day = self.estrus_day + 1
					self.conception_rate = \
						AnimalBase.config['estrus_conception_rate']
				else:
					self._return_estrus(sim_day)
			else:
				self._return_estrus(sim_day)

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

	def _5dCG2P_update(self, sim_day):
		"""
		5dCG2P protocol for tai method
		"""
		if self.days_born == self.tai_program_start_day_h:
			self.events.add_event(self.days_born, sim_day, 'Inject GnRH')
		elif self.days_born == self.tai_program_start_day_h + 5:
			self.events.add_event(self.days_born, sim_day, 'Inject PGF')
		elif self.days_born == self.tai_program_start_day_h + 6:
			self.events.add_event(self.days_born, sim_day, 'Inject PGF')
		elif self.days_born == self.tai_program_start_day_h + 8:
			self.ai_day = self.days_born
			self.conception_rate = AnimalBase.config['m5dCG2P_conception_rate']
			self.events.add_event(self.days_born, sim_day, 'Inject GnRH')

	def _5dCGP_update(self, sim_day):
		"""
		5dCGP protocol for tai method
		"""
		if self.days_born == self.tai_program_start_day_h:
			self.events.add_event(self.days_born, sim_day, 'Inject GnRH')
		elif self.days_born == self.tai_program_start_day_h + 5:
			self.events.add_event(self.days_born, sim_day, 'Inject PGF')
		elif self.days_born == self.tai_program_start_day_h + 8:
			self.ai_day = self.days_born
			self.conception_rate = AnimalBase.config['m5dCGP_conception_rate']
			self.events.add_event(self.days_born, sim_day, 'Inject GnRH')

	def _user_defined_update(self):
		"""
		User defined protocol for tai method
		"""
		if self.days_born == self.tai_program_start_day_h + \
			AnimalBase.config['tai_program_length']:
			self.ai_day = self.days_born
			self.conception_rate = AnimalBase.config['defined_conception_rate']

	def _tai_update(self, sim_day):
		"""
		Tai method update, assign tai method
		"""
		if self.days_born == AnimalBase.config['breeding_start_day_h']:
			self._determine_tai_program_day(
				AnimalBase.config['breeding_start_day_h'])

		if self.tai_method_h == '5dCG2P':
			self._5dCG2P_update(sim_day)
		elif self.tai_method_h == '5dCGP':
			self._5dCGP_update(sim_day)
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
		synch_ed_estrus = np.random.normal(avg, std)
		while synch_ed_estrus < avg - 2 * std \
			or synch_ed_estrus > avg + 2 * std:
			synch_ed_estrus = np.random.normal(avg, std)
		norm = abs(synch_ed_estrus)
		if norm >= max_val:
			norm = max_val - 1
		self.synch_ed_estrus_day = int(date + norm)

	def _synch_ed_program_day_after_abortion(self):
		"""
		Return to synch ed after abortion when spot at the preg check
		"""
		self.synch_ed_program_start_day_h = self.abortion_day

	def _2P_update(self, sim_day):
		"""
		2P protocol for synch ed method
		estrus detection happens when estrus occur
		"""
		if self.days_born == self.synch_ed_program_start_day_h:
			self.events.add_event(self.days_born, sim_day, 'Inject PGF')
			self._determine_synch_ed_estrus_day(self.days_born, 5, 3, 14)

		if self.days_born == self.synch_ed_estrus_day:
			self.events.add_event(self.days_born, sim_day, 'Estrus occurs')
			estrus_detection_rand = random()
			if estrus_detection_rand < \
				AnimalBase.config['estrus_detection_rate']:
				self.events.add_event(self.days_born, sim_day, 'Estrus detected')
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
							14, sim_day, 'Inject PGF')
						self._determine_synch_ed_estrus_day(
							self.synch_ed_program_start_day_h + 14, 3, 2, 7)
					else:
						# second round of injection also failed,
						# roll back to return_synch
						self.synch_ed_stop_day = self.synch_ed_program_start_day_h + 21
						self._determine_synch_ed_program_day(self.synch_ed_stop_day)
			else:
				self.synch_ed_stop_day = self.synch_ed_program_start_day_h + 21
				self._determine_synch_ed_program_day(self.synch_ed_stop_day)

	def _CP_update(self, sim_day):
		"""
		CP protocol for synch ed method
		estrus detection happens when estrus occur
		"""
		if self.days_born == self.synch_ed_program_start_day_h:
			self.events.add_event(self.days_born, sim_day, 'Inject CIDR')
		elif self.days_born == self.synch_ed_program_start_day_h + 7:
			self.events.add_event(self.days_born, sim_day, 'Inject PGF')
			self._determine_synch_ed_estrus_day(self.days_born, 3, 2, 7)

		if self.days_born == self.synch_ed_estrus_day:
			self.events.add_event(self.days_born, sim_day, 'Estrus occurs')
			estrus_detection_rand = random()
			if estrus_detection_rand < \
				AnimalBase.config['estrus_detection_rate']:
				self.events.add_event(self.days_born, sim_day, 'Estrus detected')
				ed_service_rand = random()
				if ed_service_rand < AnimalBase.config['ed_service_rate']:
					self.ai_day = self.synch_ed_estrus_day + 1
					self.conception_rate = \
						AnimalBase.config['ed_conception_rate']
				else:
					self.synch_ed_stop_day = self.synch_ed_program_start_day_h + 14
					self._determine_synch_ed_program_day(self.synch_ed_stop_day)
			else:
				self.synch_ed_stop_day = self.synch_ed_program_start_day_h + 14
				self._determine_synch_ed_program_day(self.synch_ed_stop_day)

	def _synch_ed_update(self, sim_day):
		"""
		Synch ed method update, assign with protocols: 2P or CP
		"""
		if self.days_born == AnimalBase.config['breeding_start_day_h']:
			self._determine_synch_ed_program_day(
				AnimalBase.config['breeding_start_day_h'])

		if self.synch_ed_method_h == '2P':
			self._2P_update(sim_day)
		elif self.synch_ed_method_h == 'CP':
			self._CP_update(sim_day)

	# Preg stage

	# after preg loss between 1 and 3 preg checks, return to
	# corresponding protocols
	def _open(self, sim_day):
		"""
		Assign breeding method for open heifers after spot open at preg check
		three methods can be assigned: ED, TAI, synch-ED
		"""
		if self.repro_program == 'ED':
			self._after_abortion_estrus(sim_day)
		elif self.repro_program == 'TAI':
			self._tai_program_day_after_abortion()
		elif self.repro_program == 'synch-ED':
			self._synch_ed_program_day_after_abortion()

	# artificial inseminated and go through 3 preg checks
	def _preg_update(self, sim_day):
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
				self.days_born, sim_day,
				'Inseminated with {}'.format(AnimalBase.config['semen_type']))
			# conception
			conception_rand = random()
			if conception_rand < self.conception_rate:
				self.days_in_preg = 1
				self.preg = True
				self.gestation_length = int(np.random.normal(
					AnimalBase.config['avg_gestation_len'], 
					AnimalBase.config['std_gestation_len']))
				while self.gestation_length < AnimalBase.config['avg_gestation_len'] \
					- 2 * AnimalBase.config['std_gestation_len'] \
					or self.gestation_length > AnimalBase.config['avg_gestation_len'] \
						+ 2 * AnimalBase.config['std_gestation_len']:
					self.gestation_length = int(np.random.normal(
						AnimalBase.config['avg_gestation_len'], 
						AnimalBase.config['std_gestation_len']))
				self.events.add_event(self.days_born, sim_day, 'Heifer pregnant')
			else:
				self.events.add_event(self.days_born, sim_day, 'Heifer not pregnant')
		# preg check 1
		elif self.days_born == self.ai_day + \
			AnimalBase.config['preg_check_day_1']:
			if self.preg:
				preg_loss_rand = random()
				if preg_loss_rand > AnimalBase.config['preg_loss_rate_1']:
					self.events.add_event(
						self.days_born, sim_day,
						'Preg check 1, confirmed')
				else:
					self.days_in_preg = 0
					self.preg = False
					self.abortion_day = self.days_born
					self._open(sim_day)
					self.events.add_event(
						self.days_born, sim_day,
						'Preg loss happened before 1st preg check')
			else:
				self.abortion_day = self.days_born
				self._open(sim_day)
				self.events.add_event(
					self.days_born, sim_day,
					'Preg check 1, not pregnant')
		# preg check 2
		elif self.days_born == self.ai_day + \
			AnimalBase.config['preg_check_day_2']:
			preg_loss_rand = random()
			if preg_loss_rand > \
				AnimalBase.config['preg_loss_rate_2']:
				self.events.add_event(
					self.days_born, sim_day,
					'Preg check 2, confirmed')
			else:
				self.days_in_preg = 0
				self.preg = False
				self.abortion_day = self.days_born
				self._open(sim_day)
				self.events.add_event(
					self.days_born, sim_day,
					'Preg loss happened between 1st and 2nd preg check')
		# preg check 3
		elif self.days_born == self.ai_day + \
			AnimalBase.config['preg_check_day_3']:
			preg_loss_rand = random()
			if preg_loss_rand > AnimalBase.config['preg_loss_rate_3']:
				self.events.add_event(
					self.days_born, sim_day, 'Preg check 3, confirmed')
			else:
				self.days_in_preg = 0
				self.preg = False
				self.abortion_day = self.days_born
				self._open(sim_day)
				self.events.add_event(
					self.days_born, sim_day,
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
