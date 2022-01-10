"""
RUFAS: Ruminant Farm Systems Model
File name: cow.py
Author(s): Manfei Li, mli497@wisc.edu
        Militsa Sotirova, militsasotirova@gmail.com
Description: This file updates the cow form first calving to leaving the herd.
            Temp: Dry matter intake is calculated by body weight and FCM
            production. Reproduction program could be chosen from the ED, TAI,
            ED-TAI projects, reference:
            http://www.dcrcouncil.org/wp-content/uploads/2019/04/Dairy-Cow-Protocol-Sheet-Updated-2018.pdf
            Preg check follows AI for three times.
            Daily milk production is based on breed and parity specific
            lactation curve model (Wood's and Milkbot) parameters.
            Health culling including 4 components: #TODO death, repro, production, and health,
                health culling for 6 reasons: Lameness, Injury, Mastitis,
                Disease, Udder, and Unknown
"""

import math
import numpy as np
from scipy.stats import truncnorm
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.manure.lactating_cow_manure_excretion import \
    manure_calculations as lactating_manure_calculations
from RUFAS.routines.animal.manure.dry_cow_manure_excretion import \
    manure_calculations as dry_manure_calculations
from random import random
from RUFAS.routines.animal.life_cycle import animal_events_constants as c


class MilkProductionHistory:
    def __init__(self, sim_day, days_in_milk, milk_prod, days_born):
        self.simulation_day = sim_day
        self.days_in_milk = days_in_milk
        self.milk_production = milk_prod
        self.days_born = days_born


class Cow(HeiferIII):
    def __init__(self, args):
        """
        Description:
            initialize the cow from heifer
        Input:
            args.id: id of the animal
            args.breed: breed of the animal
            args.birth_date: the date of the simulation when the calf was born
            args.daysBorn: age of the animal
            args.tai_method_h: timed-AI protocols used for
                reproduction programs, three of them: 5dCG2P,
                5dCGP, and user-defined
            args.synch_ed_method_h: synch ed protocols used for
                reproduction programs, two of them: 2P and CP
            args.repro_program: reproduction program used in cow,
                    three of them: ED, TAI, and ED-TAI programs
            args.presynch_method: presych protocols used for presynch
                programs, four of them: PreSynch, Double OvSynch, G6G,
                and user_defined
            args.tai_method_c: timed-AI protocols used for reproduction
                programs, five of them: OvSynch 56, OvSynch 48, CoSynch 72,
                5d CoSynch, and user-defined
            args.resynch_method: resynch protocols used for resynch
                programs, three of them: TAIafterPD, TAIbeforePD,
                and PGFatPD
            (optional: include the following to assign cow information)
            args.birth_weight: the birth weight of the animal
            args.body_weight: current body weight of the animal
            args.wean_weight: the wean weight of the animal
            args.mature_body_weight: the mature body weight of the animal
            args.events: events of the animal
            args.estrus_count : number of estrus during ED program
			args.estrus_day: the age when the heifer is estrus in ED program
			args.tai_program_start_day_h: start day for heifers in TAI program
			args.synch_ed_program_start_day_h: start day for heifers in synch_ED program
			args.synch_ed_estrus_day: the age when the heifer is estrus in synch_ED program
			args.synch_ed_stop_day: the age the the synch protocol stop for this round
			args.conception_rate: conception rate associated with repro programs and protocols
			args.ai_day: the age of animal for scheduled AI
			args.abortion_day: the age of the animal when abortion happens
			args.days_in_preg: days science pregnancy
			args.gestation_length: the prejected gestation
            args.p_gest_for_calf
            args.days_in_milk: cow's current day in milk
            args.parity: parity of the cow
            args.calving_interval: cow's most recent calving interval
        """
        super().__init__(args)

        # current hard-coded values necessary for nutrient requirement
        # calculations
        self.BCS = 3.5  # body condition score
        self.CP_milk = 3.2
        self.lactose_milk = 4.85
        self.mPrt = 3.5  # milk protein

        self.DVD = 0  # daily vertical distance, km
        self.DHD = 0  # daily horizontal distance, km
        self.CI = 0  # calving interval, days
        self.CI_history = []
        self.BW_at_calving = 0 # weight of cow when she gives birth
        self.calf_birth_weight = args['calf_birth_weight'] # calf birth weight
        self.daily_growth = 0  # change in body weight, kg
        self.calves = 0
        self.calving_to_preg_time = 0
        self.milking = False
        self.days_in_milk = 0
        self.estimated_daily_milk_produced = 0
        self.single_acc_milk_prod = 0
        self.future_cull_date = 0
        self.future_death_date = 0
        self.cull_reason = None
        self.repro_program = AnimalBase.config['cow_repro_method']
        self.first_ai = False
        self.open_stage = False
        self.fat_percent = 0
        # TAI params
        self.presynch_method = AnimalBase.config['cow_presynch_protocol']
        self.tai_method_c = AnimalBase.config['cow_TAI_protocol']
        self.presynch_program_start_day = 0
        self.tai_program_start_day_c = 0
        self.resynch_method = AnimalBase.config['cow_resynch_protocol']

        self.milk_production_history = []

        # grouping nutrition requirement values
        # Required net energy density (Mcal/kg of DM)
        self.DNED_req = 0
        # Required Metabolizing Protein Density (g/kg of DM)
        self.DMPD_req = 0

        if 'days_in_milk' in args:
            self.days_in_milk = args['days_in_milk']
            self.milking = self.days_in_milk != 0
            self.calves = args['parity']
            self.CI = args['calving_interval']

    def update_milk_production_history(self, sim_day):
        """
        Updates the animal's milk production history by appending a
        MilkProductionHistory object to the list.

        Args:
            sim_day: simulation day
        """

        self.milk_production_history.append(MilkProductionHistory(sim_day, self.days_in_milk,
                                                                  self.estimated_daily_milk_produced, self.days_born))

    @staticmethod
    def determine_param_value(mean, std):
        """
        Determine parameter value distribution for lactation curve model
        parameters.
        Args:
            mean: mean of the parameter value for l, m, n in wood's model
            std: standard deviation of the parameter value for l, m, n in
                wood's model
        Returns: a random value draw from distribution of parameters
        """
        return np.random.normal(mean, std)

    def milking_update(self, sim_day, calving_interval):
        """
        Update milking status for lactating cows.
        start at calving, daily milk production estimated by breed and parity
        specific lactation curves.
        TEMP: fat percent, FCM, body weight during lactation, and dry matter
        intake are coded here with equations with hard-coded parameters just
        for valid the simulation model indication of the place for future
        adjustment with ration formulation and economics calculation.

        Returns:
            estimated_daily_milk_produced: estimated daily milk production
                from the lactation curve
            fat_percent: calculated with days in milk, for temporary use
            daily_fat_correct_milk_production: calculated form estimated
                milk production and fat percent, for temporary use
        """
        if self.days_in_preg == AnimalBase.config['days_in_preg_when_dry']:
            self.milking = False
            self.events.add_event(self.days_born, sim_day, c.DRY)
            self.days_in_milk = 0
            self.estimated_daily_milk_produced = 0

            return 0, 0, 0

        breed_index = 0
        parity_index = 0
        if self.milking:
            self.days_in_milk += 1
        else:
            self.days_in_milk = 0

        if self.breed == 'HO':
            breed_index = 0
            parity_index = 2 if self.calves - 1 > 2 else self.calves - 1
        elif self.breed == 'JE':
            breed_index = 1
            parity_index = 2 if self.calves - 1 > 2 else self.calves - 1

        estimated_daily_milk_produced = 0
        if AnimalBase.config['lactation_curve'] == 'wood':
            l = self.determine_param_value(
                AnimalBase.config['wood_l'][breed_index][parity_index],
                AnimalBase.config['wood_l_std'][breed_index][parity_index])
            m = self.determine_param_value(
                AnimalBase.config['wood_m'][breed_index][parity_index],
                AnimalBase.config['wood_m_std'][breed_index][parity_index])
            n = self.determine_param_value(
                AnimalBase.config['wood_n'][breed_index][parity_index],
                AnimalBase.config['wood_n_std'][breed_index][parity_index])
            # TODO adding milkbot parameters

            estimated_daily_milk_produced = \
                l * math.pow(self.days_in_milk, m) * \
                math.exp((0 - n) * self.days_in_milk)
        elif AnimalBase.config['lactation_curve'] == 'milkbot':
            estimated_daily_milk_produced = AnimalBase.config['a'] * \
                                            (1 - math.exp((AnimalBase.config['c'] - self.days_in_milk) /
                                                          AnimalBase.config['b']) / 2) * \
                                            math.exp((0 - AnimalBase.config['d']) * self.days_in_milk)
        if self.milking:
            self.estimated_daily_milk_produced = estimated_daily_milk_produced
        else:
            self.estimated_daily_milk_produced = 0
        self.single_acc_milk_prod += estimated_daily_milk_produced

        # calculate fat percent in milk and fat corrected milk production
        if self.milking:
            fat_percent = 12.86 * self.days_in_milk ** (-1.081) * math.exp(
                0.0926 * (math.log(self.days_in_milk)) ** 2) * \
                          (math.log(self.days_in_milk) ** 1.107)
            daily_fat_correct_milk_production = \
                0.4 * estimated_daily_milk_produced + \
                0.15 * fat_percent * estimated_daily_milk_produced
        else:
            fat_percent = 0
            daily_fat_correct_milk_production = 0

        self.daily_growth = self.get_bw_change(calving_interval)

        self.body_weight += self.daily_growth

        # if not self.milking:
        # 	self.daily_growth = self.body_weight - prev_weight

        return estimated_daily_milk_produced, fat_percent, \
               daily_fat_correct_milk_production

    def calc_manure_excretion(self, feed, methane_model, ME_intake):
        """
        Calculates and sets the manure excretion components.
        Args:
            feed: instance of the Feed class
            methane_model: methane model used for methane emission calculations
            ME_intake: metabolizable energy intake, Mcal/kg DM
        """
        p_urine, p_feces_excrt = self.calc_base_manure()

        if self.milking:
            self.p_excrt, self.manure_excretion = lactating_manure_calculations(
                self.ration_formulation, feed, self.body_weight,
                self.days_in_milk, self.mPrt, self.estimated_daily_milk_produced,
                p_feces_excrt, p_urine, methane_model, self.fat_percent, ME_intake)
        else:
            self.p_excrt, self.manure_excretion = dry_manure_calculations(
                self.ration_formulation, feed, self.body_weight,
                self.estimated_daily_milk_produced, p_feces_excrt, p_urine, ME_intake)

    def phosphorus_rqmts(self, DMI):
        """
        Calculates and sets the animal's phosphorus requirement.
        Args:
            DMI: the Dry Matter Intake (kg)
        """
        # amount of P required for endogenous losses (g) (A.1EF.E.1)
        self.p_maint_feces = 0.001 * DMI * 1000

        # absorbed P retained for growth (g) (A.1EF.E.3)
        if self.body_weight < self.mature_body_weight:
            self.p_growth = \
                (0.0012 + 0.004635 * (self.mature_body_weight ** 0.22) *
                 (self.body_weight ** (-0.22))) * \
                self.daily_growth / 0.96 * 1000
        else:
            self.p_growth = 0

        # amount pf P required for urine production (g) (A.1EF.E.2)
        p_urine = 0.000002 * self.body_weight * 1000

        # absorbed P retained for fetal growth (g) (A.1EF.E.4)
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

        # amount of P in milk per animal (g) (A.1E.E.5)
        if self.milking:
            p_milk = 0.0009 * self.estimated_daily_milk_produced * 1000
        else:
            p_milk = 0

        # absorbed P required by the animal (g) (A.1EF.E.6)
        p_absorb = p_urine + self.p_maint_feces + self.p_growth + \
                   self.p_gest + p_milk

        # requirement of P from the ration (g) (A.1EF.E.7)
        if self.milking:
            self.p_req = p_absorb / \
                         (1.86696 - 5.01238 * self.p_conc + 5.12286 *
                          self.p_conc ** 2)
        else:
            self.p_req = p_absorb / 0.664

    def calc_daily_walking_dist(
            self, vertical_dist_to_parlor, horizontal_dist_to_parlor):
        """
        Calculates and sets the animal's daily vertical and horizontal
        walking distance (DVD and DHD).
        Args:
            vertical_dist_to_parlor: vertical distance to milking parlor, km
            horizontal_dist_to_parlor: horizontal distance to milking parlor, km
        """
        # multiplied by 2 for return trip
        self.DVD = 2 * vertical_dist_to_parlor * \
                   AnimalBase.config['cow_times_milked_per_day']
        self.DHD = 2 * horizontal_dist_to_parlor * \
                   AnimalBase.config['cow_times_milked_per_day']

    def get_bw_change(self, CI):
        """
        life cycle psedocode @[A.1A.C.56/57/58]
        Calculates the body weight change for a cow. 

        Args:
            CI: the calving interval used in the body weight
                change calculation

        Returns: the daily body weight change for a cow.
        
        """
        # on the calving day
        if self.days_in_preg == self.gestation_length:
            conceptus_growth = - self.conceptus_weight
            self.conceptus_weight = 0
            self.tissue_changed = 0
        # conceptus weight change during pregnancy
        elif self.days_in_preg > 50:
            conceptus_total_weight = (0.0148 * self.gestation_length - 2.408) * self.calf_birth_weight
            conceptus_param = conceptus_total_weight ** (1 / 3) / (self.gestation_length - 50)
            conceptus_growth = 3 * conceptus_param ** 3 * (self.days_in_preg - 50) ** 2
            self.conceptus_weight += conceptus_growth
        else:
            conceptus_growth = 0

        # growth for 1st and 2nd lactation cows
        if self.calves == 1:
            if self.days_in_preg < 1: # before pregnancy
                 target_adg_cow = \
                     (0.92 - 0.82) * 0.96 * self.mature_body_weight / CI
            else: # after pregnancy
                target_adg_cow = \
                     (0.92 * self.mature_body_weight - self.body_weight)/(self.gestation_length - self.days_in_preg+1)
        elif self.calves == 2:
            if self.days_in_preg < 1: # before pregnancy
                target_adg_cow = \
                     (1 - 0.92) * 0.96 * self.mature_body_weight / CI
            else: # after pregnancy
                target_adg_cow = \
                     (self.mature_body_weight - self.body_weight)/(self.gestation_length - self.days_in_preg+1)
        else:  # parity > 2
            target_adg_cow = 0

        if not self.days_in_milk == 0:
            if self.calves == 1:
                bodyweight_tissue = \
                    -20 / 65 * math.exp(1 - self.days_in_milk / 65) + \
                    20 / (65 ** 2) * self.days_in_milk * \
                    math.exp(1 - self.days_in_milk / 65)
                if self.days_in_preg == AnimalBase.config['days_in_preg_when_dry'] - 1:
                     self.tissue_changed = 20 * self.days_in_milk/65 * math.exp(1 - self.days_in_milk/65)
            else:  # parity > 1
                bodyweight_tissue = \
                    -40 / 70 * math.exp(1 - self.days_in_milk / 70) + \
                    40 / (70 ** 2) * self.days_in_milk * \
                    math.exp(1 - self.days_in_milk / 70)
                if self.days_in_preg == AnimalBase.config['days_in_preg_when_dry'] - 1:
                     self.tissue_changed = 40 * self.days_in_milk/70 * math.exp(1 - self.days_in_milk/70)
        else: # dry period
            bodyweight_tissue = self.tissue_changed / (self.gestation_length - AnimalBase.config['days_in_preg_when_dry'])

        return target_adg_cow + conceptus_growth + bodyweight_tissue

    def update(self, sim_day, calving_interval):
        """
        Update cow status from the moment of calving, parity+1,
        milking start, pregnancy stop, and estrus restart.

        Args:
            sim_day: simulation day
            calving_interval: the calving interval used for the daily update
        Returns:
            estimated_daily_milk_produced: estimated daily milk production
                from the lactation curve
            fat_percent: calculated with days in milk, for temporary use
            daily_fat_correct_milk_production: calculated form estimated milk
                production and fat percent, for temporary use
            cull_stage: True if a cow is culled, false if it stays in the herd
            new_born: True if a calf is born
        """
        self.update_body_weight_history(sim_day)
        self.update_milk_production_history(sim_day)
        if self.culled:
            return None

        new_born = False
        self.days_born += 1

        if self.days_in_preg > 0 and self.days_in_preg == self.gestation_length:
            self.calves += 1
            self.milking = True
            self.days_in_milk = 0
            self.days_in_preg = 0
            self.gestation_length = 0 
            if self.calves >= 2:
                last_time_given_birth = \
                    self.events.get_most_recent_date(c.NEW_BIRTH)
                self.CI = self.days_born - last_time_given_birth
                self.CI_history.append(self.CI)
            self.BW_at_calving = self.body_weight
            self.events.add_event(self.days_born, sim_day, c.NEW_BIRTH)
            self.health_cull_update()
            self.death_update()
            new_born = True

            # restarting estrus
            if self.repro_program in ['ED','ED-TAI']:
                self.estrus_day = self.determine_estrus_day(
                    self.days_born, c.ESTRUS_AFTER_CALVING_NOTE,
                    AnimalBase.config['avg_estrus_cycle_return'],
                    AnimalBase.config['std_estrus_cycle_return'], sim_day)
            # get presynch method from input
            if self.repro_program in ['TAI','ED-TAI']:
                self.presynch_method = AnimalBase.config['cow_presynch_protocol']

        # if self.milking:
        estimated_daily_milk_produced, fat_percent, \
        daily_fat_correct_milk_production = self.milking_update(sim_day, calving_interval)
        if not self.do_not_breed:
            if self.repro_program == 'ED':
                self.ed_update(sim_day)
            elif not self.open_stage:
                if self.repro_program == 'ED-TAI':
                    self.ed_tai_update(sim_day)
                if self.repro_program == 'TAI':
                    if self.days_in_milk >= AnimalBase.config['tai_program_start_day']:
                        self.tai_update(sim_day)

        self.fat_percent = fat_percent
        if not self.do_not_breed:
            self.preg_update(sim_day)
        cull_stage = self.cull_update(sim_day)

        return estimated_daily_milk_produced, fat_percent, \
               daily_fat_correct_milk_production, cull_stage, new_born

    # ED methods
    def determine_estrus_day(self, start_date, estrus_note, avg, std, sim_day):
        """
        In estrus detection program, determine estrus day and estrus note.

        Args:
            start_date: start day of a estrus cycle, 1st day when breeding start
                after calving or last estrus happened or return estrus
                from preg loss
            estrus_note: note of this estrus
            avg: average length for an estrus cycle
            std: standard deviation for an estrus cycle

        Returns: the day when this estrus should occur
        """
        estrus_cycle = truncnorm.rvs(-2, 2, avg, std)
        estrus_day = int(start_date + abs(estrus_cycle))
        self.events.add_event(estrus_day, sim_day, estrus_note)
        return estrus_day

    def ed_update(self, sim_day):
        """
        Estrus occur at estrus day,
        estrus detected with detection rate,
        service performed with service rate,
        conception succeed with conception rate
        Args:
            sim_day: simulation day
        """
        # if on estrus day, start detecting estrus
        if self.days_born == self.estrus_day:
            self.estrus_count += 1

            if 1 <= self.days_in_milk < AnimalBase.config['voluntary_waiting_period']:
                self.estrus_day = self.determine_estrus_day(
                    self.days_born, c.ESTRUS_BEFORE_VWP_NOTE,
                    AnimalBase.config['avg_estrus_cycle_cow'],
                    AnimalBase.config['std_estrus_cycle_cow'], sim_day)
            elif not self.do_not_breed:
                estrus_detection_rand = random()
                if estrus_detection_rand < AnimalBase.config['estrus_detection_rate']:
                    # Estrus detected
                    self.events.add_event(self.days_born, sim_day, c.ESTRUS_DETECTED)
                    estrus_service_rand = random()
                    if estrus_service_rand < AnimalBase.config['estrus_insemination_rate']:
                        # serviced
                        self.ai_day = self.estrus_day + 1
                        self.open_stage = False
                        self.conception_rate = AnimalBase.config['estrus_conception_rate']
                    # go to next estrus cycle, not back to estrus during resynch process
                    elif self.open_stage == False:
                        # go to next estrus cycle
                        self.estrus_day = self.determine_estrus_day(
                            self.days_born, c.BASIC_ESTRUS_NOTE,
                            AnimalBase.config['avg_estrus_cycle_cow'],
                            AnimalBase.config['std_estrus_cycle_cow'], sim_day)
                # go to next estrus cycle, not back to estrus during resynch process
                elif self.open_stage == False:
                    self.estrus_day = self.determine_estrus_day(
                        self.days_born, c.BASIC_ESTRUS_NOTE,
                        AnimalBase.config['avg_estrus_cycle_cow'],
                        AnimalBase.config['std_estrus_cycle_cow'], sim_day)

        if self.milking and not self.do_not_breed:
            self.ED_days += 1

    # TAI methods
    def OvSynch56_update(self, sim_day):
        """
        OvSynch56 protocol for tai method
        Args:
            sim_day: the simulation day
        """
        if not self.do_not_breed:
            if self.days_born == self.tai_program_start_day_c:
                self.events.add_event(self.days_born, sim_day, c.INJECT_GNRH)
                self.GnRH_injections = self.GnRH_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 7:
                self.events.add_event(self.days_born, sim_day, c.INJECT_PGF)
                self.PGF_injections = self.PGF_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 9:
                self.events.add_event(self.days_born, sim_day, c.INJECT_GNRH)
                self.GnRH_injections = self.GnRH_injections + 1
                # the next day ai
                self.ai_day = self.days_born + 1
                self.open_stage = False
                self.conception_rate = AnimalBase.config['ovsynch56_conception_rate']

    def OvSynch48_update(self, sim_day):
        """
        OvSynch48 protocol for tai method
        Args:
            sim_day: the simulation day
        """
        if not self.do_not_breed:
            if self.days_born == self.tai_program_start_day_c:
                self.events.add_event(self.days_born, sim_day, c.INJECT_GNRH)
                self.GnRH_injections = self.GnRH_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 7:
                self.events.add_event(self.days_born, sim_day, c.INJECT_PGF)
                self.PGF_injections = self.PGF_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 9:
                self.events.add_event(self.days_born, sim_day, c.INJECT_GNRH)
                self.GnRH_injections = self.GnRH_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 10:
                self.ai_day = self.days_born
                self.conception_rate = \
                    AnimalBase.config['ovsynch48_conception_rate']

    def CoSynch72_update(self, sim_day):
        """
        CoSynch72 protocol for tai method, not to be used in resynch protocol in ["TAIafterPD" and "PGFatPD"]
        Args:
            sim_day: the simulation day
        """
        if not self.do_not_breed:
            if self.days_born == self.tai_program_start_day_c:
                self.events.add_event(self.days_born, sim_day, c.INJECT_GNRH)
                self.GnRH_injections = self.GnRH_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 7:
                self.events.add_event(self.days_born, sim_day, c.INJECT_PGF)
                self.PGF_injections = self.PGF_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 10:
                self.events.add_event(self.days_born, sim_day, c.INJECT_GNRH)
                self.GnRH_injections = self.GnRH_injections + 1
                self.ai_day = self.days_born
                self.conception_rate = \
                    AnimalBase.config['cosynch72_conception_rate']

    def d5CoSynch_update(self, sim_day):
        """
        5dCoSynch protocol for tai method, not to be used in resynch protocol in ["TAIafterPD" and "PGFatPD"]
        Args:
            sim_day: the simulation day
        """
        if not self.do_not_breed:
            if self.days_born == self.tai_program_start_day_c:
                self.events.add_event(self.days_born, sim_day, c.INJECT_GNRH)
                self.GnRH_injections = self.GnRH_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 5:
                self.events.add_event(self.days_born, sim_day, c.INJECT_PGF)
                self.PGF_injections = self.PGF_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 6:
                self.events.add_event(self.days_born, sim_day, c.INJECT_PGF)
                self.PGF_injections = self.PGF_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 8:
                self.events.add_event(self.days_born, sim_day, c.INJECT_GNRH)
                self.GnRH_injections = self.GnRH_injections + 1
                self.ai_day = self.days_born
                self.conception_rate = \
                    AnimalBase.config['cosynch5d_conception_rate']

    def presynch_update(self, sim_day):
        """
        Presynch protocol for presynch method
        Args:
            sim_day: the simulation day
        """
        if self.days_born == self.presynch_program_start_day:
            self.events.add_event(self.days_born, sim_day, c.INJECT_PGF)
            self.PGF_injections = self.PGF_injections + 1
        elif self.days_born == self.presynch_program_start_day + 14:
            self.events.add_event(self.days_born, sim_day, c.INJECT_PGF)
            self.PGF_injections = self.PGF_injections + 1
            self.determine_synch_ed_estrus_day(self.days_born, 4, 2, 11)

        elif self.days_born == self.synch_ed_estrus_day:
            self.events.add_event(self.days_born, sim_day, c.ESTRUS_OCCURRED)
            estrus_detection_rand = random()
            if estrus_detection_rand < AnimalBase.config['estrus_detection_rate']:
                self.events.add_event(self.days_born, sim_day, c.ESTRUS_DETECTED)
                ed_insemination_rand = random()
                if ed_insemination_rand < AnimalBase.config['estrus_insemination_rate']:
                    self.ai_day = self.synch_ed_estrus_day + 1
                    self.conception_rate = AnimalBase.config['estrus_conception_rate']

        elif self.days_born == self.presynch_program_start_day + 26:
            self.tai_program_start_day_c = self.days_born
            self.events.add_event(self.days_born, sim_day, c.PRESYNCH_END)

    def doubleovsynch_update(self, sim_day):
        """
        Doubleovsynch protocol for presynch method
        Args:
            sim_day: the simulation day
        """
        if self.days_born == self.presynch_program_start_day:
            self.events.add_event(self.days_born, sim_day, c.INJECT_GNRH)
            self.GnRH_injections = self.GnRH_injections + 1
        elif self.days_born == self.presynch_program_start_day + 7:
            self.events.add_event(self.days_born, sim_day, c.INJECT_PGF)
            self.PGF_injections = self.PGF_injections + 1
        elif self.days_born == self.presynch_program_start_day + 10:
            self.events.add_event(self.days_born, sim_day, c.INJECT_GNRH)
            self.GnRH_injections = self.GnRH_injections + 1
        elif self.days_born == self.presynch_program_start_day + 17:
            self.tai_program_start_day_c = self.days_born
            self.events.add_event(self.days_born, sim_day, c.DOUBLE_OVSYNCH_END)

    def g6g_update(self, sim_day):
        """
        g6g protocol for presynch method.
        Args:
            sim_day: the simulation day
        """
        if self.days_born == self.presynch_program_start_day:
            self.events.add_event(self.days_born, sim_day, c.INJECT_PGF)
            self.PGF_injections = self.PGF_injections + 1
        elif self.days_born == self.presynch_program_start_day + 2:
            self.events.add_event(self.days_born, sim_day, c.INJECT_GNRH)
            self.GnRH_injections = self.GnRH_injections + 1
        elif self.days_born == self.presynch_program_start_day + 9:
            self.tai_program_start_day_c = self.days_born
            self.events.add_event(self.days_born, sim_day, c.C6G_END)

    def tai_update(self, sim_day):
        """
        Assign tai and presynch method, update time AI method status, TAI can
        be performed with or without presynch.
        Args:
            sim_day: the simulation day
        """
        if self.days_in_milk == AnimalBase.config['tai_program_start_day']:
            if self.presynch_method:
                self.presynch_program_start_day = self.days_born
            else:
                self.tai_program_start_day_c = self.days_born

        if self.presynch_method:
            if self.presynch_method == 'PreSynch':
                self.presynch_update(sim_day)
            elif self.presynch_method == 'Double OvSynch':
                self.doubleovsynch_update(sim_day)
            elif self.presynch_method == 'G6G':
                self.g6g_update(sim_day)

        if self.tai_method_c == 'OvSynch 56':
            self.OvSynch56_update(sim_day)
        elif self.tai_method_c == 'OvSynch 48':
            self.OvSynch48_update(sim_day)
        elif self.tai_method_c == 'CoSynch 72':
            self.CoSynch72_update(sim_day)
        elif self.tai_method_c == '5d CoSynch':
            self.d5CoSynch_update(sim_day)

    # ED-TAI methods
    def ed_tai_update(self, sim_day):
        """
        Update ED-TAI method, perform estrus detection before the TAI program
        Args:
            sim_day: the simulation day
        """
        # if on estrus day, start detecting estrus
        # ED before scheduled TAI start day
        if self.days_in_milk < AnimalBase.config['tai_program_start_day']:
            self.ed_update(sim_day)

        # on TAI start day, if AI not scheduled for ED method, start TAI update
        elif self.days_in_milk == AnimalBase.config['tai_program_start_day'] and self.ai_day < self.days_born:
            self.estrus_day = 0
            self.tai_program_start_day_c = self.days_born
            self.presynch_method = None
            self.tai_update(sim_day)

        # after TAI start day, if ED program stopped, continue TAI update
        elif self.days_in_milk > AnimalBase.config['tai_program_start_day']:
            self.tai_update(sim_day)

    def resynch_protocol(self, sim_day):
        """
        resynch method is applied for open cows
        conception rate adjustment is made on the day of preg check 
        Args:
            sim_day: the simulation day
        """
        # ED program after AI, TAI atart after PD
        if self.resynch_method == 'TAIafterPD':         
            # ED before 1st preg check 
            if self.days_born < self.ai_day + AnimalBase.config['preg_check_day_1']:
                self.ed_update(sim_day)
            # on the day of preg check
            elif self.days_born == self.abortion_day:
                self.conception_rate -= \
                    AnimalBase.config['conception_rate_decrease']
                self.estrus_day = 0
                self.tai_program_start_day_c = self.days_born
                self.tai_update(sim_day)
            elif self.days_born > self.abortion_day:
            # after preg check before next preg
                self.tai_update(sim_day)
        
        # only for TAI programs
        elif self.resynch_method == 'TAIbeforePD':
            if self.days_born == self.abortion_day:
                # because tai start day is before this simulation time 
                self.tai_program_start_day_c = self.abortion_day - 7
                self.conception_rate -= \
                AnimalBase.config['conception_rate_decrease']
                # adding past injections 
                self.events.add_event(
                    self.tai_program_start_day_c, sim_day, c.INJECT_GNRH)
                self.GnRH_injections = self.GnRH_injections + 1
                if self.tai_method_c in ['5d CoSynch']:
                    self.events.add_event(
                        self.tai_program_start_day_c + 1, sim_day, c.INJECT_PGF)
                    self.events.add_event(
                        self.tai_program_start_day_c + 2, sim_day, c.INJECT_PGF)
                    self.PGF_injections = self.PGF_injections + 2
            self.tai_update(sim_day)
           
            
        # PGF injection at PD, ED for 7 days after PGF, TAI start afterwards
        elif self.resynch_method == 'PGFatPD':
            # ED before 1st preg check 
            if self.days_born < self.ai_day + AnimalBase.config['preg_check_day_1']:
                self.ed_update(sim_day)
            # inject PGF at the day of preg check 
            elif self.days_born == self.abortion_day:
                self.PGF_injections = self.PGF_injections + 1
                self.events.add_event(self.days_born, sim_day, c.INJECT_PGF)
                self.estrus_day = self.determine_estrus_day(
                    self.abortion_day, c.ESTRUS_AFTER_PGF_NOTE,
                    AnimalBase.config['avg_estrus_cycle_p'],
                    AnimalBase.config['std_estrus_cycle_p'], sim_day)
                self.conception_rate -= \
                    AnimalBase.config['conception_rate_decrease']
            # start TAI program 7 days after preg check
            elif self.days_born < self.abortion_day + 7:
                self.ed_update(sim_day)
            elif self.days_born == self.abortion_day + 7:
                self.estrus_day = 0
                self.tai_program_start_day_c = self.days_born
                self.tai_update(sim_day)
            elif self.days_born > self.abortion_day + 7:
                self.tai_update(sim_day)

            

    # Preg methods
    def open(self, sim_day):
        """
        Assign breeding method for open cows after spot open at preg check
        three methods can be assigned: ED, TAI, ED-TAI
        Args:
            sim_day: the simulation day
        """
        # natural estrus happen after abortion, open_stage == false for only schedule estrus at abortion here
        if self.repro_program == 'ED' and self.open_stage == False:
            self.estrus_day = self.determine_estrus_day(
                    self.abortion_day, c.ESTRUS_AFTER_ABORTION_NOTE,
                    AnimalBase.config['avg_estrus_cycle_cow'],
                    AnimalBase.config['std_estrus_cycle_cow'], sim_day)
        # for TAI and ED-TAI program, resynch protocol starts
        if self.repro_program == 'TAI' or 'ED-TAI':
            self.presynch_method = None


    def adjust_conception(self):
        """
        Adjust conception rate based on the parity of the cow
        """
        if self.calves <= 1:
            return self.conception_rate
        elif self.calves == 2:
            return self.conception_rate - 0.05
        else:
            return self.conception_rate - 0.1

    def preg_update(self, sim_day):
        """
        Update AI for cows reach ai day, inseminate the cow with specific semen
        type. By comparing with conception rate, if conception success,
        gestation length determined
        for preg check 1, confirm the conception
        for preg check 2 and 3, confirm pregnancy,
            there are chances of preg loss in each period of time
            between preg checks
        Args:
            sim_day: the simulation day
        """
        if self.days_in_preg > 0:
            self.days_in_preg += 1

        if self.days_born == self.ai_day:
            self.events.add_event(
                self.days_born, sim_day,
                c.INSEMINATED_W_BASE + AnimalBase.config['semen_type'])
            self.semen_num += 1
            self.AI_times += 1
            conception_rand = random()
            if conception_rand < self.adjust_conception():
                self.days_in_preg = 1
                self.open_stage = False
                if self.calves != 0:
                    last_time_given_birth = \
                        self.events.get_most_recent_date(c.NEW_BIRTH)
                    self.calving_to_preg_time = self.days_born - last_time_given_birth
                self.gestation_length = int(truncnorm.rvs(-2, 2, AnimalBase.config['avg_gestation_len'],\
                        AnimalBase.config['std_gestation_len']))
                # generate calf birth weight 
                if self.breed == 'HO':
                    self.calf_birth_weight = truncnorm.rvs(-2, 2, \
                        AnimalBase.config['birth_weight_avg_ho'], AnimalBase.config['birth_weight_std_ho'])
                elif self.breed == 'JE':
                    self.calf_birth_weight = truncnorm.rvs(-2, 2, \
                        AnimalBase.config['birth_weight_avg_je'], AnimalBase.config['birth_weight_std_je'])

                self.events.add_event(self.days_born, sim_day, c.COW_PREG)
            else:
                self.events.add_event(self.days_born, sim_day, c.COW_NOT_PREG) 
                if self.repro_program in ['ED']:
                    self.estrus_day = self.determine_estrus_day(
                        self.days_born, c.ESTRUS_AFTER_AI_NOTE,
                        AnimalBase.config['avg_estrus_cycle_cow'],
                        AnimalBase.config['std_estrus_cycle_cow'], sim_day)
                elif self.resynch_method in ['TAIafterPD','PGFatPD']: 
                    self.estrus_day = self.determine_estrus_day( 
                        self.days_born, c.ESTRUS_AFTER_AI_NOTE, 
                        AnimalBase.config['avg_estrus_cycle_cow'],
                        AnimalBase.config['std_estrus_cycle_cow'], sim_day)
                    self.open_stage = True
                
        elif self.days_born == self.ai_day + \
            AnimalBase.config['preg_check_day_1']:
            self.preg_diagnoses += 1

            if self.days_in_preg > 0:
                preg_loss_rand = random()
                if preg_loss_rand > AnimalBase.config['preg_loss_rate_1']:
                    self.events.add_event(
                        self.days_born, sim_day, c.PREG_CHECK_1_PREG)
                else:
                    self.days_in_preg = 0
                    self.abortion_day = self.days_born
                    self.open(sim_day)
                    self.open_stage = True
                    self.body_weight -= self.conceptus_weight
                    self.conceptus_weight = 0
                    self.calf_birth_weight = 0
                    self.p_gest_for_calf = 0
                    self.events.add_event(
                        self.days_born, sim_day, c.PREG_LOSS_BEFORE_1)
            else:
                self.abortion_day = self.days_born
                self.open(sim_day)
                self.open_stage = True
                self.events.add_event(
                    self.days_born, sim_day, c.PREG_CHECK_1_NOT_PREG)
        
        # preg check 2
        elif self.days_in_preg > 0 and self.days_born == self.ai_day + \
            AnimalBase.config['preg_check_day_2']:
            self.preg_diagnoses += 1
            preg_loss_rand = random()
            if preg_loss_rand > \
                AnimalBase.config['preg_loss_rate_2']:
                self.events.add_event(
                    self.days_born, sim_day, c.PREG_CHECK_2_PREG)
            else:
                self.days_in_preg = 0
                self.abortion_day = self.days_born
                self.open(sim_day)
                self.open_stage = True
                self.body_weight -= self.conceptus_weight
                self.conceptus_weight = 0
                self.calf_birth_weight = 0
                self.p_gest_for_calf = 0
                self.events.add_event(
                    self.days_born, sim_day, c.PREG_LOSS_BTWN_1_AND_2)
        
        # preg check 3
        elif self.days_in_preg > 0 and self.days_born == self.ai_day + \
            AnimalBase.config['preg_check_day_3']:
            self.preg_diagnoses += 1
            preg_loss_rand = random()
            if preg_loss_rand > AnimalBase.config['preg_loss_rate_3']:
                self.events.add_event(
                    self.days_born, sim_day, c.PREG_CHECK_3_PREG)
            else:
                self.days_in_preg = 0
                self.abortion_day = self.days_born
                self.open(sim_day)
                self.open_stage = True
                self.body_weight -= self.conceptus_weight
                self.conceptus_weight = 0
                self.calf_birth_weight = 0
                self.p_gest_for_calf = 0
                self.events.add_event(
                    self.days_born, sim_day, c.PREG_LOSS_BTWN_2_AND_3)
                    
        if self.open_stage and not self.do_not_breed and self.repro_program in ['ED-TAI','TAI']:
            self.resynch_protocol(sim_day)

        if self.days_in_preg == 0 and self.days_in_milk > \
                AnimalBase.config['do_not_breed_time']:
            # only add to events if it is the first time this occurs
            if not self.do_not_breed:
                self.events.add_event(self.days_born, sim_day, c.DO_NOT_BREED)
                self.do_not_breed = True
            return True

        
    # Cull methods
    def cull_update(self, sim_day):
        """
        Update culling time and cull reasons for cow to leave the herd
        The reasons are reproduction failure, low production, and health issues
        Returns: not culled
        """
        if self.do_not_breed and self.days_in_milk > 80 and \
                self.estimated_daily_milk_produced < \
                AnimalBase.config['cull_milk_production']:
            self.culled = True
            self.events.add_event(self.days_born, sim_day, c.LOW_PROD_CULL)
            self.cull_reason = c.LOW_PROD_CULL
            return True
        if self.days_born == self.future_cull_date:
            self.culled = True
            self.events.add_event(
                self.days_born, sim_day, self.cull_reason)
            return True
        if self.days_born == self.future_death_date:
            self.culled = True
            self.events.add_event(self.days_born, sim_day, c.DEATH_CULL)
            self.cull_reason = c.DEATH_CULL
            return True
        return False

    def death_update(self):
        if self.calves >= 4:
            death_rate = AnimalBase.config['parity_death_prob'][3]
        else:
            death_rate = AnimalBase.config['parity_death_prob'][self.calves-1]
        death_rand = random()
        if (death_rand <= death_rate):
            death_upper_limit = death_lower_limit = death_time_upper_limit = death_time_lower_limit = 0
            death_date_random = random()
            for i in range(len(AnimalBase.config['death_cull_prob']) - 1):
                if (AnimalBase.config['death_cull_prob'][i] <= death_date_random < AnimalBase.config['death_cull_prob'][i+1]):
                    death_lower_limit = AnimalBase.config['death_cull_prob'][i]
                    death_upper_limit = AnimalBase.config['death_cull_prob'][i+1]
                    death_time_lower_limit = AnimalBase.config['death_cull_prob'][i]
                    death_time_upper_limit = AnimalBase.config['death_cull_prob'][i+1]
            n = (death_time_upper_limit-death_time_lower_limit) / (death_upper_limit-death_lower_limit)
            self.future_death_date = round(death_time_lower_limit + n * (death_date_random - death_lower_limit) + self.days_born)

    def health_cull_update(self):
        """
        Update cows culled for health problem, first cull or not in this parity
        will be determined with parity specific culling rate, then a cull reason
        will be determined by random draw. Then a cull day will be identified by
        reverse a distribution for cases of this reason.
        """
        # inv_cull_rate = 0
        if self.calves >= 4:
            inv_cull_rate = AnimalBase.config['parity_cull_prob'][3]
        else:
            inv_cull_rate = \
                AnimalBase.config['parity_cull_prob'][self.calves - 1]
        cull_rand = random()
        if cull_rand <= inv_cull_rate:
            cull_reason_rand = random()
            # cull_reason_cull_prob = []
            if cull_reason_rand <= 0.1633:
                cull_reason_cull_prob = AnimalBase.config['feet_leg_cull_prob']
                self.cull_reason = c.LAMENESS_CULL
            elif cull_reason_rand <= 0.4516:
                cull_reason_cull_prob = AnimalBase.config['injury_cull_prob']
                self.cull_reason = c.INJURY_CULL
            elif cull_reason_rand <= 0.6955:
                cull_reason_cull_prob = AnimalBase.config['mastitis_cull_prob']
                self.cull_reason = c.MASTITIS_CULL
            elif cull_reason_rand <= 0.8346:
                cull_reason_cull_prob = AnimalBase.config['disease_cull_prob']
                self.cull_reason = c.DISEASE_CULL
            elif cull_reason_rand <= 0.8991:
                cull_reason_cull_prob = AnimalBase.config['udder_cull_prob']
                self.cull_reason = c.UDDER_CULL
            else:
                cull_reason_cull_prob = AnimalBase.config['unkown_cull_prob']
                self.cull_reason = c.UNKNOWN_CULL

            cull_time_rand = random()
            cull_reason_upper_limit = cull_reason_lower_limit = cull_time_upper_limit = cull_time_lower_limit = 0
            for i in range(len(cull_reason_cull_prob) - 1):
                if cull_reason_cull_prob[i] <= cull_time_rand < cull_reason_cull_prob[i + 1]:
                    cull_reason_lower_limit = cull_reason_cull_prob[i]
                    cull_reason_upper_limit = cull_reason_cull_prob[i + 1]
                    cull_time_lower_limit = AnimalBase.config['cull_day_count'][i]
                    cull_time_upper_limit = AnimalBase.config['cull_day_count'][i + 1]
            x = (cull_time_upper_limit - cull_time_lower_limit) / (cull_reason_upper_limit - cull_reason_lower_limit)
            self.future_cull_date = round(
                cull_time_lower_limit + x * (cull_time_rand - cull_reason_lower_limit) + self.days_born)
