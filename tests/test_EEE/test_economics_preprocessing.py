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
    def __init__(self, data, field_keys=None):
        self._data = {
            "config.start_date": "2020:1",
            "config.end_date": "2020:365",
            "config.FIPS_county_code": 1001,
            "_default_values": {"commodity": [], "2020": []},
            "_default_fallback_values": {"commodity": [], "2020": []},
            **data,
        }
        self._field_keys = field_keys or []
        self.added_runtime = []

    def get_data(self, key):
        return self._data.get(key)

    def get_data_keys_by_properties(self, properties_key):
        if properties_key == "field_properties":
            return self._field_keys
        return []

    def add_runtime_variable_to_pool(
        self, variable_name, data, properties_blob_key, eager_termination=False, input_path=None
    ):
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


def _seed_cost_map():
    """Minimal ECONOMIC_MAP for seed cost tests."""
    return {
        "Soil_and_crop": {
            "Costs": {
                "Seeds costs": {
                    "biophysical_simulation": ["field.crop_specification", "field.field_size"],
                    "economics_files": ["commodity_prices_corn_seed_dollar_per_square_meter"],
                }
            }
        }
    }


def _corn_schedule(plant_day: int, kill_day: int, year: int = 2020) -> dict:
    """Build a minimal corn_silage crop schedule dict for tests."""
    return {
        "crop_species": "corn_silage",
        "planting_years": [year],
        "planting_days": [plant_day],
        "harvest_years": [year],
        "harvest_days": [kill_day],
        "harvest_operations": ["harvest_kill"],
        "pattern_repeat": 0,
        "planting_skip": 0,
        "harvesting_skip": 0,
    }


def test_preprocess_seed_costs_daily_array_shape_and_values(monkeypatch: pytest.MonkeyPatch) -> None:
    """Daily area array has length == sim days with correct values inside the growing period.

    Sim: 2020:1 → 2020:365  (365 days, indices 0-364)
    field_a: 1 ha corn_silage, planted day 100, killed day 200.
      plant_idx = 99, kill_idx = 199, duration = 100
      daily_value = 10,000 / 100 = 100.0
      Array is 100.0 for indices 99-198, 0.0 elsewhere.
    """
    dummy_im = DummyInputManager(
        data={
            "field_a": {"crop_specification": "RotA", "field_size": 1.0},
            "RotA.crop_schedules": [_corn_schedule(100, 200)],
            "commodity_prices_corn_seed_dollar_per_square_meter": {"fips": [1001], "2020": [0.01]},
        },
        field_keys=["field_a"],
    )
    dummy_om = DummyOutputManager({})
    monkeypatch.setattr(preprocessing, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(preprocessing, "OutputManager", lambda: dummy_om)

    preprocessor = preprocessing.EconomicPreprocessor()
    daily = preprocessor._preprocess_seed_costs()

    seed_key = "commodity_prices_corn_seed_dollar_per_square_meter"
    assert seed_key in daily
    arr = daily[seed_key]
    assert len(arr) == 365
    assert arr[98] == pytest.approx(0.0)   # day 99 (index 98) — before planting
    assert arr[99] == pytest.approx(100.0)  # planting day (index 99)
    assert arr[198] == pytest.approx(100.0) # last day of growth (index 198)
    assert arr[199] == pytest.approx(0.0)   # harvest day — not included
    assert sum(arr) == pytest.approx(10_000.0)  # 100 days × 100 m²/day


def test_preprocess_seed_costs_computes_total_cost(monkeypatch: pytest.MonkeyPatch) -> None:
    """Total seed cost = sum(daily_area) × avg_price across all fields and seed types.

    Sim: 2020:1 → 2020:365
    field_a: 1 ha corn_silage, day 100→200:  sum = 10,000 m²
    field_b: 2 ha corn_grain,  day  50→150:  sum = 20,000 m²
             2 ha alfalfa_silage (no seed key) — skipped
    corn_seed price = $0.01/m²  →  total = 30,000 × 0.01 = $300
    """
    dummy_im = DummyInputManager(
        data={
            "field_a": {"crop_specification": "RotA", "field_size": 1.0},
            "field_b": {"crop_specification": "RotB", "field_size": 2.0},
            "RotA.crop_schedules": [_corn_schedule(100, 200)],
            "RotB.crop_schedules": [
                {
                    "crop_species": "corn_grain",
                    "planting_years": [2020],
                    "planting_days": [50],
                    "harvest_years": [2020],
                    "harvest_days": [150],
                    "harvest_operations": ["harvest_kill"],
                    "pattern_repeat": 0,
                    "planting_skip": 0,
                    "harvesting_skip": 0,
                },
                {
                    "crop_species": "alfalfa_silage",
                    "planting_years": [2020],
                    "planting_days": [155],
                    "harvest_years": [2020],
                    "harvest_days": [300],
                    "harvest_operations": ["harvest_kill"],
                    "pattern_repeat": 0,
                    "planting_skip": 0,
                    "harvesting_skip": 0,
                },
            ],
            "commodity_prices_corn_seed_dollar_per_square_meter": {"fips": [1001], "2020": [0.01]},
        },
        field_keys=["field_a", "field_b"],
    )
    dummy_om = DummyOutputManager({})
    monkeypatch.setattr(preprocessing, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(preprocessing, "OutputManager", lambda: dummy_om)
    monkeypatch.setattr(preprocessing, "ECONOMIC_MAP", _seed_cost_map())

    preprocessor = preprocessing.EconomicPreprocessor()
    results = preprocessor.preprocess()

    item = results["Soil_and_crop"]["Costs"]["Seeds costs"]
    assert item["flow_type"] == "cost"
    assert item["line_item_values_by_scenario"]["baseline"] == pytest.approx(300.0)


def test_preprocess_seed_costs_warns_on_missing_field_data(monkeypatch: pytest.MonkeyPatch) -> None:
    """Seed costs handler emits warning when no field keys are available."""

    dummy_im = DummyInputManager(data={}, field_keys=[])
    dummy_om = DummyOutputManager({})

    monkeypatch.setattr(preprocessing, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(preprocessing, "OutputManager", lambda: dummy_om)
    monkeypatch.setattr(preprocessing, "ECONOMIC_MAP", _seed_cost_map())

    preprocessor = preprocessing.EconomicPreprocessor()
    results = preprocessor.preprocess()

    item = results["Soil_and_crop"]["Costs"]["Seeds costs"]
    assert item["line_item_values_by_scenario"]["baseline"] == pytest.approx(0.0)
    warning_codes = [code for code, _, _ in dummy_om.warnings]
    assert "MissingBiophysicalData" in warning_codes


def test_preprocess_seed_costs_clips_period_to_simulation_window(monkeypatch: pytest.MonkeyPatch) -> None:
    """Growing periods that extend beyond the simulation window are clipped.

    Sim: 2020:1 → 2020:365  (365 days, indices 0-364)
    field: 1 ha corn_silage, planted day 300, killed day 100 of 2021.
      plant_idx = 299, kill_idx = (2021_day100 - 2020_day1).days = 464
      Clipped range: [299, 365)  →  66 days active
      duration (unclipped) = 464 - 299 = 165
      daily_value = 10,000 / 165 ≈ 60.6
      sum(arr) ≈ 66 × 60.6 ≈ 4,000  (= 10,000 × 66/165)
    """
    dummy_im = DummyInputManager(
        data={
            "field_a": {"crop_specification": "RotA", "field_size": 1.0},
            "RotA.crop_schedules": [
                {
                    "crop_species": "corn_silage",
                    "planting_years": [2020],
                    "planting_days": [300],
                    "harvest_years": [2021],
                    "harvest_days": [100],
                    "harvest_operations": ["harvest_kill"],
                    "pattern_repeat": 0,
                    "planting_skip": 0,
                    "harvesting_skip": 0,
                }
            ],
        },
        field_keys=["field_a"],
    )
    dummy_om = DummyOutputManager({})
    monkeypatch.setattr(preprocessing, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(preprocessing, "OutputManager", lambda: dummy_om)

    preprocessor = preprocessing.EconomicPreprocessor()
    daily = preprocessor._preprocess_seed_costs()

    seed_key = "commodity_prices_corn_seed_dollar_per_square_meter"
    arr = daily[seed_key]
    assert len(arr) == 365
    assert arr[298] == pytest.approx(0.0)  # before planting

    from datetime import datetime

    plant_date = datetime.strptime("2020:300", "%Y:%j")
    kill_date = datetime.strptime("2021:100", "%Y:%j")
    start_date = datetime.strptime("2020:1", "%Y:%j")
    duration = (kill_date - plant_date).days
    expected_daily = 10_000.0 / duration
    expected_sum = 10_000.0 * 66 / duration

    assert arr[299] == pytest.approx(expected_daily)
    assert arr[364] == pytest.approx(expected_daily)
    assert sum(arr) == pytest.approx(expected_sum)
