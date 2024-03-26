import copy
from typing import List
from .feed_storage_constants import FeedStorageConstants
from .enums import CropCategory, CropType
from .harvested_crop import HarvestedCrop
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.time import Time


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
        Fractional coefficient used to adjust crude protein loss.
    adf_loss_coefficient : float, default 0.0
        Fractional coefficient used to adjust ADF loss.
    ndf_loss_coefficient : float, default 0.0
        Fractional coefficient used to adjust NDF loss.

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
    set_mass_attributes_after_loss(self, crop: HarvestedCrop, dry_matter_loss: float)
        Sets mass related attributes after loss of dry matter.
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

    def process_degradations(self, current_conditions: CurrentDayConditions, time: Time) -> None:
        """
        Processes the degradations and losses of nutrients and dry matter in the stored crops.

        Parameters
        ----------
        current_conditions : float
            Conditions on the current day of the simulation.
        time : Time
            Time instance tracking the current time of the simulation.

        """
        total_gaseous_dry_matter_loss = 0.0
        for crop in self.stored:
            gaseous_dry_matter_loss = self.calculate_dry_matter_loss_to_gas(crop, current_conditions, time)
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

            self.set_mass_attributes_after_loss(crop, gaseous_dry_matter_loss)
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

    def set_mass_attributes_after_loss(self, crop: HarvestedCrop, dry_matter_loss: float) -> None:
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

    def calculate_dry_matter_loss_to_gas(
        self, crop: HarvestedCrop, current_conditions: CurrentDayConditions, time: Time
    ) -> float:
        """
        Calculates the dry matter loss to gas, specific to dry matter loss from fermentation.

        Parameters
        ----------
        crop : HarvestedCrop
            The stored crop that is losing dry matter.
        current_conditions : CurrentDayConditions
            Current conditions of the simulated day.
        time : Time
            Time instance containing the current time of the simulation.

        Returns
        -------
        float
            The amount of dry matter lost to gas, specific to fermentation.

        Notes
        -----
        If the ambient temperature or dry matter percentage of the crop do not fall within the acceptable ranges, then
        no dry matter loss occurs. Alfalfa uses different parameters and limits for calculating dry matter loss,
        but the structure of the loss equation remains the same.

        """
        dry_matter_fraction = crop.dry_matter_percentage / 100
        average_temperature = current_conditions.mean_air_temperature

        is_alfalfa = crop.category is CropCategory.ALFALFA
        lower_temp_limit = (
            FeedStorageConstants.ALFALFA_GASEOUS_LOSS_LOWER_TEMP_LIMIT
            if is_alfalfa
            else FeedStorageConstants.NON_ALFALFA_GASEOUS_LOSS_LOWER_TEMP_LIMIT
        )
        upper_temp_limit = (
            FeedStorageConstants.ALFALFA_GASEOUS_LOSS_UPPER_TEMP_LIMIT
            if is_alfalfa
            else FeedStorageConstants.NON_ALFALFA_GASEOUS_LOSS_UPPER_TEMP_LIMIT
        )
        lower_dry_matter_limit = (
            FeedStorageConstants.ALFALFA_GASEOUS_LOSS_LOWER_DRY_MATTER_LIMIT
            if is_alfalfa
            else FeedStorageConstants.NON_ALFALFA_GASEOUS_LOSS_LOWER_DRY_MATTER_LIMIT
        )
        upper_dry_matter_limit = (
            FeedStorageConstants.ALFALFA_GASEOUS_LOSS_UPPER_DRY_MATTER_LIMIT
            if is_alfalfa
            else FeedStorageConstants.NON_ALFALFA_GASEOUS_LOSS_UPPER_DRY_MATTER_LIMIT
        )

        if (not lower_temp_limit <= average_temperature <= upper_temp_limit) or (
            not lower_dry_matter_limit <= crop.dry_matter_percentage <= upper_dry_matter_limit
        ):
            return 0.0

        if is_alfalfa:
            dry_matter_loss_fraction = 0.0156 - 0.0364 * (dry_matter_fraction - 0.20)
        else:
            dry_matter_loss_fraction = 0.00864 - 0.0193 * (dry_matter_fraction - 0.15)

        return crop.dry_matter_mass * dry_matter_loss_fraction

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
        Recalculates the relative nutrient percentage after dry matter has been lost from a stored crop.

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
            The nutrient concentration after loss.

        Notes
        -----
        The loss coefficient is upper-bounded to prevent a negative nutrient percentage from being calculated.

        """
        dry_matter_loss_fraction = dry_matter_loss / initial_dry_matter
        bounded_loss_coefficient = min(initial_nutrient_percentage, loss_coefficient)
        return (
            (initial_nutrient_percentage - bounded_loss_coefficient)
            * dry_matter_loss_fraction
            / (1 - dry_matter_loss_fraction)
        )
