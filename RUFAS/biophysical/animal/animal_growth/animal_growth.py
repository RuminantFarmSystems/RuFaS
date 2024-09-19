import math
from typing import Any

from RUFAS.input_manager import InputManager
from RUFAS.time import Time

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.animal_properties.general_properties import GeneralProperties
from RUFAS.biophysical.animal.animal_properties.reproduction_properties import ReproductionProperties
from RUFAS.biophysical.animal.animal_properties.animal_growth_properties import AnimalGrowthProperties


class AnimalGrowth:
    wean_day: int
    target_heifer_pregnant_day: int

    @classmethod
    def initialize_class_variables(cls) -> None:
        im = InputManager()
        animal_config: dict[str, dict[str, Any]] = im.get_data("animal.animal_config.farm_level")
        cls.wean_day: int = animal_config["calf"]["wean_day"]
        cls.target_heifer_pregnant_day: int = animal_config["bodyweight"]["target_heifer_preg_day"]

    @staticmethod
    def daily_routines(
        general_properties: GeneralProperties,
        animal_growth_properties: AnimalGrowthProperties,
        reproduction_properties: ReproductionProperties,
        time: Time,
    ) -> tuple[AnimalGrowthProperties, ReproductionProperties, GeneralProperties]:
        if general_properties.animal_type == AnimalType.CALF:
            animal_growth_properties.daily_growth = AnimalGrowth.calculate_calf_body_weight_change(general_properties)
            general_properties.body_weight += animal_growth_properties.daily_growth

        elif general_properties.animal_type == AnimalType.HEIFER_I or (
            general_properties.animal_type == AnimalType.HEIFER_II and not general_properties.is_pregnant
        ):
            animal_growth_properties.daily_growth = AnimalGrowth.calculate_non_pregnant_heifer_body_weight_change(
                general_properties
            )
            general_properties.body_weight += animal_growth_properties.daily_growth

        elif (
            general_properties.animal_type == AnimalType.HEIFER_II and general_properties.is_pregnant
        ) or general_properties.animal_type == AnimalType.HEIFER_III:
            if general_properties.body_weight < general_properties.mature_body_weight:
                (animal_growth_properties.daily_growth, reproduction_properties.conceptus_weight) = (
                    AnimalGrowth.calculate_pregnant_heifer_body_weight_change(
                        reproduction_properties, general_properties
                    )
                )
                general_properties.body_weight += animal_growth_properties.daily_growth
            else:
                general_properties.body_weight = general_properties.mature_body_weight
                general_properties.events.add_event(
                    general_properties.days_born, time.simulation_day, animal_constants.MATURE_BODY_WEIGHT_REGULAR
                )

        elif (
            general_properties.animal_type == AnimalType.DRY_COW or general_properties.animal_type == AnimalType.LAC_COW
        ):
            (
                animal_growth_properties.daily_growth,
                reproduction_properties.conceptus_weight,
                animal_growth_properties.tissue_changed,
            ) = AnimalGrowth.calculate_cow_body_weight_change(
                animal_growth_properties, reproduction_properties, general_properties
            )
            general_properties.body_weight += animal_growth_properties.daily_growth

        return animal_growth_properties, reproduction_properties, general_properties

    @staticmethod
    def calculate_calf_body_weight_change(general_properties: GeneralProperties) -> float:
        return general_properties.birth_weight / AnimalGrowth.wean_day

    @staticmethod
    def calculate_non_pregnant_heifer_body_weight_change(general_properties: GeneralProperties) -> float:
        divisor = abs(AnimalGrowth.target_heifer_pregnant_day - general_properties.days_born)
        if divisor == 0:
            divisor = 1
        return max(
            (0.55 * 0.96 * general_properties.mature_body_weight - 0.96 * general_properties.body_weight) / divisor,
            AnimalModuleConstants.MINIMUM_HEIFER_DAILY_GROWTH_RATE,
        )

    @staticmethod
    def calculate_pregnant_heifer_body_weight_change(
        reproduction_properties: ReproductionProperties,
        general_properties: GeneralProperties,
    ) -> tuple[float, float]:
        target_average_daily_growth_pregnant_heifer = AnimalGrowth._calculate_pregnant_heifer_target_daily_growth(
            reproduction_properties, general_properties
        )

        (conceptus_growth, reproduction_properties.conceptus_weight) = (
            AnimalGrowth._calculate_pregnant_heifer_conceptus_growth(reproduction_properties, general_properties)
        )

        return (
            target_average_daily_growth_pregnant_heifer + conceptus_growth,
            reproduction_properties.conceptus_weight,
        )

    @staticmethod
    def calculate_cow_body_weight_change(
        animal_growth_properties: AnimalGrowthProperties,
        reproduction_properties: ReproductionProperties,
        general_properties: GeneralProperties,
    ) -> tuple[float, float, float]:
        (conceptus_growth, reproduction_properties.conceptus_weight, animal_growth_properties.tissue_changed) = (
            AnimalGrowth._calculate_cow_conceptus_growth(
                animal_growth_properties, reproduction_properties, general_properties
            )
        )

        target_adg_cow = AnimalGrowth._calculate_cow_target_daily_growth(reproduction_properties, general_properties)

        (body_weight_tissue, animal_growth_properties.tissue_changed) = (
            AnimalGrowth._calculate_cow_body_weight_tissue_change(
                animal_growth_properties, reproduction_properties, general_properties
            )
        )

        return (
            target_adg_cow + conceptus_growth + body_weight_tissue,
            reproduction_properties.conceptus_weight,
            animal_growth_properties.tissue_changed,
        )

    @staticmethod
    def _calculate_pregnant_heifer_conceptus_growth(
        reproduction_properties: ReproductionProperties, general_properties: GeneralProperties
    ) -> tuple[float, float]:
        updated_conceptus_weight = reproduction_properties.conceptus_weight
        if general_properties.days_in_preg == reproduction_properties.gestation_length:
            conceptus_growth = -reproduction_properties.conceptus_weight
            updated_conceptus_weight = 0

        elif general_properties.days_in_preg > 50:
            conceptus_total_weight = (
                0.0148 * reproduction_properties.gestation_length - 2.408
            ) * reproduction_properties.calf_birth_weight
            conceptus_param = conceptus_total_weight ** (1 / 3) / (reproduction_properties.gestation_length - 50)
            conceptus_growth = 3 * conceptus_param**3 * (general_properties.days_in_preg - 50) ** 2
            updated_conceptus_weight += conceptus_growth
        else:
            conceptus_growth = 0
        return conceptus_growth, updated_conceptus_weight

    @staticmethod
    def _calculate_cow_conceptus_growth(
        animal_growth_properties: AnimalGrowthProperties,
        reproduction_properties: ReproductionProperties,
        general_properties: GeneralProperties,
    ) -> tuple[float, float, float]:
        updated_conceptus_weight = reproduction_properties.conceptus_weight
        updated_tissue_change = animal_growth_properties.tissue_changed

        if general_properties.days_in_preg == reproduction_properties.gestation_length:
            conceptus_growth = -reproduction_properties.conceptus_weight
            updated_conceptus_weight = 0
            updated_tissue_change = 0
        elif general_properties.days_in_preg > 50:
            conceptus_total_weight = (
                0.0148 * reproduction_properties.gestation_length - 2.408
            ) * reproduction_properties.calf_birth_weight
            conceptus_param = conceptus_total_weight ** (1 / 3) / (reproduction_properties.gestation_length - 50)
            conceptus_growth = 3 * conceptus_param**3 * (general_properties.days_in_preg - 50) ** 2
            updated_conceptus_weight += conceptus_growth
        else:
            conceptus_growth = 0

        return conceptus_growth, updated_conceptus_weight, updated_tissue_change

    @staticmethod
    def _calculate_pregnant_heifer_target_daily_growth(
        reproduction_properties: ReproductionProperties, general_properties: GeneralProperties
    ) -> float:
        divisor = reproduction_properties.gestation_length - general_properties.days_in_preg
        if divisor == 0:
            divisor = 1
        return (0.82 * 0.96 * general_properties.mature_body_weight - 0.96 * general_properties.body_weight) / divisor

    @staticmethod
    def _calculate_cow_target_daily_growth(
        reproduction_properties: ReproductionProperties, general_properties: GeneralProperties
    ) -> float:
        if reproduction_properties.calves == 1:
            if general_properties.days_in_preg < 1:
                target_adg_cow = (
                    (0.92 - 0.82)
                    * 0.96
                    * general_properties.mature_body_weight
                    / reproduction_properties.calving_interval
                )
            else:
                target_adg_cow = (0.92 * general_properties.mature_body_weight - general_properties.body_weight) / (
                    reproduction_properties.gestation_length - general_properties.days_in_preg + 1
                )
        elif reproduction_properties.calves == 2:
            if general_properties.days_in_preg < 1:
                target_adg_cow = (
                    (1 - 0.92) * 0.96 * general_properties.mature_body_weight / reproduction_properties.calving_interval
                )
            else:
                target_adg_cow = (general_properties.mature_body_weight - general_properties.body_weight) / (
                    reproduction_properties.gestation_length - general_properties.days_in_preg + 1
                )
        else:
            target_adg_cow = 0
        return target_adg_cow

    @staticmethod
    def _calculate_cow_body_weight_tissue_change(
        animal_growth_properties: AnimalGrowthProperties,
        reproduction_properties: ReproductionProperties,
        general_properties: GeneralProperties,
    ) -> tuple[float, float]:
        updated_tissue_changed = animal_growth_properties.tissue_changed
        if not general_properties.days_in_milk == 0:
            if reproduction_properties.calves == 1:
                body_weight_tissue = -20 / 65 * math.exp(1 - general_properties.days_in_milk / 65) + 20 / (
                    65**2
                ) * general_properties.days_in_milk * math.exp(1 - general_properties.days_in_milk / 65)
                if general_properties.days_in_preg == general_properties.dry_off_day_of_pregnancy - 1:
                    updated_tissue_changed = (
                        20 * general_properties.days_in_milk / 65 * math.exp(1 - general_properties.days_in_milk / 65)
                    )
            else:
                body_weight_tissue = -40 / 70 * math.exp(1 - general_properties.days_in_milk / 70) + 40 / (
                    70**2
                ) * general_properties.days_in_milk * math.exp(1 - general_properties.days_in_milk / 70)
                if general_properties.days_in_preg == general_properties.dry_off_day_of_pregnancy - 1:
                    updated_tissue_changed = (
                        40 * general_properties.days_in_milk / 70 * math.exp(1 - general_properties.days_in_milk / 70)
                    )
        else:
            body_weight_tissue = animal_growth_properties.tissue_changed / (
                reproduction_properties.gestation_length - general_properties.dry_off_day_of_pregnancy
            )
        return body_weight_tissue, updated_tissue_changed
