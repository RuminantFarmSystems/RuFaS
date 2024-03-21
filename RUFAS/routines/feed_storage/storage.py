import copy
from typing import List
from .enums import CropCategory, CropType
from .harvested_crop import HarvestedCrop


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

    Methods
    -------
    stored_mass()
        The total mass (kg) of currently stored crops
    receive_crop(crop: HarvestedCrop, time: Time)
        Receives a harvested crop and adds it to the storage.
    process_degradations()
        Processes the degradations and losses of the stored crops.
    give_feed(amount: float, crop_type: str)
        Gives out a specified amount of feed of a certain crop type.
    calculate_dry_matter_loss_to_gas(dry_matter: float, time_in_silo: int)
        Calculates the dry matter loss to gas.
    estimate_maximum_effluent(initial_dry_matter_percentage: float, initial_fresh_mass: float)
        Estimates the maximum amount of effluent for a stored crop.
    calculate_dry_matter_loss_to_effluent(dry_matter: float, estimated_maximum_effluent: float, time_in_silo: int)
        Calculates the dry matter loss to effluent.
    calculate_heat_generated(initial_dry_matter_percentage: float, bale_density: float)
        Calculates the total sensible heat generated.
    calculate_bale_density(initial_dry_matter: float)
        Calculates the density of a bale.
    recalculate_nutrient_fractions()
        Recalculates the relative nutrient concentrations after dry matter loss.
    recalculate_nutrient_concentration(
        initial_nutrient_concentration: float,
        loss_coefficient: float,
        dry_matter_loss: float,
        initial_dry_matter: float
    )
        Recalculates a single nutrient concentration after dry matter loss.

    """

    def __init__(self, capacity: float = float("inf")):
        self.acceptable_crops: List[CropCategory] = []
        self.capacity = capacity
        self.stored: List[HarvestedCrop] = []

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

    def process_degradations(self) -> None:
        """
        Processes the degradations and losses of the stored crops.
        """
        raise NotImplementedError("Cannot use Storage.process_degradations, use a child class.")

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

    def calculate_dry_matter_loss_to_gas(self, dry_matter: float, time_in_silo: int) -> float:
        """
        Calculates the dry matter loss to gas.

        Parameters
        ----------
        dry_matter : float
            The amount of dry matter.
        time_in_silo : int
            Time in days the crop has been in the silo.

        Returns
        -------
        float
            The amount of dry matter lost to gas.
        """
        raise NotImplementedError("Cannot use Storage.calculate_dry_matter_loss_to_gas, use a child class.")

    def estimate_maximum_effluent(self, initial_dry_matter_percentage: float, initial_fresh_mass: float) -> float:
        """
        Estimates the maximum effluence of a stored crop.

        Parameters
        ----------
        dry_matter_percentage : float
            Initial percentage of a stored crop's fresh mass that is dry matter.
        fresh_mass : float
            Initial fresh mass of a stored crop in kg.

        Returns
        -------
        float
            Estimated maximum effluent of the stored crop in kg water.

        """
        initial_dry_matter_fraction = initial_dry_matter_percentage / 100

        if initial_dry_matter_fraction >= 0.3:
            return 0.0

        return initial_fresh_mass * ((1 - initial_dry_matter_fraction) - 0.7)

    def calculate_dry_matter_loss_to_effluent(
        self, dry_matter: float, estimated_maximum_effluent: float, time_in_silo: int
    ) -> float:
        """
        Calculates the dry matter loss to effluent.

        Parameters
        ----------
        dry_matter : float
            The amount of dry matter in kg.
        estimated_maximum_effluent : float
            The estimated maximum effluent in kg.
        time_in_silo : int
            Time in days the crop has been in the silo.

        Returns
        -------
        float
            The amount of dry matter lost to effluent in kg.

        """
        return (0.1035 * estimated_maximum_effluent) * (0.1 * time_in_silo) * (1 / dry_matter)

    def calculate_heat_generated(self, initial_dry_matter_percentage: float, bale_density: float) -> float:
        """
        Calculates the total sensible heat generated.

        Parameters
        ----------
        initial_dry_matter_percentage : float
            Initial percentage of fresh mass that is not dry matter when a crop is baled.
        bale_density : float
            Density of the bale in kg dry matter per cubic meter.

        Returns
        -------
        float
            The total sensible heat generated in kJ/kg.

        """
        moisture_at_baling: float = 100 - initial_dry_matter_percentage
        heat_generated: float = 104 * (moisture_at_baling**2.18) * (bale_density**0.5) + 5.72 * (
            moisture_at_baling**1.23) * (bale_density**0.94)
        return heat_generated

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

    def recalculate_nutrient_fractions(self) -> None:
        """
        Recalculates the relative nutrient concentrations after dry matter loss.
        """
        raise NotImplementedError("Cannot use Storage.recalculate_nutrient_fractions, use a child class.")

    def recalculate_nutrient_concentration(
        self,
        initial_nutrient_concentration: float,
        loss_coefficient: float,
        dry_matter_loss: float,
        initial_dry_matter: float,
    ) -> float:
        """
        Recalculates the relative nutrient concentration after dry matter loss.

        Parameters
        ----------
        initial_nutrient_concentration : float
            Nutrient concentration in stored crop before loss.
        loss_coefficient : float
            Unitless coefficient that regulates how quickly this nutrient is lost.
        dry_matter_loss : float
            Amount of dry matter lost from stored crop in kg.
        initial_dry_matter : float
            Amount of dry matter stored crop contained before loss in kg.

        Returns
        -------
        float
            The nutrient concentration after loss.

        """
        dry_matter_loss_fraction = dry_matter_loss / initial_dry_matter
        bounded_loss_coefficient = min(initial_nutrient_concentration, loss_coefficient)
        return (
            (initial_nutrient_concentration - bounded_loss_coefficient)
            * dry_matter_loss_fraction
            / (1 - dry_matter_loss_fraction)
        )
