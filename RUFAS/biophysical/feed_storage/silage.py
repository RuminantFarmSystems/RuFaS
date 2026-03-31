from dataclasses import replace

from RUFAS.general_constants import GeneralConstants
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits
from RUFAS.weather import Weather

from .storage import Storage

"""Fraction of effluent that is dry matter by mass."""
DRY_MATTER_FRACTION_OF_EFFLUENT = 0.1035
"""Number of days that loss of effluent occurs over after a crop is ensiled."""
EFFLUENT_CONSTRAINER = 10


class Silage(Storage):
    """
    Class representing the Silage storage type, inheriting from Storage.

    Parameters
    ----------
    config : dict[str, str | float]
        Configuration dictionary for the silage storage.

    Attributes
    ----------
    om : OutputManager
        OutputManager instance for logging variables.

    Methods
    -------
    calculate_days_of_effluent_loss_to_process(crop: HarvestedCrop, time: RufasTime)
        Calculates the number of days to effluent loss needs to be processed for in the given crop.
    calculate_dry_matter_loss_to_effluent(estimated_maximum_effluent: float, days_of_loss: int)
        Calculates the total dry matter lost to effluent that occurred over the given number of days.
    calculate_moisture_loss_to_effluent(estimated_maximum_effluent: float, days_of_loss: int)
        Calculates the total moisture lost to effluent that occurred over the given number of days.

    """

    def __init__(self, config: dict[str, str | float | list[str]]) -> None:
        super().__init__(config)
        self.om = OutputManager()

    def process_degradations(self, weather: Weather, time: RufasTime) -> None:
        """
        Processes the losses of nutrients and mass to effluent in the ensiled crops, calls the parent implementation of
        of `process_degradations` to handle the fermentative loss.

        Parameters
        ----------
        weather : Weather
            Weather instance containing all weather information for the simulation.
        time : RufasTime
            RufasTime instance tracking the current time of the simulation.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.process_degradations.__name__,
            "units": MeasurementUnits.KILOGRAMS,
            "simulation_day": time.simulation_day,
            "prefix": self._prefix,
        }
        total_effluent_dry_matter_loss = 0.0
        total_effluent_moisture_loss = 0.0
        for crop in self.stored:
            effluent_loss_values = self._calculate_effluent_loss(crop, time)
            total_effluent_dry_matter_loss += effluent_loss_values["dry_matter_loss"]
            total_effluent_moisture_loss += effluent_loss_values["moisture_loss"]
            crop.non_protein_nitrogen = effluent_loss_values["non_protein_nitrogen"]
            crop.crude_protein_percent = effluent_loss_values["crude_protein_percent"]
            crop.dry_matter_mass = effluent_loss_values["dry_matter_mass"]
            crop.dry_matter_percentage = effluent_loss_values["dry_matter_percentage"]

        self.om.add_variable("total_effluent_dry_matter_loss", total_effluent_dry_matter_loss, info_map)
        self.om.add_variable("total_effluent_moisture_loss", total_effluent_moisture_loss, info_map)

        super().process_degradations(weather, time)

    def project_degradations(
        self, crops: list[HarvestedCrop], weather: Weather, time: RufasTime
    ) -> list[HarvestedCrop]:
        """
        Projects the state of crops currently stored at a given future date.

        Parameters
        ----------
        crops : list[HarvestedCrop]
            List of HarvestedCrops to project degradations for.
        weather : Weather
            Weather instance containing all weather information for the simulation.
        time : RufasTime
            RufasTime instance containing the date at which the state of the stored crops should be projected.

        Returns
        -------
        list[HarvestedCrop]
            Crops in the state they are projected to be in at the given date.

        """
        crops_projected_with_effluent_loss: list[HarvestedCrop] = []
        for crop in crops:
            effluent_loss_values = self._calculate_effluent_loss(crop, time)
            del effluent_loss_values["dry_matter_loss"]
            del effluent_loss_values["moisture_loss"]
            projected_crop = replace(crop, **effluent_loss_values)
            crops_projected_with_effluent_loss.append(projected_crop)

        return super().project_degradations(crops_projected_with_effluent_loss, weather, time)

    def _calculate_effluent_loss(self, crop: HarvestedCrop, time: RufasTime) -> dict[str, float]:
        """
        Calculates the attributes of a crop after effluent loss.

        Parameters
        ----------
        crop : HarvestedCrop
            HarvestedCrop to calculate effluent losses from.
        time : RufasTime
            RufasTime instance tracking the current time of the simulation.

        Returns
        -------
        dict[str, float]
            Mapping of crop's attributes to their values after effluent loss.

        """
        post_loss_values = {
            "dry_matter_mass": crop.dry_matter_mass,
            "dry_matter_percentage": crop.dry_matter_percentage,
            "non_protein_nitrogen": crop.non_protein_nitrogen,
            "crude_protein_percent": crop.crude_protein_percent,
            "dry_matter_loss": 0.0,
            "moisture_loss": 0.0,
        }
        days_of_effluent_to_process = self.calculate_days_of_effluent_loss_to_process(crop, time)
        if days_of_effluent_to_process == 0:
            return post_loss_values

        crop.estimated_maximum_effluent = crop.estimate_maximum_effluent()
        dry_matter_loss = self.calculate_dry_matter_loss_to_effluent(
            crop.estimated_maximum_effluent, days_of_effluent_to_process
        )
        moisture_loss = self.calculate_moisture_loss_to_effluent(
            crop.estimated_maximum_effluent, days_of_effluent_to_process
        )

        dry_matter_loss_frac = dry_matter_loss / crop.dry_matter_mass
        post_loss_values["non_protein_nitrogen"] = self.calculate_non_protein_nitrogen_after_effluent_loss(
            crop.non_protein_nitrogen, crop.crude_protein_percent, dry_matter_loss_frac
        )

        post_loss_values["crude_protein_percent"] = self.calculate_crude_protein_after_effluent_loss(
            crop.crude_protein_percent, dry_matter_loss_frac
        )

        mass_attributes = self._calculate_mass_attributes_after_loss(crop, dry_matter_loss, moisture_loss)
        post_loss_values.update(mass_attributes | {"dry_matter_loss": dry_matter_loss, "moisture_loss": moisture_loss})
        return post_loss_values

    def calculate_days_of_effluent_loss_to_process(self, crop: HarvestedCrop, time: RufasTime) -> int:
        """
        Calculates the number of days of effluent loss to process for an ensiled crop.

        Parameters
        ----------
        crop : HarvestedCrop
            Ensiled crop that is being degraded.
        time : RufasTime
            RufasTime instance containing the current time of the simulation.

        Returns
        -------
        int
            Number of days to calculate effluent loss for.

        Notes
        -----
        - Effluent loss is fixed at 10 days if the crop is still within the first 10 days of storage.
        - After that period, it is calculated as the number of days since the last degradation.
        """
        days_since_storage = (time.current_date.date() - crop.storage_time).days

        if days_since_storage <= 10:
            return max(0, min(10, (time.current_date.date() - crop.last_time_degraded).days))
        else:
            return (time.current_date.date() - crop.last_time_degraded).days

    def calculate_dry_matter_loss_to_effluent(self, estimated_maximum_effluent: float, days_of_loss: int) -> float:
        """
        Calculates the dry matter loss to effluent.

        Parameters
        ----------
        estimated_maximum_effluent : float
            The estimated maximum effluent.
        days_of_effluent_loss : int
            The number of days effluent loss will be calculated for.

        Returns
        -------
        float
            The amount of dry matter lost to effluent, in kg.

        References
        ----------
        .. [1] Feed Storage Scientific Documentation, equations FS.SIL.4, FS.SIL.6, and FS.SIL.7

        """
        return estimated_maximum_effluent * days_of_loss * DRY_MATTER_FRACTION_OF_EFFLUENT / EFFLUENT_CONSTRAINER

    def calculate_moisture_loss_to_effluent(self, estimated_maximum_effluent: float, days_of_loss: int) -> float:
        """
        Calculates the moisture loss to effluent.

        Parameters
        ----------
        estimated_maximum_effluent : float
            The estimated maximum effluent.
        days_of_effluent_loss : int
            The number of days effluent loss will be calculated for.

        Returns
        -------
        float
            The amount of moisture lost to effluent, in kg.

        References
        ----------
        .. [1] Feed Storage Scientific Documentation, equation FS.SIL.5

        """
        return estimated_maximum_effluent * days_of_loss * (1 - DRY_MATTER_FRACTION_OF_EFFLUENT) / EFFLUENT_CONSTRAINER

    def calculate_non_protein_nitrogen_after_effluent_loss(
        self, initial_non_protein_nitrogen: float, initial_crude_protein: float, loss_fraction: float
    ) -> float:
        """
        Calculates the percentage of non-protein nitrogen in a stored crop after losing dry matter to effluent.

        Parameters
        ----------
        initial_non_protein_nitrogen : float
            Percentage of non-protein nitrogen in the crop before dry matter loss occurred.
        initial_crude_protein : float
            Percentage of crude protein in the crop before dry matter loss occurred.
        loss_fraction : float
            Fraction of dry matter that was lost to effluent.

        Returns
        -------
        float
            Percentage of non-protein nitrogen remaining in the stored crop.

        References
        ----------
        .. [1] Feed Storage Scientific Documentation, equation FS.NUT.1

        """
        if loss_fraction == 0.0:
            return initial_non_protein_nitrogen

        npn_fraction = initial_non_protein_nitrogen * GeneralConstants.PERCENTAGE_TO_FRACTION
        cp_fraction = initial_crude_protein * GeneralConstants.PERCENTAGE_TO_FRACTION

        numerator = npn_fraction * cp_fraction - 0.3 * loss_fraction
        denominator = cp_fraction - 0.3 * loss_fraction

        new_npn_fraction = numerator / denominator
        new_npn_percentage = new_npn_fraction * GeneralConstants.FRACTION_TO_PERCENTAGE
        return max(0.0, new_npn_percentage)

    def calculate_crude_protein_after_effluent_loss(self, initial_crude_protein: float, loss_fraction: float) -> float:
        """
        Calculates the percentage of crude protein in a stored crop after losing dry matter to effluent.

        Parameters
        ----------
        initial_crude_protein : float
            Percentage of crude protein in the crop before dry matter loss occurred.
        loss_fraction : float
            Fraction of dry matter that was lost to effluent.

        Returns
        -------
        float
            Percentage of crude protein remaining in the stored crop.

        References
        ----------
        .. [1] Feed Storage Scientific Documentation, equation FS.NUT.1

        """
        if loss_fraction == 0.0:
            return initial_crude_protein

        new_fraction = (initial_crude_protein * GeneralConstants.PERCENTAGE_TO_FRACTION - 0.3 * loss_fraction) / (
            1 - loss_fraction
        )
        new_percentage = new_fraction * GeneralConstants.FRACTION_TO_PERCENTAGE
        return max(0.0, new_percentage)


class Bunker(Silage):
    """
    Class representing the Bunker type of Silage storage.
    """

    def __init__(self, config: dict[str, str | float | list[str]]) -> None:
        """
        Initializes a Bunker instance.
        """
        super().__init__(config)
        self.bunker_size = config["size"]


class Pile(Silage):
    """
    Class representing the Pile type of Silage storage.
    """

    def __init__(self, config: dict[str, str | float | list[str]]) -> None:
        """
        Initializes a Pile instance.
        """
        super().__init__(config)
        self.pile_size = config["size"]


class Bag(Silage):
    """
    Class representing the Bag type of Silage storage.
    """

    def __init__(self, config: dict[str, str | float | list[str]]) -> None:
        """
        Initializes a Bag instance.
        """
        super().__init__(config)
        self.bag_size = config["size"]
