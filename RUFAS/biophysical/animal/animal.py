import sys
from datetime import datetime
from random import random
from typing import Any, Callable

from scipy.stats import truncnorm
from numpy import sqrt

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_enums import Breed, Sex, AnimalStatus
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.body_weight_history import BodyWeightHistory
from RUFAS.biophysical.animal.data_types.daily_routines_output import DailyRoutinesOutput
from RUFAS.biophysical.animal.data_types.digestive_system import DigestiveSystemInputs
from RUFAS.biophysical.animal.data_types.growth import GrowthInputs, GrowthOutputs
from RUFAS.biophysical.animal.data_types.milk_production import MilkProductionInputs, MilkProductionOutputs
from RUFAS.biophysical.animal.data_types.nutrients_inputs import NutrientsInputs
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements, NutritionSupply
from RUFAS.biophysical.animal.data_types.pen_history import PenHistory
from RUFAS.biophysical.animal.data_types.reproduction import ReproductionInputs, ReproductionOutputs
from RUFAS.biophysical.animal.digestive_system.digestive_system import DigestiveSystem
from RUFAS.biophysical.animal.growth.growth import Growth
from RUFAS.biophysical.animal.nutrients.nutrients import Nutrients
from RUFAS.biophysical.animal.nutrients.nasem_requirements_calculator import NASEMRequirementsCalculator
from RUFAS.biophysical.animal.nutrients.nrc_requirements_calculator import NRCRequirementsCalculator
from RUFAS.biophysical.animal.data_types.animal_statistics import AnimalStatistics
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import (
    NewBornCalfValuesTypedDict,
    CalfValuesTypedDict,
    HeiferIValuesTypedDict,
    HeiferIIValuesTypedDict,
    CowValuesTypedDict,
    HeiferIIIValuesTypedDict,
)
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.repro_protocol_enums import (
    HeiferReproductionProtocol,
    HeiferTAISubProtocol,
    HeiferSynchEDSubProtocol,
)
from RUFAS.biophysical.animal.milk.lactation_curve import LactationCurve
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements
from RUFAS.biophysical.animal.ration.calf_ration_manager import CalfRationManager
from RUFAS.biophysical.animal.reproduction.reproduction import Reproduction
from RUFAS.data_structures.feed_storage_to_animal_connection import NutrientStandard, Feed
from RUFAS.general_constants import GeneralConstants
from RUFAS.time import Time


class Animal:
    """
    DO NOT USE THE PROPERTIES THAT START WITH '_'. INSTEAD, USE THE FUNCTIONS THAT ARE DECORATED WITH @property.
    """

    metabolizable_energy_intake: float = 0.0
    nutrient_standard: NutrientStandard

    @classmethod
    def set_nutrient_standard(cls, nutrient_standard: NutrientStandard) -> None:
        """Setter for nutrient standard class attribute."""
        cls.nutrient_standard = nutrient_standard

    @property
    def days_in_milk(self) -> int:
        if not self.animal_type.is_cow:
            return 0
        return self._days_in_milk

    @days_in_milk.setter
    def days_in_milk(self, days_in_milk: int) -> None:
        if not self.animal_type.is_cow:
            self._days_in_milk = 0
        self._days_in_milk = days_in_milk

    @property
    def days_in_pregnancy(self) -> int:
        if self.animal_type in [AnimalType.CALF, AnimalType.HEIFER_I]:
            return 0
        return self._days_in_pregnancy

    @days_in_pregnancy.setter
    def days_in_pregnancy(self, days_in_pregnancy: int) -> None:
        if self.animal_type in [AnimalType.CALF, AnimalType.HEIFER_I]:
            raise TypeError()
        self._days_in_pregnancy = days_in_pregnancy

    @property
    def is_pregnant(self) -> bool:
        if self.animal_type in {AnimalType.CALF, AnimalType.HEIFER_I}:
            return False
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
    def daily_distance(self) -> float:
        if not self.animal_type.is_cow and self.is_milking:
            return 0.0
        return self._daily_distance

    @daily_distance.setter
    def daily_distance(self, daily_distance: float) -> None:
        if not self.animal_type.is_cow:
            raise TypeError()
        self._daily_distance = daily_distance

    @property
    def reproduction(self) -> Reproduction:
        return self._reproduction

    @reproduction.setter
    def reproduction(self, reproduction: Reproduction) -> None:
        self._reproduction = reproduction

    @property
    def sold(self) -> bool:
        return True if (self.sold_at_day is not None and self.sold_at_day >= 0) else False

    @property
    def dead(self) -> bool:
        return True if (self.dead_at_day is not None and self.dead_at_day >= 0) else False

    def __init__(
        self,
        args: (
            NewBornCalfValuesTypedDict
            | CalfValuesTypedDict
            | HeiferIValuesTypedDict
            | HeiferIIValuesTypedDict
            | HeiferIIIValuesTypedDict
            | CowValuesTypedDict
        ),
        simulation_day: int = 0
    ) -> None:
        initialize_animal_methods = {
            AnimalType.CALF: self._initialize_calf_or_heiferI,
            AnimalType.HEIFER_I: self._initialize_calf_or_heiferI,
            AnimalType.HEIFER_II: self._initialize_heiferII_or_heiferIII,
            AnimalType.HEIFER_III: self._initialize_heiferII_or_heiferIII,
            AnimalType.LAC_COW: self._initialize_cow,
            AnimalType.DRY_COW: self._initialize_cow,
        }
        self.id = int(args.get("id"))
        self.breed: Breed = Breed(Breed[args.get("breed")])
        self.animal_type = AnimalType(args.get("animal_type"))
        self.days_born = int(args.get("days_born"))
        self.birth_weight = float(args.get("birth_weight"))
        self.net_merit = args.get("net_merit", 0.0)
        self.body_condition_score_5 = AnimalModuleConstants.DEFAULT_BODY_CONDITION_SCORE_5

        self.cull_reason = ""
        self.body_weight_history: list[BodyWeightHistory] = []
        self.pen_history: list[PenHistory] = []
        self.sold_at_day: int | None = None
        self.dead_at_day: int | None = None
        self.events = AnimalEvents()

        self.growth: Growth = Growth()
        self.digestive_system: DigestiveSystem = DigestiveSystem()
        self.milk_production: MilkProduction = MilkProduction()
        self.nutrients: Nutrients = Nutrients()
        self._reproduction: Reproduction = Reproduction()
        self.nutrition_requirements: NutritionRequirements = NutritionRequirements.make_empty_nutrition_requirements()
        self.nutrition_supply: NutritionSupply = NutritionSupply.make_empty_nutrition_supply()
        self.nutrition_supply.dry_matter = AnimalModuleConstants.DEFAULT_DRY_MATTER_INTAKE
        self.previous_nutrition_supply: NutritionSupply | None = None

        self.animal_statistics: AnimalStatistics = AnimalStatistics()

        self._days_in_milk: int = 0
        self._days_in_pregnancy: int = 0
        self._future_cull_date: int | None = None
        self._future_death_date: int | None = None
        self._daily_horizontal_distance: float = 0.0
        self._daily_vertical_distance: float = 0.0
        self._daily_distance: float = 0.0

        if self.animal_type == AnimalType.CALF and "body_weight" not in args.keys():
            self._initialize_newborn_calf(args, simulation_day)
        else:
            initialize_animal_methods[self.animal_type](args)

    def _initialize_newborn_calf(self, args: NewBornCalfValuesTypedDict, simulation_day: int) -> None:
        if AnimalConfig.semen_type == "conventional":
            male_calf_rate = AnimalConfig.male_calf_rate_conventional_semen
        elif AnimalConfig.semen_type == "sexed":
            male_calf_rate = AnimalConfig.male_calf_rate_sexed_semen
        else:
            raise ValueError(f"Unexpected semen type: {AnimalConfig.semen_type}")
        self.sex = Sex.MALE if random() < male_calf_rate else Sex.FEMALE

        if random() < AnimalConfig.still_birth_rate:
            self.sold_at_day = simulation_day
            self.events.add_event(0, 0, animal_constants.STILL_BIRTH)

        is_sold = True if (self.sex == Sex.MALE or random() > AnimalConfig.keep_female_calf_rate) else False
        self.sold_at_day = simulation_day if is_sold else None

        self.birth_weight = args.get("birth_weight")
        self.body_weight = args.get("birth_weight")
        self.wean_weight = 0.0
        self.mature_body_weight = float(
            truncnorm.rvs(
                -animal_constants.STDI,
                animal_constants.STDI,
                AnimalConfig.average_mature_body_weight,
                AnimalConfig.std_mature_body_weight,
            )
        )
        self.nutrients.total_phosphorus_in_animal = args.get("initial_phosphorus")

    def _initialize_calf_or_heiferI(self, args: CalfValuesTypedDict | HeiferIValuesTypedDict) -> None:
        self.sex = Sex.FEMALE
        self.birth_weight = args.get("birth_weight")
        self.body_weight = args.get("body_weight")
        self.wean_weight = args.get("wean_weight")
        self.mature_body_weight = args.get("mature_body_weight")
        self.events.init_from_string(args.get("events"))

    def _initialize_heiferII_or_heiferIII(self, args: HeiferIIValuesTypedDict | HeiferIIIValuesTypedDict) -> None:
        self._initialize_calf_or_heiferI(args)
        heifer_reproduction_program_string = args.get("heifer_reproduction_program")
        heifer_reproduction_program, heifer_reproduction_sub_program = None, None

        heifer_reproduction_program = (
            None
            if heifer_reproduction_program_string == "N/A"
            else HeiferReproductionProtocol(heifer_reproduction_program_string)
        )
        if heifer_reproduction_program == HeiferReproductionProtocol.TAI:
            heifer_reproduction_sub_program = HeiferTAISubProtocol(args.get("heifer_reproduction_sub_protocol"))
        elif heifer_reproduction_program == HeiferReproductionProtocol.SynchED:
            heifer_reproduction_sub_program = HeiferSynchEDSubProtocol(args.get("heifer_reproduction_sub_protocol"))
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
            calf_birth_weight=args.get("calf_birth_weight", 0),
        )
        self.nutrients.phosphorus_for_gestation_required_for_calf = args.get(
            "phosphorus_for_gestation_required_for_calf", 0
        )

    def _initialize_cow(self, args: CowValuesTypedDict) -> None:
        self._initialize_heiferII_or_heiferIII(args)
        self.days_in_milk = args.get("days_in_milk", 0)
        self.reproduction.calves = args.get("parity", 0)

        calving_interval = args.get("calving_interval", AnimalConfig.calving_interval)
        self.reproduction.calving_interval = calving_interval if calving_interval > 0 else AnimalConfig.calving_interval

        if self.reproduction.calves > 0:
            wood_parameters = LactationCurve.get_wood_parameters(self.reproduction.calves)
            self.milk_production.set_wood_parameters(wood_parameters["l"], wood_parameters["m"], wood_parameters["n"])

    @classmethod
    def setup_lactation_curve_parameters(cls, time: Time) -> None:
        LactationCurve.set_lactation_parameters(time)

    def reduce_milk_production(self) -> bool:
        """
        Attempts reduction of milk production.

        Returns
        -------
        bool
            True if the reduction was successful, False otherwise.

        """
        is_milk_reduction_too_high = (
            self.milk_production.milk_production_reduction + AnimalModuleConstants.MILK_REDUCTION_KG
        ) > AnimalModuleConstants.MAXIMUM_MILK_REDUCTION
        if is_milk_reduction_too_high is True:
            return False
        self.milk_production.milk_production_reduction += AnimalModuleConstants.MILK_REDUCTION_KG
        return True

    def daily_routines(self, time: Time) -> DailyRoutinesOutput:
        self.days_born += 1
        daily_routines_output: DailyRoutinesOutput = DailyRoutinesOutput(
            animal_status=AnimalStatus.REMAIN, animal_values=self.get_animal_values()
        )

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
            nutrients=self.nutrition_supply,
            days_in_milk=self.days_in_milk,
            metabolizable_energy_intake=self.metabolizable_energy_intake,
            fecal_phosphorus=self.nutrients.fecal_phosphorus,
            urine_phosphorus_required=self.nutrients.urine_phosphorus_required,
            daily_milk_produced=self.milk_production.daily_milk_produced,
            fat_content=self.milk_production.fat_content,
            crude_protein_content=self.milk_production.crude_protein_content,
        )
        self.digestive_system.process_digestion(digestive_system_inputs)

        if self.animal_type.is_cow:
            milk_production_inputs = MilkProductionInputs(
                days_in_milk=self.days_in_milk,
                days_born=self.days_born,
                days_in_pregnancy=self.days_in_pregnancy,
            )
            milk_production_outputs: MilkProductionOutputs = self.milk_production.perform_daily_milking_update(
                milk_production_inputs, time
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
            calving_interval=self.reproduction.calving_interval,
        )
        growth_outputs: GrowthOutputs = self.growth.evaluate_body_weight_change(growth_inputs, time)
        self.body_weight = growth_outputs.body_weight
        self.events += growth_outputs.events
        self.reproduction.conceptus_weight = growth_outputs.conceptus_weight

        if self.animal_type == AnimalType.HEIFER_II or self.animal_type.is_cow:
            reproduction_inputs = ReproductionInputs(
                animal_type=self.animal_type,
                body_weight=self.body_weight,
                breed=self.breed,
                days_born=self.days_born,
                days_in_pregnancy=self.days_in_pregnancy,
                days_in_milk=self.days_in_milk,
                net_merit=self.net_merit,
                phosphorus_for_gestation_required_for_calf=self.nutrients.phosphorus_for_gestation_required_for_calf,
            )
            reproduction_outputs: ReproductionOutputs = self.reproduction.reproduction_update(reproduction_inputs, time)

            self.body_weight = reproduction_outputs.body_weight
            if self.animal_type.is_cow:
                self.days_in_milk = reproduction_outputs.days_in_milk
            self.days_in_pregnancy = reproduction_outputs.days_in_pregnancy
            self.nutrients.phosphorus_for_gestation_required_for_calf = (
                reproduction_outputs.phosphorus_for_gestation_required_for_calf
            )

            if self.animal_type.is_cow and reproduction_outputs.newborn_calf_config:
                daily_routines_output.animal_status = AnimalStatus.NEW_CALF_BORN
                daily_routines_output.animal_values = reproduction_outputs.newborn_calf_config
                if self.reproduction.calves >= 2:
                    self.reproduction.calving_interval = self.days_born - self.events.get_most_recent_date(
                        animal_constants.NEW_BIRTH
                    )
                    self.reproduction.calving_interval_history.append(self.reproduction.calving_interval)

                wood_parameters = LactationCurve.get_wood_parameters(self.reproduction.calves)
                self.milk_production.set_wood_parameters(
                    wood_parameters["l"], wood_parameters["m"], wood_parameters["n"]
                )
                self.future_death_date = self.determine_future_death_date()
                self.future_cull_date, self.cull_reason = self.determine_future_cull_date()
            self.events += reproduction_outputs.events

        daily_routines_output = self.animal_life_stage_update(time, daily_routines_output)

        if self.animal_type == AnimalType.HEIFER_III and self.is_pregnant:
            self.days_in_pregnancy += 1


        return daily_routines_output

    def animal_life_stage_update(self, time: Time, daily_routines_output: DailyRoutinesOutput) -> DailyRoutinesOutput:
        if self.animal_type == AnimalType.CALF and self._evaluate_calf_for_heiferI():
            self._transition_calf_to_heiferI()
            daily_routines_output.animal_status = AnimalStatus.LIFE_STAGE_CHANGED
        elif self.animal_type == AnimalType.HEIFER_I and self._evaluate_heiferI_for_heiferII():
            self._transition_heiferI_to_heiferII(time)
            daily_routines_output.animal_status = AnimalStatus.LIFE_STAGE_CHANGED
        elif self.animal_type == AnimalType.HEIFER_II:
            if self._evaluate_heiferII_for_culling():
                self.sold_at_day = time.simulation_day
                daily_routines_output.animal_status = AnimalStatus.SOLD
            elif self._evaluate_heiferII_for_heiferIII():
                self._transition_heiferII_to_heiferIII()
                daily_routines_output.animal_status = AnimalStatus.LIFE_STAGE_CHANGED
        elif self.animal_type == AnimalType.HEIFER_III and self._evaluate_heiferIII_for_cow():
            new_born_calf_config = self._transition_heiferIII_to_cow(time)
            daily_routines_output.animal_status = AnimalStatus.NEW_CALF_BORN
            daily_routines_output.animal_values = new_born_calf_config
        elif self.animal_type == AnimalType.LAC_COW and self.is_milking == False:
            self.animal_type = AnimalType.DRY_COW
            daily_routines_output.animal_status = AnimalStatus.LIFE_STAGE_CHANGED

        if self.animal_type == AnimalType.DRY_COW and self.is_milking:
            self.animal_type = AnimalType.LAC_COW
            daily_routines_output.animal_status = AnimalStatus.LIFE_STAGE_CHANGED

        if self.days_born == self.future_cull_date:
            self.sold_at_day = time.simulation_day
            daily_routines_output.animal_status = AnimalStatus.SOLD
        if self.days_born == self.future_death_date:
            self.dead_at_day = time.simulation_day
            self.cull_reason = animal_constants.DEATH_CULL
            daily_routines_output.animal_status = AnimalStatus.DEAD
        if self.animal_type.is_cow and self.reproduction.do_not_breed and self.milk_production.daily_milk_produced < AnimalConfig.cull_milk_production:
            self.cull_reason = animal_constants.LOW_PROD_CULL
            self.sold_at_day = time.simulation_day
            daily_routines_output.animal_status = AnimalStatus.SOLD
        return daily_routines_output

    def _evaluate_calf_for_heiferI(self) -> bool:
        return self.days_born == AnimalConfig.wean_day

    def _evaluate_heiferI_for_heiferII(self) -> bool:
        return self.days_born == AnimalConfig.heifer_breed_start_day

    def _evaluate_heiferII_for_heiferIII(self) -> bool:
        return (
            self.days_born > AnimalConfig.heifer_breed_start_day
            and self.is_pregnant
            and self.days_in_pregnancy > (self.reproduction.gestation_length - AnimalConfig.heifer_prefresh_day)
        )

    def _evaluate_heiferII_for_culling(self) -> bool:
        return (not self.is_pregnant) and (self.days_born > AnimalConfig.heifer_reproduction_cull_day)

    def _evaluate_heiferIII_for_cow(self) -> bool:
        return self.days_in_pregnancy == self.reproduction.gestation_length

    def _transition_calf_to_heiferI(self) -> None:
        self.animal_type = AnimalType.HEIFER_I

    def _transition_heiferI_to_heiferII(self, time: Time) -> None:
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

        reproduction_inputs = ReproductionInputs(
            animal_type=self.animal_type,
            body_weight=self.body_weight,
            breed=self.breed,
            days_born=self.days_born,
            days_in_pregnancy=self.days_in_pregnancy,
            days_in_milk=self.days_in_milk,
            net_merit=self.net_merit,
            phosphorus_for_gestation_required_for_calf=self.nutrients.phosphorus_for_gestation_required_for_calf,
        )
        reproduction_outputs: ReproductionOutputs = self.reproduction.reproduction_update(reproduction_inputs, time)
        self.body_weight = reproduction_outputs.body_weight
        self.events += reproduction_outputs.events
        self.days_in_pregnancy = reproduction_outputs.days_in_pregnancy
        self.nutrients.phosphorus_for_gestation_required_for_calf = (
            reproduction_outputs.phosphorus_for_gestation_required_for_calf
        )

    def _transition_heiferII_to_heiferIII(self) -> None:
        self.animal_type = AnimalType.HEIFER_III

    def _transition_heiferIII_to_cow(self, time: Time) -> NewBornCalfValuesTypedDict:
        self.reproduction.cow_reproduction_program = AnimalConfig.cow_reproduction_program
        self.reproduction.cow_presynch_method = AnimalConfig.cow_presynch_method
        self.reproduction.cow_tai_method = AnimalConfig.cow_tai_method
        self.reproduction.cow_resynch_method = AnimalConfig.cow_resynch_method

        self.reproduction.calving_interval = AnimalConfig.calving_interval

        self.animal_type = AnimalType.LAC_COW

        reproduction_inputs = ReproductionInputs(
            animal_type=self.animal_type,
            body_weight=self.body_weight,
            breed=self.breed,
            days_born=self.days_born,
            days_in_pregnancy=self.days_in_pregnancy,
            days_in_milk=self.days_in_milk,
            net_merit=self.net_merit,
            phosphorus_for_gestation_required_for_calf=self.nutrients.phosphorus_for_gestation_required_for_calf,
        )
        reproduction_outputs: ReproductionOutputs = self.reproduction.reproduction_update(reproduction_inputs, time)

        self.body_weight = reproduction_outputs.body_weight
        self.events += reproduction_outputs.events
        if self.animal_type.is_cow:
            self.days_in_milk = reproduction_outputs.days_in_milk
        self.days_in_pregnancy = reproduction_outputs.days_in_pregnancy
        self.nutrients.phosphorus_for_gestation_required_for_calf = (
            reproduction_outputs.phosphorus_for_gestation_required_for_calf
        )
        wood_parameters = LactationCurve.get_wood_parameters(self.reproduction.calves)
        self.milk_production.set_wood_parameters(
            wood_parameters["l"], wood_parameters["m"], wood_parameters["n"]
        )
        return reproduction_outputs.newborn_calf_config

    def get_animal_values(self) -> dict[str, Any]:
        mapping: dict[AnimalType, Callable[[], dict[str, Any]]] = {
            AnimalType.CALF: self._get_calf_values,
            AnimalType.HEIFER_I: self._get_heiferI_values,
            AnimalType.HEIFER_II: self._get_heiferII_values,
            AnimalType.HEIFER_III: self._get_heiferIII_values,
            AnimalType.DRY_COW: self._get_cow_values,
            AnimalType.LAC_COW: self._get_cow_values,
        }
        return mapping[self.animal_type]()

    def _get_calf_values(self) -> CalfValuesTypedDict:
        return CalfValuesTypedDict(
            id=self.id,
            breed=self.breed.value,
            animal_type=self.animal_type.value,
            days_born=self.days_born,
            birth_weight=self.birth_weight,
            body_weight=self.body_weight,
            wean_weight=self.wean_weight,
            mature_body_weight=self.mature_body_weight,
            events=str(self.events),
            net_merit=self.net_merit,
        )

    def _get_heiferI_values(self) -> HeiferIValuesTypedDict:
        return HeiferIValuesTypedDict(
            id=self.id,
            breed=self.breed.value,
            animal_type=self.animal_type.value,
            days_born=self.days_born,
            birth_weight=self.birth_weight,
            body_weight=self.body_weight,
            wean_weight=self.wean_weight,
            mature_body_weight=self.mature_body_weight,
            events=str(self.events),
            net_merit=self.net_merit,
        )

    def _get_heiferII_values(self) -> HeiferIIValuesTypedDict:
        return HeiferIIValuesTypedDict(
            id=self.id,
            breed=self.breed.value,
            animal_type=self.animal_type.value,
            days_born=self.days_born,
            birth_weight=self.birth_weight,
            body_weight=self.body_weight,
            wean_weight=self.wean_weight,
            mature_body_weight=self.mature_body_weight,
            events=str(self.events),
            net_merit=self.net_merit,
            heifer_reproduction_program=self.reproduction.heifer_reproduction_program.value,
            heifer_reproduction_sub_protocol=self.reproduction.heifer_reproduction_sub_program.value,
            estrus_count=self.animal_statistics.estrus_count,
            estrus_day=self.reproduction.estrus_day,
            conception_rate=self.reproduction.conception_rate,
            ai_day=self.reproduction.ai_day,
            abortion_day=self.reproduction.abortion_day,
            days_in_pregnancy=self.days_in_pregnancy,
            gestation_length=self.reproduction.gestation_length,
            phosphorus_for_gestation_required_for_calf=self.nutrients.phosphorus_for_gestation_required_for_calf,
            calf_birth_weight=self.reproduction.calf_birth_weight,
        )

    def _get_heiferIII_values(self) -> HeiferIIIValuesTypedDict:
        return HeiferIIIValuesTypedDict(
            id=self.id,
            breed=self.breed.value,
            animal_type=self.animal_type.value,
            days_born=self.days_born,
            birth_weight=self.birth_weight,
            body_weight=self.body_weight,
            wean_weight=self.wean_weight,
            mature_body_weight=self.mature_body_weight,
            events=str(self.events),
            net_merit=self.net_merit,
            heifer_reproduction_program=self.reproduction.heifer_reproduction_program.value,
            heifer_reproduction_sub_protocol=self.reproduction.heifer_reproduction_sub_program.value,
            estrus_count=self.animal_statistics.estrus_count,
            estrus_day=self.reproduction.estrus_day,
            conception_rate=self.reproduction.conception_rate,
            ai_day=self.reproduction.ai_day,
            abortion_day=self.reproduction.abortion_day,
            days_in_pregnancy=self.days_in_pregnancy,
            gestation_length=self.reproduction.gestation_length,
            phosphorus_for_gestation_required_for_calf=self.nutrients.phosphorus_for_gestation_required_for_calf,
            calf_birth_weight=self.reproduction.calf_birth_weight,
        )

    def _get_cow_values(self) -> CowValuesTypedDict:
        return CowValuesTypedDict(
            id=self.id,
            breed=self.breed.value,
            animal_type=self.animal_type.value,
            days_born=self.days_born,
            birth_weight=self.birth_weight,
            body_weight=self.body_weight,
            wean_weight=self.wean_weight,
            mature_body_weight=self.mature_body_weight,
            events=str(self.events),
            net_merit=self.net_merit,
            calf_birth_weight=self.reproduction.calf_birth_weight,
            heifer_reproduction_program=self.reproduction.heifer_reproduction_program.value,
            heifer_reproduction_sub_protocol=self.reproduction.heifer_reproduction_sub_program.value,
            cow_reproduction_program=self.reproduction.cow_reproduction_program.value,
            cow_presynch_program=self.reproduction.cow_presynch_program.value,
            cow_ovsynch_program=self.reproduction.cow_ovsynch_program.value,
            cow_resynch_program=self.reproduction.cow_resynch_program.value,
            estrus_count=self.animal_statistics.estrus_count,
            estrus_day=self.reproduction.estrus_day,
            conception_rate=self.reproduction.conception_rate,
            ai_day=self.reproduction.ai_day,
            abortion_day=self.reproduction.abortion_day,
            days_in_pregnancy=self.days_in_pregnancy,
            gestation_length=self.reproduction.gestation_length,
            phosphorus_for_gestation_required_for_calf=self.nutrients.phosphorus_for_gestation_required_for_calf,
            days_in_milk=self.days_in_milk,
            calving_interval=self.reproduction.calving_interval,
            parity=self.reproduction.calves
        )

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
            return round(death_time_lower_limit + n * (death_date_random - death_lower_limit) + self.days_born)
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
                PenHistory(
                    start_date=current_day,
                    end_date=current_day,
                    pen=current_pen,
                    animal_types_in_pen=list(animal_types_in_pen),
                )
            )
        else:  # last_pen == curr_pen
            self.pen_history[-1]["end_date"] = current_day
            self.pen_history[-1]["animal_types_in_pen"] = list(animal_types_in_pen)

    def set_daily_walking_distance(self, vertical_dist_to_parlor: float, horizontal_dist_to_parlor: float) -> None:
        """
        Calculates and sets the animal's daily vertical and horizontal
        walking distance (DVD and DHD).

        Parameters
        ----------
        vertical_dist_to_parlor : float
            Vertical distance to milking parlor (km).
        horizontal_dist_to_parlor : float
            Horizontal distance to milking parlor (km).

        """
        if not self.animal_type.is_cow:
            raise ValueError("Cannot calculate daily walking distance for animal types other than cow.")
        self.daily_vertical_distance = 2 * vertical_dist_to_parlor * AnimalConfig.cow_times_milked_per_day
        self.daily_horizontal_distance = 2 * horizontal_dist_to_parlor * AnimalConfig.cow_times_milked_per_day
        self.daily_distance = sqrt(self.daily_vertical_distance**2 + self.daily_horizontal_distance**2)

    def set_nutrition_requirements(
        self, housing: str, walking_distance: float, previous_temperature: float, available_feeds: list[Feed]
    ) -> None:
        """Sets the nutrition requirements for an animal."""
        self.nutrition_requirements = self.calculate_nutrition_requirements(
            housing, walking_distance, previous_temperature, available_feeds
        )

    def calculate_nutrition_requirements(
        self, housing: str, walking_distance: float, previous_temperature: float, available_feeds: list[Feed]
    ) -> NutritionRequirements:
        """
        Gets the nutrition requirements for an animal.

        Parameters
        ----------
        housing : str
            The housing type of the animal, either "barn" or "grazing".
        walking_distance : float
            The walking distance to the milking parlor (m).
        previous_temperature : float
            The previous day's temperature (C).
        available_feeds : list[Feed]
            List of feeds available for ration formulation. Only needed for calf nutrition calculation.

        Returns
        -------
        NutritionRequirements
            The nutrition requirements for the animal.

        """
        if self.animal_type is AnimalType.CALF:
            calf_intake = CalfRationManager.calc_intake(
                self.birth_weight,
                self.body_weight,
                AnimalConfig.wean_day,
                AnimalConfig.wean_length,
                available_feeds,
                self.nutrient_standard,
            )
            calf_requirements = CalfRationManager.calc_requirements(
                self.days_born, self.body_weight, previous_temperature, calf_intake
            )
            # TODO: do not use dummy values for calf calcium and phosphorus requirements - issue pending.
            return NutritionRequirements(
                maintenance_energy=calf_requirements["ne_maint"],
                growth_energy=calf_requirements["ne_gain"],
                pregnancy_energy=0.0,
                lactation_energy=0.0,
                metabolizable_protein=calf_intake["me_intake"],
                calcium=0.0,
                phosphorus=0.0,
                process_based_phosphorus=0.0,
                dry_matter=calf_intake["dry_matter_intake"],
                activity_energy=0.0,
                essential_amino_acids=EssentialAminoAcidRequirements(
                    histidine=0.0,
                    isoleucine=0.0,
                    leucine=0.0,
                    lysine=0.0,
                    methionine=0.0,
                    phenylalanine=0.0,
                    threonine=0.0,
                    thryptophan=0.0,
                    valine=0.0,
                ),
            )

        days_in_pregnancy = self.days_in_pregnancy if self.is_pregnant else None
        days_in_milk = self.days_in_milk if self.is_milking else None

        if self.previous_nutrition_supply is None:
            previous_dmi = AnimalModuleConstants.DEFAULT_DRY_MATTER_INTAKE
            ndf_percentage = AnimalModuleConstants.DEFAULT_NDF_PERCENTAGE
            tdn_percentage = AnimalModuleConstants.DEFAULT_TDN_PERCENTAGE
            net_energy_diet_conc = AnimalModuleConstants.DEFAULT_NET_ENERGY_DIET_CONCENTRATION
        else:
            previous_dmi = self.previous_nutrition_supply.dry_matter
            ndf_percentage = (
                self.previous_nutrition_supply.ndf_supply / previous_dmi * GeneralConstants.FRACTION_TO_PERCENTAGE
            )
            tdn_percentage = (
                self.previous_nutrition_supply.tdn_supply / previous_dmi * GeneralConstants.FRACTION_TO_PERCENTAGE
            )
            net_energy_diet_conc = (
                self.previous_nutrition_supply.metabolizable_energy
                / previous_dmi
                * GeneralConstants.FRACTION_TO_PERCENTAGE
            )

        if self.nutrient_standard is NutrientStandard.NASEM:
            requirements = NASEMRequirementsCalculator.calculate_requirements(
                body_weight=self.body_weight,
                mature_body_weight=self.mature_body_weight,
                day_of_pregnancy=days_in_pregnancy,
                body_condition_score_5=self.body_condition_score_5,
                days_in_milk=days_in_milk,
                average_daily_gain_heifer=self.growth.daily_growth,
                animal_type=self.animal_type,
                parity=self.reproduction.calves,  # TODO: calves
                calving_interval=self.reproduction.calving_interval,  # TODO: calving interval
                milk_fat=self.milk_production.fat_percent,
                milk_true_protein=self.milk_production.true_protein_percent,
                milk_lactose=self.milk_production.lactose_percent,
                milk_production=self.milk_production.daily_milk_produced,
                housing=housing,
                distance=walking_distance,
                lactating=self.is_milking,
                ndf_percentage=ndf_percentage,
                process_based_phosphorus_requirement=self.nutrients.phosphorus_requirement,
            )
        else:
            requirements = NRCRequirementsCalculator.calculate_requirements(
                body_weight=self.body_weight,
                mature_body_weight=self.mature_body_weight,
                day_of_pregnancy=days_in_pregnancy,
                body_condition_score_5=self.body_condition_score_5,
                days_in_milk=days_in_milk,
                average_daily_gain_heifer=self.growth.daily_growth,
                animal_type=self.animal_type,
                parity=self.reproduction.calves,  # TODO: calves
                calving_interval=self.reproduction.calving_interval,  # TODO: calving interval
                milk_fat=self.milk_production.fat_percent,
                milk_true_protein=self.milk_production.true_protein_percent,
                milk_lactose=self.milk_production.lactose_percent,
                milk_production=self.milk_production.daily_milk_produced,
                housing=housing,
                distance=walking_distance,
                previous_temperature=previous_temperature,
                net_energy_diet_concentration=net_energy_diet_conc,
                days_born=self.days_born,
                TDN_percentage=tdn_percentage,
                process_based_phosphorus_requirement=self.nutrients.phosphorus_requirement,
            )

        return requirements
