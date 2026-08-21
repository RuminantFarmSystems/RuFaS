import pytest
import re

from RUFAS.EEE.economics import mapping as economics_mapping
from RUFAS.EEE.economics import preprocessing


class DummyOutputManager:
    def __init__(self, pool):
        self._pool = pool
        self.warnings = []
        self.logs = []
        self.added_variables = []

    def _get_flat_variables_pool(self):
        return self._pool

    def filter_variables_pool(self, filter_content):
        filters = filter_content.get("filters", [])
        if not filters:
            return {}
        pattern = re.compile(filters[0])
        return {name: data for name, data in self._pool.items() if pattern.search(name)}

    def add_warning(self, code, message, info):
        self.warnings.append((code, message, info))

    def add_log(self, title, message, info):
        self.logs.append((title, message, info))

    def add_variable(self, variable_name, value, info_map=None, **kwargs):
        self.added_variables.append((variable_name, value))


class DummyInputManager:
    def __init__(self, data):
        self._data = {
            "config.start_date": "2020:01:01",
            "config.end_date": "2020:12:31",
            "config.FIPS_county_code": 1001,
            "_default_values": {"commodity": [], "2020": []},
            "_default_fallback_values": {"commodity": [], "2020": []},
            **data,
        }
        self.added_runtime = []

    def get_data(self, key):
        return self._data.get(key)

    def add_runtime_variable_to_pool(
        self, variable_name, data, properties_blob_key, eager_termination=False, input_path=None
    ):
        self.added_runtime.append(
            {
                "variable_name": variable_name,
                "data": data,
                "properties_blob_key": properties_blob_key,
                "eager_termination": eager_termination,
                "input_path": input_path,
            }
        )
        return True


def test_preprocess_collects_values_and_prices(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_im = DummyInputManager({"price.csv": {"cost": 10}})
    dummy_om = DummyOutputManager({"Economic_inputs.Animal.labor": {"values": [1, 2, 3]}})

    monkeypatch.setattr(preprocessing, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(preprocessing, "OutputManager", lambda: dummy_om)
    monkeypatch.setattr(
        preprocessing,
        "ECONOMIC_MAP",
        {
            "Section": {
                "Category": {
                    "Item": {
                        "biophysical_simulation": ["Economic_inputs.Animal.labor"],
                        "economics_files": ["price.csv"],
                    }
                }
            }
        },
    )

    preprocessor = preprocessing.EconomicPreprocessor()
    results = preprocessor.preprocess()

    item = results["Section"]["Category"]["Item"]
    assert item["biophysical_values"] == [1.0, 2.0, 3.0]
    assert item["biophysical_aggregate"] == 6.0
    assert item["price_data"] == {"price.csv": {"cost": 10}}
    assert item["line_item_values_by_scenario"] == {"baseline": 6.0}
    assert dummy_im.added_runtime[-1]["variable_name"] == "economic_preprocessed"
    assert dummy_im.added_runtime[-1]["properties_blob_key"] == "economic_preprocessing_properties"
    warning_codes = [code for code, _, _ in dummy_om.warnings]
    assert "MissingPriceData" in warning_codes
    assert dummy_om.logs[-1][0] == "Economic preprocessing"


def test_preprocess_selects_price_by_selector(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_im = DummyInputManager(
        {
            "selector": "Premium",
            "price_premium": {"cost": 25},
            "price_standard": {"cost": 5},
        }
    )
    dummy_om = DummyOutputManager({"Economic_inputs.Feed.energy": [2, 3]})

    monkeypatch.setattr(preprocessing, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(preprocessing, "OutputManager", lambda: dummy_om)
    monkeypatch.setattr(
        preprocessing,
        "ECONOMIC_MAP",
        {
            "Section": {
                "Category": {
                    "Energy": {
                        "biophysical_simulation": ["Economic_inputs.Feed.energy"],
                        "economics_files": {
                            "input_manager_location": "selector",
                            "premium": "price_premium",
                            "standard": "price_standard",
                        },
                        "preprocessing": "average",
                    }
                }
            }
        },
    )

    preprocessor = preprocessing.EconomicPreprocessor()
    results = preprocessor.preprocess()

    energy_data = results["Section"]["Category"]["Energy"]
    assert energy_data["biophysical_values"] == [2.0, 3.0]
    assert energy_data["biophysical_aggregate"] == pytest.approx(2.5)
    assert energy_data["biophysical_values_by_scenario"] == {"baseline": [2.0, 3.0]}
    assert energy_data["biophysical_aggregate_by_scenario"] == {"baseline": pytest.approx(2.5)}
    assert energy_data["price_data"] == {"price_premium": {"cost": 25}}
    assert energy_data["price_values"] == [1.0]
    assert energy_data["price_aggregate"] == 1.0
    assert energy_data["line_item_values_by_scenario"] == {"baseline": pytest.approx(2.5)}
    assert energy_data["flow_type"] == "cost"
    warning_codes = [code for code, _, _ in dummy_om.warnings]
    assert "MissingPriceData" in warning_codes


def test_preprocess_reads_input_manager_values(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_im = DummyInputManager({"economic_inputs.Animal.labor_hours_per_day": 4})
    dummy_om = DummyOutputManager({})

    monkeypatch.setattr(preprocessing, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(preprocessing, "OutputManager", lambda: dummy_om)
    monkeypatch.setattr(
        preprocessing,
        "ECONOMIC_MAP",
        {
            "Section": {
                "Category": {
                    "Item": {
                        "input_manager": ["economic_inputs.Animal.labor_hours_per_day"],
                    }
                }
            }
        },
    )

    preprocessor = preprocessing.EconomicPreprocessor()
    results = preprocessor.preprocess()

    item = results["Section"]["Category"]["Item"]
    assert item["biophysical_values"] == [4.0]
    assert item["biophysical_aggregate"] == 4.0
    assert item["biophysical_values_by_scenario"] == {"baseline": [4.0]}
    assert item["biophysical_aggregate_by_scenario"] == {"baseline": 4.0}
    assert item["price_values"] == []
    assert item["price_aggregate"] == 1.0
    assert item["flow_type"] == "cost"
    assert item["line_item_values_by_scenario"] == {"baseline": 4.0}


def test_preprocess_handles_invalid_economics_path(monkeypatch: pytest.MonkeyPatch) -> None:
    class RaisingInputManager(DummyInputManager):
        def get_data(self, key):  # type: ignore[override]
            if key == "commodity_prices..broken_path.csv":
                raise ValueError("invalid literal for int() with base 10: ''")
            return super().get_data(key)

    dummy_im = RaisingInputManager({})
    dummy_om = DummyOutputManager({"Economic_inputs.Misc.value": [1]})

    monkeypatch.setattr(preprocessing, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(preprocessing, "OutputManager", lambda: dummy_om)
    monkeypatch.setattr(
        preprocessing,
        "ECONOMIC_MAP",
        {
            "Section": {
                "Category": {
                    "Item": {
                        "biophysical_simulation": ["Economic_inputs.Misc.value"],
                        "economics_files": ["commodity_prices..broken_path.csv"],
                    }
                }
            }
        },
    )

    preprocessor = preprocessing.EconomicPreprocessor()
    preprocessor.preprocess()

    warning_codes = [code for code, _, _ in dummy_om.warnings]
    assert "InvalidEconomicsFilePath" in warning_codes


def test_preprocess_skips_pool_check_on_wildcard_path(monkeypatch: pytest.MonkeyPatch) -> None:
    class CheckingInputManager(DummyInputManager):
        def check_property_exists_in_pool(self, key):  # type: ignore[override]
            if "*" in str(key):
                raise ValueError("invalid literal for int() with base 10: '*'")
            return key in self._data

    dummy_im = CheckingInputManager({})
    dummy_om = DummyOutputManager({"Economic_inputs.Misc.value": [1]})

    monkeypatch.setattr(preprocessing, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(preprocessing, "OutputManager", lambda: dummy_om)
    monkeypatch.setattr(
        preprocessing,
        "ECONOMIC_MAP",
        {
            "Section": {
                "Category": {
                    "Seeds": {
                        "biophysical_simulation": ["Economic_inputs.Misc.value"],
                        "economics_files": ["commodity_prices.*.dollar_per_square_meter.csv"],
                    }
                }
            }
        },
    )

    preprocessor = preprocessing.EconomicPreprocessor()
    preprocessor.preprocess()

    warning_codes = [code for code, _, _ in dummy_om.warnings]
    assert "MissingEconomicsFile" in warning_codes


def test_preprocess_skips_input_manager_on_wildcard_path(monkeypatch: pytest.MonkeyPatch) -> None:
    called_keys = []

    class TrackingInputManager(DummyInputManager):
        def get_data(self, key):  # type: ignore[override]
            called_keys.append(key)
            if "*" in str(key):
                raise AssertionError("Wildcard path should be skipped")
            return super().get_data(key)

        def check_property_exists_in_pool(self, key):  # type: ignore[override]
            called_keys.append(f"check:{key}")
            if "*" in str(key):
                raise AssertionError("Wildcard path should not reach pool check")
            return key in self._data

    dummy_im = TrackingInputManager({})
    dummy_om = DummyOutputManager({"Economic_inputs.Misc.value": [1]})

    monkeypatch.setattr(preprocessing, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(preprocessing, "OutputManager", lambda: dummy_om)
    monkeypatch.setattr(
        preprocessing,
        "ECONOMIC_MAP",
        {
            "Section": {
                "Category": {
                    "Seeds": {
                        "biophysical_simulation": ["Economic_inputs.Misc.value"],
                        "economics_files": ["commodity_prices.*.dollar_per_square_meter.csv"],
                    }
                }
            }
        },
    )

    preprocessor = preprocessing.EconomicPreprocessor()
    preprocessor.preprocess()

    assert not any("*" in str(key) for key in called_keys)
    warning_codes = [code for code, _, _ in dummy_om.warnings]
    assert "MissingEconomicsFile" in warning_codes


def test_preprocess_expands_input_wildcard_from_biophysical_regex(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_im = DummyInputManager(
        {
            "economic_inputs.feed.1.cost": 10,
            "economic_inputs.feed.2.cost": 20,
            "economic_inputs.feed.3.cost": 30,
        }
    )
    dummy_om = DummyOutputManager(
        {
            "FeedManager.purchase_feed.ration_interval_1_cost": {"values": [100]},
            "FeedManager.purchase_feed.ration_interval_2_cost": {"values": [200]},
            "FeedManager.purchase_feed.ration_interval_3_cost": {"values": [300]},
        }
    )

    monkeypatch.setattr(preprocessing, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(preprocessing, "OutputManager", lambda: dummy_om)
    monkeypatch.setattr(
        preprocessing,
        "ECONOMIC_MAP",
        {
            "Section": {
                "Category": {
                    "Item": {
                        "biophysical_simulation": ["FeedManager.purchase_feed.ration_interval_.*_cost"],
                        "input_manager": ["economic_inputs.feed.*.cost"],
                    }
                }
            }
        },
    )

    preprocessor = preprocessing.EconomicPreprocessor()
    results = preprocessor.preprocess()

    item = results["Section"]["Category"]["Item"]
    assert item["biophysical_values"] == [100.0, 200.0, 300.0]
    assert item["biophysical_aggregate"] == 600.0


def test_preprocess_warns_when_input_wildcard_cannot_expand(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_im = DummyInputManager({})
    dummy_om = DummyOutputManager({"Economic_inputs.Misc.value": [1]})

    monkeypatch.setattr(preprocessing, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(preprocessing, "OutputManager", lambda: dummy_om)
    monkeypatch.setattr(
        preprocessing,
        "ECONOMIC_MAP",
        {
            "Section": {
                "Category": {
                    "Item": {
                        "biophysical_simulation": ["Economic_inputs.Misc.value"],
                        "input_manager": ["economic_inputs.feed.*.cost"],
                    }
                }
            }
        },
    )

    preprocessor = preprocessing.EconomicPreprocessor()
    preprocessor.preprocess()

    warning_codes = [code for code, _, _ in dummy_om.warnings]
    assert "MissingEconomicInputWildcard" in warning_codes


def test_preprocess_exact_price_match_from_input_manager_values(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_im = DummyInputManager(
        {
            "economic_inputs.feed_names": ["x", "y"],
            "price_x": {"cost": 11},
            "price_y": {"cost": 22},
        }
    )
    dummy_om = DummyOutputManager({})
    monkeypatch.setattr(preprocessing, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(preprocessing, "OutputManager", lambda: dummy_om)
    monkeypatch.setattr(
        preprocessing,
        "ECONOMIC_MAP",
        {
            "Section": {
                "Category": {
                    "Item": {
                        "input_manager": ["economic_inputs.feed_names"],
                        "match_source": "input_manager",
                        "economics_files": {
                            "x": "price_x",
                            "y": "price_y",
                            "z": "price_z",
                        },
                    }
                }
            }
        },
    )
    preprocessor = preprocessing.EconomicPreprocessor()
    results = preprocessor.preprocess()
    price_data = results["Section"]["Category"]["Item"]["price_data"]
    assert set(price_data.keys()) == {"x", "y"}


def test_preprocess_exact_price_match_from_biophysical_wildcards(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_im = DummyInputManager({"price_1": {"cost": 9}, "price_2": {"cost": 10}})
    dummy_om = DummyOutputManager(
        {
            "FeedManager.purchase_feed.ration_interval_1_cost": {"values": [5]},
            "FeedManager.purchase_feed.ration_interval_2_cost": {"values": [7]},
        }
    )
    monkeypatch.setattr(preprocessing, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(preprocessing, "OutputManager", lambda: dummy_om)
    monkeypatch.setattr(
        preprocessing,
        "ECONOMIC_MAP",
        {
            "Section": {
                "Category": {
                    "Item": {
                        "biophysical_simulation": ["FeedManager.purchase_feed.ration_interval_.*_cost"],
                        "match_source": "biophysical_simulation",
                        "economics_files": {
                            "1": "price_1",
                            "2": "price_2",
                            "3": "price_3",
                        },
                    }
                }
            }
        },
    )
    preprocessor = preprocessing.EconomicPreprocessor()
    results = preprocessor.preprocess()
    price_data = results["Section"]["Category"]["Item"]["price_data"]
    assert set(price_data.keys()) == {"1", "2"}


def test_preprocess_bedding_mapping_style_wildcard_input_price_match(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_im = DummyInputManager(
        {
            "animal.pen_information.1.manure_streams.0.bedding_name": "sand",
            "animal.pen_information.2.manure_streams.0.bedding_name": "straw",
            "sand_price": {"cost": 3},
            "straw_price": {"cost": 4},
        }
    )
    dummy_om = DummyOutputManager(
        {
            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_1": {"values": [10]},
            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_2": {"values": [20]},
        }
    )
    monkeypatch.setattr(preprocessing, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(preprocessing, "OutputManager", lambda: dummy_om)
    monkeypatch.setattr(
        preprocessing,
        "ECONOMIC_MAP",
        {
            "Section": {
                "Category": {
                    "Bedding requirements": {
                        "biophysical_simulation": [
                            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_.*"
                        ],
                        "input_manager": ["animal.pen_information.*.manure_streams.0.bedding_name"],
                        "preprocessing": "average number of animals in each pen",
                        "match_source": "input_manager",
                        "economics_files": {
                            "sand": "sand_price",
                            "straw": "straw_price",
                            "sawdust": "sawdust_price",
                        },
                    }
                }
            }
        },
    )
    preprocessor = preprocessing.EconomicPreprocessor()
    results = preprocessor.preprocess()
    assert results["Section"]["Category"]["Bedding requirements"]["biophysical_aggregate"] == 15.0
    price_data = results["Section"]["Category"]["Bedding requirements"]["price_data"]
    assert set(price_data.keys()) == {"sand", "straw"}


def test_collect_biophysical_wildcards_does_not_return_empty_groups(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_im = DummyInputManager({})
    dummy_om = DummyOutputManager(
        {
            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_1": {"values": [1]},
            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_2": {"values": [1]},
        }
    )
    monkeypatch.setattr(preprocessing, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(preprocessing, "OutputManager", lambda: dummy_om)
    preprocessor = preprocessing.EconomicPreprocessor()
    captures = preprocessor._collect_biophysical_wildcards(
        ["AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_.*"]
    )
    assert captures == [("1",), ("2",)]


def test_preprocess_expands_input_wildcard_with_value_map(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_im = DummyInputManager(
        {
            "economic_inputs.feed.A.cost": 5,
            "economic_inputs.feed.B.cost": 6,
            "economic_inputs.feed.C.cost": 7,
        }
    )
    dummy_om = DummyOutputManager(
        {
            "FeedManager.purchase_feed.ration_interval_X_cost": {"values": [1]},
            "FeedManager.purchase_feed.ration_interval_Y_cost": {"values": [1]},
            "FeedManager.purchase_feed.ration_interval_Z_cost": {"values": [1]},
        }
    )
    monkeypatch.setattr(preprocessing, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(preprocessing, "OutputManager", lambda: dummy_om)
    monkeypatch.setattr(
        preprocessing,
        "ECONOMIC_MAP",
        {
            "Section": {
                "Category": {
                    "Item": {
                        "biophysical_simulation": ["FeedManager.purchase_feed.ration_interval_.*_cost"],
                        "input_manager": ["economic_inputs.feed.*.cost"],
                        "wildcard_value_map": {"X": "A", "Y": "B", "Z": "C"},
                    }
                }
            }
        },
    )
    preprocessor = preprocessing.EconomicPreprocessor()
    values, _ = preprocessor._fetch_input_values(
        ["economic_inputs.feed.*.cost"],
        [("X",), ("Y",), ("Z",)],
        {"X": "A", "Y": "B", "Z": "C"},
    )
    assert values == [5.0, 6.0, 7.0]


def _daily(head_per_day: int, days: int, start_day: int = 0) -> dict:
    """Build a pen daily-head payload with one ``simulation_day`` per value."""

    return {
        "values": [head_per_day] * days,
        "info_maps": [{"simulation_day": day} for day in range(start_day, start_day + days)],
    }


def _pen(pen_id: int, bedding_name: str) -> dict:
    """Build a ``pen_information`` entry referencing a bedding config by name."""

    return {"id": pen_id, "manure_streams": [{"bedding_name": bedding_name}]}


def _run_bedding(
    monkeypatch: pytest.MonkeyPatch,
    im_data: dict,
    pool: dict,
    *,
    pens: list,
    type_to_key: dict,
    economics_files: dict,
    configs_path: str = "animal.bedding_configs",
    billable_pen_combinations: list | None = None,
):
    """Run the bedding special-case handler and return its result item + OM.

    ``pens`` is injected as the real ``animal.pen_information`` list so the
    processor resolves bedding by each pen's ``id`` field (not list position).
    """

    dummy_im = DummyInputManager({**im_data, "animal.pen_information": pens})
    dummy_om = DummyOutputManager(pool)
    monkeypatch.setattr(preprocessing, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(preprocessing, "OutputManager", lambda: dummy_om)
    bedding_entry = {
        "biophysical_simulation": ["AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_.*"],
        "input_manager": ["animal.pen_information.*.manure_streams.0.bedding_name"],
        "bedding_configs_path": configs_path,
        "bedding_type_to_file_key": type_to_key,
        "economics_files": economics_files,
    }
    if billable_pen_combinations is not None:
        bedding_entry["billable_pen_combinations"] = billable_pen_combinations
    economic_map = {"Animal": {"Costs": {"Bedding requirements": bedding_entry}}}
    # The preprocessor iterates its own ECONOMIC_MAP binding, while the bedding
    # handler reads its entry from the mapping module; patch both.
    monkeypatch.setattr(preprocessing, "ECONOMIC_MAP", economic_map)
    monkeypatch.setattr(economics_mapping, "ECONOMIC_MAP", economic_map)
    results = preprocessing.EconomicPreprocessor().preprocess()
    return results["Animal"]["Costs"]["Bedding requirements"], dummy_om


def test_preprocess_bedding_bills_only_billable_pen_combinations(monkeypatch: pytest.MonkeyPatch) -> None:
    bedding, dummy_om = _run_bedding(
        monkeypatch,
        {
            "config.start_date": "2021:1",
            "config.FIPS_county_code": 1001,
            "animal.bedding_configs": [
                {"name": "calf_straw", "bedding_type": "straw"},
                {"name": "lac_and_growing_sand", "bedding_type": "sand"},
            ],
            "straw_price": {"fips": [1001], "2021": [50.0]},
            "sand_price": {"fips": [1001], "2021": [120.0]},
        },
        {
            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_0_CALF": _daily(10, 365),
            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_3_LAC_COW": _daily(90, 365),
        },
        pens=[_pen(0, "calf_straw"), _pen(3, "lac_and_growing_sand")],
        type_to_key={"straw": "straw", "sand": "sand"},
        economics_files={"straw": "straw_price", "sand": "sand_price"},
        billable_pen_combinations=["LAC_COW"],
    )
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(10800.0)
    assert bedding["biophysical_aggregate"] == pytest.approx(90.0)
    assert set(bedding["price_data"].keys()) == {"sand"}
    emitted = dict(dummy_om.added_variables)
    assert emitted["econ_bedding_total_cost"] == pytest.approx(10800.0)
    assert emitted["econ_bedding_billed_head_years"] == pytest.approx(90.0)
    assert emitted["econ_bedding_avg_price_per_head_year"] == pytest.approx(120.0)


def test_preprocess_bedding_pairs_each_pen_with_its_own_price(monkeypatch: pytest.MonkeyPatch) -> None:
    bedding, _ = _run_bedding(
        monkeypatch,
        {
            "config.start_date": "2021:1",
            "config.FIPS_county_code": 1001,
            "animal.bedding_configs": [
                {"name": "calf_straw", "bedding_type": "straw"},
                {"name": "lac_and_growing_sand", "bedding_type": "sand"},
            ],
            "straw_price": {"fips": [1001], "2021": [50.0]},
            "sand_price": {"fips": [1001], "2021": [120.0]},
        },
        {
            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_1_CALF": _daily(10, 365),
            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_2_GROWING": _daily(20, 365),
        },
        pens=[_pen(1, "calf_straw"), _pen(2, "lac_and_growing_sand")],
        type_to_key={"straw": "straw", "sand": "sand"},
        economics_files={"straw": "straw_price", "sand": "sand_price"},
    )
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(2900.0)
    assert bedding["flow_type"] == "cost"
    assert set(bedding["price_data"].keys()) == {"straw", "sand"}


def test_preprocess_bedding_total_equals_quantity_times_price(monkeypatch: pytest.MonkeyPatch) -> None:
    bedding, _ = _run_bedding(
        monkeypatch,
        {
            "config.start_date": "2021:1",
            "config.FIPS_county_code": 1001,
            "animal.bedding_configs": [
                {"name": "calf_straw", "bedding_type": "straw"},
                {"name": "lac_and_growing_sand", "bedding_type": "sand"},
            ],
            "straw_price": {"fips": [1001], "2021": [50.0]},
            "sand_price": {"fips": [1001], "2021": [50.0]},
        },
        {
            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_1_CALF": _daily(10, 365),
            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_2_GROWING": _daily(20, 365),
        },
        pens=[_pen(1, "calf_straw"), _pen(2, "lac_and_growing_sand")],
        type_to_key={"straw": "straw", "sand": "sand"},
        economics_files={"straw": "straw_price", "sand": "sand_price"},
    )
    assert bedding["biophysical_aggregate"] == pytest.approx(30.0)
    assert bedding["price_aggregate"] == pytest.approx(50.0)
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(1500.0)
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(
        bedding["biophysical_aggregate"] * bedding["price_aggregate"]
    )


def test_preprocess_bedding_resolves_by_pen_id_not_list_position(monkeypatch: pytest.MonkeyPatch) -> None:
    bedding, _ = _run_bedding(
        monkeypatch,
        {
            "config.start_date": "2021:1",
            "config.FIPS_county_code": 1001,
            "animal.bedding_configs": [
                {"name": "straw_cfg", "bedding_type": "straw"},
                {"name": "sand_cfg", "bedding_type": "sand"},
                {"name": "sawdust_cfg", "bedding_type": "sawdust"},
            ],
            "straw_price": {"fips": [1001], "2021": [50.0]},
            "sand_price": {"fips": [1001], "2021": [120.0]},
            "sawdust_price": {"fips": [1001], "2021": [70.0]},
        },
        {
            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_0_CALF": _daily(10, 365),
            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_1_GROWING": _daily(20, 365),
            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_2_CLOSE_UP": _daily(30, 365),
        },
        pens=[_pen(2, "sawdust_cfg"), _pen(0, "straw_cfg"), _pen(1, "sand_cfg")],
        type_to_key={"straw": "straw", "sand": "sand", "sawdust": "sawdust"},
        economics_files={"straw": "straw_price", "sand": "sand_price", "sawdust": "sawdust_price"},
    )
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(5000.0)


def test_preprocess_bedding_normalizes_compound_types(monkeypatch: pytest.MonkeyPatch) -> None:
    bedding, _ = _run_bedding(
        monkeypatch,
        {
            "config.start_date": "2021:1",
            "config.FIPS_county_code": 1001,
            "animal.bedding_configs": [
                {"name": "cbpb_mix", "bedding_type": "CBPB sawdust"},
                {"name": "recycled", "bedding_type": "manure solids"},
            ],
            "cbpb_price": {"fips": [1001], "2021": [10.0]},
            "ms_price": {"fips": [1001], "2021": [5.0]},
        },
        {
            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_0_CALF": _daily(10, 365),
            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_1_LAC_COW": _daily(2, 365),
        },
        pens=[_pen(0, "cbpb_mix"), _pen(1, "recycled")],
        type_to_key={"CBPB sawdust": "CBPB", "manure solids": "manure_solids"},
        economics_files={"CBPB": "cbpb_price", "manure_solids": "ms_price"},
    )
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(110.0)
    assert set(bedding["price_data"].keys()) == {"CBPB", "manure_solids"}


def test_preprocess_bedding_skips_none_type_with_no_cost(monkeypatch: pytest.MonkeyPatch) -> None:
    bedding, dummy_om = _run_bedding(
        monkeypatch,
        {
            "config.start_date": "2021:1",
            "config.FIPS_county_code": 1001,
            "animal.bedding_configs": [
                {"name": "calf_straw", "bedding_type": "straw"},
                {"name": "none (no bedding)", "bedding_type": "none"},
            ],
            "straw_price": {"fips": [1001], "2021": [50.0]},
        },
        {
            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_0_CALF": _daily(10, 365),
            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_1_GROWING": _daily(99, 365),
        },
        pens=[_pen(0, "calf_straw"), _pen(1, "none (no bedding)")],
        type_to_key={"straw": "straw"},
        economics_files={"straw": "straw_price"},
    )
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(500.0)
    assert "UnmappedBeddingType" not in [code for code, _, _ in dummy_om.warnings]


def test_preprocess_bedding_uses_leap_year_denominator(monkeypatch: pytest.MonkeyPatch) -> None:
    bedding, _ = _run_bedding(
        monkeypatch,
        {
            "config.start_date": "2020:1",
            "config.FIPS_county_code": 1001,
            "animal.bedding_configs": [{"name": "calf_straw", "bedding_type": "straw"}],
            "straw_price": {"fips": [1001], "2020": [50.0]},
        },
        {"AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_0_CALF": _daily(1, 366)},
        pens=[_pen(0, "calf_straw")],
        type_to_key={"straw": "straw"},
        economics_files={"straw": "straw_price"},
    )
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(50.0)


def test_preprocess_bedding_prorates_partial_year(monkeypatch: pytest.MonkeyPatch) -> None:
    bedding, _ = _run_bedding(
        monkeypatch,
        {
            "config.start_date": "2021:1",
            "config.FIPS_county_code": 1001,
            "animal.bedding_configs": [{"name": "calf_straw", "bedding_type": "straw"}],
            "straw_price": {"fips": [1001], "2021": [365.0]},
        },
        {"AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_0_CALF": _daily(10, 20)},
        pens=[_pen(0, "calf_straw")],
        type_to_key={"straw": "straw"},
        economics_files={"straw": "straw_price"},
    )
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(200.0)


def test_preprocess_bedding_falls_back_to_nearest_price_year(monkeypatch: pytest.MonkeyPatch) -> None:
    bedding, dummy_om = _run_bedding(
        monkeypatch,
        {
            "config.start_date": "2018:1",
            "config.FIPS_county_code": 1001,
            "animal.bedding_configs": [{"name": "calf_straw", "bedding_type": "straw"}],
            "straw_price": {"fips": [1001], "2021": [50.0]},
        },
        {"AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_0_CALF": _daily(10, 365)},
        pens=[_pen(0, "calf_straw")],
        type_to_key={"straw": "straw"},
        economics_files={"straw": "straw_price"},
    )
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(500.0)
    assert "MissingPriceYear" in [code for code, _, _ in dummy_om.warnings]


def test_preprocess_bedding_warns_on_missing_fips(monkeypatch: pytest.MonkeyPatch) -> None:
    bedding, dummy_om = _run_bedding(
        monkeypatch,
        {
            "config.start_date": "2021:1",
            "config.FIPS_county_code": 9999,
            "animal.bedding_configs": [{"name": "calf_straw", "bedding_type": "straw"}],
            "straw_price": {"fips": [1001], "2021": [50.0]},
        },
        {"AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_0_CALF": _daily(10, 365)},
        pens=[_pen(0, "calf_straw")],
        type_to_key={"straw": "straw"},
        economics_files={"straw": "straw_price"},
    )
    assert "MissingPriceData" in [code for code, _, _ in dummy_om.warnings]


def test_preprocess_bedding_unloadable_price_file_costs_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    bedding, dummy_om = _run_bedding(
        monkeypatch,
        {
            "config.start_date": "2021:1",
            "config.FIPS_county_code": 1001,
            "animal.bedding_configs": [
                {"name": "calf_straw", "bedding_type": "straw"},
                {"name": "lac_and_growing_sand", "bedding_type": "sand"},
            ],
            "sand_price": {"fips": [1001], "2021": [120.0]},
        },
        {
            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_0_CALF": _daily(10, 365),
            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_1_GROWING": _daily(20, 365),
        },
        pens=[_pen(0, "calf_straw"), _pen(1, "lac_and_growing_sand")],
        type_to_key={"straw": "straw", "sand": "sand"},
        economics_files={"straw": "straw_price", "sand": "sand_price"},
    )
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(2400.0)
    assert "MissingBeddingPriceFile" in [code for code, _, _ in dummy_om.warnings]


def test_preprocess_bedding_pairs_each_year_with_its_own_price(monkeypatch: pytest.MonkeyPatch) -> None:
    bedding, _ = _run_bedding(
        monkeypatch,
        {
            "config.start_date": "2020:1",
            "config.FIPS_county_code": 1001,
            "animal.bedding_configs": [{"name": "calf_straw", "bedding_type": "straw"}],
            "straw_price": {"fips": [1001], "2020": [10.0], "2021": [20.0]},
        },
        {"AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_0_CALF": _daily(5, 366 + 365)},
        pens=[_pen(0, "calf_straw")],
        type_to_key={"straw": "straw"},
        economics_files={"straw": "straw_price"},
    )
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(150.0)


def test_preprocess_bedding_derives_pen_id_from_underscored_name(monkeypatch: pytest.MonkeyPatch) -> None:
    bedding, _ = _run_bedding(
        monkeypatch,
        {
            "config.start_date": "2021:1",
            "config.FIPS_county_code": 1001,
            "animal.bedding_configs": [{"name": "calf_straw", "bedding_type": "straw"}],
            "straw_price": {"fips": [1001], "2021": [50.0]},
        },
        {"AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_7_CLOSE_UP": _daily(3, 365)},
        pens=[_pen(7, "calf_straw")],
        type_to_key={"straw": "straw"},
        economics_files={"straw": "straw_price"},
    )
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(150.0)


def test_bedding_line_item_flows_into_framework_breakdown() -> None:
    from RUFAS.EEE.economics.framework import EconomicFramework

    framework = EconomicFramework.__new__(EconomicFramework)
    preprocessed = {
        "Animal": {
            "Costs": {
                "Bedding requirements": {
                    "flow_type": "cost",
                    "line_item_values_by_scenario": {"baseline": 2900.0},
                    "biophysical_values": [],
                    "price_values": [50.0, 120.0],
                }
            }
        }
    }
    breakdown = framework._build_line_item_breakdown(preprocessed)
    assert breakdown["Animal"]["costs"]["Bedding requirements"]["total"] == pytest.approx(2900.0)
