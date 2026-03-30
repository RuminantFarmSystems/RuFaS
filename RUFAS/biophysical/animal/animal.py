import sys
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
from RUFAS.biophysical.animal.data_types.milk_production import (
    MilkProductionInputs,
    MilkProductionOutputs,
    MilkProductionStatistics,
)
from RUFAS.biophysical.animal.data_types.nutrients import NutrientsInputs
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements, NutritionSupply
from RUFAS.biophysical.animal.data_types.pen_history import PenHistory
from RUFAS.biophysical.animal.data_types.reproduction import (
    ReproductionInputs,
    ReproductionOutputs,
    HerdReproductionStatistics,
    AnimalReproductionStatistics,
)
from RUFAS.biophysical.animal.digestive_system.digestive_system import DigestiveSystem
from RUFAS.biophysical.animal.growth.growth import Growth
from RUFAS.biophysical.animal.nutrients.nutrients import Nutrients
from RUFAS.biophysical.animal.nutrients.nasem_requirements_calculator import NASEMRequirementsCalculator
from RUFAS.biophysical.animal.nutrients.nrc_requirements_calculator import NRCRequirementsCalculator
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
    CowReproductionProtocol,
    CowPreSynchSubProtocol,
    CowTAISubProtocol,
    CowReSynchSubProtocol,
)
from RUFAS.biophysical.animal.milk.lactation_curve import LactationCurve
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements
from RUFAS.biophysical.animal.ration.calf_ration_manager import CalfRationManager
from RUFAS.biophysical.animal.reproduction.reproduction import Reproduction
from RUFAS.data_structures.feed_storage_to_animal_connection import NutrientStandard, Feed
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime


class Animal:
    """
    This class represents an animal in the RuFaS simulation.

    DO NOT USE THE PROPERTIES THAT START WITH '_'. INSTEAD, USE THE FUNCTIONS THAT ARE DECORATED WITH @property.

    Attributes
    ----------
    id: int
        The unique identifier of the animal, (unitless).
    breed: Breed
        The breed of the animal.
    animal_type: AnimalType
        The current life stage of the animal.
    days_born: int
        The age of the animal, (simulation days).
    body_weight: float
        The body weight of the animal, (kg).
    birth_weight: float
        The birth weight of the animal, (kg).
    mature_body_weight: float
        The mature body weight of the animal, (kg).
    wean_weight: float
        The body weight of the animal at weaning, (kg).
    net_merit: float
        The net merit value of the animal, ($USD).
    body_condition_score_5: float
        The body condition score on a scale of 1 to 5, (unitless).
    cull_reason: str
        The reason for the animal to leave the herd.
    body_weight_history: list[BodyWeightHistory]
        The body weight history of the animal.
    pen_history: list[PenHistory]
        The pen history of the animal.
    sold_at_day: int | None
        The simulation day in which the animal was sold.
    dead_at_day: int | None
        The simulation day in which the animal died, (simulation day).
    events: AnimalEvents
        The AnimalEvents object that records all major events of the animal.
    growth: Growth
        The animal growth submodule that handles the body weight change of the animal.
    digestive_system: DigestiveSystem
        The digestive system submodule that handles the daily manure excretion of the animal.
    milk_production: MilkProduction
        The milk production submodule that handles the daily milk production of the animal.
    nutrients: Nutrients
        The nutrients submodule that handles the daily phosphorus update of the animal.
    _reproduction: Reproduction
        The reproduction submodule that handles the daily reproduction update of the animal.
    nutrition_requirements: NutrientsRequirements
        The nutrition requirement for the animal.
    nutrition_supply: NutritionSupply
        The supplied nutrition in the current ration interval for the animal.
    previous_nutrition_supply: NutritionSupply
        The previously supplied nutrition from the las ration interval for the animal.
    animal_statistics: AnimalStatistics
        The AnimalStatistics object that tracks all major statistics of the animal.
    _days_in_milk: int
        The number of days that the animal has been in milk production, (days).
    _days_in_pregnancy: int
        The number of days that the animal has been in pregnancy, (days).
    _future_cull_date: int | None
        The age of which the animal will be culled, (day).
    _future_death_date: int | None
        The age of which the animal will die, (day).
    _daily_horizontal_distance: float
        The daily horizontal distance traveled by the animal, (m).
    _daily_vertical_distance: float
        The daily vertical distance traveled by the animal, (m).
    _daily_distance: float
        The total daily distance traveled by the animal, (m).
    sex: Sex
        The sex of the animal.
    nutrient_standard: NutrientStandard
        The nutrient standard used to calculate nutrition related values.
    """

    nutrient_standard: NutrientStandard

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
        simulation_day: int = 0,
    ) -> None:
        """
        Initializes an Animal object.

        Parameters
        ----------
        args : (
                    NewBornCalfValuesTypedDict |
                    CalfValuesTypedDict |
                    HeiferIValuesTypedDict |
                    HeiferIIValuesTypedDict |
                    CowValuesTypedDict
                )
            The dictionary that contains the configuration to initialize an Animal object.

        """
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
        self.stillborn_day: int | None = None
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

        self._days_in_milk: int = 0
        self._milk_production_output_days_in_milk: int = 0
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

    @classmethod
    def set_nutrient_standard(cls, nutrient_standard: NutrientStandard) -> None:
        """
        Set the nutrient standard for the all animals.

        Parameters
        ----------
        nutrient_standard : NutrientStandard
            An instance of NutrientStandard that defines the standard to set.

        """
        cls.nutrient_standard = nutrient_standard

    @staticmethod
    def setup_lactation_curve_parameters(time: RufasTime) -> None:
        """
        Sets up the parameters for the lactation curve model.

        Parameters
        ----------
        time : RufasTime
            An RufasTime object representing the time used to set the lactation curve parameters.

        """
        LactationCurve.set_lactation_parameters(time)

    @property
    def days_in_milk(self) -> int:
        """
        The number of days the animal has been in milk production.

        Returns
        -------
        int
            The number of days the animal has been in milk production. If the animal
            is not a cow, returns 0.

        """
        if not self.animal_type.is_cow:
            return 0
        return self._days_in_milk

    @days_in_milk.setter
    def days_in_milk(self, days_in_milk: int) -> None:
        """
        Sets the number of days in milk for the animal.

        If the animal is not a cow, the attribute '_days_in_milk' is automatically set to 0.
        Otherwise, the provided value is assigned to '_days_in_milk'.

        Parameters
        ----------
        days_in_milk : int
            The number of days the animal has been in milk.

        """
        if not self.animal_type.is_cow:
            self._days_in_milk = 0
        self._days_in_milk = days_in_milk

    @property
    def days_in_pregnancy(self) -> int:
        """
        The total number of days an animal has been in pregnancy.

        Returns
        -------
        int
            The number of days the animal has been in pregnancy.

        Notes
        -----
        - For animals of type CALF or HEIFER_I, the pregnancy duration is always considered to be zero.
        - For all other types of animals, the value of `_days_in_pregnancy` is returned.

        """
        if self.animal_type in [AnimalType.CALF, AnimalType.HEIFER_I]:
            return 0
        return self._days_in_pregnancy

    @days_in_pregnancy.setter
    def days_in_pregnancy(self, days_in_pregnancy: int) -> None:
        """
        Sets the number of days the animal has been in pregnancy.

        Parameters
        ----------
        days_in_pregnancy : int
            The number of days the animal has been in pregnancy.

        Raises
        ------
        TypeError
            If the animal type is either CALF or HEIFER_I.

        """
        if self.animal_type in [AnimalType.CALF, AnimalType.HEIFER_I]:
            raise TypeError()
        self._days_in_pregnancy = days_in_pregnancy

    @property
    def is_pregnant(self) -> bool:
        """
        Checks if the animal is pregnant based on its type and pregnancy days.

        Returns
        -------
        bool
            True if the animal is pregnant, otherwise False.

        """
        if self.animal_type in {AnimalType.CALF, AnimalType.HEIFER_I}:
            return False
        return self.days_in_pregnancy > 0

    @property
    def is_milking(self) -> bool:
        """
        Check if the animal is milking.

        This property determines if the animal is currently milking. It specifically checks if the animal type is a cow
        and if the cow has been in milk for at least one day.

        Returns
        -------
        bool
            True if the animal is a cow and in milk, False otherwise.

        """
        if not self.animal_type.is_cow:
            return False
        return self.days_in_milk > 0

    @property
    def future_cull_date(self) -> int:
        """
        Returns the cull death date of the animal.

        If the animal is not a cow, the method returns the maximum possible integer value.
        Otherwise, it returns the pre-calculated future cull date.

        Returns
        -------
        int
            The future cull date or the maximum possible integer value if the animal is not a cow.

        """
        if not self.animal_type.is_cow:
            return sys.maxsize
        return self._future_cull_date

    @future_cull_date.setter
    def future_cull_date(self, future_cull_date: int) -> None:
        """
        Sets the future cull date for the animal.

        Parameters
        ----------
        future_cull_date : int
            The future cull date to be set for the animal.

        Raises
        ------
        TypeError
            If the animal type is not a cow.

        """
        if not self.animal_type.is_cow:
            raise TypeError()
        self._future_cull_date = future_cull_date

    @property
    def future_death_date(self) -> int:
        """
        Returns the future death date of the animal.

        If the animal is not a cow, the method returns the maximum possible integer value.
        Otherwise, it returns the pre-calculated future death date.

        Returns
        -------
        int
            The future death date of the animal in integer form (sys.maxsize for non-cow animals).

        """
        if not self.animal_type.is_cow:
            return sys.maxsize
        return self._future_death_date

    @future_death_date.setter
    def future_death_date(self, future_death_date: int) -> None:
        """
        Sets the future death date for an animal.

        Parameters
        ----------
        future_death_date : int
            The future death date to assign to the animal.

        Raises
        ------
        TypeError
            If the animal is not of type 'cow'.

        """
        if not self.animal_type.is_cow:
            raise TypeError()
        self._future_death_date = future_death_date

    @property
    def daily_horizontal_distance(self) -> float:
        """
        Returns the daily horizontal distance traveled by the animal.

        Returns
        -------
        float
            The daily horizontal distance traveled.

        Raises
        ------
        TypeError
            If the animal type is not a cow.

        """
        if not self.animal_type.is_cow:
            raise TypeError()
        return self._daily_horizontal_distance

    @daily_horizontal_distance.setter
    def daily_horizontal_distance(self, daily_horizontal_distance: float) -> None:
        """
        Sets the daily horizontal distance for the animal.

        Parameters
        ----------
        daily_horizontal_distance : float
            The distance in horizontal movement covered by the animal on a daily basis.

        Raises
        ------
        TypeError
            If the animal type is not a cow.

        """
        if not self.animal_type.is_cow:
            raise TypeError()
        self._daily_horizontal_distance = daily_horizontal_distance

    @property
    def daily_vertical_distance(self) -> float:
        """
        Returns the daily vertical distance traveled by an animal.

        Returns
        -------
        float
            The daily vertical distance traveled by the cow.

        Raises
        ------
        TypeError
            If the animal type is not a cow.

        """
        if not self.animal_type.is_cow:
            raise TypeError()
        return self._daily_vertical_distance

    @daily_vertical_distance.setter
    def daily_vertical_distance(self, daily_vertical_distance: float) -> None:
        """
        Sets the daily vertical distance for the animal.

        Parameters
        ----------
        daily_vertical_distance : float
            The distance in vertical movement units to be assigned.

        Raises
        ------
        TypeError
            If the animal type is not a cow.

        """
        if not self.animal_type.is_cow:
            raise TypeError()
        self._daily_vertical_distance = daily_vertical_distance

    @property
    def daily_distance(self) -> float:
        """
        Returns the daily distance traveled by the animal.

        If the animal is not a cow and is currently milking, the daily distance
        is considered to be 0.0. Otherwise, it returns the value of
        the stored daily distance.

        Returns
        -------
        float
            The daily distance traveled by the animal.

        """
        if not self.animal_type.is_cow and self.is_milking:
            return 0.0
        return self._daily_distance

    @daily_distance.setter
    def daily_distance(self, daily_distance: float) -> None:
        """
        Sets the daily distance traveled by the animal.

        Parameters
        ----------
        daily_distance : float
            The distance the animal travels daily.

        Raises
        ------
        TypeError
            If the animal type is not a cow.

        """
        if not self.animal_type.is_cow:
            raise TypeError()
        self._daily_distance = daily_distance

    @property
    def reproduction(self) -> Reproduction:
        """
        Gets the reproduction property of the object.

        Returns
        -------
        Reproduction
            The reproduction property of the object.

        """
        return self._reproduction

    @reproduction.setter
    def reproduction(self, reproduction: Reproduction) -> None:
        """
        Sets the reproduction attribute for the animal.

        Parameters
        ----------
        reproduction : Reproduction
            The reproduction object to be assigned.

        Raises
        ------
        TypeError
            If the animal type is either a calf or a heiferI.

        """
        if self.animal_type in [AnimalType.CALF, AnimalType.HEIFER_I]:
            raise TypeError()
        self._reproduction = reproduction

    @property
    def calves(self) -> int:
        """
        Fetches the number of calves the animal has given birth to.

        Only applicable if the animal type is a cow. If the animal
        type is not a cow, it will return 0.

        Returns
        -------
        int
            The number of calves if the animal type is a cow, otherwise 0.

        """
        if not self.animal_type.is_cow:
            return 0
        return self.reproduction.calves

    @calves.setter
    def calves(self, calves: int) -> None:
        """
        Setter method for the number of calves. Valid only for animals of type 'cow'.

        Parameters
        ----------
        calves : int
            The number of calves to set for the animal.

        Raises
        ------
        TypeError
            If the animal type is not 'cow'.

        """
        if not self.animal_type.is_cow:
            raise TypeError()
        self.reproduction.calves = calves

    @property
    def calving_interval(self) -> int:
        """
        Returns the calving interval for the animal.

        If the animal type is not a cow, the calving interval is 0.
        Otherwise, it retrieves the calving interval from the reproduction information.

        Returns
        -------
        int
            The calving interval in days or 0 if the animal is not a cow.

        """
        if not self.animal_type.is_cow:
            return 0
        return self.reproduction.calving_interval

    @calving_interval.setter
    def calving_interval(self, calving_interval: int) -> None:
        """
        Setter method for updating the calving interval of an animal.

        Parameters
        ----------
        calving_interval : int
            The interval, in days, at which the animal gives birth.

        Raises
        ------
        TypeError
            If the animal type is not a cow.

        """
        if not self.animal_type.is_cow:
            raise TypeError()
        self.reproduction.calving_interval = calving_interval

    @property
    def conceptus_weight(self) -> float:
        """
        Returns the conceptus weight of the animal.

        Returns
        -------
        float
            The weight of the conceptus. Returns 0.0 for calf and heiferI; otherwise returns the value from the
            reproduction attribute.

        """
        if self.animal_type in [AnimalType.CALF, AnimalType.HEIFER_I]:
            return 0.0
        return self.reproduction.conceptus_weight

    @conceptus_weight.setter
    def conceptus_weight(self, conceptus_weight: float) -> None:
        """
        Sets the value for the conceptus weight.

        Parameters
        ----------
        conceptus_weight : float
            The weight of the conceptus to be set.

        """
        self.reproduction.conceptus_weight = conceptus_weight

    @property
    def gestation_length(self) -> int:
        """
        Returns the gestation length for the animal.

        Returns
        -------
        int
            The gestation length of the animal in days.
            Returns 0 if the animal type is CALF or HEIFER_I, otherwise returns
            the gestation length from the reproduction attribute.

        """
        if self.animal_type in [AnimalType.CALF, AnimalType.HEIFER_I]:
            return 0
        return self.reproduction.gestation_length

    @gestation_length.setter
    def gestation_length(self, gestation_length: int) -> None:
        """
        Sets the gestation length for the animal. This property is not applicable
        for animals of type CALF or HEIFER_I and will raise a TypeError if attempted
        to set for these types.

        Parameters
        ----------
        gestation_length : int
            The gestation length to be set for the animal.

        Raises
        ------
        TypeError
            If the animal type is CALF or HEIFER_I.

        """
        if self.animal_type in [AnimalType.CALF, AnimalType.HEIFER_I]:
            raise TypeError()
        self.reproduction.gestation_length = gestation_length

    @property
    def calf_birth_weight(self) -> float:
        """
        Getter for the calf birth weight of the animal.

        Returns
        -------
        float
            The weight of the calf at birth. Defaults to 0.0 if the animal type is
            either CALF or HEIFER_I. Otherwise, it retrieves the value from the
            reproduction attribute.

        """
        if self.animal_type in [AnimalType.CALF, AnimalType.HEIFER_I]:
            return 0.0
        return self.reproduction.calf_birth_weight

    @calf_birth_weight.setter
    def calf_birth_weight(self, calf_birth_weight: float) -> None:
        """
        Setter method for the calf_birth_weight attribute.

        This method sets the calf birth weight for the animal. However, it raises a
        TypeError if the animal type is either CALF or HEIFER_I, as these types are
        not applicable for setting the calf birth weight.

        Parameters
        ----------
        calf_birth_weight : float
            The birth weight of the calf to be set.

        Raises
        ------
        TypeError
            If the animal is of type CALF or HEIFER_I.

        """
        if self.animal_type in [AnimalType.CALF, AnimalType.HEIFER_I]:
            raise TypeError()
        self.reproduction.calf_birth_weight = calf_birth_weight

    @property
    def calving_interval_history(self) -> list[int]:
        """
        Returns the calving interval history for the animal.

        Returns
        -------
        list of int
            A list containing the recorded calving intervals of the cow.

        Raises
        ------
        TypeError
            If the animal is not of type cow.

        """
        if not self.animal_type.is_cow:
            raise TypeError()
        return self.reproduction.calving_interval_history

    @property
    def heifer_reproduction_program(self) -> HeiferReproductionProtocol:
        """
        Returns the heifer reproduction program.

        Returns
        -------
        HeiferReproductionProtocol
            The heifer reproduction program from the reproduction data.

        Raises
        ------
        TypeError
            If the animal type is either CALF or HEIFER_I, which are not
            suitable for this reproduction protocol.

        """
        if self.animal_type in [AnimalType.CALF, AnimalType.HEIFER_I]:
            raise TypeError()
        return self.reproduction.heifer_reproduction_program

    @heifer_reproduction_program.setter
    def heifer_reproduction_program(self, heifer_reproduction_program: HeiferReproductionProtocol) -> None:
        """
        Sets the heifer reproduction program for the animal.

        Parameters
        ----------
        heifer_reproduction_program : HeiferReproductionProtocol
            The heifer reproduction program to set for the animal.

        Raises
        ------
        TypeError
            If the animal type is either 'CALF' or 'HEIFER_I'.

        """
        if self.animal_type in [AnimalType.CALF, AnimalType.HEIFER_I]:
            raise TypeError()
        self.reproduction.heifer_reproduction_program = heifer_reproduction_program

    @property
    def heifer_reproduction_sub_program(self) -> HeiferTAISubProtocol | HeiferSynchEDSubProtocol:
        """
        heifer_reproduction_sub_program property.

        This property retrieves the heifer reproduction subprogram associated with the current object. If the animal
        type is not applicable for heifer reproduction subprograms, a TypeError is raised.

        Returns
        -------
        HeiferTAISubProtocol or HeiferSynchEDSubProtocol
            The heifer reproduction subprogram for the given animal type.

        Raises
        ------
        TypeError
            If the animal type is either CALF or HEIFER_I.

        """
        if self.animal_type in [AnimalType.CALF, AnimalType.HEIFER_I]:
            raise TypeError()
        return self.reproduction.heifer_reproduction_sub_program

    @heifer_reproduction_sub_program.setter
    def heifer_reproduction_sub_program(
        self, heifer_reproduction_sub_program: HeiferTAISubProtocol | HeiferSynchEDSubProtocol
    ) -> None:
        """
        Sets the sub-program for heifer reproduction based on the provided protocol.

        Parameters
        ----------
        heifer_reproduction_sub_program : HeiferTAISubProtocol or HeiferSynchEDSubProtocol
            The reproduction sub-program to be assigned for heifers.

        Raises
        ------
        TypeError
            If the animal type is CALF or HEIFER_I, since the sub-program is not applicable for these types.

        """
        if self.animal_type in [AnimalType.CALF, AnimalType.HEIFER_I]:
            raise TypeError()
        self.reproduction.heifer_reproduction_sub_program = heifer_reproduction_sub_program

    @property
    def cow_reproduction_program(self) -> CowReproductionProtocol:
        """
        Cow reproduction program for the specified animal.

        This property retrieves the cow reproduction program associated with the current object.
        It checks whether the animal type is a cow, and raises a TypeError otherwise.

        Returns
        -------
        CowReproductionProtocol
            The cow reproduction program relevant to the current animal.

        Raises
        ------
        TypeError
            If the animal type is not a cow.

        """
        if not self.animal_type.is_cow:
            raise TypeError()
        return self.reproduction.cow_reproduction_program

    @cow_reproduction_program.setter
    def cow_reproduction_program(self, cow_program: CowReproductionProtocol) -> None:
        """
        Sets the cow reproduction program for the animal.

        Parameters
        ----------
        cow_program : CowReproductionProtocol
            The reproduction program specific to cows.

        Raises
        ------
        TypeError
            If the animal type is not a cow.

        """
        if not self.animal_type.is_cow:
            raise TypeError()
        self.reproduction.cow_reproduction_program = cow_program

    @property
    def cow_presynch_program(self) -> CowPreSynchSubProtocol:
        """
        Returns the cow PreSynch protocol associated with the animal.

        Returns
        -------
        CowPreSynchSubProtocol
            The PreSynch protocol specific to cows.

        Raises
        ------
        TypeError
            If the associated animal type is not a cow.

        """
        if not self.animal_type.is_cow:
            raise TypeError()
        return self.reproduction.cow_presynch_program

    @cow_presynch_program.setter
    def cow_presynch_program(self, cow_presynch_program: CowPreSynchSubProtocol) -> None:
        """
        Setter method for the cow_presynch_program property.

        This method sets the value of the cow_presynch_program attribute.
        It validates whether the animal type is a cow before assigning the value.
        If the animal type is not a cow, a TypeError is raised.

        Parameters
        ----------
        cow_presynch_program : CowPreSynchSubProtocol
            The PreSynch program to be assigned to a cow.

        Raises
        ------
        TypeError
            If the animal type is not a cow.

        """
        if not self.animal_type.is_cow:
            raise TypeError()
        self.reproduction.cow_presynch_program = cow_presynch_program

    @property
    def cow_ovsynch_program(self) -> CowTAISubProtocol:
        """
        Retrieve the CowTAISubProtocol associated with the cow's ovsynch program if the animal type is a cow.

        Returns
        -------
        CowTAISubProtocol
            The cow's ovsynch program information.

        Raises
        ------
        TypeError
            If the animal type is not a cow.

        """
        if not self.animal_type.is_cow:
            raise TypeError()
        return self.reproduction.cow_ovsynch_program

    @cow_ovsynch_program.setter
    def cow_ovsynch_program(self, cow_ovsynch_program: CowTAISubProtocol) -> None:
        """
        Setter method for the cow_ovsynch_program property.

        Parameters
        ----------
        cow_ovsynch_program : CowTAISubProtocol
            The ovsynch program to be assigned to cows.

        Raises
        ------
        TypeError
            If the animal type is not a cow, this exception is raised.

        """
        if not self.animal_type.is_cow:
            raise TypeError()
        self.reproduction.cow_ovsynch_program = cow_ovsynch_program

    @property
    def cow_resynch_program(self) -> CowReSynchSubProtocol:
        """
        Returns the cow ReSynch program specific to the cow species.

        Returns
        -------
        CowReSynchSubProtocol
            The cow's ReSynch program information.

        Raises
        ------
        TypeError
            If the animal type is not a cow.

        """
        if not self.animal_type.is_cow:
            raise TypeError()
        return self.reproduction.cow_resynch_program

    @cow_resynch_program.setter
    def cow_resynch_program(self, cow_resynch_program: CowReSynchSubProtocol) -> None:
        """
        Sets the cow ReSynch program for the object. This method ensures
        that the operation is allowed only for objects with an animal type of 'cow'.
        If the animal type is not 'cow', a TypeError is raised.

        Parameters
        ----------
        cow_resynch_program : CowReSynchSubProtocol
            The ReSynch program to be assigned to cows only.

        Raises
        ------
        TypeError
            If the animal type is not 'cow'.

        """
        if not self.animal_type.is_cow:
            raise TypeError()
        self.reproduction.cow_resynch_program = cow_resynch_program

    @property
    def stillborn(self) -> bool:
        """
        Checks if the object is stillborn based on the presence and value of `stillborn_day`.

        Returns
        -------
        bool
            True if `stillborn_day` is not None and greater than or equal to 0, otherwise False.

        """
        return True if (self.stillborn_day is not None and self.stillborn_day >= 0) else False

    @property
    def sold(self) -> bool:
        """
        Checks if the object is sold based on the presence and value of `sold_at_day`.

        Returns
        -------
        bool
            True if `sold_at_day` is not None and greater than or equal to 0, otherwise False.

        """
        return True if (self.sold_at_day is not None and self.sold_at_day >= 0) else False

    @property
    def dead(self) -> bool:
        """
        Check if the object is considered dead based on its `dead_at_day` attribute.

        Returns
        -------
        bool
            True if `dead_at_day` is not None and greater than or equal to 0, indicating
            the object is no longer alive. False otherwise.

        """
        return True if (self.dead_at_day is not None and self.dead_at_day >= 0) else False

    @property
    def milk_statistics(self) -> MilkProductionStatistics:
        """Returns the milk statistics for the animal."""
        if not self.animal_type.is_cow:
            raise TypeError()
        return MilkProductionStatistics(
            cow_id=self.id,
            pen_id=self.pen_history[-1]["pen"],
            days_in_milk=self.days_in_milk,
            estimated_daily_milk_produced=self.milk_production.daily_milk_produced,
            milk_protein=self.milk_production.true_protein_content,
            milk_fat=self.milk_production.fat_content,
            milk_lactose=self.milk_production.lactose_content,
            parity=self.calves,
        )

    def _assign_sex_to_newborn_calf(self) -> None:
        """
        Assign a sex to a newborn calf based on the semen type and male calf rate.

        Determines the sex of the calf by evaluating the type of semen used (conventional
        or sexed) and the corresponding male calf rate. Raises a ValueError if an
        unexpected semen type is encountered.

        Raises
        ------
        ValueError
            If `AnimalConfig.semen_type` is not "conventional" or "sexed".

        """
        if AnimalConfig.semen_type == "conventional":
            male_calf_rate = AnimalConfig.male_calf_rate_conventional_semen
        elif AnimalConfig.semen_type == "sexed":
            male_calf_rate = AnimalConfig.male_calf_rate_sexed_semen
        else:
            om = OutputManager()
            om.add_error(
                "Unexpected semen type",
                f"Unexpected semen type: {AnimalConfig.semen_type}",
                {"class": self.__class__.__name__, "function": self._assign_sex_to_newborn_calf.__name__},
            )
            raise ValueError(f"Unexpected semen type: {AnimalConfig.semen_type}")
        self.sex = Sex.MALE if random() < male_calf_rate else Sex.FEMALE

    def _initialize_newborn_calf(self, args: NewBornCalfValuesTypedDict, simulation_day: int) -> None:
        """
        Initialize a newborn calf with specific attributes and simulation variables.

        Parameters
        ----------
        args : NewBornCalfValuesTypedDict
            A dictionary containing values related to the newborn calf.
            Expected keys include 'birth_weight' and 'initial_phosphorus'.
        simulation_day : int
            The current day in the simulation, used for event logging and status evaluation.

        """
        self._assign_sex_to_newborn_calf()

        if random() < AnimalConfig.still_birth_rate:
            self.stillborn_day = simulation_day
            self.events.add_event(0, simulation_day, animal_constants.STILL_BIRTH)

        is_sold = (
            True
            if (self.sex == Sex.MALE or random() > AnimalConfig.keep_female_calf_rate or self.sold_at_day)
            else False
        )
        self.sold_at_day = simulation_day if is_sold else None

        self.birth_weight = args.get("birth_weight")
        self.body_weight = args.get("birth_weight", 0.0)
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
        """
        Initializes the attributes of a calf or heifer.

        Parameters
        ----------
        args : CalfValuesTypedDict or HeiferIValuesTypedDict
            A dictionary containing initial values for the calf or heifer instance.

        """
        self.sex = Sex.FEMALE
        self.birth_weight = args.get("birth_weight")
        self.body_weight = args.get("body_weight")
        self.wean_weight = args.get("wean_weight")
        self.mature_body_weight = args.get("mature_body_weight")
        self.events.init_from_string(args.get("events"))

    def _determine_heifer_reproduction_programs(
        self, args: HeiferIIValuesTypedDict | HeiferIIIValuesTypedDict
    ) -> tuple[HeiferReproductionProtocol | None, HeiferTAISubProtocol | HeiferSynchEDSubProtocol | None]:
        """
        Determines the reproduction program and sub-program for a heifer.

        Parameters
        ----------
        args : HeiferIIValuesTypedDict or HeiferIIIValuesTypedDict
            A dictionary containing information about the heifer reproduction program and sub-program.

        Returns
        -------
        tuple (HeiferReproductionProtocol, HeiferTAISubProtocol | HeiferSynchEDSubProtocol)
            A tuple where the first element is the determined heifer reproduction program and
            the second element is the corresponding sub-program for the specified reproduction program.

        """
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

        return heifer_reproduction_program, heifer_reproduction_sub_program

    def _initialize_heiferII_or_heiferIII(self, args: HeiferIIValuesTypedDict | HeiferIIIValuesTypedDict) -> None:
        """
        Initializes the attributes specific to a heifer in the HeiferII or HeiferIII stage.

        Parameters
        ----------
        args : HeiferIIValuesTypedDict or HeiferIIIValuesTypedDict
            A dictionary-like object containing the attributes and values required
            for setting up the HeiferII or HeiferIII stage, including reproduction
            details and nutrient requirements.

        Returns
        -------
        None

        """
        self._initialize_calf_or_heiferI(args)

        heifer_reproduction_program, heifer_reproduction_sub_program = self._determine_heifer_reproduction_programs(
            args
        )
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
        """
        Initializes the attributes of a cow object using the provided arguments.

        Parameters
        ----------
        args : CowValuesTypedDict
            A dictionary containing values used for initializing the cow's attributes.

        Returns
        -------
        None

        """
        self._initialize_heiferII_or_heiferIII(args)
        self.days_in_milk = args.get("days_in_milk", 0)
        self.calves = args.get("parity", 0)
        self.cow_reproduction_program = CowReproductionProtocol(args.get("cow_reproduction_program"))
        self.cow_presynch_program = CowPreSynchSubProtocol(args.get("cow_presynch_program"))
        self.cow_ovsynch_program = CowTAISubProtocol(args.get("cow_ovsynch_program"))
        self.cow_resynch_program = CowReSynchSubProtocol(args.get("cow_resynch_program"))

        calving_interval = args.get("calving_interval", AnimalConfig.calving_interval)
        self.calving_interval = calving_interval if calving_interval > 0 else AnimalConfig.calving_interval

        if self.calves > 0:
            wood_parameters = LactationCurve.get_wood_parameters(self.calves)
            self.milk_production.set_wood_parameters(wood_parameters["l"], wood_parameters["m"], wood_parameters["n"])

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
        ) > AnimalConfig.milk_reduction_maximum
        if is_milk_reduction_too_high is True:
            return False
        self.milk_production.milk_production_reduction += AnimalModuleConstants.MILK_REDUCTION_KG
        return True

    def _daily_nutrients_update(self) -> None:
        """
        Updates the daily nutrients requirements and performs phosphorus update.

        This method compiles the daily nutrient inputs required for the animal
        based on its type, weight, growth, pregnancy stages, milk production,
        and other factors. It then triggers the process to update the animal's
        phosphorus requirements.

        """
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

    def _daily_digestive_system_update(self) -> None:
        """
        Performs the daily digestive system updates for the animal.

        This method gathers all relevant inputs related to the animal's digestive
        system, including nutritional supply, metabolic energy intake, and milk
        production factors, into a `DigestiveSystemInputs` instance. It then
        passes these inputs to the `process_digestion` method of the `digestive_system`
        object, which simulates and calculates digestion-related processes for the day.

        """
        digestive_system_inputs = DigestiveSystemInputs(
            animal_type=self.animal_type,
            body_weight=self.body_weight,
            nutrients=self.nutrition_supply,
            days_in_milk=self.days_in_milk,
            metabolizable_energy_intake=self.nutrition_supply.metabolizable_energy,
            phosphorus_intake=self.nutrients.phosphorus_intake,
            phosphorus_requirement=self.nutrients.phosphorus_requirement,
            phosphorus_reserves=self.nutrients.phosphorus_reserves,
            phosphorus_endogenous_loss=self.nutrients.phosphorus_endogenous_loss,
            daily_milk_produced=self.milk_production.daily_milk_produced,
            fat_content=MilkProduction.fat_percent,
            protein_content=self.milk_production.true_protein_content,
        )
        self.digestive_system.process_digestion(digestive_system_inputs)

    def daily_milking_update(self, time: RufasTime) -> None:
        """
        Performs the daily milk production update.

        If the animal type is not a cow, the method exits without performing any operation.
        For cows, the method calculates the milking updates using the animal's daily metrics
        and adjusts the milking-related data accordingly.

        Parameters
        ----------
        time : RufasTime
            The current time context for the daily milking update.

        """
        if not self.animal_type.is_cow:
            return
        milk_production_inputs = MilkProductionInputs(
            days_in_milk=self.days_in_milk,
            days_born=self.days_born,
            days_in_pregnancy=self.days_in_pregnancy,
        )
        milk_production_outputs: MilkProductionOutputs = self.milk_production.perform_daily_milking_update(
            milk_production_inputs, time
        )
        self._milk_production_output_days_in_milk = milk_production_outputs.days_in_milk
        self.events += milk_production_outputs.events

    def daily_milking_update_without_history(self) -> None:
        """
        Performs the daily milk production update without updating the milk production history attributes.
        Intended for use prior to first ration formulation interval, since that process requires the milk production
        to be set for proper estimation of animal requirements.

        If the animal type is not a cow, the method exits without performing any operation.
        For cows, the method calculates the milking updates using the animal's daily metrics
        and adjusts the milking-related data accordingly.

        """
        if not self.animal_type.is_cow:
            return
        milk_production_inputs = MilkProductionInputs(
            days_in_milk=self.days_in_milk,
            days_born=self.days_born,
            days_in_pregnancy=self.days_in_pregnancy,
        )
        milk_production_outputs: MilkProductionOutputs = (
            self.milk_production.perform_daily_milking_update_without_history(milk_production_inputs)
        )
        self._milk_production_output_days_in_milk = milk_production_outputs.days_in_milk

    def daily_growth_update(self, time: RufasTime) -> None:
        """
        Updates the daily growth parameters of the animal based on the provided time input.

        This method gathers the necessary animal attributes and performs the daily body weight update. It then updates
        attributes such as body weight, conceptual weight, and events of the animal accordingly.

        Parameters
        ----------
        time : RufasTime
            The RufasTime instance used for updating growth and body weight changes.

        """
        growth_inputs = GrowthInputs(
            days_in_pregnancy=self.days_in_pregnancy,
            animal_type=self.animal_type,
            body_weight=self.body_weight,
            mature_body_weight=self.mature_body_weight,
            birth_weight=self.birth_weight,
            days_born=self.days_born,
            days_in_milk=self.days_in_milk,
            conceptus_weight=self.conceptus_weight,
            gestation_length=self.gestation_length,
            calf_birth_weight=self.calf_birth_weight,
            calves=self.calves,
            calving_interval=self.calving_interval,
        )
        growth_outputs: GrowthOutputs = self.growth.evaluate_body_weight_change(growth_inputs, time)
        self.body_weight = growth_outputs.body_weight
        self.events += growth_outputs.events
        self.conceptus_weight = growth_outputs.conceptus_weight

    def _determine_days_in_milk(self, reproduction_output_days_in_milk: int) -> int:
        """
        Determines the days in milk based on the values of the initial `days_in_milk`,
        milk production output `days_in_milk` and the reproduction output `days_in_milk`.

        Parameters
        ----------
        reproduction_output_days_in_milk : int
            The `days_in_milk` value from the reproduction update result.

        Returns
        -------
        int
            The determined `days_in_milk`.

        Raises
        ------
        ValueError
            If the `days_in_milk` attribute has an negative or invalid value.

        Notes
        -----
        This method determines the `days_in_milk` value based on the following conditions:

        1. **If the animal is not lactating at the start of the day (`self.days_in_milk == 0`)**:
            - The method uses the `days_in_milk` value from the reproduction update.
            - This is because a dry cow (not lactating) always has `days_in_milk = 0` in the milk production update.
            - However, if the animal gives birth that day, the reproduction update will set `days_in_milk = 1`.

        2. **If the animal is lactating at the start of the day (`self.days_in_milk > 0`)**:
            - In most cases, the method uses the `days_in_milk` value from the milk production update.
            - This is because the reproduction update does not change the `days_in_milk` for lactating cows.
            - The milk production update may either:
                - Increment `days_in_milk` by 1 (normal lactation progression).
                - Set `days_in_milk` to 0 if the animal is scheduled to dry off.

        3. **Edge case: If the animal dries off and gives birth on the same day**:
            - The lactation cycle restarts, and `days_in_milk` is set to 1.
            - This occurs when:
                - The milk production update sets `days_in_milk = 0` (indicating drying off).
                - The reproduction update sets `days_in_milk = 1` (due to giving birth).

        """
        if self.days_in_milk == 0:
            return reproduction_output_days_in_milk
        elif self.days_in_milk > 0:
            if self._milk_production_output_days_in_milk == 0 and reproduction_output_days_in_milk == 1:
                return 1
            return self._milk_production_output_days_in_milk
        else:
            raise ValueError("Unexpected days in milk value")

    def daily_reproduction_update(
        self, time: RufasTime
    ) -> tuple[NewBornCalfValuesTypedDict | None, HerdReproductionStatistics]:
        """
        Handles the daily reproduction state update for an animal.

        Parameters
        ----------
        time : RufasTime
            The RufasTime instance for updating reproduction-related dynamics.

        Returns
        -------
        NewBornCalfValuesTypedDict or None
            A dictionary containing details related to a newly born calf if a calf is born during this update;
            otherwise, None.
        HerdReproductionStatistics
            A collection of statistical properties related to the animal's reproduction lifecycle.

        """
        if not (self.animal_type == AnimalType.HEIFER_II or self.animal_type.is_cow):
            return None, HerdReproductionStatistics()

        newborn_calf_config: NewBornCalfValuesTypedDict | None = None

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
        self.days_in_pregnancy = reproduction_outputs.days_in_pregnancy
        self.nutrients.phosphorus_for_gestation_required_for_calf = (
            reproduction_outputs.phosphorus_for_gestation_required_for_calf
        )

        if self.animal_type.is_cow:
            self.days_in_milk = self._determine_days_in_milk(reproduction_outputs.days_in_milk)

            if reproduction_outputs.newborn_calf_config:
                newborn_calf_config = reproduction_outputs.newborn_calf_config
                if self.calves >= 2:
                    self.calving_interval = self.days_born - self.events.get_most_recent_date(
                        animal_constants.NEW_BIRTH
                    )
                    self.calving_interval_history.append(self.calving_interval)

                wood_parameters = LactationCurve.get_wood_parameters(self.calves)
                self.milk_production.set_wood_parameters(
                    wood_parameters["l"], wood_parameters["m"], wood_parameters["n"]
                )
                self.future_death_date = self.determine_future_death_date()
                self.future_cull_date, self.cull_reason = self.determine_future_cull_date()

        self.events += reproduction_outputs.events

        return newborn_calf_config, reproduction_outputs.herd_reproduction_statistics

    def daily_routines(self, time: RufasTime) -> DailyRoutinesOutput:
        """
        Perform daily routines for the animal, updating its status and outputs.

        Parameters
        ----------
        time : RufasTime
            The RufasTime instance.

        Returns
        -------
        DailyRoutinesOutput
            An object containing the updated animal status and any newborn calf configuration.

        """
        self.days_born += 1
        daily_routines_output: DailyRoutinesOutput = DailyRoutinesOutput(
            animal_status=AnimalStatus.REMAIN,
            newborn_calf_config=None,
            herd_reproduction_statistics=HerdReproductionStatistics(),
        )

        self._daily_nutrients_update()

        self._daily_digestive_system_update()

        self.daily_milking_update(time)

        self.daily_growth_update(time)

        newborn_calf_config, daily_routines_output.herd_reproduction_statistics = self.daily_reproduction_update(time)

        daily_routines_output.animal_status, daily_routines_output.newborn_calf_config = self.animal_life_stage_update(
            time
        )

        if self.animal_type.is_cow and newborn_calf_config is not None:
            daily_routines_output.newborn_calf_config = newborn_calf_config

        if self.animal_type == AnimalType.HEIFER_III and self.is_pregnant:
            self.days_in_pregnancy += 1

        return daily_routines_output

    def _calf_life_stage_update(self, _: RufasTime) -> tuple[AnimalStatus, None]:
        """
        Determines and updates the life stage of a calf based on specific evaluation criteria.
        Transitions the calf to the 'HeiferI' stage if the criteria are met, otherwise retains the current life stage.

        Parameters
        ----------
        _ : RufasTime
            The RufasTime instance.

        Returns
        -------
        tuple[AnimalStatus, None]
            A tuple where the first value indicates whether the life stage was changed
            (AnimalStatus.LIFE_STAGE_CHANGED) or remains the same (AnimalStatus.REMAIN).
            The second value is always None.

        """
        if self._evaluate_calf_for_heiferI():
            self._transition_calf_to_heiferI()
            return AnimalStatus.LIFE_STAGE_CHANGED, None
        return AnimalStatus.REMAIN, None

    def _heiferI_life_stage_update(self, time: RufasTime) -> tuple[AnimalStatus, None]:
        """
        Updates the life stage of a heiferI animal based on specific evaluation criteria.
        If the evaluation determines that the heiferI should transition to heiferII,
        the necessary transition is performed. Otherwise, the animal remains in its current life stage.

        Parameters
        ----------
        time : RufasTime
            The RufasTime instance used for evaluation and transition.

        Returns
        -------
        tuple[AnimalStatus, None]
            AnimalStatus.LIFE_STAGE_CHANGED, None: If the heiferI transitions to the heifer II life stage.
            AnimalStatus.REMAIN, None: If the heiferI remains in the current life stage.

        """
        if self._evaluate_heiferI_for_heiferII():
            self._transition_heiferI_to_heiferII(time)
            return AnimalStatus.LIFE_STAGE_CHANGED, None
        return AnimalStatus.REMAIN, None

    def _heiferII_life_stage_update(self, time: RufasTime) -> tuple[AnimalStatus, None]:
        """
        Updates the life stage of a heiferII based on evaluation criteria such as culling or transitioning to heiferIII.
        If the evaluation determines that the heiferII should transition to heiferIII,
        the necessary transition is performed. Otherwise, the animal remains in its current life stage.

        Parameters
        ----------
        time : RufasTime
            The RufasTime object, used to determine the current simulation day.

        Returns
        -------
        tuple[AnimalStatus, None]
            A tuple containing the status of the animal (whether it is sold, its life stage
            has changed, or it remains in the current state) and None.

        """
        if self._evaluate_heiferII_for_culling():
            self.sold_at_day = time.simulation_day
            return AnimalStatus.SOLD, None
        elif self._evaluate_heiferII_for_heiferIII():
            self._transition_heiferII_to_heiferIII()
            return AnimalStatus.LIFE_STAGE_CHANGED, None
        else:
            return AnimalStatus.REMAIN, None

    def _heiferIII_life_stage_update(self, time: RufasTime) -> tuple[AnimalStatus, NewBornCalfValuesTypedDict | None]:
        """
        Updates the life stage of a HeiferIII animal.

        Evaluates whether a HeiferIII animal transitions to the Cow life stage.
        If a transition occurs, newborn calf configuration data is returned.
        Otherwise, the animal remains in the HeiferIII stage and no calf data is produced.

        Parameters
        ----------
        time : RufasTime
            The RufasTime instance used to evaluate the life stage transition.

        Returns
        -------
        tuple[AnimalStatus, NewBornCalfValuesTypedDict | None]
            A tuple containing the animal status and optional newborn calf data.

            * `AnimalStatus.LIFE_STAGE_CHANGED` and newborn calf configuration
            if the animal transitions to Cow.
            * `AnimalStatus.REMAIN` and `None` if the animal remains in the
            HeiferIII stage.
        """
        if self.evaluate_heiferIII_for_cow():
            newborn_calf_config = self.transition_heiferIII_to_cow(time)
            return AnimalStatus.LIFE_STAGE_CHANGED, newborn_calf_config
        else:
            return AnimalStatus.REMAIN, None

    def _cow_life_stage_update(self, _: RufasTime) -> tuple[AnimalStatus, None]:
        """
        Updates the life stage of a cow based on its milking status and current animal type.

        Parameters
        ----------
        _ : RufasTime
            The RufasTime instance.

        Returns
        -------
        tuple[AnimalStatus, None]
            A tuple where the first element indicates whether the life stage has changed or remains the same,
            and the second element is always None.

        """
        if self.animal_type == AnimalType.LAC_COW and self.is_milking is False:
            self.animal_type = AnimalType.DRY_COW
            self.milk_production.milk_production_reduction = 0
            return AnimalStatus.LIFE_STAGE_CHANGED, None
        elif self.animal_type == AnimalType.DRY_COW and self.is_milking:
            self.animal_type = AnimalType.LAC_COW
            return AnimalStatus.LIFE_STAGE_CHANGED, None
        else:
            return AnimalStatus.REMAIN, None

    def animal_life_stage_update(self, time: RufasTime) -> tuple[AnimalStatus, NewBornCalfValuesTypedDict | None]:
        """
        Updates the life stage of an animal based on its type and current simulation time.

        Parameters
        ----------
        time : RufasTime
            The RufasTime instance used to determine life stage updates for the animal.

        Returns
        -------
        tuple[AnimalStatus, NewBornCalfValuesTypedDict | None]
            A tuple containing the updated animal status and, if applicable, configuration for a newborn calf.

        """
        ANIMAL_TYPE_TO_LIFE_STAGE_UPDATE_METHOD_MAP: dict[
            AnimalType, Callable[[RufasTime], tuple[AnimalStatus, NewBornCalfValuesTypedDict | None]]
        ] = {
            AnimalType.CALF: self._calf_life_stage_update,
            AnimalType.HEIFER_I: self._heiferI_life_stage_update,
            AnimalType.HEIFER_II: self._heiferII_life_stage_update,
            AnimalType.HEIFER_III: self._heiferIII_life_stage_update,
            AnimalType.LAC_COW: self._cow_life_stage_update,
            AnimalType.DRY_COW: self._cow_life_stage_update,
        }
        animal_status, newborn_calf_config = ANIMAL_TYPE_TO_LIFE_STAGE_UPDATE_METHOD_MAP[self.animal_type](time)

        if self.days_born == self.future_cull_date:
            self.sold_at_day = time.simulation_day
            animal_status = AnimalStatus.SOLD
        if self.days_born == self.future_death_date:
            self.dead_at_day = time.simulation_day
            self.cull_reason = animal_constants.DEATH_CULL
            animal_status = AnimalStatus.DEAD

        if (
            self.animal_type.is_cow
            and self.reproduction.do_not_breed
            and self.milk_production.daily_milk_produced < AnimalConfig.cull_milk_production
        ):
            self.cull_reason = animal_constants.LOW_PROD_CULL
            self.sold_at_day = time.simulation_day
            animal_status = AnimalStatus.SOLD
        return animal_status, newborn_calf_config

    def _evaluate_calf_for_heiferI(self) -> bool:
        """
        Evaluates if the calf qualifies as a heiferI based on its weaning day.

        Returns
        -------
        bool
            True if the calf has reached the weaning day as defined in AnimalConfig,
            False otherwise.

        """
        return self.days_born == AnimalConfig.wean_day

    def _evaluate_heiferI_for_heiferII(self) -> bool:
        """
        Checks if heiferI is ready for heiferII stage based on the breeding start day.

        Returns
        -------
        bool
            True if the heiferI's days born is equal to the configured heifer breed start day,
            False otherwise.

        """
        return self.days_born == AnimalConfig.heifer_breed_start_day

    def _evaluate_heiferII_for_heiferIII(self) -> bool:
        """
        Evaluate if a heiferII can transition to heiferIII stage.

        Returns
        -------
        bool
            True if the heifer meets all the conditions to transition to heifer III,
            False otherwise.

        """
        return (
            self.days_born > AnimalConfig.heifer_breed_start_day
            and self.is_pregnant
            and self.days_in_pregnancy > (self.gestation_length - AnimalConfig.heifer_prefresh_day)
        )

    def _evaluate_heiferII_for_culling(self) -> bool:
        """
        Determines whether a heiferII should be culled based on pregnancy status and age.

        Returns
        -------
        bool
            True if the heiferII is not pregnant and its age in days exceeds the culling threshold,
            False otherwise.

        """
        return (not self.is_pregnant) and (self.days_born > AnimalConfig.heifer_reproduction_cull_day)

    def evaluate_heiferIII_for_cow(self) -> bool:
        """
        Checks if a heiferIII has reached the expected gestation period, indicating it ready to become a cow.

        Returns
        -------
        bool
            True if the heiferIII is ready to become a cow;
            False otherwise.
        """
        return self.days_in_pregnancy == self.gestation_length

    def _transition_calf_to_heiferI(self) -> None:
        """
        Handles the transition of an animal from CALF to HEIFER_I stage.

        """
        self.animal_type = AnimalType.HEIFER_I

    def _transition_heiferI_to_heiferII(self, time: RufasTime) -> None:
        """
        Handles the transition of an animal from HEIFER_I to HEIFER_II stage.

        Parameters
        ----------
        time : RufasTime
            The RufasTime object used to update reproduction information.

        """
        self.animal_type = AnimalType.HEIFER_II

        self.heifer_reproduction_program = AnimalConfig.heifer_reproduction_program
        self.heifer_reproduction_sub_program = AnimalConfig.heifer_reproduction_sub_program

        self.daily_reproduction_update(time)

    def _transition_heiferII_to_heiferIII(self) -> None:
        """
        Transitions the animal state from HEIFER II to HEIFER III.

        """
        self.reproduction.reproduction_statistics = AnimalReproductionStatistics()
        self.animal_type = AnimalType.HEIFER_III

    def transition_heiferIII_to_cow(self, time: RufasTime) -> NewBornCalfValuesTypedDict:
        """
        Handles the transition of a HeiferIII to a Cow and initializes the necessary parameters for the cow.

        Parameters
        ----------
        time : RufasTime
            The RufasTime object at which the transition occurs.

        Returns
        -------
        NewBornCalfValuesTypedDict
            A dictionary containing the configuration for the newly born calf.

        Raises
        ------
        ValueError
            Raised if the HeiferIII does not give birth to a calf during the transition to a cow.

        """
        self.animal_type = AnimalType.LAC_COW

        self.cow_reproduction_program = AnimalConfig.cow_reproduction_program
        self.reproduction.cow_presynch_program = AnimalConfig.cow_presynch_method
        self.reproduction.cow_ovsynch_program = AnimalConfig.cow_tai_method
        self.reproduction.cow_resynch_program = AnimalConfig.cow_resynch_method

        self.calving_interval = AnimalConfig.calving_interval

        newborn_calf_config, _ = self.daily_reproduction_update(time)

        if not newborn_calf_config:
            raise ValueError(f"HeiferIII {self.id} should give birth to a calf when transitioning to cow.")

        wood_parameters = LactationCurve.get_wood_parameters(self.calves)
        self.milk_production.set_wood_parameters(wood_parameters["l"], wood_parameters["m"], wood_parameters["n"])
        return newborn_calf_config

    def get_animal_values(
        self,
    ) -> (
        CalfValuesTypedDict
        | HeiferIValuesTypedDict
        | HeiferIIValuesTypedDict
        | HeiferIIIValuesTypedDict
        | CowValuesTypedDict
    ):
        """
        Get the attribute values of the animal.

        Returns
        -------
        (CalfValuesTypedDict | HeiferIValuesTypedDict | HeiferIIValuesTypedDict | HeiferIIIValuesTypedDict |
         CowValuesTypedDict)
            A dictionary containing key-value pairs specific to the current animal.

        Raises
        ------
        KeyError
            If the animal_type is not present in the mapping dictionary.

        """
        mapping: dict[AnimalType, Callable[[], Any]] = {
            AnimalType.CALF: self._get_calf_values,
            AnimalType.HEIFER_I: self._get_heiferI_values,
            AnimalType.HEIFER_II: self._get_heiferII_values,
            AnimalType.HEIFER_III: self._get_heiferIII_values,
            AnimalType.DRY_COW: self._get_cow_values,
            AnimalType.LAC_COW: self._get_cow_values,
        }
        return mapping[self.animal_type]()

    def _get_calf_values(self) -> CalfValuesTypedDict:
        """
        Get the attribute values for calf.

        Returns
        -------
        CalfValuesTypedDict
            A dictionary containing key-value pairs specific to the current animal.

        """
        return CalfValuesTypedDict(
            id=self.id,
            breed=self.breed.name,
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
        """
        Get the attribute values for heiferI.

        Returns
        -------
        HeiferIValuesTypedDict
            A dictionary containing key-value pairs specific to the current animal.

        """
        return HeiferIValuesTypedDict(
            id=self.id,
            breed=self.breed.name,
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
        """
        Get the attribute values for heiferII.

        Returns
        -------
        HeiferIIValuesTypedDict
            A dictionary containing key-value pairs specific to the current animal.

        """
        return HeiferIIValuesTypedDict(
            id=self.id,
            breed=self.breed.name,
            animal_type=self.animal_type.value,
            days_born=self.days_born,
            birth_weight=self.birth_weight,
            body_weight=self.body_weight,
            wean_weight=self.wean_weight,
            mature_body_weight=self.mature_body_weight,
            events=str(self.events),
            net_merit=self.net_merit,
            heifer_reproduction_program=self.heifer_reproduction_program.value,
            heifer_reproduction_sub_protocol=self.heifer_reproduction_sub_program.value,
            estrus_count=self.reproduction.reproduction_statistics.estrus_count,
            estrus_day=self.reproduction.estrus_day,
            conception_rate=self.reproduction.conception_rate,
            ai_day=self.reproduction.ai_day,
            abortion_day=self.reproduction.abortion_day,
            days_in_pregnancy=self.days_in_pregnancy,
            gestation_length=self.gestation_length,
            phosphorus_for_gestation_required_for_calf=self.nutrients.phosphorus_for_gestation_required_for_calf,
            calf_birth_weight=self.calf_birth_weight,
        )

    def _get_heiferIII_values(self) -> HeiferIIIValuesTypedDict:
        """
        Get the attribute values for heiferIII.

        Returns
        -------
        HeiferIIIValuesTypedDict
            A dictionary containing key-value pairs specific to the current animal.

        """
        return HeiferIIIValuesTypedDict(
            id=self.id,
            breed=self.breed.name,
            animal_type=self.animal_type.value,
            days_born=self.days_born,
            birth_weight=self.birth_weight,
            body_weight=self.body_weight,
            wean_weight=self.wean_weight,
            mature_body_weight=self.mature_body_weight,
            events=str(self.events),
            net_merit=self.net_merit,
            heifer_reproduction_program=self.heifer_reproduction_program.value,
            heifer_reproduction_sub_protocol=self.heifer_reproduction_sub_program.value,
            estrus_count=self.reproduction.reproduction_statistics.estrus_count,
            estrus_day=self.reproduction.estrus_day,
            conception_rate=self.reproduction.conception_rate,
            ai_day=self.reproduction.ai_day,
            abortion_day=self.reproduction.abortion_day,
            days_in_pregnancy=self.days_in_pregnancy,
            gestation_length=self.gestation_length,
            phosphorus_for_gestation_required_for_calf=self.nutrients.phosphorus_for_gestation_required_for_calf,
            calf_birth_weight=self.calf_birth_weight,
        )

    def _get_cow_values(self) -> CowValuesTypedDict:
        """
        Get the attribute values for cow.

        Returns
        -------
        CowValuesTypedDict
            A dictionary containing key-value pairs specific to the current animal.

        """
        return CowValuesTypedDict(
            id=self.id,
            breed=self.breed.name,
            animal_type=self.animal_type.value,
            days_born=self.days_born,
            birth_weight=self.birth_weight,
            body_weight=self.body_weight,
            wean_weight=self.wean_weight,
            mature_body_weight=self.mature_body_weight,
            events=str(self.events),
            net_merit=self.net_merit,
            calf_birth_weight=self.calf_birth_weight,
            heifer_reproduction_program=self.heifer_reproduction_program.value,
            heifer_reproduction_sub_protocol=self.heifer_reproduction_sub_program.value,
            cow_reproduction_program=self.cow_reproduction_program.value,
            cow_presynch_program=self.cow_presynch_program.value,
            cow_ovsynch_program=self.cow_ovsynch_program.value,
            cow_resynch_program=self.cow_resynch_program.value,
            estrus_count=self.reproduction.reproduction_statistics.estrus_count,
            estrus_day=self.reproduction.estrus_day,
            conception_rate=self.reproduction.conception_rate,
            ai_day=self.reproduction.ai_day,
            abortion_day=self.reproduction.abortion_day,
            days_in_pregnancy=self.days_in_pregnancy,
            gestation_length=self.gestation_length,
            phosphorus_for_gestation_required_for_calf=self.nutrients.phosphorus_for_gestation_required_for_calf,
            days_in_milk=self.days_in_milk,
            calving_interval=self.calving_interval,
            parity=self.calves,
        )

    def determine_future_death_date(self) -> int:
        """
        Determine the future death date of the animal based on its parity.

        Returns
        -------
        int
            Calculated future death date in simulation days.

        Notes
        -------
        [AN.ANM.1]

        """
        if self.calves >= 4:
            death_rate = AnimalConfig.parity_death_probability[3]
        else:
            death_rate = AnimalConfig.parity_death_probability[self.calves - 1]
        death_rand = random()
        if death_rand <= death_rate:
            death_probability_upper_limit = death_probability_lower_limit = 0.0
            death_time_upper_limit = death_time_lower_limit = 0.0
            death_date_random = random()
            for i in range(len(AnimalConfig.death_day_probability) - 1):
                if (
                    AnimalConfig.death_day_probability[i]
                    <= death_date_random
                    < AnimalConfig.death_day_probability[i + 1]
                ):
                    death_probability_lower_limit = AnimalConfig.death_day_probability[i]
                    death_probability_upper_limit = AnimalConfig.death_day_probability[i + 1]
                    death_time_lower_limit = AnimalConfig.cull_day_count[i]
                    death_time_upper_limit = AnimalConfig.cull_day_count[i + 1]
            n = (death_time_upper_limit - death_time_lower_limit) / (
                death_probability_upper_limit - death_probability_lower_limit
            )
            return round(
                death_time_lower_limit + n * (death_date_random - death_probability_lower_limit) + self.days_born
            )
        return sys.maxsize

    def determine_future_cull_date(self) -> tuple[int, str]:
        """
        Determine the future cull date and reason for the animal based on parity-specific probabilities.

        Returns
        -------
        tuple[int, str]
            Future cull date in simulation days and reason for culling.

        Notes
        -------
        [AN.ANM.2]

        """
        cull_reason = ""
        future_cull_date = sys.maxsize
        if self.calves >= 4:
            inv_cull_rate = AnimalConfig.parity_cull_probability[3]
        else:
            inv_cull_rate = AnimalConfig.parity_cull_probability[self.calves - 1]
        cull_rand = random()
        if cull_rand <= inv_cull_rate:
            cull_reason_rand = random()
            cull_prob = 0.0
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
            cull_reason_upper_limit = cull_reason_lower_limit = cull_time_upper_limit = cull_time_lower_limit = 0.0
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

        Parameters
        ----------
        current_pen: int
            The id of the new pen that the animal is assigned to.
        current_day: int
            The current simulation day.
        animal_types_in_pen: set[AnimalType]
            The animal types in the new pen that the animal is assigned to.

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
        else:
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
            # TODO: do not use dummy values for calf calcium and phosphorus requirements - issue 2517.
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
            ndf_percentage = self.previous_nutrition_supply.ndf_supply / previous_dmi
            tdn_percentage = self.previous_nutrition_supply.tdn_supply / previous_dmi
            net_energy_diet_conc = self.previous_nutrition_supply.metabolizable_energy / previous_dmi

        if self.nutrient_standard is NutrientStandard.NASEM:
            requirements = NASEMRequirementsCalculator.calculate_requirements(
                body_weight=self.body_weight,
                mature_body_weight=self.mature_body_weight,
                day_of_pregnancy=days_in_pregnancy,
                body_condition_score_5=self.body_condition_score_5,
                days_in_milk=days_in_milk,
                average_daily_gain_heifer=self.growth.daily_growth,
                animal_type=self.animal_type,
                parity=self.calves,
                calving_interval=self.calving_interval,
                milk_fat=MilkProduction.fat_percent,
                milk_true_protein=MilkProduction.true_protein_percent,
                milk_lactose=MilkProduction.lactose_percent,
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
                parity=self.calves,
                calving_interval=self.calving_interval,
                milk_fat=MilkProduction.fat_percent,
                milk_true_protein=MilkProduction.true_protein_percent,
                milk_lactose=MilkProduction.lactose_percent,
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
