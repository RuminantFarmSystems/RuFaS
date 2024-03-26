from .storage import Storage
from .enums import CropCategory
from .harvested_crop import HarvestedCrop
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.general_constants import GeneralConstants
from RUFAS.time import Time
from RUFAS.output_manager import OutputManager
from typing import Optional

om = OutputManager()

"""
If the fraction of water in the fresh mass of a crop is less than the threshold value at time of storage, no
effluent loss occurs from the crop.
"""
MOISTURE_FRACTION_THRESHOLD_FOR_EFFLUENT = 0.7


class Sileage(Storage):
    """
    Class representing the Sileage storage type, inheriting from Storage.

    Methods
    -------
    process_degradations(current_conditions: CurrentDayConditions, time: Time)
        Handles the processing of mass and nutritive loss to effluence and fermentation.
    estimate_maximum_effluent(crop: HarvestedCrop)
        Estimates the maximum amount of effluent (water) that will flow out of an ensiled crop.
    calculate_dry_matter_loss_to_effluent(crop: HarvestedCrop, estimated_maximum_effluent: float, time: Time)
        Calculates the amount of dry matter lost to effluent from an ensiled crop.
    calculate_protein_loss_to_effluent(self, crop: HarvestedCrop, effluent_loss: float)
        Calculates the percentage of crude protein in the dry matter of an ensiled crop after effluent loss.
    calculate_non_protein_nitrogen_loss_to_effluent(self, crop: HarvestedCrop, effluent_loss: float)
        Calculates the percentage of non-protein nitrogen in the dry matter of an ensiled crop after effluent loss.

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
        Processes the daily degradations and losses of ensiled crops to effluence, and calls on Storage to calculate
        loss to fermentation and record the state of ensiled crops.

        Parameters
        ----------
        current_conditions : float
            Conditions on the current day of the simulation.
        time : Time
            Time instance tracking the current time of the simulation.

        Notes
        -----
        Silage calls the Storage class to handle gaseous dry matter loss, but handles dry matter loss to effluent in
        this routine.

        """
        info_map = {"class": self.__class__.__name__, "function": self.process_degradations.__name__, "units": "kg"}
        total_effluent_loss = 0.0
        for crop in self.stored:
            estimated_max_effluent = self.estimate_maximum_effluent(crop)
            effluent_loss = self.calculate_dry_matter_loss_to_effluent(crop, estimated_max_effluent, time)
            total_effluent_loss += effluent_loss

            crude_protein_effluent_coefficient = self.calculate_protein_loss_to_effluent(crop, effluent_loss)
            non_protein_nitrogen_loss_coefficient = self.calculate_non_protein_nitrogen_loss_to_effluent(
                crop, effluent_loss
            )

            crop.non_protein_nitrogen = super().recalculate_nutrient_percentage(
                crop.non_protein_nitrogen, non_protein_nitrogen_loss_coefficient, effluent_loss, crop.dry_matter_mass
            )

            crop.crude_protein_percent = super().recalculate_nutrient_percentage(
                crop.crude_protein_percent, crude_protein_effluent_coefficient, effluent_loss, crop.dry_matter_mass
            )

            self.set_mass_attributes_after_loss(crop, effluent_loss)
        om.add_variable("effluent_dry_matter_loss", total_effluent_loss, info_map)
        super().process_degradations(current_conditions, time)

    def estimate_maximum_effluent(self, crop: HarvestedCrop) -> float:
        """
        Estimates the maximum amount of water (effluent) that will flow out of an ensiled crop.

        Parameters
        ----------
        crop : HarvestedCrop
            Crop for which the maximum amount of effluent is being estimated.

        Returns
        -------
        float
            Estimated maximum effluent of the stored crop in kg water.

        Notes
        -----
        If the amount of water in the fresh mass of a crop at storage is below the threshold value, then there will be
        no effluent lost from this crop.

        """
        initial_water_fraction = 1 - crop.stored_dry_matter_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION

        return crop.stored_fresh_mass * max(0.0, initial_water_fraction - MOISTURE_FRACTION_THRESHOLD_FOR_EFFLUENT)

    def calculate_dry_matter_loss_to_effluent(
        self, crop: HarvestedCrop, estimated_maximum_effluent: float, time: Time
    ) -> float:
        """
        Calculates the amount of dry matter lost from an ensiled crop to effluent.

        Parameters
        ----------
        crop : HarvestedCrop
            The crop from which dry matter is being lost to effluent.
        estimated_maximum_effluent : float
            The estimated maximum effluent in kg.
        time : Time
            Time instance tracking the current time of the simulation.

        Returns
        -------
        float
            The amount of dry matter the crop loses to effluent in kg.

        """
        time_in_silo = crop.days_stored(time)
        return (0.1035 * estimated_maximum_effluent) * (0.1 * time_in_silo) * (1 / crop.dry_matter_mass)

    def calculate_protein_loss_to_effluent(self, crop: HarvestedCrop, effluent_loss: float) -> float:
        """
        Calculate the percentage of crude protein in the dry matter of an ensiled crop after loss to effluent.

        Parameters
        ----------
        crop : HarvestedCrop
            The crop from which crude protein is being lost to effluent.
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
            return crop.crude_protein_percent
        elif effluent_loss == 0.0:
            return 0.0
        elif crop.crude_protein_percent == 0.0:
            return 0.0

        return (crop.crude_protein_percent - 0.3 * effluent_loss) / (1 - effluent_loss)

    def calculate_non_protein_nitrogen_loss_to_effluent(self, crop: HarvestedCrop, effluent_loss: float) -> float:
        """
        Calculate the percentage of non-protein nitrogen in the dry matter of an ensiled crop after loss to effluent.

        Parameters
        ----------
        crop : HarvestedCrop
            Crop from which non-protein nitrogen is being lost to effluent.
        effluent_loss : float
            Fraction of dry matter lost to effluent.

        Returns
        -------
        float
            The percentage of crude protein in the dry matter mass that was lost to effluent.

        Notes
        -----
        Calculation of non-protein nitrogen loss uses the amount of crude protein in the crop that is present before
        crude protein is lost to effluent.

        """
        if effluent_loss == 1.0:
            return crop.non_protein_nitrogen
        elif effluent_loss == 0.0:
            return 0.0
        elif crop.non_protein_nitrogen == 0.0:
            return 0.0

        return (crop.non_protein_nitrogen * crop.crude_protein_percent - 0.3 * effluent_loss) / (
            crop.crude_protein_percent - 0.3 * effluent_loss
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
