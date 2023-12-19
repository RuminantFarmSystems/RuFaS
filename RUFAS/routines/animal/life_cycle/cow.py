from __future__ import annotations

import collections
import math
from random import random
from typing import Dict, Any

import numpy as np
from scipy.stats import truncnorm

from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.routines.animal.life_cycle import animal_constants as const
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.life_cycle.repro_protocol_enums import CowReproProtocolEnum
from RUFAS.routines.animal.manure.dry_cow_manure_excretion import \
    manure_calculations as dry_manure_calculations
from RUFAS.routines.animal.manure.lactating_cow_manure_excretion import \
    manure_calculations as lactating_manure_calculations
from RUFAS.routines.animal.ration.animal_requirements import AnimalRequirements

om = OutputManager()


class MilkProductionHistory:
    def __init__(self, sim_day, days_in_milk, milk_prod, days_born):
        self.simulation_day = sim_day
        self.days_in_milk = days_in_milk
        self.milk_production = milk_prod
        self.days_born = days_born


class Cow(HeiferIII):
    stats = collections.defaultdict(int)

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
            args.gestation_length: the projected gestation
            args.p_gest_for_calf
            args.days_in_milk: cow's current day in milk
            args.parity: parity of the cow
            args.calving_interval: cow's most recent calving interval
            args.lactation_curve: lactation curve model choice
        """
        super().__init__(args)

        # current hard-coded values necessary for nutrient requirement
        # calculations
        self.BCS = 3.5  # body condition score
        self.CP_milk = AnimalModuleConstants.MILK_CRUDE_PROTEIN
        self.lactose_milk = AnimalModuleConstants.MILK_LACTOSE
        self.mPrt = AnimalModuleConstants.MILK_TRUE_PROTEIN

        self.DVD = 0  # daily vertical distance, km
        self.DHD = 0  # daily horizontal distance, km
        self.CI = 0  # calving interval, days
        self.CI_history = []
        self.BW_at_calving = 0  # weight of cow when she gives birth
        self.calf_birth_weight = args['calf_birth_weight']  # calf birth weight
        self.daily_growth = 0  # change in body weight, kg
        self.calves = 0
        self.calving_to_preg_time = 0
        self.milking = False
        self.days_in_milk = 0
        self.estimated_daily_milk_produced = 0
        # Milk production as estimated from the lactation curve, kg/day.
        self.milk_fat_kg = 0
        # Milk fat content estimate, kg/day.
        self.milk_protein_kg = 0
        # Milk protein content estimate, kg/day.
        self.milk_production_reduction = 0.0
        self.latest_milk_production_305days = 0.0
        self.single_acc_milk_prod = 0
        self.future_cull_date = 0
        self.future_death_date = 0
        self.cull_reason = None
        self.repro_program = args['repro_program']
        self.first_ai = False
        self.fat_percent = 0

        # TAI params
        self.presynch_method = args['presynch_method']
        self.tai_method_c = args['tai_method_c']
        self.presynch_program_start_day = 0
        self.tai_program_start_day_c = 0
        self.resynch_method = args['resynch_method']

        self._is_in_presynch_period = False
        self._is_in_tai_period = False
        self._num_conception_rate_decreases = 0

        self.wood_l = 0
        self.wood_m = 0
        self.wood_n = 0

        self.lactation_curve = 'wood'
        self.milk_production_history = []
        self.breed_index = 0
        self.parity_index = 0
        self.set_breed_index()

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
            self.set_parity_index()
            self.set_lactation_curve_params()

    def get_cow_values(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "breed": self.breed,
            "birth_date": self.birth_date,
            "days_born": self.days_born,
            "birth_weight": self.birth_weight,
            "body_weight": self.body_weight,
            "wean_weight": self.wean_weight,
            "events": str(self.events),
            "repro_program": self.repro_program,
            "tai_method_h": self.tai_method_h,
            "synch_ed_method_h": self.synch_ed_method_h,
            "mature_body_weight": self.mature_body_weight,
            "estrus_count": self.estrus_count,
            "estrus_day": self.estrus_day,
            "tai_program_start_day_h": self.tai_program_start_day_h,
            "synch_ed_program_start_day_h": self.synch_ed_program_start_day_h,
            "synch_ed_estrus_day": self.synch_ed_estrus_day,
            "synch_ed_stop_day": self.synch_ed_stop_day,
            "conception_rate": self.conception_rate,
            "ai_day": self.ai_day,
            "abortion_day": self.abortion_day,
            "days_in_preg": self.days_in_preg,
            "gestation_length": self.gestation_length,
            "p_gest_for_calf": self.p_gest_for_calf,
            "calf_birth_weight": self.calf_birth_weight,
            "presynch_method": self.presynch_method,
            "tai_method_c": self.tai_method_c,
            "resynch_method": self.resynch_method,
            "days_in_milk": self.days_in_milk,
            "parity": self.calves,
            "calving_interval": self.CI
        }

    def get_replacement_values(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "breed": self.breed,
            "birth_date": self.birth_date,
            "days_born": self.days_born,
            "birth_weight": self.birth_weight,
            "body_weight": self.body_weight,
            "wean_weight": self.wean_weight,
            "events": str(self.events),
            "repro_program": self.repro_program,
            "tai_method_h": self.tai_method_h,
            "synch_ed_method_h": self.synch_ed_method_h,
            "mature_body_weight": self.mature_body_weight,
            "estrus_count": self.estrus_count,
            "estrus_day": self.estrus_day,
            "tai_program_start_day_h": self.tai_program_start_day_h,
            "synch_ed_program_start_day_h": self.synch_ed_program_start_day_h,
            "synch_ed_estrus_day": self.synch_ed_estrus_day,
            "synch_ed_stop_day": self.synch_ed_stop_day,
            "conception_rate": self.conception_rate,
            "ai_day": self.ai_day,
            "abortion_day": self.abortion_day,
            "days_in_preg": self.days_in_preg,
            "gestation_length": self.gestation_length,
            "p_gest_for_calf": self.p_gest_for_calf,
            "calf_birth_weight": self.calf_birth_weight,
            "presynch_method": self.presynch_method,
            "tai_method_c": self.tai_method_c,
            "resynch_method": self.resynch_method
        }

    @property
    def is_lactating(self):
        """
        Check if the cow is lactating.

        Returns
        -------
        bool
            True if the cow is lactating, False otherwise.

        """

        return self.milking

    @property
    def is_dry(self) -> bool:
        """
        Check if the cow is in the dry state.

        Returns
        -------
        bool
            True if the cow is in the dry state, False otherwise.

        """

        return not self.is_lactating

    def set_breed_index(self):
        """Sets the cow's breed index for use in the lactation curve parameter calculation"""
        if self.breed == 'HO':
            self.breed_index = 0
        if self.breed == 'JE':
            self.breed_index = 1

    def set_parity_index(self):
        """Sets the cow's parity index for use in the lactation curve parameter calculation"""
        self.parity_index = 2 if self.calves - 1 > 2 else self.calves - 1

    def set_lactation_curve_params(self):
        """
        Sets cow's lactation curve parameters based on cow's lactation curve attribute.
        Currently only set up for wood model.
        """
        if self.lactation_curve == 'wood':
            self.wood_l = self.determine_param_value(
                AnimalBase.config['wood_l'][self.breed_index][self.parity_index],
                AnimalBase.config['wood_l_std'][self.breed_index][self.parity_index])
            self.wood_m = self.determine_param_value(
                AnimalBase.config['wood_m'][self.breed_index][self.parity_index],
                AnimalBase.config['wood_m_std'][self.breed_index][self.parity_index])
            self.wood_n = self.determine_param_value(
                AnimalBase.config['wood_n'][self.breed_index][self.parity_index],
                AnimalBase.config['wood_n_std'][self.breed_index][self.parity_index])

    def calculate_daily_milk_produced(self) -> float:
        """Returns a float calculation of the milk produced based on a cow's lactation curve parameters"""
        if self.lactation_curve == 'wood':
            return self.wood_l * math.pow(self.days_in_milk, self.wood_m) * math.exp((0 - self.wood_n) *
                                                                                     self.days_in_milk)
        if self.lactation_curve == 'milkbot':
            return AnimalBase.config['a'] * (1 - math.exp((AnimalBase.config['c'] - self.days_in_milk) /
                                                          AnimalBase.config['b']) / 2) * \
                math.exp((0 - AnimalBase.config['d']) * self.days_in_milk)
        return 0

    def update_milk_production_history(self, sim_day):
        """
        Updates the animal's milk production history by appending a
        MilkProductionHistory object to the list.

        If milk production history has already been updated for the day,
        the most recent entry is deleted before appending the latest values.
        Once a cow reaches 305 days in milk, latest_milk_production_305days is updated.

        Parameter
        ---------
            sim_day: simulation day
        """
        if len(self.milk_production_history) > 0 and self.milk_production_history[-1].simulation_day == sim_day:
            del self.milk_production_history[-1]

        self.milk_production_history.append(
            MilkProductionHistory(sim_day, self.days_in_milk, self.estimated_daily_milk_produced, self.days_born)
        )

        if self.days_in_milk == 305 and len(self.milk_production_history) > 305:
            milk_history = [day.milk_production for day in self.milk_production_history[-305:]]
            self.latest_milk_production_305days = np.sum(milk_history)

    def calculate_fat_percent(self, days_in_milk: int):
        """
        Calculates fat percent of milk.

        Note that this equation produces 0.0 if days_in_milk is set to one,
        so we've implemented a minimum days_in_milk value of 2.

        Parameters
        ----------
        days_in_milk : int
            Number of days in milk.
        """
        if days_in_milk == 1:
            days_in_milk = 2
        fat_percent = 12.86 * days_in_milk ** (-1.081) * math.exp(
            0.0926 * (math.log(days_in_milk)) ** 2) * (math.log(days_in_milk) ** 1.107)
        return fat_percent

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
            self.events.add_event(self.days_born, sim_day, const.DRY)
            self.days_in_milk = 0
            self.estimated_daily_milk_produced = 0
            self.latest_milk_production_305days = 0.0
            return 0, 0, 0

        if self.milking:
            self.days_in_milk += 1
        else:
            self.days_in_milk = 0

        estimated_daily_milk_produced = self.calculate_daily_milk_produced()

        if estimated_daily_milk_produced > 0.0:
            daily_milk_variation = self.determine_param_value(AnimalModuleConstants.DAILY_MILK_VARIATION_MEAN,
                                                              AnimalModuleConstants.DAILY_MILK_VARIATION_STD_DEV)
            estimated_daily_milk_produced += daily_milk_variation
            estimated_daily_milk_produced += self.milk_production_reduction

        if self.milking:
            self.estimated_daily_milk_produced = max(0.0, estimated_daily_milk_produced)
            self.lactose_milk = AnimalModuleConstants.MILK_LACTOSE
            self.CP_milk = AnimalModuleConstants.MILK_CRUDE_PROTEIN
            self.mPrt = AnimalModuleConstants.MILK_TRUE_PROTEIN
        else:
            self.estimated_daily_milk_produced = 0.0
            self.lactose_milk = 0.0
            self.CP_milk = 0.0
            self.mPrt = 0.0
        self.single_acc_milk_prod += estimated_daily_milk_produced

        # calculate fat percent in milk and fat corrected milk production
        if self.milking:
            self.fat_percent = self.calculate_fat_percent(self.days_in_milk)
            daily_fat_correct_milk_production = \
                0.4 * estimated_daily_milk_produced + \
                0.15 * self.fat_percent * estimated_daily_milk_produced
            self.milk_fat_kg = self.fat_percent * estimated_daily_milk_produced
            self.milk_protein_kg = self.mPrt * self.estimated_daily_milk_produced
        else:
            self.fat_percent = 0.0
            daily_fat_correct_milk_production = 0.0
            self.milk_fat_kg = 0.0
            self.milk_protein_kg = 0.0

        self.daily_growth = self.get_bw_change(calving_interval)

        self.body_weight += self.daily_growth

        # if not self.milking:
        # 	self.daily_growth = self.body_weight - prev_weight

        return self.estimated_daily_milk_produced, self.fat_percent, \
            daily_fat_correct_milk_production

    def calc_manure_excretion(self, feed, methane_model, methane_mitigation_method, methane_mitigation_additive_amount,
                              ME_intake):
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
                p_feces_excrt, p_urine, methane_model, methane_mitigation_method, methane_mitigation_additive_amount,
                self.fat_percent, ME_intake)
        else:
            self.p_excrt, self.manure_excretion = dry_manure_calculations(
                self.ration_formulation, feed, self.body_weight,
                self.estimated_daily_milk_produced, p_feces_excrt, p_urine, methane_model, ME_intake)

    def set_nutrient_rqmts(self, animal_grouping_scenario, nutrient_conc: dict = {}):
        """
        Calculates this Cow's nutrient requirements.
        """
        if nutrient_conc and nutrient_conc['dm'] != 0.0:
            NDF_conc = nutrient_conc['NDF'] / 100
            TDN_conc = nutrient_conc['TDN'] / 100
        else:
            NDF_conc = 0.3
            TDN_conc = 0.7
        req = AnimalRequirements()
        animal_requirements = req.calc_rqmts(body_weight=self.body_weight,
                                             mature_body_weight=self.mature_body_weight,
                                             day_of_pregnancy=self.days_in_preg,
                                             animal_type=animal_grouping_scenario.get_animal_type(self),
                                             parity=self.calves,
                                             calving_interval=self.CI,
                                             milk_true_protein=self.mPrt,
                                             milk_fat=self.fat_percent,
                                             milk_lactose=self.lactose_milk,
                                             milk_production=self.estimated_daily_milk_produced,
                                             days_in_milk=self.days_in_milk,
                                             lactating=self.milking,
                                             NDF_conc=NDF_conc,
                                             TDN_conc=TDN_conc)

        self.NEmaint_requirement = animal_requirements['NEmaint_requirement']
        self.NEg_requirement = animal_requirements['NEg_requirement']
        self.NEpreg_requirement = animal_requirements['NEpreg_requirement']
        self.NEl_requirement = animal_requirements['NEl_requirement']
        self.MP_requirement = animal_requirements['MP_requirement']
        self.Ca_requirement = animal_requirements['Ca_requirement']
        self.P_requirement = animal_requirements['P_requirement']
        self.DMIest_requirement = animal_requirements['DMIest_requirement']
        self.DNED_requirement = ((animal_requirements['NEmaint_requirement'] + animal_requirements['NEl_requirement'])
                                 / self.DMIest_requirement)
        self.DMDP_requirement = (animal_requirements['MP_requirement']) / self.DMIest_requirement

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
            exp_1 = (0.05527 - 0.000075 * self.days_in_preg) * \
                    self.days_in_preg
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
        p_absorb = p_urine + self.p_maint_feces + self.p_growth + self.p_gest + p_milk

        # requirement of P from the ration (g) (A.1EF.E.7)
        if self.milking:
            self.p_req = p_absorb / \
                         (1.86696 - 5.01238 * self.p_conc_ration + 5.12286 *
                          self.p_conc_ration ** 2)
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
        self.DVD = 2 * vertical_dist_to_parlor * AnimalBase.config['cow_times_milked_per_day']
        self.DHD = 2 * horizontal_dist_to_parlor * AnimalBase.config['cow_times_milked_per_day']

    def get_bw_change(self, CI):  # noqa
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
            conceptus_total_weight = (
                                             0.0148 * self.gestation_length - 2.408) * self.calf_birth_weight
            conceptus_param = conceptus_total_weight ** (
                    1 / 3) / (self.gestation_length - 50)
            conceptus_growth = 3 * conceptus_param ** 3 * (self.days_in_preg - 50) ** 2
            self.conceptus_weight += conceptus_growth
        else:
            conceptus_growth = 0

        # growth for 1st and 2nd lactation cows
        if self.calves == 1:
            if self.days_in_preg < 1:  # before pregnancy
                target_adg_cow = \
                    (0.92 - 0.82) * 0.96 * self.mature_body_weight / CI
            else:  # after pregnancy
                target_adg_cow = \
                    (0.92 * self.mature_body_weight - self.body_weight) / \
                    (self.gestation_length - self.days_in_preg + 1)
        elif self.calves == 2:
            if self.days_in_preg < 1:  # before pregnancy
                target_adg_cow = \
                    (1 - 0.92) * 0.96 * self.mature_body_weight / CI
            else:  # after pregnancy
                target_adg_cow = \
                    (self.mature_body_weight - self.body_weight) / \
                    (self.gestation_length - self.days_in_preg + 1)
        else:  # parity > 2
            target_adg_cow = 0

        if not self.days_in_milk == 0:
            if self.calves == 1:
                bodyweight_tissue = \
                    -20 / 65 * math.exp(1 - self.days_in_milk / 65) + \
                    20 / (65 ** 2) * self.days_in_milk * \
                    math.exp(1 - self.days_in_milk / 65)
                if self.days_in_preg == AnimalBase.config['days_in_preg_when_dry'] - 1:
                    self.tissue_changed = 20 * self.days_in_milk / 65 * math.exp(1 - self.days_in_milk / 65)
            else:  # parity > 1
                bodyweight_tissue = \
                    -40 / 70 * math.exp(1 - self.days_in_milk / 70) + \
                    40 / (70 ** 2) * self.days_in_milk * \
                    math.exp(1 - self.days_in_milk / 70)
                if self.days_in_preg == AnimalBase.config['days_in_preg_when_dry'] - 1:
                    self.tissue_changed = 40 * self.days_in_milk / 70 * math.exp(1 - self.days_in_milk / 70)
        else:  # dry period
            bodyweight_tissue = self.tissue_changed / (self.gestation_length -
                                                       AnimalBase.config['days_in_preg_when_dry'])

        return target_adg_cow + conceptus_growth + bodyweight_tissue

    def update(self, sim_day, calving_interval):  # noqa
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
                    self.events.get_most_recent_date(const.NEW_BIRTH)
                self.CI = self.days_born - last_time_given_birth
                self.CI_history.append(self.CI)
            self.BW_at_calving = self.body_weight
            self.events.add_event(self.days_born, sim_day, const.NEW_BIRTH)
            self.health_cull_update()
            self.death_update()
            new_born = True
            self.set_parity_index()
            self.set_lactation_curve_params()

            # restarting estrus
            if self.repro_program in ['ED', 'ED-TAI']:
                self.restart_estrus(sim_day)

        # if self.milking:
        estimated_daily_milk_produced, fat_percent, \
            daily_fat_correct_milk_production = self.milking_update(sim_day, calving_interval)

        self.update_body_weight_history(sim_day)
        self.update_milk_production_history(sim_day)

        if self.is_breedable():
            if self.repro_program not in [CowReproProtocolEnum.ED.value,
                                          CowReproProtocolEnum.TAI.value,
                                          CowReproProtocolEnum.ED_TAI.value]:
                raise ValueError(f'Invalid cow repro program: {self.repro_program}')

            if self.repro_program == CowReproProtocolEnum.ED.value:
                self.execute_ed_protocol(sim_day)

            if self.repro_program == CowReproProtocolEnum.ED_TAI.value:
                self.ed_tai_update(sim_day)
                # self.execute_ed_tai_protocol(sim_day)

            if self.repro_program == CowReproProtocolEnum.TAI.value or self._is_in_tai_period:
                self.execute_tai_protocol(sim_day)

            if self.days_born == self.ai_day:
                self.conception_rate = self.adjust_conception()
                self._perform_ai(sim_day)

            self.preg_update(sim_day)

        cull_stage = self.cull_update(sim_day)

        return estimated_daily_milk_produced, fat_percent, daily_fat_correct_milk_production, cull_stage, new_born

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
        estrus_cycle = truncnorm.rvs(-const.STDI, const.STDI, avg, std)
        estrus_day = int(start_date + abs(estrus_cycle))
        self.events.add_event(self.days_born, sim_day, estrus_note)
        return estrus_day

    def restart_estrus(self, sim_day):
        """
        Return estrus after calving.
        """
        self.estrus_day = self.determine_estrus_day(
            self.days_born, const.ESTRUS_AFTER_CALVING_NOTE,
            AnimalBase.config['avg_estrus_cycle_return'],
            AnimalBase.config['std_estrus_cycle_return'], sim_day)

    def later_estrus(self, sim_day):
        """
        Return estrus after first estrus.
        """
        self.estrus_day = self.determine_estrus_day(
            self.estrus_day, const.ESTRUS_BEFORE_VWP_NOTE,
            AnimalBase.config['avg_estrus_cycle_cow'],
            AnimalBase.config['std_estrus_cycle_cow'], sim_day)

    def return_estrus(self, sim_day):
        """
        Return estrus after estrus not detected or not serveded.
        """
        self.estrus_day = self.determine_estrus_day(
            self.estrus_day, const.BASIC_ESTRUS_NOTE,
            AnimalBase.config['avg_estrus_cycle_cow'],
            AnimalBase.config['std_estrus_cycle_cow'], sim_day)

    def after_ai_estrus(self, sim_day):
        """
        Return estrus after AI.
        """
        self.estrus_day = self.determine_estrus_day(
            self.estrus_day, const.ESTRUS_AFTER_AI_NOTE,
            AnimalBase.config['avg_estrus_cycle_cow'],
            AnimalBase.config['std_estrus_cycle_cow'], sim_day)

    def after_abortion_estrus(self, sim_day):
        """
        Return estrus after abortion at preg check
        """
        self.estrus_day = self.determine_estrus_day(
            self.abortion_day, const.ESTRUS_AFTER_ABORTION_NOTE,
            AnimalBase.config['avg_estrus_cycle_cow'],
            AnimalBase.config['std_estrus_cycle_cow'], sim_day)

    def is_breedable(self) -> bool:
        """
        Check if the cow is breedable.

        Returns
        -------
        bool
            True if the cow is breedable, False otherwise.

        """

        return not self.do_not_breed

    def execute_ed_protocol(self, sim_day: int) -> None:
        """
        Execute the estrus detection protocol.

        Parameters
        ----------
        sim_day : int
            The current simulation day.

        Returns
        -------
        None
        """

        if self.days_born == self.estrus_day:
            if 1 <= self.days_in_milk <= self._get_voluntary_waiting_period():
                self.log_event(self.estrus_day, sim_day, const.ESTRUS_BEFORE_VWP_NOTE)
                self._simulate_estrus(self.estrus_day, sim_day, const.ESTRUS_DAY_SCHEDULED_NOTE)
            elif self.is_breedable():
                self._handle_ed_estrus_detection(sim_day)

        if self.is_lactating and self.is_breedable():
            self.ED_days += 1

    # TAI methods
    def determine_tai_program_day(self, date):
        """
        Determine the program start time when pass voluntary waiting period.
        Args:
            date: the time tai program start
        """
        self.tai_program_start_day_c = date

    def tai_program_day_after_preg_check(self, sim_day):
        """
        Description:
            resynch start after calving, resynch method assigned
        Args:
            sim_day: simulation day
        """
        if self.resynch_method == 'TAIafterPD':
            self.tai_program_start_day_c = self.abortion_day + 1
            self.conception_rate -= \
                AnimalBase.config['conception_rate_decrease']
        elif self.resynch_method == 'TAIbeforePD':
            self.tai_program_start_day_c = self.abortion_day - 6
            self.conception_rate -= \
                AnimalBase.config['conception_rate_decrease']
            if self.tai_method_c in ['OvSynch 56', 'OvSynch 48', 'CoSynch 72']:
                self.events.add_event(
                    self.tai_program_start_day_c, sim_day, const.INJECT_GNRH)
                self.GnRH_injections = self.GnRH_injections + 1
        elif self.resynch_method == 'PGFatPD':
            self.events.add_event(self.days_born, sim_day, const.INJECT_PGF)
            self.PGF_injections = self.PGF_injections + 1
            self.tai_program_start_day_c = self.abortion_day + 8
            self.conception_rate -= \
                AnimalBase.config['conception_rate_decrease']
        else:
            raise ValueError(f'Invalid resynch method: {self.resynch_method}')

    def OvSynch56_update(self, sim_day):
        """
        OvSynch56 protocol for tai method
        Args:
            sim_day: the simulation day
        """
        if not self.do_not_breed:
            if self.days_born == self.tai_program_start_day_c:
                self.events.add_event(
                    self.days_born, sim_day, const.INJECT_GNRH)
                self.GnRH_injections = self.GnRH_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 7:
                self.events.add_event(
                    self.days_born, sim_day, const.INJECT_PGF)
                self.PGF_injections = self.PGF_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 9:
                self.events.add_event(
                    self.days_born, sim_day, const.INJECT_GNRH)
                self.GnRH_injections = self.GnRH_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 10:
                self.ai_day = self.days_born
                self.conception_rate = AnimalBase.config['cow_repro_programs']['ovsynch56_conception_rate']

    def OvSynch48_update(self, sim_day):
        """
        OvSynch48 protocol for tai method
        Args:
            sim_day: the simulation day
        """
        if not self.do_not_breed:
            if self.days_born == self.tai_program_start_day_c:
                self.events.add_event(
                    self.days_born, sim_day, const.INJECT_GNRH)
                self.GnRH_injections = self.GnRH_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 7:
                self.events.add_event(
                    self.days_born, sim_day, const.INJECT_PGF)
                self.PGF_injections = self.PGF_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 9:
                self.events.add_event(
                    self.days_born, sim_day, const.INJECT_GNRH)
                self.GnRH_injections = self.GnRH_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 10:
                self.ai_day = self.days_born
                self.conception_rate = \
                    AnimalBase.config['cow_repro_programs']['ovsynch48_conception_rate']

    def CoSynch72_update(self, sim_day):
        """
        CoSynch72 protocol for tai method
        Args:
            sim_day: the simulation day
        """
        if not self.do_not_breed:
            if self.days_born == self.tai_program_start_day_c:
                self.events.add_event(
                    self.days_born, sim_day, const.INJECT_GNRH)
                self.GnRH_injections = self.GnRH_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 7:
                self.events.add_event(
                    self.days_born, sim_day, const.INJECT_PGF)
                self.PGF_injections = self.PGF_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 10:
                self.events.add_event(
                    self.days_born, sim_day, const.INJECT_GNRH)
                self.GnRH_injections = self.GnRH_injections + 1
                self.ai_day = self.days_born
                self.conception_rate = \
                    AnimalBase.config['cow_repro_programs']['cosynch72_conception_rate']

    def d5CoSynch_update(self, sim_day):
        """
        5dCoSynch protocol for tai method
        Args:
            sim_day: the simulation day
        """
        if not self.do_not_breed:
            if self.days_born == self.tai_program_start_day_c:
                self.events.add_event(
                    self.days_born, sim_day, const.INJECT_GNRH)
                self.GnRH_injections = self.GnRH_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 5:
                self.events.add_event(
                    self.days_born, sim_day, const.INJECT_PGF)
                self.PGF_injections = self.PGF_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 6:
                self.events.add_event(
                    self.days_born, sim_day, const.INJECT_PGF)
                self.PGF_injections = self.PGF_injections + 1
            elif self.days_born == self.tai_program_start_day_c + 8:
                self.events.add_event(
                    self.days_born, sim_day, const.INJECT_GNRH)
                self.GnRH_injections = self.GnRH_injections + 1
                self.ai_day = self.days_born
                self.conception_rate = \
                    AnimalBase.config['cow_repro_programs']['cosynch5d_conception_rate']

    def determine_presynch_program_day(self, date):
        """
        Determine the presynch program start time when pass voluntary
        waiting period.
        Args:
            date: the time presynch program start
        Returns: day on which the presynch program starts
        """
        self.presynch_program_start_day = date

    def presynch_update(self, sim_day):
        """
        Presynch protocol for presynch method
        Args:
            sim_day: the simulation day
        """
        if self.days_born == self.presynch_program_start_day:
            self.events.add_event(self.days_born, sim_day, const.INJECT_PGF)
            self.PGF_injections = self.PGF_injections + 1
        elif self.days_born == self.presynch_program_start_day + 14:
            self.events.add_event(self.days_born, sim_day, const.INJECT_PGF)
            self.PGF_injections = self.PGF_injections + 1
        elif self.days_born == self.presynch_program_start_day + 26:
            self.tai_program_start_day_c = self.days_born
            self.events.add_event(self.days_born, sim_day, const.PRESYNCH_END)

    def doubleovsynch_update(self, sim_day):
        """
        Doubleovsynch protocol for presynch method
        Args:
            sim_day: the simulation day
        """
        if self.days_born == self.presynch_program_start_day:
            self.events.add_event(self.days_born, sim_day, const.INJECT_GNRH)
            self.GnRH_injections = self.GnRH_injections + 1
        elif self.days_born == self.presynch_program_start_day + 7:
            self.events.add_event(self.days_born, sim_day, const.INJECT_PGF)
            self.PGF_injections = self.PGF_injections + 1
        elif self.days_born == self.presynch_program_start_day + 10:
            self.events.add_event(self.days_born, sim_day, const.INJECT_GNRH)
            self.GnRH_injections = self.GnRH_injections + 1
        elif self.days_born == self.presynch_program_start_day + 17:
            self.tai_program_start_day_c = self.days_born
            self.events.add_event(self.days_born, sim_day,
                                  const.DOUBLE_OVSYNCH_END)

    def g6g_update(self, sim_day):
        """
        g6g protocol for presynch method.
        Args:
            sim_day: the simulation day
        """
        if self.days_born == self.presynch_program_start_day:
            self.events.add_event(self.days_born, sim_day, const.INJECT_PGF)
            self.PGF_injections = self.PGF_injections + 1
        elif self.days_born == self.presynch_program_start_day + 2:
            self.events.add_event(self.days_born, sim_day, const.INJECT_GNRH)
            self.GnRH_injections = self.GnRH_injections + 1
        elif self.days_born == self.presynch_program_start_day + 9:
            self.tai_program_start_day_c = self.days_born
            self.events.add_event(self.days_born, sim_day, const.C6G_END)

    def tai_update(self, sim_day):  # noqa
        """
        Assign tai and presynch method, update time AI method status, TAI can
        be performed with or without presynch.
        Args:
            sim_day: the simulation day
        """
        if self.days_in_milk == AnimalBase.config['voluntary_waiting_period']:
            if self.presynch_method:
                self.determine_presynch_program_day(self.days_born)
            else:
                self.determine_tai_program_day(self.days_born)

        if self.presynch_method:
            if self.presynch_method == 'PreSynch':
                self.presynch_update(sim_day)
            elif self.presynch_method == 'Double OvSynch':
                self.doubleovsynch_update(sim_day)
            elif self.presynch_method == 'G6G':
                self.g6g_update(sim_day)
            else:
                raise ValueError(f'Invalid cow presynch program: {self.presynch_method}')

        if self.tai_method_c == 'OvSynch 56':
            self.OvSynch56_update(sim_day)
        elif self.tai_method_c == 'OvSynch 48':
            self.OvSynch48_update(sim_day)
        elif self.tai_method_c == 'CoSynch 72':
            self.CoSynch72_update(sim_day)
        elif self.tai_method_c == '5d CoSynch':
            self.d5CoSynch_update(sim_day)
        else:
            raise ValueError(f'Invalid cow tai program: {self.tai_method_c}')

    def _execute_hormone_delivery_schedule(self, sim_day: int, schedule: dict[int, dict]) -> None:
        """
        Execute a hormone delivery schedule.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.
        schedule : dict[int, dict]
            A dictionary of days and actions to perform on those days.

        Returns
        -------
        None
        """

        super()._execute_hormone_delivery_schedule(sim_day, schedule)

        actions = schedule.get(self.days_born)
        if actions is not None:
            if actions.get('set_presynch_end', False):
                self.log_event(self.days_born, sim_day,
                               f'{const.PRESYNCH_PERIOD_END}: {self.get_user_defined_presynch_protocol()}')
                self._is_in_presynch_period = False
                del actions['set_presynch_end']
            if actions.get('set_tai_start', False):
                self.log_event(self.days_born, sim_day,
                               f'{const.TAI_PERIOD_START}: {self.get_user_defined_repro_sub_protocol()}')
                self._is_in_tai_period = True
                del actions['set_tai_start']
            if actions.get('set_tai_end', False):
                self.log_event(self.days_born, sim_day,
                               f'{const.TAI_PERIOD_END}: {self.get_user_defined_repro_sub_protocol()}')
                self._is_in_tai_period = False
                del actions['set_tai_end']
            # if actions.get('decrease_conception_rate', False):
            #     self.log_event(self.days_born, sim_day,
            #                    f'{const.DECREASE_CONCEPTION_RATE} by {self._get_conception_rate_decrease()}')
            #     self._num_conception_rate_decreases += 1
            #     del actions['decrease_conception_rate']
            # if actions.get('set_up_tai_protocol', False):
            #     self.log_event(self.days_born, sim_day,
            #                    f'{const.SETTING_UP_TAI_PROTOCOL_IN_RESYNCH}'
            #                    f': {self.get_user_defined_repro_sub_protocol()}')
            #     self._is_in_tai_period = True
            #     del actions['set_up_tai_protocol']
            # if actions.get('simulate_estrus_after_pgf', False):
            #     self._simulate_estrus_after_pgf(self.days_born, sim_day, const.ESTRUS_AFTER_PGF_NOTE)
            #     del actions['simulate_estrus_after_pgf']
            if not actions:
                del schedule[self.days_born]

    def _simulate_estrus_after_pgf(self, start_day: int, sim_day: int, estrus_note: str) -> None:
        """
        Calculate and set the next estrus day for the animal after a PGF injection.

        Parameters
        ----------
        start_day : int
            The start day plus the estrus cycle length is the day of the next estrus.
        sim_day : int
            The current day of the entire simulation.
        estrus_note : str
            A note that describes the reason for simulating estrus.

        Returns
        -------
        None
        """

        estrus_cycle = truncnorm.rvs(-const.STDI, const.STDI,
                                     self.get_avg_estrus_cycle_after_pgf(),
                                     self.get_std_estrus_cycle_after_pgf())
        self.estrus_day = int(start_day + abs(estrus_cycle))
        self.log_event(self.days_born, sim_day, f'{estrus_note} on day {self.estrus_day}')

    def execute_tai_protocol(self, sim_day: int) -> None:
        """
        Execute the timed artificial insemination protocol.

        Parameters
        ----------
        sim_day : int
            The current simulation day.

        Returns
        -------
        None
        """

        if self._should_set_up_hormone_delivery_for_presynch():
            self._set_up_hormone_schedule('cows', self.get_user_defined_presynch_protocol(),
                                          self.days_born)
            self.log_event(self.days_born, sim_day,
                           f'{const.PRESYNCH_PERIOD_START}: {self.get_user_defined_presynch_protocol()}')

        if self._should_set_up_hormone_delivery_for_tai():
            self._set_up_hormone_schedule('cows', self.get_user_defined_repro_sub_protocol(),
                                          self.days_born)
            self._TAI_conception_rate = (self._get_user_defined_TAI_conception_rate() -
                                         (self._num_conception_rate_decreases * self._get_conception_rate_decrease()))

        if self._hormone_schedule:
            self._execute_hormone_delivery_schedule(sim_day, self._hormone_schedule)

    def _should_set_up_hormone_delivery_for_presynch(self) -> bool:
        """
        Check if the cow should set up hormone delivery for presynch.

        Returns
        -------
        bool
            True if the cow should set up hormone delivery for presynch, False otherwise.
        """

        if self.days_in_milk == self._get_voluntary_waiting_period():
            self._is_in_presynch_period = True

        if self._hormone_schedule:
            return False

        return self._is_in_presynch_period

    def _should_set_up_hormone_delivery_for_tai(self) -> bool:
        """
        Check if the cow should set up hormone delivery for timed artificial insemination.

        Returns
        -------
        bool
            True if the cow should set up hormone delivery for timed artificial insemination, False otherwise.
        """

        if self._hormone_schedule:
            return False

        return self._is_in_tai_period

    def _increment_ai_counts(self) -> None:
        """
        Increment the performed AI counts across all cows.

        Notes
        -----
        The following counts are incremented:
        - num_ai_performed: the total number of AIs performed
        - num_ai_performed_in_ED: the number of AIs performed in the ED protocol
        - num_ai_performed_in_TAI: the number of AIs performed in the TAI protocol

        Note that a cow can go through multiple breeding programs in its lifetime.

        Returns
        -------
        None
        """

        self.stats['num_ai_performed'] += 1
        self.stats['num_ai_performed_in_ED'] += 1 \
            if self.repro_program == CowReproProtocolEnum.ED.value else 0
        self.stats['num_ai_performed_in_TAI'] += 1 \
            if self.repro_program == CowReproProtocolEnum.TAI.value else 0

    def _increment_successful_conceptions(self) -> None:
        """
        Increment the successful conception counts across all heifers.

        The following counts are incremented:
        - num_successful_conceptions: the total number of successful conceptions
        - num_successful_conceptions_in_ED: the number of successful conceptions in the ED protocol
        - num_successful_conceptions_in_TAI: the number of successful conceptions in the TAI protocol

        Note that a cow can go through multiple breeding programs in its lifetime.

        Returns
        -------
        None
        """

        self.stats['num_successful_conceptions'] += 1
        self.stats['num_successful_conceptions_in_ED'] += 1 \
            if self.repro_program == CowReproProtocolEnum.ED.value else 0
        self.stats['num_successful_conceptions_in_TAI'] += 1 \
            if self.repro_program == CowReproProtocolEnum.TAI.value else 0

    def execute_ed_tai_protocol(self, sim_day: int) -> None:
        if self.days_born == self.estrus_day:
            self.estrus_count += 1
            if 1 <= self.days_in_milk <= self._get_voluntary_waiting_period():
                self.log_event(self.estrus_day, sim_day, const.ESTRUS_BEFORE_VWP_NOTE)
                self._simulate_estrus(self.estrus_day, sim_day, const.ESTRUS_DAY_SCHEDULED_NOTE)
            elif self.is_breedable() and self.days_in_milk < self._get_user_defined_tai_program_start_day():
                self._handle_ed_estrus_detection(sim_day)
            elif self.is_breedable() and self.days_in_milk >= self._get_user_defined_tai_program_start_day():
                self._is_in_tai_period = True

        if self.is_lactating and self.is_breedable():
            self.ED_days += 1

        if self.days_born >= self.ai_day:
            self._handle_ed_tai_resynch_protocols(sim_day)

    def _handle_ed_tai_resynch_protocols(self, sim_day: int) -> None:
        resynch_protocols = {
            CowReproProtocolEnum.ReSynch_TAIafterPD.value: self._handle_tai_after_preg_check,
            CowReproProtocolEnum.ReSynch_PGFatPD.value: self._handle_pgf_injection_at_preg_check
        }
        protocol = self.get_user_defined_resynch_protocol()
        resynch_protocols[protocol](sim_day)

    def _handle_tai_after_preg_check(self, sim_day: int) -> None:
        pass

    def _handle_pgf_injection_at_preg_check(self, sim_day: int) -> None:
        pass

    # ED-TAI methods
    def ed_tai_update(self, sim_day):  # noqa
        """
        Update ED-TAI method, perform estrus detection before the TAI program
        Args:
            sim_day: the simulation day
        """
        # if on estrus day, start detecting estrus
        if self.days_born == self.estrus_day and \
                self.days_in_milk < AnimalBase.config['cow_repro_programs']['tai_program_start_day']:
            self.estrus_count += 1

            if 1 <= self.days_in_milk <= AnimalBase.config['voluntary_waiting_period']:
                self.later_estrus(sim_day)
            else:
                estrus_detection_rand = random()
                if estrus_detection_rand < \
                        AnimalBase.config['cow_repro_programs']['estrus_detection_rate']:
                    # Estrus detected
                    self.events.add_event(
                        self.days_born, sim_day, const.ESTRUS_DETECTED_NOTE)
                    estrus_service_rand = random()
                    if estrus_service_rand < \
                            AnimalBase.config['cow_repro_programs']['estrus_service_rate']:
                        # serviced
                        self.ai_day = self.estrus_day + 1
                        self.conception_rate = \
                            AnimalBase.config['cow_repro_programs']['ed_conception_rate']
                    else:
                        self.return_estrus(sim_day)
                else:
                    self.return_estrus(sim_day)

        if self.milking:
            self.ED_days += 1

        if self.days_in_milk == AnimalBase.config['cow_repro_programs']['tai_program_start_day'] and \
                self.ai_day == 0:
            self.estrus_day = 0
            self.determine_tai_program_day(self.days_born)

        if self.days_in_milk == AnimalBase.config['cow_repro_programs']['tai_program_start_day'] and \
                self.ai_day == 0:
            if self.tai_method_c == 'OvSynch 56':
                self.OvSynch56_update(sim_day)
            elif self.tai_method_c == 'OvSynch 48':
                self.OvSynch48_update(sim_day)
            elif self.tai_method_c == 'CoSynch 72':
                self.CoSynch72_update(sim_day)
            elif self.tai_method_c == '5d CoSynch':
                self.d5CoSynch_update(sim_day)
            else:
                raise ValueError(f'Invalid cow tai program: {self.tai_method_c}')

    def resynch_ed_tai(self, sim_day):
        """
        Using ED at the resynch period of ED-TAI.
        Args:
            sim_day: the simulation day
        """
        if self.resynch_method == 'TAIafterPD':
            self.tai_program_start_day_c = self.abortion_day + 1
            self.conception_rate -= \
                AnimalBase.config['conception_rate_decrease']
        elif self.resynch_method == 'TAIbeforePD':
            self.tai_program_start_day_c = self.abortion_day - 6
            self.conception_rate -= \
                AnimalBase.config['conception_rate_decrease']
            if self.tai_method_c in ['OvSynch 56', 'OvSynch 48', 'CoSynch 72']:
                self.events.add_event(
                    self.tai_program_start_day_c, sim_day, const.INJECT_GNRH)
                self.GnRH_injections = self.GnRH_injections + 1
        elif self.resynch_method == 'PGFatPD':
            self.events.add_event(self.days_born, sim_day, const.INJECT_PGF)
            self.PGF_injections = self.PGF_injections + 1
            self.tai_program_start_day_c = self.abortion_day + 8
            self.conception_rate -= \
                AnimalBase.config['conception_rate_decrease']
            self.estrus_day = self.determine_estrus_day(
                self.abortion_day, const.ESTRUS_AFTER_PGF_NOTE,
                AnimalBase.config['avg_estrus_cycle_after_pgf'],
                AnimalBase.config['std_estrus_cycle_after_pgf'], sim_day)
        else:
            raise ValueError(f'Invalid cow resynch method: {self.resynch_method}')

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

    def _handle_successful_conception(self, sim_day: int) -> None:
        """
        Handle a successful conception event.

        Parameters
        ----------
        sim_day : int
            The current simulation day.

        Returns
        -------
        None
        """

        self.log_event(self.days_born, sim_day, const.SUCCESSFUL_CONCEPTION)
        self.log_event(self.days_born, sim_day, const.COW_PREG)
        self.days_in_preg = 1
        self.gestation_length = self._calculate_gestation_length()
        self.calf_birth_weight = self._calculate_calf_birth_weight(self.breed)
        if self.calves > 0:
            last_time_given_birth = self.events.get_most_recent_date(const.NEW_BIRTH)
            assert last_time_given_birth != -1
            self.calving_to_preg_time = self.days_born - last_time_given_birth
        if self.repro_program == CowReproProtocolEnum.TAI.value:
            self._set_up_tai_resynch(sim_day)

    def _handle_failed_conception(self, sim_day: int) -> None:
        """
        Handle a failed conception event.

        Parameters
        ----------
        sim_day : int
            The current simulation day.

        Returns
        -------
        None
        """

        self.log_event(self.days_born, sim_day, const.FAILED_CONCEPTION)
        self.log_event(self.days_born, sim_day, const.COW_NOT_PREG)

        if self.repro_program == CowReproProtocolEnum.ED.value:
            self._simulate_estrus(self.days_born, sim_day, const.ESTRUS_DAY_SCHEDULED_NOTE)
        elif self.repro_program == CowReproProtocolEnum.TAI.value:
            self._set_up_tai_resynch(sim_day)

    def preg_update(self, sim_day: int) -> None:
        if self.days_in_preg > 0:
            self.days_in_preg += 1

        preg_check_configs = [
            {
                "day": AnimalBase.config["cow_preg_check_day_1"],
                "loss_rate": AnimalBase.config["cow_preg_loss_rate_1"],
                "on_preg_loss": const.PREG_LOSS_BEFORE_1,
                "on_preg": const.PREG_CHECK_1_PREG,
                "on_not_preg": const.PREG_CHECK_1_NOT_PREG,
            },
            {
                "day": AnimalBase.config["cow_preg_check_day_2"],
                "loss_rate": AnimalBase.config["cow_preg_loss_rate_2"],
                "on_preg_loss": const.PREG_LOSS_BTWN_1_AND_2,
                "on_preg": const.PREG_CHECK_2_PREG,
            },
            {
                "day": AnimalBase.config["cow_preg_check_day_3"],
                "loss_rate": AnimalBase.config["cow_preg_loss_rate_3"],
                "on_preg_loss": const.PREG_LOSS_BTWN_2_AND_3,
                "on_preg": const.PREG_CHECK_3_PREG,
            }
        ]

        for preg_check_config in preg_check_configs:
            if self.days_born == self.ai_day + preg_check_config["day"]:
                self._handle_preg_check(preg_check_config, sim_day)

        if not self.is_pregnant and self.days_in_milk > self._get_do_not_breed_time():
            if self.is_breedable():
                self.log_event(self.days_born, sim_day, const.DO_NOT_BREED)
                self.do_not_breed = True

    def _handle_preg_check(self, preg_check_config: dict[str, int | str], sim_day):
        """
        Handle a pregnancy check by logging the event and terminating the pregnancy if necessary.

        Parameters
        ----------
        preg_check_config : dict[str, int | str]
            A dictionary of pregnancy check configuration values.
        sim_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        self.preg_diagnoses += 1
        if self.is_pregnant:
            if self._compare_randomized_rate_less_than(preg_check_config["loss_rate"]):
                self._terminate_pregnancy(preg_check_config["on_preg_loss"], sim_day)
            else:
                self.log_event(self.days_born, sim_day, preg_check_config["on_preg"])
                if self._is_in_tai_period:
                    self._discontinue_tai_resynch(sim_day)
        elif "on_not_preg" in preg_check_config:
            self.log_event(self.days_born, sim_day, preg_check_config["on_not_preg"])
            self.abortion_day = self.days_born
            self.open(sim_day)

    def open(self, sim_day: int) -> None:
        """
        Open cow after abortion or pregnancy loss.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.
        """

        self.log_event(self.abortion_day, sim_day, const.REBREEDING_NOTE)

        if self.repro_program == CowReproProtocolEnum.ED.value:
            self._simulate_estrus(self.estrus_day, sim_day, const.ESTRUS_DAY_SCHEDULED_NOTE)
        elif self.repro_program == CowReproProtocolEnum.TAI.value:
            if not self._is_in_tai_period:
                self._set_up_tai_resynch(sim_day)
        elif self.repro_program == CowReproProtocolEnum.ED_TAI.value:
            pass

    def _set_up_tai_resynch(self, sim_day: int) -> None:
        """
        Set up the TAI protocol after performing an AI or the first pregnancy check failed.

        Notes
        -----
        This follows the TAIbeforePD protocol, in which the first shot of GnRH is given 6 days before the first
        pregnancy check. The conception rate is decreased by the user-defined value. If the cow is pregnant
        on the first pregnancy check, the TAI protocol is discontinued.

        It is also important to note that the TAI protocol is set up in advance regardless of the outcome of the
        insemination. This is because even if the insemination is successful, the cow can still fail the first
        pregnancy check. In this case, the TAI protocol is already initiated 6 days before the first pregnancy check.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        days_before_first_preg_check = 6
        hormone_schedule_start_day = self.days_born + self._get_first_preg_check_day() - days_before_first_preg_check
        self._set_up_hormone_schedule('cows', self.get_user_defined_repro_sub_protocol(),
                                      hormone_schedule_start_day)
        self._is_in_tai_period = True
        self._num_conception_rate_decreases += 1
        self.log_event(self.days_born, sim_day,
                       f'{const.SETTING_UP_RESYNCH_TAI_IN_ADVANCE}: {self.get_user_defined_repro_sub_protocol()}')

    def _discontinue_tai_resynch(self, sim_day: int) -> None:
        """
        Discontinue the TAI protocol after passing the first pregnancy check.

        Parameters
        ----------
        sim_day : int
            The current day of the simulation.

        Returns
        -------
        None
        """

        self._is_in_tai_period = False
        self._hormone_schedule = {}
        self.log_event(self.days_born, sim_day,
                       f'{const.DISCONTINUE_RESYNCH_TAI}: {self.get_user_defined_repro_sub_protocol()}')

    @staticmethod
    def _get_first_preg_check_day() -> int:
        """
        Get the first pregnancy check day (days).

        Returns
        -------
        int
            The first pregnancy check day (days).
        """

        return AnimalBase.config['cow_preg_check_day_1']

    @staticmethod
    def _get_do_not_breed_time() -> int:
        """
        Get the user-defined value for the do-not-breed time for cows (days).

        Returns
        -------
        int
            The do not breed time for cows (days).
        """

        return AnimalBase.config['do_not_breed_time']

    @staticmethod
    def get_avg_estrus_cycle() -> int:
        """
        Get the literature value for the average estrus cycle length for cows (days).

        Returns
        -------
        float
            The average estrus cycle length for cows (days).
        """

        return AnimalBase.config['avg_estrus_cycle_cow']

    @staticmethod
    def get_std_estrus_cycle() -> float:
        """
        Get the literature value for the standard deviation of the estrus cycle length for cows (days).

        Returns
        -------
        float
            The standard deviation of the estrus cycle length for cows (days).
        """

        return AnimalBase.config['std_estrus_cycle_cow']

    @staticmethod
    def _get_voluntary_waiting_period() -> int:
        """
        Get the literature value for the voluntary waiting period for cows (days).

        Returns
        -------
        int
            The voluntary waiting period for cows (days).
        """

        return AnimalBase.config['voluntary_waiting_period']

    @staticmethod
    def _get_user_defined_tai_program_start_day() -> int:
        """
        Get the TAI program start day for cows (days) defined by the user.

        Returns
        -------
        int
            The TAI program start day for cows (days) defined by the user.
        """

        return Cow.get_user_defined_repro_sub_properties()['tai_program_start_day']

    @staticmethod
    def _get_conception_rate_decrease() -> float:
        """
        Get the conception rate decrease for cows defined by the user.

        Returns
        -------
        float
            The conception rate decrease for cows defined by the user.
        """

        return AnimalBase.config['conception_rate_decrease']

    @staticmethod
    def get_user_defined_repro_data(attribute: str) -> Any:
        """
        Get the reproduction data for cows.

        Parameters
        ----------
        attribute : str
            The name of the attribute to get from the reproduction data.

        Returns
        -------
        Any
            The value of the attribute in the reproduction data.

        Raises
        ------
        KeyError
            If the attribute is not found in the reproduction data.
        """

        if attribute not in AnimalBase.config['cows']:
            raise KeyError(f'Invalid cow repro config attribute: {attribute}')

        return AnimalBase.config['cows'][attribute]

    @staticmethod
    def get_user_defined_repro_protocol() -> str:
        """
        Get the reproduction protocol for heifers defined by the user.

        Returns
        -------
        str
            The reproduction protocol for heifers defined by the user.
        """

        return AnimalBase.config['cow_repro_method']

    @staticmethod
    def get_user_defined_repro_sub_protocol() -> str:
        """
        Get the reproduction sub protocol for cows defined by the user.

        Returns
        -------
        str
            The reproduction sub protocol for cows defined by the user.
        """

        return Cow.get_user_defined_repro_data('repro_sub_protocol')

    @staticmethod
    def get_user_defined_repro_sub_properties() -> dict:
        """
        Get the reproduction sub properties for heifers defined by the user.

        Returns
        -------
        dict
            The reproduction sub properties for heifers defined by the user.
        """

        return Cow.get_user_defined_repro_data('repro_sub_properties')

    @staticmethod
    def get_user_defined_presynch_protocol() -> str:
        """
        Get the presynch protocol for cows defined by the user.

        Returns
        -------
        str
            The presynch protocol for cows defined by the user.
        """

        return Cow.get_user_defined_repro_data('presynch_protocol')

    @staticmethod
    def get_user_defined_resynch_protocol() -> str:
        """
        Get the resynch protocol for cows defined by the user.

        Returns
        -------
        str
            The resynch protocol for cows defined by the user.
        """

        return Cow.get_user_defined_repro_data('resynch_protocol')

    @staticmethod
    def _get_user_defined_TAI_conception_rate() -> float:
        """
        Get the user-defined conception rate for cows used in the TAI protocol.

        This is to contrast with the estrus conception rate used in the ED protocol.

        Returns
        -------
        float
            The specific conception rate for cows used in the TAI protocol.
        """

        return Cow.get_user_defined_repro_sub_properties()['conception_rate']

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
            self.events.add_event(self.days_born, sim_day, const.LOW_PROD_CULL)
            self.cull_reason = const.LOW_PROD_CULL
            return True
        if self.days_born == self.future_cull_date:
            self.culled = True
            self.events.add_event(
                self.days_born, sim_day, self.cull_reason)
            return True
        if self.days_born == self.future_death_date:
            self.culled = True
            self.events.add_event(self.days_born, sim_day, const.DEATH_CULL)
            self.cull_reason = const.DEATH_CULL
            return True
        return False

    def death_update(self):
        if self.calves >= 4:
            death_rate = AnimalBase.config['parity_death_prob'][3]
        else:
            death_rate = AnimalBase.config['parity_death_prob'][self.calves - 1]
        death_rand = random()
        if (death_rand <= death_rate):
            death_upper_limit = death_lower_limit = death_time_upper_limit = death_time_lower_limit = 0
            death_date_random = random()
            for i in range(len(AnimalBase.config['death_cull_prob']) - 1):
                if (AnimalBase.config['death_cull_prob'][i] <= death_date_random <
                        AnimalBase.config['death_cull_prob'][i + 1]):
                    death_lower_limit = AnimalBase.config['death_cull_prob'][i]
                    death_upper_limit = AnimalBase.config['death_cull_prob'][i + 1]
                    death_time_lower_limit = AnimalBase.config['death_cull_prob'][i]
                    death_time_upper_limit = AnimalBase.config['death_cull_prob'][i + 1]
            n = (death_time_upper_limit - death_time_lower_limit) / (death_upper_limit - death_lower_limit)
            self.future_death_date = round(death_time_lower_limit + n * (death_date_random - death_lower_limit)
                                           + self.days_born)

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
                self.cull_reason = const.LAMENESS_CULL
            elif cull_reason_rand <= 0.4516:
                cull_reason_cull_prob = AnimalBase.config['injury_cull_prob']
                self.cull_reason = const.INJURY_CULL
            elif cull_reason_rand <= 0.6955:
                cull_reason_cull_prob = AnimalBase.config['mastitis_cull_prob']
                self.cull_reason = const.MASTITIS_CULL
            elif cull_reason_rand <= 0.8346:
                cull_reason_cull_prob = AnimalBase.config['disease_cull_prob']
                self.cull_reason = const.DISEASE_CULL
            elif cull_reason_rand <= 0.8991:
                cull_reason_cull_prob = AnimalBase.config['udder_cull_prob']
                self.cull_reason = const.UDDER_CULL
            else:
                cull_reason_cull_prob = AnimalBase.config['unknown_cull_prob']
                self.cull_reason = const.UNKNOWN_CULL

            cull_time_rand = random()
            cull_reason_upper_limit = cull_reason_lower_limit = cull_time_upper_limit = cull_time_lower_limit = 0
            for i in range(len(cull_reason_cull_prob) - 1):
                if cull_reason_cull_prob[i] <= cull_time_rand < cull_reason_cull_prob[i + 1]:
                    cull_reason_lower_limit = cull_reason_cull_prob[i]
                    cull_reason_upper_limit = cull_reason_cull_prob[i + 1]
                    cull_time_lower_limit = AnimalBase.config['cull_day_count'][i]
                    cull_time_upper_limit = AnimalBase.config['cull_day_count'][i + 1]
            x = (cull_time_upper_limit - cull_time_lower_limit) / \
                (cull_reason_upper_limit - cull_reason_lower_limit)
            self.future_cull_date = round(
                cull_time_lower_limit + x * (cull_time_rand - cull_reason_lower_limit) + self.days_born)
