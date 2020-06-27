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
			(In addition to heiferIII information)
			args.repro_program: reproduction program used in cow, three of them: ED, TAI, and ED-TAI programs
			args.presynch_method: presych protocols used for presynch programs, four of them: PreSynch, Double OvSynch, G6G, and user_defined
			args.tai_method_c: timed-AI protocols used for reproduction programs, five of them: OvSynch 56, OvSynch 48, CoSynch 72, 5d CoSynch, and user-defined
			args.resynch_method: resynch protocols used for resynch programs, three of them: TAIafterPD, TAIbeforePD, and PGFatPD
		Output:
	'''
	def __init__(self, args):
		super().__init__(args)

		#current hard-coded values necessary for nutrient requirement calculations
		self.ID = 0     #hard-coded inital value for Identification
		self.DNED_req = 1
		self.DMPD_req = 100
		self.BCS = 3.5 #body condition score
		self.CP_milk = 3.2
		self.lactose_milk = 4.85
		self.mPrt = 3.5 #milk protein


		self.DVD = 0 #daily vertical distance, km
		self.DHD = 0 #daily horizontal distance, km
		self.CI = 0 #calving interval, days
		self.CBW = 0 #weight of cow when she gives birth
		self.daily_growth = 0 #change in body weight, kg
		self.calves = 0
		self.milking = False
		self.days_in_milk = 0
		self.estimated_daily_milk_produced = 0
		self.single_acc_milk_prod = 0
		self.future_cull_date = 0
		self.cull_reason = None
		self.repro_program = args['repro_program']
		self.first_ai = False

		# TAI params
		self.presynch_method = args['presynch_method']
		self.tai_method_c = args['tai_method_c']
		self.presynch_program_start_day = 0
		self.tai_program_start_day_c = 0
		self.resynch_method = args['resynch_method']

		# economics counts
		self.ED_days = 0
		self.ED_econ_days = 0
		self.GnRH_injections = 0
		self.PGF_injections = 0
		self.semen_used = 0
		self.AI_times = 0
		self.preg_diagnoses = 0
		self.feed_cost = 0
		self.fixed_cost = 0
		self.milk_income = 0

		#figures
		self.estimated_daily_milk_produced_lst = []
		self.body_weight_lst = []

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
		if self.days_in_preg == self.gestation_length - AnimalBase.config['dry_period']:
			self.milking = False
			self.events.add_event(self.days_born, 'dry')
			self.days_in_milk = 0
			self.estimated_daily_milk_produced = 0
			self.estimated_daily_milk_produced_lst.append(self.estimated_daily_milk_produced)
			self.body_weight_lst.append(self.body_weight)
			return 0, 0, 0

		self.days_in_milk += 1
		if self.breed == 'HO':
			breed_index = 0
			parity_index = 2 if self.calves - 1 > 2 else self.calves - 1
		elif self.breed == 'JE':
			breed_index = 1
			parity_index = 2 if self.calves - 1 > 2 else self.calves - 1

		if AnimalBase.config['lactation_curve'] == 'wood':
			l = self._determine_param_value(AnimalBase.config['l'][breed_index][parity_index], AnimalBase.config['l_std'][breed_index][parity_index])
			m = self._determine_param_value(AnimalBase.config['m'][breed_index][parity_index], AnimalBase.config['m_std'][breed_index][parity_index])
			n = self._determine_param_value(AnimalBase.config['n'][breed_index][parity_index], AnimalBase.config['n_std'][breed_index][parity_index])

			estimated_daily_milk_produced = l * \
				math.pow(self.days_in_milk, m) * \
				math.exp((0 - n) * self.days_in_milk)
		elif AnimalBase.config['lactation_curve'] == 'milkbot':
			estimated_daily_milk_produced = AnimalBase.config['a'] * \
				(1 - math.exp((AnimalBase.config['c'] - self.days_in_milk) / AnimalBase.config['b']) / 2) * \
				math.exp((0 - AnimalBase.config['d']) * self.days_in_milk)
		if self.milking:
			self.estimated_daily_milk_produced = estimated_daily_milk_produced
		else:
			self.estimated_daily_milk_produced = 0
		self.single_acc_milk_prod += estimated_daily_milk_produced


		# calculate fat percent in milk and fat corrected milk production
		fat_percent = 12.86 * self.days_in_milk ** (-1.081) * math.exp((0.0926) * (math.log(self.days_in_milk)) ** 2) * (math.log(self.days_in_milk) ** 1.107)
		daily_fat_correct_milk_production = 0.4 * estimated_daily_milk_produced + 0.15 * fat_percent * estimated_daily_milk_produced

		prev_weight = self.body_weight

		# calculate body weight when milking
		if self.calves == 1:
			self.body_weight = self.mature_body_weight * (1-(1-(self.birth_weight/self.mature_body_weight)**(1/3)) * math.exp(-0.0039 * self.days_born)) **3 - (20/65) * self.days_in_milk * math.exp(1-self.days_in_milk/65) + 0.0187**3 * (self.days_in_preg - 50) ** 3
		else:
			self.body_weight = self.mature_body_weight * (1-(1-(self.birth_weight/self.mature_body_weight)**(1/3)) * math.exp(-0.006 * self.days_born)) **3 - (40/75) * self.days_in_milk * math.exp(1-self.days_in_milk/75) + 0.0187**3 * (self.days_in_preg - 50) ** 3

		if not self.milking:
			self.daily_growth = self.body_weight - prev_weight

		self.estimated_daily_milk_produced_lst.append(self.estimated_daily_milk_produced)
		self.body_weight_lst.append(self.body_weight)

		return estimated_daily_milk_produced, fat_percent, daily_fat_correct_milk_production

	'''
       	Calculates this cow's nutrient requirements.
    '''

	def calc_nutrient_rqmts(self, housing, pasture_concentrate, nutrient_rqmts):
		if self.milking:
			result = lactating_calculate_rqmts(self.body_weight, self.BCS, self.CBW, self.CI, pasture_concentrate, self.CP_milk, self.days_in_preg, self.DHD, self.DVD, self.days_in_milk, self.fat_percent, self.lactose_milk, self.estimated_daily_milk_produced, self.calves, housing, nutrient_rqmts)
			self.nutrient_rqmts = result[0]
			self.DMIest = result[1]
			self.DBW = result[2]
			self.daily_growth = self.DBW
		else:
			self.nutrient_rqmts = dry_calculate_rqmts()
		'''
		self.nutrient_rqmts = {'FU': {'op': '<=', 'val': 7.566673489860807}, 'RU': {'op': '>=', 'val': 0}, 'ME_DM': {'op': '>=', 'val': 57.238188330372566}, 'RDP_DM': {'op': '>=', 'val': 2.0347001114951313}, 'RUP_DM': {'op': '>=', 'val': 1.2716733909335047}}
		self.DMIest = 27.620363504458798
		self.DBW = -0.4125
		self.daily_growth = self.DBW
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
		if self.milking:
			self.manure_excretion = lactating_manure_calculations(self.ration_formulation, feed, self.body_weight, self.days_in_milk, self.mPrt)
		else:
			self.manure_excretion = dry_manure_calculations()
		'''
		self.manure_excretion = {"U": 0.340,
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
		self.ration_formulation = ration_formulation
		self.dry_matter_intake = 0
		for key in ration_formulation:
			if key in feed.managed_feed_names:
				DM_feed_amount = ration_formulation[key]
				self.dry_matter_intake += DM_feed_amount
	'''
		Calculates and sets the animal's daily vertical and horizontal walking distance (DVD and DHD).
		Args:
			vertical_dist_to_parlor: number, km
			horizontal_dist_to_parlor: number, km
	'''
	def calc_daily_walking_dist(self, vertical_dist_to_parlor, horizontal_dist_to_parlor):
		# multiplied by 2 for return trip
		self.DVD = 2 * vertical_dist_to_parlor * AnimalBase.config['cow_times_milked_per_day']
		self.DHD = 2 * horizontal_dist_to_parlor * AnimalBase.config['cow_times_milked_per_day']


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
		if self.culled:
			return None

		estimated_daily_milk_produced = 0
		cull_stage = False
		new_born = False
		self.days_born += 1

		if self.preg and self.days_in_preg == self.gestation_length:
			self.calves += 1
			self.milking = True
			self.days_in_milk = 0
			self.preg = False
			self.days_in_preg = 0
			self.gestation_length = 0
			birth_description = 'New birth, start milking'
			if self.calves >= 2:
				last_time_given_birth = self.events.get_most_recent_date(birth_description)
				self.CI = self.days_born - last_time_given_birth
			self.CBW = self.body_weight
			self.events.add_event(self.days_born, birth_description)
			self._health_cull_update()
			new_born = True

			# restarting estrus
			if self.repro_program in ['ED', 'ED-TAI']:
				self._restart_estrus()

		estimated_daily_milk_produced = 0
		fat_percent = 0
		daily_fat_correct_milk_production = 0
		# if self.milking:
		estimated_daily_milk_produced, fat_percent, daily_fat_correct_milk_production = self._milking_update()
		if self.repro_program == 'ED':
				self._(record_econ_stats)
		elif self.repro_program == 'ED-TAI':
				self._ed_tai_update(record_econ_stats)
		elif self.repro_program == 'TAI':
			if self.days_in_milk >= AnimalBase.config['vwp']:
				self._tai_update(record_econ_stats)

		self.fat_percent = fat_percent
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
		estrus_cycle = np.random.normal(avg, std)
		while estrus_cycle < avg - 2 * std or estrus_cycle > avg + 2 * std:
			estrus_cycle = np.random.normal(avg, std)
		estrus_day = int(start_date + abs(estrus_cycle))
		self.events.add_event(estrus_day, estrus_note)
		return estrus_day

	'''
		Description:
			return estrus after calving
	'''
	def _restart_estrus(self):
		self.estrus_day = self._determine_estrus_day(self.days_born, '1st estrus after calving', AnimalBase.config['avg_estrus_cycle_r'], AnimalBase.config['std_estrus_cycle_r'])

	'''
		Description:
			return estrus after first estrus
	'''
	def _later_estrus(self):
		self.estrus_day = self._determine_estrus_day(self.estrus_day, 'estrus occur before vwp', AnimalBase.config['avg_estrus_cycle_c'], AnimalBase.config['std_estrus_cycle_c'])

	'''
		Description:
			return estrus after estrus not detected or not serveded
	'''
	def _return_estrus(self):
		self.estrus_day = self._determine_estrus_day(self.estrus_day, 'Estrus', AnimalBase.config['avg_estrus_cycle_c'], AnimalBase.config['std_estrus_cycle_c'])

	'''
		Description:
			return estrus after AI
	'''
	def _after_ai_estrus(self):
		self.estrus_day = self._determine_estrus_day(self.estrus_day, 'Estrus after AI', AnimalBase.config['avg_estrus_cycle_c'], AnimalBase.config['std_estrus_cycle_c'])

	'''
		Description:
			return estrus after abortion at preg check
	'''
	def _after_abortion_estrus(self):
		self.estrus_day = self._determine_estrus_day(self.abortion_day, 'Estrus after abortion', AnimalBase.config['avg_estrus_cycle_c'], AnimalBase.config['std_estrus_cycle_c'])

	'''
		Description:
			estrus occur at estrus day,
			estrus detected with detection rate,
			service proformed with service rate,
			conception successed with conception rate
	'''
	def _ed_update(self, record_econ_stats):
		# if on estrus day, start detecting estrus
		if self.days_born == self.estrus_day:
			self.estrus_count += 1

			if 1 <= self.days_in_milk and self.days_in_milk <= AnimalBase.config['vwp']:
				self._later_estrus()
			else:
				estrus_detection_rand = random()
				if estrus_detection_rand < AnimalBase.config['estrus_detection_rate']:
					# Estrus detected
					self.events.add_event(self.days_born, 'Estrus detected')
					estrus_service_rand = random()
					if estrus_service_rand < AnimalBase.config['estrus_service_rate']:
						# serviced
						self.ai_day = self.estrus_day + 1
						self.conception_rate = AnimalBase.config['ed_conception_rate']
					else:
						self._return_estrus()
				else:
					self._return_estrus()

		if self.milking:
			self.ED_days += 1
			if record_econ_stats:
				self.ED_econ_days += 1


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
		self.tai_program_start_day_c = date

	'''
		Description:
			resynch start after calving, resynch method assigned
	'''
	def _tai_program_day_after_preg_check(self, record_econ_stats):
		if self.resynch_method == 'TAIafterPD':
			self.tai_program_start_day_c = self.abortion_day + 1
			self.conception_rate -= AnimalBase.config['conception_rate_decrease']
		elif self.resynch_method == 'TAIbeforePD':
			self.tai_program_start_day_c = self.abortion_day - 6
			self.conception_rate -= AnimalBase.config['conception_rate_decrease']
			if self.tai_method_c in ['OvSynch 56', 'OvSynch 48', 'CoSynch 72']:
				self.events.add_event(self.tai_program_start_day_c, 'Inject GnRH')
				self.GnRH_injections = self.GnRH_injections + 1 if record_econ_stats else self.GnRH_injections
		elif self.resynch_method == 'PGFatPD':
			self.events.add_event(self.days_born, 'Inject PGF')
			self.PGF_injections = self.PGF_injections + 1 if record_econ_stats else self.PGF_injections
			self.tai_program_start_day_c = self.abortion_day + 8
			self.conception_rate -= AnimalBase.config['conception_rate_decrease']

	'''
		Description:
			OvSynch56 protocol for tai method
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
	def _OvSynch56_update(self, record_econ_stats):
		if self.days_born == self.tai_program_start_day_c:
			self.events.add_event(self.days_born, 'Inject GnRH')
			self.GnRH_injections = self.GnRH_injections + 1 if record_econ_stats else self.GnRH_injections
		elif self.days_born == self.tai_program_start_day_c + 7:
			self.events.add_event(self.days_born, 'Inject PGF')
			self.PGF_injections = self.PGF_injections + 1 if record_econ_stats else self.PGF_injections
		elif self.days_born == self.tai_program_start_day_c + 9:
			self.events.add_event(self.days_born, 'Inject GnRH')
			self.GnRH_injections = self.GnRH_injections + 1 if record_econ_stats else self.GnRH_injections
		elif self.days_born == self.tai_program_start_day_c + 10:
			self.ai_day = self.days_born
			self.conception_rate = AnimalBase.config['ovsynch56_conception_rate']

	'''
		Description:
			OvSynch48 protocol for tai method
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
	def _OvSynch48_update(self, record_econ_stats):
		if self.days_born == self.tai_program_start_day_c:
			self.events.add_event(self.days_born, 'Inject GnRH')
			self.GnRH_injections = self.GnRH_injections + 1 if record_econ_stats else self.GnRH_injections
		elif self.days_born == self.tai_program_start_day_c + 7:
			self.events.add_event(self.days_born, 'Inject PGF')
			self.PGF_injections = self.PGF_injections + 1 if record_econ_stats else self.PGF_injections
		elif self.days_born == self.tai_program_start_day_c + 9:
			self.events.add_event(self.days_born, 'Inject GnRH')
			self.GnRH_injections = self.GnRH_injections + 1 if record_econ_stats else self.GnRH_injections
		elif self.days_born == self.tai_program_start_day_c + 10:
			self.ai_day = self.days_born
			self.conception_rate = AnimalBase.config['ovsynch48_conception_rate']

	'''
		Description:
			CoSynch72 protocol for tai method
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
	def _CoSynch72_update(self, record_econ_stats):
		if self.days_born == self.tai_program_start_day_c:
			self.events.add_event(self.days_born, 'Inject GnRH')
			self.GnRH_injections = self.GnRH_injections + 1 if record_econ_stats else self.GnRH_injections
		elif self.days_born == self.tai_program_start_day_c + 7:
			self.events.add_event(self.days_born, 'Inject PGF')
			self.PGF_injections = self.PGF_injections + 1 if record_econ_stats else self.PGF_injections
		elif self.days_born == self.tai_program_start_day_c + 10:
			self.events.add_event(self.days_born, 'Inject GnRH')
			self.GnRH_injections = self.GnRH_injections + 1 if record_econ_stats else self.GnRH_injections
			self.ai_day = self.days_born
			self.conception_rate = AnimalBase.config['cosynch72_conception_rate']

	'''
		Description:
			5dCoSynch protocol for tai method
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
	def _5dCoSynch_update(self, record_econ_stats):
		if self.days_born == self.tai_program_start_day_c:
			self.events.add_event(self.days_born, 'Inject GnRH')
			self.GnRH_injections = self.GnRH_injections + 1 if record_econ_stats else self.GnRH_injections
		elif self.days_born == self.tai_program_start_day_c + 5:
			self.events.add_event(self.days_born, 'Inject PGF')
			self.PGF_injections = self.PGF_injections + 1 if record_econ_stats else self.PGF_injections
		elif self.days_born == self.tai_program_start_day_c + 6:
			self.events.add_event(self.days_born, 'Inject PGF')
			self.PGF_injections = self.PGF_injections + 1 if record_econ_stats else self.PGF_injections
		elif self.days_born == self.tai_program_start_day_c + 8:
			self.events.add_event(self.days_born, 'Inject GnRH')
			self.GnRH_injections = self.GnRH_injections + 1 if record_econ_stats else self.GnRH_injections
			self.ai_day = self.days_born
			self.conception_rate = AnimalBase.config['_5dcosynch_conception_rate']

	'''
		Description:
			user_defined protocol for tai method
	'''
	def _user_defined_update(self):
		if self.days_born == self.tai_program_start_day_c + AnimalBase.config['tai_program_length']:
			self.ai_day = self.days_born
			self.conception_rate = AnimalBase.config['defined_conception_rate_c']

	'''
		Description:
			determine the presynch program start time when pass voluntary waiting period
		Input:
			date: the time presynch program start
		Output:
			_presynch_program_start_day = date: at this day, the presynch program starts
	'''
	def _determine_presynch_program_day(self, date):
		self.presynch_program_start_day = date

	'''
		Description:
			presynch protocol for presynch method
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
	def _presynch_update(self, record_econ_stats):
		if self.days_born == self.presynch_program_start_day:
			self.events.add_event(self.days_born, 'Inject PGF')
			self.PGF_injections = self.PGF_injections + 1 if record_econ_stats else self.PGF_injections
		elif self.days_born == self.presynch_program_start_day + 14:
			self.events.add_event(self.days_born, 'Inject PGF')
			self.PGF_injections = self.PGF_injections + 1 if record_econ_stats else self.PGF_injections
		elif self.days_born == self.presynch_program_start_day + 26:
			self.tai_program_start_day_c = self.days_born
			self.events.add_event(self.days_born, 'PreSynch end')

	'''
		Description:
			oubleovsynch protocol for presynch method
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
	def _doubleovsynch_update(self, record_econ_stats):
		if self.days_born == self.presynch_program_start_day:
			self.events.add_event(self.days_born, 'Inject GnRH')
			self.GnRH_injections = self.GnRH_injections + 1 if record_econ_stats else self.GnRH_injections
		elif self.days_born == self.presynch_program_start_day + 7:
			self.events.add_event(self.days_born, 'Inject PGF')
			self.PGF_injections = self.PGF_injections + 1 if record_econ_stats else self.PGF_injections
		elif self.days_born == self.presynch_program_start_day + 10:
			self.events.add_event(self.days_born, 'Inject GnRH')
			self.GnRH_injections = self.GnRH_injections + 1 if record_econ_stats else self.GnRH_injections
		elif self.days_born == self.presynch_program_start_day + 17:
			self.tai_program_start_day_c = self.days_born
			self.events.add_event(self.days_born, 'Double OvSynch end')

	'''
		Description:
			g6g protocol for presynch method
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
	def _g6g_update(self, record_econ_stats):
		if self.days_born == self.presynch_program_start_day:
			self.events.add_event(self.days_born, 'Inject PGF')
			self.PGF_injections = self.PGF_injections + 1 if record_econ_stats else self.PGF_injections
		elif self.days_born == self.presynch_program_start_day + 2:
			self.events.add_event(self.days_born, 'Inject GnRH')
			self.GnRH_injections = self.GnRH_injections + 1 if record_econ_stats else self.GnRH_injections
		elif self.days_born == self.presynch_program_start_day + 9:
			self.tai_program_start_day_c = self.days_born
			self.events.add_event(self.days_born, 'G6G end')

	'''
		Description:
			user_defined_presynch protocol for presynch method
	'''
	def _user_defined_presynch_update(self):
		if self.days_born == self.presynch_program_start_day:
			self.tai_program_start_day_c = self.days_born + AnimalBase.config['presynch_program_length']

	'''
		Description:
			assign tai and presynch method, update time AI method status, TAI can be performed with or without presynch
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
	def _tai_update(self, record_econ_stats):
		if self.days_in_milk == AnimalBase.config['vwp']:
			if self.presynch_method:
				self._determine_presynch_program_day(self.days_born)
			else:
				self._determine_tai_program_day(self.days_born)

		if self.presynch_method:
			if self.presynch_method == 'PreSynch':
				self._presynch_update(record_econ_stats)
			elif self.presynch_method == 'Double OvSynch':
				self._doubleovsynch_update(record_econ_stats)
			elif self.presynch_method == 'G6G':
				self._g6g_update(record_econ_stats)
			elif self.presynch_method == 'user_defined':
				self._user_defined_presynch_update()

		if self.tai_method_c == 'OvSynch 56':
			self._OvSynch56_update(record_econ_stats)
		elif self.tai_method_c == 'OvSynch 48':
			self._OvSynch48_update(record_econ_stats)
		elif self.tai_method_c == 'CoSynch 72':
			self._CoSynch72_update(record_econ_stats)
		elif self.tai_method_c == '5d CoSynch':
			self._5dCoSynch_update(record_econ_stats)
		elif self.tai_method_c == 'user_defined':
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
		if self.days_born == self.estrus_day and self.days_in_milk < AnimalBase.config['tai_program_start_day']:
			self.estrus_count += 1

			if 1 <= self.days_in_milk and self.days_in_milk <= AnimalBase.config['vwp']:
				self._later_estrus()
			else:
				estrus_detection_rand = random()
				if estrus_detection_rand < AnimalBase.config['estrus_detection_rate']:
					# Estrus detected
					self.events.add_event(self.days_born, 'Estrus detected')
					estrus_service_rand = random()
					if estrus_service_rand < AnimalBase.config['estrus_service_rate']:
						# serviced
						self.ai_day = self.estrus_day + 1
						self.conception_rate = AnimalBase.config['ed_conception_rate']
					else:
						self._return_estrus()
				else:
					self._return_estrus()

		if self.milking:
			self.ED_days += 1

		if self.days_in_milk == AnimalBase.config['tai_program_start_day'] and self.ai_day == 0:
			self.estrus_day = 0
			self._determine_tai_program_day(self.days_born)

		if self.days_in_milk == AnimalBase.config['tai_program_start_day'] and self.ai_day == 0:
			if self.tai_method_c == 'OvSynch 56':
				self._OvSynch56_update(record_econ_stats)
			elif self.tai_method_c == 'OvSynch 48':
				self._OvSynch48_update(record_econ_stats)
			elif self.tai_method_c == 'CoSynch 72':
				self._CoSynch72_update(record_econ_stats)
			elif self.tai_method_c == '5d CoSynch':
				self._5dCoSynch_update(record_econ_stats)
			elif self.tai_method_c == 'user_defined':
				self._user_defined_update()

	'''
		Description:
			using ED at the resynch period of ED-TAI
		Input:
			record_econ_stats: record injection counts in this protocol, for temparary use
		Output:
	'''
	def _resynch_ed_tai(self, record_econ_stats):
		if self.resynch_method == 'TAIafterPD':
			self.tai_program_start_day_c = self.abortion_day + 1
			self.conception_rate -= AnimalBase.config['conception_rate_decrease']
		elif self.resynch_method == 'TAIbeforePD':
			self.tai_program_start_day_c = self.abortion_day - 6
			self.conception_rate -= AnimalBase.config['conception_rate_decrease']
			if self.tai_method_c in ['OvSynch 56', 'OvSynch 48', 'CoSynch 72']:
				self.events.add_event(self.tai_program_start_day_c, 'Inject GnRH')
				self.GnRH_injections = self.GnRH_injections + 1 if record_econ_stats else self.GnRH_injections
		elif self.resynch_method == 'PGFatPD':
			self.events.add_event(self.days_born, 'Inject PGF')
			self.PGF_injections = self.PGF_injections + 1 if record_econ_stats else self.PGF_injections
			self.tai_program_start_day_c = self.abortion_day + 8
			self.conception_rate -= AnimalBase.config['conception_rate_decrease']
			self.estrus_day = self._determine_estrus_day(self.abortion_day, 'estrus after PGF', AnimalBase.config['avg_estrus_cycle_p'], AnimalBase.config['std_estrus_cycle_p'])

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
		if self.repro_program == 'ED':
			self._after_abortion_estrus()
		elif self.repro_program == 'TAI':
			self._tai_program_day_after_preg_check(record_econ_stats)
		elif self.repro_program == 'ED-TAI':
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
		if self.preg:
			self.days_in_preg += 1

		if self.days_born == self.ai_day:
			self.events.add_event(
				self.days_born, 'Inseminated with {}'.format(AnimalBase.config['semen_type']))
			if record_econ_stats:
				self.semen_used += 1
				self.AI_times += 1
			conception_rand = random()
			if conception_rand < self.conception_rate:
				self.days_in_preg = 1
				self.preg = True
				self.gestation_length = int(np.random.normal(
					AnimalBase.config['avg_gestation_len'], AnimalBase.config['std_gestation_len']))
				while self.gestation_length < AnimalBase.config['avg_gestation_len'] - 2 * AnimalBase.config['std_gestation_len'] \
					or self.gestation_length > AnimalBase.config['avg_gestation_len'] + 2 * AnimalBase.config['std_gestation_len']:
					self.gestation_length = int(np.random.normal(
					AnimalBase.config['avg_gestation_len'], AnimalBase.config['std_gestation_len']))
				self.events.add_event(self.days_born, 'Cow pregnant')
			else:
				if self.repro_program in ['ED', 'ED-TAI']:
					self.ai_day = 0
					self._after_ai_estrus()
				self.events.add_event(self.days_born, 'Cow not pregnant')
		elif self.days_born == self.ai_day + AnimalBase.config['preg_check_day_1']:
			if record_econ_stats:
				self.preg_diagnoses += 1
			if self.preg:
				preg_loss_rand = random()
				if preg_loss_rand > AnimalBase.config['preg_loss_rate_1']:
					self.events.add_event(
						self.days_born, 'Preg check 1, confirmed')
				else:
					self.days_in_preg = 0
					self.preg = False
					self.abortion_day = self.days_born
					self._open(record_econ_stats)
					self.events.add_event(
						self.days_born, 'Preg loss happened before 1st preg check')
			else:
				self.abortion_day = self.days_born
				self._open(record_econ_stats)
				self.events.add_event(
					self.days_born, 'Preg check 1, not pregnant')
		elif self.days_born == self.ai_day + AnimalBase.config['preg_check_day_2']:
			if record_econ_stats:
				self.preg_diagnoses += 1
			preg_loss_rand = random()
			if preg_loss_rand > AnimalBase.config['preg_loss_rate_2']:
				self.events.add_event(
					self.days_born, 'Preg check 2, confirmed')
			else:
				self.days_in_preg = 0
				self.preg = False
				self.abortion_day = self.days_born
				self._open(record_econ_stats)
				self.events.add_event(
					self.days_born, 'Preg loss happened between 1st and 2nd preg check')
		elif self.days_born == self.ai_day + AnimalBase.config['preg_check_day_3']:
			if record_econ_stats:
				self.preg_diagnoses += 1
			preg_loss_rand = random()
			if preg_loss_rand > AnimalBase.config['preg_loss_rate_3']:
				self.events.add_event(
					self.days_born, 'Preg check 3, confirmed')
			else:
				self.days_in_preg = 0
				self.preg = False
				self.abortion_day = self.days_born
				self._open(record_econ_stats)
				self.events.add_event(
					self.days_born, 'Preg loss happened between 2nd and 3rd preg check')
		if not self.preg and self.days_in_milk > AnimalBase.config['do_not_breed_time']:
			self.do_not_breed = True
			self.events.add_event(self.days_born, 'Do not breed')
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
		# if not self.preg and self.days_in_milk > AnimalBase.config['repro_cull_time:
		# 	self.culled = True
		# 	self.events.add_event(self.days_born, 'Cull for repro problem')
		# 	self.cull_reason = "Reproduction failure"
		# 	return True
		if self.do_not_breed and self.days_in_milk > 80 and self.estimated_daily_milk_produced < AnimalBase.config['cull_milk_production']: #estimated_daily_milk_produced < AnimalBase.config['cull_milk_production']:
			self.culled = True
			self.events.add_event(self.days_born, 'Cull for low production')
			self.cull_reason = "Low production"
			return True
		if self.days_born == self.future_cull_date:
			self.culled = True
			self.events.add_event(self.days_born, 'Cull for {}'.format(self.cull_reason))
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
		if self.calves >= 4:
			inv_cull_rate = AnimalBase.config['parity_cull_prob'][3]
		else:
			inv_cull_rate = AnimalBase.config['parity_cull_prob'][self.calves-1]
		cull_rand = random()
		if (cull_rand <= inv_cull_rate):
			cull_reason_rand = random()
			cull_reason_cp = []
			if (cull_reason_rand <= 0.1633):
				cull_reason_cp = AnimalBase.config['feet_leg_cp']
				self.cull_reason = "Lameness"
			elif (cull_reason_rand <= 0.4516):
				cull_reason_cp = AnimalBase.config['injury_cp']
				self.cull_reason = "Injury"
			elif (cull_reason_rand <= 0.6955):
				cull_reason_cp = AnimalBase.config['mastitis_cp']
				self.cull_reason = "Mastitis"
			elif (cull_reason_rand <= 0.8346):
				cull_reason_cp = AnimalBase.config['disease_cp']
				self.cull_reason = "Disease"
			elif (cull_reason_rand <= 0.8991):
				cull_reason_cp = AnimalBase.config['udder_cp']
				self.cull_reason = "Udder"
			else:
				cull_reason_cp = AnimalBase.config['unkown_cp']
				self.cull_reason = "Unknown"

			c_upper = c_lower = x_upper = x_lower = 0
			for i in range(len(cull_reason_cp) - 1):
				if (cull_reason_cp[i] <= cull_reason_rand and cull_reason_rand < cull_reason_cp[i+1]):
					c_lower = cull_reason_cp[i]
					c_upper = cull_reason_cp[i+1]
					x_lower = AnimalBase.config['cull_day_count'][i]
					x_upper = AnimalBase.config['cull_day_count'][i+1]
			ai = (x_upper-x_lower) / (c_upper-c_lower)
			self.future_cull_date = round(x_lower + ai * (cull_reason_rand - c_lower) + self.days_born)

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
			self.feed_cost += self.ration_formulation['objective']

			if cull_stage == False:
				self.fixed_cost += 2.5

			self.milk_income += estimated_daily_milk_produced * 0.40

	'''
		Description:
			TEMP: update breeding method cost and slaughter value of culled cows
		Input:
			_repro_cost, semen_cost, AI_cost, preg_check_cost, _feed_cost, _fixed_cost, _milk_income, slaughter_value for temp use
		Output:
	'''
	def get_economy_stats(self):
		if self.repro_program == 'ED':
			self.repro_cost = self.ED_days * 0.15
		if self.repro_program == 'TAI':
			self.repro_cost = self.GnRH_injections * 2.4 + self.PGF_injections * 2.65 + (self.GnRH_injections + self.PGF_injections) * 0.25
		if self.repro_program == 'ED-TAI':
			self.repro_cost = self.ED_days * 0.15 + self.GnRH_injections * 2.4 + self.PGF_injections * 2.65 + (self.GnRH_injections + self.PGF_injections) * 0.25

		semen_cost = self.semen_used * 10
		AI_cost = self.AI_times *5
		preg_check_cost = self.preg_diagnoses * 3
		slaughter_value = self.body_weight * 0.65

		return self.repro_cost, semen_cost, AI_cost, preg_check_cost, self.feed_cost, self.fixed_cost, self.milk_income, slaughter_value

	def draw_curves(self):
		fig = plt.figure()

		ax1 = fig.add_subplot(121)
		ax1.plot(self.estimated_daily_milk_produced_lst)
		ax1.spines['right'].set_visible(False)
		ax1.spines['top'].set_visible(False)
		ax1.set_title("Milk")

		ax2 = fig.add_subplot(122)
		ax2.plot(self.body_weight_lst)
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
		""".format(self.id,
				   self.birth_date,
				   self.days_born,
				   self.body_weight,
				   self.repro_program,
				   self.calves,
				   self.days_in_milk,
				   self.estimated_daily_milk_produced,
				   self.days_in_preg,
				   self.gestation_length,
				   str(self.events))

		return res_str
