from math import sqrt
from typing import Any

from RUFAS.data_structures.tillage_implements import FieldOperationEvent
from RUFAS.input_manager import InputManager
from RUFAS.units import MeasurementUnits
from RUFAS.output_manager import OutputManager
from RUFAS.util import Utility

from RUFAS.routines.EEE.tractor import Tractor
from RUFAS.routines.EEE.tractor_implement import TractorImplement

im = InputManager()
om = OutputManager()


class EnergyEstimator:
    """Class to estimate energy consumption for various operations on the farm"""

    @staticmethod
    def estimate_all() -> None:
        """Runs all estimation functions and performs pre/post processing for them."""
        base_info_map = {
            "class": EnergyEstimator.__name__,
            "function": EnergyEstimator.estimate_all.__name__,
            "units": MeasurementUnits.UNITLESS,
        }
        estimator = EnergyEstimator()
        diesel_consumption_data_list = estimator.parse_inputs_for_diesel_consumption_calculation()
        total_diesel_consumption_tractor_implement_liter_per_ton = 0
        herd_size = im.get_data("animal.herd_information.herd_num")
        for diesel_consumption_data_item in diesel_consumption_data_list:
            tractor = Tractor(
                operation_event=diesel_consumption_data_item["operation_event"],
                crop_type=diesel_consumption_data_item.get("crop_type"),
                herd_size=herd_size,
                application_depth=diesel_consumption_data_item.get("application_depth"),
                tillage_implement=diesel_consumption_data_item.get("tillage_implement"),
            )
            diesel_consumption_tractor_implement_liter_per_ton = estimator.calculate_diesel_consumption(
                diesel_consumption_data_item.get("crop_yield", 1),
                diesel_consumption_data_item["field_production_size"],
                tractor,
                diesel_consumption_data_item.get("clay_percent", 0),
            )
            variable_info_map = {
                "units": MeasurementUnits.LITERS_PER_TONS,
                "tractor_size": tractor.tractor_size.value,
                "operation_event": (
                    diesel_consumption_data_item["operation_event"].value
                    if diesel_consumption_data_item["operation_event"]
                    else diesel_consumption_data_item["operation_event"]
                ),
                "crop_type": (
                    diesel_consumption_data_item.get("crop_type")
                    if diesel_consumption_data_item.get("crop_type")
                    else diesel_consumption_data_item.get("crop_type")
                ),
                "herd_size": herd_size,
                "field_production_size": diesel_consumption_data_item["field_production_size"],
                "crop_yield": diesel_consumption_data_item.get("crop_yield", 1),
                "application_depth": diesel_consumption_data_item.get("application_depth"),
                "tillage_implement": (
                    diesel_consumption_data_item.get("tillage_implement").value
                    if diesel_consumption_data_item.get("tillage_implement")
                    else diesel_consumption_data_item.get("tillage_implement")
                ),
                "consumed_fuel": diesel_consumption_tractor_implement_liter_per_ton,
            }
            om.add_variable(
                "diesel_consumption_tractor_implement",
                diesel_consumption_tractor_implement_liter_per_ton,
                {**base_info_map, **variable_info_map},
            )
            total_diesel_consumption_tractor_implement_liter_per_ton += (
                diesel_consumption_tractor_implement_liter_per_ton
            )
        om.add_variable(
            "total_diesel_consumption_tractor_implement",
            total_diesel_consumption_tractor_implement_liter_per_ton,
            {**base_info_map, **{"units": MeasurementUnits.LITERS_PER_TONS}},
        )

    def parse_inputs_for_diesel_consumption_calculation(self) -> list[dict[str, Any]]:
        crop_and_soil_filters = [
            {
                "name": FieldOperationEvent.FERTILIZER_APPLICATION,
                "use_name": True,
                "filters": ["Field._record_fertilizer_application.fertilizer_application.field='.*'"],
                "variables": ["mass", "application_depth", "field_size", "average_clay_percent"],
            },
            {
                "name": FieldOperationEvent.TILLING,
                "use_name": True,
                "filters": ["TillageApplication._record_tillage.tillage_record.field='.*'"],
                "variables": ["tillage_depth", "implement", "field_size", "average_clay_percent"],
            },
            {
                "name": FieldOperationEvent.MANURE_APPLICATION,
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
                "name": FieldOperationEvent.HARVEST,
                "use_name": True,
                "filters": ["CropManagement._record_yield.harvest_yield.field='.*'"],
                "variables": ["dry_yield", "crop", "field_size"],
            },
            {
                "name": FieldOperationEvent.PLANTING,
                "use_name": True,
                "filters": ["Field._record_planting.crop_planting.field='.*'"],
                "variables": ["crop", "field_size", "average_clay_percent"],
            },
        ]
        result: list[dict[str, Any]] = []
        eee_to_om_key_mapping = {
            FieldOperationEvent.PLANTING: {
                "crop_type": "crop",
                "clay_percent": "average_clay_percent",
                "field_production_size": "field_size",
            },
            FieldOperationEvent.HARVEST: {
                "crop_type": "crop",
                "crop_yield": "dry_yield",
                "field_production_size": "field_size",
            },
            FieldOperationEvent.MANURE_APPLICATION: {
                "mass": "dry_matter_mass",
                "application_depth": "application_depth",
                "field_production_size": "field_size",
                "clay_percent": "average_clay_percent",
            },
            FieldOperationEvent.TILLING: {
                "application_depth": "tillage_depth",
                "tillage_implement": "implement",
                "field_production_size": "field_size",
                "clay_percent": "average_clay_percent",
            },
            FieldOperationEvent.FERTILIZER_APPLICATION: {
                "mass": "mass",
                "application_depth": "application_depth",
                "field_production_size": "field_size",
                "clay_percent": "average_clay_percent",
            },
        }
        for filter in crop_and_soil_filters:
            filtered_pool = om.filter_variables_pool(filter)
            max_index = Utility.find_max_index_from_keys(filtered_pool)
            first_key_in_pool = next(iter(filtered_pool.keys()))
            for event_type, key_mappings in eee_to_om_key_mapping.items():
                if first_key_in_pool.startswith(event_type.value):
                    for index in range(max_index + 1):
                        key_prefix = f"{event_type}_{index}"
                        _, first_om_key_in_the_map = next(iter(key_mappings.items()))
                        length = len(filtered_pool[f"{key_prefix}.{first_om_key_in_the_map}"]["values"])
                        for i in range(length):
                            event_data = {
                                eee_key: filtered_pool[f"{key_prefix}.{om_key_suffix}"]["values"][i]
                                for eee_key, om_key_suffix in key_mappings.items()
                            }
                            event_data["operation_event"] = event_type
                            result.append(event_data)
        return result

    def calculate_diesel_consumption(
        self,
        crop_yield: float,
        field_production_size: float,
        tractor: Tractor,
        clay_percent: float,
    ) -> float:
        """
        General estimate of diesel fuel consumption for a given attachment type and tractor size.
        Different practices use different types of tools/implements; the equation to estimate diesel fuel consumption
        may be the same across practices, but different implements have different parameter values.

        Parameters
        ----------
        crop_yield: float
            Amount of crop yielded per hectares (metric ton/ha)
        field_production_size: float
            The filed area under production (ha)
        tractor: Tractor
            The specifications of the tractor.
        clay_percent : float
            The clay percentage of the field under production (unitless).

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
        Implements Helper Function 412 in EEE Functions file.
        """
        tractor_axel_power = tractor.calculate_axel_power(implement)
        tractor_implement_drawbar_power = implement.calculate_drawbar_power(clay_percent)
        tractor_implement_PTO_power_needed = implement.calculate_needed_PTO(
            crop_yield_ton_per_ha, field_production_size_ha
        )
        return tractor_axel_power + tractor_implement_drawbar_power + tractor_implement_PTO_power_needed
