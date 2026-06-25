import pytest
import re

from RUFAS.EEE.economics import preprocessing


class DummyOutputManager:
    def __init__(self, pool):
        self._pool = pool
        self.warnings = []
        self.logs = []

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

    def add_runtime_variable_to_pool(self, variable_name, data, properties_blob_key, eager_termination=False):
        self.added_runtime.append(
            {
                "variable_name": variable_name,
                "data": data,
                "properties_blob_key": properties_blob_key,
                "eager_termination": eager_termination,
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
):
    """Run the dedicated bedding processor and return its result item + OM.

    ``pens`` is injected as the real ``animal.pen_information`` list so the
    processor resolves bedding by each pen's ``id`` field (not list position).
    """

    dummy_im = DummyInputManager({**im_data, "animal.pen_information": pens})
    dummy_om = DummyOutputManager(pool)
    monkeypatch.setattr(preprocessing, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(preprocessing, "OutputManager", lambda: dummy_om)
    monkeypatch.setattr(
        preprocessing,
        "ECONOMIC_MAP",
        {
            "Animal": {
                "Costs": {
                    "Bedding requirements": {
                        "biophysical_simulation": [
                            "AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_.*"
                        ],
                        "input_manager": ["animal.pen_information.*.manure_streams.0.bedding_name"],
                        "dedicated_processor": "bedding",
                        "bedding_configs_path": configs_path,
                        "bedding_type_to_file_key": type_to_key,
                        "economics_files": economics_files,
                    }
                }
            }
        },
    )
    results = preprocessing.EconomicPreprocessor().preprocess()
    return results["Animal"]["Costs"]["Bedding requirements"], dummy_om


def test_preprocess_bedding_pairs_each_pen_with_its_own_price(monkeypatch: pytest.MonkeyPatch) -> None:
    # Each pen's animal count must pair with that pen's own bedding price, and
    # the bedding_name (a config name) must resolve through bedding_configs.
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
    # pen 1: 10 head * $50 straw = 500 ; pen 2: 20 head * $120 sand = 2400
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(2900.0)
    assert bedding["flow_type"] == "cost"
    assert set(bedding["price_data"].keys()) == {"straw", "sand"}


def test_preprocess_bedding_resolves_by_pen_id_not_list_position(monkeypatch: pytest.MonkeyPatch) -> None:
    # pen_information ids [2, 0, 1] are NOT in list order; each pen's count must
    # still pair with the bedding of the entry whose ``id`` matches (issue #3088).
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
        # list order != id order: positions hold ids 2, 0, 1
        pens=[_pen(2, "sawdust_cfg"), _pen(0, "straw_cfg"), _pen(1, "sand_cfg")],
        type_to_key={"straw": "straw", "sand": "sand", "sawdust": "sawdust"},
        economics_files={"straw": "straw_price", "sand": "sand_price", "sawdust": "sawdust_price"},
    )
    # pen0=straw 10*50=500 ; pen1=sand 20*120=2400 ; pen2=sawdust 30*70=2100
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(5000.0)


def test_preprocess_bedding_normalizes_compound_types(monkeypatch: pytest.MonkeyPatch) -> None:
    # "CBPB sawdust" -> CBPB and "manure solids" -> manure_solids.
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
    # 10*10 + 2*5 = 110
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(110.0)
    assert set(bedding["price_data"].keys()) == {"CBPB", "manure_solids"}


def test_preprocess_bedding_skips_none_type_with_no_cost(monkeypatch: pytest.MonkeyPatch) -> None:
    # A pen whose bedding_type resolves to "none" must incur no cost and no
    # $1/head fallback (the config NAME is "none (no bedding)").
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
    # only the straw pen costs anything: 10 * 50 = 500; the "none" pen is free
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(500.0)
    assert "UnmappedBeddingType" not in [code for code, _, _ in dummy_om.warnings]


def test_preprocess_bedding_uses_leap_year_denominator(monkeypatch: pytest.MonkeyPatch) -> None:
    # 2020 is a leap year (366 days): 366 head-days / 366 = avg 1 head.
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
    # 20 days of 10 head in a 365-day year -> (200/365) * price, not a full year.
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
    # (10*20 / 365) * 365 = 200
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(200.0)


def test_preprocess_bedding_falls_back_to_nearest_price_year(monkeypatch: pytest.MonkeyPatch) -> None:
    # Price file only has a 2021 column but the sim runs in 2018.
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
    # Price file loads but the sim FIPS county is absent; must warn (not silent).
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
    # A mapped bedding type whose price file cannot be loaded must cost $0 and
    # warn -- not fabricate a $1/head charge -- even when another pen prices fine.
    bedding, dummy_om = _run_bedding(
        monkeypatch,
        {
            "config.start_date": "2021:1",
            "config.FIPS_county_code": 1001,
            "animal.bedding_configs": [
                {"name": "calf_straw", "bedding_type": "straw"},
                {"name": "lac_and_growing_sand", "bedding_type": "sand"},
            ],
            # "straw_price" is intentionally absent from the InputManager.
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
    # only the sand pen costs anything: 20 * 120 = 2400 (no $10 phantom straw charge)
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(2400.0)
    assert "MissingBeddingPriceFile" in [code for code, _, _ in dummy_om.warnings]


def test_preprocess_bedding_pairs_each_year_with_its_own_price(monkeypatch: pytest.MonkeyPatch) -> None:
    # A two-year sim must pair each year's average head with that year's price.
    bedding, _ = _run_bedding(
        monkeypatch,
        {
            "config.start_date": "2020:1",
            "config.FIPS_county_code": 1001,
            "animal.bedding_configs": [{"name": "calf_straw", "bedding_type": "straw"}],
            "straw_price": {"fips": [1001], "2020": [10.0], "2021": [20.0]},
        },
        # 2020 (leap, 366 days) then all of 2021 (365 days)
        {"AnimalModuleReporter.report_daily_pen_total.number_of_animals_in_pen_0_CALF": _daily(5, 366 + 365)},
        pens=[_pen(0, "calf_straw")],
        type_to_key={"straw": "straw"},
        economics_files={"straw": "straw_price"},
    )
    # 2020: 5 head * $10 = 50 ; 2021: 5 head * $20 = 100 ; total 150
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(150.0)


def test_preprocess_bedding_derives_pen_id_from_underscored_name(monkeypatch: pytest.MonkeyPatch) -> None:
    # Pen animal names contain underscores (e.g. CLOSE_UP); pen_id is the part
    # before the FIRST underscore -- no hardcoded value map needed.
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
    # pen_id resolves to "7" -> matches pen id 7 -> 3 head * $50 = 150
    assert bedding["line_item_values_by_scenario"]["baseline"] == pytest.approx(150.0)


def test_bedding_line_item_flows_into_framework_breakdown() -> None:
    # The dedicated processor's output keys must stay compatible with the
    # downstream line-item breakdown in EconomicFramework.
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
