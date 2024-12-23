from RUFAS.time import Time
from RUFAS.weather import Weather

from .enums import CropCategory
from .storage import Storage


"""Number of days over which baled crops dry down after storage."""
INITIAL_LOSS_PERIOD = 30


"""Defines the final moisture level that baleage will dry down to. TODO: make this value a user input - #2038"""
DEFAULT_FINAL_MOISTURE_PERCENTAGE = 50.0


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

    def process_degradations(self, weather: Weather, time: Time) -> None:
        """
        Processes the loss of moisture in baled crops, and calls the base class's implementation of
        `process_degradations` to process the loss of dry matter.

        Parameters
        ----------
        weather : Weather
            Weather instance containing all weather information for the simulation.
        time : Time
            Time instance tracking the current time of the simulation.

        """
        self._process_moisture_loss(time, INITIAL_LOSS_PERIOD, DEFAULT_FINAL_MOISTURE_PERCENTAGE)

        super().process_degradations(weather, time)

    def calculate_protein_loss(self) -> None:
        """
        Calculate the protein loss specific to Baleage storage.

        Returns
        -------
        None
        """
        pass
