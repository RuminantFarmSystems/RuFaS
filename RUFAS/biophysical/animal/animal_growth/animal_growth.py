import math

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.animal_properties.animal_growth_properties import AnimalGrowthProperties
from RUFAS.biophysical.animal.animal_properties.general_properties import GeneralProperties
from RUFAS.biophysical.animal.animal_properties.reproduction_properties import ReproductionProperties
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.input_manager import InputManager
from RUFAS.time import Time


class AnimalGrowth:
    wean_day: int
    target_heifer_pregnant_day: int

    @classmethod
    def initialize_class_variables(cls) -> None:
        im = InputManager()
        animal_config = im.get_data("animal.animal_config.farm_level.calf.wean_day")
        cls.wean_day = animal_config["farm_level"]["calf.wean_day"]
        cls.target_heifer_pregnant_day = animal_config["farm_level"]["bodyweight"]["target_heifer_preg_day"]

    @staticmethod
    def daily_routines(
            general_properties: GeneralProperties,
            animal_growth_properties: AnimalGrowthProperties,
            reproduction_properties: ReproductionProperties,
            time: Time) -> tuple[AnimalGrowthProperties, ReproductionProperties, GeneralProperties]:
        if general_properties.animal_type == AnimalType.CALF:
            animal_growth_properties.daily_growth = AnimalGrowth.calculate_calf_body_weight_change(
                general_properties.birth_weight)
            general_properties.body_weight += animal_growth_properties.daily_growth

        elif general_properties.animal_type == AnimalType.HEIFER_I or (
            general_properties.animal_type == AnimalType.HEIFER_II and not general_properties.is_pregnant
        ):
            animal_growth_properties.daily_growth = AnimalGrowth.calculate_non_pregnant_heifer_body_weight_change(
                general_properties.days_born, general_properties.mature_body_weight, general_properties.body_weight)
            general_properties.body_weight += animal_growth_properties.daily_growth

        elif (general_properties.animal_type == AnimalType.HEIFER_II and general_properties.is_pregnant) or \
                general_properties.animal_type == AnimalType.HEIFER_III:
            if general_properties.body_weight < general_properties.mature_body_weight:
                (
                    animal_growth_properties.daily_growth,
                    reproduction_properties
                ) = AnimalGrowth.calculate_pregnant_heifer_body_weight_change(reproduction_properties,
                                                                              general_properties.days_in_preg,
                                                                              general_properties.mature_body_weight,
                                                                              general_properties.body_weight)
                general_properties.body_weight += animal_growth_properties.daily_growth
            else:
                general_properties.body_weight = general_properties.mature_body_weight
                general_properties.events.add_event(general_properties.days_born,
                                                    time.simulation_day,
                                                    animal_constants.MATURE_BODY_WEIGHT_REGULAR)

        elif general_properties.animal_type == AnimalType.DRY_COW or \
                general_properties.animal_type == AnimalType.LAC_COW:
            (
                animal_growth_properties.daily_growth,
                animal_growth_properties,
                reproduction_properties
            ) = AnimalGrowth.calculate_cow_body_weight_change(
                animal_growth_properties, reproduction_properties, general_properties.days_in_preg,
                general_properties.mature_body_weight, general_properties.body_weight, general_properties.days_in_milk
            )
            general_properties.body_weight += animal_growth_properties.daily_growth

        return animal_growth_properties, reproduction_properties, general_properties

    @staticmethod
    def calculate_calf_body_weight_change(birth_weight: float) -> float:
        return birth_weight / AnimalGrowth.wean_day

    @staticmethod
    def calculate_non_pregnant_heifer_body_weight_change(
            days_born: int, mature_body_weight: float, body_weight: float) -> float:
        divisor = abs(AnimalGrowth.target_heifer_pregnant_day - days_born)
        if divisor == 0:
            divisor = 1
        return max(
            (0.55 * 0.96 * mature_body_weight - 0.96 * body_weight) / divisor,
            AnimalModuleConstants.MINIMUM_HEIFER_DAILY_GROWTH_RATE,
        )

    @staticmethod
    def calculate_pregnant_heifer_body_weight_change(
            reproduction_properties: ReproductionProperties, days_in_preg: int, mature_body_weight: float,
            body_weight: float) -> tuple[float, ReproductionProperties]:
        """
        Calculates the body weight change for a heifer, depending on if she
        is pregnant or not.
        If the gestation_length of the animal is equal to its days_in_preg,
        the difference is set to 1 (otherwise results in a division by 0 error).

        Returns: the daily body weight change for a heifer
        """
        # BW change due to heifer average daily gain
        divisor = reproduction_properties.gestation_length - days_in_preg
        if divisor == 0:
            divisor = 1
        target_average_daily_gain_pregnant_heifer = (0.82 * 0.96 * mature_body_weight - 0.96 * body_weight) / divisor

        # BW change due to conceptus
        if days_in_preg == reproduction_properties.gestation_length:
            conceptus_growth = -reproduction_properties.conceptus_weight
            reproduction_properties.conceptus_weight = 0
        elif days_in_preg > 50:
            conceptus_total_weight = (0.0148 * reproduction_properties.gestation_length - 2.408) * \
                                     reproduction_properties.calf_birth_weight
            conceptus_param = conceptus_total_weight ** (1 / 3) / (reproduction_properties.gestation_length - 50)
            conceptus_growth = 3 * conceptus_param ** 3 * (days_in_preg - 50) ** 2
            reproduction_properties.conceptus_weight += conceptus_growth
        else:
            conceptus_growth = 0

        return target_average_daily_gain_pregnant_heifer + conceptus_growth, reproduction_properties

    @staticmethod
    def calculate_cow_body_weight_change(       # noqa
            animal_growth_properties: AnimalGrowthProperties,
            reproduction_properties: ReproductionProperties,
            days_in_preg: int,
            mature_body_weight: float,
            body_weight: float,
            days_in_milk: int,
            dry_off_day_of_pregnancy: int
    ) -> tuple[float, AnimalGrowthProperties, ReproductionProperties]:
        # on the calving day
        if days_in_preg == reproduction_properties.gestation_length:
            conceptus_growth = -reproduction_properties.conceptus_weight
            reproduction_properties.conceptus_weight = 0
            animal_growth_properties.tissue_changed = 0
        # conceptus weight change during pregnancy
        elif days_in_preg > 50:
            conceptus_total_weight = (0.0148 * reproduction_properties.gestation_length - 2.408) * \
                                     reproduction_properties.calf_birth_weight
            conceptus_param = conceptus_total_weight ** (1 / 3) / (reproduction_properties.gestation_length - 50)
            conceptus_growth = 3 * conceptus_param**3 * (days_in_preg - 50) ** 2
            reproduction_properties.conceptus_weight += conceptus_growth
        else:
            conceptus_growth = 0

        # growth for 1st and 2nd lactation cows
        if reproduction_properties.calves == 1:
            if days_in_preg < 1:  # before pregnancy
                target_adg_cow = (0.92 - 0.82) * 0.96 * mature_body_weight / reproduction_properties.calving_interval
            else:  # after pregnancy
                target_adg_cow = (0.92 * mature_body_weight - body_weight) / (
                    reproduction_properties.gestation_length - days_in_preg + 1
                )
        elif reproduction_properties.calves == 2:
            if days_in_preg < 1:  # before pregnancy
                target_adg_cow = (1 - 0.92) * 0.96 * mature_body_weight / reproduction_properties.calving_interval
            else:  # after pregnancy
                target_adg_cow = (mature_body_weight - body_weight) / (
                    reproduction_properties.gestation_length - days_in_preg + 1
                )
        else:  # parity > 2
            target_adg_cow = 0

        if not days_in_milk == 0:
            if reproduction_properties.calves == 1:
                bodyweight_tissue = -20 / 65 * math.exp(1 - days_in_milk / 65) + 20 / (
                    65**2
                ) * days_in_milk * math.exp(1 - days_in_milk / 65)
                if days_in_preg == dry_off_day_of_pregnancy - 1:
                    animal_growth_properties.tissue_changed = 20 * days_in_milk / 65 * math.exp(1 - days_in_milk / 65)
            else:  # parity > 1
                bodyweight_tissue = -40 / 70 * math.exp(1 - days_in_milk / 70) + 40 / (
                    70**2
                ) * days_in_milk * math.exp(1 - days_in_milk / 70)
                if days_in_preg == dry_off_day_of_pregnancy - 1:
                    animal_growth_properties.tissue_changed = 40 * days_in_milk / 70 * math.exp(1 - days_in_milk / 70)
        else:  # dry period
            bodyweight_tissue = animal_growth_properties.tissue_changed / (
                reproduction_properties.gestation_length - dry_off_day_of_pregnancy
            )

        return target_adg_cow + conceptus_growth + bodyweight_tissue, animal_growth_properties, reproduction_properties
