from RUFAS.output_manager import OutputManager
from math import sqrt

from .tractor import Tractor
from .tractor_implement import TractorImplement

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
        tractor = Tractor(herd_size=herd_size)
        estimator = EnergyEstimator()
        diesel_consumption_tractor_implement_liter_per_ton = estimator.calculate_diesel_consumption(
            crop_yield, field_production_size, tractor
        )
        variable_info_map = {"unit": "liter/tone", "tractor_size": tractor.tractor_size}
        om.add_variable(
            "diesel_consumption_tractor_implement",
            diesel_consumption_tractor_implement_liter_per_ton,
            {**base_info_map, **variable_info_map},
        )

    def calculate_diesel_consumption(
        self,
        crop_yield: float,
        field_production_size: float,
        tractor: Tractor,
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
        tractor: Tractor
            The specifications of the tractor

        Returns
        -------
        float
            Diesel Consumption for Tractor-Implement (l/ton)
        """
        total_power_needed_kW = self._calculate_total_power_needed(tractor, crop_yield, field_production_size)
        x = total_power_needed_kW / tractor.power_available_kW  # helper function 411
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

    def _calculate_total_power_needed(
        self,
        tractor: Tractor,
        crop_yield_ton_per_ha: float,
        field_production_size_ha: float,
    ) -> float:
        """
        Calculates the total power needed to perform the field operation by the tractor and implement where applicable.
        Implements Helper Function 412  in EEE Functions file.
        """
        tractor_implement = TractorImplement()  # TODO get the correct value
        tactor_axel_power = tractor.calculate_axel_power(tractor_implement)
        tractor_implement_drawbar_power = tractor_implement.calculate_drawbar_power()
        tractor_implement_PTO_power_needed = tractor_implement.calculate_needed_PTO(
            crop_yield_ton_per_ha, field_production_size_ha
        )
        return tactor_axel_power + tractor_implement_drawbar_power + tractor_implement_PTO_power_needed
