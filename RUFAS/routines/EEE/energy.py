class EnergyEstimator:
    """Class to esitmate energy consumption for various operations on the farm"""

    @classmethod
    def estimate_all() -> None:
        """Runs all estimation functions and performs pre/post processing for them."""
        crop_yield = 0  # TODO get the correct value
        field_production_size = 0  # TODO get the correct value
        diesel_consumption_tractor_implement_liter_per_ton = (
            EnergyEstimator.calculate_diesel_consumption(
                crop_yield, field_production_size
            )
        )

    @classmethod
    def calculate_diesel_consumption(
        crop_yield: float, field_production_size: float
    ) -> float:
        """
        General estimate  how diesel fuel consumption is estimated for a given attachment type and tractor size.
        Different practices use different types of tools/implements; the equation to estimate diesel fuel consumption
        may be the same across practices but different implements have different parameter values.

        Parameters
        ----------
        crop_yield: float
            Amount of crop yielded per hectars (metric ton/ha)
        field_production_size: float
            The filed area under production (ha)

        Returns
        -------
        float
            Diesel Consumption Tractor-Implement (l/ton)
        """
        pass
