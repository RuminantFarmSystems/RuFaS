"""
RUFAS: Ruminant Farm Systems Model
File name: heiferIII.py
Author(s): Manfei Li, mli497@wisc.edu
           Militsa Sotirova, militsasotirova@gmail.com
Description: This file updates the heifer form close to calving to calving,
            replacement from other farms are enter the herd in this stage, and
            heifers can be sold in this stage. Body weight gain with user input
            average daily gain, once mature body weight or grow end day reached,
            grow stop.
"""
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.manure.growing_heifer_manure_excretion import \
    manure_calculations
from RUFAS.routines.animal.ration.animal_requirements import calc_rqmts
from RUFAS.routines.animal.life_cycle import animal_events_constants as c


class HeiferIII(HeiferII):
    # TODO: Rank heifers to enter the herd or sold

    def __init__(self, args):
        """
        Description:
            initialize the heifer in this stage from the second stage
        Args:
            args.id: id of the cow
            args.breed: breed of the cow
            args.birth_date: the date of the simulation when the calf was born
            args.daysBorn: age of the animal
            args.repro_program: reproduction program used in heifer,
                three of them: ED, TAI, and synch-ED programs
            args.tai_method_h: timed-AI protocols used for
                reproduction programs, three of them: 5dCG2P,
                5dCGP, and user-defined
            args.synch_ed_method_h: synch ed protocols used for
                reproduction programs, two of them: 2P and CP
            (optional: include the following to assign cow information)
            args.birth_weight: the birth weight of the cow
            args.body_weight: current body weight of the cow
            args.wean_weight: the wean weight of the cow
            args.mature_body_weight: the mature body weight of the cow
            args.events: events of the cow
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
            args.p_gest_for_calf
        """
        super().__init__(args)
        if 'conceptus_weight' in args:
            self.conceptus_weight = args['conceptus_weight']
        if 'calf_birth_weight' in args:
            self.calf_birth_weight = args['calf_birth_weight']
    
    def get_heiferIII_values(self):
        """
        Get current information from the heiferIII
        """
        return self.get_heiferII_values()

    def set_nutrient_rqmts(self, temp):
        """
        Calculates this heiferIII's nutrient requirements.
        """
        req = calc_rqmts(self.body_weight, self.mature_body_weight, self.days_in_preg,
					           animal_type = 'heifer', BCS5 = 3, PrevTemp = temp,
							ADG_heifer = self.daily_growth, Age = self.days_born
					)
        self.NEmaint = req['NEmaint']
        self.NEg = req['NEg']
        self.NEpreg = req['NEpreg']
        self.NEl = req['NEl']
        self.MP_req = req['MP_req']
        self.Ca_req = req['Ca_req']
        self.P_req = req['P_req']
        self.DMIest = req['DMIest']

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

    def update(self, sim_day):
        """
        Controls heifer's grow with average daily gain based on user's input
        until breeding start day here is the place to change growth rate with
        heifer feeding methods later when we have heifer nutrition from the
        ration formulation module next to it could build the function of
        ranking heifers.

        Returns: cow_stage - heifer close to calving, move to cow stage
        """
        self.update_body_weight_history(sim_day)
        cow_stage = False
        self.days_born += 1

        if self.days_in_preg > 0:
            self.days_in_preg += 1

        if self.body_weight < self.mature_body_weight:
            # Heifer can only grow to a maximum weight of mature_body_weight
            self.daily_growth = self.get_bw_change()

            self.body_weight += self.daily_growth

        else:
            self.body_weight = self.mature_body_weight
            self.events.add_event(self.days_born, sim_day, c.MATURE_BODY_WEIGHT_REGULAR)

        if self.days_in_preg == self.gestation_length:
            self.days_born -= 1  # will be incremented again in next stage
            cow_stage = True
        return cow_stage
