import json
import re
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
from RUFAS.EEE.economics.digester_costs import BiogasEnergyConversion, DigesterCostCalculator

# 1 kWh equals 3.6 MJ; used to price RNG energy (reported in kWh by the conversion) against the
# natural-gas commodity price, which is expressed in dollars per megajoule.
KILOWATT_HOURS_TO_MEGAJOULES = 3.6

EEE_TO_OM_KEY_MAPPING = {
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

CROP_AND_SOIL_FILTERS: list[dict[str, Any]] = [
    {
        "name": FieldOperationEvent.FERTILIZER_APPLICATION,
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
        "filters": ["Field._record_planting.crop_planting.field='.*'"],
        "variables": ["crop", "field_size", "average_clay_percent", "year", "day", "field_name"],
    },
]

im = InputManager()
om = OutputManager()


class EnergyEstimator:
    """Estimates energy consumption for the various field operations on the farm."""

    @staticmethod
    def estimate_all() -> None:
        """
        Runs the diesel consumption estimation for all field operations and reports the per-operation and total
        results.
        """
        base_info_map = {
            "class": EnergyEstimator.__name__,
            "function": EnergyEstimator.estimate_all.__name__,
            "units": MeasurementUnits.UNITLESS,
        }
        estimator = EnergyEstimator()
        diesel_consumption_data_list = estimator.parse_inputs_for_diesel_consumption_calculation()
        total_diesel_consumption_tractor_implement_liter_per_ha: float = 0.0
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
        estimator.estimate_digester_energy_production()

    def estimate_digester_energy_production(self) -> None:
        """
        Estimates the daily electricity and renewable natural gas (RNG) generated by each anaerobic digester.

        For every digester configured under ``economic_inputs.Manure.digester``, the daily captured biogas volume
        reported by the biophysical manure module is split between an RNG stream and an electricity stream according
        to the digester's ``rng_ratio``. The split volumes are converted into delivered energy using
        :meth:`~RUFAS.EEE.economics.digester_costs.DigesterCostCalculator.estimate_biogas_electricity` and
        :meth:`~RUFAS.EEE.economics.digester_costs.DigesterCostCalculator.estimate_biogas_rng`. The per-day
        electricity (kWh) and RNG (MJ) values are reported back to the :class:`~RUFAS.output_manager.OutputManager`
        under a per-digester prefix so the economics module can aggregate them by year.
        """
        info_map = {
            "class": EnergyEstimator.__name__,
            "function": EnergyEstimator.estimate_digester_energy_production.__name__,
        }
        digesters = im.get_data("economic_inputs.Manure.digester")
        if not isinstance(digesters, list):
            return

        conversion = BiogasEnergyConversion()
        for digester in digesters:
            if not isinstance(digester, dict):
                continue
            name = digester.get("name")
            if not name:
                om.add_warning(
                    "MissingDigesterName",
                    "A digester entry in 'economic_inputs.Manure.digester' has no 'name'; "
                    "cannot join it to captured biogas outputs.",
                    info_map,
                )
                continue
            rng_ratio = digester.get("rng_ratio", 0.0)

            biogas_payload = self._get_daily_captured_biogas(name)
            if biogas_payload is None:
                om.add_warning(
                    "MissingCapturedBiogas",
                    f"No captured biogas output found for digester '{name}'; skipping energy production.",
                    info_map,
                )
                continue

            biogas_values = biogas_payload.get("values", [])
            biogas_info_maps = biogas_payload.get("info_maps", [])
            for index, captured_biogas_volume in enumerate(biogas_values):
                simulation_day = None
                if index < len(biogas_info_maps) and isinstance(biogas_info_maps[index], dict):
                    simulation_day = biogas_info_maps[index].get("simulation_day")
                electricity_kwh, rng_megajoules = self.calculate_digester_energy_production(
                    captured_biogas_volume, rng_ratio, conversion
                )
                self._report_digester_energy_production(name, electricity_kwh, rng_megajoules, simulation_day)

            with open("electricity_produced_kwh.json", "w") as f:
                electricity = om.filter_variables_pool(
                    {"filters": ["Manure\\.Digester\\.energy\\..*\\.electricity_produced_kwh"]}
                )
                json.dump(electricity, f, indent=4)
            with open("rng_produced_megajoules.json", "w") as f:
                rng = om.filter_variables_pool(
                    {"filters": ["Manure\\.Digester\\.energy\\..*\\.rng_produced_megajoules"]}
                )
                json.dump(rng, f, indent=4)

    def _get_daily_captured_biogas(self, digester_name: str) -> dict[str, Any] | None:
        """
        Retrieves the daily captured biogas volume series for a digester from the ``OutputManager``.

        Parameters
        ----------
        digester_name : str
            The name of the digester, matching the biophysical manure processor name.

        Returns
        -------
        dict[str, Any] | None
            The pool payload (with ``values`` and ``info_maps``) for the digester's ``captured_biogas_volume``, or
            ``None`` if no matching output exists.
        """
        pattern = rf"\.{re.escape(digester_name)}\.captured_biogas_volume$"
        filtered_pool = om.filter_variables_pool({"filters": [pattern]})
        if not filtered_pool:
            return None
        # A digester name is unique across processors, so at most one key is expected to match.
        return next(iter(filtered_pool.values()))

    def calculate_digester_energy_production(
        self,
        captured_biogas_volume: float,
        rng_ratio: float,
        conversion: BiogasEnergyConversion | None = None,
    ) -> tuple[float, float]:
        """
        Converts a daily captured biogas volume into electricity and RNG using the RNG/electricity split ratio.

        Parameters
        ----------
        captured_biogas_volume : float
            The volume of biogas captured by the digester on a single day (m^3).
        rng_ratio : float
            Fraction of the captured biogas routed to RNG; the remainder ``(1 - rng_ratio)`` is routed to
            electricity generation (unitless).
        conversion : BiogasEnergyConversion | None
            Conversion factors passed through to the digester cost calculator. Defaults to
            :class:`~RUFAS.EEE.economics.digester_costs.BiogasEnergyConversion`.

        Returns
        -------
        tuple[float, float]
            The electricity generated (kWh) and the RNG generated (MJ) for the day.

        Notes
        -----
        The captured biogas is split by ``rng_ratio`` into an RNG stream and a combined-heat-and-power (CHP)
        electricity stream. Each stream is converted by the shared digester-cost calculator methods. The RNG energy,
        returned in kilowatt-hours, is converted to megajoules to match the natural-gas commodity price basis.
        """
        if conversion is None:
            conversion = BiogasEnergyConversion()

        biogas_to_rng = captured_biogas_volume * rng_ratio
        biogas_to_electricity = captured_biogas_volume * (1 - rng_ratio)

        electricity_result = DigesterCostCalculator.estimate_biogas_electricity(biogas_to_electricity, conversion)
        rng_result = DigesterCostCalculator.estimate_biogas_rng(biogas_to_rng, conversion)

        electricity_kwh = electricity_result["electricity_output_kwh"]
        rng_megajoules = rng_result["rng_energy_kwh"] * KILOWATT_HOURS_TO_MEGAJOULES
        return electricity_kwh, rng_megajoules

    def _report_digester_energy_production(
        self,
        digester_name: str,
        electricity_kwh: float,
        rng_megajoules: float,
        simulation_day: int | None,
    ) -> None:
        """
        Reports a digester's daily electricity and RNG production to the ``OutputManager``.

        Parameters
        ----------
        digester_name : str
            The name of the digester.
        electricity_kwh : float
            Electricity generated on the day (kWh).
        rng_megajoules : float
            RNG generated on the day (MJ).
        simulation_day : int | None
            The simulation day the values correspond to, used to aggregate by year downstream.
        """
        base_info_map = {
            "class": EnergyEstimator.__name__,
            "function": EnergyEstimator.estimate_digester_energy_production.__name__,
            "prefix": f"Manure.Digester.energy.{digester_name}",
        }
        om.add_variable(
            "electricity_produced_kwh",
            electricity_kwh,
            {**base_info_map, "units": MeasurementUnits.KILOWATT_HOURS},
            simulation_day=simulation_day,
        )
        om.add_variable(
            "rng_produced_megajoules",
            rng_megajoules,
            {**base_info_map, "units": MeasurementUnits.MEGAJOULES},
            simulation_day=simulation_day,
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
            Diesel consumption for the tractor-implement operation (l/ton).
        """
        base_info_map = {
            "class": EnergyEstimator.__name__,
            "function": EnergyEstimator.report_diesel_consumption.__name__,
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
            tillage_implement_enum = diesel_consumption_data.get("tillage_implement")
            tillage_implement = tillage_implement_enum.value if tillage_implement_enum is not None else None
            om.add_variable(
                f"tillage_implement_for_{suffix}",
                tillage_implement,
                {**base_info_map, **{"units": MeasurementUnits.UNITLESS}},
            )
        om.add_variable(
            f"diesel_consumption_for_{suffix}",
            diesel_consumption_tractor_implement_liter_per_ton,
            {**base_info_map, **{"units": MeasurementUnits.LITERS_PER_TON}},
        )

    def parse_inputs_for_diesel_consumption_calculation(self) -> list[dict[str, Any]]:
        """
        Parses the ``OutputManager`` variables pool into diesel consumption input data.

        Returns
        -------
        list[dict[str, Any]]
            A list of event data dictionaries, one per field operation event, each mapping EEE input keys to their
            values along with the associated ``operation_event``.

        Raises
        ------
        KeyError
            If an expected variable key is missing from the filtered variables pool.
        IndexError
            If a variable's value list is shorter than expected while building the event data.
        """
        result: list[dict[str, Any]] = []

        for filter_config in CROP_AND_SOIL_FILTERS:
            filtered_pool = om.filter_variables_pool(filter_config)
            if not filtered_pool:
                continue

            event_type = filter_config["name"]
            key_mappings = EEE_TO_OM_KEY_MAPPING[event_type]
            required_suffixes = set(key_mappings.values())

            group_prefixes = Utility.find_group_prefixes_from_keys(
                data=filtered_pool,
                required_suffixes=required_suffixes,
            )
            if not group_prefixes:
                continue

            first_required_suffix = next(iter(key_mappings.values()))

            for key_prefix in group_prefixes:
                first_key = f"{key_prefix}.{first_required_suffix}"
                if first_key not in filtered_pool:
                    continue

                values = filtered_pool[first_key].get("values", [])
                length = len(values)

                for i in range(length):
                    event_data: dict[str, Any] = {}

                    for eee_key, om_key_suffix in key_mappings.items():
                        full_key = f"{key_prefix}.{om_key_suffix}"
                        if full_key not in filtered_pool:
                            raise KeyError(
                                f"Expected key '{full_key}' not found in filtered pool for "
                                f"event type '{event_type.value}'."
                            )

                        field_values = filtered_pool[full_key].get("values", [])
                        if i >= len(field_values):
                            raise IndexError(
                                f"Index {i} out of range for key '{full_key}' while building "
                                f"diesel consumption event data."
                            )

                        event_data[eee_key] = field_values[i]

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

        Parameters
        ----------
        crop_yield : float
            Amount of crop yielded per hectare (metric ton/ha).
        field_production_size : float
            The field area under production (ha).
        tractor : Tractor
            The specifications of the tractor.
        clay_percent : float
            The clay percentage of the field under production (unitless).
        application_mass : float | None, optional
            The mass of a manure or fertilizer application (kg).
        application_dm_content : float | None, optional
            The dry matter content of a manure or fertilizer application (kg).

        Returns
        -------
        float
            Diesel consumption for the tractor-implement (l/ha).

        Notes
        -----
        Different practices use different types of tools/implements; the equation to estimate diesel fuel consumption
        may be the same across practices, but different implements have different parameter values.
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

        Parameters
        ----------
        tractor : Tractor
            The specifications of the tractor.
        implement : TractorImplement
            The specifications of the implement.
        crop_yield_ton_per_ha : float
            Amount of crop yielded per hectare (metric ton/ha).
        field_production_size_ha : float
            The field area under production (ha).
        clay_percent : float
            The clay percentage of the field under production (unitless).
        application_mass : float | None, optional
            The mass of a manure or fertilizer application (kg).

        Returns
        -------
        float
            The total power needed for the field operation (kW).

        References
        ----------
        Implements Helper Function 412 in the EEE Functions file.
        """
        tractor_axel_power = tractor.calculate_axel_power(implement)
        tractor_implement_drawbar_power = implement.calculate_drawbar_power(clay_percent)
        tractor_implement_PTO_power_needed = implement.calculate_needed_PTO(
            crop_yield_ton_per_ha, field_production_size_ha, application_mass
        )
        return tractor_axel_power + tractor_implement_drawbar_power + tractor_implement_PTO_power_needed
