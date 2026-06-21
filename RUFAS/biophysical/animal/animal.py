import sys
from datetime import timedelta
from random import random
from typing import Any, Callable, cast

from scipy.stats import truncnorm
from numpy import sqrt

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_genetics.animal_genetics import Genetics
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus, BeefPostWeaningDestination, Breed, Sex
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.body_weight_history import BodyWeightHistory
from RUFAS.biophysical.animal.data_types.daily_routines_output import DailyRoutinesOutput
from RUFAS.biophysical.animal.data_types.digestive_system import DigestiveSystemInputs
from RUFAS.biophysical.animal.data_types.genetic_history import GeneticHistory
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
from RUFAS.biophysical.animal.nutrients.beef_nrc_requirements_calculator import BeefNRCRequirementsCalculator
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import (
    NewBornCalfValuesTypedDict,
    BeefCowCalfValuesTypedDict,
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
    ReproStateEnum,
    BeefReproductionProtocol,
)
from RUFAS.biophysical.animal.reproduction.beef_reproduction import calculate_seasonal_conception_probability
from RUFAS.biophysical.animal.milk.lactation_curve import LactationCurve
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements
from RUFAS.biophysical.animal.ration.calf_ration_manager import CalfRationManager
from RUFAS.data_structures.feed_storage_to_animal_connection import NASEMFeed, NRCFeed
from RUFAS.biophysical.animal.reproduction.reproduction import Reproduction
from RUFAS.data_structures.feed_storage_to_animal_connection import NutrientStandard, Feed
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime


class Animal:
    """
    This class represents an animal in the RuFaS simulation.

    Parameters
    ----------
    args : NewBornCalfValuesTypedDict | CalfValuesTypedDict | HeiferIValuesTypedDict | HeiferIIValuesTypedDict \
        | HeiferIIIValuesTypedDict | CowValuesTypedDict
        Configuration data used to initialize the animal. The required keys depend on the animal type being created and
        may include identifiers, breed, age, body weight, reproduction status, and other life-stage-specific attributes.

    time : RufasTime
        Simulation time information used during initialization, including the
        current simulation day and calendar date.

    Attributes
    ----------
    nutrient_standard: NutrientStandard
        The nutrient standard used to calculate nutrition related values.
    om : OutputManager
        The singleton output manager used for model outputs.
    id: int
        The unique identifier of the animal, (unitless).
    breed: Breed
        The breed of the animal.
    animal_type: AnimalType
        The current life stage of the animal.
    days_born: int
        The age of the animal, (simulation days).
    birth_weight: float
        The birth weight of the animal, (kg).
    body_weight: float
        The body weight of the animal, (kg).
    body_condition_score_5: float
        The body condition score on a scale of 1 to 5, (unitless).
    cull_reason: str
        The reason for the animal to leave the herd.
    body_weight_history: list[BodyWeightHistory]
        The body weight history of the animal.
    pen_history: list[PenHistory]
        The pen history of the animal.
    sold_at_day: int, optional
        The simulation day in which the animal was sold.
    stillborn_day : int, optional
        The simulation day on which the animal was stillborn.
    dead_at_day: int, optional
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
    reproduction: Reproduction
        The reproduction submodule that handles the daily reproduction update of the animal.
    nutrition_requirements: NutrientsRequirements
        The nutrition requirement for the animal.
    nutrition_supply: NutritionSupply
        The supplied nutrition in the current ration interval for the animal.
    previous_nutrition_supply: NutritionSupply, optional
        Nutrition supplied during the previous ration interval.
    days_in_milk: int
        The number of days that the animal has been in milk production, (days).
    _milk_production_output_days_in_milk : int
        Days in milk used for milk production output reporting, (simulation days).
    days_in_pregnancy: int
        The number of days that the animal has been in pregnancy, (days).
    future_cull_date: int, optional
        The age of which the animal will be culled, (day).
    future_death_date: int, optional
        The age of which the animal will die, (day).
    daily_horizontal_distance: float
        The daily horizontal distance traveled by the animal, (m).
    daily_vertical_distance: float
        The daily vertical distance traveled by the animal, (m).
    daily_distance: float
        The total daily distance traveled by the animal, (m).
    genetics: Genetics, optional
        The genetic attributes of the animal.
    mature_body_weight: float
        The mature body weight of the animal, (kg).
    wean_weight: float
        The body weight of the animal at weaning, (kg).
    genetic_history: list[GeneticHistory]
        The genetic history of the animal.
    sex: Sex
        The sex of the animal.

    """

    nutrient_standard: NutrientStandard

    def __init__(
        self,
        args: (
            NewBornCalfValuesTypedDict
            | BeefCowCalfValuesTypedDict
            | CalfValuesTypedDict
            | HeiferIValuesTypedDict
            | HeiferIIValuesTypedDict
            | HeiferIIIValuesTypedDict
            | CowValuesTypedDict
        ),
        time: RufasTime,
    ) -> None:
        """
        Initializes an Animal object.
        """
        self.om = OutputManager()
        initialize_animal_methods: dict[AnimalType, Callable[..., None]] = {
            AnimalType.CALF: self._initialize_calf_or_heiferI,
            AnimalType.HEIFER_I: self._initialize_calf_or_heiferI,
            AnimalType.HEIFER_II: self._initialize_heiferII_or_heiferIII,
            AnimalType.HEIFER_III: self._initialize_heiferII_or_heiferIII,
            AnimalType.LAC_COW: self._initialize_cow,
            AnimalType.DRY_COW: self._initialize_cow,
            AnimalType.FEEDLOT_STEER: self._initialize_feedlot_animal,
            AnimalType.FEEDLOT_HEIFER: self._initialize_feedlot_animal,
            AnimalType.BEEF_CALF: self._initialize_beef_cow_calf_animal,
            AnimalType.BEEF_HEIFER_REPLACEMENT: self._initialize_beef_cow_calf_animal,
            AnimalType.BEEF_COW: self._initialize_beef_cow_calf_animal,
            AnimalType.BEEF_BULL: self._initialize_beef_cow_calf_animal,
        }
        self.id = args.get("id", 0)
        self.breed: Breed = Breed(Breed[args.get("breed")])
        self.animal_type = AnimalType(args.get("animal_type"))
        self.days_born = int(args.get("days_born"))
        # birth_weight is unused for feedlot and beef cow-calf animals (factory-managed)
        self.birth_weight = (
            0.0
            if self.animal_type.is_feedlot or self.animal_type.is_beef_cow_calf
            else float(args.get("birth_weight") or 0.0)
        )
        self.body_condition_score_5 = AnimalModuleConstants.DEFAULT_BODY_CONDITION_SCORE_5

        self.cull_reason = ""
        self.body_weight_history: list[BodyWeightHistory] = []
        self.pen_history: list[PenHistory] = []
        self.genetic_history: list[GeneticHistory] = []
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

        # Feedlot tracking attributes (default to safe values for all animal types)
        self.days_on_feed: int = 0
        self.entry_weight: float = 0.0
        self.cumulative_dmi: float = 0.0
        self.receiving_stress: bool = False
        self.step_up_phase: str = ""

        # Beef cow-calf attributes (default to safe values for all animal types)
        self.days_in_breeding_season: int | None = None
        self.calf_at_side: Animal | None = None
        self.dam: Animal | None = None
        self.lactation_day: int = 0
        self.days_since_calving: int = 0
        self.body_condition_score_9: float = AnimalModuleConstants.BEEF_DEFAULT_BCS_9
        self.times_calved: int = 0
        self.is_open: bool = True
        self._breeding_weight_event_fired: bool = False

        is_newborn_calf = self.animal_type == AnimalType.CALF and "body_weight" not in args.keys()
        if is_newborn_calf:
            newborn_args = cast(NewBornCalfValuesTypedDict, args)
            self._initialize_newborn_calf(newborn_args, time.simulation_day)
            self._initialize_newborn_calf_genetics(newborn_args, time)
        else:
            initialize_animal_methods[self.animal_type](args)
            self.genetics = (
                Genetics(
                    birth_year=(time.current_date - timedelta(days=self.days_born)).year,
                    animal_type=self.animal_type,
                    initialize_new_born_calf=False,
                )
                if AnimalConfig.simulate_genetics
                else None
            )
        self.update_genetic_history(simulation_day=time.simulation_day)

    def _initialize_newborn_calf_genetics(self, newborn_args: NewBornCalfValuesTypedDict, time: RufasTime) -> None:
        """
        Initializes the genetics for a newborn calf.

        If genetics simulation is enabled, a ``Genetics`` object is created using dam
        true breeding values (TBV) for fat and protein when both are available. If either
        dam TBV value is absent, genetics are initialized without dam information using
        the current parity count. If genetics simulation is disabled, genetics are set
        to ``None``.

        Parameters
        ----------
        newborn_args : NewBornCalfValuesTypedDict
            Dictionary of values for the newborn calf, including optional dam TBV
            values for fat and protein.
        time : RufasTime
            RufasTime object containing the current date of the simulation, used to
            set the birth year and month of the calf's genetics.
        """
        if AnimalConfig.simulate_genetics:
            dam_tbv_fat, dam_tbv_protein = newborn_args.get("dam_tbv_fat"), newborn_args.get("dam_tbv_protein")
            if dam_tbv_fat and dam_tbv_protein:
                self.genetics = Genetics(
                    birth_year=time.current_date.year,
                    birth_month=time.current_date.month,
                    animal_type=AnimalType.CALF,
                    initialize_new_born_calf=True,
                    dam_tbv_fat=dam_tbv_fat,
                    dam_tbv_protein=dam_tbv_protein,
                )
            else:
                self.genetics = Genetics(
                    birth_year=time.current_date.year,
                    animal_type=AnimalType.CALF,
                    initialize_new_born_calf=False,
                )
        else:
            self.genetics = None

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
            self.om.add_error(
                "Days in pregnancy setter error",
                "Pregnant animal cannot be type CALF or Heifer_I.",
                info_map={"class": self.__class__.__name__, "function": "days_in_pregnancy.setter"},
            )
            raise TypeError("Pregnant animal cannot be type CALF or Heifer_I.")
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

        Returns
        -------
        int
            The future cull date or the maximum possible integer value if the animal is not a cow.

        """
        if not self.animal_type.is_cow:
            return sys.maxsize
        return self._future_cull_date if self._future_cull_date is not None else sys.maxsize

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
            self.om.add_error(
                "Future cull date setter error",
                "The animal attempting to be assigned a cull date must be a cow.",
                info_map={"class": self.__class__.__name__, "function": "future_cull_date.setter"},
            )
            raise TypeError("The animal attempting to be assigned a cull date is not a cow.")
        self._future_cull_date = future_cull_date

    @property
    def future_death_date(self) -> int:
        """
        Returns the future death date of the animal.

        Returns
        -------
        int
            The future death date of the animal in integer form (sys.maxsize for non-cow animals).

        """
        if not self.animal_type.is_cow:
            return sys.maxsize
        return self._future_death_date if self._future_death_date is not None else sys.maxsize

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
            self.om.add_error(
                "Future death date setter error",
                "The animal attempting to be assigned a future death date must be a cow.",
                info_map={"class": self.__class__.__name__, "function": "future_death_date.setter"},
            )
            raise TypeError("The animal attempting to be assigned a future death date is not a cow.")
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
            self.om.add_error(
                "Daily horizontal distance property error",
                "The animal whose daily horizontal distance is attempting to be referenced must be a cow.",
                info_map={"class": self.__class__.__name__, "function": "daily_horizontal_distance.property"},
            )
            raise TypeError("The animal's daily horizontal distance attempting to be referenced here is not a cow.")
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
            self.om.add_error(
                "Daily horizontal distance setter error",
                "The animal attempting to be assigned a daily horizontal distance must be a cow.",
                info_map={"class": self.__class__.__name__, "function": "daily_horizontal_distance.setter"},
            )
            raise TypeError("The animal attempting to be assigned a daily horizontal distance is not a cow.")
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
            self.om.add_error(
                "Daily vertical distance property error",
                "The animal whose daily vertical distance is attempting to be referenced must be a cow.",
                info_map={"class": self.__class__.__name__, "function": "daily_vertical_distance.property"},
            )
            raise TypeError("The animal's daily vertical distance attempting to be referenced here is not a cow.")
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
            self.om.add_error(
                "Daily vertical distance setter error",
                "The animal attempting to be assigned a daily vertical distance must be a cow.",
                info_map={"class": self.__class__.__name__, "function": "daily_vertical_distance.setter"},
            )
            raise TypeError("The animal attempting to be assigned a daily vertical distance is not a cow.")
        self._daily_vertical_distance = daily_vertical_distance

    @property
    def daily_distance(self) -> float:
        """
        Returns the daily distance traveled by the animal.

        Returns
        -------
        float
            The daily distance traveled by the animal.

        Notes
        -----
        If the animal is not a cow and is currently milking, the daily distance is considered to be 0.0.
        Otherwise, it returns the value of the stored daily distance.

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
            self.om.add_error(
                "Daily distance setter error",
                "The animal attempting to be assigned a daily distance must be a cow.",
                info_map={"class": self.__class__.__name__, "function": "daily_distance.setter"},
            )
            raise TypeError("The animal attempting to be assigned a daily distance is not a cow.")
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
            self.om.add_error(
                "Reproduction setter error",
                "Reproduction attribute cannot be set for an Animal of type CALF or Heifer_I.",
                info_map={"class": self.__class__.__name__, "function": "reproduction.setter"},
            )
            raise TypeError("Reproduction attribute cannot be set for an Animal of type CALF or Heifer_I.")
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
            self.om.add_error(
                "Calves setter error",
                "The animal attempting to be assigned calves must be a cow.",
                info_map={"class": self.__class__.__name__, "function": "calves.setter"},
            )
            raise TypeError("The animal attempting to be assigned calves is not a cow.")
        self.reproduction.calves = calves

    @property
    def calving_interval(self) -> int:
        """
        Returns the calving interval for the animal.

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
            self.om.add_error(
                "Calving interval setter error",
                "The animal attempting to be assigned a calving interval must be a cow.",
                info_map={"class": self.__class__.__name__, "function": "calving_interval.setter"},
            )
            raise TypeError("The animal attempting to be assigned a calving interval is not a cow.")
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
        Sets the gestation length for the animal. This property is not applicable for animals of type CALF or HEIFER_I
        and will raise a TypeError if attempted to set for these types.

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
            self.om.add_error(
                "Gestation length setter error",
                "The animal attempting to be assigned a gestation length cannot be a CALF or HEIFER_I.",
                info_map={"class": self.__class__.__name__, "function": "gestation_length.setter"},
            )
            raise TypeError("The animal attempting to be assigned a gestation length cannot be a CALF or HEIFER_I.")
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
            self.om.add_error(
                "Calf birth weight setter error",
                "Calf birth weight cannot be set for an Animal of type CALF or Heifer_I.",
                info_map={"class": self.__class__.__name__, "function": "calf_birth_weight.setter"},
            )
            raise TypeError("Calf birth weight cannot be set for an Animal of type CALF or Heifer_I.")
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
            self.om.add_error(
                "Calving interval history property error",
                "Calving interval history is only a property of a cow.",
                info_map={"class": self.__class__.__name__, "function": "calving_interval_history.property"},
            )
            raise TypeError("The calving interval history property is only available for cows.")
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
            self.om.add_error(
                "Heifer repro program property error",
                "heifer_reproduction_program property is not available for an Animal of type CALF or Heifer_I.",
                info_map={"class": self.__class__.__name__, "function": "heifer_reproduction_program.property"},
            )
            raise TypeError("heifer_reproduction_program is not available for an Animal of type CALF or Heifer_I.")
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
            self.om.add_error(
                "Heifer repro program setter error",
                "heifer_reproduction_program cannot be set for an Animal of type CALF or Heifer_I.",
                info_map={"class": self.__class__.__name__, "function": "heifer_reproduction_program.setter"},
            )
            raise TypeError("heifer_reproduction_program cannot be set for an Animal of type CALF or Heifer_I.")
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
            self.om.add_error(
                "Heifer repro sub program property error",
                "heifer_reproduction_sub_program property is not available for an Animal of type CALF or Heifer_I.",
                info_map={"class": self.__class__.__name__, "function": "heifer_reproduction_sub_program.property"},
            )
            raise TypeError("heifer_reproduction_sub_program is not available for an Animal of type CALF or Heifer_I.")
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
            self.om.add_error(
                "Heifer repro sub program setter error",
                "heifer_reproduction_sub_program cannot be set for an Animal of type CALF or Heifer_I.",
                info_map={"class": self.__class__.__name__, "function": "heifer_reproduction_sub_program.setter"},
            )
            raise TypeError("heifer_reproduction_sub_program cannot be set for an Animal of type CALF or Heifer_I.")
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
            self.om.add_error(
                "Cow repro program property error",
                "The animal whose cow_reproduction_program is attempting to be referenced must be a cow.",
                info_map={"class": self.__class__.__name__, "function": "cow_reproduction_program.property"},
            )
            raise TypeError("The animal's cow_reproduction_program attempting to be referenced here is not a cow.")
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
            self.om.add_error(
                "Cow repro program setter error",
                "The animal attempting to be assigned a cow_reproduction_program must be a cow.",
                info_map={"class": self.__class__.__name__, "function": "cow_reproduction_program.setter"},
            )
            raise TypeError("The animal attempting to be assigned a cow_reproduction_program is not a cow.")
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
            self.om.add_error(
                "Cow presynch program property error",
                "The animal whose cow_presynch_program is attempting to be referenced must be a cow.",
                info_map={"class": self.__class__.__name__, "function": "cow_presynch_program.property"},
            )
            raise TypeError("The animal's cow_presynch_program attempting to be referenced here is not a cow.")
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
            self.om.add_error(
                "Cow presynch program setter error",
                "The animal attempting to be assigned a cow_presynch_program must be a cow.",
                info_map={"class": self.__class__.__name__, "function": "cow_presynch_program.setter"},
            )
            raise TypeError("The animal attempting to be assigned a cow_presynch_program is not a cow.")
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
            self.om.add_error(
                "Cow ovsynch program property error",
                "The animal whose cow_ovsynch_program is attempting to be referenced must be a cow.",
                info_map={"class": self.__class__.__name__, "function": "cow_ovsynch_program.property"},
            )
            raise TypeError("The animal's cow_ovsynch_program attempting to be referenced here is not a cow.")
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
            self.om.add_error(
                "Cow ovsynch program setter error",
                "The animal attempting to be assigned a cow_ovsynch_program must be a cow.",
                info_map={"class": self.__class__.__name__, "function": "cow_ovsynch_program.setter"},
            )
            raise TypeError("The animal attempting to be assigned a cow_ovsynch_program is not a cow.")
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
            self.om.add_error(
                "Cow resynch program property error",
                "The animal whose cow_resynch_program is attempting to be referenced must be a cow.",
                info_map={"class": self.__class__.__name__, "function": "cow_resynch_program.property"},
            )
            raise TypeError("The animal's cow_resynch_program attempting to be referenced here is not a cow.")
        return self.reproduction.cow_resynch_program

    @cow_resynch_program.setter
    def cow_resynch_program(self, cow_resynch_program: CowReSynchSubProtocol) -> None:
        """
        Sets the cow ReSynch program for the object.

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
            self.om.add_error(
                "Cow resynch program setter error",
                "The animal attempting to be assigned a cow_resynch_program must be a cow.",
                info_map={"class": self.__class__.__name__, "function": "cow_resynch_program.setter"},
            )
            raise TypeError("The animal attempting to be assigned a cow_resynch_program is not a cow.")
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
            self.om.add_error(
                "Cow milk statistics property error",
                "The animal whose milk_statistics property is attempting to be referenced must be a cow.",
                info_map={"class": self.__class__.__name__, "function": "milk_statistics.property"},
            )
            raise TypeError("The animal whose milk_statistics property is attempting to be referenced must be a cow.")
        if AnimalConfig.simulate_genetics and self.genetics is not None:
            return MilkProductionStatistics(
                cow_id=self.id,
                pen_id=self.pen_history[-1]["pen"],
                days_in_milk=self.days_in_milk,
                estimated_daily_milk_produced=self.milk_production.daily_milk_produced,
                milk_protein=self.milk_production.true_protein_content,
                milk_fat=self.milk_production.fat_content,
                milk_lactose=self.milk_production.lactose_content,
                parity=self.calves,
                days_born=self.days_born,
                days_in_pregnancy=self.days_in_pregnancy,
                animal_type=self.animal_type,
                TBV_fat=self.genetics.TBV_fat,
                TBV_protein=self.genetics.TBV_protein,
                E_permanent_fat=self.genetics.E_permanent_fat,
                E_permanent_protein=self.genetics.E_permanent_protein,
                E_temporary_fat=self.genetics.E_temporary_fat,
                E_temporary_protein=self.genetics.E_temporary_protein,
                phenotype_fat=self.genetics.phenotype_fat,
                phenotype_protein=self.genetics.phenotype_protein,
                EBV_fat=self.genetics.EBV_fat,
                EBV_protein=self.genetics.EBV_protein,
                ranking_index=self.genetics.ranking_index,
            )
        else:
            return MilkProductionStatistics(
                cow_id=self.id,
                pen_id=self.pen_history[-1]["pen"],
                days_in_milk=self.days_in_milk,
                estimated_daily_milk_produced=self.milk_production.daily_milk_produced,
                milk_protein=self.milk_production.true_protein_content,
                milk_fat=self.milk_production.fat_content,
                milk_lactose=self.milk_production.lactose_content,
                parity=self.calves,
                days_born=self.days_born,
                days_in_pregnancy=self.days_in_pregnancy,
                animal_type=self.animal_type,
            )

    def _assign_sex_to_newborn_calf(self) -> None:
        """
        Assign a sex to a newborn calf based on the semen type and male calf rate.

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
            self.om.add_error(
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

    def _initialize_feedlot_animal(self, args: Any) -> None:
        """
        Initialize a feedlot steer or heifer from a configuration dict.

        Parameters
        ----------
        args : Any
            Dict with keys: body_weight, mature_body_weight, days_on_feed (all optional).

        """
        self.sex = Sex.STEER if self.animal_type == AnimalType.FEEDLOT_STEER else Sex.FEMALE
        self.body_weight = float(args.get("body_weight", AnimalConfig.feedlot_entry_weight))
        self.mature_body_weight = float(args.get("mature_body_weight", 600.0))
        self.wean_weight = 0.0
        self.entry_weight = self.body_weight
        self.days_on_feed = int(args.get("days_on_feed", 0))
        self.receiving_stress = self.days_on_feed <= AnimalModuleConstants.RECEIVING_PERIOD_DAYS
        self._update_step_up_phase()

    def _initialize_beef_cow_calf_animal(self, args: Any) -> None:
        """
        Initialize a beef cow-calf animal from a configuration dict.

        Parameters
        ----------
        args : Any
            Dict with keys from either BeefCowCalfValuesTypedDict (persistence path)
            or NewBornCalfValuesTypedDict (calving path). Body weight is derived from
            ``body_weight`` if present, else from ``birth_weight`` (calving path).

        """
        self.body_weight = float(args.get("body_weight", args.get("birth_weight", 0.0)))
        self.mature_body_weight = float(args.get("mature_body_weight", AnimalConfig.beef_mature_cow_weight_kg))
        self.wean_weight = 0.0
        self.sex = Sex[args["sex"]] if "sex" in args else (Sex.MALE if random() < 0.5 else Sex.FEMALE)
        self.times_calved = int(args.get("times_calved", 0))
        self.is_open = bool(args.get("is_open", True))
        self.days_since_calving = int(args.get("days_since_calving", 0))
        self._days_in_pregnancy = int(args.get("days_in_pregnancy", 0))
        self.days_in_breeding_season = None
        self.calf_at_side = None
        self.dam = None
        self.lactation_day = 0
        self.body_condition_score_9 = AnimalModuleConstants.BEEF_DEFAULT_BCS_9
        self._breeding_weight_event_fired = False
        if args.get("events"):
            self.events.init_from_string(args.get("events"))

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

        heifer_reproduction_sub_program: HeiferTAISubProtocol | HeiferSynchEDSubProtocol | None = None
        heifer_reproduction_program: HeiferReproductionProtocol | None = (
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
        if self.is_pregnant:
            self.reproduction.repro_state_manager.enter(ReproStateEnum.PREGNANT)
        else:
            self.reproduction.repro_state_manager.enter(ReproStateEnum.ENTER_HERD_FROM_INIT)
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
        self._initialize_heiferII_or_heiferIII(cast(HeiferIIValuesTypedDict, args))
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

        Notes
        -----
        This method compiles the daily nutrient inputs required for the animal
        based on its type, weight, growth, pregnancy stages, milk production,
        and other factors. It then triggers the process to update the animal's
        phosphorus requirements.

        """
        if self.animal_type.is_feedlot:
            if self.nutrition_requirements is not None:
                self.nutrients.phosphorus_requirement = self.nutrition_requirements.phosphorus
            return

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

        Notes
        -----
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

        Notes
        -----
        If the animal type is not a cow, the method exits without performing any operation.
        For cows, the method calculates the milking updates using the animal's daily metrics
        and adjusts the milking-related data accordingly.

        Parameters
        ----------
        time : RufasTime
            The current time context for the daily milking update.

        """
        if self.animal_type.is_beef_cow_calf:
            self._beef_daily_suckling_update(time)
            return
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

        Notes
        -----
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

        Parameters
        ----------
        time : RufasTime
            The RufasTime instance used for updating growth and body weight changes.

        Notes
        -----
        This method gathers the necessary animal attributes and performs the daily body weight update. It then updates
        attributes such as body weight, conceptual weight, and events of the animal accordingly.

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
            self.om.add_error(
                "Cow days in milk error",
                f"Unexpected days in milk value: {self.days_in_milk}",
                info_map={"class": self.__class__.__name__, "function": self._determine_days_in_milk.__name__},
            )
            raise ValueError(f"Unexpected days in milk value: {self.days_in_milk}")

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
        NewBornCalfValuesTypedDict | None
            A dictionary containing details related to a newly born calf if a calf is born during this update;
            otherwise, None.
        HerdReproductionStatistics
            A collection of statistical properties related to the animal's reproduction lifecycle.

        """
        if self.animal_type.is_beef_cow_calf:
            return self._beef_daily_reproduction_update(time)
        if not (self.animal_type == AnimalType.HEIFER_II or self.animal_type.is_cow):
            return None, HerdReproductionStatistics()

        newborn_calf_config: NewBornCalfValuesTypedDict | None = None

        if AnimalConfig.simulate_genetics and self.genetics is not None:
            reproduction_inputs = ReproductionInputs(
                animal_type=self.animal_type,
                body_weight=self.body_weight,
                breed=self.breed,
                days_born=self.days_born,
                days_in_pregnancy=self.days_in_pregnancy,
                days_in_milk=self.days_in_milk,
                dam_tbv_fat=self.genetics.TBV_fat,
                dam_tbv_protein=self.genetics.TBV_protein,
                phosphorus_for_gestation_required_for_calf=self.nutrients.phosphorus_for_gestation_required_for_calf,
            )
        else:
            reproduction_inputs = ReproductionInputs(
                animal_type=self.animal_type,
                body_weight=self.body_weight,
                breed=self.breed,
                days_born=self.days_born,
                days_in_pregnancy=self.days_in_pregnancy,
                days_in_milk=self.days_in_milk,
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
        if self.animal_type.is_feedlot:
            return self._feedlot_daily_routines(time)

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

        if (self.animal_type.is_cow or self.animal_type == AnimalType.BEEF_COW) and newborn_calf_config is not None:
            daily_routines_output.newborn_calf_config = newborn_calf_config

        if self.animal_type == AnimalType.HEIFER_III and self.is_pregnant:
            self.days_in_pregnancy += 1

        return daily_routines_output

    def _feedlot_daily_routines(self, time: RufasTime) -> DailyRoutinesOutput:
        """
        Streamlined daily routine for feedlot finishing animals.

        Parameters
        ----------
        time : RufasTime
            Current simulation time.

        Returns
        -------
        DailyRoutinesOutput
            Daily output with animal status and empty reproduction statistics.

        """
        self.days_born += 1
        self.days_on_feed += 1

        if self.receiving_stress and self.days_on_feed > AnimalModuleConstants.RECEIVING_PERIOD_DAYS:
            self.receiving_stress = False
            self.events.add_event(self.days_born, time.simulation_day, animal_constants.RECEIVING_STRESS_END)

        self._update_step_up_phase(simulation_day=time.simulation_day)

        # Direct body weight update — Growth.evaluate_body_weight_change does not support feedlot
        effective_adg: float = AnimalConfig.feedlot_target_adg * AnimalConfig.feedlot_implant_adg_factor
        self.body_weight += effective_adg
        self.growth.daily_growth = effective_adg

        if self.nutrition_supply is not None and self.nutrition_supply.dry_matter > 0:
            self.cumulative_dmi += self.nutrition_supply.dry_matter

        animal_status, _ = self.animal_life_stage_update(time)

        return DailyRoutinesOutput(
            animal_status=animal_status,
            newborn_calf_config=None,
            herd_reproduction_statistics=HerdReproductionStatistics(),
        )

    def _calf_life_stage_update(self, _: RufasTime) -> tuple[AnimalStatus, None]:
        """
        Determines and updates the life stage of a calf based on specific evaluation criteria.

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

        Notes
        -----
        Transitions the calf to the 'HeiferI' stage if the criteria are met, otherwise retains the current life stage.

        """
        if self._evaluate_calf_for_heiferI():
            self._transition_calf_to_heiferI()
            return AnimalStatus.LIFE_STAGE_CHANGED, None
        return AnimalStatus.REMAIN, None

    def _heiferI_life_stage_update(self, time: RufasTime) -> tuple[AnimalStatus, None]:
        """
        Updates the life stage of a heiferI animal based on specific evaluation criteria.

        Parameters
        ----------
        time : RufasTime
            The RufasTime instance used for evaluation and transition.

        Returns
        -------
        tuple[AnimalStatus, None]
            AnimalStatus.LIFE_STAGE_CHANGED, None: If the heiferI transitions to the heifer II life stage.
            AnimalStatus.REMAIN, None: If the heiferI remains in the current life stage.

        Notes
        -----
        If the evaluation determines that the heiferI should transition to heiferII,
        the necessary transition is performed. Otherwise, the animal remains in its current life stage.

        """
        if self._evaluate_heiferI_for_heiferII():
            self._transition_heiferI_to_heiferII(time)
            return AnimalStatus.LIFE_STAGE_CHANGED, None
        return AnimalStatus.REMAIN, None

    def _heiferII_life_stage_update(self, time: RufasTime) -> tuple[AnimalStatus, None]:
        """
        Updates the life stage of a heiferII based on evaluation criteria such as culling or transitioning to heiferIII.

        Parameters
        ----------
        time : RufasTime
            The RufasTime object, used to determine the current simulation day.

        Returns
        -------
        tuple[AnimalStatus, None]
            A tuple containing the status of the animal (whether it is sold, its life stage
            has changed, or it remains in the current state) and None.

        Notes
        -----
        If the evaluation determines that the heiferII should transition to heiferIII,
        the necessary transition is performed. Otherwise, the animal remains in its current life stage.

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
            AnimalType.FEEDLOT_STEER: self._feedlot_life_stage_update,
            AnimalType.FEEDLOT_HEIFER: self._feedlot_life_stage_update,
            AnimalType.BEEF_CALF: self._beef_calf_life_stage_update,
            AnimalType.BEEF_HEIFER_REPLACEMENT: self._beef_replacement_heifer_life_stage_update,
            AnimalType.BEEF_COW: self._beef_cow_life_stage_update,
            AnimalType.BEEF_BULL: self._beef_bull_life_stage_update,
        }
        animal_status, newborn_calf_config = ANIMAL_TYPE_TO_LIFE_STAGE_UPDATE_METHOD_MAP[self.animal_type](time)

        if self.days_born == self.future_cull_date:
            self.sold_at_day = time.simulation_day
            animal_status = AnimalStatus.SOLD
        if self.days_born == self.future_death_date:
            self.dead_at_day = time.simulation_day
            self.cull_reason = animal_constants.DEATH_CULL
            animal_status = AnimalStatus.DEAD

        return animal_status, newborn_calf_config

    def _feedlot_life_stage_update(self, time: RufasTime) -> tuple[AnimalStatus, NewBornCalfValuesTypedDict | None]:
        """
        Check feedlot exit conditions — slaughter weight reached or max days on feed.

        Parameters
        ----------
        time : RufasTime
            Current simulation time.

        Returns
        -------
        tuple[AnimalStatus, NewBornCalfValuesTypedDict | None]
            (SOLD, None) if an exit condition is met, (REMAIN, None) otherwise.

        """
        # TODO(beef-integration): report_feedlot_performance should be called
        # here when AnimalStatus.SOLD is returned, but AnimalModuleReporter
        # cannot be imported at this layer (animal.py is below the reporter
        # in the dependency hierarchy). This call belongs in a future
        # _feedlot_update method in herd_factory.py, once feedlot animals are
        # wired into herd_manager._process_daily_herd_updates — a known gap
        # documented in the PR #32 implementation report (HerdFactory wiring,
        # known limitation #1). Tracked for the next beef integration PR.
        if self.body_weight >= AnimalConfig.feedlot_slaughter_weight:
            self.cull_reason = animal_constants.SLAUGHTER_WEIGHT_REACHED
            self.sold_at_day = time.simulation_day
            return AnimalStatus.SOLD, None

        if self.days_on_feed >= AnimalConfig.feedlot_max_days_on_feed:
            self.cull_reason = animal_constants.MAX_DAYS_ON_FEED_REACHED
            self.sold_at_day = time.simulation_day
            return AnimalStatus.SOLD, None

        return AnimalStatus.REMAIN, None

    def _beef_daily_suckling_update(self, time: RufasTime) -> None:
        """
        Track beef cow suckling: increment lactation_day when a calf is at side.

        Parameters
        ----------
        time : RufasTime
            Current simulation time (unused directly; present for interface consistency).

        """
        if self.calf_at_side is not None:
            self.lactation_day += 1

    def _beef_handle_conception_attempt(self, time: RufasTime) -> None:
        """
        Draw a daily conception attempt for an open beef cow in the breeding season.

        Parameters
        ----------
        time : RufasTime
            Current simulation time; provides day_of_year for season window check.

        Notes
        -----
        Sets ``is_open = False`` and ``_days_in_pregnancy = 1`` on successful conception.
        No state change occurs when the probability draw fails.

        """
        season_start = AnimalConfig.beef_breeding_season_start_day
        season_end = season_start + AnimalConfig.beef_breeding_season_length
        day = time.day_of_year
        if season_end <= 365:
            in_season = season_start <= day < season_end
        else:
            in_season = day >= season_start or day < (season_end % 365)
        if not in_season:
            return
        if self.days_since_calving < AnimalModuleConstants.BEEF_POSTPARTUM_ANESTRUS_DAYS:
            return
        prob = calculate_seasonal_conception_probability(
            body_condition_score=self.body_condition_score_9,
            bull_to_cow_ratio=AnimalConfig.beef_natural_service_bull_ratio,
            days_since_calving=self.days_since_calving,
        )
        if random() < prob:
            self.is_open = False
            self._days_in_pregnancy = 1

    def _beef_handle_calving(self, time: RufasTime) -> NewBornCalfValuesTypedDict | None:
        """
        Handle a beef calving event: build calf dict, apply stillbirth, reset state.

        Parameters
        ----------
        time : RufasTime
            Current simulation time; provides current_date for calf birth_date.

        Returns
        -------
        NewBornCalfValuesTypedDict | None
            Calf configuration dict, or None if stillbirth occurs.

        """
        self._days_in_pregnancy = 0
        self.days_since_calving = 0
        self.lactation_day = 0
        self.is_open = True
        self.times_calved += 1

        newborn: NewBornCalfValuesTypedDict = {
            "id": 0,
            "animal_type": AnimalType.BEEF_CALF.value,
            "breed": self.breed.name,
            "days_born": 0,
            "birth_weight": float(
                AnimalModuleConstants.BREED_CBW_KG.get(
                    self.breed.value,
                    AnimalModuleConstants.BEEF_CALF_BIRTH_WEIGHT_KG,
                )
            ),
            "birth_date": str(time.current_date),
            "initial_phosphorus": 0.0,
        }

        self.events.add_event(self.days_born, time.simulation_day, animal_constants.BEEF_CALVING)

        if random() < AnimalModuleConstants.BEEF_STILLBIRTH_RATE:
            return None

        return newborn

    def _beef_daily_reproduction_update(
        self, time: RufasTime
    ) -> tuple[NewBornCalfValuesTypedDict | None, HerdReproductionStatistics]:
        """
        Daily reproduction update for beef cow-calf animals.

        Parameters
        ----------
        time : RufasTime
            Current simulation time.

        Returns
        -------
        tuple[NewBornCalfValuesTypedDict | None, HerdReproductionStatistics]
            Calf configuration dict if calving occurs this day, else None; plus empty stats.

        Notes
        -----
        AI protocols (AI_SEASONAL, AI_CONTROLLED_BREEDING) are declared in
        BeefReproductionProtocol but raise NotImplementedError in PR-B; only
        NATURAL_SERVICE_SEASONAL is implemented here.

        """
        if self.animal_type == AnimalType.BEEF_BULL:
            return None, HerdReproductionStatistics()

        if AnimalConfig.beef_reproduction_program == BeefReproductionProtocol.AI_SEASONAL:
            raise NotImplementedError(
                "BeefReproductionProtocol.AI_SEASONAL not implemented (PR-B scope: NATURAL_SERVICE_SEASONAL only)"
            )
        if AnimalConfig.beef_reproduction_program == BeefReproductionProtocol.AI_CONTROLLED_BREEDING:
            raise NotImplementedError("BeefReproductionProtocol.AI_CONTROLLED_BREEDING not implemented (PR-B scope)")

        self.days_since_calving += 1

        if self.animal_type == AnimalType.BEEF_CALF:
            return None, HerdReproductionStatistics()

        if self.animal_type == AnimalType.BEEF_HEIFER_REPLACEMENT:
            breeding_threshold = (
                AnimalModuleConstants.BEEF_HEIFER_TARGET_BREEDING_PCT_MATURE * AnimalConfig.beef_mature_cow_weight_kg
            )
            if self.body_weight < breeding_threshold:
                return None, HerdReproductionStatistics()

        was_pregnant_at_start = self._days_in_pregnancy > 0
        if self.is_open:
            self._beef_handle_conception_attempt(time)
        if was_pregnant_at_start and self._days_in_pregnancy > 0:
            self._days_in_pregnancy += 1

        if self._days_in_pregnancy >= AnimalModuleConstants.BEEF_GESTATION_LENGTH_DAYS:
            newborn_config = self._beef_handle_calving(time)
            return newborn_config, HerdReproductionStatistics()

        return None, HerdReproductionStatistics()

    def _beef_calf_life_stage_update(self, time: RufasTime) -> tuple[AnimalStatus, NewBornCalfValuesTypedDict | None]:
        """
        Life-stage update for BEEF_CALF: check weaning threshold.

        Parameters
        ----------
        time : RufasTime
            Current simulation time.

        Returns
        -------
        tuple[AnimalStatus, NewBornCalfValuesTypedDict | None]
            REMAIN if below weaning age; otherwise result of _beef_weaning_event.

        """
        at_weaning_age = self.days_born >= AnimalConfig.beef_weaning_age_days
        at_weaning_weight = (
            AnimalConfig.beef_weaning_weight_kg is not None and self.body_weight >= AnimalConfig.beef_weaning_weight_kg
        )
        if at_weaning_age or at_weaning_weight:
            return self._beef_weaning_event(time)
        return AnimalStatus.REMAIN, None

    def _beef_weaning_event(self, time: RufasTime) -> tuple[AnimalStatus, NewBornCalfValuesTypedDict | None]:
        """
        Handle calf weaning: clear dam reference and dispatch to post-weaning destination.

        Parameters
        ----------
        time : RufasTime
            Current simulation time.

        Returns
        -------
        tuple[AnimalStatus, NewBornCalfValuesTypedDict | None]
            (SOLD, None) or (LIFE_STAGE_CHANGED, None).

        """
        self.events.add_event(self.days_born, time.simulation_day, animal_constants.CALF_WEANED)

        if self.dam is not None:
            self.dam.calf_at_side = None

        self.wean_weight = self.body_weight
        destination = AnimalConfig.beef_post_weaning_destination
        if destination is BeefPostWeaningDestination.SELL:
            self.sold_at_day = time.simulation_day
            return AnimalStatus.SOLD, None
        if destination is BeefPostWeaningDestination.REPLACEMENT_HEIFER:
            if self.sex != Sex.FEMALE:
                # Male calves under REPLACEMENT_HEIFER destination sell at weaning
                self.sold_at_day = time.simulation_day
                return AnimalStatus.SOLD, None
            self.animal_type = AnimalType.BEEF_HEIFER_REPLACEMENT
            return AnimalStatus.LIFE_STAGE_CHANGED, None
        if destination is BeefPostWeaningDestination.DIRECT_TO_FEEDLOT:
            self.animal_type = AnimalType.FEEDLOT_STEER if self.sex == Sex.MALE else AnimalType.FEEDLOT_HEIFER
            self.birth_weight = 0.0
            self._initialize_feedlot_animal(
                {"body_weight": self.body_weight, "mature_body_weight": AnimalConfig.beef_mature_cow_weight_kg}
            )
            return AnimalStatus.LIFE_STAGE_CHANGED, None
        raise ValueError(f"Unknown beef_post_weaning_destination: {destination!r}")

    def _beef_replacement_heifer_life_stage_update(
        self, time: RufasTime
    ) -> tuple[AnimalStatus, NewBornCalfValuesTypedDict | None]:
        """
        Life-stage update for BEEF_HEIFER_REPLACEMENT.

        Parameters
        ----------
        time : RufasTime
            Current simulation time.

        Returns
        -------
        tuple[AnimalStatus, NewBornCalfValuesTypedDict | None]
            LIFE_STAGE_CHANGED if promoted to BEEF_COW, else REMAIN.

        Notes
        -----
        Type promotion is deferred here (not in _beef_daily_reproduction_update) to
        avoid a same-tick race condition where _beef_cow_life_stage_update's open-cull
        check would fire on the calving day before the cow has had any chance to rebreed.

        """
        if self.times_calved >= 1:
            self.animal_type = AnimalType.BEEF_COW
            self.events.add_event(
                self.days_born, time.simulation_day, animal_constants.REPLACEMENT_HEIFER_PROMOTED_TO_COW
            )
            return AnimalStatus.LIFE_STAGE_CHANGED, None

        if not self._breeding_weight_event_fired:
            threshold = (
                AnimalModuleConstants.BEEF_HEIFER_TARGET_BREEDING_PCT_MATURE * AnimalConfig.beef_mature_cow_weight_kg
            )
            if self.body_weight >= threshold:
                self.events.add_event(
                    self.days_born,
                    time.simulation_day,
                    animal_constants.REPLACEMENT_HEIFER_REACHED_BREEDING_WEIGHT,
                )
                self._breeding_weight_event_fired = True

        return AnimalStatus.REMAIN, None

    def _beef_cow_life_stage_update(self, time: RufasTime) -> tuple[AnimalStatus, NewBornCalfValuesTypedDict | None]:
        """
        Life-stage update for BEEF_COW: age-ceiling cull and open-cow pregnancy-check mark.

        Parameters
        ----------
        time : RufasTime
            Current simulation time.

        Returns
        -------
        tuple[AnimalStatus, NewBornCalfValuesTypedDict | None]
            SOLD if age ceiling reached; REMAIN otherwise (open-cull mark sets cull_reason only).

        Notes
        -----
        Actual removal of open cows from the herd is deferred to Step 7 (PR-C); this method
        only sets cull_reason so the higher layer (herd_factory) can act.
<<<<<<< HEAD
=======
        # TODO(beef-integration): report_cow_calf_performance belongs in herd_factory.py (Step 7).
>>>>>>> a9e4401d4 (feat(animal): cow-calf PR-B — lifecycle init, seasonal reproduction (Steps 4-5))

        """
        if self.days_born >= AnimalModuleConstants.BEEF_COW_MAX_AGE_DAYS:
            self.events.add_event(self.days_born, time.simulation_day, animal_constants.COW_CULLED_AGE)
            self.cull_reason = animal_constants.COW_CULLED_AGE
            self.sold_at_day = time.simulation_day
            return AnimalStatus.SOLD, None

        season_start = AnimalConfig.beef_breeding_season_start_day
        season_end = season_start + AnimalConfig.beef_breeding_season_length
        day = time.day_of_year
        if season_end <= 365:
            season_closed = day >= season_end
            season_close_day = time.simulation_day - day + season_end
        else:
            season_closed = (season_end % 365) <= day < season_start
            season_close_day = time.simulation_day - day + (season_end % 365)
        postpartum_eligible_day = (
            time.simulation_day - self.days_since_calving + AnimalModuleConstants.BEEF_POSTPARTUM_ANESTRUS_DAYS
        )
        has_had_rebreeding_opportunity = (
            self.days_since_calving >= AnimalModuleConstants.BEEF_POSTPARTUM_ANESTRUS_DAYS
            and postpartum_eligible_day < season_close_day
        )
        if (
            self.is_open
            and has_had_rebreeding_opportunity
            and season_closed
            and self.cull_reason != animal_constants.COW_OPEN_AT_PREGNANCY_CHECK
        ):
            self.events.add_event(self.days_born, time.simulation_day, animal_constants.COW_OPEN_AT_PREGNANCY_CHECK)
            self.cull_reason = animal_constants.COW_OPEN_AT_PREGNANCY_CHECK

        return AnimalStatus.REMAIN, None

    def _beef_bull_life_stage_update(self, time: RufasTime) -> tuple[AnimalStatus, NewBornCalfValuesTypedDict | None]:
        """
        Life-stage update for BEEF_BULL: no exit conditions in PR-B scope.

        Parameters
        ----------
        time : RufasTime
            Current simulation time (unused; present for interface consistency).

        Returns
        -------
        tuple[AnimalStatus, NewBornCalfValuesTypedDict | None]
            Always (REMAIN, None).

        """
        return AnimalStatus.REMAIN, None

    def _update_step_up_phase(self, simulation_day: int = 0) -> None:
        """
        Track and log feedlot step-up diet phase based on days on feed.

        Parameters
        ----------
        simulation_day : int, optional
            Current simulation day for event logging (default 0 during init).

        """
        dof = self.days_on_feed
        if dof <= AnimalModuleConstants.STEP_UP_STARTER_END_DAY:
            new_phase, event_str = "starter", animal_constants.STEP_UP_STARTER
        elif dof <= AnimalModuleConstants.STEP_UP_TRANSITION_END_DAY:
            new_phase, event_str = "transition", animal_constants.STEP_UP_TRANSITION
        else:
            new_phase, event_str = "finisher", animal_constants.STEP_UP_FINISHER

        if new_phase != self.step_up_phase:
            self.step_up_phase = new_phase
            self.events.add_event(self.days_born, simulation_day, event_str)

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
            self.om.add_error(
                "HeiferIII transition error",
                f"HeiferIII {self.id} should give birth to a calf when transitioning to cow.",
                info_map={"class": self.__class__.__name__, "function": self.transition_heiferIII_to_cow.__name__},
            )
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
        | BeefCowCalfValuesTypedDict
    ):
        """
        Get the attribute values of the animal.

        Returns
        -------
        (CalfValuesTypedDict | HeiferIValuesTypedDict | HeiferIIValuesTypedDict | HeiferIIIValuesTypedDict |
         CowValuesTypedDict | BeefCowCalfValuesTypedDict)
            A dictionary containing key-value pairs specific to the current animal.

        Raises
        ------
        KeyError
            If the animal_type is not present in the mapping dictionary.

        """
        mapping: dict[
            AnimalType,
            Callable[
                [],
                (
                    CalfValuesTypedDict
                    | HeiferIValuesTypedDict
                    | HeiferIIValuesTypedDict
                    | HeiferIIIValuesTypedDict
                    | CowValuesTypedDict
                    | BeefCowCalfValuesTypedDict
                ),
            ],
        ] = {
            AnimalType.CALF: self._get_calf_values,
            AnimalType.HEIFER_I: self._get_heiferI_values,
            AnimalType.HEIFER_II: self._get_heiferII_values,
            AnimalType.HEIFER_III: self._get_heiferIII_values,
            AnimalType.DRY_COW: self._get_cow_values,
            AnimalType.LAC_COW: self._get_cow_values,
            AnimalType.BEEF_COW: self._get_beef_cow_calf_values,
            AnimalType.BEEF_CALF: self._get_beef_cow_calf_values,
            AnimalType.BEEF_HEIFER_REPLACEMENT: self._get_beef_cow_calf_values,
            AnimalType.BEEF_BULL: self._get_beef_cow_calf_values,
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

    def _get_beef_cow_calf_values(self) -> BeefCowCalfValuesTypedDict:
        """
        Get the attribute values for a beef cow-calf animal.

        Returns
        -------
        BeefCowCalfValuesTypedDict
            A dictionary containing key-value pairs specific to the current beef animal.

        """
        return BeefCowCalfValuesTypedDict(
            id=self.id,
            breed=self.breed.name,
            animal_type=self.animal_type.value,
            days_born=self.days_born,
            birth_weight=self.birth_weight,
            body_weight=self.body_weight,
            mature_body_weight=self.mature_body_weight,
            sex=self.sex.name,
            times_calved=self.times_calved,
            is_open=self.is_open,
            days_since_calving=self.days_since_calving,
            days_in_pregnancy=self.days_in_pregnancy,
            events=str(self.events),
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
        Updates the animal's pen history by either appending to the existing history if the animal is in a different
        pen than it was the last time this method is called or modifying the last element in the pen_history list to
        reflect the current simulation day.

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
        Calculates and sets the animal's daily vertical and horizontal walking distance (DVD and DHD).

        Parameters
        ----------
        vertical_dist_to_parlor : float
            Vertical distance to milking parlor (km).
        horizontal_dist_to_parlor : float
            Horizontal distance to milking parlor (km).

        """
        if not self.animal_type.is_cow:
            self.om.add_error(
                "Daily walking distance set method error",
                "Cannot calculate daily walking distance for animal types other than cow.",
                info_map={"class": self.__class__.__name__, "function": self.set_daily_walking_distance.__name__},
            )
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
        if self.animal_type.is_feedlot:
            if self.previous_nutrition_supply is None or self.previous_nutrition_supply.dry_matter <= 0:
                ne_conc: float = AnimalModuleConstants.DEFAULT_NET_ENERGY_DIET_CONCENTRATION
            else:
                ne_conc = (
                    self.previous_nutrition_supply.metabolizable_energy / self.previous_nutrition_supply.dry_matter
                )

            return BeefNRCRequirementsCalculator.calculate_requirements(
                body_weight=self.body_weight,
                mature_body_weight=self.mature_body_weight,
                animal_type=self.animal_type,
                breed=self.breed.value,
                sex=self.sex,
                days_on_feed=self.days_on_feed,
                target_adg=AnimalConfig.feedlot_target_adg,
                implant_adg_factor=AnimalConfig.feedlot_implant_adg_factor,
                housing=housing,
                mud_condition=AnimalConfig.feedlot_mud_condition,
                temperature_c=previous_temperature,
                ne_diet_concentration=ne_conc,
                process_based_phosphorus_requirement=0.0,
            )

        if self.animal_type is AnimalType.CALF:
            calf_intake = CalfRationManager.calculate_intake(
                self.birth_weight,
                self.body_weight,
                AnimalConfig.wean_day,
                AnimalConfig.wean_length,
                cast(list[NASEMFeed | NRCFeed], available_feeds),
                self.nutrient_standard,
            )
            calf_requirements = CalfRationManager.calculate_requirements(
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

    def update_305_day_milk_yield(self) -> None:
        """
        Update the cow's 305-day milk yield estimate.

        Notes
        -----
        Dry cows (DIM == 0) retain their previous estimate so a value carried over from
        the prior lactation isn't wiped out. The exception is a dry cow that has never
        had an in-sim lactation yet (estimate still at the 0.0 init default) — those fall
        through to ``calculate_305_day_milk_yield``, which returns the pure Wood's-curve
        integral when no current-lactation history exists. This avoids zero-valued dry
        cows pulling the herd mean down at sim start.

        For all other cows the estimate is recomputed from observed daily production
        combined with Wood's curve predictions for any unobserved DIMs in 1..305.
        """
        if self.days_in_milk == 0 and self.milk_production.milk_305_day_yield > 0.0:
            return

        self.milk_production.milk_305_day_yield = self.milk_production.calculate_305_day_milk_yield()

    def update_genetic_history(self, simulation_day: int) -> None:
        """
        Updates the genetic history record for the animal on the given simulation day.

        Parameters
        ----------
        simulation_day : int
            The current simulation day used to timestamp the genetic history entry.

        Notes
        -----
        If the animal's current genetics differ from the most recent genetic history entry, a new ``GeneticHistory``
        record is appended. Otherwise, the end day of the most recent entry is extended to the current simulation day.
        A warning is issued if a duplicate entry is detected for the same day.

        """
        if AnimalConfig.simulate_genetics and self.genetics is not None:
            if (
                len(self.genetic_history) == 0
                or self.genetic_history[-1]["genetics"] != self.genetics.dict_representation
            ):
                self.genetic_history.append(
                    GeneticHistory(
                        start_day=simulation_day,
                        end_day=simulation_day,
                        id=self.id,
                        animal_type=self.animal_type,
                        genetics=self.genetics.dict_representation,
                    )
                )
            else:
                if simulation_day == self.genetic_history[-1]["end_day"]:
                    self.om.add_warning(
                        "Duplicate Genetic History Entry",
                        f"Animal {self.id} already has a genetic history entry on day {simulation_day}.",
                        {
                            "class": Animal.__name__,
                            "function": Animal.update_genetic_history.__name__,
                        },
                    )
                self.genetic_history[-1]["end_day"] = simulation_day
        else:
            return
