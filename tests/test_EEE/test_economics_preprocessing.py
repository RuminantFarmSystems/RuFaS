import pytest

from RUFAS.EEE.economics import preprocessing


class DummyOutputManager:
    def __init__(self, pool):
        self._pool = pool
        self.warnings = []
        self.logs = []

    def _get_flat_variables_pool(self):
        return self._pool

    def add_warning(self, code, message, info):
        self.warnings.append((code, message, info))

    def add_log(self, title, message, info):
        self.logs.append((title, message, info))


class DummyInputManager:
    def __init__(self, data):
        self._data = data
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

    assert results == {
        "Section": {
            "Category": {
                "Item": {
                    "biophysical_values": [1.0, 2.0, 3.0],
                    "biophysical_aggregate": 6.0,
                    "price_data": {"price.csv": {"cost": 10}},
                }
            }
        }
    }
    assert dummy_im.added_runtime[-1]["variable_name"] == "economic_preprocessed"
    assert dummy_im.added_runtime[-1]["properties_blob_key"] == "economic_preprocessing_properties"
    assert dummy_om.warnings == []
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
    assert energy_data["price_data"] == {"price_premium": {"cost": 25}}
    assert dummy_om.warnings == []


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
