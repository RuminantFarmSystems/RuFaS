from typing import List, Dict, Union
from enum import Enum

from .harvested_crop import HarvestedCrop
from .storage import Storage
from .enums import CropType

from .baleage import Baleage
from .grain import Dry, HighMoisture
from .hay import ProtectedIndoors, ProtectedTarped, ProtectedWrapped, Unprotected
from .sileage import Bag, Bunker, Pile


class StorageType(Enum):
    """
    Maps each storage type to its respective class.
    """

    PROTECTED_INDOORS = ProtectedIndoors
    PROTECTED_WRAPPED = ProtectedWrapped
    PROTECTED_TARPED = ProtectedTarped
    UNPROTECTED = Unprotected
    BALEAGE = Baleage
    DRY = Dry
    HIGH_MOISTURE = HighMoisture
    BUNKER = Bunker
    PILE = Pile
    BAG = Bag


class FeedManager:
    """
    Manages the feed storage, handling crop reception, purchasing, degradation processing, feed distribution,
    and querying available feeds.

    Attributes
    ----------
    active_storages : List[Storage]
        List of active storage units in the simulation.
    """

    def __init__(self):
        self.active_storages: Dict[StorageType, Storage] = {}

    def receive_crop(self, harvested_crop: HarvestedCrop, storage_type: StorageType):
        """
        Receives a harvested crop and assigns it to a storage unit.

        Parameters
        ----------
        harvested_crop : HarvestedCrop
            The harvested crop to be stored.
        storage_type : StorageType
            The type of storage to use for this crop.

        Raises
        ------
        ValueError
            If the crop type is not compatible with the storage type.
        """
        pass

    def process_degradations(self):
        """
        Processes the degradation of all stored feeds over time.
        """
        for _, storage in self.active_storages.items():
            storage.process_degradations()

    def give_feed(self, amount: float, crop_type: CropType) -> float:
        """
        Distributes feed to the Animal module based on the FIFO principle.

        Parameters
        ----------
        amount : float
            The amount of feed to distribute.
        crop_type : CropType
            The type of crop to distribute.

        Returns
        -------
        float
            The actual amount of feed distributed.
        """
        pass

    def query_available_feeds(
        self, crop_type: CropType = None
    ) -> Union[Dict[CropType, float], float]:
        """
        Queries the available amount of feed in storage.

        Parameters
        ----------
        crop_type : CropType, optional
            The type of crop to query (default is None, which queries all types).

        Returns
        -------
        Union[Dict[CropType, float], float]
            The amount of available feed, either as a total or for a specific crop type.
        """
        pass

    def purchase_feed(self) -> None:
        """The purchase feed logic is currently in the Animal Module. We will move it to here."""
        pass
