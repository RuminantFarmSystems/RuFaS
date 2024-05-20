import copy
from typing import List
from .enums import CropCategory, CropType
from .harvested_crop import HarvestedCrop
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.general_constants import GeneralConstants
from RUFAS.time import Time
from RUFAS.output_manager import OutputManager
from RUFAS.weather import Weather


"""
These constants define the upper and lower bounds of temperatures that allow fermentation (in degrees C), the upper and
lower fractions of dry matter that allow fermentation, and the constants that regulate how dry matter is lost to
fermentation. These values are defined in the Feed Storage Scientific Documentation, section 1.3.
"""
ALFALFA_FERMENTATION_CONSTANTS: dict[str, float] = {
    "lower_temp_limit": 5.0,
    "upper_temp_limit": 45.0,
    "lower_dry_matter_limit": 0.20,
    "upper_dry_matter_limit": 0.60,
    "loss_coefficient": 0.0364,
    "base_loss_fraction": 0.0156,
}

NON_ALFALFA_FERMENTATION_CONSTANTS: dict[str, float] = {
    "lower_temp_limit": 0.0,
    "upper_temp_limit": 40.0,
    "lower_dry_matter_limit": 0.15,
    "upper_dry_matter_limit": 0.60,
    "loss_coefficient": 0.0193,
    "base_loss_fraction": 0.00864,
}
om = OutputManager()


class Storage:
    """
    Abstract class representing a general storage structure.

    Attributes
    ----------
    acceptable_crops : List[CropCategory]
        The list of crop categories that this storage can recieve.
    capacity : float
        The maximum capacity of the storage, currently set to infinity.
    stored : List[HarvestedCrop]
        A list of HarvestedCrop objects representing the crops stored.
    crude_protein_loss_coefficient : float, default 0.0
        Fractional coefficient used to adjust crude protein after dry matter loss.
    adf_loss_coefficient : float, default 0.0
        Fractional coefficient used to adjust ADF after dry matter loss.
    ndf_loss_coefficient : float, default 0.0
        Fractional coefficient used to adjust NDF after dry matter loss.
    sugar_loss_coefficient : float, default 0.0
        Fractional coefficient used to adjust sugar after dry matter loss.

    Methods
    -------
    stored_mass()
        The total mass (kg) of currently stored crops
    receive_crop(crop: HarvestedCrop, time: Time)
        Receives a harvested crop and adds it to the storage.
    process_degradations(current_conditions: CurrentDayConditions, time: Time)
        Processes the degradations and losses of the stored crops.
    give_feed(amount: float, crop_type: str)
        Gives out a specified amount of feed of a certain crop type.
    reset_mass_attributes_after_loss(self, crop: HarvestedCrop, dry_matter_loss: float)
        Resets mass related attributes after loss of dry matter.
    record_stored_crops(self, gaseous_dry_matter_loss: float)
        Records information about total mass and nutrient content of the stored crops.
    calculate_dry_matter_loss_to_gas(dry_matter: float, time_in_silo: int)
        Calculates the dry matter loss to gas.
    calculate_bale_density(initial_dry_matter: float)
        Calculates the density of a bale.
    recalculate_nutrient_percentage(
        initial_nutrient_percentage: float,
        loss_coefficient: float,
        dry_matter_loss: float,
        initial_dry_matter: float
    )
        Recalculates a single nutrient percentage after dry matter loss.

    """

    def __init__(self, capacity: float = float("inf")):
        self.acceptable_crops: List[CropCategory] = []
        self.capacity = capacity
        self.stored: List[HarvestedCrop] = []
        self.crude_protein_loss_coefficient = 0.0
        self.adf_loss_coefficient = 0.0
        self.ndf_loss_coefficient = 0.0
        self.sugar_loss_coefficient = 0.0

    @property
    def stored_mass(self) -> float:
        """The total mass (kg) of currently stored crops"""
        return sum(crop.fresh_mass for crop in self.stored)

    def receive_crop(self, crop: HarvestedCrop) -> None:
        """
        Receives a harvested crop and adds it to the storage.

        Parameters
        ----------
        crop : HarvestedCrop
            The harvested crop to be added to the storage.

        Returns
        -------
        None

        Raises
        ------
        NotImplementedError
            If the storage's acceptable crops is not populated.
        ValueError
            If the crop's category is not compatible with the storage.
        Exception
            If adding the crop exceeds the storage's capacity.

        """
        if not self.acceptable_crops:
            raise NotImplementedError(
                "Storage.acceptable_crops is not populated, consider populating it in the child class."
            )
        if crop.category not in self.acceptable_crops:
            raise ValueError(
                f"Can't recieve the crop, the compatible crop categories are {self.acceptable_crops=},\
                    {crop.category} is not one of them."
            )
        if self.stored_mass + crop.fresh_mass > self.capacity:
            raise Exception(
                f"Adding {crop.fresh_mass} to currently stored ({self.stored_mass})\
                    exceeds the storage capacity ({self.capacity})"
            )
        storage_crop = copy.deepcopy(crop)
        self.stored.append(storage_crop)

    def process_degradations(self, weather: Weather, time: Time) -> None:
        """
        Processes the degradations and losses of nutrients and dry matter in the stored crops.

        Parameters
        ----------
        weather : Weather
            Weather instance containing all weather information for the simulation.
        time : Time
            Time instance tracking the current time of the simulation.

        """
        total_gaseous_dry_matter_loss = 0.0
        for crop in self.stored:
            weather_conditions = self._get_conditions(crop.last_time_degraded, time, weather)
            gaseous_dry_matter_loss = self.calculate_dry_matter_loss_to_gas(crop, weather_conditions)
            total_gaseous_dry_matter_loss += gaseous_dry_matter_loss
            crop.crude_protein_percent = self.recalculate_nutrient_percentage(
                crop.crude_protein_percent,
                self.crude_protein_loss_coefficient,
                gaseous_dry_matter_loss,
                crop.dry_matter_mass,
            )
            crop.adf = self.recalculate_nutrient_percentage(
                crop.adf, self.adf_loss_coefficient, gaseous_dry_matter_loss, crop.dry_matter_mass
            )
            crop.ndf = self.recalculate_nutrient_percentage(
                crop.ndf, self.ndf_loss_coefficient, gaseous_dry_matter_loss, crop.dry_matter_mass
            )
            crop.sugar = self.recalculate_nutrient_percentage(
                crop.sugar, self.sugar_loss_coefficient, gaseous_dry_matter_loss, crop.dry_matter_mass
            )

            crop.last_time_degraded = copy.deepcopy(time)
            self.reset_mass_attributes_after_loss(crop, gaseous_dry_matter_loss)
        self.record_stored_crops(total_gaseous_dry_matter_loss)

    def give_feed(self, amount: float, crop_type: CropType) -> None:
        """
        Gives out a specified amount of feed of a certain crop type.

        Parameters
        ----------
        amount : float
            The amount of feed to give out.
        crop_type : CropType
            The type of crop to give out.

        """
        pass

    def reset_mass_attributes_after_loss(self, crop: HarvestedCrop, dry_matter_loss: float) -> None:
        """
        Resets the mass attributes of a crop after dry matter loss.

        Parameters
        ----------
        crop : HarvestedCrop
            The stored crop that has lost dry matter.
        dry_matter_loss : float
            Amount of dry matter the crop lost on the current day in kg.

        """
        pass

    def record_stored_crops(self, gaseous_dry_matter_loss: float) -> None:
        """
        Records the total mass and nutrient amounts held in storage.

        Parameters
        ----------
        gaseous_dry_matter_loss : float
            Total amount of gaseous dry matter lost from storage in kg.

        """
        pass

    def calculate_dry_matter_loss_to_gas(self, crop: HarvestedCrop, conditions: list[CurrentDayConditions]) -> float:
        """
        Calculates the dry matter loss to gas, specific to dry matter loss from fermentation.

        Parameters
        ----------
        crop : HarvestedCrop
            The stored crop that is losing dry matter.
        conditions : list[CurrentDayConditions]
            List of daily conditions over which dry matter loss will be calculated for.

        Returns
        -------
        float
            The amount of dry matter lost to gas, specific to fermentation in kg.

        References
        ----------
        .. [1] Feed Storage Scientific Documentation equations 1.3.1 and 1.3.2

        Notes
        -----
        If the ambient temperature or dry matter percentage of the crop do not fall within the acceptable ranges, then
        no dry matter loss occurs. Alfalfa uses different parameters and limits for calculating dry matter loss,
        but the structure of the loss equation remains the same.

        """
        dry_matter_fraction = crop.dry_matter_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION

        is_alfalfa = crop.category is CropCategory.ALFALFA
        constants = ALFALFA_FERMENTATION_CONSTANTS if is_alfalfa else NON_ALFALFA_FERMENTATION_CONSTANTS
        lower_temp_limit = constants["lower_temp_limit"]
        upper_temp_limit = constants["upper_temp_limit"]
        lower_dry_matter_limit = constants["lower_dry_matter_limit"]
        upper_dry_matter_limit = constants["upper_dry_matter_limit"]
        loss_coefficient = constants["loss_coefficient"]
        base_loss_fraction = constants["base_loss_fraction"]

        dry_matter_loss_fraction = 0.0

        for day in conditions:
            outside_temp_range = not lower_temp_limit <= day.mean_air_temperature <= upper_temp_limit
            outside_dry_fraction_range = not lower_dry_matter_limit <= dry_matter_fraction <= upper_dry_matter_limit
            if outside_temp_range or outside_dry_fraction_range:
                continue

            fraction_lost = base_loss_fraction - loss_coefficient * (dry_matter_fraction - lower_dry_matter_limit)
            dry_matter_loss_fraction += fraction_lost
            dry_matter_fraction -= fraction_lost

        return crop.dry_matter_mass * dry_matter_loss_fraction

    def _get_conditions(
        self, last_degradations_time: Time, current_time: Time, weather: Weather
    ) -> list[CurrentDayConditions]:
        """
        Gets the weather conditions for the days between the current time and the time that degradations were last
        processed.

        Parameters
        ----------
        last_degradations_time : Time
            Time instance recording the last day a crop's degradations were processed.
        time : Time
            Time instance containing the current time of the simulation.
        weather : Weather
            Weather instance containing all weather data for the simulation.

        Notes
        -----
        If the current day is the same as or before the last day that the crop was degraded, no weather conditions will
        be returned.

        """
        starting_day_offset = last_degradations_time.simulation_day - current_time.simulation_day

        if starting_day_offset >= 0:
            return []

        conditions = weather.get_conditions_series(current_time, starting_day_offset + 1, 0)

        return conditions

    def calculate_bale_density(self, initial_dry_matter: float) -> float:
        """
        Calculates the density of a bale.

        Parameters
        ----------
        initial_dry_matter_percentage : float
            The initial dry matter percentage of the bale.

        Returns
        -------
        float
            The density of the bale in kg dry matter per cubic meter.

        """
        moisture_fraction = 1 - (initial_dry_matter / 100)
        return 100 + 440 * moisture_fraction

    def recalculate_nutrient_percentage(
        self,
        initial_nutrient_percentage: float,
        loss_coefficient: float,
        dry_matter_loss: float,
        initial_dry_matter: float,
    ) -> float:
        """
        Calculates the updated relative nutrient percentage after dry matter has been lost from a stored crop.

        Parameters
        ----------
        initial_nutrient_percentage : float
            Nutrient percentage in stored crop before loss.
        loss_coefficient : float
            Fractional loss coefficient that regulates how quickly this nutrient is lost.
        dry_matter_loss : float
            Amount of dry matter lost from stored crop in kg.
        initial_dry_matter : float
            Amount of dry matter stored crop contained before loss in kg.

        Returns
        -------
        float
            The nutrient percentage after dry matter loss.

        Notes
        -----
        When stored crops lose dry matter, they do not always lose proportional amounts of the nutrients they are
        composed of. In this case, the concentration of the nutrient within the dry matter changes which is why it must
        be recalculated. If a negative nutrient percentage would be calculated after losing dry matter, the percentage
        is calculated to be 0 and a warning is logged to the OuputManager. If a negative nutrient percentage would have
        been calculated, a warning is logged to the Output Manager that the method is preventing this. If all dry matter
        is lost from the stored crop, the updated percentage of the nutrient in the dry matter is set as 0 to prevent a
        division by zero error.

        """
        dry_matter_loss_fraction = dry_matter_loss / initial_dry_matter
        initial_nutrient_fraction = initial_nutrient_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION

        if dry_matter_loss_fraction == 1.0:
            return 0.0

        fraction_of_nutrient_in_lost_dry_matter = loss_coefficient * dry_matter_loss_fraction
        if initial_nutrient_fraction < fraction_of_nutrient_in_lost_dry_matter:
            info_map = {"class": self.__class__.__name__, "function": self.recalculate_nutrient_percentage.__name__}
            warning_title = (
                f"Nutrient fraction {initial_nutrient_fraction} is less than nutrient fraction in dry matter loss "
                + f"{fraction_of_nutrient_in_lost_dry_matter}"
            )
            warning_message = "Calculating updated percentage of nutrient in stored crop dry matter to be 0"
            om.add_warning(warning_title, warning_message, info_map)
            return 0.0

        updated_nutrient_fraction = (initial_nutrient_fraction - fraction_of_nutrient_in_lost_dry_matter) / (
            1 - dry_matter_loss_fraction
        )
        updated_nutrient_percentage = updated_nutrient_fraction * GeneralConstants.FRACTION_TO_PERCENTAGE

        return updated_nutrient_percentage
