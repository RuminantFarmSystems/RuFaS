from __future__ import annotations

import collections
import math
from random import random
from typing import Literal, Any, Callable

from scipy.stats import truncnorm

from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.life_cycle import animal_constants as const
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.hormone_delivery_schedule import HormoneDeliverySchedule
from RUFAS.routines.animal.life_cycle.repro_protocol_enums import HeiferReproProtocolEnum
from RUFAS.routines.animal.life_cycle.repro_protocol_misc import InternalReproSettings
from RUFAS.routines.animal.manure.growing_heifer_manure_excretion import manure_calculations
from RUFAS.routines.animal.ration.animal_requirements import AnimalRequirements

om = OutputManager()


class HeiferII(HeiferI):
    """
    This class represents the attributes and activities that are characteristic of
    heifers in the second stage of their life cycle.

    Class Attributes
    ----------------
    stats : collections.defaultdict[str, int]
        A dictionary that stores statistics about all the heiferIIs instances that have been created.
        Currently, the following statistics are being tracked:
        - `num_ai_performed`: The number of times AI was performed across all heiferIIs.
        - `num_successful_conceptions`: The number of successful conceptions out of all AI performed.
        - `num_ai_performed_in_ED`: The number of times AI was performed in the ED protocol.
        - `num_successful_conceptions_in_ED`: The number of successful conceptions out of all AI performed in the ED.
        - `num_ai_performed_in_TAI`: The number of times AI was performed in the TAI protocol.
        - `num_successful_conceptions_in_TAI`: The number of successful conceptions out of all AI performed in the TAI.
        - `num_ai_performed_in_SynchED`: The number of times AI was performed in the SynchED protocol.
        - `num_successful_conceptions_in_SynchED`: The number of successful conceptions out of all AI performed
        in the SynchED.
    """

    stats = collections.defaultdict(int)

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
        self.CIDR_injections = 0
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
        self._hormone_schedule = None
        self._TAI_conception_rate = 0.0

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
        self._hormone_schedule = None
        self._TAI_conception_rate = 0.0

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

    def update(self, sim_day):  # noqa: C901
        """
        Controls heifer's grow with average daily gain based on user's input
        until breeding start day. Here is the place to change growth rate with
        heifer feeding methods later when we have heifer nutrition from the
        ration formulation module. Breeding starts with assigned
        reproduction program. Time to move to the 3rd stage --
        replacement stage determined based on gestion length and user input of
        replacement time. Culling for reproduction problem occur when heifer
        doesn't get pregnant for a long time.

        # TODO: Refactor this method. Git issue #1038.

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

        if self.repro_program != HeiferII.get_user_defined_repro_protocol():
            if self.days_born <= self._get_breeding_start_day():
                self._set_repro_program(sim_day, HeiferII.get_user_defined_repro_protocol())

        # breeding method assign to heifer
        if self.days_born >= self._get_breeding_start_day():
            if self.repro_program == HeiferReproProtocolEnum.ED.value:
                self.execute_ed_protocol(sim_day)
            elif self.repro_program == HeiferReproProtocolEnum.TAI.value:
                self.execute_tai_protocol(sim_day)
            elif self.repro_program == HeiferReproProtocolEnum.SynchED.value:
                self.execute_synch_ed_protocol(sim_day)
            else:
                raise ValueError(f"Invalid heifer repro program: {self.repro_program}")

            if self.days_born == self.ai_day:
                self._perform_ai(sim_day)
            elif self.is_pregnant:
                self.days_in_preg += 1
                self.preg_update(sim_day)

            # prior to calving, heifer move to replacement group (heiferIII)
            if self.days_in_preg == self.gestation_length - AnimalBase.config["prefresh_day"]:
                self.days_born -= 1  # will be increment again in next stage
                third_stage = True
                self.log_event(self.days_born, sim_day, const.HEIFERII_TO_III)
        # cull heifer for reproduction reason
        if self.days_in_preg == 0 and self.days_born > AnimalBase.config["heifer_repro_cull_time"]:
            self.log_event(self.days_born, sim_day, const.HEIFER_REPRO_CULL)
            cull_stage = True

        return cull_stage, third_stage

    def _simulate_estrus(self, start_day: int, sim_day: int, estrus_note: str,
                         avg_estrus_cycle: float, std_estrus_cycle: float,
                         max_cycle_length: float = math.inf) -> None:
        """
        Calculate and set the next estrus day for the animal.

        Parameters
        ----------
        start_day : int
            The start day plus the estrus cycle length is the day of the next estrus.
        sim_day : int
            The current day of the entire simulation.
        estrus_note : str
            A note that describes the reason for simulating estrus.
        avg_estrus_cycle : float
            The average estrus cycle length.
        std_estrus_cycle : float
            The standard deviation of the estrus cycle length.
        max_cycle_length : float
            The maximum estrus cycle length.

        Returns
        -------
        None
        """

        estrus_cycle = truncnorm.rvs(-const.STDI, const.STDI,
                                     avg_estrus_cycle, std_estrus_cycle)
        if abs(estrus_cycle) >= max_cycle_length:
            estrus_cycle = max_cycle_length - 1
        self.estrus_day = int(start_day + abs(estrus_cycle))
        self.log_event(self.days_born, sim_day, f'{estrus_note} on day {self.estrus_day}')

    @staticmethod
    def _compare_randomized_rate_less_than(reference_rate: float) -> bool:
        """
        Compare a randomized rate to a reference rate.

        Parameters
        ----------
        reference_rate : float
            The reference rate to compare to.

        Returns
        -------
        bool
            True if the randomized rate is less than the reference rate, False otherwise.
        """

        return random() < reference_rate

    def log_event(self, event_day: int, sim_day: int, event_note: str) -> None:
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
        """

        self.events.add_event(event_day, sim_day, event_note)

    @staticmethod
    def get_avg_estrus_cycle() -> int:
        """
        Get the average estrus cycle length for heifers (days).

        Returns
        -------
        int
            The average estrus cycle length for heifers (days).
        """

        return AnimalBase.config['avg_estrus_cycle_heifer']

    @staticmethod
    def get_std_estrus_cycle() -> float:
        """
        Get the standard deviation of the estrus cycle length for heifers (days).

        Returns
        -------
        float
            The standard deviation of the estrus cycle length for heifers (days).
        """

        return AnimalBase.config['std_estrus_cycle_heifer']

    @staticmethod
    def get_avg_estrus_cycle_after_pgf() -> int:
        """
        Get the average estrus cycle length for heifers and cows after PGF (days).

        Returns
        -------
        int
            The average estrus cycle length for heifers and cows after PGF (days).
        """

        return AnimalBase.config['avg_estrus_cycle_after_pgf']

    @staticmethod
    def get_std_estrus_cycle_after_pgf() -> float:
        """
        Get the standard deviation of the estrus cycle length for heifers and cows after PGF (days).

        Returns
        -------
        float
            The standard deviation of the estrus cycle length for heifers and cows after PGF (days).
        """

        return AnimalBase.config['std_estrus_cycle_after_pgf']

    def get_general_estrus_detection_rate(self) -> float:
        """
        Get the general estrus detection rate for heifers.

        Returns
        -------
        float
            The general estrus detection rate for heifers.
        """

        return self.get_user_defined_repro_data('estrus_detection_rate')

    @staticmethod
    def _get_user_defined_synch_ed_estrus_detection_rate() -> float:
        """
        Get the user-defined estrus detection rate for heifers used in the SynchED protocol.

        Returns
        -------
        float
            The user-defined estrus detection rate for heifers used in the SynchED protocol.
        """

        return HeiferII.get_user_defined_repro_sub_properties()['estrus_detection_rate']

    @staticmethod
    def _get_default_synch_ed_estrus_detection_rate() -> float:
        """
        Get the default estrus detection rate for heifers used in the SynchED protocol.

        Returns
        -------
        float
            The default estrus detection rate for heifers used in the SynchED protocol.
        """

        return InternalReproSettings.HEIFER_REPRO_PROTOCOLS[
            HeiferReproProtocolEnum.SynchED.value]['default_sub_properties']['estrus_detection_rate']

    def _get_user_defined_or_default_synch_ed_estrus_detection_rate(self) -> float:
        """
        Get the estrus detection rate for heifers used in the SynchED protocol.

        Returns
        -------
        float
            The estrus detection rate for heifers used in the SynchED protocol.
        """

        if self.get_user_defined_repro_protocol() == HeiferReproProtocolEnum.SynchED.value:
            return self._get_user_defined_synch_ed_estrus_detection_rate()
        else:
            return self._get_default_synch_ed_estrus_detection_rate()

    def get_general_conception_rate(self) -> float:
        """
        Get the general conception rate for heifers.

        Returns
        -------
        float
            The general conception rate for heifers.
        """

        return self.get_user_defined_repro_data('estrus_conception_rate')

    @staticmethod
    def get_user_defined_tai_conception_rate() -> float:
        """
        Get the user-defined conception rate for heifers used in TAI protocols.

        This is to contrast with the estrus conception rate used in the ED protocol.

        Returns
        -------
        float
            The specific conception rate for heifers used in the TAI protocol.
        """

        return HeiferII.get_user_defined_repro_sub_properties()['conception_rate']

    @staticmethod
    def _get_default_TAI_conception_rate() -> float:
        """
        Get the default conception rate for heifers used in TAI protocols.

        Notes
        -----
        This is to contrast with the estrus conception rate used in the ED protocol.

        Returns
        -------
        float
            The default conception rate for heifers used in the TAI protocol.
        """

        return InternalReproSettings.HEIFER_REPRO_PROTOCOLS[
            HeiferReproProtocolEnum.TAI.value]['default_sub_properties']['conception_rate']

    def _get_user_defined_or_default_TAI_conception_rate(self) -> float:
        """
        Get the conception rate for heifers used in TAI protocols.

        This is to contrast with the estrus conception rate used in the ED protocol.

        Returns
        -------
        float
            The conception rate for heifers used in the TAI protocol.
        """

        if self.get_user_defined_repro_protocol() == HeiferReproProtocolEnum.TAI.value:
            return self.get_user_defined_tai_conception_rate()
        else:
            return self._get_default_TAI_conception_rate()

    def _detect_estrus(self, detection_rate: float) -> bool:
        """
        Determine if estrus was detected.

        Estrus is detected if a randomized rate is less than the estrus detection rate.

        Parameters
        ----------
        detection_rate : float
            The reference estrus detection rate to compare to.

        Returns
        -------
        bool
            True if estrus was detected, False otherwise.
        """

        self.estrus_count += 1
        return self._compare_randomized_rate_less_than(detection_rate)

    def execute_ed_protocol(self, sim_day: int) -> None:
        """
        Execute the ED protocol.

        Notes
        -----
        The two main differences between how estrus detection is handled in the ED protocol and the
        SynchED protocol are:
        1. The estrus detection rate and conception rate are different.
        2. Here, when estrus is not detected, another estrus is simulated. In the SynchED protocol,
              when estrus is not detected, TAI will be performed next.


        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        if not self.is_pregnant:
            self.ED_days += 1
        if self.days_born == self._get_breeding_start_day():
            self._simulate_estrus(self._get_breeding_start_day(), sim_day, const.ESTRUS_DAY_SCHEDULED_NOTE,
                                  self.get_avg_estrus_cycle(), self.get_std_estrus_cycle())
        elif self.days_born == self.estrus_day:
            self._handle_generic_estrus_detection(sim_day)

    def _handle_generic_estrus_detection(self, sim_day: int) -> None:
        """
        Perform a typical estrus detection used in the ED protocol.

        Parameters
        ----------
        sim_day : int

        Returns
        -------

        """
        self._handle_estrus_detection(
            sim_day,
            on_estrus_detected=self._handle_estrus_detected,
            on_estrus_not_detected=self._handle_estrus_not_detected
        )

    def _handle_estrus_detection(self, sim_day: int,
                                 on_estrus_detected: Callable[[int], None],
                                 on_estrus_not_detected: Callable[[int], None]
                                 ) -> None:
        """
        A skeletal method for handling estrus detection that needs to be provided with the
        appropriate functions to call when estrus is detected and when estrus is not detected.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.
        on_estrus_detected : Callable[[int], None]
            A function to call when estrus is detected.
        on_estrus_not_detected : Callable[[int], None]
            A function to call when estrus is not detected.

        Returns
        -------
        None
        """

        self.log_event(self.days_born, sim_day, const.ESTRUS_OCCURRED_NOTE)
        is_estrus_detected = self._detect_estrus(self.get_general_estrus_detection_rate())
        if is_estrus_detected:
            self.log_event(self.days_born, sim_day,
                           f'{const.ESTRUS_DETECTED_NOTE}, '
                           f'with estrus detection rate at {self.get_general_estrus_detection_rate()}')
            on_estrus_detected(sim_day)
        else:
            self.log_event(self.days_born, sim_day,
                           f'{const.ESTRUS_NOT_DETECTED_NOTE}, '
                           f'with estrus detection rate at {self.get_general_estrus_detection_rate()}')
            on_estrus_not_detected(sim_day)

    def _handle_estrus_detected(self, sim_day: int) -> None:
        """
        Perform the typical actions associated with estrus detection as used in the ED protocol.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        self.conception_rate = self.get_general_conception_rate()
        self.ai_day = self.days_born + 1
        self.log_event(self.days_born, sim_day, f'{const.AI_DAY_SCHEDULED_NOTE} on day {self.ai_day}')

    def _handle_estrus_not_detected(self, sim_day: int) -> None:
        """
        Perform the typical actions associated with estrus not being detected as used in the ED protocol.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        self._simulate_estrus(self.days_born, sim_day, const.ESTRUS_DAY_SCHEDULED_NOTE,
                              self.get_avg_estrus_cycle(), self.get_std_estrus_cycle())

    def _deliver_hormones(self, hormones: list[str], delivery_day: int, sim_day: int) -> None:
        """
        Deliver hormones to the heifer.

        Parameters
        ----------
        hormones : list[str]
            A list of hormones to deliver. Supported options: 'GnRH', 'PGF', 'CIDR'.
        delivery_day : int
            The day of the heifer's life when the hormones were delivered.
        sim_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        for hormone in hormones:
            if hormone == 'GnRH':
                self.GnRH_injections += 1
                event = const.INJECT_GNRH
            elif hormone == 'PGF':
                self.PGF_injections += 1
                event = const.INJECT_PGF
            elif hormone == 'CIDR':
                event = const.INJECT_CIDR
                self.CIDR_injections += 1
            else:
                raise ValueError(f'Invalid hormone: {hormone}')

            self.log_event(delivery_day, sim_day, event)

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

        actions = schedule.get(self.days_born)
        if actions is not None:
            if actions.get('deliver_hormones') is not None:
                self._deliver_hormones(actions['deliver_hormones'], self.days_born, sim_day)
                del actions['deliver_hormones']

            if actions.get('set_ai_day', False):
                self.ai_day = self.days_born
                self.log_event(self.days_born, sim_day, f'{const.AI_DAY_SCHEDULED_NOTE} on day {self.ai_day}')
                del actions['set_ai_day']

            if actions.get('set_conception_rate', False):
                self.conception_rate = self._TAI_conception_rate
                del actions['set_conception_rate']

            if not actions:
                del schedule[self.days_born]

    @staticmethod
    def _get_breeding_start_day() -> int:
        """
        Get the day of the heifer's life when breeding starts.

        Returns
        -------
        int
            The day of the heifer's life when breeding starts.
        """

        return AnimalBase.config['breeding_start_day_h']

    @staticmethod
    def get_user_defined_repro_data(attribute: str) -> Any:
        """
        Get the reproduction data for heifers defined by the user.

        Parameters
        ----------
        attribute : str
            The attribute to get from the reproduction data.

        Returns
        -------
        Any
            The value of the attribute.

        Raises
        ------
        KeyError
            If the attribute is not a valid attribute.
        """

        if attribute not in AnimalBase.config['heifers']:
            raise KeyError(f'Invalid heifer repro config attribute: {attribute}')

        return AnimalBase.config['heifers'][attribute]

    @staticmethod
    def get_user_defined_repro_protocol() -> str:
        """
        Get the reproduction protocol for heifers defined by the user.

        Returns
        -------
        str
            The reproduction protocol for heifers defined by the user.
        """

        return AnimalBase.config['heifer_repro_method']

    @staticmethod
    def get_user_defined_repro_sub_protocol() -> str:
        """
        Get the reproduction sub protocol for heifers defined by the user.

        Returns
        -------
        str
            The reproduction sub protocol for heifers defined by the user.
        """

        return HeiferII.get_user_defined_repro_data('repro_sub_protocol')

    @staticmethod
    def _get_default_repro_sub_protocol(protocol: str) -> str:
        """
        Get the default reproduction sub-protocol for heifers for a given reproduction protocol.

        Notes
        -----
        The default reproduction sub-protocol for heifers is defined in the InternalReproSettings
        class.

        Parameters
        ----------
        protocol : str
            The reproduction protocol to get the default sub protocol for.

        Returns
        -------
        str
            The default reproduction sub protocol for heifers for the given reproduction protocol.
        """

        return InternalReproSettings.HEIFER_REPRO_PROTOCOLS[protocol]['default_sub_protocol']

    def _get_user_defined_or_default_repro_sub_protocol(self) -> str:
        """
        Get the reproduction sub protocol for the heifer.

        Notes
        -----
        When the current reproduction protocol is the same as the user-defined protocol, the
        user-defined sub-protocol is used. Otherwise, the default sub-protocol for the current
        reproduction protocol is used.

        Returns
        -------
        str
            The reproduction sub-protocol for the heifer.
        """

        if self.repro_program == HeiferII.get_user_defined_repro_protocol():
            repro_sub_protocol = HeiferII.get_user_defined_repro_sub_protocol()
        else:
            repro_sub_protocol = self._get_default_repro_sub_protocol(self.repro_program)
        return repro_sub_protocol

    @staticmethod
    def get_user_defined_repro_sub_properties() -> dict:
        """
        Get the reproduction sub properties for heifers defined by the user.

        Returns
        -------
        dict
            The reproduction sub properties for heifers defined by the user.
        """

        return HeiferII.get_user_defined_repro_data('repro_sub_properties')

    def execute_tai_protocol(self, sim_day: int) -> None:
        """
        Execute the timed artificial insemination (TAI) protocol.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        if self.days_born == self._get_breeding_start_day():
            self._set_up_hormone_schedule('heifers', self._get_user_defined_or_default_repro_sub_protocol(),
                                          self.days_born)
            self._TAI_conception_rate = self._get_user_defined_or_default_TAI_conception_rate()

        if self._hormone_schedule:
            self._execute_hormone_delivery_schedule(sim_day, self._hormone_schedule)

    def execute_synch_ed_protocol(self, sim_day: int) -> None:
        """
        Execute the SynchED protocol.

        This method may be called every day after the heifer enters the breeding phase. However,
        only on certain days will the heifer receive hormone injections or be checked for estrus.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        if self.days_born == self._get_breeding_start_day():
            self._set_up_hormone_schedule('heifers', self._get_user_defined_or_default_repro_sub_protocol(),
                                          self.days_born)

        self._handle_synch_ed_hormone_delivery_and_set_estrus_day(sim_day)

        if self.days_born == self.estrus_day:
            self._handle_synch_ed_estrus_detection(sim_day)

    def _set_up_hormone_schedule(self, animal_category: Literal['heifers', 'cows'],
                                 repro_sub_protocol: str, start_from: int) -> None:
        """
        Set up the hormone delivery schedule for the heifer. Used in TAI and SynchED protocols.

        Parameters
        ----------
        animal_category : Literal['heifers', 'cows']
            The animal category to use. Either 'heifers' or 'cows'.
        repro_sub_protocol : str
            The reproduction sub protocol to use.
        start_from : int
            The day of the heifer's life when the hormone delivery schedule starts.

        Returns
        -------
        None
        """

        self._hormone_schedule = HormoneDeliverySchedule.get_adjusted_schedule(
            animal_category, repro_sub_protocol, start_from
        )
        if self._hormone_schedule is None:
            raise Exception(f'No hormone delivery schedule for {animal_category} - '
                            f'{repro_sub_protocol}')

    def _handle_synch_ed_hormone_delivery_and_set_estrus_day(self, sim_day: int) -> None:
        """
        Handle hormone delivery and set the estrus day for the heifers in the SynchED program.

        Estrus day is calculated and set after the last hormone delivery.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        if self._hormone_schedule:
            self._execute_hormone_delivery_schedule(sim_day, self._hormone_schedule)
            if not self._hormone_schedule:
                self._simulate_estrus(self.days_born, sim_day, const.ESTRUS_DAY_SCHEDULED_NOTE,
                                      self.get_avg_estrus_cycle_after_pgf(),
                                      self.get_std_estrus_cycle_after_pgf(),
                                      max_cycle_length=14)

    def _handle_synch_ed_estrus_detection(self, sim_day: int) -> None:
        """
        Handle estrus detection in the heifers in the SynchED program.

        If estrus is detected, AI day is set to the next day.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        self.log_event(self.days_born, sim_day, const.ESTRUS_OCCURRED_NOTE)
        is_estrus_detected = self._detect_estrus(self._get_user_defined_or_default_synch_ed_estrus_detection_rate())
        if is_estrus_detected:
            self.log_event(self.days_born, sim_day, const.ESTRUS_DETECTED_NOTE)
            self.conception_rate = self.get_user_defined_tai_conception_rate()
            self.ai_day = self.days_born + 1
            self.log_event(self.days_born, sim_day, f'{const.AI_DAY_SCHEDULED_NOTE} on day {self.ai_day}')
        else:
            self._handle_estrus_not_detected_in_synch_ed(sim_day)

    def _handle_estrus_not_detected_in_synch_ed(self, sim_day: int) -> None:
        """
        Handle the scenario where estrus is not detected in the heifers in the SynchED program.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        self.log_event(self.days_born, sim_day, const.ESTRUS_NOT_DETECTED_NOTE)
        self.log_event(self.days_born, sim_day, const.TAI_AFTER_ESTRUS_NOT_DETECTED_IN_SYNCH_ED_NOTE)
        internal_fallback_protocol = InternalReproSettings.HEIFER_REPRO_PROTOCOLS[
            self._get_user_defined_or_default_repro_sub_protocol()]['when_estrus_not_detected']

        self._set_repro_program(sim_day, internal_fallback_protocol['repro_protocol'])
        self._set_up_hormone_schedule('heifers', internal_fallback_protocol['repro_sub_protocol'], self.days_born)
        self._TAI_conception_rate = internal_fallback_protocol['repro_sub_properties']['conception_rate']
        self._execute_hormone_delivery_schedule(sim_day, self._hormone_schedule)

    def _set_repro_program(self, sim_day: int, repro_program: str) -> None:
        """
        Set the reproduction program for the heifer.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.
        repro_program : str
            The reproduction program to set.

        Returns
        -------
        None
        """

        if repro_program not in [HeiferReproProtocolEnum.ED.value,
                                 HeiferReproProtocolEnum.TAI.value,
                                 HeiferReproProtocolEnum.SynchED.value]:
            raise ValueError(f'Invalid repro program: {repro_program}')

        if self.repro_program == repro_program:
            return

        self.log_event(self.days_born, sim_day,
                       f'{const.SETTING_REPRO_PROGRAM_NOTE} from {self.repro_program} '
                       f'to {repro_program}')
        self.repro_program = repro_program

    def open(self, sim_day: int) -> None:
        """
        Open heifer after abortion or pregnancy loss.

        Notes
        -----
        Regardless of the reproduction program used for the first breeding, the rebreeding
        program is estrus detection (ED). The new estrus day will be the abortion day plus
        the estrus cycle length.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.
        """

        self.log_event(self.abortion_day, sim_day, const.REBREEDING_NOTE)
        self._set_repro_program(sim_day, HeiferReproProtocolEnum.ED.value)
        self._simulate_estrus(self.abortion_day, sim_day, const.ESTRUS_DAY_SCHEDULED_NOTE,
                              self.get_avg_estrus_cycle(), self.get_std_estrus_cycle())

    @property
    def is_pregnant(self):
        """
        Determine if the heifer is pregnant.

        Returns
        -------
        bool
            True if the heifer is pregnant, False otherwise.
        """

        return self.days_in_preg > 0

    def _perform_ai(self, sim_day: int) -> None:
        """
        Perform artificial insemination on the heifer.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        self.log_event(self.days_born, sim_day, const.AI_PERFORMED_NOTE)
        self.log_event(self.days_born, sim_day, const.INSEMINATED_W_BASE + AnimalBase.config["semen_type"])
        self.semen_num += 1
        self.AI_times += 1
        self._increment_ai_counts()
        conception_successful = self._compare_randomized_rate_less_than(self.conception_rate)
        if conception_successful:
            self._handle_successful_conception(sim_day)
            self._increment_successful_conceptions()
        else:
            self._handle_failed_conception(sim_day)

    def _increment_ai_counts(self) -> None:
        """
        Increment the performed AI counts across all heifers.

        Notes
        -----
        The following counts are incremented:
        - num_ai_performed: the total number of AIs performed
        - num_ai_performed_in_ED: the number of AIs performed in the ED protocol
        - num_ai_performed_in_TAI: the number of AIs performed in the TAI protocol
        - num_ai_performed_in_SynchED: the number of AIs performed in the SynchED protocol

        Note that a heifer can go through multiple breeding programs in its lifetime. For example,
        a heifer can be bred using the TAI protocol, then open, then bred using the ED protocol.

        Returns
        -------
        None
        """

        self.stats['num_ai_performed'] += 1
        self.stats['num_ai_performed_in_ED'] += 1 if self.repro_program == 'ED' else 0
        self.stats['num_ai_performed_in_TAI'] += 1 if self.repro_program == 'TAI' else 0
        self.stats['num_ai_performed_in_SynchED'] += 1 if self.repro_program == 'SynchED' else 0

    def _increment_successful_conceptions(self) -> None:
        """
        Increment the successful conception counts across all heifers.

        The following counts are incremented:
        - num_successful_conceptions: the total number of successful conceptions
        - num_successful_conceptions_in_ED: the number of successful conceptions in the ED protocol
        - num_successful_conceptions_in_TAI: the number of successful conceptions in the TAI protocol
        - num_successful_conceptions_in_SynchED: the number of successful conceptions in the SynchED protocol

        Note that a heifer can go through multiple breeding programs in its lifetime. For example,
        a heifer can be bred using the TAI protocol, then open, then bred using the ED protocol.

        Returns
        -------
        None
        """

        self.stats['num_successful_conceptions'] += 1
        self.stats['num_successful_conceptions_in_ED'] += 1 if self.repro_program == 'ED' else 0
        self.stats['num_successful_conceptions_in_TAI'] += 1 if self.repro_program == 'TAI' else 0
        self.stats['num_successful_conceptions_in_SynchED'] += 1 if self.repro_program == 'SynchED' else 0

    def _handle_successful_conception(self, sim_day: int):
        """
        Handle a successful conception in the heifer by logging the event and initializing pregnancy parameters.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        self.log_event(self.days_born, sim_day, const.HEIFER_PREG)
        self._initialize_pregnancy_parameters()

    def _handle_failed_conception(self, sim_day: int) -> None:
        """
        Handle a failed conception in the heifer by logging the event and simulating estrus.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        self.log_event(self.days_born, sim_day, const.HEIFER_NOT_PREG)
        self._set_repro_program(sim_day, HeiferReproProtocolEnum.ED.value)
        self._simulate_estrus(self.days_born, sim_day, const.ESTRUS_DAY_SCHEDULED_NOTE,
                              self.get_avg_estrus_cycle(), self.get_std_estrus_cycle())

    @staticmethod
    def _calculate_gestation_length() -> int:
        """
        Calculate the gestation length of the heifer (days).

        Returns
        -------
        int
            The gestation length of the heifer (days).

        """
        return int(truncnorm.rvs(-const.STDI, const.STDI,
                                 AnimalBase.config["avg_gestation_len"],
                                 AnimalBase.config["std_gestation_len"]))

    @staticmethod
    def _calculate_calf_birth_weight(breed: Literal['HO', 'JE']) -> float:
        """
        Calculate the birth weight of the calf.

        Parameters
        ----------
        breed : Literal['HO', 'JE']
            The breed of the heifer.

        Returns
        -------
        float
            The birth weight of the calf.
        """

        return truncnorm.rvs(-const.STDI, const.STDI,
                             AnimalBase.config[f"birth_weight_avg_{breed.lower()}"],
                             AnimalBase.config[f"birth_weight_std_{breed.lower()}"])

    def _initialize_pregnancy_parameters(self) -> None:
        """
        Initialize the pregnancy parameters for the heifer.

        Returns
        -------
        None
        """

        self.days_in_preg = 1
        self.abortion_day = 0
        self.breeding_to_preg_time = self.days_born - self._get_breeding_start_day()
        self.gestation_length = self._calculate_gestation_length()
        self.calf_birth_weight = self._calculate_calf_birth_weight(self.breed)

    def preg_update(self, sim_day: int) -> None:
        """
        Update the pregnancy status of the heifer.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

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
        elif "on_not_preg" in preg_check_config:
            self.log_event(self.days_born, sim_day, preg_check_config["on_not_preg"])
            self.abortion_day = self.days_born
            self.open(sim_day)

    def _terminate_pregnancy(self, preg_loss_const: str, sim_day: int) -> None:
        """
        Terminate the pregnancy by logging the event and resetting the pregnancy parameters.

        Parameters
        ----------
        preg_loss_const : str
            The description of the pregnancy loss event.
        sim_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        self.log_event(self.days_born, sim_day, preg_loss_const)
        self.abortion_day = self.days_born
        self.days_in_preg = 0
        self.open(sim_day)
        self.body_weight -= self.conceptus_weight
        self.conceptus_weight = 0
        self.calf_birth_weight = 0
        self.p_gest_for_calf = 0
