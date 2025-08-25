from RUFAS.biophysical.manure.storage.storage import Storage


class DailySpread(Storage):
    def __init__(
        self,
        name: str,
        cover: str,
        surface_area: float,
        capacity: float,
        storage_time_period: int = 1,
    ):
        """Initialize DailySpread object."""
        super().__init__(
            name=name,
            is_housing_emissions_calculator=False,
            cover=cover,
            storage_time_period=storage_time_period,
            surface_area=surface_area,
            capacity=capacity,
        )
