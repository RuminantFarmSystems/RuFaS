from .storage import Storage
from .enums import CropCategory


class Grain(Storage):
    def __init__(self, capacity: float = float("inf")):
        super().__init__(capacity)
        self.acceptable_crops = [
            CropCategory.CORN,
            CropCategory.SMALL_GRAIN,
            CropCategory.SOY,
        ]

    """
    Represents grain storage and manages its specific attributes and behaviors.

    Inherits from Storage.
    """

    pass


class Dry(Grain):
    """
    Represents dry grain storage and manages its specific attributes and behaviors.

    Inherits from Grain.
    """

    pass


class HighMoisture(Grain):
    """
    Represents high-moisture grain storage and manages its specific attributes and behaviors.

    Inherits from Grain.
    """

    pass
