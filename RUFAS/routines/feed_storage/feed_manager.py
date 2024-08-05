from typing import List, Dict
from enum import Enum
from .harvested_crop import HarvestedCrop
from .storage import Storage
from .enums import CropType, CropCategory

from .baleage import Baleage
from .grain import Grain, Dry, HighMoisture
from .hay import Hay, ProtectedIndoors, ProtectedTarped, ProtectedWrapped, Unprotected
from .silage import Silage, Bag, Bunker, Pile
from ...time import Time
from ...weather import Weather

# Defines the compatilibty between Crop Categories and Storage Types.
CROP_TO_STORAGE_MAPPING: Dict[CropCategory, List[Storage]] = {
    CropCategory.ALFALFA: [Hay, Silage, Baleage],
    CropCategory.CORN: [Grain, Silage],
    CropCategory.GRASS: [Hay, Silage, Baleage],
    CropCategory.SMALL_GRAIN: [Hay, Grain, Silage, Baleage],
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


QUERY_RESULT_DATA_TYPE = Dict[str, CropCategory | CropType | float]


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

    def _query_result_factory(
        self, crop_category: CropCategory, crop_type: CropType, amount: float
    ) -> QUERY_RESULT_DATA_TYPE:
        return {
            "category": crop_category,
            "type": crop_type,
            "amount": amount,
        }

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
        compatible_storage_classes = CROP_TO_STORAGE_MAPPING.get(harvested_crop.category, [])
        is_crop_compatible_with_storage = any(
            issubclass(storage_type.value, storage_class) for storage_class in compatible_storage_classes
        )

        if not is_crop_compatible_with_storage:
            raise ValueError(
                f"Crop of category '{harvested_crop.category}' is not compatible with storage type '{storage_type}'. "
                f"Compatible storage types are: {', '.join([cls.__name__ for cls in compatible_storage_classes])}"
            )

        if storage_type not in self.active_storages:
            self.active_storages[storage_type] = storage_type.value()

        self.active_storages[storage_type].receive_crop(harvested_crop)

    def process_degradations(self, weather: Weather, time: Time) -> None:
        """
        Processes the degradation of all stored feeds over time.
        """
        for _, storage in self.active_storages.items():
            storage.process_degradations(weather, time)

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
        self,
        query_crop_types: List[CropType] | None = None,
        query_crop_categories: List[CropCategory] | None = None,
        query_storage_types: List[StorageType] | None = None,
    ) -> List[QUERY_RESULT_DATA_TYPE]:
        """
        Queries the available amount of feed in storage.

        Parameters
        ----------
        query_crop_types : List[CropType], optional, default=None
            The types of crop to query (if None, all crop types are queried).
        query_crop_categories : List[CropCategory], optional, default=None
            The categories of crop to query (if None, all crop categories are queried).
        query_storage_types : List[StorageType], optional, default=None
            The types of storage to query (if None, all storages types are queried).

        Returns
        -------
        List[QUERY_RESULT_DATA_TYPE]
            The amount of available feed, either as a total or for a specific crop type.
        """
        query_all_crop_types = query_crop_types is None
        query_all_crop_categories = query_crop_categories is None
        query_all_storage_types = query_storage_types is None
        results: List[QUERY_RESULT_DATA_TYPE] = []

        for storage_type, storage in self.active_storages.items():
            is_storage_queryable = query_all_storage_types or storage_type in query_storage_types
            if not is_storage_queryable:
                continue
            for stored_crop in storage.stored:
                is_crop_type_queryable = query_all_crop_types or stored_crop.type in query_crop_types
                is_crop_category_queryable = query_all_crop_categories or stored_crop.category in query_crop_categories
                if not (is_crop_type_queryable and is_crop_category_queryable):
                    continue
                for previous_result in results:
                    if (
                        stored_crop.type == previous_result["type"]
                        and stored_crop.category == previous_result["category"]
                    ):
                        previous_result["amount"] += stored_crop.fresh_mass
                        break
                else:
                    results.append(
                        self._query_result_factory(
                            stored_crop.category,
                            stored_crop.type,
                            stored_crop.fresh_mass,
                        )
                    )

        return results

    def purchase_feed(self) -> None:
        """The purchase feed logic is currently in the Animal Module. We will move it to here."""
        pass

    def setup_stored_feeds(self, feeds_info: dict[str, dict[str, str | float]], time: Time) -> None:
        """Sets up HarvestedCrops for the Feed Manager to degrade, if running end-to-end testing."""
        reusable_values = feeds_info["reusable_values"]
        reusable_values.update({"harvest_time": time, "storage_time": time})

        hay_values = feeds_info["hay_values"]
        hay_values.update(
            {"category": CropCategory(hay_values["category"]), "type": CropType(hay_values["crop_type"])},
            **reusable_values,
        )
        del hay_values["crop_type"]
        baleage_values = feeds_info["baleage_values"]
        baleage_values.update(
            {"category": CropCategory(baleage_values["category"]), "type": CropType(baleage_values["crop_type"])},
            **reusable_values,
        )
        del baleage_values["crop_type"]
        grain_values = feeds_info["grain_values"]
        grain_values.update(
            {"category": CropCategory(grain_values["category"]), "type": CropType(grain_values["crop_type"])},
            **reusable_values,
        )
        del grain_values["crop_type"]
        silage_values = feeds_info["silage_values"]
        silage_values.update(
            {"category": CropCategory(silage_values["category"]), "type": CropType(silage_values["crop_type"])},
            **reusable_values,
        )
        del silage_values["crop_type"]

        storages: dict[StorageType, Storage] = {
            StorageType.PROTECTED_INDOORS: ProtectedIndoors(),
            StorageType.PROTECTED_WRAPPED: ProtectedWrapped(),
            StorageType.PROTECTED_TARPED: ProtectedTarped(),
            StorageType.UNPROTECTED: Unprotected(),
            StorageType.BALEAGE: Baleage(),
            StorageType.DRY: Dry(),
            StorageType.HIGH_MOISTURE: HighMoisture(),
            StorageType.BUNKER: Bunker(),
            StorageType.PILE: Pile(),
            StorageType.BAG: Bag(),
        }
        storages[StorageType.PROTECTED_INDOORS].receive_crop(HarvestedCrop(**hay_values))  # type: ignore[arg-type]
        storages[StorageType.PROTECTED_WRAPPED].receive_crop(HarvestedCrop(**hay_values))  # type: ignore[arg-type]
        storages[StorageType.PROTECTED_TARPED].receive_crop(HarvestedCrop(**hay_values))  # type: ignore[arg-type]
        storages[StorageType.UNPROTECTED].receive_crop(HarvestedCrop(**hay_values))  # type: ignore[arg-type]
        storages[StorageType.BALEAGE].receive_crop(HarvestedCrop(**baleage_values))  # type: ignore[arg-type]
        storages[StorageType.DRY].receive_crop(HarvestedCrop(**grain_values))  # type: ignore[arg-type]
        storages[StorageType.HIGH_MOISTURE].receive_crop(HarvestedCrop(**grain_values))  # type: ignore[arg-type]
        storages[StorageType.BUNKER].receive_crop(HarvestedCrop(**silage_values))  # type: ignore[arg-type]
        storages[StorageType.PILE].receive_crop(HarvestedCrop(**silage_values))  # type: ignore[arg-type]
        storages[StorageType.BAG].receive_crop(HarvestedCrop(**silage_values))  # type: ignore[arg-type]

        self.active_storages = storages
