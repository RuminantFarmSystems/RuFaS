"""
RUFAS: Ruminant Farm Systems Model
File name: heiferI.py
Author(s): Manfei Li, mli497@wisc.edu
			Militsa Sotirova, militsasotirova@gmail.com
Description: This file updates the heifer form wean to start breeding.
			Body weight gain with user input heifer average daily gain.

"""
###############################################################################

from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.manure.growing_heifer_manure_excretion import \
    manure_calculations
from RUFAS.routines.animal.ration.animal_requirements import calc_rqmts
from RUFAS.routines.animal.life_cycle import animal_constants as const


class HeiferI(Calf):
    def __init__(self, args):
        """
        Description:
            initialize the 1st heifer group from calf information
        Input:
            args.id: id of the animal
            args.breed: breed of the animal
            args.birth_date: the date of the simulation when the calf was born
            args.daysBorn: age of the animal
            (optional: include the following to assign animal information)
            args.birth_weight: the birth weight of the animal
            args.body_weight: current body weight of the animal
            args.wean_weight: the wean weight of the animal
            args.mature_body_weight: the mature body weight of the animal
            args.events: events of the animal
        """
        super().__init__(args)

    def get_heiferI_values(self):
        """
        Get current information from the heiferI
        """
        return self.get_calf_values()

    def set_nutrient_rqmts(self, temp):
        """
        Calculates this heiferI's nutrient requirements.
        """
        req = calc_rqmts(self.body_weight, self.mature_body_weight, None,
                         animal_type='heifer', BCS5=3, PrevTemp=temp,
                         ADG_heifer=self.daily_growth,
                         Age=self.days_born
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

        # absorbed P required by the animal (g) (A.1A-F.E.6)
        p_absorb = p_urine + self.p_maint_feces + self.p_growth

        # requirement of P from the ration (g) (A.1B-D.E.7)
        self.p_req = p_absorb / 0.664

    def get_non_preg_bw_change(self):
        """
        Calculates the body weight change for a heifer that is not pregnant.
        If the days_born of the animal is equal to 400,
        the difference is set to 1 (otherwise results in a division by 0 error).

        Returns: the daily body weight change for a heifer that is not pregnant
        """
        divisor = AnimalBase.config['target_heifer_preg_day'] - AnimalBase.config['wean_day']
        if divisor == 0:
            divisor = 1
        return (0.55 * 0.96 * self.mature_body_weight -
                self.wean_weight) / divisor

    def update(self, sim_day: int) -> bool:
        """
        Controls heifer's grow with average daily gain based on non-preg ADG based on NRC.
        Here is the place to change growth rate with heifer feeding methods later
        when we have heifer nutrition from the ration furmulation module.
        Once reach the breeding start day,
        this heifer would be move to next stage, the heiferII stage

        Returns: the second stage of heifer -- breeding stage starts
        """
        self.update_body_weight_history(sim_day)
        second_stage = False

        self.daily_growth = self.get_non_preg_bw_change()

        self.body_weight += self.daily_growth

        self.days_born += 1
        if self.days_born == AnimalBase.config['breeding_start_day_h']:
            second_stage = True
            self.events.add_event(self.days_born, sim_day, const.BREEDING_START)
            self.days_born -= 1  # will increment in next stage again

        return second_stage
