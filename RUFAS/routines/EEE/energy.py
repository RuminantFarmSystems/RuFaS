from math import sqrt
from typing import Any, Dict, List

from RUFAS.output_manager import OutputManager
from RUFAS.util import Utility
from RUFAS.routines.field.crop.crop_enum import CropSpecies

from .tractor import Tractor
from .tractor_implement import TractorImplement
from .enums import TractorSize, FieldOperationEvent, TillageImplement

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
        estimator = EnergyEstimator()
        diesel_conumption_data = estimator.parse_inputs_for_diesel_consumption_calculation()
        tractor = Tractor(
            diesel_conumption_data["event_type"],
            diesel_conumption_data["crop_type"],
            diesel_conumption_data["herd_size"],  # TODO
            diesel_conumption_data["application_depth"],
        )

        diesel_consumption_tractor_implement_liter_per_ton = estimator.calculate_diesel_consumption(
            diesel_conumption_data["crop_yield"],
            diesel_conumption_data["field_production_size"],
            tractor,
            diesel_conumption_data["clay_percent"],
        )
        variable_info_map = {"unit": "liter/tone", "tractor_size": tractor.tractor_size}
        om.add_variable(
            "diesel_consumption_tractor_implement",
            diesel_consumption_tractor_implement_liter_per_ton,
            {**base_info_map, **variable_info_map},
        )

    def parse_inputs_for_diesel_consumption_calculation(self) -> List[Dict[str, Any]]:
        filters = [
            {
                "name": FieldOperationEvent.FERTILIZER_APPLICATION,
                "use_name": True,
                "filters": ["Field._record_fertilizer_application.fertilizer_application.field='.*'"],
                "variables": ["event_type", "mass", "application_depth", "field_size", "average_clay_percent"],
            },
            {
                "name": "Tillage",
                "use_name": True,
                "filters": ["TillageApplication._record_tillage.tillage_record.field='.*'"],
                "variables": ["event_type", "tillage_depth", "implement", "field_size", "average_clay_percent"],
            },
            {
                "name": FieldOperationEvent.MANURE_APPLICATION,
                "use_name": True,
                "filters": ["Field._record_manure_application.manure_application.field='.*'"],
                "variables": [
                    "event_type",
                    "dry_matter_mass",
                    "dry_matter_fraction",
                    "application_depth",
                    "field_size",
                    "average_clay_percent",
                ],
            },
            {
                "name": FieldOperationEvent.HARVEST,
                "use_name": True,
                "filters": ["CropManagement._record_yield.harvest_yield.field='.*'"],
                "variables": ["event_type", "dry_yield", "crop", "field_size"],
            },
            {
                "name": FieldOperationEvent.PLANTING,
                "use_name": True,
                "filters": ["Field._record_planting.crop_planting.field='.*'"],
                "variables": ["event_type", "crop", "field_size", "average_clay_percent"],
            },
        ]  # TODO remove event type
        result: List[Dict[str, Any]] = []
        eee_to_om_key_mapping = {
            FieldOperationEvent.PLANTING: {
                "crop_type": "crop",
                "clay_percent": "average_clay_percent",
                "field_size": "field_size",
            },
            FieldOperationEvent.HARVEST: {
                "crop_type": "crop",
                "dry_yield": "dry_yield",
                "field_size": "field_size",
            },
            FieldOperationEvent.MANURE_APPLICATION: {
                "dry_matter_mass": ".dry_matter_mass",
                "dry_matter_fraction": "dry_matter_fraction",
                "application_depth": "application_depth",
                "field_size": "field_size",
                "clay_percent": "average_clay_percent",
            },
            FieldOperationEvent.TILLING: {
                "tillage_depth": "tillage_depth",
                "implement": "implement",
                "field_size": "field_size",
                "clay_percent": "average_clay_percent",
            },
            FieldOperationEvent.FERTILIZER_APPLICATION: {
                "mass": "mass",
                "application_depth": "application_depth",
                "field_size": "field_size",
                "clay_percent": "average_clay_percent",
            },
        }
        for filter in filters:
            filtered_pool = om.filter_variables_pool_complex(filter)
            max_index = Utility.find_max_index_from_keys(filtered_pool)
            first_key_in_pool = next(iter(filtered_pool.keys()))
            for mapping_key in eee_to_om_key_mapping.keys():
                if first_key_in_pool.startswith(mapping_key.value):
                    for index in range(max_index):
                        key_prefix = f"{mapping_key}_{index}"
                        first_key_in_the_map = next(iter(eee_to_om_key_mapping[mapping_key].keys()))
                        length = len(filtered_pool[f"{key_prefix}.{first_key_in_the_map}"])
                        d = {
                            eee_to_om_key_mapping[mapping_key][k]: filtered_pool[
                                f"{key_prefix}.{eee_to_om_key_mapping[mapping_key][k]}"
                            ][i]
                            for i in range(length)
                            for k in eee_to_om_key_mapping[mapping_key].keys()
                        }
                        d["event_type"] = mapping_key
                        result.append(d)
        return result

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
