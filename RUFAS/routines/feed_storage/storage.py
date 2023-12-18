import copy
from typing import List, Optional
from RUFAS.time import Time
from .enums import CropType
from .harvested_crop import HarvestedCrop


class Storage:
    """
    Abstract class representing a general storage structure.

    Attributes
    ----------
    stored : List[HarvestedCrop]
        A list of HarvestedCrop objects representing the crops stored.
    capacity : float
        The maximum capacity of the storage, currently set to infinity.

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

    def __init__(self, capacity: Optional[float]):
        self.stored: List[HarvestedCrop] = []
        self.capacity = capacity or float("inf")

    @property
    def stored_mass(self) -> float:
        """The total mass (kg) of currently stored crops"""
        return sum(crop.fresh_mass for crop in self.stored)

    def receive_crop(self, crop: HarvestedCrop, time: Time) -> None:
        """
        Receives a harvested crop and adds it to the storage.

        Parameters
        ----------
        crop : HarvestedCrop
            The harvested crop to be added to the storage.
        time : Time
            An instance of the Time class, needed to set storage time.

        Returns
        -------
        None
        """
        if self.stored_mass + crop.fresh_mass > self.capacity:
            raise Exception(
                f"Adding {crop.fresh_mass} to currently stored ({self.stored_mass})\
                    exceeds the storage capacity ({self.capacity})"
            )
        storage_crop = copy.deepcopy(crop)
        storage_crop.storage_time = time
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

    def calculate_dry_matter_loss_to_gas(
        self, dry_matter: float, time_in_silo: int
    ) -> float:
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

    def calculate_heat_generated(self) -> float:
        """
        Calculates the total sensible heat generated.

        Returns
        -------
        float
            The total sensible heat generated in kJ/kg.
        """
        pass

    def calculate_bale_density(self, initial_dry_matter: float) -> float:
        """
        Calculates the density of a bale.

        Parameters
        ----------
        initial_dry_matter : float
            The initial dry matter of the bale.

        Returns
        -------
        float
            The density of the bale.
        """
        pass

    def recalculate_nutrient_fractions(self):
        """
        Recalculates the relative nutrient concentrations after dry matter loss.

        Returns
        -------
        None
        """
        pass
