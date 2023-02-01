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

import numpy as np
from scipy.stats import truncnorm
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.ration.growing_heifer_ration import calculate_rqmts
from RUFAS.routines.animal.manure.growing_heifer_manure_excretion import \
    manure_calculations
from random import random
import math
from RUFAS.routines.animal.life_cycle import animal_events_constants as const


class HeiferII(HeiferI):
    def __init__(self, args):
        """
        Description:
            initialize the heifer in this stage from the first stage and
             initialize or assigns the repro program parameters
        Input:
            args.id: id of the animal
            args.breed: breed of the animal
            args.birth_date: the date of the simulation when the calf was born
            args.daysBorn: age of the animal
            args.repro_program: reproduction program used in heifer,
                three of them: ED, TAI, and synch-ED programs
            args.tai_method_h: timed-AI protocols used for
                reproduction programs, three of them: 5dCG2P,
                5dCGP, and user-defined
            args.synch_ed_method_h: synch ed protocols used for
                reproduction programs, two of them: 2P and CP
            (optional: include the following to assign animal information)
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
        """
        super().__init__(args)

        if 'estrus_count' in args:
            self.assign_heiferII_values(args)
        else:
            self.init_values(args)

        self.target_adg_heifer_preg = 0
        self.breeding_to_preg_time = 0
        self.conceptus_weight = 0

        self.ED_days = 0
        self.GnRH_injections = 0
        self.PGF_injections = 0
        self.CIDR_count = 0
        self.semen_num = 0
        self.AI_times = 0
        self.preg_diagnoses = 0

    def get_bw_change(self):
        """
        Calculates the body weight change for a heifer, depending on if she
        is pregnant or not.
        If the gestation_length of the animal is equal to its days_in_preg,
        the difference is set to 1 (otherwise results in a division by 0 error).

        Returns: the daily body weight change for a heifer
        """
        if self.days_in_preg > 0:
            # BW change due to heifer average daily gain
            divisor = (self.gestation_length - self.days_in_preg)
            if divisor == 0:
                divisor = 1
            target_ADG_heifer_preg = (0.82 * 0.96 * self.mature_body_weight -
                                            0.96 * self.body_weight) / divisor
            
            # BW change due to conceptus
            if self.days_in_preg == self.gestation_length:
                conceptus_growth = - self.conceptus_weight
                self.conceptus_weight = 0
            elif self.days_in_preg > 50:
                conceptus_total_weight = (0.0148 * self.gestation_length - 2.408) * self.calf_birth_weight
                conceptus_param = conceptus_total_weight ** (1 / 3) / (self.gestation_length - 50)
                conceptus_growth = 3 * conceptus_param ** 3 * (self.days_in_preg - 50) ** 2
                self.conceptus_weight += conceptus_growth
            else:
                conceptus_growth = 0
            
            return target_ADG_heifer_preg + conceptus_growth

        else:
            return self.get_non_preg_bw_change()
        
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

        # general repro
        self.conception_rate = 0
        self.ai_day = 0
        self.abortion_day = 0
        self.days_in_preg = 0
        self.preg = False
        self.gestation_length = 0

        # new calf related
        self.p_gest_for_calf = 0
        self.calf_birth_weight = 0

    def assign_heiferII_values(self, args):
        """
            Assign the repro program with given vales
        """
        self.repro_program = AnimalBase.config['heifer_repro_method']

        # Estrus variables
        self.estrus_count = args['estrus_count']
        self.estrus_day = args['estrus_day']

        # TAI variables
        self.tai_method_h = AnimalBase.config['heifer_TAI_protocol']
        self.tai_program_start_day_h = args['tai_program_start_day_h']

        # synch_ED variables
        self.synch_ed_method_h = AnimalBase.config['heifer_synchED_protocol']
        self.synch_ed_program_start_day_h = args['synch_ed_program_start_day_h']
        self.synch_ed_estrus_day = args['synch_ed_estrus_day']
        self.synch_ed_stop_day = args['synch_ed_stop_day']

        # general repro
        self.conception_rate = args['conception_rate']
        self.ai_day = args['ai_day']
        self.abortion_day = args['abortion_day']
        self.days_in_preg = args['days_in_preg']
        self.gestation_length = args['gestation_length']

        # new calf related
        self.p_gest_for_calf = args['p_gest_for_calf']
        self.calf_birth_weight = args['calf_birth_weight']

    def get_heiferII_values(self):
        """
        Get current information from the heiferII
        """
        values = {
            'id': self.id,
            'breed': self.breed,
            'birth_date': self.birth_date,
            'days_born': self.days_born,
            'net_merit': self.net_merit,
            'birth_weight': self.birth_weight,
            'body_weight': self.body_weight,
            'wean_weight': self.wean_weight,
            'events': str(self.events),
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
            'p_gest_for_calf': self.p_gest_for_calf,
            'calf_birth_weight': self.calf_birth_weight
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
            manure_calculations(self.ration_formulation, feed,
                                self.body_weight, p_feces_excrt, p_urine)

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

        self.days_born += 1

        if self.body_weight < self.mature_body_weight:
            # Heifer can only grow to a maximum weight of mature_body_weight
            self.daily_growth = self.get_bw_change()

            self.body_weight += self.daily_growth

            self.heifer_feed_cost += self.body_weight * 0.0068

        else:
            self.body_weight = self.mature_body_weight
            self.events.add_event(self.days_born, sim_day, const.MATURE_BODY_WEIGHT_REGULAR)

        self.ED_days = 0
        self.GnRH_injections = 0
        self.PGF_injections = 0
        self.CIDR_count = 0
        # breeding method assign to heifer
        if self.days_born >= AnimalBase.config['breeding_start_day_h']:
            if self.repro_program == 'ED':
                self.ed_update(sim_day)
            elif self.repro_program == 'TAI':
                self.tai_update(sim_day)
            elif self.repro_program == 'synch-ED':
                self.synch_ed_update(sim_day)
            self.preg_update(sim_day)
            # prior to calving, heifer move to replacement group (heiferIII)
            if self.days_in_preg == self.gestation_length - \
                AnimalBase.config['prefresh_day']:
                self.days_born -= 1  # will be increment again in next stage
                third_stage = True
                self.events.add_event(self.days_born, sim_day, const.HEIFERII_TO_III)

            self.heifer_hormone_cost += 1.83 * self.GnRH_injections + 2.29 * self.PGF_injections + 12.53 * self.CIDR_count
            self.heifer_ed_cost += self.ED_days * 0.03
            self.heifer_ai_semen_cost += 10 * self.AI_times + 15 * self.semen_num 
            self.heifer_pc_cost += 4.37 * self.preg_diagnoses
        
        # cull heifer for reproduction reason
        if self.days_in_preg == 0 and \
            self.days_born > AnimalBase.config['heifer_repro_cull_time']: 
            self.events.add_event(
                self.days_born, sim_day, const.HEIFER_REPRO_CULL)
            cull_stage = True

        return cull_stage, third_stage

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
        self.events.add_event(self.days_born, sim_day, estrus_note)
        return estrus_day

    def ed_update(self, sim_day):
        """
        Estrus occur at estrus day,
        estrus detected with detection rate,
        AI preformed with insemination rate,
        conception successed with conception rate
        """
        if self.days_born == AnimalBase.config['breeding_start_day_h']:
            self.estrus_day = self.determine_estrus_day(
                self.days_born, const.FIRST_ESTRUS_NOTE, 
                AnimalBase.config['avg_estrus_cycle_heifer'],
                AnimalBase.config['std_estrus_cycle_heifer'], sim_day)

        # if on estrus day, start detecting estrus
        if self.days_born == self.estrus_day:
            self.estrus_count += 1
            self.events.add_event(self.days_born, sim_day, const.ESTRUS_OCCURRED)
            estrus_detection_rand = random()
            if estrus_detection_rand < \
                AnimalBase.config['estrus_detection_rate_h']:
                # Estrus detected
                self.events.add_event(self.days_born, sim_day, const.ESTRUS_DETECTED)
                ed_insemination_rand = random()
                if ed_insemination_rand < AnimalBase.config['estrus_insemination_rate_h']:
                    # serviced
                    self.ai_day = self.estrus_day + 1
                    if self.conception_rate == 0: 
                        self.conception_rate = AnimalBase.config['estrus_conception_rate_h']
                    else:
                        self.conception_rate = AnimalBase.config['estrus_conception_rate_h'] - 0.05
                    # #adjust for sexed semen:
                    # if AnimalBase.config['semen_type'][-5:] == "sexed":
                    #     self.conception_rate -= AnimalBase.config['conception_rate_drop_sexed_semen']
                # Return estrus after estrus not serviced
                else:
                    self.estrus_day = self.determine_estrus_day(self.days_born, const.BASIC_ESTRUS_NOTE, 
                    AnimalBase.config['avg_estrus_cycle_heifer'],
                    AnimalBase.config['std_estrus_cycle_heifer'], sim_day)
            # Return estrus after estrus not detected 
            else:
                self.estrus_day = self.determine_estrus_day(self.days_born, const.BASIC_ESTRUS_NOTE, 
                    AnimalBase.config['avg_estrus_cycle_heifer'],
                    AnimalBase.config['std_estrus_cycle_heifer'], sim_day)

        if self.days_in_preg == 0:
            self.ED_days += 1

    # TAI methods
    # protocol 5dCG2P
    def d5CG2P_update(self, sim_day):
        """
        5dCG2P protocol for tai method
        """
        if self.days_born == self.tai_program_start_day_h:
            self.events.add_event(self.days_born, sim_day, const.INJECT_GNRH)
            self.GnRH_injections = self.GnRH_injections + 1
            self.events.add_event(self.days_born, sim_day, const.INJECT_CIDR)
            self.CIDR_count = self.CIDR_count + 1
        elif self.days_born == self.tai_program_start_day_h + 5:
            self.events.add_event(self.days_born, sim_day, const.INJECT_PGF)
            self.PGF_injections = self.PGF_injections + 1
        elif self.days_born == self.tai_program_start_day_h + 6:
            self.events.add_event(self.days_born, sim_day, const.INJECT_PGF)
            self.PGF_injections = self.PGF_injections + 1
        elif self.days_born == self.tai_program_start_day_h + 8:
            self.ai_day = self.days_born
            self.conception_rate = AnimalBase.config['TAI_conception_rate_h']
            # #adjust for sexed semen:
            # if AnimalBase.config['semen_type'][-5:] == "sexed":
            #     self.conception_rate -= AnimalBase.config['conception_rate_drop_sexed_semen']
            self.events.add_event(self.days_born, sim_day, const.INJECT_GNRH)
            self.GnRH_injections = self.GnRH_injections + 1

    # protocol 5dCGP
    def d5CGP_update(self, sim_day):
        """
        5dCGP protocol for tai method
        """
        if self.days_born == self.tai_program_start_day_h:
            self.events.add_event(self.days_born, sim_day, const.INJECT_GNRH)
            self.GnRH_injections = self.GnRH_injections + 1
        elif self.days_born == self.tai_program_start_day_h + 5:
            self.events.add_event(self.days_born, sim_day, const.INJECT_PGF)
            self.PGF_injections = self.PGF_injections + 1
        elif self.days_born == self.tai_program_start_day_h + 8:
            self.ai_day = self.days_born
            self.conception_rate = AnimalBase.config['TAI_conception_rate_h']
            # #adjust for sexed semen:
            # if AnimalBase.config['semen_type'][-5:] == "sexed":
            #     self.conception_rate -= AnimalBase.config['conception_rate_drop_sexed_semen']
            self.events.add_event(self.days_born, sim_day, const.INJECT_GNRH)
            self.GnRH_injections = self.GnRH_injections + 1

    def tai_update(self, sim_day):
        """
        Tai method update, assign tai method
        """
        if self.days_born == AnimalBase.config['breeding_start_day_h']:
            self.tai_program_start_day_h = AnimalBase.config['breeding_start_day_h']

        if self.tai_method_h == '5dCG2P':
            self.d5CG2P_update(sim_day)
        elif self.tai_method_h == '5dCGP':
            self.d5CGP_update(sim_day)


    # synch-ED methods
    def determine_synch_ed_estrus_day(self, start_date, estrus_note, avg, std, max_val, sim_day):
        """
        Determine synch ed leading estrus start day, with normal distribution

        Args:
            date: start of the synch ed day
            avg: average of estrus occur after synch ed
            std: standard deviation of synch ed
            max_val: max value can go for the normal distribution,
                avoiding negative value
        """
        synch_ed_estrus = truncnorm.rvs(-2, 2, avg, std)
        norm = abs(synch_ed_estrus)
        if norm >= max_val:
            norm = max_val - 1
        synch_ed_estrus_day = int(start_date + norm)
        self.events.add_event(self.days_born, sim_day, estrus_note)
        return synch_ed_estrus_day

    def P2_update(self, sim_day):
        """
        2P protocol for synch ed method
        estrus detection happens when estrus occur
        """
        if self.days_born == self.synch_ed_program_start_day_h:
            self.events.add_event(self.days_born, sim_day, const.INJECT_PGF)
            self.PGF_injections = self.PGF_injections + 1
        if self.days_born == self.synch_ed_program_start_day_h + 14:
                    # second round of injection
            self.events.add_event(self.days_born, sim_day,const.INJECT_PGF)
            self.PGF_injections = self.PGF_injections + 1
            self.synch_ed_estrus_day = self.determine_synch_ed_estrus_day(self.days_born, const.SYNCH_ESTRUS, 4, 1.5, 7, sim_day)

        if self.days_born > self.synch_ed_program_start_day_h + 14 and self.days_born < self.synch_ed_estrus_day:
            self.ED_days += 1

        if self.days_born == self.synch_ed_estrus_day:
            self.events.add_event(self.days_born, sim_day, const.ESTRUS_OCCURRED)
            estrus_detection_rand = random()
            if estrus_detection_rand < \
                AnimalBase.config['estrus_detection_rate_h_synch']:
                self.events.add_event(self.days_born, sim_day, const.ESTRUS_DETECTED)
                ed_insemination_rand = random()
                if ed_insemination_rand < AnimalBase.config['estrus_insemination_rate']:
                    self.ai_day = self.synch_ed_estrus_day + 1
                    self.conception_rate = \
                        AnimalBase.config['estrus_conception_rate_h']
                    # #adjust for sexed semen:
                    # if AnimalBase.config['semen_type'][-5:] == "sexed":
                    #     self.conception_rate -= AnimalBase.config['conception_rate_drop_sexed_semen']
            else:
                # finish up with TAI
                self.synch_ed_stop_day = self.synch_ed_program_start_day_h + 21
                self.tai_program_start_day_h = self.synch_ed_stop_day
                self.tai_update(sim_day)
        elif self.synch_ed_stop_day != 0 and self.days_born >= self.synch_ed_stop_day:
                    # finish up with TAI
            self.tai_update(sim_day)

    def CP_update(self, sim_day):
        """
        CP protocol for synch ed method
        estrus detection happens when estrus occur
        """
        if self.days_born == self.synch_ed_program_start_day_h:
            self.events.add_event(self.days_born, sim_day, const.INJECT_CIDR)
            self.CIDR_count = self.CIDR_count + 1
        elif self.days_born == self.synch_ed_program_start_day_h + 7:
            self.events.add_event(self.days_born, sim_day, const.INJECT_PGF)
            self.PGF_injections = self.PGF_injections + 1
            self.synch_ed_estrus_day = self.determine_synch_ed_estrus_day(self.days_born, const.SYNCH_ESTRUS, 5, 1.5, 7, sim_day)

        if self.days_born > self.synch_ed_program_start_day_h + 7 and self.days_born < self.synch_ed_estrus_day:
            self.ED_days += 1

        if self.days_born == self.synch_ed_estrus_day:
            self.events.add_event(self.days_born, sim_day, const.ESTRUS_OCCURRED)
            estrus_detection_rand = random()
            if estrus_detection_rand < \
                AnimalBase.config['estrus_detection_rate_h_synch']:
                self.events.add_event(self.days_born, sim_day, const.ESTRUS_DETECTED)
                ed_insemination_rand = random()
                if ed_insemination_rand < AnimalBase.config['ed_insemination_rate']:
                    self.ai_day = self.synch_ed_estrus_day + 1
                    self.conception_rate = \
                        AnimalBase.config['estrus_conception_rate_h']
                    # #adjust for sexed semen:
                    # if AnimalBase.config['semen_type'][-5:] == "sexed":
                    #     self.conception_rate -= AnimalBase.config['conception_rate_drop_sexed_semen']
                else:
                    self.synch_ed_stop_day = self.synch_ed_program_start_day_h + 14
                    self.synch_ed_program_start_day_h = self.synch_ed_stop_day
            else:
                self.synch_ed_stop_day = self.synch_ed_program_start_day_h + 14
                self.synch_ed_program_start_day_h = self.synch_ed_stop_day

    def synch_ed_update(self, sim_day):
        """
        Synch ed method update, assign with protocols: 2P or CP
        """
        if self.days_born == AnimalBase.config['breeding_start_day_h']:
            self.synch_ed_program_start_day_h = AnimalBase.config['breeding_start_day_h']

        if self.synch_ed_method_h == '2P':
            self.P2_update(sim_day)
        elif self.synch_ed_method_h == 'CP':
            self.CP_update(sim_day)

    # Preg stage
    # after preg loss between 1 and 3 preg checks, return to corresponding protocols
    def open(self, sim_day):
        """
        Assign breeding method for open heifers after spot open at preg check
        three methods can be assigned: ED, TAI, synch-ED
        """
        self.ai_day = 0
        # if self.repro_program == 'ED':
        if self.estrus_day < self.days_born:
            self.estrus_day = self.determine_estrus_day(self.abortion_day, const.ESTRUS_AFTER_ABORTION_NOTE, 
            AnimalBase.config['avg_estrus_cycle_heifer'],
            AnimalBase.config['std_estrus_cycle_heifer'], sim_day)
        # elif self.repro_program == 'TAI':
        #     self.estrus_day = self.determine_estrus_day(self.abortion_day, const.ESTRUS_AFTER_ABORTION_NOTE, 
        #         AnimalBase.config['avg_estrus_cycle_heifer'],
        #         AnimalBase.config['std_estrus_cycle_heifer'], sim_day)
        #     self.repro_program = 'ED'
        # elif self.repro_program == 'synch-ED':
        #     self.estrus_day = self.determine_estrus_day(self.abortion_day, const.ESTRUS_AFTER_ABORTION_NOTE, 
        #         AnimalBase.config['avg_estrus_cycle_heifer'],
        #         AnimalBase.config['std_estrus_cycle_heifer'], sim_day)
        self.repro_program = 'ED'


    def adjust_conception(self):
        """
        Adjust conception rate based on semen type
        """
        adjusted_conception_rate = self.conception_rate
        #adjust for sexed semen:
        if AnimalBase.config['semen_type'][-5:] == "sexed":
            adjusted_conception_rate -= AnimalBase.config['conception_rate_drop_sexed_semen']
        return adjusted_conception_rate
    
    # artificial inseminated 
    def preg_update(self, sim_day):
        """
        update AI for heifers reach ai day, inseminate the heifer with specific
            semen type
        by comparing with conception rate, if conception success, gestation
            length determined
        for preg check 1, confirm the conception
        for preg check 2 and 3, confirm pregnancy, there are chances of preg
            loss in each period of time between preg checks
        """
        if self.days_in_preg > 0:
            self.days_in_preg += 1

        self.semen_num = 0
        self.AI_times = 0
        self.preg_diagnoses = 0

        # AI
        if self.days_born == self.ai_day:
            self.events.add_event(
                self.days_born, sim_day, const.INSEMINATED_W_BASE + AnimalBase.config['semen_type'])
            self.semen_num += 1
            self.AI_times += 1
            # conception
            conception_rand = random()
            if conception_rand < self.adjust_conception():
                self.days_in_preg = 1
                self.abortion_day = 0
                self.breeding_to_preg_time = self.days_born - AnimalBase.config['breeding_start_day_h']
                self.gestation_length = int(truncnorm.rvs(-2, 2, AnimalBase.config['avg_gestation_len'],\
                        AnimalBase.config['std_gestation_len']))
                # generate calf birth weight 
                if self.breed == 'HO':
                    self.calf_birth_weight = truncnorm.rvs(-2, 2, \
                        AnimalBase.config['birth_weight_avg_ho'], AnimalBase.config['birth_weight_std_ho'])
                elif self.breed == 'JE':
                    self.calf_birth_weight = truncnorm.rvs(-2, 2, \
                        AnimalBase.config['birth_weight_avg_je'], AnimalBase.config['birth_weight_std_je'])
                self.events.add_event(self.days_born, sim_day, const.HEIFER_PREG)
            else:
                self.events.add_event(self.days_born, sim_day, const.HEIFER_NOT_PREG)
                # estrus detection after ai before preg check
                self.repro_program = 'ED'
                self.estrus_day = self.determine_estrus_day(
                    self.estrus_day, const.ESTRUS_AFTER_AI_NOTE, 
                AnimalBase.config['avg_estrus_cycle_heifer'],
                AnimalBase.config['std_estrus_cycle_heifer'], sim_day)

        # preg check 1 
        if self.days_born == self.ai_day + \
            AnimalBase.config['preg_check_day_1']:
            self.preg_diagnoses += 1

            if self.days_in_preg > 0:
                preg_loss_rand = random()
                if preg_loss_rand > AnimalBase.config['preg_loss_rate_1']:
                    self.events.add_event(
                        self.days_born, sim_day, const.PREG_CHECK_1_PREG)
                else:
                    self.days_in_preg = 0
                    self.abortion_day = self.days_born
                    self.open(sim_day)
                    self.body_weight -= self.conceptus_weight
                    self.conceptus_weight = 0
                    self.calf_birth_weight = 0
                    self.p_gest_for_calf = 0
                    self.events.add_event(
                        self.days_born, sim_day, const.PREG_LOSS_BEFORE_1)
            else:
                self.abortion_day = self.days_born
                self.open(sim_day)
                self.events.add_event(
                    self.days_born, sim_day, const.PREG_CHECK_1_NOT_PREG)
        
        # preg check 2
        elif self.days_born == self.ai_day + \
            AnimalBase.config['preg_check_day_2']:
            self.preg_diagnoses += 1
            preg_loss_rand = random()
            if preg_loss_rand > \
                AnimalBase.config['preg_loss_rate_2']:
                self.events.add_event(
                    self.days_born, sim_day, const.PREG_CHECK_2_PREG)
            else:
                self.days_in_preg = 0
                self.abortion_day = self.days_born
                self.open(sim_day)
                self.body_weight -= self.conceptus_weight
                self.conceptus_weight = 0
                self.calf_birth_weight = 0
                self.p_gest_for_calf = 0
                self.events.add_event(
                    self.days_born, sim_day, const.PREG_LOSS_BTWN_1_AND_2)
        
        # preg check 3
        elif self.days_born == self.ai_day + \
            AnimalBase.config['preg_check_day_3']:
            self.preg_diagnoses += 1
            preg_loss_rand = random()
            if preg_loss_rand > AnimalBase.config['preg_loss_rate_3']:
                self.events.add_event(
                    self.days_born, sim_day, const.PREG_CHECK_3_PREG)
            else:
                self.days_in_preg = 0
                self.abortion_day = self.days_born
                self.open(sim_day)
                self.body_weight -= self.conceptus_weight
                self.conceptus_weight = 0
                self.calf_birth_weight = 0
                self.p_gest_for_calf = 0
                self.events.add_event(
                    self.days_born, sim_day, const.PREG_LOSS_BTWN_2_AND_3)
        

