from .storage import Storage
from .enums import CropCategory
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.time import Time
from typing import Optional


class Sileage(Storage):
    """
    Class representing the Sileage storage type, inheriting from Storage.

    Methods
    -------
    estimate_maximum_effluent(initial_dry_matter_percentage: float, initial_fresh_mass: float)
        Estimates the maximum amount of effluent for a stored crop.
    calculate_dry_matter_loss_to_effluent(dry_matter: float, estimated_maximum_effluent: float, time_in_silo: int)
        Calculates the dry matter loss to effluent.

    """

    def __init__(self, capacity: float = float("inf")):
        super().__init__(capacity)
        self.acceptable_crops = [
            CropCategory.ALFALFA,
            CropCategory.CORN,
            CropCategory.GRASS,
            CropCategory.SMALL_GRAIN,
        ]

    def process_degradations(self, current_conditions: CurrentDayConditions, time: Time) -> None:
        """
        Processes the daily degradations and losses of ensiled crops.

        Parameters
        ----------
        temperature : float
            Ambient temperature in degrees C.
        time : Time
            The number of days this crop has been stored for.

        Notes
        -----
        Silage calls the Storage class to handle gaseous dry matter loss, but handles dry matter loss to effluent in
        this routine.

        """
        for crop in self.stored:
            estimated_max_effluent = self.estimate_maximum_effluent(
                crop.initial_dry_matter_percentage, crop.initial_fresh_mass
            )
            time_in_silo = crop.days_stored(time)
            effluent_loss = self.calculate_dry_matter_loss_to_effluent(
                crop.dry_matter, estimated_max_effluent, time_in_silo
            )
            crude_protein_effluent_coefficient = self.calculate_protein_loss_to_effluent(
                crop.crude_protein_percent, effluent_loss
            )
            non_protein_nitrogen_loss_coefficient = self.calculate_non_protein_nitrogen_loss_to_effluent(
                crop.non_protein_nitrogen, crop.crude_protein_percent, effluent_loss
            )

            crop.crude_protein_percent = self.recalculate_nutrient_concentration(
                crop.crude_protein_percent, crude_protein_effluent_coefficient, effluent_loss, crop.dry_matter_mass
            )
            crop.non_protein_nitrogen = self.recalculate_nutrient_concentration(
                crop.non_protein_nitrogen, non_protein_nitrogen_loss_coefficient, effluent_loss, crop.dry_matter_mass
            )

            self.set_mass_attributes_after_loss(crop, effluent_loss)
        super().process_degradations(current_conditions, time)

    def estimate_maximum_effluent(self, initial_dry_matter_percentage: float, initial_fresh_mass: float) -> float:
        """
        Estimates the maximum effluence of a stored crop.

        Parameters
        ----------
        dry_matter_percentage : float
            Initial percentage of a stored crop's fresh mass that is dry matter.
        fresh_mass : float
            Initial fresh mass of a stored crop in kg.

        Returns
        -------
        float
            Estimated maximum effluent of the stored crop in kg water.

        """
        initial_dry_matter_fraction = initial_dry_matter_percentage / 100

        if initial_dry_matter_fraction >= 0.3:
            return 0.0

        return initial_fresh_mass * ((1 - initial_dry_matter_fraction) - 0.7)

    def calculate_dry_matter_loss_to_effluent(
        self, dry_matter: float, estimated_maximum_effluent: float, time_in_silo: int
    ) -> float:
        """
        Calculates the dry matter loss to effluent.

        Parameters
        ----------
        dry_matter : float
            The amount of dry matter in kg.
        estimated_maximum_effluent : float
            The estimated maximum effluent in kg.
        time_in_silo : int
            Time in days the crop has been in the silo.

        Returns
        -------
        float
            The amount of dry matter lost to effluent in kg.

        """
        return (0.1035 * estimated_maximum_effluent) * (0.1 * time_in_silo) * (1 / dry_matter)

    def calculate_protein_loss_to_effluent(self, initial_crude_protein: float, effluent_loss: float) -> float:
        """
        Calculate crude protein lost to effluent loss of dry matter.

        Parameters
        ----------
        initial_crude_protein : float
            Percentage of dry matter mass that is crude protein before loss to effluent.
        effluent_loss : float
            Fraction of dry matter lost to effluent.

        Returns
        -------
        float
            The percentage of crude protein in the dry matter mass that was lost to effluent.

        Notes
        -----
        If all dry matter mass is lost to effluent, all crude protein is lost too.

        """
        if effluent_loss == 1.0:
            return initial_crude_protein
        elif effluent_loss == 0.0:
            return 0.0
        elif initial_crude_protein == 0.0:
            return 0.0

        return (initial_crude_protein - 0.3 * effluent_loss) / (1 - effluent_loss)

    def calculate_non_protein_nitrogen_loss_to_effluent(
        self, initial_non_protein_nitrogen: float, initial_crude_protein: float, effluent_loss: float
    ) -> float:
        """
        Calculate non-protein nitrogen losst to effluent loss of dry matter.

        Parameters
        ----------
        initial_non_protein_nitrogen : float
            Percentage of dry matter mass that is non-protein nitrogen before loss to effluent.
        initial_crude_protein : float
            Percentage of dry matter mass that is crude protein before loss to effluent.
        effluent_loss : float
            Fraction of dry matter lost to effluent.

        Returns
        -------
        float
            The percentage of crude protein in the dry matter mass that was lost to effluent.

        """
        if effluent_loss == 1.0:
            return initial_non_protein_nitrogen
        elif effluent_loss == 0.0:
            return 0.0
        elif initial_non_protein_nitrogen == 0.0:
            return 0.0

        return (initial_non_protein_nitrogen * initial_crude_protein - 0.3 * effluent_loss) / (
            initial_crude_protein - 0.3 * effluent_loss
        )


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
