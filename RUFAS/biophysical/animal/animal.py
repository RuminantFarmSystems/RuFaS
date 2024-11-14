import sys
from random import random
from typing import Any, Callable

from scipy.stats import truncnorm

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.animal_enums import Breed, Sex, AnimalStatus
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.daily_routines_output import DailyRoutinesOutput
from RUFAS.biophysical.animal.data_types.digestive_system_inputs import DigestiveSystemInputs
from RUFAS.biophysical.animal.data_types.digestive_system_outputs import DigestiveSystemOutputs
from RUFAS.biophysical.animal.data_types.growth_inputs import GrowthInputs
from RUFAS.biophysical.animal.data_types.growth_outputs import GrowthOutputs
from RUFAS.biophysical.animal.data_types.milk_production_inputs import MilkProductionInputs
from RUFAS.biophysical.animal.data_types.milk_production_outputs import MilkProductionOutputs
from RUFAS.biophysical.animal.data_types.nutrients_inputs import NutrientsInputs
from RUFAS.biophysical.animal.data_types.reproduction_io import ReproductionInputs, ReproductionOutputs
from RUFAS.biophysical.animal.digestive_system.digestive_system import DigestiveSystem
from RUFAS.biophysical.animal.growth.growth import Growth
from RUFAS.biophysical.animal.nutrients.nutrients import Nutrients
from RUFAS.biophysical.animal.data_types.animal_statistics import AnimalStatistics
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import AnimalBaseInitArgsTypedDict
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.repro_protocol_enums import HeiferReproductionProtocol
from RUFAS.biophysical.animal.milk.lactation_curve import LactationCurve
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.biophysical.animal.reproduction.reproduction import Reproduction
from RUFAS.time import Time


class Animal:
    animal_type: AnimalType
    birth_date: str
    birth_weight: float
    body_weight: float
    breed: Breed
    sex: Sex
    id: int
    mature_body_weight: float
    net_merit: float
    nutrient: dict[str, float]
    nutrient_concentrations: dict[str, float]
    culled: bool = False
    cull_reason: str = ""
    dead: bool = False
    days_born: int = 0
    days_in_pregnancy: int = 0
    events: AnimalEvents = AnimalEvents()
    days_in_milk: int = 0
    future_cull_date: int = sys.maxsize
    future_death_date: int = sys.maxsize
    ration_formulation = {"objective": 0.00}
    sold: bool = False
    sold_at_day: int = sys.maxsize
    wean_weight: float = 0.0
    metabolizable_energy_intake: float = 0.0

    @property
    def is_pregnant(self) -> bool:
        return self.days_in_pregnancy > 0

    @property
    def is_milking(self) -> bool:
        return self.days_in_milk > 0

    def __init__(self, args: AnimalBaseInitArgsTypedDict) -> None:
        self.id = int(args.get("id"))
        self.breed = Breed(args.get("breed"))
        self.animal_type = AnimalType(args.get("animal_type"))
        self.birth_date = args.get("birth_date")
        self.days_born = int(args.get("days_born"))
        self.birth_weight = float(args.get("birth_weight"))
        self.mature_body_weight = float(truncnorm.rvs(
            -animal_constants.STDI,
            animal_constants.STDI,
            AnimalConfig.average_mature_body_weight,
            AnimalConfig.std_mature_body_weight,
        ))

        self.culled = False

        self.animal_statistics = AnimalStatistics()
        self.growth: Growth = Growth()
        self.animal_statistics: AnimalStatistics = AnimalStatistics()
        self.digestive_system: DigestiveSystem = DigestiveSystem()
        self.milk_production: MilkProduction = MilkProduction()
        self.nutrients: Nutrients = Nutrients()
        self.reproduction: Reproduction = Reproduction(do_not_breed=False)

    @classmethod
    def setup_lactation_curve_parameters(cls, time: Time) -> None:
        LactationCurve.set_lactation_parameters(time)

    def daily_routines(self, time: Time) -> DailyRoutinesOutput:
        self.days_born += 1

        nutrients_inputs = NutrientsInputs(
            animal_type=self.animal_type,
            body_weight=self.body_weight,
            mature_body_weight=self.mature_body_weight,
            daily_growth=self.growth.daily_growth,
            days_in_pregnancy=self.days_in_pregnancy,
            days_in_milk=self.days_in_milk,
            daily_milk_produced=self.milk_production.daily_milk_produced,
        )
        self.nutrients.perform_daily_phosphorus_update(nutrients_inputs)

        digestive_system_inputs = DigestiveSystemInputs(
            animal_type=self.animal_type,
            body_weight=self.body_weight,
            nutrients=self.nutrient,
            nutrient_concentrations=self.nutrient_concentrations,
            days_in_milk=self.days_in_milk,
            metabolizable_energy_intake=self.metabolizable_energy_intake,
            fecal_phosphorus=self.nutrients.fecal_phosphorus,
            urine_phosphorus_required=self.nutrients.urine_phosphorus_required,
            daily_milk_produced=self.milk_production.daily_milk_produced,
            fat_content=self.milk_production.fat_content,
            crude_protein_content=self.milk_production.crude_protein_content,
        )
        digestive_system_outputs: DigestiveSystemOutputs = self.digestive_system.process_digestion(
            digestive_system_inputs)
        self.animal_statistics.methane_emission = digestive_system_outputs.methane_emission
        self.animal_statistics.phosphorus_excreted = digestive_system_outputs.phosphorus_excreted


        milk_production_inputs = MilkProductionInputs(
            days_in_milk=self.days_in_milk,
            days_born=self.days_born,
            days_in_pregnancy=self.days_in_pregnancy,
        )
        milk_production_outputs: MilkProductionOutputs = (
            self.milk_production.perform_daily_milking_update(milk_production_inputs, time)
        )
        self.days_in_milk = milk_production_outputs.days_in_milk
        self.events += milk_production_outputs.events

        growth_inputs = GrowthInputs(
            days_in_pregnancy=self.days_in_pregnancy,
            animal_type=self.animal_type,
            body_weight=self.body_weight,
            mature_body_weight=self.mature_body_weight,
            birth_weight=self.birth_weight,
            days_born=self.days_born,
            days_in_milk=self.days_in_milk,
            conceptus_weight=self.reproduction.conceptus_weight,
            gestation_length=self.reproduction.gestation_length,
            calf_birth_weight=self.reproduction.calf_birth_weight,
            calves=self.reproduction.calves,
            calving_interval=self.reproduction.calving_interval
        )
        growth_outputs: GrowthOutputs = self.growth.evaluate_body_weight_change(growth_inputs, time)
        self.body_weight = growth_outputs.body_weight
        self.events += growth_outputs.events
        self.reproduction.conceptus_weight = growth_outputs.conceptus_weight

        reproduction_inputs = ReproductionInputs(
            animal_type=self.animal_type,
            body_weight=self.body_weight,
            breed=self.breed,
            days_born=self.days_born,
            days_in_pregnancy=self.days_in_pregnancy,
            days_in_milk=self.days_in_milk,
            net_merit=self.net_merit,
            phosphorus_for_gestation_required_for_calf=self.nutrients.phosphorus_for_gestation_required_for_calf
        )
        reproduction_outputs: ReproductionOutputs = self.reproduction.reproduction_update(
            reproduction_inputs, time)
        self.body_weight = reproduction_outputs.body_weight
        self.events += reproduction_outputs.events
        self.days_in_milk = reproduction_outputs.days_in_milk
        self.days_in_pregnancy = reproduction_outputs.days_in_pregnancy
        self.nutrients.phosphorus_for_gestation_required_for_calf = (
            reproduction_outputs.phosphorus_for_gestation_required_for_calf)
        self.future_cull_date = reproduction_outputs.future_cull_date if reproduction_outputs.future_cull_date \
            else self.future_cull_date
        self.future_death_date = reproduction_outputs.future_death_date if reproduction_outputs.future_death_date \
            else self.future_death_date
        self.cull_reason = reproduction_outputs.cull_reason if reproduction_outputs.cull_reason else self.cull_reason


        daily_routines_output: DailyRoutinesOutput = self.animal_life_stage_update()
        if self.animal_type.is_cow and reproduction_outputs.newborn_calf_config:
            daily_routines_output.animal_status = AnimalStatus.NEW_CALF_BORN
            daily_routines_output.animal_values = reproduction_outputs.newborn_calf_config
            self.future_death_date = self.determine_future_death_date()
            self.future_cull_date, self.cull_reason = self.determine_future_cull_date()

        return daily_routines_output

    def animal_life_stage_update(self) -> DailyRoutinesOutput:
        daily_routines_output: DailyRoutinesOutput = DailyRoutinesOutput(
                animal_status=AnimalStatus.REMAIN,
                animal_values=self.get_animal_values()
            )
        if self.animal_type == AnimalType.CALF and self._evaluate_calf_for_heiferI():
            self._transition_calf_to_heiferI()
            daily_routines_output.animal_status = AnimalStatus.LIFE_STAGE_CHANGED
        elif self.animal_type == AnimalType.HEIFER_I and self._evaluate_heiferI_for_heiferII():
            self._transition_heiferI_to_heiferII()
            daily_routines_output.animal_status = AnimalStatus.LIFE_STAGE_CHANGED
        elif self.animal_type == AnimalType.HEIFER_II and self._evaluate_heiferII_for_heiferIII():
            if not self._evaluate_heiferII_for_culling():
                self._transition_heiferII_to_heiferIII()
                daily_routines_output.animal_status = AnimalStatus.LIFE_STAGE_CHANGED
            else:
                self.culled = True
                daily_routines_output.animal_status = AnimalStatus.CULLED
        elif self.animal_type == AnimalType.HEIFER_III and self._evaluate_heiferIII_for_cow():
            self._transition_heiferIII_to_cow()
            daily_routines_output.animal_status = AnimalStatus.LIFE_STAGE_CHANGED

        if self.days_born == self.future_cull_date:
            self.culled = True
            daily_routines_output.animal_status = AnimalStatus.CULLED
        if self.days_born == self.future_death_date:
            self.dead = True
            daily_routines_output.animal_status = AnimalStatus.DEAD
        return daily_routines_output

    def _evaluate_calf_for_heiferI(self) -> bool:
        return self.days_born == AnimalConfig.wean_day

    def _evaluate_heiferI_for_heiferII(self) -> bool:
        return self.days_born == AnimalConfig.heifer_breed_start_day

    def _evaluate_heiferII_for_heiferIII(self) -> bool:
        return (
            self.days_born > AnimalConfig.heifer_breed_start_day
            and self.is_pregnant
            and self.days_in_pregnancy
            > (self.reproduction.gestation_length - AnimalConfig.heifer_prefresh_day)
        )

    def _evaluate_heiferII_for_culling(self) -> bool:
        return (not self.is_pregnant) and (
            self.days_born > AnimalConfig.heifer_reproduction_cull_day
        )

    def _evaluate_heiferIII_for_cow(self) -> bool:
        return self.days_born == self.reproduction.gestation_length

    def _transition_calf_to_heiferI(self) -> None:
        self.animal_type = AnimalType.HEIFER_I

    def _transition_heiferI_to_heiferII(self) -> None:
        self.reproduction.heifer_reproduction_program = AnimalConfig.heifer_reproduction_program
        self.reproduction.heifer_reproduction_sub_program = AnimalConfig.heifer_reproduction_sub_program

        self.reproduction.heifer_tai_method = (
            AnimalConfig.heifer_reproduction_sub_program
            if AnimalConfig.heifer_reproduction_program == HeiferReproductionProtocol.TAI.value
            else ""
        )
        self.reproduction.heifer_synch_ed_method = (
            AnimalConfig.heifer_reproduction_sub_program
            if AnimalConfig.heifer_reproduction_program == HeiferReproductionProtocol.SynchED.value
            else ""
        )

        self.animal_type = AnimalType.HEIFER_II

    def _transition_heiferII_to_heiferIII(self) -> None:
        self.animal_type = AnimalType.HEIFER_III

    def _transition_heiferIII_to_cow(self) -> None:
        self.reproduction.cow_reproduction_program = AnimalConfig.cow_reproduction_program
        self.reproduction.cow_presynch_method = AnimalConfig.cow_presynch_method
        self.reproduction.cow_tai_method = AnimalConfig.cow_tai_method
        self.reproduction.cow_resynch_method = AnimalConfig.cow_resynch_method

        self.animal_type = AnimalType.DRY_COW

    def get_animal_values(self) -> dict[str, Any]:
        mapping: dict[AnimalType, Callable[[], dict[str, Any]]] = {
            AnimalType.CALF: self._get_calf_values,
            AnimalType.HEIFER_I: self._get_heiferI_values,
            AnimalType.HEIFER_II: self._get_heiferII_values,
            AnimalType.HEIFER_III: self._get_heiferIII_values,
            AnimalType.DRY_COW: self._get_cow_values,
            AnimalType.LAC_COW: self._get_cow_values
        }
        return mapping[self.animal_type]()

    def _get_calf_values(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "breed": self.breed,
            "birth_date": self.birth_date,
            "days_born": self.days_born,
            "birth_weight": self.birth_weight,
            "body_weight": self.body_weight,
            "wean_weight": self.wean_weight,
            "mature_body_weight": self.mature_body_weight,
            "events": str(self.events),
            "net_merit": self.net_merit,
        }

    def _get_heiferI_values(self) -> dict[str, Any]:
        return self.get_animal_values()

    def _get_heiferII_values(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "breed": self.breed,
            "birth_date": self.birth_date,
            "days_born": self.days_born,
            "birth_weight": self.birth_weight,
            "body_weight": self.body_weight,
            "wean_weight": self.wean_weight,
            "events": str(self.events),
            "repro_program": self.reproduction.heifer_reproduction_program,
            "repro_sub_protocol": self.reproduction.heifer_reproduction_sub_program,
            "mature_body_weight": self.mature_body_weight,
            "estrus_count": self.animal_statistics.estrus_count,
            "estrus_day": self.reproduction.estrus_day,
            # "tai_program_start_day_h": self.tai_program_start_day,
            # "synch_ed_program_start_day_h": self.synch_ed_program_start_day_h,
            # "synch_ed_estrus_day": self.synch_ed_estrus_day,
            # "synch_ed_stop_day": self.synch_ed_stop_day,
            "conception_rate": self.reproduction.conception_rate,
            "ai_day": self.reproduction.ai_day,
            "abortion_day": self.reproduction.abortion_day,
            "days_in_preg": self.days_in_pregnancy,
            "gestation_length": self.reproduction.gestation_length,
            "p_gest_for_calf": self.nutrients.phosphorus_for_gestation_required_for_calf,
            "calf_birth_weight": self.reproduction.calf_birth_weight,
            "net_merit": self.net_merit,
        }

    def _get_heiferIII_values(self) -> dict[str, Any]:
        return self._get_heiferII_values()

    def _get_cow_values(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "breed": self.breed,
            "birth_date": self.birth_date,
            "days_born": self.days_born,
            "birth_weight": self.birth_weight,
            "body_weight": self.body_weight,
            "wean_weight": self.wean_weight,
            "events": str(self.events),
            "repro_program": self.reproduction.cow_reproduction_program,
            "repro_sub_protocol": self.heifer_reproduction_sub_program,
            "mature_body_weight": self.mature_body_weight,
            "estrus_count": self.animal_statistics.estrus_count,
            "estrus_day": self.reproduction.estrus_day,
            # "tai_program_start_day_h": self.tai_program_start_day_h,
            # "synch_ed_program_start_day_h": self.synch_ed_program_start_day_h,
            # "synch_ed_estrus_day": self.synch_ed_estrus_day,
            # "synch_ed_stop_day": self.synch_ed_stop_day,
            "conception_rate": self.reproduction.conception_rate,
            "ai_day": self.reproduction.ai_day,
            "abortion_day": self.reproduction.abortion_day,
            "days_in_preg": self.days_in_pregnancy,
            "gestation_length": self.reproduction.gestation_length,
            "p_gest_for_calf": self.nutrients.phosphorus_for_gestation_required_for_calf,
            "calf_birth_weight": self.reproduction.calf_birth_weight,
            # "presynch_method": self.presynch_method,
            # "tai_method_c": self.tai_method_c,
            # "resynch_method": self.resynch_method,
            "days_in_milk": self.days_in_milk,
            "parity": self.reproduction.calves,
            "calving_interval": self.reproduction.calving_interval,
            "net_merit": self.net_merit,
        }

    def determine_future_death_date(self) -> int:
        """
        Determine the future death date of the animal based on its parity.

        Returns
        -------
        int
            Calculated future death date in simulation days.
        """
        if self.reproduction.calves >= 4:
            death_rate = AnimalConfig.parity_death_probability[3]
        else:
            death_rate = AnimalConfig.parity_death_probability[self.reproduction.calves - 1]
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
                    death_time_lower_limit = AnimalConfig.cull_day_count[i]
                    death_time_upper_limit = AnimalConfig.cull_day_count[i + 1]
            n = (death_time_upper_limit - death_time_lower_limit) / (death_upper_limit - death_lower_limit)
            return round(
                death_time_lower_limit + n * (death_date_random - death_lower_limit) + self.days_born
            )
        return sys.maxsize

    def determine_future_cull_date(self) -> tuple[int, str]:
        """
        Determine the future cull date and reason for the animal based on parity-specific probabilities.

        Returns
        -------
        tuple[int, str]
            Future cull date in simulation days and reason for culling.
        """
        cull_reason = ""
        future_cull_date = sys.maxsize
        if self.reproduction.calves >= 4:
            inv_cull_rate = AnimalConfig.parity_cull_probability[3]
        else:
            inv_cull_rate = AnimalConfig.parity_cull_probability[self.reproduction.calves - 1]
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
                cull_time_lower_limit + x * (cull_time_rand - cull_reason_lower_limit) + self.days_born
            )

        return future_cull_date, cull_reason