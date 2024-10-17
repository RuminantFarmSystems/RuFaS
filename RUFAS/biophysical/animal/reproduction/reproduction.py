import math
from random import random
from typing import Union, Callable, Literal

from scipy.stats import truncnorm

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_properties.animal_statistics import AnimalStatistics
from RUFAS.biophysical.animal.animal_properties.general_properties import GeneralProperties
from RUFAS.biophysical.animal.animal_properties.reproduction_properties import ReproductionProperties
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.preg_check_config import PregCheckConfig
from RUFAS.biophysical.animal.data_types.repro_protocol_enums import HeiferReproductionProtocol, \
    CowReproductionProtocol, ReproStateEnum, CowTAISubProtocol, CowPreSynchSubProtocol, CowReSynchSubProtocol

from RUFAS.biophysical.animal.reproduction.hormone_delivery_schedule import HormoneDeliverySchedule
from RUFAS.biophysical.animal.reproduction.repro_protocol_misc import InternalReproSettings
from RUFAS.time import Time


class Reproduction:
    @staticmethod
    def reproduction_update(general_properties: GeneralProperties,
                            reproduction_properties: ReproductionProperties,
                            animal_statistics: AnimalStatistics,
                            time: Time) -> tuple[
        GeneralProperties, ReproductionProperties, AnimalStatistics
    ]:
        if general_properties.animal_type == AnimalType.HEIFER_II:
            general_properties, reproduction_properties, animal_statistics = Reproduction.heiferII_reproduction_update(
                general_properties, reproduction_properties, animal_statistics, time
            )
        else:
            general_properties, reproduction_properties, animal_statistics = Reproduction.cow_reproduction_update(
                general_properties, reproduction_properties, animal_statistics, time
            )

        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def heiferII_reproduction_update(general_properties: GeneralProperties,
                                     reproduction_properties: ReproductionProperties,
                                     animal_statistics: AnimalStatistics,
                                     time: Time) -> tuple[
        GeneralProperties, ReproductionProperties, AnimalStatistics
    ]:
        if reproduction_properties.heifer_reproduction_program != AnimalConfig.heifer_reproduction_program and \
                general_properties.days_born <= AnimalConfig.heifer_breed_start_day:
            general_properties.events.add_event(
                general_properties.days_born,
                time.simulation_day,
                f"{animal_constants.SETTING_REPRO_PROGRAM_NOTE} from "
                f"{reproduction_properties.heifer_reproduction_program} "
                f"to {AnimalConfig.heifer_reproduction_program}",
            )
            reproduction_properties.heifer_reproduction_program = AnimalConfig.heifer_reproduction_program

        elif general_properties.days_born >= AnimalConfig.heifer_breed_start_day:
            if reproduction_properties.heifer_reproduction_program == HeiferReproductionProtocol.ED.value:
                (
                    general_properties,
                    reproduction_properties,
                    animal_statistics
                ) = Reproduction.execute_heifer_ed_protocol(
                    general_properties, reproduction_properties, animal_statistics, time.simulation_day
                )
            elif reproduction_properties.heifer_reproduction_program == HeiferReproductionProtocol.TAI.value:
                (
                    general_properties,
                    reproduction_properties,
                    animal_statistics
                ) = Reproduction.execute_heifer_tai_protocol(
                    general_properties, reproduction_properties, animal_statistics, time.simulation_day)
            elif reproduction_properties.heifer_reproduction_program == HeiferReproductionProtocol.SynchED.value:
                (
                    general_properties,
                    reproduction_properties,
                    animal_statistics
                ) = Reproduction.execute_heifer_synch_ed_protocol(
                    general_properties, reproduction_properties, animal_statistics, time.simulation_day
                )
            else:
                raise ValueError(f"Invalid heifer repro program: {reproduction_properties.heifer_reproduction_program}")

            if general_properties.days_born == reproduction_properties.ai_day:
                general_properties, reproduction_properties, animal_statistics = Reproduction._perform_ai(
                    general_properties, reproduction_properties, animal_statistics, time.simulation_day
                )
            elif general_properties.is_pregnant:
                general_properties.days_in_preg += 1
                general_properties, reproduction_properties, animal_statistics = Reproduction.heifer_pregnancy_update(
                    general_properties, reproduction_properties, animal_statistics, time.simulation_day
                )
        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def cow_reproduction_update(general_properties: GeneralProperties,
                                reproduction_properties: ReproductionProperties,
                                animal_statistics: AnimalStatistics,
                                time: Time) -> tuple[
        GeneralProperties, ReproductionProperties, AnimalStatistics
    ]:
        if general_properties.is_pregnant and \
                general_properties.days_in_preg == reproduction_properties.gestation_length:
            # how to signal a newborn
            general_properties, reproduction_properties = Reproduction.cow_give_birth(general_properties,
                                                                                      reproduction_properties,
                                                                                      time)
        if not reproduction_properties.do_not_breed:
            if reproduction_properties.cow_reproduction_program not in [
                CowReproductionProtocol.ED.value,
                CowReproductionProtocol.TAI.value,
                CowReproductionProtocol.ED_TAI.value,
            ]:
                raise ValueError(f"Invalid cow repro program: {reproduction_properties.cow_reproduction_program}")

            if reproduction_properties.cow_reproduction_program != AnimalConfig.cow_reproduction_program:
                general_properties, reproduction_properties = Reproduction._set_cow_reproduction_program(
                    general_properties, reproduction_properties, time.simulation_day,
                    CowReproductionProtocol(AnimalConfig.cow_reproduction_program)
                )
                general_properties.events.add_event(
                    general_properties.days_born,
                    time.simulation_day,
                    f"Pre-existing days in milk: {general_properties.days_in_milk}",
                )
                general_properties.events.add_event(
                    general_properties.days_born,
                    time.simulation_day,
                    f"Pre-existing days in preg: {general_properties.days_in_preg}",
                )
                general_properties.events.add_event(
                    general_properties.days_born,
                    time.simulation_day,
                    f"Pre-existing AI day: {reproduction_properties.ai_day}")
                general_properties.events.add_event(
                    general_properties.days_born,
                    time.simulation_day,
                    f"Pre-existing estrus day: {reproduction_properties.estrus_day}",
                )
                if not general_properties.is_pregnant:
                    reproduction_properties.repro_state_manager.enter(ReproStateEnum.ENTER_HERD_FROM_INIT)
                    general_properties.events.add_event(
                        general_properties.days_born,
                        time.simulation_day,
                        f"Current repro state(s): {reproduction_properties.repro_state_manager}",
                    )

            if reproduction_properties.cow_reproduction_program == CowReproductionProtocol.ED_TAI:
                general_properties, reproduction_properties = Reproduction.execute_cow_ed_tai_protocol(
                    general_properties, reproduction_properties, time.simulation_day)
            if reproduction_properties.cow_reproduction_program == CowReproductionProtocol.ED or \
                    reproduction_properties.repro_state_manager.is_in_any(
                        {
                            ReproStateEnum.WAITING_FULL_ED_CYCLE,
                            ReproStateEnum.WAITING_SHORT_ED_CYCLE,
                            ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH,
                        }
                    ):
                general_properties, reproduction_properties, animal_statistics = Reproduction.execute_cow_ed_protocol(
                    general_properties, reproduction_properties, animal_statistics, time.simulation_day)

            if reproduction_properties.cow_reproduction_program == CowReproductionProtocol.TAI or \
                    reproduction_properties.repro_state_manager.is_in_any(
                        {
                            ReproStateEnum.IN_PRESYNCH,
                            ReproStateEnum.HAS_DONE_PRESYNCH,
                            ReproStateEnum.IN_OVSYNCH,
                        }
                    ):
                general_properties, reproduction_properties, animal_statistics = Reproduction.execute_cow_tai_protocol(
                    general_properties, reproduction_properties, animal_statistics, time.simulation_day)

            if general_properties.days_born == reproduction_properties.ai_day:
                reproduction_properties = Reproduction._calculate_conception_rate_on_ai_day(reproduction_properties)
                reproduction_properties.repro_state_manager.enter(ReproStateEnum.AFTER_AI)
                general_properties.events.add_event(
                    general_properties.days_born,
                    time.simulation_day,
                    f"Current repro state(s): {reproduction_properties.repro_state_manager}",
                )
                general_properties, reproduction_properties, animal_statistics = Reproduction._perform_ai(
                    general_properties, reproduction_properties, animal_statistics, time.simulation_day)
            general_properties, reproduction_properties, animal_statistics = Reproduction.cow_pregnancy_update(
                general_properties, reproduction_properties, animal_statistics, time.simulation_day
            )

            return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def cow_give_birth(general_properties: GeneralProperties, reproduction_properties: ReproductionProperties,
                       time: Time) -> tuple[GeneralProperties, ReproductionProperties]:
        reproduction_properties.repro_state_manager.reset()
        reproduction_properties.calves += 1
        general_properties.days_in_milk = 1
        general_properties.days_in_preg = 0
        reproduction_properties.gestation_length = 0

        if reproduction_properties.calves >= 2:
            reproduction_properties.calving_interval = general_properties.days_born - \
                                                   general_properties.events.get_most_recent_date(
                                                       animal_constants.NEW_BIRTH)
            reproduction_properties.calving_interval_history.append(reproduction_properties.calving_interval)

        reproduction_properties.body_weight_at_calving = general_properties.body_weight

        general_properties.events.add_event(general_properties.days_born, time.simulation_day,
                                            animal_constants.NEW_BIRTH)
        general_properties.events.add_event(
            general_properties.days_born, time.simulation_day,
            f"{animal_constants.NUM_CALVES_BORN_NOTE}: {reproduction_properties.calves}")

        general_properties.future_cull_date, general_properties.cull_reason = Reproduction.determine_future_cull_date(
            general_properties, reproduction_properties)
        general_properties.future_death_date = Reproduction.determine_future_death_date(general_properties,
                                                                                        reproduction_properties)

        if reproduction_properties.cow_reproduction_program != AnimalConfig.cow_reproduction_program:
            general_properties, reproduction_properties = Reproduction._set_cow_reproduction_program(
                general_properties, reproduction_properties, time.simulation_day,
                CowReproductionProtocol(AnimalConfig.cow_reproduction_program)
            )
            reproduction_properties.repro_state_manager.reset()

        if reproduction_properties.cow_reproduction_program in [
            CowReproductionProtocol.ED.value,
            CowReproductionProtocol.ED_TAI.value,
        ]:
            general_properties, reproduction_properties = Reproduction._simulate_estrus(
                general_properties,
                reproduction_properties,
                general_properties.days_born,
                time.simulation_day,
                f"{animal_constants.ESTRUS_AFTER_CALVING_NOTE}: {animal_constants.ESTRUS_DAY_SCHEDULED_NOTE}",
                AnimalConfig.average_estrus_cycle_return,
                AnimalConfig.std_estrus_cycle_return,
            )

        return general_properties, reproduction_properties

    @staticmethod
    def determine_future_death_date(general_properties: GeneralProperties,
                                    reproduction_properties: ReproductionProperties) -> int:
        if reproduction_properties.calves >= 4:
            death_rate = AnimalConfig.parity_death_probability[3]
        else:
            death_rate = AnimalConfig.parity_death_probability[reproduction_properties.calves - 1]
        death_rand = random()
        if death_rand <= death_rate:
            death_upper_limit = death_lower_limit = death_time_upper_limit = death_time_lower_limit = 0
            death_date_random = random()
            for i in range(len(AnimalConfig.death_day_probability) - 1):
                if (
                    AnimalConfig.death_day_probability[i]
                    <= death_date_random
                    < AnimalConfig.death_day_probability[i + 1]
                ):
                    death_lower_limit = AnimalConfig.death_day_probability[i]
                    death_upper_limit = AnimalConfig.death_day_probability[i + 1]
                    death_time_lower_limit = AnimalConfig.death_day_probability[i]
                    death_time_upper_limit = AnimalConfig.death_day_probability[i + 1]
            n = (death_time_upper_limit - death_time_lower_limit) / (death_upper_limit - death_lower_limit)
            return round(
                death_time_lower_limit + n * (death_date_random - death_lower_limit) + general_properties.days_born
            )
        return int(math.inf)

    @staticmethod
    def determine_future_cull_date(general_properties: GeneralProperties,
                                   reproduction_properties: ReproductionProperties) -> tuple[int, str]:
        """
        Update cows culled for health problem, first cull or not in this parity
        will be determined with parity specific culling rate, then a cull reason
        will be determined by random draw. Then a cull day will be identified by
        reverse a distribution for cases of this reason.
        """
        cull_reason = ""
        future_cull_date = int(math.inf)
        if reproduction_properties.calves >= 4:
            inv_cull_rate = AnimalConfig.parity_cull_probability[3]
        else:
            inv_cull_rate = AnimalConfig.parity_cull_probability[reproduction_properties.calves - 1]
        cull_rand = random()
        if cull_rand <= inv_cull_rate:
            cull_reason_rand = random()
            cull_prob = 0
            if cull_reason_rand <= (cull_prob := cull_prob + AnimalConfig.feet_leg_cull_probability):
                cull_reason_cull_prob = AnimalConfig.feet_leg_cull_day_probability
                cull_reason = animal_constants.LAMENESS_CULL

            elif cull_reason_rand <= (cull_prob := cull_prob + AnimalConfig.injury_cull_probability):
                cull_reason_cull_prob = AnimalConfig.injury_cull_day_probability
                cull_reason = animal_constants.INJURY_CULL

            elif cull_reason_rand <= (cull_prob := cull_prob + AnimalConfig.mastitis_cull_probability):
                cull_reason_cull_prob = AnimalConfig.mastitis_cull_day_probability
                cull_reason = animal_constants.MASTITIS_CULL

            elif cull_reason_rand <= (cull_prob := cull_prob + AnimalConfig.disease_cull_probability):
                cull_reason_cull_prob = AnimalConfig.disease_cull_day_probability
                cull_reason = animal_constants.DISEASE_CULL

            elif cull_reason_rand <= (cull_prob + AnimalConfig.udder_cull_probability):
                cull_reason_cull_prob = AnimalConfig.udder_cull_day_probability
                cull_reason = animal_constants.UDDER_CULL

            else:
                cull_reason_cull_prob = AnimalConfig.unknown_cull_day_probability
                cull_reason = animal_constants.UNKNOWN_CULL

            cull_time_rand = random()
            cull_reason_upper_limit = cull_reason_lower_limit = cull_time_upper_limit = cull_time_lower_limit = 0
            for i in range(len(cull_reason_cull_prob) - 1):
                if cull_reason_cull_prob[i] <= cull_time_rand < cull_reason_cull_prob[i + 1]:
                    cull_reason_lower_limit = cull_reason_cull_prob[i]
                    cull_reason_upper_limit = cull_reason_cull_prob[i + 1]
                    cull_time_lower_limit = AnimalConfig.cull_day_count[i]
                    cull_time_upper_limit = AnimalConfig.cull_day_count[i + 1]
            x = (cull_time_upper_limit - cull_time_lower_limit) / (cull_reason_upper_limit - cull_reason_lower_limit)
            future_cull_date = round(
                cull_time_lower_limit + x * (cull_time_rand - cull_reason_lower_limit) + general_properties.days_born
            )

        return future_cull_date, cull_reason

    @staticmethod
    def _set_heifer_reproduction_program(general_properties: GeneralProperties,
                                         reproduction_properties: ReproductionProperties,
                                         simulation_day: int,
                                         repro_program: HeiferReproductionProtocol) -> tuple[
        GeneralProperties, ReproductionProperties
    ]:
        """
        Set the reproduction program for the cow if her current program does not match the user-defined program.

        Notes
        -----
        When a cow entering the herd through initialization, her reproduction program may not match the user-defined
        program. This method can be used to correct that.

        Parameters
        ----------
        simulation_day : int
            The current day of the entire simulation.
        repro_program : str
            The reproduction program to set for the cow.
        """

        if repro_program not in [
            HeiferReproductionProtocol.ED.value,
            HeiferReproductionProtocol.TAI.value,
            HeiferReproductionProtocol.SynchED.value
        ]:
            raise ValueError(f"Invalid repro program: {repro_program}")

        if reproduction_properties.heifer_reproduction_program == repro_program:
            return general_properties, reproduction_properties

        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            f"{animal_constants.SETTING_REPRO_PROGRAM_NOTE} from {reproduction_properties.heifer_reproduction_program} "
            f"to {repro_program}",
        )
        reproduction_properties.heifer_reproduction_program = repro_program

        return general_properties, reproduction_properties

    @staticmethod
    def _set_cow_reproduction_program(general_properties: GeneralProperties,
                                      reproduction_properties: ReproductionProperties, simulation_day: int,
                                      repro_program: CowReproductionProtocol) -> tuple[
        GeneralProperties, ReproductionProperties
    ]:
        """
        Set the reproduction program for the cow if her current program does not match the user-defined program.

        Notes
        -----
        When a cow entering the herd through initialization, her reproduction program may not match the user-defined
        program. This method can be used to correct that.

        Parameters
        ----------
        simulation_day : int
            The current day of the entire simulation.
        repro_program : str
            The reproduction program to set for the cow.
        """

        if repro_program not in [
            CowReproductionProtocol.ED.value,
            CowReproductionProtocol.TAI.value,
            CowReproductionProtocol.ED_TAI.value
        ]:
            raise ValueError(f"Invalid repro program: {repro_program}")

        if reproduction_properties.cow_reproduction_program == repro_program:
            return general_properties, reproduction_properties

        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            f"{animal_constants.SETTING_REPRO_PROGRAM_NOTE} from {reproduction_properties.cow_reproduction_program} "
            f"to {repro_program}",
        )
        reproduction_properties.cow_reproduction_program = repro_program

        return general_properties, reproduction_properties

    @staticmethod
    def _simulate_estrus(
        general_properties: GeneralProperties,
        reproduction_properties: ReproductionProperties,
        start_day: int,
        simulation_day: int,
        estrus_note: str,
        avg_estrus_cycle: float,
        std_estrus_cycle: float,
        max_cycle_length: float = math.inf,
    ) -> tuple[GeneralProperties, ReproductionProperties]:
        """
        Calculate and set the next estrus day for the animal.

        Parameters
        ----------
        start_day : int
            The start day plus the estrus cycle length is the day of the next estrus.
        simulation_day : int
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

        estrus_cycle = truncnorm.rvs(-animal_constants.STDI, animal_constants.STDI, avg_estrus_cycle, std_estrus_cycle)
        if abs(estrus_cycle) >= max_cycle_length:
            estrus_cycle = max_cycle_length - 1
        reproduction_properties.estrus_day = int(start_day + abs(estrus_cycle))
        general_properties.events.add_event(general_properties.days_born,
                                            simulation_day,
                                            f"{estrus_note} on day {reproduction_properties.estrus_day}")
        return general_properties, reproduction_properties

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

    @staticmethod
    def _detect_estrus(detection_rate: float) -> bool:
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

        return Reproduction._compare_randomized_rate_less_than(detection_rate)

    @staticmethod
    def execute_heifer_ed_protocol(
        general_properties: GeneralProperties,
        reproduction_properties: ReproductionProperties,
        animal_statistics: AnimalStatistics,
        simulation_day: int
    ) -> tuple[GeneralProperties, ReproductionProperties, AnimalStatistics]:
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
        simulation_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        if not general_properties.is_pregnant:
            animal_statistics.ED_days += 1
        if general_properties.days_born == AnimalConfig.heifer_breed_start_day:
            general_properties, reproduction_properties = Reproduction._simulate_estrus(
                general_properties,
                reproduction_properties,
                AnimalConfig.heifer_breed_start_day,
                simulation_day,
                animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
                AnimalConfig.average_estrus_cycle_heifer,
                AnimalConfig.std_estrus_cycle_heifer,
            )
        elif general_properties.days_born == reproduction_properties.estrus_day:
            (
                general_properties,
                reproduction_properties,
                animal_statistics
            ) = Reproduction._handle_generic_estrus_detection(
                general_properties, reproduction_properties, animal_statistics, simulation_day
            )

        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def _handle_generic_estrus_detection(
        general_properties: GeneralProperties,
        reproduction_properties: ReproductionProperties,
        animal_statistics: AnimalStatistics,
        simulation_day: int
    ) -> tuple[GeneralProperties, ReproductionProperties, AnimalStatistics]:
        """
        Perform a typical estrus detection used in the ED protocol.

        Parameters
        ----------
        simulation_day : int

        Returns
        -------

        """
        general_properties, reproduction_properties, animal_statistics = Reproduction._handle_estrus_detection(
            general_properties,
            reproduction_properties,
            animal_statistics,
            simulation_day,
            on_estrus_detected=Reproduction._handle_estrus_detected,
            on_estrus_not_detected=Reproduction._handle_estrus_not_detected,
        )
        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def _handle_estrus_detection(
        general_properties: GeneralProperties, reproduction_properties: ReproductionProperties,
        animal_statistics: AnimalStatistics, simulation_day: int,
        on_estrus_detected: Callable[[GeneralProperties, ReproductionProperties, int],
                                     tuple[GeneralProperties, ReproductionProperties]],
        on_estrus_not_detected: Callable[[GeneralProperties, ReproductionProperties, int], tuple[
            GeneralProperties, ReproductionProperties]],
    ) -> tuple[GeneralProperties, ReproductionProperties, AnimalStatistics]:
        """
        A skeletal method for handling estrus detection that needs to be provided with the
        appropriate functions to call when estrus is detected and when estrus is not detected.

        Parameters
        ----------
        simulation_day : int
            The current day of the entire simulation.
        on_estrus_detected : Callable[[int], None]
            A function to call when estrus is detected.
        on_estrus_not_detected : Callable[[int], None]
            A function to call when estrus is not detected.

        Returns
        -------
        None
        """
        estrus_detection_rate = AnimalConfig.heifer_estrus_detection_rate \
            if general_properties.animal_type == AnimalType.HEIFER_II else AnimalConfig.cow_estrus_detection_rate
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            animal_constants.ESTRUS_OCCURRED_NOTE,
        )
        is_estrus_detected = Reproduction._detect_estrus(estrus_detection_rate)
        animal_statistics.estrus_count += 1
        if is_estrus_detected:
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                f"{animal_constants.ESTRUS_DETECTED_NOTE}, "
                f"with estrus detection rate at {estrus_detection_rate}",
            )
            general_properties, reproduction_properties = on_estrus_detected(
                general_properties, reproduction_properties, simulation_day)
        else:
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                f"{animal_constants.ESTRUS_NOT_DETECTED_NOTE}, "
                f"with estrus detection rate at {estrus_detection_rate}",
            )
            general_properties, reproduction_properties = on_estrus_not_detected(
                general_properties, reproduction_properties, simulation_day)

        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def _handle_estrus_detected(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties]:
        """
        Perform the typical actions associated with estrus detection as used in the ED protocol.

        Parameters
        ----------
        simulation_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        reproduction_properties.conception_rate = AnimalConfig.heifer_estrus_conception_rate
        reproduction_properties.ai_day = general_properties.days_born + 1
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            f"{animal_constants.AI_DAY_SCHEDULED_NOTE} on day {reproduction_properties.ai_day}",
        )
        return general_properties, reproduction_properties

    @staticmethod
    def _handle_estrus_not_detected(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties]:
        """
        Perform the typical actions associated with estrus not being detected as used in the ED protocol.

        Parameters
        ----------
        simulation_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        general_properties, reproduction_properties = Reproduction._simulate_estrus(
            general_properties,
            reproduction_properties,
            general_properties.days_born,
            simulation_day,
            animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
            AnimalConfig.average_estrus_cycle_heifer,
            AnimalConfig.std_estrus_cycle_heifer,
        )
        return general_properties, reproduction_properties

    @staticmethod
    def _deliver_hormones(general_properties: GeneralProperties, animal_statistics: AnimalStatistics,
                          hormones: list[str], delivery_day: int, simulation_day: int) -> tuple[
        GeneralProperties, AnimalStatistics
    ]:
        """
        Deliver hormones to the heifer.

        Parameters
        ----------
        hormones : list[str]
            A list of hormones to deliver. Supported options: 'GnRH', 'PGF', 'CIDR'.
        delivery_day : int
            The day of the heifer's life when the hormones were delivered.
        simulation_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        for hormone in hormones:
            if hormone == "GnRH":
                animal_statistics.GnRH_injections += 1
                event = animal_constants.INJECT_GNRH
            elif hormone == "PGF":
                animal_statistics.PGF_injections += 1
                event = animal_constants.INJECT_PGF
            elif hormone == "CIDR":
                animal_statistics.CIDR_injections += 1
                event = animal_constants.INJECT_CIDR
            else:
                raise ValueError(f"Invalid hormone: {hormone}")

            general_properties.events.add_event(
                delivery_day,
                simulation_day,
                event,
            )
        return general_properties, animal_statistics

    @staticmethod
    def _execute_hormone_delivery_schedule(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            animal_statistics: AnimalStatistics,
            simulation_day: int,
            schedule: dict[int, dict]) -> tuple[GeneralProperties, ReproductionProperties, AnimalStatistics]:
        """
        Execute a hormone delivery schedule.

        Parameters
        ----------
        simulation_day : int
            The current day of the entire simulation.
        schedule : dict[int, dict]
            A dictionary of days and actions to perform on those days.

        Returns
        -------
        None
        """

        actions = schedule.get(general_properties.days_born)
        if actions is not None:
            if actions.get("deliver_hormones") is not None:
                general_properties, animal_statistics = Reproduction._deliver_hormones(
                    general_properties, animal_statistics, actions["deliver_hormones"], general_properties.days_born,
                    simulation_day)
                del actions["deliver_hormones"]

            if actions.get("set_ai_day", False):
                reproduction_properties.ai_day = general_properties.days_born
                general_properties.events.add_event(
                    general_properties.days_born,
                    simulation_day,
                    f"{animal_constants.AI_DAY_SCHEDULED_NOTE} on day {reproduction_properties.ai_day}",
                )
                del actions["set_ai_day"]

            if actions.get("set_conception_rate", False):
                reproduction_properties.conception_rate = reproduction_properties.cow_TAI_conception_rate
                del actions["set_conception_rate"]

            if not actions:
                del schedule[general_properties.days_born]
        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def execute_heifer_tai_protocol(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            animal_statistics: AnimalStatistics,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties, AnimalStatistics]:
        """
        Execute the timed artificial insemination (TAI) protocol.

        Parameters
        ----------
        simulation_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """
        reproduction_properties.heifer_reproduction_sub_program = AnimalConfig.heifer_reproduction_sub_program if \
            reproduction_properties.heifer_reproduction_program == AnimalConfig.heifer_reproduction_program else \
            InternalReproSettings.HEIFER_REPRO_PROTOCOLS[reproduction_properties.heifer_reproduction_program.value][
                "default_sub_protocol"]
        if general_properties.days_born == AnimalConfig.heifer_breed_start_day:
            reproduction_properties = Reproduction._set_up_hormone_schedule(
                general_properties,
                reproduction_properties,
                general_properties.days_born,
            )
            reproduction_properties.TAI_conception_rate = \
                AnimalConfig.heifer_reproduction_sub_program_conception_rate if \
                    AnimalConfig.heifer_reproduction_program == HeiferReproductionProtocol.TAI.value \
                    else InternalReproSettings.HEIFER_REPRO_PROTOCOLS[HeiferReproductionProtocol.TAI.value][
                    "default_sub_properties"]["conception_rate"]

        if reproduction_properties.hormone_schedule:
            (
                general_properties, reproduction_properties, animal_statistics
            ) = Reproduction._execute_hormone_delivery_schedule(
                general_properties, reproduction_properties, animal_statistics, simulation_day,
                reproduction_properties.hormone_schedule)

        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def execute_heifer_synch_ed_protocol(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            animal_statistics: AnimalStatistics,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties, AnimalStatistics]:
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

        if general_properties.days_born == AnimalConfig.heifer_breed_start_day:
            reproduction_properties.heifer_reproduction_sub_program = AnimalConfig.heifer_reproduction_sub_program if \
                reproduction_properties.heifer_reproduction_program == AnimalConfig.heifer_reproduction_program else \
                InternalReproSettings.HEIFER_REPRO_PROTOCOLS[reproduction_properties.heifer_reproduction_program.value][
                    "default_sub_protocol"]
            reproduction_properties = Reproduction._set_up_hormone_schedule(
                general_properties,
                reproduction_properties,
                general_properties.days_born,
            )

        (
            general_properties,
            reproduction_properties,
            animal_statistics
        ) = Reproduction._handle_synch_ed_hormone_delivery_and_set_estrus_day(
            general_properties, reproduction_properties, animal_statistics, simulation_day
        )

        if general_properties.days_born == reproduction_properties.estrus_day:
            (
                general_properties, reproduction_properties, animal_statistics
            ) = Reproduction._handle_synch_ed_estrus_detection(
                general_properties, reproduction_properties, animal_statistics, simulation_day
            )

        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def _set_up_hormone_schedule(
        general_properties: GeneralProperties,
        reproduction_properties: ReproductionProperties,
        start_from: int,
    ) -> ReproductionProperties:
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

        Raises
        ------
        Exception
            If there is no hormone delivery schedule for the animal category.

        """
        if general_properties.animal_type == AnimalType.HEIFER_II:
            reproduction_properties.hormone_schedule = HormoneDeliverySchedule.get_adjusted_schedule(
                "heifers", reproduction_properties.heifer_reproduction_sub_program.value, start_from
            )
            if reproduction_properties.hormone_schedule is None:
                raise Exception(f"No hormone delivery schedule for {general_properties.animal_type} - "
                                f"{reproduction_properties.heifer_reproduction_sub_program}")

        else:
            reproduction_properties.hormone_schedule = HormoneDeliverySchedule.get_adjusted_schedule(
                "cows", reproduction_properties.cow_reproduction_sub_program.value, start_from
            )
            if reproduction_properties.hormone_schedule is None:
                raise Exception(f"No hormone delivery schedule for {general_properties.animal_type} - "
                                f"{reproduction_properties.cow_reproduction_sub_program}")
        return reproduction_properties

    @staticmethod
    def _handle_synch_ed_hormone_delivery_and_set_estrus_day(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            animal_statistics: AnimalStatistics,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties, AnimalStatistics]:
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

        if reproduction_properties.hormone_schedule:
            (
                general_properties, reproduction_properties, animal_statistics
            ) = Reproduction._execute_hormone_delivery_schedule(
                general_properties, reproduction_properties, animal_statistics, simulation_day,
                reproduction_properties.hormone_schedule)
            if not reproduction_properties.hormone_schedule:
                general_properties, reproduction_properties = Reproduction._simulate_estrus(
                    general_properties,
                    reproduction_properties,
                    general_properties.days_born,
                    simulation_day,
                    animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
                    AnimalConfig.average_estrus_cycle_after_pgf,
                    AnimalConfig.std_estrus_cycle_after_pgf,
                    max_cycle_length=14
                )

        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def _handle_synch_ed_estrus_detection(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            animal_statistics: AnimalStatistics,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties, AnimalStatistics]:
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
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            animal_constants.ESTRUS_OCCURRED_NOTE,
        )
        synch_ed_estrus_detection_rate = AnimalConfig.heifer_reproduction_sub_program_estrus_detection_rate if \
            AnimalConfig.heifer_reproduction_program == HeiferReproductionProtocol.SynchED.value else \
            InternalReproSettings.HEIFER_REPRO_PROTOCOLS[HeiferReproductionProtocol.SynchED.value][
                "default_sub_properties"]["estrus_detection_rate"]
        is_estrus_detected = Reproduction._detect_estrus(synch_ed_estrus_detection_rate)

        if is_estrus_detected:
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                animal_constants.ESTRUS_DETECTED_NOTE,
            )
            reproduction_properties.conception_rate = AnimalConfig.heifer_reproduction_sub_program_conception_rate
            reproduction_properties.ai_day = general_properties.days_born + 1
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                f"{animal_constants.AI_DAY_SCHEDULED_NOTE} on day {reproduction_properties.ai_day}",
            )
        else:
            (
                general_properties,
                reproduction_properties,
                animal_statistics
            ) = Reproduction._handle_estrus_not_detected_in_synch_ed(
                general_properties, reproduction_properties, animal_statistics, simulation_day
            )
        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def _handle_estrus_not_detected_in_synch_ed(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            animal_statistics: AnimalStatistics,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties, AnimalStatistics]:
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
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            animal_constants.ESTRUS_NOT_DETECTED_NOTE,
        )
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            animal_constants.TAI_AFTER_ESTRUS_NOT_DETECTED_IN_SYNCH_ED_NOTE,
        )
        heifer_repro_sub_protocol = reproduction_properties.heifer_reproduction_sub_program \
            if reproduction_properties.heifer_reproduction_sub_program == AnimalConfig.heifer_reproduction_sub_program \
            else InternalReproSettings.HEIFER_REPRO_PROTOCOLS[
            reproduction_properties.heifer_reproduction_sub_program.value]["default_sub_protocol"]

        internal_fallback_protocol = InternalReproSettings.HEIFER_REPRO_PROTOCOLS[
            heifer_repro_sub_protocol]["when_estrus_not_detected"]

        if reproduction_properties.heifer_reproduction_program.value != internal_fallback_protocol['repro_protocol']:
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                f"{animal_constants.SETTING_REPRO_PROGRAM_NOTE} from "
                f"{reproduction_properties.heifer_reproduction_program} to "
                f"{internal_fallback_protocol['repro_protocol']}",
            )
            reproduction_properties.heifer_reproduction_program = internal_fallback_protocol["repro_protocol"]

        reproduction_properties = Reproduction._set_up_hormone_schedule(
            general_properties,
            reproduction_properties,
            general_properties.days_born,
        )
        reproduction_properties.TAI_conception_rate = internal_fallback_protocol["repro_sub_properties"][
            "conception_rate"]

        (
            general_properties, reproduction_properties, animal_statistics
        ) = Reproduction._execute_hormone_delivery_schedule(
            general_properties, reproduction_properties, animal_statistics, simulation_day,
            reproduction_properties.hormone_schedule)

        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def open_heifer(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties]:
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
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            animal_constants.REBREEDING_NOTE,
        )
        if reproduction_properties.heifer_reproduction_program != HeiferReproductionProtocol.ED:
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                f"{animal_constants.SETTING_REPRO_PROGRAM_NOTE} from "
                f"{reproduction_properties.heifer_reproduction_program} to "
                f"{HeiferReproductionProtocol.ED}",
            )
            reproduction_properties.heifer_reproduction_program = HeiferReproductionProtocol.ED

        general_properties, reproduction_properties = Reproduction._simulate_estrus(
            general_properties,
            reproduction_properties,
            reproduction_properties.abortion_day,
            simulation_day,
            animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
            AnimalConfig.average_estrus_cycle_heifer,
            AnimalConfig.std_estrus_cycle_heifer,
        )

        return general_properties, reproduction_properties

    @staticmethod
    def _perform_ai(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            animal_statistics: AnimalStatistics,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties, AnimalStatistics]:
        """
        Perform artificial insemination on the heifer.

        Parameters
        ----------
        simulation_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            animal_constants.AI_PERFORMED_NOTE,
        )
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            animal_constants.INSEMINATED_W_BASE + AnimalConfig.semen_type,
        )
        animal_statistics.semen_num += 1
        animal_statistics.AI_times += 1

        if general_properties.animal_type == AnimalType.HEIFER_II:
            animal_statistics = Reproduction._increment_heifer_ai_counts(reproduction_properties, animal_statistics)
        else:
            animal_statistics = Reproduction._increment_cow_ai_counts(animal_statistics)

        conception_successful = Reproduction._compare_randomized_rate_less_than(reproduction_properties.conception_rate)
        if conception_successful:
            if general_properties.animal_type == AnimalType.HEIFER_II:
                general_properties, reproduction_properties = Reproduction._handle_successful_heifer_conception(
                    general_properties, reproduction_properties, simulation_day)
                animal_statistics = Reproduction._increment_successful_heifer_conceptions(
                    reproduction_properties, animal_statistics)
            else:
                general_properties, reproduction_properties = Reproduction._handle_successful_cow_conception(
                    general_properties, reproduction_properties, simulation_day)
                animal_statistics = Reproduction._increment_successful_cow_conceptions(
                    reproduction_properties, animal_statistics)
        else:
            if general_properties.animal_type == AnimalType.HEIFER_II:
                general_properties, reproduction_properties = Reproduction._handle_failed_heifer_conception(
                    general_properties, reproduction_properties, simulation_day
                )
            else:
                general_properties, reproduction_properties = Reproduction._handle_failed_cow_conception(
                    general_properties, reproduction_properties, simulation_day
                )

        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def _increment_heifer_ai_counts(reproduction_properties: ReproductionProperties,
            animal_statistics: AnimalStatistics) -> AnimalStatistics:
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

        animal_statistics.num_ai_performed += 1
        animal_statistics.num_ai_performed_in_ED += 1 if \
            reproduction_properties.heifer_reproduction_program == HeiferReproductionProtocol.ED else 0
        animal_statistics.num_ai_performed_in_TAI += 1 if \
            reproduction_properties.heifer_reproduction_program == HeiferReproductionProtocol.TAI else 0
        animal_statistics.num_ai_performed_in_SynchED += 1 if \
            reproduction_properties.heifer_reproduction_program == HeiferReproductionProtocol.SynchED else 0
        return animal_statistics

    @staticmethod
    def _increment_successful_heifer_conceptions(reproduction_properties: ReproductionProperties,
            animal_statistics: AnimalStatistics) -> AnimalStatistics:
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
        animal_statistics.num_successful_conceptions += 1
        animal_statistics.num_successful_conceptions_in_ED += 1 if \
            reproduction_properties.heifer_reproduction_program == HeiferReproductionProtocol.ED else 0
        animal_statistics.num_successful_conceptions_in_TAI += 1 if \
            reproduction_properties.heifer_reproduction_program == HeiferReproductionProtocol.TAI else 0
        animal_statistics.num_successful_conceptions_in_SynchED += 1 if \
            reproduction_properties.heifer_reproduction_program == HeiferReproductionProtocol.SynchED else 0
        return animal_statistics

    @staticmethod
    def _handle_successful_heifer_conception(general_properties: GeneralProperties,
                                      reproduction_properties: ReproductionProperties,
                                      simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties]:
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
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            animal_constants.HEIFER_PREG,
        )
        general_properties, reproduction_properties = Reproduction._initialize_pregnancy_parameters(
            general_properties, reproduction_properties)
        return general_properties, reproduction_properties

    @staticmethod
    def _handle_failed_heifer_conception(general_properties: GeneralProperties,
                                  reproduction_properties: ReproductionProperties,
                                  simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties]:
        """
        Handle a failed conception in the heifer by logging the event and simulating estrus.

        Parameters
        ----------
        simulation_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            animal_constants.HEIFER_NOT_PREG,
        )
        if general_properties.animal_type == AnimalType.HEIFER_II:
            general_properties, reproduction_properties = Reproduction._set_heifer_reproduction_program(
                general_properties, reproduction_properties, simulation_day, HeiferReproductionProtocol.ED)
        else:
            general_properties, reproduction_properties = Reproduction._set_cow_reproduction_program(
                general_properties, reproduction_properties, simulation_day, CowReproductionProtocol.ED)

        average_estrus_cycle = AnimalConfig.average_estrus_cycle_heifer if \
            general_properties.animal_type == AnimalType.HEIFER_II else AnimalConfig.average_estrus_cycle_cow
        std_estrus_cycle = AnimalConfig.std_estrus_cycle_heifer if \
            general_properties.animal_type == AnimalType.HEIFER_II else AnimalConfig.std_estrus_cycle_cow

        general_properties, reproduction_properties = Reproduction._simulate_estrus(
            general_properties,
            reproduction_properties,
            general_properties.days_born,
            simulation_day,
            animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
            average_estrus_cycle,
            std_estrus_cycle,
        )
        return general_properties, reproduction_properties

    @staticmethod
    def _calculate_gestation_length() -> int:
        """
        Calculate the gestation length of the heifer (days).

        Returns
        -------
        int
            The gestation length of the heifer (days).

        """
        return int(
            truncnorm.rvs(
                -animal_constants.STDI,
                animal_constants.STDI,
                AnimalConfig.average_gestation_length,
                AnimalConfig.std_gestation_length,
            )
        )

    @staticmethod
    def _calculate_calf_birth_weight(breed: Literal["HO", "JE"]) -> float:
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
        average_birth_weight_by_breed = {
            "HO": AnimalConfig.birth_weight_avg_ho,
            "JE": AnimalConfig.birth_weight_avg_je,
        }
        std_birth_weight_by_breed = {
            "HO": AnimalConfig.birth_weight_std_ho,
            "JE": AnimalConfig.birth_weight_std_je,
        }
        birth_weight = truncnorm.rvs(
            -animal_constants.STDI,
            animal_constants.STDI,
            average_birth_weight_by_breed[breed],
            std_birth_weight_by_breed[breed],
        )
        return float(birth_weight)

    @staticmethod
    def _initialize_pregnancy_parameters(general_properties: GeneralProperties,
                                         reproduction_properties: ReproductionProperties
                                         ) -> tuple[GeneralProperties, ReproductionProperties]:
        """
        Initialize the pregnancy parameters for the heifer.

        Returns
        -------
        None
        """

        general_properties.days_in_preg = 1
        reproduction_properties.abortion_day = 0
        reproduction_properties.breeding_to_preg_time = general_properties.days_born - \
                                                        AnimalConfig.heifer_breed_start_day
        reproduction_properties.gestation_length = Reproduction._calculate_gestation_length()
        reproduction_properties.calf_birth_weight = Reproduction._calculate_calf_birth_weight(
            general_properties.breed.value)

        return general_properties, reproduction_properties

    @staticmethod
    def heifer_pregnancy_update(general_properties: GeneralProperties,
                                reproduction_properties: ReproductionProperties,
                                animal_statistics: AnimalStatistics,
                                simulation_day: int) -> tuple[
        GeneralProperties, ReproductionProperties, AnimalStatistics
    ]:
        """
        Update the pregnancy status of the heifer.

        Parameters
        ----------
        simulation_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """
        preg_check_configs: list[PregCheckConfig] = [
            {
                "day": AnimalConfig.first_pregnancy_check_day,
                "loss_rate": AnimalConfig.first_pregnancy_check_loss_rate,
                "on_preg_loss": animal_constants.PREG_LOSS_BEFORE_1,
                "on_preg": animal_constants.PREG_CHECK_1_PREG,
                "on_not_preg": animal_constants.PREG_CHECK_1_NOT_PREG,
            },
            {
                "day": AnimalConfig.second_pregnancy_check_day,
                "loss_rate": AnimalConfig.second_pregnancy_check_loss_rate,
                "on_preg_loss": animal_constants.PREG_LOSS_BTWN_1_AND_2,
                "on_preg": animal_constants.PREG_CHECK_2_PREG,
            },
            {
                "day": AnimalConfig.third_pregnancy_check_day,
                "loss_rate": AnimalConfig.third_pregnancy_check_loss_rate,
                "on_preg_loss": animal_constants.PREG_LOSS_BTWN_2_AND_3,
                "on_preg": animal_constants.PREG_CHECK_3_PREG,
            },
        ]

        for preg_check_config in preg_check_configs:
            if general_properties.days_born == reproduction_properties.ai_day + preg_check_config["day"]:
                (
                    general_properties, reproduction_properties, animal_statistics
                ) = Reproduction._handle_heifer_pregnancy_check(
                    general_properties, reproduction_properties, animal_statistics, preg_check_config, simulation_day)
        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def _handle_heifer_pregnancy_check(general_properties: GeneralProperties,
                                       reproduction_properties: ReproductionProperties,
                                       animal_statistics: AnimalStatistics,
                                       preg_check_config: PregCheckConfig,
                                       simulation_day: int) -> tuple[
        GeneralProperties, ReproductionProperties, AnimalStatistics
    ]:
        """
        Handle a pregnancy check by logging the event and terminating the pregnancy if necessary.

        Parameters
        ----------
        preg_check_config : dict[str, str | int | float]
            A dictionary of pregnancy check configuration values.
        sim_day : int
            The current day of the entire simulation.

        Returns
        -------
        None
        """

        animal_statistics.preg_diagnoses += 1
        if general_properties.is_pregnant:
            if Reproduction._compare_randomized_rate_less_than(preg_check_config["loss_rate"]):
                general_properties, reproduction_properties, animal_statistics = Reproduction._terminate_pregnancy(
                    general_properties, reproduction_properties, animal_statistics,
                    preg_check_config["on_preg_loss"], simulation_day)
            else:
                general_properties.events.add_event(
                    general_properties.days_born,
                    simulation_day,
                    preg_check_config["on_preg"],
                )
        elif "on_not_preg" in preg_check_config:
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                preg_check_config["on_not_preg"],
            )
            reproduction_properties.abortion_day = general_properties.days_born
            general_properties, reproduction_properties = Reproduction.open_heifer(
                general_properties, reproduction_properties, simulation_day
            )
        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def _handle_cow_pregnancy_check(general_properties: GeneralProperties,
                                    reproduction_properties: ReproductionProperties,
                                    animal_statistics: AnimalStatistics,
                                    preg_check_config: PregCheckConfig,
                                    simulation_day: int) -> tuple[
        GeneralProperties, ReproductionProperties, AnimalStatistics
    ]:
        """
        Handle a pregnancy check by logging the event and terminating the pregnancy if necessary.

        Notes
        -----
        If the cow is not pregnant at the start of the method or loses the pregnancy after,
        she will essentially go through the steps as specified in the open() method.

        When the TAIbeforePD resynch protocol is used, the TAI program instituted prior to the
        first pregnancy check will be discontinued if the cow remains pregnant.

        Parameters
        ----------
        preg_check_config : dict[str, str | int | float]
            A dictionary of pregnancy check configuration values.
        sim_day : int
            The current day of the entire simulation.
        """

        animal_statistics.preg_diagnoses += 1
        if general_properties.is_pregnant:
            if Reproduction._compare_randomized_rate_less_than(preg_check_config["loss_rate"]):
                reproduction_properties.repro_state_manager.exit(ReproStateEnum.PREGNANT)
                general_properties, reproduction_properties, animal_statistics = Reproduction._terminate_pregnancy(
                    general_properties, reproduction_properties, animal_statistics,
                    preg_check_config["on_preg_loss"], simulation_day)
            else:
                general_properties.events.add_event(
                    general_properties.days_born,
                    simulation_day,
                    preg_check_config["on_preg"],
                )
                if reproduction_properties.repro_state_manager.is_in(ReproStateEnum.IN_OVSYNCH):
                    (
                        general_properties,
                        reproduction_properties
                    ) = Reproduction._exit_ovsynch_program_early_when_first_preg_check_passed_or_estrus_detected(
                        general_properties, reproduction_properties, simulation_day
                    )
        elif "on_not_preg" in preg_check_config:  # Due to failed conception
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                preg_check_config["on_not_preg"],
            )
            reproduction_properties.abortion_day = general_properties.days_born
            general_properties, reproduction_properties, animal_statistics = Reproduction.open_cow(
                general_properties, reproduction_properties, animal_statistics, simulation_day
            )
        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def _terminate_pregnancy(general_properties: GeneralProperties,
                             reproduction_properties: ReproductionProperties,
                             animal_statistics: AnimalStatistics,
                             preg_loss_const: str,
                             simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties, AnimalStatistics]:
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
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            preg_loss_const,
        )
        reproduction_properties.abortion_day = general_properties.days_born
        general_properties.days_in_preg = 0
        if general_properties.animal_type == AnimalType.HEIFER_II:
            general_properties, reproduction_properties = Reproduction.open_heifer(
                general_properties, reproduction_properties, simulation_day
            )
        else:
            general_properties, reproduction_properties, animal_statistics = Reproduction.open_cow(
                general_properties, reproduction_properties, animal_statistics, simulation_day
            )
        general_properties.body_weight -= reproduction_properties.conceptus_weight
        reproduction_properties.conceptus_weight = 0
        reproduction_properties.calf_birth_weight = 0
        reproduction_properties.p_gest_for_calf = 0
        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def _calculate_conception_rate_on_ai_day(reproduction_properties: ReproductionProperties,) -> \
            ReproductionProperties:
        if AnimalConfig.should_decrease_conception_rate_in_rebreeding:
            reproduction_properties.conception_rate -= reproduction_properties.num_conception_rate_decreases * \
                                                       AnimalConfig.conception_rate_decrease

        if AnimalConfig.should_decrease_conception_rate_by_parity:
            reproduction_properties.conception_rate = Reproduction._decrease_conception_rate_by_parity(
                reproduction_properties.calves, reproduction_properties.conception_rate)

        reproduction_properties.conception_rate = max(0.0, reproduction_properties.conception_rate)
        return reproduction_properties

    @staticmethod
    def execute_cow_ed_protocol(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            animal_statistics: AnimalStatistics,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties, AnimalStatistics]:
        """
        Execute the estrus detection protocol. This method is used in the ED and ED-TAI protocols.

        Notes
        -----
        When the number of days in milk is less than the voluntary waiting period, the cow is in the fresh state.
        After the voluntary waiting period, depending on the current state of the cow, different actions are taken.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """

        if 1 <= general_properties.days_in_milk <= AnimalConfig.voluntary_waiting_period:
            general_properties, reproduction_properties = Reproduction._repeat_estrus_simulation_before_vwp(
                general_properties, reproduction_properties, simulation_day
            )

        elif general_properties.days_in_milk > AnimalConfig.voluntary_waiting_period:
            # For cows entering the herd but no estrus day has been set
            if (
                    reproduction_properties.repro_state_manager.is_in(ReproStateEnum.ENTER_HERD_FROM_INIT)
                    and general_properties.days_born > reproduction_properties.estrus_day
            ):
                general_properties, reproduction_properties = Reproduction._simulate_estrus(
                    general_properties,
                    reproduction_properties,
                    general_properties.days_born,
                    simulation_day,
                    animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
                    AnimalConfig.average_estrus_cycle_cow,
                    AnimalConfig.std_estrus_cycle_cow,
                )

            if reproduction_properties.repro_state_manager.is_in_any({ReproStateEnum.FRESH,
                                                                      ReproStateEnum.ENTER_HERD_FROM_INIT}):
                reproduction_properties.repro_state_manager.enter(ReproStateEnum.WAITING_FULL_ED_CYCLE)
                general_properties.events.add_event(
                    general_properties.days_born,
                    simulation_day,
                    f"Current repro state(s): {reproduction_properties.repro_state_manager}",
                )

            if general_properties.days_born == reproduction_properties.estrus_day:
                # Used in PGFatPD resynch program
                if reproduction_properties.repro_state_manager.is_in(ReproStateEnum.WAITING_SHORT_ED_CYCLE):
                    reproduction_properties.repro_state_manager.exit(ReproStateEnum.WAITING_SHORT_ED_CYCLE)
                    (
                        general_properties,
                        reproduction_properties,
                        animal_statistics
                    ) = Reproduction._handle_estrus_detection(
                        general_properties,
                        reproduction_properties,
                        animal_statistics,
                        simulation_day,
                        on_estrus_detected=Reproduction._setup_ai_day_after_estrus_detected,
                        on_estrus_not_detected=lambda general_properties, reproduction_properties, _:
                        reproduction_properties.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH),
                    )
                    if reproduction_properties.repro_state_manager.is_in(ReproStateEnum.IN_OVSYNCH):
                        general_properties.events.add_event(
                            general_properties.days_born,
                            simulation_day,
                            f"Current repro state(s): {reproduction_properties.repro_state_manager}",
                        )

                elif reproduction_properties.repro_state_manager.is_in(ReproStateEnum.WAITING_FULL_ED_CYCLE):
                    reproduction_properties.repro_state_manager.exit(ReproStateEnum.WAITING_FULL_ED_CYCLE)
                    (
                        general_properties,
                        reproduction_properties,
                        animal_statistics
                    ) = Reproduction._handle_estrus_detection(
                        general_properties,
                        reproduction_properties,
                        animal_statistics,
                        simulation_day,
                        on_estrus_detected=Reproduction._setup_ai_day_after_estrus_detected,
                        on_estrus_not_detected=Reproduction._simulate_full_estrus_cycle,
                    )

                # Used in the initial ED portion of the ED-TAI protocol
                elif reproduction_properties.repro_state_manager.is_in(
                        ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH):
                    reproduction_properties.repro_state_manager.exit(
                        ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH)
                    (
                        general_properties,
                        reproduction_properties,
                        animal_statistics
                    ) = Reproduction._handle_estrus_detection(
                        general_properties,
                        reproduction_properties,
                        animal_statistics,
                        simulation_day,
                        on_estrus_detected=Reproduction._setup_ai_day_after_estrus_detected,
                        on_estrus_not_detected=Reproduction._simulate_full_estrus_cycle_before_ovsynch,
                    )
        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def _repeat_estrus_simulation_before_vwp(general_properties: GeneralProperties,
                                             reproduction_properties: ReproductionProperties,
                                             simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties]:
        """
        Repeat the estrus simulation before the voluntary waiting period.

        Parameters
        ----------
        simulation_day : int
            The current simulation day.
        """

        if reproduction_properties.repro_state_manager.is_in_empty_state() or \
                reproduction_properties.repro_state_manager.is_in(ReproStateEnum.ENTER_HERD_FROM_INIT):
            reproduction_properties.repro_state_manager.enter(ReproStateEnum.FRESH)
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                f"Current repro state(s): {reproduction_properties.repro_state_manager}",
            )
        if general_properties.days_born == reproduction_properties.estrus_day:
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                animal_constants.ESTRUS_BEFORE_VOLUNTARY_WAITING_PERIOD_NOTE,
            )
            general_properties, reproduction_properties = Reproduction._simulate_estrus(
                general_properties,
                reproduction_properties,
                general_properties.days_born,
                simulation_day,
                animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
                AnimalConfig.average_estrus_cycle_cow,
                AnimalConfig.std_estrus_cycle_cow,
            )
        elif general_properties.days_born > reproduction_properties.estrus_day:
            general_properties, reproduction_properties = Reproduction._simulate_estrus(
                general_properties,
                reproduction_properties,
                general_properties.days_born,
                simulation_day,
                animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
                AnimalConfig.average_estrus_cycle_cow,
                AnimalConfig.std_estrus_cycle_cow,
            )
        return general_properties, reproduction_properties

    @staticmethod
    def _setup_ai_day_after_estrus_detected(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties]:
        """
        Handle the estrus detected event.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """
        if reproduction_properties.repro_state_manager.is_in(ReproStateEnum.IN_OVSYNCH):
            (
                general_properties,
                reproduction_properties
            ) = Reproduction._exit_ovsynch_program_early_when_first_preg_check_passed_or_estrus_detected(
                general_properties,
                reproduction_properties,
                simulation_day
            )

        reproduction_properties.repro_state_manager.enter(ReproStateEnum.ESTRUS_DETECTED)
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            f"Current repro state(s): {reproduction_properties.repro_state_manager}",
        )
        reproduction_properties.conception_rate = AnimalConfig.cow_estrus_conception_rate
        reproduction_properties.ai_day = general_properties.days_born + 1
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            f"{animal_constants.AI_DAY_SCHEDULED_NOTE} on day {reproduction_properties.ai_day}",
        )

        return general_properties, reproduction_properties

    @staticmethod
    def _simulate_full_estrus_cycle(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties]:
        """
        Handle the estrus not detected event.

        Parameters
        ----------
        simulation_day : int
            The current simulation day.
        """

        reproduction_properties.repro_state_manager.enter(ReproStateEnum.WAITING_FULL_ED_CYCLE, keep_existing=True)
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            f"Current repro state(s): {reproduction_properties.repro_state_manager}",
        )
        Reproduction._simulate_estrus(
            general_properties,
            reproduction_properties,
            general_properties.days_born,
            simulation_day,
            animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
            AnimalConfig.average_estrus_cycle_cow,
            AnimalConfig.std_estrus_cycle_cow,
        )
        return general_properties, reproduction_properties

    @staticmethod
    def _simulate_full_estrus_cycle_before_ovsynch(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties]:
        """
        Simulate another estrus cycle before the OvSynch program in the ED-TAI protocol.

        Notes
        -----
        This method is called when the estrus is not detected on an estrus day during the period
        between the voluntary waiting period and the start of the OvSynch program. It will schedule
        the next estrus day and if this day is beyond the OvSynch program start day, the estrus
        detection process will be canceled and the cow will enter the OvSynch program.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """

        reproduction_properties.repro_state_manager.enter(ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH)
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            f"Current repro state(s): {reproduction_properties.repro_state_manager}",
        )
        Reproduction._simulate_estrus(
            general_properties,
            reproduction_properties,
            general_properties.days_born,
            simulation_day,
            animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
            AnimalConfig.average_estrus_cycle_cow,
            AnimalConfig.std_estrus_cycle_cow,
        )
        return general_properties, reproduction_properties

    @staticmethod
    def _execute_cow_hormone_delivery_schedule(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            animal_statistics: AnimalStatistics,
            simulation_day: int,
            schedule: dict[int, dict]) -> tuple[GeneralProperties, ReproductionProperties, AnimalStatistics]:
        """
        Execute a hormone delivery schedule for cows.

        Notes
        -----
        This method overrides the similar method in the HeiferII class. In addition to the actions performed by the
        version in the HeiferII class, this method can also perform the following actions:
        - set the presynch end day
        - set the TAI start day
        - set the TAI end day

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.
        schedule : dict[int, dict]
            A dictionary of days and actions to perform on those days.
        """

        (
            general_properties, reproduction_properties, animal_statistics
        ) = Reproduction._execute_hormone_delivery_schedule(
            general_properties, reproduction_properties, animal_statistics, simulation_day, schedule
        )

        actions = schedule.get(general_properties.days_born)
        if actions is not None:
            if actions.get("set_presynch_end", False):
                general_properties.events.add_event(
                    general_properties.days_born,
                    simulation_day,
                    f"{animal_constants.PRESYNCH_PERIOD_END}: {AnimalConfig.cow_presynch_method}",
                )
                reproduction_properties.repro_state_manager.exit(ReproStateEnum.IN_PRESYNCH)
                reproduction_properties.repro_state_manager.enter(ReproStateEnum.HAS_DONE_PRESYNCH)
                del actions["set_presynch_end"]

            if actions.get("set_ovsynch_end", False):
                general_properties.events.add_event(
                    general_properties.days_born,
                    simulation_day,
                    f"{animal_constants.OVSYNCH_PERIOD_END_NOTE}: {AnimalConfig.cow_ovsynch_method}",
                )
                reproduction_properties.repro_state_manager.exit(ReproStateEnum.IN_OVSYNCH)
                del actions["set_ovsynch_end"]

            if not actions:
                del schedule[general_properties.days_born]
        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def execute_cow_tai_protocol(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            animal_statistics: AnimalStatistics,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties, AnimalStatistics]:
        """
        Execute the TAI protocol by setting up and executing hormone delivery schedules for
        the presynch and ovsynch programs.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """

        if AnimalConfig.cow_presynch_method == "None":
            if 1 <= general_properties.days_in_milk < AnimalConfig.ovsynch_program_start_day:
                general_properties, reproduction_properties = Reproduction._enter_fresh_state_if_in_empty_state(
                    general_properties, reproduction_properties, simulation_day
                )
            elif general_properties.days_in_milk >= AnimalConfig.ovsynch_program_start_day:
                general_properties, reproduction_properties = Reproduction._setup_ovsynch_on_ovsynch_start_day_if_valid(
                    general_properties, reproduction_properties, simulation_day)
            if reproduction_properties.hormone_schedule:
                (
                    general_properties,
                    reproduction_properties,
                    animal_statistics
                ) = Reproduction._execute_cow_hormone_delivery_schedule(
                    general_properties, reproduction_properties, animal_statistics, simulation_day,
                    reproduction_properties.hormone_schedule)
            return general_properties, reproduction_properties, animal_statistics

        if 1 <= general_properties.days_in_milk < AnimalConfig.presynch_program_start_day:
            general_properties, reproduction_properties = Reproduction._enter_fresh_state_if_in_empty_state(
                general_properties, reproduction_properties, simulation_day
            )
        elif general_properties.days_in_milk >= AnimalConfig.presynch_program_start_day:
            general_properties, reproduction_properties = Reproduction._setup_presynch_on_presynch_start_day_if_valid(
                general_properties, reproduction_properties, simulation_day
            )
            if reproduction_properties.hormone_schedule:
                (
                    general_properties,
                    reproduction_properties,
                    animal_statistics
                ) = Reproduction._execute_cow_hormone_delivery_schedule(
                    general_properties, reproduction_properties, animal_statistics, simulation_day,
                    reproduction_properties.hormone_schedule)
            general_properties, reproduction_properties = Reproduction._setup_ovsynch_on_ovsynch_start_day_if_valid(
                general_properties, reproduction_properties, simulation_day)
        if reproduction_properties.hormone_schedule:
            (
                general_properties,
                reproduction_properties,
                animal_statistics
            ) = Reproduction._execute_cow_hormone_delivery_schedule(
                general_properties, reproduction_properties, animal_statistics, simulation_day,
                reproduction_properties.hormone_schedule)

        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def _setup_presynch_on_presynch_start_day_if_valid(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties]:
        """
        Set up a presynch program on the presynch start day if it does not exist.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """
        (
            should_set_up_hormone_delivery_for_presynch,
            general_properties
        ) = Reproduction._should_set_up_hormone_delivery_for_presynch(
            general_properties, reproduction_properties, simulation_day)

        if should_set_up_hormone_delivery_for_presynch:
            Reproduction._set_up_hormone_schedule(general_properties, reproduction_properties,
                                                  general_properties.days_born)
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                f"{animal_constants.PRESYNCH_PERIOD_START}: {AnimalConfig.cow_presynch_method}",
            )
        return general_properties, reproduction_properties

    @staticmethod
    def _enter_fresh_state_if_in_empty_state(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties]:
        """
        Enter the fresh state if the cow is in no repro state initially.

        Parameters
        ----------
        simulation_day : int
            The current simulation day.
        """

        if reproduction_properties.repro_state_manager.is_in_empty_state() or \
                reproduction_properties.repro_state_manager.is_in(
            ReproStateEnum.ENTER_HERD_FROM_INIT
        ):
            reproduction_properties.repro_state_manager.enter(ReproStateEnum.FRESH)
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                f"Current repro state(s): {reproduction_properties.repro_state_manager}",
            )
        return general_properties, reproduction_properties

    @staticmethod
    def _setup_ovsynch_on_ovsynch_start_day_if_valid(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties]:
        """
        Set up an OvSynch program on the OvSynch start day if it does not exist.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """
        (
            should_set_up_hormone_delivery_for_ovsynch,
            general_properties
        ) = Reproduction._should_set_up_hormone_delivery_for_ovsynch(
            general_properties, reproduction_properties, simulation_day
        )

        if should_set_up_hormone_delivery_for_ovsynch:
            reproduction_properties = Reproduction._set_up_hormone_schedule(
                general_properties, reproduction_properties, general_properties.days_born)
            reproduction_properties.cow_TAI_conception_rate = AnimalConfig.ovsynch_program_conception_rate
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                f"{animal_constants.OVSYNCH_PERIOD_START_NOTE}: {AnimalConfig.cow_ovsynch_method}",
            )
        return general_properties, reproduction_properties

    @staticmethod
    def _should_set_up_hormone_delivery_for_presynch(general_properties: GeneralProperties,
                                                     reproduction_properties: ReproductionProperties,
                                                     simulation_day: int) -> tuple[bool, GeneralProperties]:
        """
        Check if the cow should set up hormone delivery for a presynch program.

        Returns
        -------
        bool
            True if the cow should set up hormone delivery for a presynch program, False otherwise.
        """

        if reproduction_properties.cow_reproduction_program != CowReproductionProtocol.TAI.value:
            return False, general_properties

        if AnimalConfig.cow_presynch_method not in [
            CowPreSynchSubProtocol.Presynch_PreSynch.value,
            CowPreSynchSubProtocol.Presynch_DoubleOvSynch.value,
            CowPreSynchSubProtocol.Presynch_G6G.value,
        ]:
            return False, general_properties

        if reproduction_properties.hormone_schedule:
            return False, general_properties

        if general_properties.days_in_milk == AnimalConfig.presynch_program_start_day and \
                reproduction_properties.repro_state_manager.is_in_any(
            {ReproStateEnum.FRESH, ReproStateEnum.ENTER_HERD_FROM_INIT}
        ):
            reproduction_properties.repro_state_manager.enter(ReproStateEnum.IN_PRESYNCH)
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                f"Current repro state(s): {reproduction_properties.repro_state_manager}",
            )
            return True, general_properties

        if general_properties.days_in_milk > AnimalConfig.presynch_program_start_day and \
                reproduction_properties.repro_state_manager.is_in(
            ReproStateEnum.ENTER_HERD_FROM_INIT
        ):
            reproduction_properties.repro_state_manager.enter(ReproStateEnum.IN_PRESYNCH)
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                f"Current repro state(s): {reproduction_properties.repro_state_manager}",
            )
            return True, general_properties

        return reproduction_properties.repro_state_manager.is_in(ReproStateEnum.IN_PRESYNCH), general_properties

    @staticmethod
    def _should_set_up_hormone_delivery_for_ovsynch(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            simulation_day: int) -> tuple[bool, GeneralProperties]:
        """
        Check if the cow should set up hormone delivery for timed artificial insemination.

        Notes
        -----
        If the number of days in milk is equal to the OvSynch program start day and the cow is in
        the fresh state or has just gone through a presynch program, then the cow should be scheduled
        for an OvSynch program.

        If the OvSynch program start day happens before the last day of the presynch program, then
        the start day of the OvSynch program will be adjusted to be the last day of the presynch program.
        In other words, if both presynch and OvSynch programs are scheduled, then their schedules
        cannot be overlapped.

        Returns
        -------
        bool
            True if the cow should set up a hormone delivery schedule for an OvSynch program, False otherwise.
        """

        if reproduction_properties.hormone_schedule:
            return False, general_properties

        if AnimalConfig.cow_ovsynch_method not in [
            CowTAISubProtocol.TAI_OvSynch_48.value,
            CowTAISubProtocol.TAI_OvSynch_56.value,
            CowTAISubProtocol.TAI_CoSynch_72.value,
            CowTAISubProtocol.TAI_5d_CoSynch.value,
        ]:
            return False, general_properties

        if reproduction_properties.repro_state_manager.is_in(ReproStateEnum.IN_PRESYNCH):
            return False, general_properties

        if general_properties.days_in_milk == AnimalConfig.ovsynch_program_start_day:
            if reproduction_properties.repro_state_manager.is_in_empty_state() or \
                    reproduction_properties.repro_state_manager.is_in_any(
                {
                    ReproStateEnum.ENTER_HERD_FROM_INIT,
                    ReproStateEnum.FRESH,
                    ReproStateEnum.HAS_DONE_PRESYNCH,
                }
            ):
                reproduction_properties.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
                general_properties.events.add_event(
                    general_properties.days_born,
                    simulation_day,
                    f"Current repro state(s): {reproduction_properties.repro_state_manager}",
                )
                return True, general_properties

        if general_properties.days_in_milk > AnimalConfig.ovsynch_program_start_day:
            if reproduction_properties.repro_state_manager.is_in_any(
                {ReproStateEnum.HAS_DONE_PRESYNCH, ReproStateEnum.ENTER_HERD_FROM_INIT}
            ):
                reproduction_properties.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
                general_properties.events.add_event(
                    general_properties.days_born,
                    simulation_day,
                    f"Current repro state(s): {reproduction_properties.repro_state_manager}",
                )
                return True, general_properties

        return reproduction_properties.repro_state_manager.is_in(ReproStateEnum.IN_OVSYNCH), general_properties

    @staticmethod
    def _increment_cow_ai_counts(animal_statistics: AnimalStatistics) -> AnimalStatistics:
        """
        Increment the performed AI counts across all cows.
        """

        animal_statistics.num_ai_performed += 1
        return animal_statistics

    @staticmethod
    def _increment_successful_cow_conceptions(animal_statistics: AnimalStatistics) -> AnimalStatistics:
        """
        Increment the successful conception counts across all heifers.
        """

        animal_statistics.num_successful_conceptions += 1
        return animal_statistics

    @staticmethod
    def execute_cow_ed_tai_protocol(general_properties: GeneralProperties,
                                    reproduction_properties: ReproductionProperties,
                                    simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties]:
        """
        Execute the ED-TAI protocol by checking the days in milk and taking the appropriate actions.

        Notes
        -----
        The following actions are taken:
        - If the days in milk is between 1 and the program start day, no actions will be taken.

        - If the days in milk is between the program start day and the TAI program start day, the cow
        will be monitored for estrus daily during this period.

        - If the days in milk is greater than or equal to the TAI program start day, the cow will be
        scheduled for a TAI program if estrus has not been detected before the TAI start day.

        Parameters
        ----------
        simulation_day : int
            The current simulation day.
        """

        if 1 <= general_properties.days_in_milk <= AnimalConfig.voluntary_waiting_period:
            general_properties, reproduction_properties = Reproduction._repeat_estrus_simulation_before_vwp(
                general_properties, reproduction_properties, simulation_day
            )

        elif AnimalConfig.voluntary_waiting_period < general_properties.days_in_milk < \
                AnimalConfig.ovsynch_program_start_day:
            if (
                reproduction_properties.repro_state_manager.is_in(ReproStateEnum.ENTER_HERD_FROM_INIT)
                and general_properties.days_born > reproduction_properties.estrus_day
            ):
                general_properties, reproduction_properties = Reproduction._simulate_estrus(
                    general_properties,
                    reproduction_properties,
                    general_properties.days_born,
                    simulation_day,
                    animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
                    AnimalConfig.average_estrus_cycle_cow,
                    AnimalConfig.std_estrus_cycle_cow,
                )

            if reproduction_properties.repro_state_manager.is_in_any({ReproStateEnum.FRESH,
                                                                      ReproStateEnum.ENTER_HERD_FROM_INIT}):
                reproduction_properties.repro_state_manager.enter(ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH)
                general_properties.events.add_event(
                    general_properties.days_born,
                    simulation_day,
                    f"Current repro state(s): {reproduction_properties.repro_state_manager}",
                )

        elif general_properties.days_in_milk >= AnimalConfig.ovsynch_program_start_day:
            (
                general_properties,
                reproduction_properties
            ) = Reproduction._handle_estrus_not_detected_before_ovsynch_start_day(
                general_properties, reproduction_properties, simulation_day)

        return general_properties, reproduction_properties

    @staticmethod
    def _handle_estrus_not_detected_before_ovsynch_start_day(general_properties: GeneralProperties,
                                                             reproduction_properties: ReproductionProperties,
                                                             simulation_day: int) -> tuple[
        GeneralProperties, ReproductionProperties
    ]:
        """
        Redirect the cow to enter an OvSynch program when estrus has not been detected between the
        voluntary waiting period and the OvSynch program start day.

        Parameters
        ----------
        simulation_day : int
            The current simulation day.
        """

        if reproduction_properties.repro_state_manager.is_in(ReproStateEnum.ENTER_HERD_FROM_INIT):
            reproduction_properties.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                f"Current repro state(s): {reproduction_properties.repro_state_manager}",
            )

        elif reproduction_properties.repro_state_manager.is_in(ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH):
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                animal_constants.ESTRUS_NOT_DETECTED_BETWEEN_VWP_AND_OVSYNCH_START_DAY_NOTE,
            )
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                animal_constants.CANCEL_ESTRUS_DETECTION_NOTE
            )
            reproduction_properties.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                f"Current repro state(s): {reproduction_properties.repro_state_manager}",
            )

        elif reproduction_properties.repro_state_manager.is_in(ReproStateEnum.FRESH):  # When no ED is instituted
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                animal_constants.NO_ED_INSTITUTED_BEFORE_OVSYNCH_IN_ED_TAI_NOTE,
            )
            reproduction_properties.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                f"Current repro state(s): {reproduction_properties.repro_state_manager}",
            )
        return general_properties, reproduction_properties

    @staticmethod
    def _decrease_conception_rate_by_parity(calves: int, conception_rate: float) -> float:
        """
        Adjust conception rate based on the parity of the cow.

        Parameters
        ----------
        calves : int
            The number of calves the cow has had.
        conception_rate : float
            The conception rate to adjust.

        Returns
        -------
        float
            The adjusted conception rate.
        """

        if calves <= 1:
            return conception_rate
        elif calves == 2:
            return conception_rate - 0.05
        else:
            return conception_rate - 0.1

    @staticmethod
    def _handle_successful_cow_conception(general_properties: GeneralProperties,
                                          reproduction_properties: ReproductionProperties,
                                          simulation_day: int) -> tuple[
        GeneralProperties, ReproductionProperties
    ]:
        """
        Set the gestation length, calf birth weight, and calving to pregnancy time and
        schedule a TAI program in advance if the resynch protocol is TAIbeforePD.

        Notes
        -----
        When a successful conception occurs, the following variables are set:
        - days_in_preg: Initialized to 1.
        - gestation_length: Calculated using the '_calculate_gestation_length' method.
        - calf_birth_weight: Calculated using the '_calculate_calf_birth_weight' method.
        - calving_to_preg_time: Calculated as the difference between the current simulation day and the
            most recent birth event.
        - If the resynch protocol is TAIbeforePD, an OvSynch program will be scheduled in advance.

        Parameters
        ----------
        sim_day : int
            The current simulation day.
        """
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            f"{animal_constants.SUCCESSFUL_CONCEPTION}, "
            f"with conception rate at {reproduction_properties.conception_rate}",
        )
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            animal_constants.COW_PREG,
        )

        general_properties.days_in_preg = 1
        reproduction_properties.repro_state_manager.enter(ReproStateEnum.PREGNANT)
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            f"Current repro state(s): {reproduction_properties.repro_state_manager}",
        )

        reproduction_properties.gestation_length = Reproduction._calculate_gestation_length()
        reproduction_properties.calf_birth_weight = Reproduction._calculate_calf_birth_weight(
            general_properties.breed.value)

        if reproduction_properties.calves > 0:
            last_time_given_birth = general_properties.events.get_most_recent_date(animal_constants.NEW_BIRTH)
            reproduction_properties.calving_to_preg_time = general_properties.days_born - last_time_given_birth

        if reproduction_properties.cow_reproduction_program in [
            CowReproductionProtocol.TAI.value,
            CowReproductionProtocol.ED_TAI.value,
        ]:
            if AnimalConfig.cow_resynch_method == CowReSynchSubProtocol.Resynch_TAIbeforePD.value:
                general_properties, reproduction_properties = Reproduction._schedule_ovsynch_program_in_advance(
                    general_properties, reproduction_properties, simulation_day
                )
                reproduction_properties.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH, keep_existing=True)
                general_properties.events.add_event(
                    general_properties.days_born,
                    simulation_day,
                    f"Current repro state(s): {reproduction_properties.repro_state_manager}",
                )
        return general_properties, reproduction_properties

    @staticmethod
    def _handle_failed_cow_conception(general_properties: GeneralProperties,
                                      reproduction_properties: ReproductionProperties,
                                      simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties]:
        """
        Manage different scenarios that the cow's repro states can be in when a failed conception occurs.

        Notes
        -----
        If the repro program is ED or ED-TAI, after a failed conception, the cow will be
        scheduled for a full estrus cycle.
        If the repro program is TAI and the resynch protocol is TAIbeforePD, the cow will be
        scheduled for an OvSynch program in advance.
        If the repro program is ED-TAI and the resynch protocol is TAIAfterPD, the cow will also
        be scheduled for an OvSynch program in advance, while monitoring for estrus at the same time.

        Parameters
        ----------
        simulation_day : int
            The current simulation day.
        """
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            f"{animal_constants.FAILED_CONCEPTION}, " f"with conception rate at "
            f"{reproduction_properties.conception_rate}",
        )
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            animal_constants.COW_NOT_PREG,
        )

        if reproduction_properties.cow_reproduction_program in [
            CowReproductionProtocol.ED.value,
            CowReproductionProtocol.ED_TAI.value,
        ]:
            reproduction_properties.repro_state_manager.enter(ReproStateEnum.WAITING_FULL_ED_CYCLE)
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                f"Current repro state(s): {reproduction_properties.repro_state_manager}",
            )
            general_properties, reproduction_properties = Reproduction._simulate_estrus(
                general_properties,
                reproduction_properties,
                general_properties.days_born,
                simulation_day,
                animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
                AnimalConfig.average_estrus_cycle_cow,
                AnimalConfig.std_estrus_cycle_cow,
            )

        if reproduction_properties.cow_reproduction_program in [
            CowReproductionProtocol.TAI.value,
            CowReproductionProtocol.ED_TAI.value,
        ]:
            if AnimalConfig.cow_resynch_method == CowReSynchSubProtocol.Resynch_TAIbeforePD.value:
                general_properties, reproduction_properties = Reproduction._schedule_ovsynch_program_in_advance(
                    general_properties,
                    reproduction_properties,
                    simulation_day,
                )

                if reproduction_properties.cow_reproduction_program == CowReproductionProtocol.ED_TAI:
                    # We want to keep the ED protocol running at the same time as the OvSynch program.
                    reproduction_properties.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH, keep_existing=True)
                    general_properties.events.add_event(
                        general_properties.days_born,
                        simulation_day,
                        f"Current repro state(s): {reproduction_properties.repro_state_manager}",
                    )
                elif reproduction_properties.cow_reproduction_program == CowReproductionProtocol.TAI:
                    reproduction_properties.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
                    general_properties.events.add_event(
                        general_properties.days_born,
                        simulation_day,
                        f"Current repro state(s): {reproduction_properties.repro_state_manager}",
                    )
        return general_properties, reproduction_properties

    @staticmethod
    def cow_pregnancy_update(general_properties: GeneralProperties,
                             reproduction_properties: ReproductionProperties,
                             animal_statistics: AnimalStatistics,
                             simulation_day: int) -> tuple[
        GeneralProperties, ReproductionProperties, AnimalStatistics
    ]:
        """
        Perform a pregnancy check if the current day is a designated pregnancy check day.

        Notes
        -----
        The method uses a list of dictionaries, each representing a specific pregnancy check configuration.
        The method iterates through each configuration, checking if the current simulation day
        matches a scheduled pregnancy check day. If so, it calls the '_handle_preg_check' method
        with the specific configuration and the current simulation day.

        Parameters
        ----------
        sim_day : int
            The current day of the simulation.
        """

        if general_properties.is_pregnant:
            general_properties.days_in_preg += 1

        preg_check_configs: list[PregCheckConfig] = [
            {
                "day": AnimalConfig.first_pregnancy_check_day,
                "loss_rate": AnimalConfig.first_pregnancy_check_loss_rate,
                "on_preg_loss": animal_constants.PREG_LOSS_BEFORE_1,
                "on_preg": animal_constants.PREG_CHECK_1_PREG,
                "on_not_preg": animal_constants.PREG_CHECK_1_NOT_PREG,
            },
            {
                "day": AnimalConfig.second_pregnancy_check_day,
                "loss_rate": AnimalConfig.second_pregnancy_check_loss_rate,
                "on_preg_loss": animal_constants.PREG_LOSS_BTWN_1_AND_2,
                "on_preg": animal_constants.PREG_CHECK_2_PREG,
            },
            {
                "day": AnimalConfig.third_pregnancy_check_day,
                "loss_rate": AnimalConfig.third_pregnancy_check_loss_rate,
                "on_preg_loss": animal_constants.PREG_LOSS_BTWN_2_AND_3,
                "on_preg": animal_constants.PREG_CHECK_3_PREG,
            },
        ]

        for preg_check_config in preg_check_configs:
            if general_properties.days_born == reproduction_properties.ai_day + preg_check_config["day"]:
                (general_properties,
                    reproduction_properties,
                    animal_statistics
                 ) = Reproduction._handle_cow_pregnancy_check(
                    general_properties,
                    reproduction_properties,
                    animal_statistics,
                    preg_check_config,
                    simulation_day)

        return general_properties, reproduction_properties, animal_statistics

    def _check_do_not_breed_flag(self, sim_day: int) -> None:
        """
        Check if the cow should still be in the breeding stage and mark her as do-not-breed if necessary.

        Notes
        -----
        If the cow still cannot get pregnant after the do-not-breed time has passed, she will be
        marked as do-not-breed.

        Important caveat: If even a cow is already pregnant, we cannot mark her as do-not-breed
        yet because she may still lose the pregnancy.

        Parameters
        ----------
        sim_day : int
            The current day of the simulation.
        """

        if not self.is_pregnant and self.days_in_milk > self.get_do_not_breed_time():
            if not self.do_not_breed:
                self.log_event(
                    self.days_born,
                    sim_day,
                    f"{const.DO_NOT_BREED}, days in milk: {self.days_in_milk}, not pregnant",
                )
                self.do_not_breed = True

    @staticmethod
    def open_cow(general_properties: GeneralProperties,
                 reproduction_properties: ReproductionProperties,
                 animal_statistics: AnimalStatistics,
                 simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties, AnimalStatistics]:
        """
        Manage and set up the different states an open cow can be in during rebreeding depending on
        the current repro protocol and the resynch program.

        Notes
        -----
        If the current protocol is ED, this method will simulate another full estrus cycle.
        In the TAI and ED-TAI protocols, if the resynch method is TAIafterPD, the cow will
        go through an OvSynch program next. If the resynch method is TAIbeforePD, the cow will
        essentially go through an OvSynch program also but with some extra considerations for her
        current state in the estrus detection process. If the resynch method is PGFatPD,
        the cow will get a PGF injection, then go through a short estrus cycle, and may need to go
        through an OvSynch program next.

        Parameters
        ----------
        sim_day : int
            The current day of the entire simulation.
        """

        reproduction_properties.num_conception_rate_decreases += 1

        if reproduction_properties.cow_reproduction_program == CowReproductionProtocol.ED:
            if general_properties.days_born > reproduction_properties.estrus_day:  # No estrus day scheduled yet
                reproduction_properties.repro_state_manager.enter(ReproStateEnum.WAITING_FULL_ED_CYCLE)
                general_properties.events.add_event(
                    general_properties.days_born,
                    simulation_day,
                    f"Current repro state(s): {reproduction_properties.repro_state_manager}",
                )
                general_properties.events.add_event(
                    general_properties.days_born,
                    simulation_day,
                    f"days in milk: {general_properties.days_in_milk}",
                )
                general_properties, reproduction_properties = Reproduction._simulate_estrus(
                    general_properties,
                    reproduction_properties,
                    general_properties.days_born,
                    simulation_day,
                    animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
                    AnimalConfig.average_estrus_cycle_cow,
                    AnimalConfig.std_estrus_cycle_cow,
                )
            return general_properties, reproduction_properties, animal_statistics

        # For both TAI and ED-TAI protocols
        if AnimalConfig.cow_resynch_method == CowReSynchSubProtocol.Resynch_TAIafterPD:
            reproduction_properties.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                f"Current repro state(s): {reproduction_properties.repro_state_manager}",
            )

        elif AnimalConfig.cow_resynch_method == CowReSynchSubProtocol.Resynch_TAIbeforePD:
            general_properties, reproduction_properties = Reproduction._handle_open_cow_in_tai_before_pd_resynch(
                general_properties, reproduction_properties, simulation_day
            )

        elif AnimalConfig.cow_resynch_method == CowReSynchSubProtocol.Resynch_PGFatPD:
            (
                general_properties,
                reproduction_properties,
            animal_statistics
            ) = Reproduction._handle_open_cow_in_pgf_at_pd_resynch(
                general_properties, reproduction_properties, animal_statistics, simulation_day
            )

        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def _handle_open_cow_in_pgf_at_pd_resynch(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            animal_statistics: AnimalStatistics,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties, AnimalStatistics]:
        """
        Perform a PGF injection for an open cow in the PGFatPD resynch protocol and simulate a short estrus cycle.

        Notes
        -----
        For simplicity, an open cow in the PGFatPD resynch protocol will get a PGF injection if any of
        the three pregnancy checks fails, without distinguishing between the first and the other two
        pregnancy checks. How the short estrus cycle following the PGF injection is handled is specified
        in the execute_ed_protocol() method. Basically, if estrus is detected, an AI will be performed
        on the next day. If estrus is not detected, a TAI program will be initiated.

        Parameters
        ----------
        simulation_day : int
            The current day of the simulation.
        """

        single_pgf_injection_schedule = {general_properties.days_born: {"deliver_hormones": ["PGF"]}}
        (
            general_properties,
            reproduction_properties,
            animal_statistics
        ) = Reproduction._execute_cow_hormone_delivery_schedule(
            general_properties,
            reproduction_properties,
            animal_statistics,
            simulation_day,
            single_pgf_injection_schedule
        )
        reproduction_properties.repro_state_manager.enter(ReproStateEnum.WAITING_SHORT_ED_CYCLE)
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            f"Current repro state(s): {reproduction_properties.repro_state_manager}",
        )
        general_properties, reproduction_properties = Reproduction._simulate_estrus(
            general_properties,
            reproduction_properties,
            general_properties.days_born,
            simulation_day,
            animal_constants.SIMULATE_ESTRUS_AFTER_PGF_NOTE,
            AnimalConfig.average_estrus_cycle_after_pgf,
            AnimalConfig.std_estrus_cycle_after_pgf,
            max_cycle_length=animal_constants.MAX_ESTRUS_CYCLE_LENGTH_PGF_AT_PREG_CHECK,
        )

        return general_properties, reproduction_properties, animal_statistics

    @staticmethod
    def _handle_open_cow_in_tai_before_pd_resynch(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties]:
        """
        Redirect an open cow in the TAIbeforePD resynch protocol to an OvSynch program after the second or third
        pregnancy check failed and stop any pre-existing estrus detection.

        Notes
        -----
        When the user selects the TAIbeforePD resynch protocol, an OvSynch program will have already been initiated
        prior to the first pregnancy check regardless of the outcome of conception result after performing an AI.
        If the first pregnancy check fails, that OvSynch program set up in advance will be continued.
        On the other hand, if the second or third pregnancy check fails, there was no OvSynch program
        set up in advance, so this method will redirect the cow into an OvSynch program.

        After an AI, a cow in the TAIbeforePD resynch protocol will also be waiting for estrus
        to occur. This method will stop such estrus monitoring if it is still ongoing
        because the cow has already reached the first pregnancy check day.

        Parameters
        ----------
        sim_day : int
            The current day of the simulation.
        """

        if reproduction_properties.repro_state_manager.is_in_empty_state():
            reproduction_properties.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                f"Current repro state(s): {reproduction_properties.repro_state_manager}",
            )

        if reproduction_properties.repro_state_manager.is_in(ReproStateEnum.WAITING_FULL_ED_CYCLE):
            reproduction_properties.repro_state_manager.exit(ReproStateEnum.WAITING_FULL_ED_CYCLE)
            general_properties.events.add_event(
                general_properties.days_born,
                simulation_day,
                animal_constants.CANCEL_ESTRUS_DETECTION_NOTE,
            )

        return general_properties, reproduction_properties

    @staticmethod
    def _schedule_ovsynch_program_in_advance(
        general_properties: GeneralProperties,
        reproduction_properties: ReproductionProperties,
        simulation_day: int,
        days_before_first_preg_check: int = animal_constants.DAYS_BEFORE_FIRST_PREG_CHECK_TO_START_TAI,
    ) -> tuple[GeneralProperties, ReproductionProperties]:
        """
        Schedule an OvSynch program in advance for the TAIbeforePD resynch protocol after performing an AI.

        Parameters
        ----------
        simulation_day : int
            The current day of the entire simulation.
        days_before_first_preg_check : int, optional, default=const.DAYS_BEFORE_FIRST_PREG_CHECK_TO_START_TAI
            The number of days before the first pregnancy check to schedule the OvSynch program.
        """

        hormone_schedule_start_day = general_properties.days_born + AnimalConfig.first_pregnancy_check_day - \
                                     days_before_first_preg_check
        reproduction_properties = Reproduction._set_up_hormone_schedule(
            general_properties, reproduction_properties, hormone_schedule_start_day)
        reproduction_properties.TAI_conception_rate = AnimalConfig.ovsynch_program_conception_rate
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            f"{animal_constants.SETTING_UP_OVSYNCH_PROGRAM_IN_ADVANCE_NOTE}: {AnimalConfig.cow_ovsynch_method}",
        )

        return general_properties, reproduction_properties

    @staticmethod
    def _exit_ovsynch_program_early_when_first_preg_check_passed_or_estrus_detected(
            general_properties: GeneralProperties,
            reproduction_properties: ReproductionProperties,
            simulation_day: int) -> tuple[GeneralProperties, ReproductionProperties]:
        """
        Exit the scheduled OvSynch program early in TAIbeforePD resynch protocol when
        the first pregnancy check is successful or estrus has been detected.

        Notes
        -----
        When the user selects the TAIbeforePD resynch protocol, an OvSynch program will be initiated prior to the first
        pregnancy check regardless of the outcome of conception result after performing an AI.
        If the first pregnancy check is successful or estrus has been detected before the first pregnancy check,
        the ongoing OvSynch program should be discontinued.

        Parameters
        ----------
        sim_day : int
            The current day of the simulation.
        """

        reproduction_properties.repro_state_manager.exit(ReproStateEnum.IN_OVSYNCH)
        reproduction_properties.hormone_schedule = {}
        general_properties.events.add_event(
            general_properties.days_born,
            simulation_day,
            f"{animal_constants.DISCONTINUE_OVSYNCH_PROGRAM_IN_TAI_BEFORE_PD_NOTE}:"
            f" {AnimalConfig.cow_ovsynch_method}",
        )
        return general_properties, reproduction_properties
