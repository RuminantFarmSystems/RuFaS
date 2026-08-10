"""Special-case preprocessing for the ``Seeds costs`` line item.

Seed costs cannot be derived from the generic biophysical/price pipeline: the
responsible field area must be reconstructed from each field's crop schedule,
spread across every planting-to-kill growing period, and multiplied by a
per-square-meter seed price that varies by year and FIPS county. This module
houses that logic in :class:`SeedCostHandler`.
"""

from datetime import datetime, timedelta
from typing import Any

from RUFAS.biophysical.field.manager.schedule import Schedule
from RUFAS.util import Utility
from RUFAS.EEE.economics.fallback_values import BIOPHYSICAL_FALLBACKS
from RUFAS.EEE.economics.special_cases.base import SpecialCaseHandler


class SeedCostHandler(SpecialCaseHandler):
    """Build the ``Seeds costs`` preprocessing entry from field crop schedules."""

    section = "Soil_and_crop"
    name = "Seeds costs"

    _CROP_TO_SEED_KEY: dict[str, str] = {
        "corn_grain": "commodity_prices_corn_seed_dollar_per_square_meter",
        "corn_silage": "commodity_prices_corn_seed_dollar_per_square_meter",
        "soybean_grain": "commodity_prices_soybean_seed_dollar_per_square_meter",
        "soybean_hay": "commodity_prices_soybean_seed_dollar_per_square_meter",
        "winter_wheat_grain": "commodity_prices_wheat_seed_dollar_per_square_meter",
        "winter_wheat_silage": "commodity_prices_wheat_seed_dollar_per_square_meter",
        "winter_wheat_baleage": "commodity_prices_wheat_seed_dollar_per_square_meter",
        "winter_wheat_hay": "commodity_prices_wheat_seed_dollar_per_square_meter",
        "triticale_grain": "commodity_prices_wheat_seed_dollar_per_square_meter",
        "triticale_silage": "commodity_prices_wheat_seed_dollar_per_square_meter",
        "triticale_baleage": "commodity_prices_wheat_seed_dollar_per_square_meter",
        "triticale_hay": "commodity_prices_wheat_seed_dollar_per_square_meter",
        "cereal_rye_grain": "commodity_prices_wheat_seed_dollar_per_square_meter",
        "cereal_rye_silage": "commodity_prices_wheat_seed_dollar_per_square_meter",
        "cereal_rye_baleage": "commodity_prices_wheat_seed_dollar_per_square_meter",
        "cereal_rye_hay": "commodity_prices_wheat_seed_dollar_per_square_meter",
    }

    _HA_TO_M2: float = 10_000.0

    # Harvest operations that terminate a crop's life in the field.
    _FINAL_HARVEST_OPS: frozenset[str] = frozenset({"harvest_kill", "kill_only"})

    def _growing_periods(self, schedule: dict[str, Any]) -> list[tuple[datetime, datetime]]:
        """Return (planting_date, kill_date) pairs for one crop schedule entry.

        Pairs each planting event with its corresponding final harvest
        (``harvest_kill`` or ``kill_only``).  Intermediate ``harvest_only``
        operations are ignored.  Pattern expansion (``pattern_repeat``,
        ``planting_skip``, ``harvesting_skip``) is applied before pairing.
        """
        pattern_repeat = int(schedule.get("pattern_repeat") or 0)
        planting_skip = int(schedule.get("planting_skip") or 0)
        harvesting_skip = int(schedule.get("harvesting_skip") or 0)

        raw_p_years: list[int] = list(schedule.get("planting_years") or [])
        raw_p_days: list[int] = list(schedule.get("planting_days") or [])
        raw_h_years: list[int] = list(schedule.get("harvest_years") or [])
        raw_h_days: list[int] = list(schedule.get("harvest_days") or [])
        raw_h_ops: list[str] = list(schedule.get("harvest_operations") or [])

        if not raw_p_years or not raw_h_years:
            return []

        p_years = Schedule.repeat_pattern(raw_p_years, planting_skip, pattern_repeat)
        p_days = Utility.elongate_list(raw_p_days * (pattern_repeat + 1), len(p_years))
        h_years = Schedule.repeat_pattern(raw_h_years, harvesting_skip, pattern_repeat)
        h_days = Utility.elongate_list(raw_h_days * (pattern_repeat + 1), len(h_years))
        h_ops = Utility.elongate_list(raw_h_ops * (pattern_repeat + 1), len(h_years))

        events: list[tuple[datetime, str]] = []
        for y, d in zip(p_years, p_days):
            events.append((datetime.strptime(f"{y}:{d}", "%Y:%j"), "plant"))
        for y, d, op in zip(h_years, h_days, h_ops):
            events.append((datetime.strptime(f"{y}:{d}", "%Y:%j"), op))
        events.sort(key=lambda e: e[0])

        periods: list[tuple[datetime, datetime]] = []
        plant_date: datetime | None = None
        for date, op in events:
            if op == "plant":
                plant_date = date
            elif op in self._FINAL_HARVEST_OPS and plant_date is not None:
                periods.append((plant_date, date))
                plant_date = None
        return periods

    def _preprocess_seed_costs(self) -> dict[str, list[float]]:
        """Build a daily time-series of responsible field area (m²) per seed key.

        For each field, each crop's planting-to-kill periods are located within
        the simulation window.  The field's area in m² is spread evenly over
        each growing period (``field_size_m² / period_duration``), then
        accumulated into a per-simulation-day array keyed by seed commodity.

        Returns
        -------
        dict[str, list[float]]
            Keys are seed commodity price keys; values are lists of length
            ``total_sim_days`` where each element is the total m² for that
            seed on that simulation day.
        """
        im = self.context.im
        om = self.context.om
        info_map = {"class": self.__class__.__name__, "function": "_preprocess_seed_costs"}

        try:
            start_date = datetime.strptime(str(im.get_data("config.start_date")), "%Y:%j")
            end_date = datetime.strptime(str(im.get_data("config.end_date")), "%Y:%j")
        except Exception:
            om.add_warning(
                "MissingConfigDates",
                "Could not parse simulation start/end dates for seed cost preprocessing",
                info_map,
            )
            return {}

        total_sim_days: int = (end_date - start_date).days + 1

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
            field_size_ha = field_data.get("field_size")
            if crop_spec is None or field_size_ha is None:
                continue
            try:
                field_size_m2 = float(field_size_ha) * self._HA_TO_M2
            except (TypeError, ValueError):
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
                seed_key = self._CROP_TO_SEED_KEY.get(crop_species, f"fallback_{crop_species}")

                if seed_key not in daily_area_by_seed.keys():
                    daily_area_by_seed[seed_key] = [0.0] * total_sim_days

                growing_periods = self._growing_periods(schedule)
                for plant_date, kill_date in growing_periods:
                    plant_idx = (plant_date - start_date).days
                    kill_idx = (kill_date - start_date).days

                    # Clip to simulation window.
                    clipped_start = max(plant_idx, 0)
                    clipped_end = min(kill_idx, total_sim_days)
                    if clipped_start >= clipped_end:
                        continue

                    duration = clipped_end - clipped_start
                    daily_value = field_size_m2 / duration
                    for i in range(clipped_start, clipped_end):
                        daily_area_by_seed[seed_key][i] += daily_value

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
