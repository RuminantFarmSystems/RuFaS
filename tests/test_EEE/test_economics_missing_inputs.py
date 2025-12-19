import pytest

from RUFAS.EEE.economics import framework, partial_budget


class DummyOutputManager:
    def __init__(self):
        self.warnings = []

    def add_warning(self, code, message, info):
        self.warnings.append((code, message, info))

    def add_log(self, *args, **kwargs):
        return None


class MissingInputManager:
    def __init__(self):
        self.checked = []

    def check_property_exists_in_pool(self, key):
        self.checked.append(key)
        return False

    def get_data(self, key):  # pragma: no cover - guarded by pool check
        raise AssertionError("get_data should not be called when pool check fails")


def test_partial_budget_ignores_missing_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_im = MissingInputManager()
    dummy_om = DummyOutputManager()

    monkeypatch.setattr(partial_budget, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(partial_budget, "OutputManager", lambda: dummy_om)

    pb = partial_budget.PartialBudget()

    assert pb.has_partial_budget_activity() is False
    assert dummy_im.checked == [
        "economics.partial_budget.additional_revenue",
        "economics.partial_budget.reduced_costs",
        "economics.partial_budget.additional_costs",
        "economics.partial_budget.reduced_revenue",
    ]
    warning_codes = [code for code, _, _ in dummy_om.warnings]
    assert warning_codes.count("MissingPartialBudgetInput") == 4


def test_capital_cost_present_handles_missing_table(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_im = MissingInputManager()
    dummy_om = DummyOutputManager()

    class DummyPartialBudget:
        def __init__(self):
            self.called = False

        def has_partial_budget_activity(self):
            return False

    class DummyPreprocessor:
        def preprocess(self):
            return {}

    monkeypatch.setattr(framework, "InputManager", lambda: dummy_im)
    monkeypatch.setattr(framework, "OutputManager", lambda: dummy_om)
    monkeypatch.setattr(framework, "PartialBudget", lambda: DummyPartialBudget())
    monkeypatch.setattr(framework, "EconomicPreprocessor", lambda: DummyPreprocessor())

    ef = framework.EconomicFramework()

    assert ef._capital_cost_present() is False
    assert dummy_im.checked == ["capital_costs.capital_cost_breakdown"]
    warning_codes = [code for code, _, _ in dummy_om.warnings]
    assert warning_codes == ["MissingCapitalCostData"]
