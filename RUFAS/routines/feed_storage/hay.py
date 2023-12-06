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

