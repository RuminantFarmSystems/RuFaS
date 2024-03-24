from .storage import Storage
from .enums import CropCategory, BaleSize


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

    def __init__(self, bale_diameter: BaleSize, capacity: float = float("inf")):
        super().__init__(capacity)
        self.acceptable_crops = [
            CropCategory.ALFALFA,
            CropCategory.GRASS,
            CropCategory.SMALL_GRAIN,
        ]
        self.bale_diameter = bale_diameter

    @property
    def bale_density(self) -> float:
        """
        Calculate and return the density of the hay bale.

        Returns
        -------
        float
            The density of the hay bale.
        """
        densities = []
        for crop in self.stored:
            moisture_at_baling = 100 - crop.initial_dry_matter_percentage
            bale_density = self.calculate_bale_density(moisture_at_baling)
            densities.append(bale_density)
        average_density = sum(densities) / len(densities)
        return average_density

    @property
    def bale_size(self) -> float:
        """
        Return the size (diameter) of the hay bale.

        Returns
        -------
        float
            The diameter of the hay bale in meters.
        """
        return self.bale_diameter.value()

    def calculate_protein_loss(self):
        """
        Calculates the protein loss in the hay.

        Returns
        -------
        None
        """
        pass


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
