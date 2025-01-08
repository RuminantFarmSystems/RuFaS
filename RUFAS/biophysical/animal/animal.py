import sys
from datetime import datetime, date
from random import random
from typing import Any, Callable, Optional

from scipy.stats import truncnorm

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.animal_enums import Breed, Sex, AnimalStatus
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.body_weight_history import BodyWeightHistory
from RUFAS.biophysical.animal.data_types.daily_routines_output import DailyRoutinesOutput
from RUFAS.biophysical.animal.data_types.digestive_system import DigestiveSystemInputs
from RUFAS.biophysical.animal.data_types.growth import GrowthInputs, GrowthOutputs
from RUFAS.biophysical.animal.data_types.milk_production import MilkProductionInputs, MilkProductionOutputs
from RUFAS.biophysical.animal.data_types.nutrients_inputs import NutrientsInputs
from RUFAS.biophysical.animal.data_types.pen_history import PenHistory
from RUFAS.biophysical.animal.data_types.reproduction import ReproductionInputs, ReproductionOutputs
from RUFAS.biophysical.animal.digestive_system.digestive_system import DigestiveSystem
from RUFAS.biophysical.animal.growth.growth import Growth
from RUFAS.biophysical.animal.nutrients.nutrients import Nutrients
from RUFAS.biophysical.animal.data_types.animal_statistics import AnimalStatistics
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import (NewBornCalfValuesTypedDict, CalfValuesTypedDict,
                                                                    HeiferIValuesTypedDict, HeiferIIValuesTypedDict,
                                                                    CowValuesTypedDict, HeiferIIIValuesTypedDict)
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.repro_protocol_enums import HeiferReproductionProtocol, HeiferTAISubProtocol, \
    HeiferSynchEDSubProtocol
from RUFAS.biophysical.animal.milk.lactation_curve import LactationCurve
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.biophysical.animal.reproduction.reproduction import Reproduction
from RUFAS.time import Time


class Animal:
    """
    DO NOT USE THE PROPERTIES THAT START WITH '_'. INSTEAD, USE THE FUNCTIONS THAT ARE DECORATED WITH @property.
    """
    metabolizable_energy_intake: float = 0.0

    # calf_not_applicable_properties: set[str] = {
    #     "body_weight",
    #     "daily_horizontal_distance",
    #     "daily_vertical_distance",
    #     "dry_matter_intake",
    #     "dry_matter_intake_estimation",
    #     "events",
    #     "nutrient",
    #     "nutrient_concentrations",
    #     "nutrient_requirements",
    # }

    @property
    def days_in_milk(self) -> int:
        if not self.animal_type.is_cow:
            raise TypeError()
        return self._days_in_milk

    @days_in_milk.setter
    def days_in_milk(self, days_in_milk: int) -> None:
        if not self.animal_type.is_cow:
            raise TypeError()
        self._days_in_milk = days_in_milk

    @property
    def days_in_pregnancy(self) -> int:
        if self.animal_type in [AnimalType.CALF, AnimalType.HEIFER_I]:
            raise TypeError()
        return self._days_in_pregnancy

    @days_in_pregnancy.setter
    def days_in_pregnancy(self, days_in_pregnancy: int) -> None:
        if self.animal_type in [AnimalType.CALF, AnimalType.HEIFER_I]:
            raise TypeError()
        self._days_in_pregnancy = days_in_pregnancy

    @property
    def is_pregnant(self) -> bool:
        if self.animal_type in {AnimalType.CALF, AnimalType.HEIFER_I}:
            # check which is more time efficient [] or {} or ()
            raise False
        return self.days_in_pregnancy > 0

    @property
    def is_milking(self) -> bool:
        if not self.animal_type.is_cow:
            return False
        return self.days_in_milk > 0

    @property
    def future_cull_date(self) -> int:
        if not self.animal_type.is_cow:
            return sys.maxsize
        return self._future_cull_date

    @future_cull_date.setter
    def future_cull_date(self, future_cull_date: int) -> None:
        if not self.animal_type.is_cow:
            raise TypeError()
        self._future_cull_date = future_cull_date

    @property
    def future_death_date(self) -> int:
        if not self.animal_type.is_cow:
            return sys.maxsize
        return self._future_death_date

    @future_death_date.setter
    def future_death_date(self, future_death_date: int) -> None:
        if not self.animal_type.is_cow:
            raise TypeError()
        self._future_death_date = future_death_date

    @property
    def daily_horizontal_distance(self) -> float:
        if not self.animal_type.is_cow:
            raise TypeError()
        return self._daily_horizontal_distance

    @daily_horizontal_distance.setter
    def daily_horizontal_distance(self, daily_horizontal_distance: float) -> None:
        if not self.animal_type.is_cow:
            raise TypeError()
        self._daily_horizontal_distance = daily_horizontal_distance

    @property
    def daily_vertical_distance(self) -> float:
        if not self.animal_type.is_cow:
            raise TypeError()
        return self._daily_vertical_distance

    @daily_vertical_distance.setter
    def daily_vertical_distance(self, daily_vertical_distance: float) -> None:
        if not self.animal_type.is_cow:
            raise TypeError()
        self._daily_vertical_distance = daily_vertical_distance

    @property
    def reproduction(self) -> Reproduction:
        return self._reproduction

    @reproduction.setter
    def reproduction(self, reproduction: Reproduction) -> None:
        self._reproduction = reproduction

    def __init__(
            self,
            args: NewBornCalfValuesTypedDict | CalfValuesTypedDict | HeiferIValuesTypedDict |
                   HeiferIIValuesTypedDict | HeiferIIIValuesTypedDict | CowValuesTypedDict) -> None:
        initialize_animal_methods = {
            AnimalType.CALF: self._initialize_calf_or_heiferI,
            AnimalType.HEIFER_I: self._initialize_calf_or_heiferI,
            AnimalType.HEIFER_II: self._initialize_heiferII_or_heiferIII,
            AnimalType.HEIFER_III: self._initialize_heiferII_or_heiferIII,
            AnimalType.LAC_COW: self._initialize_cow,
            AnimalType.DRY_COW: self._initialize_cow
        }
        self.id = int(args.get("id"))
        self.breed = Breed(args.get("breed"))
        self.animal_type = AnimalType(args.get("animal_type"))
        self.birth_date = datetime.strptime(args.get("birth_date"), "%Y-%m-%d").date()
        self.days_born = int(args.get("days_born"))
        self.birth_weight = float(args.get("birth_weight"))
        self.net_merit = args.get("net_merit", 0.0)

        self.cull_reason = ""
        self.body_weight_history: list[BodyWeightHistory] = []
        self.pen_history: list[PenHistory] = []
        self.sold: bool = False
        self.dead: bool = False
        self.sold_at_day: int | None = None
        # remove sold and dead to use sold_at_day and dead_at_day instead
        self.dry_matter_intake: float = 0.0

        self.events = AnimalEvents()

        self.nutrient: dict[str, float] = {}
        self.nutrient_concentrations: dict[str, float] = {}
        self.nutrient_requirements: dict[str, float] = {}

        self.growth: Growth = Growth()
        self.digestive_system: DigestiveSystem = DigestiveSystem()
        self.milk_production: MilkProduction = MilkProduction()
        self.nutrients: Nutrients = Nutrients()
        self._reproduction: Reproduction = Reproduction()

        self.animal_statistics: AnimalStatistics = AnimalStatistics()

        self._days_in_milk: int = 0
        self._days_in_pregnancy: int = 0
        self._future_cull_date: int | None = None
        self._future_death_date: int | None = None
        self._daily_horizontal_distance: float = 0.0
        self._daily_vertical_distance: float = 0.0

        if self.animal_type == AnimalType.CALF and "body_weight" not in args.keys():
            self._initialize_newborn_calf(args)
        else:
            initialize_animal_methods[self.animal_type](args)

    def _initialize_newborn_calf(self, args: NewBornCalfValuesTypedDict) -> None:
        if AnimalConfig.semen_type == "conventional":
            male_calf_rate = AnimalConfig.male_calf_rate_conventional_semen
        elif AnimalConfig.semen_type == "sexed":
            male_calf_rate = AnimalConfig.male_calf_rate_sexed_semen
        else:
            raise ValueError(f"Unexpected semen type: {AnimalConfig.semen_type}")
        self.sex = Sex.MALE if random() < male_calf_rate else Sex.FEMALE

        if random() < AnimalConfig.still_birth_rate:
            self.sold = True
            self.events.add_event(0, 0, animal_constants.STILL_BIRTH)

        self.sold = True if (self.sex == Sex.MALE or random() > AnimalConfig.keep_female_calf_rate) else False

        self.birth_weight = args.get("birth_weight")
        self.body_weight = args.get("birth_weight")
        self.wean_weight = 0.0
        self.mature_body_weight = float(truncnorm.rvs(
            -animal_constants.STDI,
            animal_constants.STDI,
            AnimalConfig.average_mature_body_weight,
            AnimalConfig.std_mature_body_weight,
        ))
        self.nutrients.total_phosphorus_in_animal = args.get("initial_phosphorus")

    def _initialize_calf_or_heiferI(self, args: CalfValuesTypedDict | HeiferIValuesTypedDict) -> None:
        self.sold = False
        self.sex = Sex.FEMALE
        self.birth_weight = args.get("birth_weight")
        self.body_weight = args.get("body_weight")
        self.wean_weight = args.get("wean_weight")
        self.mature_body_weight = args.get("mature_body_weight")
        self.events.init_from_string(args.get("events"))

    def _initialize_heiferII_or_heiferIII(self, args: HeiferIIValuesTypedDict | HeiferIIIValuesTypedDict) -> None:
        self._initialize_calf_or_heiferI(args)
        heifer_reproduction_program = HeiferReproductionProtocol(args.get("heifer_repro_program"))
        heifer_reproduction_sub_program = None
        if heifer_reproduction_program == HeiferReproductionProtocol.TAI:
            heifer_reproduction_sub_program = HeiferTAISubProtocol(args.get("heifer_repro_sub_protocol"))
        elif heifer_reproduction_program == HeiferReproductionProtocol.SynchED:
            heifer_reproduction_sub_program = HeiferSynchEDSubProtocol(args.get("heifer_repro_sub_protocol"))
        self.days_in_pregnancy = args.get("days_in_pregnancy", 0)
        self.reproduction = Reproduction(
            heifer_reproduction_program=heifer_reproduction_program,
            heifer_reproduction_sub_program=heifer_reproduction_sub_program,
            ai_day=args.get("ai_day", 0),
            estrus_count=args.get("estrus_count", 0),
            estrus_day=args.get("estrus_day", 0),
            abortion_day=args.get("abortion_day", 0),
            conception_rate=args.get("conception_rate", 0),
            gestation_length=args.get("gestation_length", 0),
            calf_birth_weight=args.get("calf_birth_weight", 0)
        )
        self.nutrients.phosphorus_for_gestation_required_for_calf = args.get(
            "phosphorus_for_gestation_required_for_calf", 0)

    def _initialize_cow(self, args: CowValuesTypedDict) -> None:
        self._initialize_heiferII_or_heiferIII(args)
        self.days_in_milk = args.get("days_in_milk", 0)
        self.reproduction.calves = args.get("calves", 0)
        self.reproduction.calving_interval = args.get("calving_interval", 0)


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
        self.digestive_system.process_digestion(digestive_system_inputs)


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


        daily_routines_output: DailyRoutinesOutput = self.animal_life_stage_update(time.simulation_day)
        if self.animal_type.is_cow and reproduction_outputs.newborn_calf_config:
            daily_routines_output.animal_status = AnimalStatus.NEW_CALF_BORN
            daily_routines_output.animal_values = reproduction_outputs.newborn_calf_config

        return daily_routines_output

    def animal_life_stage_update(self, simulation_day: int) -> DailyRoutinesOutput:
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
                self.sold = True
                daily_routines_output.animal_status = AnimalStatus.SOLD
        elif self.animal_type == AnimalType.HEIFER_III and self._evaluate_heiferIII_for_cow():
            self._transition_heiferIII_to_cow()
            daily_routines_output.animal_status = AnimalStatus.LIFE_STAGE_CHANGED
        elif self.animal_type == AnimalType.LAC_COW and self.is_milking == False:
            self.animal_type = AnimalType.DRY_COW
            daily_routines_output.animal_status = AnimalStatus.LIFE_STAGE_CHANGED
        elif self.animal_type == AnimalType.DRY_COW and self.is_milking == True:
            self.animal_type = AnimalType.LAC_COW
            daily_routines_output.animal_status = AnimalStatus.LIFE_STAGE_CHANGED

        if self.days_born == self.future_cull_date:
            self.sold = True
            self.sold_at_day = simulation_day
            daily_routines_output.animal_status = AnimalStatus.SOLD
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
            "repro_sub_protocol": self.reproduction.heifer_reproduction_sub_program,
            "mature_body_weight": self.mature_body_weight,
            "estrus_count": self.animal_statistics.estrus_count,
            "estrus_day": self.reproduction.estrus_day,
            "conception_rate": self.reproduction.conception_rate,
            "ai_day": self.reproduction.ai_day,
            "abortion_day": self.reproduction.abortion_day,
            "days_in_preg": self.days_in_pregnancy,
            "gestation_length": self.reproduction.gestation_length,
            "p_gest_for_calf": self.nutrients.phosphorus_for_gestation_required_for_calf,
            "calf_birth_weight": self.reproduction.calf_birth_weight,
            "days_in_milk": self.days_in_milk,
            "parity": self.reproduction.calves,
            "calving_interval": self.reproduction.calving_interval,
            "net_merit": self.net_merit,
        }

    def update_pen_history(self, current_pen: int, current_day: int, animal_types_in_pen: set[AnimalType]) -> None:
        """
        Updates the animal's pen history by either appending to the existing
        history if the animal is in a different pen than it was the last time
        this method is called or modifying the last element in the pen_history
        list to reflect the current simulation day.

        Args:
            curr_pen: the pen that the animal is currently in
            curr_day: the current simulation day
            classes_in_pen: the classes in the animal's current pen
        """
        last_pen = self.pen_history[-1]["pen"] if len(self.pen_history) > 0 else None
        if last_pen is None or last_pen != current_pen:
            self.pen_history.append(
                PenHistory(start_date=current_day, end_date=current_day, pen=current_pen,
                           animal_types_in_pen=list(animal_types_in_pen))
            )
        else:  # last_pen == curr_pen
            self.pen_history[-1]["end_date"] = current_day
            self.pen_history[-1]["animal_types_in_pen"] = list(animal_types_in_pen)

    def calculate_daily_walking_distance(self, vertical_dist_to_parlor: float, horizontal_dist_to_parlor: float) -> float:
        """
        Calculates and sets the animal's daily vertical and horizontal
        walking distance (DVD and DHD).

        Parameters
        ----------
        vertical_dist_to_parlor : float
            Vertical distance to milking parlor (km).
        horizontal_dist_to_parlor : float
            Horizontal distance to milking parlor, km.

        """
        if not self.animal_type.is_cow:
            raise ValueError("Cannot calculate daily walking distance for animal types other than cow.")
        self.daily_vertical_distance = 2 * vertical_dist_to_parlor * AnimalConfig.cow_times_milked_per_day
        self.daily_horizontal_distance = 2 * horizontal_dist_to_parlor * AnimalConfig.cow_times_milked_per_day