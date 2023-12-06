from .storage import Storage
from typing import Optional


class Sileage(Storage):
    """
    Class representing the Sileage storage type, inheriting from Storage.

    Methods are placeholders as per the design document and are to be implemented.
    """

    def calculate_protein_loss(self):
        """
        Placeholder method to calculate protein loss specific to Sileage.

        Returns
        -------
        None
        """
        pass

    def calculate_dry_matter_loss_to_gas(
        self, dry_matter: float, time_in_silo: int
    ) -> float:
        """
        Calculates the dry matter loss to gas, specific to Sileage.

        Parameters
        ----------
        dry_matter : float
            The amount of dry matter.
        time_in_silo : int
            Time in days the crop has been in the silo.

        Returns
        -------
        float
            The amount of dry matter lost to gas, specific to Sileage.
        """
        pass

    def calculate_dry_matter_loss_to_effluent(
        self, dry_matter: float, estimated_maximum_effluent: float, time_in_silo: int
    ) -> float:
        """
        Calculates the dry matter loss to effluent, specific to Sileage.

        Parameters
        ----------
        dry_matter : float
            The amount of dry matter.
        estimated_maximum_effluent : float
            The estimated maximum effluent.
        time_in_silo : int
            Time in days the crop has been in the silo.

        Returns
        -------
        float
            The amount of dry matter lost to effluent, specific to Sileage.
        """
        pass


class Bunker(Sileage):
    """
    Class representing the Bunker type of Sileage storage.
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


class Pile(Sileage):
    """
    Class representing the Pile type of Sileage storage.
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


class Bag(Sileage):
    """
    Class representing the Bag type of Sileage storage.
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
