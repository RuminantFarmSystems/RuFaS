import math
import random
from math import floor
from typing import Callable, Union, Any, Optional

from scipy.stats import truncnorm

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_genetics.animal_genetics import AnimalGenetics
from RUFAS.biophysical.animal.data_types.animal_enums import Breed
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import NewBornCalfValuesTypedDict
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.preg_check_config import PregnancyCheckConfig
from RUFAS.biophysical.animal.data_types.repro_protocol_enums import (
    HeiferReproductionProtocol,
    CowReproductionProtocol,
    ReproStateEnum,
    CowTAISubProtocol,
    CowPreSynchSubProtocol,
    CowReSynchSubProtocol,
    HeiferTAISubProtocol,
    HeiferSynchEDSubProtocol,
)
from RUFAS.biophysical.animal.data_types.reproduction import (
    ReproductionOutputs,
    ReproductionInputs,
    ReproductionDataStream,
    AnimalReproductionStatistics,
    HerdReproductionStatistics,
)

from RUFAS.biophysical.animal.reproduction.hormone_delivery_schedule import HormoneDeliverySchedule
from RUFAS.biophysical.animal.reproduction.repro_protocol_misc import InternalReproSettings
from RUFAS.biophysical.animal.reproduction.repro_state_manager import ReproStateManager
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.rufas_time import RufasTime
from RUFAS.util import Utility

HEIFER_REPRODUCTION_SUB_PROTOCOLS = Union[HeiferTAISubProtocol, HeiferSynchEDSubProtocol]
COW_REPRODUCTION_SUB_PROTOCOLS = Union[CowPreSynchSubProtocol, CowTAISubProtocol, CowReSynchSubProtocol]


class Reproduction:
    """
    Manages the reproduction protocol for heifers and cows, including artificial insemination (AI), hormone
    delivery, pregnancy checks, estrus detection, and pregnancy management.

    Parameters
    ----------
    heifer_reproduction_program : HeiferReproductionProtocol, optional
        The reproduction program for heifers, by default None.
    heifer_reproduction_sub_program : HEIFER_REPRODUCTION_SUB_PROTOCOLS, optional
        The sub-program for heifer reproduction, by default None.
    cow_reproduction_program : CowReproductionProtocol, optional
        The reproduction program for cows, by default None.
    ai_day : int, optional
        The day of artificial insemination, by default 0.
    estrus_day : int, optional
        The day estrus is expected, by default 0.
    abortion_day : int, optional
        The day of abortion, by default 0.
    breeding_to_preg_time : int, optional
        Time taken from breeding to pregnancy, by default 0.
    conception_rate : float, optional
        Conception rate of the animal, by default 0.0.
    TAI_conception_rate : float, optional
        Timed artificial insemination (TAI) conception rate, by default 0.0.
        We will only initialize the TAI conception rate for cows if this value is passed in as an input.
        The TAI conception rate for heifers will be dynamically determined later on.
    num_conception_rate_decreases : int, optional
        Number of times the conception rate decreases, by default 0.
    hormone_schedule : dict[int, dict[str, Any]], optional
        The hormone schedule for the reproduction protocol, by default None.
    gestation_length : int, optional
        Length of the gestation period, by default 0.
    conceptus_weight : float, optional
        Weight of the conceptus, by default 0.0.
    calf_birth_weight : float, optional
        Birth weight of the calf, by default 0.0.
    calves : int, optional
        Number of calves, by default 0.
    calving_interval : int, optional
        Interval between calvings, by default 0.
    calving_interval_history : list[int], optional
        History of calving intervals, by default None.
    body_weight_at_calving : float, optional
        Body weight of the animal at calving, by default 0.0.
    do_not_breed : bool, optional
        Flag indicating if the animal should not breed, by default False.

    Notes
    -----
    This class mutates a ReproductionDataStream object during the update process, relying on the side effect. This
    could lead to potential unexpected behaviors.
    """

    def __init__(
        self,
        heifer_reproduction_program: Optional[HeiferReproductionProtocol] = None,
        heifer_reproduction_sub_program: Optional[HEIFER_REPRODUCTION_SUB_PROTOCOLS] = None,
        cow_reproduction_program: Optional[CowReproductionProtocol] = None,
        cow_presynch_program: Optional[CowPreSynchSubProtocol] = None,
        cow_ovsynch_program: Optional[CowTAISubProtocol] = None,
        cow_resynch_program: Optional[CowReSynchSubProtocol] = None,
        ai_day: int = 0,
        estrus_day: int = 0,
        abortion_day: int = 0,
        breeding_to_preg_time: int = 0,
        conception_rate: float = 0.0,
        cow_TAI_conception_rate: float = 0.0,
        num_conception_rate_decreases: int = 0,
        hormone_schedule: Optional[dict[int, dict[str, Any]]] = None,
        gestation_length: int = 0,
        conceptus_weight: float = 0.0,
        calf_birth_weight: float = 0.0,
        calves: int = 0,
        calving_interval: int = AnimalConfig.calving_interval,
        calving_interval_history: Optional[list[int]] = None,
        body_weight_at_calving: float = 0.0,
        do_not_breed: bool = False,
        estrus_count: int = 0,
    ) -> None:
        self.heifer_reproduction_program = heifer_reproduction_program or AnimalConfig.heifer_reproduction_program
        self.heifer_reproduction_sub_program = (
            heifer_reproduction_sub_program or AnimalConfig.heifer_reproduction_sub_program
        )
        self.cow_reproduction_program = cow_reproduction_program or AnimalConfig.cow_reproduction_program
        self.cow_presynch_program = cow_presynch_program or AnimalConfig.cow_presynch_method
        self.cow_ovsynch_program = cow_ovsynch_program or AnimalConfig.cow_tai_method
        self.cow_resynch_program = cow_resynch_program or AnimalConfig.cow_resynch_method

        self.ai_day = ai_day
        self.estrus_day = estrus_day
        self.abortion_day = abortion_day
        self.breeding_to_preg_time = breeding_to_preg_time
        self.gestation_length = gestation_length

        self.conceptus_weight = conceptus_weight
        self.calf_birth_weight = calf_birth_weight
        self.body_weight_at_calving = body_weight_at_calving

        self.conception_rate = conception_rate
        self.TAI_conception_rate = cow_TAI_conception_rate
        self.num_conception_rate_decreases = num_conception_rate_decreases

        self.calves = calves
        self.calving_interval = calving_interval if calving_interval > 0 else AnimalConfig.calving_interval

        self.calving_interval_history = calving_interval_history or []

        self.hormone_schedule = hormone_schedule or {}
        self.do_not_breed = do_not_breed

        self.repro_state_manager = ReproStateManager()

        self.reproduction_statistics = AnimalReproductionStatistics(estrus_count=estrus_count)

    def reproduction_update(self, reproduction_inputs: ReproductionInputs, time: RufasTime) -> ReproductionOutputs:
        """
        Update the reproduction status of the animal.

        Parameters
        ----------
        reproduction_inputs : ReproductionInputs
            The inputs for the reproduction protocol.
        time : RufasTime
            The current time in the simulation.

        Returns
        -------
        ReproductionOutputs
            Updated reproduction outputs for the animal.
        """
        reproduction_data_stream = ReproductionDataStream(
            animal_type=reproduction_inputs.animal_type,
            body_weight=reproduction_inputs.body_weight,
            breed=reproduction_inputs.breed,
            days_born=reproduction_inputs.days_born,
            days_in_pregnancy=reproduction_inputs.days_in_pregnancy,
            days_in_milk=reproduction_inputs.days_in_milk,
            events=AnimalEvents(),
            net_merit=reproduction_inputs.net_merit,
            phosphorus_for_gestation_required_for_calf=reproduction_inputs.phosphorus_for_gestation_required_for_calf,
            herd_reproduction_statistics=HerdReproductionStatistics(),
            newborn_calf_config=None,
        )
        self.reproduction_statistics.reset_daily_statistics()

        if reproduction_data_stream.animal_type == AnimalType.HEIFER_II:
            reproduction_data_stream = self.heiferII_reproduction_update(reproduction_data_stream, time)
        elif reproduction_data_stream.animal_type.is_cow:
            reproduction_data_stream = self.cow_reproduction_update(reproduction_data_stream, time)
        else:
            raise TypeError(f"Unknown animal type: {reproduction_data_stream.animal_type}")

        return ReproductionOutputs(
            body_weight=reproduction_data_stream.body_weight,
            days_in_milk=reproduction_data_stream.days_in_milk,
            days_in_pregnancy=reproduction_data_stream.days_in_pregnancy,
            events=reproduction_data_stream.events,
            phosphorus_for_gestation_required_for_calf=(
                reproduction_data_stream.phosphorus_for_gestation_required_for_calf
            ),
            herd_reproduction_statistics=reproduction_data_stream.herd_reproduction_statistics,
            newborn_calf_config=reproduction_data_stream.newborn_calf_config,
        )

    def heiferII_reproduction_update(
        self, reproduction_data_stream: ReproductionDataStream, time: RufasTime
    ) -> ReproductionDataStream:
        """
        Update reproduction status for heiferII based on the protocol.

        Parameters
        ----------
        reproduction_data_stream : ReproductionDataStream
            Current reproduction datastream.
        time : RufasTime
            The current time in the simulation.

        Returns
        -------
        ReproductionDataStream
            Updated reproduction datastream for the heifer.
        """
        if (
            self.heifer_reproduction_program != AnimalConfig.heifer_reproduction_program
            and reproduction_data_stream.days_born <= AnimalConfig.heifer_breed_start_day
        ):
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                time.simulation_day,
                f"{animal_constants.SETTING_REPRO_PROGRAM_NOTE} from "
                f"{self.heifer_reproduction_program} "
                f"to {AnimalConfig.heifer_reproduction_program}",
            )
            self.heifer_reproduction_program = AnimalConfig.heifer_reproduction_program

        if reproduction_data_stream.days_born >= AnimalConfig.heifer_breed_start_day:
            reproduction_data_stream = self._execute_heifer_reproduction_protocol(
                reproduction_data_stream, time.simulation_day
            )

            if reproduction_data_stream.days_born == self.ai_day:
                reproduction_data_stream = self._perform_ai(reproduction_data_stream, time.simulation_day)
            elif reproduction_data_stream.is_pregnant:
                reproduction_data_stream.days_in_pregnancy += 1
                reproduction_data_stream = self.heifer_pregnancy_update(reproduction_data_stream, time.simulation_day)
        return reproduction_data_stream

    def cow_reproduction_update(
        self, reproduction_data_stream: ReproductionDataStream, time: RufasTime
    ) -> ReproductionDataStream:
        """
        Update reproduction status for cows based on the protocol.

        Parameters
        ----------
        reproduction_data_stream : ReproductionDataStream
            Current reproduction datastream.
        time : RufasTime
            The current time in the simulation.

        Returns
        -------
        ReproductionDataStream
            Updated reproduction datastream for the cow.
        """
        if reproduction_data_stream.is_pregnant and reproduction_data_stream.days_in_pregnancy == self.gestation_length:
            reproduction_data_stream = self.cow_give_birth(reproduction_data_stream, time)

        if not self.do_not_breed:
            self._validate_cow_reproduction_program()
            reproduction_data_stream = self._update_cow_repro_program_and_log_repro_stats_if_needed(
                reproduction_data_stream, time.simulation_day
            )

            reproduction_data_stream = self._execute_cow_reproduction_protocols(
                reproduction_data_stream, time.simulation_day
            )

            reproduction_data_stream = self._handle_cow_ai_day(reproduction_data_stream, time.simulation_day)

            reproduction_data_stream = self.cow_pregnancy_update(reproduction_data_stream, time.simulation_day)

        reproduction_data_stream = self._check_do_not_breed_flag(time.simulation_day, reproduction_data_stream)

        return reproduction_data_stream

    def _validate_cow_reproduction_program(self) -> None:
        """Ensures the cow reproduction program is one of the valid protocols."""
        if self.cow_reproduction_program not in [
            CowReproductionProtocol.ED,
            CowReproductionProtocol.TAI,
            CowReproductionProtocol.ED_TAI,
        ]:
            raise ValueError(f"Invalid cow repro program: {self.cow_reproduction_program}")

    def _update_cow_repro_program_and_log_repro_stats_if_needed(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Updates the cow reproduction program to match configuration, logging any pre-existing state."""
        if self.cow_reproduction_program != CowReproductionProtocol(AnimalConfig.cow_reproduction_program):
            reproduction_data_stream = self._set_cow_reproduction_program(
                reproduction_data_stream, simulation_day, CowReproductionProtocol(AnimalConfig.cow_reproduction_program)
            )
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"Pre-existing days in milk: {reproduction_data_stream.days_in_milk}",
            )
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"Pre-existing days in preg: {reproduction_data_stream.days_in_pregnancy}",
            )
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born, simulation_day, f"Pre-existing AI day: {self.ai_day}"
            )
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"Pre-existing estrus day: {self.estrus_day}",
            )
            if not reproduction_data_stream.is_pregnant:
                self.repro_state_manager.enter(ReproStateEnum.ENTER_HERD_FROM_INIT)
                reproduction_data_stream.events.add_event(
                    reproduction_data_stream.days_born,
                    simulation_day,
                    f"Current repro state(s): {self.repro_state_manager}",
                )
        return reproduction_data_stream

    def _execute_cow_reproduction_protocols(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Executes the relevant cow reproduction protocol methods based on current program and state."""
        if self.cow_reproduction_program == CowReproductionProtocol.ED_TAI:
            reproduction_data_stream = self.execute_cow_ed_tai_protocol(reproduction_data_stream, simulation_day)
        if self.cow_reproduction_program == CowReproductionProtocol.ED or self.repro_state_manager.is_in_any(
            {
                ReproStateEnum.WAITING_FULL_ED_CYCLE,
                ReproStateEnum.WAITING_SHORT_ED_CYCLE,
                ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH,
            }
        ):
            reproduction_data_stream = self.execute_cow_ed_protocol(reproduction_data_stream, simulation_day)

        if self.cow_reproduction_program == CowReproductionProtocol.TAI or self.repro_state_manager.is_in_any(
            {
                ReproStateEnum.IN_PRESYNCH,
                ReproStateEnum.HAS_DONE_PRESYNCH,
                ReproStateEnum.IN_OVSYNCH,
            }
        ):
            reproduction_data_stream = self.execute_cow_tai_protocol(reproduction_data_stream, simulation_day)
        return reproduction_data_stream

    def _handle_cow_ai_day(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Performs AI and related updates if the current day matches the cow's AI day."""
        if reproduction_data_stream.days_born == self.ai_day:
            self._calculate_conception_rate_on_ai_day()
            self.repro_state_manager.enter(ReproStateEnum.AFTER_AI)
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"Current repro state(s): {self.repro_state_manager}",
            )
            reproduction_data_stream = self._perform_ai(reproduction_data_stream, simulation_day)

        return reproduction_data_stream

    def _execute_heifer_reproduction_protocol(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Executes the appropriate heifer reproduction protocol based on the current reproduction program."""
        if self.heifer_reproduction_program == HeiferReproductionProtocol.ED:
            return self.execute_heifer_ed_protocol(reproduction_data_stream, simulation_day)
        elif self.heifer_reproduction_program == HeiferReproductionProtocol.TAI:
            return self.execute_heifer_tai_protocol(reproduction_data_stream, simulation_day)
        elif self.heifer_reproduction_program == HeiferReproductionProtocol.SynchED:
            return self.execute_heifer_synch_ed_protocol(reproduction_data_stream, simulation_day)
        else:
            raise ValueError(f"Invalid heifer repro program: {self.heifer_reproduction_program}")

    def _add_cow_give_birth_events(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Adds the new_birth event and records the parity for cow giving birth."""
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born, simulation_day, animal_constants.NEW_BIRTH
        )
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            f"{animal_constants.NUM_CALVES_BORN_NOTE}: {self.calves}",
        )
        return reproduction_data_stream

    def _update_cow_repro_program_and_reset_repro_state_if_needed(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """
        Updates the cow's reproduction program and resets reproduction state if it differs from the configured program.
        """
        if self.cow_reproduction_program != AnimalConfig.cow_reproduction_program:
            reproduction_data_stream = self._set_cow_reproduction_program(
                reproduction_data_stream, simulation_day, AnimalConfig.cow_reproduction_program
            )
            self.repro_state_manager.reset()
        return reproduction_data_stream

    def _simulate_estrus_if_eligible(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Simulates estrus if the cow reproduction program is ED or ED_TAI."""
        if self.cow_reproduction_program in [
            CowReproductionProtocol.ED,
            CowReproductionProtocol.ED_TAI,
        ]:
            reproduction_data_stream = self._simulate_estrus(
                reproduction_data_stream,
                reproduction_data_stream.days_born,
                simulation_day,
                f"{animal_constants.ESTRUS_AFTER_CALVING_NOTE}: {animal_constants.ESTRUS_DAY_SCHEDULED_NOTE}",
                AnimalConfig.average_estrus_cycle_return,
                AnimalConfig.std_estrus_cycle_return,
            )
        return reproduction_data_stream

    def cow_give_birth(
        self, reproduction_data_stream: ReproductionDataStream, time: RufasTime
    ) -> ReproductionDataStream:
        """Handle the birth of a calf, resetting reproduction states and updating outputs."""
        self.repro_state_manager.reset()
        self.calves += 1
        reproduction_data_stream.days_in_milk = 1
        reproduction_data_stream.days_in_pregnancy = 0
        self.gestation_length = 0
        self.body_weight_at_calving = reproduction_data_stream.body_weight

        reproduction_data_stream = self._add_cow_give_birth_events(reproduction_data_stream, time.simulation_day)

        reproduction_data_stream = self._update_cow_repro_program_and_reset_repro_state_if_needed(
            reproduction_data_stream, time.simulation_day
        )

        reproduction_data_stream = self._simulate_estrus_if_eligible(reproduction_data_stream, time.simulation_day)

        newborn_calf_net_merit = AnimalGenetics.assign_net_merit_value_to_newborn_calf(
            time, reproduction_data_stream.breed, reproduction_data_stream.net_merit
        )
        reproduction_data_stream.newborn_calf_config = NewBornCalfValuesTypedDict(
            breed=reproduction_data_stream.breed.name,
            animal_type=AnimalType.CALF.value,
            birth_date=time.current_date.strftime("%Y-%m-%d"),
            days_born=0,
            birth_weight=self.calf_birth_weight,
            initial_phosphorus=reproduction_data_stream.phosphorus_for_gestation_required_for_calf,
            net_merit=newborn_calf_net_merit,
        )

        return reproduction_data_stream

    def _set_heifer_reproduction_program(
        self,
        reproduction_data_stream: ReproductionDataStream,
        simulation_day: int,
        repro_program: HeiferReproductionProtocol,
    ) -> ReproductionDataStream:
        """Set the reproduction program for a heifer if it does not match the current program."""

        if repro_program not in [
            HeiferReproductionProtocol.ED,
            HeiferReproductionProtocol.TAI,
            HeiferReproductionProtocol.SynchED,
        ]:
            raise ValueError(f"Invalid repro program: {repro_program}")

        if self.heifer_reproduction_program == repro_program:
            return reproduction_data_stream

        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            f"{animal_constants.SETTING_REPRO_PROGRAM_NOTE} from {self.heifer_reproduction_program} "
            f"to {repro_program}",
        )
        self.heifer_reproduction_program = repro_program

        return reproduction_data_stream

    def _set_cow_reproduction_program(
        self,
        reproduction_data_stream: ReproductionDataStream,
        simulation_day: int,
        repro_program: CowReproductionProtocol,
    ) -> ReproductionDataStream:
        """Set the reproduction program for a cow if it does not match the current program."""

        if repro_program not in [
            CowReproductionProtocol.ED,
            CowReproductionProtocol.TAI,
            CowReproductionProtocol.ED_TAI,
        ]:
            raise ValueError(f"Invalid repro program: {repro_program}")

        if self.cow_reproduction_program == repro_program:
            return reproduction_data_stream

        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            f"{animal_constants.SETTING_REPRO_PROGRAM_NOTE} from {self.cow_reproduction_program} "
            f"to {repro_program}",
        )
        self.cow_reproduction_program = repro_program

        return reproduction_data_stream

    def _simulate_first_estrus(
        self,
        reproduction_data_stream: ReproductionDataStream,
        start_day: int,
        simulation_day: int,
        estrus_note: str,
        avg_estrus_cycle: float,
        max_cycle_length: float = math.inf,
    ) -> ReproductionDataStream:
        """
        Calculate and set first next estrus day for an heiferII.

        Parameters
        ----------
        start_day : int
            The day to begin the estrus cycle calculation.
        simulation_day : int
            The current simulation day.
        estrus_note : str
            Note explaining the reason for estrus simulation.
        avg_estrus_cycle : float
            Average length of the estrus cycle.
        max_cycle_length : float, optional
            Maximum allowable length for the estrus cycle, by default inf.

        Returns
        -------
        ReproductionDataStream
            Updated reproduction datastream after estrus simulation.
        """
        estrus_cycle = random.randint(1, floor(avg_estrus_cycle))
        if estrus_cycle >= max_cycle_length:
            estrus_cycle = max_cycle_length - 1
        self.estrus_day = start_day + estrus_cycle
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born, simulation_day, f"{estrus_note} on day {self.estrus_day}"
        )
        return reproduction_data_stream

    def _simulate_estrus(
        self,
        reproduction_data_stream: ReproductionDataStream,
        start_day: int,
        simulation_day: int,
        estrus_note: str,
        avg_estrus_cycle: float,
        std_estrus_cycle: float,
        max_cycle_length: float = math.inf,
    ) -> ReproductionDataStream:
        """
        Calculate and set the next estrus day for the animal.

        Parameters
        ----------
        start_day : int
            The day to begin the estrus cycle calculation.
        simulation_day : int
            The current simulation day.
        estrus_note : str
            Note explaining the reason for estrus simulation.
        avg_estrus_cycle : float
            Average length of the estrus cycle.
        std_estrus_cycle : float
            Standard deviation of the estrus cycle length.
        max_cycle_length : float, optional
            Maximum allowable length for the estrus cycle, by default inf.

        Returns
        -------
        ReproductionDataStream
            Updated reproduction datastream after estrus simulation.
        """
        estrus_cycle = truncnorm.rvs(-animal_constants.STDI, animal_constants.STDI, avg_estrus_cycle, std_estrus_cycle)
        if abs(estrus_cycle) >= max_cycle_length:
            estrus_cycle = max_cycle_length - 1
        self.estrus_day = int(start_day + abs(estrus_cycle))
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born, simulation_day, f"{estrus_note} on day {self.estrus_day}"
        )
        return reproduction_data_stream

    def _detect_estrus(self, detection_rate: float) -> bool:
        """Determine if estrus is detected based on a randomized comparison with a detection rate."""

        return Utility.compare_randomized_rate_less_than(detection_rate)

    def execute_heifer_ed_protocol(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Execute the estrus detection (ED) protocol for heifers."""

        if not reproduction_data_stream.is_pregnant:
            self.reproduction_statistics.ED_days += 1
        else:
            self.reproduction_statistics.ED_days = 0
        if reproduction_data_stream.days_born == AnimalConfig.heifer_breed_start_day:
            reproduction_data_stream = self._simulate_first_estrus(
                reproduction_data_stream,
                AnimalConfig.heifer_breed_start_day,
                simulation_day,
                animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
                AnimalConfig.average_estrus_cycle_heifer,
            )
        elif reproduction_data_stream.days_born == self.estrus_day:
            reproduction_data_stream = self._handle_generic_estrus_detection(reproduction_data_stream, simulation_day)

        return reproduction_data_stream

    def _handle_generic_estrus_detection(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Perform general estrus detection, using specific functions for detected and non-detected cases."""
        reproduction_data_stream = self._handle_estrus_detection(
            reproduction_data_stream,
            simulation_day,
            on_estrus_detected=self._handle_estrus_detected,
            on_estrus_not_detected=self._handle_estrus_not_detected,
        )
        return reproduction_data_stream

    def _handle_estrus_detection(
        self,
        reproduction_data_stream: ReproductionDataStream,
        simulation_day: int,
        on_estrus_detected: Callable[[ReproductionDataStream, int], ReproductionDataStream],
        on_estrus_not_detected: Callable[[ReproductionDataStream, int], ReproductionDataStream],
    ) -> ReproductionDataStream:
        """Handle estrus detection and call specific functions when detected and not detected."""
        estrus_detection_rate = (
            AnimalConfig.heifer_estrus_detection_rate
            if reproduction_data_stream.animal_type == AnimalType.HEIFER_II
            else AnimalConfig.cow_estrus_detection_rate
        )
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            animal_constants.ESTRUS_OCCURRED_NOTE,
        )
        is_estrus_detected = self._detect_estrus(estrus_detection_rate)
        self.reproduction_statistics.estrus_count += 1
        if is_estrus_detected:
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"{animal_constants.ESTRUS_DETECTED_NOTE}, " f"with estrus detection rate at {estrus_detection_rate}",
            )
            reproduction_data_stream = on_estrus_detected(reproduction_data_stream, simulation_day)
        else:
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"{animal_constants.ESTRUS_NOT_DETECTED_NOTE}, "
                f"with estrus detection rate at {estrus_detection_rate}",
            )
            reproduction_data_stream = on_estrus_not_detected(reproduction_data_stream, simulation_day)

        return reproduction_data_stream

    def _handle_estrus_detected(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Perform actions associated with estrus detection in the ED protocol."""

        self.conception_rate = AnimalConfig.heifer_estrus_conception_rate
        self.ai_day = reproduction_data_stream.days_born + 1
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            f"{animal_constants.AI_DAY_SCHEDULED_NOTE} on day {self.ai_day}",
        )
        return reproduction_data_stream

    def _handle_estrus_not_detected(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Perform actions when estrus is not detected in the ED protocol."""

        reproduction_data_stream = self._simulate_estrus(
            reproduction_data_stream,
            reproduction_data_stream.days_born,
            simulation_day,
            animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
            AnimalConfig.average_estrus_cycle_heifer,
            AnimalConfig.std_estrus_cycle_heifer,
        )
        return reproduction_data_stream

    def _deliver_hormones(
        self,
        reproduction_data_stream: ReproductionDataStream,
        hormones: list[str],
        delivery_day: int,
        simulation_day: int,
    ) -> ReproductionDataStream:
        """Deliver hormones on the specified day."""

        for hormone in hormones:
            if hormone == "GnRH":
                self.reproduction_statistics.GnRH_injections += 1
                event = animal_constants.INJECT_GNRH
            elif hormone == "PGF":
                self.reproduction_statistics.PGF_injections += 1
                event = animal_constants.INJECT_PGF
            elif hormone == "CIDR":
                self.reproduction_statistics.CIDR_injections += 1
                event = animal_constants.INJECT_CIDR
            else:
                raise ValueError(f"Invalid hormone: {hormone}")

            reproduction_data_stream.events.add_event(
                delivery_day,
                simulation_day,
                event,
            )
        return reproduction_data_stream

    def _execute_hormone_delivery_schedule(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int, schedule: dict[int, dict[str, Any]]
    ) -> ReproductionDataStream:
        """Execute hormone delivery schedule on the specified days."""

        actions = schedule.get(reproduction_data_stream.days_born)
        if actions is not None:
            if actions.get("deliver_hormones") is not None:
                reproduction_data_stream = self._deliver_hormones(
                    reproduction_data_stream,
                    actions["deliver_hormones"],
                    reproduction_data_stream.days_born,
                    simulation_day,
                )
                del actions["deliver_hormones"]

            if actions.get("set_ai_day", False):
                self.ai_day = reproduction_data_stream.days_born
                reproduction_data_stream.events.add_event(
                    reproduction_data_stream.days_born,
                    simulation_day,
                    f"{animal_constants.AI_DAY_SCHEDULED_NOTE} on day {self.ai_day}",
                )
                del actions["set_ai_day"]

            if actions.get("set_conception_rate", False):
                self.conception_rate = self.TAI_conception_rate
                del actions["set_conception_rate"]

            if not actions:
                del schedule[reproduction_data_stream.days_born]
        return reproduction_data_stream

    def execute_heifer_tai_protocol(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Execute the Timed Artificial Insemination (TAI) protocol for heifers."""

        self.heifer_reproduction_sub_program = (
            AnimalConfig.heifer_reproduction_sub_program
            if self.heifer_reproduction_program == AnimalConfig.heifer_reproduction_program
            else InternalReproSettings.HEIFER_REPRO_PROTOCOLS[self.heifer_reproduction_program.value][
                "default_sub_protocol"
            ]
        )
        if reproduction_data_stream.days_born == AnimalConfig.heifer_breed_start_day:
            reproduction_data_stream = self._set_up_hormone_schedule(
                reproduction_data_stream, reproduction_data_stream.days_born, self.heifer_reproduction_sub_program.value
            )

            self.TAI_conception_rate = (
                AnimalConfig.heifer_reproduction_sub_program_conception_rate
                if AnimalConfig.heifer_reproduction_program == HeiferReproductionProtocol.TAI
                else InternalReproSettings.HEIFER_REPRO_PROTOCOLS[HeiferReproductionProtocol.TAI.value][
                    "default_sub_properties"
                ]["conception_rate"]
            )

        if self.hormone_schedule:
            reproduction_data_stream = self._execute_hormone_delivery_schedule(
                reproduction_data_stream, simulation_day, self.hormone_schedule
            )

        return reproduction_data_stream

    def execute_heifer_synch_ed_protocol(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Execute the SynchED protocol for heifers."""

        if reproduction_data_stream.days_born == AnimalConfig.heifer_breed_start_day:
            self.heifer_reproduction_sub_program = (
                AnimalConfig.heifer_reproduction_sub_program
                if self.heifer_reproduction_program == AnimalConfig.heifer_reproduction_program
                else InternalReproSettings.HEIFER_REPRO_PROTOCOLS[self.heifer_reproduction_program.value][
                    "default_sub_protocol"
                ]
            )
            reproduction_data_stream = self._set_up_hormone_schedule(
                reproduction_data_stream, reproduction_data_stream.days_born, self.heifer_reproduction_sub_program.value
            )

        reproduction_data_stream = self._handle_synch_ed_hormone_delivery_and_set_estrus_day(
            reproduction_data_stream, simulation_day
        )

        if reproduction_data_stream.days_born == self.estrus_day:
            reproduction_data_stream = self._handle_synch_ed_estrus_detection(reproduction_data_stream, simulation_day)

        return reproduction_data_stream

    def _set_up_hormone_schedule(
        self, reproduction_data_stream: ReproductionDataStream, start_from: int, reproduction_sub_protocol: str
    ) -> ReproductionDataStream:
        """Set up the hormone delivery schedule for heifers or cows."""
        if reproduction_data_stream.animal_type == AnimalType.HEIFER_II:
            hormone_schedule = HormoneDeliverySchedule.get_adjusted_schedule(
                "heifers", reproduction_sub_protocol, start_from
            )
            if hormone_schedule is None:
                raise Exception(
                    f"No hormone delivery schedule for {reproduction_data_stream.animal_type} - "
                    f"{self.heifer_reproduction_sub_program}"
                )
            self.hormone_schedule = hormone_schedule

        else:
            hormone_schedule = HormoneDeliverySchedule.get_adjusted_schedule(
                "cows", reproduction_sub_protocol, start_from
            )
            if hormone_schedule is None:
                raise Exception(
                    f"No hormone delivery schedule for {reproduction_data_stream.animal_type} - "
                    f"{self.cow_ovsynch_program}"
                )
            self.hormone_schedule = hormone_schedule
        return reproduction_data_stream

    def _handle_synch_ed_hormone_delivery_and_set_estrus_day(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Deliver hormones and set the estrus day for heifers in the SynchED protocol."""

        if self.hormone_schedule:
            reproduction_data_stream = self._execute_hormone_delivery_schedule(
                reproduction_data_stream, simulation_day, self.hormone_schedule
            )
            if not self.hormone_schedule:
                reproduction_data_stream = self._simulate_estrus(
                    reproduction_data_stream,
                    reproduction_data_stream.days_born,
                    simulation_day,
                    animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
                    AnimalConfig.average_estrus_cycle_after_pgf,
                    AnimalConfig.std_estrus_cycle_after_pgf,
                    max_cycle_length=14,
                )

        return reproduction_data_stream

    def _handle_synch_ed_estrus_detection(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Handle estrus detection for heifers in the SynchED program."""
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            animal_constants.ESTRUS_OCCURRED_NOTE,
        )
        synch_ed_estrus_detection_rate = (
            AnimalConfig.heifer_reproduction_sub_program_estrus_detection_rate
            if AnimalConfig.heifer_reproduction_program == HeiferReproductionProtocol.SynchED
            else InternalReproSettings.HEIFER_REPRO_PROTOCOLS[HeiferReproductionProtocol.SynchED.value][
                "default_sub_properties"
            ]["estrus_detection_rate"]
        )
        is_estrus_detected = self._detect_estrus(synch_ed_estrus_detection_rate)

        if is_estrus_detected:
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                animal_constants.ESTRUS_DETECTED_NOTE,
            )
            self.conception_rate = AnimalConfig.heifer_reproduction_sub_program_conception_rate
            self.ai_day = reproduction_data_stream.days_born + 1
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"{animal_constants.AI_DAY_SCHEDULED_NOTE} on day {self.ai_day}",
            )
        else:
            reproduction_data_stream = self._handle_estrus_not_detected_in_synch_ed(
                reproduction_data_stream, simulation_day
            )
        return reproduction_data_stream

    def _handle_estrus_not_detected_in_synch_ed(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """
        Handle the case where estrus is not detected for heifers in the SynchED program.

        If estrus is not detected, this method updates the reproduction program and sets up
        the next steps according to the fallback protocol.
        """
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            animal_constants.ESTRUS_NOT_DETECTED_NOTE,
        )
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            animal_constants.TAI_AFTER_ESTRUS_NOT_DETECTED_IN_SYNCH_ED_NOTE,
        )
        heifer_repro_sub_protocol = (
            self.heifer_reproduction_sub_program
            if self.heifer_reproduction_sub_program == AnimalConfig.heifer_reproduction_sub_program
            else (
                InternalReproSettings.HEIFER_REPRO_PROTOCOLS[self.heifer_reproduction_program.value][
                    "default_sub_protocol"
                ]
            )
        )
        internal_fallback_protocol = InternalReproSettings.HEIFER_REPRO_PROTOCOLS[heifer_repro_sub_protocol.value][
            "when_estrus_not_detected"
        ]

        if self.heifer_reproduction_program.value != internal_fallback_protocol["repro_protocol"]:
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"{animal_constants.SETTING_REPRO_PROGRAM_NOTE} from "
                f"{self.heifer_reproduction_program} to "
                f"{internal_fallback_protocol['repro_protocol']}",
            )
            self.heifer_reproduction_program = HeiferReproductionProtocol(internal_fallback_protocol["repro_protocol"])

        reproduction_data_stream = self._set_up_hormone_schedule(
            reproduction_data_stream, reproduction_data_stream.days_born, heifer_repro_sub_protocol.value
        )

        self.TAI_conception_rate = internal_fallback_protocol["repro_sub_properties"]["conception_rate"]

        reproduction_data_stream = self._execute_hormone_delivery_schedule(
            reproduction_data_stream, simulation_day, self.hormone_schedule
        )

        return reproduction_data_stream

    def open_heifer(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Handle the status of an open heifer (post-abortion or pregnancy loss)."""
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            animal_constants.REBREEDING_NOTE,
        )
        if self.heifer_reproduction_program != HeiferReproductionProtocol.ED:
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"{animal_constants.SETTING_REPRO_PROGRAM_NOTE} from "
                f"{self.heifer_reproduction_program} to "
                f"{HeiferReproductionProtocol.ED}",
            )
            self.heifer_reproduction_program = HeiferReproductionProtocol.ED

        reproduction_data_stream = self._simulate_estrus(
            reproduction_data_stream,
            self.abortion_day,
            simulation_day,
            animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
            AnimalConfig.average_estrus_cycle_heifer,
            AnimalConfig.std_estrus_cycle_heifer,
        )

        return reproduction_data_stream

    def _perform_ai(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Perform artificial insemination (AI) on the animal."""
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            animal_constants.AI_PERFORMED_NOTE,
        )
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            animal_constants.INSEMINATED_W_BASE + AnimalConfig.semen_type,
        )
        self.reproduction_statistics.semen_number += 1
        self.reproduction_statistics.AI_times += 1

        if reproduction_data_stream.animal_type == AnimalType.HEIFER_II:
            reproduction_data_stream = self._increment_heifer_ai_counts(reproduction_data_stream)
        else:
            reproduction_data_stream = self._increment_cow_ai_counts(reproduction_data_stream)

        conception_successful = Utility.compare_randomized_rate_less_than(self.conception_rate)
        if conception_successful:
            if reproduction_data_stream.animal_type == AnimalType.HEIFER_II:
                reproduction_data_stream = self._handle_successful_heifer_conception(
                    reproduction_data_stream, simulation_day
                )
                reproduction_data_stream = self._increment_successful_heifer_conceptions(reproduction_data_stream)
            else:
                reproduction_data_stream = self._handle_successful_cow_conception(
                    reproduction_data_stream, simulation_day
                )
                reproduction_data_stream = self._increment_successful_cow_conceptions(reproduction_data_stream)
        else:
            if reproduction_data_stream.animal_type == AnimalType.HEIFER_II:
                reproduction_data_stream = self._handle_failed_heifer_conception(
                    reproduction_data_stream, simulation_day
                )
            else:
                reproduction_data_stream = self._handle_failed_cow_conception(reproduction_data_stream, simulation_day)

        return reproduction_data_stream

    def _increment_heifer_ai_counts(self, reproduction_data_stream: ReproductionDataStream) -> ReproductionDataStream:
        """Increment the AI counts for heifers."""

        reproduction_data_stream.herd_reproduction_statistics.total_num_ai_performed += 1
        reproduction_data_stream.herd_reproduction_statistics.heifer_num_ai_performed += 1

        if self.heifer_reproduction_program == HeiferReproductionProtocol.ED:
            reproduction_data_stream.herd_reproduction_statistics.heifer_num_ai_performed_in_ED += 1
        elif self.heifer_reproduction_program == HeiferReproductionProtocol.TAI:
            reproduction_data_stream.herd_reproduction_statistics.heifer_num_ai_performed_in_TAI += 1
        elif self.heifer_reproduction_program == HeiferReproductionProtocol.SynchED:
            reproduction_data_stream.herd_reproduction_statistics.heifer_num_ai_performed_in_SynchED += 1
        return reproduction_data_stream

    def _increment_successful_heifer_conceptions(
        self, reproduction_data_stream: ReproductionDataStream
    ) -> ReproductionDataStream:
        """Increment the counts of successful conceptions for heifers."""
        reproduction_data_stream.herd_reproduction_statistics.total_num_successful_conceptions += 1
        reproduction_data_stream.herd_reproduction_statistics.heifer_num_successful_conceptions += 1

        if self.heifer_reproduction_program == HeiferReproductionProtocol.ED:
            reproduction_data_stream.herd_reproduction_statistics.heifer_num_successful_conceptions_in_ED += 1
        elif self.heifer_reproduction_program == HeiferReproductionProtocol.TAI:
            reproduction_data_stream.herd_reproduction_statistics.heifer_num_successful_conceptions_in_TAI += 1
        elif self.heifer_reproduction_program == HeiferReproductionProtocol.SynchED:
            reproduction_data_stream.herd_reproduction_statistics.heifer_num_successful_conceptions_in_SynchED += 1
        return reproduction_data_stream

    def _handle_successful_heifer_conception(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Handle a successful conception event for a heifer."""
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            animal_constants.HEIFER_PREG,
        )
        reproduction_data_stream = self._initialize_pregnancy_parameters(reproduction_data_stream)
        return reproduction_data_stream

    def _handle_failed_heifer_conception(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Handle a failed conception event for a heifer."""
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            animal_constants.HEIFER_NOT_PREG,
        )
        if reproduction_data_stream.animal_type == AnimalType.HEIFER_II:
            reproduction_data_stream = self._set_heifer_reproduction_program(
                reproduction_data_stream, simulation_day, HeiferReproductionProtocol.ED
            )
        else:
            reproduction_data_stream = self._set_cow_reproduction_program(
                reproduction_data_stream, simulation_day, CowReproductionProtocol.ED
            )

        average_estrus_cycle = (
            AnimalConfig.average_estrus_cycle_heifer
            if reproduction_data_stream.animal_type == AnimalType.HEIFER_II
            else AnimalConfig.average_estrus_cycle_cow
        )
        std_estrus_cycle = (
            AnimalConfig.std_estrus_cycle_heifer
            if reproduction_data_stream.animal_type == AnimalType.HEIFER_II
            else AnimalConfig.std_estrus_cycle_cow
        )

        reproduction_data_stream = self._simulate_estrus(
            reproduction_data_stream,
            reproduction_data_stream.days_born - 1,
            simulation_day,
            animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
            average_estrus_cycle,
            std_estrus_cycle,
        )
        return reproduction_data_stream

    def _calculate_gestation_length(self) -> int:
        """Calculate the gestation length for the heifer."""
        return int(
            truncnorm.rvs(
                -animal_constants.STDI,
                animal_constants.STDI,
                AnimalConfig.average_gestation_length,
                AnimalConfig.std_gestation_length,
            )
        )

    def _calculate_calf_birth_weight(self, breed: Breed) -> float:
        """
         Calculates the birth weight of the calf based on the breed.

        Notes
        ------
        [AN.BWT.6]


         Parameters
         ----------
         breed: Breed
             The breed of the animal.

         Returns
         -------
         float
             The birth weight for the calf (kg).
        """

        average_birth_weight_by_breed = {
            Breed.HO: AnimalConfig.birth_weight_avg_ho,
            Breed.JE: AnimalConfig.birth_weight_avg_je,
        }
        std_birth_weight_by_breed = {
            Breed.HO: AnimalConfig.birth_weight_std_ho,
            Breed.JE: AnimalConfig.birth_weight_std_je,
        }
        birth_weight = truncnorm.rvs(
            -animal_constants.STDI,
            animal_constants.STDI,
            average_birth_weight_by_breed[breed],
            std_birth_weight_by_breed[breed],
        )
        return float(birth_weight)

    def _initialize_pregnancy_parameters(
        self, reproduction_data_stream: ReproductionDataStream
    ) -> ReproductionDataStream:
        """Initialize parameters related to pregnancy for the heifer."""

        reproduction_data_stream.days_in_pregnancy = 1
        self.abortion_day = 0
        self.breeding_to_preg_time = reproduction_data_stream.days_born - AnimalConfig.heifer_breed_start_day
        self.gestation_length = self._calculate_gestation_length()
        self.calf_birth_weight = self._calculate_calf_birth_weight(reproduction_data_stream.breed)

        return reproduction_data_stream

    def heifer_pregnancy_update(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Update the pregnancy status for a heifer."""
        pregnancy_check_configs: list[PregnancyCheckConfig] = [
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

        for pregnancy_check_config in pregnancy_check_configs:
            if reproduction_data_stream.days_born == self.ai_day + pregnancy_check_config["day"]:
                reproduction_data_stream = self._handle_heifer_pregnancy_check(
                    reproduction_data_stream, pregnancy_check_config, simulation_day
                )
        return reproduction_data_stream

    def _handle_heifer_pregnancy_check(
        self,
        reproduction_data_stream: ReproductionDataStream,
        pregnancy_check_config: PregnancyCheckConfig,
        simulation_day: int,
    ) -> ReproductionDataStream:
        """Handle pregnancy checks for heifers and take appropriate actions based on results."""

        self.reproduction_statistics.pregnancy_diagnoses += 1
        if reproduction_data_stream.is_pregnant:
            if Utility.compare_randomized_rate_less_than(pregnancy_check_config["loss_rate"]):
                reproduction_data_stream = self._terminate_pregnancy(
                    reproduction_data_stream, pregnancy_check_config["on_preg_loss"], simulation_day
                )
            else:
                reproduction_data_stream.events.add_event(
                    reproduction_data_stream.days_born,
                    simulation_day,
                    pregnancy_check_config["on_preg"],
                )
        elif "on_not_preg" in pregnancy_check_config:
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                pregnancy_check_config["on_not_preg"],
            )
            self.abortion_day = reproduction_data_stream.days_born
            reproduction_data_stream = self.open_heifer(reproduction_data_stream, simulation_day)
        return reproduction_data_stream

    def _handle_cow_pregnancy_check(
        self,
        reproduction_data_stream: ReproductionDataStream,
        pregnancy_check_config: PregnancyCheckConfig,
        simulation_day: int,
    ) -> ReproductionDataStream:
        """Handle a pregnancy check for cows and update the state based on the outcome."""

        self.reproduction_statistics.pregnancy_diagnoses += 1
        if reproduction_data_stream.is_pregnant:
            if Utility.compare_randomized_rate_less_than(pregnancy_check_config["loss_rate"]):
                self.repro_state_manager.exit(ReproStateEnum.PREGNANT)
                reproduction_data_stream = self._terminate_pregnancy(
                    reproduction_data_stream, pregnancy_check_config["on_preg_loss"], simulation_day
                )
            else:
                reproduction_data_stream.events.add_event(
                    reproduction_data_stream.days_born,
                    simulation_day,
                    pregnancy_check_config["on_preg"],
                )
                if self.repro_state_manager.is_in(ReproStateEnum.IN_OVSYNCH):
                    reproduction_data_stream = (
                        self._exit_ovsynch_program_early_when_first_preg_check_passed_or_estrus_detected(
                            reproduction_data_stream, simulation_day
                        )
                    )
        elif "on_not_preg" in pregnancy_check_config:  # Due to failed conception
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                pregnancy_check_config["on_not_preg"],
            )
            self.abortion_day = reproduction_data_stream.days_born
            reproduction_data_stream = self.open_cow(reproduction_data_stream, simulation_day)
        return reproduction_data_stream

    def _terminate_pregnancy(
        self, reproduction_data_stream: ReproductionDataStream, preg_loss_const: str, simulation_day: int
    ) -> ReproductionDataStream:
        """Terminate pregnancy and reset related parameters if pregnancy is lost."""
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            preg_loss_const,
        )
        self.abortion_day = reproduction_data_stream.days_born
        reproduction_data_stream.days_in_pregnancy = 0
        if reproduction_data_stream.animal_type == AnimalType.HEIFER_II:
            reproduction_data_stream = self.open_heifer(reproduction_data_stream, simulation_day)
        else:
            reproduction_data_stream = self.open_cow(reproduction_data_stream, simulation_day)
        reproduction_data_stream.body_weight -= self.conceptus_weight
        self.conceptus_weight = 0
        self.calf_birth_weight = 0
        reproduction_data_stream.phosphorus_for_gestation_required_for_calf = 0
        return reproduction_data_stream

    def _calculate_conception_rate_on_ai_day(self) -> None:
        """Adjust conception rate on the AI day based on breeding history and parity."""
        if AnimalConfig.should_decrease_conception_rate_in_rebreeding:
            self.conception_rate -= self.num_conception_rate_decreases * AnimalConfig.conception_rate_decrease

        if AnimalConfig.should_decrease_conception_rate_by_parity:
            self.conception_rate = self._decrease_conception_rate_by_parity(self.calves, self.conception_rate)

        self.conception_rate = max(0.0, self.conception_rate)

    def execute_cow_ed_protocol(  # noqa
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Execute the estrus detection (ED) protocol for cows."""
        if not reproduction_data_stream.is_pregnant:
            self.reproduction_statistics.ED_days += 1
        else:
            self.reproduction_statistics.ED_days = 0
        if 1 <= reproduction_data_stream.days_in_milk <= AnimalConfig.voluntary_waiting_period:
            reproduction_data_stream = self._repeat_estrus_simulation_before_vwp(
                reproduction_data_stream, simulation_day
            )

        elif reproduction_data_stream.days_in_milk > AnimalConfig.voluntary_waiting_period:
            if (
                self.repro_state_manager.is_in(ReproStateEnum.ENTER_HERD_FROM_INIT)
                and reproduction_data_stream.days_born > self.estrus_day
            ):
                reproduction_data_stream = self._simulate_estrus(
                    reproduction_data_stream,
                    reproduction_data_stream.days_born,
                    simulation_day,
                    animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
                    AnimalConfig.average_estrus_cycle_cow,
                    AnimalConfig.std_estrus_cycle_cow,
                )

            if self.repro_state_manager.is_in_any({ReproStateEnum.FRESH, ReproStateEnum.ENTER_HERD_FROM_INIT}):
                self.repro_state_manager.enter(ReproStateEnum.WAITING_FULL_ED_CYCLE)
                reproduction_data_stream.events.add_event(
                    reproduction_data_stream.days_born,
                    simulation_day,
                    f"Current repro state(s): {self.repro_state_manager}",
                )

            if reproduction_data_stream.days_born == self.estrus_day:
                if self.repro_state_manager.is_in(ReproStateEnum.WAITING_SHORT_ED_CYCLE):
                    self.repro_state_manager.exit(ReproStateEnum.WAITING_SHORT_ED_CYCLE)
                    reproduction_data_stream = self._handle_estrus_detection(
                        reproduction_data_stream,
                        simulation_day,
                        on_estrus_detected=self._setup_ai_day_after_estrus_detected,
                        on_estrus_not_detected=self._enter_ovsynch_repro_state,
                    )
                    if self.repro_state_manager.is_in(ReproStateEnum.IN_OVSYNCH):
                        reproduction_data_stream.events.add_event(
                            reproduction_data_stream.days_born,
                            simulation_day,
                            f"Current repro state(s): {self.repro_state_manager}",
                        )

                elif self.repro_state_manager.is_in(ReproStateEnum.WAITING_FULL_ED_CYCLE):
                    self.repro_state_manager.exit(ReproStateEnum.WAITING_FULL_ED_CYCLE)
                    reproduction_data_stream = self._handle_estrus_detection(
                        reproduction_data_stream,
                        simulation_day,
                        on_estrus_detected=self._setup_ai_day_after_estrus_detected,
                        on_estrus_not_detected=self._simulate_full_estrus_cycle,
                    )

                elif self.repro_state_manager.is_in(ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH):
                    self.repro_state_manager.exit(ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH)
                    reproduction_data_stream = self._handle_estrus_detection(
                        reproduction_data_stream,
                        simulation_day,
                        on_estrus_detected=self._setup_ai_day_after_estrus_detected,
                        on_estrus_not_detected=self._simulate_full_estrus_cycle_before_ovsynch,
                    )
        return reproduction_data_stream

    def _enter_ovsynch_repro_state(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Updates the reproduction state to 'IN_OVSYNCH'"""
        self.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
        assert simulation_day
        return reproduction_data_stream

    def _repeat_estrus_simulation_before_vwp(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Repeat estrus simulation for cows before the voluntary waiting period (VWP)."""
        if self.repro_state_manager.is_in_empty_state() or self.repro_state_manager.is_in(
            ReproStateEnum.ENTER_HERD_FROM_INIT
        ):
            self.repro_state_manager.enter(ReproStateEnum.FRESH)
            reproduction_data_stream.days_in_pregnancy = 0
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"Current repro state(s): {self.repro_state_manager}",
            )
        if reproduction_data_stream.days_born == self.estrus_day:
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                animal_constants.ESTRUS_BEFORE_VOLUNTARY_WAITING_PERIOD_NOTE,
            )
            reproduction_data_stream = self._simulate_estrus(
                reproduction_data_stream,
                reproduction_data_stream.days_born,
                simulation_day,
                animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
                AnimalConfig.average_estrus_cycle_cow,
                AnimalConfig.std_estrus_cycle_cow,
            )
        elif reproduction_data_stream.days_born > self.estrus_day:
            reproduction_data_stream = self._simulate_estrus(
                reproduction_data_stream,
                reproduction_data_stream.days_born,
                simulation_day,
                animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
                AnimalConfig.average_estrus_cycle_cow,
                AnimalConfig.std_estrus_cycle_cow,
            )
        return reproduction_data_stream

    def _setup_ai_day_after_estrus_detected(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Set up the AI day for cows when estrus is detected."""
        if self.repro_state_manager.is_in(ReproStateEnum.IN_OVSYNCH):
            reproduction_data_stream = self._exit_ovsynch_program_early_when_first_preg_check_passed_or_estrus_detected(
                reproduction_data_stream, simulation_day
            )

        self.repro_state_manager.enter(ReproStateEnum.ESTRUS_DETECTED)
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            f"Current repro state(s): {self.repro_state_manager}",
        )
        self.conception_rate = AnimalConfig.cow_estrus_conception_rate
        self.ai_day = reproduction_data_stream.days_born + 1
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            f"{animal_constants.AI_DAY_SCHEDULED_NOTE} on day {self.ai_day}",
        )

        return reproduction_data_stream

    def _simulate_full_estrus_cycle(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Simulate a full estrus cycle when estrus is not detected."""

        self.repro_state_manager.enter(ReproStateEnum.WAITING_FULL_ED_CYCLE, keep_existing=True)
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            f"Current repro state(s): {self.repro_state_manager}",
        )
        self._simulate_estrus(
            reproduction_data_stream,
            reproduction_data_stream.days_born,
            simulation_day,
            animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
            AnimalConfig.average_estrus_cycle_cow,
            AnimalConfig.std_estrus_cycle_cow,
        )
        return reproduction_data_stream

    def _simulate_full_estrus_cycle_before_ovsynch(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Simulate an estrus cycle before the OvSynch program in the ED-TAI protocol."""

        self.repro_state_manager.enter(ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH)
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            f"Current repro state(s): {self.repro_state_manager}",
        )
        self._simulate_estrus(
            reproduction_data_stream,
            reproduction_data_stream.days_born,
            simulation_day,
            animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
            AnimalConfig.average_estrus_cycle_cow,
            AnimalConfig.std_estrus_cycle_cow,
        )
        return reproduction_data_stream

    def _execute_cow_hormone_delivery_schedule(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int, schedule: dict[int, dict[str, Any]]
    ) -> ReproductionDataStream:
        """Execute hormone delivery schedule for cows."""

        reproduction_data_stream = self._execute_hormone_delivery_schedule(
            reproduction_data_stream, simulation_day, schedule
        )

        actions = schedule.get(reproduction_data_stream.days_born)
        if actions is not None:
            if actions.get("set_presynch_end", False):
                reproduction_data_stream.events.add_event(
                    reproduction_data_stream.days_born,
                    simulation_day,
                    f"{animal_constants.PRESYNCH_PERIOD_END}: {AnimalConfig.cow_presynch_method}",
                )
                self.repro_state_manager.exit(ReproStateEnum.IN_PRESYNCH)
                self.repro_state_manager.enter(ReproStateEnum.HAS_DONE_PRESYNCH)
                del actions["set_presynch_end"]

            if actions.get("set_ovsynch_end", False):
                reproduction_data_stream.events.add_event(
                    reproduction_data_stream.days_born,
                    simulation_day,
                    f"{animal_constants.OVSYNCH_PERIOD_END_NOTE}: {AnimalConfig.cow_ovsynch_method}",
                )
                self.repro_state_manager.exit(ReproStateEnum.IN_OVSYNCH)
                del actions["set_ovsynch_end"]

            if not actions:
                del schedule[reproduction_data_stream.days_born]
        return reproduction_data_stream

    def execute_cow_tai_protocol(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """
        Execute the TAI protocol for cows, setting up hormone delivery schedules for presynch and ovsynch programs.
        """

        if AnimalConfig.cow_presynch_method == CowPreSynchSubProtocol.NONE:
            if 1 <= reproduction_data_stream.days_in_milk < AnimalConfig.ovsynch_program_start_day:
                reproduction_data_stream = self._enter_fresh_state_if_in_empty_state(
                    reproduction_data_stream, simulation_day
                )
            elif reproduction_data_stream.days_in_milk >= AnimalConfig.ovsynch_program_start_day:
                reproduction_data_stream = self._setup_ovsynch_on_ovsynch_start_day_if_valid(
                    reproduction_data_stream, simulation_day
                )
            if self.hormone_schedule:
                reproduction_data_stream = self._execute_cow_hormone_delivery_schedule(
                    reproduction_data_stream, simulation_day, self.hormone_schedule
                )
            return reproduction_data_stream

        if 1 <= reproduction_data_stream.days_in_milk < AnimalConfig.presynch_program_start_day:
            reproduction_data_stream = self._enter_fresh_state_if_in_empty_state(
                reproduction_data_stream, simulation_day
            )
        elif reproduction_data_stream.days_in_milk >= AnimalConfig.presynch_program_start_day:
            reproduction_data_stream = self._setup_presynch_on_presynch_start_day_if_valid(
                reproduction_data_stream, simulation_day
            )
            if self.hormone_schedule:
                reproduction_data_stream = self._execute_cow_hormone_delivery_schedule(
                    reproduction_data_stream, simulation_day, self.hormone_schedule
                )
            reproduction_data_stream = self._setup_ovsynch_on_ovsynch_start_day_if_valid(
                reproduction_data_stream, simulation_day
            )
        if self.hormone_schedule:
            reproduction_data_stream = self._execute_cow_hormone_delivery_schedule(
                reproduction_data_stream, simulation_day, self.hormone_schedule
            )

        return reproduction_data_stream

    def _reset_ai_day_if_needed(
        self, program_to_enter: str, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Resets the pre-existing AI day for an animal to enter PreSynch or OvSynch."""
        if self.ai_day > 0:
            self.ai_day = 0
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"Resetting the pre-existing AI day to enter {program_to_enter} period.",
            )
        return reproduction_data_stream

    def _setup_presynch_on_presynch_start_day_if_valid(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Set up the presynch program for cows on the start day if applicable."""
        should_set_up_hormone_delivery_for_presynch, reproduction_data_stream = (
            self._should_set_up_hormone_delivery_for_presynch(reproduction_data_stream, simulation_day)
        )

        if should_set_up_hormone_delivery_for_presynch:
            self._set_up_hormone_schedule(
                reproduction_data_stream, reproduction_data_stream.days_born, AnimalConfig.cow_presynch_method.value
            )
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"{animal_constants.PRESYNCH_PERIOD_START}: {AnimalConfig.cow_presynch_method}",
            )
            reproduction_data_stream = self._reset_ai_day_if_needed(
                "PreSynch", reproduction_data_stream, simulation_day
            )
        return reproduction_data_stream

    def _enter_fresh_state_if_in_empty_state(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Enter the fresh state for cows if the current reproduction state is empty."""

        if self.repro_state_manager.is_in_empty_state() or self.repro_state_manager.is_in(
            ReproStateEnum.ENTER_HERD_FROM_INIT
        ):
            self.repro_state_manager.enter(ReproStateEnum.FRESH)
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"Current repro state(s): {self.repro_state_manager}",
            )
        return reproduction_data_stream

    def _setup_ovsynch_on_ovsynch_start_day_if_valid(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Set up an OvSynch program for cows on the OvSynch start day if applicable."""
        should_set_up_hormone_delivery_for_ovsynch, reproduction_data_stream = (
            self._should_set_up_hormone_delivery_for_ovsynch(reproduction_data_stream, simulation_day)
        )

        if should_set_up_hormone_delivery_for_ovsynch:
            reproduction_data_stream = self._set_up_hormone_schedule(
                reproduction_data_stream, reproduction_data_stream.days_born, AnimalConfig.cow_ovsynch_method.value
            )
            self.TAI_conception_rate = AnimalConfig.ovsynch_program_conception_rate
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"{animal_constants.OVSYNCH_PERIOD_START_NOTE}: {AnimalConfig.cow_ovsynch_method}",
            )
            reproduction_data_stream = self._reset_ai_day_if_needed("OvSynch", reproduction_data_stream, simulation_day)
        return reproduction_data_stream

    def _should_set_up_hormone_delivery_for_presynch(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> tuple[bool, ReproductionDataStream]:
        """Determine if hormone delivery should be set up for presynch based on current status."""

        if self.cow_reproduction_program != CowReproductionProtocol.TAI:
            return False, reproduction_data_stream

        if AnimalConfig.cow_presynch_method not in [
            CowPreSynchSubProtocol.Presynch_PreSynch,
            CowPreSynchSubProtocol.Presynch_DoubleOvSynch,
            CowPreSynchSubProtocol.Presynch_G6G,
        ]:
            return False, reproduction_data_stream

        if self.hormone_schedule:
            return False, reproduction_data_stream

        if (
            reproduction_data_stream.days_in_milk == AnimalConfig.presynch_program_start_day
            and self.repro_state_manager.is_in_any({ReproStateEnum.FRESH, ReproStateEnum.ENTER_HERD_FROM_INIT})
        ):
            self.repro_state_manager.enter(ReproStateEnum.IN_PRESYNCH)
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"Current repro state(s): {self.repro_state_manager}",
            )
            return True, reproduction_data_stream

        if (
            reproduction_data_stream.days_in_milk > AnimalConfig.presynch_program_start_day
            and self.repro_state_manager.is_in_any({ReproStateEnum.ENTER_HERD_FROM_INIT})
        ):
            self.repro_state_manager.enter(ReproStateEnum.IN_PRESYNCH)
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"Current repro state(s): {self.repro_state_manager}",
            )
            return True, reproduction_data_stream

        return self.repro_state_manager.is_in(ReproStateEnum.IN_PRESYNCH), reproduction_data_stream

    def _should_set_up_hormone_delivery_for_ovsynch(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> tuple[bool, ReproductionDataStream]:
        """Determine if hormone delivery should be set up for OvSynch based on current status."""

        if self.hormone_schedule:
            return False, reproduction_data_stream
        if AnimalConfig.cow_ovsynch_method not in [
            CowTAISubProtocol.TAI_OvSynch_48,
            CowTAISubProtocol.TAI_OvSynch_56,
            CowTAISubProtocol.TAI_CoSynch_72,
            CowTAISubProtocol.TAI_5d_CoSynch,
        ]:
            return False, reproduction_data_stream

        if self.repro_state_manager.is_in(ReproStateEnum.IN_PRESYNCH):
            return False, reproduction_data_stream

        if reproduction_data_stream.days_in_milk == AnimalConfig.ovsynch_program_start_day:
            if self.repro_state_manager.is_in_empty_state() or self.repro_state_manager.is_in_any(
                {
                    ReproStateEnum.ENTER_HERD_FROM_INIT,
                    ReproStateEnum.FRESH,
                    ReproStateEnum.HAS_DONE_PRESYNCH,
                }
            ):
                self.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
                reproduction_data_stream.events.add_event(
                    reproduction_data_stream.days_born,
                    simulation_day,
                    f"Current repro state(s): {self.repro_state_manager}",
                )
                return True, reproduction_data_stream

        if reproduction_data_stream.days_in_milk > AnimalConfig.ovsynch_program_start_day:
            if self.repro_state_manager.is_in_any(
                {ReproStateEnum.HAS_DONE_PRESYNCH, ReproStateEnum.ENTER_HERD_FROM_INIT}
            ):
                self.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
                reproduction_data_stream.events.add_event(
                    reproduction_data_stream.days_born,
                    simulation_day,
                    f"Current repro state(s): {self.repro_state_manager}",
                )
                return True, reproduction_data_stream

        return self.repro_state_manager.is_in(ReproStateEnum.IN_OVSYNCH), reproduction_data_stream

    def _increment_cow_ai_counts(self, reproduction_data_stream: ReproductionDataStream) -> ReproductionDataStream:
        """Increment AI counts for cows."""
        reproduction_data_stream.herd_reproduction_statistics.total_num_ai_performed += 1
        reproduction_data_stream.herd_reproduction_statistics.cow_num_ai_performed += 1

        if self.cow_reproduction_program == CowReproductionProtocol.ED:
            reproduction_data_stream.herd_reproduction_statistics.cow_num_ai_performed_in_ED += 1
        elif self.cow_reproduction_program == CowReproductionProtocol.TAI:
            reproduction_data_stream.herd_reproduction_statistics.cow_num_ai_performed_in_TAI += 1
        elif self.cow_reproduction_program == CowReproductionProtocol.ED_TAI:
            reproduction_data_stream.herd_reproduction_statistics.cow_num_ai_performed_in_ED_TAI += 1

        return reproduction_data_stream

    def _increment_successful_cow_conceptions(
        self, reproduction_data_stream: ReproductionDataStream
    ) -> ReproductionDataStream:
        """Increment successful conception counts for cows."""
        reproduction_data_stream.herd_reproduction_statistics.total_num_successful_conceptions += 1
        reproduction_data_stream.herd_reproduction_statistics.cow_num_successful_conceptions += 1

        if self.cow_reproduction_program == CowReproductionProtocol.ED:
            reproduction_data_stream.herd_reproduction_statistics.cow_num_successful_conceptions_in_ED += 1
        elif self.cow_reproduction_program == CowReproductionProtocol.TAI:
            reproduction_data_stream.herd_reproduction_statistics.cow_num_successful_conceptions_in_TAI += 1
        elif self.cow_reproduction_program == CowReproductionProtocol.ED_TAI:
            reproduction_data_stream.herd_reproduction_statistics.cow_num_successful_conceptions_in_ED_TAI += 1

        return reproduction_data_stream

    def execute_cow_ed_tai_protocol(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Execute the ED-TAI protocol for cows, monitoring days in milk and scheduling AI or estrus detection."""
        if 1 <= reproduction_data_stream.days_in_milk <= AnimalConfig.voluntary_waiting_period:
            reproduction_data_stream = self._repeat_estrus_simulation_before_vwp(
                reproduction_data_stream, simulation_day
            )

        elif (
            AnimalConfig.voluntary_waiting_period
            < reproduction_data_stream.days_in_milk
            < AnimalConfig.ovsynch_program_start_day
        ):
            if (
                self.repro_state_manager.is_in(ReproStateEnum.ENTER_HERD_FROM_INIT)
                and reproduction_data_stream.days_born > self.estrus_day
            ):
                reproduction_data_stream = self._simulate_estrus(
                    reproduction_data_stream,
                    reproduction_data_stream.days_born,
                    simulation_day,
                    animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
                    AnimalConfig.average_estrus_cycle_cow,
                    AnimalConfig.std_estrus_cycle_cow,
                )

            if self.repro_state_manager.is_in_any({ReproStateEnum.FRESH, ReproStateEnum.ENTER_HERD_FROM_INIT}):
                self.repro_state_manager.enter(ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH)
                reproduction_data_stream.events.add_event(
                    reproduction_data_stream.days_born,
                    simulation_day,
                    f"Current repro state(s): {self.repro_state_manager}",
                )

        elif reproduction_data_stream.days_in_milk >= AnimalConfig.ovsynch_program_start_day:
            reproduction_data_stream = self._handle_estrus_not_detected_before_ovsynch_start_day(
                reproduction_data_stream, simulation_day
            )
        return reproduction_data_stream

    def _handle_estrus_not_detected_before_ovsynch_start_day(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Redirect cow to OvSynch if estrus was not detected before the OvSynch start day."""

        if self.repro_state_manager.is_in(ReproStateEnum.ENTER_HERD_FROM_INIT):
            self.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"Current repro state(s): {self.repro_state_manager}",
            )

        elif self.repro_state_manager.is_in(ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH):
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                animal_constants.ESTRUS_NOT_DETECTED_BETWEEN_VWP_AND_OVSYNCH_START_DAY_NOTE,
            )
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born, simulation_day, animal_constants.CANCEL_ESTRUS_DETECTION_NOTE
            )
            self.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"Current repro state(s): {self.repro_state_manager}",
            )

        elif self.repro_state_manager.is_in(ReproStateEnum.FRESH):  # When no ED is instituted
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                animal_constants.NO_ED_INSTITUTED_BEFORE_OVSYNCH_IN_ED_TAI_NOTE,
            )
            self.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"Current repro state(s): {self.repro_state_manager}",
            )
        return reproduction_data_stream

    def _decrease_conception_rate_by_parity(self, calves: int, conception_rate: float) -> float:
        """Adjust conception rate based on cow parity."""

        if calves <= 1:
            return conception_rate
        elif calves == 2:
            return conception_rate - 0.05
        else:
            return conception_rate - 0.1

    def _handle_successful_cow_conception(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Handle successful conception for cows, setting pregnancy parameters and scheduling resynch as needed."""
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            f"{animal_constants.SUCCESSFUL_CONCEPTION}, " f"with conception rate at {self.conception_rate}",
        )
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            animal_constants.COW_PREG,
        )
        reproduction_data_stream.days_in_pregnancy = 1
        self.repro_state_manager.enter(ReproStateEnum.PREGNANT)
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            f"Current repro state(s): {self.repro_state_manager}",
        )

        self.gestation_length = self._calculate_gestation_length()
        self.calf_birth_weight = self._calculate_calf_birth_weight(reproduction_data_stream.breed)

        if self.calves > 0:
            last_time_given_birth = reproduction_data_stream.events.get_most_recent_date(animal_constants.NEW_BIRTH)
            self.reproduction_statistics.calving_to_pregnancy_time = (
                reproduction_data_stream.days_in_milk - last_time_given_birth
            )
        if self.cow_reproduction_program in [
            CowReproductionProtocol.TAI,
            CowReproductionProtocol.ED_TAI,
        ]:
            if AnimalConfig.cow_resynch_method == CowReSynchSubProtocol.Resynch_TAIbeforePD:
                reproduction_data_stream = self._schedule_ovsynch_program_in_advance(
                    reproduction_data_stream, simulation_day
                )
                self.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH, keep_existing=True)
                reproduction_data_stream.events.add_event(
                    reproduction_data_stream.days_born,
                    simulation_day,
                    f"Current repro state(s): {self.repro_state_manager}",
                )
        return reproduction_data_stream

    def _handle_failed_cow_conception(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Handle failed conception for cows, scheduling appropriate repro actions based on protocol."""
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            f"{animal_constants.FAILED_CONCEPTION}, " f"with conception rate at " f"{self.conception_rate}",
        )
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            animal_constants.COW_NOT_PREG,
        )

        if self.cow_reproduction_program in [
            CowReproductionProtocol.ED,
            CowReproductionProtocol.ED_TAI,
        ]:
            self.repro_state_manager.enter(ReproStateEnum.WAITING_FULL_ED_CYCLE)
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"Current repro state(s): {self.repro_state_manager}",
            )
            reproduction_data_stream = self._simulate_estrus(
                reproduction_data_stream,
                reproduction_data_stream.days_born,
                simulation_day,
                animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
                AnimalConfig.average_estrus_cycle_cow,
                AnimalConfig.std_estrus_cycle_cow,
            )

        if self.cow_reproduction_program in [
            CowReproductionProtocol.TAI,
            CowReproductionProtocol.ED_TAI,
        ]:
            if AnimalConfig.cow_resynch_method == CowReSynchSubProtocol.Resynch_TAIbeforePD:
                reproduction_data_stream = self._schedule_ovsynch_program_in_advance(
                    reproduction_data_stream, simulation_day
                )

                if self.cow_reproduction_program == CowReproductionProtocol.ED_TAI:
                    # We want to keep the ED protocol running at the same time as the OvSynch program.
                    self.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH, keep_existing=True)
                    reproduction_data_stream.events.add_event(
                        reproduction_data_stream.days_born,
                        simulation_day,
                        f"Current repro state(s): {self.repro_state_manager}",
                    )
                elif self.cow_reproduction_program == CowReproductionProtocol.TAI:
                    self.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
                    reproduction_data_stream.events.add_event(
                        reproduction_data_stream.days_born,
                        simulation_day,
                        f"Current repro state(s): {self.repro_state_manager}",
                    )
        return reproduction_data_stream

    def cow_pregnancy_update(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Update pregnancy status for cows, performing checks on designated pregnancy check days."""

        if reproduction_data_stream.is_pregnant:
            reproduction_data_stream.days_in_pregnancy += 1

        pregnancy_check_configs: list[PregnancyCheckConfig] = [
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

        for pregnancy_check_config in pregnancy_check_configs:
            if reproduction_data_stream.days_born == self.ai_day + pregnancy_check_config["day"]:
                reproduction_data_stream = self._handle_cow_pregnancy_check(
                    reproduction_data_stream, pregnancy_check_config, simulation_day
                )

        return reproduction_data_stream

    def _check_do_not_breed_flag(
        self, simulation_day: int, reproduction_data_stream: ReproductionDataStream
    ) -> ReproductionDataStream:
        """Check if cow should be marked as do-not-breed if not pregnant beyond breeding window."""
        if (
            not reproduction_data_stream.is_pregnant
            and reproduction_data_stream.days_in_milk > AnimalConfig.do_not_breed_time
        ):
            if not self.do_not_breed:
                reproduction_data_stream.events.add_event(
                    reproduction_data_stream.days_born,
                    simulation_day,
                    f"{animal_constants.DO_NOT_BREED}, days in milk: {reproduction_data_stream.days_in_milk}, "
                    f"not pregnant",
                )
                self.do_not_breed = True
        return reproduction_data_stream

    def open_cow(self, reproduction_data_stream: ReproductionDataStream, simulation_day: int) -> ReproductionDataStream:
        """Handle an open cow's status, determining next steps based on reproduction protocol and resynch program."""

        self.num_conception_rate_decreases += 1
        if (
            AnimalConfig.dry_off_day_of_pregnancy <= AnimalConfig.third_pregnancy_check_day
            and not reproduction_data_stream.is_milking
        ):
            self.do_not_breed = True
            return reproduction_data_stream

        if (
            self.cow_reproduction_program == CowReproductionProtocol.ED
            or AnimalConfig.cow_resynch_method == CowReSynchSubProtocol.NONE
        ):
            if reproduction_data_stream.days_born > self.estrus_day:
                self.repro_state_manager.enter(ReproStateEnum.WAITING_FULL_ED_CYCLE)
                reproduction_data_stream.events.add_event(
                    reproduction_data_stream.days_born,
                    simulation_day,
                    f"Current repro state(s): {self.repro_state_manager}",
                )
                reproduction_data_stream.events.add_event(
                    reproduction_data_stream.days_born,
                    simulation_day,
                    f"days in milk: {reproduction_data_stream.days_in_milk}",
                )
                reproduction_data_stream = self._simulate_estrus(
                    reproduction_data_stream,
                    reproduction_data_stream.days_born,
                    simulation_day,
                    animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
                    AnimalConfig.average_estrus_cycle_cow,
                    AnimalConfig.std_estrus_cycle_cow,
                )
            return reproduction_data_stream

        if AnimalConfig.cow_resynch_method == CowReSynchSubProtocol.Resynch_TAIafterPD:
            self.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"Current repro state(s): {self.repro_state_manager}",
            )

        elif AnimalConfig.cow_resynch_method == CowReSynchSubProtocol.Resynch_TAIbeforePD:
            reproduction_data_stream = self._handle_open_cow_in_tai_before_pd_resynch(
                reproduction_data_stream, simulation_day
            )

        elif AnimalConfig.cow_resynch_method == CowReSynchSubProtocol.Resynch_PGFatPD:
            reproduction_data_stream = self._handle_open_cow_in_pgf_at_pd_resynch(
                reproduction_data_stream, simulation_day
            )

        return reproduction_data_stream

    def _handle_open_cow_in_pgf_at_pd_resynch(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Deliver a PGF injection and simulate a short estrus cycle for an open cow in the PGFatPD protocol."""

        single_pgf_injection_schedule = {reproduction_data_stream.days_born: {"deliver_hormones": ["PGF"]}}
        reproduction_data_stream = self._execute_cow_hormone_delivery_schedule(
            reproduction_data_stream, simulation_day, single_pgf_injection_schedule
        )
        self.repro_state_manager.enter(ReproStateEnum.WAITING_SHORT_ED_CYCLE)
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            f"Current repro state(s): {self.repro_state_manager}",
        )
        reproduction_data_stream = self._simulate_estrus(
            reproduction_data_stream,
            reproduction_data_stream.days_born,
            simulation_day,
            animal_constants.SIMULATE_ESTRUS_AFTER_PGF_NOTE,
            AnimalConfig.average_estrus_cycle_after_pgf,
            AnimalConfig.std_estrus_cycle_after_pgf,
            max_cycle_length=animal_constants.MAX_ESTRUS_CYCLE_LENGTH_PGF_AT_PREG_CHECK,
        )

        return reproduction_data_stream

    def _handle_open_cow_in_tai_before_pd_resynch(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """Redirect an open cow in the TAIbeforePD protocol to the OvSynch program and stop estrus detection."""

        if self.repro_state_manager.is_in_empty_state():
            self.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH)
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                f"Current repro state(s): {self.repro_state_manager}",
            )

        if self.repro_state_manager.is_in(ReproStateEnum.WAITING_FULL_ED_CYCLE):
            self.repro_state_manager.exit(ReproStateEnum.WAITING_FULL_ED_CYCLE)
            reproduction_data_stream.events.add_event(
                reproduction_data_stream.days_born,
                simulation_day,
                animal_constants.CANCEL_ESTRUS_DETECTION_NOTE,
            )

        return reproduction_data_stream

    def _schedule_ovsynch_program_in_advance(
        self,
        reproduction_data_stream: ReproductionDataStream,
        simulation_day: int,
        days_before_first_preg_check: int = animal_constants.DAYS_BEFORE_FIRST_PREG_CHECK_TO_START_TAI,
    ) -> ReproductionDataStream:
        """Schedule an OvSynch program in advance for cows in the TAIbeforePD resynch protocol."""

        hormone_schedule_start_day = (
            reproduction_data_stream.days_born + AnimalConfig.first_pregnancy_check_day - days_before_first_preg_check
        )
        reproduction_data_stream = self._set_up_hormone_schedule(
            reproduction_data_stream, hormone_schedule_start_day, AnimalConfig.cow_ovsynch_method.value
        )
        self.TAI_conception_rate = AnimalConfig.ovsynch_program_conception_rate
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            f"{animal_constants.SETTING_UP_OVSYNCH_PROGRAM_IN_ADVANCE_NOTE}: {AnimalConfig.cow_ovsynch_method}",
        )

        return reproduction_data_stream

    def _exit_ovsynch_program_early_when_first_preg_check_passed_or_estrus_detected(
        self, reproduction_data_stream: ReproductionDataStream, simulation_day: int
    ) -> ReproductionDataStream:
        """
        Exit the OvSynch program early in the TAIbeforePD protocol when a pregnancy check is passed
        or estrus is detected.
        """

        self.repro_state_manager.exit(ReproStateEnum.IN_OVSYNCH)
        self.hormone_schedule = {}
        reproduction_data_stream.events.add_event(
            reproduction_data_stream.days_born,
            simulation_day,
            f"{animal_constants.DISCONTINUE_OVSYNCH_PROGRAM_IN_TAI_BEFORE_PD_NOTE}:"
            f" {AnimalConfig.cow_ovsynch_method}",
        )
        return reproduction_data_stream
