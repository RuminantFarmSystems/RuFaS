from pytest_mock import MockerFixture
import pytest

from RUFAS.EEE.economics.dcfror import DCFRORCalculator


def test_prepare_costs_applies_digester_cost_curve(mocker: MockerFixture) -> None:
    calc = DCFRORCalculator.__new__(DCFRORCalculator)
    calc.om = mocker.Mock()
    calc.im = mocker.Mock()
    calc.im.get_data.side_effect = lambda key: {
        "animal_properties.herd_information.cow_num": 1000.0,
        "manure_management_properties.anaerobic_digester": [{"hydraulic_retention_time": 30.0}],
    }[key]
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

    assert prepared["capital_cost"] == pytest.approx(8009.0)
    assert prepared["operating_costs"].tolist() == pytest.approx([251.0, 251.0])


def test_prepare_costs_without_digester_rows_unchanged(mocker: MockerFixture) -> None:
    calc = DCFRORCalculator.__new__(DCFRORCalculator)
    calc.om = mocker.Mock()
    calc.im = mocker.Mock()
    calc.im.get_data.side_effect = KeyError

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
