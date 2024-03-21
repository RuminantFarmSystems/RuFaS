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
    calculate_dry_matter_loss_to_effluent(dry_matter: float, estimated_maximum_effluent: float, time_in_silo: int)
        Calculates the dry matter loss to effluent.
    calculate_protein_degradation()
        Calculates protein degradation.
    calculate_heat_generated()
        Calculates the total sensible heat generated.
    calculate_bale_density(initial_dry_matter: float)
        Calculates the density of a bale.
    recalculate_nutrient_fractions()
        Recalculates the relative nutrient concentrations after dry matter loss.
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

    def process_degradations(self):
        """
        Processes the degradations and losses of the stored crops.

        Returns
        -------
        None
        """
        pass

    def give_feed(self, amount: float, crop_type: CropType):
        """
        Gives out a specified amount of feed of a certain crop type.

        Parameters
        ----------
        amount : float
            The amount of feed to give out.
        crop_type : CropType
            The type of crop to give out.

        Returns
        -------
        None
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
        pass

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
    ):
        """
        Calculates the dry matter loss to effluent.

        Parameters
        ----------
        dry_matter : float
            The amount of dry matter.
        estimated_maximum_effluent : float
            The estimated maximum effluent.
        time_in_silo : int
            Time in days the crop has been in the silo.

        Returns
        -------
        float
            The amount of dry matter lost to effluent.
        """
        pass

    def calculate_protein_degradation(self):
        """
        Calculates protein degradation.

        Returns
        -------
        None
        """
        pass

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
        moisture_at_baling = 1 - initial_dry_matter_percentage
        return 104 * (moisture_at_baling**2.18) * (bale_density**0.5) + 5.72 * (moisture_at_baling**1.23) * (
            bale_density**0.94
        )

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

    def recalculate_nutrient_fractions(self):
        """
        Recalculates the relative nutrient concentrations after dry matter loss.

        Returns
        -------
        None
        """
        pass
