'''
RUFAS: Ruminant Farm Systems Model
File name: heiferII.py
Author(s): Manfei Li, mli497@wisc.edu
	       Militsa Sotirova, militsasotirova@gmail.com
Description: This file updates the heifer form breeding to close to calving.
			Body weight gain with user input average daily gain,
			once mature body weight or grow end day reached, grow stop.
			TODO: Body weight changed could be based on nutrition intake later fron Ration Formulation.
			Reproduction program could be chosen from the ED, TAI, Synch-ED projects, reference:
			http://www.dcrcouncil.org/wp-content/uploads/2018/12/Dairy-Heifer-Protocol-Sheet-Updated-2018.pdf
			Preg check follows AI for three times.
'''
###############################################################################


import numpy as np
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.ration.growing_heifer_ration import calculate_rqmts
from RUFAS.routines.animal.manure.growing_heifer_manure_excretion import manure_calculations
from random import random

class HeiferII(HeiferI):
	'''
		Description:
			initialize the heifer in this stage from the first stage and initialize or assigns the repro program parameters
		Input:
			(In addition to heiferI information)
			args.repro_program: reproduction program used in heifer, three of them: ED, TAI, and synch-ED programs
			args.tai_method_h: timed-AI protocols used for reproduction programs, three of them: 5dCG2P, 5dCGP, and user-defined
			args.synch_ed_method_h: synch ed protocols used for reproduction programs, two of them: 2P and CP
			(optional: include the following to assign repro program parameters)
			args.mature_body_weight
			args.estrus_count
			args.estrus_day
			args.tai_program_start_day_h
			args.synch_ed_program_start_day_h
			args.synch_ed_estrus_day
			args.stop_day
			args.conception_rate
			args.ai_day
			args.abortion_day
			args.days_in_preg
			args.gestation_length
		Output:
	'''
	def __init__(self, args):
		super().__init__(args)

		if 'mature_body_weight' in args:
			self.assign_heiferII_values(args)
		else:
			self.init_values(args)
		
	'''
		Initialize repro program values
	'''
	def init_values(self, args):
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

	'''
		Assign the repro program with given vales
	'''
	def assign_heiferII_values(self, args):
		self.repro_program = args['repro_program']
		self.mature_body_weight = args['mature_body_weight']

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
		self.stop_day = args['stop_day']

		self.conception_rate = args['conception_rate']
		self.ai_day = args['ai_day']
		self.abortion_day = args['abortion_day']
		self.days_in_preg = args['days_in_preg']
		self.preg = self.days_in_preg != 0
		self.gestation_length = args['gestation_length']

	'''
		Get current information from the heiferII
	'''
	def get_heiferII_values(self):
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
            'stop_day': self.stop_day,
            'conception_rate': self.conception_rate,
            'ai_day': self.ai_day,
            'abortion_day': self.abortion_day,
            'days_in_preg': self.days_in_preg,
            'gestation_length': self.gestation_length
        }
		return values

	'''
       	Calculates this heiferII's nutrient requirements.
    '''
	def calc_nutrient_rqmts(self):
		self.nutrient_rqmts, self.DMIest, self.DBW = calculate_rqmts()
		
	'''
		Calculates and sets the manure excretion components.
	'''  
	def calc_manure_excretion(self, feed):
		self.manure_excretion = manure_calculations()

	'''
		Sets this animal's ration formulation.
		Args:
			ration_formulation: dictionary representing the calculated ration
	'''
	def set_ration(self, ration_formulation, feed):
		self.ration_formulation = ration_formulation  
		self.dry_matter_intake = 0
		for key in ration_formulation:
			if key in feed.managed_feed_names:
				DM_feed_amount = ration_formulation[key]
				self.dry_matter_intake += DM_feed_amount
		
	'''
		Description:
			controls heifer's grow with average daily gain based on user's input untill breeding start day
			here is the place to change growth rate with heifer feeding methods later when we have heifer nutrition from the ration furmulation module
			breeding start with assigned reproduction program
			time to move to the 3rd stage -- replacement stage determined based on gestion length and user input of replacement timw
			culling for reproduction problem occur when heifer doesn't get pregnant for a long time
		Input:
		Output:
			cull_stage: culling for reproduction failure
			third_stage: move to next stage -- heiferIII stage when time comes
	'''
	def update(self):
		cull_stage = False
		third_stage = False
		
		prev_weight = self.body_weight
		self.days_born += 1

		if self.days_born < AnimalBase.config['grow_end_day']:
			# Heifer can only grow to a maximum weight of mature_body_weight
			if self.body_weight < AnimalBase.config['mature_body_weight']:
				gained_weight = np.random.normal(AnimalBase.config['avg_daily_gain_h'], AnimalBase.config['std_daily_gain_h'])
				while gained_weight < AnimalBase.config['avg_daily_gain_h'] - 2 * AnimalBase.config['std_daily_gain_h'] \
					or gained_weight > AnimalBase.config['avg_daily_gain_h'] + 2 * AnimalBase.config['std_daily_gain_h']:
					gained_weight = np.random.normal(AnimalBase.config['avg_daily_gain_h'], AnimalBase.config['std_daily_gain_h'])
				self.body_weight += gained_weight
			if self.body_weight > AnimalBase.config['mature_body_weight']:
				self.body_weight = AnimalBase.config['mature_body_weight']
				self.mature_body_weight = self.body_weight
				self.events.add_event(self.days_born, 'Mature body weight prior to grow end day')
		
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
			if self.days_in_preg == self.gestation_length - AnimalBase.config['replacement_day']:
				self.days_born -= 1	# will be increment again in next stage
				third_stage = True
				self.events.add_event(self.days_born, 'moving to heiferIII')
		# cull heifer for reproduction reason
		if not self.preg and self.days_born > AnimalBase.config['heifer_repro_cull_time']:
			self.events.add_event(self.days_born, 'Cull for heifer repro problem')
			cull_stage = True

		return cull_stage, third_stage

	################ ED methods #################

	'''
		Description:
			in estrus detection program, determine estrus day and estrus note
		Input:
			start_date: start day of a estrus cycle, 1st day when breeding start or last estrus happend or return estrus from preg loss
			estrus_note: note of this estrus
		Output:
			estrus_day: the day when this estrus should occur
	'''
	def _determine_estrus_day(self, start_date, estrus_note):
		estrus_cycle = np.random.normal(AnimalBase.config['avg_estrus_cycle_h'], AnimalBase.config['std_estrus_cycle_h'])
		while estrus_cycle < AnimalBase.config['avg_estrus_cycle_h'] - 2 * AnimalBase.config['std_estrus_cycle_h'] \
			or estrus_cycle > AnimalBase.config['avg_estrus_cycle_h'] + 2 * AnimalBase.config['std_estrus_cycle_h']:
			estrus_cycle = np.random.normal(AnimalBase.config['avg_estrus_cycle_h'], AnimalBase.config['std_estrus_cycle_h'])
		estrus_day =  int(start_date + estrus_cycle)
		self.events.add_event(estrus_day, estrus_note)
		return estrus_day

	'''
		Description:
			return estrus after estrus not detected or not serviced
	'''
	def _return_estrus(self):
		self.estrus_day = self._determine_estrus_day(self.estrus_day, 'Estrus')

	'''
		Description:
			return estrus after AI
	'''
	def _after_ai_estrus(self):
		self.estrus_day = self._determine_estrus_day(self.estrus_day, 'Estrus after AI')

	'''
		Description:
			return estrus after abortion at preg check
	'''
	def _after_abortion_estrus(self):
		self.estrus_day = self._determine_estrus_day(self.abortion_day, 'Estrus after abortion')

	'''
		Description:
			estrus occur at estrus day,
			estrus detected with detection rate,
			service proformed with service rate,
			conception successed with conception rate
	'''
	def _ed_update(self):
		if self.days_born == AnimalBase.config['breeding_start_day_h']:
			self.estrus_day = self._determine_estrus_day(AnimalBase.config['breeding_start_day_h'], 'First estrus')

		# if on estrus day, start detecting estrus
		if self.days_born == self.estrus_day:
			self.estrus_count += 1

			estrus_detection_rand = random()
			if estrus_detection_rand < AnimalBase.config['estrus_detection_rate']:
				# Estrus detected
				self.events.add_event(self.days_born, 'Estrus detected')
				ed_service_rand = random()
				if ed_service_rand < AnimalBase.config['estrus_service_rate']:
					# serviced
					self.ai_day = self.estrus_day + 1
					self.conception_rate = AnimalBase.config['estrus_conception_rate']
				else:
					self._return_estrus()
			else:
				self._return_estrus()

	################ TAI methods #################

	'''
		Description:
			determine the program start time when reach breeding start time
		Input:
			date: the time breeding program start
		Output:
	'''
	def _determine_tai_program_day(self, date):
		self.tai_program_start_day_h = date

	'''
		Description:
			determine the TAI restart date after abortion preg checks
	'''
	def _tai_program_day_after_abortion(self):
		self.tai_program_start_day_h = self.abortion_day + 1

	'''
		Description:
			5dCG2P protocol for tai method
	'''
	def _5dCG2P_update(self):
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

	'''
		Description:
			5dCGP protocol for tai method
	'''
	def _5dCGP_update(self):
		if self.days_born == self.tai_program_start_day_h:
			self.events.add_event(self.days_born, 'Inject GnRH')
		elif self.days_born == self.tai_program_start_day_h + 5:
			self.events.add_event(self.days_born, 'Inject PGF')
		elif self.days_born == self.tai_program_start_day_h + 8:
			self.ai_day = self.days_born
			self.conception_rate = AnimalBase.config['m5dCGP_conception_rate']
			self.events.add_event(self.days_born, 'Inject GnRH')

	'''
		Description:
			user defined protocol for tai method
	'''
	def _user_defined_update(self):
		if self.days_born == self.tai_program_start_day_h + AnimalBase.config['tai_program_length']:
			self.ai_day = self.days_born
			self.conception_rate = AnimalBase.config['defined_conception_rate']

	'''
		Description:
			tai method update, assign tai method
	'''
	def _tai_update(self):
		if self.days_born == AnimalBase.config['breeding_start_day_h']:
			self._determine_tai_program_day(AnimalBase.config['breeding_start_day_h'])

		if self.tai_method_h == '5dCG2P':
			self._5dCG2P_update()
		elif self.tai_method_h == '5dCGP':
			self._5dCGP_update()
		elif self.tai_method_h == 'user_defined':
			self._user_defined_update()

	################ synch-ED methods #################

	'''
		Description:
			determine the program start time when reach breeding start time
		Input:
			date: the time breeding program start
		Output:
	'''
	def _determine_synch_ed_program_day(self, date):
		self.synch_ed_program_start_day_h = date

	'''
		Description:
			determine synch ed leading estrus start day, with nornal distribution
		Input:
			date: start of the synch ed day
			avg: average of estrus occur after synch ed
			std: standard diviation of synch ed
			max: max value can go for the normal distribution, avoiding negtive value
		Output:
	'''
	def _determine_synch_ed_estrus_day(self, date, avg, std, max):
		synch_ed_estrus = np.random.normal(avg, std)
		while synch_ed_estrus < avg - 2 * std or synch_ed_estrus > avg + 2 * std:
			synch_ed_estrus = np.random.normal(avg, std)
		norm = abs(synch_ed_estrus)
		if norm >= max:
			norm = max - 1
		self.synch_ed_estrus_day = int(date + norm)

	'''
		Description:
			return to synch ed after abortion when spot at the preg check
	'''
	def _synch_ed_program_day_after_abortion(self):
		self.synch_ed_program_start_day_h = self.abortion_day

	'''
		Description:
			2P protocol for synch ed method
			estrus detection happens when estrus occur
	'''
	def _2P_update(self):
		if self.days_born == self.synch_ed_program_start_day_h:
			self.events.add_event(self.days_born, 'Inject PGF')
			self._determine_synch_ed_estrus_day(self.days_born, 5, 3, 14)

		if self.days_born == self.synch_ed_estrus_day:
			self.events.add_event(self.days_born, 'Estrus occurs')
			estrus_detection_rand = random()
			if estrus_detection_rand < AnimalBase.config['estrus_detection_rate']:
				self.events.add_event(self.days_born, 'Estrus detected')
				ed_service_rand = random()
				if ed_service_rand < AnimalBase.config['estrus_service_rate']:
					self.ai_day = self.synch_ed_estrus_day + 1
					self.conception_rate = AnimalBase.config['ed_conception_rate']
				else:
					if self.days_born - self.synch_ed_program_start_day_h < 14:
						# second round of injection
						self.events.add_event(self.synch_ed_program_start_day_h + 14, 'Inject PGF')
						self._determine_synch_ed_estrus_day(self.synch_ed_program_start_day_h + 14, 3, 2, 7)
					else:
						# second round of injection also failed, roll back to return_synch
						self.stop_day = self.synch_ed_program_start_day_h + 21
						self._determine_synch_ed_program_day(self.stop_day)
			else:
				self.stop_day = self.synch_ed_program_start_day_h + 21
				self._determine_synch_ed_program_day(self.stop_day)

	'''
		Description:
			CP protocol for synch ed method
			estrus detection happens when estrus occur
	'''
	def _CP_update(self):
		if (self.days_born == self.synch_ed_program_start_day_h):
			self.events.add_event(self.days_born, 'Inject CIDR')
		elif (self.days_born == self.synch_ed_program_start_day_h + 7):
			self.events.add_event(self.days_born, 'Inject PGF')
			self._determine_synch_ed_estrus_day(self.days_born, 3, 2, 7)

		if self.days_born == self.synch_ed_estrus_day:
			self.events.add_event(self.days_born, 'Estrus occurs')
			estrus_detection_rand = random()
			if estrus_detection_rand < AnimalBase.config['estrus_detection_rate']:
				self.events.add_event(self.days_born, 'Estrus detected')
				ed_service_rand = random()
				if ed_service_rand < AnimalBase.config['ed_service_rate']:
					self.ai_day = self.synch_ed_estrus_day + 1
					self.conception_rate = AnimalBase.config['ed_conception_rate']
				else:
					self.stop_day = self.synch_ed_program_start_day_h + 14
					self._determine_synch_ed_program_day(self.stop_day)
			else:
				self.stop_day = self.synch_ed_program_start_day_h + 14
				self._determine_synch_ed_program_day(self.stop_day)

	'''
		Description:
			synch ed method update, assign with protocols: 2P or CP
	'''
	def _synch_ed_update(self):
		if self.days_born == AnimalBase.config['breeding_start_day_h']:
			self._determine_synch_ed_program_day(AnimalBase.config['breeding_start_day_h'])

		if self.synch_ed_method_h == '2P':
			self._2P_update()
		elif self.synch_ed_method_h == 'CP':
			self._CP_update()

	################ Preg stage #################

	# after preg loss between 1 and 3 preg checks, return to coresponding protocols
	'''
		Description:
			assign breeding method for open heifers after spot open at preg check
			three methods can be assigned: ED, TAI, synch-ED

	'''
	def _open(self):
		if self.repro_program == 'ED':
			self._after_abortion_estrus()
		elif self.repro_program == 'TAI':
			self._tai_program_day_after_abortion()
		elif self.repro_program == 'synch-ED':
			self._synch_ed_program_day_after_abortion()

	# artificial inseminated and go through 3 preg checks
	'''
		Description:
			update AI for heifers reach ai day, inseminate the heifer with specific semen type
			by comparing with conception rate, if conception success, gestion length determined
			for preg chek 1, confirm the conception
			for preg chek 2 and 3, confirm pregnacy, there are chances of preg loss in each period of time between preg checks
	'''
	def _preg_update(self):
		if self.preg:
			self.days_in_preg += 1

		# AI
		if self.days_born == self.ai_day:
			self.events.add_event(self.days_born, 'Inseminated with {}'.format(AnimalBase.config['semen_type']))
			# conception
			conception_rand = random()
			if conception_rand < self.conception_rate:
				self.days_in_preg = 1
				self.preg = True
				self.gestation_length = int(np.random.normal(AnimalBase.config['avg_gestation_len'], AnimalBase.config['std_gestation_len']))
				while self.gestation_length < AnimalBase.config['avg_gestation_len'] - 2 * AnimalBase.config['std_gestation_len'] \
					or self.gestation_length > AnimalBase.config['avg_gestation_len'] + 2 * AnimalBase.config['std_gestation_len']:
					self.gestation_length = int(np.random.normal(AnimalBase.config['avg_gestation_len'], AnimalBase.config['std_gestation_len']))
				self.events.add_event(self.days_born, 'Heifer pregnant')
			else:
				self.events.add_event(self.days_born, 'Heifer not pregnant')
		# preg check 1
		elif self.days_born == self.ai_day + AnimalBase.config['preg_check_day_1']:
			if self.preg:
				preg_loss_rand = random()
				if preg_loss_rand > AnimalBase.config['preg_loss_rate_1']:
					self.events.add_event(self.days_born, 'Preg check 1, confirmed')
				else:
					self.days_in_preg = 0
					self.preg = False
					self.abortion_day = self.days_born
					self._open()
					self.events.add_event(self.days_born, 'Preg loss happened before 1st preg check')
			else:
				self.abortion_day = self.days_born
				self._open()
				self.events.add_event(self.days_born, 'Preg check 1, not pregnant')
		# preg check 2
		elif self.days_born == self.ai_day + AnimalBase.config['preg_check_day_2']:
			preg_loss_rand = random()
			if preg_loss_rand > AnimalBase.config['preg_loss_rate_2']:
				self.events.add_event(self.days_born, 'Preg check 2, confirmed')
			else:
				self.days_in_preg = 0
				self.preg = False
				self.abortion_day = self.days_born
				self._open()
				self.events.add_event(self.days_born, 'Preg loss happened between 1st and 2nd preg check')
		# preg check 3
		elif self.days_born == self.ai_day + AnimalBase.config['preg_check_day_3']:
			preg_loss_rand = random()
			if preg_loss_rand > AnimalBase.config['preg_loss_rate_3']:
				self.events.add_event(self.days_born, 'Preg check 3, confirmed')
			else:
				self.days_in_preg = 0
				self.preg = False
				self.abortion_day = self.days_born
				self._open()
				self.events.add_event(self.days_born, 'Preg loss happened between 2nd and 3rd preg check')

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
		""".format(self.id,
				   self.birth_date,
				   self.days_born,
				   self.body_weight,
				   AnimalBase.config['breeding_start_day_h'],
				   self.repro_program,
				   self.days_in_preg,
				   self.gestation_length,
				   str(self.events))

		return res_str