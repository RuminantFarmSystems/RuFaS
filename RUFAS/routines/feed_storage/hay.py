from .storage import Storage
from .enums import CropCategory
from .harvested_crop import HarvestedCrop
from ...current_day_conditions import CurrentDayConditions
from ...general_constants import GeneralConstants
from ...time import Time


"""
This final moisture fraction that expected to be contained in a hay crop. References Feed Storage Scientific
Documentation equation 1.2.6.
"""
FINAL_MOISTURE_FRACTION = 0.12


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

    def __init__(self, capacity: float = float("inf")) -> None:
        super().__init__(capacity)
        self.acceptable_crops = [
            CropCategory.ALFALFA,
            CropCategory.GRASS,
            CropCategory.SMALL_GRAIN,
        ]

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

    def calculate_dry_matter_loss_to_gas(
        self, crop: HarvestedCrop, weather_conditions: list[CurrentDayConditions], time: Time
    ) -> float:
        """
        Calculates the base amount of gaseous dry matter lost in a hayed crop.

        Parameters
        ----------
        crop : HarvestedCrop
            The hayed crop to process dry matter loss in.
        weather_conditions : list[CurrentDayConditions]
            List of daily weather conditions over which dry matter loss will be calculated.
        time : Time
            Time instance containing the time that loss should be processed up to.

        References
        ----------
        .. [1] Feed Storage Scientific Documentation, equations 1.2.3 and 1.2.7.

        """
        days_stored = time.simulation_day - crop.storage_time.simulation_day
        if days_stored == 0:
            return 0.0

        processed_initial_dry_matter_loss = self._calculate_initial_dry_matter_loss_to_gas(
            crop, crop.last_time_degraded
        )
        processed_subsequent_dry_matter_loss = self._calculate_subsequent_dry_matter_loss_to_gas(
            crop, crop.last_time_degraded
        )
        processed_loss = processed_initial_dry_matter_loss + processed_subsequent_dry_matter_loss

        current_initial_dry_matter_loss = self._calculate_initial_dry_matter_loss_to_gas(crop, time)
        current_subsequent_dry_matter_loss = self._calculate_subsequent_dry_matter_loss_to_gas(crop, time)
        current_loss = current_initial_dry_matter_loss + current_subsequent_dry_matter_loss

        return current_loss - processed_loss

    def _calculate_initial_dry_matter_loss_to_gas(self, crop: HarvestedCrop, time: Time) -> float:
        """
        Calculates the amount of gaseous dry matter lost in a hayed crop in its first 30 days of storage.

        Parameters
        ----------
        crop : HarvestedCrop
            The hayed crop to process dry matter loss in.
        time : Time
            Time instance containing the time that loss should be processed up to.

        Returns
        -------
        float
            Gaseous dry matter loss from the hayed crop that occurred in the first 30 days of storage in kg.

        References
        ----------
        .. [1] Feed Storage Scientific Documentation, equation 1.2.3

        """
        days_stored = time.simulation_day - crop.storage_time.simulation_day
        if days_stored == 0:
            return 0.0
        days_in_window = min(days_stored, 30)
        dry_fraction = crop.initial_dry_matter_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION
        moisture_fraction = 1 - dry_fraction
        numerator = moisture_fraction - FINAL_MOISTURE_FRACTION * dry_fraction * (1 - 0.004 * days_in_window)
        denominator = dry_fraction * (14206 - 2433 * (0.004 * days_in_window) / (1 - 0.004 * days_in_window))
        return crop.total_sensible_heat_generated + 2433 * numerator / denominator

    def _calculate_subsequent_dry_matter_loss_to_gas(self, crop: HarvestedCrop, time: Time) -> float:
        """
        Calculates the amount of gaseous dry matter lost in a hayed crop in its first 30 days of storage.

        Parameters
        ----------
        crop : HarvestedCrop
            The hayed crop to process dry matter loss in.
        time : Time
            Time instance containing the time that loss should be processed up to.

        Returns
        -------
        float
            Gaseous dry matter loss from the hayed crop that occurred after the first 30 days of storage in kg.

        References
        ----------
        .. [1] Feed Storage Scientific Documentation, equation 1.2.7

        """
        days_stored = time.simulation_day - crop.storage_time.simulation_day
        days_past_30_day_window = max(0, days_stored - 30)

        return 0.0001 * days_past_30_day_window


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
