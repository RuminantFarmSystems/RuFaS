from math import sqrt

from RUFAS.output_manager import OutputManager
from RUFAS.routines.field.crop.crop_enum import CropSpecies

from .tractor import Tractor
from .tractor_implement import TractorImplement
from .enums import TractorSize, FieldOperationEvent

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
        filters = [
            {
                "name": "Fertilizer",
                "use_name": True,
                "filters": ["Field._record_fertilizer_application.fertilizer_application.field='.*'"],
                "variables": ["mass", "application_depth", "field_size", "average_clay_percent"],
            },
            {
                "name": "Tillage",
                "use_name": True,
                "filters": ["TillageApplication._record_tillage.tillage_record.field='.*'"],
                "variables": ["tillage_depth", "implement", "field_size", "average_clay_percent"],
            },
            {
                "name": "Manure",
                "use_name": True,
                "filters": ["Field._record_manure_application.manure_application.field='.*'"],
                "variables": [
                    "dry_matter_mass",
                    "dry_matter_fraction",
                    "application_depth",
                    "field_size",
                    "average_clay_percent",
                ],
            },
            {
                "name": "Harvestings",
                "use_name": True,
                "filters": ["CropManagement._record_yield.harvest_yield.field='.*'"],
                "variables": ["dry_yield", "crop", "field_size"],
            },
            {
                "name": "Plantings",
                "use_name": True,
                "filters": ["Field._plant_crop.crop_planting.field='.*'"],
                "variables": ["crop", "field_size", "average_clay_percent"],
            },
        ]
        crop_yield = 0  # TODO get the correct value
        field_production_size = 0  # TODO get the correct value
        herd_size = 0  # TODO get the correct value
        operation_event = FieldOperationEvent.PLANTING  # TODO get the correct value
        crop_type = CropSpecies.ALFALFA_BALEAGE  # TODO get the correct value
        tractor_size = (
            TractorSize.SMALL
        )  # TODO get the correct value, how do we determine this? based on dataset or herdsize?
        herd_size: int = 750  # TODO get the correct value
        application_depth: float = 10  # TODO get the correct value
        clay_percent = 0  # TODO get the correct value
        tractor = Tractor(operation_event, crop_type, tractor_size, herd_size, application_depth)
        estimator = EnergyEstimator()
        diesel_consumption_tractor_implement_liter_per_ton = estimator.calculate_diesel_consumption(
            crop_yield,
            field_production_size,
            tractor,
            clay_percent,
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
        clay_percent: float,
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
        diesel_consumption_tractor_implement_liter_per_ton = 0
        for implement in tractor.implements:
            total_power_needed_kW = self._calculate_total_power_needed(
                tractor,
                implement,
                crop_yield,
                field_production_size,
                clay_percent,
            )
            x = total_power_needed_kW / tractor.power_available_kW  # helper function 411
            specific_fuel_consumption_liter_per_kWh = (
                (2.64 * x) + 3.91 - 0.203 * sqrt(738 * x + 172)
            )  # helper function 410
            tractor_implement_operation_time_hr = implement.calculate_operation_time_hr(
                field_production_size, crop_yield
            )
            diesel_consumption_tractor_implement_liter_per_ton += (
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
        implement: TractorImplement,
        crop_yield_ton_per_ha: float,
        field_production_size_ha: float,
        clay_percent: float,
    ) -> float:
        """
        Calculates the total power needed to perform the field operation by the tractor and implement where applicable.
        Implements Helper Function 412  in EEE Functions file.
        """
        tactor_axel_power = tractor.calculate_axel_power(implement)
        tractor_implement_drawbar_power = implement.calculate_drawbar_power(clay_percent)
        tractor_implement_PTO_power_needed = implement.calculate_needed_PTO(
            crop_yield_ton_per_ha, field_production_size_ha
        )
        return tactor_axel_power + tractor_implement_drawbar_power + tractor_implement_PTO_power_needed
