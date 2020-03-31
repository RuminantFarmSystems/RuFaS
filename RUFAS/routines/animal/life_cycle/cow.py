'''
RUFAS: Ruminant Farm Systems Model
File name: cow.py
Author(s): Manfei Li, mli497@wisc.edu
		   Militsa Sotirova, militsasotirova@gmail.com
Description: This file updates the cow form first calving to leaving the herd.
			Temp: Body weight change uses equations for lactation cows (decrease for the first 50 days and increase later on)
			Temp: Dry matter intake is calculated by body weight and FCM production.
			TODO: different body weight for different lactations and individual mature body weight.
			TODO: Dry Matter Intake and Body Weight changed could be based on nutrition intake later from Ration Formulation.
			Reproduction program could be chosen from the ED, TAI, ED-TAI projects, reference:
			http://www.dcrcouncil.org/wp-content/uploads/2019/04/Dairy-Cow-Protocol-Sheet-Updated-2018.pdf
			Preg check follows AI for three times.
			Daily milk production is based on breed and parity specific lactation curve model (Wood's and Milkbot) parameters.
			Culling including 3 components: repro, production, and health,
				health culling for 6 reasons: Lameness, Injury, Mastitis, Disease, Udder, and Unknown
'''
###############################################################################

import math
import numpy as np
import matplotlib.pyplot as plt
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.ration.lactating_cow_ration import calculate_rqmts as lactating_calculate_rqmts
from RUFAS.routines.animal.ration.dry_cow_ration import calculate_rqmts as dry_calculate_rqmts
from RUFAS.routines.animal.manure.lactating_cow_manure_excretion import manure_calculations as lactating_manure_calculations
from RUFAS.routines.animal.manure.dry_cow_manure_excretion import manure_calculations as dry_manure_calculations
from random import random

class Cow(HeiferIII):
	'''
		Description:
			initialize the cow from heifer
		Input:
			heiferIII: third stage of heifer, pass heifer information from heiferIII
			args.repro_program: reproduction program used in cow, three of them: ED, TAI, and ED-TAI programs
			args.presynch_method: presych protocols used for presynch programs, four of them: PreSynch, Double OvSynch, G6G, and user_defined
			args.tai_method_c: timed-AI protocols used for reproduction programs, five of them: OvSynch 56, OvSynch 48, CoSynch 72, 5d CoSynch, and user-defined
			args.resynch_method: resynch protocols used for resynch programs, three of them: TAIafterPD, TAIbeforePD, and PGFatPD
		Output:
	'''
	def __init__(self, heiferIII, args):
		super().init_from_heiferIII(heiferIII)

		#current hard-coded values necessary for nutrient requirement calculations
		self.ID = 0     #hard-coded inital value for Identification
		self.weekn = 1
		self.LACT = 1   #Lactation number of the cow
		self.RecDNED = 1
		self.RecDMPD = 100
		self.AVGMILK_kg = 50
		self._BCS = 3.5 #body condition score
		self._CP_milk = 3.2
		self._lactose_milk = 4.85
		self._mPrt = 3.5 #milk protein


		self._DVD = 0 #daily vertical distance, km
		self._DHD = 0 #daily horizontal distance, km
		self._CI = 0 #calving interval, days
		self._CBW = 0 #weight of cow when she gives birth
		self._daily_growth = 0 #change in body weight, kg
		self._calves = 0
		self._milking = False
		self._days_in_milk = 0
		self._estimated_daily_milk_produced = 0
		self._single_acc_milk_prod = 0
		self._future_cull_date = 0
		self._cull_reason = None
		self._repro_program = args['repro_program']
		self._first_ai = False

		# TAI params
		self._presynch_method = args['presynch_method']
		self._tai_method_c = args['tai_method_c']
		self._presynch_program_start_day = 0
		self._tai_program_start_day_c = 0
		self._resynch_method = args['resynch_method']

		# economics counts
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

		#figures
		self._estimated_daily_milk_produced_lst = []
		self._body_weight_lst = []

	'''
		Description:
            initialize the cow in this stage from the third stage of heifer and initialize the repro program parameters for coding purpose
		Input:
			heiferIII: another heifer out of the herd
		Output:
	'''
	def init_from_cow(self, cow):
		super().init_from_heiferIII(Cow)

		#current hard-coded values necessary for nutrient requirement calculations
		self.ID = 0		#hard-coded inital value for Identification
		self._BCS = 3.5 #body condition score
		self._CP_milk = 3.2
		self._lactose_milk = 4.85

		self._daily_growth = 0
		self._calves = cow._calves
		self._milking = cow._milking
		self._days_in_milk = cow._days_in_milk
		self._estimated_daily_milk_produced = cow._estimated_daily_milk_produced
		self._single_acc_milk_prod = cow._single_acc_milk_prod
		self._future_cull_date = cow._future_cull_date
		self._cull_reason = cow._cull_reason
		self._repro_program = cow._repro_program
		self._first_ai = cow._first_ai

		# TAI params
		self._presynch_method = cow._presynch_method
		self._tai_method_c = cow._tai_method_c
		self._presynch_program_start_day = cow._presynch_program_start_day
		self._tai_program_start_day_c = cow._tai_program_start_day_c
		self._resynch_method = cow._resynch_method

		# economics counts
		self._ED_days = cow._ED_days
		self._GnRH_injections = cow._GnRH_injections
		self._PGF_injections = cow._PGF_injections
		self._semen_used = cow._semen_used
		self._AI_times = cow._AI_times
		self._preg_diagnoses = cow._preg_diagnoses
		self._feed_cost = cow._feed_cost
		self._fixed_cost = cow._fixed_cost
		self._milk_income = cow._milk_income

		#figures
		self._estimated_daily_milk_produced_lst = cow._estimated_daily_milk_produced_lst
		self._body_weight_lst = cow._body_weight_lst

	'''
		Description:
			determine parameter value distribution for lactation curve model parameters
		Input:
			mean: mean of the parameter value for l, m, n in wood's model
			std: standard deviation of the parameter value for l, m, n in wood's model
		Output:
			np.random.normal(mean, std): a random value draw from distribution of parameters
	'''
	def _determine_param_value(self, mean, std):
		return np.random.normal(mean, std)

	'''
		Description:
			update milking status for lactating cows
			start at calving, daily milk production estimated by breed and parity specific lactation curves
			TEMP: fat percent, FCM, body weight during lactation, and dry matter intake are coded here with equations with hard-coded parameters just for valid the simulation model indication of the place for future adjustment with ration formulation and ecnomics caculation
		Input:
		Output:
			estimated_daily_milk_produced: estimated daily milk production from the lactation curve
			fat_percent: calculated with days in milk, for temporary use
			daily_fat_correct_milk_production: calculated form estimated milk production and fat percent, for temporary use
	'''
	def _milking_update(self):
		if self._days_in_preg == self._gestation_length - AnimalBase.config['dry_period']:
			self._milking = False
			self._events.add_event(self._days_born, 'dry')
			self._days_in_milk = 0
			self._estimated_daily_milk_produced = 0
			self._estimated_daily_milk_produced_lst.append(self._estimated_daily_milk_produced)
			self._body_weight_lst.append(self._body_weight)
			return 0, 0, 0

		self._days_in_milk += 1
		if self._breed == 'HO':
			breed_index = 0
			parity_index = 2 if self._calves - 1 > 2 else self._calves - 1
		elif self._breed == 'JE':
			breed_index = 1
			parity_index = 2 if self._calves - 1 > 2 else self._calves - 1

		if AnimalBase.config['lactation_curve'] == 'wood':
			l = self._determine_param_value(AnimalBase.config['l'][breed_index][parity_index], AnimalBase.config['l_std'][breed_index][parity_index])
			m = self._determine_param_value(AnimalBase.config['m'][breed_index][parity_index], AnimalBase.config['m_std'][breed_index][parity_index])
			n = self._determine_param_value(AnimalBase.config['n'][breed_index][parity_index], AnimalBase.config['n_std'][breed_index][parity_index])

			estimated_daily_milk_produced = l * \
				math.pow(self._days_in_milk, m) * \
				math.exp((0 - n) * self._days_in_milk)
		elif AnimalBase.config['lactation_curve'] == 'milkbot':
			estimated_daily_milk_produced = AnimalBase.config['a'] * \
				(1 - math.exp((AnimalBase.config['c'] - self._days_in_milk) / AnimalBase.config['b']) / 2) * \
				math.exp((0 - AnimalBase.config['d']) * self._days_in_milk)
		if self._milking:
			self._estimated_daily_milk_produced = estimated_daily_milk_produced
		else:
			self._estimated_daily_milk_produced = 0
		self._single_acc_milk_prod += estimated_daily_milk_produced


		# calculate fat percent in milk and fat corrected milk production
		fat_percent = 12.86 * self._days_in_milk ** (-1.081) * math.exp((0.0926) * (math.log(self._days_in_milk)) ** 2) * (math.log(self._days_in_milk) ** 1.107)
		daily_fat_correct_milk_production = 0.4 * estimated_daily_milk_produced + 0.15 * fat_percent * estimated_daily_milk_produced

		prev_weight = self._body_weight

		# calculate body weight when milking
		if self._calves == 1:
			self._body_weight = self._mature_body_weight * (1-(1-(self._birth_weight/self._mature_body_weight)**(1/3)) * math.exp(-0.0039 * self._days_born)) **3 - (20/65) * self._days_in_milk * math.exp(1-self._days_in_milk/65) + 0.0187**3 * (self._days_in_preg - 50) ** 3
		else:
			self._body_weight = self._mature_body_weight * (1-(1-(self._birth_weight/self._mature_body_weight)**(1/3)) * math.exp(-0.006 * self._days_born)) **3 - (40/75) * self._days_in_milk * math.exp(1-self._days_in_milk/75) + 0.0187**3 * (self._days_in_preg - 50) ** 3

		if not self._milking:
			self._daily_growth = self._body_weight - prev_weight

		self._estimated_daily_milk_produced_lst.append(self._estimated_daily_milk_produced)
		self._body_weight_lst.append(self._body_weight)

		return estimated_daily_milk_produced, fat_percent, daily_fat_correct_milk_production

	'''
       	Calculates this cow's nutrient requirements.
    '''
	def calc_nutrient_rqmts(self, housing, pasture_concentrate, nutrient_rqmts):
		if self._milking:
			result = lactating_calculate_rqmts(self._body_weight, self._BCS, self._CBW, self._CI, pasture_concentrate, self._CP_milk, self._days_in_preg, self._DHD, self._DVD, self._days_in_milk, self._fat_percent, self._lactose_milk, self._estimated_daily_milk_produced, self._calves, housing, nutrient_rqmts)
			self._nutrient_rqmts = result[0]
			self._DMIest = result[1]
			self._DBW = result[2]
			self._daily_growth = self._DBW
		else:
			self._nutrient_rqmts = dry_calculate_rqmts()
		'''
		self._nutrient_rqmts = {'FU': {'op': '<=', 'val': 7.566673489860807}, 'RU': {'op': '>=', 'val': 0}, 'ME_DM': {'op': '>=', 'val': 57.238188330372566}, 'RDP_DM': {'op': '>=', 'val': 2.0347001114951313}, 'RUP_DM': {'op': '>=', 'val': 1.2716733909335047}}
		self._DMIest = 27.620363504458798
		self._DBW = -0.4125
		self._daily_growth = self._DBW
		'''

	'''
       	Calculates this cow's nutrient requirements.
    '''
	def calc_init_nutrient_rqmts(self, vertical_distance, horizontal_distance, housing, pasture_concentrate, nutrient_rqmts):
		self.calc_daily_walking_dist(vertical_distance, horizontal_distance)
		self.calc_nutrient_rqmts(housing, pasture_concentrate, nutrient_rqmts)

	'''
		Calculates and sets the manure excretion components.
	'''
	def calc_manure_excretion(self, feed):
		if self._milking:
			self._manure_excretion = lactating_manure_calculations(self._ration_formulation, feed, self._body_weight, self._days_in_milk, self._mPrt)
		else:
			self._manure_excretion = dry_manure_calculations()
		'''
		self._manure_excretion = {"U": 0.340,
			"TAN_s": 0.14,
			"MN": 532.407,
			"Mkg": 70.792,
			"VSd": 7087.413,
			"VSnd": 859.390}
		'''
	'''
		Sets this animal's ration formulation.
		Args:
			ration_formulation: dictionary representing the calculated ration
	'''
	def set_ration(self, ration_formulation, feed):
		self._ration_formulation = ration_formulation
		self._dry_matter_intake = 0
		for key in ration_formulation:
			if key in feed.managed_feed_names:
				DM_feed_amount = ration_formulation[key]
				self._dry_matter_intake += DM_feed_amount
	'''
		Calculates and sets the animal's daily vertical and horizontal walking distance (DVD and DHD).
		Args:
			vertical_dist_to_parlor: number, km
			horizontal_dist_to_parlor: number, km
	'''
	def calc_daily_walking_dist(self, vertical_dist_to_parlor, horizontal_dist_to_parlor):
		# multiplied by 2 for return trip
		self._DVD = 2 * vertical_dist_to_parlor * AnimalBase.config['cow_times_milked_per_day']
		self._DHD = 2 * horizontal_dist_to_parlor * AnimalBase.config['cow_times_milked_per_day']


	'''
		Description:
			update cow status from the moment of calving, parity+1, milking start, pregnancy stop, and estrus restart
			TEMP: calculate cost and income related values for validating model
		Input:
			record_econ_stats: record cost and income in different functions for temporary use
		Output:
			estimated_daily_milk_produced: estimated daily milk production from the lactation curve
			fat_percent: calculated with days in milk, for temporary use
			daily_fat_correct_milk_production: calculated form estimated milk production and fat percent, for temporary use
			cull_stage: True if a cow is culled, false if it stays in the herd
			new_born: True if a calf is born
	'''
	def update(self, record_econ_stats):
		if self._culled:
			return None

		estimated_daily_milk_produced = 0
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
			birth_description = 'New birth, start milking'
			if self._calves >= 2:
				last_time_given_birth = self._events.get_most_recent_date(birth_description)
				self._CI = self._days_born - last_time_given_birth
			self._CBW = self._body_weight
			self._events.add_event(self._days_born, birth_description)
			self._health_cull_update()
			new_born = True

			# restarting estrus
			if self._repro_program in ['ED', 'ED-TAI']:
				self._restart_estrus()

		estimated_daily_milk_produced = 0
		fat_percent = 0
		daily_fat_correct_milk_production = 0
		# if self._milking:
		estimated_daily_milk_produced, fat_percent, daily_fat_correct_milk_production = self._milking_update()
		if self._repro_program == 'ED':
				self._ed_update(record_econ_stats)
		elif self._repro_program == 'ED-TAI':
				self._ed_tai_update(record_econ_stats)
		elif self._repro_program == 'TAI':
			if self._days_in_milk >= AnimalBase.config['vwp']:
				self._tai_update(record_econ_stats)

		self._fat_percent = fat_percent
		self._preg_update(record_econ_stats)
		cull_stage = self._cull_update(estimated_daily_milk_produced)

		self._economy_update(cull_stage, estimated_daily_milk_produced, record_econ_stats)

		return estimated_daily_milk_produced, fat_percent, daily_fat_correct_milk_production, cull_stage, new_born

	################ ED methods #################
	'''
		Description:
			in estrus detection program, determine estrus day and estrus note
		Input:
			start_date: start day of a estrus cycle, 1st day when breeding start after calving or last estrus happend or return estrus from preg loss
			estrus_note: note of this estrus
			avg: average length for an estrus cycle
			std: standard divation for an estrus cycle
		Output:
			estrus_day: the day when this estrus should occur
	'''
	def _determine_estrus_day(self, start_date, estrus_note, avg, std):
		estrus_day = int(start_date + abs(np.random.normal(avg, std)))
		self._events.add_event(estrus_day, estrus_note)
		return estrus_day

	'''
		Description:
			return estrus after calving
	'''
	def _restart_estrus(self):
		self._estrus_day = self._determine_estrus_day(self._days_born, '1st estrus after calving', AnimalBase.config['avg_estrus_cycle_r'], AnimalBase.config['std_estrus_cycle_r'])

	'''
		Description:
			return estrus after first estrus
	'''
	def _later_estrus(self):
		self._estrus_day = self._determine_estrus_day(self._estrus_day, 'estrus occur before vwp', AnimalBase.config['avg_estrus_cycle_c'], AnimalBase.config['std_estrus_cycle_c'])

	'''
		Description:
			return estrus after estrus not detected or not serveded
	'''
	def _return_estrus(self):
		self._estrus_day = self._determine_estrus_day(self._estrus_day, 'Estrus', AnimalBase.config['avg_estrus_cycle_c'], AnimalBase.config['std_estrus_cycle_c'])

	'''
		Description:
			return estrus after AI
	'''
	def _after_ai_estrus(self):
		self._estrus_day = self._determine_estrus_day(self._estrus_day, 'Estrus after AI', AnimalBase.config['avg_estrus_cycle_c'], AnimalBase.config['std_estrus_cycle_c'])

	'''
		Description:
			return estrus after abortion at preg check
	'''
	def _after_abortion_estrus(self):
		self._estrus_day = self._determine_estrus_day(self._abortion_day, 'Estrus after abortion', AnimalBase.config['avg_estrus_cycle_c'], AnimalBase.config['std_estrus_cycle_c'])

	'''
		Description:
			estrus occur at estrus day,
			estrus detected with detection rate,
			service proformed with service rate,
			conception successed with conception rate
	'''
	def _ed_update(self, record_econ_stats):
		# if on estrus day, start detecting estrus
		if self._days_born == self._estrus_day:
			self._estrus_count += 1

			if 1 <= self._days_in_milk and self._days_in_milk <= AnimalBase.config['vwp']:
				self._later_estrus()
			else:
				estrus_detection_rand = random()
				if estrus_detection_rand < AnimalBase.config['estrus_detection_rate']:
					# Estrus detected
					self._events.add_event(self._days_born, 'Estrus detected')
					estrus_service_rand = random()
					if estrus_service_rand < AnimalBase.config['estrus_service_rate']:
						# serviced
						self._ai_day = self._estrus_day + 1
						self._conception_rate = AnimalBase.config['ed_conception_rate']
					else:
						self._return_estrus()
				else:
					self._return_estrus()

		if self._milking:
			self._ED_days += 1
			if record_econ_stats:
				self._ED_econ_days += 1


	################ TAI methods #################

	'''
		Description:
			determine the program start time when pass voluntary waiting period
		Input:
			date: the time tai program start
		Output:
			_tai_program_start_day_c = date: at this day, the tai program starts
	'''
	def _determine_tai_program_day(self, date):
		self._tai_program_start_day_c = date

	'''
		Description:
			resynch start after calving, resynch method assigned
	'''
	def _tai_program_day_after_preg_check(self, record_econ_stats):
		if self._resynch_method == 'TAIafterPD':
			self._tai_program_start_day_c = self._abortion_day + 1
			self._conception_rate -= AnimalBase.config['conception_rate_decrease']
		elif self._resynch_method == 'TAIbeforePD':
			self._tai_program_start_day_c = self._abortion_day - 6
			self._conception_rate -= AnimalBase.config['conception_rate_decrease']
			if self._tai_method_c in ['OvSynch 56', 'OvSynch 48', 'CoSynch 72']:
				self._events.add_event(self._tai_program_start_day_c, 'Inject GnRH')
				self._GnRH_injections = self._GnRH_injections + 1 if record_econ_stats else self._GnRH_injections
		elif self._resynch_method == 'PGFatPD':
			self._events.add_event(self._days_born, 'Inject PGF')
			self._PGF_injections = self._PGF_injections + 1 if record_econ_stats else self._PGF_injections
			self._tai_program_start_day_c = self._abortion_day + 8
			self._conception_rate -= AnimalBase.config['conception_rate_decrease']

	'''
		Description:
			OvSynch56 protocol for tai method
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
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
			self._conception_rate = AnimalBase.config['ovsynch56_conception_rate']

	'''
		Description:
			OvSynch48 protocol for tai method
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
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
			self._conception_rate = AnimalBase.config['ovsynch48_conception_rate']

	'''
		Description:
			CoSynch72 protocol for tai method
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
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
			self._conception_rate = AnimalBase.config['cosynch72_conception_rate']

	'''
		Description:
			5dCoSynch protocol for tai method
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
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
			self._conception_rate = AnimalBase.config['_5dcosynch_conception_rate']

	'''
		Description:
			user_defined protocol for tai method
	'''
	def _user_defined_update(self):
		if self._days_born == self._tai_program_start_day_c + AnimalBase.config['tai_program_length']:
			self._ai_day = self._days_born
			self._conception_rate = AnimalBase.config['defined_conception_rate_c']

	'''
		Description:
			determine the presynch program start time when pass voluntary waiting period
		Input:
			date: the time presynch program start
		Output:
			_presynch_program_start_day = date: at this day, the presynch program starts
	'''
	def _determine_presynch_program_day(self, date):
		self._presynch_program_start_day = date

	'''
		Description:
			presynch protocol for presynch method
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
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

	'''
		Description:
			oubleovsynch protocol for presynch method
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
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

	'''
		Description:
			g6g protocol for presynch method
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
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

	'''
		Description:
			user_defined_presynch protocol for presynch method
	'''
	def _user_defined_presynch_update(self):
		if self._days_born == self._presynch_program_start_day:
			self._tai_program_start_day_c = self._days_born + AnimalBase.config['presynch_program_length']

	'''
		Description:
			assign tai and presynch method, update time AI method status, TAI can be performed with or without presynch
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
	def _tai_update(self, record_econ_stats):
		if self._days_in_milk == AnimalBase.config['vwp']:
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

	'''
		Description:
			update ED-TAI method, perform estrus detection before the TAI program
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
	def _ed_tai_update(self, record_econ_stats):
		# if on estrus day, start detecting estrus
		if self._days_born == self._estrus_day and self._days_in_milk < AnimalBase.config['tai_program_start_day']:
			self._estrus_count += 1

			if 1 <= self._days_in_milk and self._days_in_milk <= AnimalBase.config['vwp']:
				self._later_estrus()
			else:
				estrus_detection_rand = random()
				if estrus_detection_rand < AnimalBase.config['estrus_detection_rate']:
					# Estrus detected
					self._events.add_event(self._days_born, 'Estrus detected')
					estrus_service_rand = random()
					if estrus_service_rand < AnimalBase.config['estrus_service_rate']:
						# serviced
						self._ai_day = self._estrus_day + 1
						self._conception_rate = AnimalBase.config['ed_conception_rate']
					else:
						self._return_estrus()
				else:
					self._return_estrus()

		if self._milking:
			self._ED_days += 1

		if self._days_in_milk == AnimalBase.config['tai_program_start_day'] and self._ai_day == 0:
			self._estrus_day = 0
			self._determine_tai_program_day(self._days_born)

		if self._days_in_milk == AnimalBase.config['tai_program_start_day'] and self._ai_day == 0:
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

	'''
		Description:
			using ED at the resynch period of ED-TAI
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
	def _resynch_ed_tai(self, record_econ_stats):
		if self._resynch_method == 'TAIafterPD':
			self._tai_program_start_day_c = self._abortion_day + 1
			self._conception_rate -= AnimalBase.config['conception_rate_decrease']
		elif self._resynch_method == 'TAIbeforePD':
			self._tai_program_start_day_c = self._abortion_day - 6
			self._conception_rate -= AnimalBase.config['conception_rate_decrease']
			if self._tai_method_c in ['OvSynch 56', 'OvSynch 48', 'CoSynch 72']:
				self._events.add_event(self._tai_program_start_day_c, 'Inject GnRH')
				self._GnRH_injections = self._GnRH_injections + 1 if record_econ_stats else self._GnRH_injections
		elif self._resynch_method == 'PGFatPD':
			self._events.add_event(self._days_born, 'Inject PGF')
			self._PGF_injections = self._PGF_injections + 1 if record_econ_stats else self._PGF_injections
			self._tai_program_start_day_c = self._abortion_day + 8
			self._conception_rate -= AnimalBase.config['conception_rate_decrease']
			self._estrus_day = self._determine_estrus_day(self._abortion_day, 'estrus after PGF', AnimalBase.config['avg_estrus_cycle_p'], AnimalBase.config['std_estrus_cycle_p'])

	################ Preg methods #################

	'''
		Description:
			assign breeding method for open cows after spot open at preg check
			three methods can be assigned: ED, TAI, ED-TAI
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
	def _open(self, record_econ_stats):
		if self._repro_program == 'ED':
			self._after_abortion_estrus()
		elif self._repro_program == 'TAI':
			self._tai_program_day_after_preg_check(record_econ_stats)
		elif self._repro_program == 'ED-TAI':
			self._resynch_ed_tai(record_econ_stats)

	'''
		Description:
			update AI for cows reach ai day, inseminate the cow with specific semen type
			by comparing with conception rate, if conception success, gestion length determined
			for preg chek 1, confirm the conception
			for preg chek 2 and 3, confirm pregnacy, there are chances of preg loss in each period of time between preg checks
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
	def _preg_update(self, record_econ_stats):
		if self._preg:
			self._days_in_preg += 1

		if self._days_born == self._ai_day:
			self._events.add_event(
				self._days_born, 'Inseminated with {}'.format(AnimalBase.config['semen_type']))
			if record_econ_stats:
				self._semen_used += 1
				self._AI_times += 1
			conception_rand = random()
			if conception_rand < self._conception_rate:
				self._days_in_preg = 1
				self._preg = True
				self._gestation_length = int(np.random.normal(
					AnimalBase.config['avg_gestation_len'], AnimalBase.config['std_gestation_len']))
				self._events.add_event(self._days_born, 'Cow pregnant')
			else:
				if self._repro_program in ['ED', 'ED-TAI']:
					self._ai_day = 0
					self._after_ai_estrus()
				self._events.add_event(self._days_born, 'Cow not pregnant')
		elif self._days_born == self._ai_day + AnimalBase.config['preg_check_day_1']:
			if record_econ_stats:
				self._preg_diagnoses += 1
			if self._preg:
				preg_loss_rand = random()
				if preg_loss_rand > AnimalBase.config['preg_loss_rate_1']:
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
		elif self._days_born == self._ai_day + AnimalBase.config['preg_check_day_2']:
			if record_econ_stats:
				self._preg_diagnoses += 1
			preg_loss_rand = random()
			if preg_loss_rand > AnimalBase.config['preg_loss_rate_2']:
				self._events.add_event(
					self._days_born, 'Preg check 2, confirmed')
			else:
				self._days_in_preg = 0
				self._preg = False
				self._abortion_day = self._days_born
				self._open(record_econ_stats)
				self._events.add_event(
					self._days_born, 'Preg loss happened between 1st and 2nd preg check')
		elif self._days_born == self._ai_day + AnimalBase.config['preg_check_day_3']:
			if record_econ_stats:
				self._preg_diagnoses += 1
			preg_loss_rand = random()
			if preg_loss_rand > AnimalBase.config['preg_loss_rate_3']:
				self._events.add_event(
					self._days_born, 'Preg check 3, confirmed')
			else:
				self._days_in_preg = 0
				self._preg = False
				self._abortion_day = self._days_born
				self._open(record_econ_stats)
				self._events.add_event(
					self._days_born, 'Preg loss happened between 2nd and 3rd preg check')
		if not self._preg and self._days_in_milk > AnimalBase.config['do_not_breed_time']:
			self._do_not_breed = True
			self._events.add_event(self._days_born, 'Do not breed')
			return True


	################ Cull methods #################

	'''
		Description:
			update culling time and cull reasons for cow to leave the herd
			the reasons are reproduction failure, low production, and health issues
		Input:
			record_econ_stats: record income from beef for temporary use
		Output:
			not culled
	'''
	def _cull_update(self, record_econ_stats):
		# if not self._preg and self._days_in_milk > AnimalBase.config['repro_cull_time:
		# 	self._culled = True
		# 	self._events.add_event(self._days_born, 'Cull for repro problem')
		# 	self._cull_reason = "Reproduction failure"
		# 	return True
		if self._do_not_breed and self._days_in_milk > 80 and self._estimated_daily_milk_produced < AnimalBase.config['cull_milk_production']: #estimated_daily_milk_produced < AnimalBase.config['cull_milk_production']:
			self._culled = True
			self._events.add_event(self._days_born, 'Cull for low production')
			self._cull_reason = "Low production"
			return True
		if self._days_born == self._future_cull_date:
			self._culled = True
			self._events.add_event(self._days_born, 'Cull for {}'.format(self._cull_reason))
			return True
		return False

	'''
		Description:
			update cows culled for health problem, first cull or not in this parity will be determined with parity specific culling rate
				then a cull reason will be determined by random draw
				then a cull day will be identified by reverse a distribution for cases of this reason
	'''
	def _health_cull_update(self):
		inv_cull_rate = 0
		if self._calves >= 4:
			inv_cull_rate = AnimalBase.config['parity_cull_prob'][3]
		else:
			inv_cull_rate = AnimalBase.config['parity_cull_prob'][self._calves-1]
		cull_rand = random()
		if (cull_rand <= inv_cull_rate):
			cull_reason_rand = random()
			cull_reason_cp = []
			if (cull_reason_rand <= 0.1633):
				cull_reason_cp = AnimalBase.config['feet_leg_cp']
				self._cull_reason = "Lameness"
			elif (cull_reason_rand <= 0.4516):
				cull_reason_cp = AnimalBase.config['injury_cp']
				self._cull_reason = "Injury"
			elif (cull_reason_rand <= 0.6955):
				cull_reason_cp = AnimalBase.config['mastitis_cp']
				self._cull_reason = "Mastitis"
			elif (cull_reason_rand <= 0.8346):
				cull_reason_cp = AnimalBase.config['disease_cp']
				self._cull_reason = "Disease"
			elif (cull_reason_rand <= 0.8991):
				cull_reason_cp = AnimalBase.config['udder_cp']
				self._cull_reason = "Udder"
			else:
				cull_reason_cp = AnimalBase.config['unkown_cp']
				self._cull_reason = "Unknown"

			c_upper = c_lower = x_upper = x_lower = 0
			for i in range(len(cull_reason_cp) - 1):
				if (cull_reason_cp[i] <= cull_reason_rand and cull_reason_rand < cull_reason_cp[i+1]):
					c_lower = cull_reason_cp[i]
					c_upper = cull_reason_cp[i+1]
					x_lower = AnimalBase.config['cull_day_count'][i]
					x_upper = AnimalBase.config['cull_day_count'][i+1]
			ai = (x_upper-x_lower) / (c_upper-c_lower)
			self._future_cull_date = round(x_lower + ai * (cull_reason_rand - c_lower) + self._days_born)

	'''
		Description:
			TEMP: update cost and income calculation for feed cost, fixed cost and milking income
		Input:
			AnimalBasecull_stage, estimated_daily_milk_produced, record_econ_stats from temp use
		Output:
	'''
	def _economy_update(self, cull_stage, estimated_daily_milk_produced, record_econ_stats):
		# cow economics
		if record_econ_stats:
			self._feed_cost += self._ration_formulation['objective']

			if cull_stage == False:
				self._fixed_cost += 2.5

			self._milk_income += estimated_daily_milk_produced * 0.40

	'''
		Description:
			TEMP: update breeding method cost and slaughter value of culled cows
		Input:
			_repro_cost, semen_cost, AI_cost, preg_check_cost, _feed_cost, _fixed_cost, _milk_income, slaughter_value for temp use
		Output:
	'''
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

	def draw_curves(self):
		fig = plt.figure()

		ax1 = fig.add_subplot(121)
		ax1.plot(self._estimated_daily_milk_produced_lst)
		ax1.spines['right'].set_visible(False)
		ax1.spines['top'].set_visible(False)
		ax1.set_title("Milk")

		ax2 = fig.add_subplot(122)
		ax2.plot(self._body_weight_lst)
		ax2.spines['right'].set_visible(False)
		ax2.spines['top'].set_visible(False)
		ax2.set_title("Weight")

		plt.plot()
		plt.show()

	def __str__(self):
		res_str = """
			==> Cow: \n
			ID: {} \n
			Enter herd date: {}\n
			Days Born: {}\n
			Body Weight: {}kg\n
			Repro program: {}\n
			Parity: {}\n
			Days in milk: {}\n
			Milk produced: {}kg\n
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
				   self._estimated_daily_milk_produced,
				   self._days_in_preg,
				   self._gestation_length,
				   str(self._events))

		return res_str
