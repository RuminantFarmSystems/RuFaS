from datetime import date

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
from RUFAS.general_constants import GeneralConstants
from RUFAS.rufas_time import RufasTime
from RUFAS.weather import Weather

from .storage import Storage

"""
This final moisture percentage that expected to be contained in a hay crop. References Feed Storage Scientific
Documentation equation FS.HAY.3.
"""
FINAL_MOISTURE_PERCENTAGE = 12

"""Number of days after a hayed crop is stored during which it experiences increased dry matter and moisture loss."""
INITIAL_LOSS_PERIOD = 30

"""
These loss coefficients determine how much additional dry matter is lost in specific types of hayed crops.
References Feed Storage Scientific Documentation table FS.HAY.7.
"""
PROTECTED_WRAPPED_ADDITIONAL_LOSS_COEFFICIENT = 0.000_021_6
PROTECTED_TARPED_ADDITIONAL_LOSS_COEFFICIENT = 0.000_010_8
UNPROTECTED_OUTDOOR_ADDITIONAL_LOSS_COEFFICIENT = 0.000_06


class Hay(Storage):
    """
    Represents a Hay storage subclass of Storage.

    Parameters
    ----------
    config : dict[str, str | float]
        Configuration dictionary for the hay storage.

    Attributes
    ----------
    bale_size : float
        Diameter of the hay bale in meters.
    target_dry_matter : float
        The target dry matter content of hay after drying down in storage (unitless).
    additional_dry_matter_loss_coefficient : float
        Coefficient determining how much additional dry matter is lost in hayed crops (unitless).

    Methods
    -------
    calculate_protein_loss():
        Calculates the protein loss in the hay.
    """

    def __init__(self, config: dict[str, str | float | list[str]]) -> None:
        super().__init__(config)
        bale_size = config["bale_size"]
        assert isinstance(bale_size, (float, int))
        self.bale_size: float = bale_size
        target_dry_matter = config["target_dry_matter"]
        assert isinstance(target_dry_matter, (float, int))
        self.target_dry_matter: float = target_dry_matter
        additional_dry_matter_loss_coefficient = config["additional_dry_matter_loss_coefficient"]
        assert isinstance(additional_dry_matter_loss_coefficient, (float, int))
        self.additional_dry_matter_loss_coefficient: float = additional_dry_matter_loss_coefficient

    def process_degradations(self, weather: Weather, time: RufasTime) -> None:
        """
        Processes the loss of moisture in hayed crops, and calls the base class's implementation of
        `process_degradations` to process the loss of dry matter.

        Parameters
        ----------
        weather : Weather
            Weather instance containing all weather information for the simulation.
        time : RufasTime
            RufasTime instance tracking the current time of the simulation.

        References
        ----------
        Feed Storage Scientific Documentation table FS.HAY.9.

        """
        self._process_moisture_loss(time, INITIAL_LOSS_PERIOD, FINAL_MOISTURE_PERCENTAGE)

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
        moisture_loss_projected_crops = self._project_moisture_loss(
            crops, time, INITIAL_LOSS_PERIOD, FINAL_MOISTURE_PERCENTAGE
        )
        return super().project_degradations(moisture_loss_projected_crops, weather, time)

    def calculate_dry_matter_loss_to_gas(
        self, crop: HarvestedCrop, weather_conditions: list[CurrentDayConditions], time: RufasTime
    ) -> float:
        """
        Calculates the base amount of gaseous dry matter lost in a hayed crop.

        Parameters
        ----------
        crop : HarvestedCrop
            The hayed crop to process dry matter loss in.
        weather_conditions : list[CurrentDayConditions]
            List of daily weather conditions over which dry matter loss will be calculated.
        time : RufasTime
            RufasTime instance containing the time that loss should be processed up to.

        Returns
        -------
        float
            Mass of gaseous dry matter lost since from hayed crop since the last time it losses were processed for it
            (kg).

        References
        ----------
        .. [1] Feed Storage Scientific Documentation, equations FS.HAY.1, FS.HAY.2., FS.HAY.3, FS.HAY.4, FS.HAY.5,
        FS.HAY.6, FS.HAY.7

        """
        days_stored = (time.current_date.date() - crop.storage_time).days
        if days_stored == 0:
            return 0.0

        processed_initial_dry_matter_loss = self._calculate_initial_dry_matter_loss_to_gas(
            crop, crop.last_time_degraded
        )
        processed_subsequent_dry_matter_loss = self._calculate_subsequent_dry_matter_loss_to_gas(
            crop, crop.last_time_degraded
        )
        processed_loss = processed_initial_dry_matter_loss + processed_subsequent_dry_matter_loss

        current_initial_dry_matter_loss = self._calculate_initial_dry_matter_loss_to_gas(crop, time.current_date.date())
        current_subsequent_dry_matter_loss = self._calculate_subsequent_dry_matter_loss_to_gas(
            crop, time.current_date.date()
        )
        current_loss = current_initial_dry_matter_loss + current_subsequent_dry_matter_loss

        additional_loss = self._calculate_additional_dry_matter_loss(crop, weather_conditions)

        return current_loss - processed_loss + additional_loss

    def _calculate_initial_dry_matter_loss_to_gas(self, crop: HarvestedCrop, time: date) -> float:
        """
        Calculates the amount of gaseous dry matter lost in a hayed crop in its first 30 days of storage.

        Parameters
        ----------
        crop : HarvestedCrop
            The hayed crop to process dry matter loss in.
        time : date
            The date that loss should be processed up to.

        Returns
        -------
        float
            Gaseous dry matter loss from the hayed crop that occurred in the first 30 days of storage (kg).

        References
        ----------
        .. [1] Feed Storage Scientific Documentation, equation FS.HAY.3, FS.HAY.4, FS.HAY.5

        """
        days_stored = (time - crop.storage_time).days
        days_in_window = min(days_stored, INITIAL_LOSS_PERIOD)
        fraction_of_total_loss = days_in_window / INITIAL_LOSS_PERIOD

        initial_moisture_percentage = 100 - crop.initial_dry_matter_percentage

        numerator = crop.total_sensible_heat_generated + 2433 * (
            initial_moisture_percentage
            - (FINAL_MOISTURE_PERCENTAGE * crop.initial_dry_matter_percentage) / (1 - FINAL_MOISTURE_PERCENTAGE)
        )
        denominator = crop.initial_dry_matter_percentage * (
            14206 - 2433 * FINAL_MOISTURE_PERCENTAGE / (1 - FINAL_MOISTURE_PERCENTAGE)
        )

        fraction_of_initial_dry_matter_lost = numerator / denominator * fraction_of_total_loss
        return crop.initial_dry_matter_mass * fraction_of_initial_dry_matter_lost

    def _calculate_subsequent_dry_matter_loss_to_gas(self, crop: HarvestedCrop, time: date) -> float:
        """
        Calculates the amount of gaseous dry matter lost in a hayed crop after its first 30 days of storage.

        Parameters
        ----------
        crop : HarvestedCrop
            The hayed crop to process dry matter loss in.
        time : date
            The date that loss should be processed up to.

        Returns
        -------
        float
            Gaseous dry matter loss from the hayed crop that occurred after the first 30 days of storage (kg).

        References
        ----------
        .. [1] Feed Storage Scientific Documentation, equation FS.HAY.6

        """
        days_stored = (time - crop.storage_time).days
        days_past_30_day_window = max(0, days_stored - INITIAL_LOSS_PERIOD)

        return 0.0001 * days_past_30_day_window

    def _calculate_additional_dry_matter_loss(
        self, crop: HarvestedCrop, weather_conditions: list[CurrentDayConditions]
    ) -> float:
        """
        Calculates additional dry matter loss in hayed crops.

        Parameters
        ----------
        crop : HarvestedCrop
            The hayed crop to process dry matter loss in.
        weather_conditions : list[CurrentDayConditions]
            List of daily weather conditions over which additional dry matter loss will be calculated.

        Returns
        -------
        float
            Loss of dry matter that occurred over the specified period of weather conditions in kg.

        Notes
        -----
        If the additional dry matter loss coefficient is 0, the equation this method implements will always result in
        zero, so 0 is returned immediately in this case to avoid unnecessary computation.

        References
        ----------
        .. [1] Feed Storage Scienitific Documentation, equation FS.HAY.7 and Table FS.HAY.8

        """
        if self.additional_dry_matter_loss_coefficient == 0.0:
            return 0.0

        constant_factor = self.additional_dry_matter_loss_coefficient / crop.bale_density * self.bale_size**3
        conditions = [
            weather.rainfall
            * GeneralConstants.MM_TO_CM
            * max(0.0, (weather.max_air_temperature + weather.min_air_temperature) / 2)
            for weather in weather_conditions
        ]
        additional_loss = sum(conditions)
        return additional_loss * constant_factor


class ProtectedIndoors(Hay):
    """
    Represents protected indoors hay storage, a subclass of Hay.
    """

    def __init__(self, config: dict[str, str | float | list[str]]) -> None:
        super().__init__(config)


class ProtectedWrapped(Hay):
    """
    Represents protected wrapped hay storage, a subclass of Hay.
    """

    def __init__(self, config: dict[str, str | float | list[str]]) -> None:
        super().__init__(config)
        self.additional_dry_matter_loss_coefficient = PROTECTED_WRAPPED_ADDITIONAL_LOSS_COEFFICIENT


class ProtectedTarped(Hay):
    """
    Represents protected tarped hay storage, a subclass of Hay.
    """

    def __init__(self, config: dict[str, str | float | list[str]]) -> None:
        super().__init__(config)
        self.additional_dry_matter_loss_coefficient = PROTECTED_TARPED_ADDITIONAL_LOSS_COEFFICIENT


class Unprotected(Hay):
    """
    Represents unprotected hay storage, a subclass of Hay.

    Notes
    -----
    The nutrient-specific loss coefficients are listed in tables FS.HAY.10 and FS.HAY.11 of the Feed Storage
    Scientific Documentation.

    """

    def __init__(self, config: dict[str, str | float | list[str]]) -> None:
        super().__init__(config)
        self.additional_dry_matter_loss_coefficient = UNPROTECTED_OUTDOOR_ADDITIONAL_LOSS_COEFFICIENT
        self.ndf_loss_coefficient = 0.17
        self.crude_protein_loss_coefficient = 0.4
