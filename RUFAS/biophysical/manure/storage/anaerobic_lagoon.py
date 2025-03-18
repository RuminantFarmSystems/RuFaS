from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover


class AnaerobicLagoon(Storage):
    """
    Anaerobic Lagoon class

    Parameters
    ----------
    name: str
        The name of the storage.
    is_housing_emissions_calculator: bool
        True if the storage is used for housing emissions calculation.
    cover: StorageCover
        The cover for the storage.
    storage_time_period: int | None
        The storage time period.
    surface_area: float
        The surface area of the storage.
    nitrous_oxide_emissions_factor: float
        The nitrous oxide emissions factor.
    capacity: float
        The capacity of the storage.

    """

    def __init__(self,
                 name: str,
                 is_housing_emissions_calculator: bool,
                 cover: StorageCover,
                 storage_time_period: int | None,
                 surface_area: float,
                 nitrous_oxide_emissions_factor: float,
                 capacity: float,
                 ):
        """Initialize Anaerobic Lagoon object."""
        super().__init__(name, is_housing_emissions_calculator, cover, storage_time_period, surface_area,
                         nitrous_oxide_emissions_factor, capacity)
