from .storage import Storage
from .enums import CropCategory
from typing import Optional


class Sileage(Storage):
    """
    Class representing the Sileage storage type, inheriting from Storage.

    Methods are placeholders as per the design document and are to be implemented.
    """

    def __init__(self, capacity: float = float("inf")):
        super().__init__(capacity)
        self.acceptable_crops = [
            CropCategory.ALFALFA,
            CropCategory.CORN,
            CropCategory.GRASS,
            CropCategory.SMALL_GRAIN,
        ]

    def calculate_dry_matter_loss_to_gas(
        self, dry_matter: float, dry_matter_percentage: float, crop_category: CropCategory, temperature: float
    ) -> float:
        """
        Calculates the dry matter loss to gas, specific to Sileage.

        Parameters
        ----------
        dry_matter : float
            The amount of dry matter in kg.
        dry_matter_percentage : float
            Pecentage of fresh mass that is dry matter.
        crop_category : CropCategory
            Type of the crop.
        temperature : float
            Ambient temperature outside the silo in degrees C.

        Returns
        -------
        float
            The amount of dry matter lost to gas, specific to Sileage.

        Notes
        -----
        The equations and conditions for gaseous dry matter loss in Alfalfa silage follow the same structure as those
        for other crops, but use different values.

        """
        dry_matter_fraction = dry_matter_percentage / 100
        if crop_category is CropCategory.ALFALFA:
            if (not 5.0 <= temperature <= 45.0) or (not 20.0 <= dry_matter_percentage <= 60.0):
                return 0.0
            dry_matter_loss_fraction = 0.0156 - 0.0364 * (dry_matter_fraction - 0.20)
        else:
            if (not 0.0 <= temperature <= 40.0) or (not 15.0 <= dry_matter_percentage <= 60.0):
                return 0.0
            dry_matter_loss_fraction = 0.00864 - 0.0193 * (dry_matter_fraction - 0.15)

        return dry_matter * dry_matter_loss_fraction


class Bunker(Sileage):
    """
    Class representing the Bunker type of Sileage storage.
    """

    def __init__(self, bunker_size: Optional[str] = None):
        """
        Initializes a Bunker instance with optional bunker size.

        Parameters
        ----------
        bunker_size : Optional[str], optional
            The size of the bunker, by default None
        """
        super().__init__()
        self.bunker_size = bunker_size


class Pile(Sileage):
    """
    Class representing the Pile type of Sileage storage.
    """

    def __init__(self, pile_size: Optional[str] = None):
        """
        Initializes a Pile instance with optional pile size.

        Parameters
        ----------
        pile_size : Optional[str], optional
            The size of the pile, by default None
        """
        super().__init__()
        self.pile_size = pile_size


class Bag(Sileage):
    """
    Class representing the Bag type of Sileage storage.
    """

    def __init__(self, bag_size: Optional[int] = None):
        """
        Initializes a Bag instance with optional bag size.

        Parameters
        ----------
        bag_size : Optional[int], optional
            The diameter of the bag in feet, by default None
        """
        super().__init__()
        self.bag_size = bag_size
