from enum import Enum

from RUFAS.biophysical.feed_storage.hay import Hay, ProtectedIndoors, ProtectedWrapped, ProtectedTarped, Unprotected
from RUFAS.biophysical.feed_storage.silage import Bunker, Pile, Bag
from RUFAS.biophysical.feed_storage.baleage import Baleage
from RUFAS.biophysical.feed_storage.grain import Dry, HighMoisture
from RUFAS.biophysical.feed_storage.storage import Storage
from RUFAS.output_manager import OutputManager


class StorageType(Enum):
    """Enumeration of feed storage types."""

    Hay = Hay
    ProtectedIndoors = ProtectedIndoors
    ProtectedWrapped = ProtectedWrapped
    ProtectedTarped = ProtectedTarped
    Unprotected = Unprotected

    Baleage = Baleage

    Dry = Dry
    HighMoisture = HighMoisture

    Bunker = Bunker
    Pile = Pile
    Bag = Bag

    @classmethod
    def get_storage_class(cls, storage_type: str) -> type["Storage"]:
        """
        Get the corresponding feed storage class directly from the Enum.

        Parameters
        ----------
        storage_type : str
            The type of feed storage as a string (from JSON).

        Returns
        -------
        type[Storage]
            The class corresponding to the feed storage type.

        Raises
        ------
        ValueError
            If the feed storage type is not recognized.

        """
        try:
            storage: type["Storage"] = cls[storage_type].value
            return storage
        except KeyError:
            OutputManager().add_error(
                "Unknown storage type error",
                f"Error trying to get unknown storage type: {storage_type}.",
                info_map={"class": cls.__name__, "function": cls.get_storage_class.__name__},
            )
            raise ValueError(f"Unknown storage type: {storage_type}.")
