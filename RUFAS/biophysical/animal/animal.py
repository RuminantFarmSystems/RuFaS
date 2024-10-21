from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_growth.animal_growth import AnimalGrowth
from RUFAS.biophysical.animal.animal_nutrients.animal_phosphorus import AnimalNutrient
from RUFAS.biophysical.animal.animal_properties.animal_growth_properties import AnimalGrowthProperties
from RUFAS.biophysical.animal.animal_properties.animal_health_properties import AnimalHealthProperties
from RUFAS.biophysical.animal.animal_properties.animal_statistics import AnimalStatistics
from RUFAS.biophysical.animal.animal_properties.digestive_system_properties import DigestiveSystemProperties
from RUFAS.biophysical.animal.animal_properties.general_properties import GeneralProperties
from RUFAS.biophysical.animal.animal_properties.milk_production_properties import MilkProductionProperties
from RUFAS.biophysical.animal.animal_properties.nutrient_properties import NutrientProperties
from RUFAS.biophysical.animal.animal_properties.reproduction_properties import ReproductionProperties
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import AnimalBaseInitArgsTypedDict
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.repro_protocol_enums import HeiferReproProtocolEnum
from RUFAS.biophysical.animal.milk.lactation_curve import LactationCurve
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.biophysical.animal.reproduction.reproduction import Reproduction
from RUFAS.time import Time


class Animal:
    def __init__(self, args: AnimalBaseInitArgsTypedDict) -> None:
        self.id = 0
        self.last_visited: int = 0

        self.general_properties: GeneralProperties = GeneralProperties(
            id=args.get("id"),
            breed=args.get("breed"),
            birth_date=args.get("birth_date"),
            days_born=args.get("days_born"),
            birth_weight=args.get("birth_weight"),
        )
        self.growth_properties: AnimalGrowthProperties = AnimalGrowthProperties()
        self.health_properties: AnimalHealthProperties = AnimalHealthProperties()
        self.animal_statistics: AnimalStatistics = AnimalStatistics()
        self.digestive_properties: DigestiveSystemProperties = DigestiveSystemProperties()
        self.milk_production_properties: MilkProductionProperties = MilkProductionProperties()
        self.nutrient_properties: NutrientProperties = NutrientProperties()
        self.reproduction_properties: ReproductionProperties = ReproductionProperties()

    @classmethod
    def setup_lactation_curve_parameters(cls, time: Time) -> None:
        LactationCurve.set_lactation_parameters(time)

    def daily_routines(self, time: Time) -> None:
        self.general_properties.days_born += 1

        AnimalNutrient.perform_daily_phosphorus_update(self.nutrient_properties, self.general_properties)
        # DigestiveSystem
        MilkProduction.perform_daily_milking_update(self.milk_production_properties, self.general_properties, time)
        # AnimalGrowth.
        # Reproduction.     # newborn possibility

        self.animal_life_stage_update()
        self.last_visited = time.simulation_day

    def animal_life_stage_update(self) -> None:
        if self.general_properties.animal_type == AnimalType.CALF and self._evaluate_calf_for_heiferI():
            self._transition_calf_to_heiferI()
        elif self.general_properties.animal_type == AnimalType.HEIFER_I and self._evaluate_heiferI_for_heiferII():
            self._transition_heiferI_to_heiferII()
        elif self.general_properties.animal_type == AnimalType.HEIFER_II and self._evaluate_heiferII_for_heiferIII():
            if not self._evaluate_heiferII_for_culling():
                self._transition_heiferII_to_heiferIII()
            else:
                self.general_properties.culled = True
        elif self.general_properties.animal_type == AnimalType.HEIFER_III and self._evaluate_heiferIII_for_cow():
            self._transition_heiferIII_to_cow()

        if self.general_properties.days_born == self.general_properties.future_cull_date:
            self.general_properties.culled = True
        if self.general_properties.days_born == self.general_properties.future_death_date:
            self.general_properties.dead = True

    def _evaluate_calf_for_heiferI(self) -> bool:
        return self.general_properties.days_born == AnimalConfig.wean_day

    def _evaluate_heiferI_for_heiferII(self) -> bool:
        return self.general_properties.days_born == AnimalConfig.heifer_breed_start_day

    def _evaluate_heiferII_for_heiferIII(self) -> bool:
        return (
            self.general_properties.days_born > AnimalConfig.heifer_breed_start_day
            and self.general_properties.is_pregnant
            and self.general_properties.days_in_preg
            > (self.reproduction_properties.gestation_length - AnimalConfig.heifer_prefresh_day)
        )

    def _evaluate_heiferII_for_culling(self) -> bool:
        return (not self.general_properties.is_pregnant) and (
            self.general_properties.days_born > AnimalConfig.heifer_reproduction_cull_day
        )

    def _evaluate_heiferIII_for_cow(self) -> bool:
        return self.general_properties.days_born == self.reproduction_properties.gestation_length

    def _transition_calf_to_heiferI(self) -> None:
        self.general_properties.animal_type = AnimalType.HEIFER_I

    def _transition_heiferI_to_heiferII(self) -> None:
        self.reproduction_properties.heifer_reproduction_program = AnimalConfig.heifer_reproduction_program
        self.reproduction_properties.heifer_reproduction_sub_program = AnimalConfig.heifer_reproduction_sub_program

        self.reproduction_properties.heifer_tai_method = (
            AnimalConfig.heifer_reproduction_sub_program
            if AnimalConfig.heifer_reproduction_program == HeiferReproProtocolEnum.TAI.value
            else ""
        )
        self.reproduction_properties.heifer_synch_ed_method = (
            AnimalConfig.heifer_reproduction_sub_program
            if AnimalConfig.heifer_reproduction_program == HeiferReproProtocolEnum.SynchED.value
            else ""
        )

        self.general_properties.animal_type = AnimalType.HEIFER_II

    def _transition_heiferII_to_heiferIII(self) -> None:
        self.general_properties.animal_type = AnimalType.HEIFER_III

    def _transition_heiferIII_to_cow(self) -> None:
        self.reproduction_properties.cow_reproduction_program = AnimalConfig.cow_reproduction_program
        self.reproduction_properties.cow_presynch_method = AnimalConfig.cow_presynch_method
        self.reproduction_properties.cow_tai_method = AnimalConfig.cow_tai_method
        self.reproduction_properties.cow_resynch_method = AnimalConfig.cow_resynch_method

        self.general_properties.animal_type = AnimalType.DRY_COW
