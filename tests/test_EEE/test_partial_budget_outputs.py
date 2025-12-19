import numpy as np
import pytest

from RUFAS.EEE.economics import partial_budget


class DummyOutputManager:
    def __init__(self) -> None:
        self.variables = []
        self.logs = []

    def add_variable(self, name, value, info):
        self.variables.append((name, value, info))

    def add_warning(self, *args, **kwargs):
        return None

    def add_log(self, *args, **kwargs):
        self.logs.append(args)


class DummyInputManager:
    def __init__(self, payload):
        self.payload = payload

    def check_property_exists_in_pool(self, key):
        return key in self.payload

    def get_data(self, key):
        return self.payload[key]


def test_partial_budget_exports_all_series(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "economics.partial_budget.additional_revenue": [10.0, 20.0],
        "economics.partial_budget.reduced_costs": [1.0],
        "economics.partial_budget.additional_costs": np.array([2.0, 4.0, 6.0]),
        "economics.partial_budget.reduced_revenue": 3.0,
    }

    dummy_im = DummyInputManager(payload)
    dummy_om = DummyOutputManager()

    monkeypatch.setattr(partial_budget, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(partial_budget, "OutputManager", lambda: dummy_om)

    pb = partial_budget.PartialBudget()
    pb.calculate_partial_budget()

    exported = {name: value for name, value, _ in dummy_om.variables}

    assert exported["pba_additional_revenue"] == [10.0, 20.0, 0.0]
    assert exported["pba_reduced_costs"] == [1.0, 0.0, 0.0]
    assert exported["pba_additional_costs"] == [2.0, 4.0, 6.0]
    assert exported["pba_reduced_revenue"] == [3.0, 0.0, 0.0]
    assert exported["pba_net_change"] == pytest.approx([6.0, 16.0, -6.0])
    assert exported["pba_cumulative_net_change"] == pytest.approx([6.0, 22.0, 16.0])
    assert "pba_summary" in exported

