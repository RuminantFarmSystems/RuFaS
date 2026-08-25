"""Special-case preprocessing for the ``Bedding requirements`` line item.

Bedding prices are annual ``dollar_per_head`` commodity tables, while the
simulation reports each pen's animal count daily. The generic pipeline cannot
express this line item because each pen's count must be paired with that pen's
own bedding price: the pen's ``bedding_name`` (a user config name such as
``"calf_straw"``) is resolved to its canonical ``bedding_type`` (``"straw"``)
and then to a price file, and each calendar year is billed as ``(average head
present that year) * (that year's dollar-per-head price)``, summed across pens
and years (issue #3088). Only pens whose animal combination is listed in the
mapping's ``billable_pen_combinations`` are billed, because the prices are per
lactating cow.
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, ClassVar

from RUFAS.general_constants import GeneralConstants
from RUFAS.units import MeasurementUnits
from RUFAS.util import Utility
from RUFAS.EEE.economics import mapping
from RUFAS.EEE.economics.fallback_values import ECONOMIC_PRICE_FALLBACK
from RUFAS.EEE.economics.special_cases.base import SpecialCaseHandler


class BeddingRequirementsHandler(SpecialCaseHandler):
    """Owner of the preprocessing for the ``Bedding requirements`` line item."""

    section: ClassVar[str] = "Animal"
    name: ClassVar[str] = "Bedding requirements"

    def _get_mapping_details(self) -> dict[str, Any]:
        """
        Returns this line item's entry from the economic mapping.

        Returns
        -------
        dict[str, Any]
            The ``Bedding requirements`` mapping entry, or an empty dict when the
            entry is absent.

        Notes
        -----
        The mapping module is read dynamically (rather than importing the
        ``ECONOMIC_MAP`` name directly) so the entry stays patchable in tests.
        """
        for entries in mapping.ECONOMIC_MAP.get(self.section, {}).values():
            if isinstance(entries, dict) and self.name in entries:
                details = entries[self.name]
                return details if isinstance(details, dict) else {}
        return {}

    def _normalize_bedding_type(self, raw: Any) -> str:
        """
        Normalizes a bedding type into a plain string.

        Parameters
        ----------
        raw : Any
            The bedding type value to normalize.

        Returns
        -------
        str
            ``raw.value`` when ``raw`` exposes a ``value`` attribute, otherwise ``raw``,
            converted to a string.

        Notes
        -----
        A bedding type may be a plain string (read directly from JSON input) or an
        enum-like object exposing a ``value`` attribute. Returning the underlying
        value as a string in both cases lets downstream lookups always compare
        against strings.

        """
        return str(getattr(raw, "value", raw))

    def _build_bedding_name_to_type(self, details: dict[str, Any]) -> dict[str, str]:
        """
        Maps each bedding config ``name`` to its canonical ``bedding_type``.

        Parameters
        ----------
        details : dict[str, Any]
            The mapping entry being processed. Only ``bedding_configs_path`` is
            used here.

        Returns
        -------
        dict[str, str]
            A mapping of each bedding config ``name`` to its ``bedding_type``.
            Empty when no bedding configs are available.

        Notes
        -----
        A pen refers to its bedding by the user-defined ``name`` field of a
        bedding config (e.g. ``"calf_straw"``), while commodity price files are
        keyed by the canonical ``bedding_type`` (e.g. ``"straw"``). This lookup
        translates the former into the latter so the correct price file can be
        selected for each pen (issue #3088).

        The bedding configs are read from the InputManager at
        ``bedding_configs_path`` (defaulting to ``"animal.bedding_configs"``)
        and are expected to be a list of dicts. A missing or non-list config blob,
        or an entry without a ``name`` and ``bedding_type``, emits a warning; the
        malformed entry is skipped.

        Examples
        --------
        Given the following ``animal.bedding_configs`` input::

            [
                {"name": "calf_straw", "bedding_type": "straw"},
                {"name": "closeup_sawdust", "bedding_type": "sawdust"},
                {"name": "lac_and_growing_sand", "bedding_type": "sand"},
                {"name": "none (no bedding)", "bedding_type": "none"},
            ]

        the returned mapping is::

            {
                "calf_straw": "straw",
                "closeup_sawdust": "sawdust",
                "lac_and_growing_sand": "sand",
                "none (no bedding)": "none",
            }

        A pen whose ``bedding_name`` is ``"calf_straw"`` therefore resolves to
        type ``"straw"``, which selects the straw ``dollar_per_head`` price file.
        A pen resolving to ``"none"`` is later treated as having no bedding cost.
        """

        info_map = {"class": self.__class__.__name__, "function": self._build_bedding_name_to_type.__name__}
        path = details.get("bedding_configs_path") or "animal.bedding_configs"
        configs = self.context.im.get_data(path)
        name_to_type: dict[str, str] = {}
        if not isinstance(configs, (list, tuple)):
            self.context.om.add_warning(
                "InvalidBeddingConfigs",
                f"Bedding configs at '{path}' are missing or not a list; no bedding names can be resolved",
                info_map,
            )
            return name_to_type
        for config in configs:
            if not isinstance(config, dict) or "name" not in config or "bedding_type" not in config:
                self.context.om.add_warning(
                    "InvalidBeddingConfigEntry",
                    f"Skipping malformed bedding config entry (missing 'name' or 'bedding_type'): {config!r}",
                    info_map,
                )
                continue
            name_to_type[str(config["name"])] = self._normalize_bedding_type(config["bedding_type"])
        return name_to_type

    def _get_simulation_start_date(self) -> datetime:
        """
        Returns the simulation start date.

        Returns
        -------
        datetime
            The calendar date of the first simulation day.

        Notes
        -----
        The start date is read from ``config.start_date`` in the ``YYYY:day_of_year``
        format (for example ``"2013:20"``) and converted to a calendar date. The
        start year, when needed, is available as ``.year`` on the returned date.

        """
        return datetime.strptime(str(self.context.im.get_data("config.start_date")), "%Y:%j")

    def _extract_output_data(self, output_data: Any) -> tuple[list[float], list[Any]]:
        """
        Extracts aligned daily values and info maps from one OutputManager entry.

        Parameters
        ----------
        output_data : Any
            The stored output data for a single reported variable.

        Returns
        -------
        tuple[list[float], list[Any]]
            The numeric daily values.
            The info map for each value, index-aligned with the values.

        Notes
        -----
        The output data is normally a mapping of the form
        ``{"values": [...], "info_maps": [...]}``, but a bare list or scalar is also
        accepted. Non-numeric values are dropped with a warning, and each retained
        value keeps its matching info map (an empty dict when none exists).

        """

        if isinstance(output_data, dict) and "values" in output_data:
            raw_values = output_data.get("values", [])
            raw_info_maps = output_data.get("info_maps", [])
        elif isinstance(output_data, (list, tuple)):
            raw_values, raw_info_maps = list(output_data), []
        else:
            raw_values, raw_info_maps = [output_data], []

        values: list[float] = []
        info_maps: list[Any] = []
        dropped_count = 0
        for index, value in enumerate(raw_values):
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                dropped_count += 1
                continue
            values.append(numeric)
            info_maps.append(raw_info_maps[index] if index < len(raw_info_maps) else {})
        if dropped_count:
            self.context.om.add_warning(
                "NonNumericOutputData",
                f"Dropped {dropped_count} non-numeric value(s) from an output data entry",
                {"class": self.__class__.__name__, "function": self._extract_output_data.__name__},
            )
        return values, info_maps

    def _collect_pen_data(self, sim_paths: list[str]) -> dict[str, dict[str, dict[str, list[Any]]]]:
        """
        Collects each pen's daily head counts from the OutputManager, grouped by scenario.

        Parameters
        ----------
        sim_paths : list[str]
            The biophysical variable-name patterns to match.

        Returns
        -------
        dict[str, dict[str, dict[str, list[Any]]]]
            A nested mapping of the form
            ``{scenario: {pen_capture: {"values": [...], "info_maps": [...]}}}``.

        Notes
        -----
        Each pattern is matched against the variables pool; the wildcard portion of a
        matched variable name (for example ``"0_CALF"``) identifies the pen. Results are
        grouped by scenario, which is ``"baseline"`` for a single run or the run's name
        in a multi-run comparison.

        Examples
        --------
        For a single run whose pool holds two pen variables, e.g.
        ``number_of_animals_in_pen_0_CALF`` and ``number_of_animals_in_pen_3_LAC_COW``,
        the returned structure looks like::

            {
                "baseline": {
                    "0_CALF": {
                        "values": [9, 9, 8],
                        "info_maps": [
                            {"units": "animals", "simulation_day": 0},
                            {"units": "animals", "simulation_day": 1},
                            {"units": "animals", "simulation_day": 2},
                        ],
                    },
                    "3_LAC_COW": {
                        "values": [88, 89, 88],
                        "info_maps": [
                            {"units": "animals", "simulation_day": 0},
                            {"units": "animals", "simulation_day": 1},
                            {"units": "animals", "simulation_day": 2},
                        ],
                    },
                }
            }

        """

        pool = getattr(self.context.om, "variables_pool", {})
        baseline_mode = True
        scenario_names: set[str] = set()
        if isinstance(pool, dict) and pool:
            baseline_mode = all(isinstance(value, dict) and "values" in value for value in pool.values())
            if not baseline_mode:
                scenario_names = {name for name, data in pool.items() if isinstance(data, dict) and data}

        pen_data: dict[str, dict[str, dict[str, list[Any]]]] = {}
        for path in sim_paths:
            capture_pattern = re.compile(path.replace(".*", "(.+?)") + "$")
            filtered_pool = self.context.om.filter_variables_pool({"filters": [path]})
            for variable_name, output_data in filtered_pool.items():
                match = capture_pattern.search(variable_name)
                if match is None:
                    continue
                groups = [group for group in match.groups() if group]
                if not groups:
                    continue
                capture = groups[0]
                if baseline_mode:
                    scenario = "baseline"
                else:
                    candidate = variable_name.split(".", 1)[0]
                    scenario = candidate if candidate in scenario_names else "baseline"
                values, info_maps = self._extract_output_data(output_data)
                bucket = pen_data.setdefault(scenario, {}).setdefault(capture, {"values": [], "info_maps": []})
                bucket["values"].extend(values)
                bucket["info_maps"].extend(info_maps)
        return pen_data

    def _group_daily_counts_by_year(
        self, values: list[float], info_maps: list[Any], start_date: datetime
    ) -> dict[int, list[float]]:
        """
        Groups a pen's daily head counts by calendar year.

        Parameters
        ----------
        values : list[float]
            The pen's daily head counts.
        info_maps : list[Any]
            The info map for each value, providing ``simulation_day``. Index-aligned
            with ``values``.
        start_date : datetime
            The calendar date of the first simulation day.

        Returns
        -------
        dict[int, list[float]]
            A mapping of each calendar year to the daily head counts recorded in that year.

        Notes
        -----
        Each value's calendar date is ``start_date`` plus its ``simulation_day`` (taken
        from the info map, or the 0-indexed position when absent). ``simulation_day`` is
        itself 0-indexed (``(current_date - start_date).days``), so no offset is applied.

        """

        counts_by_year: dict[int, list[float]] = defaultdict(list)
        for index, value in enumerate(values):
            sim_day = None
            if index < len(info_maps) and isinstance(info_maps[index], dict):
                sim_day = info_maps[index].get("simulation_day")
            if sim_day is None:
                sim_day = index
            calendar_date = start_date + timedelta(days=int(sim_day))
            counts_by_year[calendar_date.year].append(value)
        return counts_by_year

    def _get_annual_bedding_price(
        self,
        price_dict: dict[str, list[float | str]],
        year: int,
        fips: Any,
        file_key: str,
        warned_years: set[str],
        info_map: dict[str, str],
    ) -> float:
        """
        Looks up the dollar-per-head bedding price for a year at the simulation county.

        Parameters
        ----------
        price_dict : dict[str, list[float | str]]
            The loaded price table, expected as ``{"fips": [...], "<year>": [...], ...}``.
        year : int
            The calendar year to price.
        fips : Any
            The simulation's FIPS county code.
        file_key : str
            The price-file key, used in warning messages and to de-duplicate warnings.
        warned_years : set[str]
            The set of warning keys already emitted, so each warning fires only once.
        info_map : dict[str, str]
            Contextual information attached to any emitted warning.

        Returns
        -------
        float
            The dollar-per-head price for the year, or the fallback cost when unavailable.

        Notes
        -----
        The price table holds one column per year, indexed by FIPS county code. When
        the requested year has no column, the nearest available year is used. A missing
        or malformed table, an unknown county, or a missing year each emit a single
        warning and fall back to the default cost.

        """

        fallback = ECONOMIC_PRICE_FALLBACK.get("cost", 1.0)
        if not isinstance(price_dict, dict) or not isinstance(price_dict.get("fips"), list):
            warn_key = f"{file_key}:malformed"
            if warn_key not in warned_years:
                warned_years.add(warn_key)
                self.context.om.add_warning(
                    "MissingPriceData",
                    f"Bedding price data for '{file_key}' is missing or malformed; "
                    f"using fallback cost ${fallback}/head.",
                    info_map,
                )
            return fallback
        try:
            fips_idx = price_dict["fips"].index(fips)
        except ValueError:
            warn_key = f"{file_key}:fips:{fips}"
            if warn_key not in warned_years:
                warned_years.add(warn_key)
                self.context.om.add_warning(
                    "MissingPriceData",
                    f"FIPS county '{fips}' not found in bedding price file '{file_key}'; "
                    f"using fallback cost ${fallback}/head.",
                    info_map,
                )
            return fallback

        year_columns = sorted(int(key) for key in price_dict if str(key).isdigit())
        if not year_columns:
            return fallback

        use_year = year if year in year_columns else min(year_columns, key=lambda candidate: abs(candidate - year))
        if use_year != year:
            warn_key = f"{file_key}:{year}"
            if warn_key not in warned_years:
                warned_years.add(warn_key)
                self.context.om.add_warning(
                    "MissingPriceYear",
                    f"No bedding price column for year {year} in '{file_key}'; using nearest year {use_year}.",
                    info_map,
                )
        try:
            return float(price_dict[str(use_year)][fips_idx])
        except (KeyError, IndexError, TypeError, ValueError):
            return fallback

    def _get_pen_bedding_name(self, pen_entry: Any, bedding_name_keys: list[str]) -> Any:
        """
        Gets a pen entry's bedding name by following the mapping path keys.

        Parameters
        ----------
        pen_entry : Any
            One entry from the ``pen_information`` list.
        bedding_name_keys : list[str]
            The ordered keys or indices leading to the bedding name inside the
            entry, for example ``["manure_streams", "0", "bedding_name"]``.

        Returns
        -------
        Any
            The bedding name, or ``None`` if the path cannot be resolved.

        Notes
        -----
        Numeric keys index into lists and string keys index into dicts. Any missing key,
        out-of-range index, or non-indexable value stops the walk and returns ``None``.

        """

        data = pen_entry
        for key in bedding_name_keys:
            if isinstance(data, (list, tuple)):
                try:
                    index = int(key)
                except (TypeError, ValueError):
                    return None
                if not 0 <= index < len(data):
                    return None
                data = data[index]
            elif isinstance(data, dict):
                if key not in data:
                    return None
                data = data[key]
            else:
                return None
        return data

    def _build_pen_id_to_bedding_name(self, details: dict[str, Any]) -> dict[str, Any]:
        """
        Maps each pen's ``id`` to its first manure stream's ``bedding_name``.

        Parameters
        ----------
        details : dict[str, Any]
            The mapping entry being processed. Its ``input_manager`` path locates the pens.

        Returns
        -------
        dict[str, Any]
            A mapping of each pen ``id`` (as a string) to its bedding name. Empty when no
            pen list is available.

        Notes
        -----
        Pen totals are reported under the pen's ``id`` field, while the input
        ``pen_information`` is a list whose order need not match those ids. Matching on
        ``id`` (rather than list position) keeps each pen paired with its own bedding
        even when ids are reordered or non-contiguous (issue #3088). The pen list and
        the bedding-name location within each entry are derived from the mapping's
        ``input_manager`` path.

        """

        info_map = {"class": self.__class__.__name__, "function": self._build_pen_id_to_bedding_name.__name__}
        input_paths = details.get("input_manager") or []
        template = input_paths[0] if input_paths else "animal.pen_information.*.manure_streams.0.bedding_name"
        if "*" not in template:
            return {}

        prefix, _, suffix = template.partition(".*.")
        pens = self.context.im.get_data(prefix)

        pen_map: dict[str, Any] = {}
        if not isinstance(pens, (list, tuple)):
            self.context.om.add_warning(
                "InvalidPenInformation",
                f"Pen information at '{prefix}' is missing or not a list; no bedding can be billed",
                info_map,
            )
            return pen_map
        bedding_name_keys = suffix.split(".") if suffix else []
        for entry in pens:
            if isinstance(entry, dict) and "id" in entry:
                pen_map[str(entry["id"])] = self._get_pen_bedding_name(entry, bedding_name_keys)
        return pen_map

    def process(self) -> dict[str, Any]:
        """
        Computes bedding cost per pen, per year, then sums them (issue #3088).

        Returns
        -------
        dict[str, Any]
            The preprocessed line item, matching the shape produced by the generic
            pipeline (including ``line_item_values_by_scenario`` and ``flow_type``).

        Notes
        -----
        For each pen the bedding name (an input config name) is resolved to its
        canonical ``bedding_type`` and then to a price file. For each simulation year
        the cost is ``(average head present that year) * (that year's dollar-per-head
        price)``. Pens with no bedding (``bedding_type`` of ``"none"``) incur no cost.

        When the mapping declares ``billable_pen_combinations`` (e.g. ``["LAC_COW"]``,
        because the dollar-per-head prices are per lactating cow), pens of any other
        animal combination are excluded from the bill.

        The headline results are also emitted as small standalone output variables
        (``econ_bedding_total_cost``, ``econ_bedding_billed_head_years``,
        ``econ_bedding_avg_price_per_head_year``) for lightweight report filters.

        """

        info_map = {"class": self.__class__.__name__, "function": self.process.__name__}
        details = self._get_mapping_details()

        name_to_type = self._build_bedding_name_to_type(details)
        pen_id_to_bedding_name = self._build_pen_id_to_bedding_name(details)
        type_to_key = details.get("bedding_type_to_file_key") or {}
        normalized_type_to_key = {str(key).strip().lower(): value for key, value in type_to_key.items()}
        economics_files_details = details.get("economics_files")
        economics_files = economics_files_details if isinstance(economics_files_details, dict) else {}
        billable_pen_combinations = details.get("billable_pen_combinations")
        billable_combinations = (
            {str(combination).strip().upper() for combination in billable_pen_combinations}
            if billable_pen_combinations
            else None
        )

        start_date = self._get_simulation_start_date()
        fips = self.context.im.get_data("config.FIPS_county_code")

        sim_paths = [str(path) for path in details.get("biophysical_simulation") or []]
        pen_data_by_scenario = self._collect_pen_data(sim_paths)
        if not pen_data_by_scenario:
            pen_data_by_scenario = {"baseline": {}}

        price_cache: dict[str, Any] = {}
        price_data: dict[str, Any] = {}
        warned_years: set[str] = set()
        price_values: list[float] = []

        line_item_values_by_scenario: dict[str, float] = {}
        values_by_scenario: dict[str, list[float]] = {}
        aggregates_by_scenario: dict[str, float] = {}

        for scenario, pens in pen_data_by_scenario.items():
            scenario_cost = 0.0
            scenario_head_years = 0.0
            scenario_values: list[float] = []
            for capture, daily_data in pens.items():
                pen_id = capture.split("_", 1)[0]
                pen_combination = capture.split("_", 1)[1] if "_" in capture else ""

                if billable_combinations is not None and pen_combination.strip().upper() not in billable_combinations:
                    scenario_values.extend(daily_data.get("values", []))
                    continue

                bedding_name = pen_id_to_bedding_name.get(pen_id)
                if bedding_name is None:
                    self.context.om.add_warning("MissingBeddingName", f"No bedding_name for pen '{pen_id}'", info_map)
                    continue

                bedding_type = name_to_type.get(str(bedding_name))
                if bedding_type is None:
                    self.context.om.add_warning(
                        "UnknownBeddingConfig",
                        f"Bedding '{bedding_name}' (pen '{pen_id}') is not in bedding_configs; no cost applied",
                        info_map,
                    )
                    continue

                normalized_type = str(bedding_type).strip().lower()
                if not normalized_type or normalized_type == "none":
                    scenario_values.extend(daily_data.get("values", []))
                    continue

                file_key = normalized_type_to_key.get(normalized_type)
                economics_file = economics_files.get(file_key) if file_key else None
                if file_key is None or economics_file is None:
                    self.context.om.add_warning(
                        "UnmappedBeddingType",
                        f"Bedding type '{bedding_type}' (pen '{pen_id}') has no economics price file; "
                        "no cost applied",
                        info_map,
                    )
                    continue

                if file_key not in price_cache:
                    fetched = self.context.get_data_with_handling(economics_file, info_map)
                    price_cache[file_key] = fetched
                    if fetched is not None:
                        price_data[file_key] = fetched
                pen_price_dict = price_cache[file_key]
                if pen_price_dict is None:
                    self.context.om.add_warning(
                        "MissingBeddingPriceFile",
                        f"Bedding type '{bedding_type}' (pen '{pen_id}') maps to '{economics_file}' "
                        "which could not be loaded; no cost applied",
                        info_map,
                    )
                    scenario_values.extend(daily_data.get("values", []))
                    continue

                daily_values = daily_data.get("values", [])
                daily_info_maps = daily_data.get("info_maps", [])
                scenario_values.extend(daily_values)

                counts_by_year = self._group_daily_counts_by_year(daily_values, daily_info_maps, start_date)
                for year, daily in counts_by_year.items():
                    if not daily:
                        continue
                    days_in_year = (
                        GeneralConstants.LEAP_YEAR_LENGTH
                        if Utility.is_leap_year(year)
                        else GeneralConstants.YEAR_LENGTH
                    )
                    average_head = sum(daily) / days_in_year
                    price = self._get_annual_bedding_price(pen_price_dict, year, fips, file_key, warned_years, info_map)
                    price_values.append(price)
                    scenario_head_years += average_head
                    scenario_cost += average_head * price

            line_item_values_by_scenario[scenario] = scenario_cost
            values_by_scenario[scenario] = scenario_values
            aggregates_by_scenario[scenario] = scenario_head_years

        if details.get("economics_files") and not price_data:
            self.context.om.add_warning(
                "MissingEconomicsFile",
                f"No commodity pricing retrieved for '{self.name}'",
                info_map,
            )

        total_cost = sum(line_item_values_by_scenario.values())
        total_head_years = sum(aggregates_by_scenario.values())
        price_aggregate = self.context.aggregate(price_values, "average")

        self.context.om.add_variable(
            "econ_bedding_total_cost",
            total_cost,
            dict(info_map, units=MeasurementUnits.DOLLARS),
        )
        self.context.om.add_variable(
            "econ_bedding_billed_head_years",
            total_head_years,
            dict(info_map, units=MeasurementUnits.ANIMALS),
        )
        self.context.om.add_variable(
            "econ_bedding_avg_price_per_head_year",
            price_aggregate if price_aggregate is not None else 0.0,
            dict(info_map, units=MeasurementUnits.DOLLARS),
        )

        biophysical_values = [value for scenario_values in values_by_scenario.values() for value in scenario_values]
        return {
            "biophysical_values": biophysical_values,
            "biophysical_aggregate": total_head_years,
            "biophysical_values_by_scenario": values_by_scenario,
            "biophysical_aggregate_by_scenario": aggregates_by_scenario,
            "price_data": price_data,
            "price_values": price_values,
            "price_aggregate": price_aggregate,
            "line_item_values_by_scenario": line_item_values_by_scenario,
            "flow_type": "cost",
        }


__all__ = ["BeddingRequirementsHandler"]
