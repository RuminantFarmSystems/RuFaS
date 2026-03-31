from typing import Any

from RUFAS.biophysical.field.crop.harvest_operations import HarvestOperation
from RUFAS.data_structures.tillage_implements import FieldOperationEvent, TractorSize
from RUFAS.input_manager import InputManager
from RUFAS.units import MeasurementUnits
from RUFAS.user_constants import UserConstants
from RUFAS.general_constants import GeneralConstants
from RUFAS.output_manager import OutputManager
from RUFAS.util import Utility

from RUFAS.EEE.tractor import Tractor
from RUFAS.EEE.tractor_implement import TractorImplement

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
        total_diesel_consumption_tractor_implement_liter_per_ha = 0
        herd_size = im.get_data("animal.herd_information.herd_num")
        for diesel_consumption_data_item in diesel_consumption_data_list:
            harvest_type: HarvestOperation | None = None
            if harvest_type_str := diesel_consumption_data_item.get("harvest_type"):
                harvest_type = HarvestOperation(harvest_type_str)
            tractor = Tractor(
                operation_event=diesel_consumption_data_item["operation_event"],
                crop_type=diesel_consumption_data_item.get("crop_type"),
                herd_size=herd_size,
                application_depth=diesel_consumption_data_item.get("application_depth"),
                tillage_implement=diesel_consumption_data_item.get("tillage_implement"),
                harvest_type=harvest_type,
            )

            diesel_consumption_tractor_implement_liter_per_ha = estimator.calculate_diesel_consumption(
                diesel_consumption_data_item.get("crop_yield", 0),
                diesel_consumption_data_item["field_production_size"],
                tractor,
                diesel_consumption_data_item.get("clay_percent", 0),
                diesel_consumption_data_item.get("mass"),
                diesel_consumption_data_item.get("dry_matter_fraction"),
            )
            estimator.report_diesel_consumption(
                diesel_consumption_data_item,
                herd_size,
                tractor.tractor_size,
                diesel_consumption_tractor_implement_liter_per_ha,
            )
            total_diesel_consumption_tractor_implement_liter_per_ha = diesel_consumption_tractor_implement_liter_per_ha
        om.add_variable(
            "total_diesel_consumption_tractor_implement",
            total_diesel_consumption_tractor_implement_liter_per_ha,
            {**base_info_map, **{"units": MeasurementUnits.LITERS_PER_HA}},
        )

    def report_diesel_consumption(
        self,
        diesel_consumption_data: dict[str, Any],
        herd_size: int,
        tractor_size: TractorSize,
        diesel_consumption_tractor_implement_liter_per_ton: float,
    ) -> None:
        """
        Reports diesel consumption data for a specific tractor-implement operation.

        Parameters
        ----------
        diesel_consumption_data : dict[str, Any]
            Diesel consumption data for the operation.
        herd_size : int
            Number of animals in the herd.
        tractor_size : TractorSize
            Size of the tractor used.
        diesel_consumption_tractor_implement_liter_per_ton : float
            Diesel consumption per ton of implement.
        """
        base_info_map = {
            "class": EnergyEstimator.__name__,
            "function": EnergyEstimator.estimate_all.__name__,
        }
        operation_event: FieldOperationEvent = diesel_consumption_data["operation_event"]
        operation_event_str: str = (
            operation_event.value if operation_event else str(diesel_consumption_data["operation_event"])
        )
        operation_date: str = f"{diesel_consumption_data['operation_year']}_{diesel_consumption_data['operation_day']}"
        field_name: str = diesel_consumption_data["field_name"]
        suffix = f"{operation_event_str}_{operation_date}_{field_name}"
        om.add_variable(
            f"tractor_size_for_{suffix}", tractor_size.value, {**base_info_map, **{"units": MeasurementUnits.UNITLESS}}
        )
        om.add_variable(
            f"operation_event_for_{suffix}",
            operation_event_str,
            {**base_info_map, **{"units": MeasurementUnits.UNITLESS}},
        )
        if operation_event in [FieldOperationEvent.HARVEST, FieldOperationEvent.PLANTING]:
            om.add_variable(
                f"crop_type_for_{suffix}",
                diesel_consumption_data.get("crop_type"),
                {**base_info_map, **{"units": MeasurementUnits.UNITLESS}},
            )
        om.add_variable(f"herd_size_for_{suffix}", herd_size, {**base_info_map, **{"units": MeasurementUnits.ANIMALS}})
        om.add_variable(
            f"field_production_size_for_{suffix}",
            diesel_consumption_data["field_production_size"],
            {**base_info_map, **{"units": MeasurementUnits.HECTARE}},
        )
        if operation_event == FieldOperationEvent.HARVEST:
            om.add_variable(
                f"crop_yield_for_{suffix}",
                diesel_consumption_data.get("crop_yield", 1),
                {**base_info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}},
            )
        if operation_event in [
            FieldOperationEvent.MANURE_APPLICATION,
            FieldOperationEvent.FERTILIZER_APPLICATION,
            FieldOperationEvent.TILLING,
        ]:
            om.add_variable(
                f"application_depth_for_{suffix}",
                diesel_consumption_data.get("application_depth"),
                {**base_info_map, **{"units": MeasurementUnits.CENTIMETERS}},
            )
        if operation_event in [FieldOperationEvent.MANURE_APPLICATION, FieldOperationEvent.FERTILIZER_APPLICATION]:
            om.add_variable(
                f"application_mass_{suffix}",
                diesel_consumption_data.get("mass"),
                {**base_info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}},
            )
        if operation_event == FieldOperationEvent.TILLING:
            om.add_variable(
                f"tillage_implement_for_{suffix}",
                (
                    diesel_consumption_data.get("tillage_implement").value
                    if diesel_consumption_data.get("tillage_implement")
                    else diesel_consumption_data.get("tillage_implement")
                ),
                {**base_info_map, **{"units": MeasurementUnits.UNITLESS}},
            )
        om.add_variable(
            f"diesel_consumption_for_{suffix}",
            diesel_consumption_tractor_implement_liter_per_ton,
            {**base_info_map, **{"units": MeasurementUnits.LITERS_PER_TON}},
        )

    def parse_inputs_for_diesel_consumption_calculation(self) -> list[dict[str, Any]]:
        """
        Parses the OutputManager variables pool for diesel consumption calculation.
        """
        crop_and_soil_filters = [
            {
                "name": FieldOperationEvent.FERTILIZER_APPLICATION,
                "use_name": True,
                "filters": ["Field._record_fertilizer_application.fertilizer_application.field='.*'"],
                "variables": [
                    "mass",
                    "application_depth",
                    "field_size",
                    "average_clay_percent",
                    "year",
                    "day",
                    "field_name",
                ],
            },
            {
                "name": FieldOperationEvent.TILLING,
                "use_name": True,
                "filters": ["TillageApplication._record_tillage.tillage_record.field='.*'"],
                "variables": [
                    "tillage_depth",
                    "implement",
                    "field_size",
                    "average_clay_percent",
                    "year",
                    "day",
                    "field_name",
                ],
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
                    "year",
                    "day",
                    "field_name",
                ],
            },
            {
                "name": FieldOperationEvent.HARVEST,
                "use_name": True,
                "filters": ["CropManagement._record_yield.harvest_yield.field='.*'"],
                "variables": [
                    "dry_yield",
                    "crop",
                    "field_size",
                    "harvest_year",
                    "harvest_day",
                    "field_name",
                    "harvest_type",
                ],
            },
            {
                "name": FieldOperationEvent.PLANTING,
                "use_name": True,
                "filters": ["Field._record_planting.crop_planting.field='.*'"],
                "variables": ["crop", "field_size", "average_clay_percent", "year", "day", "field_name"],
            },
        ]
        result: list[dict[str, Any]] = []
        eee_to_om_key_mapping = {
            FieldOperationEvent.PLANTING: {
                "crop_type": "crop",
                "clay_percent": "average_clay_percent",
                "field_production_size": "field_size",
                "operation_year": "year",
                "operation_day": "day",
                "field_name": "field_name",
            },
            FieldOperationEvent.HARVEST: {
                "crop_type": "crop",
                "crop_yield": "dry_yield",
                "field_production_size": "field_size",
                "operation_year": "harvest_year",
                "operation_day": "harvest_day",
                "field_name": "field_name",
                "harvest_type": "harvest_type",
            },
            FieldOperationEvent.MANURE_APPLICATION: {
                "mass": "dry_matter_mass",
                "dry_matter_fraction": "dry_matter_fraction",
                "application_depth": "application_depth",
                "field_production_size": "field_size",
                "clay_percent": "average_clay_percent",
                "operation_year": "year",
                "operation_day": "day",
                "field_name": "field_name",
            },
            FieldOperationEvent.TILLING: {
                "application_depth": "tillage_depth",
                "tillage_implement": "implement",
                "field_production_size": "field_size",
                "clay_percent": "average_clay_percent",
                "operation_year": "year",
                "operation_day": "day",
                "field_name": "field_name",
            },
            FieldOperationEvent.FERTILIZER_APPLICATION: {
                "mass": "mass",
                "application_depth": "application_depth",
                "field_production_size": "field_size",
                "clay_percent": "average_clay_percent",
                "operation_year": "year",
                "operation_day": "day",
                "field_name": "field_name",
            },
        }
        for filter in crop_and_soil_filters:
            filtered_pool = om.filter_variables_pool(filter)
            max_index = Utility.find_max_index_from_keys(filtered_pool)
            if max_index is None or max_index < 0:
                continue
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
        application_mass: float | None = None,
        application_dm_content: float | None = None,
    ) -> float:
        """
        General estimate of diesel fuel consumption for a given attachment type and tractor size.
        Different practices use different types of tools/implements; the equation to estimate diesel fuel consumption
        may be the same across practices, but different implements have different parameter values.

        Parameters
        ----------
        crop_yield: float
            Amount of crop yielded per hectares (metric ton/ha).
        field_production_size: float
            The filed area under production (ha).
        tractor: Tractor
            The specifications of the tractor.
        clay_percent : float
            The clay percentage of the field under production (unitless).
        application_mass : float | None = None
            The mass of a manure or fertilizer application (kg).
        application_dm_content : float | None = None
            The dry matter content of a manure or fertilizer application (kg).

        Returns
        -------
        float
            Diesel Consumption for Tractor-Implement (l/ha).
        """
        diesel_consumption_tractor_implement_liter_ha = 0.0
        for implement in tractor.implements:
            crop_yield_ton_ha = crop_yield * GeneralConstants.KILOGRAMS_TO_MEGAGRAMS
            if application_mass and application_dm_content:
                application_mass_per_ha = (
                    application_mass * GeneralConstants.KILOGRAMS_TO_MEGAGRAMS / application_dm_content
                ) / field_production_size
            else:
                application_mass_per_ha = None

            total_power_needed_kW = self._calculate_total_power_needed(
                tractor, implement, crop_yield_ton_ha, field_production_size, clay_percent, application_mass_per_ha
            )

            specific_fuel_consumption_liter_per_kWh = UserConstants.SPECIFIC_FUEL_CONSUMPTION

            tractor_implement_operation_time_hr = implement.calculate_operation_time_hr(
                field_production_size, crop_yield_ton_ha, application_mass_per_ha
            )
            diesel_consumption_tractor_implement_liter_ha += (
                specific_fuel_consumption_liter_per_kWh
                * total_power_needed_kW
                * tractor_implement_operation_time_hr
                / field_production_size
            )
        return diesel_consumption_tractor_implement_liter_ha

    def _calculate_total_power_needed(
        self,
        tractor: Tractor,
        implement: TractorImplement,
        crop_yield_ton_per_ha: float,
        field_production_size_ha: float,
        clay_percent: float,
        application_mass: float | None = None,
    ) -> float:
        """
        Calculates the total power needed to perform the field operation by the tractor and implement where applicable.
        Implements Helper Function 412 in EEE Functions file.

        Parameters
        ----------
        tractor : Tractor
            The specifications of the tractor.
        implement : TractorImplement
            The specifications of the implement.
        crop_yield_ton_per_ha : float
            Amount of crop yielded per hectares (metric ton/ha)
        field_production_size_ha : float
            The filed area under production (ha)
        clay_percent : float
            The clay percentage of the field under production (unitless).
        application_mass : float | None = None
            The mass of a manure or fertilizer application (kg).

        Returns
        -------
        float
            The total power needed for the field operation (kW)
        """
        tractor_axel_power = tractor.calculate_axel_power(implement)
        tractor_implement_drawbar_power = implement.calculate_drawbar_power(clay_percent)
        tractor_implement_PTO_power_needed = implement.calculate_needed_PTO(
            crop_yield_ton_per_ha, field_production_size_ha, application_mass
        )
        return tractor_axel_power + tractor_implement_drawbar_power + tractor_implement_PTO_power_needed
