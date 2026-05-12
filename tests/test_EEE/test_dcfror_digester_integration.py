from pytest_mock import MockerFixture
import pytest

from RUFAS.EEE.economics.dcfror import DCFRORCalculator


def test_prepare_costs_applies_digester_cost_curve(mocker: MockerFixture) -> None:
    calc = DCFRORCalculator.__new__(DCFRORCalculator)
    calc.om = mocker.Mock()
    calc.im = mocker.Mock()
    calc.im.get_data.side_effect = lambda key: {
        "animal_properties.herd_information.cow_num": 1000.0,
        "economic_inputs.Manure.digester.system_type": "Covered Lagoon - RNG",
    }[key]

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
            "project_term": 2,
        }
    )

    assert prepared["capital_cost"] == pytest.approx(1_500_009.0)
    assert prepared["operating_costs"].tolist() == pytest.approx([263_552.25, 263_552.25])


def test_prepare_costs_without_digester_rows_unchanged(mocker: MockerFixture) -> None:
    calc = DCFRORCalculator.__new__(DCFRORCalculator)
    calc.om = mocker.Mock()
    calc.im = mocker.Mock()

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
            "project_term": 2,
        }
    )

    assert prepared["capital_cost"] == pytest.approx(10.0)
    assert prepared["operating_costs"].tolist() == pytest.approx([1.0, 1.0])
