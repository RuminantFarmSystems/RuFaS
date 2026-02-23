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


def test_partial_budget_exports_all_series(monkeypatch: pytest.MonkeyPatch) -> None:
    preprocessed = {
        "Section": {
            "Revenue": {
                "Milk": {
                    "flow_type": "revenue",
                    "line_item_values_by_scenario": {"baseline": 100.0, "alternative": 110.0},
                },
                "Cull cows": {
                    "flow_type": "revenue",
                    "line_item_values_by_scenario": {"baseline": 50.0, "alternative": 47.0},
                },
            },
            "Costs": {
                "Feed": {
                    "flow_type": "cost",
                    "line_item_values_by_scenario": {"baseline": 25.0, "alternative": 27.0},
                },
                "Labor": {
                    "flow_type": "cost",
                    "line_item_values_by_scenario": {"baseline": 10.0, "alternative": 8.0},
                },
            },
        }
    }

    dummy_im = object()
    dummy_om = DummyOutputManager()

    monkeypatch.setattr(partial_budget, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(partial_budget, "OutputManager", lambda: dummy_om)

    pb = partial_budget.PartialBudget()
    pb.calculate_partial_budget(preprocessed)

    exported = {name: value for name, value, _ in dummy_om.variables}

    assert exported["econ_pba_additional_revenue"] == [10.0]
    assert exported["econ_pba_reduced_costs"] == [2.0]
    assert exported["econ_pba_additional_costs"] == [2.0]
    assert exported["econ_pba_reduced_revenue"] == [3.0]
    assert exported["econ_pba_net_change"] == pytest.approx([7.0])
    assert exported["econ_pba_cumulative_net_change"] == pytest.approx([7.0])
    assert "econ_pba_summary" in exported


def test_partial_budget_exports_net_annual_cash_flow_for_single_scenario(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    preprocessed = {
        "Section": {
            "Revenue": {
                "Milk": {
                    "flow_type": "revenue",
                    "line_item_values_by_scenario": {"baseline": 120.0},
                }
            },
            "Costs": {
                "Feed": {
                    "flow_type": "cost",
                    "line_item_values_by_scenario": {"baseline": 80.0},
                }
            },
        }
    }

    dummy_im = object()
    dummy_om = DummyOutputManager()

    monkeypatch.setattr(partial_budget, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(partial_budget, "OutputManager", lambda: dummy_om)

    pb = partial_budget.PartialBudget()
    pb.calculate_partial_budget(preprocessed)

    exported = {name: value for name, value, _ in dummy_om.variables}

    assert exported["econ_pba_net_annual_cash_flow"] == [40.0]
    assert exported["econ_pba_revenue_total"] == [120.0]
    assert exported["econ_pba_cost_total"] == [80.0]
    assert exported["econ_pba_additional_revenue"] == [0.0]
    assert exported["econ_pba_reduced_costs"] == [0.0]
    assert exported["econ_pba_additional_costs"] == [0.0]
    assert exported["econ_pba_reduced_revenue"] == [0.0]
    assert "econ_pba_summary" in exported
