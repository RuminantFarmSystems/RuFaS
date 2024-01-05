from typing import List, Dict
from enum import Enum
from .harvested_crop import HarvestedCrop
from .storage import Storage
from .enums import CropType, CropCategory

from .baleage import Baleage
from .grain import Grain, Dry, HighMoisture
from .hay import Hay, ProtectedIndoors, ProtectedTarped, ProtectedWrapped, Unprotected
from .sileage import Sileage, Bag, Bunker, Pile

# Defines the compatilibty between Crop Categories and Storage Types.
CROP_TO_STORAGE_MAPPING: Dict[CropCategory, List[Storage]] = {
    CropCategory.ALFALFA: [Hay, Sileage, Baleage],
    CropCategory.CORN: [Grain, Sileage],
    CropCategory.GRASS: [Hay, Sileage, Baleage],
    CropCategory.SMALL_GRAIN: [Hay, Grain, Sileage, Baleage],
    CropCategory.SOY: [Grain],
}


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
    Dict[StorageType, Storage]
        Containts the list of active storage units in the simulation and their mapping from StorageType(Enum).
    """

    def __init__(self):
        self.active_storages: Dict[StorageType, Storage] = {}

    def receive_crop(
        self,
        harvested_crop: HarvestedCrop,
        storage_type: StorageType,
    ) -> None:
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
        compatible_storage_classes = CROP_TO_STORAGE_MAPPING.get(
            harvested_crop.category, []
        )
        is_crop_compatible_with_storage = any(
            issubclass(storage_type.value, storage_class)
            for storage_class in compatible_storage_classes
        )

        if not is_crop_compatible_with_storage:
            raise ValueError(
                f"Crop of category '{harvested_crop.category}' is not compatible with storage type '{storage_type}'. "
                f"Compatible storage types are: {', '.join([cls.__name__ for cls in compatible_storage_classes])}"
            )

        if storage_type not in self.active_storages:
            self.active_storages[storage_type] = storage_type.value()

        self.active_storages[storage_type].receive_crop(harvested_crop)

    def process_degradations(self) -> None:
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
        self, queryable_crops: List[CropType] = None
    ) -> Dict[CropType, float]:
        """
        Queries the available amount of feed in storage.

        Parameters
        ----------
        queryable_crops : List[CropType], optional
            The types of crop to query (default is None, which queries all types).

        Returns
        -------
        Dict[CropType, float]
            The amount of available feed, either as a total or for a specific crop type.
        """
        query_all = queryable_crops is None
        available_feeds: Dict[CropType, float] = {}

        for storage in self.active_storages.values():
            for stored_crop in storage.stored:
                if query_all or stored_crop.type in queryable_crops:
                    if stored_crop.type not in available_feeds:
                        available_feeds[stored_crop.type] = 0

                    available_feeds[stored_crop.type] += stored_crop.fresh_mass

        return available_feeds

    def purchase_feed(self) -> None:
        """The purchase feed logic is currently in the Animal Module. We will move it to here."""
        pass
