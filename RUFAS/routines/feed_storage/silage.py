from .harvested_crop import HarvestedCrop
from .storage import Storage
from .enums import CropCategory
from typing import Optional
from RUFAS.time import Time
from RUFAS.weather import Weather


"""Fraction of effluent that is dry matter by mass."""
DRY_MATTER_FRACTION_OF_EFFLUENT = 0.1035
"""Number of days that loss of effluent occurs over after a crop is ensiled."""
EFFLUENT_CONSTRAINER = 10


class Silage(Storage):
    """
    Class representing the Silage storage type, inheriting from Storage.

    Methods
    -------
    calculate_days_of_effluent_loss_to_process(crop: HarvestedCrop, time: Time)
        Calculates the number of days to effluent loss needs to be processed for in the given crop.
    calculate_dry_matter_loss_to_effluent(estimated_maximum_effluent: float, days_of_loss: int)
        Calculates the total dry matter lost to effluent that occurred over the given number of days.
    calculate_moisture_loss_to_effluent(estimated_maximum_effluent: float, days_of_loss: int)
        Calculates the total moisture lost to effluent that occurred over the given number of days.

    """

    def __init__(self, capacity: float = float("inf")):
        super().__init__(capacity)
        self.acceptable_crops = [
            CropCategory.ALFALFA,
            CropCategory.CORN,
            CropCategory.GRASS,
            CropCategory.SMALL_GRAIN,
        ]

    def process_degradations(self, weather: Weather, time: Time) -> None:
        """
        Processes the degradations and losses of nutrients and dry matter in the stored crops.

        Parameters
        ----------
        weather : Weather
            Weather instance containing all weather information for the simulation.
        time : Time
            Time instance tracking the current time of the simulation.

        Notes
        -----
        This method also records the total amount of gaseous dry matter loss happened from all stored crops.

        """
        pass

    def calculate_days_of_effluent_loss_to_process(self, crop: HarvestedCrop, time: Time) -> int:
        """
        Calculates the number of days that effluent loss needs to be calculated for in an ensiled crop.

        Parameters
        ----------
        crop : HarvestedCrop
            Ensiled crop that is being degraded.
        time : Time
            Time instance containing the current time of the simulation.

        Notes
        -----
        Effluent loss only occurs in an ensiled crop during the first 10 days of storage, so this method calculates the
        numbers of days which were in that initial 10-day period between the time when the crop was last degraded and
        the current time.

        """
        days_of_effluent_processed = min(
            EFFLUENT_CONSTRAINER, crop.last_time_degraded.simulation_day - crop.storage_time.simulation_day
        )
        total_days_of_effluent_since_storage = min(
            EFFLUENT_CONSTRAINER, time.simulation_day - crop.storage_time.simulation_day
        )
        days_of_effluent_to_process = total_days_of_effluent_since_storage - days_of_effluent_processed
        return days_of_effluent_to_process

    def calculate_dry_matter_loss_to_effluent(self, estimated_maximum_effluent: float, days_of_loss: int) -> float:
        """
        Calculates the dry matter loss to effluent.

        Parameters
        ----------
        estimated_maximum_effluent : float
            The estimated maximum effluent.
        days_of_effluent_loss : int
            The number of days effluent loss will be calculated for.

        Returns
        -------
        float
            The amount of dry matter lost to effluent, in kg.

        References
        ----------
        .. [1] Feed Storage Scientific Documentation, equation 1.3.1.1

        """
        return estimated_maximum_effluent * days_of_loss * DRY_MATTER_FRACTION_OF_EFFLUENT / EFFLUENT_CONSTRAINER

    def calculate_moisture_loss_to_effluent(self, estimated_maximum_effluent: float, days_of_loss: int) -> float:
        """
        Calculates the moisture loss to effluent.

        Parameters
        ----------
        estimated_maximum_effluent : float
            The estimated maximum effluent.
        days_of_effluent_loss : int
            The number of days effluent loss will be calculated for.

        Returns
        -------
        float
            The amount of moisture lost to effluent, in kg.

        References
        ----------
        .. [1] Feed Storage Scientific Documentation, equation 1.3.1.2

        """
        return estimated_maximum_effluent * days_of_loss * (1 - DRY_MATTER_FRACTION_OF_EFFLUENT) / EFFLUENT_CONSTRAINER


class Bunker(Silage):
    """
    Class representing the Bunker type of Silage storage.
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


class Pile(Silage):
    """
    Class representing the Pile type of Silage storage.
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


class Bag(Silage):
    """
    Class representing the Bag type of Silage storage.
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
