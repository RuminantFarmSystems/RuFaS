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
from __future__ import annotations

import math
from random import random
from typing import Literal

from scipy.stats import truncnorm

from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.life_cycle import animal_constants as const
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.hormone_delivery_schedule import HormoneDeliverySchedule
from RUFAS.routines.animal.manure.growing_heifer_manure_excretion import manure_calculations
from RUFAS.routines.animal.ration.animal_requirements import AnimalRequirements

om = OutputManager()


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

        if "estrus_count" in args:
            self.assign_heiferII_values(args)
        else:
            self.init_values(args)

        self.target_adg_heifer_preg = 0
        self.breeding_to_preg_time = 0
        self.conceptus_weight = 0

        self.ED_days = 0
        self.GnRH_injections = 0
        self.PGF_injections = 0
        self.semen_num = 0
        self.AI_times = 0
        self.preg_diagnoses = 0

        self.ai_day = 0
        self.estrus_day = 0
        self.conception_rate = 0.0
        self.tai_program_start_day = 0
        self.synch_ed_program_start_day = 0
        self.abortion_day = None
        self.p_gest_for_calf = 0

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
            divisor = self.gestation_length - self.days_in_preg
            if divisor == 0:
                divisor = 1
            target_ADG_heifer_preg = (0.82 * 0.96 * self.mature_body_weight -
                                      0.96 * self.body_weight) / divisor

            # BW change due to conceptus
            if self.days_in_preg == self.gestation_length:
                conceptus_growth = -self.conceptus_weight
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
        self.repro_program = args["repro_program"]

        # Estrus variables
        self.estrus_count = 0
        self.estrus_day = 0

        # TAI variables
        self.tai_method_h = args["tai_method_h"]
        self.tai_program_start_day_h = 0

        # synch_ED variables
        self.synch_ed_method_h = args["synch_ed_method_h"]
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
        self.calf_birth_weight = 0

    def assign_heiferII_values(self, args):
        """
        Assign the repro program with given vales
        """
        self.repro_program = args["repro_program"]

        # Estrus variables
        self.estrus_count = args["estrus_count"]
        self.estrus_day = args["estrus_day"]

        # TAI variables
        self.tai_method_h = args["tai_method_h"]
        self.tai_program_start_day_h = args["tai_program_start_day_h"]

        # synch_ED variables
        self.synch_ed_method_h = args["synch_ed_method_h"]
        self.synch_ed_program_start_day_h = args["synch_ed_program_start_day_h"]
        self.synch_ed_estrus_day = args["synch_ed_estrus_day"]
        self.synch_ed_stop_day = args["synch_ed_stop_day"]

        self.conception_rate = args["conception_rate"]
        self.ai_day = args["ai_day"]
        self.abortion_day = args["abortion_day"]
        self.days_in_preg = args["days_in_preg"]
        self.gestation_length = args["gestation_length"]
        self.p_gest_for_calf = args["p_gest_for_calf"]
        self.calf_birth_weight = args["calf_birth_weight"]

    def get_heiferII_values(self):
        """
        Get current information from the heiferII
        """
        values = {
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
            "tai_program_start_day_h": self.tai_program_start_day,
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
        }
        return values

    def set_nutrient_rqmts(self, temp, animal_grouping_scenario, nutrient_conc: dict = {},
                           metabolizable_energy: float = 15.625, previous_DMI: float = 10.0):
        """
        Calculates this heiferII's nutrient requirements.
        """
        if metabolizable_energy == 0.0:
            metabolizable_energy = 15.625
        if previous_DMI == 0.0:
            previous_DMI = 10.0
        if nutrient_conc and nutrient_conc['dm'] != 0.0:
            NDF_conc = nutrient_conc['NDF'] / 100
            TDN_conc = nutrient_conc['TDN'] / 100
            net_energy_diet_concentration = (metabolizable_energy * 0.64) / previous_DMI
        else:
            NDF_conc = 0.3
            TDN_conc = 0.7
            net_energy_diet_concentration = 1.0
        req = AnimalRequirements()
        animal_requirements = req.calc_rqmts(body_weight=self.body_weight,
                                             mature_body_weight=self.mature_body_weight,
                                             day_of_pregnancy=self.days_in_preg,
                                             animal_type=animal_grouping_scenario.get_animal_type(self),
                                             body_condition_score_5=3,
                                             previous_temperature=temp,
                                             average_daily_gain_heifer=self.daily_growth,
                                             NDF_conc=NDF_conc,
                                             TDN_conc=TDN_conc,
                                             net_energy_diet_concentration=net_energy_diet_concentration,
                                             days_born=self.days_born)
        self.NEmaint_requirement = animal_requirements['NEmaint_requirement']
        self.NEg_requirement = animal_requirements['NEg_requirement']
        self.NEpreg_requirement = animal_requirements['NEpreg_requirement']
        self.NEl_requirement = animal_requirements['NEl_requirement']
        self.MP_requirement = animal_requirements['MP_requirement']
        self.Ca_requirement = animal_requirements['Ca_requirement']
        self.P_requirement = animal_requirements['P_requirement']
        self.DMIest_requirement = animal_requirements['DMIest_requirement']

    def calc_manure_excretion(self, feed, methane_model):
        """
        Calculates and sets the manure excretion components.

        Args:
            feed: instance of the Feed class
            methane_model: methane model used for methane emission calculations
        """
        p_urine, p_feces_excrt = self.calc_base_manure()

        self.p_excrt, self.manure_excretion = manure_calculations(
            self.ration_formulation, feed, self.body_weight, p_feces_excrt, p_urine, methane_model
        )

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
        self.p_growth = (
                (0.0012 + 0.004635 * (self.mature_body_weight ** 0.22) * (self.body_weight ** (-0.22)))
                * self.daily_growth
                / 0.96
                * 1000
        )

        # absorbed P retained for fetal growth (g) (A.1C-F.E.4)
        if self.days_in_preg >= 190:
            exp_1 = (0.05527 - 0.000075 * self.days_in_preg) * self.days_in_preg
            exp_2 = (0.05527 - 0.000075 * (self.days_in_preg - 1)) * (self.days_in_preg - 1)
            self.p_gest = (0.00002743 * math.exp(exp_1) - 0.00002743 * math.exp(exp_2)) * 1000
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

        else:
            self.body_weight = self.mature_body_weight
            self.events.add_event(self.days_born, sim_day, const.MATURE_BODY_WEIGHT_REGULAR)

        # breeding method assign to heifer
        if self.days_born >= self._get_breeding_start_day():
            if self.repro_program == "ED":
                self.execute_ed_protocol(sim_day)
            elif self.repro_program == "TAI":
                self.execute_tai_protocol(sim_day)
            elif self.repro_program == "SynchED":
                self.synch_ed_update(sim_day)
            else:
                raise ValueError(f"Invalid heifer repro program: {self.repro_program}")

            if self.days_born == self.ai_day:
                self._perform_ai(sim_day)  # days_in_preg = 1
            elif self.is_pregnant:
                self.days_in_preg += 1
                self.preg_update(sim_day)

            # prior to calving, heifer move to replacement group (heiferIII)
            if self.days_in_preg == self.gestation_length - AnimalBase.config["prefresh_day"]:
                self.days_born -= 1  # will be increment again in next stage
                third_stage = True
                self.events.add_event(self.days_born, sim_day, const.HEIFERII_TO_III)
        # cull heifer for reproduction reason
        if self.days_in_preg == 0 and self.days_born > AnimalBase.config["heifer_repro_cull_time"]:
            self.events.add_event(self.days_born, sim_day, const.HEIFER_REPRO_CULL)
            cull_stage = True

        return cull_stage, third_stage

    def _simulate_estrus(self, start_day: int, sim_day: int, estrus_note: str):
        estrus_cycle = truncnorm.rvs(-const.STDI, const.STDI, self.avg_estrus_cycle, self.std_estrus_cycle)
        self.estrus_day = int(start_day + abs(estrus_cycle))
        self.log_event(self.days_born, sim_day, estrus_note)

    @staticmethod
    def _compare_randomized_rate_less_than(reference_rate: float) -> bool:
        return random() < reference_rate

    def log_event(self, event_day: int, sim_day: int, event_note: str):
        """
        Log a specific event on a given day in the simulation.

        Parameters
        ----------
        event_day : int
            The day of the animal's life when the event occurred.
        sim_day : int
            The current day of the entire simulation.
        event_note : str
            A note or description associated with the event.

        Notes
        -----
        This function adds the event to the animal's event history.
        """

        self.events.add_event(event_day, sim_day, event_note)

    @property
    def avg_estrus_cycle(self):
        return AnimalBase.config['avg_estrus_cycle_heifer']

    @property
    def std_estrus_cycle(self):
        return AnimalBase.config['std_estrus_cycle_heifer']

    def _detect_estrus(self, sim_day: int) -> bool:
        self.estrus_count += 1
        return self._compare_randomized_rate_less_than(self._get_repro_data('estrus_detection_rate'))

    def _decide_on_ai(self, estrus_detected: bool) -> bool:
        if not estrus_detected:
            return False

        should_perform_ai = self._compare_randomized_rate_less_than(self._get_repro_data('estrus_insemination_rate'))
        if not should_perform_ai:
            return False

        self.ai_day = self.days_born + 1
        # TODO: Check if we need to subtract 0.05 from a positive conception rate
        self.conception_rate = self._get_repro_data('estrus_conception_rate')
        return True

    def execute_ed_protocol(self, sim_day: int):
        if not self.is_pregnant:
            self.ED_days += 1
        if self.days_born == self._get_breeding_start_day():
            self._simulate_estrus(self._get_breeding_start_day(), sim_day, const.ESTRUS_DAY_SCHEDULED_NOTE)
        elif self.days_born == self.estrus_day:
            self.log_event(self.days_born, sim_day, const.ESTRUS_OCCURRED)

            estrus_detected = self._detect_estrus(sim_day)
            if estrus_detected:
                self.log_event(self.days_born, sim_day, const.ESTRUS_DETECTED)

            is_ai_scheduled = self._decide_on_ai(estrus_detected)
            if is_ai_scheduled:
                self.log_event(self.days_born, sim_day, const.AI_DAY_SCHEDULED_NOTE)
            else:
                self._simulate_estrus(self.days_born, sim_day, const.ESTRUS_DAY_SCHEDULED_NOTE)

    # TODO: Where to use this?
    def tai_program_day_after_abortion(self):
        """
        Determine the TAI restart date after abortion preg checks
        """
        self.tai_program_start_day_h = self.abortion_day + 1

    def _deliver_hormones(self, hormones: list[str], delivery_day: int, sim_day: int):
        for hormone in hormones:
            if hormone == 'GnRH':
                self.GnRH_injections += 1
                event = const.INJECT_GNRH
            elif hormone == 'PGF':
                self.PGF_injections += 1
                event = const.INJECT_PGF
            else:
                raise ValueError(f'Invalid hormone: {hormone}')

            self.log_event(delivery_day, sim_day, event)

    @staticmethod
    def _adjust_hormone_delivery_schedule_start_days(schedule: dict[int, dict], start_day: int):
        adjusted_schedule = {}
        for offset_days, actions in schedule.items():
            adjusted_schedule[start_day + offset_days] = actions
        return adjusted_schedule

    def _execute_hormone_delivery_schedule(self, sim_day: int, schedule: dict[int, dict]) -> None:
        actions = schedule.get(self.days_born)
        if actions is not None:
            if actions.get('deliver_hormones') is not None:
                self._deliver_hormones(actions['deliver_hormones'], self.days_born, sim_day)
            if actions.get('set_ai_day', False):
                self.ai_day = self.days_born
                self.log_event(self.days_born, sim_day, const.AI_DAY_SCHEDULED_NOTE)
            if actions.get('set_conception_rate', False):
                self.conception_rate = self._get_repro_data('estrus_conception_rate')

    @staticmethod
    def _get_breeding_start_day():
        return AnimalBase.config['breeding_start_day_h']

    @staticmethod
    def _get_repro_data(attribute: str):
        return AnimalBase.config['heifers'][attribute]

    def execute_tai_protocol(self, sim_day: int):
        if self.days_born == self._get_breeding_start_day():
            self.tai_program_start_day = self._get_breeding_start_day()

        tai_sub_protocol = self._get_repro_data('repro_protocols')['TAI']['sub_protocol']

        hormone_delivery_schedule = HormoneDeliverySchedule.get_schedule('heifers', tai_sub_protocol)
        if hormone_delivery_schedule is None:
            raise Exception(f'No hormone delivery schedule for {tai_sub_protocol}')

        adjusted_schedule = self._adjust_hormone_delivery_schedule_start_days(hormone_delivery_schedule,
                                                                              self.tai_program_start_day)
        self._execute_hormone_delivery_schedule(sim_day, adjusted_schedule)

    # synch-ED methods

    def determine_synch_ed_program_day(self, date):
        """
        Determine the program start time when reach breeding start time

        Args:
            date: the time breeding program start
        """
        self.synch_ed_program_start_day_h = date

    def determine_synch_ed_estrus_day(self, date, avg, std, max_val):
        """
        Determine synch ed leading estrus start day, with normal distribution

        Args:
            date: start of the synch ed day
            avg: average of estrus occur after synch ed
            std: standard deviation of synch ed
            max_val: max value can go for the normal distribution,
                avoiding negative value
        """
        synch_ed_estrus = truncnorm.rvs(-const.STDI, const.STDI, avg, std)
        norm = abs(synch_ed_estrus)
        if norm >= max_val:
            norm = max_val - 1
        self.synch_ed_estrus_day = int(date + norm)

    def synch_ed_program_day_after_abortion(self):
        """
        Return to synch ed after abortion when spot at the preg check
        """
        self.synch_ed_program_start_day_h = self.abortion_day

    def P2_update(self, sim_day):
        """
        2P protocol for synch ed method
        estrus detection happens when estrus occur
        """
        if self.days_born == self.synch_ed_program_start_day_h:
            self.events.add_event(self.days_born, sim_day, const.INJECT_PGF)
            self.PGF_injections = self.PGF_injections + 1
            self.determine_synch_ed_estrus_day(self.days_born, 5, 3, 14)

        if self.days_born == self.synch_ed_estrus_day:
            self.events.add_event(self.days_born, sim_day, const.ESTRUS_OCCURRED)
            estrus_detection_rand = random()
            if estrus_detection_rand < AnimalBase.config["estrus_detection_rate"]:
                self.events.add_event(self.days_born, sim_day, const.ESTRUS_DETECTED)
                ed_service_rand = random()
                if ed_service_rand < AnimalBase.config["estrus_service_rate"]:
                    self.ai_day = self.synch_ed_estrus_day + 1
                    self.conception_rate = AnimalBase.config["estrus_conception_rate"]
                else:
                    if self.days_born - self.synch_ed_program_start_day_h < 14:
                        # second round of injection
                        self.events.add_event(self.synch_ed_program_start_day_h + 14, sim_day, const.INJECT_PGF)
                        self.PGF_injections = self.PGF_injections + 1
                        self.determine_synch_ed_estrus_day(self.synch_ed_program_start_day_h + 14, 3, 2, 7)
                    else:
                        # second round of injection also failed,
                        # roll back to return_synch
                        self.synch_ed_stop_day = self.synch_ed_program_start_day_h + 21
                        self.determine_synch_ed_program_day(self.synch_ed_stop_day)
            else:
                self.synch_ed_stop_day = self.synch_ed_program_start_day_h + 21
                self.determine_synch_ed_program_day(self.synch_ed_stop_day)

    def CP_update(self, sim_day):
        """
        CP protocol for synch ed method
        estrus detection happens when estrus occur
        """
        if self.days_born == self.synch_ed_program_start_day_h:
            self.events.add_event(self.days_born, sim_day, const.INJECT_CIDR)
        elif self.days_born == self.synch_ed_program_start_day_h + 7:
            self.events.add_event(self.days_born, sim_day, const.INJECT_PGF)
            self.PGF_injections = self.PGF_injections + 1
            self.determine_synch_ed_estrus_day(self.days_born, 3, 2, 7)

        if self.days_born == self.synch_ed_estrus_day:
            self.events.add_event(self.days_born, sim_day, const.ESTRUS_OCCURRED)
            estrus_detection_rand = random()
            if estrus_detection_rand < AnimalBase.config["estrus_detection_rate"]:
                self.events.add_event(self.days_born, sim_day, const.ESTRUS_DETECTED)
                ed_service_rand = random()
                if ed_service_rand < AnimalBase.config["ed_service_rate"]:
                    self.ai_day = self.synch_ed_estrus_day + 1
                    self.conception_rate = AnimalBase.config["estrus_conception_rate"]
                else:
                    self.synch_ed_stop_day = self.synch_ed_program_start_day_h + 14
                    self.determine_synch_ed_program_day(self.synch_ed_stop_day)
            else:
                self.synch_ed_stop_day = self.synch_ed_program_start_day_h + 14
                self.determine_synch_ed_program_day(self.synch_ed_stop_day)

    def synch_ed_update(self, sim_day):
        """
        Synch ed method update, assign with protocols: 2P or CP
        """
        if self.days_born == AnimalBase.config["breeding_start_day_h"]:
            self.determine_synch_ed_program_day(AnimalBase.config["breeding_start_day_h"])

        if self.synch_ed_method_h == "2P":
            self.P2_update(sim_day)
        elif self.synch_ed_method_h == "CP":
            self.CP_update(sim_day)

    # Preg stage

    # after preg loss between 1 and 3 preg checks, return to
    # corresponding protocols
    def open(self, sim_day):
        """
        Assign breeding method for open heifers after spot open at preg check
        three methods can be assigned: ED, TAI, synch-ED
        """
        if self.repro_program == "ED":
            self._simulate_estrus(self.abortion_day, sim_day, const.ESTRUS_AFTER_ABORTION_NOTE)
        elif self.repro_program == "TAI":
            self.tai_program_start_day = self.abortion_day + 1
        elif self.repro_program == "synch-ED":
            self.synch_ed_program_day_after_abortion()

    @property
    def is_pregnant(self):
        return self.days_in_preg > 0

    def _perform_ai(self, sim_day: int):
        self.log_event(self.days_born, sim_day, const.AI_PERFORMED_NOTE)
        self.log_event(self.days_born, sim_day, const.INSEMINATED_W_BASE + AnimalBase.config["semen_type"])
        self.semen_num += 1
        self.AI_times += 1
        conception_successful = self._compare_randomized_rate_less_than(self.conception_rate)
        if conception_successful:
            self._handle_successful_conception(sim_day)
        else:
            self._handle_failed_conception(sim_day)

    def _handle_successful_conception(self, sim_day: int):
        self.log_event(self.days_born, sim_day, const.HEIFER_PREG)
        self._initialize_pregnancy_parameters()

    def _handle_failed_conception(self, sim_day: int):
        self.log_event(self.days_born, sim_day, const.HEIFER_NOT_PREG)
        self._simulate_estrus(self.days_born, sim_day, const.ESTRUS_DAY_SCHEDULED_NOTE)

    @staticmethod
    def _calculate_gestation_length():
        return int(truncnorm.rvs(-const.STDI, const.STDI,
                                 AnimalBase.config["avg_gestation_len"],
                                 AnimalBase.config["std_gestation_len"]))

    @staticmethod
    def _calculate_calf_birth_weight(breed: Literal['HO', 'JE']):
        return truncnorm.rvs(-const.STDI, const.STDI,
                             AnimalBase.config[f"birth_weight_avg_{breed.lower()}"],
                             AnimalBase.config[f"birth_weight_std_{breed.lower()}"])

    def _initialize_pregnancy_parameters(self):
        self.days_in_preg = 1
        self.abortion_day = 0
        self.breeding_to_preg_time = self.days_born - self._get_breeding_start_day()
        self.gestation_length = self._calculate_gestation_length()
        self.calf_birth_weight = self._calculate_calf_birth_weight(self.breed)

    def preg_update(self, sim_day: int):  # noqa
        preg_check_configs = [
            {
                "day": AnimalBase.config["preg_check_day_1"],
                "loss_rate": AnimalBase.config["preg_loss_rate_1"],
                "on_preg_loss": const.PREG_LOSS_BEFORE_1,
                "on_preg": const.PREG_CHECK_1_PREG,
                "on_not_preg": const.PREG_CHECK_1_NOT_PREG
            },
            {
                "day": AnimalBase.config["preg_check_day_2"],
                "loss_rate": AnimalBase.config["preg_loss_rate_2"],
                "on_preg_loss": const.PREG_LOSS_BTWN_1_AND_2,
                "on_preg": const.PREG_CHECK_2_PREG
            },
            {
                "day": AnimalBase.config["preg_check_day_3"],
                "loss_rate": AnimalBase.config["preg_loss_rate_3"],
                "on_preg_loss": const.PREG_LOSS_BTWN_2_AND_3,
                "on_preg": const.PREG_CHECK_3_PREG
            }
        ]

        for preg_check_config in preg_check_configs:
            if self.days_born == self.ai_day + preg_check_config["day"]:
                self._handle_preg_check(preg_check_config, sim_day)

    def _handle_preg_check(self, preg_check_config: dict[str, int | str], sim_day):
        self.preg_diagnoses += 1
        if self.is_pregnant:
            if self._compare_randomized_rate_less_than(preg_check_config["loss_rate"]):
                self._terminate_pregnancy(preg_check_config["on_preg_loss"], sim_day)
            else:
                self.log_event(self.days_born, sim_day, preg_check_config["on_preg"])
        elif "on_not_preg" in preg_check_config:
            self.abortion_day = self.days_born
            self.open(sim_day)
            self.log_event(self.days_born, sim_day, preg_check_config["on_not_preg"])

    def _terminate_pregnancy(self, preg_loss_const, sim_day):
        self.days_in_preg = 0
        self.abortion_day = self.days_born
        self.open(sim_day)
        self.body_weight -= self.conceptus_weight
        self.conceptus_weight = 0
        self.calf_birth_weight = 0
        self.p_gest_for_calf = 0
        self.log_event(self.days_born, sim_day, preg_loss_const)
