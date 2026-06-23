from pytest_mock import MockerFixture
import pytest

from RUFAS.EEE.economics.dcfror import DCFRORCalculator
from RUFAS.EEE.economics.digester_costs import DigesterCostCalculator


class _PoolStub:
    """Faithful stand-in for ``InputManager.get_data``.

    Resolves a dotted data address against a nested dict and returns ``None``
    on any missing segment -- exactly like the real ``InputManager``. Unlike
    ``Mock(side_effect={...})``, this fails when the code queries the WRONG
    address, so it catches data-address mistakes.

    This matters for issue #3063: the bug was masked twice because the tests
    mocked the exact (wrong) addresses the code used. The real input pool keeps
    the digester config at ``manure_management.anaerobic_digester`` and the herd
    at ``animal.herd_information.cow_num`` -- NOT ``manure_management_properties``
    / ``animal_properties`` (those are schema references, not pool addresses).
    """

    def __init__(self, pool: dict) -> None:
        self._pool = pool

    def get_data(self, address: str):
        node = self._pool
        for part in address.split("."):
            if not isinstance(node, dict) or part not in node:
                return None
            node = node[part]
        return node


def test_get_digester_config_reads_correct_address(mocker: MockerFixture) -> None:
    """``_get_digester_config`` must read the real pool address for digesters.

    Uses a faithful pool stub, so it fails if the code queries any address other
    than ``manure_management.anaerobic_digester`` (the regression that caused the
    fix for #3063 to silently no-op).
    """

    calc = DCFRORCalculator.__new__(DCFRORCalculator)
    calc.im = _PoolStub(
        {"manure_management": {"anaerobic_digester": [{"hydraulic_retention_time": 10}, {"hydraulic_retention_time": 25}]}}
    )

    config = calc._get_digester_config()

    assert [d["hydraulic_retention_time"] for d in config] == [10, 25]


def test_get_digester_config_empty_when_no_digesters(mocker: MockerFixture) -> None:
    """A scenario with no digesters (e.g. ``no_manure``) yields an empty list."""

    calc = DCFRORCalculator.__new__(DCFRORCalculator)
    calc.im = _PoolStub({"manure_management": {"anaerobic_digester": []}})
    assert calc._get_digester_config() == []

    # Missing key entirely (get_data returns None) is also handled cleanly.
    calc.im = _PoolStub({})
    assert calc._get_digester_config() == []


def test_prepare_costs_applies_digester_cost_curve(mocker: MockerFixture) -> None:
    calc = DCFRORCalculator.__new__(DCFRORCalculator)
    calc.om = mocker.Mock()
    calc.im = _PoolStub(
        {
            "animal": {"herd_information": {"cow_num": 1000.0}},
            "manure_management": {"anaerobic_digester": [{"hydraulic_retention_time": 30.0}]},
        }
    )
    mocker.patch(
        "RUFAS.EEE.economics.dcfror.DigesterCostCalculator.calculate_digester_capital_cost",
        return_value=1000.0,
    )
    mocker.patch(
        "RUFAS.EEE.economics.dcfror.DigesterCostCalculator.capital_recovery_factor",
        return_value=0.2,
    )
    mocker.patch(
        "RUFAS.EEE.economics.dcfror.DigesterCostCalculator.calculate_digester_capex",
        return_value=5000.0,
    )
    mocker.patch(
        "RUFAS.EEE.economics.dcfror.DigesterCostCalculator.scale_installed_cost",
        return_value=8000.0,
    )
    mocker.patch(
        "RUFAS.EEE.economics.dcfror.DigesterCostCalculator.calculate_digester_operational_cost",
        return_value=250.0,
    )

    prepared = calc._prepare_costs(
        {
            "cost_capital_multiple": [{"Item": "Digester", "Cost": 1.0}, {"Item": "Other", "Cost": 9.0}],
            "interest_rate_construction": 0.05,
            "construction_term": 1,
            "construction_finish_pcts": [1.0],
            "cost_operational_units": [[1.0, 1.0]],
            "cost_operational_unit_cost": [[1.0, 1.0]],
            "units_produced": [[2.0, 2.0]],
            "unit_cost": [[10.0, 10.0]],
            "goal_seek_unit_price_multiplier": 1.0,
            "loan_interest_rate": 0.07,
            "project_term": 2,
        }
    )

    # base 10 - prior digester row (1.0) + computed capex (8000) = 8009
    assert prepared["capital_cost"] == pytest.approx(8009.0)
    assert prepared["operating_costs"].tolist() == pytest.approx([251.0, 251.0])


def test_prepare_costs_without_digester_config_unchanged(mocker: MockerFixture) -> None:
    calc = DCFRORCalculator.__new__(DCFRORCalculator)
    calc.om = mocker.Mock()
    calc.im = _PoolStub({})  # no manure_management -> get_data returns None -> no digester costing

    prepared = calc._prepare_costs(
        {
            "cost_capital_multiple": [{"Item": "Barn", "Cost": 10.0}],
            "interest_rate_construction": 0.05,
            "construction_term": 1,
            "construction_finish_pcts": [1.0],
            "cost_operational_units": [[1.0, 1.0]],
            "cost_operational_unit_cost": [[1.0, 1.0]],
            "units_produced": [[2.0, 2.0]],
            "unit_cost": [[10.0, 10.0]],
            "goal_seek_unit_price_multiplier": 1.0,
            "loan_interest_rate": 0.07,
            "project_term": 2,
        }
    )

    assert prepared["capital_cost"] == pytest.approx(10.0)
    assert prepared["operating_costs"].tolist() == pytest.approx([1.0, 1.0])


def test_prepare_costs_uses_real_digester_costs_not_fallback(mocker: MockerFixture) -> None:
    """Regression test for issue #3063.

    With the capital-cost breakdown shipped in ``economic_inputs.json`` (a single
    non-digester ``"Fallback capital cost"`` row of $15,000) and digesters present
    in the manure config, the real ``DigesterCostCalculator`` must run so the
    capital cost reaching DCFROR reflects digester CAPEX rather than the $15,000
    fallback.

    Nothing here mocks ``DigesterCostCalculator`` and no ``"digester"`` row is
    injected into the breakdown, so it exercises the real costing path. The
    faithful ``_PoolStub`` also makes the test fail if the digester / herd data
    addresses are wrong (the second half of the #3063 fix).
    """

    cow_num = 1500.0
    # Mirror input/data/manure/example_freestall_processor_configs.json (two digesters).
    digester_config = [
        {"hydraulic_retention_time": 10},
        {"hydraulic_retention_time": 25},
    ]
    loan_interest_rate = 0.05
    project_term = 20

    calc = DCFRORCalculator.__new__(DCFRORCalculator)
    calc.om = mocker.Mock()
    # Real pool layout (verified against a live freestall load).
    calc.im = _PoolStub(
        {
            "animal": {"herd_information": {"cow_num": cow_num}},
            "manure_management": {"anaerobic_digester": digester_config},
        }
    )

    prepared = calc._prepare_costs(
        {
            # Exactly the breakdown shipped in economic_inputs.json: no digester row.
            "cost_capital_multiple": [{"Item": "Fallback capital cost", "Cost": 15000.0}],
            "interest_rate_construction": 0.04,
            "construction_term": 1,
            "construction_finish_pcts": [1.0],
            "cost_operational_units": [[1.0] * project_term],
            "cost_operational_unit_cost": [[1000.0] * project_term],
            "units_produced": [[1.0] * project_term],
            "unit_cost": [[2500.0] * project_term],
            "goal_seek_unit_price_multiplier": 1.0,
            "loan_interest_rate": loan_interest_rate,
            "project_term": project_term,
        }
    )

    # Independently recompute expected digester CAPEX/OPEX with the real
    # calculator, aggregated across BOTH configured digesters.
    crf = DigesterCostCalculator.capital_recovery_factor(loan_interest_rate, project_term)
    expected_capex = 0.0
    expected_opex = 0.0
    for digester in digester_config:
        volume_proxy = max(1.0, cow_num * float(digester["hydraulic_retention_time"]))
        annual_fixed_cost = DigesterCostCalculator.calculate_digester_capital_cost(
            animal_units=cow_num, digester_volume=volume_proxy
        )
        capex = DigesterCostCalculator.calculate_digester_capex(annual_fixed_cost, crf)
        capex = DigesterCostCalculator.scale_installed_cost(
            base_cost=capex, volume=volume_proxy, base_volume=max(1.0, cow_num), install_factor=0.6
        )
        expected_capex += capex
        expected_opex += DigesterCostCalculator.calculate_digester_operational_cost(
            True,
            animal_units=cow_num,
            farm_type_flag=1.0,
            below_ground_flag=1.0,
            concrete_flag=1.0,
            steel_flag=0.0,
        )

    # The fallback no longer wins -- the core acceptance criterion of #3063.
    assert prepared["capital_cost"] != pytest.approx(15000.0)
    # Capital cost = non-digester base ($15k) + aggregated digester CAPEX.
    assert prepared["capital_cost"] == pytest.approx(15000.0 + expected_capex)
    # Multi-digester aggregation actually summed both digesters (not just one).
    assert expected_capex > 0.0
    # Operating costs include the aggregated Equation-4 digester OPEX.
    assert prepared["operating_costs"].tolist() == pytest.approx([1000.0 + expected_opex] * project_term)
