from typing import List
from harvested_crop import HarvestedCrop
from harvested_crop import CropType


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
    receive_crop(crop: HarvestedCrop):
        Receives a harvested crop and adds it to the storage.
    process_degradations():
        Processes the degradations and losses of the stored crops.
    give_feed(amount: float, crop_type: str):
        Gives out a specified amount of feed of a certain crop type.
    calculate_dry_matter_loss_to_gas(dry_matter: float, time_in_silo: int):
        Calculates the dry matter loss to gas.
    calculate_dry_matter_loss_to_effluent(dry_matter: float, estimated_maximum_effluent: float, time_in_silo: int):
        Calculates the dry matter loss to effluent.
    calculate_protein_degradation():
        Calculates protein degradation.
    calculate_heat_generated():
        Calculates the total sensible heat generated.
    calculate_bale_density(initial_dry_matter: float):
        Calculates the density of a bale.
    recalculate_nutrient_fractions():
        Recalculates the relative nutrient concentrations after dry matter loss.
    """

    def __init__(self):
        self.stored: List[HarvestedCrop] = []
        self.capacity = float("inf")

    def receive_crop(self, crop: HarvestedCrop):
        """
        Receives a harvested crop and adds it to the storage.

        Parameters
        ----------
        crop : HarvestedCrop
            The harvested crop to be added to the storage.

        Returns
        -------
        None
        """
        pass

    def process_degradations(self):
        """
        Processes the degradations and losses of the stored crops.

        Returns
        -------
        None
        """
        pass

 