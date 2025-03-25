from RUFAS.time import Time
from RUFAS.weather import Weather

from RUFAS.data_structures.crop_soil_to_feed_storage_connection import CropCategory
from .storage import Storage
from RUFAS.input_manager import InputManager

"""Number of days over which baled crops dry down after storage."""
INITIAL_LOSS_PERIOD = 30


class Baleage(Storage):
    """
    Class representing Baleage storage, a subclass of Storage.

    Attributes
    ----------
    bale_density : float
        Density of the bale, calculated based on the dry matter.
    post_wilting_moisture_percentage : float
        The post-wilting moisture level that baleage will dry down to (unitless).
    acceptable_crops : list[CropCategory]
        The list of acceptable crops for this storage type.
    Methods
    -------
    calculate_protein_loss():
        Calculates the protein loss specific to Baleage storage.
    
    """

    def __init__(self, capacity: float = float("inf")):
        super().__init__(capacity)
        im = InputManager()
        self.post_wilting_moisture_percentage: float = im.get_data("feed_management.post_wilting_moisture_percentage")
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
        self._process_moisture_loss(time, INITIAL_LOSS_PERIOD, self.post_wilting_moisture_percentage)

        super().process_degradations(weather, time)

    def calculate_protein_loss(self) -> None:
        """
        Calculate the protein loss specific to Baleage storage.

        Returns
        -------
        None
        """
        pass
