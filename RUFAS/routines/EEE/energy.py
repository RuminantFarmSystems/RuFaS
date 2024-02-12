from RUFAS.output_manager import OutputManager
from math import sqrt

from .tractor import TractorSpecs

om = OutputManager()


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
        herd_size = 0  # TODO get the correct value
        tractor_specs = TractorSpecs(herd_size=herd_size)
        estimator = EnergyEstimator()
        diesel_consumption_tractor_implement_liter_per_ton = estimator.calculate_diesel_consumption(
            crop_yield, field_production_size, tractor_specs
        )
        variable_info_map = {"unit": "liter/tone", "tractor_size": tractor_specs.tractor_size}
        om.add_variable(
            "diesel_consumption_tractor_implement",
            diesel_consumption_tractor_implement_liter_per_ton,
            {**base_info_map, **variable_info_map},
        )

    def calculate_diesel_consumption(
        self,
        crop_yield: float,
        field_production_size: float,
        tractor_specs: TractorSpecs,
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
        tractor_specs: TractorSpecs
            The specifications of the tractor

        Returns
        -------
        float
            Diesel Consumption for Tractor-Implement (l/ton)
        """
        total_power_needed_kW = self._calculate_total_power_needed()
        x = total_power_needed_kW / tractor_specs.power_available_kW  # helper function 411
        specific_fuel_consumption_liter_per_kWh = (2.64 * x) + 3.91 - 0.203 * sqrt(738 * x + 172)  # helper function 410
        tractor_implement_operation_time_hr = 0  # TODO get the correct value
        diesel_consumption_tractor_implement_liter_per_ton = (
            specific_fuel_consumption_liter_per_kWh
            * total_power_needed_kW
            * tractor_implement_operation_time_hr
            / field_production_size
            / crop_yield
        )
        return diesel_consumption_tractor_implement_liter_per_ton

    def _calculate_total_power_needed(self) -> None:  # TODO implement
        pass
