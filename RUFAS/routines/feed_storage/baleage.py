from .storage import Storage
from .enums import CropCategory


class Baleage(Storage):
    """
    Class representing Baleage storage, a subclass of Storage.

    Attributes
    ----------
    bale_density : float
        Density of the bale, calculated based on the dry matter.

    Methods
    -------
    calculate_protein_loss():
        Calculates the protein loss specific to Baleage storage.
    """

    def __init__(self, capacity: float = float("inf")):
        super().__init__(capacity)
        self.acceptable_crops = [
            CropCategory.ALFALFA,
            CropCategory.GRASS,
            CropCategory.SMALL_GRAIN,
        ]
        self.bale_density: float = 0

    def calculate_protein_loss(self) -> None:
        """
        Calculate the protein loss specific to Baleage storage.

        Returns
        -------
        None
        """
        pass
