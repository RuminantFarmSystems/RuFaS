from storage import Storage


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

    @property
    def bale_density(self) -> float:
        """
        Calculate and return the density of the hay bale.

        Returns
        -------
        float
            The density of the hay bale.
        """
        pass

  