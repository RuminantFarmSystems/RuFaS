from enum import Enum
from RUFAS.output_manager import OutputManager
from math import sqrt

om = OutputManager()


class TractorSize(Enum):
    """
    Enum for Tractor Sizes.
    """

    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"


class EnergyEstimator:
    """Class to esitmate energy consumption for various operations on the farm"""

    @classmethod
    def estimate_all() -> None:
        """Runs all estimation functions and performs pre/post processing for them."""
        base_info_map = {
            "class": EnergyEstimator.__name__,
            "function": EnergyEstimator.estimate_all.__name__,
            "unit": "unitless",
        }
        crop_yield = 0  # TODO get the correct value
        field_production_size = 0  # TODO get the correct value
        estimator = EnergyEstimator()
        diesel_consumption_tractor_implement_liter_per_ton = (
            estimator.calculate_diesel_consumption(crop_yield, field_production_size)
        )
        variable_info_map = {"unit": "liter/tone"}
        om.add_variable(
            "diesel_consumption_tractor_implement",
            diesel_consumption_tractor_implement_liter_per_ton,
            {**base_info_map, **variable_info_map},
        )

    def calculate_diesel_consumption(
        self, crop_yield: float, field_production_size: float
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
            Diesel Consumption for Tractor-Implement (l/ton)
        """
        tractor_implement_specific_fuel_consumption_liter_per_kWh = (
            self._calculate_tractor_specific_fuel_consumption()
        )
        tractor_implement_total_power_needed_kW = 0  # TODO get the correct value
        tractor_implement_operation_time_hr = 0  # TODO get the correct value
        diesel_consumption_tractor_implement_liter_per_ton = (
            tractor_implement_specific_fuel_consumption_liter_per_kWh
            * tractor_implement_total_power_needed_kW
            * tractor_implement_operation_time_hr
            / field_production_size
            / crop_yield
        )
        return diesel_consumption_tractor_implement_liter_per_ton

    def _calculate_tractor_specific_fuel_consumption(self) -> float:
        """
        Calculates Specific Fuel Consumption: Specific fuel consumption in simple words measures fuel efficiency.
        It measures the fuel required per unit of power generated hence, the unit is liter/kWh.
        Corresponds to helper functions 410 and 411 in EEE Functions sheet.
        """
        tractor_total_power_needed = 0  # TODO get the correct value
        tractor_size_power_available = 0  # TODO get the correct value
        x = tractor_total_power_needed / tractor_size_power_available
        return (2.64 * x) + 3.91 - 0.203 * sqrt(738 * x + 172)
