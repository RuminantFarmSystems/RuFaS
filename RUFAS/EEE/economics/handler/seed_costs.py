from datetime import datetime, timedelta
from typing import Any

from RUFAS.EEE.economics.mapping import CROP_TO_SEED_KEY
from RUFAS.biophysical.field.crop.harvest_operations import FINAL_HARVEST_OPERATIONS
from RUFAS.biophysical.field.manager.schedule import Schedule
from RUFAS.general_constants import GeneralConstants
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.util import Utility
from RUFAS.EEE.economics.fallback_values import BIOPHYSICAL_FALLBACKS
from RUFAS.EEE.economics.handler.base import Handler


class SeedCostHandler(Handler):
    """Build the ``Seeds costs`` preprocessing entry from field crop schedules."""
    section = "Soil_and_crop"
    name = "Seeds costs"

    def _growing_periods(self, schedule: dict[str, Any]) -> list[tuple[datetime, datetime]]:
        """
        Return (planting_date, kill_date) pairs for one crop schedule entry.

        Each planting event is paired with its corresponding final harvest
        (``harvest_kill`` or ``kill_only``); intermediate ``harvest_only``
        operations are ignored. Pattern expansion (``pattern_repeat``,
        ``planting_skip``, ``harvesting_skip``) is applied before events are
        paired. Planting and harvest events are combined, sorted by date, then
        scanned so that each planting is matched to the next final-harvest
        operation that follows it.

        Parameters
        ----------
        schedule : dict[str, Any]
            Single crop schedule entry. Recognized keys:

            ``pattern_repeat`` : int
                Number of additional times the base pattern repeats.
            ``planting_skip`` : int
                Year offset applied between successive planting repeats.
            ``harvesting_skip`` : int
                Year offset applied between successive harvest repeats.
            ``planting_years`` : list[int]
                Years of each planting event.
            ``planting_days`` : list[int]
                Days of year (1-366) of each planting event.
            ``harvest_years`` : list[int]
                Years of each harvest event.
            ``harvest_days`` : list[int]
                Days of year (1-366) of each harvest event.
            ``harvest_operations`` : list[str]
                Operation type for each harvest event (e.g. ``harvest_kill``,
                ``kill_only``, ``harvest_only``).

        Returns
        -------
        list[tuple[datetime, datetime]]
            ``(planting_date, kill_date)`` pairs, one per completed growing
            period. Returns an empty list if the schedule has no planting years
            or no harvest years.
        """
        pattern_repeat = int(schedule.get("pattern_repeat") or 0)
        planting_skip = int(schedule.get("planting_skip") or 0)
        harvesting_skip = int(schedule.get("harvesting_skip") or 0)

        raw_planting_years: list[int] = list(schedule.get("planting_years") or [])
        raw_planting_days: list[int] = list(schedule.get("planting_days") or [])
        raw_harvest_years: list[int] = list(schedule.get("harvest_years") or [])
        raw_harvest_days: list[int] = list(schedule.get("harvest_days") or [])
        raw_harvest_operations: list[str] = list(schedule.get("harvest_operations") or [])

        if not raw_planting_years or not raw_harvest_years:
            return []

        planting_years = Schedule.repeat_pattern(raw_planting_years, planting_skip, pattern_repeat)
        planting_days = Utility.elongate_list(raw_planting_days * (pattern_repeat + 1), len(planting_years))
        harvest_years = Schedule.repeat_pattern(raw_harvest_years, harvesting_skip, pattern_repeat)
        harvest_days = Utility.elongate_list(raw_harvest_days * (pattern_repeat + 1), len(harvest_years))
        harvest_operations = Utility.elongate_list(raw_harvest_operations * (pattern_repeat + 1), len(harvest_years))

        events: list[tuple[datetime, str]] = []
        for year, day in zip(planting_years, planting_days):
            events.append((datetime.strptime(f"{year}:{day}", "%Y:%j"), "plant"))
        for year, day, operation in zip(harvest_years, harvest_days, harvest_operations):
            events.append((datetime.strptime(f"{year}:{day}", "%Y:%j"), operation))
        events.sort(key=lambda e: e[0])

        periods: list[tuple[datetime, datetime]] = []
        plant_date: datetime | None = None
        for date, operation in events:
            if operation == "plant":
                plant_date = date
            elif operation in FINAL_HARVEST_OPERATIONS and plant_date is not None:
                periods.append((plant_date, date))
                plant_date = None
        return periods

    def _parse_simulation_window(self) -> tuple[datetime, int] | None:
        """
        Parse the simulation window from config.

        Returns
        -------
        tuple[datetime, int] or None
            ``(start_date, total_sim_days)`` where ``total_sim_days`` is the
            inclusive day count between the configured start and end dates.
            ``None`` if either date cannot be parsed (a warning is recorded).
        """
        im = InputManager()
        try:
            config_data = im.get_data("config")
            start_date = datetime.strptime(str(config_data["start_date"]), "%Y:%j")
            end_date = datetime.strptime(str(config_data["end_date"]), "%Y:%j")
        except Exception:
            self.context.om.add_warning(
                "MissingConfigDates",
                "Could not parse simulation start/end dates for seed cost preprocessing",
                {"class": self.__class__.__name__, "function": "_parse_simulation_window"},
            )
            return None
        return start_date, (end_date - start_date).days + 1

    def _field_area_m2(self, field_data: dict[str, Any]) -> float | None:
        """
        Convert a field's configured size to square meters.

        Parameters
        ----------
        field_data : dict[str, Any]
            Field properties entry; ``field_size`` is read in hectares.

        Returns
        -------
        float or None
            Field area in m², or ``None`` if ``field_size`` is missing or not
            numeric.
        """
        field_size_ha = field_data.get("field_size")
        if field_size_ha is None:
            return None
        try:
            return float(field_size_ha) * GeneralConstants.HECTARES_PER_SQUARE_METER
        except (TypeError, ValueError):
            return None

    def _accumulate_growing_period(
        self,
        daily_area: list[float],
        field_size_m2: float,
        plant_date: datetime,
        kill_date: datetime,
        start_date: datetime,
        total_sim_days: int,
    ) -> list[float]:
        """
        Spread one growing period's field area across the simulation days it covers.

        The growing period is clipped to the simulation window, then the field
        area is distributed evenly over the clipped days
        (``field_size_m2 / clipped_duration``) and added to ``daily_area``.
        Periods that fall entirely outside the window contribute nothing.

        Parameters
        ----------
        daily_area : list[float]
            Per-simulation-day area accumulator (length ``total_sim_days``).
        field_size_m2 : float
            Field area in m² to allocate across the period.
        plant_date, kill_date : datetime
            Planting and kill dates bounding the growing period.
        start_date : datetime
            Simulation start date (index origin for ``daily_area``).
        total_sim_days : int
            Length of ``daily_area``.

        Returns
        -------
        list[float]
            A new per-simulation-day accumulator equal to ``daily_area`` with
            this period's shares added. The input list is not modified.
        """
        updated_area = list(daily_area)

        clipped_start = max((plant_date - start_date).days, 0)
        clipped_end = min((kill_date - start_date).days, total_sim_days)
        if clipped_start >= clipped_end:
            return updated_area

        daily_value = field_size_m2 / (clipped_end - clipped_start)
        for i in range(clipped_start, clipped_end):
            updated_area[i] += daily_value
        return updated_area

    def _preprocess_seed_costs(self) -> dict[str, list[float]]:
        """
        Build a daily time-series of allocated seeded area (m²) per seed key.

        For each field, every crop's planting-to-kill growing periods are
        located within the simulation window. The field's area in m² is spread
        evenly over each period so that each day carries a share of it
        (``field_size_m² / period_duration``); a period's daily shares sum back
        to the field area. Shares are accumulated per simulation day, keyed by
        seed commodity, so overlapping fields and periods add together.

        Returns
        -------
        dict[str, list[float]]
            Keys are seed commodity price keys; values are lists of length
            ``total_sim_days`` where each element is the total allocated area
            (m²) for that seed on that simulation day.
        """
        im = InputManager()
        om = OutputManager()
        info_map = {"class": self.__class__.__name__, "function": "_preprocess_seed_costs"}

        simulation_window = self._parse_simulation_window()
        if simulation_window is None:
            return {}
        start_date, total_simulation_days = simulation_window

        try:
            field_keys = im.get_data_keys_by_properties("field_properties")
        except Exception:
            om.add_warning(
                "MissingFieldData",
                "Could not retrieve field keys for seed cost preprocessing",
                info_map,
            )
            return {}

        daily_area_by_seed: dict[str, list[float]] = {}

        for field_key in field_keys:
            field_data = im.get_data(field_key)
            if not isinstance(field_data, dict):
                continue
            crop_spec = field_data.get("crop_specification")
            field_size_m2 = self._field_area_m2(field_data)
            if crop_spec is None or field_size_m2 is None:
                continue

            crop_schedules = im.get_data(f"{crop_spec}.crop_schedules")
            if not isinstance(crop_schedules, list) or not crop_schedules:
                om.add_warning(
                    "MissingCropSchedule",
                    f"No crop schedules found for '{crop_spec}' in field '{field_key}'",
                    info_map,
                )
                continue

            for schedule in crop_schedules:
                if not isinstance(schedule, dict):
                    continue
                crop_species = schedule.get("crop_species")
                if not isinstance(crop_species, str):
                    continue
                seed_key = CROP_TO_SEED_KEY.get(crop_species, f"fallback_{crop_species}")
                daily_area = daily_area_by_seed.setdefault(seed_key, [0.0] * total_simulation_days)

                for plant_date, kill_date in self._growing_periods(schedule):
                    daily_area = self._accumulate_growing_period(
                        daily_area, field_size_m2, plant_date, kill_date, start_date, total_simulation_days
                    )
                daily_area_by_seed[seed_key] = daily_area

        return daily_area_by_seed

    def _extract_daily_seed_price(self, price_data: Any) -> list[float]:
        """Extract a per-simulation-day price series from seed pricing payloads.

        Yearly prices are resolved per commodity key (with fallback prices for
        malformed payloads or missing years), then expanded so each simulation
        day carries its year's price.

        Parameters
        ----------
        price_data : Any
            Mapping of commodity price keys to pricing payloads keyed by year
            and FIPS code.

        Returns
        -------
        list[float]
            One price per simulation day, matching the length of the daily
            area series produced by ``_preprocess_seed_costs``.
        """
        im = self.context.im
        om = self.context.om
        info_map = {"class": self.__class__.__name__, "function": self._extract_daily_seed_price.__name__}
        start_date = datetime.strptime(str(im.get_data("config.start_date")), "%Y:%j")
        end_date = datetime.strptime(str(im.get_data("config.end_date")), "%Y:%j")
        start_year: int = start_date.year
        end_year: int = end_date.year
        fips_code: int = int(im.get_data("config.FIPS_county_code"))
        days_count = (end_date - start_date).days + 1

        daily_seed_price: list[float] = []
        for key, value in price_data.items():
            fallback_prices: list[float] | None = None
            price_by_year: dict[int, float] = {}
            if "fallback" in key:
                daily_seed_price = BIOPHYSICAL_FALLBACKS["seed_cost"] * days_count
                break
            if not isinstance(value, dict) or "fips" not in value or not isinstance(value["fips"], list):
                om.add_warning(
                    "MissingPriceData",
                    f"Price data missing for key: {key}, FIPS: '{fips_code}' is not in expected format."
                    "Using fallback price.",
                    info_map,
                )
                fallback_prices = self.context.get_fallback_price(start_year, end_year, key)
                price_by_year = {start_year + i: price for i, price in enumerate(fallback_prices)}
            else:
                fips_idx = value["fips"].index(fips_code)
                for year in range(start_year, end_year + 1):
                    try:
                        price_by_year[year] = value[f"{year}"][fips_idx]
                    except (KeyError, IndexError):
                        om.add_warning(
                            "MissingPriceData",
                            f"Price data missing for year '{year}' and FIPS '{fips_code}' in '{key}'."
                            "Using fallback price.",
                            info_map,
                        )
                        if fallback_prices is None:
                            fallback_prices = self.context.get_fallback_price(start_year, end_year, key)
                        price_by_year[year] = fallback_prices[year - start_year]
            for i in range(days_count):
                daily_seed_price.append(price_by_year[(start_date + timedelta(days=i)).year])
        return daily_seed_price

    def process(self) -> dict[str, Any]:
        """Build the full preprocessing result entry for the Seeds costs line item.

        Scenario names are resolved from the OutputManager variables pool the
        same way the generic pipeline does for regular line items. Field
        schedules and sizes come from the InputManager and do not vary by
        scenario, so every scenario receives the same seed cost values.
        """

        om = self.context.om
        info_map = {"class": self.__class__.__name__, "function": "process"}

        scenario_names = self.context.scenario_names()

        biophysical_values_by_scenario: dict[str, dict[str, list[float]]] = {}
        biophysical_aggregate_by_scenario: dict[str, dict[str, float]] = {}
        line_item_values_by_scenario: dict[str, float] = {}

        for scenario_name in scenario_names:
            daily_area_by_seed = self._preprocess_seed_costs()

            biophysical_values: dict[str, list[float]] = {}
            bio_total: dict[str, float] = {}
            price_data: dict[str, list[float]] = {}
            price_values: dict[str, list[float]] = {}
            price_aggregate: dict[str, float] = {}
            total_seed_cost = 0.0
            for seed_key, daily_area in daily_area_by_seed.items():
                raw_price = self.context.get_data_with_handling(seed_key, info_map)
                if raw_price is None:
                    om.add_warning(
                        "MissingEconomicsFile",
                        f"Seed commodity pricing '{seed_key}' not found in InputManager, using fallback price.",
                        info_map,
                    )

                extracted_prices = self._extract_daily_seed_price({seed_key: raw_price})
                if not extracted_prices:
                    continue

                daily_price_per_area = [
                    seed_cost * area_m2 for seed_cost, area_m2 in zip(extracted_prices, daily_area)
                ]
                biophysical_values[seed_key] = daily_area_by_seed[seed_key]
                price_values[seed_key] = extracted_prices
                bio_total[seed_key] = sum(biophysical_values[seed_key])
                price_data[seed_key] = raw_price
                price_aggregate[seed_key] = self.context.aggregate(extracted_prices, "average")
                total_seed_cost += sum(daily_price_per_area)

            biophysical_values_by_scenario[scenario_name] = biophysical_values
            biophysical_aggregate_by_scenario[scenario_name] = bio_total
            line_item_values_by_scenario[scenario_name] = total_seed_cost

            if not daily_area_by_seed:
                om.add_warning(
                    "MissingBiophysicalData",
                    "No field data found for seed cost preprocessing",
                    info_map,
                )

        return {
            "biophysical_values": biophysical_values,
            "biophysical_aggregate": bio_total,
            "biophysical_values_by_scenario": biophysical_values_by_scenario,
            "biophysical_aggregate_by_scenario": biophysical_aggregate_by_scenario,
            "price_data": price_data,
            "price_values": price_values,
            "price_aggregate": price_aggregate,
            "line_item_values_by_scenario": line_item_values_by_scenario,
            "flow_type": "cost",
        }


__all__ = ["SeedCostHandler"]
