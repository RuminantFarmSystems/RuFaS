from RUFAS.rufas_time import RufasTime
from RUFAS.weather import Weather

from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
from .storage import Storage

"""Number of days over which baled crops dry down after storage."""
INITIAL_LOSS_PERIOD = 30


class Baleage(Storage):
    """
    Class representing Baleage storage, a subclass of Storage.

    Parameters
    ----------
    config : dict[str, str | float]
        Configuration dictionary for the baleage storage.

    Attributes
    ----------
    bale_density : float
        Density of the bale, calculated based on the dry matter.
    post_wilting_moisture_percentage : float
        The post-wilting moisture level that baleage will dry down to (unitless).

    Methods
    -------
    calculate_protein_loss():
        Calculates the protein loss specific to Baleage storage.
    """

    def __init__(self, config: dict[str, str | float | list[str]]) -> None:
        super().__init__(config)
        post_wilting_moisture_percentage = config["post_wilting_moisture_percentage"]
        assert isinstance(post_wilting_moisture_percentage, (float, int))
        self.post_wilting_moisture_percentage: float = post_wilting_moisture_percentage
        bale_density = config["bale_density"]
        assert isinstance(bale_density, (float, int))
        self.bale_density: float = bale_density

    def process_degradations(self, weather: Weather, time: RufasTime) -> None:
        """
        Processes the loss of moisture in baled crops, and calls the base class's implementation of
        `process_degradations` to process the loss of dry matter.

        Parameters
        ----------
        weather : Weather
            Weather instance containing all weather information for the simulation.
        time : RufasTime
            RufasTime instance tracking the current time of the simulation.

        """
        self._process_moisture_loss(time, INITIAL_LOSS_PERIOD, self.post_wilting_moisture_percentage)

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
            crops, time, INITIAL_LOSS_PERIOD, self.post_wilting_moisture_percentage
        )
        return super().project_degradations(moisture_loss_projected_crops, weather, time)

    def calculate_protein_loss(self) -> None:
        """
        Calculate the protein loss specific to Baleage storage.

        Returns
        -------
        None
        """
        pass
