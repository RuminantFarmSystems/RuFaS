import pandas as pd

from RUFAS.EEE.economics import framework


class DummyOutputManager:
    def __init__(self) -> None:
        self.variables = []

    def add_variable(self, name, value, info_map):
        self.variables.append((name, value, info_map))

    def add_warning(self, *args, **kwargs):
        return None

    def add_error(self, *args, **kwargs):
        return None


class DummyPartialBudget:
    def has_partial_budget_activity(self, _preprocessed):
        return False

    def calculate_partial_budget(self, _preprocessed):
        return None


def test_framework_exports_line_item_breakdown(monkeypatch):
    preprocessed = {
        "Animal": {
            "Costs": {
                "purchased heifers": {
                    "flow_type": "cost",
                    "biophysical_values": [1000, 200, 30, 4],
                    "price_values": [1, 1, 1, 1],
                    "line_item_values_by_scenario": {"baseline": 1234.0},
                }
            },
            "Revenues": {
                "milk": {
                    "flow_type": "revenue",
                    "biophysical_values": [3, 5],
                    "price_values": [4.0],
                    "line_item_values_by_scenario": {"baseline": 32.0},
                }
            },
        }
    }

    dummy_om = DummyOutputManager()

    monkeypatch.setattr(
        framework, "InputManager", lambda: type("IM", (), {"get_data": lambda *_: pd.DataFrame({"Cost": []})})()
    )
    monkeypatch.setattr(framework, "OutputManager", lambda: dummy_om)
    monkeypatch.setattr(
        framework, "EconomicPreprocessor", lambda: type("Pre", (), {"preprocess": lambda *_: preprocessed})()
    )
    monkeypatch.setattr(framework, "PartialBudget", lambda: DummyPartialBudget())

    ef = framework.EconomicFramework()
    ef.run_economic_analysis()

    exported = {name: value for name, value, _ in dummy_om.variables}
    assert "econ_economic_line_item_breakdown" in exported

    breakdown = exported["econ_economic_line_item_breakdown"]
    heifers = breakdown["Animal"]["costs"]["purchased heifers"]
    assert heifers["total"] == 1234.0
    assert heifers["biophysical_values"] == [1000, 200, 30, 4]
    assert heifers["prices"] == [1, 1, 1, 1]

    milk = breakdown["Animal"]["revenues"]["milk"]
    assert milk["total"] == 32.0
