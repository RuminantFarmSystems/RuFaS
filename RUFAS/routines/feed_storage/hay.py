from .storage import Storage
from .enums import CropCategory
from .harvested_crop import HarvestedCrop
from ...general_constants import GeneralConstants
from ...time import Time


"""
This final moisture fraction that expected to be contained in a hay crop. Refernces Feed Storage Scientific
Documentation equation 1.2.6.
"""
FINAL_MOISTURE_FRACTION = 0.12

class Hay(Storage):
    """
    Represents a Hay storage subclass of Storage.

    Attributes
    ----------
    bale_density : float
        Density of the hay bale calculated based on its moisture content.
    bale_size : float
        Diameter of the hay bale in meters.

    Methods
    -------
    calculate_protein_loss():
        Calculates the protein loss in the hay.
    """

    def __init__(self, capacity: float = float("inf")):
        super().__init__(capacity)
        self.acceptable_crops = [
            CropCategory.ALFALFA,
            CropCategory.GRASS,
            CropCategory.SMALL_GRAIN,
        ]

    @property
    def bale_size(self) -> float:
        """
        Return the size (diameter) of the hay bale.

        Returns
        -------
        float
            The diameter of the hay bale in meters.
        """
        pass

    def calculate_dry_matter_loss_to_gas(self, crop: HarvestedCrop, time: Time) -> float:
        """
        Calculates the base amount of gaseous dry matter lost in a hayed crop.

        Parameters
        ----------
        crop : HarvestedCrop
            The hayed crop to process dry matter loss in.
        time : Time
            Time instance containing the time that loss should be processed up to.

        References
        ----------
        .. [1] Feed Storage Scientific Documentation, equations 1.2.3 and 1.2.7.

        """
        days_stored = time.simulation_day - crop.storage_time.simulation_day
        if days_stored == 0:
            return 0.0
        
        moisture_fraction = 1 - crop.initial_dry_matter_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION
        days_in_initial_30_day_window = min(days_stored, 30)
        numerator = moisture_fraction - 
        loss_in_first_30_days = 


class ProtectedIndoors(Hay):
    """
    Represents protected indoors hay storage, a subclass of Hay.
    """

    pass


class ProtectedWrapped(Hay):
    """
    Represents protected wrapped hay storage, a subclass of Hay.
    """

    pass


class ProtectedTarped(Hay):
    """
    Represents protected tarped hay storage, a subclass of Hay.
    """

    pass


class Unprotected(Hay):
    """
    Represents unprotected hay storage, a subclass of Hay.
    """

    pass
