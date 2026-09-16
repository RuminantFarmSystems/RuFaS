import pytest

from RUFAS.EEE.economics import partial_budget
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits


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


BREAKDOWN_PREPROCESSED = {
    "Animal": {
        "Revenue": {
            "Milk": {
                "flow_type": "revenue",
                "biophysical_aggregate": 30.0,
                "biophysical_aggregate_by_scenario": {"baseline": 10.0, "alternative": 20.0},
                "price_aggregate": 2.0,
                "line_item_values_by_scenario": {"baseline": 20.0, "alternative": 40.0},
            }
        },
        "Costs": {
            "Feed": {
                "flow_type": "cost",
                "biophysical_aggregate": 5.0,
                "price_aggregate": None,
                "line_item_values_by_scenario": {"baseline": 5.0, "alternative": float("nan")},
            },
            "Unpriced": {"flow_type": "cost", "biophysical_values": [1.0]},
        },
    },
    "Manure": {
        "Costs": {
            "Labor": {
                "biophysical_aggregate": "3",
                "price_aggregate": "1.5",
                "line_item_values_by_scenario": {"baseline": "4.5", "alternative": 6.0},
            }
        }
    },
}

EXPECTED_BREAKDOWN_ROWS = [
    {
        "module": "Animal",
        "flow_type": "revenue",
        "item": "Milk",
        "scenario": "baseline",
        "biophysical_aggregate": 10.0,
        "price_aggregate": 2.0,
        "line_item_value": 20.0,
    },
    {
        "module": "Animal",
        "flow_type": "revenue",
        "item": "Milk",
        "scenario": "alternative",
        "biophysical_aggregate": 20.0,
        "price_aggregate": 2.0,
        "line_item_value": 40.0,
    },
    {
        "module": "Animal",
        "flow_type": "cost",
        "item": "Feed",
        "scenario": "baseline",
        "biophysical_aggregate": 5.0,
        "price_aggregate": None,
        "line_item_value": 5.0,
    },
    {
        "module": "Animal",
        "flow_type": "cost",
        "item": "Feed",
        "scenario": "alternative",
        "biophysical_aggregate": 5.0,
        "price_aggregate": None,
        "line_item_value": 0.0,
    },
    {
        "module": "Manure",
        "flow_type": "cost",
        "item": "Labor",
        "scenario": "baseline",
        "biophysical_aggregate": 3.0,
        "price_aggregate": 1.5,
        "line_item_value": 4.5,
    },
    {
        "module": "Manure",
        "flow_type": "cost",
        "item": "Labor",
        "scenario": "alternative",
        "biophysical_aggregate": 3.0,
        "price_aggregate": 1.5,
        "line_item_value": 6.0,
    },
]


def _make_partial_budget(monkeypatch: pytest.MonkeyPatch) -> tuple[partial_budget.PartialBudget, DummyOutputManager]:
    dummy_om = DummyOutputManager()
    monkeypatch.setattr(partial_budget, "InputManager", lambda: object())
    monkeypatch.setattr(partial_budget, "OutputManager", lambda: dummy_om)
    return partial_budget.PartialBudget(), dummy_om


def test_line_item_breakdown_lists_one_row_per_item_and_scenario(monkeypatch: pytest.MonkeyPatch) -> None:
    pb, _ = _make_partial_budget(monkeypatch)

    rows = pb.build_line_item_breakdown(BREAKDOWN_PREPROCESSED)

    assert rows == EXPECTED_BREAKDOWN_ROWS


def test_line_item_breakdown_is_empty_without_preprocessed_data(monkeypatch: pytest.MonkeyPatch) -> None:
    pb, _ = _make_partial_budget(monkeypatch)

    assert pb.build_line_item_breakdown(None) == []
    assert pb.build_line_item_breakdown({}) == []


def test_line_item_breakdown_reconciles_with_single_scenario_totals(monkeypatch: pytest.MonkeyPatch) -> None:
    preprocessed = {
        "Animal": {
            "Revenue": {
                "Milk": {"flow_type": "revenue", "line_item_values_by_scenario": {"baseline": 120.0}},
                "Calves": {"flow_type": "revenue", "line_item_values_by_scenario": {"baseline": "30"}},
            },
            "Costs": {
                "Feed": {"flow_type": "cost", "line_item_values_by_scenario": {"baseline": 80.0}},
                "Bedding": {"flow_type": "cost", "line_item_values_by_scenario": {"baseline": float("nan")}},
            },
        }
    }
    pb, dummy_om = _make_partial_budget(monkeypatch)

    pb.calculate_partial_budget(preprocessed)
    rows = pb.build_line_item_breakdown(preprocessed)

    exported = {name: value for name, value, _ in dummy_om.variables}
    revenue_rows = sum(row["line_item_value"] for row in rows if row["flow_type"] == "revenue")
    cost_rows = sum(row["line_item_value"] for row in rows if row["flow_type"] == "cost")
    assert revenue_rows == pytest.approx(exported["econ_pba_revenue_total"][0]) == pytest.approx(150.0)
    assert cost_rows == pytest.approx(exported["econ_pba_cost_total"][0]) == pytest.approx(80.0)
    assert [row["item"] for row in rows] == ["Milk", "Calves", "Feed", "Bedding"]


def test_export_line_item_breakdown_logs_one_entry_per_row(monkeypatch: pytest.MonkeyPatch) -> None:
    pb, dummy_om = _make_partial_budget(monkeypatch)

    rows = pb.export_line_item_breakdown(BREAKDOWN_PREPROCESSED)

    logged = [(value, info) for name, value, info in dummy_om.variables if name == "econ_pba_breakdown"]
    assert [value for value, _ in logged] == rows == EXPECTED_BREAKDOWN_ROWS
    units = logged[0][1]["units"]
    assert set(units) == set(EXPECTED_BREAKDOWN_ROWS[0])
    assert units["line_item_value"] is MeasurementUnits.DOLLARS
    assert all(info["function"] == "export_line_item_breakdown" for _, info in logged)


def test_export_line_item_breakdown_renders_as_csv_columns(monkeypatch: pytest.MonkeyPatch) -> None:
    om = OutputManager()
    om.flush_pools()
    monkeypatch.setattr(partial_budget, "InputManager", lambda: object())
    pb = partial_budget.PartialBudget()

    rows = pb.export_line_item_breakdown(BREAKDOWN_PREPROCESSED)

    filtered = om.filter_variables_pool({"filters": ["econ_pba_breakdown$"]})
    ((key, data),) = filtered.items()
    assert key.endswith("partial_budget.export_line_item_breakdown.econ_pba_breakdown")
    assert data["values"] == rows

    columns = om._dict_to_csv_column_list(key, data)
    assert [column.name for column in columns] == [
        f"{key}.module (unitless)",
        f"{key}.flow_type (unitless)",
        f"{key}.item (unitless)",
        f"{key}.scenario (unitless)",
        f"{key}.biophysical_aggregate (unitless)",
        f"{key}.price_aggregate (unitless)",
        f"{key}.line_item_value ($)",
    ]
    assert columns[2].tolist() == ["Milk", "Milk", "Feed", "Feed", "Labor", "Labor"]
    assert columns[-1].tolist() == [row["line_item_value"] for row in rows]

    om.flush_pools()
